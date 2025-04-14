import os
import pandas as pd
import psycopg2
from dotenv import load_dotenv

# === Load environment variables ===
load_dotenv()

CSV_PATH = os.getenv("COMP_USAGE_CSV_PATH")

DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

# === Helper to convert usage values ===
def parse_usage(val):
    return float(val) if val != "NoUsage" and pd.notna(val) else None

# === Name overrides for proper matching ===
override_name_map = {
    "tapu-koko": "tapu koko",
    "tapu-lele": "tapu lele",
    "tapu-bulu": "tapu bulu",
    "tapu-fini": "tapu fini",
    "mr-mime": "mr. mime",
    "mr-rime": "mr. rime",
    "mime-jr": "mime jr.",
    "ho-oh": "ho-oh",
    "type-null": "type: null",
    "walking-wake": "walking wake",
    "iron-hands": "iron hands",
    "chien-pao": "chien-pao",
    "ting-lu": "ting-lu",
    "wo-chien": "wo-chien",
    "flutter-mane": "flutter mane",
    "sandy-shocks": "sandy shocks",
    "slither-wing": "slither wing",
    "roaring-moon": "roaring moon",
    "great-tusk": "great tusk",
    "brute-bonnet": "brute bonnet",
    "scream-tail": "scream tail",
    "raging-bolt": "raging bolt",
    "gouging-fire": "gouging fire",
    "chi": "chi-yu",
    "farfetchd": "farfetch'd",
    "sirfetchd": "sirfetch'd",
    "jangmo": "jangmo-o",
    "hakamo": "hakamo-o",
    "kommo": "kommo-o",
    "nidoranf": "nidoran (female)",
    "nidoranm": "nidoran (male)"
}

# === Load CSV ===
usage_df = pd.read_csv(CSV_PATH)
usage_df.columns = usage_df.columns.str.strip().str.lower().str.replace(" ", "_").str.replace("-", "_")
usage_df.rename(columns={"name": "usage_label"}, inplace=True)

usage_cols = [col for col in usage_df.columns if "smogon_vgc_usage" in col or "worlds_vgc_usage" in col]
usage_df = usage_df[["usage_label"] + usage_cols]

# Normalize base names with override support
def normalize_base(label):
    label = label.strip().lower()
    return override_name_map.get(label, label.split("-")[0])

usage_df["base_name"] = usage_df["usage_label"].apply(normalize_base)

# === Connect to PostgreSQL ===
conn = psycopg2.connect(
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT
)
cur = conn.cursor()

# === Load Pokémon table live ===
cur.execute("SELECT id, pokemon_name, alternate_form_name FROM pokemon;")
pokemon_rows = cur.fetchall()

pokemon_df = pd.DataFrame(pokemon_rows, columns=["id", "pokemon_name", "alternate_form_name"])
pokemon_df["base_name"] = pokemon_df["pokemon_name"].str.lower()

# === Match by base name and row order ===
matched_rows = []
fallback_count = 0
skipped_names = []

for name, usage_group in usage_df.groupby("base_name"):
    poke_group = pokemon_df[pokemon_df["base_name"] == name]

    usage_group = usage_group.reset_index(drop=True)
    poke_group = poke_group.reset_index(drop=True)

    if len(poke_group) == 0:
        print(f"❌ Skipping '{name}' — no match found in DB")
        skipped_names.append(name)
        continue

    if len(usage_group) != len(poke_group):
        print(f"⚠️ Mismatch for '{name}' ({len(usage_group)} vs {len(poke_group)}), defaulting to index 0")

    for i in range(len(usage_group)):
        row = usage_group.loc[i]

        if i < len(poke_group):
            pokemon_id = int(poke_group.loc[i, "id"])
        else:
            pokemon_id = int(poke_group.loc[0, "id"])  # fallback to first
            fallback_count += 1

        matched_rows.append({
            "pokemon_id": pokemon_id,
            "smogon_vgc_usage_2022": parse_usage(row.get("smogon_vgc_usage_2022")),
            "smogon_vgc_usage_2023": parse_usage(row.get("smogon_vgc_usage_2023")),
            "smogon_vgc_usage_2024": parse_usage(row.get("smogon_vgc_usage_2024")),
            "worlds_vgc_usage_2022": parse_usage(row.get("worlds_vgc_usage_2022")),
            "worlds_vgc_usage_2023": parse_usage(row.get("worlds_vgc_usage_2023")),
            "worlds_vgc_usage_2024": parse_usage(row.get("worlds_vgc_usage_2024")),
        })

# === Insert into DB ===
for entry in matched_rows:
    try:
        cur.execute("""
            INSERT INTO pokemon_competitive_usage (
                pokemon_id,
                smogon_vgc_usage_2022,
                smogon_vgc_usage_2023,
                smogon_vgc_usage_2024,
                worlds_vgc_usage_2022,
                worlds_vgc_usage_2023,
                worlds_vgc_usage_2024
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (pokemon_id) DO UPDATE SET
                smogon_vgc_usage_2022 = EXCLUDED.smogon_vgc_usage_2022,
                smogon_vgc_usage_2023 = EXCLUDED.smogon_vgc_usage_2023,
                smogon_vgc_usage_2024 = EXCLUDED.smogon_vgc_usage_2024,
                worlds_vgc_usage_2022 = EXCLUDED.worlds_vgc_usage_2022,
                worlds_vgc_usage_2023 = EXCLUDED.worlds_vgc_usage_2023,
                worlds_vgc_usage_2024 = EXCLUDED.worlds_vgc_usage_2024;
        """, (
            entry["pokemon_id"],
            entry["smogon_vgc_usage_2022"],
            entry["smogon_vgc_usage_2023"],
            entry["smogon_vgc_usage_2024"],
            entry["worlds_vgc_usage_2022"],
            entry["worlds_vgc_usage_2023"],
            entry["worlds_vgc_usage_2024"],
        ))
        # print(f"✅ Inserted: {entry['pokemon_id']}")
    except Exception as e:
        print(f"❌ Failed on ID {entry['pokemon_id']}: {e}")
        raise e

conn.commit()
cur.close()
conn.close()

# === Final Log ===
print(f"\n✅ Done! Inserted {len(matched_rows)} records.")
print(f"⚠️ Used fallback for {fallback_count} mismatched forms.")
print(f"❌ Skipped {len(skipped_names)} base names with 0 DB matches.")

