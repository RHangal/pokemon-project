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

# === Load Pokémon CSV ===
df = pd.read_csv(CSV_PATH)
df.columns = (
    df.columns
    .str.strip()
    .str.lower()
    .str.replace(" ", "_")
    .str.replace("-", "_")
)

# === Connect to PostgreSQL ===
conn = psycopg2.connect(
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT
)
cur = conn.cursor()

# === Loop and update gender_ratio_id using numeric match ===
for _, row in df.iterrows():
    pokemon_id = int(row['pokemon_id'])

    male = row.get('male_ratio')
    female = row.get('female_ratio')

    try:
        if male is not None and female is not None:
            male_val = float(male)
            female_val = float(female)

            cur.execute("""
                SELECT id FROM pokemon_gender_ratio
                WHERE male_percent = %s AND female_percent = %s
                LIMIT 1;
            """, (male_val, female_val))

            result = cur.fetchone()
            if result:
                gender_ratio_id = result[0]
                cur.execute("""
                    UPDATE pokemon
                    SET gender_ratio_id = %s
                    WHERE pokemon_id = %s;
                """, (gender_ratio_id, pokemon_id))
                print(f"✅ Updated gender_ratio_id for {row['pokemon_name']} → {male_val} / {female_val}")
            else:
                print(f"⚠️ No match for {row['pokemon_name']} → {male_val} / {female_val}")
        else:
            print(f"⚠️ Missing gender ratio for {row['pokemon_name']}")

    except Exception as e:
        print(f"❌ Failed on {row['pokemon_name']}: {e}")
        raise e

conn.commit()
cur.close()
conn.close()

