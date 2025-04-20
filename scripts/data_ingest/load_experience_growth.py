import pandas as pd
from scripts.utils.db_utils import get_db_connection, get_csv_path

def main():
    conn = None
    cur = None

    try:
        # === Load and clean the CSV ===
        df = pd.read_csv(get_csv_path("pokemon_database.csv"))
        df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

        # === Extract and clean experience growth data ===
        exp = df[['experience_growth', 'experience_growth_total']].dropna().drop_duplicates()
        exp['experience_growth'] = exp['experience_growth'].str.replace('"', '').str.strip()
        exp['experience_growth_total'] = exp['experience_growth_total'].astype(int)
        exp = exp.sort_values(by='experience_growth_total').reset_index(drop=True)

        # === Connect to DB and insert data ===
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("BEGIN;")

        for _, row in exp.iterrows():
            cur.execute("""
                INSERT INTO pokemon_experience_growth (description, growth_total)
                VALUES (%s, %s)
                ON CONFLICT (description) DO NOTHING;
            """, (row['experience_growth'], row['experience_growth_total']))

        conn.commit()
        print("✅ Experience growth values inserted successfully.")

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
