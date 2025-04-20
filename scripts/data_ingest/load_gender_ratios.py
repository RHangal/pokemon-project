import pandas as pd
from scripts.utils.db_utils import get_db_connection, get_csv_path

def main():
    conn = None
    cur = None

    try:
        # === Load and clean the CSV ===
        df = pd.read_csv(get_csv_path("pokemon_database.csv"))
        df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

        # === Extract and clean gender ratios ===
        gender = df[['male_ratio', 'female_ratio']].dropna().drop_duplicates()
        gender['male_ratio'] = gender['male_ratio'].astype(float)
        gender['female_ratio'] = gender['female_ratio'].astype(float)
        gender['label'] = gender['male_ratio'].astype(str) + " / " + gender['female_ratio'].astype(str)
        gender = gender.sort_values(by='male_ratio').reset_index(drop=True)

        # === Connect to DB and insert data ===
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("BEGIN;")

        for _, row in gender.iterrows():
            cur.execute("""
                INSERT INTO pokemon_gender_ratio (label, male_percent, female_percent)
                VALUES (%s, %s, %s)
                ON CONFLICT (label) DO NOTHING;
            """, (row['label'], row['male_ratio'], row['female_ratio']))

        conn.commit()
        print("✅ Gender ratios inserted successfully.")

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
