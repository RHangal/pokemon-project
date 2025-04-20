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

# === Extract and clean experience growth info ===
exp = df[['experience_growth', 'experience_growth_total']].dropna().drop_duplicates()

# Remove quotes and whitespace from text
exp['experience_growth'] = exp['experience_growth'].str.replace('"', '').str.strip()
exp['experience_growth_total'] = exp['experience_growth_total'].astype(int)

exp = exp.sort_values(by='experience_growth_total').reset_index(drop=True)

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
for _, row in exp.iterrows():
    cur.execute("""
        INSERT INTO pokemon_experience_growth (description, growth_total)
        VALUES (%s, %s)
        ON CONFLICT (description) DO NOTHING;
    """, (row['experience_growth'], row['experience_growth_total']))

conn.commit()
cur.close()
conn.close()

print("✅ Experience growth values inserted successfully!")

