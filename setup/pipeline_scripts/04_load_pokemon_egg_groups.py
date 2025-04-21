import pandas as pd
from scripts.utils.db_utils import get_csv_path

def run(cur):
    # === Load and clean CSV ===
    df = pd.read_csv(get_csv_path("pokemon_database.csv"))
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

    # === Extract and normalize egg groups ===
    egg_cols = ['primary_egg_group', 'secondary_egg_group']
    egg_groups = pd.concat([df[col] for col in egg_cols], axis=0)
    egg_groups = egg_groups.dropna().drop_duplicates()
    egg_groups = egg_groups.str.replace('"', '').str.strip().reset_index(drop=True)
    egg_groups = egg_groups.to_frame(name='name').sort_values(by='name')

    # === Insert into DB (shared transaction) ===
    for name in egg_groups['name']:
        cur.execute("""
            INSERT INTO pokemon_egg_groups (name)
            VALUES (%s)
            ON CONFLICT (name) DO NOTHING;
        """, (name,))

