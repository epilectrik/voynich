"""
PHASE_702 Feasibility Check: per-(scribe, Currier-class, placement) token counts.

Joins Davis 2020 scribe attribution onto H-track transcript and reports bucket
sizes to determine which scribes have sufficient N for substrate metric tests.

Pre-test floor: N >= 1000 P-placement tokens per (scribe, Currier-B) bucket
for primary substrate metrics (C2032 lag2/lag1, C2015 char-LM, C2022 Markov).
"""

import csv
import sys
from collections import defaultdict
from pathlib import Path

# Add scripts/ to path
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from scripts.voynich import Transcript

ATTRIBUTION_CSV = ROOT / 'phases' / 'PHASE_702_SCRIBE_SUBSTRATE' / 'data' / 'davis_scribe_attribution.csv'


def load_attribution():
    """Load Davis attribution as {folio: (scribe, confidence)}."""
    attr = {}
    with open(ATTRIBUTION_CSV, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            folio = row['folio'].strip()
            scribe = row['scribe'].strip()
            conf = row['confidence'].strip()
            attr[folio] = (scribe, conf)
    return attr


def folio_match(token_folio, attribution_keys):
    """
    Match transcript folio to attribution CSV folio.

    Transcript folios: 'f1r', 'f67r1', 'f86v3', 'f115r' etc.
    Attribution folios should match directly. If a transcript folio has a
    foldout sub-panel (e.g., 'f86v3') but CSV only has 'f86v', return parent.
    """
    if token_folio in attribution_keys:
        return token_folio
    # Try stripping panel suffix (e.g., f67r1 -> f67r)
    for suffix_len in (1,):
        if len(token_folio) > 2 and token_folio[-1].isdigit():
            stripped = token_folio[:-suffix_len]
            if stripped in attribution_keys:
                return stripped
    return None


def main():
    print(f"Loading attribution from {ATTRIBUTION_CSV.relative_to(ROOT)}")
    attr = load_attribution()
    print(f"  Loaded {len(attr)} folio attributions")
    attribution_keys = set(attr.keys())

    print("\nLoading H-track transcript...")
    tx = Transcript()

    # Count all H-track tokens by (scribe, currier_class, placement_class)
    # Currier class: 'A', 'B', 'NA' (AZC)
    # Placement class: 'P' (paragraph text), 'L' (label), 'other' (R/S/C/X/Y/N/T diagram)
    buckets = defaultdict(int)
    folio_to_scribe = {}
    unmatched_folios = set()
    matched_folios = set()

    for token in tx.all(h_only=True):
        # Skip empty words and uncertain tokens
        if not token.word.strip():
            continue
        if '*' in token.word:
            continue

        matched = folio_match(token.folio, attribution_keys)
        if matched is None:
            unmatched_folios.add(token.folio)
            continue

        scribe, conf = attr[matched]
        matched_folios.add(token.folio)
        folio_to_scribe[token.folio] = scribe

        placement = token.placement
        if placement.startswith('P'):
            place_class = 'P'
        elif placement.startswith('L'):
            place_class = 'L'
        else:
            place_class = 'other'

        currier = token.language if token.language else 'NA'
        if currier not in ('A', 'B'):
            currier = 'NA'

        buckets[(scribe, currier, place_class)] += 1

    # Report
    print("\n" + "=" * 70)
    print("PER-(SCRIBE, CURRIER-CLASS, PLACEMENT) TOKEN COUNTS")
    print("=" * 70)
    print(f"\n{'Scribe':<8}{'Currier':<10}{'Placement':<12}{'N':>10}")
    print("-" * 40)

    scribes = sorted(set(k[0] for k in buckets.keys()))
    curriers = ['A', 'B', 'NA']
    placements = ['P', 'L', 'other']

    for scribe in scribes:
        for currier in curriers:
            for placement in placements:
                n = buckets.get((scribe, currier, placement), 0)
                if n > 0:
                    print(f"{scribe:<8}{currier:<10}{placement:<12}{n:>10}")
        print()

    # Per-scribe Currier-B P-placement totals (the substrate test's target bucket)
    print("=" * 70)
    print("SUBSTRATE TEST TARGET: Currier-B, P-placement tokens per scribe")
    print("=" * 70)
    print(f"\n{'Scribe':<8}{'N (B, P)':>12}{'Status':>20}")
    print("-" * 40)
    for scribe in scribes:
        n = buckets.get((scribe, 'B', 'P'), 0)
        if n >= 3000:
            status = 'PASS (>=3000)'
        elif n >= 1000:
            status = 'MARGINAL (1000-3000)'
        elif n > 0:
            status = 'INSUFFICIENT'
        else:
            status = 'NONE'
        print(f"{scribe:<8}{n:>12}{status:>20}")

    # Per-scribe totals (all placements, all dialects)
    print("\n" + "=" * 70)
    print("PER-SCRIBE TOTAL H-TRACK TOKEN COUNTS (all placements, all dialects)")
    print("=" * 70)
    print(f"\n{'Scribe':<8}{'Total':>12}")
    print("-" * 20)
    for scribe in scribes:
        total = sum(v for k, v in buckets.items() if k[0] == scribe)
        print(f"{scribe:<8}{total:>12}")

    grand_total = sum(buckets.values())
    print(f"\n{'TOTAL':<8}{grand_total:>12}")

    # Folio coverage diagnostics
    print(f"\nFolios with H-track tokens matched to a Davis scribe: {len(matched_folios)}")
    if unmatched_folios:
        print(f"\nUnmatched transcript folios ({len(unmatched_folios)}):")
        for f in sorted(unmatched_folios):
            n = sum(1 for t in tx.all(h_only=True)
                    if t.folio == f and t.word.strip() and '*' not in t.word)
            print(f"  {f}: {n} tokens")

    # Confidence breakdown for matched folios
    conf_counts = defaultdict(int)
    for folio, scribe in folio_to_scribe.items():
        # Get conf for the matched key
        matched = folio_match(folio, attribution_keys)
        _, conf = attr[matched]
        conf_counts[conf] += 1
    print(f"\nFolio attribution confidence distribution:")
    for conf, n in sorted(conf_counts.items()):
        print(f"  {conf}: {n} folios")

    # Decision summary
    print("\n" + "=" * 70)
    print("FEASIBILITY VERDICT")
    print("=" * 70)
    eligible_scribes = [s for s in scribes
                        if buckets.get((s, 'B', 'P'), 0) >= 1000]
    print(f"\nScribes eligible for Currier-B substrate test (N >= 1000 P-tokens):")
    for s in eligible_scribes:
        n = buckets.get((s, 'B', 'P'), 0)
        print(f"  Scribe {s}: N = {n}")

    if len(eligible_scribes) >= 2:
        print(f"\n  -> {len(eligible_scribes)}-way cross-scribe comparison FEASIBLE")
    elif len(eligible_scribes) == 1:
        print(f"\n  -> Only 1 eligible scribe: substrate test NOT feasible as cross-scribe comparison")
        print(f"     Substrate is effectively monoscribal in P-placement Currier B")
    else:
        print(f"\n  -> No eligible scribes: data issue or attribution misalignment")


if __name__ == '__main__':
    main()
