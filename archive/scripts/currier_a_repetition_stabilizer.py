"""
F-A-008: Repetition as Relational Stabilizer Fit

Tests whether universal-reference entries (cross-domain vocabulary)
receive more internal reinforcement (repetition) than exclusive entries.

Core question: Does the registry reinforce what it selects?

Partitions entries by MIDDLE universality:
1. Universal-Anchored: >=1 MIDDLE appearing in >=6 prefix classes
2. Mixed: both universal and exclusive MIDDLEs
3. Exclusive-Only: all MIDDLEs are prefix-bound (single-domain)

Pre-declared outcomes:
- Universal entries have higher repetition → F2 (relational stabilization)
- No difference → F1 (selection only, not reinforcement)
- Exclusive entries have more → F1 (repetition as local redundancy)

Tier F2 if universal > exclusive with p < 0.05, F1 otherwise.
"""

import os
import json
from collections import defaultdict, Counter
import math
import random

# Known prefixes from CAS-MORPH phase
PREFIXES = ['ch', 'qo', 'sh', 'da', 'ok', 'ot', 'ct', 'ol']

# Extended suffixes for decomposition
SUFFIXES = ['aiin', 'ain', 'ar', 'al', 'or', 'ol', 'am', 'an', 'in',
            'y', 'dy', 'ey', 'edy', 'eedy', 'chy', 'shy',
            'r', 'l', 's', 'd', 'n', 'm']
SUFFIX_PATTERNS = sorted(SUFFIXES, key=len, reverse=True)


def load_currier_a_full():
    """Load Currier A tokens with full metadata."""
    filepath = r'C:\git\voynich\data\transcriptions\interlinear_full_words.txt'

    tokens = []

    with open(filepath, 'r', encoding='utf-8') as f:
        header = f.readline().strip().split('\t')

        for line in f:
            parts = line.strip().split('\t')
            if len(parts) > 11:
                currier = parts[6].strip('"').strip()
                if currier == 'A':
                    token = parts[0].strip('"').strip().lower()
                    folio = parts[2].strip('"').strip() if len(parts) > 2 else ''
                    section = parts[3].strip('"').strip() if len(parts) > 3 else ''
                    line_num = parts[11].strip('"').strip()

                    # Skip damaged tokens
                    if token and '*' not in token:
                        tokens.append({
                            'token': token,
                            'folio': folio,
                            'section': section,
                            'line_num': line_num
                        })

    return tokens


def decompose_token(token):
    """Decompose token into PREFIX + MIDDLE + SUFFIX."""
    prefix = None
    remainder = token

    for p in sorted(PREFIXES, key=len, reverse=True):
        if token.startswith(p):
            prefix = p
            remainder = token[len(p):]
            break

    if not prefix:
        return None, None, None

    suffix = None
    middle = remainder

    for s in SUFFIX_PATTERNS:
        if remainder.endswith(s) and len(remainder) > len(s):
            suffix = s
            middle = remainder[:-len(s)]
            break
        elif remainder == s:
            suffix = s
            middle = ''
            break

    if not suffix:
        if len(remainder) >= 2:
            suffix = remainder[-2:]
            middle = remainder[:-2]
        elif len(remainder) == 1:
            suffix = remainder
            middle = ''
        else:
            suffix = ''
            middle = ''

    return prefix, middle, suffix


def build_middle_universality_map():
    """Build map of MIDDLE → number of prefixes it works with."""
    data_path = r'C:\git\voynich\results\currier_a_modeling_data.json'

    with open(data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    p_middle_given_prefix = data['target_1_token_census']['p_middle_given_prefix']

    # For each MIDDLE, count prefixes
    middle_prefix_count = defaultdict(int)

    for prefix in PREFIXES:
        if prefix in p_middle_given_prefix:
            for middle, prob in p_middle_given_prefix[prefix].items():
                if prob > 0:
                    middle_prefix_count[middle] += 1

    return middle_prefix_count


def detect_repetition(tokens):
    """
    Detect repetition pattern in a sequence of tokens.
    Returns (block, repetition_count) or (None, 1) if no repetition.

    Uses simplified block-matching algorithm.
    """
    if len(tokens) < 2:
        return None, 1

    # Try different block sizes
    for block_size in range(1, len(tokens) // 2 + 1):
        block = tokens[:block_size]

        # Check if this block repeats
        repetitions = 0
        pos = 0

        while pos + block_size <= len(tokens):
            segment = tokens[pos:pos + block_size]

            # Allow 25% tolerance for near-matches
            matches = sum(1 for a, b in zip(block, segment) if a == b)
            if matches >= 0.75 * block_size:
                repetitions += 1
                pos += block_size
            else:
                break

        if repetitions >= 2:
            return block, repetitions

    return None, 1


def classify_entry_universality(middles, middle_prefix_count):
    """
    Classify entry by MIDDLE universality.

    Returns:
    - 'universal': >=1 MIDDLE in >=6 prefix classes
    - 'mixed': both universal (>=6) and exclusive (=1)
    - 'shared': all MIDDLEs in 2-5 prefix classes
    - 'exclusive': all MIDDLEs in 1 prefix class only
    """
    if not middles:
        return 'unknown'

    universality_scores = []
    for m in middles:
        score = middle_prefix_count.get(m, 1)
        universality_scores.append(score)

    has_universal = any(s >= 6 for s in universality_scores)
    has_exclusive = any(s == 1 for s in universality_scores)
    all_exclusive = all(s == 1 for s in universality_scores)
    all_shared = all(2 <= s <= 5 for s in universality_scores)

    if has_universal and has_exclusive:
        return 'mixed'
    elif has_universal:
        return 'universal'
    elif all_exclusive:
        return 'exclusive'
    elif all_shared:
        return 'shared'
    else:
        return 'mixed'  # Combination of shared and exclusive


def mann_whitney_u(x, y):
    """Compute Mann-Whitney U test statistic and approximate p-value."""
    nx, ny = len(x), len(y)

    if nx == 0 or ny == 0:
        return 0, 1.0

    # Rank all values
    combined = [(v, 'x', i) for i, v in enumerate(x)] + [(v, 'y', i) for i, v in enumerate(y)]
    combined.sort(key=lambda t: t[0])

    # Assign ranks (handle ties by averaging)
    ranks = {}
    i = 0
    while i < len(combined):
        j = i
        while j < len(combined) and combined[j][0] == combined[i][0]:
            j += 1
        avg_rank = (i + 1 + j) / 2
        for k in range(i, j):
            group, idx = combined[k][1], combined[k][2]
            if group == 'x':
                ranks[('x', idx)] = avg_rank
            else:
                ranks[('y', idx)] = avg_rank
        i = j

    # Sum of ranks for x
    r1 = sum(ranks[('x', i)] for i in range(nx))

    # U statistic
    u1 = r1 - nx * (nx + 1) / 2
    u2 = nx * ny - u1
    u = min(u1, u2)

    # Normal approximation for p-value
    mu = nx * ny / 2
    sigma = math.sqrt(nx * ny * (nx + ny + 1) / 12)

    if sigma == 0:
        return u, 1.0

    z = (u - mu) / sigma

    from math import erf
    p = 2 * (1 - 0.5 * (1 + erf(abs(z) / math.sqrt(2))))

    return u, p


def run_analysis():
    """Main analysis function."""
    print("=" * 70)
    print("F-A-008: REPETITION AS RELATIONAL STABILIZER FIT")
    print("=" * 70)
    print()

    # Step 1: Build MIDDLE universality map
    print("Step 1: Building MIDDLE universality map...")
    middle_prefix_count = build_middle_universality_map()

    universal_middles = sum(1 for c in middle_prefix_count.values() if c >= 6)
    exclusive_middles = sum(1 for c in middle_prefix_count.values() if c == 1)
    shared_middles = sum(1 for c in middle_prefix_count.values() if 2 <= c <= 5)

    print(f"  Total MIDDLEs: {len(middle_prefix_count)}")
    print(f"  Universal (>=6 prefixes): {universal_middles}")
    print(f"  Shared (2-5 prefixes): {shared_middles}")
    print(f"  Exclusive (1 prefix): {exclusive_middles}")

    # Step 2: Load and group tokens into entries
    print("\nStep 2: Loading and grouping Currier A tokens into entries...")
    tokens = load_currier_a_full()

    # Group by (folio, line_num) = entry
    entries = defaultdict(list)
    for t in tokens:
        key = (t['folio'], t['line_num'])
        entries[key].append(t)

    print(f"  Total tokens: {len(tokens)}")
    print(f"  Total entries: {len(entries)}")

    # Step 3: Compute entry-level metrics
    print("\nStep 3: Computing entry-level metrics...")

    entry_data = []

    for (folio, line_num), entry_tokens in entries.items():
        if len(entry_tokens) < 2:
            continue

        # Get section
        section = entry_tokens[0]['section']

        # Decompose tokens and collect MIDDLEs
        token_strs = [t['token'] for t in entry_tokens]
        middles = []

        for tok in token_strs:
            prefix, middle, suffix = decompose_token(tok)
            if prefix and middle:
                middles.append(middle)

        if not middles:
            continue

        # Classify entry universality
        universality_class = classify_entry_universality(middles, middle_prefix_count)

        # Compute mean universality score
        scores = [middle_prefix_count.get(m, 1) for m in middles]
        mean_universality = sum(scores) / len(scores)

        # Detect repetition
        block, rep_count = detect_repetition(token_strs)

        entry_data.append({
            'folio': folio,
            'line_num': line_num,
            'section': section,
            'token_count': len(entry_tokens),
            'middle_count': len(middles),
            'universality_class': universality_class,
            'mean_universality': mean_universality,
            'repetition_count': rep_count,
            'has_repetition': rep_count >= 2
        })

    print(f"  Entries with metrics: {len(entry_data)}")

    # Step 4: Partition by universality class
    print("\n" + "-" * 50)
    print("Step 4: Partitioning entries by universality...")

    bins = defaultdict(list)
    for e in entry_data:
        bins[e['universality_class']].append(e)

    for cls in ['universal', 'mixed', 'shared', 'exclusive', 'unknown']:
        if cls in bins:
            entries_in_bin = bins[cls]
            n = len(entries_in_bin)
            mean_rep = sum(e['repetition_count'] for e in entries_in_bin) / n if n else 0
            rep_rate = sum(1 for e in entries_in_bin if e['has_repetition']) / n if n else 0
            print(f"\n{cls.upper()} (n={n}):")
            print(f"  Mean repetition count: {mean_rep:.2f}")
            print(f"  Repetition rate: {100*rep_rate:.1f}%")

    # Step 5: Statistical comparison (Universal vs Exclusive)
    print("\n" + "-" * 50)
    print("Step 5: Statistical comparison (Universal vs Exclusive)...")

    universal_reps = [e['repetition_count'] for e in bins['universal']]
    exclusive_reps = [e['repetition_count'] for e in bins['exclusive']]
    mixed_reps = [e['repetition_count'] for e in bins['mixed']]
    shared_reps = [e['repetition_count'] for e in bins['shared']]

    # Main comparison: Universal vs Exclusive
    if universal_reps and exclusive_reps:
        u, p = mann_whitney_u(universal_reps, exclusive_reps)
        univ_mean = sum(universal_reps) / len(universal_reps)
        excl_mean = sum(exclusive_reps) / len(exclusive_reps)

        print(f"\nUniversal vs Exclusive:")
        print(f"  Universal mean: {univ_mean:.2f} (n={len(universal_reps)})")
        print(f"  Exclusive mean: {excl_mean:.2f} (n={len(exclusive_reps)})")
        print(f"  Difference: {univ_mean - excl_mean:+.2f}")
        print(f"  Mann-Whitney U: {u:.0f}, p={p:.4f}")
        print(f"  Direction: {'UNIVERSAL > EXCLUSIVE' if univ_mean > excl_mean else 'EXCLUSIVE > UNIVERSAL'}")
    else:
        p = 1.0
        univ_mean = 0
        excl_mean = 0
        print("\n  Insufficient data for Universal vs Exclusive comparison")

    # Secondary: Universal+Mixed vs Exclusive
    universal_plus = universal_reps + mixed_reps
    if universal_plus and exclusive_reps:
        u2, p2 = mann_whitney_u(universal_plus, exclusive_reps)
        up_mean = sum(universal_plus) / len(universal_plus)
        print(f"\n(Universal + Mixed) vs Exclusive:")
        print(f"  Universal+Mixed mean: {up_mean:.2f} (n={len(universal_plus)})")
        print(f"  Exclusive mean: {excl_mean:.2f} (n={len(exclusive_reps)})")
        print(f"  Difference: {up_mean - excl_mean:+.2f}")
        print(f"  Mann-Whitney p={p2:.4f}")

    # Step 6: Section-stratified analysis
    print("\n" + "-" * 50)
    print("Step 6: Section-stratified analysis...")

    section_results = {}
    significant_sections = 0

    for section in ['H', 'P', 'T']:
        sec_universal = [e['repetition_count'] for e in bins['universal'] if e['section'] == section]
        sec_exclusive = [e['repetition_count'] for e in bins['exclusive'] if e['section'] == section]

        if len(sec_universal) >= 5 and len(sec_exclusive) >= 5:
            u_sec, p_sec = mann_whitney_u(sec_universal, sec_exclusive)
            univ_sec_mean = sum(sec_universal) / len(sec_universal)
            excl_sec_mean = sum(sec_exclusive) / len(sec_exclusive)

            section_results[section] = {
                'n_universal': len(sec_universal),
                'n_exclusive': len(sec_exclusive),
                'mean_universal': univ_sec_mean,
                'mean_exclusive': excl_sec_mean,
                'diff': univ_sec_mean - excl_sec_mean,
                'p': p_sec
            }

            if p_sec < 0.05 and univ_sec_mean > excl_sec_mean:
                significant_sections += 1

            print(f"\n{section} section:")
            print(f"  Universal: {univ_sec_mean:.2f} (n={len(sec_universal)})")
            print(f"  Exclusive: {excl_sec_mean:.2f} (n={len(sec_exclusive)})")
            print(f"  Difference: {univ_sec_mean - excl_sec_mean:+.2f}, p={p_sec:.4f}")
        else:
            print(f"\n{section} section: insufficient data")

    # Step 7: Correlation analysis
    print("\n" + "-" * 50)
    print("Step 7: Correlation (universality score vs repetition)...")

    all_universality = [e['mean_universality'] for e in entry_data]
    all_repetition = [e['repetition_count'] for e in entry_data]

    # Spearman correlation
    def spearman(x, y):
        n = len(x)
        if n < 3:
            return 0, 1.0

        def rank(arr):
            sorted_idx = sorted(range(len(arr)), key=lambda i: arr[i])
            ranks = [0] * len(arr)
            for i, idx in enumerate(sorted_idx):
                ranks[idx] = i + 1
            return ranks

        rx = rank(x)
        ry = rank(y)

        mean_rx = sum(rx) / n
        mean_ry = sum(ry) / n

        cov = sum((rx[i] - mean_rx) * (ry[i] - mean_ry) for i in range(n))
        std_rx = math.sqrt(sum((rx[i] - mean_rx)**2 for i in range(n)))
        std_ry = math.sqrt(sum((ry[i] - mean_ry)**2 for i in range(n)))

        if std_rx == 0 or std_ry == 0:
            return 0, 1.0

        rho = cov / (std_rx * std_ry)

        if abs(rho) >= 1.0:
            return rho, 0.0

        t_stat = rho * math.sqrt((n - 2) / (1 - rho**2))
        from math import erf
        p_val = 2 * (1 - 0.5 * (1 + erf(abs(t_stat) / math.sqrt(2))))

        return rho, p_val

    rho, p_corr = spearman(all_universality, all_repetition)
    print(f"\nSpearman correlation (universality vs repetition):")
    print(f"  rho = {rho:.4f}, p = {p_corr:.4f}")
    print(f"  {'SIGNIFICANT' if p_corr < 0.05 else 'NOT SIGNIFICANT'}")

    # Step 8: Determine fit tier
    print("\n" + "=" * 70)
    print("RESULT SUMMARY")
    print("=" * 70)

    # Primary criterion: Universal > Exclusive with p < 0.05
    if universal_reps and exclusive_reps:
        primary_effect = univ_mean > excl_mean and p < 0.05
        opposite_effect = excl_mean > univ_mean and p < 0.05
    else:
        primary_effect = False
        opposite_effect = False

    print(f"\nPre-declared outcome conditions:")
    print(f"  1. Universal > Exclusive (p < 0.05): {'YES' if primary_effect else 'NO'}")
    print(f"  2. Exclusive > Universal (p < 0.05): {'YES' if opposite_effect else 'NO'}")
    print(f"  3. Section robustness: {significant_sections} sections show effect")

    if primary_effect:
        fit_tier = "F2"
        result = "SUCCESS"
        interpretation = "Relational stabilization: Registry reinforces cross-domain anchors through repetition."
    elif opposite_effect:
        fit_tier = "F1"
        result = "OPPOSITE"
        interpretation = "Local redundancy: Repetition compensates for lack of cross-domain stability."
    else:
        fit_tier = "F1"
        result = "NULL"
        interpretation = "No effect: Relationality enforced through selection only, not repetition."

    print(f"\n{'='*50}")
    print(f"FIT TIER: {fit_tier}")
    print(f"RESULT: {result}")
    print(f"{'='*50}")
    print(f"\nInterpretation: {interpretation}")

    # Compile results
    results = {
        'fit_id': 'F-A-008',
        'fit_name': 'Repetition as Relational Stabilizer',
        'fit_tier': fit_tier,
        'result': result,
        'date': '2026-01-10',
        'entry_summary': {
            'total_entries': len(entry_data),
            'universal': len(bins['universal']),
            'mixed': len(bins['mixed']),
            'shared': len(bins['shared']),
            'exclusive': len(bins['exclusive'])
        },
        'repetition_by_class': {
            'universal': {
                'n': len(universal_reps),
                'mean': sum(universal_reps) / len(universal_reps) if universal_reps else 0,
                'rep_rate': sum(1 for e in bins['universal'] if e['has_repetition']) / len(bins['universal']) if bins['universal'] else 0
            },
            'exclusive': {
                'n': len(exclusive_reps),
                'mean': sum(exclusive_reps) / len(exclusive_reps) if exclusive_reps else 0,
                'rep_rate': sum(1 for e in bins['exclusive'] if e['has_repetition']) / len(bins['exclusive']) if bins['exclusive'] else 0
            }
        },
        'primary_test': {
            'universal_mean': float(univ_mean) if universal_reps else None,
            'exclusive_mean': float(excl_mean) if exclusive_reps else None,
            'difference': float(univ_mean - excl_mean) if universal_reps and exclusive_reps else None,
            'p_value': float(p)
        },
        'correlation': {
            'rho': float(rho),
            'p': float(p_corr)
        },
        'section_results': {
            k: {kk: float(vv) if isinstance(vv, float) else vv for kk, vv in v.items()}
            for k, v in section_results.items()
        },
        'criteria_check': {
            'primary_effect': primary_effect,
            'opposite_effect': opposite_effect,
            'significant_sections': significant_sections
        },
        'interpretation': interpretation,
        'supports_constraints': ['C287-C290', 'C252'] if primary_effect else [],
        'introduces_new_constraints': False
    }

    # Save results
    output_path = r'C:\git\voynich\results\currier_a_repetition_stabilizer.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to: {output_path}")

    return results


if __name__ == '__main__':
    run_analysis()
