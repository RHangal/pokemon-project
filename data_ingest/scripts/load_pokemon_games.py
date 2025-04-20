import os
import pandas as pd
import psycopg2
from dotenv import load_dotenv

# === Load environment variables ===
load_dotenv()

GAMES_CSV_PATH = os.getenv("GAMES_CSV_PATH")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

# === Load and clean the CSV ===
games_df = pd.read_csv(GAMES_CSV_PATH, quotechar='"', encoding='utf-8', dtype=str)

# Normalize column names
games_df.columns = games_df.columns.str.strip().str.lower().str.replace(" ", "_")

# Normalize multi-line release years field
games_df['releaseyearsbysystem'] = games_df['releaseyearsbysystem'] \
    .str.replace('\n', ' | ', regex=True) \
    .str.replace('\r', '', regex=True) \
    .str.strip()

# === Connect to PostgreSQL ===
conn = psycopg2.connect(
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT
)
cur = conn.cursor()

# === Truncate the existing table to start fresh ===
cur.execute("TRUNCATE TABLE pokemon_games RESTART IDENTITY CASCADE;")
conn.commit()

# === Insert games data ===
for _, row in games_df.iterrows():
    cur.execute("""
        INSERT INTO pokemon_games (game_name, game_release_year, details, release_years_by_system)
        VALUES (%s, %s, %s, %s)
    """, (
        row['gamename'],
        int(row['gamereleaseyear']) if row['gamereleaseyear'] and row['gamereleaseyear'].isdigit() else None,
        row['details'],
        row['releaseyearsbysystem']
    ))

conn.commit()
cur.close()
conn.close()

print("✅ Pokémon games inserted successfully (clean and complete)!")

