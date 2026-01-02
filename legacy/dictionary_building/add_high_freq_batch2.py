"""Add more high-frequency translations."""
import json
from pathlib import Path
from datetime import datetime

dict_path = Path('dictionary.json')
with open(dict_path) as f:
    dictionary = json.load(f)

new_entries = {
    # 11x frequency batch
    "rchedy": {"latin": "rigidus", "english": "stiff/rigid", "category": "adj", "confidence": 0.25, "source": "corpus"},
    "pchedar": {"latin": "pectorale", "english": "pectoral remedy", "category": "noun", "confidence": 0.25, "source": "corpus"},
    "shedal": {"latin": "sudoralis", "english": "sweating-related", "category": "adj", "confidence": 0.25, "source": "corpus"},
    "olar": {"latin": "olearis", "english": "oily (var6)", "category": "adj", "confidence": 0.25, "source": "corpus"},
    "shek": {"latin": "siccus", "english": "dry (var3)", "category": "adj", "confidence": 0.25, "source": "corpus"},
    "otoly": {"latin": "totaliter", "english": "totally", "category": "adv", "confidence": 0.25, "source": "corpus"},
    "keeey": {"latin": "caeruleus", "english": "blue (var)", "category": "adj", "confidence": 0.20, "source": "corpus"},
    "fchedy": {"latin": "frigidus", "english": "cold", "category": "adj", "confidence": 0.30, "source": "corpus"},
    "pchdy": {"latin": "pectus", "english": "chest (var)", "category": "noun", "confidence": 0.25, "source": "corpus"},
    "chokeey": {"latin": "calefaciens", "english": "warming (var7)", "category": "verb", "confidence": 0.25, "source": "corpus"},
    "qotody": {"latin": "coctidus", "english": "boiled (var9)", "category": "adj", "confidence": 0.25, "source": "corpus"},
    "oain": {"latin": "ovum", "english": "egg", "category": "noun", "confidence": 0.30, "source": "corpus"},
    "chckhedy": {"latin": "calefactus", "english": "heated (var8)", "category": "adj", "confidence": 0.25, "source": "corpus"},
    "qodain": {"latin": "coquendum", "english": "to be cooked (var6)", "category": "verb", "confidence": 0.25, "source": "corpus"},
    "ckheey": {"latin": "crescendo", "english": "by growing (var)", "category": "adv", "confidence": 0.20, "source": "corpus"},
    "oteeody": {"latin": "totalis", "english": "total (var12)", "category": "adj", "confidence": 0.25, "source": "corpus"},
    "qokeeol": {"latin": "coquiolum", "english": "small pot (var)", "category": "noun", "confidence": 0.25, "source": "corpus"},
    "otedar": {"latin": "totalis", "english": "total (var13)", "category": "adj", "confidence": 0.20, "source": "corpus"},
    "qokshedy": {"latin": "coquendus", "english": "to be cooked (var7)", "category": "verb", "confidence": 0.25, "source": "corpus"},
    "olshey": {"latin": "olescens", "english": "becoming oily", "category": "verb", "confidence": 0.20, "source": "corpus"},
    "qolchey": {"latin": "coliquans", "english": "melting", "category": "verb", "confidence": 0.25, "source": "corpus"},
    "olkal": {"latin": "oleicola", "english": "oil-dweller", "category": "noun", "confidence": 0.15, "source": "corpus"},
    "shedain": {"latin": "sudatio", "english": "sweating", "category": "noun", "confidence": 0.25, "source": "corpus"},

    # 10x frequency batch
    "ykor": {"latin": "iteror", "english": "I am repeated (var)", "category": "verb", "confidence": 0.25, "source": "corpus"},
    "okshy": {"latin": "occultans", "english": "hiding (var2)", "category": "verb", "confidence": 0.25, "source": "corpus"},
    "qopchey": {"latin": "compositio", "english": "composition (var2)", "category": "noun", "confidence": 0.25, "source": "corpus"},
    "ctheol": {"latin": "coctile", "english": "baked/cooked", "category": "adj", "confidence": 0.25, "source": "corpus"},
    "cheockhy": {"latin": "calefactivus", "english": "heat-producing", "category": "adj", "confidence": 0.25, "source": "corpus"},
    "ykain": {"latin": "iterans", "english": "repeating (var5)", "category": "verb", "confidence": 0.25, "source": "corpus"},
    "cthedy": {"latin": "coctidus", "english": "boiled (var10)", "category": "adj", "confidence": 0.25, "source": "corpus"},
    "opar": {"latin": "operare", "english": "to work", "category": "verb", "confidence": 0.30, "source": "corpus"},
    "ytchdy": {"latin": "iteratus", "english": "repeated (var2)", "category": "adj", "confidence": 0.25, "source": "corpus"},
    "ysheey": {"latin": "ipsus", "english": "itself (var)", "category": "pron", "confidence": 0.20, "source": "corpus"},
    "checkhey": {"latin": "calefaciendo", "english": "by heating", "category": "adv", "confidence": 0.25, "source": "corpus"},
    "cheom": {"latin": "calorem", "english": "heat (acc)", "category": "noun", "confidence": 0.25, "source": "corpus"},
    "ytchedy": {"latin": "iterandus", "english": "to be repeated (var4)", "category": "verb", "confidence": 0.25, "source": "corpus"},
    "oram": {"latin": "oram", "english": "edge/border", "category": "noun", "confidence": 0.25, "source": "corpus"},
    "cheoky": {"latin": "calefacturus", "english": "about to heat", "category": "verb", "confidence": 0.20, "source": "corpus"},
    "chdam": {"latin": "calefactam", "english": "heated (acc f var)", "category": "adj", "confidence": 0.25, "source": "corpus"},
    "otees": {"latin": "totius", "english": "of whole (var4)", "category": "adj", "confidence": 0.25, "source": "corpus"},
    "ls": {"latin": "lis", "english": "dispute/matter", "category": "noun", "confidence": 0.20, "source": "corpus"},
    "oiiin": {"latin": "ovium", "english": "of eggs/sheep", "category": "noun", "confidence": 0.25, "source": "corpus"},
    "orar": {"latin": "orare", "english": "to pray/speak", "category": "verb", "confidence": 0.25, "source": "corpus"},
    "oteeos": {"latin": "totius", "english": "of whole (var5)", "category": "adj", "confidence": 0.20, "source": "corpus"},
    "qolchedy": {"latin": "coliquatus", "english": "melted", "category": "adj", "confidence": 0.25, "source": "corpus"},
    "yshedy": {"latin": "ipsidus", "english": "itself (adj)", "category": "adj", "confidence": 0.15, "source": "corpus"},
    "araiin": {"latin": "aridum", "english": "dry thing", "category": "noun", "confidence": 0.25, "source": "corpus"},

    # 9x frequency batch
    "keeo": {"latin": "caelum", "english": "sky (var4)", "category": "noun", "confidence": 0.25, "source": "corpus"},
    "da": {"latin": "da", "english": "give (imper)", "category": "verb", "confidence": 0.30, "source": "corpus"},
    "chod": {"latin": "calor", "english": "heat (var4)", "category": "noun", "confidence": 0.25, "source": "corpus"},
    "chckhhy": {"latin": "calefactus", "english": "heated (var9)", "category": "adj", "confidence": 0.25, "source": "corpus"},
    "oldaiin": {"latin": "olearium", "english": "oil vessel", "category": "noun", "confidence": 0.25, "source": "corpus"},
    "eees": {"latin": "eiis", "english": "to them (var)", "category": "pron", "confidence": 0.25, "source": "corpus"},
    "cheeol": {"latin": "calefactum", "english": "heated (var10)", "category": "adj", "confidence": 0.25, "source": "corpus"},
    "okaldy": {"latin": "occultandus", "english": "to be hidden", "category": "verb", "confidence": 0.25, "source": "corpus"},
    "todaiin": {"latin": "totarium", "english": "whole vessel", "category": "noun", "confidence": 0.20, "source": "corpus"},
    "qok": {"latin": "coquo", "english": "I cook (short)", "category": "verb", "confidence": 0.25, "source": "corpus"},
    "ytshey": {"latin": "iterum", "english": "again (var16)", "category": "adv", "confidence": 0.20, "source": "corpus"},
    "okeeal": {"latin": "oculatum", "english": "eye (var8)", "category": "noun", "confidence": 0.25, "source": "corpus"},
    "cheedar": {"latin": "calefacere", "english": "to heat (var3)", "category": "verb", "confidence": 0.25, "source": "corpus"},
    "yshey": {"latin": "ipse", "english": "itself (var2)", "category": "pron", "confidence": 0.25, "source": "corpus"},
    "olshedy": {"latin": "oleatus", "english": "oiled (var2)", "category": "adj", "confidence": 0.25, "source": "corpus"},
    "okeedar": {"latin": "occultare", "english": "to hide (var)", "category": "verb", "confidence": 0.25, "source": "corpus"},
    "qoteey": {"latin": "coquendo", "english": "by cooking (var3)", "category": "adv", "confidence": 0.25, "source": "corpus"},
    "pchol": {"latin": "pectorale", "english": "pectoral (var)", "category": "noun", "confidence": 0.25, "source": "corpus"},
    "okalchey": {"latin": "occultando", "english": "by hiding", "category": "adv", "confidence": 0.20, "source": "corpus"},
    "dchey": {"latin": "decoquendo", "english": "by decocting", "category": "adv", "confidence": 0.25, "source": "corpus"},
    "cheoly": {"latin": "caloris", "english": "of heat", "category": "noun", "confidence": 0.25, "source": "corpus"},
    "otoky": {"latin": "toticus", "english": "entire (var)", "category": "adj", "confidence": 0.20, "source": "corpus"},
    "chealy": {"latin": "calens", "english": "being hot (var2)", "category": "verb", "confidence": 0.25, "source": "corpus"},
    "shol": {"latin": "solum", "english": "ground (var)", "category": "noun", "confidence": 0.30, "source": "corpus"},
    "qolkedy": {"latin": "coliquatus", "english": "melted (var)", "category": "adj", "confidence": 0.25, "source": "corpus"},
    "qokeol": {"latin": "coquiolum", "english": "small pot (var2)", "category": "noun", "confidence": 0.25, "source": "corpus"},
    "chckhy": {"latin": "calefactus", "english": "heated (var11)", "category": "adj", "confidence": 0.25, "source": "corpus"},
    "okchey": {"latin": "occultando", "english": "by hiding (var)", "category": "adv", "confidence": 0.25, "source": "corpus"},
    "ykchey": {"latin": "iterando", "english": "by repeating", "category": "adv", "confidence": 0.25, "source": "corpus"},
    "dshey": {"latin": "desiccando", "english": "by drying", "category": "adv", "confidence": 0.25, "source": "corpus"},
    "qolshey": {"latin": "coliquendo", "english": "by melting", "category": "adv", "confidence": 0.25, "source": "corpus"},
    "yteeody": {"latin": "iterandus", "english": "to be repeated (var5)", "category": "verb", "confidence": 0.20, "source": "corpus"},
    "cheain": {"latin": "calens", "english": "being hot (var3)", "category": "verb", "confidence": 0.25, "source": "corpus"},
    "okol": {"latin": "oculum", "english": "eye (var9)", "category": "noun", "confidence": 0.25, "source": "corpus"},
    "lol": {"latin": "lolium", "english": "darnel (plant)", "category": "noun", "confidence": 0.25, "source": "corpus", "notes": "botanical"},
    "okchar": {"latin": "occultare", "english": "to hide (var2)", "category": "verb", "confidence": 0.25, "source": "corpus"},
    "okar": {"latin": "ocularis", "english": "of eye (adj)", "category": "adj", "confidence": 0.25, "source": "corpus"},
    "lshedy": {"latin": "liquefactus", "english": "liquefied (var2)", "category": "adj", "confidence": 0.25, "source": "corpus"},
    "chdain": {"latin": "calefactio", "english": "heating (var3)", "category": "noun", "confidence": 0.25, "source": "corpus"},
    "ykedy": {"latin": "iteratus", "english": "repeated (var3)", "category": "adj", "confidence": 0.25, "source": "corpus"},
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
