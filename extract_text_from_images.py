"""extract_text_for_images.py
Contains helper functions for actually extracting the data from an album image.

"""
import logging
import os, json
import pathlib
import shutil
import time
from ocr_api_client.client import OCRAPIClient, Languages, OCREngines
from album_image_util.util import get_parts_of_image, save_cropped_image_parts_to_temporary_storage, parse_title, parse_genres, ImageParts, get_image_creation_date
from dotenv import load_dotenv
load_dotenv()
# Constants
ALBUMS_FOLDER = os.path.join(os.getcwd(), "album_images")
ALBUM_IMAGES_FOLDER = os.path.join(os.getcwd(), "album_images")
PROCESSED_ALBUM_IMAGES_FOLDER = os.path.join(os.getcwd(), "processed_album_images")
ALBUMS_FILE_PATH = os.path.join(os.getcwd(), "albums.json")
ocr = OCRAPIClient(os.environ["OCR_API_KEY"])

# Logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

# Helper functions
def write_to_albums_data_file(data:dict)->None:
    """Writes content to the album_images data file.

    :param data The data to write"""
    with open(ALBUMS_FILE_PATH, "w", encoding="UTF-8") as album_file:
        album_file.write(json.dumps(data, indent=True))

def get_albums_data_file()->dict:
    """Gets the content of the album_images data file and returns it as a dictionary.

    :return The album_images data file as a dictionary."""
    return json.loads(open(ALBUMS_FILE_PATH, "r", encoding="UTF-8").read())

# Corrections to genre
def apply_genre_correction(input_text:str)->str:
    """Tries to correct a genre name by using preconfigured genre corrections."""
    pass # Not applied yet

def get_safe_filename(input_filename:str)->str:
    """Removes any strange characters from a filename string, producing a filename that should not
    return any errors in a moving process or similar.

    :param input_filename: The filename that is not sanitized."""
    INVALID_CHARS = [
    "%",
    "&",
    "{",
    "}",
    "\\",
    "<",
    ">",
    "*",
    "?",
    "/",
    "$",
    "!",
    "'",
    "\"",
    ":",
    "@"] # Any characters we do not want in the filename
    output_filename = input_filename
    for replace_character in INVALID_CHARS:
        output_filename = output_filename.replace(replace_character, "")
    return output_filename
if __name__ == "__main__":
    # Create initial JSON file if not exists
    if not os.path.exists(ALBUMS_FILE_PATH):
        write_to_albums_data_file({"album_images":[]})
        logger.info("Initial JSON file for storing album_images was created.")

    if not os.path.exists(PROCESSED_ALBUM_IMAGES_FOLDER):
        os.mkdir(PROCESSED_ALBUM_IMAGES_FOLDER)
        logger.info("Created file for moving processed album_images.")

    albums_data = get_albums_data_file()
    for image_file in os.listdir(ALBUM_IMAGES_FOLDER):
        image_filepath = os.path.join(ALBUM_IMAGES_FOLDER, image_file)
        # Process the file
        cropped_image_parts = get_parts_of_image(image_filepath)
        # Create album data
        album_data = {}
        # Get when the image was created. Use the first image part in the list
        image_creation_date = get_image_creation_date(list(cropped_image_parts.values())[-1])
        album_data["date"] = str(image_creation_date)
        if image_creation_date is None:
            logger.warning(
            f"Missing image creation date for {image_filepath}! The album will not be added and has to be processed manually.")
            continue
        cropped_image_filepaths = save_cropped_image_parts_to_temporary_storage(cropped_image_parts)
        try:
                # For each part, crop and get data
                for part, filepath in cropped_image_filepaths.items():
                    response = ocr.get_text(filepath, language=Languages.SWEDISH, ocr_engine=OCREngines.OCR_ENGINE_2)
                    logger.debug(f"OCR response: {response}")
                    part_text = response["ParsedResults"][0]["ParsedText"]
                    if part == ImageParts.title:
                        output = parse_title(part_text)
                        # Process title and artist separately
                        album_data["title"] = output["title"]
                        album_data["artist"] = output["artist"]
                    else:
                        if part == ImageParts.genres:
                            output = parse_genres(part_text)
                        elif part == ImageParts.comments:
                            output = part_text
                        album_data[part] = output
                if any([value is None for value in album_data.values()]):
                    logger.warning(f"Missing values for {image_filepath}! The album will not be added and has to be processed manually.")
                    continue
        except Exception as e:
            logger.critical(f"Failed conversion for {image_filepath}: {e} The album will not be added and has to be processed manually.", exc_info=True)
            continue
        logger.info(f"Created data for an album: {album_data}.")
        # Save album data
        albums_data["album_images"].append(album_data)
        write_to_albums_data_file(albums_data)
        # Move album image
        new_image_filename = get_safe_filename( f"{album_data['artist'][0]}-{album_data['title']}{pathlib.Path(image_file).suffix}")
        new_image_filepath = os.path.join(PROCESSED_ALBUM_IMAGES_FOLDER,new_image_filename)
        shutil.move(image_filepath, new_image_filepath)
        logger.info("Waiting a little until processing next image...")
        time.sleep(0.5)