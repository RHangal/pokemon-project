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

# === Load Pokémon CSV ===
df = pd.read_csv(CSV_PATH)
df.columns = (
    df.columns
    .str.strip()
    .str.lower()
    .str.replace(" ", "_")
    .str.replace("-", "_")
)

# === Connect to PostgreSQL ===
conn = psycopg2.connect(
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT
)
cur = conn.cursor()

# === Build a cache of base_happiness → ID ===
cur.execute("SELECT id, base_happiness FROM pokemon_happiness;")
happiness_map = {int(h): id for id, h in cur.fetchall()}

# === Loop and update base_happiness_id ===
for _, row in df.iterrows():
    pokemon_id = int(row['pokemon_id'])
    raw_happiness = row['base_happiness']

    try:
        happiness_value = int(raw_happiness)
        happiness_id = happiness_map.get(happiness_value)

        if happiness_id:
            cur.execute("""
                UPDATE pokemon
                SET base_happiness_id = %s
                WHERE pokemon_id = %s;
            """, (happiness_id, pokemon_id))
            print(f"✅ Updated base_happiness_id for {row['pokemon_name']} ({happiness_value})")
        else:
            print(f"⚠️ No matching base_happiness_id for: {row['pokemon_name']} → {happiness_value}")

    except Exception as e:
        print(f"❌ Failed on {row['pokemon_name']}: {e}")
        raise e

conn.commit()
cur.close()
conn.close()

