"""warnings.py
Detects inconsistencies in data, such as similar genre names, uncommon letters, etc."""
from difflib import SequenceMatcher
from extract_text_from_images import get_albums_data_file
from warnings import warn
previous_genre_names = [] # Store previous genre names
previous_artist_names = [] # Do the same with artists
previous_title_names = [] # ...and titles
previous_dates = [] # Also store previous date

def check_texts_similar(text_1:str, text_2:str)->bool:
    """Checks if a text is similar, but not identical to, another text
    If it is, True is returned.

    :param text_1: The first text to include in the comparison

    :param text_2: The second text to include in the comparison"""
    return text_1 != text_2 and SequenceMatcher(None, text_1, text_2).ratio() > 0.9 # 0.9 is the current golden number

album_data = get_albums_data_file()
for album in album_data["album_images"]:
    # Create a text to identify the album, used in warnings
    album_information_text = f"Album {album['title']} by {','.join(album['artist'])}"
    # Check if we have data that is similar or identical and it should imply a warning
    SIMILARITY_CHECKS = [{
        "data": album["genres"],
        "compare_with": previous_genre_names,
        "warn_if_identical": False
    },
    {
        "data": album["artist"],
        "compare_with": previous_artist_names,
        "warn_if_identical": False
    },
    {
        "data": [album["title"]],
        "compare_with": previous_title_names,
        "warn_if_identical": True
    }
    ]
    for similarity_check in SIMILARITY_CHECKS: # Run all checks
        i = 0
        for datapoint in similarity_check["data"]:
            # For all the previous data
            for previous_data in similarity_check["compare_with"]:
                if previous_data == datapoint and similarity_check["warn_if_identical"]:
                    warn(f"Duplicate found: {datapoint} (index {i}) is identical to previous datapoint.")
                elif check_texts_similar(previous_data, datapoint):
                    warn(f"Similar texts found found: {datapoint} (index {i}) is similar to previous datapoint: {previous_data}.")
            i+= 1
    # Check if date is missing
    if "date" not in album:
        warn(f"{album_information_text}: \"date\" attribute is missing.")
    else:
        if album["date"] in previous_dates:
            warn(f"There are multiple albums for the date {album['date']}.")
        previous_dates.append(album["date"])
    previous_title_names.append(album["title"])
    previous_artist_names.extend(album["artist"])
    previous_genre_names.extend(album["genres"])
