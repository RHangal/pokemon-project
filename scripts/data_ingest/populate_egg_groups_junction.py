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

# === Define egg group slots in CSV ===
slot_columns = {
    'primary': 'primary_egg_group',
    'secondary': 'secondary_egg_group'
}

def main():
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("BEGIN;")

        # Build egg group → id map
        cur.execute("SELECT id, name FROM pokemon_egg_groups;")
        egg_group_map = {name.lower(): id for id, name in cur.fetchall()}

        for _, row in df.iterrows():
            name = row.get('pokemon_name', '').strip().lower()
            form = row.get('alternate_form_name', None)
            form = form.strip().lower() if pd.notna(form) else None

            # Resolve Pokémon ID
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

            # Insert junction entries
            for slot, col in slot_columns.items():
                group_name = row.get(col)

                if pd.notna(group_name) and isinstance(group_name, str):
                    clean_group = group_name.strip().lower()
                    group_id = egg_group_map.get(clean_group)

                    if group_id:
                        try:
                            cur.execute("""
                                INSERT INTO pokemon_egg_groups_junction (pokemon_id, egg_group_id, slot)
                                VALUES (%s, %s, %s)
                                ON CONFLICT DO NOTHING;
                            """, (pokemon_id, group_id, slot))

                            if name in ['flutter mane', 'incineroar']:
                                print(f"🔎 [{name.title()}] - Linked to egg group '{clean_group}' (slot: {slot})")
                        except Exception as e:
                            print(f"❌ Failed to link {name} to {clean_group} ({slot}): {e}")
                            raise e
                    else:
                        print(f"⚠️ Egg group '{clean_group}' not found in DB for {name}")

        conn.commit()
        print("✅ Egg group junctions inserted successfully.")

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
