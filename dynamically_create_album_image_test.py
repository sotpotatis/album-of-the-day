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
remote_album_cover_request = requests.get("https://lastfm.freetls.fastly.net/i/u/300x300/9ca12ef96bc94cb4ccbefcb7d1da10b1.png")
remote_album_cover_content = BytesIO(remote_album_cover_request.content)
REMOTE_ALBUM_COVER = Image.open(remote_album_cover_content)
ARCHIVO_BLACK_PATH = "ArchivoBlack-Regular.ttf"
images = create_image(
    artist_name="Gidge",
    album_name="Autumn Bells",
    genre_names="microhouse,ambient techno,future garage,nature recordings,deep house".split(","),
    album_cover=REMOTE_ALBUM_COVER,
    comments="""vad gör man dagen efter att ha kommit tillbaka från att ha spenderat ett par dagar borta hemifrån? jo, det finns två svar på den frågan. plockar svamp, för det fanns väldigt mycket svamp ute. har plockat rekordmycket idag tror jag. nummer två: lyssnar igenom microhousealbum, eftersom jag avser att skriva om albumet Tanum Teleport av Boeoes Kaelstigen som är uppkallat efter antenner som blivit ett landmärke nära den platsen jag just kommit hem ifrån (Tanum) och behöver veta vad som anses vara ett bra microhousealbum. dessa två saker kom tillsammans i ”Autumn Bells”, som är ett album som både har skogen som tema och microhouse-influenser. jag fokuserade på house-elementen i lyssningen, även om albumet inkluderar en rad andra genrer. vi kommer till det, och det är väldigt trevligt eftersom jag inte är ett stort fan av house-element. och mycket riktigt är öppningslåten är mer ambient-fokuserad. det är i andra låten, som har två distinkta delar, som house-elementen blir mer tydliga. i andra halvan av You dyker ett sample som påminner om såna man kan hitta i någon elektronisk låt som man skulle kunna lyssnat på i fyran upp och som då hade placerats innan ett, vad man då skulle tycka vara, ett ”sjukt drop”. men vad som finns på Autumn Bells och vad som inte finns på de låtarna man lyssnade på då är atmosfär. på ”I Fell In Love” används house-/techno-trummorna tillsammans med regnsamples och en pianoslinga för att skapa en atmosfären av en regnig skog. det gör det lyssningsbart och ändå framlyftningsbart. ”Rest” erbjuder en lugn låt med få trummor och fragmentsamples av röster. och ”Dusk” lyckad faktiskt sonifiera känslan av en solnedgång en regnig höstdag och hamnar i ett stort lugn i mitten - breddat av pianoslingor och fler lugna röster. Autumn Bells är ytterligare ett exempel på album som brukar house-element som stundtals inte faller mig i smaken (som i Fauna Pt II till exempel) men vars atmosfär och övriga delar väger upp och ändå skapar ett intressant album samt ett som en person som inte är ett så stort fan av house-influenser ändå kan förstå har kvalitet. albumet avslutas med en låt som har ett namn som vi alla kan känna igen - ”Norrland” och använder någon trumpetliknande synth som känns mystisk och trevlig. tillsammans med intensiva house-trummor dyker samples av fåglar långsamt upp, och sedan kulminerar låten i vad jag onekligen kan säga är ett väldigt fint cresendo där ovannämnd synth blir intensiv. det hela avslutas sedan genom att sista minuten är lugn och utan trummor för att en sista gång sätta atmosfären, ett bevis både på finstämdhet och måttfullhet. jag kan förstå varför detta finns på topplistan av de bästa microhousealbumen utan att alls ha lyssnat mycket på genren. lustigt nog, eller kanske passande nog finns flera likheter med min uppkommande text om albumet Tanum Teleport: precis som Boeoes Kaelstigen är Gidge en svensk electronic-artist, och dessutom en duo, precis som Boeoes Kaelstigen är. och dessutom har vi ju som sagt, referenser till svenska platser, om än olika sådana och olika specifika sådana.""",    font_path=ARCHIVO_BLACK_PATH,
    input_image=TEMPLATE_IMAGE_PILLOW
)
for image in images:
    image.show()