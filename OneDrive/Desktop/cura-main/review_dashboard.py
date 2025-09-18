import os
import sys
import streamlit as st
from pymongo import MongoClient
from bson.objectid import ObjectId
from dotenv import load_dotenv

# --- Add project root to the Python path ---
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)
# -----------------------------------------
from core.llm_wrapper import get_llm_response
from utils.logger import get_logger

# --- Explicitly find and load the .env file ---
dotenv_path = os.path.join(project_root, '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path=dotenv_path)
else:
    st.error(".env file not found. Please ensure it's in the project's root directory.")
    st.stop()
# ---------------------------------------------

# --- Configuration and Database Connection ---
logger = get_logger(__name__)
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = "cura_db"

def get_db_collection():
    """Establishes connection to MongoDB and returns the collection object."""
    if not MONGO_URI:
        st.error("MONGO_URI environment variable not set. Please configure it in your .env file.")
        return None
    try:
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]
        return db["conversations"]
    except Exception as e:
        st.error(f"Failed to connect to MongoDB: {e}")
        return None

def generate_ai_notes(chat: dict) -> str:
    """Uses an LLM to analyze a conversation and suggest actionable notes."""
    logger.info(f"Generating AI notes for conversation ID: {chat['_id']}")
    # ... (rest of the function remains the same)
    system_message = "You are an expert medical data analyst..." # Abbreviated for clarity
    prompt = f"""
    Please analyze the following conversation...
    - User Input: "{chat.get('user_input', 'N/A')}"
    ...
    """ # Abbreviated for clarity
    ai_note = get_llm_response(prompt, system_message)
    return ai_note if ai_note else "AI analysis failed or returned no response."

# --- Main Dashboard UI ---
st.set_page_config(layout="wide")
st.title("🤖 Cura Chatbot: Expert Review Dashboard")
st.markdown("Review user conversations to find gaps and improve the knowledge graph.")

collection = get_db_collection()

if collection is not None:
    st.sidebar.header("Filter Conversations")
    review_status = st.sidebar.radio("Select Review Status", ('Unreviewed', 'Reviewed', 'All'))
    query = {}
    if review_status == 'Unreviewed': query = {"reviewed_by_expert": False}
    elif review_status == 'Reviewed': query = {"reviewed_by_expert": True}
    conversations = list(collection.find(query).sort("timestamp", 1))

    if not conversations:
        st.warning(f"No {review_status.lower()} conversations found.")
    else:
        for chat in conversations:
            chat_id = chat["_id"]
            with st.container():
                st.markdown("---")
                col1, col2 = st.columns([2, 1])
                with col1:
                    # ... (Code to display conversation and delete button remains the same)
                    st.markdown(f"**Conversation ID:** `{chat_id}`")
                    st.text_area("User Query", chat.get("user_input"), height=100, key=f"user_{chat_id}")
                    st.text_area("Bot's Reply", chat.get("bot_response"), height=200, key=f"bot_{chat_id}")
                    if st.button("Delete Conversation", key=f"delete_{chat_id}", type="primary"):
                        collection.delete_one({"_id": ObjectId(chat_id)})
                        st.success(f"Conversation {chat_id} has been deleted.")
                        st.rerun()

                with col2:
                    st.subheader("System Analysis")
                    st.json(chat.get("analysis", {}))
                    st.subheader("Expert Actions")

                    # --- NEW: Added instructions inside an expander ---
                    with st.expander("Show Note Formatting Instructions"):
                        st.markdown("""
                        **Please use one of the following formats for your notes:**
                        - **To add a new alias for a symptom:**
                          `ADD ALIAS: your alias -> official symptom name`
                          *Example: `ADD ALIAS: ear pulling -> ear pain`*
                        - **To flag a bot's response for a condition:**
                          `FLAG RESPONSE: Condition Name -> Your feedback`
                          *Example: `FLAG RESPONSE: Common Cold -> The bot's tone was too alarming.`*
                        - **To add a new symptom for future KG updates:**
                          `ADD SYMPTOM: Condition Name -> new symptom description`
                          *Example: `ADD SYMPTOM: Gout -> sudden, severe attacks of pain, typically in the big toe`*
                        """)
                    # --- END OF NEW CODE ---

                    if st.button("🤖 Generate AI Notes", key=f"gen_notes_{chat_id}"):
                        st.session_state[f"notes_{chat_id}"] = generate_ai_notes(chat)
                    
                    notes = st.text_area("Add or Edit Review Notes", key=f"notes_{chat_id}", 
                                         placeholder="Click 'Generate AI Notes' or write notes using the format above.",
                                         height=150)

                    if st.button("Mark as Reviewed & Save Notes", key=f"review_{chat_id}"):
                        collection.update_one(
                            {"_id": ObjectId(chat_id)},
                            {"$set": {"reviewed_by_expert": True, "expert_notes": notes}}
                        )
                        st.success(f"Conversation {chat_id} marked as reviewed.")
                        st.rerun()