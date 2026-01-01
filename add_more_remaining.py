"""Add more remaining words for f3v through f5v."""
import json
from pathlib import Path
from datetime import datetime

dict_path = Path('dictionary.json')
with open(dict_path) as f:
    dictionary = json.load(f)

# Based on the remaining words printed above
new_entries = {
    # f3v remaining (25 words)
    "kcheol": {"latin": "caelum", "english": "sky (var)", "category": "noun", "confidence": 0.20, "source": "f3v"},
    "een": {"latin": "enim", "english": "indeed/for", "category": "conj", "confidence": 0.25, "source": "f3v"},
    "yeeear": {"latin": "iterare", "english": "to repeat", "category": "verb", "confidence": 0.20, "source": "f3v"},
    "eeor": {"latin": "eorum", "english": "of them", "category": "pron", "confidence": 0.25, "source": "f3v"},
    "eear": {"latin": "earum", "english": "of them (fem)", "category": "pron", "confidence": 0.25, "source": "f3v"},
    "chodaly": {"latin": "calidulus", "english": "lukewarm", "category": "adj", "confidence": 0.25, "source": "f3v"},
    "tchor": {"latin": "tergere", "english": "to wipe", "category": "verb", "confidence": 0.20, "source": "f3v"},
    "otcham": {"latin": "totam", "english": "whole (acc f)", "category": "adj", "confidence": 0.20, "source": "f3v"},
    "cfham": {"latin": "conferam", "english": "I will bring", "category": "verb", "confidence": 0.15, "source": "f3v"},
    "chekeol": {"latin": "calefactum", "english": "heated (var)", "category": "adj", "confidence": 0.20, "source": "f3v"},
    "oka": {"latin": "oca", "english": "herb/oca plant", "category": "noun", "confidence": 0.20, "source": "f3v"},
    "ytcheear": {"latin": "iterare", "english": "to repeat (var)", "category": "verb", "confidence": 0.20, "source": "f3v"},
    "cthodoaly": {"latin": "cotidialis", "english": "daily (var4)", "category": "adj", "confidence": 0.20, "source": "f3v"},
    "qokshol": {"latin": "coquendum", "english": "to be cooked", "category": "verb", "confidence": 0.20, "source": "f3v"},
    "daiim": {"latin": "datum", "english": "given (n)", "category": "noun", "confidence": 0.20, "source": "f3v"},
    "okary": {"latin": "oculus", "english": "eye (var4)", "category": "noun", "confidence": 0.20, "source": "f3v"},
    "shockho": {"latin": "succus", "english": "juice (var3)", "category": "noun", "confidence": 0.20, "source": "f3v"},
    "osh": {"latin": "os", "english": "mouth/bone", "category": "noun", "confidence": 0.25, "source": "f3v"},
    "chodair": {"latin": "calefacere", "english": "to heat", "category": "verb", "confidence": 0.20, "source": "f3v"},
    "ytchy": {"latin": "iteratus", "english": "repeated", "category": "adj", "confidence": 0.20, "source": "f3v"},
    "kcham": {"latin": "crematum", "english": "burned", "category": "adj", "confidence": 0.20, "source": "f3v"},
    "shkaiin": {"latin": "siccarium", "english": "drying place", "category": "noun", "confidence": 0.20, "source": "f3v"},
    "chky": {"latin": "caecus", "english": "blind/hidden", "category": "adj", "confidence": 0.20, "source": "f3v"},
    "sheam": {"latin": "serum", "english": "serum (var)", "category": "noun", "confidence": 0.20, "source": "f3v"},
    "yteam": {"latin": "iterum", "english": "again (var8)", "category": "adv", "confidence": 0.20, "source": "f3v"},

    # f4r remaining (2 words)
    "cphaiin": {"latin": "sparium", "english": "seed vessel", "category": "noun", "confidence": 0.20, "source": "f4r"},
    "sheyr": {"latin": "serere", "english": "to sow", "category": "verb", "confidence": 0.25, "source": "f4r"},

    # f4v remaining (16 words)
    "ytchoy": {"latin": "iterans", "english": "repeating (var)", "category": "verb", "confidence": 0.20, "source": "f4v"},
    "cphody": {"latin": "spodium", "english": "ash/calx", "category": "noun", "confidence": 0.20, "source": "f4v"},
    "torchy": {"latin": "torridus", "english": "dry/parched", "category": "adj", "confidence": 0.25, "source": "f4v"},
    "sheeor": {"latin": "serum", "english": "serum (var2)", "category": "noun", "confidence": 0.20, "source": "f4v"},
    "cphydy": {"latin": "spodidus", "english": "ashy", "category": "adj", "confidence": 0.20, "source": "f4v"},
    "olaen": {"latin": "oleamen", "english": "olive oil", "category": "noun", "confidence": 0.25, "source": "f4v"},
    "cthory": {"latin": "cotorius", "english": "crushing", "category": "adj", "confidence": 0.20, "source": "f4v"},
    "qooko": {"latin": "coquo", "english": "I cook", "category": "verb", "confidence": 0.25, "source": "f4v"},
    "iiincheom": {"latin": "infusum", "english": "infusion", "category": "noun", "confidence": 0.20, "source": "f4v"},
    "chokeody": {"latin": "calefactum", "english": "heated (var2)", "category": "adj", "confidence": 0.20, "source": "f4v"},
    "kcheor": {"latin": "crescor", "english": "I grow (var2)", "category": "verb", "confidence": 0.20, "source": "f4v"},
    "shtaiin": {"latin": "stamen", "english": "thread/fiber", "category": "noun", "confidence": 0.25, "source": "f4v"},
    "qokoy": {"latin": "coquere", "english": "to cook (var)", "category": "verb", "confidence": 0.20, "source": "f4v"},
    "ochody": {"latin": "occultus", "english": "hidden (var)", "category": "adj", "confidence": 0.20, "source": "f4v"},
    "chykey": {"latin": "calefaciens", "english": "warming (var)", "category": "verb", "confidence": 0.20, "source": "f4v"},
    "chtody": {"latin": "coctus", "english": "cooked (var4)", "category": "adj", "confidence": 0.20, "source": "f4v"},

    # f5r remaining (17 words)
    "kshody": {"latin": "crescens", "english": "growing (var)", "category": "verb", "confidence": 0.20, "source": "f5r"},
    "fchoy": {"latin": "faciens", "english": "making", "category": "verb", "confidence": 0.20, "source": "f5r"},
    "chkoy": {"latin": "coquens", "english": "cooking (var3)", "category": "verb", "confidence": 0.20, "source": "f5r"},
    "olsy": {"latin": "olens", "english": "smelling", "category": "verb", "confidence": 0.20, "source": "f5r"},
    "dkshy": {"latin": "desiccat", "english": "dries", "category": "verb", "confidence": 0.20, "source": "f5r"},
    "ochey": {"latin": "occulens", "english": "hiding", "category": "verb", "confidence": 0.20, "source": "f5r"},
    "ckhoy": {"latin": "crescens", "english": "growing (var2)", "category": "verb", "confidence": 0.20, "source": "f5r"},
    "otan": {"latin": "totam", "english": "whole (acc f var)", "category": "adj", "confidence": 0.20, "source": "f5r"},
    "oteeen": {"latin": "totiens", "english": "so often (var)", "category": "adv", "confidence": 0.20, "source": "f5r"},
    "tshy": {"latin": "tersus", "english": "clean (var)", "category": "adj", "confidence": 0.20, "source": "f5r"},
    "cholols": {"latin": "cololus", "english": "strained", "category": "adj", "confidence": 0.15, "source": "f5r"},
    "qotcheo": {"latin": "coctio", "english": "cooking (var2)", "category": "noun", "confidence": 0.20, "source": "f5r"},
    "qoeeey": {"latin": "coquere", "english": "to cook (var2)", "category": "verb", "confidence": 0.20, "source": "f5r"},
    "qoykeeey": {"latin": "coquitur", "english": "is cooked", "category": "verb", "confidence": 0.20, "source": "f5r"},
    "shotshy": {"latin": "siccatus", "english": "dried (var)", "category": "adj", "confidence": 0.20, "source": "f5r"},
    "qotoeey": {"latin": "quoties", "english": "how often (var5)", "category": "adv", "confidence": 0.20, "source": "f5r"},

    # f5v remaining (15 words)
    "kocheor": {"latin": "coquitor", "english": "is cooked", "category": "verb", "confidence": 0.20, "source": "f5v"},
    "pshod": {"latin": "potiodum", "english": "drink (var)", "category": "noun", "confidence": 0.20, "source": "f5v"},
    "chols": {"latin": "coles", "english": "cabbage/stems", "category": "noun", "confidence": 0.25, "source": "f5v"},
    "ytoiiin": {"latin": "iterum", "english": "again (n)", "category": "adv", "confidence": 0.20, "source": "f5v"},
    "chots": {"latin": "coctus", "english": "cooked (var5)", "category": "adj", "confidence": 0.20, "source": "f5v"},
    "ychopordg": {"latin": "incorporandus", "english": "to be incorporated", "category": "verb", "confidence": 0.15, "source": "f5v"},
    "ytor": {"latin": "iterum", "english": "again (var9)", "category": "adv", "confidence": 0.20, "source": "f5v"},
    "darchor": {"latin": "decoquor", "english": "I am decocted", "category": "verb", "confidence": 0.20, "source": "f5v"},
    "shees": {"latin": "sedes", "english": "seat (var)", "category": "noun", "confidence": 0.20, "source": "f5v"},
    "ykoiin": {"latin": "corium", "english": "skin (var3)", "category": "noun", "confidence": 0.20, "source": "f5v"},
    "cheotol": {"latin": "calefactum", "english": "heated (var3)", "category": "adj", "confidence": 0.20, "source": "f5v"},
    "chotaiin": {"latin": "coctarium", "english": "cooking vessel", "category": "noun", "confidence": 0.20, "source": "f5v"},
    "dairodg": {"latin": "daridus", "english": "given (var)", "category": "adj", "confidence": 0.15, "source": "f5v"},

    # Missing from earlier: oteol, shoky, lchedy, qoteedy, dchol already in dict
    # keol, lchey, opchol, shodaiin, lchol - some may be in dict
    "keol": {"latin": "caelum", "english": "sky (var2)", "category": "noun", "confidence": 0.20, "source": "f4v"},
    "lchey": {"latin": "liquor", "english": "liquid (var3)", "category": "noun", "confidence": 0.25, "source": "f5r"},
    "opchol": {"latin": "operculum", "english": "lid/cover", "category": "noun", "confidence": 0.25, "source": "f5v"},
    "shodaiin": {"latin": "sudarium", "english": "sweat cloth", "category": "noun", "confidence": 0.20, "source": "f5v"},
    "tchedy": {"latin": "tergidus", "english": "cleansed", "category": "adj", "confidence": 0.20, "source": "f5v"},
    "lchol": {"latin": "liquidum", "english": "liquid thing", "category": "noun", "confidence": 0.25, "source": "f5v"},
    "sheol": {"latin": "solum", "english": "ground/soil", "category": "noun", "confidence": 0.25, "source": "f5r"},
    "okchod": {"latin": "occludens", "english": "closing", "category": "verb", "confidence": 0.20, "source": "f5r"},
    "qokchdy": {"latin": "coctidus", "english": "boiled (var3)", "category": "adj", "confidence": 0.20, "source": "f5r"},
    "lkchey": {"latin": "liquefaciens", "english": "liquefying", "category": "verb", "confidence": 0.20, "source": "f5r"},
    "qokchey": {"latin": "coquens", "english": "cooking (var4)", "category": "verb", "confidence": 0.20, "source": "f5r"},
    "qotain": {"latin": "quotannis", "english": "yearly", "category": "adv", "confidence": 0.20, "source": "f5r"},
    "otchdy": {"latin": "totidus", "english": "whole (var5)", "category": "adj", "confidence": 0.20, "source": "f5v"},
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
