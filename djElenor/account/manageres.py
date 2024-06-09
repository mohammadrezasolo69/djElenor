from datetime import datetime

from django.contrib.auth.base_user import BaseUserManager
from django.db.models import Q
from django.db.models.expressions import Exists, OuterRef
from django.contrib.auth.models import Group
from djElenor.order.models import Order


class CustomUserManager(BaseUserManager["User"]):
    def _create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError('phone is required')
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, phone_number, password, **extra_fields):
        extra_fields.setdefault('is_active', False)
        extra_fields.setdefault('is_verify_phone_number', False)
        extra_fields.setdefault('is_verify_email', False)
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(phone_number, password, **extra_fields)

    def create_superuser(self, phone_number, password, **extra_fields):
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_verify_phone_number', True)
        extra_fields.setdefault('is_verify_email', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('verify_phone_number_date', datetime.now())
        extra_fields.setdefault('verify_email_date', datetime.now())

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(phone_number, password, **extra_fields)

    def customers(self):
        orders = Order.objects.values("user_id")
        return self.get_queryset().filter(
            Q(is_staff=False)
            | (Q(is_staff=True) & (Exists(orders.filter(user_id=OuterRef("pk")))))
        )

