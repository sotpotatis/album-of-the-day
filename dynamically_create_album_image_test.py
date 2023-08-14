"""dynamically_create_album_image_test.py
A test that you can run to test the function to dynamically create an album of the day image.
The template image is included inside the utility."""
import logging
import urllib.request
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
remote_album_cover_request = requests.get("https://lastfm.freetls.fastly.net/i/u/770x0/d3e80f8205ce446cbfb11c22c92245e9.jpg#d3e80f8205ce446cbfb11c22c92245e9")
remote_album_cover_content = BytesIO(remote_album_cover_request.content)
REMOTE_ALBUM_COVER = Image.open(remote_album_cover_content)
ARCHIVO_BLACK_PATH = "ArchivoBlack-Regular.ttf"
print(response.status_code)
images = create_image(
    artist_name="Sharon an ",
    album_name="Today",
    genre_names="slowcore,indie pop,dream pop,jangle pop".split(","),
    album_cover=REMOTE_ALBUM_COVER,
    comments="""Galaxie 500’s album ”On Fire” var ett av de albumen som var ett soundtrack till vintern 2022/2023. med låtar som ”Snowstorm” och lugna men ändå intressanta gitarrer hör albumet till ett av mina mest spelade från den perioden. en perfekt vinterkänsla helt enkelt. så när jag upptäckte att Galaxie 500 har ett album som förmedlar känslan av sommaren, blev jag självklart glad. de har ett soundtrack för båda perioderna! albumet startar med ”Flowers” och ”Pictures” som båda har bandets signaturgitarrer och sång och mycket väl känns somriga, både på namnen och musiken. gitarren i ”Pictures” för fram låten på ett energiskt sätt. tredje låten, ”Parking Lot” placerar lyssnaren på en tunnelbanetåg i början av sommaren, där man ser folk lämna storstaden. de dagar jag åker från staden under sommaren har jag befunnit mig på ett tåg, så låten påminner mig om början på alla somrar - och rymmer därför minnen av det som varit där i. ”Don’t Let Our Youth Go To Waste” hör man redan på titeln på att det är en låt som påminner om skapade sommarminnen. och det är precis som ”Snowstorm” är en perfekt vinterlåt en perfekt sommarlåt. även nästa låt ”Temperature’s Rising” är ytterligare en låt som är perfekt att spela under början av sommaren och hör till en av låtarna från albumet som jag spelat mycket denna sommar. ”Oblivious” introducerar munspel i bilden. ”Instrumental” låter Galaxie 500s riktigt fina gitarrer tala helt för sig själva. den mer energiska Tugboat övergår i den lugnare King Of Spain som är ett fint outro. när cymbalen slår sista gången inser man att albumet verkligen målat upp en bild av tidig sommar. som sagt så går sommaren mot sitt slut, eller åtminstone sommarlovet, men albumet kan istället som sagt påminna om allt som hänt mellan början av sommaren och nu. och gitarrerna är värda att lyfta fram - albumets gitarrer har hyllats av bland annat Sonic Youths Thurston Moore som kallade detta album ”the guitar record of 1988”. då Sonic Youth är kända för att göra underverk och experimentera med gitarrer är detta ett stort men 110% värdigt statement.""",
    input_image=TEMPLATE_IMAGE_PILLOW,
    font_path=ARCHIVO_BLACK_PATH
)
for image in images:
    image.show()