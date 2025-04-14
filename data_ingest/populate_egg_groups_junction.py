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

# === Build egg group name → ID map (using 'name' not 'egg_group') ===
cur.execute("SELECT id, name FROM pokemon_egg_groups;")
egg_group_map = {name.lower(): id for id, name in cur.fetchall()}

# === Map CSV columns to slot names ===
slot_columns = {
    'primary': 'primary_egg_group',
    'secondary': 'secondary_egg_group'
}

# === Loop through Pokémon rows ===
for _, row in df.iterrows():
    pokemon_id = int(row['pokemon_id'])

    for slot, csv_col in slot_columns.items():
        group_name = row.get(csv_col)

        if group_name and isinstance(group_name, str):
            group_id = egg_group_map.get(group_name.lower())
            if group_id:
                try:
                    cur.execute("""
                        INSERT INTO pokemon_egg_groups_junction (pokemon_id, egg_group_id, slot)
                        VALUES (%s, %s, %s)
                        ON CONFLICT DO NOTHING;
                    """, (pokemon_id, group_id, slot))
                    print(f"✅ Linked {row['pokemon_name']} → {group_name} ({slot})")
                except Exception as e:
                    print(f"❌ Failed to link {row['pokemon_name']} → {group_name} ({slot}): {e}")
                    raise e
            else:
                print(f"⚠️ Egg group '{group_name}' not found for {row['pokemon_name']}")

conn.commit()
cur.close()
conn.close()

