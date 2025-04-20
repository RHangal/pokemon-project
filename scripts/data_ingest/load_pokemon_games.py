import pandas as pd
from scripts.utils.db_utils import get_db_connection, get_csv_path

def main():
    conn = None
    cur = None

    try:
        # === Load and clean the CSV ===
        games_df = pd.read_csv(get_csv_path("pokemon_games.csv"), quotechar='"', encoding='utf-8', dtype=str)
        games_df.columns = games_df.columns.str.strip().str.lower().str.replace(" ", "_")

        # Normalize multiline field
        games_df['releaseyearsbysystem'] = games_df['releaseyearsbysystem'] \
            .str.replace('\n', ' | ', regex=True) \
            .str.replace('\r', '', regex=True) \
            .str.strip()

        # === Connect to PostgreSQL ===
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("BEGIN;")  # Start atomic transaction
        cur.execute("TRUNCATE TABLE pokemon_games RESTART IDENTITY CASCADE;")

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
        print("✅ Pokémon games inserted successfully.")

    except Exception as e:
        if conn:
            conn.rollback()
            print("⚠️ Rolled back due to error.")
        print(f"❌ Error: {e}")
        raise

    finally:
        if cur: cur.close()
        if conn: conn.close()
        print("🔒 Connection closed.")

if __name__ == "__main__":
    main()
