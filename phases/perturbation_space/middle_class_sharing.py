#!/usr/bin/env python
"""
MIDDLE Material Class Sharing Analysis

Analyzes how MIDDLEs are shared across material classes (M-A/B/C/D)
to identify behavioral overlap patterns.

Key questions:
1. Which MIDDLEs are universal (all 4 classes)?
2. Which are bridging (2-3 classes)?
3. Which are exclusive (1 class)?
4. What properties characterize each sharing pattern?

Output: Apparatus-centric interpretation of MIDDLE behavioral scope.
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
OUTPUT_FILE = RESULTS_DIR / "middle_class_sharing.json"

# Prefix to material class mapping
PREFIX_TO_CLASS = {
    'ch': 'M-A',  # Mobile, Distinct (volatile)
    'qo': 'M-A',
    'sh': 'M-B',  # Mobile, Homogeneous
    'ok': 'M-B',
    'da': 'M-C',  # Stable, Distinct
    'ot': 'M-C',
    'ol': 'M-D',  # Stable, Homogeneous (baseline)
    'ct': 'M-D',
}

# Material class properties
CLASS_PROPERTIES = {
    'M-A': {'mobility': 'mobile', 'composition': 'distinct', 'hazard': 'high'},
    'M-B': {'mobility': 'mobile', 'composition': 'homogeneous', 'hazard': 'medium'},
    'M-C': {'mobility': 'stable', 'composition': 'distinct', 'hazard': 'medium'},
    'M-D': {'mobility': 'stable', 'composition': 'homogeneous', 'hazard': 'low'},
}

PREFIXES = ['ch', 'sh', 'qo', 'da', 'ok', 'ot', 'ol', 'ct']
SUFFIXES = ['y', 'dy', 'chy', 'shy', 'ain', 'aiin', 'in', 'n', 's', 'l', 'r', 'm']


def load_currier_a():
    """Load Currier A tokens."""
    import pandas as pd

    df = pd.read_csv(DATA_PATH, sep='\t', low_memory=False, na_values='NA')
    df = df[(df['language'] == 'A') &
            (df['transcriber'] == 'H') &
            (df['word'].notna()) &
            (~df['word'].str.contains(r'\*', na=False))]
    return df


def decompose_token(word):
    """Extract PREFIX, MIDDLE, SUFFIX from token."""
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


def analyze_middle_sharing(df):
    """Analyze how MIDDLEs are shared across material classes."""

    # Track MIDDLE occurrences by class and prefix
    middle_by_class = defaultdict(lambda: defaultdict(int))
    middle_by_prefix = defaultdict(lambda: defaultdict(int))
    middle_total = Counter()
    middle_suffixes = defaultdict(list)

    for _, row in df.iterrows():
        prefix, middle, suffix = decompose_token(row['word'])
        if prefix is None or middle is None:
            continue

        material_class = PREFIX_TO_CLASS[prefix]
        middle_by_class[middle][material_class] += 1
        middle_by_prefix[middle][prefix] += 1
        middle_total[middle] += 1
        middle_suffixes[middle].append(suffix)

    print(f"Total unique MIDDLEs: {len(middle_total)}")
    print(f"Total decomposed tokens: {sum(middle_total.values())}")

    # Classify MIDDLEs by sharing pattern
    sharing_patterns = {
        'universal': [],      # All 4 classes
        'tri_class': [],      # 3 classes
        'bi_class': [],       # 2 classes
        'exclusive': [],      # 1 class only
    }

    # Also track by specific class combinations
    class_combos = defaultdict(list)

    for middle, class_counts in middle_by_class.items():
        classes = set(class_counts.keys())
        n_classes = len(classes)

        combo_key = tuple(sorted(classes))
        class_combos[combo_key].append(middle)

        if n_classes == 4:
            sharing_patterns['universal'].append(middle)
        elif n_classes == 3:
            sharing_patterns['tri_class'].append(middle)
        elif n_classes == 2:
            sharing_patterns['bi_class'].append(middle)
        else:
            sharing_patterns['exclusive'].append(middle)

    return middle_by_class, middle_by_prefix, middle_total, middle_suffixes, sharing_patterns, class_combos


def analyze_sharing_properties(middle_by_class, middle_total, middle_suffixes, sharing_patterns):
    """Analyze properties of each sharing pattern group."""

    results = {}

    for pattern, middles in sharing_patterns.items():
        if not middles:
            continue

        # Frequency statistics
        freqs = [middle_total[m] for m in middles]

        # Suffix entropy (decision predictability)
        entropies = []
        for m in middles:
            suffixes = middle_suffixes[m]
            if len(suffixes) > 1:
                counts = Counter(suffixes)
                total = sum(counts.values())
                probs = [c/total for c in counts.values()]
                entropy = -sum(p * np.log2(p) for p in probs if p > 0)
                entropies.append(entropy)

        results[pattern] = {
            'count': len(middles),
            'pct_of_total': len(middles) / len(middle_total) * 100,
            'mean_frequency': np.mean(freqs),
            'median_frequency': np.median(freqs),
            'total_tokens': sum(freqs),
            'token_pct': sum(freqs) / sum(middle_total.values()) * 100,
            'mean_suffix_entropy': np.mean(entropies) if entropies else 0,
        }

    return results


def analyze_bridging_patterns(class_combos, middle_total, middle_by_class):
    """Analyze specific bridging patterns between class pairs."""

    print("\n" + "="*60)
    print("BRIDGING PATTERN ANALYSIS")
    print("="*60)

    # Focus on 2-class combinations
    bi_class_combos = {k: v for k, v in class_combos.items() if len(k) == 2}

    # Property-based groupings
    property_bridges = {
        'mobility_bridge': [],      # M-A+M-B or M-C+M-D (same mobility)
        'composition_bridge': [],   # M-A+M-C or M-B+M-D (same composition)
        'diagonal_bridge': [],      # M-A+M-D or M-B+M-C (opposite on both)
        'adjacent_bridge': [],      # Differ on one property only
    }

    for combo, middles in bi_class_combos.items():
        c1, c2 = combo
        p1 = CLASS_PROPERTIES[c1]
        p2 = CLASS_PROPERTIES[c2]

        same_mobility = p1['mobility'] == p2['mobility']
        same_composition = p1['composition'] == p2['composition']

        if same_mobility and same_composition:
            # Shouldn't happen with different classes
            pass
        elif same_mobility:
            property_bridges['mobility_bridge'].extend(middles)
        elif same_composition:
            property_bridges['composition_bridge'].extend(middles)
        elif not same_mobility and not same_composition:
            property_bridges['diagonal_bridge'].extend(middles)
        else:
            property_bridges['adjacent_bridge'].extend(middles)

    print("\nProperty-based bridging:")
    for bridge_type, middles in property_bridges.items():
        if middles:
            total_tokens = sum(middle_total[m] for m in middles)
            print(f"\n  {bridge_type}:")
            print(f"    MIDDLEs: {len(middles)}")
            print(f"    Tokens: {total_tokens}")

            # Show top examples
            sorted_middles = sorted(middles, key=lambda m: middle_total[m], reverse=True)
            print(f"    Top 5: {sorted_middles[:5]}")

    return property_bridges


def analyze_universal_middles(sharing_patterns, middle_by_class, middle_total, middle_suffixes):
    """Deep dive into universal MIDDLEs."""

    print("\n" + "="*60)
    print("UNIVERSAL MIDDLE ANALYSIS")
    print("="*60)

    universal = sharing_patterns['universal']

    if not universal:
        print("No universal MIDDLEs found.")
        return {}

    print(f"\nUniversal MIDDLEs (appear in all 4 classes): {len(universal)}")

    # Sort by frequency
    sorted_universal = sorted(universal, key=lambda m: middle_total[m], reverse=True)

    print("\nTop 15 Universal MIDDLEs:")
    print("-" * 70)
    print(f"{'MIDDLE':<12} {'Total':>8} {'M-A':>8} {'M-B':>8} {'M-C':>8} {'M-D':>8}")
    print("-" * 70)

    universal_details = []

    for middle in sorted_universal[:15]:
        classes = middle_by_class[middle]
        total = middle_total[middle]

        # Calculate class distribution evenness (entropy)
        class_counts = [classes.get(c, 0) for c in ['M-A', 'M-B', 'M-C', 'M-D']]
        class_total = sum(class_counts)
        if class_total > 0:
            probs = [c/class_total for c in class_counts]
            evenness = -sum(p * np.log2(p) for p in probs if p > 0) / 2  # Normalized by max entropy
        else:
            evenness = 0

        print(f"'{middle}'".ljust(12) +
              f"{total:>8}" +
              f"{classes.get('M-A', 0):>8}" +
              f"{classes.get('M-B', 0):>8}" +
              f"{classes.get('M-C', 0):>8}" +
              f"{classes.get('M-D', 0):>8}")

        universal_details.append({
            'middle': middle,
            'total': total,
            'by_class': dict(classes),
            'evenness': evenness,
            'top_suffixes': Counter(middle_suffixes[middle]).most_common(3),
        })

    # Analyze distribution patterns
    print("\n\nClass distribution patterns in universal MIDDLEs:")

    ma_dominant = [m for m in universal if middle_by_class[m].get('M-A', 0) > sum(middle_by_class[m].values()) * 0.4]
    md_dominant = [m for m in universal if middle_by_class[m].get('M-D', 0) > sum(middle_by_class[m].values()) * 0.4]
    balanced = [m for m in universal if m not in ma_dominant and m not in md_dominant]

    print(f"  M-A dominant (>40%): {len(ma_dominant)}")
    print(f"  M-D dominant (>40%): {len(md_dominant)}")
    print(f"  Balanced: {len(balanced)}")

    return {
        'count': len(universal),
        'details': universal_details,
        'ma_dominant': len(ma_dominant),
        'md_dominant': len(md_dominant),
        'balanced': len(balanced),
    }


def analyze_exclusive_middles(sharing_patterns, middle_by_class, middle_total):
    """Analyze class-exclusive MIDDLEs."""

    print("\n" + "="*60)
    print("EXCLUSIVE MIDDLE ANALYSIS")
    print("="*60)

    exclusive = sharing_patterns['exclusive']

    # Group by which class they're exclusive to
    exclusive_by_class = defaultdict(list)
    for middle in exclusive:
        classes = list(middle_by_class[middle].keys())
        if len(classes) == 1:
            exclusive_by_class[classes[0]].append(middle)

    print("\nExclusive MIDDLEs by material class:")

    class_stats = {}
    for mc in ['M-A', 'M-B', 'M-C', 'M-D']:
        middles = exclusive_by_class[mc]
        total_tokens = sum(middle_total[m] for m in middles)

        print(f"\n  {mc} ({CLASS_PROPERTIES[mc]['mobility']}, {CLASS_PROPERTIES[mc]['composition']}):")
        print(f"    Exclusive MIDDLEs: {len(middles)}")
        print(f"    Total tokens: {total_tokens}")

        # Top 5
        sorted_middles = sorted(middles, key=lambda m: middle_total[m], reverse=True)
        if sorted_middles:
            print(f"    Top 5: {sorted_middles[:5]}")

        class_stats[mc] = {
            'count': len(middles),
            'tokens': total_tokens,
            'top_5': sorted_middles[:5],
        }

    return class_stats


def infer_behavioral_properties(property_bridges, universal_analysis, exclusive_stats):
    """Infer what shared/exclusive MIDDLEs might represent behaviorally."""

    print("\n" + "="*60)
    print("BEHAVIORAL INFERENCE (Tier 3)")
    print("="*60)

    inferences = []

    # Universal MIDDLEs
    if universal_analysis.get('count', 0) > 0:
        print("\n## Universal MIDDLEs")
        print("These appear in ALL material classes, suggesting:")
        print("  - Material-independent apparatus states")
        print("  - Universal situational fingerprints")
        print("  - Common operating conditions regardless of material type")
        inferences.append({
            'pattern': 'universal',
            'interpretation': 'Material-independent apparatus states',
            'count': universal_analysis['count'],
        })

    # Mobility bridges
    mobility_middles = property_bridges.get('mobility_bridge', [])
    if mobility_middles:
        print(f"\n## Mobility Bridges ({len(mobility_middles)} MIDDLEs)")
        print("These appear in classes with SAME mobility:")
        print("  - M-A + M-B (both mobile)")
        print("  - M-C + M-D (both stable)")
        print("Suggests: Situations related to PHASE BEHAVIOR")
        print("  - Mobile-shared: flow, circulation, phase change")
        print("  - Stable-shared: containment, settling, accumulation")
        inferences.append({
            'pattern': 'mobility_bridge',
            'interpretation': 'Phase behavior situations',
            'count': len(mobility_middles),
        })

    # Composition bridges
    composition_middles = property_bridges.get('composition_bridge', [])
    if composition_middles:
        print(f"\n## Composition Bridges ({len(composition_middles)} MIDDLEs)")
        print("These appear in classes with SAME composition:")
        print("  - M-A + M-C (both distinct/separable)")
        print("  - M-B + M-D (both homogeneous)")
        print("Suggests: Situations related to FRACTIONATION BEHAVIOR")
        print("  - Distinct-shared: separation, contamination risk")
        print("  - Homogeneous-shared: mixing, uniformity")
        inferences.append({
            'pattern': 'composition_bridge',
            'interpretation': 'Fractionation behavior situations',
            'count': len(composition_middles),
        })

    # Diagonal bridges (opposite on both properties)
    diagonal_middles = property_bridges.get('diagonal_bridge', [])
    if diagonal_middles:
        print(f"\n## Diagonal Bridges ({len(diagonal_middles)} MIDDLEs)")
        print("These appear in classes OPPOSITE on both properties:")
        print("  - M-A + M-D (mobile/distinct vs stable/homogeneous)")
        print("  - M-B + M-C (mobile/homogeneous vs stable/distinct)")
        print("Suggests: Situations that transcend material properties")
        print("  - Pure apparatus states (not material-dependent)")
        print("  - Possibly: temperature, time, generic conditions")
        inferences.append({
            'pattern': 'diagonal_bridge',
            'interpretation': 'Property-transcendent apparatus states',
            'count': len(diagonal_middles),
        })

    # Exclusive MIDDLEs
    print("\n## Class-Exclusive MIDDLEs")
    for mc, stats in exclusive_stats.items():
        if stats['count'] > 0:
            props = CLASS_PROPERTIES[mc]
            print(f"\n  {mc}-exclusive ({stats['count']} MIDDLEs):")
            print(f"    Properties: {props['mobility']}, {props['composition']}")
            print(f"    Interpretation: Situations ONLY this material class produces")
            if mc == 'M-A':
                print("    Likely: Volatile phase behaviors, contamination scenarios")
            elif mc == 'M-B':
                print("    Likely: Flow perturbations in uniform materials")
            elif mc == 'M-C':
                print("    Likely: Separation/settling of stable distinct materials")
            elif mc == 'M-D':
                print("    Likely: Baseline/anchor states, stable reference conditions")

    return inferences


def main():
    print("="*60)
    print("MIDDLE MATERIAL CLASS SHARING ANALYSIS")
    print("="*60)

    # Load data
    print("\nLoading Currier A data...")
    df = load_currier_a()
    print(f"Loaded {len(df)} tokens")

    # Analyze sharing patterns
    (middle_by_class, middle_by_prefix, middle_total,
     middle_suffixes, sharing_patterns, class_combos) = analyze_middle_sharing(df)

    # Summary statistics
    print("\n" + "="*60)
    print("SHARING PATTERN SUMMARY")
    print("="*60)

    pattern_stats = analyze_sharing_properties(
        middle_by_class, middle_total, middle_suffixes, sharing_patterns)

    print(f"\n{'Pattern':<15} {'MIDDLEs':>10} {'%Types':>10} {'Tokens':>10} {'%Tokens':>10}")
    print("-" * 55)
    for pattern in ['universal', 'tri_class', 'bi_class', 'exclusive']:
        if pattern in pattern_stats:
            s = pattern_stats[pattern]
            print(f"{pattern:<15} {s['count']:>10} {s['pct_of_total']:>9.1f}% {s['total_tokens']:>10} {s['token_pct']:>9.1f}%")

    # Detailed analyses
    property_bridges = analyze_bridging_patterns(class_combos, middle_total, middle_by_class)
    universal_analysis = analyze_universal_middles(
        sharing_patterns, middle_by_class, middle_total, middle_suffixes)
    exclusive_stats = analyze_exclusive_middles(
        sharing_patterns, middle_by_class, middle_total)

    # Behavioral inferences
    inferences = infer_behavioral_properties(
        property_bridges, universal_analysis, exclusive_stats)

    # Build results
    results = {
        'metadata': {
            'date': '2026-01-11',
            'total_tokens': len(df),
            'unique_middles': len(middle_total),
        },
        'sharing_summary': pattern_stats,
        'universal_analysis': universal_analysis,
        'exclusive_by_class': exclusive_stats,
        'property_bridges': {k: len(v) for k, v in property_bridges.items()},
        'inferences': inferences,
    }

    # Final synthesis
    print("\n" + "="*60)
    print("SYNTHESIS")
    print("="*60)

    total_shared = (pattern_stats.get('universal', {}).get('count', 0) +
                   pattern_stats.get('tri_class', {}).get('count', 0) +
                   pattern_stats.get('bi_class', {}).get('count', 0))
    total_exclusive = pattern_stats.get('exclusive', {}).get('count', 0)

    print(f"""
MIDDLE Sharing Structure:
  - {total_shared} MIDDLEs ({total_shared/len(middle_total)*100:.1f}%) are SHARED across classes
  - {total_exclusive} MIDDLEs ({total_exclusive/len(middle_total)*100:.1f}%) are CLASS-EXCLUSIVE

Behavioral Interpretation:
  - Universal MIDDLEs = apparatus states independent of material
  - Mobility bridges = phase behavior situations
  - Composition bridges = fractionation behavior situations
  - Exclusive MIDDLEs = material-specific perturbations

This supports the apparatus-centric model: MIDDLEs encode
situational fingerprints, and their class-sharing patterns
reveal which situations depend on material properties vs
which are universal apparatus states.
""")

    # Save results
    def convert_types(obj):
        if isinstance(obj, dict):
            return {k: convert_types(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_types(i) for i in obj]
        elif isinstance(obj, (np.bool_, bool)):
            return bool(obj)
        elif isinstance(obj, (np.integer, np.floating)):
            return float(obj)
        elif isinstance(obj, tuple):
            return list(obj)
        return obj

    with open(OUTPUT_FILE, 'w') as f:
        json.dump(convert_types(results), f, indent=2)

    print(f"\nResults saved to: {OUTPUT_FILE}")

    return results


if __name__ == '__main__':
    main()
