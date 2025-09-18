import json
import os
from typing import List, Set, Dict
from core.llm_wrapper import get_llm_response
from utils.logger import get_logger
# --- Import the dynamic layer to fetch expert-added aliases ---
from core.dynamic_kg_layer import get_dynamic_aliases

logger = get_logger(__name__)
KG_FILE_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'kg.json')

# --- 1. BUILD THE STATIC ALIAS MAP (from kg.json) ---
STATIC_ALIAS_MAP: Dict[str, str] = {}
ALL_SYMPTOM_NAMES: Set[str] = set()
try:
    with open(KG_FILE_PATH, 'r', encoding='utf-8') as f:
        knowledge_graph = json.load(f)
        for condition in knowledge_graph.get("conditions", []):
            symptoms = condition.get("common_symptoms", []) + condition.get("specific_symptoms", [])
            for symptom_obj in symptoms:
                official_name = symptom_obj["name"].lower()
                ALL_SYMPTOM_NAMES.add(official_name)
                STATIC_ALIAS_MAP[official_name] = official_name # Map name to itself
                for alias in symptom_obj.get("aliases", []):
                    STATIC_ALIAS_MAP[alias.lower()] = official_name
    logger.info(f"Loaded {len(STATIC_ALIAS_MAP)} static aliases and {len(ALL_SYMPTOM_NAMES)} unique symptoms from kg.json.")
except Exception as e:
    logger.error(f"Failed to build static alias map from kg.json: {e}")

def normalize_symptoms(user_input: str) -> List[str]:
    """
    Uses an LLM to map conversational language to a known list of official symptoms,
    enhanced with a dynamic layer of expert-added aliases from a database.
    """
    if not ALL_SYMPTOM_NAMES:
        logger.error("The list of official symptom names is empty. Cannot normalize.")
        return []

    # --- 2. COMBINE STATIC AND DYNAMIC ALIASES ---
    logger.info("Fetching dynamic aliases from the database...")
    dynamic_aliases = get_dynamic_aliases()
    # Dynamic aliases can override static ones if there's a conflict
    combined_alias_map = {**STATIC_ALIAS_MAP, **dynamic_aliases}
    logger.info(f"Using a combined map of {len(combined_alias_map)} aliases.")
    # ----------------------------------------------

    # Create a simple list of all known aliases for the prompt
    known_aliases_list_str = ", ".join(f'"{alias}"' for alias in sorted(combined_alias_map.keys()))

    system_message = "You are an expert at mapping conversational language to official medical symptoms. Return only a JSON object."
    prompt = f"""
    Analyze the user's text and map any symptom phrases you find to the most accurate term from the provided list of known aliases.

    ### LIST OF KNOWN ALIASES:
    [{known_aliases_list_str}]
    
    ### USER TEXT:
    "{user_input}"
    
    ### TASK:
    Return a JSON object with one key, "extracted_aliases", containing a list of the best-matching aliases from the provided list.

    ### FINAL JSON OUTPUT:
    """
    
    llm_response = get_llm_response(prompt, system_message)
    if not llm_response:
        logger.warning("LLM provided no response for normalization.")
        return []

    try:
        data = json.loads(llm_response)
        extracted_aliases = data.get("extracted_aliases", [])
        if not isinstance(extracted_aliases, list):
            return []

        # --- 3. MAP EXTRACTED ALIASES TO OFFICIAL SYMPTOM NAMES ---
        normalized_symptoms: Set[str] = set()
        for alias in extracted_aliases:
            official_name = combined_alias_map.get(alias.lower())
            if official_name:
                normalized_symptoms.add(official_name)
        
        final_list = sorted(list(normalized_symptoms))
        logger.info(f"Normalization successful. Mapped to: {final_list}")
        return final_list

    except json.JSONDecodeError:
        logger.error(f"Failed to decode JSON from LLM during normalization. Response: {llm_response}")
        return []