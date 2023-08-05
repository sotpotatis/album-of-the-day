"""retrieve_artist_details.py
Example code to retrieve artist details.
Very useful for testing."""
from last_fm_api_client.last_fm_api_client.client import Client
from dotenv import load_dotenv
import os, logging, datetime

# Constants for testing: set if needed
ARTIST = "mentalt syk"
# Initialize logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
# Load dotenv
load_dotenv()
client = Client(os.environ["LAST_FM_API_KEY"], os.environ["LAST_FM_API_USER_AGENT"])
logger.info("Retrieving artist...")
artist = client.get_artist(ARTIST)
logger.info(
    f"Artist information: name: {artist.artist.name}, URL: {artist.artist.url}, biography: {artist.artist.bio.content}."
)
logger.info(f"Tags: {artist.artist.tags}")
