import pandas as pd
from scripts.utils.db_utils import get_db_connection, get_csv_path

# === Load and clean the CSV ===
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

    # Build cache of catch_rate → id
    cur.execute("SELECT id, catch_rate FROM pokemon_catch_rate;")
    catch_rate_map = {int(rate): id for id, rate in cur.fetchall()}

    for _, row in df.iterrows():
        pokemon_id = int(row["pokemon_id"])
        raw_catch_rate = row["catch_rate"]

        try:
            catch_rate_value = int(raw_catch_rate)
            catch_rate_id = catch_rate_map.get(catch_rate_value)

            if catch_rate_id:
                cur.execute("""
                    UPDATE pokemon
                    SET catch_rate_id = %s
                    WHERE pokemon_id = %s;
                """, (catch_rate_id, pokemon_id))
                print(f"✅ Updated catch_rate_id for {row['pokemon_name']} ({catch_rate_value})")
            else:
                print(f"⚠️ No matching catch_rate_id for: {row['pokemon_name']} → {catch_rate_value}")

        except Exception as e:
            print(f"❌ Failed on {row['pokemon_name']}: {e}")
            raise e

    conn.commit()
    print("🚀 Catch rate linking completed.")

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
