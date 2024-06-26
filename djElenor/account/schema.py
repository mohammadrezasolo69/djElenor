from django.contrib.auth import get_user_model


import graphene
import graphql_jwt
from graphene_django import DjangoObjectType
from graphql_jwt.decorators import login_required
from graphql_jwt.shortcuts import create_refresh_token, get_token

from djElenor.account.selectors import get_user_by_phone_number
from djElenor.account.services import get_or_create_user
from djElenor.utils.generate_random_code import generate_random
from djElenor.utils.redis_connection import redis_set, redis_get, redis_delete
from djElenor.utils.sender import sms_sender


# ------------------------------- Query ---------------------------------
class UserType(DjangoObjectType):
    class Meta:
        model = get_user_model()
        fields = (
            'id', "avatar", 'phone_number', "note", 'is_active', 'first_name', 'last_name',
            'is_superuser', 'is_staff', "language_code",
            "search_document", "is_verify_email", "is_verify_phone_number",
            "addresses", "default_shipping_address", "default_billing_address"
        )


class Query(graphene.ObjectType):
    user = graphene.Field(UserType, phone_number=graphene.String())

    @staticmethod
    @login_required
    def resolve_user(root, info, phone_number=None):
        user = get_user_by_phone_number(phone_number=phone_number)
        return user


# ------------------------------- Mutation ---------------------------------
class RequestOtp(graphene.Mutation):
    class Arguments:
        phone_number = graphene.String(required=True)

    ok = graphene.Boolean()
    message = graphene.String()

    @staticmethod
    def mutate(root, info, phone_number):
        # otp_code = generate_random(length=6, use_digit=True)
        otp_code = '123456'

        redis_set(key=phone_number, data=otp_code, ex=120)
        sms_sender(phone_number=phone_number, body=otp_code)
        return RequestOtp(ok=True, message='otp send .')


class VerifyOtp(graphene.Mutation):
    class Arguments:
        phone_number = graphene.String(required=True)
        code = graphene.String(required=True)

    ok = graphene.Boolean()
    message = graphene.String()
    is_new_user = graphene.String(default_value=None)
    user = graphene.Field(UserType, default_value=None)
    access_token = graphene.String(default_value=None)
    refresh_token = graphene.String(default_value=None)

    @staticmethod
    def mutate(root, info, phone_number, code):
        # get otp_code from cache
        otp_code_cache = redis_get(key=phone_number)

        # check otp_code_cache no expiration
        if otp_code_cache is None:
            return VerifyOtp(ok=False, message='Code expiration')

        # check code is otp_code_cache
        if str(otp_code_cache) != code:
            return VerifyOtp(ok=False, message='Code incorrect')

        # create or get user
        user, is_new_user = get_or_create_user(phone_number=str(phone_number))

        # create jwt token
        access_token = get_token(user)
        refresh_token = create_refresh_token(user)

        # delete otp code from cache
        redis_delete(key=phone_number)

        return VerifyOtp(
            ok=True, is_new_user=is_new_user, message='successfully',
            user=user, access_token=access_token, refresh_token=refresh_token
        )


class Mutation(graphene.ObjectType):
    request_otp = RequestOtp.Field()
    verify_otp = VerifyOtp.Field()

    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()
