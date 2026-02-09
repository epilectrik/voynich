"""Add translations for f8r-f10v folios continuation."""
import json
from pathlib import Path
from datetime import datetime

dict_path = Path('dictionary.json')
with open(dict_path) as f:
    dictionary = json.load(f)

new_entries = {
    # f7v remaining
    "dchory": {"latin": "decolor", "english": "discolored", "category": "adj", "confidence": 0.20, "source": "f7v"},
    "chockhy": {"latin": "coctivus", "english": "cooking-related", "category": "adj", "confidence": 0.20, "source": "f7v"},
    "qodaly": {"latin": "coquendus", "english": "to be cooked (var2)", "category": "verb", "confidence": 0.20, "source": "f7v"},
    "ykeedy": {"latin": "icterus", "english": "jaundice (var)", "category": "noun", "confidence": 0.25, "source": "f7v"},
    "oaiin": {"latin": "ovarium", "english": "ovary", "category": "noun", "confidence": 0.30, "source": "f7v", "notes": "women's health"},

    # f8r (59 words - major batch)
    "otshal": {"latin": "totalis", "english": "total (var4)", "category": "adj", "confidence": 0.20, "source": "f8r"},
    "chopy": {"latin": "copia", "english": "abundance", "category": "noun", "confidence": 0.25, "source": "f8r"},
    "cfhodar": {"latin": "confodere", "english": "to pierce", "category": "verb", "confidence": 0.15, "source": "f8r"},
    "tchty": {"latin": "tectus", "english": "covered", "category": "adj", "confidence": 0.20, "source": "f8r"},
    "kcheals": {"latin": "crescalis", "english": "growing (adj)", "category": "adj", "confidence": 0.15, "source": "f8r"},
    "okche": {"latin": "occulens", "english": "hiding (var)", "category": "verb", "confidence": 0.20, "source": "f8r"},
    "ry": {"latin": "res", "english": "thing/matter", "category": "noun", "confidence": 0.25, "source": "f8r"},
    "shesed": {"latin": "secedo", "english": "I withdraw", "category": "verb", "confidence": 0.15, "source": "f8r"},
    "chofchy": {"latin": "confectus", "english": "prepared", "category": "adj", "confidence": 0.25, "source": "f8r"},
    "cheeey": {"latin": "calidus", "english": "hot (var2)", "category": "adj", "confidence": 0.20, "source": "f8r"},
    "scho": {"latin": "schola", "english": "school/method", "category": "noun", "confidence": 0.15, "source": "f8r"},
    "ckooaiin": {"latin": "coquarium", "english": "cooking pot", "category": "noun", "confidence": 0.20, "source": "f8r"},
    "tosh": {"latin": "tostus", "english": "toasted", "category": "adj", "confidence": 0.25, "source": "f8r"},
    "ckcheey": {"latin": "crescens", "english": "growing (var4)", "category": "verb", "confidence": 0.20, "source": "f8r"},
    "koltoldy": {"latin": "coltolandus", "english": "to be cultivated", "category": "verb", "confidence": 0.15, "source": "f8r"},
    "chocty": {"latin": "coctus", "english": "cooked (var8)", "category": "adj", "confidence": 0.20, "source": "f8r"},
    "cheeody": {"latin": "calidulus", "english": "lukewarm (var2)", "category": "adj", "confidence": 0.20, "source": "f8r"},
    "choto": {"latin": "cocto", "english": "by cooking (var)", "category": "noun", "confidence": 0.20, "source": "f8r"},
    "kchoan": {"latin": "cresconum", "english": "of growing", "category": "noun", "confidence": 0.15, "source": "f8r"},
    "oldal": {"latin": "oleum", "english": "oil (var2)", "category": "noun", "confidence": 0.25, "source": "f8r"},
    "ychay": {"latin": "iterans", "english": "repeating (var4)", "category": "verb", "confidence": 0.20, "source": "f8r"},
    "okchedar": {"latin": "occultare", "english": "to hide", "category": "verb", "confidence": 0.20, "source": "f8r"},
    "opaldy": {"latin": "opacare", "english": "to shade", "category": "verb", "confidence": 0.15, "source": "f8r"},
    "ckhodeey": {"latin": "crescendo", "english": "by growing", "category": "adv", "confidence": 0.15, "source": "f8r"},
    "dchody": {"latin": "decoctus", "english": "decocted (var)", "category": "adj", "confidence": 0.20, "source": "f8r"},
    "shotchey": {"latin": "saturans", "english": "saturating (var)", "category": "verb", "confidence": 0.20, "source": "f8r"},
    "otcheeody": {"latin": "totalis", "english": "total (var5)", "category": "adj", "confidence": 0.15, "source": "f8r"},
    "kcheeam": {"latin": "crematum", "english": "burned (var2)", "category": "adj", "confidence": 0.15, "source": "f8r"},
    "shchdy": {"latin": "succidus", "english": "sappy (var2)", "category": "adj", "confidence": 0.20, "source": "f8r"},
    "otchol": {"latin": "totum", "english": "whole (var5)", "category": "adj", "confidence": 0.20, "source": "f8r"},
    "dcheol": {"latin": "decoquere", "english": "to decoct", "category": "verb", "confidence": 0.20, "source": "f8r"},
    "dykeeey": {"latin": "dissiccans", "english": "drying (var)", "category": "verb", "confidence": 0.15, "source": "f8r"},
    "qokeeal": {"latin": "coquendum", "english": "to be cooked (var2)", "category": "verb", "confidence": 0.20, "source": "f8r"},
    "pshy": {"latin": "pulsus", "english": "pulse", "category": "noun", "confidence": 0.25, "source": "f8r", "notes": "medical term"},
    "sheochar": {"latin": "sudorare", "english": "to sweat", "category": "verb", "confidence": 0.25, "source": "f8r"},
    "ycheam": {"latin": "iteratum", "english": "repeated (n var)", "category": "noun", "confidence": 0.15, "source": "f8r"},
    "shekaiin": {"latin": "siccarium", "english": "drying vessel", "category": "noun", "confidence": 0.20, "source": "f8r"},
    "otchokeeody": {"latin": "totalis", "english": "total (var6)", "category": "adj", "confidence": 0.10, "source": "f8r"},

    # f8v (40 words)
    "cthod": {"latin": "coctidus", "english": "boiled (var4)", "category": "adj", "confidence": 0.20, "source": "f8v"},
    "soocth": {"latin": "subiectus", "english": "subjected", "category": "adj", "confidence": 0.15, "source": "f8v"},
    "opcheaiin": {"latin": "operculum", "english": "lid (var)", "category": "noun", "confidence": 0.20, "source": "f8v"},
    "opydaiin": {"latin": "opodium", "english": "plant juice", "category": "noun", "confidence": 0.20, "source": "f8v"},
    "shcthal": {"latin": "succidalis", "english": "juicy (adj)", "category": "adj", "confidence": 0.15, "source": "f8v"},
    "sheaiin": {"latin": "sudarium", "english": "sweat cloth (var)", "category": "noun", "confidence": 0.25, "source": "f8v"},
    "chykchy": {"latin": "calidicus", "english": "warming (var4)", "category": "adj", "confidence": 0.20, "source": "f8v"},
    "cty": {"latin": "coctus", "english": "cooked (short)", "category": "adj", "confidence": 0.20, "source": "f8v"},
    "qody": {"latin": "coquitur", "english": "is cooked (var2)", "category": "verb", "confidence": 0.20, "source": "f8v"},
    "dolar": {"latin": "dolere", "english": "to hurt", "category": "verb", "confidence": 0.25, "source": "f8v"},
    "dshol": {"latin": "desiccare", "english": "to dry (var)", "category": "verb", "confidence": 0.20, "source": "f8v"},
    "chean": {"latin": "calens", "english": "being hot", "category": "verb", "confidence": 0.20, "source": "f8v"},
    "shealy": {"latin": "sudans", "english": "sweating (var)", "category": "verb", "confidence": 0.20, "source": "f8v"},
    "chary": {"latin": "calor", "english": "heat (var2)", "category": "noun", "confidence": 0.25, "source": "f8v"},
    "otchar": {"latin": "totalis", "english": "total (var7)", "category": "adj", "confidence": 0.15, "source": "f8v"},
    "etaiin": {"latin": "etiam", "english": "also/even", "category": "adv", "confidence": 0.30, "source": "f8v"},
    "cthan": {"latin": "coctanum", "english": "cooked item", "category": "noun", "confidence": 0.15, "source": "f8v"},
    "chotain": {"latin": "coctanus", "english": "cooking-related", "category": "adj", "confidence": 0.15, "source": "f8v"},
    "ocholy": {"latin": "occulius", "english": "more hidden", "category": "adj", "confidence": 0.15, "source": "f8v"},
    "dairaiin": {"latin": "dativarium", "english": "for giving", "category": "noun", "confidence": 0.15, "source": "f8v"},
    "choteey": {"latin": "calefaciens", "english": "warming (var5)", "category": "verb", "confidence": 0.20, "source": "f8v"},
    "pchodaiin": {"latin": "spodarium", "english": "ash vessel", "category": "noun", "confidence": 0.15, "source": "f8v"},
    "olchdy": {"latin": "oleatus", "english": "oiled", "category": "adj", "confidence": 0.25, "source": "f8v"},
    "ytchar": {"latin": "iterare", "english": "to repeat (var3)", "category": "verb", "confidence": 0.20, "source": "f8v"},
    "cphodaiin": {"latin": "spodarium", "english": "ash container", "category": "noun", "confidence": 0.15, "source": "f8v"},

    # f9r (30 words)
    "tydlo": {"latin": "triduum", "english": "three days (var)", "category": "noun", "confidence": 0.20, "source": "f9r"},
    "choly": {"latin": "colere", "english": "to cultivate", "category": "verb", "confidence": 0.25, "source": "f9r"},
    "orchey": {"latin": "oriendo", "english": "by rising", "category": "adv", "confidence": 0.15, "source": "f9r"},
    "sary": {"latin": "sanus", "english": "healthy (var3)", "category": "adj", "confidence": 0.25, "source": "f9r"},
    "oykeey": {"latin": "oleifaciens", "english": "producing oil", "category": "verb", "confidence": 0.15, "source": "f9r"},
    "okchody": {"latin": "occultus", "english": "hidden (var3)", "category": "adj", "confidence": 0.20, "source": "f9r"},
    "toeoky": {"latin": "toticus", "english": "entire", "category": "adj", "confidence": 0.15, "source": "f9r"},
    "toiin": {"latin": "totium", "english": "whole (n)", "category": "noun", "confidence": 0.20, "source": "f9r"},
    "qotod": {"latin": "coctidus", "english": "boiled (var5)", "category": "adj", "confidence": 0.15, "source": "f9r"},
    "ram": {"latin": "ramus", "english": "branch", "category": "noun", "confidence": 0.30, "source": "f9r", "notes": "botanical"},
    "yshy": {"latin": "ipse", "english": "himself/itself", "category": "pron", "confidence": 0.20, "source": "f9r"},
    "chokcho": {"latin": "calefactio", "english": "heating (n)", "category": "noun", "confidence": 0.20, "source": "f9r"},
    "chcthod": {"latin": "coctidus", "english": "boiled (var6)", "category": "adj", "confidence": 0.15, "source": "f9r"},
    "ytol": {"latin": "iterum", "english": "again (var11)", "category": "adv", "confidence": 0.20, "source": "f9r"},
    "dayty": {"latin": "datus", "english": "given (var3)", "category": "adj", "confidence": 0.20, "source": "f9r"},
    "chokoiin": {"latin": "calefactorium", "english": "heater (var2)", "category": "noun", "confidence": 0.20, "source": "f9r"},
    "dsholdy": {"latin": "desiccandus", "english": "to be dried", "category": "verb", "confidence": 0.20, "source": "f9r"},
    "ot": {"latin": "totus", "english": "whole (short)", "category": "adj", "confidence": 0.25, "source": "f9r"},
    "shotchedy": {"latin": "saturandus", "english": "to be saturated", "category": "verb", "confidence": 0.15, "source": "f9r"},
    "okchy": {"latin": "occultus", "english": "hidden (var4)", "category": "adj", "confidence": 0.20, "source": "f9r"},
    "shokchdy": {"latin": "succidus", "english": "sappy (var3)", "category": "adj", "confidence": 0.20, "source": "f9r"},
    "cthodo": {"latin": "coctidus", "english": "boiled (var7)", "category": "adj", "confidence": 0.15, "source": "f9r"},
    "yteeoy": {"latin": "iteranus", "english": "repetitive", "category": "adj", "confidence": 0.15, "source": "f9r"},
    "dchees": {"latin": "decoquens", "english": "decocting (var)", "category": "verb", "confidence": 0.20, "source": "f9r"},
    "shokchol": {"latin": "succiolum", "english": "small juice (var)", "category": "noun", "confidence": 0.20, "source": "f9r"},

    # f9v (21 words)
    "fochor": {"latin": "foculare", "english": "to heat on fire", "category": "verb", "confidence": 0.20, "source": "f9v"},
    "oporody": {"latin": "operandus", "english": "to be worked", "category": "verb", "confidence": 0.15, "source": "f9v"},
    "opy": {"latin": "opus", "english": "work", "category": "noun", "confidence": 0.30, "source": "f9v"},
    "qopchypcho": {"latin": "coquitio", "english": "cooking process", "category": "noun", "confidence": 0.10, "source": "f9v"},
    "qofol": {"latin": "coqufolium", "english": "cooking leaf", "category": "noun", "confidence": 0.10, "source": "f9v"},
    "chkaiin": {"latin": "calefactorium", "english": "heater (var3)", "category": "noun", "confidence": 0.20, "source": "f9v"},
    "oeees": {"latin": "oves", "english": "sheep (var)", "category": "noun", "confidence": 0.20, "source": "f9v"},
    "ytey": {"latin": "iterum", "english": "again (var12)", "category": "adv", "confidence": 0.20, "source": "f9v"},
    "toldy": {"latin": "tollendus", "english": "to be removed", "category": "verb", "confidence": 0.20, "source": "f9v"},
    "ypchy": {"latin": "ipsius", "english": "of itself", "category": "pron", "confidence": 0.20, "source": "f9v"},
    "olcfholy": {"latin": "oleofolium", "english": "oily leaf", "category": "noun", "confidence": 0.15, "source": "f9v"},
    "te": {"latin": "te", "english": "you (acc)", "category": "pron", "confidence": 0.30, "source": "f9v"},
    "choy": {"latin": "calor", "english": "heat (var3)", "category": "noun", "confidence": 0.25, "source": "f9v"},
    "ksheody": {"latin": "crescendus", "english": "to be grown", "category": "verb", "confidence": 0.15, "source": "f9v"},
    "ctchy": {"latin": "coctivus", "english": "cooking (adj var)", "category": "adj", "confidence": 0.15, "source": "f9v"},
    "rokyd": {"latin": "roratus", "english": "bedewed", "category": "adj", "confidence": 0.15, "source": "f9v"},
    "chyty": {"latin": "caliditas", "english": "warmth (var3)", "category": "noun", "confidence": 0.20, "source": "f9v"},
    "kyty": {"latin": "crematus", "english": "burned (var3)", "category": "adj", "confidence": 0.15, "source": "f9v"},
    "okeear": {"latin": "ocularis", "english": "of eyes (adj)", "category": "adj", "confidence": 0.20, "source": "f9v"},

    # f10r (27 words)
    "pchocthy": {"latin": "pectoricus", "english": "pectoral", "category": "adj", "confidence": 0.20, "source": "f10r"},
    "octhody": {"latin": "occultandus", "english": "to be hidden", "category": "verb", "confidence": 0.15, "source": "f10r"},
    "chorchy": {"latin": "coloricus", "english": "colored (var2)", "category": "adj", "confidence": 0.15, "source": "f10r"},
    "pchodol": {"latin": "spodolum", "english": "ash (dim)", "category": "noun", "confidence": 0.15, "source": "f10r"},
    "chopchal": {"latin": "compositalum", "english": "compound (dim)", "category": "noun", "confidence": 0.15, "source": "f10r"},
    "ypch": {"latin": "ipsius", "english": "of itself (var)", "category": "pron", "confidence": 0.15, "source": "f10r"},
    "kom": {"latin": "cum", "english": "with (var)", "category": "prep", "confidence": 0.25, "source": "f10r"},
    "cthoor": {"latin": "coctorum", "english": "of cooked things (var)", "category": "noun", "confidence": 0.15, "source": "f10r"},
    "chair": {"latin": "calere", "english": "to be hot", "category": "verb", "confidence": 0.25, "source": "f10r"},
    "otytchol": {"latin": "totalis", "english": "total (var8)", "category": "adj", "confidence": 0.10, "source": "f10r"},
    "etyd": {"latin": "etiam", "english": "also (var)", "category": "adv", "confidence": 0.20, "source": "f10r"},
    "ctho": {"latin": "cocto", "english": "by cooking (var2)", "category": "noun", "confidence": 0.20, "source": "f10r"},
    "chtchor": {"latin": "coctorum", "english": "of cooked (var2)", "category": "noun", "confidence": 0.15, "source": "f10r"},
    "doiir": {"latin": "dolere", "english": "to hurt (var)", "category": "verb", "confidence": 0.20, "source": "f10r"},
    "qoctholy": {"latin": "coctilis", "english": "boiled (adj var)", "category": "adj", "confidence": 0.15, "source": "f10r"},
    "qokchol": {"latin": "coquendum", "english": "to be cooked (var3)", "category": "verb", "confidence": 0.20, "source": "f10r"},
    "ykchaiin": {"latin": "iterarium", "english": "repetition", "category": "noun", "confidence": 0.15, "source": "f10r"},
    "qotchor": {"latin": "coquitor", "english": "is cooked (var3)", "category": "verb", "confidence": 0.20, "source": "f10r"},
    "oykchor": {"latin": "oleicoquor", "english": "oil-cooked", "category": "adj", "confidence": 0.10, "source": "f10r"},
    "tcheod": {"latin": "tergidus", "english": "cleansed (var2)", "category": "adj", "confidence": 0.15, "source": "f10r"},
    "qokcheey": {"latin": "coquendo", "english": "by cooking", "category": "adv", "confidence": 0.20, "source": "f10r"},
    "ykeeal": {"latin": "iterandus", "english": "to be repeated (var)", "category": "verb", "confidence": 0.15, "source": "f10r"},
    "chckhaiin": {"latin": "calefactorium", "english": "heater (var4)", "category": "noun", "confidence": 0.15, "source": "f10r"},

    # f10v (14 words)
    "paiin": {"latin": "patina", "english": "dish/pan", "category": "noun", "confidence": 0.25, "source": "f10v"},
    "otydy": {"latin": "totidus", "english": "whole (var6)", "category": "adj", "confidence": 0.15, "source": "f10v"},
    "chcthor": {"latin": "calefactor", "english": "heater (n)", "category": "noun", "confidence": 0.20, "source": "f10v"},
    "choiin": {"latin": "calorum", "english": "of heats", "category": "noun", "confidence": 0.15, "source": "f10v"},
    "dsho": {"latin": "desicco", "english": "I dry (var)", "category": "verb", "confidence": 0.20, "source": "f10v"},
    "olty": {"latin": "oleitus", "english": "oiled (var)", "category": "adj", "confidence": 0.20, "source": "f10v"},
    "qotchytor": {"latin": "coquitor", "english": "is cooked (var4)", "category": "verb", "confidence": 0.15, "source": "f10v"},
    "shoiin": {"latin": "sudorium", "english": "sweat (gen pl)", "category": "noun", "confidence": 0.20, "source": "f10v"},
    "qotchey": {"latin": "coquendo", "english": "by cooking (var)", "category": "adv", "confidence": 0.20, "source": "f10v"},
    "shcthey": {"latin": "succidus", "english": "sappy (var4)", "category": "adj", "confidence": 0.15, "source": "f10v"},
    "qokchyky": {"latin": "coquitio", "english": "cooking (n var)", "category": "noun", "confidence": 0.10, "source": "f10v"},
    "qotoiin": {"latin": "coquitorium", "english": "cooking place", "category": "noun", "confidence": 0.15, "source": "f10v"},
    "chckhan": {"latin": "calefactanum", "english": "heated thing", "category": "noun", "confidence": 0.10, "source": "f10v"},
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
