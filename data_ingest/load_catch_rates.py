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

# === Extract unique catch rates ===
catch_rates = df[['catch_rate']].dropna().drop_duplicates()
catch_rates['catch_rate'] = catch_rates['catch_rate'].astype(int)

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
for rate in catch_rates['catch_rate']:
    cur.execute("""
        INSERT INTO pokemon_catch_rate (catch_rate)
        VALUES (%s)
        ON CONFLICT DO NOTHING;
    """, (rate,))

conn.commit()
cur.close()
conn.close()

print("✅ Catch rates inserted successfully!")

