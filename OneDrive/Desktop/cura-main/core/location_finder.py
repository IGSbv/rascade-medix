import requests
from typing import List, Dict
from utils.config import GOOGLE_PLACES_API_KEY
from utils.logger import get_logger

logger = get_logger(__name__)
PLACES_API_URL = "https://maps.googleapis.com/maps/api/place/textsearch/json"

def find_nearby_doctors(specialist: str, location: str) -> List[Dict]:
    if not GOOGLE_PLACES_API_KEY:
        logger.warning("GOOGLE_PLACES_API_KEY is not set. Skipping doctor search.")
        return []

    query = f"{specialist} near {location}"
    params = {'query': query, 'key': GOOGLE_PLACES_API_KEY, 'language': 'en'}

    try:
        logger.info(f"Searching for doctors with query: '{query}'")
        response = requests.get(PLACES_API_URL, params=params, timeout=10)
        response.raise_for_status()
        results = response.json().get('results', [])
        
        doctor_list = []
        for place in results[:5]:
            doctor_list.append({
                "name": place.get('name'),
                "address": place.get('formatted_address'),
                "rating": place.get('rating', 0.0),
                "total_ratings": place.get('user_ratings_total', 0)
            })
        
        sorted_doctors = sorted(
            doctor_list, 
            key=lambda d: d.get('rating', 0.0), 
            reverse=True
        )
        logger.info(f"Found and sorted {len(sorted_doctors)} doctors/clinics.")
        return sorted_doctors
    except Exception as e:
        logger.error(f"An unexpected error occurred calling Google Places API: {e}")
        return []