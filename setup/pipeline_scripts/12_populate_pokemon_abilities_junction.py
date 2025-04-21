import pandas as pd
from scripts.utils.db_utils import get_csv_path

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

# === Ability slot mapping ===
slot_columns = {
    'primary': 'primary_ability',
    'secondary': 'secondary_ability',
    'hidden': 'hidden_ability',
    'event': 'special_event_ability'
}

def run(cur):
    # Load ability ID map
    cur.execute("SELECT id, name FROM pokemon_ability;")
    ability_map = {name.lower(): id for id, name in cur.fetchall()}

    for _, row in df.iterrows():
        name = row.get('pokemon_name', '').strip().lower()
        form = row.get('alternate_form_name', None)
        form = form.strip().lower() if pd.notna(form) else None

        # Match Pokémon ID using name + form
        cur.execute("""
            SELECT id FROM pokemon
            WHERE LOWER(pokemon_name) = %s
                AND (alternate_form_name IS NULL AND %s IS NULL OR LOWER(alternate_form_name) = %s)
            LIMIT 1;
        """, (name, form, form))
        result = cur.fetchone()

        if not result:
            print(f"❌ Couldn't find Pokémon ID for: {name} ({form})")
            continue

        pokemon_id = result[0]

        # Insert junction entries
        for slot, col in slot_columns.items():
            ability_name = row.get(col)
            if pd.notna(ability_name) and isinstance(ability_name, str):
                clean_ability = ability_name.strip().lower()
                ability_id = ability_map.get(clean_ability)

                if ability_id:
                    try:
                        cur.execute("""
                            INSERT INTO pokemon_abilities_junction (pokemon_id, ability_id, slot)
                            VALUES (%s, %s, %s)
                            ON CONFLICT DO NOTHING;
                        """, (pokemon_id, ability_id, slot))

                        if name in ['flutter mane', 'incineroar']:
                            print(f"🔎 [{name.title()}] - Linked to ability '{clean_ability}' (slot: {slot})")
                    except Exception as e:
                        print(f"❌ Failed to link {name} → {clean_ability} ({slot}): {e}")
                        raise e
                else:
                    print(f"⚠️ Ability '{clean_ability}' not found in DB for {name}")

