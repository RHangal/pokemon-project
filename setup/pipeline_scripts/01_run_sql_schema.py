import os
from scripts.utils.db_utils import get_root_path

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

def run(cur):
    try:
        for file_path in SQL_FILES:
            print(f"📄 Executing: {os.path.basename(file_path)}")
            with open(file_path, "r") as f:
                sql = f.read()
                cur.execute(sql)
            print(f"✅ Completed: {os.path.basename(file_path)}\n")
    except Exception as e:
        print(f"❌ Error while executing SQL files: {e}")
        raise
