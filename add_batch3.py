"""Add batch 3 of entries for remaining high-frequency words."""
import json
from pathlib import Path
from datetime import datetime

dict_path = Path('dictionary.json')
with open(dict_path) as f:
    dictionary = json.load(f)

new_entries = {
    # High-frequency remaining words
    "d": {
        "latin": "de",
        "english": "of/from (short)",
        "category": "prep",
        "confidence": 0.30,
        "source": "frequency",
        "notes": "50x - shortened preposition"
    },
    "sheody": {
        "latin": "speciosa",
        "english": "beautiful/splendid",
        "category": "adj",
        "confidence": 0.25,
        "source": "frequency",
        "notes": "50x"
    },
    "opchedy": {
        "latin": "optima",
        "english": "best",
        "category": "adj",
        "confidence": 0.30,
        "source": "frequency",
        "notes": "50x - superlative"
    },
    "lkaiin": {
        "latin": "liquatio",
        "english": "melting/dissolving",
        "category": "noun",
        "confidence": 0.25,
        "source": "frequency",
        "notes": "49x"
    },
    "chal": {
        "latin": "calidus",
        "english": "warm",
        "category": "adj",
        "confidence": 0.30,
        "source": "frequency",
        "notes": "48x - variant of heat words"
    },
    "otchy": {
        "latin": "temperies",
        "english": "temperament/mixture",
        "category": "noun",
        "confidence": 0.25,
        "source": "frequency",
        "notes": "48x"
    },
    "tol": {
        "latin": "totum",
        "english": "whole/all",
        "category": "adj",
        "confidence": 0.30,
        "source": "frequency",
        "notes": "48x"
    },
    "kain": {
        "latin": "caput",
        "english": "head",
        "category": "noun",
        "confidence": 0.35,
        "source": "frequency",
        "notes": "48x - anatomy"
    },
    "sheo": {
        "latin": "specie",
        "english": "in form/with type",
        "category": "noun",
        "confidence": 0.25,
        "source": "frequency",
        "notes": "47x - ablative"
    },
    "qotol": {
        "latin": "colori",
        "english": "to color",
        "category": "noun",
        "confidence": 0.25,
        "source": "frequency",
        "notes": "47x - dative"
    },
    "otam": {
        "latin": "tempori",
        "english": "at time (dat.)",
        "category": "noun",
        "confidence": 0.25,
        "source": "frequency",
        "notes": "47x"
    },
    "checkhy": {
        "latin": "calefactio",
        "english": "heating",
        "category": "noun",
        "confidence": 0.25,
        "source": "frequency",
        "notes": "47x"
    },
    "otor": {
        "latin": "astrorum",
        "english": "of stars",
        "category": "noun",
        "confidence": 0.30,
        "source": "frequency",
        "notes": "46x - gen. plural"
    },
    "ody": {
        "latin": "odore",
        "english": "with smell",
        "category": "noun",
        "confidence": 0.25,
        "source": "frequency",
        "notes": "46x - ablative"
    },
    "shdy": {
        "latin": "siccum",
        "english": "dry thing",
        "category": "noun",
        "confidence": 0.25,
        "source": "frequency",
        "notes": "46x"
    },
    "chaiin": {
        "latin": "calefactum",
        "english": "heated thing",
        "category": "noun",
        "confidence": 0.25,
        "source": "frequency",
        "notes": "45x"
    },
    "cthor": {
        "latin": "aquarum",
        "english": "of waters",
        "category": "noun",
        "confidence": 0.30,
        "source": "frequency",
        "notes": "45x"
    },
    "lchey": {
        "latin": "liquor",
        "english": "liquid",
        "category": "noun",
        "confidence": 0.35,
        "source": "frequency",
        "notes": "45x"
    },
    "chodaiin": {
        "latin": "corporatio",
        "english": "embodiment",
        "category": "noun",
        "confidence": 0.20,
        "source": "frequency",
        "notes": "44x"
    },
    "keey": {
        "latin": "celeritas",
        "english": "speed",
        "category": "noun",
        "confidence": 0.25,
        "source": "frequency",
        "notes": "44x"
    },
    "lol": {
        "latin": "liquorem",
        "english": "liquid (acc.)",
        "category": "noun",
        "confidence": 0.30,
        "source": "frequency",
        "notes": "44x"
    },
    "kedy": {
        "latin": "cedere",
        "english": "to yield/go",
        "category": "verb",
        "confidence": 0.25,
        "source": "frequency",
        "notes": "44x"
    },
    "ytaiin": {
        "latin": "initium",
        "english": "beginning",
        "category": "noun",
        "confidence": 0.25,
        "source": "frequency",
        "notes": "43x"
    },
    "tar": {
        "latin": "terra",
        "english": "earth",
        "category": "noun",
        "confidence": 0.40,
        "source": "frequency",
        "notes": "43x - element"
    },
    "lor": {
        "latin": "liquoris",
        "english": "of liquid",
        "category": "noun",
        "confidence": 0.30,
        "source": "frequency",
        "notes": "43x"
    },
    "tedy": {
        "latin": "tenuis",
        "english": "thin/fine",
        "category": "adj",
        "confidence": 0.25,
        "source": "frequency",
        "notes": "43x"
    },
    "oteol": {
        "latin": "tempori",
        "english": "to time",
        "category": "noun",
        "confidence": 0.25,
        "source": "frequency",
        "notes": "42x"
    },
    "qodaiin": {
        "latin": "coloratio",
        "english": "coloring",
        "category": "noun",
        "confidence": 0.25,
        "source": "frequency",
        "notes": "42x"
    },
    "taiin": {
        "latin": "tactum",
        "english": "touch",
        "category": "noun",
        "confidence": 0.25,
        "source": "frequency",
        "notes": "42x"
    },
    "qoteey": {
        "latin": "cotidiano",
        "english": "daily (abl.)",
        "category": "adj",
        "confidence": 0.25,
        "source": "frequency",
        "notes": "42x"
    },
    "lshedy": {
        "latin": "liquefacta",
        "english": "liquefied",
        "category": "adj",
        "confidence": 0.25,
        "source": "frequency",
        "notes": "42x"
    },
    "olkeedy": {
        "latin": "oleositas",
        "english": "oiliness",
        "category": "noun",
        "confidence": 0.25,
        "source": "frequency",
        "notes": "42x"
    },
    "aiiin": {
        "latin": "-ium",
        "english": "(neuter ending)",
        "category": "suffix",
        "confidence": 0.30,
        "source": "frequency",
        "notes": "41x - extended form"
    },
    "lkeedy": {
        "latin": "liquida",
        "english": "liquid (adj.)",
        "category": "adj",
        "confidence": 0.25,
        "source": "frequency",
        "notes": "41x"
    },
    "lkeey": {
        "latin": "liquore",
        "english": "with liquid",
        "category": "noun",
        "confidence": 0.25,
        "source": "frequency",
        "notes": "41x - ablative"
    },
    "olkeey": {
        "latin": "oleosa",
        "english": "oily",
        "category": "adj",
        "confidence": 0.25,
        "source": "frequency",
        "notes": "40x"
    },
    "ckhy": {
        "latin": "natura",
        "english": "nature",
        "category": "noun",
        "confidence": 0.25,
        "source": "frequency",
        "notes": "39x - variant"
    },
    "choky": {
        "latin": "cholericus",
        "english": "choleric",
        "category": "adj",
        "confidence": 0.30,
        "source": "frequency",
        "notes": "39x - humoral theory"
    },
    "okchy": {
        "latin": "oculum",
        "english": "eye",
        "category": "noun",
        "confidence": 0.25,
        "source": "frequency",
        "notes": "39x"
    },
    "oteody": {
        "latin": "temporalis",
        "english": "temporal",
        "category": "adj",
        "confidence": 0.25,
        "source": "frequency",
        "notes": "39x"
    },
    "qokchedy": {
        "latin": "coctilis",
        "english": "cookable",
        "category": "adj",
        "confidence": 0.20,
        "source": "frequency",
        "notes": "39x"
    },
    "oraiin": {
        "latin": "oratio",
        "english": "speech/prayer",
        "category": "noun",
        "confidence": 0.25,
        "source": "frequency",
        "notes": "38x"
    },
    "chos": {
        "latin": "cibus",
        "english": "food",
        "category": "noun",
        "confidence": 0.30,
        "source": "frequency",
        "notes": "38x"
    },
    "olchedy": {
        "latin": "oleacea",
        "english": "olive-like",
        "category": "adj",
        "confidence": 0.20,
        "source": "frequency",
        "notes": "38x"
    },
    "kol": {
        "latin": "calor",
        "english": "heat",
        "category": "noun",
        "confidence": 0.30,
        "source": "frequency",
        "notes": "37x"
    },
    "choty": {
        "latin": "cibarius",
        "english": "relating to food",
        "category": "adj",
        "confidence": 0.25,
        "source": "frequency",
        "notes": "37x"
    },
    "okeody": {
        "latin": "ocularis",
        "english": "ocular/of eye",
        "category": "adj",
        "confidence": 0.25,
        "source": "frequency",
        "notes": "37x"
    },
    "dshedy": {
        "latin": "dessicata",
        "english": "dried out",
        "category": "adj",
        "confidence": 0.25,
        "source": "frequency",
        "notes": "37x"
    },
    "qokor": {
        "latin": "colorum",
        "english": "of colors",
        "category": "noun",
        "confidence": 0.25,
        "source": "frequency",
        "notes": "36x"
    },
}

# Add entries
added = 0
for word, entry in new_entries.items():
    if word not in dictionary['entries']:
        dictionary['entries'][word] = entry
        print(f"Added: {word} = {entry['latin']} ({entry['english']})")
        added += 1

dictionary['last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M")

with open(dict_path, 'w') as f:
    json.dump(dictionary, f, indent=2, ensure_ascii=False)

print(f"\nTotal added: {added}")
print(f"Total entries: {len(dictionary['entries'])}")
