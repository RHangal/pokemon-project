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

    for _, row in df.iterrows():
        pokemon_id = int(row["pokemon_id"])
        male = row.get("male_ratio")
        female = row.get("female_ratio")

        try:
            if male is not None and female is not None:
                male_val = float(male)
                female_val = float(female)

                cur.execute("""
                    SELECT id FROM pokemon_gender_ratio
                    WHERE male_percent = %s AND female_percent = %s
                    LIMIT 1;
                """, (male_val, female_val))

                result = cur.fetchone()
                if result:
                    gender_ratio_id = result[0]
                    cur.execute("""
                        UPDATE pokemon
                        SET gender_ratio_id = %s
                        WHERE pokemon_id = %s;
                    """, (gender_ratio_id, pokemon_id))
                    print(f"✅ Updated gender_ratio_id for {row['pokemon_name']} → {male_val} / {female_val}")
                else:
                    print(f"⚠️ No match for {row['pokemon_name']} → {male_val} / {female_val}")
            else:
                print(f"⚠️ Missing gender ratio for {row['pokemon_name']}")

        except Exception as e:
            print(f"❌ Failed on {row['pokemon_name']}: {e}")
            raise e

    conn.commit()
    print("🚀 Gender ratio linking completed.")

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
