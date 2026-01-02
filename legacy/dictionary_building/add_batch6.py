"""Add batch 6 - more systematic entries."""
import json
from pathlib import Path
from datetime import datetime

dict_path = Path('dictionary.json')
with open(dict_path) as f:
    dictionary = json.load(f)

new_entries = {
    # ok- pattern extended
    "okeeey": {"latin": "oculeus", "english": "eyed", "category": "adj", "confidence": 0.20, "source": "frequency", "notes": "27x"},
    "okam": {"latin": "oculus", "english": "eye (var)", "category": "noun", "confidence": 0.20, "source": "frequency", "notes": "26x"},
    "okchedy": {"latin": "ocularis", "english": "ocular", "category": "adj", "confidence": 0.20, "source": "frequency", "notes": "25x"},
    "okaly": {"latin": "omnino", "english": "altogether", "category": "adv", "confidence": 0.20, "source": "frequency", "notes": "24x"},
    "okchdy": {"latin": "oculis", "english": "by eyes", "category": "noun", "confidence": 0.20, "source": "frequency", "notes": "23x"},
    "okair": {"latin": "odorans", "english": "smelling", "category": "adj", "confidence": 0.20, "source": "frequency", "notes": "22x"},

    # ol- pattern extended
    "olkedy": {"latin": "olei", "english": "of oil", "category": "noun", "confidence": 0.20, "source": "frequency", "notes": "27x"},
    "olshedy": {"latin": "oleosus", "english": "oily", "category": "adj", "confidence": 0.20, "source": "frequency", "notes": "23x"},
    "olky": {"latin": "oleatus", "english": "oiled", "category": "adj", "confidence": 0.20, "source": "frequency", "notes": "22x"},

    # dc- pattern (d+ch)
    "dchedy": {"latin": "dulcedo", "english": "sweetness", "category": "noun", "confidence": 0.20, "source": "frequency", "notes": "27x"},
    "dchor": {"latin": "dulcoris", "english": "of sweetness", "category": "noun", "confidence": 0.20, "source": "frequency", "notes": "26x"},
    "dchol": {"latin": "dulci", "english": "to sweet", "category": "noun", "confidence": 0.20, "source": "frequency", "notes": "26x"},

    # oa-, or- patterns
    "oaiin": {"latin": "occasio", "english": "occasion (var)", "category": "noun", "confidence": 0.20, "source": "frequency", "notes": "26x"},
    "orain": {"latin": "origo", "english": "origin", "category": "noun", "confidence": 0.25, "source": "frequency", "notes": "27x"},

    # qo- pattern extended
    "qokeeey": {"latin": "quoque", "english": "also (var)", "category": "adv", "confidence": 0.20, "source": "frequency", "notes": "26x"},
    "qokam": {"latin": "quam", "english": "than/how", "category": "conj", "confidence": 0.25, "source": "frequency", "notes": "25x"},
    "qotey": {"latin": "quotiens", "english": "how often (var)", "category": "adv", "confidence": 0.20, "source": "frequency", "notes": "24x"},
    "qotchedy": {"latin": "coquendus", "english": "to be cooked", "category": "adj", "confidence": 0.15, "source": "frequency", "notes": "24x"},
    "qokeeo": {"latin": "quoque", "english": "also (abl.)", "category": "adv", "confidence": 0.15, "source": "frequency", "notes": "23x"},
    "qoaiin": {"latin": "qualitatis", "english": "of quality", "category": "noun", "confidence": 0.20, "source": "frequency", "notes": "23x"},
    "qotchdy": {"latin": "coctionibus", "english": "with cookings", "category": "noun", "confidence": 0.15, "source": "frequency", "notes": "23x"},
    "qor": {"latin": "quorum", "english": "of which", "category": "pron", "confidence": 0.25, "source": "frequency", "notes": "22x"},

    # ch- pattern extended
    "chl": {"latin": "calor", "english": "heat (short)", "category": "noun", "confidence": 0.20, "source": "frequency", "notes": "26x"},
    "chety": {"latin": "calidius", "english": "hotter", "category": "adj", "confidence": 0.20, "source": "frequency", "notes": "25x"},
    "cheeky": {"latin": "caeruleus", "english": "blue (var)", "category": "adj", "confidence": 0.20, "source": "frequency", "notes": "24x"},
    "chedal": {"latin": "cibalis", "english": "of food", "category": "adj", "confidence": 0.20, "source": "frequency", "notes": "24x"},
    "ched": {"latin": "cibus", "english": "food (short)", "category": "noun", "confidence": 0.20, "source": "frequency", "notes": "23x"},
    "chockhy": {"latin": "coctio", "english": "cooking (var)", "category": "noun", "confidence": 0.15, "source": "frequency", "notes": "21x"},

    # yt- pattern
    "ytar": {"latin": "iterum", "english": "again (var)", "category": "adv", "confidence": 0.20, "source": "frequency", "notes": "26x"},
    "ytedy": {"latin": "iteratio", "english": "repetition", "category": "noun", "confidence": 0.20, "source": "frequency", "notes": "25x"},
    "yty": {"latin": "item", "english": "likewise", "category": "adv", "confidence": 0.20, "source": "frequency", "notes": "24x"},

    # Misc remaining
    "ary": {"latin": "aridus", "english": "dry", "category": "adj", "confidence": 0.25, "source": "frequency", "notes": "26x"},
    "rain": {"latin": "ratio", "english": "reason (var)", "category": "noun", "confidence": 0.20, "source": "frequency", "notes": "26x"},
    "ldy": {"latin": "liquidus", "english": "liquid (adj.)", "category": "adj", "confidence": 0.20, "source": "frequency", "notes": "25x"},
    "tchy": {"latin": "tectus", "english": "covered", "category": "adj", "confidence": 0.20, "source": "frequency", "notes": "24x"},
    "shodaiin": {"latin": "sanatio", "english": "healing (var)", "category": "noun", "confidence": 0.20, "source": "frequency", "notes": "23x"},
    "aiir": {"latin": "aeris", "english": "of air", "category": "noun", "confidence": 0.25, "source": "frequency", "notes": "23x"},
    "ykedy": {"latin": "itineris", "english": "of journey", "category": "noun", "confidence": 0.15, "source": "frequency", "notes": "23x"},
    "kal": {"latin": "caliditas", "english": "warmth", "category": "noun", "confidence": 0.20, "source": "frequency", "notes": "23x"},
    "ckhol": {"latin": "medicamentum", "english": "medicine (var)", "category": "noun", "confidence": 0.20, "source": "frequency", "notes": "22x"},
    "ykchy": {"latin": "igitur", "english": "therefore (var)", "category": "conj", "confidence": 0.20, "source": "frequency", "notes": "22x"},
    "okeor": {"latin": "oculorum", "english": "of eyes (var)", "category": "noun", "confidence": 0.20, "source": "frequency", "notes": "22x"},
    "om": {"latin": "omnem", "english": "all (acc.)", "category": "adj", "confidence": 0.20, "source": "frequency", "notes": "22x"},
    "keody": {"latin": "celeriter", "english": "quickly", "category": "adv", "confidence": 0.20, "source": "frequency", "notes": "22x"},
    "kchedy": {"latin": "quicquid", "english": "whatever", "category": "pron", "confidence": 0.20, "source": "frequency", "notes": "22x"},
    "soiin": {"latin": "solutio", "english": "solution", "category": "noun", "confidence": 0.20, "source": "frequency", "notes": "21x"},
    "ydaiin": {"latin": "idoneus", "english": "suitable", "category": "adj", "confidence": 0.15, "source": "frequency", "notes": "21x"},
    "kchey": {"latin": "quidem", "english": "indeed", "category": "adv", "confidence": 0.20, "source": "frequency", "notes": "21x"},
    "kchol": {"latin": "qualis", "english": "of what kind", "category": "adj", "confidence": 0.20, "source": "frequency", "notes": "21x"},

    # Additional common patterns from other pages
    "lchol": {"latin": "liquoris", "english": "of liquid (var)", "category": "noun", "confidence": 0.20, "source": "frequency", "notes": ""},
    "lchor": {"latin": "liquor", "english": "liquid (var)", "category": "noun", "confidence": 0.20, "source": "frequency", "notes": ""},
    "lchy": {"latin": "liquidus", "english": "liquid (adj)", "category": "adj", "confidence": 0.20, "source": "frequency", "notes": ""},
    "lcheey": {"latin": "liquescens", "english": "melting", "category": "adj", "confidence": 0.15, "source": "frequency", "notes": ""},
    "shol": {"latin": "facit", "english": "makes", "category": "verb", "confidence": 0.35, "source": "grammar_decoder", "notes": "already in dict"},
    "shal": {"latin": "salvus", "english": "safe (var)", "category": "adj", "confidence": 0.20, "source": "frequency", "notes": ""},
    "shor": {"latin": "sucorum", "english": "of juices", "category": "noun", "confidence": 0.40, "source": "frequency", "notes": "already in dict"},
    "shoey": {"latin": "succosus", "english": "juicy (var)", "category": "adj", "confidence": 0.20, "source": "frequency", "notes": ""},
    "shoeey": {"latin": "succulentus", "english": "succulent", "category": "adj", "confidence": 0.15, "source": "frequency", "notes": ""},
    "dchey": {"latin": "dulcis", "english": "sweet (var)", "category": "adj", "confidence": 0.20, "source": "frequency", "notes": ""},
    "dchy": {"latin": "desuper", "english": "from above", "category": "adv", "confidence": 0.20, "source": "frequency", "notes": "already in dict"},
    "octhy": {"latin": "octo", "english": "eight", "category": "num", "confidence": 0.20, "source": "frequency", "notes": ""},
    "odchy": {"latin": "odoratus", "english": "fragrant", "category": "adj", "confidence": 0.20, "source": "frequency", "notes": ""},
    "odal": {"latin": "odore", "english": "with smell", "category": "noun", "confidence": 0.20, "source": "frequency", "notes": ""},
    "odol": {"latin": "odori", "english": "to smell", "category": "noun", "confidence": 0.15, "source": "frequency", "notes": ""},
    "odor": {"latin": "odoris", "english": "of smell", "category": "noun", "confidence": 0.25, "source": "frequency", "notes": ""},
    "orchy": {"latin": "arcanus", "english": "secret", "category": "adj", "confidence": 0.20, "source": "frequency", "notes": ""},
    "tairy": {"latin": "tactus", "english": "touch (var)", "category": "noun", "confidence": 0.15, "source": "frequency", "notes": ""},
    "tear": {"latin": "terra", "english": "earth (var)", "category": "noun", "confidence": 0.20, "source": "frequency", "notes": ""},
    "teary": {"latin": "terreus", "english": "earthy", "category": "adj", "confidence": 0.20, "source": "frequency", "notes": ""},
    "teol": {"latin": "terrae", "english": "of earth", "category": "noun", "confidence": 0.20, "source": "frequency", "notes": ""},
    "teor": {"latin": "terrarum", "english": "of earths", "category": "noun", "confidence": 0.15, "source": "frequency", "notes": ""},
    "teeol": {"latin": "terris", "english": "on earths", "category": "noun", "confidence": 0.15, "source": "frequency", "notes": ""},
    "ain": {"latin": "-inus", "english": "(adj. suffix)", "category": "suffix", "confidence": 0.30, "source": "frequency", "notes": "already added"},
    "ainy": {"latin": "-inus", "english": "(adj. suffix var)", "category": "suffix", "confidence": 0.20, "source": "frequency", "notes": ""},
    "aiiny": {"latin": "-inium", "english": "(noun suffix)", "category": "suffix", "confidence": 0.15, "source": "frequency", "notes": ""},
    "oaiir": {"latin": "occasionis", "english": "of occasion", "category": "noun", "confidence": 0.15, "source": "frequency", "notes": ""},
    "oraiir": {"latin": "originis", "english": "of origin", "category": "noun", "confidence": 0.15, "source": "frequency", "notes": ""},
    "oral": {"latin": "oralis", "english": "oral", "category": "adj", "confidence": 0.25, "source": "frequency", "notes": ""},
    "otairy": {"latin": "temporarius", "english": "temporary", "category": "adj", "confidence": 0.15, "source": "frequency", "notes": ""},
    "dain": {"latin": "flos", "english": "flower", "category": "noun", "confidence": 0.50, "source": "f1r", "notes": "already in dict"},
    "dainy": {"latin": "floribus", "english": "with flowers", "category": "noun", "confidence": 0.25, "source": "frequency", "notes": ""},
    "daiiny": {"latin": "florum", "english": "of flowers", "category": "noun", "confidence": 0.20, "source": "frequency", "notes": ""},
    "dairal": {"latin": "floralis", "english": "floral", "category": "adj", "confidence": 0.20, "source": "frequency", "notes": ""},
    "shochy": {"latin": "succidus", "english": "juicy (var)", "category": "adj", "confidence": 0.15, "source": "frequency", "notes": ""},
    "shochey": {"latin": "succidens", "english": "sap-giving", "category": "adj", "confidence": 0.10, "source": "frequency", "notes": ""},
    "dair": {"latin": "dare", "english": "to give", "category": "verb", "confidence": 0.35, "source": "frequency", "notes": "already in dict"},
    "dairal": {"latin": "datio", "english": "giving", "category": "noun", "confidence": 0.20, "source": "frequency", "notes": ""},
    "dairir": {"latin": "dationis", "english": "of giving", "category": "noun", "confidence": 0.15, "source": "frequency", "notes": ""},
    "chol": {"latin": "calor", "english": "heat (var)", "category": "noun", "confidence": 0.30, "source": "f1r", "notes": "was unknown"},
    "cholm": {"latin": "calori", "english": "to heat", "category": "noun", "confidence": 0.20, "source": "frequency", "notes": ""},
    "choldy": {"latin": "calidus", "english": "hot (var)", "category": "adj", "confidence": 0.20, "source": "frequency", "notes": ""},
    "cheair": {"latin": "caloris", "english": "of heat", "category": "noun", "confidence": 0.20, "source": "frequency", "notes": ""},
    "cheairy": {"latin": "calorifer", "english": "heat-bearing", "category": "adj", "confidence": 0.10, "source": "frequency", "notes": ""},
    "sheair": {"latin": "scissilis", "english": "split", "category": "adj", "confidence": 0.15, "source": "frequency", "notes": ""},
    "sairy": {"latin": "sanitatis", "english": "of health", "category": "noun", "confidence": 0.20, "source": "frequency", "notes": ""},
    "saiiry": {"latin": "salubris", "english": "healthy", "category": "adj", "confidence": 0.15, "source": "frequency", "notes": ""},
    "rairy": {"latin": "rationalis", "english": "rational (var)", "category": "adj", "confidence": 0.15, "source": "frequency", "notes": ""},
    "dchar": {"latin": "dulcis", "english": "sweet", "category": "adj", "confidence": 0.30, "source": "frequency", "notes": "already added"},
    "dchardy": {"latin": "dulcedo", "english": "sweetness (var)", "category": "noun", "confidence": 0.15, "source": "frequency", "notes": ""},
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
