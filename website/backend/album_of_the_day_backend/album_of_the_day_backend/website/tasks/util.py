"""utilities.py
Includes various utilities, such as converting Last.FM
responses to Django models."""
from website.models import Album, Artist, Genre
from difflib import SequenceMatcher
from typing import Optional, Union, List
import logging

logger = logging.getLogger(__name__)


def check_text_similarity(text_1: str, text_2: str) -> float:
    """Check how similar texts are to each other.

    :param text_1: The first text to check.

    :param text_2: The second text to check."""
    return SequenceMatcher(None, text_1, text_2).ratio()


def check_texts_similar(text_1: str, text_2: str, threshold: float) -> bool:
    """This function checks if the similarity is enough based on a threshold that educated guesses think is the golden number.

    :param text_1: The first text to check.

    :param text_2: The second text to check.

    :param threshold: The threshold to use for when texts should be considered to be similar.
    """
    similarity = check_text_similarity(text_1, text_2)
    if similarity == 1:
        logger.info(f"Similarity check for {text_1} and {text_2} passed - is identical")
    elif (
        similarity >= threshold
    ):  # Educated guesses think that this is the golden number.
        logger.warning(
            f"Matched {text_1} and {text_2} with some similarity (similarity {similarity}), but not 100%. Still enough in threshold for match."
        )
    else:
        logger.info(
            f"Matched {text_1} and {text_2}  with too low similarity. (similarity {similarity})"
        )
        return False
    return True


def check_artist_name_similar(text_1: str, text_2: str) -> bool:
    """Checks if two artist names are similar enough to be considered the same artist.
    Simply a shortcut call to check_texts_similar that is based on a golden number for artist name similarity.
    This number is based on educated guesses. See the notes in find_django_album_from_details for more information about threshold
    checks.

    :param text_1: The first text to check.

    :param text_2: The second text to check."""
    return check_texts_similar(
        text_1, text_2, 0.85
    )  # 0.85 is the (current) golden similarity number for artist names


def check_genre_name_similar(text_1: str, text_2: str) -> bool:
    """Checks if two genre names are similar enough to be considered the same genre.
    Simply a shortcut call to check_texts_similar that is based on a golden number for genre name similarity.
    This number is based on educated guesses. See the notes in find_django_album_from_details for more information about threshold
    checks. (the information is related to artist names, but you should get the idea

    :param text_1: The first text to check.

    :param text_2: The second text to check."""
    return check_texts_similar(
        text_1, text_2, 0.9
    )  # 0.9 is the (current) golden similarity number for genre names


def find_django_album_from_details(
    artist_names: Union[str, List[str]], album_name: str
) -> Optional[Album]:
    """Searches for an album in the database based on its name and artist name.

    :param artist_name The artist behind the album. Pass a list to check for multiple artists

    :param album_name The name of the album"""
    logger.info(
        f"Looking in the database for an album named {album_name} by {artist_names}"
    )
    albums = Album.objects.filter(name=album_name)
    if len(albums) < 1:
        logger.info("Found no album with the requested details.")
        return None
    else:
        logger.info(
            f"Found {len(albums)} album(s) with the requested details. Comparing artists..."
        )
        for album in albums:
            for artist in album.artists.all():
                for artist_name in artist_names:
                    similar = check_text_similarity(artist.name, artist_name)
                    # NOTE:
                    # I am using a similarity-based comparison because there might be a discrepancy in input artists.
                    # For example, if Last.FM wants to write it as "Jenny Hval feat. Susanna" rather than "Jenny Hval & Susanna",
                    # I want both to match the same artist. If this is a good approach or if it will lead to bad tagging
                    # will be told by time, but I don't think it will. This approach will also hopefully catch spelling errors.
                    # NOTE 2:
                    # It is very unlikely that the same artist has created two albums with the same name but with different featured
                    # artists. It is more likely that the data simply is wrong. Therefore, as long one artist is similar (even when using
                    # multiple artists), data is returned.
                    if similar:
                        return album
        logger.info("Artist in found albums compared, but no matches were found.")
        return None


def find_django_genre_from_name(genre_name: str) -> Optional[Genre]:
    """Tries to find a Django genre based on an input name.
    Like the function find_django_album_from_details, this function applies a similarity-based approach.

    :param genre_name: The name of the genre to look for."""
    logger.info(f"Looking for genre {genre_name} in the database...")
    # NOTE: Here, we get all genres rather than search for a genre.
    # Why? To make sure that "punk rock", "punkrock" and "punk-rock" matches.
    # Could rely on search, but this feels homey and safe. Like the open arms
    # of that small village that you end up in when driving down country roads.
    # Been a while since I got a comment like that into my source code! <3
    all_genres = Genre.objects.all()
    for genre in all_genres:
        if check_genre_name_similar(genre.name, genre_name):
            logger.info(f"Found {genre_name} in the database: {genre}. Returning...")
            return genre
    logger.info("All genres iterated over, but no matches were found.")
    return None


def find_django_artist_from_name(artist_name: str) -> Optional[Artist]:
    """Tries to find a Django artist based on an input name.
    Like the function find_django_album_from_details, this function applies a similarity-based approach.

    :param artist_name: The name of the artist to look for."""
    all_artists = Artist.objects.all()
    for artist in all_artists:
        if check_artist_name_similar(artist.name, artist_name):
            logger.info(
                f"Found artist {artist_name} in the database: {artist}. Returning..."
            )
            return artist
    logger.info("All artists iterated over, but no matches were found.")
    return None


def add_album_to_database(
    artist_names: Union[str, List[str]],
    album_name: str,
    album_genres: Optional[List[str]] = None,
) -> Album:
    """Adds a new album to the database.


    :param artist_names: The name of the album artist. For multiple artists, pass a list of artists.

    :param album_name: The name of the album.

    :param album_genres: Optional: Genres to add to the album."""
    logger.info(f"Creating {album_name} by {artist_names} in the database...")
    # Create a list of artists to use
    logger.info("Getting artists for album...")
    if isinstance(artist_names, str):
        artist_names = [artist_names]
    artists_to_use = []
    for artist_name in artist_names:
        # Try to find the artist in database.
        artists = Artist.objects.filter(name__contains=artist_name)
        artist_to_use = None
        # Iterate over matches and compare similarity
        logger.info(f"Comparing {len(artists)} similar artists...")
        for similar_artist in artists:
            if check_artist_name_similar(similar_artist.name, artist_name):
                logger.info(f"Found similar artist: {artist_name}.")
                artist_to_use = similar_artist
                continue
        if not artist_to_use:
            logger.info("Creating new artist...")
            artist_to_use = Artist(name=artist_name)
            artist_to_use.save()
            logger.info(f"Added artist: {artist_to_use}")
        else:
            logger.info("Using previous album artist.")
        artists_to_use.append(artist_to_use)
    # And create a list of artists to use, but it is optional depending on if
    # the argument was passed or not
    genres_to_use = []
    if album_genres is not None:
        logger.info("Getting genres for album...")
        for genre_name in album_genres:
            database_genre = find_django_genre_from_name(genre_name)
            if database_genre is None:
                logger.info(f"Adding genre {genre_name} to database...")
                database_genre = Genre(name=genre_name)
                database_genre.save()
                logger.info("Genre saved in database.")
            else:
                logger.info(f"Found existing genre for name {genre_name}.")
            genres_to_use.append(database_genre)
    logger.info("Adding album to database...")
    new_album = Album(name=album_name)
    new_album.save()
    logger.info("Album was saved in database. Adding artists to album...")
    for artist_to_use in artists_to_use:
        new_album.artists.add(artist_to_use)
        logger.info(f"Added artist {artist_to_use} to the album.")
    if len(genres_to_use) > 0:
        logger.info("Adding genres to album...")
        for genre_to_use in genres_to_use:
            new_album.genres.add(genre_to_use)
            logger.info(f"Added genre {genre_to_use} to the album.")
    return new_album  # Return the album that was created.
