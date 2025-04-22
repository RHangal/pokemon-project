# api/main.py
from fastapi import FastAPI
from api.routes import pokemon, competitive, sql
from api.graphql.schema import graphql_app

app = FastAPI(title="Pokémon API")

app.include_router(pokemon.router, prefix="/pokemon", tags=["Pokémon"])
app.include_router(competitive.router, prefix="/competitive", tags=["Competitive_Pokémon_View"])
app.include_router(sql.router, prefix="/sql", tags=["SQL"])

# mount GraphQL
app.mount("/graphql", graphql_app)
app.add_websocket_route("/graphql", graphql_app)

