import pandas as pd
from scripts.utils.db_utils import get_db_connection, get_csv_path

def main():
    conn = None
    cur = None

    try:
        # === Load the CSV ===
        df = pd.read_csv(get_csv_path("pokemon_database.csv"))
        df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

        # === Extract unique, non-null catch rates ===
        catch_rates = df[['catch_rate']].dropna().drop_duplicates()
        catch_rates['catch_rate'] = catch_rates['catch_rate'].astype(int)

        # === DB Connection ===
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("BEGIN;")

        for rate in catch_rates['catch_rate']:
            cur.execute("""
                INSERT INTO pokemon_catch_rate (catch_rate)
                VALUES (%s)
                ON CONFLICT DO NOTHING;
            """, (rate,))

        conn.commit()
        print("✅ Catch rates inserted successfully.")

    except Exception as e:
        print(f"❌ Error: {e}")
        if conn:
            conn.rollback()
            print("⚠️ Rolled back transaction due to error.")
        raise

    finally:
        if cur: cur.close()
        if conn: conn.close()
        print("🔒 Connection closed.")

if __name__ == "__main__":
    main()
