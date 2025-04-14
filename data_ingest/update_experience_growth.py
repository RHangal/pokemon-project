import os
import pandas as pd
import psycopg2
from dotenv import load_dotenv

# === Load environment variables ===
load_dotenv()

CSV_PATH = os.getenv("CSV_PATH")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

# === Load and clean Pokémon CSV ===
df = pd.read_csv(CSV_PATH)
df.columns = (
    df.columns
    .str.strip()
    .str.lower()
    .str.replace(" ", "_")
    .str.replace("-", "_")
)

df = df.applymap(lambda x: x.strip(' "\'') if isinstance(x, str) else x)

# === Connect to PostgreSQL ===
conn = psycopg2.connect(
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT
)
cur = conn.cursor()

# === Build a cache of experience growth descriptions → ID ===
cur.execute("SELECT id, description FROM pokemon_experience_growth;")
growth_map = {desc.lower(): id for id, desc in cur.fetchall()}

# === Loop and update experience_growth_id ===
for _, row in df.iterrows():
    pokemon_id = int(row['pokemon_id'])
    raw_desc = row['experience_growth']

    try:
        key = raw_desc.lower().strip()
        growth_id = growth_map.get(key)

        if growth_id:
            cur.execute("""
                UPDATE pokemon
                SET experience_growth_id = %s
                WHERE pokemon_id = %s;
            """, (growth_id, pokemon_id))
            print(f"✅ Updated experience_growth_id for {row['pokemon_name']} → {raw_desc}")
        else:
            print(f"⚠️ No match for {row['pokemon_name']} → '{raw_desc}'")

    except Exception as e:
        print(f"❌ Failed on {row['pokemon_name']}: {e}")
        raise e

conn.commit()
cur.close()
conn.close()

