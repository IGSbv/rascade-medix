import sys
import os
import json
import csv
from utils.logger import get_logger

# --- Add project root to the Python path ---
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)
# -----------------------------------------

logger = get_logger(__name__)

KG_FILE_PATH = os.path.join(project_root, 'data', 'kg.json')
DATASET_PATH = os.path.join(project_root, 'data', 'medical_dataset.csv')

def create_symptom_object(symptom_str: str) -> dict:
    """Helper function to create a symptom object."""
    symptom_name = symptom_str.strip()
    return {"name": symptom_name, "aliases": [symptom_name]}

def main():
    """Main function to run fully automated KG expansion from a CSV dataset."""
    logger.info("--- Starting Automated KG Expansion ---")

    try:
        with open(KG_FILE_PATH, 'r') as f:
            kg_data = json.load(f)
        existing_names = {cond['name'].lower() for cond in kg_data.get("conditions", [])}
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.error(f"Could not load kg.json: {e}. Aborting.")
        return

    try:
        with open(DATASET_PATH, 'r', newline='') as f:
            reader = csv.DictReader(f)
            dataset_rows = list(reader)
    except FileNotFoundError:
        logger.error(f"Dataset file not found at {DATASET_PATH}.")
        return

    new_conditions = []
    for row in dataset_rows:
        name = row.get('name', '').strip()
        if not name or name.lower() in existing_names:
            continue

        new_cond = {
            "name": name,
            "category": row.get('category', 'Uncategorized').strip(),
            "common_symptoms": [create_symptom_object(s) for s in row.get('common_symptoms', '').split(';') if s.strip()],
            "specific_symptoms": [create_symptom_object(s) for s in row.get('specific_symptoms', '').split(';') if s.strip()],
            "risk_factors": [rf.strip() for rf in row.get('risk_factors', '').split(';') if rf.strip()],
            "specialist": row.get('specialist', 'General Practitioner').strip(),
            "recommendation": row.get('recommendation', 'Consult a doctor.').strip(),
            "severity": row.get('severity', 'unknown').strip()
        }
        new_conditions.append(new_cond)
        existing_names.add(name.lower())

    if not new_conditions:
        logger.info("No new conditions to add from the dataset.")
        return

    print(f"\nReady to add {len(new_conditions)} new conditions:")
    for cond in new_conditions: print(f"  - {cond['name']}")
    
    if input("\nApprove and add all? (yes/no): ").lower() != 'yes':
        logger.warning("User rejected the batch update.")
        return

    kg_data["conditions"].extend(new_conditions)
    with open(KG_FILE_PATH, 'w') as f:
        json.dump(kg_data, f, indent=2)
    logger.info(f"SUCCESS: Added {len(new_conditions)} new conditions.")

if __name__ == "__main__":
    main()