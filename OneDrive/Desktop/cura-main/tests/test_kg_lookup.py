import sys
import os
from unittest.mock import patch

# --- Add project root to the Python path ---
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)
# -----------------------------------------

from core.kg_lookup import find_conditions

# A mock knowledge graph using the final "alias" structure.
MOCK_CONDITIONS = [
    {
        "name": "Influenza",
        "common_symptoms": [{"name": "fever"}, {"name": "cough"}, {"name": "fatigue"}],
        "specific_symptoms": [{"name": "body aches"}]
    },
    {
        "name": "Pneumonia",
        "common_symptoms": [{"name": "fever"}, {"name": "cough"}],
        "specific_symptoms": [{"name": "chest pain"}]
    },
    {
        "name": "Allergies",
        "common_symptoms": [{"name": "cough"}],
        "specific_symptoms": [{"name": "sneezing"}]
    }
]


def test_weighted_scoring_and_sorting():
    """
    Tests that the weighted score is calculated correctly and results are sorted.
    """
    # Use a 'with' statement to apply the patch only inside this test
    with patch('core.kg_lookup.CONDITIONS', MOCK_CONDITIONS):
        symptoms = ["cough", "fatigue", "chest pain"]
        
        # Expected scores:
        # Pneumonia: (cough=1) + (chest pain=3) = 4
        # Influenza: (cough=1) + (fatigue=1) = 2
        # Allergies: (cough=1) = 1
        
        results = find_conditions(symptoms)
        
        assert len(results) == 3
        assert results[0]["name"] == "Pneumonia"
        assert results[1]["name"] == "Influenza"
        assert results[2]["name"] == "Allergies"

def test_specific_symptom_priority():
    """
    Tests that a single specific symptom can outweigh multiple common ones.
    """
    with patch('core.kg_lookup.CONDITIONS', MOCK_CONDITIONS):
        symptoms = ["body aches"]
        results = find_conditions(symptoms)
        assert len(results) == 1
        assert results[0]["name"] == "Influenza"

def test_no_matching_conditions():
    """
    Tests that symptoms not in our mock KG return an empty list.
    """
    with patch('core.kg_lookup.CONDITIONS', MOCK_CONDITIONS):
        symptoms = ["dizziness"]
        results = find_conditions(symptoms)
        assert results == []

def test_empty_symptom_list():
    """
    Tests that an empty list of symptoms returns an empty list.
    This test does not need the patch as it shouldn't access the data.
    """
    symptoms = []
    results = find_conditions(symptoms)
    assert results == []