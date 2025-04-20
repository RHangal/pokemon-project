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

# === Load and clean the CSV ===
df = pd.read_csv(CSV_PATH)

# Normalize column names
df.columns = (
    df.columns
    .str.strip()
    .str.lower()
    .str.replace(" ", "_")
    .str.replace("-", "_")
)

# Strip quotes from all string values
df = df.applymap(lambda x: x.strip(' "\'') if isinstance(x, str) else x)

# === Connect to PostgreSQL ===
conn = psycopg2.connect(
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT
)
cur = conn.cursor()

# === Insert all Pokémon ===
for i, row in df.iterrows():
    row = row.where(pd.notna(row), None)

    try:
        cur.execute("""
            INSERT INTO pokemon (
                pokemon_id, pokedex_number, pokemon_name, classification,
                alternate_form_name, pre_evolution_pokemon_id, evolution_details,
                game_id, catch_rate_id, base_happiness_id, experience_growth_id, gender_ratio_id,
                health_stat, attack_stat, defense_stat, special_attack_stat,
                special_defense_stat, speed_stat, base_stat_total,
                health_ev, attack_ev, defense_ev, special_attack_ev,
                special_defense_ev, speed_ev, ev_yield_total
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s,
                    NULL, NULL, NULL, NULL, NULL,
                    %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (pokemon_id)
            DO UPDATE SET
                pokedex_number = EXCLUDED.pokedex_number,
                pokemon_name = EXCLUDED.pokemon_name,
                classification = EXCLUDED.classification,
                alternate_form_name = EXCLUDED.alternate_form_name,
                pre_evolution_pokemon_id = EXCLUDED.pre_evolution_pokemon_id,
                evolution_details = EXCLUDED.evolution_details,
                game_id = EXCLUDED.game_id,
                catch_rate_id = EXCLUDED.catch_rate_id,
                base_happiness_id = EXCLUDED.base_happiness_id,
                experience_growth_id = EXCLUDED.experience_growth_id,
                gender_ratio_id = EXCLUDED.gender_ratio_id,
                health_stat = EXCLUDED.health_stat,
                attack_stat = EXCLUDED.attack_stat,
                defense_stat = EXCLUDED.defense_stat,
                special_attack_stat = EXCLUDED.special_attack_stat,
                special_defense_stat = EXCLUDED.special_defense_stat,
                speed_stat = EXCLUDED.speed_stat,
                base_stat_total = EXCLUDED.base_stat_total,
                health_ev = EXCLUDED.health_ev,
                attack_ev = EXCLUDED.attack_ev,
                defense_ev = EXCLUDED.defense_ev,
                special_attack_ev = EXCLUDED.special_attack_ev,
                special_defense_ev = EXCLUDED.special_defense_ev,
                speed_ev = EXCLUDED.speed_ev,
                ev_yield_total = EXCLUDED.ev_yield_total;
        """, (
            int(row['pokemon_id']),
            int(row['pokedex_number']),
            row['pokemon_name'],
            row['classification'],
            row.get('alternate_form_name'),
            int(row['pre_evolution_pokemon_id']) if row['pre_evolution_pokemon_id'] is not None else None,
            row.get('evolution_details'),

            int(row['health_stat']),
            int(row['attack_stat']),
            int(row['defense_stat']),
            int(row['special_attack_stat']),
            int(row['special_defense_stat']),
            int(row['speed_stat']),
            int(row['base_stat_total']),

            int(row['health_ev']),
            int(row['attack_ev']),
            int(row['defense_ev']),
            int(row['special_attack_ev']),
            int(row['special_defense_ev']),
            int(row['speed_ev']),
            int(row['ev_yield_total'])
        ))
        print(f"✅ Inserted or updated: {row['pokemon_name']}")
    except Exception as e:
        print(f"❌ Failed on row {i} ({row['pokemon_name']}): {e}")
        raise e

conn.commit()
cur.close()
conn.close()

