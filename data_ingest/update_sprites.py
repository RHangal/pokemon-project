import os
import psycopg2
from dotenv import load_dotenv

# === Load env ===
load_dotenv()
SPRITE_PATH = os.getenv("SPRITE_PATH")  # should end in "/" or "\\"

DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

# === Overrides for weird cases ===
sprite_override_map = {
    "nidoran (female)": "nidoran-f",
    "nidoran (male)": "nidoran-m",
    # add more if needed
}

# === Normalize a name to its sprite filename ===
def normalize(name):
    name = name.lower().strip()
    if name in sprite_override_map:
        return sprite_override_map[name]
    return (
        name.replace(" ", "-")
            .replace("'", "")
            .replace(".", "")
            .replace("é", "e")
    )

# === Connect to DB ===
conn = psycopg2.connect(
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT
)
cur = conn.cursor()

# === Fetch Pokémon names ===
cur.execute("SELECT id, pokemon_name, alternate_form_name FROM pokemon;")
rows = cur.fetchall()

updated = 0
missing = []

for poke_id, name, alt_form in rows:
    base = normalize(name)
    if alt_form:
        base += "-" + normalize(alt_form)

    filename = f"{base}.png"
    sprite_path = os.path.join(SPRITE_PATH, filename)

    if os.path.exists(sprite_path):
        cur.execute("""
            UPDATE pokemon
            SET sprite_path = %s
            WHERE id = %s;
        """, (sprite_path, poke_id))
        updated += 1
    else:
        missing.append(filename)

conn.commit()
cur.close()
conn.close()

# === Report ===
print(f"✅ Updated {updated} Pokémon with sprite paths.")
if missing:
    print("❌ Missing sprite files:")
    for m in missing:
        print(" -", m)

