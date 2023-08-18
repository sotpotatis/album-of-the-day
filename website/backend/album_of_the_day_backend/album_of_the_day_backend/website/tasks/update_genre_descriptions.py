"""update_genre_descriptions.py
Updates the genre descriptions based on online metadata.
"""
import time

import django

django.setup()
from website.models import Genre
from last_fm_api_client.client import Client, LastFMDataNotFound
import logging, os, re

LAST_FM_GENRE_DESCRIPTION_FILTER_REGEX = re.compile("([\s\S]+)Read more([\s\S]*)")


def update_genre_descriptions():
    """Updates the descriptions for all genres in the database based on online metadata."""
    # Set up logging
    logger = logging.getLogger(__name__)
    # Initialize client
    last_fm_api = Client(
        os.environ["LAST_FM_API_KEY"], os.environ["LAST_FM_USER_AGENT"]
    )
    logger.info("Getting genres...")
    genres = Genre.objects.all()
    logger.info("Genres retrieved. Updating description.")
    for genre in genres:
        try:
            tag_data = last_fm_api.get_tag(genre.name)
            tag_description = tag_data.tag.wiki.content
            # Strip the last disclaimer part of the tag description
            if "Read more" in tag_description:
                logger.info("Stripping off the read more part...")
                tag_description = (
                    re.search(LAST_FM_GENRE_DESCRIPTION_FILTER_REGEX, tag_description)
                    .group(1)
                    .strip()
                    .strip(".")
                )
            else:  # We expect Last.FM to return a disclaimer, so mark anomalies
                logger.warning(
                    f'Did not find "Read more"-part in tag {tag_description}. This is logged as a warning to detect anomalies since it is not expected.'
                )
            logger.info(f"New description: {tag_description}.")
            if tag_description != genre.description:
                logger.info(f"Found a new description for {genre.name}. Updating...")
                genre.description = tag_description
                genre.description_source = "last_fm"
                genre.save()
                logger.info(
                    f"Successfully updated the description in the database for genre {genre.name}."
                )
            else:
                logger.info(
                    f"Description for genre {genre} is identical. No update will be performed."
                )
        except LastFMDataNotFound as e:
            logger.info(
                f"Found no Last.FM description for {genre.name}. Will be skipped!",
                exc_info=True,
            )
        except Exception as e:
            logger.critical(
                f"An unexpected error happened when retrieving or updating a genre description: {e}.",
                exc_info=True,
            )
            raise e  # Raise the exception since this not expected output.
        time.sleep(1)  # Avoid spamming the Last.FM API:)


if __name__ == "__main__":
    update_genre_descriptions()
