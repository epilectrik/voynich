#!/usr/bin/env python3
"""
Probabilistic Currier-A Bundle Generator

Goal: NOT to "generate Currier A text" but to see WHERE AND HOW the generator fails.
Failure modes = new structure.

Hard constraints (include these ONLY):
1. MIDDLE atomic incompatibility graph (C475)
2. Observed line length distribution (C233, C250-C252)
3. PREFIX priors (empirical marginal frequencies)
4. LINE as the specification context (frozen)

Explicitly NOT included (want to see if they emerge or fail):
- Marker exclusivity rules
- Section conditioning
- AZC family information
- HT correlations
- Suffix preferences
- Adjacency coherence (C424)

Expected outcomes:
- Generator will respect incompatibility cleanly ✓
- Universal MIDDLEs will appear as glue ✓
- Over-mixing relative to real A ✗
- Under-representation of pure block entries ✗
- No section isolation ✗
- Wrong repetition statistics ✗
"""

import csv
import json
import random
import numpy as np
from collections import defaultdict, Counter
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional

# Paths
BASE_PATH = Path(__file__).parent.parent.parent
DATA_FILE = BASE_PATH / "data" / "transcriptions" / "interlinear_full_words.txt"
OUTPUT_FILE = BASE_PATH / "results" / "a_bundle_generator.json"

# PREFIX definitions
PREFIXES = ['ch', 'qo', 'sh', 'da', 'ok', 'ot', 'ct', 'ol']

# SUFFIX definitions
SUFFIXES = [
    'aiin', 'aiiin', 'ain', 'iin', 'in',
    'ar', 'or', 'al', 'ol', 'am', 'an',
    'dy', 'edy', 'eedy', 'chy', 'shy', 'ty', 'ky', 'ly', 'ry', 'y',
    'r', 'l', 's', 'd', 'n', 'm'
]

# AZC folios (for exclusion - we want all Currier A, not just AZC)
ZODIAC_FOLIOS = {
    'f57v', 'f70v1', 'f70v2', 'f71r', 'f71v',
    'f72r1', 'f72r2', 'f72r3', 'f72v1', 'f72v2', 'f72v3',
    'f73r', 'f73v'
}
AC_FOLIOS = {
    'f116v', 'f65r', 'f65v', 'f67r1', 'f67r2', 'f67v1', 'f67v2',
    'f68r1', 'f68r2', 'f68r3', 'f68v1', 'f68v2', 'f68v3',
    'f69r', 'f69v', 'f70r1', 'f70r2'
}
ALL_AZC_FOLIOS = ZODIAC_FOLIOS | AC_FOLIOS


def decompose_token(token: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """Decompose token into PREFIX, MIDDLE, SUFFIX."""
    if not token or len(token) < 2:
        return None, None, None
    if token.startswith('[') or token.startswith('<') or '*' in token:
        return None, None, None

    prefix = None
    rest = token
    for p in sorted(PREFIXES, key=len, reverse=True):
        if token.startswith(p):
            prefix = p
            rest = token[len(p):]
            break

    suffix = None
    middle = rest
    for s in sorted(SUFFIXES, key=len, reverse=True):
        if rest.endswith(s) and len(rest) > len(s):
            suffix = s
            middle = rest[:-len(s)]
            break

    if not middle:
        middle = None

    return prefix, middle, suffix


def load_currier_a_data() -> Tuple[Dict, Dict, List[str], Dict]:
    """
    Load all Currier A data (AZC folios).
    Returns:
        line_data: {(folio, line) -> [(token, prefix, middle, suffix), ...]}
        middle_to_prefix: {middle -> set of prefixes}
        all_middles: sorted list of all MIDDLEs
        empirical_priors: {prefix_freq, middle_freq, suffix_freq, line_lengths}
    """
    line_data = defaultdict(list)
    middle_to_prefix = defaultdict(set)
    all_middles_set = set()

    prefix_counts = Counter()
    middle_counts = Counter()
    suffix_counts = Counter()
    line_lengths = []

    current_line = None
    current_line_tokens = []

    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            word = row.get('"word"', row.get('word', '')).strip().strip('"')
            folio = row.get('"folio"', row.get('folio', '')).strip().strip('"')
            line = row.get('"line_number"', row.get('line_number', '')).strip().strip('"')

            # Only AZC folios (Currier A)
            if folio not in ALL_AZC_FOLIOS:
                continue

            prefix, middle, suffix = decompose_token(word)

            if middle:
                line_data[(folio, line)].append((word, prefix, middle, suffix))
                if prefix:
                    middle_to_prefix[middle].add(prefix)
                    prefix_counts[prefix] += 1
                middle_counts[middle] += 1
                if suffix:
                    suffix_counts[suffix] += 1
                all_middles_set.add(middle)

    # Compute line lengths
    for key, tokens in line_data.items():
        line_lengths.append(len(tokens))

    all_middles = sorted(all_middles_set)

    # Normalize counts to frequencies
    total_prefix = sum(prefix_counts.values()) or 1
    total_middle = sum(middle_counts.values()) or 1
    total_suffix = sum(suffix_counts.values()) or 1

    empirical_priors = {
        'prefix_freq': {p: c/total_prefix for p, c in prefix_counts.items()},
        'middle_freq': {m: c/total_middle for m, c in middle_counts.items()},
        'suffix_freq': {s: c/total_suffix for s, c in suffix_counts.items()},
        'line_lengths': line_lengths,
        'line_length_mean': np.mean(line_lengths),
        'line_length_std': np.std(line_lengths)
    }

    return dict(line_data), dict(middle_to_prefix), all_middles, empirical_priors


def build_compatibility_graph(line_data: Dict, all_middles: List[str]) -> Dict[str, Set[str]]:
    """
    Build MIDDLE compatibility graph from line co-occurrence.
    compatible[m1] = set of MIDDLEs that can co-occur with m1.
    """
    compatible = defaultdict(set)

    for (folio, line), tokens in line_data.items():
        middles_in_line = [m for (w, p, m, s) in tokens if m]
        for i, m1 in enumerate(middles_in_line):
            for m2 in middles_in_line[i+1:]:
                compatible[m1].add(m2)
                compatible[m2].add(m1)

    return dict(compatible)


def generate_line(
    target_length: int,
    prefix_freq: Dict[str, float],
    middle_freq: Dict[str, float],
    suffix_freq: Dict[str, float],
    compatible: Dict[str, Set[str]],
    all_middles: List[str],
    middle_to_prefix: Dict[str, Set[str]],
    max_attempts: int = 1000
) -> List[Tuple[str, str, str]]:
    """
    Generate a single synthetic line.

    Algorithm:
    1. Sample line length from empirical distribution (already passed as target_length)
    2. Iteratively sample MIDDLEs:
       - Sample from middle_freq
       - Check compatibility with all already-selected MIDDLEs
       - If incompatible, reject and resample
       - Stop when target_length reached or dead-end
    3. Assign PREFIX based on middle_to_prefix (sample from associated prefixes)
    4. Assign SUFFIX uniformly at random

    Returns: [(prefix, middle, suffix), ...]
    """
    selected_middles = []

    # Build sampling distribution (weighted by frequency)
    middle_probs = np.array([middle_freq.get(m, 1e-10) for m in all_middles])
    middle_probs /= middle_probs.sum()

    # Suffix sampling distribution
    suffix_list = list(suffix_freq.keys())
    suffix_probs = np.array([suffix_freq[s] for s in suffix_list])
    suffix_probs /= suffix_probs.sum()

    attempts = 0
    while len(selected_middles) < target_length and attempts < max_attempts:
        attempts += 1

        # Sample a MIDDLE
        candidate = np.random.choice(all_middles, p=middle_probs)

        # Check compatibility with all selected MIDDLEs
        is_compatible = True
        for existing in selected_middles:
            if candidate not in compatible.get(existing, set()) and candidate != existing:
                is_compatible = False
                break

        if is_compatible:
            selected_middles.append(candidate)

    # Now assign PREFIX and SUFFIX
    result = []
    for middle in selected_middles:
        # PREFIX: sample from associated prefixes (or None if no prefix)
        associated_prefixes = list(middle_to_prefix.get(middle, set()))
        if associated_prefixes:
            prefix = random.choice(associated_prefixes)
        else:
            # Sample from overall prefix distribution
            prefix_list = list(prefix_freq.keys())
            prefix_probs_arr = np.array([prefix_freq[p] for p in prefix_list])
            prefix_probs_arr /= prefix_probs_arr.sum()
            prefix = np.random.choice(prefix_list, p=prefix_probs_arr) if prefix_list else None

        # SUFFIX: uniform random
        suffix = np.random.choice(suffix_list, p=suffix_probs) if suffix_list else None

        result.append((prefix, middle, suffix))

    return result


def generate_synthetic_corpus(
    n_lines: int,
    line_lengths: List[int],
    prefix_freq: Dict[str, float],
    middle_freq: Dict[str, float],
    suffix_freq: Dict[str, float],
    compatible: Dict[str, Set[str]],
    all_middles: List[str],
    middle_to_prefix: Dict[str, Set[str]]
) -> List[List[Tuple[str, str, str]]]:
    """Generate n_lines synthetic lines."""
    synthetic_lines = []

    for i in range(n_lines):
        # Sample line length from empirical distribution
        target_length = random.choice(line_lengths)

        line = generate_line(
            target_length, prefix_freq, middle_freq, suffix_freq,
            compatible, all_middles, middle_to_prefix
        )
        synthetic_lines.append(line)

        if (i + 1) % 500 == 0:
            print(f"   Generated {i+1}/{n_lines} lines...")

    return synthetic_lines


# ============================================================
# DIAGNOSTIC METRICS
# ============================================================

def compute_diagnostics(lines: List, is_real: bool = True) -> Dict:
    """
    Compute diagnostic metrics for a corpus (real or synthetic).

    Metrics:
    1. Line length distribution
    2. MIDDLE frequency distribution
    3. PREFIX frequency distribution
    4. Mixing metrics (how many different prefixes per line)
    5. Repetition metrics (how often same MIDDLE appears in a line)
    6. Block purity (fraction of lines with single prefix family)
    7. Universal MIDDLE usage
    """
    diagnostics = {}

    # Convert to common format: [[(prefix, middle, suffix), ...], ...]
    if is_real:
        # Real data is {(folio, line) -> [(token, prefix, middle, suffix), ...]}
        processed_lines = []
        for key, tokens in lines.items():
            processed_lines.append([(p, m, s) for (w, p, m, s) in tokens])
    else:
        # Synthetic data is already [[(prefix, middle, suffix), ...], ...]
        processed_lines = lines

    # 1. Line lengths
    line_lengths = [len(line) for line in processed_lines]
    diagnostics['line_length_mean'] = np.mean(line_lengths) if line_lengths else 0
    diagnostics['line_length_std'] = np.std(line_lengths) if line_lengths else 0
    diagnostics['line_length_median'] = np.median(line_lengths) if line_lengths else 0

    # 2. MIDDLE frequencies
    middle_counts = Counter()
    for line in processed_lines:
        for (p, m, s) in line:
            if m:
                middle_counts[m] += 1
    total_middles = sum(middle_counts.values()) or 1
    diagnostics['unique_middles'] = len(middle_counts)
    diagnostics['middle_entropy'] = -sum(
        (c/total_middles) * np.log2(c/total_middles + 1e-10)
        for c in middle_counts.values()
    )

    # 3. PREFIX frequencies
    prefix_counts = Counter()
    for line in processed_lines:
        for (p, m, s) in line:
            if p:
                prefix_counts[p] += 1
    total_prefixes = sum(prefix_counts.values()) or 1
    diagnostics['prefix_distribution'] = {p: c/total_prefixes for p, c in prefix_counts.most_common(10)}

    # 4. Mixing metrics (prefixes per line)
    prefixes_per_line = []
    for line in processed_lines:
        line_prefixes = set(p for (p, m, s) in line if p)
        prefixes_per_line.append(len(line_prefixes))

    diagnostics['prefixes_per_line_mean'] = np.mean(prefixes_per_line) if prefixes_per_line else 0
    diagnostics['prefixes_per_line_std'] = np.std(prefixes_per_line) if prefixes_per_line else 0

    # Fraction of lines with different mixing levels
    diagnostics['lines_zero_mixing'] = sum(1 for x in prefixes_per_line if x <= 1) / len(prefixes_per_line) if prefixes_per_line else 0
    diagnostics['lines_low_mixing'] = sum(1 for x in prefixes_per_line if x <= 2) / len(prefixes_per_line) if prefixes_per_line else 0
    diagnostics['lines_high_mixing'] = sum(1 for x in prefixes_per_line if x >= 4) / len(prefixes_per_line) if prefixes_per_line else 0

    # 5. Repetition metrics (same MIDDLE appearing multiple times in a line)
    lines_with_repetition = 0
    total_repetitions = 0
    for line in processed_lines:
        line_middles = [m for (p, m, s) in line if m]
        middle_set = set(line_middles)
        if len(line_middles) > len(middle_set):
            lines_with_repetition += 1
            total_repetitions += len(line_middles) - len(middle_set)

    diagnostics['lines_with_repetition_frac'] = lines_with_repetition / len(processed_lines) if processed_lines else 0
    diagnostics['avg_repetitions_per_line'] = total_repetitions / len(processed_lines) if processed_lines else 0

    # 6. Block purity (lines with single dominant prefix)
    pure_blocks = 0
    for line in processed_lines:
        line_prefixes = [p for (p, m, s) in line if p]
        if line_prefixes:
            most_common = Counter(line_prefixes).most_common(1)[0]
            if most_common[1] / len(line_prefixes) >= 0.8:  # 80% same prefix
                pure_blocks += 1

    diagnostics['pure_block_frac'] = pure_blocks / len(processed_lines) if processed_lines else 0

    # 7. Universal MIDDLE usage
    universal_middles = {'a', 'o', 'e', 'ee', 'eo'}
    universal_count = sum(middle_counts.get(m, 0) for m in universal_middles)
    diagnostics['universal_middle_frac'] = universal_count / total_middles

    # 8. Top MIDDLEs
    diagnostics['top_middles'] = dict(middle_counts.most_common(10))

    return diagnostics


def compare_diagnostics(real_diag: Dict, synth_diag: Dict) -> Dict:
    """Compare real vs synthetic diagnostics and compute residuals."""
    comparison = {}

    # Numeric comparisons
    numeric_keys = [
        'line_length_mean', 'line_length_std', 'line_length_median',
        'unique_middles', 'middle_entropy',
        'prefixes_per_line_mean', 'prefixes_per_line_std',
        'lines_zero_mixing', 'lines_low_mixing', 'lines_high_mixing',
        'lines_with_repetition_frac', 'avg_repetitions_per_line',
        'pure_block_frac', 'universal_middle_frac'
    ]

    for key in numeric_keys:
        real_val = real_diag.get(key, 0)
        synth_val = synth_diag.get(key, 0)
        diff = synth_val - real_val
        rel_diff = diff / (abs(real_val) + 1e-10)

        comparison[key] = {
            'real': round(real_val, 4),
            'synthetic': round(synth_val, 4),
            'difference': round(diff, 4),
            'relative_diff': round(rel_diff, 4)
        }

    return comparison


def main():
    print("=" * 70)
    print("PROBABILISTIC CURRIER-A BUNDLE GENERATOR")
    print("=" * 70)
    print("\nGoal: See WHERE AND HOW the generator fails (failure modes = structure)")
    print()

    # Step 1: Load Currier A data
    print("1. Loading Currier A data (AZC folios)...")
    line_data, middle_to_prefix, all_middles, priors = load_currier_a_data()
    print(f"   Loaded {len(line_data)} lines with {len(all_middles)} unique MIDDLEs")
    print(f"   Line length: mean={priors['line_length_mean']:.1f}, std={priors['line_length_std']:.1f}")

    # Step 2: Build compatibility graph
    print("\n2. Building MIDDLE compatibility graph...")
    compatible = build_compatibility_graph(line_data, all_middles)
    total_compatible = sum(len(v) for v in compatible.values()) // 2
    print(f"   Compatible pairs: {total_compatible}")

    # Step 3: Compute diagnostics on real data
    print("\n3. Computing diagnostics on real Currier A...")
    real_diagnostics = compute_diagnostics(line_data, is_real=True)
    print(f"   Line length: {real_diagnostics['line_length_mean']:.2f} +/- {real_diagnostics['line_length_std']:.2f}")
    print(f"   Prefixes per line: {real_diagnostics['prefixes_per_line_mean']:.2f}")
    print(f"   Lines with zero mixing: {100*real_diagnostics['lines_zero_mixing']:.1f}%")
    print(f"   Pure block fraction: {100*real_diagnostics['pure_block_frac']:.1f}%")
    print(f"   Lines with repetition: {100*real_diagnostics['lines_with_repetition_frac']:.1f}%")
    print(f"   Universal MIDDLE fraction: {100*real_diagnostics['universal_middle_frac']:.1f}%")

    # Step 4: Generate synthetic corpus
    n_synthetic = len(line_data)
    print(f"\n4. Generating {n_synthetic} synthetic lines...")

    synthetic_lines = generate_synthetic_corpus(
        n_lines=n_synthetic,
        line_lengths=priors['line_lengths'],
        prefix_freq=priors['prefix_freq'],
        middle_freq=priors['middle_freq'],
        suffix_freq=priors['suffix_freq'],
        compatible=compatible,
        all_middles=all_middles,
        middle_to_prefix=middle_to_prefix
    )
    print(f"   Generated {len(synthetic_lines)} synthetic lines")

    # Step 5: Compute diagnostics on synthetic data
    print("\n5. Computing diagnostics on synthetic data...")
    synth_diagnostics = compute_diagnostics(synthetic_lines, is_real=False)
    print(f"   Line length: {synth_diagnostics['line_length_mean']:.2f} +/- {synth_diagnostics['line_length_std']:.2f}")
    print(f"   Prefixes per line: {synth_diagnostics['prefixes_per_line_mean']:.2f}")
    print(f"   Lines with zero mixing: {100*synth_diagnostics['lines_zero_mixing']:.1f}%")
    print(f"   Pure block fraction: {100*synth_diagnostics['pure_block_frac']:.1f}%")
    print(f"   Lines with repetition: {100*synth_diagnostics['lines_with_repetition_frac']:.1f}%")
    print(f"   Universal MIDDLE fraction: {100*synth_diagnostics['universal_middle_frac']:.1f}%")

    # Step 6: Compare and identify residuals
    print("\n6. Comparing real vs synthetic (RESIDUAL ANALYSIS)...")
    comparison = compare_diagnostics(real_diagnostics, synth_diagnostics)

    print("\n" + "=" * 70)
    print("RESIDUAL ANALYSIS - WHERE THE GENERATOR FAILS")
    print("=" * 70)

    # Sort by absolute relative difference
    sorted_metrics = sorted(
        comparison.items(),
        key=lambda x: abs(x[1]['relative_diff']),
        reverse=True
    )

    print("\n   Metric                        | Real    | Synth   | Diff    | Rel.Diff")
    print("   " + "-" * 75)

    failures = []
    for metric, vals in sorted_metrics:
        status = "FAIL" if abs(vals['relative_diff']) > 0.2 else "OK"
        print(f"   {metric:30} | {vals['real']:7.3f} | {vals['synthetic']:7.3f} | {vals['difference']:+7.3f} | {vals['relative_diff']:+7.3f} {status}")

        if abs(vals['relative_diff']) > 0.2:
            failures.append((metric, vals))

    # Step 7: Interpret failures
    print("\n" + "=" * 70)
    print("FAILURE INTERPRETATION")
    print("=" * 70)

    failure_interpretations = {
        'lines_zero_mixing': "Generator OVER-MIXES: Real A has more single-prefix lines",
        'lines_low_mixing': "Generator OVER-MIXES: Real A has more low-mixing lines",
        'lines_high_mixing': "Generator UNDER-MIXES: Real A has more high-mixing lines (unlikely)",
        'pure_block_frac': "Generator produces fewer PURE BLOCKS than real A",
        'prefixes_per_line_mean': "Generator has wrong PREFIX diversity per line",
        'lines_with_repetition_frac': "Generator has wrong REPETITION structure",
        'avg_repetitions_per_line': "Generator has wrong REPETITION intensity",
        'universal_middle_frac': "Generator uses universal MIDDLEs differently",
        'middle_entropy': "Generator has wrong MIDDLE diversity",
        'unique_middles': "Generator uses different number of unique MIDDLEs"
    }

    for metric, vals in failures:
        interpretation = failure_interpretations.get(metric, f"Generator deviates on {metric}")
        direction = "higher" if vals['difference'] > 0 else "lower"
        print(f"\n   {metric}:")
        print(f"      Real: {vals['real']:.4f}")
        print(f"      Synthetic: {vals['synthetic']:.4f} ({direction})")
        print(f"      >>> {interpretation}")

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    n_failures = len(failures)
    n_total = len(comparison)

    if n_failures == 0:
        verdict = "SUSPICIOUSLY GOOD"
        interpretation = "Generator matches too well - check for constraint leakage"
    elif n_failures <= 3:
        verdict = "PARTIAL SUCCESS"
        interpretation = "Generator captures most structure but fails on specific dimensions"
    else:
        verdict = "EXPECTED FAILURE"
        interpretation = "Generator fails on multiple dimensions - structure exists beyond constraints"

    print(f"\n   >>> {verdict} ({n_failures}/{n_total} metrics fail) <<<")
    print(f"   {interpretation}")

    # Save results
    output = {
        'probe_id': 'A_BUNDLE_GENERATOR',
        'goal': 'See where and how the generator fails (failure modes = structure)',
        'constraints_included': [
            'MIDDLE atomic incompatibility (C475)',
            'Line length distribution (C233, C250-C252)',
            'PREFIX priors (empirical frequencies)',
            'LINE as specification context'
        ],
        'constraints_excluded': [
            'Marker exclusivity rules',
            'Section conditioning',
            'AZC family information',
            'HT correlations',
            'Suffix preferences',
            'Adjacency coherence (C424)'
        ],
        'corpus_size': {
            'real_lines': len(line_data),
            'synthetic_lines': len(synthetic_lines),
            'unique_middles': len(all_middles)
        },
        'real_diagnostics': {k: (v if not isinstance(v, (np.floating, np.integer)) else float(v))
                            for k, v in real_diagnostics.items() if not isinstance(v, dict)},
        'synthetic_diagnostics': {k: (v if not isinstance(v, (np.floating, np.integer)) else float(v))
                                  for k, v in synth_diagnostics.items() if not isinstance(v, dict)},
        'comparison': comparison,
        'failures': [(m, v) for m, v in failures],
        'verdict': {
            'status': verdict,
            'n_failures': n_failures,
            'n_total': n_total,
            'interpretation': interpretation
        }
    }

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, default=str)

    print(f"\n\nResults saved to: {OUTPUT_FILE}")

    return output


if __name__ == "__main__":
    main()
