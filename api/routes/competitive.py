# api/routes/competitive.py
from fastapi import APIRouter, Query, HTTPException
from typing import List, Optional
from starlette.status import HTTP_404_NOT_FOUND, HTTP_400_BAD_REQUEST
from psycopg2.extras import RealDictCursor
from api.db import get_db_connection
from api.models.competitive import CompetitiveFactors

router = APIRouter()

@router.get("/", response_model=List[CompetitiveFactors])
def get_competitive_info(
    ids: List[int] = Query(
        ..., 
        description="List of Pokémon IDs to fetch competitive data for, e.g. ?ids=1&ids=2",
        min_items=1,
        max_items=50
    )
):
    placeholders = ",".join(["%s"] * len(ids))
    sql = f"SELECT * FROM pokemon_competitive_factors_view WHERE pokemon_id IN ({placeholders}) ORDER BY pokemon_id;"

    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute(sql, tuple(ids))
    results = cur.fetchall()
    cur.close()
    conn.close()

    found_ids = {row["pokemon_id"] for row in results}
    missing = [i for i in ids if i not in found_ids]
    if missing:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail={
                "message": f"No competitive data found for IDs: {missing}",
                "found": results,
                "missing_ids": missing
            }
        )

    return results

ALLOWED_FORMATS = {"smogon_vgc", "worlds_vgc"}
ALLOWED_YEARS = {2022, 2023, 2024}

@router.get("/filter", response_model=List[CompetitiveFactors])
def filter_competitive(
    # --- Typing & Abilities & Stats (unchanged) ---
    types: Optional[List[str]] = Query(None, min_items=1, max_items=2),
    types_logic: str = Query("or", regex="^(and|or)$"),
    abilities: Optional[List[str]] = Query(None, min_items=1, max_items=4),

    base_stat_total_min: Optional[int] = Query(None, ge=0),
    base_stat_total_max: Optional[int] = Query(None, ge=0),
    health_stat_min: Optional[int] = Query(None, ge=0),
    health_stat_max: Optional[int] = Query(None, ge=0),
    attack_stat_min: Optional[int] = Query(None, ge=0),
    attack_stat_max: Optional[int] = Query(None, ge=0),
    defense_stat_min: Optional[int] = Query(None, ge=0),
    defense_stat_max: Optional[int] = Query(None, ge=0),
    special_attack_stat_min: Optional[int] = Query(None, ge=0),
    special_attack_stat_max: Optional[int] = Query(None, ge=0),
    special_defense_stat_min: Optional[int] = Query(None, ge=0),
    special_defense_stat_max: Optional[int] = Query(None, ge=0),
    speed_stat_min: Optional[int] = Query(None, ge=0),
    speed_stat_max: Optional[int] = Query(None, ge=0),

    # --- New usage filters ---
    usage_min: Optional[float] = Query(None, ge=0.0, le=100.0, description="Minimum usage %"),
    usage_max: Optional[float] = Query(None, ge=0.0, le=100.0, description="Maximum usage %"),
    formats: Optional[List[str]] = Query(
        None,
        description="Which formats—smogon_vgc or worlds_vgc. Defaults to both if omitted"
    ),
    years: Optional[List[int]] = Query(
        None,
        description="Which years (2022–2024). Defaults to all if omitted"
    ),
):
    # Validation for format & year lists
    fmt_list = formats or list(ALLOWED_FORMATS)
    if any(f not in ALLOWED_FORMATS for f in fmt_list):
        raise HTTPException(400, detail=f"formats must be subset of {ALLOWED_FORMATS}")
    yr_list = years or sorted(ALLOWED_YEARS)
    if any(y not in ALLOWED_YEARS for y in yr_list):
        raise HTTPException(400, detail=f"years must be subset of {sorted(ALLOWED_YEARS)}")

    # Must have ≥1 filter
    if not any([
        types, abilities,
        base_stat_total_min, base_stat_total_max,
        health_stat_min, health_stat_max,
        attack_stat_min, attack_stat_max,
        defense_stat_min, defense_stat_max,
        special_attack_stat_min, special_attack_stat_max,
        special_defense_stat_min, special_defense_stat_max,
        speed_stat_min, speed_stat_max,
        usage_min, usage_max
    ]):
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="At least one filter parameter must be provided."
        )

    clauses: List[str] = []
    params: List = []

    # -- typing (same as before) --
    if types:
        if types_logic == "or":
            clauses.append("(primary_type = ANY(%s) OR secondary_type = ANY(%s))")
            params.extend([types, types])
        else:  # AND logic
            t1, t2 = (types + types)[:2]
            clauses.append("""
                ((primary_type = %s AND secondary_type = %s)
                 OR (primary_type = %s AND secondary_type = %s))
            """)
            params.extend([t1, t2, t2, t1])

    # -- abilities (array overlap) --
    if abilities:
        clauses.append(
            "ARRAY[primary_ability, secondary_ability, hidden_ability, event_ability] && %s"
        )
        params.append(abilities)

    # -- stats (same loop as before) --
    stat_fields = [
        ("base_stat_total", base_stat_total_min, base_stat_total_max),
        ("health_stat", health_stat_min, health_stat_max),
        ("attack_stat", attack_stat_min, attack_stat_max),
        ("defense_stat", defense_stat_min, defense_stat_max),
        ("special_attack_stat", special_attack_stat_min, special_attack_stat_max),
        ("special_defense_stat", special_defense_stat_min, special_defense_stat_max),
        ("speed_stat", speed_stat_min, speed_stat_max),
    ]
    for col, mn, mx in stat_fields:
        if mn is not None:
            clauses.append(f"{col} >= %s"); params.append(mn)
        if mx is not None:
            clauses.append(f"{col} <= %s"); params.append(mx)

    # -- usage (OR over all selected format/year columns) --
    if usage_min is not None or usage_max is not None:
        usage_clauses = []
        for fmt in fmt_list:
            for yr in yr_list:
                col = f"{fmt}_usage_{yr}"
                sub = []
                if usage_min is not None:
                    sub.append(f"{col} >= %s"); params.append(usage_min)
                if usage_max is not None:
                    sub.append(f"{col} <= %s"); params.append(usage_max)
                if sub:
                    usage_clauses.append("(" + " AND ".join(sub) + ")")
        # combine all with OR
        clauses.append("(" + " OR ".join(usage_clauses) + ")")

    # build and run
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
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="No Pokémon matched the provided filters."
        )

    return rows