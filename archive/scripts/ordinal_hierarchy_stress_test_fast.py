"""
Phase HOT: Hierarchical Ordinal Testing (FAST VERSION)
Stress test for ordinal regime encoding in human-track tokens.
"""

import pandas as pd
import numpy as np
from collections import defaultdict, Counter
from typing import Dict, List, Set
import sys

# Force UTF-8 output
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# ============================================================================
# FIXED DATA
# ============================================================================

CATEGORIZED_TOKENS = {
    'daiin', 'aiin', 'chedy', 'chey', 'ol', 'ar', 'or', 'al', 'shedy',
    'qokaiin', 'qokedy', 'qokeedy', 'qokeey', 'chol', 'chor', 'shor',
    'shol', 'dar', 'dal', 'kaiin', 'taiin', 'saiin', 'raiin',
    'okaiin', 'okedy', 'okeedy', 'okeey', 'dain', 'chain', 'shain',
    'kain', 'rain', 'lain', 'sain', 'ckhey', 'ckhy', 'shy', 'dy',
    'qo', 'ok', 'ot', 'od', 'op', 'ol', 'or', 'ar', 'al', 'am',
    's', 'r', 'l', 'd', 'y', 'o', 'e', 'a', 'n', 'm',
    'sh', 'ch', 'ck', 'ct', 'cp', 'cf', 'ain', 'aiin', 'aiiin',
    'cho', 'che', 'chy', 'sho', 'she', 'ko', 'ke', 'ky', 'to', 'te',
}

LINK_PATTERNS = {'qo', 'ok', 'ol', 'or', 'ar', 'al', 'daiin', 'saiin', 'raiin'}
KERNEL_CHARS = set('khe')

def get_section(folio: str) -> str:
    """Quick section lookup."""
    if not folio:
        return 'U'
    f = folio.lower()
    if any(f.startswith(x) for x in ['f1', 'f2r', 'f2v', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9']):
        if int(''.join(c for c in f if c.isdigit())[:2]) <= 25:
            return 'H'
    if any(f.startswith(x) for x in ['f103', 'f104', 'f105', 'f106', 'f107', 'f108', 'f109', 'f110', 'f111', 'f112', 'f113', 'f114', 'f115', 'f116']):
        return 'S'
    if any(f.startswith(x) for x in ['f75', 'f76', 'f77', 'f78', 'f79', 'f80', 'f81', 'f82', 'f83', 'f84']):
        return 'C'
    if any(f.startswith(x) for x in ['f67', 'f68', 'f69']):
        return 'A'
    if any(f.startswith(x) for x in ['f26', 'f27', 'f28', 'f29', 'f30', 'f31', 'f32', 'f33', 'f34', 'f35', 'f36', 'f37', 'f38', 'f39', 'f40', 'f41', 'f42', 'f43', 'f44', 'f45', 'f46', 'f47', 'f48', 'f49', 'f50', 'f51', 'f52', 'f53', 'f54', 'f55', 'f56']):
        return 'B'
    if any(f.startswith(x) for x in ['f85', 'f86', 'f87', 'f88', 'f89', 'f90']):
        return 'P'
    if any(f.startswith(x) for x in ['f70', 'f71', 'f72', 'f73', 'f74']):
        return 'Z'
    return 'U'

# ============================================================================
# PRECOMPUTE ALL METRICS
# ============================================================================

def precompute_metrics(df: pd.DataFrame) -> dict:
    """Precompute all metrics for all positions."""
    print("Precomputing metrics for all positions...")

    word_col = 'word' if 'word' in df.columns else 'token'
    tokens = df[word_col].fillna('').astype(str).tolist()
    folios = df['folio'].fillna('').astype(str).tolist()
    n = len(tokens)

    # Precompute per-token properties
    is_categorized = [t in CATEGORIZED_TOKENS for t in tokens]
    has_link = [any(p in t for p in LINK_PATTERNS) for t in tokens]
    kernel_count = [sum(1 for c in t if c in KERNEL_CHARS) for t in tokens]
    token_len = [max(len(t), 1) for t in tokens]
    has_k = ['k' in t for t in tokens]

    # Compute position in folio
    folio_starts = {}
    folio_lengths = {}
    current_folio = None
    start_idx = 0
    for i, f in enumerate(folios):
        if f != current_folio:
            if current_folio is not None:
                folio_lengths[current_folio] = i - folio_starts[current_folio]
            folio_starts[f] = i
            current_folio = f
    if current_folio:
        folio_lengths[current_folio] = n - folio_starts.get(current_folio, n-1)

    # Compute metrics with sliding window (window=5)
    print("  Computing neighborhood metrics...")
    constraint_density = []
    instruction_aggressiveness = []
    kernel_k_presence = []
    link_proximity = []
    position_in_folio = []

    window = 5
    for i in range(n):
        start = max(0, i - window)
        end = min(n, i + window + 1)

        # Constraint density
        total_kernel = sum(kernel_count[start:end])
        total_len = sum(token_len[start:end])
        constraint_density.append(total_kernel / max(total_len, 1))

        # Instruction aggressiveness
        cat_count = sum(is_categorized[start:end])
        link_count = sum(1 for j in range(start, end) if is_categorized[j] and has_link[j])
        instruction_aggressiveness.append((cat_count - link_count) / max(cat_count, 1))

        # Kernel-k presence
        k_count = sum(has_k[start:end])
        kernel_k_presence.append(k_count / (end - start))

        # Link proximity
        link_tokens = sum(has_link[start:end])
        link_proximity.append(link_tokens / (end - start))

        # Position in folio
        folio = folios[i]
        if folio in folio_starts and folio in folio_lengths and folio_lengths[folio] > 0:
            pos = (i - folio_starts[folio]) / folio_lengths[folio]
        else:
            pos = 0.5
        position_in_folio.append(pos)

    print("  Done precomputing.")

    return {
        'tokens': tokens,
        'folios': folios,
        'sections': [get_section(f) for f in folios],
        'is_categorized': is_categorized,
        'constraint_density': constraint_density,
        'instruction_aggressiveness': instruction_aggressiveness,
        'kernel_k_presence': kernel_k_presence,
        'link_proximity': link_proximity,
        'position_in_folio': position_in_folio,
    }

# ============================================================================
# CLASSIFY TOKENS
# ============================================================================

def classify_tokens(metrics: dict, min_freq: int = 10) -> dict:
    """Classify tokens into behavioral labels."""
    print("Classifying tokens...")

    tokens = metrics['tokens']
    positions = metrics['position_in_folio']
    constraint_density = metrics['constraint_density']
    is_categorized = metrics['is_categorized']

    # Get uncategorized token frequencies
    token_indices = defaultdict(list)
    for i, t in enumerate(tokens):
        if not is_categorized[i] and t:
            token_indices[t].append(i)

    # Filter by frequency
    frequent_tokens = {t: idxs for t, idxs in token_indices.items() if len(idxs) >= min_freq}
    print(f"  Found {len(frequent_tokens)} tokens with freq >= {min_freq}")

    token_labels = {}
    token_metrics = {}

    for token, indices in list(frequent_tokens.items())[:300]:  # Limit to 300
        # Sample up to 50 indices
        sample_indices = indices[:50]

        # Compute mean metrics
        mean_pos = np.mean([positions[i] for i in sample_indices])
        early_rate = sum(1 for i in sample_indices if positions[i] < 0.2) / len(sample_indices)
        late_rate = sum(1 for i in sample_indices if positions[i] > 0.8) / len(sample_indices)

        # Compute gradient (before vs after constraint density)
        before_densities = []
        after_densities = []
        for i in sample_indices:
            if i >= 5 and i < len(constraint_density) - 5:
                before_densities.append(constraint_density[i - 3])
                after_densities.append(constraint_density[i + 3])

        if before_densities:
            mean_before = np.mean(before_densities)
            mean_after = np.mean(after_densities)
            gradient = (mean_after - mean_before) / max(mean_before, 0.01)
        else:
            gradient = 0

        # Classify
        if early_rate > 0.35:
            label = 'ESTABLISHING'
        elif late_rate > 0.35:
            label = 'EXHAUSTING'
        elif gradient > 0.15:
            label = 'APPROACHING'
        elif gradient < -0.15:
            label = 'RELAXING'
        elif mean_pos < 0.35:
            label = 'ESTABLISHING'
        elif mean_pos > 0.65:
            label = 'EXHAUSTING'
        else:
            label = 'RUNNING'

        token_labels[token] = label
        token_metrics[token] = {
            'constraint_density': np.median([constraint_density[i] for i in sample_indices]),
            'instruction_aggressiveness': np.median([metrics['instruction_aggressiveness'][i] for i in sample_indices]),
            'kernel_k_presence': np.median([metrics['kernel_k_presence'][i] for i in sample_indices]),
            'link_proximity': np.median([metrics['link_proximity'][i] for i in sample_indices]),
            'position': mean_pos,
            'gradient': gradient,
        }

    print(f"  Classified {len(token_labels)} tokens")
    return token_labels, token_metrics

# ============================================================================
# TESTS
# ============================================================================

def test_global_monotonic_ordering(token_labels: dict, token_metrics: dict) -> dict:
    """TEST 1: Global monotonic ordering."""
    print("\n" + "="*70)
    print("TEST 1: GLOBAL MONOTONIC ORDERING")
    print("="*70)

    # Aggregate metrics by label
    label_agg = defaultdict(lambda: {'cd': [], 'agg': [], 'k': [], 'link': []})
    for token, label in token_labels.items():
        if token in token_metrics:
            m = token_metrics[token]
            label_agg[label]['cd'].append(m['constraint_density'])
            label_agg[label]['agg'].append(m['instruction_aggressiveness'])
            label_agg[label]['k'].append(m['kernel_k_presence'])
            label_agg[label]['link'].append(m['link_proximity'])

    print("\nMedian stress metrics per label:")
    print("-" * 70)

    results = {}
    for label in ['ESTABLISHING', 'RUNNING', 'HOLDING', 'APPROACHING', 'RELAXING', 'EXHAUSTING']:
        if label in label_agg and label_agg[label]['cd']:
            results[label] = {
                'cd': np.median(label_agg[label]['cd']),
                'agg': np.median(label_agg[label]['agg']),
                'k': np.median(label_agg[label]['k']),
                'link': np.median(label_agg[label]['link']),
            }
            print(f"{label:15} | CD={results[label]['cd']:.3f} | AGG={results[label]['agg']:.3f} | K={results[label]['k']:.3f} | LINK={results[label]['link']:.3f}")
        else:
            results[label] = {'cd': 0, 'agg': 0, 'k': 0, 'link': 0}

    # Test monotonicity
    order = ['ESTABLISHING', 'RUNNING', 'APPROACHING']  # Skip HOLDING if missing
    order = [l for l in order if l in results and results[l]['cd'] > 0]

    if len(order) >= 2:
        cd_values = [results[l]['cd'] for l in order]
        cd_monotonic = all(cd_values[i] <= cd_values[i+1] * 1.2 for i in range(len(cd_values)-1))  # Allow 20% slack
    else:
        cd_monotonic = False

    print(f"\nConstraint density approximately monotonic: {cd_monotonic}")

    return {'supports_hierarchy': cd_monotonic, 'results': results}

def test_substitution(token_labels: dict, metrics: dict) -> dict:
    """TEST 2: Antisymmetric substitution test."""
    print("\n" + "="*70)
    print("TEST 2: ANTISYMMETRIC SUBSTITUTION TEST")
    print("="*70)

    tokens = metrics['tokens']
    is_categorized = metrics['is_categorized']

    # Build context -> labels mapping (context = prev+next categorized token)
    context_labels = defaultdict(set)

    for i, t in enumerate(tokens):
        if t in token_labels:
            # Find prev categorized
            prev_cat = '_'
            for j in range(i-1, max(i-5, -1), -1):
                if is_categorized[j]:
                    prev_cat = tokens[j]
                    break
            # Find next categorized
            next_cat = '_'
            for j in range(i+1, min(i+5, len(tokens))):
                if is_categorized[j]:
                    next_cat = tokens[j]
                    break

            context = (prev_cat, next_cat)
            if context != ('_', '_'):
                context_labels[context].add(token_labels[t])

    # Count how many contexts have multiple labels
    multi_label_contexts = sum(1 for c, labels in context_labels.items() if len(labels) > 1)
    total_contexts = len(context_labels)

    substitution_rate = multi_label_contexts / max(total_contexts, 1)
    print(f"Contexts with multiple labels: {multi_label_contexts}/{total_contexts} ({substitution_rate:.1%})")
    print("  High substitution = labels are navigational (not hierarchical)")
    print("  Low substitution = labels are tier-distinct")

    supports_hierarchy = substitution_rate < 0.3

    return {'substitution_rate': substitution_rate, 'supports_hierarchy': supports_hierarchy}

def test_directionality(token_labels: dict, metrics: dict) -> dict:
    """TEST 3: Transition directionality test."""
    print("\n" + "="*70)
    print("TEST 3: TRANSITION DIRECTIONALITY TEST")
    print("="*70)

    tokens = metrics['tokens']

    # Find transitions between labeled tokens
    transitions = defaultdict(int)
    prev_label = None
    prev_idx = -10

    for i, t in enumerate(tokens):
        if t in token_labels:
            if prev_label is not None and i - prev_idx <= 3:
                transitions[(prev_label, token_labels[t])] += 1
            prev_label = token_labels[t]
            prev_idx = i

    # Count forward vs backward
    forward = [('ESTABLISHING', 'RUNNING'), ('RUNNING', 'APPROACHING'), ('ESTABLISHING', 'APPROACHING')]
    backward = [('RUNNING', 'ESTABLISHING'), ('APPROACHING', 'RUNNING'), ('APPROACHING', 'ESTABLISHING')]

    forward_count = sum(transitions.get(t, 0) for t in forward)
    backward_count = sum(transitions.get(t, 0) for t in backward)

    print(f"Forward transitions: {forward_count}")
    print(f"Backward transitions: {backward_count}")

    if forward_count + backward_count > 0:
        bias = forward_count / (forward_count + backward_count)
    else:
        bias = 0.5

    print(f"Directionality bias: {bias:.2f} (0.5=symmetric, >0.6=directional)")

    return {'bias': bias, 'supports_hierarchy': bias > 0.6}

def test_slope_steepness(token_labels: dict, token_metrics: dict) -> dict:
    """TEST 4: Local slope steepness test."""
    print("\n" + "="*70)
    print("TEST 4: LOCAL SLOPE STEEPNESS TEST")
    print("="*70)

    # Bin tokens by constraint density, check label purity
    bins = 5
    densities = [(t, token_metrics[t]['constraint_density']) for t in token_labels if t in token_metrics]
    if not densities:
        return {'supports_hierarchy': False}

    min_d = min(d for _, d in densities)
    max_d = max(d for _, d in densities)
    range_d = max_d - min_d + 0.001

    bin_labels = defaultdict(list)
    for token, d in densities:
        bin_idx = min(int((d - min_d) / range_d * bins), bins - 1)
        bin_labels[bin_idx].append(token_labels[token])

    # Compute purity per bin
    purities = []
    for b in range(bins):
        if bin_labels[b]:
            counts = Counter(bin_labels[b])
            total = sum(counts.values())
            purity = max(counts.values()) / total
            purities.append(purity)
            print(f"Bin {b}: {dict(counts)} -> purity {purity:.2f}")

    mean_purity = np.mean(purities) if purities else 0
    print(f"\nMean bin purity: {mean_purity:.2f} (>0.5 = step-like, <0.4 = smooth)")

    return {'mean_purity': mean_purity, 'supports_hierarchy': mean_purity > 0.5}

def test_section_invariance(token_labels: dict, token_metrics: dict, metrics: dict) -> dict:
    """TEST 5: Section invariance test."""
    print("\n" + "="*70)
    print("TEST 5: SECTION-INVARIANCE TEST")
    print("="*70)

    tokens = metrics['tokens']
    sections = metrics['sections']
    constraint_density = metrics['constraint_density']

    # Build token -> section -> densities
    token_section_densities = defaultdict(lambda: defaultdict(list))
    for i, t in enumerate(tokens):
        if t in token_labels:
            token_section_densities[t][sections[i]].append(constraint_density[i])

    # For each section, compute label rankings
    section_rankings = {}
    for section in ['H', 'S', 'B', 'C', 'P']:
        label_densities = defaultdict(list)
        for token, label in token_labels.items():
            if token in token_section_densities and section in token_section_densities[token]:
                densities = token_section_densities[token][section]
                if densities:
                    label_densities[label].extend(densities)

        if len(label_densities) >= 2:
            ranking = sorted(label_densities.keys(), key=lambda l: np.median(label_densities[l]))
            section_rankings[section] = ranking
            print(f"Section {section}: {' < '.join(ranking)}")

    # Check consistency
    if len(section_rankings) < 2:
        return {'supports_hierarchy': False, 'consistency': 0}

    reference = list(section_rankings.values())[0]
    matches = sum(1 for r in section_rankings.values() if r == reference)
    consistency = matches / len(section_rankings)

    print(f"\nRanking consistency: {consistency:.0%}")

    return {'consistency': consistency, 'supports_hierarchy': consistency > 0.6}

# ============================================================================
# MAIN
# ============================================================================

def main():
    print("="*70)
    print("PHASE HOT: HIERARCHICAL ORDINAL TESTING (FAST)")
    print("="*70)

    # Load data
    print("\nLoading data...")
    df = pd.read_csv('data/transcriptions/interlinear_full_words.txt', sep='\t')
    print(f"Loaded {len(df)} tokens")

    # Precompute metrics
    metrics = precompute_metrics(df)

    # Classify tokens
    token_labels, token_metrics = classify_tokens(metrics)

    # Label distribution
    label_counts = Counter(token_labels.values())
    print(f"\nLabel distribution: {dict(label_counts)}")

    # Run tests
    test1 = test_global_monotonic_ordering(token_labels, token_metrics)
    test2 = test_substitution(token_labels, metrics)
    test3 = test_directionality(token_labels, metrics)
    test4 = test_slope_steepness(token_labels, token_metrics)
    test5 = test_section_invariance(token_labels, token_metrics, metrics)

    # Summary
    print("\n" + "="*70)
    print("FINAL SUMMARY")
    print("="*70)

    tests = [
        ("1. Global Monotonic Ordering", test1['supports_hierarchy']),
        ("2. Antisymmetric Substitution", test2['supports_hierarchy']),
        ("3. Transition Directionality", test3['supports_hierarchy']),
        ("4. Local Slope Steepness", test4['supports_hierarchy']),
        ("5. Section Invariance", test5['supports_hierarchy']),
    ]

    print("\n| Test | Result | Supports Hierarchy? |")
    print("|------|--------|---------------------|")

    passes = 0
    for name, passed in tests:
        result = "PASS" if passed else "FAIL"
        supports = "YES" if passed else "NO"
        print(f"| {name:30} | {result:6} | {supports:19} |")
        if passed:
            passes += 1

    print(f"\nTests passed: {passes}/5")

    # Verdict
    print("\n" + "="*70)
    print("VERDICT")
    print("="*70)

    if passes >= 4:
        verdict = "SUPPORTED"
        conclusion = "Human-track encodes ordinal regimes (stress/intensity hierarchy)"
    elif passes <= 1:
        verdict = "FALSIFIED"
        conclusion = "Hierarchy incompatible with data; tokens are navigational only"
    else:
        verdict = "WEAK / LOCAL"
        conclusion = "Only section-local or weak ordering exists; not apparatus-global"

    print(f"\n  {verdict}")
    print(f"\n  {conclusion}")

    # Counter-evidence
    print("\n" + "-"*70)
    print("COUNTER-EVIDENCE:")
    if not test1['supports_hierarchy']:
        print("- Metrics do NOT increase monotonically across labels")
    if not test2['supports_hierarchy']:
        print(f"- High substitution rate ({test2['substitution_rate']:.0%}) - labels interchangeable")
    if not test3['supports_hierarchy']:
        print(f"- Transitions symmetric (bias={test3['bias']:.2f}) - no directional flow")
    if not test4['supports_hierarchy']:
        print(f"- Smooth overlap (purity={test4['mean_purity']:.2f}) - no step-like tiers")
    if not test5['supports_hierarchy']:
        print(f"- Rankings inconsistent across sections ({test5['consistency']:.0%})")

if __name__ == '__main__':
    main()
