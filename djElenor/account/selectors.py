from django.contrib.auth import get_user_model


def get_user_by_phone_number(phone_number: str) -> get_user_model:
    user = get_user_model().objects.filter(phone_number=phone_number).last()
    return user


def get_user_by_jwt_token(jwt_token: str) -> get_user_model:
    pass