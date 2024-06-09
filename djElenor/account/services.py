from datetime import datetime

from django.contrib.auth import get_user_model
from djElenor.account.selectors import get_user_by_phone_number


def get_or_create_user(phone_number):
    user = get_user_by_phone_number(phone_number)
    if user:
        return user, False

    user = get_user_model().objects.create(
        phone_number=phone_number, is_verify_phone_number=True, verify_phone_number_date=datetime.now(), is_active=True)
    return user, True
