import os
import pandas as pd
import psycopg2
from dotenv import load_dotenv

# === Load environment variables from .env ===
load_dotenv()

CSV_PATH = os.getenv("CSV_PATH")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

# === Load the CSV ===
df = pd.read_csv(CSV_PATH)

# === Clean column names ===
df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

# === Extract and clean egg groups ===
egg_cols = ['primary_egg_group', 'secondary_egg_group']
egg_groups = pd.concat([df[col] for col in egg_cols], axis=0)

egg_groups = egg_groups.dropna().drop_duplicates()
egg_groups = egg_groups.str.replace('"', '').str.strip().reset_index(drop=True)
egg_groups = egg_groups.to_frame(name='name').sort_values(by='name')

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
for name in egg_groups['name']:
    cur.execute("""
        INSERT INTO pokemon_egg_groups (name)
        VALUES (%s)
        ON CONFLICT (name) DO NOTHING;
    """, (name,))

conn.commit()
cur.close()
conn.close()

print("✅ Egg groups inserted successfully!")

