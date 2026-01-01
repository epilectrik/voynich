"""Add translations for f6r-f10v folios.

Continuing women's health/botanical medical context:
- Preparations: decoctions, infusions, ointments
- Ingredients: oils, juices, powders
- Actions: heating, drying, purging, soothing
- Body parts and conditions
"""
import json
from pathlib import Path
from datetime import datetime

dict_path = Path('dictionary.json')
with open(dict_path) as f:
    dictionary = json.load(f)

new_entries = {
    # f5r last word (with asterisk - transcription note)
    "oka*or": {"latin": "oculorum", "english": "of eyes (var)", "category": "noun", "confidence": 0.15, "source": "f5r", "notes": "asterisk in original"},

    # f6r (28 words)
    "foar": {"latin": "foris", "english": "outside", "category": "adv", "confidence": 0.25, "source": "f6r"},
    "cholor": {"latin": "color", "english": "color (var)", "category": "noun", "confidence": 0.25, "source": "f6r"},
    "cphol": {"latin": "spolium", "english": "skin/covering", "category": "noun", "confidence": 0.20, "source": "f6r"},
    "chckh": {"latin": "cachet", "english": "is hidden", "category": "verb", "confidence": 0.15, "source": "f6r"},
    "chopchol": {"latin": "compositus", "english": "compounded (var)", "category": "adj", "confidence": 0.20, "source": "f6r"},
    "chotols": {"latin": "coctilis", "english": "boiled/baked", "category": "adj", "confidence": 0.20, "source": "f6r"},
    "poeear": {"latin": "potare", "english": "to drink", "category": "verb", "confidence": 0.25, "source": "f6r"},
    "cheoees": {"latin": "calidis", "english": "with hot things", "category": "adj", "confidence": 0.20, "source": "f6r"},
    "ykeor": {"latin": "iteror", "english": "I am repeated", "category": "verb", "confidence": 0.20, "source": "f6r"},
    "yaiir": {"latin": "aeris", "english": "of air", "category": "noun", "confidence": 0.20, "source": "f6r"},
    "okoiin": {"latin": "ocularium", "english": "eye remedy", "category": "noun", "confidence": 0.25, "source": "f6r"},
    "ytaly": {"latin": "iterans", "english": "repeating (var2)", "category": "verb", "confidence": 0.20, "source": "f6r"},
    "odam": {"latin": "odam", "english": "swelling", "category": "noun", "confidence": 0.20, "source": "f6r"},
    "ckham": {"latin": "crematum", "english": "burned (var)", "category": "adj", "confidence": 0.20, "source": "f6r"},
    "ychol": {"latin": "iterum", "english": "again (liquid)", "category": "adv", "confidence": 0.20, "source": "f6r"},
    "pchar": {"latin": "spargere", "english": "to scatter", "category": "verb", "confidence": 0.20, "source": "f6r"},
    "ckhaiin": {"latin": "cremarium", "english": "burning vessel", "category": "noun", "confidence": 0.20, "source": "f6r"},
    "sheeol": {"latin": "serum", "english": "serum (var3)", "category": "noun", "confidence": 0.20, "source": "f6r"},
    "skaiiodar": {"latin": "siccationis", "english": "of drying", "category": "noun", "confidence": 0.15, "source": "f6r"},
    "chory": {"latin": "coloris", "english": "of color (var)", "category": "noun", "confidence": 0.20, "source": "f6r"},
    "shodairy": {"latin": "sudoris", "english": "of sweat", "category": "noun", "confidence": 0.25, "source": "f6r"},
    "olchory": {"latin": "olearis", "english": "oily (var4)", "category": "adj", "confidence": 0.20, "source": "f6r"},
    "qokeeor": {"latin": "coquitor", "english": "is being cooked", "category": "verb", "confidence": 0.20, "source": "f6r"},
    "ychedy": {"latin": "iherba", "english": "the herb", "category": "noun", "confidence": 0.20, "source": "f6r"},
    "pchodar": {"latin": "spondere", "english": "to promise", "category": "verb", "confidence": 0.15, "source": "f6r"},
    "okchom": {"latin": "occultum", "english": "hidden thing (var)", "category": "noun", "confidence": 0.20, "source": "f6r"},
    "charody": {"latin": "calor", "english": "heat (var)", "category": "noun", "confidence": 0.25, "source": "f6r"},
    "ykcheor": {"latin": "iterare", "english": "to repeat (var2)", "category": "verb", "confidence": 0.20, "source": "f6r"},

    # f6v (40 words - first 30)
    "koar": {"latin": "corium", "english": "skin (var4)", "category": "noun", "confidence": 0.20, "source": "f6v"},
    "oheekar": {"latin": "olecare", "english": "to oil", "category": "verb", "confidence": 0.20, "source": "f6v"},
    "qoar": {"latin": "coquar", "english": "I am cooked", "category": "verb", "confidence": 0.20, "source": "f6v"},
    "chapchy": {"latin": "caput", "english": "head (var)", "category": "noun", "confidence": 0.25, "source": "f6v"},
    "oees": {"latin": "oves", "english": "sheep (pl)", "category": "noun", "confidence": 0.20, "source": "f6v"},
    "qoekchar": {"latin": "coquicare", "english": "to cook well", "category": "verb", "confidence": 0.20, "source": "f6v"},
    "cheas": {"latin": "caleas", "english": "you heat", "category": "verb", "confidence": 0.20, "source": "f6v"},
    "qoair": {"latin": "coquaris", "english": "you are cooked", "category": "verb", "confidence": 0.20, "source": "f6v"},
    "oochockhy": {"latin": "occoctus", "english": "boiled down", "category": "adj", "confidence": 0.20, "source": "f6v"},
    "chekchoy": {"latin": "calefaciens", "english": "warming (var2)", "category": "verb", "confidence": 0.20, "source": "f6v"},
    "rychos": {"latin": "ricinus", "english": "castor oil plant", "category": "noun", "confidence": 0.25, "source": "f6v"},
    "sos": {"latin": "sus", "english": "pig/swine", "category": "noun", "confidence": 0.20, "source": "f6v"},
    "dady": {"latin": "datus", "english": "given (var2)", "category": "adj", "confidence": 0.25, "source": "f6v"},
    "dey": {"latin": "de", "english": "from/about", "category": "prep", "confidence": 0.30, "source": "f6v"},
    "okody": {"latin": "occultus", "english": "hidden (var2)", "category": "adj", "confidence": 0.20, "source": "f6v"},
    "ytody": {"latin": "iteratus", "english": "repeated (var)", "category": "adj", "confidence": 0.20, "source": "f6v"},
    "cshe": {"latin": "crescens", "english": "growing (var3)", "category": "verb", "confidence": 0.20, "source": "f6v"},
    "chodam": {"latin": "calefactam", "english": "heated (acc f)", "category": "adj", "confidence": 0.20, "source": "f6v"},
    "doldom": {"latin": "dolendum", "english": "to be mourned", "category": "verb", "confidence": 0.15, "source": "f6v"},
    "tchody": {"latin": "tergidus", "english": "cleansed (var)", "category": "adj", "confidence": 0.20, "source": "f6v"},
    "cheokeechy": {"latin": "calefactus", "english": "warmed (var)", "category": "adj", "confidence": 0.20, "source": "f6v"},
    "chocphar": {"latin": "conspargere", "english": "to sprinkle", "category": "verb", "confidence": 0.20, "source": "f6v"},
    "ykeedy": {"latin": "icterus", "english": "jaundice", "category": "noun", "confidence": 0.25, "source": "f6v"},
    "dealy": {"latin": "dealbus", "english": "whitened", "category": "adj", "confidence": 0.20, "source": "f6v"},
    "ycheold": {"latin": "iteratum", "english": "repeated (n)", "category": "noun", "confidence": 0.20, "source": "f6v"},
    "qodaly": {"latin": "coquendus", "english": "to be cooked (var)", "category": "verb", "confidence": 0.20, "source": "f6v"},
    "cheokaiin": {"latin": "calefactorium", "english": "heating device", "category": "noun", "confidence": 0.20, "source": "f6v"},
    "charar": {"latin": "calefacere", "english": "to heat (var)", "category": "verb", "confidence": 0.20, "source": "f6v"},
    "oaiin": {"latin": "ovarium", "english": "ovary", "category": "noun", "confidence": 0.30, "source": "f6v", "notes": "women's health term"},
    "ykeeoldy": {"latin": "iterandus", "english": "to be repeated", "category": "verb", "confidence": 0.20, "source": "f6v"},

    # f7r (25 words)
    "fchodaiin": {"latin": "focarium", "english": "hearth/brazier", "category": "noun", "confidence": 0.20, "source": "f7r"},
    "shopchey": {"latin": "suspiciens", "english": "looking up", "category": "verb", "confidence": 0.15, "source": "f7r"},
    "qko": {"latin": "quo", "english": "where/which", "category": "pron", "confidence": 0.25, "source": "f7r"},
    "qoos": {"latin": "quos", "english": "whom (acc pl)", "category": "pron", "confidence": 0.25, "source": "f7r"},
    "chorochy": {"latin": "coloratus", "english": "colored (var)", "category": "adj", "confidence": 0.20, "source": "f7r"},
    "dcheey": {"latin": "decoquens", "english": "decocting", "category": "verb", "confidence": 0.20, "source": "f7r"},
    "keor": {"latin": "caerulea", "english": "blue", "category": "adj", "confidence": 0.20, "source": "f7r"},
    "dold": {"latin": "dolor", "english": "pain (var2)", "category": "noun", "confidence": 0.25, "source": "f7r"},
    "oeeees": {"latin": "ovium", "english": "of sheep", "category": "noun", "confidence": 0.20, "source": "f7r"},
    "cheodaiin": {"latin": "calefactorium", "english": "heater (var)", "category": "noun", "confidence": 0.20, "source": "f7r"},
    "ytcheey": {"latin": "iterans", "english": "repeating (var3)", "category": "verb", "confidence": 0.20, "source": "f7r"},
    "chald": {"latin": "calidus", "english": "hot (var)", "category": "adj", "confidence": 0.25, "source": "f7r"},
    "lochey": {"latin": "loquens", "english": "speaking", "category": "verb", "confidence": 0.20, "source": "f7r"},
    "kchos": {"latin": "crassus", "english": "thick", "category": "adj", "confidence": 0.25, "source": "f7r"},
    "ksholochey": {"latin": "consoildens", "english": "consolidating", "category": "verb", "confidence": 0.15, "source": "f7r"},
    "qotoees": {"latin": "quoties", "english": "how often (var6)", "category": "adv", "confidence": 0.20, "source": "f7r"},
    "chkoldy": {"latin": "calidulus", "english": "lukewarm (var)", "category": "adj", "confidence": 0.20, "source": "f7r"},
    "dshoy": {"latin": "desicco", "english": "I dry", "category": "verb", "confidence": 0.20, "source": "f7r"},
    "chotchy": {"latin": "coctus", "english": "cooked (var6)", "category": "adj", "confidence": 0.20, "source": "f7r"},
    "deeeese": {"latin": "depressus", "english": "pressed down", "category": "adj", "confidence": 0.15, "source": "f7r"},
    "cpholaiin": {"latin": "spolearium", "english": "covering", "category": "noun", "confidence": 0.15, "source": "f7r"},
    "sheodychy": {"latin": "sudoricus", "english": "causing sweat", "category": "adj", "confidence": 0.25, "source": "f7r"},
    "chockhy": {"latin": "coctivus", "english": "relating to cooking", "category": "adj", "confidence": 0.20, "source": "f7r"},
    "doeey": {"latin": "doleo", "english": "I hurt", "category": "verb", "confidence": 0.25, "source": "f7r"},
    "sheochey": {"latin": "sudorans", "english": "sweating", "category": "verb", "confidence": 0.20, "source": "f7r"},

    # f7v (32 words - first 25)
    "polyshy": {"latin": "politus", "english": "polished/refined", "category": "adj", "confidence": 0.20, "source": "f7v"},
    "qopchy": {"latin": "coquitur", "english": "is cooked (var)", "category": "verb", "confidence": 0.20, "source": "f7v"},
    "otshol": {"latin": "totum", "english": "whole (var4)", "category": "adj", "confidence": 0.20, "source": "f7v"},
    "tshodody": {"latin": "tergendus", "english": "to be wiped", "category": "verb", "confidence": 0.15, "source": "f7v"},
    "chochy": {"latin": "coctus", "english": "cooked (var7)", "category": "adj", "confidence": 0.20, "source": "f7v"},
    "chcphhy": {"latin": "conspersus", "english": "sprinkled", "category": "adj", "confidence": 0.15, "source": "f7v"},
    "cthd": {"latin": "coctidus", "english": "boiled (short)", "category": "adj", "confidence": 0.15, "source": "f7v"},
    "dykchy": {"latin": "dissiccans", "english": "drying out", "category": "verb", "confidence": 0.20, "source": "f7v"},
    "chkeey": {"latin": "calefaciens", "english": "warming (var3)", "category": "verb", "confidence": 0.20, "source": "f7v"},
    "ty": {"latin": "tibi", "english": "to you", "category": "pron", "confidence": 0.25, "source": "f7v"},
    "choteeen": {"latin": "cotidie", "english": "daily (var5)", "category": "adv", "confidence": 0.20, "source": "f7v"},
    "oeear": {"latin": "olearis", "english": "of oil", "category": "adj", "confidence": 0.20, "source": "f7v"},
    "choschy": {"latin": "conspicus", "english": "visible", "category": "adj", "confidence": 0.15, "source": "f7v"},
    "deees": {"latin": "deses", "english": "inactive", "category": "adj", "confidence": 0.15, "source": "f7v"},
    "dchodaiin": {"latin": "decoquarium", "english": "decoction vessel", "category": "noun", "confidence": 0.20, "source": "f7v"},
    "tcheey": {"latin": "tergeo", "english": "I wipe", "category": "verb", "confidence": 0.20, "source": "f7v"},
    "sheod": {"latin": "sudor", "english": "sweat (var)", "category": "noun", "confidence": 0.25, "source": "f7v"},
    "sheodaiin": {"latin": "sudorium", "english": "sweat bath", "category": "noun", "confidence": 0.25, "source": "f7v", "notes": "bathing/women's health"},
    "oksholshol": {"latin": "oculus", "english": "eye (compound)", "category": "noun", "confidence": 0.15, "source": "f7v"},
    "qochchey": {"latin": "coquens", "english": "cooking (var5)", "category": "verb", "confidence": 0.20, "source": "f7v"},
    "dchokchy": {"latin": "decoctus", "english": "decocted", "category": "adj", "confidence": 0.20, "source": "f7v"},
    "ytal": {"latin": "iterum", "english": "again (var10)", "category": "adv", "confidence": 0.20, "source": "f7v"},
    "chotar": {"latin": "coctare", "english": "to cook often", "category": "verb", "confidence": 0.20, "source": "f7v"},
    "dchory": {"latin": "decolor", "english": "discolored", "category": "adj", "confidence": 0.20, "source": "f7v"},
    "kochey": {"latin": "coquens", "english": "cooking (var6)", "category": "verb", "confidence": 0.20, "source": "f7v"},
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
