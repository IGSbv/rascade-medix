import os
from pymongo import MongoClient
from typing import Dict
from dotenv import load_dotenv

# --- Load environment variables ---
project_root = os.path.join(os.path.dirname(__file__), '..')
dotenv_path = os.path.join(project_root, '.env')
load_dotenv(dotenv_path=dotenv_path)

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = "cura_db"
client, collection = None, None

if MONGO_URI:
    try:
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]
        collection = db["conversations"]
    except Exception:
        client = None

def get_dynamic_aliases() -> Dict[str, str]:
    """
    Fetches all reviewed notes starting with 'ADD ALIAS' and parses them
    into a dictionary of {new_alias: official_symptom}.
    """
    # --- THIS IS THE FIX ---
    # We must check if the collection object is not None
    if collection is None:
        return {}
    # --- END OF FIX ---

    aliases = {}
    # Find all reviewed chats that have an expert note for adding an alias
    notes_cursor = collection.find(
        {"reviewed_by_expert": True, "expert_notes": {"$regex": "^ADD ALIAS:"}},
        {"expert_notes": 1} # Only retrieve the notes field
    )

    for doc in notes_cursor:
        try:
            # Parse the note e.g., "ADD ALIAS: ear pulling -> ear pain"
            parts = doc['expert_notes'].replace("ADD ALIAS:", "").strip().split("->")
            if len(parts) == 2:
                alias = parts[0].strip().lower()
                official_name = parts[1].strip().lower()
                aliases[alias] = official_name
        except Exception:
            continue # Ignore malformed notes
    return aliases