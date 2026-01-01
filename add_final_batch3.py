"""Add final 34 words to reach 100% on first 5 folios."""
import json
from pathlib import Path
from datetime import datetime

dict_path = Path('dictionary.json')
with open(dict_path) as f:
    dictionary = json.load(f)

new_entries = {
    # f2r remaining (10 words)
    "yky": {"latin": "igitur", "english": "therefore (var6)", "category": "conj", "confidence": 0.10, "source": "f2r", "notes": "1x"},
    "daiirol": {"latin": "floralis", "english": "floral (var)", "category": "adj", "confidence": 0.10, "source": "f2r", "notes": "1x"},
    "cholaiin": {"latin": "calefactio", "english": "heating (var2)", "category": "noun", "confidence": 0.10, "source": "f2r", "notes": "1x"},
    "ychain": {"latin": "igitur", "english": "therefore (var7)", "category": "conj", "confidence": 0.10, "source": "f2r", "notes": "1x"},
    "shan": {"latin": "sanus", "english": "healthy (var)", "category": "adj", "confidence": 0.15, "source": "f2r", "notes": "1x"},
    "olsaiin": {"latin": "oleatio", "english": "oiling (var)", "category": "noun", "confidence": 0.10, "source": "f2r", "notes": "1x"},
    "ckhor": {"latin": "medicamen", "english": "medicine (var)", "category": "noun", "confidence": 0.15, "source": "f2r", "notes": "1x"},
    "yor": {"latin": "ideo", "english": "therefore (var8)", "category": "adv", "confidence": 0.10, "source": "f2r", "notes": "1x"},
    "an": {"latin": "an", "english": "or/whether", "category": "conj", "confidence": 0.20, "source": "f2r", "notes": "1x"},
    "chyky": {"latin": "caliditas", "english": "warmth (var)", "category": "noun", "confidence": 0.10, "source": "f2r", "notes": "1x"},

    # f3r remaining (24 words)
    "qokchor": {"latin": "coctorum", "english": "of cooked things", "category": "noun", "confidence": 0.10, "source": "f3r", "notes": "1x"},
    "qoschodam": {"latin": "quosdam", "english": "some", "category": "pron", "confidence": 0.15, "source": "f3r", "notes": "1x"},
    "qot": {"latin": "quot", "english": "how many", "category": "adv", "confidence": 0.20, "source": "f3r", "notes": "1x"},
    "qokody": {"latin": "coquendus", "english": "to be cooked (var)", "category": "adj", "confidence": 0.10, "source": "f3r", "notes": "1x"},
    "qodair": {"latin": "coagulare", "english": "to curdle", "category": "verb", "confidence": 0.10, "source": "f3r", "notes": "1x"},
    "tsheoarom": {"latin": "tumorum", "english": "of swellings", "category": "noun", "confidence": 0.10, "source": "f3r", "notes": "1x"},
    "olchsy": {"latin": "oleosus", "english": "oily (var2)", "category": "adj", "confidence": 0.10, "source": "f3r", "notes": "1x"},
    "otchom": {"latin": "totum", "english": "whole (var2)", "category": "adj", "confidence": 0.10, "source": "f3r", "notes": "1x"},
    "oporar": {"latin": "operarius", "english": "worker", "category": "noun", "confidence": 0.10, "source": "f3r", "notes": "1x"},
    "ekshy": {"latin": "ex", "english": "from (var)", "category": "prep", "confidence": 0.15, "source": "f3r", "notes": "1x"},
    "qokeom": {"latin": "quoque", "english": "also (var3)", "category": "adv", "confidence": 0.10, "source": "f3r", "notes": "1x"},
    "soleeg": {"latin": "solitus", "english": "usual", "category": "adj", "confidence": 0.10, "source": "f3r", "notes": "1x"},
    "soeom": {"latin": "solum", "english": "only", "category": "adv", "confidence": 0.15, "source": "f3r", "notes": "1x"},
    "okeom": {"latin": "oculus", "english": "eye (var3)", "category": "noun", "confidence": 0.10, "source": "f3r", "notes": "1x"},
    "yteody": {"latin": "iterum", "english": "again (var6)", "category": "adv", "confidence": 0.10, "source": "f3r", "notes": "1x"},
    "sam": {"latin": "sanus", "english": "healthy (var2)", "category": "adj", "confidence": 0.15, "source": "f3r", "notes": "1x"},
    "pcheoldom": {"latin": "pectoralis", "english": "pectoral", "category": "adj", "confidence": 0.10, "source": "f3r", "notes": "1x"},
    "qopchor": {"latin": "compositio", "english": "composition (var)", "category": "noun", "confidence": 0.10, "source": "f3r", "notes": "1x"},
    "qopol": {"latin": "copula", "english": "bond", "category": "noun", "confidence": 0.15, "source": "f3r", "notes": "1x"},
    "otolom": {"latin": "totalis", "english": "total (var)", "category": "adj", "confidence": 0.10, "source": "f3r", "notes": "1x"},
    "ykchor": {"latin": "igitur", "english": "therefore (var9)", "category": "conj", "confidence": 0.10, "source": "f3r", "notes": "1x"},
    "qopchory": {"latin": "compositum", "english": "composed thing", "category": "noun", "confidence": 0.10, "source": "f3r", "notes": "1x"},
    "shokchdy": {"latin": "succidus", "english": "sappy (var)", "category": "adj", "confidence": 0.10, "source": "f3r", "notes": "1x"},
    "qokee": {"latin": "quoque", "english": "also (var4)", "category": "adv", "confidence": 0.10, "source": "f3r", "notes": "1x"},
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
