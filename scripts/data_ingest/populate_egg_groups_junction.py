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

# === Build egg group name → ID map ===
cur.execute("SELECT id, name FROM pokemon_egg_groups;")
egg_group_map = {name.lower(): id for id, name in cur.fetchall()}

# === Define slot columns from CSV ===
slot_columns = {
    'primary': 'primary_egg_group',
    'secondary': 'secondary_egg_group'
}

# === Insert into junction table ===
for _, row in df.iterrows():
    name = row.get('pokemon_name', '').strip().lower()
    form = row.get('alternate_form_name', None)
    form = form.strip().lower() if pd.notna(form) else None

    # Find the correct pokemon.id from DB
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

    for slot, csv_col in slot_columns.items():
        group_name = row.get(csv_col)

        if pd.notna(group_name) and isinstance(group_name, str):
            clean_group = group_name.strip().lower()
            group_id = egg_group_map.get(clean_group)

            if group_id:
                try:
                    cur.execute("""
                        INSERT INTO pokemon_egg_groups_junction (pokemon_id, egg_group_id, slot)
                        VALUES (%s, %s, %s)
                        ON CONFLICT DO NOTHING;
                    """, (pokemon_id, group_id, slot))

                    if name in ['flutter mane', 'incineroar']:
                        print(f"🔎 [{name.title()}] - Linked to egg group '{clean_group}' (slot: {slot}, id: {group_id})")

                except Exception as e:
                    print(f"❌ Failed to link {name} to {clean_group} ({slot}): {e}")
                    raise e
            else:
                print(f"⚠️ Egg group '{clean_group}' not found in DB for {name}")

conn.commit()
cur.close()
conn.close()
