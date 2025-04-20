import pandas as pd
from scripts.utils.db_utils import get_db_connection, get_csv_path

# === Load and clean Pokémon CSV ===
df = pd.read_csv(get_csv_path("pokemon_database.csv"))
df.columns = (
    df.columns
    .str.strip()
    .str.lower()
    .str.replace(" ", "_")
    .str.replace("-", "_")
)
df = df.applymap(lambda x: x.strip(' "\'') if isinstance(x, str) else x)

# === Main DB operation ===
conn = None
cur = None

try:
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("BEGIN;")  # atomic transaction

    # Build cache: experience_growth.description → id
    cur.execute("SELECT id, description FROM pokemon_experience_growth;")
    growth_map = {desc.lower(): id for id, desc in cur.fetchall()}

    for _, row in df.iterrows():
        pokemon_id = int(row["pokemon_id"])
        raw_desc = row["experience_growth"]

        try:
            key = raw_desc.lower().strip()
            growth_id = growth_map.get(key)

            if growth_id:
                cur.execute("""
                    UPDATE pokemon
                    SET experience_growth_id = %s
                    WHERE pokemon_id = %s;
                """, (growth_id, pokemon_id))
                print(f"✅ Updated experience_growth_id for {row['pokemon_name']} → {raw_desc}")
            else:
                print(f"⚠️ No match for {row['pokemon_name']} → '{raw_desc}'")

        except Exception as e:
            print(f"❌ Failed on {row['pokemon_name']}: {e}")
            raise e

    conn.commit()
    print("🚀 Experience growth linking completed.")

except Exception as e:
    if conn:
        conn.rollback()
        print("⚠️ Rolled back due to error.")
    raise

finally:
    if cur:
        cur.close()
    if conn:
        conn.close()
    print("🔒 Connection closed.")
