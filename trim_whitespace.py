"""trim_whitespace.py
Trims whitespace in genre names, artist names, album names and comments
about albums. The OCR API often returns inconsistent whitespace characters, for example
multiple spaces, spaces in the middle of stuff, etc. etc."""
from extract_text_from_images import get_albums_data_file, write_to_albums_data_file
import logging, re
logger = logging.getLogger(__name__)
albums_data = get_albums_data_file() # Get all albums
# Define helper functions for trimming whitespace
def trim_whitespace(input_text:str)->str:
    """Trims whitespace and removes things such as double spaces from a string.

    :param input_text: The input text to process."""
    input_text = input_text.strip().strip(" ") # Fix any leading or trailing spaces
    input_text = re.sub(" {2,}", " ", input_text) # Fix any double spaces
    # Dashes, such as in singer-songwriter, often have spaces between
    # them after being OCR:d for some reason
    input_text = input_text.replace("- ", "-").replace(" -", "-")
    return input_text

if __name__ == "__main__":
    processed_albums = [] # Processed output
    total_albums = len(albums_data["album_images"])
    i = 1
    for album in albums_data["album_images"]:
        logger.info(f"Processing album {i}/{total_albums} ({album})")
        processed_album = album
        processed_album["title"] = trim_whitespace(album["title"])
        # Process artists
        processed_artists = []
        for artist in album["artist"]:
            processed_artists.append(trim_whitespace(artist))
        processed_album["artist"] = processed_artists
        # Process genres
        processed_genres = []
        for genre in album["genres"]:
            # All genres should be in lowercase. Do it here for extra convenience
            processed_genres.append(trim_whitespace(genre).lower())
        processed_album["genres"] = processed_genres
        # Process comments
        processed_album["comments"] = trim_whitespace(album["comments"])
        processed_albums.append(processed_album)
        i+=1
    # Write processed albums
    logger.info("Writing updated album data....")
    albums_data["album_images"] = processed_albums
    write_to_albums_data_file(albums_data)