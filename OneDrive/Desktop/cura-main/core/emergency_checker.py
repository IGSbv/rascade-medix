import json
import os
from utils.logger import get_logger

# Initialize logger
logger = get_logger(__name__)

# --- Load the Knowledge Graph ---
# Construct the path to the kg.json file relative to this script's location
# __file__ is the path to the current script (emergency_checker.py)
# os.path.dirname(__file__) is the directory of the current script (core/)
# os.path.join(..., '..', 'data', 'kg.json') goes up one level and then into data/
KG_FILE_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'kg.json')

try:
    with open(KG_FILE_PATH, 'r') as f:
        knowledge_graph = json.load(f)
    EMERGENCY_SYMPTOMS = knowledge_graph.get("emergency_symptoms", [])
    logger.info("Emergency symptoms loaded successfully.")
except FileNotFoundError:
    logger.error(f"Knowledge Graph file not found at {KG_FILE_PATH}")
    EMERGENCY_SYMPTOMS = []
except json.JSONDecodeError:
    logger.error(f"Error decoding JSON from {KG_FILE_PATH}")
    EMERGENCY_SYMPTOMS = []

def is_emergency(user_input: str) -> bool:
    """
    Checks if the user input contains any predefined emergency symptoms.

    Args:
        user_input (str): The raw text input from the user.

    Returns:
        bool: True if an emergency symptom is found, False otherwise.
    """
    if not user_input:
        return False

    # Normalize the input to lowercase for case-insensitive matching
    lower_input = user_input.lower()

    for symptom in EMERGENCY_SYMPTOMS:
        if symptom.lower() in lower_input:
            logger.warning(f"Emergency keyword found: '{symptom}' in user input.")
            return True
            
    return False

# --- Example Usage (for testing the script directly) ---
if __name__ == '__main__':
    test_input_emergency = "I have severe chest pain and headache."
    test_input_normal = "i have a cough and fever."
    
    print(f"Checking input: '{test_input_emergency}'")
    print(f"Is it an emergency? {is_emergency(test_input_emergency)}") # Should be True
    
    print("\n" + "-"*20 + "\n")
    
    print(f"Checking input: '{test_input_normal}'")
    print(f"Is it an emergency? {is_emergency(test_input_normal)}") # Should be False