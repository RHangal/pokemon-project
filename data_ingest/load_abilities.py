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

# === Load the CSV ===
df = pd.read_csv(CSV_PATH)
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

# === Clean + deduplicate ===
ability_pairs = ability_pairs.dropna().drop_duplicates()
ability_pairs['name'] = ability_pairs['name'].str.replace('"', '').str.strip()
ability_pairs['description'] = ability_pairs['description'].str.replace('"', '').str.strip()

# === Connect to PostgreSQL ===
conn = psycopg2.connect(
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT
)

cur = conn.cursor()

# === Insert into DB ===
for _, row in ability_pairs.iterrows():
    cur.execute("""
        INSERT INTO pokemon_ability (name, description)
        VALUES (%s, %s)
        ON CONFLICT (name) DO NOTHING;
    """, (row['name'], row['description']))

conn.commit()
cur.close()
conn.close()

print("✅ Abilities with descriptions inserted successfully!")

