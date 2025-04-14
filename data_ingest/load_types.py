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

# === Extract unique types from both columns ===
type_cols = ['primary_type', 'secondary_type']
all_types = pd.concat([df[col] for col in type_cols], axis=0)

# === Clean and deduplicate ===
all_types = all_types.dropna().drop_duplicates().str.replace('"', '').str.strip()
all_types = all_types.to_frame(name='type').sort_values(by='type').reset_index(drop=True)

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
for t in all_types['type']:
    cur.execute("""
        INSERT INTO pokemon_types (type)
        VALUES (%s)
        ON CONFLICT (type) DO NOTHING;
    """, (t,))

conn.commit()
cur.close()
conn.close()

print("✅ Pokémon types inserted successfully!")

