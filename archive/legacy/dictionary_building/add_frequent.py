"""Add entries for highest-frequency untranslated words."""
import json
from pathlib import Path
from datetime import datetime

dict_path = Path('dictionary.json')
with open(dict_path) as f:
    dictionary = json.load(f)

# New entries based on frequency and morphological analysis
# These are educated guesses based on patterns and botanical context
new_entries = {
    # Standalone frequent words
    "ol": {
        "latin": "oleum",
        "english": "oil",
        "category": "noun",
        "confidence": 0.45,
        "source": "frequency",
        "notes": "537x most frequent - botanical oils common in herbals"
    },
    "aiin": {
        "latin": "-ium",
        "english": "(noun ending)",
        "category": "suffix",
        "confidence": 0.40,
        "source": "frequency",
        "notes": "469x - likely Latin -ium neuter ending"
    },
    "dy": {
        "latin": "-dum",
        "english": "(gerundive)",
        "category": "suffix",
        "confidence": 0.35,
        "source": "frequency",
        "notes": "270x - Latin gerundive ending"
    },
    "al": {
        "latin": "aliud",
        "english": "other/another",
        "category": "adj",
        "confidence": 0.35,
        "source": "frequency",
        "notes": "260x - common modifier"
    },
    "chy": {
        "latin": "calor",
        "english": "heat/warmth",
        "category": "noun",
        "confidence": 0.35,
        "source": "frequency",
        "notes": "155x - ch- relates to cth- (water/liquid), chy could be heat"
    },
    "chdy": {
        "latin": "calidus",
        "english": "hot/warm",
        "category": "adj",
        "confidence": 0.35,
        "source": "frequency",
        "notes": "150x - variant of chy with -dy suffix"
    },
    "dol": {
        "latin": "dolorem",
        "english": "pain (acc.)",
        "category": "noun",
        "confidence": 0.40,
        "source": "frequency",
        "notes": "117x - accusative of dolor"
    },
    "shy": {
        "latin": "siccus",
        "english": "dry",
        "category": "adj",
        "confidence": 0.35,
        "source": "frequency",
        "notes": "104x - sh- prefix, opposite of wet"
    },
    "dam": {
        "latin": "datur",
        "english": "is given",
        "category": "verb",
        "confidence": 0.35,
        "source": "frequency",
        "notes": "98x - passive form of dare"
    },
    "shor": {
        "latin": "sucorum",
        "english": "of juices",
        "category": "noun",
        "confidence": 0.40,
        "source": "frequency",
        "notes": "97x - genitive plural of succus"
    },
    "r": {
        "latin": "res",
        "english": "thing/matter",
        "category": "noun",
        "confidence": 0.30,
        "source": "frequency",
        "notes": "97x - abbreviated form"
    },

    # qo- prefix words (possibly quo-/cu- in Latin)
    "qokeey": {
        "latin": "quoque",
        "english": "also/too",
        "category": "adv",
        "confidence": 0.30,
        "source": "frequency",
        "notes": "308x - qo- prefix very common"
    },
    "qokeedy": {
        "latin": "quotidie",
        "english": "daily",
        "category": "adv",
        "confidence": 0.30,
        "source": "frequency",
        "notes": "306x - variant of qokeey"
    },
    "qokain": {
        "latin": "quantum",
        "english": "how much",
        "category": "adv",
        "confidence": 0.30,
        "source": "frequency",
        "notes": "279x"
    },
    "qokedy": {
        "latin": "quod",
        "english": "which/that",
        "category": "conj",
        "confidence": 0.30,
        "source": "frequency",
        "notes": "272x"
    },
    "qokaiin": {
        "latin": "qualitas",
        "english": "quality",
        "category": "noun",
        "confidence": 0.30,
        "source": "frequency",
        "notes": "262x"
    },
    "qokal": {
        "latin": "qualis",
        "english": "of what kind",
        "category": "adj",
        "confidence": 0.30,
        "source": "frequency",
        "notes": "191x"
    },
    "qol": {
        "latin": "colere",
        "english": "to cultivate",
        "category": "verb",
        "confidence": 0.30,
        "source": "frequency",
        "notes": "151x - agricultural context"
    },

    # ok- prefix words (possibly oc-/ox- in Latin)
    "okaiin": {
        "latin": "occasio",
        "english": "occasion/opportunity",
        "category": "noun",
        "confidence": 0.30,
        "source": "frequency",
        "notes": "212x"
    },
    "okeey": {
        "latin": "oculus",
        "english": "eye",
        "category": "noun",
        "confidence": 0.35,
        "source": "frequency",
        "notes": "177x - medical context"
    },
    "okain": {
        "latin": "odor",
        "english": "smell/odor",
        "category": "noun",
        "confidence": 0.35,
        "source": "frequency",
        "notes": "144x - botanical property"
    },
    "okal": {
        "latin": "opus",
        "english": "work/need",
        "category": "noun",
        "confidence": 0.30,
        "source": "frequency",
        "notes": "138x"
    },
    "okar": {
        "latin": "ora",
        "english": "edge/border",
        "category": "noun",
        "confidence": 0.30,
        "source": "frequency",
        "notes": "130x - plant anatomy"
    },
    "okedy": {
        "latin": "operis",
        "english": "of work",
        "category": "noun",
        "confidence": 0.30,
        "source": "frequency",
        "notes": "119x"
    },

    # ot- prefix words (zodiac-related, possibly at-/t-)
    "otedy": {
        "latin": "tempus",
        "english": "time/season",
        "category": "noun",
        "confidence": 0.35,
        "source": "frequency",
        "notes": "156x - zodiac context, seasons"
    },
    "otaiin": {
        "latin": "aetatem",
        "english": "age/time",
        "category": "noun",
        "confidence": 0.30,
        "source": "frequency",
        "notes": "154x"
    },
    "otal": {
        "latin": "astrum",
        "english": "star",
        "category": "noun",
        "confidence": 0.40,
        "source": "frequency",
        "notes": "143x - astronomical section"
    },
    "otar": {
        "latin": "altare",
        "english": "altar/high place",
        "category": "noun",
        "confidence": 0.30,
        "source": "frequency",
        "notes": "141x"
    },
    "oteey": {
        "latin": "tempore",
        "english": "at time",
        "category": "noun",
        "confidence": 0.30,
        "source": "frequency",
        "notes": "140x - ablative of tempus"
    },
    "oty": {
        "latin": "aetas",
        "english": "age",
        "category": "noun",
        "confidence": 0.30,
        "source": "frequency",
        "notes": "115x"
    },

    # ch- prefix words
    "cheey": {
        "latin": "caeruleus",
        "english": "blue",
        "category": "adj",
        "confidence": 0.30,
        "source": "frequency",
        "notes": "174x - color descriptor"
    },
    "cheol": {
        "latin": "calidior",
        "english": "warmer",
        "category": "adj",
        "confidence": 0.30,
        "source": "frequency",
        "notes": "172x - comparative"
    },
    "chody": {
        "latin": "corpus",
        "english": "body",
        "category": "noun",
        "confidence": 0.40,
        "source": "frequency",
        "notes": "94x - medical context"
    },
    "cheody": {
        "latin": "corporis",
        "english": "of body",
        "category": "noun",
        "confidence": 0.35,
        "source": "frequency",
        "notes": "89x - genitive"
    },

    # sh- prefix words
    "sheey": {
        "latin": "species",
        "english": "kind/type",
        "category": "noun",
        "confidence": 0.35,
        "source": "frequency",
        "notes": "144x"
    },
    "sheol": {
        "latin": "speciei",
        "english": "of kind",
        "category": "noun",
        "confidence": 0.30,
        "source": "frequency",
        "notes": "114x - genitive"
    },
    "sheedy": {
        "latin": "spiritus",
        "english": "spirit/breath",
        "category": "noun",
        "confidence": 0.35,
        "source": "frequency",
        "notes": "84x - medical/alchemical"
    },

    # Common botanical/medical terms
    "dair": {
        "latin": "dare",
        "english": "to give",
        "category": "verb",
        "confidence": 0.35,
        "source": "frequency",
        "notes": "106x - dosage instructions"
    },
    "sar": {
        "latin": "sanare",
        "english": "to heal",
        "category": "verb",
        "confidence": 0.40,
        "source": "frequency",
        "notes": "Similar to sanat"
    },
    "lchedy": {
        "latin": "lacerta",
        "english": "lizard/small creature",
        "category": "noun",
        "confidence": 0.25,
        "source": "frequency",
        "notes": "119x - medicinal ingredients"
    },
    "saiin": {
        "latin": "sanatio",
        "english": "healing",
        "category": "noun",
        "confidence": 0.35,
        "source": "frequency",
        "notes": "144x - noun form of sanare"
    },
    "qoky": {
        "latin": "coquere",
        "english": "to cook/prepare",
        "category": "verb",
        "confidence": 0.35,
        "source": "frequency",
        "notes": "147x - preparation method"
    },
    "qokar": {
        "latin": "coctura",
        "english": "cooking/decoction",
        "category": "noun",
        "confidence": 0.35,
        "source": "frequency",
        "notes": "152x"
    },
    "oky": {
        "latin": "omnis",
        "english": "all/every",
        "category": "adj",
        "confidence": 0.30,
        "source": "frequency",
        "notes": "102x"
    },
    "cthar": {
        "latin": "aquae",
        "english": "of water",
        "category": "noun",
        "confidence": 0.45,
        "source": "frequency",
        "notes": "Related to cthy=aqua, genitive form"
    },
    "oly": {
        "latin": "olei",
        "english": "of oil",
        "category": "noun",
        "confidence": 0.40,
        "source": "frequency",
        "notes": "58x - genitive of oleum"
    },
    "shol": {  # Already in dict as facit, but check
        "latin": "facit",
        "english": "makes",
        "category": "verb",
        "confidence": 0.35,
        "source": "grammar_decoder",
        "notes": "Already in dictionary"
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
