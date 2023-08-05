"""retrieve_artist_details.py
Example code to retrieve an album
Very useful for testing."""
from last_fm_api_client.last_fm_api_client.client import Client
from dotenv import load_dotenv
import os, logging

# Constants for testing: set if needed
ARTIST = "Mitski"
ALBUM_NAME = "Bug Like an Angel"
# Initialize logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
# Load dotenv
load_dotenv()
client = Client(os.environ["LAST_FM_API_KEY"], os.environ["LAST_FM_API_USER_AGENT"])
logger.info("Retrieving artist...")
album = client.get_album(ARTIST, ALBUM_NAME)
logger.info(f"Album information: name: {album.album.name}, URL: {album.album.url}.")
if album.album.tracks is not None:
    for track in album.album.tracks.track:
        logger.info(
            f"{track.attr.rank} Track {track.name} ({round(track.duration/60, 2)} minutes)"
        )
else:
    logger.warning("No track data for album found.")
logger.info(f"Tags: {album.album.tags}")
logger.info(f"Images: {album.album.image}")
