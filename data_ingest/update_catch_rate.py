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

# === Build a cache of catch_rate values → ID ===
cur.execute("SELECT id, catch_rate FROM pokemon_catch_rate;")
catch_rate_map = {int(rate): id for id, rate in cur.fetchall()}

# === Loop through Pokémon rows and update catch_rate_id ===
for _, row in df.iterrows():
    pokemon_id = int(row['pokemon_id'])
    raw_catch_rate = row['catch_rate']

    try:
        catch_rate_value = int(raw_catch_rate)
        catch_rate_id = catch_rate_map.get(catch_rate_value)

        if catch_rate_id:
            cur.execute("""
                UPDATE pokemon
                SET catch_rate_id = %s
                WHERE pokemon_id = %s;
            """, (catch_rate_id, pokemon_id))
            print(f"✅ Updated catch_rate_id for {row['pokemon_name']} ({catch_rate_value})")
        else:
            print(f"⚠️ No matching catch_rate_id for: {row['pokemon_name']} → {catch_rate_value}")

    except Exception as e:
        print(f"❌ Failed on {row['pokemon_name']}: {e}")
        raise e

conn.commit()
cur.close()
conn.close()

