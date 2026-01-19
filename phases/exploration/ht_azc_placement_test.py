#!/usr/bin/env python3
"""
HT-AZC Placement Affinity Test

Tests whether HT density differs between R (radial/interior) and S (sector/boundary)
placements in Zodiac AZC folios.

Hypothesis:
  If HT serves as "attention at phase boundaries," HT density should differ
  between R and S placement families.

This is a SINGLE focused test. Stop after this regardless of outcome.
"""

import json
import csv
import numpy as np
from pathlib import Path
from collections import defaultdict, Counter
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

BASE = Path(__file__).parent.parent.parent
RESULTS = BASE / "results"
TRANSCRIPTION = BASE / "data" / "transcriptions" / "interlinear_full_words.txt"
AZC_FOLIO_FEATURES = RESULTS / "azc_folio_features.json"
GRAMMAR_PATH = RESULTS / "canonical_grammar.json"

def load_azc_features():
    """Load AZC folio features."""
    with open(AZC_FOLIO_FEATURES) as f:
        data = json.load(f)
    return data.get('folios', {})

def load_transcription():
    """Load full transcription."""
    rows = []
    with open(TRANSCRIPTION, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t', quotechar='"')
        for row in reader:
            transcriber = row.get('transcriber', '').strip().strip('"')
            if transcriber != 'H':
                continue
            rows.append(row)
    return rows

def load_b_grammar():
    """Load B grammar vocabulary for HT classification."""
    # Load from canonical_grammar - extract terminal symbols
    with open(GRAMMAR_PATH) as f:
        data = json.load(f)

    # The grammar has terminals list with symbol field
    terminals = data.get('terminals', {}).get('list', [])
    vocab = set()
    for t in terminals:
        if 'symbol' in t:
            vocab.add(t['symbol'])

    return vocab

def get_zodiac_folios(azc_features):
    """Get list of Zodiac (section='Z') folios."""
    zodiac = []
    for folio, features in azc_features.items():
        if features.get('section') == 'Z':
            zodiac.append(folio)
    return zodiac

def classify_token_system(token, b_vocab):
    """
    Classify a token as HT (Human Track) or operational.

    HT = tokens NOT in the canonical B grammar vocabulary.
    This matches the definition in human_track.md.
    """
    # Skip damaged tokens
    if '*' in token or '?' in token:
        return 'DAMAGED'

    # HT is defined as NOT in the 479-type B grammar
    # But since we only have 20 high-level terminals, use prefix heuristic

    # HT prefixes (from C347 - disjoint from B prefixes)
    ht_prefixes = {'yk', 'op', 'yt', 'sa', 'so', 'ka', 'dc', 'pc'}

    # B prefixes (from C347)
    b_prefixes = {'ch', 'qo', 'sh', 'da', 'ok', 'ot', 'ct', 'ol'}

    # Check prefix
    for p in sorted(ht_prefixes, key=len, reverse=True):
        if token.startswith(p):
            return 'HT'

    for p in sorted(b_prefixes, key=len, reverse=True):
        if token.startswith(p):
            return 'B'

    # If no clear prefix, check if in B vocabulary
    if token in b_vocab:
        return 'B'

    # Default to HT for unclassified (conservative - matches residue definition)
    return 'HT'

def get_placement_family(placement):
    """Classify placement into R (radial) or S (sector) family."""
    if not placement:
        return 'OTHER'
    if placement.startswith('R'):
        return 'R'
    elif placement.startswith('S'):
        return 'S'
    elif placement == 'C':
        return 'C'  # Central - separate category
    else:
        return 'OTHER'

def extract_zodiac_tokens(rows, zodiac_folios, b_vocab):
    """
    Extract all tokens from Zodiac AZC folios with placement and HT classification.
    """
    tokens = []

    for row in rows:
        folio = row.get('folio', '').strip('"')
        if folio not in zodiac_folios:
            continue

        language = row.get('language', '').strip('"')
        placement = row.get('placement', '').strip('"')
        token = row.get('word', '').strip('"')

        # Only AZC tokens (language == 'NA')
        if language != 'NA':
            continue

        if not token or not placement:
            continue

        # Classify
        system = classify_token_system(token, b_vocab)
        family = get_placement_family(placement)

        if system == 'DAMAGED':
            continue

        tokens.append({
            'folio': folio,
            'token': token,
            'placement': placement,
            'family': family,
            'is_ht': system == 'HT'
        })

    return tokens

def run_placement_affinity_test(tokens):
    """
    Test whether HT density differs between R and S placement families.
    """
    print("=" * 70)
    print("HT-AZC Placement Affinity Test")
    print("=" * 70)
    print("\nHypothesis: HT density differs between R (radial) and S (sector) positions")
    print("=" * 70)

    # Count by family
    family_counts = defaultdict(lambda: {'ht': 0, 'non_ht': 0, 'total': 0})

    for t in tokens:
        family = t['family']
        family_counts[family]['total'] += 1
        if t['is_ht']:
            family_counts[family]['ht'] += 1
        else:
            family_counts[family]['non_ht'] += 1

    print(f"\n[1] Token counts by placement family:")
    for family in ['R', 'S', 'C', 'OTHER']:
        counts = family_counts[family]
        if counts['total'] > 0:
            ht_rate = counts['ht'] / counts['total']
            print(f"    {family}: {counts['total']} tokens, HT={counts['ht']} ({ht_rate:.1%})")

    # Build contingency table for R vs S
    r_counts = family_counts['R']
    s_counts = family_counts['S']

    if r_counts['total'] < 10 or s_counts['total'] < 10:
        print("\n[ERROR] Insufficient data for R vs S comparison")
        return {'error': 'insufficient_data'}

    # Contingency table
    #              HT    Non-HT
    # R-family     a     b
    # S-family     c     d

    contingency = np.array([
        [r_counts['ht'], r_counts['non_ht']],
        [s_counts['ht'], s_counts['non_ht']]
    ])

    print(f"\n[2] Contingency table (R vs S):")
    print(f"              HT      Non-HT")
    print(f"    R-family  {r_counts['ht']:5d}   {r_counts['non_ht']:5d}")
    print(f"    S-family  {s_counts['ht']:5d}   {s_counts['non_ht']:5d}")

    # Chi-squared test
    chi2, p_value, dof, expected = stats.chi2_contingency(contingency)

    # Cramér's V
    n = contingency.sum()
    cramers_v = np.sqrt(chi2 / n) if n > 0 else 0

    # HT rates
    r_ht_rate = r_counts['ht'] / r_counts['total']
    s_ht_rate = s_counts['ht'] / s_counts['total']

    print(f"\n[3] Statistical test:")
    print(f"    Chi-squared: {chi2:.2f}")
    print(f"    Degrees of freedom: {dof}")
    print(f"    P-value: {p_value:.4f}")
    print(f"    Cramer's V: {cramers_v:.3f}")

    print(f"\n[4] HT rates:")
    print(f"    R-family: {r_ht_rate:.1%}")
    print(f"    S-family: {s_ht_rate:.1%}")
    print(f"    Difference: {abs(r_ht_rate - s_ht_rate):.1%}")

    # Interpretation
    print(f"\n[5] Interpretation:")

    significant = p_value < 0.05
    meaningful_effect = cramers_v > 0.1

    if significant:
        if s_ht_rate > r_ht_rate:
            direction = "S > R"
            interpretation = "HT preferentially marks BOUNDARIES (sector positions)"
        else:
            direction = "R > S"
            interpretation = "HT preferentially marks INTERIOR (radial positions)"

        print(f"    SIGNIFICANT (p={p_value:.4f} < 0.05)")
        print(f"    Direction: {direction}")
        print(f"    Interpretation: {interpretation}")

        if meaningful_effect:
            print(f"    Effect size: MEANINGFUL (V={cramers_v:.3f} > 0.1)")
            verdict = "SIGNIFICANT_MEANINGFUL"
        else:
            print(f"    Effect size: SMALL (V={cramers_v:.3f} < 0.1)")
            verdict = "SIGNIFICANT_SMALL"
    else:
        print(f"    NOT SIGNIFICANT (p={p_value:.4f} > 0.05)")
        print(f"    Interpretation: HT is position-UNIFORM across R and S")
        verdict = "NOT_SIGNIFICANT"

    # Extended analysis: by specific placement
    print(f"\n[6] Detailed breakdown by specific placement:")
    placement_counts = defaultdict(lambda: {'ht': 0, 'non_ht': 0, 'total': 0})

    for t in tokens:
        p = t['placement']
        placement_counts[p]['total'] += 1
        if t['is_ht']:
            placement_counts[p]['ht'] += 1
        else:
            placement_counts[p]['non_ht'] += 1

    for p in sorted(placement_counts.keys()):
        counts = placement_counts[p]
        if counts['total'] >= 5:  # Only show placements with enough data
            rate = counts['ht'] / counts['total']
            print(f"    {p:4s}: {counts['total']:4d} tokens, HT={counts['ht']:3d} ({rate:.1%})")

    # Final verdict
    print(f"\n{'='*70}")
    print("VERDICT")
    print("=" * 70)

    if verdict == "SIGNIFICANT_MEANINGFUL":
        print(f"\nHT shows SIGNIFICANT placement affinity with MEANINGFUL effect size")
        print(f"-> Document as C457")
        action = "DOCUMENT_C457"
    elif verdict == "SIGNIFICANT_SMALL":
        print(f"\nHT shows SIGNIFICANT placement affinity but SMALL effect size")
        print(f"-> Document as C457 with caveat about practical significance")
        action = "DOCUMENT_C457_WEAK"
    else:
        print(f"\nHT shows NO significant placement affinity")
        print(f"-> Close investigation: HT anchors globally, not positionally")
        action = "CLOSE_INVESTIGATION"

    results = {
        'contingency': contingency.tolist(),
        'chi2': float(chi2),
        'p_value': float(p_value),
        'cramers_v': float(cramers_v),
        'r_ht_rate': float(r_ht_rate),
        's_ht_rate': float(s_ht_rate),
        'r_total': r_counts['total'],
        's_total': s_counts['total'],
        'verdict': verdict,
        'action': action,
        'placement_breakdown': {p: dict(c) for p, c in placement_counts.items()}
    }

    return results

def main():
    print("=" * 70)
    print("HT-AZC Placement Affinity Test")
    print("=" * 70)
    print("\nThis is a SINGLE focused test per the approved plan.")
    print("Stop after this regardless of outcome.")
    print("=" * 70)

    # Load data
    print("\n[Loading data...]")
    azc_features = load_azc_features()
    print(f"  AZC folios: {len(azc_features)}")

    zodiac_folios = get_zodiac_folios(azc_features)
    print(f"  Zodiac folios: {len(zodiac_folios)}")
    print(f"    {', '.join(sorted(zodiac_folios))}")

    b_vocab = load_b_grammar()
    print(f"  B grammar terminals: {len(b_vocab)}")

    rows = load_transcription()
    print(f"  Transcription rows: {len(rows)}")

    # Extract Zodiac tokens
    tokens = extract_zodiac_tokens(rows, zodiac_folios, b_vocab)
    print(f"  Zodiac AZC tokens: {len(tokens)}")

    # Run test
    results = run_placement_affinity_test(tokens)

    # Save results
    output = {
        'metadata': {
            'test': 'HT-AZC Placement Affinity',
            'hypothesis': 'HT density differs between R and S placements in Zodiac AZC',
            'n_zodiac_folios': len(zodiac_folios),
            'n_tokens': len(tokens)
        },
        'results': results
    }

    output_path = RESULTS / "ht_azc_placement_affinity.json"
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\n[SAVED] {output_path}")

    return results

if __name__ == "__main__":
    main()
