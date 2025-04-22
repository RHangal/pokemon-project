import strawberry
from typing import List, Optional, Set
from graphql import GraphQLError
from psycopg2.extras import RealDictCursor
from fastapi import FastAPI
from strawberry.asgi import GraphQL

from api.db import get_db_connection
from api.graphql.types.competitive import GQLCompetitiveFactors

# Allowed formats and years
ALLOWED_FORMATS: Set[str] = {"smogon_vgc", "worlds_vgc"}
ALLOWED_YEARS: Set[int] = {2022, 2023, 2024}

@strawberry.input
class CompetitiveFilter:
    # Typing & Abilities & Stats
    types: Optional[List[str]] = None
    types_logic: Optional[str] = "or"
    abilities: Optional[List[str]] = None

    base_stat_total_min: Optional[int] = None
    base_stat_total_max: Optional[int] = None
    health_stat_min: Optional[int] = None
    health_stat_max: Optional[int] = None
    attack_stat_min: Optional[int] = None
    attack_stat_max: Optional[int] = None
    defense_stat_min: Optional[int] = None
    defense_stat_max: Optional[int] = None
    special_attack_stat_min: Optional[int] = None
    special_attack_stat_max: Optional[int] = None
    special_defense_stat_min: Optional[int] = None
    special_defense_stat_max: Optional[int] = None
    speed_stat_min: Optional[int] = None
    speed_stat_max: Optional[int] = None

    # Usage filters
    usage_min: Optional[float] = None  # 0.0 - 100.0
    usage_max: Optional[float] = None
    formats: Optional[List[str]] = None
    years: Optional[List[int]] = None

@strawberry.type
class Query:
    @strawberry.field
    def competitive_filter(self, filters: CompetitiveFilter) -> List[GQLCompetitiveFactors]:
        # Validate formats and years
        fmt_list = filters.formats or list(ALLOWED_FORMATS)
        if any(f not in ALLOWED_FORMATS for f in fmt_list):
            raise GraphQLError(f"formats must be subset of {ALLOWED_FORMATS}")
        yr_list = filters.years or sorted(ALLOWED_YEARS)
        if any(y not in ALLOWED_YEARS for y in yr_list):
            raise GraphQLError(f"years must be subset of {sorted(ALLOWED_YEARS)}")

        # Require at least one filter
        provided_any = any([
            filters.types, filters.abilities,
            filters.base_stat_total_min, filters.base_stat_total_max,
            filters.health_stat_min, filters.health_stat_max,
            filters.attack_stat_min, filters.attack_stat_max,
            filters.defense_stat_min, filters.defense_stat_max,
            filters.special_attack_stat_min, filters.special_attack_stat_max,
            filters.special_defense_stat_min, filters.special_defense_stat_max,
            filters.speed_stat_min, filters.speed_stat_max,
            filters.usage_min is not None, filters.usage_max is not None,
        ])
        if not provided_any:
            raise GraphQLError("At least one filter parameter must be provided.")

        clauses: List[str] = []
        params: List = []

        # Typing
        if filters.types:
            if filters.types_logic == "or":
                clauses.append("(primary_type = ANY(%s) OR secondary_type = ANY(%s))")
                params.extend([filters.types, filters.types])
            else:
                t1, t2 = (filters.types + filters.types)[:2]
                clauses.append(
                    "((primary_type = %s AND secondary_type = %s)"
                    " OR (primary_type = %s AND secondary_type = %s))"
                )
                params.extend([t1, t2, t2, t1])

        # Abilities
        if filters.abilities:
            clauses.append(
                "ARRAY[primary_ability, secondary_ability, hidden_ability, event_ability] && %s"
            )
            params.append(filters.abilities)

        # Stats loop
        stat_fields = [
            ("base_stat_total", filters.base_stat_total_min, filters.base_stat_total_max),
            ("health_stat", filters.health_stat_min, filters.health_stat_max),
            ("attack_stat", filters.attack_stat_min, filters.attack_stat_max),
            ("defense_stat", filters.defense_stat_min, filters.defense_stat_max),
            ("special_attack_stat", filters.special_attack_stat_min, filters.special_attack_stat_max),
            ("special_defense_stat", filters.special_defense_stat_min, filters.special_defense_stat_max),
            ("speed_stat", filters.speed_stat_min, filters.speed_stat_max),
        ]
        for col, mn, mx in stat_fields:
            if mn is not None:
                clauses.append(f"{col} >= %s"); params.append(mn)
            if mx is not None:
                clauses.append(f"{col} <= %s"); params.append(mx)

        # Usage OR over format/year columns
        if filters.usage_min is not None or filters.usage_max is not None:
            usage_clauses: List[str] = []
            for fmt in fmt_list:
                for yr in yr_list:
                    col = f"{fmt}_usage_{yr}"
                    sub: List[str] = []
                    if filters.usage_min is not None:
                        sub.append(f"{col} >= %s"); params.append(filters.usage_min)
                    if filters.usage_max is not None:
                        sub.append(f"{col} <= %s"); params.append(filters.usage_max)
                    if sub:
                        usage_clauses.append("(" + " AND ".join(sub) + ")")
            clauses.append("(" + " OR ".join(usage_clauses) + ")")

        # Final SQL
        where_sql = " AND ".join(clauses)
        sql = f"""
            SELECT *
            FROM pokemon_competitive_factors_view
            WHERE {where_sql}
            ORDER BY pokemon_id
            LIMIT 500;
        """

        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute(sql, tuple(params))
        rows = cur.fetchall()
        cur.close()
        conn.close()

        if not rows:
            raise GraphQLError("No Pokémon matched the provided filters.")

        return [GQLCompetitiveFactors(**r) for r in rows]
    
    @strawberry.field
    def competitive_info(self, ids: List[int]) -> List[GQLCompetitiveFactors]:
        # Validate list length
        if not ids or len(ids) > 50:
            raise GraphQLError("Provide between 1 and 50 IDs.")

        placeholders = ",".join("%s" for _ in ids)
        sql = (
            f"SELECT * FROM pokemon_competitive_factors_view "
            f"WHERE pokemon_id IN ({placeholders}) ORDER BY pokemon_id;"
        )
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute(sql, tuple(ids))
        rows = cur.fetchall()
        cur.close()
        conn.close()

        # Check missing
        found = {r["pokemon_id"] for r in rows}
        missing = [i for i in ids if i not in found]
        if missing:
            raise GraphQLError(f"No competitive data found for IDs: {missing}")

        return [GQLCompetitiveFactors(**r) for r in rows]

# Create schema and mount on FastAPI
schema = strawberry.Schema(query=Query)
graphql_app = GraphQL(schema)
app = FastAPI()
app.add_route("/graphql", graphql_app)
app.add_websocket_route("/graphql", graphql_app)
