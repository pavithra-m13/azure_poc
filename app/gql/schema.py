import strawberry
from strawberry.fastapi import GraphQLRouter
from gql.queries import Query
from gql.mutations import Mutation
from auth.dependencies import get_context

# GraphQL Schema
schema = strawberry.Schema(query=Query, mutation=Mutation)

# GraphQL router with authentication
graphql_app = GraphQLRouter(
    schema,
    context_getter=get_context,
    graphiql=True
)