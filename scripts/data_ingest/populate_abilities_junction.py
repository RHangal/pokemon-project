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

# === Build ability name → ID map ===
cur.execute("SELECT id, name FROM pokemon_ability;")
ability_map = {name.lower(): id for id, name in cur.fetchall()}

# === Map CSV columns to slot labels ===
slot_columns = {
    'primary': 'primary_ability',
    'secondary': 'secondary_ability',
    'hidden': 'hidden_ability',
    'event': 'special_event_ability'
}

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

    for slot, col in slot_columns.items():
        ability_name = row.get(col)

        if pd.notna(ability_name) and isinstance(ability_name, str):
            clean_ability = ability_name.strip().lower()
            ability_id = ability_map.get(clean_ability)

            if ability_id:
                try:
                    cur.execute("""
                        INSERT INTO pokemon_abilities_junction (pokemon_id, ability_id, slot)
                        VALUES (%s, %s, %s)
                        ON CONFLICT DO NOTHING;
                    """, (pokemon_id, ability_id, slot))

                    if name in ['flutter mane', 'incineroar']:
                        print(f"🔎 [{name.title()}] - Linked to ability '{clean_ability}' (slot: {slot}, id: {ability_id})")
                except Exception as e:
                    print(f"❌ Failed to link {name} to {clean_ability} ({slot}): {e}")
                    raise e
            else:
                print(f"⚠️ Ability '{clean_ability}' not found in DB for {name}")

conn.commit()
cur.close()
conn.close()
