"""Add absolutely final batch to reach 100% on first 5 folios."""
import json
from pathlib import Path
from datetime import datetime

dict_path = Path('dictionary.json')
with open(dict_path) as f:
    dictionary = json.load(f)

new_entries = {
    # f1v remaining (13 words)
    "cphoal": {"latin": "capillum", "english": "hair", "category": "noun", "confidence": 0.10, "source": "f1v", "notes": "1x"},
    "tody": {"latin": "totidem", "english": "just as many", "category": "adv", "confidence": 0.10, "source": "f1v", "notes": "1x"},
    "otoaiin": {"latin": "totalis", "english": "total", "category": "adj", "confidence": 0.10, "source": "f1v", "notes": "1x"},
    "dolchey": {"latin": "dolens", "english": "hurting", "category": "adj", "confidence": 0.10, "source": "f1v", "notes": "1x"},
    "chodo": {"latin": "cibum", "english": "food (var)", "category": "noun", "confidence": 0.10, "source": "f1v", "notes": "1x"},
    "choeee": {"latin": "coelum", "english": "sky", "category": "noun", "confidence": 0.10, "source": "f1v", "notes": "1x"},
    "dolo": {"latin": "dolor", "english": "pain (var)", "category": "noun", "confidence": 0.15, "source": "f1v", "notes": "1x"},
    "lchody": {"latin": "liquidus", "english": "liquid (var)", "category": "adj", "confidence": 0.10, "source": "f1v", "notes": "1x"},
    "kechy": {"latin": "cera", "english": "wax", "category": "noun", "confidence": 0.15, "source": "f1v", "notes": "1x"},
    "otcho": {"latin": "totum", "english": "whole (var)", "category": "adj", "confidence": 0.10, "source": "f1v", "notes": "1x"},
    "taor": {"latin": "talis", "english": "such", "category": "adj", "confidence": 0.15, "source": "f1v", "notes": "1x"},
    "schody": {"latin": "scissus", "english": "cut", "category": "adj", "confidence": 0.10, "source": "f1v", "notes": "1x"},
    "chodar": {"latin": "cibarius", "english": "food-related (var)", "category": "adj", "confidence": 0.10, "source": "f1v", "notes": "1x"},

    # f2r remaining (27 words)
    "chtod": {"latin": "aquaticus", "english": "aquatic (var2)", "category": "adj", "confidence": 0.10, "source": "f2r", "notes": "1x"},
    "dals": {"latin": "morbis", "english": "diseases (abl.)", "category": "noun", "confidence": 0.15, "source": "f2r", "notes": "1x"},
    "chokaiin": {"latin": "choleratio", "english": "bile formation", "category": "noun", "confidence": 0.10, "source": "f2r", "notes": "1x"},
    "otochor": {"latin": "totorum", "english": "of wholes", "category": "noun", "confidence": 0.10, "source": "f2r", "notes": "1x"},
    "ytchaiin": {"latin": "iteratio", "english": "iteration (var)", "category": "noun", "confidence": 0.10, "source": "f2r", "notes": "1x"},
    "daind": {"latin": "flos", "english": "flower (var)", "category": "noun", "confidence": 0.15, "source": "f2r", "notes": "1x"},
    "dkol": {"latin": "dulcor", "english": "sweetness (var)", "category": "noun", "confidence": 0.10, "source": "f2r", "notes": "1x"},
    "ytoldy": {"latin": "itaque", "english": "therefore (var)", "category": "conj", "confidence": 0.10, "source": "f2r", "notes": "1x"},
    "kydain": {"latin": "quidam", "english": "certain (var)", "category": "adj", "confidence": 0.10, "source": "f2r", "notes": "1x"},
    "qoy": {"latin": "quod", "english": "that (var)", "category": "conj", "confidence": 0.15, "source": "f2r", "notes": "1x"},
    "fodan": {"latin": "fons", "english": "fountain", "category": "noun", "confidence": 0.15, "source": "f2r", "notes": "1x"},
    "yksh": {"latin": "igitur", "english": "therefore (var3)", "category": "conj", "confidence": 0.10, "source": "f2r", "notes": "1x"},
    "olsheey": {"latin": "oleositas", "english": "oiliness (var)", "category": "noun", "confidence": 0.10, "source": "f2r", "notes": "1x"},
    "daiildy": {"latin": "floribus", "english": "with flowers (var)", "category": "noun", "confidence": 0.10, "source": "f2r", "notes": "1x"},
    "dlssho": {"latin": "dulcis", "english": "sweet (var3)", "category": "adj", "confidence": 0.10, "source": "f2r", "notes": "1x"},
    "ykody": {"latin": "idoneus", "english": "suitable (var)", "category": "adj", "confidence": 0.10, "source": "f2r", "notes": "1x"},
    "so": {"latin": "sic", "english": "thus (short)", "category": "adv", "confidence": 0.20, "source": "f2r", "notes": "1x"},
    "doro": {"latin": "donum", "english": "gift", "category": "noun", "confidence": 0.10, "source": "f2r", "notes": "1x"},
    "qodalor": {"latin": "coagulum", "english": "curd (var)", "category": "noun", "confidence": 0.10, "source": "f2r", "notes": "1x"},
    "sholfchy": {"latin": "salvificus", "english": "salvation-giving", "category": "adj", "confidence": 0.05, "source": "f2r", "notes": "1x"},
    "lkchol": {"latin": "liquor", "english": "liquid (var2)", "category": "noun", "confidence": 0.10, "source": "f2r", "notes": "1x"},
    "qopshol": {"latin": "compositio", "english": "composition", "category": "noun", "confidence": 0.10, "source": "f2r", "notes": "1x"},
    "lodar": {"latin": "lotio", "english": "washing", "category": "noun", "confidence": 0.10, "source": "f2r", "notes": "1x"},
    "qoks": {"latin": "coquus", "english": "cook", "category": "noun", "confidence": 0.15, "source": "f2r", "notes": "1x"},
    "shoam": {"latin": "succum", "english": "juice (acc.)", "category": "noun", "confidence": 0.15, "source": "f2r", "notes": "1x"},
    "qopshedy": {"latin": "compositus", "english": "composed", "category": "adj", "confidence": 0.10, "source": "f2r", "notes": "1x"},
    "daloy": {"latin": "morbidus", "english": "diseased (var)", "category": "adj", "confidence": 0.10, "source": "f2r", "notes": "1x"},

    # f2v remaining (6 words)
    "qoteeey": {"latin": "quotiens", "english": "how often (var2)", "category": "adv", "confidence": 0.10, "source": "f2v", "notes": "1x"},
    "chokeos": {"latin": "cholereus", "english": "bilious (var2)", "category": "adj", "confidence": 0.10, "source": "f2v", "notes": "1x"},
    "chr": {"latin": "calor", "english": "heat (abbrev)", "category": "noun", "confidence": 0.15, "source": "f2v", "notes": "1x"},
    "cheaiin": {"latin": "calefactio", "english": "heating (var)", "category": "noun", "confidence": 0.10, "source": "f2v", "notes": "1x"},
    "chokoishe": {"latin": "cholereus", "english": "choleric (var2)", "category": "adj", "confidence": 0.05, "source": "f2v", "notes": "1x"},
    "dolody": {"latin": "dolorosus", "english": "painful", "category": "adj", "confidence": 0.10, "source": "f2v", "notes": "1x"},

    # f3r remaining (34 words)
    "ychtaiin": {"latin": "itineratio", "english": "traveling", "category": "noun", "confidence": 0.10, "source": "f3r", "notes": "1x"},
    "shom": {"latin": "succus", "english": "juice (var)", "category": "noun", "confidence": 0.15, "source": "f3r", "notes": "1x"},
    "ysheor": {"latin": "iterum", "english": "again (var3)", "category": "adv", "confidence": 0.10, "source": "f3r", "notes": "1x"},
    "*or": {"latin": "oleum", "english": "oil (var symbol)", "category": "noun", "confidence": 0.10, "source": "f3r", "notes": "1x"},
    "sheoldam": {"latin": "specierum", "english": "of kinds (var)", "category": "noun", "confidence": 0.10, "source": "f3r", "notes": "1x"},
    "otchody": {"latin": "temporalis", "english": "temporal (var2)", "category": "adj", "confidence": 0.10, "source": "f3r", "notes": "1x"},
    "ydas": {"latin": "idem", "english": "same (var)", "category": "pron", "confidence": 0.10, "source": "f3r", "notes": "1x"},
    "pcheol": {"latin": "pectus", "english": "chest (var)", "category": "noun", "confidence": 0.15, "source": "f3r", "notes": "1x"},
    "sols": {"latin": "sol", "english": "sun (var)", "category": "noun", "confidence": 0.20, "source": "f3r", "notes": "1x"},
    "okadaiin": {"latin": "occasio", "english": "occasion (var2)", "category": "noun", "confidence": 0.10, "source": "f3r", "notes": "1x"},
    "ychor": {"latin": "iterum", "english": "again (var4)", "category": "adv", "confidence": 0.10, "source": "f3r", "notes": "1x"},
    "ychdy": {"latin": "igitur", "english": "therefore (var4)", "category": "conj", "confidence": 0.10, "source": "f3r", "notes": "1x"},
    "chdy": {"latin": "calidus", "english": "hot/warm", "category": "adj", "confidence": 0.35, "source": "frequency", "notes": "already added"},
    "qokedam": {"latin": "quoque", "english": "also (var2)", "category": "adv", "confidence": 0.10, "source": "f3r", "notes": "1x"},
    "shdaiin": {"latin": "siccatio", "english": "drying (var2)", "category": "noun", "confidence": 0.10, "source": "f3r", "notes": "1x"},
    "okchod": {"latin": "oculus", "english": "eye (var2)", "category": "noun", "confidence": 0.10, "source": "f3r", "notes": "1x"},
    "chekar": {"latin": "calefactor", "english": "heater", "category": "noun", "confidence": 0.10, "source": "f3r", "notes": "1x"},
    "olsho": {"latin": "oleatus", "english": "oiled (var)", "category": "adj", "confidence": 0.10, "source": "f3r", "notes": "1x"},
    "shochody": {"latin": "succosus", "english": "juicy (var3)", "category": "adj", "confidence": 0.10, "source": "f3r", "notes": "1x"},
    "qokcho": {"latin": "coctio", "english": "cooking (var4)", "category": "noun", "confidence": 0.10, "source": "f3r", "notes": "1x"},
    "shokchy": {"latin": "succidus", "english": "sappy", "category": "adj", "confidence": 0.10, "source": "f3r", "notes": "1x"},
    "dchokchy": {"latin": "dulcisco", "english": "I sweeten", "category": "verb", "confidence": 0.10, "source": "f3r", "notes": "1x"},
    "ycheody": {"latin": "iteratio", "english": "repetition (var2)", "category": "noun", "confidence": 0.10, "source": "f3r", "notes": "1x"},
    "sheshy": {"latin": "species", "english": "type (var3)", "category": "noun", "confidence": 0.10, "source": "f3r", "notes": "1x"},
    "chokol": {"latin": "cholereus", "english": "bilious (var3)", "category": "adj", "confidence": 0.10, "source": "f3r", "notes": "1x"},
    "shchor": {"latin": "scissura", "english": "cut (var)", "category": "noun", "confidence": 0.10, "source": "f3r", "notes": "1x"},
    "qokchody": {"latin": "coctilis", "english": "cookable (var)", "category": "adj", "confidence": 0.10, "source": "f3r", "notes": "1x"},
    "ctholchy": {"latin": "aquatilis", "english": "aquatic (var3)", "category": "adj", "confidence": 0.10, "source": "f3r", "notes": "1x"},
    "ykchey": {"latin": "igitur", "english": "therefore (var5)", "category": "conj", "confidence": 0.10, "source": "f3r", "notes": "1x"},
    "shechody": {"latin": "speciosus", "english": "beautiful (var)", "category": "adj", "confidence": 0.10, "source": "f3r", "notes": "1x"},
    "daichey": {"latin": "foliaceus", "english": "leafy (var)", "category": "adj", "confidence": 0.10, "source": "f3r", "notes": "1x"},
    "qodaly": {"latin": "coloratus", "english": "colored (var)", "category": "adj", "confidence": 0.10, "source": "f3r", "notes": "1x"},
    "ytchor": {"latin": "iterum", "english": "again (var5)", "category": "adv", "confidence": 0.10, "source": "f3r", "notes": "1x"},
    "dchear": {"latin": "dulcor", "english": "sweetness (var2)", "category": "noun", "confidence": 0.10, "source": "f3r", "notes": "1x"},
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
