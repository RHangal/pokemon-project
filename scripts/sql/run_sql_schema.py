import os
from scripts.utils.db_utils import get_db_connection, get_root_path

# === Resolve base paths ===
SCHEMA_DIR = os.path.join(get_root_path(), "db_schema")
SQL_TABLES_DIR = os.path.join(SCHEMA_DIR, "sql", "tables")
SQL_VIEWS_DIR = os.path.join(SCHEMA_DIR, "sql", "views")

# SQL files to execute in order
SQL_FILES = [
    os.path.join(SQL_TABLES_DIR, "01_create_core_tables.sql"),
    os.path.join(SQL_TABLES_DIR, "02_create_core_pokemon_table.sql"),
    os.path.join(SQL_TABLES_DIR, "03_create_junction_tables.sql"),
    os.path.join(SQL_TABLES_DIR, "04_create_competitive_table.sql"),
    os.path.join(SQL_VIEWS_DIR, "pokemon_competitive_factors_view.sql"),
]

def run_sql_file(cur, path):
    with open(path, "r") as f:
        sql = f.read()
        cur.execute(sql)

def main():
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        print("✅ Connected to database.")

        cur.execute("BEGIN;")  # Start atomic transaction

        for file_path in SQL_FILES:
            print(f"📄 Executing: {os.path.basename(file_path)}")
            run_sql_file(cur, file_path)
            print(f"✅ Completed: {os.path.basename(file_path)}\n")

        conn.commit()
        print("🚀 All SQL scripts executed successfully.")

    except Exception as e:
        if conn:
            conn.rollback()
            print("⚠️ Rolled back all changes due to error.")
        print(f"❌ Error: {e}")
        raise
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
        print("🔒 Connection closed.")

if __name__ == "__main__":
    main()
