"""ocr_output_preview.py
Previews all the texts that have been extracted via OCR on a website.
Also runs spell-check on everything."""
import os
from flask import Flask, render_template
from extract_text_from_images import get_albums_data_file
from spylls.hunspell import Dictionary
app = Flask(__name__)
SPELLCHECK_DIRECTORY = os.path.join(os.getcwd(), "spellcheck") # Put spellcheck files here
swedish_spellcheck = Dictionary.from_files(os.path.join(SPELLCHECK_DIRECTORY, "sv"))
english_spellcheck = Dictionary.from_files(os.path.join(SPELLCHECK_DIRECTORY, "en"))
@app.route("/")
def index():
    albums = get_albums_data_file() # Get all albums
    final_data = [] # Albums sorted and ran through spellcheck
    for album in albums["album_images"]:
        # Run spellcheck
        comment_words = [] # Present comment words as split metadata so the website can show it.
        for word in album["comments"].split(" "):
            highlighted = False # Whether spellcheck triggered
            if not swedish_spellcheck.lookup(word) and not english_spellcheck.lookup(word): # If word is in spellcheck
                highlighted = True
            comment_words.append({
            "word": word,
            "highlighted": highlighted})
        album["comment_words"] = comment_words
        final_data.append(album)
    return render_template("index.html", data=final_data)

if __name__ == "__main__":
    app.run(debug=True)