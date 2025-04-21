import pandas as pd
from scripts.utils.db_utils import get_csv_path

def run(cur):
    # === Load and clean the CSV ===
    df = pd.read_csv(get_csv_path("pokemon_database.csv"))
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

    # === Extract unique, non-null catch rates ===
    catch_rates = df[['catch_rate']].dropna().drop_duplicates()
    catch_rates['catch_rate'] = catch_rates['catch_rate'].astype(int)

    # === Insert into DB (assumes outer transaction is already started) ===
    for rate in catch_rates['catch_rate']:
        cur.execute("""
            INSERT INTO pokemon_catch_rate (catch_rate)
            VALUES (%s)
            ON CONFLICT DO NOTHING;
        """, (rate,))

