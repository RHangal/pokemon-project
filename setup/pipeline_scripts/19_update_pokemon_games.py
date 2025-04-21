import pandas as pd
import re
import unicodedata
from scripts.utils.db_utils import get_csv_path

# === Normalize function (basic text normalization) ===
def normalize(text):
    if not isinstance(text, str):
        return ""
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("utf-8")  # remove non-ascii
    text = text.replace("\xa0", " ")  # replace non-breaking spaces
    text = re.sub(r"[^\w\s]", "", text.lower())  # remove punctuation
    return text.strip()

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

def run(cur):
    # Load and normalize all game names from DB
    cur.execute("SELECT id, game_name FROM pokemon_games;")
    game_rows = cur.fetchall()
    game_entries = [(gid, normalize(name)) for gid, name in game_rows]

    for _, row in df.iterrows():
        pokemon_id = int(row["pokemon_id"])
        raw_game = row.get("game(s)_of_origin")

        if not raw_game or pd.isna(raw_game):
            print(f"⚠️ Missing game for {row['pokemon_name']}")
            continue

        game_key = normalize(raw_game)

        # Match if all words in game_key are in game name
        keywords = game_key.split()
        matches = [
            (gid, gname) for gid, gname in game_entries
            if all(word in gname for word in keywords)
        ]

        if matches:
            matches.sort(key=lambda x: x[0])  # lowest ID wins
            game_id = matches[0][0]

            cur.execute("""
                UPDATE pokemon
                SET game_id = %s
                WHERE pokemon_id = %s;
            """, (game_id, pokemon_id))

            print(f"✅ Linked {row['pokemon_name']} → {raw_game} → {matches[0][1]} (ID: {game_id})")
        else:
            print(f"❌ No match for {row['pokemon_name']} → '{raw_game}'")

