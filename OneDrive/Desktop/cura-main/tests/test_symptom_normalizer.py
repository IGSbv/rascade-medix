import sys
import os
import pytest
from unittest.mock import patch

# --- Add project root to the Python path ---
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)
# -----------------------------------------

from core.symptom_normalizer import normalize_symptoms

@patch('core.symptom_normalizer.get_llm_response')
def test_normalization_with_aliases(mock_llm_call):
    """
    Tests that raw phrases from the LLM are correctly mapped to official symptom names via aliases.
    """
    # Arrange: Simulate the LLM extracting conversational phrases.
    mock_llm_call.return_value = "lights are too bright, my head hurts, feeling queasy"
    
    # Act: Run the normalization function.
    normalized = normalize_symptoms("doesn't matter what we put here, the mock is used")
    
    # Assert: Check that the phrases were correctly mapped to their official names.
    # We use a set because the order is not guaranteed.
    assert set(normalized) == {"sensitivity to light and sound", "headache", "nausea"}

@patch('core.symptom_normalizer.get_llm_response')
def test_normalization_with_no_matches(mock_llm_call):
    # ...
    # Arrange: Use phrases that are truly not medical symptoms
    mock_llm_call.return_value = "my car is broken, my phone is dead" # <-- This is definitely not in the KG
    
    # Act
    normalized = normalize_symptoms("irrelevant")
    
    # Assert
    assert normalized == []

@patch('core.symptom_normalizer.get_llm_response')
def test_normalization_handles_messy_llm_output(mock_llm_call):
    """
    Tests that leading/trailing spaces and case differences are handled.
    """
    # Arrange
    mock_llm_call.return_value = "  Head Hurts , runny NOSE, "
    
    # Act
    normalized = normalize_symptoms("irrelevant")
    
    # Assert
    assert set(normalized) == {"headache", "runny nose"}