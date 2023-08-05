"""detect_data_gaps.py
Detects any data gaps - aka. missing review methods."""
import datetime
import math
import warnings
from typing import Optional
from extract_text_from_images import get_albums_data_file, write_to_albums_data_file
albums_data = get_albums_data_file()
latest_date :Optional[datetime.date] = None
sorted_albums = albums_data["album_images"] # Sort albums by date


def date_string_to_date(date_str:str)->datetime.date:
    """Converts a date string to a date.

    :param date_str: The date input as a string."""
    return datetime.date.fromisoformat(date_str)


def sort_function(album_data:dict):
    """Sort key returning a parsed date given an album data input.

    :param album_data: Album data as a dictionary."""
    return date_string_to_date(album_data["date"])
sorted_albums.sort(key=sort_function) # Sort albums by date
write_to_albums_data_file({"album_images": sorted_albums}) # Bonus: write the sorted data to albums.json
for album in sorted_albums:
    album_date = date_string_to_date(album["date"])
    # Validate that the limit has not been exceeded
    if latest_date is not None:
        days_difference = math.floor((album_date - latest_date).days)
        if days_difference > 2:
            warnings.warn(f"Data gap: {album['title']} gap is greater than 2 days (difference from previous album: {days_difference}) ({latest_date}-{album_date}).")
    latest_date = album_date