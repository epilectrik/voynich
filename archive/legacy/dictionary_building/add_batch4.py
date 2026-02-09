"""Add batch 4 of entries."""
import json
from pathlib import Path
from datetime import datetime

dict_path = Path('dictionary.json')
with open(dict_path) as f:
    dictionary = json.load(f)

new_entries = {
    # ch- variants
    "ches": {
        "latin": "cibus",
        "english": "food",
        "category": "noun",
        "confidence": 0.25,
        "source": "frequency",
        "notes": "36x"
    },
    "chees": {
        "latin": "cibi",
        "english": "of food",
        "category": "noun",
        "confidence": 0.25,
        "source": "frequency",
        "notes": "33x - genitive"
    },
    "cheos": {
        "latin": "cibum",
        "english": "food (acc.)",
        "category": "noun",
        "confidence": 0.25,
        "source": "frequency",
        "notes": "33x"
    },
    "cheal": {
        "latin": "calidae",
        "english": "of warm",
        "category": "adj",
        "confidence": 0.25,
        "source": "frequency",
        "notes": "30x"
    },
    "chedar": {
        "latin": "calidarum",
        "english": "of hot things",
        "category": "adj",
        "confidence": 0.20,
        "source": "frequency",
        "notes": "30x"
    },
    "checthy": {
        "latin": "calefacio",
        "english": "I heat",
        "category": "verb",
        "confidence": 0.20,
        "source": "frequency",
        "notes": "28x"
    },
    "chckhey": {
        "latin": "calefaciens",
        "english": "heating (pres. part.)",
        "category": "adj",
        "confidence": 0.20,
        "source": "frequency",
        "notes": "30x"
    },

    # sh- variants
    "sheckhy": {
        "latin": "siccatio",
        "english": "drying",
        "category": "noun",
        "confidence": 0.25,
        "source": "frequency",
        "notes": "35x"
    },
    "shcthy": {
        "latin": "siccitatis",
        "english": "of dryness",
        "category": "noun",
        "confidence": 0.25,
        "source": "frequency",
        "notes": "31x"
    },

    # l- and ol- combinations
    "lkain": {
        "latin": "liquamen",
        "english": "liquid sauce",
        "category": "noun",
        "confidence": 0.25,
        "source": "frequency",
        "notes": "35x"
    },
    "olkain": {
        "latin": "oleum",
        "english": "oil (variant)",
        "category": "noun",
        "confidence": 0.25,
        "source": "frequency",
        "notes": "33x"
    },
    "olkaiin": {
        "latin": "oleatio",
        "english": "oiling process",
        "category": "noun",
        "confidence": 0.25,
        "source": "frequency",
        "notes": "31x"
    },
    "olor": {
        "latin": "olor",
        "english": "swan/smell",
        "category": "noun",
        "confidence": 0.20,
        "source": "frequency",
        "notes": "31x"
    },
    "oldy": {
        "latin": "olidi",
        "english": "smelly",
        "category": "adj",
        "confidence": 0.20,
        "source": "frequency",
        "notes": "28x"
    },
    "olchey": {
        "latin": "oleaceus",
        "english": "oily",
        "category": "adj",
        "confidence": 0.20,
        "source": "frequency",
        "notes": "29x"
    },
    "lkar": {
        "latin": "liquaris",
        "english": "liquid (adj.)",
        "category": "adj",
        "confidence": 0.20,
        "source": "frequency",
        "notes": "30x"
    },
    "lkedy": {
        "latin": "liquescit",
        "english": "melts",
        "category": "verb",
        "confidence": 0.20,
        "source": "frequency",
        "notes": "29x"
    },

    # ok- variants
    "okor": {
        "latin": "oculorum",
        "english": "of eyes",
        "category": "noun",
        "confidence": 0.25,
        "source": "frequency",
        "notes": "34x"
    },

    # ot- variants
    "otchedy": {
        "latin": "temporalis",
        "english": "temporal",
        "category": "adj",
        "confidence": 0.25,
        "source": "frequency",
        "notes": "34x"
    },
    "otchey": {
        "latin": "tempore",
        "english": "at time (abl.)",
        "category": "noun",
        "confidence": 0.25,
        "source": "frequency",
        "notes": "31x"
    },
    "otchdy": {
        "latin": "temporibus",
        "english": "at times (abl. pl.)",
        "category": "noun",
        "confidence": 0.20,
        "source": "frequency",
        "notes": "30x"
    },
    "oteos": {
        "latin": "temporum",
        "english": "of times",
        "category": "noun",
        "confidence": 0.20,
        "source": "frequency",
        "notes": "29x"
    },
    "otchol": {
        "latin": "tempestatis",
        "english": "of weather",
        "category": "noun",
        "confidence": 0.20,
        "source": "frequency",
        "notes": "28x"
    },

    # qo- variants
    "qokeody": {
        "latin": "coloratus",
        "english": "colored",
        "category": "adj",
        "confidence": 0.25,
        "source": "frequency",
        "notes": "32x"
    },
    "qopchedy": {
        "latin": "confectus",
        "english": "prepared",
        "category": "adj",
        "confidence": 0.25,
        "source": "frequency",
        "notes": "32x"
    },
    "qokchey": {
        "latin": "coctione",
        "english": "with cooking",
        "category": "noun",
        "confidence": 0.20,
        "source": "frequency",
        "notes": "30x"
    },
    "qo": {
        "latin": "quo",
        "english": "where/to which",
        "category": "adv",
        "confidence": 0.30,
        "source": "frequency",
        "notes": "29x"
    },
    "qotor": {
        "latin": "colorum",
        "english": "of colors",
        "category": "noun",
        "confidence": 0.20,
        "source": "frequency",
        "notes": "29x"
    },

    # Other words
    "ykar": {
        "latin": "igitur",
        "english": "therefore",
        "category": "conj",
        "confidence": 0.25,
        "source": "frequency",
        "notes": "36x"
    },
    "sy": {
        "latin": "sic",
        "english": "thus/so",
        "category": "adv",
        "confidence": 0.30,
        "source": "frequency",
        "notes": "35x"
    },
    "oiin": {
        "latin": "omnem",
        "english": "all (acc.)",
        "category": "adj",
        "confidence": 0.25,
        "source": "frequency",
        "notes": "33x"
    },
    "pchedy": {
        "latin": "pectus",
        "english": "chest/breast",
        "category": "noun",
        "confidence": 0.30,
        "source": "frequency",
        "notes": "34x - anatomy"
    },
    "tchedy": {
        "latin": "tactus",
        "english": "touch",
        "category": "noun",
        "confidence": 0.25,
        "source": "frequency",
        "notes": "33x"
    },
    "chedaiin": {
        "latin": "cibatio",
        "english": "feeding",
        "category": "noun",
        "confidence": 0.20,
        "source": "frequency",
        "notes": "32x"
    },
    "dchy": {
        "latin": "desuper",
        "english": "from above",
        "category": "adv",
        "confidence": 0.20,
        "source": "frequency",
        "notes": "30x"
    },
    "daly": {
        "latin": "dalus",
        "english": "torch/fire",
        "category": "noun",
        "confidence": 0.20,
        "source": "frequency",
        "notes": "30x"
    },
    "ykeedy": {
        "latin": "iterum",
        "english": "again",
        "category": "adv",
        "confidence": 0.25,
        "source": "frequency",
        "notes": "30x"
    },
    "os": {
        "latin": "os",
        "english": "mouth/bone",
        "category": "noun",
        "confidence": 0.35,
        "source": "frequency",
        "notes": "29x - anatomy"
    },
    "kchy": {
        "latin": "quia",
        "english": "because",
        "category": "conj",
        "confidence": 0.25,
        "source": "frequency",
        "notes": "29x"
    },
    "opchey": {
        "latin": "optimum",
        "english": "best (n.)",
        "category": "noun",
        "confidence": 0.25,
        "source": "frequency",
        "notes": "29x"
    },
    "aly": {
        "latin": "alium",
        "english": "garlic/other",
        "category": "noun",
        "confidence": 0.25,
        "source": "frequency",
        "notes": "29x"
    },
    "sair": {
        "latin": "sanitas",
        "english": "health",
        "category": "noun",
        "confidence": 0.30,
        "source": "frequency",
        "notes": "28x"
    },
    "yteey": {
        "latin": "ideo",
        "english": "therefore",
        "category": "adv",
        "confidence": 0.25,
        "source": "frequency",
        "notes": "28x"
    },
    "yteedy": {
        "latin": "identidem",
        "english": "repeatedly",
        "category": "adv",
        "confidence": 0.20,
        "source": "frequency",
        "notes": "28x"
    },
}

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
