import graphene

import djElenor.account.schema as account
import djElenor.product.schema as product


class Query(
    account.Query,
    product.ProductQueries,
    graphene.ObjectType
):
    pass


class Mutation(
    account.Mutation,
    graphene.ObjectType
):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation, auto_camelcase=False)
