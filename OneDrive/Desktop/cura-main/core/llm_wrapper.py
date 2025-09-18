import openai
from typing import Optional
from utils.config import OPENAI_API_KEY
from utils.logger import get_logger

# Initialize logger
logger = get_logger(__name__)

# Initialize client to None to ensure it always exists
client = None

if not OPENAI_API_KEY:
    logger.error("OPENAI_API_KEY environment variable not found.")
else:
    try:
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        logger.info("OpenAI client initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize OpenAI client: {e}")
        client = None


def get_llm_response(prompt: str, system_message: str = "You are a helpful assistant.") -> Optional[str]:
    """
    Sends a prompt to the LLM and returns the response.

    Args:
        prompt (str): The user's prompt to send to the LLM.
        system_message (str): The system message to set the LLM's behavior.

    Returns:
        str | None: The text content of the LLM's response, or None if an error occurred.
    """
    if not client:
        logger.error("OpenAI client is not initialized. Cannot get LLM response.")
        return None

    try:
        logger.info(f"Sending prompt to LLM: '{prompt[:80]}...'") # Log a snippet
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ],
            temperature=0.0,
            # --- THIS IS THE FIX ---
            # Increased from 100 to 400 to allow for longer, more detailed responses.
            max_tokens=1000
            # --- END OF FIX ---
        )
        
        content = response.choices[0].message.content
        logger.info("LLM response received successfully.")
        return content.strip()

    except Exception as e:
        logger.error(f"An error occurred while calling the OpenAI API: {e}")
        return None