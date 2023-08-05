"""dynamically_create_album_image_test.py
A test that you can run to test the function to dynamically create an album of the day image.
The template image is included inside the utility."""
import logging
from io import BytesIO

import requests

logging.basicConfig(level=logging.INFO)
from album_image_util.template_image_data import TEMPLATE_IMAGE_PILLOW, ALBUM_COVER_PLACEHOLDER_IMAGE_PILLOW
from album_image_util.util import create_image
from PIL import Image
from PIL import ImageFont
# Note: provide the font yourself
# The font (Archivo Black) can be downloaded from many sources!
DEMO_IMAGE = ALBUM_COVER_PLACEHOLDER_IMAGE_PILLOW
# Example to use a remote album cover
remote_album_cover_request = requests.get("https://lastfm.freetls.fastly.net/i/u/300x300/8437125020b04a868984a7878ee9b856.jpg")
remote_album_cover_content = BytesIO(remote_album_cover_request.content)
REMOTE_ALBUM_COVER = Image.open(remote_album_cover_content)
ARCHIVO_BLACK_PATH = "ArchivoBlack-Regular.ttf"
images = create_image(
    artist_name="Test artist",
    album_name="Test album",
    genre_names=["test genre 1", "test genre 2", "test genre 3", "test genre 4"],
    album_cover=REMOTE_ALBUM_COVER,
    comments=""" Lorem ipsum dolor sit amet, consectetur adipiscing elit. Duis pretium lectus metus, eu interdum neque scelerisque id. Duis pharetra ligula sed metus porttitor dignissim. Fusce ligula sem, sollicitudin porta dolor id, ultrices consectetur mi. Nullam mattis sed felis vitae dapibus. Nam pretium risus turpis, sit amet ultricies augue auctor vitae. Cras pharetra dolor ante, in suscipit nisi mattis aliquam. Pellentesque et arcu eget dolor hendrerit imperdiet. Nam iaculis mi nisl, nec pulvinar nulla scelerisque ac. Duis congue laoreet venenatis. Curabitur gravida mauris sed ipsum tincidunt convallis. Nam ut quam sed tellus malesuada aliquet vitae eget lectus. """,
    font_path=ARCHIVO_BLACK_PATH,
    input_image=TEMPLATE_IMAGE_PILLOW
)
for image in images:
    image.show()