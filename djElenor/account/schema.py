from django.contrib.auth import get_user_model

import graphene
from graphene_django import DjangoObjectType
from graphql_jwt.decorators import login_required

from djElenor.account.selectors import get_user_by_phone_number


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
