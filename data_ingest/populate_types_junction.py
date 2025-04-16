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

# Strip quotes and whitespace from string fields
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

# === Build lowercase type name → id lookup map from DB ===
cur.execute("SELECT id, type FROM pokemon_types;")
type_map = {t.lower(): id for id, t in cur.fetchall()}

# === Clear existing entries for a clean reset (optional)
# ⚠️ Uncomment this if you're resetting the table
# cur.execute("DELETE FROM pokemon_types_junction;")

# === Insert into junction table ===
for _, row in df.iterrows():
    pokemon_id = int(row['pokemon_id'])
    name = row.get('pokemon_name', '').lower()

    for slot in ['primary', 'secondary']:
        col = f'{slot}_type'
        type_name = row.get(col)

        if pd.notna(type_name) and isinstance(type_name, str):
            clean_type = type_name.strip().lower()
            type_id = type_map.get(clean_type)

            if type_id:
                try:
                    cur.execute("""
                        INSERT INTO pokemon_types_junction (pokemon_id, type_id, slot)
                        VALUES (%s, %s, %s)
                        ON CONFLICT DO NOTHING;
                    """, (pokemon_id, type_id, slot))

                    # 🔍 Print info if it's Flutter Mane or Incineroar
                    if name in ['flutter mane', 'incineroar']:
                        print(f"🔎 [{name.title()}] - Linked to type '{clean_type}' (slot: {slot}, id: {type_id})")

                except Exception as e:
                    print(f"❌ Failed to link {name} to {type_name} ({slot}): {e}")
                    raise e
            else:
                print(f"⚠️ Type '{type_name}' not found in DB for {name}")


conn.commit()
cur.close()
conn.close()
