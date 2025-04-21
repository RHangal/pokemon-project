from fastapi import FastAPI, Depends
from .db import get_db_connection
import psycopg2.extras

app = FastAPI()

@app.get("/")
def root():
    return {"message": "🚀 FastAPI is live!"}

@app.get("/pokemon")
def get_all_pokemon(conn = Depends(get_db_connection)):
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT id, pokemon_name, alternate_form_name, sprite_path FROM pokemon ORDER BY id LIMIT 50;")
    results = cur.fetchall()
    cur.close()
    return results

