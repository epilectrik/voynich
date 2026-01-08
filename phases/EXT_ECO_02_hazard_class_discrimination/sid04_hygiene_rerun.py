"""
SID-04 Hygiene Rerun

Rerun key SID-04 metrics with explicit filtering safeguards
to see if results change dramatically.

Original SID-04 claims:
- Temporal clustering: z=127
- Section exclusivity: z=27
- Hazard avoidance: z=5.8
- Run length CV: 0.87
"""

import sys
import os
import math
import random
from collections import defaultdict, Counter
from pathlib import Path
import numpy as np
from scipy import stats

project_root = Path(__file__).parent.parent.parent

# =============================================================================
# ORIGINAL SID-04 TOKEN CLASSIFICATION (for comparison)
# =============================================================================

GRAMMAR_PREFIXES = {'qo', 'ch', 'sh', 'ok', 'da', 'ot', 'ct', 'kc', 'pc', 'fc'}
GRAMMAR_SUFFIXES = {'aiin', 'dy', 'ol', 'or', 'ar', 'ain', 'ey', 'edy', 'eey'}

FORBIDDEN_PAIRS = [
    ('shey', 'aiin'), ('shey', 'al'), ('shey', 'c'), ('chol', 'r'),
    ('chedy', 'ee'), ('chey', 'chedy'), ('l', 'chol'), ('dy', 'aiin'),
    ('dy', 'chey'), ('or', 'dal'), ('ar', 'chol'), ('qo', 'shey'),
    ('qo', 'shy'), ('ok', 'shol'), ('ol', 'shor'), ('dar', 'qokaiin'),
    ('qokaiin', 'qokedy')
]

HAZARD_TOKENS = set()
for a, b in FORBIDDEN_PAIRS:
    HAZARD_TOKENS.add(a)
    HAZARD_TOKENS.add(b)


def is_grammar_token_original(token: str) -> bool:
    """Original SID-04 classification."""
    t = token.lower()
    for pf in GRAMMAR_PREFIXES:
        if t.startswith(pf):
            return True
    for sf in GRAMMAR_SUFFIXES:
        if t.endswith(sf):
            return True
    return False


def is_grammar_token_strict(token: str) -> bool:
    """Strict classification with additional filters."""
    t = token.lower().strip()

    # Filter: empty or very short
    if len(t) < 2:
        return True  # Treat as grammar (exclude from residue)

    # Filter: contains non-alpha (transcription artifacts)
    if not t.isalpha():
        return True  # Treat as grammar (exclude from residue)

    # Filter: hazard tokens
    if t in HAZARD_TOKENS:
        return True  # Treat as grammar (exclude from residue)

    # Original classification
    for pf in GRAMMAR_PREFIXES:
        if t.startswith(pf):
            return True
    for sf in GRAMMAR_SUFFIXES:
        if t.endswith(sf):
            return True

    return False


def load_transcription():
    """Load transcription with explicit cleaning."""
    filepath = project_root / 'data' / 'transcriptions' / 'interlinear_full_words.txt'

    data = []

    with open(filepath, 'r', encoding='utf-8') as f:
        header = f.readline()
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) >= 4:
                word = parts[0].strip('"').strip()
                folio = parts[2].strip('"') if len(parts) > 2 else ''
                section = parts[3].strip('"') if len(parts) > 3 else ''

                # Skip empty or placeholder
                if word and not word.startswith('*') and word.isalpha():
                    data.append({
                        'token': word,
                        'folio': folio,
                        'section': section,
                    })

    return data


def test_temporal_clustering(data, is_grammar_func):
    """
    Test 1: Temporal Clustering
    Do residue tokens cluster (repeat consecutively) more than random?
    """
    residue_tokens = [d['token'] for d in data if not is_grammar_func(d['token'])]

    if len(residue_tokens) < 100:
        return {'z_score': 0, 'note': 'Too few residue tokens'}

    # Count consecutive repeats
    repeats = 0
    for i in range(1, len(residue_tokens)):
        if residue_tokens[i] == residue_tokens[i-1]:
            repeats += 1

    observed_rate = repeats / (len(residue_tokens) - 1)

    # Expected under random (based on vocabulary size)
    vocab = Counter(residue_tokens)
    expected_rate = sum((c/len(residue_tokens))**2 for c in vocab.values())

    # Z-score (approximation)
    n = len(residue_tokens) - 1
    std = math.sqrt(expected_rate * (1 - expected_rate) / n)
    z = (observed_rate - expected_rate) / std if std > 0 else 0

    return {
        'observed_rate': round(observed_rate, 4),
        'expected_rate': round(expected_rate, 4),
        'z_score': round(z, 1),
        'residue_count': len(residue_tokens),
    }


def test_section_exclusivity(data, is_grammar_func):
    """
    Test 2: Section Exclusivity
    Do residue tokens appear in only one section?
    """
    residue_by_section = defaultdict(set)

    for d in data:
        if not is_grammar_func(d['token']):
            residue_by_section[d['section']].add(d['token'])

    if len(residue_by_section) < 2:
        return {'z_score': 0, 'note': 'Too few sections'}

    # All unique residue tokens
    all_residue = set()
    for tokens in residue_by_section.values():
        all_residue.update(tokens)

    # Count tokens exclusive to one section
    exclusive = 0
    for token in all_residue:
        sections_with_token = sum(1 for s, tokens in residue_by_section.items() if token in tokens)
        if sections_with_token == 1:
            exclusive += 1

    exclusivity_rate = exclusive / len(all_residue) if all_residue else 0

    # Expected under random (rough approximation)
    n_sections = len(residue_by_section)
    expected_exclusive = (1/n_sections) ** (n_sections - 1)  # Very rough

    return {
        'exclusive_tokens': exclusive,
        'total_residue_types': len(all_residue),
        'exclusivity_rate': round(exclusivity_rate, 3),
        'n_sections': n_sections,
    }


def test_hazard_avoidance(data, is_grammar_func):
    """
    Test 3: Hazard Avoidance
    Do residue tokens appear further from hazard tokens than expected?
    """
    tokens = [d['token'] for d in data]

    # Find hazard positions
    hazard_positions = [i for i, t in enumerate(tokens) if t in HAZARD_TOKENS]

    if not hazard_positions:
        return {'z_score': 0, 'note': 'No hazard tokens found'}

    # Find residue positions
    residue_positions = [i for i, t in enumerate(tokens) if not is_grammar_func(t)]

    if not residue_positions:
        return {'z_score': 0, 'note': 'No residue tokens found'}

    # Calculate distances from each residue to nearest hazard
    distances = []
    for rp in residue_positions:
        min_dist = min(abs(rp - hp) for hp in hazard_positions)
        distances.append(min_dist)

    observed_mean = np.mean(distances)

    # Expected under random placement
    n = len(tokens)
    n_hazards = len(hazard_positions)
    expected_mean = n / (n_hazards + 1) / 2  # Rough approximation

    # Bootstrap for z-score
    random.seed(42)
    null_means = []
    for _ in range(1000):
        random_positions = random.sample(range(n), len(residue_positions))
        null_dists = [min(abs(rp - hp) for hp in hazard_positions) for rp in random_positions]
        null_means.append(np.mean(null_dists))

    z = (observed_mean - np.mean(null_means)) / np.std(null_means) if np.std(null_means) > 0 else 0

    return {
        'observed_mean_distance': round(observed_mean, 2),
        'null_mean_distance': round(np.mean(null_means), 2),
        'z_score': round(z, 1),
        'residue_count': len(residue_positions),
        'hazard_count': len(hazard_positions),
    }


def test_run_length_cv(data, is_grammar_func):
    """
    Test 4: Run Length Coefficient of Variation
    Do residue runs have geometric-like (memoryless) length distribution?
    """
    tokens = [d['token'] for d in data]

    # Find residue runs
    runs = []
    current_run = 0

    for t in tokens:
        if not is_grammar_func(t):
            current_run += 1
        else:
            if current_run > 0:
                runs.append(current_run)
            current_run = 0

    if current_run > 0:
        runs.append(current_run)

    if len(runs) < 10:
        return {'cv': 0, 'note': 'Too few runs'}

    mean_run = np.mean(runs)
    std_run = np.std(runs)
    cv = std_run / mean_run if mean_run > 0 else 0

    # Geometric distribution has CV = sqrt(1-p)/p ≈ 1 for small p

    return {
        'mean_run_length': round(mean_run, 2),
        'std_run_length': round(std_run, 2),
        'cv': round(cv, 2),
        'n_runs': len(runs),
        'geometric_expected_cv': '~1.0',
    }


def main():
    print("SID-04 Hygiene Rerun")
    print("=" * 60)

    # Load data
    print("\nLoading transcription...")
    data = load_transcription()
    print(f"  Loaded {len(data)} tokens")

    # Run with ORIGINAL classification
    print("\n" + "=" * 60)
    print("ORIGINAL CLASSIFICATION (SID-04 method)")
    print("=" * 60)

    residue_orig = [d for d in data if not is_grammar_token_original(d['token'])]
    print(f"Residue tokens: {len(residue_orig)}")

    t1_orig = test_temporal_clustering(data, is_grammar_token_original)
    t2_orig = test_section_exclusivity(data, is_grammar_token_original)
    t3_orig = test_hazard_avoidance(data, is_grammar_token_original)
    t4_orig = test_run_length_cv(data, is_grammar_token_original)

    print(f"\nTest 1 - Temporal Clustering:")
    for k, v in t1_orig.items():
        print(f"  {k}: {v}")

    print(f"\nTest 2 - Section Exclusivity:")
    for k, v in t2_orig.items():
        print(f"  {k}: {v}")

    print(f"\nTest 3 - Hazard Avoidance:")
    for k, v in t3_orig.items():
        print(f"  {k}: {v}")

    print(f"\nTest 4 - Run Length CV:")
    for k, v in t4_orig.items():
        print(f"  {k}: {v}")

    # Run with STRICT classification
    print("\n" + "=" * 60)
    print("STRICT CLASSIFICATION (with hygiene filters)")
    print("=" * 60)

    residue_strict = [d for d in data if not is_grammar_token_strict(d['token'])]
    print(f"Residue tokens: {len(residue_strict)}")

    t1_strict = test_temporal_clustering(data, is_grammar_token_strict)
    t2_strict = test_section_exclusivity(data, is_grammar_token_strict)
    t3_strict = test_hazard_avoidance(data, is_grammar_token_strict)
    t4_strict = test_run_length_cv(data, is_grammar_token_strict)

    print(f"\nTest 1 - Temporal Clustering:")
    for k, v in t1_strict.items():
        print(f"  {k}: {v}")

    print(f"\nTest 2 - Section Exclusivity:")
    for k, v in t2_strict.items():
        print(f"  {k}: {v}")

    print(f"\nTest 3 - Hazard Avoidance:")
    for k, v in t3_strict.items():
        print(f"  {k}: {v}")

    print(f"\nTest 4 - Run Length CV:")
    for k, v in t4_strict.items():
        print(f"  {k}: {v}")

    # Comparison
    print("\n" + "=" * 60)
    print("COMPARISON: Original vs Strict")
    print("=" * 60)

    print(f"""
| Metric                | Original | Strict | Change |
|-----------------------|----------|--------|--------|
| Residue count         | {len(residue_orig):,} | {len(residue_strict):,} | {len(residue_strict) - len(residue_orig):+,} |
| Temporal clustering z | {t1_orig.get('z_score', 'N/A')} | {t1_strict.get('z_score', 'N/A')} | {t1_strict.get('z_score', 0) - t1_orig.get('z_score', 0):+.1f} |
| Section exclusivity   | {t2_orig.get('exclusivity_rate', 'N/A')} | {t2_strict.get('exclusivity_rate', 'N/A')} | {(t2_strict.get('exclusivity_rate', 0) - t2_orig.get('exclusivity_rate', 0))*100:+.1f}% |
| Hazard avoidance z    | {t3_orig.get('z_score', 'N/A')} | {t3_strict.get('z_score', 'N/A')} | {t3_strict.get('z_score', 0) - t3_orig.get('z_score', 0):+.1f} |
| Run length CV         | {t4_orig.get('cv', 'N/A')} | {t4_strict.get('cv', 'N/A')} | {t4_strict.get('cv', 0) - t4_orig.get('cv', 0):+.2f} |
""")

    # Verdict
    print("=" * 60)
    print("VERDICT")
    print("=" * 60)

    # Check if any metric changed by more than 50%
    changes = []

    if t1_orig.get('z_score', 0) > 0:
        pct = abs(t1_strict.get('z_score', 0) - t1_orig.get('z_score', 0)) / t1_orig.get('z_score', 1) * 100
        changes.append(('Temporal clustering', pct))

    if t3_orig.get('z_score', 0) > 0:
        pct = abs(t3_strict.get('z_score', 0) - t3_orig.get('z_score', 0)) / t3_orig.get('z_score', 1) * 100
        changes.append(('Hazard avoidance', pct))

    if t4_orig.get('cv', 0) > 0:
        pct = abs(t4_strict.get('cv', 0) - t4_orig.get('cv', 0)) / t4_orig.get('cv', 1) * 100
        changes.append(('Run length CV', pct))

    max_change = max(changes, key=lambda x: x[1]) if changes else ('N/A', 0)

    if max_change[1] < 20:
        print(f"\n** RESULTS STABLE ** (max change: {max_change[0]} at {max_change[1]:.1f}%)")
        print("SID-04 findings are ROBUST to hygiene filtering.")
    elif max_change[1] < 50:
        print(f"\n** MINOR CHANGES ** (max change: {max_change[0]} at {max_change[1]:.1f}%)")
        print("SID-04 findings are MOSTLY stable, minor recalibration may be warranted.")
    else:
        print(f"\n** SIGNIFICANT CHANGES ** (max change: {max_change[0]} at {max_change[1]:.1f}%)")
        print("SID-04 findings AFFECTED by token filtering. Full audit recommended.")


if __name__ == '__main__':
    main()
