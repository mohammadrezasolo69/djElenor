import uuid
from functools import partial
from django.utils.translation import gettext_lazy as _

from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.contrib.postgres.indexes import GinIndex
from django.db import models
from django.db.models import JSONField, Value

from django.forms.models import model_to_dict
from django.utils import timezone
from django.utils.crypto import get_random_string
from django_countries.fields import Country, CountryField
from phonenumber_field.modelfields import PhoneNumber, PhoneNumberField

from djElenor.account.manageres import CustomUserManager
# from ..app.models import App
# from ..core.models import ModelWithExternalReference, ModelWithMetadata
# from ..core.utils.json_serializer import CustomJsonEncoder
from ..order.models import Order


# from ..permission.enums import AccountPermissions, BasePermissionEnum, get_permissions
# from ..permission.models import Permission, PermissionsMixin, _user_has_perm
# from ..site.models import SiteSettings
# from . import CustomerEvents
# from .validators import validate_possible_number


# class PossiblePhoneNumberField(PhoneNumberField):
#     """Less strict field for phone numbers written to database."""
#
#     default_validators = [validate_possible_number]
#

class AddressQueryset(models.QuerySet["Address"]):
    def annotate_default(self, user):
        # Set default shipping/billing address pk to None
        # if default shipping/billing address doesn't exist
        default_shipping_address_pk, default_billing_address_pk = None, None
        if user.default_shipping_address:
            default_shipping_address_pk = user.default_shipping_address.pk
        if user.default_billing_address:
            default_billing_address_pk = user.default_billing_address.pk

        return user.addresses.annotate(
            user_default_shipping_address_pk=Value(
                default_shipping_address_pk, models.IntegerField()
            ),
            user_default_billing_address_pk=Value(
                default_billing_address_pk, models.IntegerField()
            ),
        )


AddressManager = models.Manager.from_queryset(AddressQueryset)


class Address(models.Model):
    first_name = models.CharField(max_length=256, blank=True)
    last_name = models.CharField(max_length=256, blank=True)
    company_name = models.CharField(max_length=256, blank=True)
    street_address_1 = models.CharField(max_length=256, blank=True)
    street_address_2 = models.CharField(max_length=256, blank=True)
    city = models.CharField(max_length=256, blank=True)
    city_area = models.CharField(max_length=128, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country = CountryField()
    country_area = models.CharField(max_length=128, blank=True)
    phone = PhoneNumberField(blank=True, default="", db_index=True)

    objects = AddressManager()

    class Meta:
        ordering = ("pk",)
        indexes = [
            # *ModelWithMetadata.Meta.indexes,
            GinIndex(
                name="address_search_gin",
                # `opclasses` and `fields` should be the same length
                fields=["first_name", "last_name", "city", "country"],
                opclasses=["gin_trgm_ops"] * 4,
            ),
            GinIndex(
                name="warehouse_address_search_gin",
                # `opclasses` and `fields` should be the same length
                fields=[
                    "company_name",
                    "street_address_1",
                    "street_address_2",
                    "city",
                    "postal_code",
                    "phone",
                ],
                opclasses=["gin_trgm_ops"] * 6,
            ),
        ]

    def __eq__(self, other):
        if not isinstance(other, Address):
            return False
        return self.as_data() == other.as_data()

    __hash__ = models.Model.__hash__

    def as_data(self):
        """Return the address as a dict suitable for passing as kwargs.

        Result does not contain the primary key or an associated user.
        """
        data = model_to_dict(self, exclude=["id", "user"])
        if isinstance(data["country"], Country):
            data["country"] = data["country"].code
        if isinstance(data["phone"], PhoneNumber):
            data["phone"] = data["phone"].as_e164
        return data

    def get_copy(self):
        """Return a new instance of the same address."""
        return Address.objects.create(**self.as_data())


class User(AbstractUser):
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ("-id",)
        indexes = [
            GinIndex(name="user_search_gin", fields=["search_document"], opclasses=["gin_trgm_ops"]),
            GinIndex(
                name="order_user_search_gin", fields=["email", "first_name", "last_name"],
                opclasses=["gin_trgm_ops"] * 3),
        ]

    username = None

    uuid = models.UUIDField(default=uuid.uuid4(), unique=True)
    avatar = models.ImageField(upload_to="user-avatars", blank=True, null=True)
    phone_number = PhoneNumberField(unique=True,blank=True)
    note = models.TextField(null=True, blank=True)
    language_code = models.CharField(max_length=10, choices=settings.LANGUAGES, default='en')
    search_document = models.TextField(blank=True, null=True)

    is_active = models.BooleanField(default=False)
    is_verify_phone_number = models.BooleanField(default=False)
    is_verify_email = models.BooleanField(default=False)

    verify_phone_number_date = models.DateTimeField(null=True, blank=True)
    verify_email_date = models.DateTimeField(null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)

    # ---------------------- Relation Fields ----------------------
    addresses = models.ManyToManyField(Address, blank=True, related_name="users")
    default_shipping_address = models.ForeignKey(
        Address, on_delete=models.SET_NULL, null=True, blank=True,related_name='+')
    default_billing_address = models.ForeignKey(
        Address, on_delete=models.SET_NULL, null=True, blank=True,related_name='+')

    # ---------------------- Setting ----------------------
    objects = CustomUserManager()
    REQUIRED_FIELDS = []
    USERNAME_FIELD = 'phone_number'

    # ---------------------- Methods ----------------------

    def __str__(self):
        return str(self.uuid)

    @property
    def get_verify_phone_number_date(self):
        if self.verify_phone_number_date:
            return self.verify_phone_number_date.strftime('%H:%M - %Y/%m/%d')

    @property
    def get_verify_email_date(self):
        if self.verify_email_date:
            return self.verify_email_date.strftime('%H:%M - %Y/%m/%d')

    @property
    def get_created_date(self):
        return self.created_date.strftime('%H:%M - %Y/%m/%d')


class CustomerNote(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.SET_NULL)
    date = models.DateTimeField(db_index=True, auto_now_add=True)
    content = models.TextField()
    is_public = models.BooleanField(default=True)
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="notes", on_delete=models.CASCADE)

    class Meta:
        ordering = ("date",)


class CustomerEvent(models.Model):
    """Model used to store events that happened during the customer lifecycle."""

    date = models.DateTimeField(default=timezone.now, editable=False)
    type = models.CharField(
        max_length=255,
        # choices=[
        #     (type_name.upper(), type_name) for type_name, _ in CustomerEvents.CHOICES
        # ],
    )
    order = models.ForeignKey("order.Order", on_delete=models.SET_NULL, null=True)
    parameters = JSONField(blank=True, default=dict, )
    user = models.ForeignKey(
        User, related_name="events", on_delete=models.CASCADE, null=True
    )

    # app = models.ForeignKey(App, related_name="+", on_delete=models.SET_NULL, null=True)

    class Meta:
        ordering = ("date",)

    def __repr__(self):
        return f"{self.__class__.__name__}(type={self.type!r}, user={self.user!r})"


class StaffNotificationRecipient(models.Model):
    user = models.OneToOneField(
        User,
        related_name="staff_notification",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    staff_email = models.EmailField(unique=True, blank=True, null=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ("staff_email",)

    def get_email(self):
        return self.user.email if self.user else self.staff_email

# class GroupManager(models.Manager):
#     """The manager for the auth's Group model."""
#
#     use_in_migrations = True
#
#     def get_by_natural_key(self, name):
#         return self.get(name=name)


# class Group(models.Model):
#     """The system provides a way to group users.
#
#     Groups are a generic way of categorizing users to apply permissions, or
#     some other label, to those users. A user can belong to any number of
#     groups.
#
#     A user in a group automatically has all the permissions granted to that
#     group. For example, if the group 'Site editors' has the permission
#     can_edit_home_page, any user in that group will have that permission.
#
#     Beyond permissions, groups are a convenient way to categorize users to
#     apply some label, or extended functionality, to them. For example, you
#     could create a group 'Special users', and you could write code that would
#     do special things to those users -- such as giving them access to a
#     members-only portion of your site, or sending them members-only email
#     messages.
#     """
#
#     name = models.CharField("name", max_length=150, unique=True)
#     # permissions = models.ManyToManyField(
#     #     Permission,
#     #     verbose_name="permissions",
#     #     blank=True,
#     # )
#     restricted_access_to_channels = models.BooleanField(default=False)
#
#     objects = GroupManager()
#
#     class Meta:
#         verbose_name = "group"
#         verbose_name_plural = "groups"
#
#     def __str__(self):
#         return self.name
#
#     def natural_key(self):
#         return (self.name,)
