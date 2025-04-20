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
    name = row.get('pokemon_name', '').strip().lower()
    form = row.get('alternate_form_name', None)
    form = form.strip().lower() if pd.notna(form) else None

    # Find the correct pokemon.id from the DB
    cur.execute("""
        SELECT id FROM pokemon
        WHERE LOWER(pokemon_name) = %s AND 
              (alternate_form_name IS NULL AND %s IS NULL OR LOWER(alternate_form_name) = %s)
        LIMIT 1;
    """, (name, form, form))
    result = cur.fetchone()

    if not result:
        print(f"❌ Couldn't find Pokémon ID for: {name} ({form})")
        continue

    pokemon_id = result[0]

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

                    if name in ['flutter mane', 'incineroar']:
                        print(f"🔎 [{name.title()}] - Linked to type '{clean_type}' (slot: {slot}, id: {type_id})")
                except Exception as e:
                    print(f"❌ Failed to link {name} to {clean_type} ({slot}): {e}")
                    raise e
            else:
                print(f"⚠️ Type '{clean_type}' not found in DB for {name}")



conn.commit()
cur.close()
conn.close()
