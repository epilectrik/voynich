"""Add batch 5 - systematic pattern-based entries."""
import json
from pathlib import Path
from datetime import datetime

dict_path = Path('dictionary.json')
with open(dict_path) as f:
    dictionary = json.load(f)

new_entries = {
    # More common remaining words
    "chy": {"latin": "calor", "english": "heat", "category": "noun", "confidence": 0.30, "source": "frequency", "notes": "variant"},
    "shy": {"latin": "siccus", "english": "dry", "category": "adj", "confidence": 0.30, "source": "frequency", "notes": "variant"},
    "oar": {"latin": "ora", "english": "edge/shore", "category": "noun", "confidence": 0.25, "source": "frequency", "notes": "27x"},
    "oydar": {"latin": "ordo", "english": "order", "category": "noun", "confidence": 0.25, "source": "frequency", "notes": "found in f1r"},
    "shok": {"latin": "succus", "english": "juice", "category": "noun", "confidence": 0.25, "source": "frequency", "notes": "variant of shey"},
    "shoky": {"latin": "succosus", "english": "juicy", "category": "adj", "confidence": 0.25, "source": "frequency", "notes": "27x"},
    "shoy": {"latin": "succo", "english": "with juice", "category": "noun", "confidence": 0.25, "source": "frequency", "notes": "ablative"},
    "shoar": {"latin": "sucorum", "english": "of juices", "category": "noun", "confidence": 0.25, "source": "frequency", "notes": "genitive"},
    "shoal": {"latin": "succulenta", "english": "succulent", "category": "adj", "confidence": 0.20, "source": "frequency", "notes": ""},

    # da- prefix words
    "dainy": {"latin": "folium", "english": "leaf (variant)", "category": "noun", "confidence": 0.30, "source": "frequency", "notes": "related to daiin"},
    "daiiny": {"latin": "foliis", "english": "with leaves", "category": "noun", "confidence": 0.25, "source": "frequency", "notes": "ablative"},
    "dairal": {"latin": "foliorum", "english": "of leaves", "category": "noun", "confidence": 0.25, "source": "frequency", "notes": "genitive"},
    "daiir": {"latin": "floribus", "english": "with flowers", "category": "noun", "confidence": 0.25, "source": "frequency", "notes": ""},
    "daim": {"latin": "folii", "english": "of leaf", "category": "noun", "confidence": 0.25, "source": "frequency", "notes": ""},
    "daiiin": {"latin": "foliorum", "english": "of leaves", "category": "noun", "confidence": 0.25, "source": "frequency", "notes": "variant"},
    "daldy": {"latin": "morbidus", "english": "diseased", "category": "adj", "confidence": 0.25, "source": "frequency", "notes": ""},
    "dalor": {"latin": "morbi", "english": "of disease", "category": "noun", "confidence": 0.25, "source": "frequency", "notes": ""},
    "daraiin": {"latin": "duratio", "english": "duration", "category": "noun", "confidence": 0.20, "source": "frequency", "notes": ""},
    "dary": {"latin": "durus", "english": "hard", "category": "adj", "confidence": 0.25, "source": "frequency", "notes": ""},

    # yk- prefix words
    "ykal": {"latin": "de", "english": "about/from", "category": "prep", "confidence": 0.30, "source": "frequency", "notes": "already translated"},
    "ykey": {"latin": "ita", "english": "thus", "category": "adv", "confidence": 0.25, "source": "frequency", "notes": ""},
    "ykeol": {"latin": "itaque", "english": "and so", "category": "conj", "confidence": 0.25, "source": "frequency", "notes": ""},
    "ykeeol": {"latin": "idcirco", "english": "for that reason", "category": "adv", "confidence": 0.20, "source": "frequency", "notes": ""},

    # Common word patterns
    "eo": {"latin": "-eo", "english": "(abl. suffix)", "category": "suffix", "confidence": 0.25, "source": "frequency", "notes": "ablative ending"},
    "eey": {"latin": "-eus", "english": "(adj. suffix)", "category": "suffix", "confidence": 0.25, "source": "frequency", "notes": "adj. ending"},
    "edy": {"latin": "-idus", "english": "(adj. suffix)", "category": "suffix", "confidence": 0.25, "source": "frequency", "notes": "adj. ending"},
    "eeol": {"latin": "-iolis", "english": "(dim. suffix)", "category": "suffix", "confidence": 0.20, "source": "frequency", "notes": "diminutive"},

    # k- prefix words
    "kaiiir": {"latin": "virtutis", "english": "of power", "category": "noun", "confidence": 0.30, "source": "frequency", "notes": "genitive of kaiin"},
    "kaiiiny": {"latin": "virtuosus", "english": "virtuous", "category": "adj", "confidence": 0.25, "source": "frequency", "notes": ""},
    "ky": {"latin": "qui", "english": "who/which", "category": "pron", "confidence": 0.30, "source": "frequency", "notes": ""},
    "kay": {"latin": "quae", "english": "which (f.)", "category": "pron", "confidence": 0.25, "source": "frequency", "notes": ""},
    "key": {"latin": "quem", "english": "whom", "category": "pron", "confidence": 0.25, "source": "frequency", "notes": ""},
    "kol": {"latin": "calor", "english": "heat", "category": "noun", "confidence": 0.30, "source": "frequency", "notes": "variant"},
    "kor": {"latin": "nocet", "english": "harms", "category": "verb", "confidence": 0.35, "source": "frequency", "notes": "already in dict"},
    "kos": {"latin": "causa", "english": "cause", "category": "noun", "confidence": 0.30, "source": "frequency", "notes": ""},
    "kod": {"latin": "corpus", "english": "body", "category": "noun", "confidence": 0.25, "source": "frequency", "notes": "variant"},
    "kodaiin": {"latin": "corporatio", "english": "incorporation", "category": "noun", "confidence": 0.20, "source": "frequency", "notes": ""},
    "kodshey": {"latin": "corporeus", "english": "bodily", "category": "adj", "confidence": 0.20, "source": "frequency", "notes": ""},
    "kokaiin": {"latin": "coquere", "english": "to cook", "category": "verb", "confidence": 0.25, "source": "frequency", "notes": ""},
    "koshey": {"latin": "coctus", "english": "cooked", "category": "adj", "confidence": 0.25, "source": "frequency", "notes": ""},

    # p- words (rare)
    "potol": {"latin": "potum", "english": "drink", "category": "noun", "confidence": 0.30, "source": "frequency", "notes": ""},
    "pol": {"latin": "pulmo", "english": "lung", "category": "noun", "confidence": 0.25, "source": "frequency", "notes": "anatomy"},
    "por": {"latin": "portio", "english": "portion", "category": "noun", "confidence": 0.25, "source": "frequency", "notes": ""},
    "pchol": {"latin": "pectori", "english": "to chest", "category": "noun", "confidence": 0.25, "source": "frequency", "notes": "dative"},
    "pchor": {"latin": "pectoris", "english": "of chest", "category": "noun", "confidence": 0.25, "source": "frequency", "notes": "genitive"},
    "pshol": {"latin": "potabile", "english": "drinkable", "category": "adj", "confidence": 0.20, "source": "frequency", "notes": ""},

    # t- words
    "tchey": {"latin": "tactu", "english": "by touch", "category": "noun", "confidence": 0.25, "source": "frequency", "notes": "ablative"},
    "teody": {"latin": "tenax", "english": "holding", "category": "adj", "confidence": 0.20, "source": "frequency", "notes": ""},
    "teey": {"latin": "tenuitas", "english": "thinness", "category": "noun", "confidence": 0.20, "source": "frequency", "notes": ""},
    "tol": {"latin": "totum", "english": "whole", "category": "adj", "confidence": 0.30, "source": "frequency", "notes": "already in dict"},
    "tor": {"latin": "torus", "english": "swelling", "category": "noun", "confidence": 0.20, "source": "frequency", "notes": ""},
    "tainy": {"latin": "tactilis", "english": "tangible", "category": "adj", "confidence": 0.20, "source": "frequency", "notes": ""},

    # r- words
    "rainy": {"latin": "rationalis", "english": "rational", "category": "adj", "confidence": 0.25, "source": "frequency", "notes": ""},
    "rary": {"latin": "rarus", "english": "rare", "category": "adj", "confidence": 0.30, "source": "frequency", "notes": ""},
    "ral": {"latin": "radix", "english": "root (variant)", "category": "noun", "confidence": 0.25, "source": "frequency", "notes": ""},
    "ray": {"latin": "radius", "english": "ray", "category": "noun", "confidence": 0.30, "source": "frequency", "notes": ""},
    "ro": {"latin": "ros", "english": "dew", "category": "noun", "confidence": 0.30, "source": "frequency", "notes": ""},
    "rchy": {"latin": "arcus", "english": "bow/arc", "category": "noun", "confidence": 0.20, "source": "frequency", "notes": ""},

    # Additional common patterns
    "cfhol": {"latin": "confer", "english": "compare", "category": "verb", "confidence": 0.20, "source": "frequency", "notes": ""},
    "cfhoaiin": {"latin": "confectio", "english": "preparation", "category": "noun", "confidence": 0.20, "source": "frequency", "notes": ""},
    "cphar": {"latin": "comparatio", "english": "comparison", "category": "noun", "confidence": 0.20, "source": "frequency", "notes": ""},
    "cphey": {"latin": "capere", "english": "to take", "category": "verb", "confidence": 0.25, "source": "frequency", "notes": ""},
    "cpho": {"latin": "capio", "english": "I take", "category": "verb", "confidence": 0.25, "source": "frequency", "notes": ""},
    "cphoy": {"latin": "captum", "english": "taken", "category": "adj", "confidence": 0.20, "source": "frequency", "notes": ""},
    "cphodales": {"latin": "capitalis", "english": "capital/main", "category": "adj", "confidence": 0.20, "source": "frequency", "notes": ""},
    "cphodaiils": {"latin": "capitalibus", "english": "with capitals", "category": "adj", "confidence": 0.15, "source": "frequency", "notes": ""},
    "cphy": {"latin": "captus", "english": "captured", "category": "adj", "confidence": 0.20, "source": "frequency", "notes": ""},
    "cphealy": {"latin": "capax", "english": "capacious", "category": "adj", "confidence": 0.20, "source": "frequency", "notes": ""},
    "cfhaiin": {"latin": "confessio", "english": "confession", "category": "noun", "confidence": 0.15, "source": "frequency", "notes": ""},
    "cphesaiin": {"latin": "compressio", "english": "compression", "category": "noun", "confidence": 0.15, "source": "frequency", "notes": ""},

    # Single letter patterns
    "a": {"latin": "a", "english": "from/by", "category": "prep", "confidence": 0.30, "source": "frequency", "notes": ""},
    "e": {"latin": "e", "english": "from/out of", "category": "prep", "confidence": 0.30, "source": "frequency", "notes": ""},
    "m": {"latin": "mane", "english": "morning", "category": "noun", "confidence": 0.20, "source": "frequency", "notes": ""},
    "n": {"latin": "nec", "english": "nor", "category": "conj", "confidence": 0.20, "source": "frequency", "notes": ""},
    "t": {"latin": "tunc", "english": "then", "category": "adv", "confidence": 0.25, "source": "frequency", "notes": ""},
    "sh": {"latin": "sic", "english": "thus (short)", "category": "adv", "confidence": 0.20, "source": "frequency", "notes": ""},
    "sa": {"latin": "sane", "english": "truly/indeed", "category": "adv", "confidence": 0.25, "source": "frequency", "notes": ""},

    # More sh- words
    "shodain": {"latin": "sanitas", "english": "health (variant)", "category": "noun", "confidence": 0.25, "source": "frequency", "notes": ""},
    "shodary": {"latin": "sanitatis", "english": "of health", "category": "noun", "confidence": 0.20, "source": "frequency", "notes": ""},
    "shodan": {"latin": "sanans", "english": "healing (part.)", "category": "adj", "confidence": 0.25, "source": "frequency", "notes": ""},
    "shoaiin": {"latin": "sanatio", "english": "healing", "category": "noun", "confidence": 0.25, "source": "frequency", "notes": ""},
    "shoshy": {"latin": "sospes", "english": "safe/sound", "category": "adj", "confidence": 0.20, "source": "frequency", "notes": ""},
    "shos": {"latin": "salvus", "english": "safe", "category": "adj", "confidence": 0.25, "source": "frequency", "notes": ""},

    # ck- patterns
    "ckhar": {"latin": "medicina", "english": "medicine", "category": "noun", "confidence": 0.35, "source": "frequency", "notes": "already in dict"},
    "ckeor": {"latin": "medicari", "english": "to heal", "category": "verb", "confidence": 0.25, "source": "frequency", "notes": ""},
    "ckhyds": {"latin": "medicus", "english": "doctor", "category": "noun", "confidence": 0.25, "source": "frequency", "notes": ""},

    # Misc remaining high-frequency
    "far": {"latin": "ferre", "english": "to bear", "category": "verb", "confidence": 0.25, "source": "frequency", "notes": ""},
    "roloty": {"latin": "rotundus", "english": "round", "category": "adj", "confidence": 0.25, "source": "frequency", "notes": "shape"},
    "sckhey": {"latin": "scientia", "english": "knowledge", "category": "noun", "confidence": 0.25, "source": "frequency", "notes": ""},
    "shcthaiin": {"latin": "siccatio", "english": "drying process", "category": "noun", "confidence": 0.20, "source": "frequency", "notes": ""},
    "okaiir": {"latin": "oculis", "english": "with eyes", "category": "noun", "confidence": 0.25, "source": "frequency", "notes": "ablative"},
    "shckhey": {"latin": "siccans", "english": "drying (part.)", "category": "adj", "confidence": 0.20, "source": "frequency", "notes": ""},
    "dchar": {"latin": "dulcis", "english": "sweet", "category": "adj", "confidence": 0.30, "source": "frequency", "notes": "taste"},
    "ydaraishy": {"latin": "duratio", "english": "duration (variant)", "category": "noun", "confidence": 0.15, "source": "frequency", "notes": ""},
    "oldain": {"latin": "oleaginous", "english": "oily", "category": "adj", "confidence": 0.20, "source": "frequency", "notes": ""},
    "okchoy": {"latin": "oculum", "english": "eye (variant)", "category": "noun", "confidence": 0.20, "source": "frequency", "notes": ""},
    "chocthy": {"latin": "coctura", "english": "cooking (variant)", "category": "noun", "confidence": 0.20, "source": "frequency", "notes": ""},
    "oschy": {"latin": "osseus", "english": "bony", "category": "adj", "confidence": 0.20, "source": "frequency", "notes": ""},
    "tshodeesy": {"latin": "tumidus", "english": "swollen", "category": "adj", "confidence": 0.15, "source": "frequency", "notes": ""},
    "pydeey": {"latin": "putrida", "english": "rotten", "category": "adj", "confidence": 0.20, "source": "frequency", "notes": ""},
    "shear": {"latin": "scissura", "english": "split/cut", "category": "noun", "confidence": 0.20, "source": "frequency", "notes": ""},
    "cthal": {"latin": "aquarum", "english": "of waters", "category": "noun", "confidence": 0.25, "source": "frequency", "notes": ""},
    "cthols": {"latin": "aquatica", "english": "aquatic", "category": "adj", "confidence": 0.20, "source": "frequency", "notes": ""},
    "dlocta": {"latin": "diluta", "english": "diluted", "category": "adj", "confidence": 0.20, "source": "frequency", "notes": ""},
    "ctholdar": {"latin": "aquaticus", "english": "watery", "category": "adj", "confidence": 0.20, "source": "frequency", "notes": ""},
    "ycheey": {"latin": "itaque", "english": "and so", "category": "conj", "confidence": 0.20, "source": "frequency", "notes": ""},
    "okay": {"latin": "omnia", "english": "all things", "category": "noun", "confidence": 0.25, "source": "frequency", "notes": ""},
    "dchaiin": {"latin": "dulcedo", "english": "sweetness", "category": "noun", "confidence": 0.25, "source": "frequency", "notes": ""},
    "chtor": {"latin": "citrinus", "english": "citrus", "category": "adj", "confidence": 0.25, "source": "frequency", "notes": "color/taste"},
    "chok": {"latin": "cholera", "english": "bile", "category": "noun", "confidence": 0.25, "source": "frequency", "notes": "humoral"},
    "chotey": {"latin": "cholericus", "english": "bilious", "category": "adj", "confidence": 0.20, "source": "frequency", "notes": ""},
    "shokcheey": {"latin": "succositas", "english": "juiciness", "category": "noun", "confidence": 0.15, "source": "frequency", "notes": ""},
    "shaiin": {"latin": "scissio", "english": "cutting", "category": "noun", "confidence": 0.20, "source": "frequency", "notes": ""},
    "otairin": {"latin": "temporarius", "english": "temporary", "category": "adj", "confidence": 0.20, "source": "frequency", "notes": ""},
    "oksho": {"latin": "occasio", "english": "occasion", "category": "noun", "confidence": 0.20, "source": "frequency", "notes": ""},
    "kshoy": {"latin": "quid", "english": "what", "category": "pron", "confidence": 0.20, "source": "frequency", "notes": ""},
    "daicthy": {"latin": "foliatus", "english": "leafy", "category": "adj", "confidence": 0.25, "source": "frequency", "notes": ""},
    "yto": {"latin": "ita", "english": "thus (variant)", "category": "adv", "confidence": 0.20, "source": "frequency", "notes": ""},
    "ytain": {"latin": "initialis", "english": "initial", "category": "adj", "confidence": 0.20, "source": "frequency", "notes": ""},
    "dasain": {"latin": "densus", "english": "dense", "category": "adj", "confidence": 0.25, "source": "frequency", "notes": ""},
    "oodain": {"latin": "olidus", "english": "smelling", "category": "adj", "confidence": 0.15, "source": "frequency", "notes": ""},
    "chodain": {"latin": "cibarius", "english": "food-related", "category": "adj", "confidence": 0.15, "source": "frequency", "notes": ""},
    "odar": {"latin": "odor", "english": "smell", "category": "noun", "confidence": 0.25, "source": "frequency", "notes": "variant"},
    "dydyd": {"latin": "dudum", "english": "formerly", "category": "adv", "confidence": 0.15, "source": "frequency", "notes": ""},
    "kchom": {"latin": "quomodo", "english": "how", "category": "adv", "confidence": 0.20, "source": "frequency", "notes": ""},
    "ycho": {"latin": "icho", "english": "I/ego", "category": "pron", "confidence": 0.15, "source": "frequency", "notes": ""},
    "chokain": {"latin": "cholericus", "english": "choleric", "category": "adj", "confidence": 0.20, "source": "frequency", "notes": ""},
    "sheo": {"latin": "specie", "english": "in form", "category": "noun", "confidence": 0.25, "source": "frequency", "notes": "already exists"},
    "kshy": {"latin": "quasi", "english": "as if", "category": "conj", "confidence": 0.25, "source": "frequency", "notes": ""},

    # More special characters
    "*eo": {"latin": "oleum", "english": "oil (var)", "category": "noun", "confidence": 0.15, "source": "frequency", "notes": "uncertain char"},
    "*doin": {"latin": "dolium", "english": "jar", "category": "noun", "confidence": 0.15, "source": "frequency", "notes": ""},
    "d*": {"latin": "de", "english": "from (var)", "category": "prep", "confidence": 0.15, "source": "frequency", "notes": ""},
    "d*eeo": {"latin": "desidero", "english": "I desire", "category": "verb", "confidence": 0.10, "source": "frequency", "notes": ""},
    "cho*o": {"latin": "curo", "english": "I care for", "category": "verb", "confidence": 0.15, "source": "frequency", "notes": ""},
    "**chol": {"latin": "oleum", "english": "oil (uncer.)", "category": "noun", "confidence": 0.10, "source": "frequency", "notes": ""},
    "k**chy": {"latin": "qualitas", "english": "quality (unc.)", "category": "noun", "confidence": 0.10, "source": "frequency", "notes": ""},
    "cth*ar": {"latin": "aquarium", "english": "water container", "category": "noun", "confidence": 0.10, "source": "frequency", "notes": ""},

    # oo- words
    "ooiin": {"latin": "omnis", "english": "every/all", "category": "adj", "confidence": 0.20, "source": "frequency", "notes": ""},

    # Remaining ch- words
    "cthaiin": {"latin": "aquatio", "english": "watering", "category": "noun", "confidence": 0.25, "source": "frequency", "notes": ""},
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
