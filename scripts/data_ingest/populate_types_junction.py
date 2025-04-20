import pandas as pd
from scripts.utils.db_utils import get_db_connection, get_csv_path

# === Load and clean CSV ===
df = pd.read_csv(get_csv_path("pokemon_database.csv"))
df.columns = (
    df.columns
    .str.strip()
    .str.lower()
    .str.replace(" ", "_")
    .str.replace("-", "_")
)
df = df.applymap(lambda x: x.strip(' "\'') if isinstance(x, str) else x)

# === Slot labels for type columns ===
type_slots = ['primary', 'secondary']

def main():
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("BEGIN;")

        # Build type name → id lookup map
        cur.execute("SELECT id, type FROM pokemon_types;")
        type_map = {t.lower(): id for id, t in cur.fetchall()}

        for _, row in df.iterrows():
            name = row.get('pokemon_name', '').strip().lower()
            form = row.get('alternate_form_name', None)
            form = form.strip().lower() if pd.notna(form) else None

            # Get correct Pokémon ID
            cur.execute("""
                SELECT id FROM pokemon
                WHERE LOWER(pokemon_name) = %s AND 
                      (alternate_form_name IS NULL AND %s IS NULL OR LOWER(alternate_form_name) = %s)
                LIMIT 1;
            """, (name, form, form))
            result = cur.fetchone()

            if not result:
                print(f"❌ Couldn't find Pokémon ID for: {name} ({form})")
                continue

            pokemon_id = result[0]

            for slot in type_slots:
                type_val = row.get(f"{slot}_type")
                if pd.notna(type_val) and isinstance(type_val, str):
                    clean_type = type_val.strip().lower()
                    type_id = type_map.get(clean_type)

                    if type_id:
                        try:
                            cur.execute("""
                                INSERT INTO pokemon_types_junction (pokemon_id, type_id, slot)
                                VALUES (%s, %s, %s)
                                ON CONFLICT DO NOTHING;
                            """, (pokemon_id, type_id, slot))

                            if name in ['flutter mane', 'incineroar']:
                                print(f"🔎 [{name.title()}] - Linked to type '{clean_type}' (slot: {slot})")
                        except Exception as e:
                            print(f"❌ Failed to link {name} to {clean_type} ({slot}): {e}")
                            raise e
                    else:
                        print(f"⚠️ Type '{clean_type}' not found in DB for {name}")

        conn.commit()
        print("✅ Pokémon types junctions inserted successfully.")

    except Exception as e:
        if conn:
            conn.rollback()
            print("⚠️ Rolled back due to error.")
        raise
    finally:
        if cur: cur.close()
        if conn: conn.close()
        print("🔒 Connection closed.")

if __name__ == "__main__":
    main()
