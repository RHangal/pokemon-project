import pandas as pd
from scripts.utils.db_utils import get_db_connection, get_csv_path

def main():
    conn = None
    cur = None

    try:
        # === Load and clean the CSV ===
        df = pd.read_csv(get_csv_path("pokemon_database.csv"))
        df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

        # === Extract and clean unique types ===
        type_cols = ['primary_type', 'secondary_type']
        all_types = pd.concat([df[col] for col in type_cols], axis=0)
        all_types = all_types.dropna().drop_duplicates().str.replace('"', '').str.strip()
        all_types = all_types.to_frame(name='type').sort_values(by='type').reset_index(drop=True)

        # === Connect to PostgreSQL ===
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("BEGIN;")  # Atomic operation

        for t in all_types['type']:
            cur.execute("""
                INSERT INTO pokemon_types (type)
                VALUES (%s)
                ON CONFLICT (type) DO NOTHING;
            """, (t,))

        conn.commit()
        print("✅ Pokémon types inserted successfully.")

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
