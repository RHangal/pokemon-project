import pandas as pd
from scripts.utils.db_utils import get_csv_path

def run(cur):
    # === Load and clean the CSV ===
    df = pd.read_csv(get_csv_path("pokemon_database.csv"))
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

    # === Extract and clean unique base happiness values ===
    happiness = df[['base_happiness']].dropna().drop_duplicates()
    happiness['base_happiness'] = happiness['base_happiness'].astype(int)
    happiness = happiness.sort_values(by='base_happiness')

    for val in happiness['base_happiness']:
        cur.execute("""
            INSERT INTO pokemon_happiness (base_happiness)
            VALUES (%s)
            ON CONFLICT DO NOTHING;
        """, (val,))


