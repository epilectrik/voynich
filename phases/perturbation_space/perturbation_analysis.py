#!/usr/bin/env python
"""
Perturbation Space Analysis Phase

Tests the hypothesis that MIDDLE frequency tier (Core vs Tail) correlates
with operational complexity in Currier B execution.

Four tests:
A. HT density vs Core/Tail - Do rare MIDDLEs require more human attention?
B. Recovery-path diversity vs tier - Do edge cases have fewer escape routes?
C. Time-to-STATE-C vs rarity - Do rare variants take longer to stabilize?
D. Synthesis - Consolidate perturbation space model

Methodology:
1. Classify MIDDLEs from Currier A into Core (top 30) and Tail
2. Find tokens in Currier B that contain these MIDDLEs (shared vocabulary)
3. Analyze B-context properties of tokens by MIDDLE tier
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
PHASE_DIR = Path("C:/git/voynich/phases/perturbation_space")
OUTPUT_FILE = RESULTS_DIR / "perturbation_space_analysis.json"

# Prefixes for decomposition
PREFIXES = ['ch', 'sh', 'qo', 'da', 'ok', 'ot', 'ol', 'ct']
SUFFIXES = ['y', 'dy', 'chy', 'shy', 'ain', 'aiin', 'in', 'n', 's', 'l', 'r', 'm']

# Known HT markers (from constraint system)
HT_MARKERS = {'s', 'f', 'p', 'cfh', 'cph', 'ckh', 'cth'}

# Kernel operators (for recovery analysis)
KERNEL_TOKENS = {'e', 'k', 'h'}


def load_data():
    """Load both Currier A and B data."""
    import pandas as pd

    df = pd.read_csv(DATA_PATH, sep='\t', low_memory=False, na_values='NA')

    # Filter valid tokens
    df = df[(df['transcriber'] == 'H') &
            (df['word'].notna()) &
            (~df['word'].str.contains(r'\*', na=False))]

    currier_a = df[df['language'] == 'A'].copy()
    currier_b = df[df['language'] == 'B'].copy()

    return currier_a, currier_b


def decompose_token(word):
    """Extract PREFIX, MIDDLE, SUFFIX from token."""
    word = str(word).lower().strip()

    # Extract prefix
    prefix = None
    for p in PREFIXES:
        if word.startswith(p):
            prefix = p
            break

    if not prefix:
        return None, None, None

    remainder = word[len(prefix):]

    # Extract suffix
    suffix = ''
    for s in sorted(SUFFIXES, key=len, reverse=True):
        if remainder.endswith(s):
            suffix = s
            remainder = remainder[:-len(s)]
            break

    return prefix, remainder, suffix


def classify_middles_from_a(currier_a):
    """Classify MIDDLEs into Core and Tail based on Currier A frequency."""
    middle_counts = Counter()

    for _, row in currier_a.iterrows():
        prefix, middle, suffix = decompose_token(row['word'])
        if prefix and middle is not None:
            middle_counts[middle] += 1

    # Sort by frequency
    sorted_middles = sorted(middle_counts.keys(),
                           key=lambda x: middle_counts[x],
                           reverse=True)

    # Core = top 30, Tail = rest
    core_middles = set(sorted_middles[:30])
    tail_middles = set(sorted_middles[30:])

    print(f"MIDDLE Classification from Currier A:")
    print(f"  Total unique MIDDLEs: {len(middle_counts)}")
    print(f"  Core (top 30): {len(core_middles)}")
    print(f"  Tail: {len(tail_middles)}")

    # Show top 10 core
    print(f"\n  Top 10 Core MIDDLEs:")
    for m in sorted_middles[:10]:
        print(f"    '{m}': {middle_counts[m]}")

    return core_middles, tail_middles, middle_counts


def find_shared_vocabulary(currier_a, currier_b):
    """Find tokens that appear in both A and B."""
    a_tokens = set(currier_a['word'].str.lower().str.strip())
    b_tokens = set(currier_b['word'].str.lower().str.strip())

    shared = a_tokens & b_tokens
    print(f"\nVocabulary overlap:")
    print(f"  A tokens: {len(a_tokens)}")
    print(f"  B tokens: {len(b_tokens)}")
    print(f"  Shared: {len(shared)} ({len(shared)/len(a_tokens)*100:.1f}% of A)")

    return shared


def has_ht_marker(token):
    """Check if token contains HT marker."""
    token = str(token).lower()
    for marker in HT_MARKERS:
        if marker in token:
            return True
    return False


def test_a_ht_density(currier_b, core_middles, tail_middles):
    """
    Test A: HT density vs Core/Tail MIDDLEs

    Question: Do rare MIDDLEs require more human attention?

    Method: For B tokens containing Core vs Tail MIDDLEs,
    compare the rate of HT markers in surrounding context.
    """
    print("\n" + "="*60)
    print("TEST A: HT DENSITY VS MIDDLE TIER")
    print("="*60)

    # Classify B tokens by MIDDLE tier
    core_tokens = []
    tail_tokens = []

    for _, row in currier_b.iterrows():
        prefix, middle, suffix = decompose_token(row['word'])
        if prefix is None or middle is None:
            continue

        token_data = {
            'word': row['word'],
            'middle': middle,
            'folio': row.get('folio', ''),
            'line': row.get('line_number', 0),
            'has_ht': has_ht_marker(row['word']),
        }

        if middle in core_middles:
            core_tokens.append(token_data)
        elif middle in tail_middles:
            tail_tokens.append(token_data)

    print(f"\nB tokens by MIDDLE tier:")
    print(f"  Core MIDDLEs: {len(core_tokens)} tokens")
    print(f"  Tail MIDDLEs: {len(tail_tokens)} tokens")

    if len(core_tokens) == 0 or len(tail_tokens) == 0:
        print("  Insufficient data for comparison")
        return {'status': 'insufficient_data'}

    # Calculate HT density
    core_ht_rate = sum(1 for t in core_tokens if t['has_ht']) / len(core_tokens)
    tail_ht_rate = sum(1 for t in tail_tokens if t['has_ht']) / len(tail_tokens)

    print(f"\nHT marker rate:")
    print(f"  Core MIDDLEs: {core_ht_rate*100:.2f}%")
    print(f"  Tail MIDDLEs: {tail_ht_rate*100:.2f}%")

    # Chi-squared test
    core_ht = sum(1 for t in core_tokens if t['has_ht'])
    core_no_ht = len(core_tokens) - core_ht
    tail_ht = sum(1 for t in tail_tokens if t['has_ht'])
    tail_no_ht = len(tail_tokens) - tail_ht

    contingency = [[core_ht, core_no_ht], [tail_ht, tail_no_ht]]

    if min(core_ht, tail_ht) >= 5:
        chi2, p_value, dof, expected = stats.chi2_contingency(contingency)
        print(f"\nChi-squared test: chi2={chi2:.2f}, p={p_value:.4f}")
    else:
        # Fisher's exact for small counts
        odds_ratio, p_value = stats.fisher_exact(contingency)
        chi2 = None
        print(f"\nFisher's exact test: p={p_value:.4f}")

    # Interpretation
    ratio = tail_ht_rate / core_ht_rate if core_ht_rate > 0 else float('inf')

    confirmed = tail_ht_rate > core_ht_rate and p_value < 0.05

    if confirmed:
        print(f"\n[OK] CONFIRMED: Tail MIDDLEs have {ratio:.2f}x higher HT density")
        print("  -> Rare variants require more human attention")
    else:
        if tail_ht_rate > core_ht_rate:
            print(f"\n[--] Pattern present but not significant (p={p_value:.3f})")
        else:
            print(f"\n[--] Pattern not observed (Core >= Tail)")

    return {
        'core_tokens': len(core_tokens),
        'tail_tokens': len(tail_tokens),
        'core_ht_rate': float(core_ht_rate),
        'tail_ht_rate': float(tail_ht_rate),
        'ratio': float(ratio),
        'p_value': float(p_value),
        'confirmed': confirmed,
    }


def test_b_recovery_diversity(currier_b, core_middles, tail_middles):
    """
    Test B: Recovery-path diversity vs MIDDLE tier

    Question: Do edge cases have fewer escape routes?

    Method: For tokens with Core vs Tail MIDDLEs,
    count diversity of following token types (recovery options).
    """
    print("\n" + "="*60)
    print("TEST B: RECOVERY-PATH DIVERSITY VS MIDDLE TIER")
    print("="*60)

    # Build transition model by folio/line
    folio_lines = defaultdict(list)

    for _, row in currier_b.iterrows():
        key = (row.get('folio', ''), row.get('line_number', 0))
        prefix, middle, suffix = decompose_token(row['word'])
        folio_lines[key].append({
            'word': str(row['word']).lower(),
            'prefix': prefix,
            'middle': middle,
            'suffix': suffix,
        })

    # Calculate following-token diversity for Core vs Tail
    core_successors = []
    tail_successors = []

    for key, tokens in folio_lines.items():
        for i, token in enumerate(tokens[:-1]):  # Skip last token
            if token['middle'] is None:
                continue

            next_token = tokens[i + 1]
            next_prefix = next_token['prefix'] or next_token['word'][:2]

            if token['middle'] in core_middles:
                core_successors.append(next_prefix)
            elif token['middle'] in tail_middles:
                tail_successors.append(next_prefix)

    print(f"\nTransition data:")
    print(f"  Core MIDDLE transitions: {len(core_successors)}")
    print(f"  Tail MIDDLE transitions: {len(tail_successors)}")

    if len(core_successors) < 50 or len(tail_successors) < 50:
        print("  Insufficient transition data")
        return {'status': 'insufficient_data'}

    # Calculate diversity (entropy of successor distribution)
    def successor_entropy(successors):
        counts = Counter(successors)
        total = sum(counts.values())
        probs = [c/total for c in counts.values()]
        return -sum(p * np.log2(p) for p in probs if p > 0)

    core_entropy = successor_entropy(core_successors)
    tail_entropy = successor_entropy(tail_successors)

    core_unique = len(set(core_successors))
    tail_unique = len(set(tail_successors))

    print(f"\nSuccessor diversity:")
    print(f"  Core: {core_unique} unique successors, entropy={core_entropy:.3f} bits")
    print(f"  Tail: {tail_unique} unique successors, entropy={tail_entropy:.3f} bits")

    # Bootstrap test for entropy difference
    combined = core_successors + tail_successors
    observed_diff = core_entropy - tail_entropy

    boot_diffs = []
    n_core = len(core_successors)
    for _ in range(1000):
        np.random.shuffle(combined)
        boot_core = combined[:n_core]
        boot_tail = combined[n_core:]
        boot_diff = successor_entropy(boot_core) - successor_entropy(boot_tail)
        boot_diffs.append(boot_diff)

    p_value = np.mean(np.array(boot_diffs) >= observed_diff)

    print(f"\nCore - Tail entropy difference: {observed_diff:.3f}")
    print(f"Bootstrap p-value: {p_value:.4f}")

    # Hypothesis: Tail has LOWER diversity (fewer escape routes)
    confirmed = tail_entropy < core_entropy and p_value < 0.05

    if confirmed:
        print(f"\n[OK] CONFIRMED: Tail MIDDLEs have fewer recovery options")
        print(f"  -> Edge cases are more constrained")
    else:
        if tail_entropy < core_entropy:
            print(f"\n[--] Pattern present but not significant (p={p_value:.3f})")
        else:
            print(f"\n[--] Pattern not observed (Tail >= Core diversity)")

    # Show top successors
    print(f"\nTop successors after Core MIDDLEs:")
    for succ, count in Counter(core_successors).most_common(5):
        print(f"  {succ}: {count} ({count/len(core_successors)*100:.1f}%)")

    print(f"\nTop successors after Tail MIDDLEs:")
    for succ, count in Counter(tail_successors).most_common(5):
        print(f"  {succ}: {count} ({count/len(tail_successors)*100:.1f}%)")

    return {
        'core_transitions': len(core_successors),
        'tail_transitions': len(tail_successors),
        'core_entropy': float(core_entropy),
        'tail_entropy': float(tail_entropy),
        'core_unique': core_unique,
        'tail_unique': tail_unique,
        'entropy_diff': float(observed_diff),
        'p_value': float(p_value),
        'confirmed': confirmed,
    }


def test_c_time_to_state_c(currier_b, core_middles, tail_middles):
    """
    Test C: Time-to-STATE-C vs MIDDLE rarity

    Question: Do rare variants take longer to stabilize?

    Method: For tokens with Core vs Tail MIDDLEs,
    measure how many tokens until reaching e-operator (stability anchor).
    """
    print("\n" + "="*60)
    print("TEST C: TIME-TO-STATE-C VS MIDDLE TIER")
    print("="*60)

    # Build line sequences
    folio_lines = defaultdict(list)

    for _, row in currier_b.iterrows():
        key = (row.get('folio', ''), row.get('line_number', 0))
        word = str(row['word']).lower()
        prefix, middle, suffix = decompose_token(word)

        # Check if token contains stability anchor
        has_e = 'e' in word and not word.startswith('e')  # e inside, not at start

        folio_lines[key].append({
            'word': word,
            'prefix': prefix,
            'middle': middle,
            'has_e': has_e,
        })

    # Calculate distance to next e-containing token
    core_distances = []
    tail_distances = []

    for key, tokens in folio_lines.items():
        for i, token in enumerate(tokens):
            if token['middle'] is None:
                continue

            # Find distance to next e-token
            distance = 0
            for j in range(i + 1, len(tokens)):
                distance += 1
                if tokens[j]['has_e']:
                    break
            else:
                # No e found in rest of line
                distance = len(tokens) - i  # Use remaining length

            if token['middle'] in core_middles:
                core_distances.append(distance)
            elif token['middle'] in tail_middles:
                tail_distances.append(distance)

    print(f"\nDistance-to-stability data:")
    print(f"  Core MIDDLE tokens: {len(core_distances)}")
    print(f"  Tail MIDDLE tokens: {len(tail_distances)}")

    if len(core_distances) < 50 or len(tail_distances) < 50:
        print("  Insufficient data")
        return {'status': 'insufficient_data'}

    core_mean = np.mean(core_distances)
    core_std = np.std(core_distances)
    tail_mean = np.mean(tail_distances)
    tail_std = np.std(tail_distances)

    print(f"\nMean distance to stability anchor:")
    print(f"  Core: {core_mean:.2f} +/- {core_std:.2f} tokens")
    print(f"  Tail: {tail_mean:.2f} +/- {tail_std:.2f} tokens")

    # Mann-Whitney U test
    stat, p_value = stats.mannwhitneyu(tail_distances, core_distances,
                                        alternative='greater')

    print(f"\nMann-Whitney U (Tail > Core): p={p_value:.4f}")

    # Hypothesis: Tail takes LONGER to stabilize
    confirmed = tail_mean > core_mean and p_value < 0.05

    if confirmed:
        ratio = tail_mean / core_mean
        print(f"\n[OK] CONFIRMED: Tail MIDDLEs take {ratio:.2f}x longer to stabilize")
        print(f"  -> Edge cases require more recovery effort")
    else:
        if tail_mean > core_mean:
            print(f"\n[--] Pattern present but not significant (p={p_value:.3f})")
        else:
            print(f"\n[--] Pattern not observed (Core >= Tail distance)")

    return {
        'core_count': len(core_distances),
        'tail_count': len(tail_distances),
        'core_mean': float(core_mean),
        'core_std': float(core_std),
        'tail_mean': float(tail_mean),
        'tail_std': float(tail_std),
        'p_value': float(p_value),
        'confirmed': confirmed,
    }


def synthesize_results(test_a, test_b, test_c, middle_counts, core_middles, tail_middles):
    """
    Synthesis: Consolidate perturbation space model.
    """
    print("\n" + "="*60)
    print("SYNTHESIS: PERTURBATION SPACE MODEL")
    print("="*60)

    confirmed_count = sum([
        test_a.get('confirmed', False),
        test_b.get('confirmed', False),
        test_c.get('confirmed', False),
    ])

    print(f"\nTests confirmed: {confirmed_count}/3")

    # Core statistics
    core_usage = sum(middle_counts[m] for m in core_middles if m in middle_counts)
    tail_usage = sum(middle_counts[m] for m in tail_middles if m in middle_counts)
    total_usage = core_usage + tail_usage

    print(f"\nMIDDLE Distribution:")
    print(f"  Core: {len(core_middles)} types, {core_usage} tokens ({core_usage/total_usage*100:.1f}%)")
    print(f"  Tail: {len(tail_middles)} types, {tail_usage} tokens ({tail_usage/total_usage*100:.1f}%)")

    synthesis = {
        'tests_confirmed': confirmed_count,
        'core_types': len(core_middles),
        'tail_types': len(tail_middles),
        'core_usage_pct': float(core_usage / total_usage) if total_usage > 0 else 0,
        'tail_usage_pct': float(tail_usage / total_usage) if total_usage > 0 else 0,
    }

    # Build interpretation
    print("\n" + "-"*60)
    print("PERTURBATION SPACE INTERPRETATION")
    print("-"*60)

    if confirmed_count >= 2:
        print("""
The MIDDLE frequency tier (Core vs Tail) correlates with operational
complexity in Currier B execution:

CORE MIDDLEs (common operating manifold):
  - Represent frequently encountered situations
  - Allow flexible recovery paths
  - Require less human attention
  - Stabilize quickly

TAIL MIDDLEs (perturbation space):
  - Represent rare edge cases
  - Have constrained recovery options
  - Trigger heightened attention (HT)
  - Require more effort to stabilize

This pattern is consistent with a physical control system where:
  - Normal operations follow well-worn paths
  - Perturbations require careful, specific handling
  - The system tightens control when rare situations arise
""")
        synthesis['interpretation'] = 'perturbation_model_supported'
        synthesis['confidence'] = 'moderate' if confirmed_count == 2 else 'high'

    else:
        print("""
The MIDDLE frequency tier shows limited correlation with B-layer
operational complexity. The Core/Tail distinction may primarily
reflect recognition frequency rather than operational difficulty.
""")
        synthesis['interpretation'] = 'perturbation_model_limited'
        synthesis['confidence'] = 'low'

    return synthesis


def main():
    print("="*60)
    print("PERTURBATION SPACE ANALYSIS PHASE")
    print("="*60)

    # Load data
    print("\nLoading data...")
    currier_a, currier_b = load_data()
    print(f"Currier A: {len(currier_a)} tokens")
    print(f"Currier B: {len(currier_b)} tokens")

    # Classify MIDDLEs from A
    core_middles, tail_middles, middle_counts = classify_middles_from_a(currier_a)

    # Check vocabulary overlap
    shared = find_shared_vocabulary(currier_a, currier_b)

    # Run tests
    results = {
        'metadata': {
            'date': '2026-01-11',
            'currier_a_tokens': len(currier_a),
            'currier_b_tokens': len(currier_b),
            'core_middles': len(core_middles),
            'tail_middles': len(tail_middles),
            'shared_vocabulary': len(shared),
        }
    }

    results['test_a_ht_density'] = test_a_ht_density(currier_b, core_middles, tail_middles)
    results['test_b_recovery'] = test_b_recovery_diversity(currier_b, core_middles, tail_middles)
    results['test_c_stability'] = test_c_time_to_state_c(currier_b, core_middles, tail_middles)
    results['synthesis'] = synthesize_results(
        results['test_a_ht_density'],
        results['test_b_recovery'],
        results['test_c_stability'],
        middle_counts,
        core_middles,
        tail_middles
    )

    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)

    tests = [
        ('A: HT Density', results['test_a_ht_density']),
        ('B: Recovery Diversity', results['test_b_recovery']),
        ('C: Time-to-STATE-C', results['test_c_stability']),
    ]

    for name, result in tests:
        if result.get('status') == 'insufficient_data':
            status = '[--] Insufficient data'
        elif result.get('confirmed'):
            status = '[OK] CONFIRMED'
        else:
            status = '[--] Not confirmed'
        print(f"  {name}: {status}")

    print(f"\nOverall: {results['synthesis']['tests_confirmed']}/3 tests confirmed")
    print(f"Interpretation: {results['synthesis']['interpretation']}")
    print(f"Confidence: {results['synthesis']['confidence']}")

    # Save results (convert numpy types)
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

    return results


if __name__ == '__main__':
    main()
