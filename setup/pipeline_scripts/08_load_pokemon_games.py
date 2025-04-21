import pandas as pd
from scripts.utils.db_utils import get_csv_path

def run(cur):
    # === Load and clean the CSV ===
    games_df = pd.read_csv(get_csv_path("pokemon_games.csv"), quotechar='"', encoding='utf-8', dtype=str)
    games_df.columns = games_df.columns.str.strip().str.lower().str.replace(" ", "_")

    # Normalize multiline field
    games_df['releaseyearsbysystem'] = games_df['releaseyearsbysystem'] \
        .str.replace('\n', ' | ', regex=True) \
        .str.replace('\r', '', regex=True) \
        .str.strip()

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

