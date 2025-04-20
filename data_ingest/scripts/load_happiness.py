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

# === Extract unique base happiness values ===
happiness = df[['base_happiness']].dropna().drop_duplicates()
happiness['base_happiness'] = happiness['base_happiness'].astype(int)
happiness = happiness.sort_values(by='base_happiness')

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
for val in happiness['base_happiness']:
    cur.execute("""
        INSERT INTO pokemon_happiness (base_happiness)
        VALUES (%s)
        ON CONFLICT DO NOTHING;
    """, (val,))

conn.commit()
cur.close()
conn.close()

print("✅ Base happiness values inserted successfully!")

