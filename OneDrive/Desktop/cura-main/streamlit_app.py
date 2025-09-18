import streamlit as st
import sys
import os

# --- Add project root to the Python path ---
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)
# -----------------------------------------

from core.emergency_checker import is_emergency
from core.symptom_normalizer import normalize_symptoms
from core.kg_lookup import find_conditions
from core.external_api_client import get_medlineplus_info
from core.location_finder import find_nearby_doctors
from core.llm_wrapper import get_llm_response
from utils.logger import get_logger
from utils.chat_recorder import record_chat

logger = get_logger(__name__)

st.set_page_config(layout="wide", page_title="Cura Chatbot", page_icon="🤖")

st.title("🤖 Cura Symptom Checker Chatbot")
st.markdown("This chatbot is for informational purposes only and is not a substitute for professional medical advice.")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("Describe your symptoms..."):
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.spinner("Analyzing your symptoms..."):
        # Your chatbot logic here
        user_input = prompt
        user_location = "New York" # You can change this to a dynamic input if you want

        if is_emergency(user_input):
            emergency_response = "Your symptoms may indicate a medical emergency. Please seek immediate medical attention or contact emergency services."
            record_chat(user_input, ["emergency"], [], emergency_response)
            response = emergency_response
        else:
            normalized_symptoms = normalize_symptoms(user_input)
            if not normalized_symptoms:
                fallback_response = "I'm sorry, I couldn't identify any specific symptoms. Could you please describe them differently?"
                record_chat(user_input, [], [], fallback_response)
                response = fallback_response
            else:
                conditions = find_conditions(normalized_symptoms)
                if not conditions:
                    fallback_response = "Based on your symptoms, I couldn't find a specific match. It's always best to consult a doctor for an accurate diagnosis."
                    record_chat(user_input, normalized_symptoms, [], fallback_response)
                    response = fallback_response
                else:
                    top_condition = conditions[0]
                    detailed_info = get_medlineplus_info(top_condition['name'])
                    
                    nearby_doctors = []
                    if user_location and top_condition.get('specialist'):
                        nearby_doctors = find_nearby_doctors(top_condition['specialist'], user_location)

                    conditions_summary = ", ".join([cond['name'] for cond in conditions])
                    
                    doctor_info_string = ""
                    if nearby_doctors:
                        doctor_info_string = "\n\nBased on your location, here are some highly-rated local specialists:\n"
                        for doctor in nearby_doctors:
                            doctor_info_string += f"- {doctor['name']} (Rating: {doctor.get('rating', 'N/A')}/5.0)\n  Address: {doctor['address']}\n"
                    
                    system_message = "You are a helpful and empathetic AI medical assistant. Your role is to synthesize medical data into a clear, helpful, and safe response for the user."
                    
                    final_prompt = f"""
                    A user described their symptoms: "{user_input}"
                    Possible conditions are: {conditions_summary}.
                    Detailed information about the most likely condition, '{top_condition['name']}':
                    ---
                    {detailed_info or "No detailed information was available."}
                    ---
                    Synthesize this into a *brief and concise* conversational response. Limit your response to *three to four sentences*, focusing on the most likely condition and a single recommendation.
                    
                    Follow these guidelines:
                    1. Start with an empathetic acknowledgment.
                    2. Present the most likely condition and a brief summary of the information.
                    3. If doctors are available, include this text EXACTLY: {doctor_info_string}
                    4. You MUST end with this mandatory safety disclaimer:
                       "This information is for educational purposes only and not medical advice. Consult a qualified healthcare provider for a diagnosis."
                    """
                    
                    final_response = get_llm_response(final_prompt, system_message)
                    if not final_response:
                        final_response = "I am having trouble generating a response right now. Please try again later."
                        
                    record_chat(user_input, normalized_symptoms, conditions, final_response)
                    response = final_response

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.markdown(response)
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})