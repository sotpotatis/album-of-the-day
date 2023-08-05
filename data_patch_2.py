"""data_patch_2.py
Adds the "date" attribute to some really old albums that did not have this attribute present."""
import os
import warnings
from difflib import SequenceMatcher

from extract_text_from_images import get_albums_data_file, write_to_albums_data_file, PROCESSED_ALBUM_IMAGES_FOLDER, get_safe_filename
from trim_whitespace import trim_whitespace
from album_image_util.util import get_image_creation_date
import logging
from PIL import Image
logger = logging.getLogger(__name__)
albums_data = get_albums_data_file()
processed_album_files = os.listdir(PROCESSED_ALBUM_IMAGES_FOLDER)

def text_similarity(text_1:str, text_2:str)->float:
    """Since some output images had a discrepancy in things like transcription,
    characters, etc., this is a helper function to compare two texts for similarity.
    Aka. I started using a similarity-based approach to compare stuff.

    :param text_1: The first text to compare.

    :param text_2: The second text to compare."""
    return SequenceMatcher(None, text_1, text_2).ratio()

for i in range(len(albums_data["album_images"])):
    album = albums_data["album_images"][i]
    if "date" not in album:
        # Now, look if the album has a corresponding output file in the PROCESSED_ALBUM_IMAGES_FOLDER folder.
        album_filename = get_safe_filename(f"{album['artist'][0]}-{album['title']}") # Possible album filename, without suffix
        for processed_album_file in processed_album_files:
            trimmed_filename = trim_whitespace(processed_album_file)
            if trimmed_filename.startswith(album_filename) or text_similarity(trimmed_filename, album_filename) > 0.8:
                logger.info(f"Found album file for {album['title']}. Getting date...")
                # We use the album_image_util library which includes a function to extract the date
                image = Image.open(os.path.join(PROCESSED_ALBUM_IMAGES_FOLDER, processed_album_file))
                date = get_image_creation_date(image).isoformat()
                if date is not None:
                    logger.info(f"Date for {album['title']} extracted.")
                    album["date"] = date
                    albums_data["album_images"][i] = album # Update the album with the date
                    continue
        if "date" not in album:
            warnings.warn(f"Failed to find an album output image for {album['title']}. You will have to add a date manually!")
write_to_albums_data_file(albums_data)