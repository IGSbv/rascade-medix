import json
import os
from typing import List, Dict, Any
from utils.logger import get_logger

logger = get_logger(__name__)
KG_FILE_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'kg.json')
try:
    with open(KG_FILE_PATH, 'r', encoding='utf-8') as f:
        knowledge_graph = json.load(f)
    CONDITIONS = knowledge_graph.get("conditions", [])
    logger.info(f"Knowledge graph with {len(CONDITIONS)} conditions loaded.")
except Exception as e:
    logger.error(f"Failed to load knowledge graph: {e}")
    CONDITIONS = []

def find_conditions(normalized_symptoms: List[str]) -> List[Dict[str, Any]]:
    if not normalized_symptoms or not CONDITIONS:
        return []
    symptom_set = set(normalized_symptoms)
    scored_conditions = []
    COMMON_SYMPTOM_WEIGHT = 1
    SPECIFIC_SYMPTOM_WEIGHT = 3

    for condition_data in CONDITIONS:
        common = {s['name'] for s in condition_data.get("common_symptoms", [])}
        specific = {s['name'] for s in condition_data.get("specific_symptoms", [])}
        common_matches = len(symptom_set.intersection(common))
        specific_matches = len(symptom_set.intersection(specific))
        total_matches = common_matches + specific_matches
        
        if total_matches > 0:
            score = (common_matches * COMMON_SYMPTOM_WEIGHT) + (specific_matches * SPECIFIC_SYMPTOM_WEIGHT)
            scored_conditions.append({
                "score": score,
                "match_count": total_matches,
                "data": condition_data
            })
    
    if not scored_conditions:
        return []

    sorted_conditions = sorted(
        scored_conditions,
        key=lambda x: (x['match_count'], x['score']),
        reverse=True
    )
    top_matches = [item['data'] for item in sorted_conditions[:3]]
    if sorted_conditions:
        logger.info(f"Found {len(top_matches)} matches. Best match count: {sorted_conditions[0]['match_count']}, Score: {sorted_conditions[0]['score']}")
    return top_matches