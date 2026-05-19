"""
Audit: which folios contribute Scribe 3's 875 Currier-A P-placement tokens?

Davis attributes all of Currier A to Scribe 1 in her narrative (p. 179), but
the CSV puts Scribe 3 on Q16 inner bifolium (botanical, Currier-A-typical) and
on Q8 bifolium 58/65 (also botanical). If the 875 A-tokens concentrate on
those folios, the data is internally consistent and Davis just didn't
explicitly address dialect for those minor Scribe-3 botanical pages.

If the tokens come from elsewhere, our CSV has an error.
"""

import csv
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from scripts.voynich import Transcript

ATTRIBUTION_CSV = ROOT / 'phases' / 'PHASE_702_SCRIBE_SUBSTRATE' / 'data' / 'davis_scribe_attribution.csv'


def load_attribution():
    attr = {}
    with open(ATTRIBUTION_CSV, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            attr[row['folio'].strip()] = (row['scribe'].strip(),
                                          row['confidence'].strip(),
                                          row['notes'].strip())
    return attr


def folio_match(token_folio, attribution_keys):
    if token_folio in attribution_keys:
        return token_folio
    if len(token_folio) > 2 and token_folio[-1].isdigit():
        stripped = token_folio[:-1]
        if stripped in attribution_keys:
            return stripped
    return None


def main():
    attr = load_attribution()
    keys = set(attr.keys())

    tx = Transcript()

    # Per-folio counts for Scribe 3 in Currier A, P-placement
    folio_counts = defaultdict(int)
    folio_examples = defaultdict(list)

    for token in tx.all(h_only=True):
        if not token.word.strip() or '*' in token.word:
            continue
        if token.language != 'A':
            continue
        if not token.placement.startswith('P'):
            continue

        matched = folio_match(token.folio, keys)
        if matched is None:
            continue
        scribe, conf, notes = attr[matched]
        if scribe != '3':
            continue

        folio_counts[token.folio] += 1
        if len(folio_examples[token.folio]) < 3:
            folio_examples[token.folio].append(token.word)

    print("=" * 70)
    print("SCRIBE 3 + CURRIER A + P-PLACEMENT — per-folio breakdown")
    print("=" * 70)
    print(f"\n{'Folio':<10}{'N':>6}  {'Davis CSV mapping (notes)':<40}{'Examples'}")
    print("-" * 95)

    total = 0
    for folio in sorted(folio_counts.keys(), key=lambda f: -folio_counts[f]):
        n = folio_counts[folio]
        total += n
        matched = folio_match(folio, keys)
        scribe, conf, notes = attr[matched]
        examples = ', '.join(folio_examples[folio])
        print(f"{folio:<10}{n:>6}  {notes:<40}{examples}")

    print(f"\nTOTAL: {total}")

    # Davis's narrative claim: Scribe 3 = Q8 inner bifolium (58/65),
    # Q16 inner bifolium, Q18 starred (f103-f116).
    # Among these, only Q8 (58/65) and Q16 inner are botanical → could be Currier A.
    # Q18 is starred paragraphs → Currier B.
    print("\n" + "=" * 70)
    print("DAVIS'S SCRIBE-3 ATTRIBUTION (from paper narrative + table)")
    print("=" * 70)
    print("""
Davis assigns Scribe 3 to:
  - Q8 inner bifolium: f58, f65   (botanical, potentially Currier A)
  - Q16 inner bifolium: f93-f96 region  (botanical, potentially Currier A)
  - Q18 starred paragraphs: f103-f116  (Currier B per Currier 1976)

Expected Currier-A-typed folios under Scribe 3: f58, f65, f93/f94/f95/f96 region.
""")


if __name__ == '__main__':
    main()
