import os
import re
from dotenv import load_dotenv
from azure.storage.blob import ContainerClient
from scripts.utils.db_utils import get_db_connection

# === Load env ===
load_dotenv()

# === Azure Blob Config ===
AZURE_CONNECTION_STRING = os.getenv("AZURE_CONNECTION_STRING")
CONTAINER_NAME = "pokemon-sprites"
BASE_URL = f"https://pokemonrgstorage.blob.core.windows.net/{CONTAINER_NAME}"

# === Normalize name for loose matching ===
def normalize(name):
    name = name.lower()
    name = re.sub(r"[^\w\s-]", "", name)
    return name.replace(" ", "").replace("-", "")

def run(cur):
    # === Step 1: Fetch all blob names ===
    container_client = ContainerClient.from_connection_string(
        conn_str=AZURE_CONNECTION_STRING,
        container_name=CONTAINER_NAME
    )
    blob_names = [blob.name for blob in container_client.list_blobs()]
    blob_map = {normalize(os.path.splitext(name)[0]): f"{BASE_URL}/{name}" for name in blob_names}

    # === Step 2: Load Pokémon from DB ===
    cur.execute("SELECT id, pokemon_name, alternate_form_name FROM pokemon;")
    rows = cur.fetchall()

    # === Step 3: Build update map ===
    updates = []

    for id, name, form in rows:
        base = normalize(name or "")
        alt = normalize(form) if form else ""
        key_exact = normalize(f"{name} {form}") if form else base

        match = blob_map.get(key_exact)
        if not match:
            match = blob_map.get(base)

        if match:
            updates.append((match, id))
        else:
            print(f"⚠️ No sprite found for: {name} ({form})")

    # === Step 4: Apply updates ===
    for url, poke_id in updates:
        cur.execute("""
            UPDATE pokemon
            SET sprite_path = %s
            WHERE id = %s;
        """, (url, poke_id))

    print(f"✅ Updated {len(updates)} Pokémon with sprite URLs.")
