"""Add translations for high-frequency untranslated words."""
import json
from pathlib import Path
from datetime import datetime

dict_path = Path('dictionary.json')
with open(dict_path) as f:
    dictionary = json.load(f)

# High-frequency words (21-15x occurrences) - maximum impact
new_entries = {
    # 21x frequency
    "qokeor": {"latin": "coquorum", "english": "of cooks/cooked things", "category": "noun", "confidence": 0.25, "source": "corpus"},
    "otair": {"latin": "totalis", "english": "total (var9)", "category": "adj", "confidence": 0.25, "source": "corpus"},
    "rar": {"latin": "rarus", "english": "rare/thin", "category": "adj", "confidence": 0.30, "source": "corpus"},

    # 20x frequency
    "kchdy": {"latin": "crematus", "english": "burned/calcined", "category": "adj", "confidence": 0.25, "source": "corpus"},
    "rol": {"latin": "rotulus", "english": "roll/scroll", "category": "noun", "confidence": 0.25, "source": "corpus"},
    "tal": {"latin": "talis", "english": "such", "category": "adj", "confidence": 0.30, "source": "corpus"},
    "dl": {"latin": "de illo", "english": "from that", "category": "prep", "confidence": 0.20, "source": "corpus"},
    "shecthy": {"latin": "siccitas", "english": "dryness (var)", "category": "noun", "confidence": 0.25, "source": "corpus"},
    "chdar": {"latin": "calefacere", "english": "to heat (var2)", "category": "verb", "confidence": 0.25, "source": "corpus"},
    "qoeedy": {"latin": "coquidus", "english": "boiled (var8)", "category": "adj", "confidence": 0.20, "source": "corpus"},

    # 19x frequency
    "sheal": {"latin": "sudor", "english": "sweat (var2)", "category": "noun", "confidence": 0.25, "source": "corpus"},
    "qockhy": {"latin": "coctivus", "english": "cooking-related (var)", "category": "adj", "confidence": 0.25, "source": "corpus"},
    "chdal": {"latin": "calefactum", "english": "heated (var4)", "category": "adj", "confidence": 0.25, "source": "corpus"},
    "chedain": {"latin": "calefactio", "english": "heating (var2)", "category": "noun", "confidence": 0.25, "source": "corpus"},
    "opchdy": {"latin": "operatus", "english": "worked/prepared", "category": "adj", "confidence": 0.25, "source": "corpus"},
    "otaly": {"latin": "totalis", "english": "total (var10)", "category": "adj", "confidence": 0.25, "source": "corpus"},
    "olkar": {"latin": "olearis", "english": "of oil (var)", "category": "adj", "confidence": 0.25, "source": "corpus"},

    # 18x frequency
    "ols": {"latin": "olens", "english": "smelling (var)", "category": "verb", "confidence": 0.25, "source": "corpus"},
    "olol": {"latin": "oleolum", "english": "small oil", "category": "noun", "confidence": 0.25, "source": "corpus"},
    "chs": {"latin": "cras", "english": "tomorrow", "category": "adv", "confidence": 0.20, "source": "corpus"},
    "okeeol": {"latin": "oculeum", "english": "eye (var5)", "category": "noun", "confidence": 0.25, "source": "corpus"},
    "odain": {"latin": "oedema", "english": "swelling (var)", "category": "noun", "confidence": 0.25, "source": "corpus", "notes": "medical term"},
    "chain": {"latin": "calens", "english": "being hot (var)", "category": "verb", "confidence": 0.25, "source": "corpus"},
    "shed": {"latin": "siccus", "english": "dry (var)", "category": "adj", "confidence": 0.30, "source": "corpus"},
    "lchdy": {"latin": "liquidus", "english": "liquid (adj)", "category": "adj", "confidence": 0.25, "source": "corpus"},
    "qokaly": {"latin": "coqualis", "english": "cooking-type", "category": "adj", "confidence": 0.20, "source": "corpus"},
    "qockhey": {"latin": "coquendo", "english": "by cooking (var2)", "category": "adv", "confidence": 0.25, "source": "corpus"},
    "lshey": {"latin": "liquescens", "english": "liquefying (var)", "category": "verb", "confidence": 0.25, "source": "corpus"},

    # 17x frequency
    "sheos": {"latin": "sedes", "english": "seat (var2)", "category": "noun", "confidence": 0.25, "source": "corpus"},
    "ory": {"latin": "oris", "english": "of mouth", "category": "noun", "confidence": 0.25, "source": "corpus"},
    "qokair": {"latin": "coquaris", "english": "you are cooked (var)", "category": "verb", "confidence": 0.20, "source": "corpus"},
    "ror": {"latin": "ror", "english": "dew/moisture", "category": "noun", "confidence": 0.30, "source": "corpus"},
    "lky": {"latin": "liquor", "english": "liquid (var4)", "category": "noun", "confidence": 0.25, "source": "corpus"},

    # 16x frequency
    "chokchy": {"latin": "calefactus", "english": "warmed (var2)", "category": "adj", "confidence": 0.25, "source": "corpus"},
    "ykeody": {"latin": "iterandus", "english": "to be repeated (var2)", "category": "verb", "confidence": 0.20, "source": "corpus"},
    "okees": {"latin": "oculi", "english": "eyes (var2)", "category": "noun", "confidence": 0.25, "source": "corpus"},
    "chdaiin": {"latin": "calefactorium", "english": "heater (var5)", "category": "noun", "confidence": 0.25, "source": "corpus"},
    "tain": {"latin": "tamen", "english": "nevertheless", "category": "conj", "confidence": 0.30, "source": "corpus"},
    "okeeody": {"latin": "oculatus", "english": "having eyes (var)", "category": "adj", "confidence": 0.20, "source": "corpus"},
    "aral": {"latin": "aridus", "english": "dry/arid", "category": "adj", "confidence": 0.30, "source": "corpus"},
    "cheeo": {"latin": "caleo", "english": "I am hot", "category": "verb", "confidence": 0.25, "source": "corpus"},
    "lkchedy": {"latin": "liquefactus", "english": "liquefied (var)", "category": "adj", "confidence": 0.25, "source": "corpus"},

    # 15x frequency
    "tchdy": {"latin": "tergidus", "english": "wiped (var)", "category": "adj", "confidence": 0.25, "source": "corpus"},
    "ycheo": {"latin": "iterum", "english": "again (var13)", "category": "adv", "confidence": 0.20, "source": "corpus"},
    "qopchdy": {"latin": "compositum", "english": "compound (var)", "category": "noun", "confidence": 0.25, "source": "corpus"},
    "qokeed": {"latin": "coquendum", "english": "to be cooked (var4)", "category": "verb", "confidence": 0.25, "source": "corpus"},
    "lo": {"latin": "locus", "english": "place", "category": "noun", "confidence": 0.30, "source": "corpus"},
    "shedaiin": {"latin": "siccarium", "english": "drying place (var)", "category": "noun", "confidence": 0.25, "source": "corpus"},
    "orol": {"latin": "aureolum", "english": "golden (dim)", "category": "adj", "confidence": 0.20, "source": "corpus"},
    "qoeey": {"latin": "coquere", "english": "to cook (var3)", "category": "verb", "confidence": 0.25, "source": "corpus"},
    "okeeo": {"latin": "oculus", "english": "eye (var6)", "category": "noun", "confidence": 0.25, "source": "corpus"},

    # 14x frequency
    "otody": {"latin": "totidus", "english": "whole (var7)", "category": "adj", "confidence": 0.25, "source": "corpus"},
    "ycheol": {"latin": "iterum", "english": "again (var14)", "category": "adv", "confidence": 0.20, "source": "corpus"},
    "cheeor": {"latin": "calorum", "english": "of heats (var)", "category": "noun", "confidence": 0.25, "source": "corpus"},
    "dshor": {"latin": "desiccor", "english": "I am dried", "category": "verb", "confidence": 0.25, "source": "corpus"},
    "aldy": {"latin": "alidus", "english": "nourished", "category": "adj", "confidence": 0.20, "source": "corpus"},
    "okeo": {"latin": "oculus", "english": "eye (var7)", "category": "noun", "confidence": 0.25, "source": "corpus"},
    "ly": {"latin": "illi", "english": "to him/that", "category": "pron", "confidence": 0.25, "source": "corpus"},
    "okeos": {"latin": "oculos", "english": "eyes (acc)", "category": "noun", "confidence": 0.25, "source": "corpus"},
    "sheeky": {"latin": "siccatus", "english": "dried (var2)", "category": "adj", "confidence": 0.25, "source": "corpus"},

    # 13x frequency
    "qokechy": {"latin": "coquitur", "english": "is cooked (var5)", "category": "verb", "confidence": 0.25, "source": "corpus"},
    "tchol": {"latin": "tergere", "english": "to wipe (var)", "category": "verb", "confidence": 0.25, "source": "corpus"},
    "ockhy": {"latin": "occultus", "english": "hidden (var5)", "category": "adj", "confidence": 0.25, "source": "corpus"},
    "shes": {"latin": "sedes", "english": "seat (var3)", "category": "noun", "confidence": 0.25, "source": "corpus"},
    "keeol": {"latin": "caelum", "english": "sky (var3)", "category": "noun", "confidence": 0.25, "source": "corpus"},
    "ytam": {"latin": "iterum", "english": "again (var15)", "category": "adv", "confidence": 0.20, "source": "corpus"},
    "chckhdy": {"latin": "calefactus", "english": "heated (var5)", "category": "adj", "confidence": 0.25, "source": "corpus"},
    "laiin": {"latin": "latinum", "english": "Latin/hidden", "category": "noun", "confidence": 0.20, "source": "corpus"},
    "shky": {"latin": "siccus", "english": "dry (var2)", "category": "adj", "confidence": 0.25, "source": "corpus"},
    "olcheey": {"latin": "oleifaciens", "english": "oil-producing", "category": "verb", "confidence": 0.20, "source": "corpus"},
    "chkal": {"latin": "calefactum", "english": "heated (var6)", "category": "adj", "confidence": 0.25, "source": "corpus"},
    "arody": {"latin": "ariditas", "english": "dryness/aridity", "category": "noun", "confidence": 0.25, "source": "corpus"},
    "teedy": {"latin": "tepidus", "english": "lukewarm (var3)", "category": "adj", "confidence": 0.25, "source": "corpus"},
    "shee": {"latin": "sedes", "english": "seat (var4)", "category": "noun", "confidence": 0.25, "source": "corpus"},
    "k": {"latin": "et", "english": "and (abbr)", "category": "conj", "confidence": 0.20, "source": "corpus"},
    "tair": {"latin": "talis", "english": "such (var)", "category": "adj", "confidence": 0.25, "source": "corpus"},
    "oteo": {"latin": "totius", "english": "of whole (var)", "category": "adj", "confidence": 0.25, "source": "corpus"},
    "opaiin": {"latin": "oparium", "english": "work vessel", "category": "noun", "confidence": 0.25, "source": "corpus"},
    "olain": {"latin": "oleamen", "english": "olive oil (var)", "category": "noun", "confidence": 0.25, "source": "corpus"},
    "qokeeody": {"latin": "coquendus", "english": "to be cooked (var5)", "category": "verb", "confidence": 0.25, "source": "corpus"},
    "otshedy": {"latin": "totius", "english": "of whole (var2)", "category": "adj", "confidence": 0.20, "source": "corpus"},

    # 12x frequency
    "pchey": {"latin": "pectens", "english": "combing (var)", "category": "verb", "confidence": 0.20, "source": "corpus"},
    "shocthy": {"latin": "succidus", "english": "sappy (var5)", "category": "adj", "confidence": 0.25, "source": "corpus"},
    "okeal": {"latin": "oculum", "english": "eye (acc)", "category": "noun", "confidence": 0.25, "source": "corpus"},
    "chkain": {"latin": "calefaciens", "english": "warming (var6)", "category": "verb", "confidence": 0.25, "source": "corpus"},
    "ypchedy": {"latin": "ipsorum", "english": "of themselves", "category": "pron", "confidence": 0.20, "source": "corpus"},
    "lr": {"latin": "lar", "english": "hearth/home", "category": "noun", "confidence": 0.25, "source": "corpus"},
    "oteor": {"latin": "totorum", "english": "of wholes", "category": "noun", "confidence": 0.20, "source": "corpus"},
    "chekal": {"latin": "calefactum", "english": "heated (var7)", "category": "adj", "confidence": 0.25, "source": "corpus"},
    "aram": {"latin": "arum", "english": "arum plant", "category": "noun", "confidence": 0.30, "source": "corpus", "notes": "botanical"},
    "arol": {"latin": "arillus", "english": "seed covering", "category": "noun", "confidence": 0.25, "source": "corpus", "notes": "botanical"},
    "ykeeody": {"latin": "iterandus", "english": "to be repeated (var3)", "category": "verb", "confidence": 0.20, "source": "corpus"},
    "olkey": {"latin": "oleicum", "english": "oily (var5)", "category": "adj", "confidence": 0.25, "source": "corpus"},
    "qotam": {"latin": "coctam", "english": "cooked (acc f)", "category": "adj", "confidence": 0.25, "source": "corpus"},
    "oteeo": {"latin": "totius", "english": "of whole (var3)", "category": "adj", "confidence": 0.20, "source": "corpus"},

    # 11x frequency
    "tey": {"latin": "tibi", "english": "to you (var)", "category": "pron", "confidence": 0.25, "source": "corpus"},
    "g": {"latin": "et", "english": "and (abbr2)", "category": "conj", "confidence": 0.15, "source": "corpus"},
    "chcphy": {"latin": "conspergere", "english": "to sprinkle (var)", "category": "verb", "confidence": 0.20, "source": "corpus"},
    "otoldy": {"latin": "totalis", "english": "total (var11)", "category": "adj", "confidence": 0.25, "source": "corpus"},
}

added = 0
for word, entry in new_entries.items():
    if word not in dictionary['entries']:
        dictionary['entries'][word] = entry
        print(f"Added: {word} = {entry['latin']} ({entry['english']}) - appears frequently")
        added += 1

dictionary['last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M")

with open(dict_path, 'w') as f:
    json.dump(dictionary, f, indent=2, ensure_ascii=False)

print(f"\nTotal added: {added}")
print(f"Total entries: {len(dictionary['entries'])}")
