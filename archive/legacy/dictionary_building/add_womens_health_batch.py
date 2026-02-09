"""Add translation entries with women's health/botanical medical context.

Based on our motive hypothesis:
- 15th century Northern Italian medical/botanical text
- Likely women's health focus (gynecological, herbal remedies)
- Encoded to protect from Church persecution

Key Latin medical vocabulary domains:
- Gynecological: matrix, uterus, menstrua, partus, lac, mamma
- Preparations: decoctum, infusum, pulvis, unguentum, potio
- Conditions: dolor, febris, tumor, morbus, flux, sanguis
- Actions: purgat, mundificat, confortat, provocat
"""
import json
from pathlib import Path
from datetime import datetime

dict_path = Path('dictionary.json')
with open(dict_path) as f:
    dictionary = json.load(f)

# f3v words - applying women's health/medical vocabulary
new_entries = {
    # -aiin suffix words (Latin -ium endings)
    "koaiin": {"latin": "corium", "english": "skin/membrane", "category": "noun", "confidence": 0.25, "source": "f3v", "notes": "ko-+aiin pattern, medical context"},
    "ykoaiin": {"latin": "corium", "english": "skin (var)", "category": "noun", "confidence": 0.20, "source": "f3v", "notes": "y-prefix variant"},
    "choraiin": {"latin": "corarium", "english": "of the skin", "category": "noun", "confidence": 0.20, "source": "f4r", "notes": "chor-+aiin"},
    "koraiin": {"latin": "corium", "english": "skin (var2)", "category": "noun", "confidence": 0.20, "source": "f4r", "notes": "kor-+aiin"},
    "pchooiin": {"latin": "pectorium", "english": "chest remedy", "category": "noun", "confidence": 0.20, "source": "f4v", "notes": "pch-prefix, medical"},
    "choaiin": {"latin": "coagium", "english": "coagulation", "category": "noun", "confidence": 0.20, "source": "f4v", "notes": "medical preparation"},
    "otoiin": {"latin": "totius", "english": "of the whole", "category": "adj", "confidence": 0.20, "source": "f4v", "notes": "ot-prefix"},
    "qotchoiin": {"latin": "quotidiani", "english": "daily (gen)", "category": "adj", "confidence": 0.20, "source": "f4v", "notes": "for daily use"},
    "pydaiin": {"latin": "podium", "english": "base/foot", "category": "noun", "confidence": 0.20, "source": "f4r", "notes": "py-+daiin"},

    # -chy suffix words (Latin -cus/-ica endings - often adjectives)
    "kodalchy": {"latin": "calidicus", "english": "warming", "category": "adj", "confidence": 0.20, "source": "f4r", "notes": "medical property"},
    "chpady": {"latin": "sparsus", "english": "scattered", "category": "adj", "confidence": 0.15, "source": "f4r", "notes": "chp- cluster"},
    "shtchy": {"latin": "siccatus", "english": "dried", "category": "adj", "confidence": 0.25, "source": "f4r", "notes": "preparation method"},
    "shytchy": {"latin": "siccitas", "english": "dryness", "category": "noun", "confidence": 0.20, "source": "f4r", "notes": "medical property"},
    "chopchy": {"latin": "compositus", "english": "compounded", "category": "adj", "confidence": 0.25, "source": "f4v", "notes": "preparation method"},
    "ckhochy": {"latin": "coctus", "english": "cooked/boiled", "category": "adj", "confidence": 0.25, "source": "f4r", "notes": "preparation method"},

    # qo- prefix words (Latin quo-/cu- related)
    "qotoy": {"latin": "quotidianus", "english": "daily (var)", "category": "adj", "confidence": 0.25, "source": "f3v", "notes": "dosage frequency"},
    "qoteeol": {"latin": "quoties", "english": "how often (var4)", "category": "adv", "confidence": 0.20, "source": "f3v", "notes": "dosage instruction"},
    "qodar": {"latin": "quodam", "english": "certain/some", "category": "pron", "confidence": 0.25, "source": "f3v", "notes": "qo-+dar pattern"},
    "qokshy": {"latin": "coquens", "english": "cooking", "category": "verb", "confidence": 0.20, "source": "f4v", "notes": "preparation"},
    "qocthy": {"latin": "coctio", "english": "cooking/boiling", "category": "noun", "confidence": 0.25, "source": "f4v", "notes": "preparation method"},

    # Medical/preparation terms
    "cphor": {"latin": "color", "english": "color", "category": "noun", "confidence": 0.25, "source": "f3v", "notes": "diagnostic sign"},
    "okchor": {"latin": "occurrens", "english": "occurring", "category": "verb", "confidence": 0.20, "source": "f3v", "notes": "ok-+chor"},
    "olytol": {"latin": "olitor", "english": "gardener/cultivator", "category": "noun", "confidence": 0.20, "source": "f3v", "notes": "botanical context"},
    "shkchor": {"latin": "succurrit", "english": "helps/relieves", "category": "verb", "confidence": 0.25, "source": "f4v", "notes": "sh-+k+chor pattern"},

    # Body parts and conditions (women's health context)
    "okom": {"latin": "oculorum", "english": "of eyes", "category": "noun", "confidence": 0.25, "source": "f3v", "notes": "genitive form"},
    "okai": {"latin": "oculi", "english": "eyes", "category": "noun", "confidence": 0.25, "source": "f3v", "notes": "plural form"},
    "daiidy": {"latin": "dativum", "english": "given/dose", "category": "noun", "confidence": 0.20, "source": "f3v", "notes": "da-prefix, dosage"},
    "choteol": {"latin": "catellus", "english": "small vessel", "category": "noun", "confidence": 0.20, "source": "f4v", "notes": "cho-+teol"},

    # Short common words
    "sha": {"latin": "sana", "english": "healthy (fem)", "category": "adj", "confidence": 0.30, "source": "f3v", "notes": "short form"},
    "ees": {"latin": "eis", "english": "to them", "category": "pron", "confidence": 0.25, "source": "f3v", "notes": "dative pronoun"},
    "seees": {"latin": "sedes", "english": "seat/location", "category": "noun", "confidence": 0.20, "source": "f3v", "notes": "anatomical term"},
    "cto": {"latin": "cocto", "english": "by cooking", "category": "noun", "confidence": 0.20, "source": "f4v", "notes": "ablative"},

    # Compound/variant words
    "cheeykam": {"latin": "calefaciam", "english": "I will warm", "category": "verb", "confidence": 0.15, "source": "f3v", "notes": "complex form"},
    "doiin": {"latin": "dolium", "english": "vessel/jar", "category": "noun", "confidence": 0.25, "source": "f4r", "notes": "container"},
    "ytoy": {"latin": "iterum", "english": "again (var7)", "category": "adv", "confidence": 0.20, "source": "f4r", "notes": "repetition"},
    "shain": {"latin": "sanans", "english": "healing", "category": "verb", "confidence": 0.25, "source": "f4r", "notes": "present participle"},
    "tydy": {"latin": "triduum", "english": "three days", "category": "noun", "confidence": 0.20, "source": "f4r", "notes": "dosage timing"},
    "tcheay": {"latin": "trachea", "english": "throat/windpipe", "category": "noun", "confidence": 0.25, "source": "f4r", "notes": "anatomy"},
    "cpholdy": {"latin": "coloratus", "english": "colored", "category": "adj", "confidence": 0.20, "source": "f4r", "notes": "diagnostic"},
    "shyshol": {"latin": "suscitat", "english": "rouses/stimulates", "category": "verb", "confidence": 0.20, "source": "f4r", "notes": "medical action"},

    # f4v additional words
    "ksheo": {"latin": "cresceo", "english": "I grow (var)", "category": "verb", "confidence": 0.20, "source": "f4v", "notes": "botanical"},
    "kchoy": {"latin": "cacho", "english": "hidden", "category": "adj", "confidence": 0.15, "source": "f4v", "notes": "k-+choy"},
    "dolds": {"latin": "dolens", "english": "hurting", "category": "verb", "confidence": 0.25, "source": "f4v", "notes": "symptom"},
    "dlod": {"latin": "dolor", "english": "pain (var)", "category": "noun", "confidence": 0.25, "source": "f4v", "notes": "symptom"},
    "cheory": {"latin": "coloris", "english": "of color", "category": "noun", "confidence": 0.20, "source": "f4v", "notes": "genitive"},
}

added = 0
for word, entry in new_entries.items():
    if word not in dictionary['entries']:
        dictionary['entries'][word] = entry
        print(f"Added: {word} = {entry['latin']} ({entry['english']})")
        added += 1
    else:
        print(f"Exists: {word}")

dictionary['last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M")

with open(dict_path, 'w') as f:
    json.dump(dictionary, f, indent=2, ensure_ascii=False)

print(f"\nTotal added: {added}")
print(f"Total entries: {len(dictionary['entries'])}")
