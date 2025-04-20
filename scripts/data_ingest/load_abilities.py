import pandas as pd
from scripts.utils.db_utils import get_db_connection, get_csv_path

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

# === Insert into DB with atomic transaction ===
conn = None
cur = None

try:
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("BEGIN;")

    for _, row in ability_pairs.iterrows():
        cur.execute("""
            INSERT INTO pokemon_ability (name, description)
            VALUES (%s, %s)
            ON CONFLICT (name) DO NOTHING;
        """, (row['name'], row['description']))

    conn.commit()
    print("✅ Abilities with descriptions inserted successfully.")

except Exception as e:
    print(f"❌ Error: {e}")
    if conn:
        conn.rollback()
        print("⚠️ Rolled back due to error.")
    raise

finally:
    if cur: cur.close()
    if conn: conn.close()
    print("🔒 Connection closed.")
