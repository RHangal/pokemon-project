# api/routes/pokemon.py
from fastapi import APIRouter, Query, HTTPException
from typing import List
from starlette.status import HTTP_404_NOT_FOUND
from psycopg2.extras import RealDictCursor
from api.db import get_db_connection
from api.models.pokemon import Pokemon

router = APIRouter()

@router.get("/", response_model=List[Pokemon])
def get_pokemon(
    ids: List[int] = Query(
        ...,
        description="List of Pokémon IDs to fetch, e.g. ?ids=1&ids=2&ids=3. Must provide 1–50 IDs.",
        min_items=1,
        max_items=50
    )
):
    # Build the IN‑clause placeholders
    placeholders = ",".join("%s" for _ in ids)
    sql = f"SELECT * FROM pokemon WHERE id IN ({placeholders}) ORDER BY id;"

    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute(sql, tuple(ids))
    results = cur.fetchall()
    cur.close()
    conn.close()

    # Detect any missing IDs
    found_ids = {row["id"] for row in results}
    missing = [i for i in ids if i not in found_ids]
    if missing:
        # Raise a 404 but include the partial results
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail={
                "message": f"No Pokémon found for IDs: {missing}",
                "found": results,
                "missing_ids": missing
            }
        )

    return results
