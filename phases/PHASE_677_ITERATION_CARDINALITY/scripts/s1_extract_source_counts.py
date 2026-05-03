"""
Phase 677 Stage 1: Extract iteration counts from matched source recipes.

For each of 11 Phase-668-validated matched folios, extract numeric mentions
from the corresponding English recipe text. Output: per-recipe candidate
iteration counts for pre-registration.

Sources: testamentum_complete_english.txt + structural profile line ranges.

Strategy:
  - Numeric digits: \\b\\d+\\b
  - Written numbers (English): one/two/three/four/five/six/seven/eight/nine/ten/
    eleven/twelve/twenty/thrice/ninefold/etc.
  - Latin numerals (in case English uses them): semel/bis/ter/quater/quinquies/
    sexies/septies/octies/novies/decies/duodecies
  - Multiplier markers: "times", "fold", "cycles"

Output: phases/PHASE_677_ITERATION_CARDINALITY/results/source_counts.json
        Each entry has: folio, chapter, n_words, raw_numbers, written_numbers,
        latin_numerals, candidate_iterations (manual review).

This script does NOT pre-register the test counts — that's a manual step
after reviewing the extracted candidates. Stage 2 uses the pre-registered
selections.
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "phases" / "PER_DOMAIN_BRIDGE_CALIBRATION" / "scripts"))
from shared_627 import load_pl_structural_profile

OUT_PATH = Path(__file__).resolve().parents[1] / "results" / "source_counts.json"

MATCHED = {
    "f75r":  ("Mercuriorum", 19, "aqua vitae (×4 reflux + ×9 cycles per memory)"),
    "f76r":  ("Practica", 16, "element separation (silver-plate test)"),
    "f84r":  ("Practica", 12, "gold dissolution (balneum + putrefaction)"),
    "f79r":  ("Mercuriorum", 12, "mercury sublimation -> elixir"),
    "f82r":  ("Mercuriorum", 19, "III.19.1-5 multi-recipe"),
    "f76v":  ("Mercuriorum", 15, "ferment conversion (join H + bind)"),
    "f81v":  ("Mercuriorum", 18, "potable gold / water of life"),
    "f112v": ("Mercuriorum", 1,  "lunaria -> quicksilver pipeline origin"),
    "f103r": ("Mercuriorum", 16, "ferment multiplication"),
    "f116r": ("Mercuriorum", 4,  "fixation / fusibility test"),
    "f112r": ("Mercuriorum", 11, "red mercury tincture (cohobation)"),
}

WRITTEN_EN = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
    "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12,
    "thirteen": 13, "fourteen": 14, "fifteen": 15, "twenty": 20, "thirty": 30,
    "forty": 40, "fifty": 50, "hundred": 100,
    "twice": 2, "thrice": 3, "double": 2, "triple": 3, "quadruple": 4,
    "ninefold": 9, "tenfold": 10, "sevenfold": 7, "fivefold": 5, "fourfold": 4,
    "threefold": 3, "twofold": 2, "first": 1, "second": 2, "third": 3,
    "fourth": 4, "fifth": 5, "sixth": 6, "seventh": 7, "eighth": 8,
    "ninth": 9, "tenth": 10,
}

LATIN_NUM = {
    "semel": 1, "bis": 2, "ter": 3, "quater": 4, "quinquies": 5, "sexies": 6,
    "septies": 7, "octies": 8, "novies": 9, "decies": 10, "undecies": 11,
    "duodecies": 12,
    "primus": 1, "secundus": 2, "tertius": 3, "quartus": 4, "quintus": 5,
    "sextus": 6, "septimus": 7, "octavus": 8, "nonus": 9, "decimus": 10,
}

# Multiplier context hints (within +/-5 words of number)
MULT_CONTEXTS = ["times", "time", "fold", "cycles", "cycle", "iterat",
                 "repeat", "again", "round", "rounds", "passes", "operations",
                 "distillations", "reflux", "sublimation"]


def find_numeric_mentions(text):
    """Extract all numeric mentions: digits, written numbers, Latin numerals."""
    text_lower = text.lower()

    # Digits (1-99)
    digits = []
    for m in re.finditer(r"\b(\d+)\b", text_lower):
        n = int(m.group(1))
        if 1 <= n <= 99:
            # Get context: 50 chars around
            start = max(0, m.start() - 50)
            end = min(len(text_lower), m.end() + 50)
            context = text_lower[start:end].replace("\n", " ")
            # Check for multiplier hint nearby
            mult_hint = any(c in context for c in MULT_CONTEXTS)
            digits.append({"n": n, "context": context, "mult_hint": mult_hint})

    # Written English numbers
    written = []
    for word, n in WRITTEN_EN.items():
        for m in re.finditer(r"\b" + word + r"\b", text_lower):
            start = max(0, m.start() - 50)
            end = min(len(text_lower), m.end() + 50)
            context = text_lower[start:end].replace("\n", " ")
            mult_hint = any(c in context for c in MULT_CONTEXTS)
            written.append({"n": n, "word": word, "context": context, "mult_hint": mult_hint})

    # Latin numerals (in case)
    latin = []
    for word, n in LATIN_NUM.items():
        for m in re.finditer(r"\b" + word + r"\b", text_lower):
            start = max(0, m.start() - 50)
            end = min(len(text_lower), m.end() + 50)
            context = text_lower[start:end].replace("\n", " ")
            latin.append({"n": n, "word": word, "context": context})

    return digits, written, latin


def main():
    pl_struct = load_pl_structural_profile()
    chapters = pl_struct["E1_chapters"]

    en_path = Path(__file__).resolve().parents[3] / "sources" / "pseudo_lull_testamentum" / "testamentum_complete_english.txt"
    en_lines = en_path.read_text(encoding="utf-8").splitlines()

    results = {}
    for folio, (book, chapter_num, label) in MATCHED.items():
        # Find chapter
        ch = None
        for c in chapters:
            if c.get("part") == book and c.get("number") == chapter_num:
                ch = c
                break
        if ch is None:
            print(f"  {folio}: chapter not found ({book} {chapter_num})")
            continue
        en_start = ch.get("en_line_start", 0) - 1
        en_end = ch.get("en_line_end", 0)
        text = "\n".join(en_lines[en_start:en_end])
        n_words = len(text.split())

        digits, written, latin = find_numeric_mentions(text)

        results[folio] = {
            "book": book, "chapter": chapter_num, "label": label,
            "n_words": n_words,
            "digits": digits, "written_numbers": written, "latin_numerals": latin,
        }

        print(f"\n=== {folio} ({book} {chapter_num}: {label}) — {n_words} words ===")
        if digits:
            print("  DIGITS:")
            for d in digits:
                hint = " *MULT*" if d["mult_hint"] else ""
                print(f"    {d['n']:>3}{hint}  ...{d['context']}...")
        if written:
            print("  WRITTEN:")
            for w in written:
                hint = " *MULT*" if w["mult_hint"] else ""
                print(f"    {w['n']:>3} ({w['word']}){hint}  ...{w['context']}...")
        if latin:
            print("  LATIN NUMERALS:")
            for l in latin:
                print(f"    {l['n']:>3} ({l['word']})  ...{l['context']}...")

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(results, indent=2, default=str))
    print(f"\nWrote {OUT_PATH}")


if __name__ == "__main__":
    main()
