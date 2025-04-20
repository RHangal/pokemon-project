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

# === Extract and clean gender ratios ===
gender = df[['male_ratio', 'female_ratio']].dropna().drop_duplicates()

# Remove quotes and convert to float
gender['male_ratio'] = gender['male_ratio'].astype(float)
gender['female_ratio'] = gender['female_ratio'].astype(float)

# Create a label like "87.5 / 12.5"
gender['label'] = gender['male_ratio'].astype(str) + " / " + gender['female_ratio'].astype(str)

# Sort for nice visuals
gender = gender.sort_values(by='male_ratio').reset_index(drop=True)

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
for _, row in gender.iterrows():
    cur.execute("""
        INSERT INTO pokemon_gender_ratio (label, male_percent, female_percent)
        VALUES (%s, %s, %s)
        ON CONFLICT (label) DO NOTHING;
    """, (row['label'], row['male_ratio'], row['female_ratio']))

conn.commit()
cur.close()
conn.close()

print("✅ Gender ratios inserted successfully!")

