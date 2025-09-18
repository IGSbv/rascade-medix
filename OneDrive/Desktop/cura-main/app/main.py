from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import sys
import os

from fastapi.middleware.cors import CORSMiddleware
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
# --- Corrected Import Path ---
from utils.chat_recorder import record_chat

logger = get_logger(__name__)
app = FastAPI(
    title="Symptom Checker Chatbot (Stable Version)",
    description="An API that uses a reliable KG-First model for symptom analysis and records chats.",
    version="7.0.0"
)

# CORS Middleware Configuration
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class UserQuery(BaseModel):
    text: str
    location: Optional[str] = None

class ChatbotResponse(BaseModel):
    response: str

# NEW: Root endpoint to resolve 404 errors for the base URL.
@app.get("/")
async def read_root():
    return {"message": "Symptom Checker API is up and running!"}

@app.post("/diagnose", response_model=ChatbotResponse, tags=["Chatbot"])
async def diagnose(query: UserQuery):
    user_input = query.text
    user_location = query.location
    logger.info(f"Received new query: '{user_input}' | Location: {user_location}")

    if is_emergency(user_input):
        emergency_response = "Your symptoms may indicate a medical emergency. Please seek immediate medical attention or contact emergency services."
        record_chat(user_input, ["emergency"], [], emergency_response)
        return ChatbotResponse(response=emergency_response)

    normalized_symptoms = normalize_symptoms(user_input)
    if not normalized_symptoms:
        fallback_response = "I'm sorry, I couldn't identify any specific symptoms. Could you please describe them differently?"
        record_chat(user_input, [], [], fallback_response)
        return ChatbotResponse(response=fallback_response)

    conditions = find_conditions(normalized_symptoms)
    if not conditions:
        fallback_response = "Based on your symptoms, I couldn't find a specific match. It's always best to consult a doctor for an accurate diagnosis."
        record_chat(user_input, normalized_symptoms, [], fallback_response)
        return ChatbotResponse(response=fallback_response)

    top_condition = conditions[0]
    detailed_info = get_medlineplus_info(top_condition['name'])
    
    nearby_doctors = []
    if user_location and top_condition.get('specialist'):
        nearby_doctors = find_nearby_doctors(top_condition['specialist'], user_location)

    try:
        conditions_summary = ", ".join([cond['name'] for cond in conditions])
        
        doctor_info_string = ""
        if nearby_doctors:
            doctor_info_string = "\n\nBased on your location, here are some highly-rated local specialists:\n"
            for doctor in nearby_doctors:
                doctor_info_string += f"- {doctor['name']} (Rating: {doctor.get('rating', 'N/A')}/5.0)\n  Address: {doctor['address']}\n"
        
        system_message = "You are a helpful and empathetic AI medical assistant. Your role is to synthesize medical data into a clear, helpful, and safe response for the user."
        
        # CHANGED: The prompt now explicitly asks for a concise summary.
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
            raise ValueError("LLM failed to generate a response.")
            
        # Record the final, successful interaction
        record_chat(user_input, normalized_symptoms, conditions, final_response)
        
        return ChatbotResponse(response=final_response)

    except Exception as e:
        logger.error(f"Error during final response generation: {e}")
        raise HTTPException(status_code=500, detail="Internal error while generating response.")