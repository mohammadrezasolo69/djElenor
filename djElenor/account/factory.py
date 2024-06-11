import random
from django.contrib.auth import get_user_model
from django.conf import settings
from datetime import datetime
import factory


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = get_user_model()
        exclude = ("addresses", "default_shipping_address", "default_billing_address")

    @staticmethod
    def choice_language_code():
        result = tuple(settings.LANGUAGE_CODE)
        number = random.randrange(0, len(result) - 1)
        return result[number][0]

    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    email = factory.LazyAttribute(lambda o: f'{o.last_name.replace(" ", "")}@gmail.com')
    phone_number = factory.LazyAttribute(lambda o: f"+98937{random.randrange(1111111, 99999999)}")
    language_code = factory.LazyFunction(choice_language_code)
    is_active = factory.Faker('boolean')
    is_verify_phone_number = factory.Faker('boolean')
    is_verify_email = factory.Faker('boolean')
    verify_phone_number_date = factory.LazyFunction(datetime.now)
    verify_email_date = factory.LazyFunction(datetime.now)
    created_date = factory.LazyFunction(datetime.now)
    avatar = factory.Faker('url')
    note = factory.Faker('name')
    search_document = factory.Faker('name')

    # TODO: after write AddressFactory
    addresses = None
    default_shipping_address = None
    default_billing_address = None
