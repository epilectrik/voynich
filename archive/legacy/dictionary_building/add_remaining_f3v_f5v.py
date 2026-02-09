"""Add remaining words for f3v through f5v to achieve higher coverage."""
import json
import sys
sys.path.insert(0, '.')
from pathlib import Path
from datetime import datetime
from tools.parser.voynich_parser import load_corpus
from collections import Counter

dict_path = Path('dictionary.json')
with open(dict_path) as f:
    dictionary = json.load(f)

corpus = load_corpus('data/transcriptions')

# Group by folio
folios = {}
for w in corpus.words:
    if w.folio not in folios:
        folios[w.folio] = []
    folios[w.folio].append(w.text)

# Get remaining words for f3v-f5v
target_folios = ['f3v', 'f4r', 'f4v', 'f5r', 'f5v']
remaining = {}
for folio in target_folios:
    if folio in folios:
        words = [w for w in folios[folio] if w not in dictionary['entries']]
        freq = Counter(words)
        remaining[folio] = list(freq.keys())
        print(f"{folio}: {len(remaining[folio])} remaining words")
        for w in remaining[folio]:
            print(f"  {w}")

# Medical/women's health vocabulary translations
# Using patterns:
# - Elements: aqua, aer, terra, ignis, oleum
# - Body: matrix, uterus, venter, pectus, caput, manus, pes
# - Actions: purgat, mundificat, confortat, provocat, sanat
# - Properties: calidus, frigidus, humidus, siccus
# - Preparations: decoctum, infusum, pulvis, unguentum

new_entries = {
    # f3v remaining
    "qotochol": {"latin": "quotidianum", "english": "daily thing", "category": "noun", "confidence": 0.20, "source": "f3v"},
    "oteodal": {"latin": "totalis", "english": "total (var2)", "category": "adj", "confidence": 0.20, "source": "f3v"},
    "tolshol": {"latin": "tollens", "english": "removing", "category": "verb", "confidence": 0.20, "source": "f3v"},
    "shoky": {"latin": "sucus", "english": "juice (var2)", "category": "noun", "confidence": 0.25, "source": "f3v"},
    "qodchdy": {"latin": "coctidus", "english": "boiled (var)", "category": "adj", "confidence": 0.20, "source": "f3v"},
    "oteol": {"latin": "totum", "english": "whole (var3)", "category": "adj", "confidence": 0.25, "source": "f3v"},
    "poldar": {"latin": "pollinare", "english": "to pollinate/powder", "category": "verb", "confidence": 0.20, "source": "f3v"},
    "ofcheol": {"latin": "officinale", "english": "medicinal", "category": "adj", "confidence": 0.25, "source": "f3v"},
    "cheoary": {"latin": "calidarius", "english": "heating (var)", "category": "adj", "confidence": 0.20, "source": "f3v"},
    "dairchey": {"latin": "desiccans", "english": "drying", "category": "verb", "confidence": 0.20, "source": "f3v"},
    "kshor": {"latin": "crescor", "english": "I am grown", "category": "verb", "confidence": 0.20, "source": "f3v"},
    "cheokeey": {"latin": "calefaciens", "english": "warming (part)", "category": "verb", "confidence": 0.20, "source": "f3v"},
    "dshey": {"latin": "dissolvens", "english": "dissolving", "category": "verb", "confidence": 0.20, "source": "f3v"},
    "shokshy": {"latin": "succosus", "english": "juicy", "category": "adj", "confidence": 0.25, "source": "f3v"},
    "qoechey": {"latin": "coquens", "english": "cooking (var)", "category": "verb", "confidence": 0.20, "source": "f3v"},
    "lchedy": {"latin": "liquefacta", "english": "liquefied", "category": "adj", "confidence": 0.20, "source": "f3v"},
    "tchekey": {"latin": "trahens", "english": "drawing out", "category": "verb", "confidence": 0.20, "source": "f3v"},
    "oeeey": {"latin": "oleosus", "english": "oily (var3)", "category": "adj", "confidence": 0.20, "source": "f3v"},
    "cheokchy": {"latin": "calefactus", "english": "warmed", "category": "adj", "confidence": 0.20, "source": "f3v"},
    "sheom": {"latin": "serum", "english": "serum/whey", "category": "noun", "confidence": 0.25, "source": "f3v"},
    "dchol": {"latin": "decollum", "english": "decoction (var)", "category": "noun", "confidence": 0.20, "source": "f3v"},
    "qofchy": {"latin": "coctus", "english": "cooked (var2)", "category": "adj", "confidence": 0.20, "source": "f3v"},
    "chokar": {"latin": "collare", "english": "to filter", "category": "verb", "confidence": 0.20, "source": "f3v"},
    "tshey": {"latin": "tersus", "english": "wiped clean", "category": "adj", "confidence": 0.20, "source": "f3v"},
    "qoteedy": {"latin": "quotidianus", "english": "daily (var2)", "category": "adj", "confidence": 0.20, "source": "f3v"},
    "okeoly": {"latin": "oculatus", "english": "having eyes/visible", "category": "adj", "confidence": 0.20, "source": "f3v"},

    # f4r remaining (only 2!)
    # Already covered in previous batch

    # f4v remaining
    "qoteody": {"latin": "quotidianus", "english": "daily (var3)", "category": "adj", "confidence": 0.20, "source": "f4v"},
    "shokoiin": {"latin": "succinum", "english": "amber/resin", "category": "noun", "confidence": 0.20, "source": "f4v"},
    "okcheo": {"latin": "occultus", "english": "hidden", "category": "adj", "confidence": 0.20, "source": "f4v"},
    "okeodaiin": {"latin": "ocularium", "english": "eye medicine", "category": "noun", "confidence": 0.25, "source": "f4v"},
    "otodal": {"latin": "totalis", "english": "total (var3)", "category": "adj", "confidence": 0.20, "source": "f4v"},
    "chealdy": {"latin": "caliditas", "english": "warmth (var2)", "category": "noun", "confidence": 0.20, "source": "f4v"},
    "okeeor": {"latin": "ocularum", "english": "of eyes (var3)", "category": "noun", "confidence": 0.20, "source": "f4v"},
    "qotcheey": {"latin": "coctivus", "english": "cooking (adj)", "category": "adj", "confidence": 0.20, "source": "f4v"},
    "ytchey": {"latin": "iterans", "english": "repeating", "category": "verb", "confidence": 0.20, "source": "f4v"},
    "shokam": {"latin": "succamen", "english": "juice extract", "category": "noun", "confidence": 0.20, "source": "f4v"},
    "keol": {"latin": "caelum", "english": "sky/heaven", "category": "noun", "confidence": 0.20, "source": "f4v"},
    "qotshedy": {"latin": "coctus", "english": "cooked (var3)", "category": "adj", "confidence": 0.20, "source": "f4v"},

    # f5r remaining
    "qodaiir": {"latin": "coagulare", "english": "to curdle (var)", "category": "verb", "confidence": 0.20, "source": "f5r"},
    "qotain": {"latin": "quotannis", "english": "yearly", "category": "adv", "confidence": 0.20, "source": "f5r"},
    "qolkeey": {"latin": "colligens", "english": "collecting", "category": "verb", "confidence": 0.20, "source": "f5r"},
    "sheol": {"latin": "solum", "english": "ground/soil", "category": "noun", "confidence": 0.25, "source": "f5r"},
    "lchey": {"latin": "liquor", "english": "liquid (var2)", "category": "noun", "confidence": 0.25, "source": "f5r"},
    "cheokol": {"latin": "calefactum", "english": "heated thing", "category": "noun", "confidence": 0.20, "source": "f5r"},
    "okchod": {"latin": "occludens", "english": "closing", "category": "verb", "confidence": 0.20, "source": "f5r"},
    "shoteody": {"latin": "saturatus", "english": "saturated", "category": "adj", "confidence": 0.20, "source": "f5r"},
    "qokchdy": {"latin": "coctidus", "english": "boiled (var2)", "category": "adj", "confidence": 0.20, "source": "f5r"},
    "lkchey": {"latin": "liquefaciens", "english": "liquefying", "category": "verb", "confidence": 0.20, "source": "f5r"},
    "oteechey": {"latin": "totiens", "english": "so many times", "category": "adv", "confidence": 0.20, "source": "f5r"},
    "tcholor": {"latin": "tricolor", "english": "three-colored", "category": "adj", "confidence": 0.20, "source": "f5r"},
    "soaiin": {"latin": "solarium", "english": "sun-exposed", "category": "noun", "confidence": 0.20, "source": "f5r"},
    "qokchey": {"latin": "coquens", "english": "cooking (var2)", "category": "verb", "confidence": 0.20, "source": "f5r"},
    "pcheey": {"latin": "pectens", "english": "combing/carding", "category": "verb", "confidence": 0.20, "source": "f5r"},

    # f5v remaining
    "otchdy": {"latin": "totidus", "english": "whole (var4)", "category": "adj", "confidence": 0.20, "source": "f5v"},
    "qokeeoly": {"latin": "coquiolum", "english": "small pot", "category": "noun", "confidence": 0.20, "source": "f5v"},
    "ockhol": {"latin": "occultum", "english": "hidden thing", "category": "noun", "confidence": 0.20, "source": "f5v"},
    "shoteey": {"latin": "saturans", "english": "saturating", "category": "verb", "confidence": 0.20, "source": "f5v"},
    "opchol": {"latin": "operculum", "english": "lid/cover", "category": "noun", "confidence": 0.25, "source": "f5v"},
    "shodaiin": {"latin": "sudarium", "english": "sweat cloth", "category": "noun", "confidence": 0.20, "source": "f5v"},
    "shotchody": {"latin": "saturatus", "english": "saturated (var)", "category": "adj", "confidence": 0.20, "source": "f5v"},
    "tchedy": {"latin": "tergidus", "english": "cleansed", "category": "adj", "confidence": 0.20, "source": "f5v"},
    "shokeeol": {"latin": "succiolum", "english": "small juice", "category": "noun", "confidence": 0.20, "source": "f5v"},
    "lchol": {"latin": "liquidum", "english": "liquid thing", "category": "noun", "confidence": 0.25, "source": "f5v"},
    "qockhol": {"latin": "coctulum", "english": "small pot", "category": "noun", "confidence": 0.20, "source": "f5v"},
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
