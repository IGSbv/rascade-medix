import sys
import os
import pytest
from unittest.mock import patch

# --- Add project root to the Python path ---
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)
# -----------------------------------------

from core.symptom_normalizer import normalize_symptoms
from core.kg_lookup import find_conditions

# NOTE: These are integration tests. They use the real kg.json file
# and test the interaction between the symptom_normalizer and kg_lookup modules.

@patch('core.symptom_normalizer.get_llm_response')
def test_rheumatoid_arthritis_scenario(mock_llm_call):
    """
    Tests if the system can correctly identify Rheumatoid Arthritis by picking up
    on the key specific symptom of symmetrical pain from a conversational query.
    """
    # Arrange: Simulate the user's complex query.
    input_text = "I am exhausted all the time and my joints ache. It's weird, it's the same joints on both sides, like both of my wrists and both of my knees are very stiff and painful, especially when I first wake up."
    
    # Simulate the LLM extracting the key phrases. Your new KG has an alias for this.
    mock_llm_call.return_value = "exhausted, joints ache, pain on both sides, stiff"
    
    # Act: Run the full pipeline
    normalized = normalize_symptoms(input_text)
    results = find_conditions(normalized)
    
    # Assert: Check that RA is the top result.
    assert results, "Should have found at least one condition"
    assert results[0]["name"] == "Rheumatoid Arthritis"

@patch('core.symptom_normalizer.get_llm_response')
def test_anemia_scenario(mock_llm_call):
    """
    Tests if the weighted scoring correctly prioritizes Anemia despite the user
    emphasizing a more common symptom (headache).
    """
    # Arrange: Simulate the user's query.
    input_text = "My main problem is these awful headaches, but I've also been getting really out of breath just from climbing the stairs, and my friend said I look very pale."
    
    # Simulate the LLM extracting the key phrases.
    mock_llm_call.return_value = "headaches, out of breath, pale"
    
    # Act: Run the full pipeline
    normalized = normalize_symptoms(input_text)
    results = find_conditions(normalized)
    
    # Assert: Check that Anemia is the top result due to its higher-scoring specific symptoms.
    assert results, "Should have found at least one condition"
    assert results[0]["name"] == "Anemia"