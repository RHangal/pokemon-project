import pandas as pd
from scripts.utils.db_utils import get_db_connection, get_csv_path

def main():
    conn = None
    cur = None

    try:
        # === Load and clean CSV ===
        df = pd.read_csv(get_csv_path("pokemon_database.csv"))
        df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

        # === Extract and normalize egg groups ===
        egg_cols = ['primary_egg_group', 'secondary_egg_group']
        egg_groups = pd.concat([df[col] for col in egg_cols], axis=0)
        egg_groups = egg_groups.dropna().drop_duplicates()
        egg_groups = egg_groups.str.replace('"', '').str.strip().reset_index(drop=True)
        egg_groups = egg_groups.to_frame(name='name').sort_values(by='name')

        # === DB Connection ===
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("BEGIN;")

        for name in egg_groups['name']:
            cur.execute("""
                INSERT INTO pokemon_egg_groups (name)
                VALUES (%s)
                ON CONFLICT (name) DO NOTHING;
            """, (name,))

        conn.commit()
        print("✅ Egg groups inserted successfully.")

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
