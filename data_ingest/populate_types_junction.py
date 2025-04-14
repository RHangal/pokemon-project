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

# === Load and clean CSV ===
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

# === Build type lookup map ===
cur.execute("SELECT id, type FROM pokemon_types;")
type_map = {t.lower(): id for id, t in cur.fetchall()}

# === Insert into junction table ===
for _, row in df.iterrows():
    pokemon_id = int(row['pokemon_id'])

    for slot in ['primary', 'secondary']:
        col = f'{slot}_type'
        type_name = row.get(col)

        if type_name and isinstance(type_name, str):
            type_id = type_map.get(type_name.lower())
            if type_id:
                try:
                    cur.execute("""
                        INSERT INTO pokemon_types_junction (pokemon_id, type_id, slot)
                        VALUES (%s, %s, %s)
                        ON CONFLICT DO NOTHING;
                    """, (pokemon_id, type_id, slot))
                    print(f"✅ Linked {row['pokemon_name']} to {type_name} ({slot})")
                except Exception as e:
                    print(f"❌ Failed to link {row['pokemon_name']} to {type_name} ({slot}): {e}")
                    raise e
            else:
                print(f"⚠️ Type '{type_name}' not found for {row['pokemon_name']}")

conn.commit()
cur.close()
conn.close()

