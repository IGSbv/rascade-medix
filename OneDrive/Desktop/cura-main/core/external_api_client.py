import requests
import xml.etree.ElementTree as ET
from typing import Optional
from utils.logger import get_logger

logger = get_logger(__name__)
MEDLINE_API_URL = "https://wsearch.nlm.nih.gov/ws/query"

def get_medlineplus_info(disease_name: str) -> Optional[str]:
    params = {'db': 'healthTopics', 'term': disease_name}
    try:
        logger.info(f"Querying MedlinePlus for: '{disease_name}'")
        response = requests.get(MEDLINE_API_URL, params=params, timeout=10)
        response.raise_for_status()
        root = ET.fromstring(response.content)
        summary_element = root.find(".//content[@name='FullSummary']")
        
        if summary_element is not None and summary_element.text:
            summary = summary_element.text.strip()
            if summary.startswith("<![CDATA[") and summary.endswith("]]>"):
                summary = summary[9:-3].strip()
            logger.info(f"Successfully fetched summary for '{disease_name}'.")
            return summary
        else:
            logger.warning(f"No 'FullSummary' found for '{disease_name}' in MedlinePlus response.")
            return None
    except Exception as e:
        logger.error(f"An error occurred while calling or parsing MedlinePlus API: {e}")
        return None