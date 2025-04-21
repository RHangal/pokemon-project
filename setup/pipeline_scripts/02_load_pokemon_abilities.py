import pandas as pd
from scripts.utils.db_utils import get_csv_path

def run(cur):
    # === Load and clean the CSV ===
    csv_path = get_csv_path("pokemon_database.csv")
    df = pd.read_csv(csv_path)
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

    # === Combine all ability/description pairs ===
    ability_pairs = pd.concat([
        df[['primary_ability', 'primary_ability_description']].rename(columns={
            'primary_ability': 'name',
            'primary_ability_description': 'description'
        }),
        df[['secondary_ability', 'secondary_ability_description']].rename(columns={
            'secondary_ability': 'name',
            'secondary_ability_description': 'description'
        }),
        df[['hidden_ability', 'hidden_ability_description']].rename(columns={
            'hidden_ability': 'name',
            'hidden_ability_description': 'description'
        }),
        df[['special_event_ability', 'special_event_ability_description']].rename(columns={
            'special_event_ability': 'name',
            'special_event_ability_description': 'description'
        })
    ], axis=0)

    # === Clean and deduplicate ===
    ability_pairs = ability_pairs.dropna().drop_duplicates()
    ability_pairs['name'] = ability_pairs['name'].str.strip().str.replace('"', '')
    ability_pairs['description'] = ability_pairs['description'].str.strip().str.replace('"', '')

    # === Insert into DB (assumes outer transaction is already started) ===
    for _, row in ability_pairs.iterrows():
        cur.execute("""
            INSERT INTO pokemon_ability (name, description)
            VALUES (%s, %s)
            ON CONFLICT (name) DO NOTHING;
        """, (row['name'], row['description']))

