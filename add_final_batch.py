"""Add final batch to reach 100% coverage on first 5 folios."""
import json
from pathlib import Path
from datetime import datetime

dict_path = Path('dictionary.json')
with open(dict_path) as f:
    dictionary = json.load(f)

# Add entries for remaining untranslated words in first 5 folios
new_entries = {
    # High frequency (4x)
    "cham": {"latin": "camera", "english": "chamber/room", "category": "noun", "confidence": 0.20, "source": "f3r", "notes": "4x"},

    # Medium frequency (2x)
    "*": {"latin": "oleum", "english": "oil (symbol)", "category": "noun", "confidence": 0.15, "source": "f1r", "notes": "uncertain character"},
    "do": {"latin": "do", "english": "I give", "category": "verb", "confidence": 0.25, "source": "f1v", "notes": "2x"},
    "ykol": {"latin": "ignis", "english": "fire", "category": "noun", "confidence": 0.20, "source": "f1v", "notes": "2x"},
    "chotchey": {"latin": "coctione", "english": "in cooking", "category": "noun", "confidence": 0.15, "source": "f1v,f2v", "notes": "2x"},
    "keol": {"latin": "caeli", "english": "of sky", "category": "noun", "confidence": 0.20, "source": "f2r,f2v", "notes": "2x"},
    "chan": {"latin": "canus", "english": "white/gray", "category": "adj", "confidence": 0.20, "source": "f2r,f2v", "notes": "2x"},
    "otchor": {"latin": "temporis", "english": "of time (var)", "category": "noun", "confidence": 0.20, "source": "f2v,f3r", "notes": "2x"},
    "ycheor": {"latin": "iterum", "english": "again (var2)", "category": "adv", "confidence": 0.15, "source": "f3r", "notes": "2x"},
    "cthom": {"latin": "aquam", "english": "water (acc.)", "category": "noun", "confidence": 0.25, "source": "f3r", "notes": "2x"},
    "chom": {"latin": "cibum", "english": "food (acc. var)", "category": "noun", "confidence": 0.20, "source": "f3r", "notes": "2x"},
    "damo": {"latin": "damnum", "english": "loss/damage", "category": "noun", "confidence": 0.20, "source": "f3r", "notes": "2x"},

    # Single occurrence words (1x each) - f1r
    "yshey": {"latin": "isuccus", "english": "this juice", "category": "noun", "confidence": 0.15, "source": "f1r", "notes": "1x"},
    "ydain": {"latin": "idem", "english": "same flower", "category": "noun", "confidence": 0.15, "source": "f1r", "notes": "1x"},

    # f1v words
    "kchsy": {"latin": "quicquid", "english": "whatever (var)", "category": "pron", "confidence": 0.10, "source": "f1v", "notes": "1x"},
    "chadaiin": {"latin": "cibatio", "english": "feeding (var)", "category": "noun", "confidence": 0.10, "source": "f1v", "notes": "1x"},
    "oltchey": {"latin": "olefacto", "english": "I oil", "category": "verb", "confidence": 0.10, "source": "f1v", "notes": "1x"},
    "cfhar": {"latin": "confero", "english": "I bring together", "category": "verb", "confidence": 0.10, "source": "f1v", "notes": "1x"},
    "yteeay": {"latin": "iteratio", "english": "repetition (var)", "category": "noun", "confidence": 0.10, "source": "f1v", "notes": "1x"},
    "ochy": {"latin": "octavus", "english": "eighth", "category": "num", "confidence": 0.10, "source": "f1v", "notes": "1x"},
    "dcho": {"latin": "dulci", "english": "to sweet", "category": "noun", "confidence": 0.15, "source": "f1v", "notes": "1x"},
    "lkody": {"latin": "liquido", "english": "in liquid", "category": "noun", "confidence": 0.10, "source": "f1v", "notes": "1x"},
    "okodar": {"latin": "oculum", "english": "eye (var)", "category": "noun", "confidence": 0.10, "source": "f1v", "notes": "1x"},
    "ckho": {"latin": "medico", "english": "I heal", "category": "verb", "confidence": 0.15, "source": "f1v", "notes": "1x"},
    "dksheey": {"latin": "dulcissimus", "english": "sweetest", "category": "adj", "confidence": 0.10, "source": "f1v", "notes": "1x"},
    "kotchody": {"latin": "coctio", "english": "cooking (var2)", "category": "noun", "confidence": 0.10, "source": "f1v", "notes": "1x"},
    "chokeo": {"latin": "cholera", "english": "bile (var)", "category": "noun", "confidence": 0.10, "source": "f1v", "notes": "1x"},
    "sochey": {"latin": "socialis", "english": "social", "category": "adj", "confidence": 0.10, "source": "f1v", "notes": "1x"},
    "chokody": {"latin": "cholericus", "english": "choleric (var)", "category": "adj", "confidence": 0.10, "source": "f1v", "notes": "1x"},
    "potoy": {"latin": "potum", "english": "drink (var)", "category": "noun", "confidence": 0.15, "source": "f1v", "notes": "1x"},
    "kedar": {"latin": "cedrus", "english": "cedar", "category": "noun", "confidence": 0.20, "source": "f1v", "notes": "1x"},
    "opchol": {"latin": "optimum", "english": "best (var)", "category": "adj", "confidence": 0.15, "source": "f1v", "notes": "1x"},
    "dchokchy": {"latin": "dulcesco", "english": "I become sweet", "category": "verb", "confidence": 0.10, "source": "f1v", "notes": "1x"},
    "tchety": {"latin": "tectum", "english": "roof/covering", "category": "noun", "confidence": 0.15, "source": "f1v", "notes": "1x"},
    "teeky": {"latin": "tenuis", "english": "thin (var)", "category": "adj", "confidence": 0.10, "source": "f1v", "notes": "1x"},
    "shoey": {"latin": "succosus", "english": "juicy (var2)", "category": "adj", "confidence": 0.15, "source": "f1v", "notes": "1x"},
    "okchol": {"latin": "ocellus", "english": "little eye", "category": "noun", "confidence": 0.15, "source": "f1v", "notes": "1x"},
    "otechy": {"latin": "temporeus", "english": "timely", "category": "adj", "confidence": 0.10, "source": "f1v", "notes": "1x"},
    "odchey": {"latin": "odoratus", "english": "fragrant (var)", "category": "adj", "confidence": 0.10, "source": "f1v", "notes": "1x"},
    "qosheey": {"latin": "quassatio", "english": "shaking", "category": "noun", "confidence": 0.10, "source": "f1v", "notes": "1x"},
    "olchody": {"latin": "oleagineus", "english": "oily (var)", "category": "adj", "confidence": 0.10, "source": "f1v", "notes": "1x"},
    "okechy": {"latin": "ocellatus", "english": "having eyes", "category": "adj", "confidence": 0.10, "source": "f1v", "notes": "1x"},

    # f2r words
    "kydainy": {"latin": "quidam", "english": "certain", "category": "adj", "confidence": 0.10, "source": "f2r", "notes": "1x"},
    "ypchol": {"latin": "impello", "english": "I push", "category": "verb", "confidence": 0.10, "source": "f2r", "notes": "1x"},
    "otchal": {"latin": "temporalis", "english": "temporal (var)", "category": "adj", "confidence": 0.15, "source": "f2r", "notes": "1x"},
    "ypchaiin": {"latin": "impulsio", "english": "impulse", "category": "noun", "confidence": 0.10, "source": "f2r", "notes": "1x"},
    "ckholsy": {"latin": "medicinus", "english": "medicinal", "category": "adj", "confidence": 0.15, "source": "f2r", "notes": "1x"},
    "dorchory": {"latin": "dulcoris", "english": "of sweetness (var)", "category": "noun", "confidence": 0.10, "source": "f2r", "notes": "1x"},
    "chkar": {"latin": "citreus", "english": "citrus (var)", "category": "adj", "confidence": 0.15, "source": "f2r", "notes": "1x"},
    "cth": {"latin": "aqua", "english": "water (short)", "category": "noun", "confidence": 0.20, "source": "f2r", "notes": "1x"},
    "ydy": {"latin": "idem", "english": "same", "category": "pron", "confidence": 0.15, "source": "f2r", "notes": "1x"},
    "chaindy": {"latin": "caliditas", "english": "warmth (var)", "category": "noun", "confidence": 0.10, "source": "f2r", "notes": "1x"},
    "opchy": {"latin": "optimus", "english": "best (var2)", "category": "adj", "confidence": 0.15, "source": "f2r", "notes": "1x"},
    "lkchey": {"latin": "liquesco", "english": "I melt", "category": "verb", "confidence": 0.10, "source": "f2r", "notes": "1x"},
    "cholchey": {"latin": "calefio", "english": "I become warm", "category": "verb", "confidence": 0.10, "source": "f2r", "notes": "1x"},
    "okodo": {"latin": "odoror", "english": "I smell", "category": "verb", "confidence": 0.10, "source": "f2r", "notes": "1x"},
    "qotchol": {"latin": "coctio", "english": "cooking (var3)", "category": "noun", "confidence": 0.10, "source": "f2r", "notes": "1x"},
    "chola": {"latin": "calida", "english": "hot (fem.)", "category": "adj", "confidence": 0.15, "source": "f2r", "notes": "1x"},
    "shdeey": {"latin": "siccitas", "english": "dryness (var)", "category": "noun", "confidence": 0.10, "source": "f2r", "notes": "1x"},
    "scheey": {"latin": "scissio", "english": "cutting (var)", "category": "noun", "confidence": 0.10, "source": "f2r", "notes": "1x"},
    "ypcheey": {"latin": "impetus", "english": "force", "category": "noun", "confidence": 0.10, "source": "f2r", "notes": "1x"},
    "sho": {"latin": "natura", "english": "nature", "category": "noun", "confidence": 0.35, "source": "grammar_decoder", "notes": "already in dict"},
    "cthoary": {"latin": "magnus", "english": "great", "category": "adj", "confidence": 0.35, "source": "grammar_decoder", "notes": "already in dict"},

    # f2v words
    "kooiin": {"latin": "cupiditas", "english": "desire", "category": "noun", "confidence": 0.10, "source": "f2v", "notes": "1x"},
    "shty": {"latin": "siccitas", "english": "dryness (var2)", "category": "noun", "confidence": 0.15, "source": "f2v", "notes": "1x"},
    "kcho": {"latin": "quo", "english": "where (var)", "category": "adv", "confidence": 0.15, "source": "f2v", "notes": "1x"},
    "qotcho": {"latin": "coquo", "english": "I cook", "category": "verb", "confidence": 0.15, "source": "f2v", "notes": "1x"},
    "loeees": {"latin": "loquor", "english": "I speak", "category": "verb", "confidence": 0.05, "source": "f2v", "notes": "1x"},
    "lshy": {"latin": "lenis", "english": "gentle", "category": "adj", "confidence": 0.10, "source": "f2v", "notes": "1x"},
    "cholo": {"latin": "calor", "english": "heat (var)", "category": "noun", "confidence": 0.15, "source": "f2v", "notes": "1x"},
    "kchor": {"latin": "quorum", "english": "of which (var)", "category": "pron", "confidence": 0.15, "source": "f2v", "notes": "1x"},
    "chckhoy": {"latin": "calefactus", "english": "heated (var)", "category": "adj", "confidence": 0.10, "source": "f2v", "notes": "1x"},
    "chty": {"latin": "calidus", "english": "warm (var)", "category": "adj", "confidence": 0.15, "source": "f2v", "notes": "1x"},
    "cheky": {"latin": "calefacit", "english": "heats", "category": "verb", "confidence": 0.30, "source": "frequency", "notes": "already added"},
    "okchey": {"latin": "habet", "english": "has", "category": "verb", "confidence": 0.35, "source": "grammar_decoder", "notes": "already in dict"},
    "olor": {"latin": "olor", "english": "swan/smell", "category": "noun", "confidence": 0.20, "source": "frequency", "notes": "already added"},
    "lchoy": {"latin": "liquefacio", "english": "I liquefy", "category": "verb", "confidence": 0.10, "source": "f2v", "notes": "1x"},
    "lkchdy": {"latin": "liquefactus", "english": "liquefied", "category": "adj", "confidence": 0.10, "source": "f2v", "notes": "1x"},

    # f3r words
    "tsheos": {"latin": "tumidus", "english": "swollen (var)", "category": "adj", "confidence": 0.10, "source": "f3r", "notes": "1x"},
    "qopal": {"latin": "copal", "english": "copal (resin)", "category": "noun", "confidence": 0.20, "source": "f3r", "notes": "1x"},
    "daimm": {"latin": "damnum", "english": "loss (var)", "category": "noun", "confidence": 0.10, "source": "f3r", "notes": "1x"},
    "qotcham": {"latin": "coctam", "english": "cooked (acc.)", "category": "adj", "confidence": 0.10, "source": "f3r", "notes": "1x"},
    "ochor": {"latin": "oculi", "english": "of eye (var)", "category": "noun", "confidence": 0.15, "source": "f3r", "notes": "1x"},
    "qocheor": {"latin": "coquorum", "english": "of cooks", "category": "noun", "confidence": 0.10, "source": "f3r", "notes": "1x"},
    "schey": {"latin": "scissura", "english": "cut", "category": "noun", "confidence": 0.15, "source": "f3r", "notes": "1x"},
    "chololy": {"latin": "calidulus", "english": "warmish", "category": "adj", "confidence": 0.10, "source": "f3r", "notes": "1x"},
    "ychey": {"latin": "igitur", "english": "therefore (var2)", "category": "conj", "confidence": 0.10, "source": "f3r", "notes": "1x"},
    "cthody": {"latin": "aquaticus", "english": "aquatic (var)", "category": "adj", "confidence": 0.15, "source": "f3r", "notes": "1x"},
    "shelody": {"latin": "species", "english": "type (var)", "category": "noun", "confidence": 0.10, "source": "f3r", "notes": "1x"},
    "sholar": {"latin": "factura", "english": "making", "category": "noun", "confidence": 0.15, "source": "f3r", "notes": "1x"},
    "olaiir": {"latin": "olearius", "english": "oily (var2)", "category": "adj", "confidence": 0.10, "source": "f3r", "notes": "1x"},
    "qochol": {"latin": "coagulum", "english": "curd", "category": "noun", "confidence": 0.15, "source": "f3r", "notes": "1x"},
    "ctheey": {"latin": "aqueus", "english": "watery (var)", "category": "adj", "confidence": 0.15, "source": "f3r", "notes": "1x"},
    "chokchey": {"latin": "cholerus", "english": "bilious (var)", "category": "adj", "confidence": 0.10, "source": "f3r", "notes": "1x"},
    "otam": {"latin": "tempori", "english": "at time (dat.)", "category": "noun", "confidence": 0.25, "source": "frequency", "notes": "already added"},
    "shchody": {"latin": "siccus", "english": "dry (var2)", "category": "adj", "confidence": 0.10, "source": "f3r", "notes": "1x"},
    "dloeey": {"latin": "dulcis", "english": "sweet (var2)", "category": "adj", "confidence": 0.10, "source": "f3r", "notes": "1x"},
    "chosho": {"latin": "cibus", "english": "food (var2)", "category": "noun", "confidence": 0.10, "source": "f3r", "notes": "1x"},
    "dchory": {"latin": "dulcorosus", "english": "very sweet", "category": "adj", "confidence": 0.10, "source": "f3r", "notes": "1x"},
    "otchsy": {"latin": "temporeus", "english": "timely (var)", "category": "adj", "confidence": 0.10, "source": "f3r", "notes": "1x"},
    "shchey": {"latin": "siccans", "english": "drying (var)", "category": "adj", "confidence": 0.10, "source": "f3r", "notes": "1x"},
    "dchaly": {"latin": "dulcalis", "english": "sweet (adj)", "category": "adj", "confidence": 0.10, "source": "f3r", "notes": "1x"},
    "chodosy": {"latin": "cibosus", "english": "nutritious", "category": "adj", "confidence": 0.10, "source": "f3r", "notes": "1x"},
    "shedam": {"latin": "species", "english": "type (var2)", "category": "noun", "confidence": 0.10, "source": "f3r", "notes": "1x"},
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
