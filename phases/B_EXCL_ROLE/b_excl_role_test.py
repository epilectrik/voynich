#!/usr/bin/env python3
"""
B-EXCL-ROLE: B-Exclusive MIDDLEs as Grammar-Internal Operators

Phase: B-EXCL-ROLE
Research Question: Are B-exclusive MIDDLEs structurally localized grammar operators?

Tests:
1. Grammar Adjacency Enrichment (LINK, kernel, boundary)
2. Positional Rigidity vs CEI
3. Type Concentration

Expected: B-EXCL show localized, concentrated, grammar-adjacent behavior.
"""

import json
from pathlib import Path
from collections import Counter, defaultdict
from scipy.stats import spearmanr, chi2_contingency, fisher_exact
import numpy as np

# =============================================================================
# CONFIGURATION
# =============================================================================

PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_PATH = PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt'
B_METRICS_PATH = PROJECT_ROOT / 'results' / 'b_macro_scaffold_audit.json'
OUTPUT_PATH = PROJECT_ROOT / 'results' / 'b_excl_role.json'

# PREFIX/SUFFIX lists (same as MIDDLE-AB)
PREFIXES = ['ch', 'sh', 'qo', 'da', 'ok', 'ot', 'ol', 'ct']
EXTENDED_PREFIXES = [
    'pch', 'tch', 'kch', 'dch', 'fch', 'rch', 'sch',
    'lch', 'lk', 'lsh', 'yk',
    'ke', 'te', 'se', 'de', 'pe',
    'so', 'ko', 'to', 'do', 'po',
    'sa', 'ka', 'ta',
    'al', 'ar', 'or',
]
ALL_PREFIXES = sorted(EXTENDED_PREFIXES + PREFIXES, key=len, reverse=True)

SUFFIXES = [
    'odaiin', 'edaiin', 'adaiin', 'okaiin', 'ekaiin', 'akaiin',
    'otaiin', 'etaiin', 'ataiin',
    'daiin', 'kaiin', 'taiin', 'aiin', 'oiin', 'eiin',
    'chedy', 'shedy', 'kedy', 'tedy',
    'cheey', 'sheey', 'keey', 'teey',
    'chey', 'shey', 'key', 'tey',
    'chy', 'shy', 'ky', 'ty', 'dy', 'hy', 'ly', 'ry',
    'edy', 'eey', 'ey',
    'chol', 'shol', 'kol', 'tol',
    'chor', 'shor', 'kor', 'tor',
    'eeol', 'eol', 'ool',
    'iin', 'ain', 'oin', 'ein', 'in', 'an', 'on', 'en',
    'ol', 'or', 'ar', 'al', 'er', 'el',
    'am', 'om', 'em', 'im',
    'y', 'l', 'r', 'm', 'n', 's', 'g',
]

# Kernel token (per C243)
KERNEL_TOKEN = 'daiin'

# REGIME ordering
REGIME_ORDER = {'REGIME_2': 0, 'REGIME_1': 1, 'REGIME_4': 2, 'REGIME_3': 3}


def extract_middle(token):
    """Extract MIDDLE from token."""
    prefix = None
    for p in ALL_PREFIXES:
        if token.startswith(p):
            prefix = p
            break
    if not prefix:
        return None, None, None

    remainder = token[len(prefix):]
    suffix = None
    for s in SUFFIXES:
        if remainder.endswith(s) and len(remainder) >= len(s):
            suffix = s
            break

    if suffix:
        middle = remainder[:-len(suffix)]
    else:
        middle = remainder
        suffix = ''

    if middle == '':
        middle = '_EMPTY_'

    return prefix, middle, suffix


def is_link_token(token):
    """Check if token is a LINK token (qo- prefix per C366)."""
    return token.startswith('qo')


def is_kernel_token(token):
    """Check if token is a kernel token (daiin per C243)."""
    return token == KERNEL_TOKEN or token.startswith('daiin')


def load_data():
    """Load H-only transcript with positional information."""
    # Group tokens by (folio, line) to reconstruct line structure
    a_middles = Counter()
    b_middles = Counter()
    b_lines = defaultdict(list)  # (folio, line_num) -> [(pos, word, middle)]

    with open(DATA_PATH, 'r', encoding='utf-8') as f:
        header = f.readline()

        for line in f:
            parts = line.strip().split('\t')
            if len(parts) > 14:
                transcriber = parts[12].strip('"').strip()
                if transcriber != 'H':
                    continue

                word = parts[0].strip('"').strip().lower()
                lang = parts[6].strip('"').strip()
                folio = parts[2].strip('"').strip()
                line_num = parts[11].strip('"').strip()
                try:
                    pos = int(parts[13].strip('"').strip())  # line_initial = position
                except:
                    continue

                if not word or '*' in word:
                    continue

                prefix, middle, suffix = extract_middle(word)

                if lang == 'A' and middle:
                    a_middles[middle] += 1
                elif lang == 'B':
                    # Store with position for adjacency analysis
                    b_lines[(folio, line_num)].append({
                        'pos': pos,
                        'word': word,
                        'middle': middle,
                        'is_link': is_link_token(word),
                        'is_kernel': is_kernel_token(word),
                    })
                    if middle:
                        b_middles[middle] += 1

    return a_middles, b_middles, b_lines


def build_middle_classifications(a_middles, b_middles):
    """Build SHARED and B-EXCL sets."""
    a_set = set(a_middles.keys())
    b_set = set(b_middles.keys())

    shared = a_set & b_set
    b_excl = b_set - a_set

    return shared, b_excl


def test1_grammar_adjacency(b_lines, shared, b_excl):
    """
    TEST 1: Grammar Adjacency Enrichment

    Check if B-EXCL MIDDLEs are enriched adjacent to LINK/kernel/boundary positions.
    """
    # Counters for B-EXCL occurrences
    b_excl_total = 0
    b_excl_link_adjacent = 0
    b_excl_kernel_adjacent = 0
    b_excl_boundary = 0

    # Counters for SHARED occurrences (baseline)
    shared_total = 0
    shared_link_adjacent = 0
    shared_kernel_adjacent = 0
    shared_boundary = 0

    for (folio, line_num), tokens in b_lines.items():
        if len(tokens) == 0:
            continue

        # Sort by position
        tokens = sorted(tokens, key=lambda x: x['pos'])
        n_tokens = len(tokens)

        for i, tok in enumerate(tokens):
            middle = tok['middle']
            if middle is None:
                continue

            # Check if at boundary (first or last position)
            is_boundary = (i == 0) or (i == n_tokens - 1)

            # Check if adjacent to LINK
            is_link_adj = False
            if i > 0 and tokens[i-1]['is_link']:
                is_link_adj = True
            if i < n_tokens - 1 and tokens[i+1]['is_link']:
                is_link_adj = True

            # Check if adjacent to kernel
            is_kernel_adj = False
            if i > 0 and tokens[i-1]['is_kernel']:
                is_kernel_adj = True
            if i < n_tokens - 1 and tokens[i+1]['is_kernel']:
                is_kernel_adj = True

            # Classify and count
            if middle in b_excl:
                b_excl_total += 1
                if is_link_adj:
                    b_excl_link_adjacent += 1
                if is_kernel_adj:
                    b_excl_kernel_adjacent += 1
                if is_boundary:
                    b_excl_boundary += 1
            elif middle in shared:
                shared_total += 1
                if is_link_adj:
                    shared_link_adjacent += 1
                if is_kernel_adj:
                    shared_kernel_adjacent += 1
                if is_boundary:
                    shared_boundary += 1

    # Compute rates
    b_excl_link_rate = b_excl_link_adjacent / b_excl_total if b_excl_total > 0 else 0
    b_excl_kernel_rate = b_excl_kernel_adjacent / b_excl_total if b_excl_total > 0 else 0
    b_excl_boundary_rate = b_excl_boundary / b_excl_total if b_excl_total > 0 else 0

    shared_link_rate = shared_link_adjacent / shared_total if shared_total > 0 else 0
    shared_kernel_rate = shared_kernel_adjacent / shared_total if shared_total > 0 else 0
    shared_boundary_rate = shared_boundary / shared_total if shared_total > 0 else 0

    # Compute enrichment
    link_enrichment = b_excl_link_rate / shared_link_rate if shared_link_rate > 0 else float('inf')
    kernel_enrichment = b_excl_kernel_rate / shared_kernel_rate if shared_kernel_rate > 0 else float('inf')
    boundary_enrichment = b_excl_boundary_rate / shared_boundary_rate if shared_boundary_rate > 0 else float('inf')

    # Fisher's exact test for each
    def fisher_test(a, b, c, d):
        """2x2 contingency: [[a, b], [c, d]]"""
        try:
            _, p = fisher_exact([[a, b], [c, d]])
            return p
        except:
            return 1.0

    link_p = fisher_test(
        b_excl_link_adjacent, b_excl_total - b_excl_link_adjacent,
        shared_link_adjacent, shared_total - shared_link_adjacent
    )
    kernel_p = fisher_test(
        b_excl_kernel_adjacent, b_excl_total - b_excl_kernel_adjacent,
        shared_kernel_adjacent, shared_total - shared_kernel_adjacent
    )
    boundary_p = fisher_test(
        b_excl_boundary, b_excl_total - b_excl_boundary,
        shared_boundary, shared_total - shared_boundary
    )

    return {
        'b_excl_total': b_excl_total,
        'shared_total': shared_total,
        'link': {
            'b_excl_count': b_excl_link_adjacent,
            'b_excl_rate': b_excl_link_rate,
            'shared_count': shared_link_adjacent,
            'shared_rate': shared_link_rate,
            'enrichment': link_enrichment,
            'p_value': link_p,
        },
        'kernel': {
            'b_excl_count': b_excl_kernel_adjacent,
            'b_excl_rate': b_excl_kernel_rate,
            'shared_count': shared_kernel_adjacent,
            'shared_rate': shared_kernel_rate,
            'enrichment': kernel_enrichment,
            'p_value': kernel_p,
        },
        'boundary': {
            'b_excl_count': b_excl_boundary,
            'b_excl_rate': b_excl_boundary_rate,
            'shared_count': shared_boundary,
            'shared_rate': shared_boundary_rate,
            'enrichment': boundary_enrichment,
            'p_value': boundary_p,
        },
    }


def test2_positional_rigidity(b_lines, b_excl, b_metrics):
    """
    TEST 2: Positional Rigidity vs CEI

    High-CEI folios should show tighter B-EXCL localization (lower positional entropy).
    """
    folio_metrics = {}

    for (folio, line_num), tokens in b_lines.items():
        if folio not in folio_metrics:
            folio_metrics[folio] = {'positions': [], 'total_tokens': 0}

        tokens = sorted(tokens, key=lambda x: x['pos'])
        n_tokens = len(tokens)
        folio_metrics[folio]['total_tokens'] += n_tokens

        for i, tok in enumerate(tokens):
            if tok['middle'] in b_excl:
                # Normalized position (0-1)
                norm_pos = i / max(1, n_tokens - 1) if n_tokens > 1 else 0.5
                folio_metrics[folio]['positions'].append(norm_pos)

    # Compute positional entropy per folio
    folio_entropy = {}
    for folio, data in folio_metrics.items():
        positions = data['positions']
        if len(positions) < 3:
            continue

        # Discretize into 5 bins
        bins = [0, 0.2, 0.4, 0.6, 0.8, 1.0]
        hist, _ = np.histogram(positions, bins=bins)
        total = sum(hist)
        if total == 0:
            continue

        # Shannon entropy
        probs = hist / total
        entropy = -sum(p * np.log(p + 1e-10) for p in probs if p > 0)
        folio_entropy[folio] = entropy

    # Correlate with CEI
    common_folios = sorted(set(folio_entropy.keys()) & set(b_metrics.keys()))

    if len(common_folios) < 10:
        return {'error': f'Only {len(common_folios)} folios'}

    entropies = [folio_entropy[f] for f in common_folios]
    ceis = [b_metrics[f]['cei'] for f in common_folios]

    rho, p = spearmanr(entropies, ceis)

    # Regime breakdown
    regime_entropies = defaultdict(list)
    for f in common_folios:
        regime = b_metrics[f]['regime']
        regime_entropies[regime].append(folio_entropy[f])

    regime_means = {r: np.mean(v) for r, v in regime_entropies.items()}

    return {
        'n_folios': len(common_folios),
        'entropy_vs_cei': {
            'rho': rho,
            'p': p,
        },
        'regime_means': regime_means,
        'mean_entropy': np.mean(entropies),
        'std_entropy': np.std(entropies),
    }


def test3_type_concentration(b_lines, b_excl, shared):
    """
    TEST 3: Type Concentration

    A few B-EXCL MIDDLEs should dominate usage (top-10 > 60%).
    """
    # Count B-EXCL usage across all folios
    b_excl_usage = Counter()
    shared_usage = Counter()

    for (folio, line_num), tokens in b_lines.items():
        for tok in tokens:
            middle = tok['middle']
            if middle in b_excl:
                b_excl_usage[middle] += 1
            elif middle in shared:
                shared_usage[middle] += 1

    # B-EXCL concentration
    b_excl_total = sum(b_excl_usage.values())
    b_excl_sorted = sorted(b_excl_usage.values(), reverse=True)

    top5_b_excl = sum(b_excl_sorted[:5]) / b_excl_total if b_excl_total > 0 else 0
    top10_b_excl = sum(b_excl_sorted[:10]) / b_excl_total if b_excl_total > 0 else 0
    top20_b_excl = sum(b_excl_sorted[:20]) / b_excl_total if b_excl_total > 0 else 0

    # SHARED concentration (baseline)
    shared_total = sum(shared_usage.values())
    shared_sorted = sorted(shared_usage.values(), reverse=True)

    top5_shared = sum(shared_sorted[:5]) / shared_total if shared_total > 0 else 0
    top10_shared = sum(shared_sorted[:10]) / shared_total if shared_total > 0 else 0
    top20_shared = sum(shared_sorted[:20]) / shared_total if shared_total > 0 else 0

    # Top B-EXCL examples
    top_b_excl = b_excl_usage.most_common(15)

    return {
        'b_excl': {
            'total_usage': b_excl_total,
            'unique_types': len(b_excl_usage),
            'top5_coverage': top5_b_excl,
            'top10_coverage': top10_b_excl,
            'top20_coverage': top20_b_excl,
            'top15_examples': top_b_excl,
        },
        'shared': {
            'total_usage': shared_total,
            'unique_types': len(shared_usage),
            'top5_coverage': top5_shared,
            'top10_coverage': top10_shared,
            'top20_coverage': top20_shared,
        },
        'concentration_ratio': {
            'top10_b_excl_vs_shared': top10_b_excl / top10_shared if top10_shared > 0 else float('inf'),
        },
    }


def load_b_complexity_metrics():
    """Load CEI and REGIME per B folio."""
    with open(B_METRICS_PATH, 'r') as f:
        data = json.load(f)

    metrics = {}
    for folio, features in data.get('features', {}).items():
        metrics[folio] = {
            'cei': features.get('cei_total', 0),
            'regime': features.get('regime', 'UNKNOWN'),
        }

    return metrics


def main():
    print("=" * 70)
    print("B-EXCL-ROLE: B-Exclusive MIDDLEs as Grammar-Internal Operators")
    print("=" * 70)
    print()

    # Load data
    print("Loading H-only data with positions...")
    a_middles, b_middles, b_lines = load_data()
    print(f"  A unique MIDDLEs: {len(a_middles):,}")
    print(f"  B unique MIDDLEs: {len(b_middles):,}")
    print(f"  B lines: {len(b_lines):,}")
    print()

    # Build classifications
    print("Building MIDDLE classifications...")
    shared, b_excl = build_middle_classifications(a_middles, b_middles)
    print(f"  SHARED: {len(shared):,}")
    print(f"  B-EXCL: {len(b_excl):,}")
    print()

    # Load B metrics
    print("Loading B complexity metrics...")
    b_metrics = load_b_complexity_metrics()
    print(f"  Folios with metrics: {len(b_metrics):,}")
    print()

    # TEST 1: Grammar Adjacency
    print("=" * 70)
    print("TEST 1: Grammar Adjacency Enrichment")
    print("=" * 70)
    test1_results = test1_grammar_adjacency(b_lines, shared, b_excl)

    print(f"\nTotal B-EXCL occurrences: {test1_results['b_excl_total']:,}")
    print(f"Total SHARED occurrences: {test1_results['shared_total']:,}")

    for adj_type in ['link', 'kernel', 'boundary']:
        r = test1_results[adj_type]
        sig = "***" if r['p_value'] < 0.001 else "**" if r['p_value'] < 0.01 else "*" if r['p_value'] < 0.05 else ""
        print(f"\n{adj_type.upper()} adjacency:")
        print(f"  B-EXCL: {r['b_excl_rate']:.3f} ({r['b_excl_count']:,})")
        print(f"  SHARED: {r['shared_rate']:.3f} ({r['shared_count']:,})")
        print(f"  Enrichment: {r['enrichment']:.2f}x, p={r['p_value']:.4f} {sig}")

    # TEST 2: Positional Rigidity
    print()
    print("=" * 70)
    print("TEST 2: Positional Rigidity vs CEI")
    print("=" * 70)
    test2_results = test2_positional_rigidity(b_lines, b_excl, b_metrics)

    if 'error' not in test2_results:
        rho = test2_results['entropy_vs_cei']['rho']
        p = test2_results['entropy_vs_cei']['p']
        sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else ""
        print(f"\nPositional entropy vs CEI:")
        print(f"  rho = {rho:.3f}, p = {p:.4f} {sig}")
        print(f"  (Expect NEGATIVE: high CEI = tighter localization)")

        print(f"\nRegime means (entropy):")
        for regime in ['REGIME_2', 'REGIME_1', 'REGIME_4', 'REGIME_3']:
            if regime in test2_results['regime_means']:
                print(f"  {regime}: {test2_results['regime_means'][regime]:.3f}")
    else:
        print(f"  Error: {test2_results['error']}")

    # TEST 3: Type Concentration
    print()
    print("=" * 70)
    print("TEST 3: Type Concentration")
    print("=" * 70)
    test3_results = test3_type_concentration(b_lines, b_excl, shared)

    print(f"\nB-EXCL concentration:")
    print(f"  Total usage: {test3_results['b_excl']['total_usage']:,}")
    print(f"  Unique types: {test3_results['b_excl']['unique_types']:,}")
    print(f"  Top-5 coverage: {test3_results['b_excl']['top5_coverage']:.1%}")
    print(f"  Top-10 coverage: {test3_results['b_excl']['top10_coverage']:.1%}")
    print(f"  Top-20 coverage: {test3_results['b_excl']['top20_coverage']:.1%}")

    print(f"\nSHARED concentration (baseline):")
    print(f"  Total usage: {test3_results['shared']['total_usage']:,}")
    print(f"  Top-10 coverage: {test3_results['shared']['top10_coverage']:.1%}")

    print(f"\nTop 15 B-EXCL MIDDLEs:")
    for middle, count in test3_results['b_excl']['top15_examples']:
        print(f"  {middle}: {count}")

    # Evaluation
    print()
    print("=" * 70)
    print("EVALUATION")
    print("=" * 70)

    tests_passed = 0

    # TEST 1: Any enrichment > 1.5x with p < 0.05
    test1_pass = any(
        test1_results[adj]['enrichment'] > 1.5 and test1_results[adj]['p_value'] < 0.05
        for adj in ['link', 'kernel', 'boundary']
    )
    if test1_pass:
        tests_passed += 1
        print("\nTEST 1: PASS - Grammar adjacency enrichment > 1.5x (p < 0.05)")
    else:
        print("\nTEST 1: FAIL - No significant adjacency enrichment")

    # TEST 2: Negative correlation with p < 0.05
    test2_pass = False
    if 'error' not in test2_results:
        rho = test2_results['entropy_vs_cei']['rho']
        p = test2_results['entropy_vs_cei']['p']
        test2_pass = rho < -0.2 and p < 0.05
    if test2_pass:
        tests_passed += 1
        print("TEST 2: PASS - Positional rigidity increases with CEI")
    else:
        print("TEST 2: FAIL - No significant rigidity-CEI relationship")

    # TEST 3: Top-10 > 60%
    test3_pass = test3_results['b_excl']['top10_coverage'] > 0.60
    if test3_pass:
        tests_passed += 1
        print("TEST 3: PASS - Top-10 B-EXCL cover > 60% of usage")
    else:
        print(f"TEST 3: FAIL - Top-10 cover only {test3_results['b_excl']['top10_coverage']:.1%}")

    # Verdict
    print()
    print("=" * 70)
    if tests_passed >= 2:
        print("VERDICT: HYPOTHESIS SUPPORTED")
        print("B-exclusive MIDDLEs are grammar-internal operators.")
    else:
        print("VERDICT: HYPOTHESIS NOT SUPPORTED")
        print("B-exclusive MIDDLEs are NOT clearly grammar-internal operators.")
    print(f"Tests passed: {tests_passed}/3")
    print("=" * 70)

    # Save results
    results = {
        'metadata': {
            'phase': 'B-EXCL-ROLE',
            'question': 'Are B-exclusive MIDDLEs grammar-internal operators?',
        },
        'classifications': {
            'shared_count': len(shared),
            'b_excl_count': len(b_excl),
        },
        'test1_adjacency': test1_results,
        'test2_rigidity': test2_results,
        'test3_concentration': test3_results,
        'evaluation': {
            'test1_pass': bool(test1_pass),
            'test2_pass': bool(test2_pass),
            'test3_pass': bool(test3_pass),
            'tests_passed': tests_passed,
            'verdict': 'SUPPORTED' if tests_passed >= 2 else 'NOT_SUPPORTED',
        },
    }

    print()
    print(f"Saving results to {OUTPUT_PATH}...")
    with open(OUTPUT_PATH, 'w') as f:
        json.dump(results, f, indent=2)

    print("\nDone.")
    return results


if __name__ == '__main__':
    main()
