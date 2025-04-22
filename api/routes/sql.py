# api/routes/sql.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from psycopg2.extras import RealDictCursor
from api.db import get_db_connection

router = APIRouter()

class SQLQuery(BaseModel):
    query: str

@router.post("/", response_model=List[Dict[str, Any]])
def execute_sql(sql: SQLQuery):
    raw = sql.query.strip()
    lowered = raw.lower()

    # Only allow a single SELECT statement
    if not lowered.startswith("select"):
        raise HTTPException(status_code=400, detail="Only SELECT statements are allowed.")
    # Disallow semicolons to prevent multi-statement injection
    if ";" in raw:
        raise HTTPException(status_code=400, detail="Semicolons are not allowed in query.")

    # Disallow other DML/DDL keywords
    forbidden = ["insert ", "update ", "delete ", "drop ", "alter ", "create ", "grant ", "revoke "]
    for kw in forbidden:
        if kw in lowered:
            raise HTTPException(status_code=400, detail=f"Forbidden keyword in query: {kw.strip()}")

    # Execute the query
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cur.execute(raw)
    except Exception as e:
        cur.close()
        conn.close()
        raise HTTPException(status_code=400, detail=f"Error executing query: {e}")
    results = cur.fetchall()
    cur.close()
    conn.close()
    return results


