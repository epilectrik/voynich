#!/usr/bin/env python3
"""
TEMPORAL COVERAGE TRAJECTORIES
Push #5: Is Currier A static-optimal or dynamically scheduled?

Tests whether the manuscript manages WHEN coverage occurs, not just THAT it occurs.

Three mutually exclusive models:
- Model A (Static-Optimal): Order doesn't matter, any permutation equally good
- Model B (Weak Temporal): Soft pedagogy, some front-loading but uniform tails
- Model C (Strong Scheduling): Active trajectory planning with phases

Four signals measured:
1. Cumulative Coverage Curve
2. Marginal Novelty Rate
3. Tail-Pressure Trajectory
4. Prefix Regime Cycling
"""

import csv
import json
import random
import statistics
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict, List, Tuple, Set, Optional
import math

# Paths
BASE_PATH = Path(__file__).parent.parent.parent
DATA_FILE = BASE_PATH / "data" / "transcriptions" / "interlinear_full_words.txt"

# PREFIX definitions
PREFIXES = ['ch', 'qo', 'sh', 'da', 'ok', 'ot', 'ct', 'ol']
SUFFIXES = [
    'aiin', 'aiiin', 'ain', 'iin', 'in',
    'ar', 'or', 'al', 'ol', 'am', 'an',
    'dy', 'edy', 'eedy', 'chy', 'shy', 'ty', 'ky', 'ly', 'ry', 'y',
    'r', 'l', 's', 'd', 'n', 'm'
]

# AZC folios (Currier A entries)
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

    # Extract prefix (longest match)
    for p in sorted(PREFIXES, key=len, reverse=True):
        if token.startswith(p):
            prefix = p
            rest = token[len(p):]
            break

    middle = rest
    suffix = None

    # Extract suffix (longest match)
    for s in sorted(SUFFIXES, key=len, reverse=True):
        if rest.endswith(s) and len(rest) > len(s):
            suffix = s
            middle = rest[:-len(s)]
            break

    if not middle:
        middle = None

    return prefix, middle, suffix


def load_currier_a_entries() -> List[Dict]:
    """Load all Currier A entries in manuscript order."""
    entries = []
    entry_index = 0

    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            word = row.get('"word"', row.get('word', '')).strip().strip('"')
            folio = row.get('"folio"', row.get('folio', '')).strip().strip('"')
            line_num = row.get('"line_number"', row.get('line_number', '')).strip().strip('"')

            # Filter to AZC folios only
            if folio not in ALL_AZC_FOLIOS:
                continue

            prefix, middle, suffix = decompose_token(word)
            if middle:  # Only entries with valid MIDDLE
                entries.append({
                    'index': entry_index,
                    'folio': folio,
                    'line': line_num,
                    'word': word,
                    'prefix': prefix or '',
                    'middle': middle,
                    'suffix': suffix or ''
                })
                entry_index += 1

    return entries


def compute_middle_frequencies(entries: List[Dict]) -> Dict[str, int]:
    """Compute frequency of each MIDDLE."""
    freq = Counter(e['middle'] for e in entries)
    return dict(freq)


def compute_cumulative_coverage(entries: List[Dict], all_middles: Set[str]) -> List[float]:
    """Compute cumulative coverage curve."""
    seen = set()
    coverage = []
    total = len(all_middles)

    for entry in entries:
        seen.add(entry['middle'])
        coverage.append(len(seen) / total)

    return coverage


def compute_marginal_novelty(entries: List[Dict]) -> List[int]:
    """Compute marginal novelty (new MIDDLEs per entry)."""
    seen = set()
    novelty = []

    for entry in entries:
        m = entry['middle']
        if m not in seen:
            novelty.append(1)
            seen.add(m)
        else:
            novelty.append(0)

    return novelty


def rolling_mean(data: List[float], window: int) -> List[float]:
    """Compute rolling mean."""
    result = []
    for i in range(len(data)):
        start = max(0, i - window // 2)
        end = min(len(data), i + window // 2 + 1)
        result.append(sum(data[start:end]) / (end - start))
    return result


def compute_tail_pressure(entries: List[Dict], middle_freq: Dict[str, int],
                          percentile: float = 25) -> List[float]:
    """Compute rolling tail pressure (fraction of rare MIDDLEs)."""
    # Define "rare" as bottom percentile
    sorted_freq = sorted(middle_freq.values())
    threshold = sorted_freq[int(len(sorted_freq) * percentile / 100)]

    rare_middles = {m for m, f in middle_freq.items() if f <= threshold}

    # Rolling window fraction
    window = 50
    tail_pressure = []

    for i in range(len(entries)):
        start = max(0, i - window // 2)
        end = min(len(entries), i + window // 2 + 1)
        window_entries = entries[start:end]

        rare_count = sum(1 for e in window_entries if e['middle'] in rare_middles)
        tail_pressure.append(rare_count / len(window_entries))

    return tail_pressure


def compute_prefix_entropy(entries: List[Dict], window: int = 50) -> List[float]:
    """Compute rolling entropy of PREFIX distribution."""
    entropy_series = []

    for i in range(len(entries)):
        start = max(0, i - window // 2)
        end = min(len(entries), i + window // 2 + 1)
        window_entries = entries[start:end]

        # Count prefixes (including empty)
        prefix_counts = Counter(e['prefix'] for e in window_entries)
        total = sum(prefix_counts.values())

        # Shannon entropy
        entropy = 0
        for count in prefix_counts.values():
            if count > 0:
                p = count / total
                entropy -= p * math.log2(p)

        entropy_series.append(entropy)

    return entropy_series


def compute_dominant_prefix_runs(entries: List[Dict], window: int = 30) -> List[Tuple[str, int]]:
    """Identify runs of dominant prefix."""
    runs = []
    current_dominant = None
    current_length = 0

    for i in range(0, len(entries), window):
        window_entries = entries[i:i+window]
        prefix_counts = Counter(e['prefix'] for e in window_entries if e['prefix'])

        if prefix_counts:
            dominant = prefix_counts.most_common(1)[0][0]
        else:
            dominant = 'NONE'

        if dominant == current_dominant:
            current_length += 1
        else:
            if current_dominant is not None:
                runs.append((current_dominant, current_length))
            current_dominant = dominant
            current_length = 1

    if current_dominant is not None:
        runs.append((current_dominant, current_length))

    return runs


def generate_random_permutation_coverage(entries: List[Dict], all_middles: Set[str],
                                         n_trials: int = 100) -> Dict:
    """Generate coverage curves from random permutations."""
    coverages = []

    for _ in range(n_trials):
        shuffled = entries.copy()
        random.shuffle(shuffled)
        cov = compute_cumulative_coverage(shuffled, all_middles)
        coverages.append(cov)

    # Compute mean and std at each position
    n = len(entries)
    mean_cov = []
    std_cov = []

    for i in range(n):
        values = [cov[i] for cov in coverages]
        mean_cov.append(statistics.mean(values))
        std_cov.append(statistics.stdev(values) if len(values) > 1 else 0)

    return {'mean': mean_cov, 'std': std_cov}


def generate_greedy_coverage(entries: List[Dict], all_middles: Set[str]) -> List[float]:
    """Generate greedy-optimal coverage curve (always pick novel MIDDLE first)."""
    # Sort by whether MIDDLE is novel at that point
    seen = set()
    sorted_entries = []
    remaining = entries.copy()

    while remaining:
        # Find entries with novel MIDDLEs
        novel = [e for e in remaining if e['middle'] not in seen]

        if novel:
            # Pick first novel entry
            entry = novel[0]
        else:
            # No more novel, pick any
            entry = remaining[0]

        sorted_entries.append(entry)
        seen.add(entry['middle'])
        remaining.remove(entry)

    return compute_cumulative_coverage(sorted_entries, all_middles)


def analyze_coverage_timing(real_cov: List[float], random_cov: Dict,
                           greedy_cov: List[float]) -> Dict:
    """Analyze when coverage milestones are reached."""
    milestones = [0.25, 0.50, 0.75, 0.90, 0.95, 1.0]
    results = {}

    for milestone in milestones:
        # Real
        real_idx = next((i for i, c in enumerate(real_cov) if c >= milestone), len(real_cov))

        # Random mean
        random_idx = next((i for i, c in enumerate(random_cov['mean']) if c >= milestone), len(random_cov['mean']))

        # Greedy
        greedy_idx = next((i for i, c in enumerate(greedy_cov) if c >= milestone), len(greedy_cov))

        n = len(real_cov)
        results[f'{int(milestone*100)}pct'] = {
            'real_pct': real_idx / n,
            'random_pct': random_idx / n,
            'greedy_pct': greedy_idx / n,
            'real_vs_random': (real_idx - random_idx) / n,  # negative = faster
            'real_vs_greedy': (real_idx - greedy_idx) / n
        }

    return results


def analyze_novelty_phases(novelty: List[int], n_phases: int = 3) -> Dict:
    """Analyze novelty rate by phases."""
    phase_size = len(novelty) // n_phases
    phases = {}

    for i in range(n_phases):
        start = i * phase_size
        end = (i + 1) * phase_size if i < n_phases - 1 else len(novelty)
        phase_novelty = novelty[start:end]

        phases[f'phase_{i+1}'] = {
            'total_novel': sum(phase_novelty),
            'rate': sum(phase_novelty) / len(phase_novelty),
            'entries': len(phase_novelty)
        }

    return phases


def analyze_tail_pressure_phases(tail_pressure: List[float], n_phases: int = 3) -> Dict:
    """Analyze tail pressure by phases."""
    phase_size = len(tail_pressure) // n_phases
    phases = {}

    for i in range(n_phases):
        start = i * phase_size
        end = (i + 1) * phase_size if i < n_phases - 1 else len(tail_pressure)
        phase_tp = tail_pressure[start:end]

        phases[f'phase_{i+1}'] = {
            'mean': statistics.mean(phase_tp),
            'std': statistics.stdev(phase_tp) if len(phase_tp) > 1 else 0,
            'max': max(phase_tp),
            'min': min(phase_tp)
        }

    return phases


def analyze_prefix_cycling(entropy_series: List[float], runs: List[Tuple[str, int]]) -> Dict:
    """Analyze prefix regime patterns."""
    # Entropy statistics
    third = len(entropy_series) // 3
    entropy_by_third = {
        'first': statistics.mean(entropy_series[:third]),
        'middle': statistics.mean(entropy_series[third:2*third]),
        'last': statistics.mean(entropy_series[2*third:])
    }

    # Run analysis
    run_lengths = [r[1] for r in runs]
    prefix_sequence = [r[0] for r in runs]

    # Check for cycling vs blocks
    unique_prefixes = set(prefix_sequence)
    prefix_appearances = {p: prefix_sequence.count(p) for p in unique_prefixes}

    return {
        'entropy_by_third': entropy_by_third,
        'mean_run_length': statistics.mean(run_lengths) if run_lengths else 0,
        'max_run_length': max(run_lengths) if run_lengths else 0,
        'n_regime_changes': len(runs),
        'prefix_appearances': prefix_appearances,
        'is_cycling': any(v > 1 for v in prefix_appearances.values()),
        'dominant_prefixes': [p for p, v in prefix_appearances.items() if v >= 2]
    }


def determine_verdict(coverage_timing: Dict, novelty_phases: Dict,
                     tail_phases: Dict, prefix_analysis: Dict) -> Dict:
    """Determine which model fits the data."""
    evidence = {
        'static_optimal': [],
        'weak_temporal': [],
        'strong_scheduling': []
    }

    # Coverage timing analysis
    cov_90 = coverage_timing.get('90pct', {})
    real_vs_random = cov_90.get('real_vs_random', 0)

    if abs(real_vs_random) < 0.03:
        evidence['static_optimal'].append('Coverage timing matches random')
    elif real_vs_random > 0.05:
        # SLOWER than random = deliberate back-loading
        evidence['strong_scheduling'].append(f'Coverage BACK-LOADED: 90% reached {real_vs_random*100:.1f}% later than random')
    elif real_vs_random < -0.05:
        evidence['strong_scheduling'].append(f'Coverage FRONT-LOADED: 90% reached {abs(real_vs_random)*100:.1f}% faster than random')
    else:
        evidence['weak_temporal'].append(f'Coverage timing near random')

    # Novelty phase analysis
    phase_1_rate = novelty_phases['phase_1']['rate']
    phase_2_rate = novelty_phases['phase_2']['rate']
    phase_3_rate = novelty_phases['phase_3']['rate']

    if abs(phase_1_rate - phase_3_rate) < 0.02:
        evidence['static_optimal'].append('Uniform novelty rate across phases')
    elif phase_1_rate > phase_3_rate * 1.5:
        evidence['strong_scheduling'].append(f'FRONT-LOADED novelty: Phase 1 ({phase_1_rate:.3f}) >> Phase 3 ({phase_3_rate:.3f})')
        # Check for novelty trough
        if phase_2_rate < min(phase_1_rate, phase_3_rate) * 0.8:
            evidence['strong_scheduling'].append(f'NOVELTY TROUGH in Phase 2 ({phase_2_rate:.3f})')
    else:
        evidence['weak_temporal'].append('Mild novelty gradient')

    # Tail pressure analysis - check for U-shape
    tp_1 = tail_phases['phase_1']['mean']
    tp_2 = tail_phases['phase_2']['mean']
    tp_3 = tail_phases['phase_3']['mean']

    # U-shaped pattern detection
    if tp_2 < tp_1 * 0.7 and tp_2 < tp_3 * 0.7:
        evidence['strong_scheduling'].append(f'U-SHAPED tail pressure: {tp_1:.3f} -> {tp_2:.3f} -> {tp_3:.3f}')
    elif abs(tp_1 - tp_3) < 0.015:
        evidence['static_optimal'].append('Uniform tail pressure endpoints')
    elif tp_3 > tp_1 * 1.3:
        evidence['strong_scheduling'].append(f'Back-loaded tail pressure ({tp_1:.3f} -> {tp_3:.3f})')
    elif tp_1 > tp_3 * 1.3:
        evidence['strong_scheduling'].append(f'Front-loaded tail pressure ({tp_1:.3f} -> {tp_3:.3f})')
    else:
        evidence['weak_temporal'].append('Mild tail pressure gradient')

    # Prefix cycling analysis
    if prefix_analysis['is_cycling']:
        n_cycling = len(prefix_analysis['dominant_prefixes'])
        evidence['strong_scheduling'].append(f'PREFIX CYCLING: {n_cycling} prefixes cycle across manuscript')
    elif prefix_analysis['max_run_length'] > 5:
        evidence['weak_temporal'].append(f'Prefix blocks detected (max run: {prefix_analysis["max_run_length"]})')
    else:
        evidence['static_optimal'].append('No clear prefix structure')

    # Entropy gradient
    ent = prefix_analysis['entropy_by_third']
    ent_range = max(ent.values()) - min(ent.values())
    if ent_range > 0.15:
        if ent['first'] < ent['middle']:
            evidence['strong_scheduling'].append(f'Prefix diversity INCREASES then stabilizes')

    # Derive interpretation
    interpretation = None
    if (real_vs_random > 0.05 and  # Slow coverage
        phase_1_rate > phase_3_rate * 1.5 and  # Front-loaded novelty
        prefix_analysis['is_cycling']):  # Prefix cycling
        interpretation = "PEDAGOGICAL_PACING: Introduce early, reinforce throughout, cycle domains"

    # Verdict
    scores = {k: len(v) for k, v in evidence.items()}
    winner = max(scores, key=scores.get)

    return {
        'verdict': winner.upper().replace('_', '-'),
        'scores': scores,
        'evidence': evidence,
        'confidence': scores[winner] / sum(scores.values()) if sum(scores.values()) > 0 else 0,
        'interpretation': interpretation
    }


def main():
    print("=" * 60)
    print("TEMPORAL COVERAGE TRAJECTORIES")
    print("Push #5: Static-optimal or dynamically scheduled?")
    print("=" * 60)

    # Load data
    print("\n[1/5] Loading Currier A entries in manuscript order...")
    entries = load_currier_a_entries()
    print(f"  Loaded {len(entries)} entries")

    # Get all MIDDLEs and frequencies
    middle_freq = compute_middle_frequencies(entries)
    all_middles = set(middle_freq.keys())
    print(f"  {len(all_middles)} unique MIDDLEs")

    # Signal 1: Cumulative Coverage
    print("\n[2/5] Computing cumulative coverage curves...")
    real_coverage = compute_cumulative_coverage(entries, all_middles)
    random_coverage = generate_random_permutation_coverage(entries, all_middles, n_trials=100)
    greedy_coverage = generate_greedy_coverage(entries, all_middles)

    coverage_timing = analyze_coverage_timing(real_coverage, random_coverage, greedy_coverage)

    print(f"  Coverage at 50%: Real={coverage_timing['50pct']['real_pct']*100:.1f}%, "
          f"Random={coverage_timing['50pct']['random_pct']*100:.1f}%, "
          f"Greedy={coverage_timing['50pct']['greedy_pct']*100:.1f}%")
    print(f"  Coverage at 90%: Real={coverage_timing['90pct']['real_pct']*100:.1f}%, "
          f"Random={coverage_timing['90pct']['random_pct']*100:.1f}%, "
          f"Greedy={coverage_timing['90pct']['greedy_pct']*100:.1f}%")

    # Signal 2: Marginal Novelty
    print("\n[3/5] Computing marginal novelty rate...")
    novelty = compute_marginal_novelty(entries)
    novelty_rolling = rolling_mean([float(n) for n in novelty], window=100)
    novelty_phases = analyze_novelty_phases(novelty, n_phases=3)

    print(f"  Phase 1 novelty rate: {novelty_phases['phase_1']['rate']:.4f}")
    print(f"  Phase 2 novelty rate: {novelty_phases['phase_2']['rate']:.4f}")
    print(f"  Phase 3 novelty rate: {novelty_phases['phase_3']['rate']:.4f}")

    # Signal 3: Tail Pressure
    print("\n[4/5] Computing tail pressure trajectory...")
    tail_pressure = compute_tail_pressure(entries, middle_freq, percentile=25)
    tail_phases = analyze_tail_pressure_phases(tail_pressure, n_phases=3)

    print(f"  Phase 1 tail pressure: {tail_phases['phase_1']['mean']:.4f}")
    print(f"  Phase 2 tail pressure: {tail_phases['phase_2']['mean']:.4f}")
    print(f"  Phase 3 tail pressure: {tail_phases['phase_3']['mean']:.4f}")

    # Signal 4: Prefix Regime Cycling
    print("\n[5/5] Analyzing prefix regime patterns...")
    entropy_series = compute_prefix_entropy(entries, window=50)
    prefix_runs = compute_dominant_prefix_runs(entries, window=30)
    prefix_analysis = analyze_prefix_cycling(entropy_series, prefix_runs)

    print(f"  Entropy by thirds: first={prefix_analysis['entropy_by_third']['first']:.3f}, "
          f"middle={prefix_analysis['entropy_by_third']['middle']:.3f}, "
          f"last={prefix_analysis['entropy_by_third']['last']:.3f}")
    print(f"  Prefix cycling: {prefix_analysis['is_cycling']}")
    print(f"  Regime changes: {prefix_analysis['n_regime_changes']}")

    # Determine verdict
    verdict = determine_verdict(coverage_timing, novelty_phases, tail_phases, prefix_analysis)

    print("\n" + "=" * 60)
    print("VERDICT")
    print("=" * 60)
    print(f"\n  Model: {verdict['verdict']}")
    print(f"  Confidence: {verdict['confidence']:.1%}")
    if verdict.get('interpretation'):
        print(f"  Interpretation: {verdict['interpretation']}")
    print(f"\n  Evidence scores:")
    for model, score in verdict['scores'].items():
        print(f"    {model}: {score}")
    print(f"\n  Key evidence for {verdict['verdict']}:")
    for ev in verdict['evidence'][verdict['verdict'].lower().replace('-', '_')]:
        print(f"    - {ev}")

    # Build output
    results = {
        'probe_id': 'TEMPORAL_COVERAGE_TRAJECTORIES',
        'question': 'Is Currier A static-optimal or dynamically scheduled?',
        'configuration': {
            'n_entries': len(entries),
            'n_middles': len(all_middles),
            'n_random_trials': 100,
            'novelty_window': 100,
            'tail_percentile': 25,
            'prefix_window': 50
        },
        'signal_1_coverage': {
            'description': 'When are coverage milestones reached?',
            'timing': coverage_timing,
            'diagnostic': 'Earlier than random = front-loaded, later = back-loaded'
        },
        'signal_2_novelty': {
            'description': 'How does novelty rate change over manuscript?',
            'phases': novelty_phases,
            'total_novel': sum(novelty),
            'diagnostic': 'Spikes early/mid/late? Bursts or droughts?'
        },
        'signal_3_tail_pressure': {
            'description': 'When are rare MIDDLEs introduced?',
            'phases': tail_phases,
            'overall_mean': statistics.mean(tail_pressure),
            'diagnostic': 'Front-loaded = early difficulty, back-loaded = escalation'
        },
        'signal_4_prefix': {
            'description': 'How do prefix regimes evolve?',
            'entropy_by_third': prefix_analysis['entropy_by_third'],
            'is_cycling': prefix_analysis['is_cycling'],
            'n_regime_changes': prefix_analysis['n_regime_changes'],
            'mean_run_length': prefix_analysis['mean_run_length'],
            'dominant_prefixes': prefix_analysis['dominant_prefixes'],
            'diagnostic': 'Blocks = cognitive load min, cycling = multi-axis traversal'
        },
        'verdict': verdict
    }

    # Save results
    output_file = Path(__file__).parent.parent.parent / 'results' / 'temporal_coverage_trajectories.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to: {output_file}")

    return results


if __name__ == '__main__':
    main()
