"""import_albums_from_json.py
Imports albums stored in a JSON file that fulfills the format provided by
extract_text_from_images.py"""
import datetime
import logging
import time
from pathlib import Path
from argparse import ArgumentParser
import os, django, json, logging

os.environ["DJANGO_SETTINGS_MODULE"] = "album_of_the_day.settings"
django.setup()  # Set up Django
from website.models import Album, AlbumOfTheDay, Genre
from website.tasks.util import (
    add_album_to_database,
    find_django_album_from_details,
    find_django_genre_from_name,
)

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)
# Set up CLI
cli = ArgumentParser()
cli.add_argument("input_file", type=Path, help="The path to the input data file.")
arguments = cli.parse_args()
if not os.path.exists(arguments.input_file):
    raise FileNotFoundError("The input file was not found")
album_json_content = json.loads(open(arguments.input_file, "r").read())
logger.info("Starting import of albums...")
for album_data in album_json_content["album_images"]:
    album_name = album_data["title"]
    album_artists = album_data["artist"]
    album_artists_text = ",".join(album_artists)
    album_genres = album_data["genres"]
    album_comments = album_data["comments"]
    album_date = datetime.datetime.strptime(album_data["date"], "%Y-%m-%d")
    logger.info(f"-->Importing {album_name} by {album_artists_text}.")
    # Double check that the album is not in the database already
    previous_album_of_the_day = AlbumOfTheDay.objects.filter(date=album_date).first()
    if previous_album_of_the_day is not None:
        logger.warning(
            f"""The album {album_name} by {album_artists_text} seem to already be in the database.
        It will not be created and will have to be created manually! Press enter to continue."""
        )
        input()
        continue
    # Figure out what album to use for the AlbumOfTheDay entry.
    database_album = find_django_album_from_details(
        album_name=album_name, artist_names=album_artists
    )
    if database_album is None:
        logger.info(f"Adding album {album_name} by {album_artists_text} to database...")
        database_album = add_album_to_database(
            artist_names=album_artists, album_name=album_name, album_genres=album_genres
        )
        logger.info("Album added.")
    else:
        logger.info(f"Found a previous album entry for {album_name} in the database.")
    # ...and finally create "the whole thing"!
    logger.info("Prerequisites retrieved. Creating album of the day entry...")
    album_of_the_day = AlbumOfTheDay(
        album=database_album,
        date=album_date,
        comments=album_comments,
        comments_source="ocr",
    )
    album_of_the_day.save()
    logger.info(
        f"-->Import done: album of the day entry for {album_name} by {album_artists_text} was added to the database."
    )
    time.sleep(1)
