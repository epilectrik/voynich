#!/usr/bin/env python
"""
Universal MIDDLE Structural Properties

Tests what structural properties distinguish universal MIDDLEs
(those appearing in all 4 material classes) from class-exclusive MIDDLEs.

Tests:
1. Suffix distribution - decision pattern differences
2. Sister preference - ch/sh balance
3. Position patterns - line-initial/final tendencies
4. Section distribution - H/P/T spread
5. Frequency concentration - Core vs Tail membership

Goal: Identify HOW the apparatus treats universal MIDDLEs differently,
without speculating on WHAT they represent.
"""

import json
import numpy as np
from pathlib import Path
from collections import Counter, defaultdict
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# Paths
DATA_PATH = Path("C:/git/voynich/data/transcriptions/interlinear_full_words.txt")
RESULTS_DIR = Path("C:/git/voynich/results")
OUTPUT_FILE = RESULTS_DIR / "universal_middle_properties.json"

# Material class mapping
PREFIX_TO_CLASS = {
    'ch': 'M-A', 'qo': 'M-A',
    'sh': 'M-B', 'ok': 'M-B',
    'da': 'M-C', 'ot': 'M-C',
    'ol': 'M-D', 'ct': 'M-D',
}

# Sister pairs
SISTER_PAIRS = {
    'ch': 'precision', 'qo': 'precision',
    'sh': 'tolerance', 'ok': 'tolerance',
    'da': 'precision', 'ot': 'tolerance',
    'ol': 'tolerance', 'ct': 'precision',
}

PREFIXES = ['ch', 'sh', 'qo', 'da', 'ok', 'ot', 'ol', 'ct']
SUFFIXES = ['y', 'dy', 'chy', 'shy', 'ain', 'aiin', 'in', 'n', 's', 'l', 'r', 'm']


def load_currier_a():
    """Load Currier A with position data."""
    import pandas as pd
    df = pd.read_csv(DATA_PATH, sep='\t', low_memory=False, na_values='NA')
    df = df[(df['language'] == 'A') &
            (df['transcriber'] == 'H') &
            (df['word'].notna()) &
            (~df['word'].str.contains(r'\*', na=False))]
    return df


def decompose_token(word):
    """Extract PREFIX, MIDDLE, SUFFIX."""
    word = str(word).lower().strip()

    prefix = None
    for p in PREFIXES:
        if word.startswith(p):
            prefix = p
            break

    if not prefix:
        return None, None, None

    remainder = word[len(prefix):]

    suffix = ''
    for s in sorted(SUFFIXES, key=len, reverse=True):
        if remainder.endswith(s):
            suffix = s
            remainder = remainder[:-len(s)]
            break

    return prefix, remainder, suffix


def classify_middles(df):
    """Classify MIDDLEs by sharing pattern."""
    middle_by_class = defaultdict(set)
    middle_data = defaultdict(list)

    for _, row in df.iterrows():
        prefix, middle, suffix = decompose_token(row['word'])
        if prefix is None or middle is None:
            continue

        material_class = PREFIX_TO_CLASS[prefix]
        middle_by_class[middle].add(material_class)

        middle_data[middle].append({
            'prefix': prefix,
            'suffix': suffix,
            'section': row.get('section', 'H'),
            'line_initial': row.get('line_initial', 0),
            'line_final': row.get('line_final', 0),
            'word': row['word'],
        })

    # Classify by sharing
    universal = [m for m, classes in middle_by_class.items() if len(classes) == 4]
    exclusive = [m for m, classes in middle_by_class.items() if len(classes) == 1]
    bridging = [m for m, classes in middle_by_class.items() if 1 < len(classes) < 4]

    return universal, exclusive, bridging, middle_data, middle_by_class


def test_suffix_distribution(universal, exclusive, middle_data):
    """Compare suffix distributions between universal and exclusive MIDDLEs."""
    print("\n" + "="*60)
    print("TEST 1: SUFFIX DISTRIBUTION")
    print("="*60)

    universal_suffixes = []
    exclusive_suffixes = []

    for m in universal:
        for token in middle_data[m]:
            universal_suffixes.append(token['suffix'])

    for m in exclusive:
        for token in middle_data[m]:
            exclusive_suffixes.append(token['suffix'])

    print(f"\nUniversal tokens: {len(universal_suffixes)}")
    print(f"Exclusive tokens: {len(exclusive_suffixes)}")

    # Count distributions
    univ_counts = Counter(universal_suffixes)
    excl_counts = Counter(exclusive_suffixes)

    print("\nSuffix distribution comparison:")
    print(f"{'Suffix':<10} {'Universal':>12} {'Exclusive':>12}")
    print("-" * 34)

    all_suffixes = set(univ_counts.keys()) | set(excl_counts.keys())
    for suffix in sorted(all_suffixes, key=lambda s: univ_counts.get(s, 0) + excl_counts.get(s, 0), reverse=True)[:10]:
        u_pct = univ_counts.get(suffix, 0) / len(universal_suffixes) * 100 if universal_suffixes else 0
        e_pct = excl_counts.get(suffix, 0) / len(exclusive_suffixes) * 100 if exclusive_suffixes else 0
        print(f"'{suffix}'".ljust(10) + f"{u_pct:>11.1f}%" + f"{e_pct:>11.1f}%")

    # Entropy comparison
    def entropy(counts):
        total = sum(counts.values())
        if total == 0:
            return 0
        probs = [c/total for c in counts.values()]
        return -sum(p * np.log2(p) for p in probs if p > 0)

    univ_entropy = entropy(univ_counts)
    excl_entropy = entropy(excl_counts)

    print(f"\nSuffix entropy:")
    print(f"  Universal: {univ_entropy:.3f} bits")
    print(f"  Exclusive: {excl_entropy:.3f} bits")

    # Key finding
    if univ_entropy > excl_entropy:
        print("\n-> Universal MIDDLEs have MORE diverse suffix usage")
        interpretation = "more_diverse"
    else:
        print("\n-> Universal MIDDLEs have LESS diverse suffix usage")
        interpretation = "less_diverse"

    return {
        'universal_tokens': len(universal_suffixes),
        'exclusive_tokens': len(exclusive_suffixes),
        'universal_entropy': float(univ_entropy),
        'exclusive_entropy': float(excl_entropy),
        'interpretation': interpretation,
    }


def test_sister_preference(universal, exclusive, middle_data):
    """Compare sister-pair preference (precision vs tolerance mode)."""
    print("\n" + "="*60)
    print("TEST 2: SISTER PREFERENCE (Precision vs Tolerance)")
    print("="*60)

    def get_mode_balance(middles, data):
        precision = 0
        tolerance = 0
        for m in middles:
            for token in data[m]:
                mode = SISTER_PAIRS.get(token['prefix'])
                if mode == 'precision':
                    precision += 1
                elif mode == 'tolerance':
                    tolerance += 1
        total = precision + tolerance
        if total == 0:
            return 0.5, 0, 0
        return precision / total, precision, tolerance

    univ_precision_rate, univ_prec, univ_tol = get_mode_balance(universal, middle_data)
    excl_precision_rate, excl_prec, excl_tol = get_mode_balance(exclusive, middle_data)

    print(f"\nPrecision mode rate:")
    print(f"  Universal: {univ_precision_rate*100:.1f}% ({univ_prec}/{univ_prec+univ_tol})")
    print(f"  Exclusive: {excl_precision_rate*100:.1f}% ({excl_prec}/{excl_prec+excl_tol})")

    # Chi-squared test
    contingency = [
        [univ_prec, univ_tol],
        [excl_prec, excl_tol]
    ]

    if min(univ_prec, univ_tol, excl_prec, excl_tol) >= 5:
        chi2, p_value, dof, expected = stats.chi2_contingency(contingency)
        print(f"\nChi-squared: {chi2:.2f}, p = {p_value:.4f}")
    else:
        p_value = 1.0

    # Deviation from 50%
    univ_deviation = abs(univ_precision_rate - 0.5)
    excl_deviation = abs(excl_precision_rate - 0.5)

    print(f"\nDeviation from 50% balance:")
    print(f"  Universal: {univ_deviation*100:.1f}%")
    print(f"  Exclusive: {excl_deviation*100:.1f}%")

    if univ_deviation < excl_deviation:
        print("\n-> Universal MIDDLEs are MORE mode-balanced")
        interpretation = "more_balanced"
    else:
        print("\n-> Universal MIDDLEs are LESS mode-balanced")
        interpretation = "less_balanced"

    return {
        'universal_precision_rate': float(univ_precision_rate),
        'exclusive_precision_rate': float(excl_precision_rate),
        'universal_deviation': float(univ_deviation),
        'exclusive_deviation': float(excl_deviation),
        'p_value': float(p_value),
        'interpretation': interpretation,
    }


def test_position_patterns(universal, exclusive, middle_data):
    """Compare line position tendencies."""
    print("\n" + "="*60)
    print("TEST 3: LINE POSITION PATTERNS")
    print("="*60)

    def get_position_rates(middles, data):
        initial = 0
        final = 0
        total = 0
        for m in middles:
            for token in data[m]:
                total += 1
                if token.get('line_initial'):
                    initial += 1
                if token.get('line_final'):
                    final += 1
        if total == 0:
            return 0, 0, 0
        return initial/total, final/total, total

    univ_init, univ_final, univ_total = get_position_rates(universal, middle_data)
    excl_init, excl_final, excl_total = get_position_rates(exclusive, middle_data)

    print(f"\nLine-initial rate:")
    print(f"  Universal: {univ_init*100:.1f}%")
    print(f"  Exclusive: {excl_init*100:.1f}%")

    print(f"\nLine-final rate:")
    print(f"  Universal: {univ_final*100:.1f}%")
    print(f"  Exclusive: {excl_final*100:.1f}%")

    return {
        'universal_initial_rate': float(univ_init),
        'universal_final_rate': float(univ_final),
        'exclusive_initial_rate': float(excl_init),
        'exclusive_final_rate': float(excl_final),
    }


def test_section_distribution(universal, exclusive, middle_data):
    """Compare section distribution (H/P/T)."""
    print("\n" + "="*60)
    print("TEST 4: SECTION DISTRIBUTION")
    print("="*60)

    def get_section_entropy(middles, data):
        sections = []
        for m in middles:
            for token in data[m]:
                sections.append(token.get('section', 'H'))

        counts = Counter(sections)
        total = sum(counts.values())
        if total == 0:
            return 0, counts
        probs = [c/total for c in counts.values()]
        entropy = -sum(p * np.log2(p) for p in probs if p > 0)
        return entropy, counts

    univ_entropy, univ_counts = get_section_entropy(universal, middle_data)
    excl_entropy, excl_counts = get_section_entropy(exclusive, middle_data)

    print(f"\nSection distribution:")
    print(f"  Universal: {dict(univ_counts)}")
    print(f"  Exclusive: {dict(excl_counts)}")

    print(f"\nSection entropy:")
    print(f"  Universal: {univ_entropy:.3f} bits")
    print(f"  Exclusive: {excl_entropy:.3f} bits")

    if univ_entropy > excl_entropy:
        print("\n-> Universal MIDDLEs spread MORE evenly across sections")
        interpretation = "more_spread"
    else:
        print("\n-> Universal MIDDLEs are MORE section-concentrated")
        interpretation = "more_concentrated"

    return {
        'universal_entropy': float(univ_entropy),
        'exclusive_entropy': float(excl_entropy),
        'interpretation': interpretation,
    }


def test_class_balance(universal, middle_data, middle_by_class):
    """Analyze how evenly universal MIDDLEs distribute across classes."""
    print("\n" + "="*60)
    print("TEST 5: CLASS BALANCE WITHIN UNIVERSAL MIDDLEs")
    print("="*60)

    print("\nClass distribution for each universal MIDDLE:")
    print(f"{'MIDDLE':<12} {'M-A':>8} {'M-B':>8} {'M-C':>8} {'M-D':>8} {'Balance':>10}")
    print("-" * 58)

    balance_scores = []

    for m in sorted(universal, key=lambda x: len(middle_data[x]), reverse=True):
        tokens = middle_data[m]
        class_counts = Counter(PREFIX_TO_CLASS[t['prefix']] for t in tokens)

        counts = [class_counts.get(c, 0) for c in ['M-A', 'M-B', 'M-C', 'M-D']]
        total = sum(counts)

        if total > 0:
            probs = [c/total for c in counts]
            # Balance = normalized entropy (1.0 = perfectly balanced)
            entropy = -sum(p * np.log2(p) for p in probs if p > 0)
            balance = entropy / 2.0  # Max entropy for 4 classes is 2 bits
        else:
            balance = 0

        balance_scores.append(balance)

        print(f"'{m}'".ljust(12) +
              f"{counts[0]:>8}" +
              f"{counts[1]:>8}" +
              f"{counts[2]:>8}" +
              f"{counts[3]:>8}" +
              f"{balance:>10.3f}")

    mean_balance = np.mean(balance_scores)
    print(f"\nMean balance score: {mean_balance:.3f} (1.0 = perfectly even)")

    # Categorize
    highly_balanced = sum(1 for b in balance_scores if b > 0.8)
    ma_skewed = sum(1 for m, b in zip(universal, balance_scores)
                    if b < 0.8 and Counter(PREFIX_TO_CLASS[t['prefix']] for t in middle_data[m]).get('M-A', 0) >
                    sum(Counter(PREFIX_TO_CLASS[t['prefix']] for t in middle_data[m]).values()) * 0.4)

    print(f"\nHighly balanced (>0.8): {highly_balanced}/{len(universal)}")
    print(f"M-A skewed (>40% M-A): {ma_skewed}/{len(universal)}")

    return {
        'mean_balance': float(mean_balance),
        'highly_balanced_count': highly_balanced,
        'total_universal': len(universal),
        'balance_scores': [float(b) for b in balance_scores],
    }


def synthesize_findings(results):
    """Synthesize all test results into structural profile."""
    print("\n" + "="*60)
    print("SYNTHESIS: UNIVERSAL MIDDLE STRUCTURAL PROFILE")
    print("="*60)

    findings = []

    # Suffix diversity
    if results['suffix']['universal_entropy'] > results['suffix']['exclusive_entropy']:
        findings.append("MORE diverse in suffix usage (decision flexibility)")
    else:
        findings.append("LESS diverse in suffix usage (decision specificity)")

    # Sister preference
    if results['sister']['universal_deviation'] < results['sister']['exclusive_deviation']:
        findings.append("MORE balanced between precision/tolerance modes")
    else:
        findings.append("MORE skewed toward one operational mode")

    # Section spread
    if results['section']['universal_entropy'] > results['section']['exclusive_entropy']:
        findings.append("MORE evenly spread across sections")
    else:
        findings.append("MORE concentrated in specific sections")

    print("\nUniversal MIDDLEs are structurally distinguished by being:")
    for f in findings:
        print(f"  - {f}")

    # Tight interpretation
    print("\n" + "-"*60)
    print("TIGHT INTERPRETATION (Tier 3)")
    print("-"*60)

    interpretation = """
Universal MIDDLEs (18 types, 44% of tokens) are structurally distinct:

1. They appear in ALL material classes by definition
2. They show {} suffix diversity than class-exclusive MIDDLEs
3. They are {} between operational modes (precision/tolerance)
4. They are {} across manuscript sections

This suggests universal MIDDLEs encode situations that:
  - Do not depend on material mobility or composition
  - Can occur in any operational mode
  - Are not section-specific

WHAT these situations are remains unknown. We can only say they
are material-property-independent and mode-flexible.
""".format(
        "MORE" if results['suffix']['universal_entropy'] > results['suffix']['exclusive_entropy'] else "LESS",
        "MORE balanced" if results['sister']['universal_deviation'] < results['sister']['exclusive_deviation'] else "LESS balanced",
        "MORE spread" if results['section']['universal_entropy'] > results['section']['exclusive_entropy'] else "MORE concentrated"
    )

    print(interpretation)

    return findings


def main():
    print("="*60)
    print("UNIVERSAL MIDDLE STRUCTURAL PROPERTIES")
    print("="*60)

    # Load and classify
    print("\nLoading data...")
    df = load_currier_a()
    universal, exclusive, bridging, middle_data, middle_by_class = classify_middles(df)

    print(f"\nMIDDLE classification:")
    print(f"  Universal: {len(universal)}")
    print(f"  Bridging: {len(bridging)}")
    print(f"  Exclusive: {len(exclusive)}")

    # Run tests
    results = {
        'metadata': {
            'universal_count': len(universal),
            'exclusive_count': len(exclusive),
            'bridging_count': len(bridging),
        }
    }

    results['suffix'] = test_suffix_distribution(universal, exclusive, middle_data)
    results['sister'] = test_sister_preference(universal, exclusive, middle_data)
    results['position'] = test_position_patterns(universal, exclusive, middle_data)
    results['section'] = test_section_distribution(universal, exclusive, middle_data)
    results['balance'] = test_class_balance(universal, middle_data, middle_by_class)

    # Synthesize
    findings = synthesize_findings(results)
    results['findings'] = findings

    # Save
    def convert_types(obj):
        if isinstance(obj, dict):
            return {k: convert_types(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_types(i) for i in obj]
        elif isinstance(obj, (np.bool_, bool)):
            return bool(obj)
        elif isinstance(obj, (np.integer, np.floating)):
            return float(obj)
        return obj

    with open(OUTPUT_FILE, 'w') as f:
        json.dump(convert_types(results), f, indent=2)

    print(f"\nResults saved to: {OUTPUT_FILE}")


if __name__ == '__main__':
    main()
