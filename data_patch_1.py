"""data_patch_1.py
Solves an issue where the data in albums.json looked like this
{
   "title": {
    "artist": [
     "Hit Home"
    ],
    "title": "After The Fact"
   },
   "genres": [
    "midwest emo",
    "math rock"
   ],
   "comments": "ett ok\u00e4nt album som inte\r\nborde vara ok\u00e4nt.\r\nkortare I\u00e5tar kring 3\r\nminuter. I\u00e5ter bra och\r\ncoolt cover med spegeln\r\noch det dessutom!\r\n"
  },
(as you can see, the title key is wrong)
"""
from extract_text_from_images import get_albums_data_file, write_to_albums_data_file
import logging, warnings
# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)
logger.info("Applying fixes to data...")
album_data = get_albums_data_file()
new_albums = [] # Create list to store albums in
number_of_fixes = 0 # Count how many fixes that were done
for album in album_data["album_images"]:
    fixed_album = album
    if isinstance(album["title"], dict):
        for key, value in album["title"].items():
            fixed_album[key] = value # Move keys outside
        logger.info(f"Applied corrections to album {album['title']}.")
        number_of_fixes += 1
    new_albums.append(fixed_album)
album_data["albums"] = new_albums # Update original file with new content
if number_of_fixes == 0:
    warnings.warn("No fixes were completed. If you didn't expect the data to be clean, ensure that the data format and/or the patching code is correct.")
# Write data
logger.info("Fixes completed. Writing data to file...")
write_to_albums_data_file(album_data)
logger.info("Fixes written to file.")
