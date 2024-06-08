from datetime import datetime

from django.contrib.auth import get_user_model


def get_or_create_user(phone_number):
    user, created = get_user_model().objects.get_or_create(
        phone_number=phone_number, is_verify=True, verify_date=datetime.now(), is_active=True)
    return user, created