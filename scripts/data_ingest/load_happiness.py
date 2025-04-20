import pandas as pd
from scripts.utils.db_utils import get_db_connection, get_csv_path

def main():
    conn = None
    cur = None

    try:
        # === Load and clean the CSV ===
        df = pd.read_csv(get_csv_path("pokemon_database.csv"))
        df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

        # === Extract and clean unique base happiness values ===
        happiness = df[['base_happiness']].dropna().drop_duplicates()
        happiness['base_happiness'] = happiness['base_happiness'].astype(int)
        happiness = happiness.sort_values(by='base_happiness')

        # === Connect to DB and insert data ===
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("BEGIN;")

        for val in happiness['base_happiness']:
            cur.execute("""
                INSERT INTO pokemon_happiness (base_happiness)
                VALUES (%s)
                ON CONFLICT DO NOTHING;
            """, (val,))

        conn.commit()
        print("✅ Base happiness values inserted successfully.")

    except Exception as e:
        print(f"❌ Error: {e}")
        if conn:
            conn.rollback()
            print("⚠️ Rolled back transaction.")
        raise

    finally:
        if cur: cur.close()
        if conn: conn.close()
        print("🔒 Connection closed.")

if __name__ == "__main__":
    main()
