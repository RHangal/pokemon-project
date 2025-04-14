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

# === Load and clean the CSV ===
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
    'event': 'special_event_ability'  # CSV uses this name
}

# === Loop through Pokémon rows ===
for _, row in df.iterrows():
    pokemon_id = int(row['pokemon_id'])

    for slot, csv_col in slot_columns.items():
        ability_name = row.get(csv_col)

        if ability_name and isinstance(ability_name, str):
            ability_id = ability_map.get(ability_name.lower())
            if ability_id:
                try:
                    cur.execute("""
                        INSERT INTO pokemon_abilities_junction (pokemon_id, ability_id, slot)
                        VALUES (%s, %s, %s)
                        ON CONFLICT DO NOTHING;
                    """, (pokemon_id, ability_id, slot))
                    print(f"✅ Linked {row['pokemon_name']} → {ability_name} ({slot})")
                except Exception as e:
                    print(f"❌ Failed to link {row['pokemon_name']} → {ability_name} ({slot}): {e}")
                    raise e
            else:
                print(f"⚠️ Ability '{ability_name}' not found for {row['pokemon_name']}")

conn.commit()
cur.close()
conn.close()

