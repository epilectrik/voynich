#!/usr/bin/env python3
"""
F-AZC-006: Boundary Airlock Profile

Question: Does AZC act as an entropy discontinuity in the A-space?

Method:
- Measure option-space metrics in windows:
  - N tokens BEFORE AZC entry
  - INSIDE AZC
  - N tokens AFTER AZC exit
- Metrics: MIDDLE diversity, suffix entropy, escape availability
- Fit models: step vs ramp vs null

Success Criteria:
- Sharp entropy drop/redistribution at entry
- Rebound after exit
- Step model fits better than ramp or null

Why This Matters:
Confirms AZC's role as transition corridor. Integrates with "legality sieve" result from F-AZC-004.
"""

import json
import sys
from pathlib import Path
from collections import defaultdict, Counter
from math import log2
import numpy as np

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from archive.scripts.currier_a_token_generator import decompose_token

# Escape prefixes
ESCAPE_PREFIXES = {'qo', 'ct'}


def load_all_tokens_ordered():
    """Load all tokens in document order."""
    filepath = Path(__file__).parent.parent.parent / 'data' / 'transcriptions' / 'interlinear_full_words.txt'

    tokens = []
    with open(filepath, 'r', encoding='utf-8') as f:
        header = f.readline()
        for line_idx, line in enumerate(f):
            parts = line.strip().split('\t')
            if len(parts) > 12:
                # Filter to PRIMARY transcriber (H) only
                transcriber = parts[12].strip('"').strip()
                if transcriber != 'H':
                    continue
                currier = parts[6].strip('"').strip()
                token = parts[0].strip('"').strip().lower()
                folio = parts[2].strip('"').strip()

                if not token:
                    continue

                # Classify system
                if currier == 'A':
                    system = 'A'
                elif currier == 'B':
                    system = 'B'
                elif currier == 'NA':
                    system = 'AZC'
                else:
                    system = 'unknown'

                # Decompose
                result = decompose_token(token)
                if result[0]:
                    prefix, middle, suffix = result
                    is_escape = prefix in ESCAPE_PREFIXES
                else:
                    prefix, middle, suffix = None, None, None
                    is_escape = False

                tokens.append({
                    'token': token,
                    'folio': folio,
                    'system': system,
                    'line_idx': line_idx,
                    'prefix': prefix,
                    'middle': middle,
                    'suffix': suffix,
                    'is_escape': is_escape
                })

    return tokens


def calculate_window_metrics(tokens):
    """Calculate option-space metrics for a token window."""

    decomposed = [t for t in tokens if t['prefix'] is not None]

    if len(decomposed) < 5:
        return None

    # Counts
    prefix_counts = Counter(t['prefix'] for t in decomposed)
    middle_counts = Counter(t['middle'] for t in decomposed)
    suffix_counts = Counter(t['suffix'] for t in decomposed)

    # Entropy calculation
    def entropy(counts):
        total = sum(counts.values())
        if total == 0:
            return 0.0
        ent = 0.0
        for c in counts.values():
            if c > 0:
                p = c / total
                ent -= p * log2(p)
        return ent

    prefix_ent = entropy(prefix_counts)
    middle_ent = entropy(middle_counts)
    suffix_ent = entropy(suffix_counts)

    # Escape rate
    escape_count = sum(1 for t in decomposed if t['is_escape'])
    escape_rate = escape_count / len(decomposed) * 100

    # Diversity (unique types / total)
    type_diversity = len(set(t['token'] for t in tokens)) / len(tokens)
    middle_diversity = len(middle_counts) / len(decomposed) if decomposed else 0

    return {
        'n_tokens': len(tokens),
        'n_decomposed': len(decomposed),
        'prefix_entropy': prefix_ent,
        'middle_entropy': middle_ent,
        'suffix_entropy': suffix_ent,
        'total_entropy': prefix_ent + middle_ent + suffix_ent,
        'escape_rate': escape_rate,
        'type_diversity': type_diversity,
        'middle_diversity': middle_diversity,
        'n_unique_middles': len(middle_counts)
    }


def find_azc_boundaries(tokens):
    """Find entry and exit points for AZC sections."""

    boundaries = []
    current_system = None
    azc_start = None

    for i, t in enumerate(tokens):
        if current_system != t['system']:
            # System change
            if t['system'] == 'AZC' and current_system == 'A':
                # Entry into AZC from A
                azc_start = i
            elif current_system == 'AZC' and t['system'] == 'A':
                # Exit from AZC to A
                if azc_start is not None:
                    boundaries.append({
                        'entry': azc_start,
                        'exit': i,
                        'length': i - azc_start
                    })
                azc_start = None
            elif current_system == 'AZC' and t['system'] != 'A':
                # AZC to non-A (e.g., B) - record but note it's not A-exit
                if azc_start is not None:
                    boundaries.append({
                        'entry': azc_start,
                        'exit': i,
                        'length': i - azc_start,
                        'exit_to_non_A': True
                    })
                azc_start = None

            current_system = t['system']

    return boundaries


def analyze_boundary_profile(tokens, window_size=50):
    """Analyze entropy profile around AZC boundaries."""

    boundaries = find_azc_boundaries(tokens)

    profiles = []

    for b in boundaries:
        entry = b['entry']
        exit_idx = b['exit']

        # Before window (A tokens before AZC)
        before_start = max(0, entry - window_size)
        before_tokens = [t for t in tokens[before_start:entry] if t['system'] == 'A']

        # Inside AZC
        azc_tokens = tokens[entry:exit_idx]

        # After window (A tokens after AZC)
        after_end = min(len(tokens), exit_idx + window_size)
        after_tokens = [t for t in tokens[exit_idx:after_end] if t['system'] == 'A']

        before_metrics = calculate_window_metrics(before_tokens)
        azc_metrics = calculate_window_metrics(azc_tokens)
        after_metrics = calculate_window_metrics(after_tokens)

        if before_metrics and azc_metrics:
            profiles.append({
                'entry_idx': entry,
                'exit_idx': exit_idx,
                'azc_length': b['length'],
                'before': before_metrics,
                'azc': azc_metrics,
                'after': after_metrics,
                'exit_to_non_A': b.get('exit_to_non_A', False)
            })

    return profiles


def compute_aggregate_profile(profiles):
    """Compute aggregate statistics across all boundary crossings."""

    if not profiles:
        return None

    before_entropies = [p['before']['total_entropy'] for p in profiles if p['before']]
    azc_entropies = [p['azc']['total_entropy'] for p in profiles if p['azc']]
    after_entropies = [p['after']['total_entropy'] for p in profiles if p['after']]

    before_escapes = [p['before']['escape_rate'] for p in profiles if p['before']]
    azc_escapes = [p['azc']['escape_rate'] for p in profiles if p['azc']]
    after_escapes = [p['after']['escape_rate'] for p in profiles if p['after']]

    before_diversity = [p['before']['middle_diversity'] for p in profiles if p['before']]
    azc_diversity = [p['azc']['middle_diversity'] for p in profiles if p['azc']]
    after_diversity = [p['after']['middle_diversity'] for p in profiles if p['after']]

    return {
        'n_boundaries': len(profiles),
        'total_entropy': {
            'before_mean': np.mean(before_entropies) if before_entropies else None,
            'azc_mean': np.mean(azc_entropies) if azc_entropies else None,
            'after_mean': np.mean(after_entropies) if after_entropies else None,
            'before_std': np.std(before_entropies) if before_entropies else None,
            'azc_std': np.std(azc_entropies) if azc_entropies else None,
            'after_std': np.std(after_entropies) if after_entropies else None
        },
        'escape_rate': {
            'before_mean': np.mean(before_escapes) if before_escapes else None,
            'azc_mean': np.mean(azc_escapes) if azc_escapes else None,
            'after_mean': np.mean(after_escapes) if after_escapes else None
        },
        'middle_diversity': {
            'before_mean': np.mean(before_diversity) if before_diversity else None,
            'azc_mean': np.mean(azc_diversity) if azc_diversity else None,
            'after_mean': np.mean(after_diversity) if after_diversity else None
        }
    }


def test_step_model(profiles, metric_key):
    """Test if there's a significant step change at AZC boundaries."""
    from scipy import stats

    before_vals = [p['before'][metric_key] for p in profiles if p['before']]
    azc_vals = [p['azc'][metric_key] for p in profiles if p['azc']]
    after_vals = [p['after'][metric_key] for p in profiles if p['after']]

    results = {}

    # Before vs AZC
    if len(before_vals) >= 3 and len(azc_vals) >= 3:
        stat, p = stats.mannwhitneyu(before_vals, azc_vals, alternative='two-sided')
        results['before_vs_azc'] = {
            'u_stat': float(stat),
            'p_value': float(p),
            'significant': bool(p < 0.05),
            'before_mean': float(np.mean(before_vals)),
            'azc_mean': float(np.mean(azc_vals)),
            'direction': 'decrease' if np.mean(before_vals) > np.mean(azc_vals) else 'increase'
        }

    # AZC vs After
    if len(azc_vals) >= 3 and len(after_vals) >= 3:
        stat, p = stats.mannwhitneyu(azc_vals, after_vals, alternative='two-sided')
        results['azc_vs_after'] = {
            'u_stat': float(stat),
            'p_value': float(p),
            'significant': bool(p < 0.05),
            'azc_mean': float(np.mean(azc_vals)),
            'after_mean': float(np.mean(after_vals)),
            'direction': 'decrease' if np.mean(azc_vals) > np.mean(after_vals) else 'increase'
        }

    return results


def main():
    print("=" * 60)
    print("F-AZC-006: Boundary Airlock Profile")
    print("=" * 60)
    print()

    # Load data
    tokens = load_all_tokens_ordered()

    a_count = sum(1 for t in tokens if t['system'] == 'A')
    azc_count = sum(1 for t in tokens if t['system'] == 'AZC')
    b_count = sum(1 for t in tokens if t['system'] == 'B')

    print(f"Total tokens: {len(tokens)}")
    print(f"Currier A: {a_count}")
    print(f"AZC: {azc_count}")
    print(f"Currier B: {b_count}")
    print()

    # Find and analyze boundaries
    profiles = analyze_boundary_profile(tokens, window_size=100)

    print(f"AZC boundary crossings found: {len(profiles)}")
    print()

    if not profiles:
        print("Insufficient boundary crossings for analysis")
        return

    # Aggregate profile
    aggregate = compute_aggregate_profile(profiles)

    print("=" * 60)
    print("Aggregate Boundary Profile (mean across crossings)")
    print("=" * 60)
    print()

    print(f"{'Metric':<25} {'Before A':>12} {'Inside AZC':>12} {'After A':>12}")
    print("-" * 60)

    if aggregate['total_entropy']['before_mean'] is not None:
        print(f"{'Total entropy (bits)':<25} {aggregate['total_entropy']['before_mean']:>12.2f} {aggregate['total_entropy']['azc_mean']:>12.2f} {aggregate['total_entropy']['after_mean'] if aggregate['total_entropy']['after_mean'] else 'N/A':>12}")

    if aggregate['escape_rate']['before_mean'] is not None:
        after_esc = f"{aggregate['escape_rate']['after_mean']:.1f}%" if aggregate['escape_rate']['after_mean'] else 'N/A'
        print(f"{'Escape rate':<25} {aggregate['escape_rate']['before_mean']:>11.1f}% {aggregate['escape_rate']['azc_mean']:>11.1f}% {after_esc:>12}")

    if aggregate['middle_diversity']['before_mean'] is not None:
        after_div = f"{aggregate['middle_diversity']['after_mean']:.3f}" if aggregate['middle_diversity']['after_mean'] else 'N/A'
        print(f"{'MIDDLE diversity':<25} {aggregate['middle_diversity']['before_mean']:>12.3f} {aggregate['middle_diversity']['azc_mean']:>12.3f} {after_div:>12}")
    print()

    # Statistical tests
    print("=" * 60)
    print("Step Model Tests")
    print("=" * 60)
    print()

    # Test escape rate step
    escape_test = test_step_model(profiles, 'escape_rate')

    if 'before_vs_azc' in escape_test:
        t = escape_test['before_vs_azc']
        print(f"Escape rate: Before A -> AZC")
        print(f"  Before mean: {t['before_mean']:.1f}%, AZC mean: {t['azc_mean']:.1f}%")
        print(f"  Mann-Whitney U p-value: {t['p_value']:.6f}")
        print(f"  Result: {'SIGNIFICANT STEP ***' if t['significant'] else 'NOT SIGNIFICANT'}")
        print()

    if 'azc_vs_after' in escape_test:
        t = escape_test['azc_vs_after']
        print(f"Escape rate: AZC -> After A")
        print(f"  AZC mean: {t['azc_mean']:.1f}%, After mean: {t['after_mean']:.1f}%")
        print(f"  Mann-Whitney U p-value: {t['p_value']:.6f}")
        print(f"  Result: {'SIGNIFICANT STEP ***' if t['significant'] else 'NOT SIGNIFICANT'}")
        print()

    # Test total entropy step
    entropy_test = test_step_model(profiles, 'total_entropy')

    if 'before_vs_azc' in entropy_test:
        t = entropy_test['before_vs_azc']
        print(f"Total entropy: Before A -> AZC")
        print(f"  Before mean: {t['before_mean']:.2f} bits, AZC mean: {t['azc_mean']:.2f} bits")
        print(f"  Mann-Whitney U p-value: {t['p_value']:.6f}")
        print(f"  Result: {'SIGNIFICANT STEP ***' if t['significant'] else 'NOT SIGNIFICANT'}")
        print()

    # Interpretation
    print("=" * 60)
    print("INTERPRETATION")
    print("=" * 60)
    print()

    escape_step_entry = escape_test.get('before_vs_azc', {}).get('significant', False)
    escape_step_exit = escape_test.get('azc_vs_after', {}).get('significant', False)
    entropy_step_entry = entropy_test.get('before_vs_azc', {}).get('significant', False)

    evidence_count = sum([escape_step_entry, escape_step_exit, entropy_step_entry])

    print(f"Evidence for airlock behavior: {evidence_count}/3")
    print(f"  - Escape step at entry: {'YES' if escape_step_entry else 'NO'}")
    print(f"  - Escape rebound at exit: {'YES' if escape_step_exit else 'NO'}")
    print(f"  - Entropy step at entry: {'YES' if entropy_step_entry else 'NO'}")
    print()

    if evidence_count >= 2:
        conclusion = "AZC acts as an AIRLOCK - sharp entropy discontinuity"
        role = "TRANSITION CORRIDOR with step-change behavior"
        fit_tier = "F2"
    elif evidence_count == 1:
        conclusion = "AZC shows WEAK airlock behavior"
        role = "PARTIAL TRANSITION CORRIDOR"
        fit_tier = "F3"
    else:
        conclusion = "AZC does NOT show airlock behavior"
        role = "CONTINUOUS SYSTEM (no step change)"
        fit_tier = "F4"

    print(f"CONCLUSION: {conclusion}")
    print(f"ROLE: {role}")
    print(f"Fit tier: {fit_tier}")

    # Prepare output
    output = {
        'fit_id': 'F-AZC-006',
        'question': 'Does AZC act as an entropy discontinuity?',
        'metadata': {
            'total_tokens': len(tokens),
            'a_tokens': a_count,
            'azc_tokens': azc_count,
            'boundary_crossings': len(profiles)
        },
        'aggregate_profile': {
            'total_entropy': {k: round(v, 3) if v is not None else None for k, v in aggregate['total_entropy'].items()},
            'escape_rate': {k: round(v, 2) if v is not None else None for k, v in aggregate['escape_rate'].items()},
            'middle_diversity': {k: round(v, 4) if v is not None else None for k, v in aggregate['middle_diversity'].items()}
        },
        'step_tests': {
            'escape_rate': {k: {kk: round(vv, 4) if isinstance(vv, float) else vv for kk, vv in v.items()} for k, v in escape_test.items()},
            'total_entropy': {k: {kk: round(vv, 4) if isinstance(vv, float) else vv for kk, vv in v.items()} for k, v in entropy_test.items()}
        },
        'evidence': {
            'escape_step_entry': escape_step_entry,
            'escape_step_exit': escape_step_exit,
            'entropy_step_entry': entropy_step_entry,
            'evidence_count': evidence_count
        },
        'interpretation': {
            'conclusion': conclusion,
            'role': role,
            'fit_tier': fit_tier
        }
    }

    # Save results
    output_path = Path(__file__).parent.parent.parent / 'results' / 'azc_boundary_airlock.json'
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to: {output_path}")

    return output


if __name__ == '__main__':
    main()
