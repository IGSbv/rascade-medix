import sys
import os
import pytest

# --- Add project root to the Python path ---
# This allows us to import from the 'core' module
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)
# -----------------------------------------

from core.emergency_checker import is_emergency

def test_emergency_symptoms_are_detected():
    """
    Tests that inputs containing keywords from the emergency list return True.
    """
    emergency_inputs = [
        "I have severe chest pain.",
        "My father is having seizures.",
        "There is severe bleeding from the wound.",
        "I am having difficulty breathing."
    ]
    for text in emergency_inputs:
        assert is_emergency(text) is True, f"Failed to detect emergency in: '{text}'"

def test_normal_symptoms_are_not_emergencies():
    """
    Tests that inputs with non-emergency keywords return False.
    """
    normal_inputs = [
        "I have a cough and a fever.",
        "My nose is runny and I'm sneezing.",
        "I just feel tired.",
        "My muscles are aching."
    ]
    for text in normal_inputs:
        assert is_emergency(text) is False, f"Incorrectly flagged normal symptom in: '{text}'"

def test_edge_cases():
    """
    Tests edge cases like empty or irrelevant strings.
    """
    assert is_emergency("") is False, "Empty string should not be an emergency."
    assert is_emergency("   ") is False, "Whitespace string should not be an emergency."
    assert is_emergency("The quick brown fox jumps over the lazy dog.") is False, "Irrelevant text should not be an emergency."