"""update_daily_rotations.py
Updates the "Daily rotations" which is a list showing what I have listened to for a certain day.
"""
import time

import django

django.setup()
from website.models import DailyRotation, Album, Artist, Genre
from last_fm_api_client.client import Client, LastFMDataNotFound
from last_fm_api_client.models import RecentTrack, AlbumDetails
from typing import List, Tuple
import logging, os, datetime, pytz
import util


def update_daily_rotations():
    """update_daily_rotations.py
    Updates the "Daily rotations" which is a list showing what I have listened to for a certain day.
    """
    # Set up logging
    logger = logging.getLogger(__name__)
    # Initialize client
    last_fm_api = Client(
        os.environ["LAST_FM_API_KEY"], os.environ["LAST_FM_USER_AGENT"]
    )
    logger.info("Started the task to update daily rotations.")
    # Check if there is a daily rotation for the current day.
    # Timezone can be sent via an environment variable, Europe/Stockholm is the default
    now = datetime.datetime.now(
        tz=pytz.timezone(os.environ.get("TIMEZONE", "Europe/Stockholm"))
    )
    now_start_of_day = now.replace(hour=0, minute=1, second=1)
    now_end_of_day = now.replace(hour=23, minute=59, second=59)
    today_rotation = DailyRotation.objects.filter(day=now.date()).first()
    if today_rotation:
        logger.info("There is already a daily rotation for today. Exiting the task.")
    else:
        logger.info("Generating daily rotation for today...")
        logger.info("Retrieving scrobbles...")
        scrobble_data = last_fm_api.get_scrobbles(
            os.environ["LAST_FM_USERNAME"], now_start_of_day, now_end_of_day
        )
        logger.info("Scrobbles retrieved. Looping over...")
        # Find all albums that were scrobbled.
        # Requirement: first tracks scrobbled.
        found_album_scrobbles: List[Tuple[AlbumDetails, List[RecentTrack]]] = []
        found_tags: List[str] = []
        album_buffer: List[
            RecentTrack
        ] = []  # Store tracks with the same album before checking for an album scrobble
        album_name = None
        artist_name = None
        for track in scrobble_data.recenttracks.track:
            if track.artist.text is None or track.album.text is None:
                logger.debug(
                    f"Ignoring scrobble with empty artist or empty album name: {track}..."
                )
                continue
            if (artist_name is None and album_name is None) or (
                track.album.text == album_name and track.artist.text == artist_name
            ):
                # Avoid duplicates
                is_duplicate = False
                for buffer_track in album_buffer:
                    if buffer_track.name == track.name:
                        logger.debug(
                            f"Found duplicate scrobble {track.name}. Ignoring..."
                        )
                        is_duplicate = True
                        break
                if not is_duplicate:
                    logger.debug("Adding a track to the buffer...")
                    album_buffer.append(track)
            else:
                logger.debug(
                    f"Resetting album buffer: {track.album.text}!={album_name}, {track.artist.text}!={artist_name}"
                )
                # Check if we found an album that has been scrobbled
                logger.info(f"Checking album: {album_name}...")
                do_check = True
                try:
                    album_data = last_fm_api.get_album(artist_name, album_name)
                    time.sleep(
                        1
                    )  # Sleep a little while to avoid spamming the Last.FM API.
                except LastFMDataNotFound as e:
                    logger.info(
                        f"Found no Last.FM album for {album_name} by {artist_name}. Will be skipped!",
                        exc_info=True,
                    )
                    do_check = False
                except Exception as e:
                    logger.critical(
                        f"An unexpected error happened when retrieving detailed information for an album: {e}.",
                        exc_info=True,
                    )
                    raise e  # Raise the exception since this not expected output.
                if do_check and album_data.album.tracks is None:
                    logger.info(
                        f"Found no track data for album {album_name}. Will be skipped."
                    )
                    do_check = False
                if do_check:
                    # Now, compare the tracklist!
                    album_tracks = album_data.album.tracks.track
                    number_of_album_tracks = len(album_tracks)
                    number_of_scrobbled_tracks = len(album_buffer)
                    # Allow a 1 track discrepancy
                    logger.info(
                        f"{number_of_scrobbled_tracks} scrobbled tracks on album, {number_of_album_tracks} tracks on album."
                    )
                    if number_of_album_tracks - 1 <= number_of_scrobbled_tracks:
                        logger.info(
                            f"Detected an album scrobble for album {album_name}. Adding..."
                        )
                        found_album_scrobbles.append((album_data.album, album_buffer))
                        # Process tags
                        tags = album_data.album.tags.tag
                        if not isinstance(
                            tags, list
                        ):  # Last.FM doesn't always return a list.
                            tags = [tags]
                        for tag in tags:
                            print(tag)
                            tag_name = tag.name.lower()
                            if tag_name not in album_data:
                                logger.info(f"Found new tag: {tag_name}!")
                                found_tags.append(tag_name)
                            else:
                                logger.debug(
                                    f"Ignoring duplicate found tag: {tag_name}"
                                )
                        """
                        NOTE:
                        The following code additionally checks that album tracks were scrobbled in order. I decided to remove this because of several issues:
                        * There is, apparently a discrepancy between some track names from the scrobbles endpoint and album track names. Especially appendixes such as (Remix)
                        etc. made it somewhat difficult to compare track names properly
                        * Last.FM sometimes seems to have returned scrobbles out of order
                        That, compared with the fact that I don't shuffle albums on purpose (has happened once or twice that the button was pressed, but it's very rare) made me decide
                        to not use this code until it becomes more reliable, since the chance the above code is wrong is very low and this code risks leaving out some of the albums.
                        # Check if the album was scrobbled in order so not just a few tracks from it were played
                        # or the shuffle button was automatically pressed (I never shuffle albums and you shouldn't)
                        track_orders = []
                        # Create mapping: track name -> track order
                        track_name_to_order = {}
                        for album_track in album_tracks:
                            if album_track.attr.rank is None:
                                logger.warning(f"Track {album_track.name} on album {album_name} has no set rank. The check will be stopped!")
                                do_check = False
                                break
                            track_name_to_order[album_track.name] = album_track.attr.rank
                        if do_check:
                            logger.info("Tracklist parsed. Comparing against the buffer...")
                            # Check that the tracks were scrobbled in order
                            for buffer_track in album_buffer:
                                track_order_found = False
                                for track_name, track_order in track_name_to_order.items():
                                    if buffer_track.name.startswith(track_name) or buffer_track.name == track_name:
                                        if track_order not in track_orders: # Filter out duplicates
                                            track_orders.append(track_order)
                                        track_order_found = True
                                    if not track_order_found:
                                        logger.warning(f"Discrepancy: {buffer_track.name} not in track name to order mappings: {track_name_to_order.keys()}. The album will be skipped.")
                            # Sort everything
                            sorted_track_orders = track_orders.copy()
                            sorted_track_orders.sort()
                            track_orders.sort()
                            # We are a little nice here, since Last.fm seem to be a little inconsistent in their storage
                            if track_orders == sorted_track_orders or len(track_orders) == len(sorted_track_orders):
                                logger.info("Found a scrobbled album. Adding to the list of scrobbled albums...")
                                found_album_scrobbles.append((album_data.album, album_buffer))
                                for tag in album_data.album.tags.tag:
                                    tag_name = tag.name.lower()
                                    if tag_name not in album_data:
                                        logger.info(f"Found new tag: {tag_name}!")
                                        found_tags.append(tag_name)
                                    else:
                                        logger.debug(f"Ignoring duplicate found tag: {tag_name}")
                            else:
                                logger.warning("Ignored album from the list of scrobbled albums since there was a track order mismatch. Logging as warning to detect anomalies.")"""
                # If we get here, we should reset the buffer
                logger.info("Resetting buffer...")
                album_buffer = []
            album_name = track.album.text
            artist_name = track.artist.text
        # Now, we can parse all the albums that were scrobbled on the day and create a daily rotation.
        logger.info(
            f"Found {len(found_album_scrobbles)} scrobbled albums and {len(found_tags)} scrobbled tags for {now.date()}."
        )
        if len(found_album_scrobbles) == 0:
            logger.warning(
                "No daily scrobbles found. The task will not create a daily rotation."
            )
            exit(1)
        # Convert all albums to Django models
        albums_django = []
        # ...do the same with tags
        genres_django = []
        # Iterate over albums and tags and perform the conversion.
        # Because of the low quality of Last.FM tags, tags that are not present in the database
        # from before are simply ignored.
        # However, new albums will be created if not exists.
        for found_album, _ in found_album_scrobbles:
            logger.info(
                f"Looking for album {found_album.name} by {found_album.artist} in Django database..."
            )
            found_album_django = util.find_django_album_from_details(
                artist_names=found_album.artist, album_name=found_album.name
            )
            if found_album_django is not None:
                logger.info("Album found!")
            else:
                logger.info("Album not found in database. Creating...")
                found_album_django = util.add_album_to_database(
                    artist_names=found_album.artist, album_name=found_album.name
                )
                logger.info("Album created and added to database.")
            albums_django.append(found_album_django)
        logger.info("Albums processed. Processing tags...")
        for found_tag in found_tags:
            found_tag_django = Genre.objects.filter(name=found_tag).first()
            if found_tag_django is not None:
                logger.info(f"Found tag {found_tag} in the list of genres. Adding...")
                genres_django.append(found_tag_django)
            else:
                logger.info(
                    f"Did not find {found_tag} in the genre list. It will be skipped!"
                )
        logger.info("Tags processed. Creating daily rotation...")
        daily_rotation = DailyRotation(
            day=now.date(),
            description=None,
        )
        daily_rotation.save()
        # Add albums
        for album_django in albums_django:
            daily_rotation.albums.add(album_django)
            logger.info(f"Added album {album_django.name} to daily rotation.")
        # Add genres
        for genre_django in genres_django:
            daily_rotation.genres.add(genre_django)
            logger.info(f"Added album {genre_django.name} to daily rotation.")
        logger.info(
            f"The daily rotation for day {now.date()} has been created and saved into the database."
        )


if __name__ == "__main__":
    update_daily_rotations()
