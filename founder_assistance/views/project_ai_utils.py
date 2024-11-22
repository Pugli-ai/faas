from django.conf import settings
from openai import OpenAI
import logging

logger = logging.getLogger(__name__)

# Initialize OpenAI client with error handling
try:
    if not settings.OPENAI_API_KEY:
        print("[WARNING] OpenAI API key is not set in settings")
        logger.warning("OpenAI API key is not configured in settings")
        client = None
    else:
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        print("[INFO] OpenAI client configured successfully")
except Exception as e:
    print(f"[ERROR] Failed to initialize OpenAI client: {str(e)}")
    logger.error(f"Failed to initialize OpenAI client: {str(e)}")
    client = None

# Legal Assistant ID
LEGAL_ASSISTANT_ID = "asst_9YrzjgX3iqTC23uvWRPOeTZ0"

def get_openai_client():
    """Get the OpenAI client instance"""
    return client
