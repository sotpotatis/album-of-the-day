"""retrieve_tag.py
Example code to retrieve a tag
Very useful for testing."""
from last_fm_api_client.last_fm_api_client.client import Client
from dotenv import load_dotenv
import os, logging, datetime

# Constants for testing: set if needed
TAG_NAME = "hardcore punk"
# Initialize logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
# Load dotenv
load_dotenv()
client = Client(os.environ["LAST_FM_API_KEY"], os.environ["LAST_FM_API_USER_AGENT"])
logger.info("Retrieving tag...")
tag = client.get_tag(TAG_NAME)
logger.info(f"Tag information: {tag.tag.wiki.content}.")
