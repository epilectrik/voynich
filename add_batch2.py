"""Add batch 2 of entries for remaining high-frequency words."""
import json
from pathlib import Path
from datetime import datetime

dict_path = Path('dictionary.json')
with open(dict_path) as f:
    dictionary = json.load(f)

# More entries based on remaining frequency and patterns
new_entries = {
    # ch- prefix variants
    "chckhy": {
        "latin": "calefactus",
        "english": "heated",
        "category": "adj",
        "confidence": 0.30,
        "source": "frequency",
        "notes": "140x - ch+ck pattern, heated/warmed"
    },
    "chcthy": {
        "latin": "caliditas",
        "english": "heat/warmth (n.)",
        "category": "noun",
        "confidence": 0.30,
        "source": "frequency",
        "notes": "79x - ch+cth compound"
    },
    "cheor": {
        "latin": "calorem",
        "english": "heat (acc.)",
        "category": "noun",
        "confidence": 0.30,
        "source": "frequency",
        "notes": "100x - accusative"
    },
    "cho": {
        "latin": "cum",
        "english": "with (short)",
        "category": "prep",
        "confidence": 0.35,
        "source": "frequency",
        "notes": "68x - shortened form of chey"
    },
    "cheo": {
        "latin": "calore",
        "english": "with heat",
        "category": "noun",
        "confidence": 0.30,
        "source": "frequency",
        "notes": "65x - ablative"
    },
    "cheky": {
        "latin": "calefacit",
        "english": "heats/warms",
        "category": "verb",
        "confidence": 0.30,
        "source": "frequency",
        "notes": "65x"
    },
    "cheedy": {
        "latin": "calidior",
        "english": "hotter",
        "category": "adj",
        "confidence": 0.30,
        "source": "frequency",
        "notes": "59x - comparative"
    },
    "chear": {
        "latin": "calor",
        "english": "heat",
        "category": "noun",
        "confidence": 0.30,
        "source": "frequency",
        "notes": "51x"
    },
    "char": {
        "latin": "caro",
        "english": "flesh/meat",
        "category": "noun",
        "confidence": 0.30,
        "source": "frequency",
        "notes": "72x - medical context"
    },

    # qo- prefix more variants
    "qokey": {
        "latin": "quomodo",
        "english": "how/in what way",
        "category": "adv",
        "confidence": 0.30,
        "source": "frequency",
        "notes": "107x"
    },
    "qokol": {
        "latin": "color",
        "english": "color",
        "category": "noun",
        "confidence": 0.35,
        "source": "frequency",
        "notes": "105x - botanical description"
    },
    "qotedy": {
        "latin": "quotiens",
        "english": "how often",
        "category": "adv",
        "confidence": 0.30,
        "source": "frequency",
        "notes": "92x"
    },
    "qoty": {
        "latin": "cottus",
        "english": "cooked/boiled",
        "category": "adj",
        "confidence": 0.30,
        "source": "frequency",
        "notes": "87x - preparation method"
    },
    "qotaiin": {
        "latin": "quotidianus",
        "english": "daily",
        "category": "adj",
        "confidence": 0.30,
        "source": "frequency",
        "notes": "79x"
    },
    "qoteedy": {
        "latin": "cotidie",
        "english": "every day",
        "category": "adv",
        "confidence": 0.30,
        "source": "frequency",
        "notes": "74x"
    },
    "qokchy": {
        "latin": "coctio",
        "english": "cooking/digestion",
        "category": "noun",
        "confidence": 0.30,
        "source": "frequency",
        "notes": "69x"
    },
    "qotain": {
        "latin": "quotus",
        "english": "which (number)",
        "category": "adj",
        "confidence": 0.25,
        "source": "frequency",
        "notes": "64x"
    },
    "qotchy": {
        "latin": "coctum",
        "english": "cooked thing",
        "category": "noun",
        "confidence": 0.25,
        "source": "frequency",
        "notes": "63x"
    },
    "qotar": {
        "latin": "coloris",
        "english": "of color",
        "category": "noun",
        "confidence": 0.25,
        "source": "frequency",
        "notes": "63x - genitive"
    },
    "qotal": {
        "latin": "colorum",
        "english": "of colors",
        "category": "noun",
        "confidence": 0.25,
        "source": "frequency",
        "notes": "59x - gen. plural"
    },
    "qokchdy": {
        "latin": "coctionis",
        "english": "of cooking",
        "category": "noun",
        "confidence": 0.25,
        "source": "frequency",
        "notes": "56x"
    },
    "qokeol": {
        "latin": "colore",
        "english": "with color",
        "category": "noun",
        "confidence": 0.25,
        "source": "frequency",
        "notes": "52x - ablative"
    },

    # ok- prefix more variants
    "okeedy": {
        "latin": "oculis",
        "english": "with eyes",
        "category": "noun",
        "confidence": 0.30,
        "source": "frequency",
        "notes": "105x - ablative plural"
    },
    "okol": {
        "latin": "oculum",
        "english": "eye (acc.)",
        "category": "noun",
        "confidence": 0.30,
        "source": "frequency",
        "notes": "82x"
    },
    "okeol": {
        "latin": "oculo",
        "english": "in eye",
        "category": "noun",
        "confidence": 0.25,
        "source": "frequency",
        "notes": "66x - ablative"
    },
    "okey": {
        "latin": "odoris",
        "english": "of smell",
        "category": "noun",
        "confidence": 0.25,
        "source": "frequency",
        "notes": "63x"
    },

    # ot- prefix more variants
    "oteedy": {
        "latin": "temporis",
        "english": "of time",
        "category": "noun",
        "confidence": 0.30,
        "source": "frequency",
        "notes": "100x - genitive"
    },
    "otain": {
        "latin": "aetatis",
        "english": "of age",
        "category": "noun",
        "confidence": 0.25,
        "source": "frequency",
        "notes": "96x"
    },
    "otol": {
        "latin": "astri",
        "english": "of star",
        "category": "noun",
        "confidence": 0.30,
        "source": "frequency",
        "notes": "86x - genitive"
    },
    "otey": {
        "latin": "tunc",
        "english": "then/at that time",
        "category": "adv",
        "confidence": 0.25,
        "source": "frequency",
        "notes": "57x"
    },

    # sh- prefix more variants
    "shckhy": {
        "latin": "siccitas",
        "english": "dryness",
        "category": "noun",
        "confidence": 0.30,
        "source": "frequency",
        "notes": "60x - noun from siccus"
    },
    "sheor": {
        "latin": "specierum",
        "english": "of kinds",
        "category": "noun",
        "confidence": 0.25,
        "source": "frequency",
        "notes": "51x - gen. plural"
    },

    # Standalone words
    "ain": {
        "latin": "-inus",
        "english": "(adj. suffix)",
        "category": "suffix",
        "confidence": 0.30,
        "source": "frequency",
        "notes": "89x - Latin adj ending"
    },
    "am": {
        "latin": "amarus",
        "english": "bitter",
        "category": "adj",
        "confidence": 0.40,
        "source": "frequency",
        "notes": "88x - common botanical taste"
    },
    "o": {
        "latin": "aut",
        "english": "or",
        "category": "conj",
        "confidence": 0.30,
        "source": "frequency",
        "notes": "81x"
    },
    "sol": {
        "latin": "sol",
        "english": "sun",
        "category": "noun",
        "confidence": 0.45,
        "source": "frequency",
        "notes": "75x - astronomical/botanical"
    },
    "raiin": {
        "latin": "ratio",
        "english": "reason/method",
        "category": "noun",
        "confidence": 0.30,
        "source": "frequency",
        "notes": "75x"
    },
    "air": {
        "latin": "aer",
        "english": "air",
        "category": "noun",
        "confidence": 0.45,
        "source": "frequency",
        "notes": "74x - element"
    },
    "dor": {
        "latin": "dulcor",
        "english": "sweetness",
        "category": "noun",
        "confidence": 0.35,
        "source": "frequency",
        "notes": "73x - botanical taste"
    },
    "sain": {
        "latin": "sanus",
        "english": "healthy",
        "category": "adj",
        "confidence": 0.35,
        "source": "frequency",
        "notes": "68x - medical context"
    },
    "odaiin": {
        "latin": "odoratio",
        "english": "fragrance",
        "category": "noun",
        "confidence": 0.30,
        "source": "frequency",
        "notes": "60x"
    },
    "cthol": {
        "latin": "aquarum",
        "english": "of waters",
        "category": "noun",
        "confidence": 0.35,
        "source": "frequency",
        "notes": "60x - gen. plural of aqua"
    },
    "ykeey": {
        "latin": "ita",
        "english": "thus/so",
        "category": "adv",
        "confidence": 0.25,
        "source": "frequency",
        "notes": "58x"
    },
    "l": {
        "latin": "lac",
        "english": "milk",
        "category": "noun",
        "confidence": 0.35,
        "source": "frequency",
        "notes": "58x - medicinal"
    },
    "sor": {
        "latin": "sordis",
        "english": "of dirt/filth",
        "category": "noun",
        "confidence": 0.25,
        "source": "frequency",
        "notes": "57x"
    },
    "sal": {
        "latin": "salis",
        "english": "of salt",
        "category": "noun",
        "confidence": 0.35,
        "source": "frequency",
        "notes": "55x - genitive"
    },
    "keedy": {
        "latin": "celeritas",
        "english": "speed/quickness",
        "category": "noun",
        "confidence": 0.25,
        "source": "frequency",
        "notes": "53x"
    },
    "kar": {
        "latin": "carens",
        "english": "lacking",
        "category": "adj",
        "confidence": 0.25,
        "source": "frequency",
        "notes": "52x"
    },
    "olaiin": {
        "latin": "oleatio",
        "english": "oiling",
        "category": "noun",
        "confidence": 0.30,
        "source": "frequency",
        "notes": "52x - process"
    },
    "cthey": {
        "latin": "aqueus",
        "english": "watery",
        "category": "adj",
        "confidence": 0.35,
        "source": "frequency",
        "notes": "50x - adj from aqua"
    },
}

# Add entries that don't already exist
added = 0
for word, entry in new_entries.items():
    if word not in dictionary['entries']:
        dictionary['entries'][word] = entry
        print(f"Added: {word} = {entry['latin']} ({entry['english']})")
        added += 1

# Update timestamp
dictionary['last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M")

# Save
with open(dict_path, 'w') as f:
    json.dump(dictionary, f, indent=2, ensure_ascii=False)

print(f"\nTotal added: {added}")
print(f"Total entries: {len(dictionary['entries'])}")
