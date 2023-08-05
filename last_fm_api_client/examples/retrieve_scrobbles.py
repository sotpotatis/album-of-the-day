"""retrieve_scrobbles.py
Example code to retrieve scrobbles.
Very useful for testing."""
from last_fm_api_client.last_fm_api_client.client import Client
from dotenv import load_dotenv
import os, logging, datetime

# Constants for testing: set if needed
SCROBBLE_USER = "coolaalbin"
SCROBBLE_START_PERIOD = datetime.datetime.now() - datetime.timedelta(days=2)
SCROBBLE_END_PERIOD = datetime.datetime.now()
# Initialize logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
# Load dotenv
load_dotenv()
client = Client(os.environ["LAST_FM_API_KEY"], os.environ["LAST_FM_API_USER_AGENT"])
logger.info("Retrieving scrobbles...")
scrobbles = client.get_scrobbles(
    SCROBBLE_USER, SCROBBLE_START_PERIOD, SCROBBLE_END_PERIOD
)
logger.info("Scrobbles retrieved.")
for scrobble in scrobbles.recenttracks.track:
    logger.info(
        f"{scrobble.date.timestamp}: Scrobbled {scrobble.name} by {scrobble.artist} on {scrobble.album.text}."
    )
logger.info(
    f"Just printed out information about {len(scrobbles.recenttracks.track)} scrobbles."
)
