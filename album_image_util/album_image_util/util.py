"""album_image_util.py
Utility to do things like crop story images for OCR, strip titles, etc."""
import datetime
import logging
import math
import os
import statistics
import textwrap
from typing import Dict, List, Union, Optional, Tuple
from PIL import Image, ImageColor, ImageDraw, ImageFont
from PIL.Image import Image as ImageType
from PIL.ImageFont import FreeTypeFont
from PIL.ImageDraw import ImageDraw
from PIL.ExifTags import TAGS as EXIF_TAGS
import tempfile
from string import ascii_letters
# Logger


logger = logging.getLogger(__name__)

# Define exceptions



class ParsingException(Exception):
    pass


# Other constants
IMAGE_SIZE = (828, 1792) # Required image size - same for all images
ALPHABET = ascii_letters + "ÅåÄäÖö" # Add Swedish letters
BLACK_COLOR = ImageColor.getrgb("black")
# Statics for image part naming - see below for usage
class ImageParts:
    title = "title"
    genres = "genres"
    comments = "comments"

# For cropping images or knowing where the different parts in an image is,
# the constants below offer help!
CROP_INFORMATION = {  # Mapping: part of image --> (left, top, right, bottom) crop coordinates
    ImageParts.title: (0, 205, IMAGE_SIZE[0], 405),
    ImageParts.genres: (495, 470, IMAGE_SIZE[0], 965),
    ImageParts.comments: (0, 1064, IMAGE_SIZE[0], IMAGE_SIZE[1])
}
ALBUM_IMAGE_BASE_CROP_SIZE = 300 # The base size to try cropping album images to
ALBUM_IMAGE_CROP_PARTS = (65, 500, 65+ALBUM_IMAGE_BASE_CROP_SIZE, 500+ALBUM_IMAGE_BASE_CROP_SIZE) # Same as CROP_INFORMATION but for adding an album cover.
FONT_SIZES = { # Font sizes (start font size, mimimum font size) for each part of image (used when creating images, see below)
    ImageParts.title: [50, 20],
    ImageParts.genres: [30, 15],
    ImageParts.comments: [25, 15]
}
def get_parts_of_image(input_image_filepath:str)->Dict[str, Image.Image]:
    """Function to extract the three main content parts of an input image.

    :param input_image_filepath: A filepath to the input image to read data from.

    :returns A dictionary mapping of image type --> Pillow Image.Image object."""
    with Image.open(input_image_filepath) as input_image:
        # Ensure the image size is correct
        if input_image.size != IMAGE_SIZE:
            raise ParsingException(f"Image file size discrepancy: input image size {input_image.size} is not equal to required size {IMAGE_SIZE}.")
        # Split image into different parts
        cropped_images = {}
        for part_to_crop, cropping_details in CROP_INFORMATION.items(): # Crop each part
            cropped_images[part_to_crop] = input_image.crop(cropping_details)
        return cropped_images # Return the cropped images

def save_cropped_image_parts_to_temporary_storage(cropped_image_parts:Dict[str, Image.Image])->Dict[str,str]:
    """Function to save a dictionary of cropped image parts to a temporary file.

    :param cropped_image_parts: The return from get_parts_of_image().

    :returns  A dictonary mapping of image type -> image temporary filepath where the image is accessible"""
    cropped_image_paths = {}
    for cropped_part, cropped_part_image in cropped_image_parts.items():
        cropped_part_temporary_file = tempfile.mktemp(suffix=".jpeg")
        cropped_part_image.save(cropped_part_temporary_file)
        cropped_image_paths[cropped_part] = cropped_part_temporary_file
    return cropped_image_paths

def delete_cropped_image_temporary_files(cropped_image_paths:Dict[str, str])->None:
    """Function to delete temporarily saved images that might have been saved by using save_cropped_image_parts_to_temporary_storage().

    :param cropped_image_paths: Return from save_cropped_image_parts_to_temporary_storage() containing image types and paths."""
    for cropped_image_path in cropped_image_paths.values():
        os.remove(cropped_image_path)


def strip_text(text):
    return text.strip().replace("\r", " ").replace("\n",  " ").strip().strip("\r").strip("\n")

def parse_title(ocr_text:str)->Optional[Dict[str,Union[List,str]]]:
    """Parses a title by extracting artists etc. from it.

    :param ocr_text: The text that was received for the OCR transcription of the title."""
    if "-" not in ocr_text:
        return None
    artists_string, album_title = strip_text(ocr_text).split("-")
    artists = artists_string.split("&") # Split the artists that are featured
    return {"artist": artists, "title": album_title}


def parse_genres(ocr_text:str)->List[str]:
    """Parses album genre tags by splitting them properly

    :param ocr_text: The text that was received for the OCR transcription of the title."""
    return strip_text(ocr_text).split(",")

# Constant for the get_image_creation_date below.
# Note that all my album of the day images have been created with the same app and therefore have the exact
# same tag set, which is DateTimeOriginal
IMAGE_DATETIME_EXIF_TAG_ID = 306


def get_image_creation_date(image:Image)->Optional[datetime.date]:
    """Gets the date where an image was created.

    :param image: The input image.

    :returns A datetime of the image creation date if it could be found.."""
    exif_data = image.getexif()
    if exif_data is None: # If no exif data
        return None
    creation_time = exif_data.get(IMAGE_DATETIME_EXIF_TAG_ID) # This is the DateTime tag of the image. See https://exiv2.org/tags.html
    if creation_time is None: # If no creation time
        return None
    # Return parsed creation time
    # Also strip the seconds off, my metadata had some issues with invalid seconds
    creation_time = creation_time[:-3].strip()
    return datetime.datetime.strptime(creation_time, "%Y:%m:%d %H:%M").date()

def get_font_size_to_fit_boundaries(image_draw:ImageDraw, font_path:str, text:str, boundaries:Tuple[int,int,int,int], start_font_size:int, lower_limit:Optional[int]=None)->Tuple[Optional[int], Optional[str], Optional[FreeTypeFont]]:
    """
    Returns the font size where a font fits perfectly inside rectangle boundaries.

    :param font_to_use: The font to use in the calculation.
    :param text: The text to check boundaries with.
    :param boundaries: The boundaries to fit the text to.
    :param start_font_size: The starting font size to check the boundaries with.
    :param lower_limit: Define the lowest allowed font size."""
    if lower_limit is None:
        lower_limit = 1
    current_font_size = start_font_size
    bounding_left, bounding_top, bounding_right, bounding_bottom = boundaries #
    max_width = bounding_right - bounding_left # Get the max width from the boundaries
    max_height = bounding_bottom - bounding_top
    logger.debug(f"Attempting to find font size for boundaries: {boundaries}. Max height is {max_height}, max width is {max_width}")
    while True:
        font_to_use = ImageFont.truetype(font_path, current_font_size)
        # First, calculate the average length for each character to figure out how much text
        # we can fit on one line. Thank you https://www.alpharithms.com/fit-custom-font-wrapped-text-image-python-pillow-552321/
        # for this tip
        character_average_size = statistics.mean(font_to_use.getlength(character) for character in ALPHABET)
        logger.debug(f"Average character size for font size {current_font_size}: {character_average_size}.")
        text_multiline = textwrap.fill(text=text, width=math.floor(max_width / character_average_size)) # Split the input text to fit
        # Then, we get the bounding box for the text and start fitting it horizontally
        text_left, text_top, text_right, text_bottom = image_draw.multiline_textbbox(xy=(0,0), font=font_to_use, text=text_multiline) # Returns left, top, right, bottom coordinates
        text_height = text_bottom - text_top
        text_width = text_right - text_left
        logger.debug(f"Text height: {text_height}, width {text_width}.")
        if text_height > max_height: # If we need to shrink the text even more
            if current_font_size - 1 <= lower_limit: # If we got past the minimum limit
                return None, None, font_to_use
        else:
            return current_font_size, text_multiline, font_to_use
        current_font_size -= 1

def center_text_inside_box(image_draw:ImageDraw, box_boundaries:Tuple[int,int,int,int], font_to_use:FreeTypeFont, text:str, center_vertically:Optional[bool]=None, center_horizontally:Optional[bool]=None)->Tuple[int,int]:
    """Centers a text inside a box.

    :param box_boundaries: The boundaries of the box in the format left, top, right and bottom coordinates.

    :param font_to_use: The font that should be used.

    :param text: The text that the font should display.

    :param center_vertically: Whether to center vertically or not. Default is False

    :param center_horizontally: Whether to center horizontally or not. Default is True."""
    # Fill out defaults
    if center_vertically is None:
        center_vertically = False
    if center_horizontally is None:
        center_horizontally = True
    box_left, box_top, box_right, box_bottom = box_boundaries
    text_left, text_top, text_right, text_bottom  = image_draw.multiline_textbbox(xy=(0,0), text=text, font=font_to_use)
    text_width = text_right - text_left
    text_height = text_bottom - text_top
    # Calculate total width of box
    box_width = box_right - box_left
    box_height = box_bottom - box_top
    # Do the same with the text
    if center_vertically:
        top_coordinate = box_top+(box_height-text_height)//2
    else:
        top_coordinate = box_top
    if center_horizontally:
        left_coordinate = box_left+(box_width-text_width)//2
    else:
        left_coordinate = box_left
    return (left_coordinate, top_coordinate)

def create_image(input_image:ImageType, album_cover:ImageType, font_path:str, artist_name:Union[str,List[str]], album_name:str, genre_names:List[str], comments:str)->List[ImageType]:
    """All the other utilities above are for parsing images that have been created,
    for usage with OCR etc. However, this function allows you to automatically create a new
    album of the day image! It dynamically crops the text to fit the set areas.

    :param input_image: An Image instance that we can add text on. The opened image must be the album of the day
    template image.

    :param album_cover: An Image instance of an album cover. Will be square-cropped.

    :param font_to_use: A path to the font to use, in Truetype (.ttf) format. Recommended is to use Archivo Black.

    :param artist_name: The name of the artist entry on the image. Multiple artists will automatically be joined with &.

    :param album_name: The name of the album.

    :param genre_names: A list of genre names.

    :param comments: The comments on the album."""
    # Ensure that the image size is correct
    if input_image.size != IMAGE_SIZE:
        raise ParsingException(
            f"The input image has a different size than the standard format: {input_image.size}!={IMAGE_SIZE}. Please ensure the input image is the correct template.")
    # Ensure that the album cover is in square format
    if album_cover.size[0] != album_cover.size[1]:
        raise ParsingException(
            "The album cover size is not square format. Please only provide album covers in square format."
        )
    if isinstance(artist_name, str): # Convert single names to list.
        artist_name = [artist_name]
    # Now, start constructing the image!
    image_draw = ImageDraw(input_image)
    image_title = f"{' & '.join(artist_name)} - {album_name}"
    genre_text = ", ".join(genre_names)
    comments_pages:Tuple[str, FreeTypeFont] = []  # Comments split by pages: a tuple of (text, font)
    for image_part, part_text in [(
        ImageParts.title, image_title
    ),
        (ImageParts.genres,genre_text)
    ,
        (ImageParts.comments, comments)
    ]: # Iterate over each part and add it to the image to create a base image (everything but comments)
        logger.debug(f"Constructing image for part {image_part}.")
        boundaries = CROP_INFORMATION[image_part] # Get the boundaries for the current part
        start_font_size, minimum_font_size = FONT_SIZES[image_part]
        font_size, part_text_split, font_to_use = get_font_size_to_fit_boundaries(image_draw, font_path, part_text, boundaries, start_font_size, minimum_font_size)
        logger.debug(f"Font size for {image_part} calculated to {font_size}.")
        # If we get a too small font size back from our function, we have to manually create the image.
        if font_size is None:
            logger.info("Comments needs to be split into multiple pages. Starting...")
            if image_part != ImageParts.comments:
                raise ParsingException(f"Failed to find a font size that will fit the image for the part: {image_part}. The image must be handled manually.")
            # If the comments are too big, we can split the text in multiple parts!
            comments_words = comments.split(" ")
            current_words = []
            i = 0
            previous_part_text_split = None
            previous_font_to_use = None
            while i < len(comments_words):
                current_words.append(comments_words[i])
                current_font_size, part_text_split, font_to_use = get_font_size_to_fit_boundaries(image_draw, font_path, " ".join(current_words), boundaries, start_font_size, minimum_font_size)
                if current_font_size is None or i == len(comments_words)-1:
                    if len(current_words) > 1: # If we have a word buffer, we have found the words to include on the current image
                        logger.info(f"Done finding comment text for page {len(comments_pages)+1}.")
                        comments_pages.append((previous_part_text_split, previous_font_to_use)
                                              if i != len(comments_words)-1 else (part_text_split, font_to_use))
                        current_words = [comments_words[i]]
                    else: # If we failed to calculate
                        raise ParsingException("Failed to split a too large comment into multiple images (even the first word overflows). The image must be handled manually.")
                previous_part_text_split = part_text_split
                previous_font_to_use = font_to_use
                i+=1
        else:
            if image_part != ImageParts.comments:
                image_draw.multiline_text(
                    xy=center_text_inside_box(image_draw, boundaries, font_to_use, part_text_split, center_vertically=image_part==ImageParts.title),
                    font=font_to_use,
                    text=part_text_split,
                    align="center",
                    fill=BLACK_COLOR
                )
                logger.debug(f"Added text for image part {image_part}.")
            else: # If the comments fit on one page
                comments_pages = [(part_text_split, font_to_use)]
    logger.info(f"Done parsing image text: we have {len(comments_pages)} pages.")
    # Add album cover to the image
    album_cover_width, album_cover_height = album_cover.size
    if album_cover_width >= 300 or album_cover_height >= 300:
        album_cover.thumbnail((300,300))
        input_image.paste(album_cover, box=ALBUM_IMAGE_CROP_PARTS)
    else:
        # Use the smallest value to crop
        thumbnail_size = min(album_cover_width, album_cover_height)
        album_cover.thumbnail((thumbnail_size, thumbnail_size))
        # Generate the box to use
        box_to_paste_into = list(ALBUM_IMAGE_CROP_PARTS)
        # (subtract ALBUM_IMAGE_BASE_CROP_SIZE (the base width + height) and add the smallest
        # size instead.
        box_to_paste_into[2] = box_to_paste_into[2] - ALBUM_IMAGE_BASE_CROP_SIZE + thumbnail_size
        box_to_paste_into[3] = box_to_paste_into[3] - ALBUM_IMAGE_BASE_CROP_SIZE + thumbnail_size
        box_to_paste_into = tuple(box_to_paste_into)
        input_image.paste(album_cover, box=box_to_paste_into)

    logger.info("Base image created.")
    # Now we have got a base image! All that is left is to add comments to it.
    # Comments might be split on multiple pages, so that is why we handle them separately
    base_image = input_image.copy()
    all_images = []
    current_page_number = 1
    for comments_text, font_to_use in comments_pages:
        logger.debug(f"Generating image {current_page_number}/{len(comments_pages)}")
        page_image = base_image.copy()
        image_draw = ImageDraw(page_image) # Reset image to base
        comment_boundaries = CROP_INFORMATION[ImageParts.comments]
        image_draw.multiline_text(
            xy=center_text_inside_box(image_draw, comment_boundaries, font_to_use, comments_text),
            font=font_to_use,
            text=comments_text,
            align="center",
            fill=BLACK_COLOR
        )
        all_images.append(page_image)
        current_page_number += 1
    logger.debug(f"Returning generated images: ({len(all_images)})")
    return all_images # Return the generated images
