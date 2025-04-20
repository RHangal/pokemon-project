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

    # Build cache of base_happiness → id
    cur.execute("SELECT id, base_happiness FROM pokemon_happiness;")
    happiness_map = {int(h): id for id, h in cur.fetchall()}

    for _, row in df.iterrows():
        pokemon_id = int(row["pokemon_id"])
        raw_happiness = row["base_happiness"]

        try:
            happiness_value = int(raw_happiness)
            happiness_id = happiness_map.get(happiness_value)

            if happiness_id:
                cur.execute("""
                    UPDATE pokemon
                    SET base_happiness_id = %s
                    WHERE pokemon_id = %s;
                """, (happiness_id, pokemon_id))
                print(f"✅ Updated base_happiness_id for {row['pokemon_name']} ({happiness_value})")
            else:
                print(f"⚠️ No matching base_happiness_id for: {row['pokemon_name']} → {happiness_value}")

        except Exception as e:
            print(f"❌ Failed on {row['pokemon_name']}: {e}")
            raise e

    conn.commit()
    print("🚀 Base happiness linking completed.")

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
