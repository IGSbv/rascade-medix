import os
from pymongo import MongoClient
from datetime import datetime
from typing import Dict, Any, List
from utils.logger import get_logger

# --- Add this to load environment variables for this module ---
from dotenv import load_dotenv
project_root = os.path.join(os.path.dirname(__file__), '..')
dotenv_path = os.path.join(project_root, '.env')
load_dotenv(dotenv_path=dotenv_path)
# ---------------------------------------------------------

logger = get_logger(__name__)

# --- Connect to MongoDB ---
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = "cura_db"

client = None
chat_collection = None

if not MONGO_URI:
    logger.warning("MONGO_URI environment variable not set. Chat recording is disabled.")
else:
    try:
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]
        chat_collection = db["conversations"]
        logger.info("MongoDB client for chat recording initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize MongoDB client: {e}")
        client = None

def record_chat(
    user_input: str,
    normalized_symptoms: List[str],
    matched_conditions: List[Dict[str, Any]],
    bot_response: str
) -> None:
    """Saves a record of the user interaction to the database."""
    if not client or chat_collection is None:
        return # Do nothing if the database isn't configured

    try:
        # Extract just the names for cleaner storage
        condition_names = [cond.get("name", "Unknown") for cond in matched_conditions]

        chat_record = {
            "timestamp": datetime.utcnow(),
            "user_input": user_input,
            "analysis": {
                "normalized_symptoms": normalized_symptoms,
                "matched_conditions": condition_names
            },
            "bot_response": bot_response,
            "feedback": None,
            "reviewed_by_expert": False,
            "expert_notes": ""
        }
        chat_collection.insert_one(chat_record)
        logger.info("Successfully recorded chat interaction to the database.")
    except Exception as e:
        logger.error(f"Failed to record chat to MongoDB: {e}")