"""Download the species name list from PokeAPI's CSV data into species.txt.

Usage: python fetch_species.py [en|es|fr|de|it]
Use the language your game is set to, since OCR reads what the game prints.
"""
import csv
import io
import sys
import urllib.request

LANG_IDS = {"en": "9", "es": "7", "fr": "5", "de": "6", "it": "8"}
URL = "https://raw.githubusercontent.com/PokeAPI/pokeapi/master/data/v2/csv/pokemon_species_names.csv"

lang = sys.argv[1] if len(sys.argv) > 1 else "en"
if lang not in LANG_IDS:
    sys.exit(f"Supported languages: {', '.join(LANG_IDS)}")

raw = urllib.request.urlopen(URL).read().decode("utf-8")
rows = csv.DictReader(io.StringIO(raw))
names = [r["name"] for r in rows if r["local_language_id"] == LANG_IDS[lang]]
with open("species.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(names) + "\n")
print(f"Wrote {len(names)} species names ({lang}) to species.txt")
