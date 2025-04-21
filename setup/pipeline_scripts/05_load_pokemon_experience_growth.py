import pandas as pd
from scripts.utils.db_utils import get_csv_path

def run(cur):
    # === Load and clean the CSV ===
    df = pd.read_csv(get_csv_path("pokemon_database.csv"))
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

    # === Extract and clean experience growth data ===
    exp = df[['experience_growth', 'experience_growth_total']].dropna().drop_duplicates()
    exp['experience_growth'] = exp['experience_growth'].str.replace('"', '').str.strip()
    exp['experience_growth_total'] = exp['experience_growth_total'].astype(int)
    exp = exp.sort_values(by='experience_growth_total').reset_index(drop=True)

    for _, row in exp.iterrows():
        cur.execute("""
            INSERT INTO pokemon_experience_growth (description, growth_total)
            VALUES (%s, %s)
            ON CONFLICT (description) DO NOTHING;
        """, (row['experience_growth'], row['experience_growth_total']))

