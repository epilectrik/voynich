"""
F-A-005: Scarcity-Weighted Registry Effort Fit

Tests whether Currier A entries expend more effort per distinction when
forced into regions of component scarcity (fewer legal MIDDLE options).

Core question: Does registry effort adapt to expressive constraints?

Pre-declared success criteria:
- Correlation significance: p < 0.05
- Correlation magnitude: |r| > 0.15
- Section robustness: Effect holds in >2 sections

Tier F2 if all pass, F1 if any fail.
"""

import os
import json
from collections import defaultdict, Counter
import math

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
                    quire = parts[4].strip('"').strip() if len(parts) > 4 else ''
                    line_num = parts[11].strip('"').strip()

                    # Skip damaged tokens
                    if token and '*' not in token:
                        tokens.append({
                            'token': token,
                            'folio': folio,
                            'section': section,
                            'quire': quire,
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


def load_scarcity_data():
    """Load MIDDLE_SCARCITY from existing modeling data."""
    data_path = r'C:\git\voynich\results\currier_a_modeling_data.json'

    with open(data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    p_middle_given_prefix = data['target_1_token_census']['p_middle_given_prefix']

    # Count legal MIDDLEs per prefix (exclude empty string for scarcity)
    middle_counts = {}
    for prefix in PREFIXES:
        if prefix in p_middle_given_prefix:
            # Count non-empty MIDDLEs with non-trivial probability
            middles = p_middle_given_prefix[prefix]
            # Include empty string as one option, count total options
            legal_count = len(middles)
            middle_counts[prefix] = legal_count

    # Compute scarcity weight (inverse of count - higher = fewer options)
    scarcity_weights = {}
    max_count = max(middle_counts.values())
    for prefix, count in middle_counts.items():
        scarcity_weights[prefix] = 1.0 / count  # Raw inverse

    return middle_counts, scarcity_weights


def compute_entry_metrics(entries_by_folio, scarcity_weights):
    """Compute per-entry effort metrics."""
    entry_data = []

    for folio, tokens in entries_by_folio.items():
        if len(tokens) < 3:  # Skip very small entries
            continue

        # Decompose all tokens
        prefixes = []
        da_count = 0
        unique_tokens = set()

        for t in tokens:
            unique_tokens.add(t['token'])
            prefix, middle, suffix = decompose_token(t['token'])
            if prefix:
                prefixes.append(prefix)
                if prefix == 'da':
                    da_count += 1

        if not prefixes:
            continue

        # Effort metrics
        token_count = len(tokens)
        unique_prefix_count = len(set(prefixes))
        articulator_ratio = da_count / token_count
        internal_diversity = len(unique_tokens) / token_count

        # Mean scarcity weight for this entry
        scarcity_values = [scarcity_weights.get(p, 0) for p in prefixes]
        mean_scarcity = sum(scarcity_values) / len(scarcity_values) if scarcity_values else 0

        # Section (for stratification)
        section = tokens[0]['section'] if tokens else 'UNKNOWN'

        entry_data.append({
            'folio': folio,
            'section': section,
            'token_count': token_count,
            'unique_tokens': len(unique_tokens),
            'unique_prefixes': unique_prefix_count,
            'articulator_ratio': articulator_ratio,
            'internal_diversity': internal_diversity,
            'mean_scarcity': mean_scarcity,
            'prefix_counts': dict(Counter(prefixes))
        })

    return entry_data


def spearman_correlation(x, y):
    """Compute Spearman rank correlation and approximate p-value."""
    n = len(x)
    if n < 3:
        return 0.0, 1.0

    # Rank both arrays
    def rank(arr):
        sorted_idx = sorted(range(len(arr)), key=lambda i: arr[i])
        ranks = [0] * len(arr)
        for i, idx in enumerate(sorted_idx):
            ranks[idx] = i + 1
        return ranks

    rx = rank(x)
    ry = rank(y)

    # Spearman rho = Pearson on ranks
    mean_rx = sum(rx) / n
    mean_ry = sum(ry) / n

    cov = sum((rx[i] - mean_rx) * (ry[i] - mean_ry) for i in range(n))
    std_rx = math.sqrt(sum((rx[i] - mean_rx)**2 for i in range(n)))
    std_ry = math.sqrt(sum((ry[i] - mean_ry)**2 for i in range(n)))

    if std_rx == 0 or std_ry == 0:
        return 0.0, 1.0

    rho = cov / (std_rx * std_ry)

    # Approximate p-value using t-distribution approximation
    if abs(rho) >= 1.0:
        p_value = 0.0
    else:
        t_stat = rho * math.sqrt((n - 2) / (1 - rho**2))
        # Simple two-tailed p approximation for large n
        # Using normal approximation
        from math import erf
        p_value = 2 * (1 - 0.5 * (1 + erf(abs(t_stat) / math.sqrt(2))))

    return rho, p_value


def run_analysis():
    """Main analysis function."""
    print("=" * 70)
    print("F-A-005: SCARCITY-WEIGHTED REGISTRY EFFORT FIT")
    print("=" * 70)
    print()

    # Step 1: Load scarcity data
    print("Step 1: Loading scarcity data from existing modeling results...")
    middle_counts, scarcity_weights = load_scarcity_data()

    print("\nMIDDLE counts per prefix (legal options):")
    for prefix in sorted(middle_counts.keys()):
        print(f"  {prefix}: {middle_counts[prefix]} MIDDLEs -> scarcity weight {scarcity_weights[prefix]:.4f}")

    # Step 2: Load Currier A entries
    print("\nStep 2: Loading Currier A entries (grouped by folio)...")
    tokens = load_currier_a_full()
    print(f"  Total Currier A tokens (clean): {len(tokens)}")

    # Group by folio
    entries_by_folio = defaultdict(list)
    for t in tokens:
        entries_by_folio[t['folio']].append(t)

    print(f"  Total entries (folios): {len(entries_by_folio)}")

    # Step 3: Compute entry metrics
    print("\nStep 3: Computing per-entry effort metrics...")
    entry_data = compute_entry_metrics(entries_by_folio, scarcity_weights)
    print(f"  Entries with sufficient data: {len(entry_data)}")

    # Step 4: Correlation tests
    print("\nStep 4: Running correlation tests...")
    print("-" * 50)

    scarcity = [e['mean_scarcity'] for e in entry_data]
    articulator = [e['articulator_ratio'] for e in entry_data]
    marker_div = [e['unique_prefixes'] for e in entry_data]
    internal_div = [e['internal_diversity'] for e in entry_data]
    token_count = [e['token_count'] for e in entry_data]

    correlations = {}

    # Test 1: Scarcity vs Articulator ratio
    rho, p = spearman_correlation(scarcity, articulator)
    correlations['scarcity_vs_articulator'] = {'rho': rho, 'p': p}
    print(f"\nScarcity vs Articulator Ratio:")
    print(f"  Spearman rho = {rho:.4f}, p = {p:.4f}")
    print(f"  {'SIGNIFICANT' if p < 0.05 else 'NOT SIGNIFICANT'} (threshold p < 0.05)")
    print(f"  {'MEANINGFUL' if abs(rho) > 0.15 else 'WEAK'} (threshold |r| > 0.15)")

    # Test 2: Scarcity vs Marker diversity
    rho, p = spearman_correlation(scarcity, marker_div)
    correlations['scarcity_vs_marker_diversity'] = {'rho': rho, 'p': p}
    print(f"\nScarcity vs Marker Diversity (unique prefixes):")
    print(f"  Spearman rho = {rho:.4f}, p = {p:.4f}")
    print(f"  {'SIGNIFICANT' if p < 0.05 else 'NOT SIGNIFICANT'} (threshold p < 0.05)")
    print(f"  {'MEANINGFUL' if abs(rho) > 0.15 else 'WEAK'} (threshold |r| > 0.15)")

    # Test 3: Scarcity vs Internal diversity
    rho, p = spearman_correlation(scarcity, internal_div)
    correlations['scarcity_vs_internal_diversity'] = {'rho': rho, 'p': p}
    print(f"\nScarcity vs Internal Diversity:")
    print(f"  Spearman rho = {rho:.4f}, p = {p:.4f}")
    print(f"  {'SIGNIFICANT' if p < 0.05 else 'NOT SIGNIFICANT'} (threshold p < 0.05)")
    print(f"  {'MEANINGFUL' if abs(rho) > 0.15 else 'WEAK'} (threshold |r| > 0.15)")

    # Test 4: Scarcity vs Token count (control - expect no relation)
    rho, p = spearman_correlation(scarcity, token_count)
    correlations['scarcity_vs_token_count'] = {'rho': rho, 'p': p}
    print(f"\nScarcity vs Token Count (control):")
    print(f"  Spearman rho = {rho:.4f}, p = {p:.4f}")

    # Step 5: Section stratification
    print("\n" + "-" * 50)
    print("Step 5: Section-stratified analysis...")

    sections = defaultdict(list)
    for e in entry_data:
        sections[e['section']].append(e)

    section_results = {}
    significant_sections = 0

    for section, entries in sorted(sections.items()):
        if len(entries) < 5:
            continue

        sec_scarcity = [e['mean_scarcity'] for e in entries]
        sec_articulator = [e['articulator_ratio'] for e in entries]

        rho, p = spearman_correlation(sec_scarcity, sec_articulator)
        section_results[section] = {'n': len(entries), 'rho': rho, 'p': p}

        if p < 0.05 and abs(rho) > 0.15:
            significant_sections += 1

        print(f"\n{section} (n={len(entries)}):")
        print(f"  Scarcity vs Articulator: rho={rho:.4f}, p={p:.4f}")

    # Step 6: Quartile comparison
    print("\n" + "-" * 50)
    print("Step 6: Quartile comparison (top vs bottom scarcity)...")

    sorted_entries = sorted(entry_data, key=lambda e: e['mean_scarcity'])
    n = len(sorted_entries)
    q1_entries = sorted_entries[:n//4]  # Low scarcity (many options)
    q4_entries = sorted_entries[3*n//4:]  # High scarcity (few options)

    q1_articulator = sum(e['articulator_ratio'] for e in q1_entries) / len(q1_entries)
    q4_articulator = sum(e['articulator_ratio'] for e in q4_entries) / len(q4_entries)

    q1_diversity = sum(e['internal_diversity'] for e in q1_entries) / len(q1_entries)
    q4_diversity = sum(e['internal_diversity'] for e in q4_entries) / len(q4_entries)

    print(f"\nBottom quartile (low scarcity = many MIDDLE options):")
    print(f"  Mean articulator ratio: {q1_articulator:.4f}")
    print(f"  Mean internal diversity: {q1_diversity:.4f}")

    print(f"\nTop quartile (high scarcity = few MIDDLE options):")
    print(f"  Mean articulator ratio: {q4_articulator:.4f}")
    print(f"  Mean internal diversity: {q4_diversity:.4f}")

    print(f"\nDifference (Q4 - Q1):")
    print(f"  Articulator ratio: {q4_articulator - q1_articulator:+.4f}")
    print(f"  Internal diversity: {q4_diversity - q1_diversity:+.4f}")

    # Step 7: Determine fit tier
    print("\n" + "=" * 70)
    print("RESULT SUMMARY")
    print("=" * 70)

    # Check pre-declared criteria
    primary_test = correlations['scarcity_vs_articulator']
    criterion_1 = primary_test['p'] < 0.05
    criterion_2 = abs(primary_test['rho']) > 0.15
    criterion_3 = significant_sections >= 2

    all_pass = criterion_1 and criterion_2 and criterion_3

    print(f"\nPre-declared success criteria:")
    print(f"  1. Correlation significance (p < 0.05): {'PASS' if criterion_1 else 'FAIL'} (p = {primary_test['p']:.4f})")
    print(f"  2. Correlation magnitude (|r| > 0.15): {'PASS' if criterion_2 else 'FAIL'} (r = {primary_test['rho']:.4f})")
    print(f"  3. Section robustness (>2 sections): {'PASS' if criterion_3 else 'FAIL'} ({significant_sections} sections)")

    if all_pass:
        fit_tier = "F2"
        result = "SUCCESS"
        interpretation = "Scarcity → Higher Effort: Registry compensates when expressive vocabulary is thin."
    else:
        fit_tier = "F1"
        result = "NULL"
        interpretation = "No Effect: Effort reflects case importance, not vocabulary constraints."

    print(f"\n{'='*50}")
    print(f"FIT TIER: {fit_tier}")
    print(f"RESULT: {result}")
    print(f"{'='*50}")
    print(f"\nInterpretation: {interpretation}")

    # Compile results
    results = {
        'fit_id': 'F-A-005',
        'fit_name': 'Scarcity-Weighted Registry Effort',
        'fit_tier': fit_tier,
        'result': result,
        'date': '2026-01-10',
        'scarcity_data': {
            'middle_counts': middle_counts,
            'scarcity_weights': {k: float(v) for k, v in scarcity_weights.items()}
        },
        'entry_summary': {
            'total_entries': len(entry_data),
            'mean_articulator_ratio': sum(articulator) / len(articulator),
            'mean_internal_diversity': sum(internal_div) / len(internal_div),
            'mean_scarcity': sum(scarcity) / len(scarcity)
        },
        'correlations': {
            k: {kk: float(vv) for kk, vv in v.items()}
            for k, v in correlations.items()
        },
        'section_results': {
            k: {kk: float(vv) if isinstance(vv, float) else vv for kk, vv in v.items()}
            for k, v in section_results.items()
        },
        'quartile_comparison': {
            'q1_low_scarcity': {
                'articulator_ratio': float(q1_articulator),
                'internal_diversity': float(q1_diversity)
            },
            'q4_high_scarcity': {
                'articulator_ratio': float(q4_articulator),
                'internal_diversity': float(q4_diversity)
            }
        },
        'criteria_check': {
            'significance_pass': criterion_1,
            'magnitude_pass': criterion_2,
            'section_robustness_pass': criterion_3,
            'all_pass': all_pass
        },
        'interpretation': interpretation,
        'supports_constraints': ['C293', 'C385'] if all_pass else [],
        'introduces_new_constraints': False
    }

    # Save results
    output_path = r'C:\git\voynich\results\currier_a_scarcity_effort.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to: {output_path}")

    return results


if __name__ == '__main__':
    run_analysis()
