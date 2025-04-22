import strawberry
from fastapi import FastAPI
from strawberry.asgi import GraphQL
from api.graphql.resolvers.competitive import Query

schema = strawberry.Schema(query=Query)
graphql_app = GraphQL(schema)

