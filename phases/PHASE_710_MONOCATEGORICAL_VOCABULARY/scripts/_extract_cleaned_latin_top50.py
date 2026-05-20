"""Extract top-50 from Codicillus filtering out OCR fragments (len<3) and obvious abbreviations.
Categorize each as OPERATION/ENTITY/PROPERTY/FUNCTION/AMBIGUOUS.
"""
from __future__ import annotations
import json
import re
import sys
from collections import Counter
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path("C:/git/voynich")
COD_PATH = ROOT / 'sources' / 'codicillus' / 'codicillus_complete_latin.txt'

# Manual category assignments for top Latin word-forms (look up each in Lewis & Short equivalent)
# Methodology: looked up each form in standard Latin lexicon equivalent.
# Conservative: ambiguous forms (e.g., "que" could be enclitic FUNCTION) tagged by primary use.
CATEGORIES = {
    "et": "FUNCTION", "que": "FUNCTION", "in": "FUNCTION", "de": "FUNCTION",
    "ad": "FUNCTION", "cum": "FUNCTION", "ut": "FUNCTION", "non": "FUNCTION",
    "si": "FUNCTION", "per": "FUNCTION", "sed": "FUNCTION", "ex": "FUNCTION",
    "aut": "FUNCTION", "vel": "FUNCTION", "sub": "FUNCTION", "ac": "FUNCTION",
    "tamen": "FUNCTION", "etiam": "FUNCTION", "enim": "FUNCTION", "quam": "FUNCTION",
    "sic": "FUNCTION", "scilicet": "FUNCTION", "autem": "FUNCTION", "magis": "FUNCTION",
    "vt": "FUNCTION", "ana": "FUNCTION",  # 'ana' in pharmacy texts = 'of each' weight marker
    "est": "OPERATION", "sit": "OPERATION", "sunt": "OPERATION", "fit": "OPERATION",
    "fiat": "OPERATION", "esse": "OPERATION", "facit": "OPERATION", "habet": "OPERATION",
    "potest": "OPERATION", "videtur": "OPERATION", "dicit": "OPERATION",
    "operatur": "OPERATION", "fiunt": "OPERATION",
    "quod": "ENTITY",  # relative pronoun, refers to entities
    "qui": "ENTITY", "quae": "ENTITY", "qua": "ENTITY", "uod": "ENTITY",
    "uae": "ENTITY", "hoc": "ENTITY", "haec": "ENTITY", "illa": "ENTITY",
    "ipse": "ENTITY", "ille": "ENTITY", "ipsa": "ENTITY",
    "ignis": "ENTITY", "aqua": "ENTITY", "terra": "ENTITY", "aer": "ENTITY",
    "sol": "ENTITY", "luna": "ENTITY", "deus": "ENTITY", "pars": "ENTITY",
    "modus": "ENTITY", "natura": "ENTITY", "spiritus": "ENTITY", "corpus": "ENTITY",
    "lapis": "ENTITY", "sua": "ENTITY", "suis": "ENTITY", "drach": "ENTITY",
    "vnc": "ENTITY", "id": "ENTITY",
    "calidum": "PROPERTY", "frigidum": "PROPERTY", "humidum": "PROPERTY",
    "omnis": "PROPERTY", "magnus": "PROPERTY", "primus": "PROPERTY",
    "prima": "PROPERTY", "primo": "PROPERTY",
    # Additional words from real top-50:
    "fuit": "OPERATION",       # was (past tense of esse)
    "ista": "ENTITY",          # that (demonstrative pronoun)
    "nec": "FUNCTION",         # and not / nor
    "sulfur": "ENTITY",        # sulfur (noun, material)
    "sue": "ENTITY",           # her/its (possessive pronoun)
    "nisi": "FUNCTION",        # unless
    "sui": "ENTITY",           # his/their own (possessive pronoun)
    "corporis": "ENTITY",      # of body (noun genitive)
    "nam": "FUNCTION",         # for, because
    "suo": "ENTITY",           # his own (possessive pronoun)
    "illud": "ENTITY",         # that (pronoun)
    "post": "FUNCTION",        # after (preposition)
    "folio": "ENTITY",         # page (noun)
    "aque": "ENTITY",          # variant of aqua
    "opus": "ENTITY",          # work / the work (noun)
    "sine": "FUNCTION",        # without (preposition)
    "forma": "ENTITY",         # form (noun)
    "alia": "ENTITY",          # other (pronoun)
    "ideo": "FUNCTION",        # therefore
    "illam": "ENTITY",         # that one (pronoun)
    "fiunt": "OPERATION",      # they become
}

# Obvious OCR/abbreviation noise + English contamination to filter
NOISE_FORMS = {"page", "the", "red", "er", "uo", "no", "us", "is", "se", "ue", "re",
               "na", "cu", "su", "ij", "ca", "dc", "cx", "cft", "fi", "eft", "funt",
               "and", "with", "corp"}


def main():
    text = Path(COD_PATH).read_text(encoding='utf-8', errors='replace').lower()
    words = re.findall(r'[a-zA-Z]+', text)
    counter = Counter(words)

    # Filter: length >= 3 AND not in noise list
    filtered = [(w, c) for w, c in counter.most_common(200)
                if len(w) >= 3 and w not in NOISE_FORMS]

    top50 = filtered[:50]
    print(f"\n=== Codicillus top-50 cleaned (len>=3, OCR noise filtered) ===")
    out_items = {}
    cat_counter = Counter()
    uncat = []
    for w, c in top50:
        cat = CATEGORIES.get(w, "UNCATEGORIZED")
        cat_counter[cat] += 1
        if cat == "UNCATEGORIZED":
            uncat.append(w)
        out_items[w] = {"category": cat, "count": c}
        print(f"  {w:<15} count={c:<6} cat={cat}")

    print(f"\n  Category distribution: {dict(cat_counter)}")
    if uncat:
        print(f"  Uncategorized (need lookup): {uncat}")
    print(f"  N = {len(top50)}")
    print(f"  OPERATION fraction: {cat_counter.get('OPERATION', 0) / len(top50):.2%}")
    print(f"  ENTITY fraction:    {cat_counter.get('ENTITY', 0) / len(top50):.2%}")
    print(f"  PROPERTY fraction:  {cat_counter.get('PROPERTY', 0) / len(top50):.2%}")
    print(f"  FUNCTION fraction:  {cat_counter.get('FUNCTION', 0) / len(top50):.2%}")
    print(f"  Dominant: {cat_counter.most_common(1)[0]}")

    # Write out for use in main test
    out_path = ROOT / 'phases' / 'PHASE_710_MONOCATEGORICAL_VOCABULARY' / 'reference_data' / 'codicillus_real_top50.json'
    out_path.write_text(json.dumps({"items": out_items}, indent=2), encoding='utf-8')
    print(f"\nWritten: {out_path.relative_to(ROOT)}")


if __name__ == '__main__':
    main()
