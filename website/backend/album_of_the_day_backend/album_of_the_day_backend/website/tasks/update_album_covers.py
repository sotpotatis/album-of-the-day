"""update_album_covers.py
Updates the album covers of all albums in the database."""
import time
import django, logging

django.setup()
from website.models import Album, retrieve_and_update_cover_url_for_instance

# Create logger
logger = logging.getLogger(__name__)


def update_album_covers():
    """Updates album covers for all albums in the database."""
    logger.info("Updating all album covers...")
    for album in Album.objects.all():
        logger.info(f"Running retrieval function for album {album.name}...")
        retrieve_and_update_cover_url_for_instance(album)
        logger.info(f"Cover for {album.name} updated.")
        time.sleep(1)  # Avoid spamming the Last.FM API:)


if __name__ == "__main__":
    update_album_covers()
