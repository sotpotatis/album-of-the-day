"""update_spotify_uids.py
Updates Spotify UIDs for each album. Searches Spotify to try to find a linked album."""
import logging, django
import time

django.setup()
from website.models import Album, retrieve_and_update_spotify_uid_for_instance

# Create a logger
logger = logging.getLogger(__name__)


def update_spotify_uids():
    """Runs the task to update Spotify UIDs for all albums."""
    for album in Album.objects.all():
        logger.info(f"Running task to update Spotify UID for {album.spotify_uid}...")
        retrieve_and_update_spotify_uid_for_instance(album)
        logger.info(f"Spotify UID for album {album.spotify_uid} updated.")
        time.sleep(1)  # Avoid spamming the Last.FM API:)


if __name__ == "__main__":
    update_spotify_uids()
