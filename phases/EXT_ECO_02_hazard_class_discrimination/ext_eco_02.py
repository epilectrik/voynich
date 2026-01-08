"""
Phase EXT-ECO-02: Hazard Class Discrimination
Tests whether CONTAINMENT_TIMING and ENERGY_OVERSHOOT hazards
show different structural signatures than batch-focused hazards.

Hypothesis:
- Batch-focused: PHASE_ORDERING, COMPOSITION_JUMP, RATE_MISMATCH (~71%)
- Apparatus-focused: CONTAINMENT_TIMING, ENERGY_OVERSHOOT (~29%)

Tests:
1. Severity Distribution - Do apparatus hazards have higher severity?
2. LINK Proximity - Is LINK density different near apparatus hazard tokens?
3. Rapid Intervention - Do short action runs cluster near apparatus tokens?
4. Token Frequency - Are apparatus hazard tokens more/less frequent?
5. Kernel Distance - Different proximity to kernel (k, h, e)?
"""

import json
import os
import sys
from collections import defaultdict
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Hazard definitions from hazards.py
HAZARD_TRANSITIONS = {
    'PHASE_ORDERING': [
        ('shey', 'aiin', 0.9),
        ('shey', 'al', 0.8),
        ('shey', 'c', 0.7),
        ('chol', 'r', 0.8),
        ('chedy', 'ee', 0.7),
        ('chey', 'chedy', 0.6),
        ('l', 'chol', 0.7),
    ],
    'COMPOSITION_JUMP': [
        ('dy', 'aiin', 0.8),
        ('dy', 'chey', 0.7),
        ('or', 'dal', 0.8),
        ('ar', 'chol', 0.7),
    ],
    'CONTAINMENT_TIMING': [
        ('qo', 'shey', 0.9),
        ('qo', 'shy', 0.8),
        ('ok', 'shol', 0.7),
        ('ol', 'shor', 0.7),
    ],
    'RATE_MISMATCH': [
        ('dar', 'qokaiin', 0.6),
    ],
    'ENERGY_OVERSHOOT': [
        ('qokaiin', 'qokedy', 0.9),
    ],
}

# Classification
BATCH_FOCUSED = ['PHASE_ORDERING', 'COMPOSITION_JUMP', 'RATE_MISMATCH']
APPARATUS_FOCUSED = ['CONTAINMENT_TIMING', 'ENERGY_OVERSHOOT']

# LINK tokens (waiting/non-intervention) - tokens ending in -aiin, -ain, etc.
# These are the high-frequency LINK-class tokens from the grammar
LINK_TOKENS = {'daiin', 'aiin', 'okaiin', 'qokaiin', 'chkaiin', 'otaiin', 'oraiin',
               'ain', 'dain', 'chain', 'shain', 'rain', 'kain', 'taiin', 'saiin'}

# Kernel tokens
KERNEL_TOKENS = {'k', 'h', 'e', 'qo', 'ol', 'or', 'ar', 'al', 'ok', 'ot'}


def load_transcription():
    """Load the canonical transcription."""
    trans_path = project_root / 'data' / 'transcriptions' / 'interlinear_full_words.txt'

    folios = defaultdict(list)

    with open(trans_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            parts = line.split('\t')
            if len(parts) >= 2:
                folio_id = parts[0].split('.')[0] if '.' in parts[0] else parts[0]
                # Strip quotes from tokens
                raw_tokens = parts[1].split() if len(parts) > 1 else []
                tokens = [t.strip('"') for t in raw_tokens]
                folios[folio_id].extend(tokens)

    return folios


def get_hazard_tokens(hazard_classes):
    """Get all tokens involved in specified hazard classes."""
    tokens = set()
    for hclass in hazard_classes:
        for t1, t2, _ in HAZARD_TRANSITIONS.get(hclass, []):
            tokens.add(t1)
            tokens.add(t2)
    return tokens


def test_1_severity_distribution():
    """
    Test 1: Severity Distribution
    Do apparatus hazards have higher severity (more urgent)?

    Prediction:
    - Apparatus hazards: higher mean severity (immediate danger)
    - Batch hazards: lower mean severity (quality degradation)
    """
    print("  Test 1: Severity Distribution")

    batch_severities = []
    apparatus_severities = []

    for hclass in BATCH_FOCUSED:
        for _, _, sev in HAZARD_TRANSITIONS.get(hclass, []):
            batch_severities.append(sev)

    for hclass in APPARATUS_FOCUSED:
        for _, _, sev in HAZARD_TRANSITIONS.get(hclass, []):
            apparatus_severities.append(sev)

    batch_mean = sum(batch_severities) / len(batch_severities) if batch_severities else 0
    apparatus_mean = sum(apparatus_severities) / len(apparatus_severities) if apparatus_severities else 0

    # Effect size (Cohen's d approximation)
    import statistics
    if len(batch_severities) > 1 and len(apparatus_severities) > 1:
        pooled_std = statistics.stdev(batch_severities + apparatus_severities)
        effect_size = (apparatus_mean - batch_mean) / pooled_std if pooled_std > 0 else 0
    else:
        effect_size = 0

    return {
        'batch_mean_severity': round(batch_mean, 3),
        'apparatus_mean_severity': round(apparatus_mean, 3),
        'batch_count': len(batch_severities),
        'apparatus_count': len(apparatus_severities),
        'difference': round(apparatus_mean - batch_mean, 3),
        'effect_size': round(effect_size, 3),
        'apparatus_higher': apparatus_mean > batch_mean,
    }


def test_2_link_proximity(folios):
    """
    Test 2: LINK Proximity
    Is LINK density different near apparatus hazard tokens vs batch hazard tokens?

    Prediction:
    - Batch hazards: higher LINK nearby (patience protects batch)
    - Apparatus hazards: lower LINK nearby (faster response needed)
    """
    print("  Test 2: LINK Proximity")

    batch_tokens = get_hazard_tokens(BATCH_FOCUSED)
    apparatus_tokens = get_hazard_tokens(APPARATUS_FOCUSED)

    # Count LINK tokens within window of hazard tokens
    window_size = 3

    batch_link_counts = []
    apparatus_link_counts = []

    for folio_id, tokens in folios.items():
        for i, token in enumerate(tokens):
            # Get window around this token
            start = max(0, i - window_size)
            end = min(len(tokens), i + window_size + 1)
            window = tokens[start:end]

            link_count = sum(1 for t in window if t in LINK_TOKENS)

            if token in batch_tokens:
                batch_link_counts.append(link_count)
            elif token in apparatus_tokens:
                apparatus_link_counts.append(link_count)

    batch_mean = sum(batch_link_counts) / len(batch_link_counts) if batch_link_counts else 0
    apparatus_mean = sum(apparatus_link_counts) / len(apparatus_link_counts) if apparatus_link_counts else 0

    return {
        'batch_mean_link_nearby': round(batch_mean, 3),
        'apparatus_mean_link_nearby': round(apparatus_mean, 3),
        'batch_observations': len(batch_link_counts),
        'apparatus_observations': len(apparatus_link_counts),
        'difference': round(batch_mean - apparatus_mean, 3),
        'batch_higher': batch_mean > apparatus_mean,
    }


def test_3_rapid_intervention(folios):
    """
    Test 3: Rapid Intervention Patterns
    Do short action runs cluster near apparatus hazard tokens?

    Prediction:
    - Apparatus hazards: more short runs (urgent intervention)
    - Batch hazards: longer runs (gradual adjustment)
    """
    print("  Test 3: Rapid Intervention Patterns")

    batch_tokens = get_hazard_tokens(BATCH_FOCUSED)
    apparatus_tokens = get_hazard_tokens(APPARATUS_FOCUSED)

    # Find action runs (sequences without LINK tokens)
    batch_run_lengths = []
    apparatus_run_lengths = []

    for folio_id, tokens in folios.items():
        current_run = []
        near_batch = False
        near_apparatus = False

        for token in tokens:
            if token in LINK_TOKENS:
                # End of run
                if current_run:
                    run_len = len(current_run)
                    if near_batch:
                        batch_run_lengths.append(run_len)
                    if near_apparatus:
                        apparatus_run_lengths.append(run_len)
                current_run = []
                near_batch = False
                near_apparatus = False
            else:
                current_run.append(token)
                if token in batch_tokens:
                    near_batch = True
                if token in apparatus_tokens:
                    near_apparatus = True

    batch_mean = sum(batch_run_lengths) / len(batch_run_lengths) if batch_run_lengths else 0
    apparatus_mean = sum(apparatus_run_lengths) / len(apparatus_run_lengths) if apparatus_run_lengths else 0

    # Count short runs (< 3 tokens)
    batch_short = sum(1 for r in batch_run_lengths if r < 3)
    apparatus_short = sum(1 for r in apparatus_run_lengths if r < 3)

    batch_short_rate = batch_short / len(batch_run_lengths) if batch_run_lengths else 0
    apparatus_short_rate = apparatus_short / len(apparatus_run_lengths) if apparatus_run_lengths else 0

    return {
        'batch_mean_run_length': round(batch_mean, 3),
        'apparatus_mean_run_length': round(apparatus_mean, 3),
        'batch_short_run_rate': round(batch_short_rate, 3),
        'apparatus_short_run_rate': round(apparatus_short_rate, 3),
        'batch_runs': len(batch_run_lengths),
        'apparatus_runs': len(apparatus_run_lengths),
        'apparatus_shorter_runs': apparatus_mean < batch_mean,
        'apparatus_more_short_runs': apparatus_short_rate > batch_short_rate,
    }


def test_4_token_frequency(folios):
    """
    Test 4: Token Frequency
    Are apparatus hazard tokens more or less frequent in the corpus?

    Prediction:
    - Apparatus hazards: less frequent (rare emergency states)
    - Batch hazards: more frequent (routine operations)
    """
    print("  Test 4: Token Frequency")

    batch_tokens = get_hazard_tokens(BATCH_FOCUSED)
    apparatus_tokens = get_hazard_tokens(APPARATUS_FOCUSED)

    # Count occurrences
    token_counts = defaultdict(int)
    total_tokens = 0

    for folio_id, tokens in folios.items():
        for token in tokens:
            token_counts[token] += 1
            total_tokens += 1

    batch_total = sum(token_counts.get(t, 0) for t in batch_tokens)
    apparatus_total = sum(token_counts.get(t, 0) for t in apparatus_tokens)

    batch_rate = batch_total / total_tokens if total_tokens > 0 else 0
    apparatus_rate = apparatus_total / total_tokens if total_tokens > 0 else 0

    # Per-token average
    batch_per_token = batch_total / len(batch_tokens) if batch_tokens else 0
    apparatus_per_token = apparatus_total / len(apparatus_tokens) if apparatus_tokens else 0

    return {
        'batch_total_occurrences': batch_total,
        'apparatus_total_occurrences': apparatus_total,
        'batch_corpus_rate': round(batch_rate, 4),
        'apparatus_corpus_rate': round(apparatus_rate, 4),
        'batch_per_hazard_token': round(batch_per_token, 1),
        'apparatus_per_hazard_token': round(apparatus_per_token, 1),
        'total_tokens': total_tokens,
        'apparatus_rarer': apparatus_rate < batch_rate,
    }


def test_5_kernel_distance(folios):
    """
    Test 5: Kernel Distance
    Are apparatus hazard tokens closer to or further from kernel tokens?

    Prediction:
    - Apparatus hazards: closer to kernel (control-critical)
    - Batch hazards: further from kernel (processing states)
    """
    print("  Test 5: Kernel Distance")

    batch_tokens = get_hazard_tokens(BATCH_FOCUSED)
    apparatus_tokens = get_hazard_tokens(APPARATUS_FOCUSED)

    # Measure average distance to nearest kernel token
    batch_distances = []
    apparatus_distances = []

    for folio_id, tokens in folios.items():
        for i, token in enumerate(tokens):
            # Find nearest kernel token
            min_dist = float('inf')
            for j, other in enumerate(tokens):
                if other in KERNEL_TOKENS:
                    dist = abs(i - j)
                    if dist > 0 and dist < min_dist:
                        min_dist = dist

            if min_dist < float('inf'):
                if token in batch_tokens:
                    batch_distances.append(min_dist)
                elif token in apparatus_tokens:
                    apparatus_distances.append(min_dist)

    batch_mean = sum(batch_distances) / len(batch_distances) if batch_distances else 0
    apparatus_mean = sum(apparatus_distances) / len(apparatus_distances) if apparatus_distances else 0

    return {
        'batch_mean_kernel_distance': round(batch_mean, 3),
        'apparatus_mean_kernel_distance': round(apparatus_mean, 3),
        'batch_observations': len(batch_distances),
        'apparatus_observations': len(apparatus_distances),
        'difference': round(apparatus_mean - batch_mean, 3),
        'apparatus_closer': apparatus_mean < batch_mean,
    }


def evaluate_results(results):
    """
    Evaluate test results and determine verdict.
    """
    # Count how many tests support the hybrid model
    supports_hybrid = 0
    total_tests = 5

    # Test 1: Apparatus should have HIGHER severity
    if results['test_1']['apparatus_higher']:
        supports_hybrid += 1

    # Test 2: Apparatus should have LOWER LINK nearby (batch should be higher)
    if results['test_2']['batch_higher']:
        supports_hybrid += 1

    # Test 3: Apparatus should have SHORTER runs
    if results['test_3']['apparatus_shorter_runs']:
        supports_hybrid += 1

    # Test 4: Apparatus should be RARER
    if results['test_4']['apparatus_rarer']:
        supports_hybrid += 1

    # Test 5: Apparatus should be CLOSER to kernel
    if results['test_5']['apparatus_closer']:
        supports_hybrid += 1

    # Determine verdict
    if supports_hybrid >= 4:
        verdict = 'HYBRID_CONFIRMED'
        confidence = 'HIGH'
    elif supports_hybrid >= 3:
        verdict = 'HYBRID_SUPPORTED'
        confidence = 'MODERATE'
    elif supports_hybrid >= 2:
        verdict = 'AMBIGUOUS'
        confidence = 'LOW'
    else:
        verdict = 'HYBRID_REJECTED'
        confidence = 'HIGH'

    return {
        'tests_supporting_hybrid': supports_hybrid,
        'total_tests': total_tests,
        'support_rate': round(supports_hybrid / total_tests, 2),
        'verdict': verdict,
        'confidence': confidence,
    }


def generate_report(results, evaluation, output_dir):
    """Generate markdown report."""
    report = f"""# Phase EXT-ECO-02: Hazard Class Discrimination

**Status:** COMPLETE
**Date:** {datetime.now().strftime('%Y-%m-%d')}
**Tier:** 3 (External Alignment Only)

---

## Purpose

Stress test the hybrid hazard model: Do CONTAINMENT_TIMING and ENERGY_OVERSHOOT
hazards show different structural signatures than batch-focused hazards?

**Classification:**
- **Batch-Focused:** PHASE_ORDERING, COMPOSITION_JUMP, RATE_MISMATCH (12/17 = 71%)
- **Apparatus-Focused:** CONTAINMENT_TIMING, ENERGY_OVERSHOOT (5/17 = 29%)

---

## Test Results

### Test 1: Severity Distribution

| Metric | Value |
|--------|-------|
| batch_mean_severity | {results['test_1']['batch_mean_severity']} |
| apparatus_mean_severity | {results['test_1']['apparatus_mean_severity']} |
| difference | {results['test_1']['difference']} |
| effect_size | {results['test_1']['effect_size']} |

**Prediction:** Apparatus hazards should have HIGHER severity (more urgent)
**Observed:** {'Apparatus HIGHER' if results['test_1']['apparatus_higher'] else 'Batch higher or equal'}
**Supports Hybrid:** {'YES' if results['test_1']['apparatus_higher'] else 'NO'}

---

### Test 2: LINK Proximity

| Metric | Value |
|--------|-------|
| batch_mean_link_nearby | {results['test_2']['batch_mean_link_nearby']} |
| apparatus_mean_link_nearby | {results['test_2']['apparatus_mean_link_nearby']} |
| difference | {results['test_2']['difference']} |

**Prediction:** Apparatus hazards should have LOWER LINK nearby (faster response needed)
**Observed:** {'Batch higher LINK' if results['test_2']['batch_higher'] else 'Apparatus higher or equal LINK'}
**Supports Hybrid:** {'YES' if results['test_2']['batch_higher'] else 'NO'}

---

### Test 3: Rapid Intervention Patterns

| Metric | Value |
|--------|-------|
| batch_mean_run_length | {results['test_3']['batch_mean_run_length']} |
| apparatus_mean_run_length | {results['test_3']['apparatus_mean_run_length']} |
| batch_short_run_rate | {results['test_3']['batch_short_run_rate']} |
| apparatus_short_run_rate | {results['test_3']['apparatus_short_run_rate']} |

**Prediction:** Apparatus hazards should have SHORTER action runs (urgent intervention)
**Observed:** {'Apparatus SHORTER' if results['test_3']['apparatus_shorter_runs'] else 'Batch shorter or equal'}
**Supports Hybrid:** {'YES' if results['test_3']['apparatus_shorter_runs'] else 'NO'}

---

### Test 4: Token Frequency

| Metric | Value |
|--------|-------|
| batch_total_occurrences | {results['test_4']['batch_total_occurrences']} |
| apparatus_total_occurrences | {results['test_4']['apparatus_total_occurrences']} |
| batch_per_hazard_token | {results['test_4']['batch_per_hazard_token']} |
| apparatus_per_hazard_token | {results['test_4']['apparatus_per_hazard_token']} |

**Prediction:** Apparatus hazard tokens should be RARER (emergency states)
**Observed:** {'Apparatus RARER' if results['test_4']['apparatus_rarer'] else 'Apparatus more common'}
**Supports Hybrid:** {'YES' if results['test_4']['apparatus_rarer'] else 'NO'}

---

### Test 5: Kernel Distance

| Metric | Value |
|--------|-------|
| batch_mean_kernel_distance | {results['test_5']['batch_mean_kernel_distance']} |
| apparatus_mean_kernel_distance | {results['test_5']['apparatus_mean_kernel_distance']} |
| difference | {results['test_5']['difference']} |

**Prediction:** Apparatus hazard tokens should be CLOSER to kernel (control-critical)
**Observed:** {'Apparatus CLOSER' if results['test_5']['apparatus_closer'] else 'Batch closer or equal'}
**Supports Hybrid:** {'YES' if results['test_5']['apparatus_closer'] else 'NO'}

---

## Summary

| Metric | Value |
|--------|-------|
| Tests supporting hybrid | {evaluation['tests_supporting_hybrid']}/{evaluation['total_tests']} |
| Support rate | {evaluation['support_rate']} |
| **Verdict** | **{evaluation['verdict']}** |
| **Confidence** | **{evaluation['confidence']}** |

---

## Interpretation

"""

    if evaluation['verdict'] in ['HYBRID_CONFIRMED', 'HYBRID_SUPPORTED']:
        report += """The hybrid hazard model is **SUPPORTED**. CONTAINMENT_TIMING and ENERGY_OVERSHOOT
hazards show structurally distinct signatures from batch-focused hazards.

**Refined Hazard Interpretation:**

| Hazard Type | Classes | % | Primary Mode |
|-------------|---------|---|--------------|
| Batch-Focused | PHASE_ORDERING, COMPOSITION_JUMP, RATE_MISMATCH | 71% | Opportunity-loss (batch ruination) |
| Apparatus-Focused | CONTAINMENT_TIMING, ENERGY_OVERSHOOT | 29% | Equipment protection |

This tightens the interpretation by accounting for:
- The 3020 rapid intervention runs (apparatus protection responses)
- The Test F ambiguity in EXT-ECO-01 (physical-instability got STRONG there)
- Real workshop concerns (both product AND equipment matter)
"""
    elif evaluation['verdict'] == 'AMBIGUOUS':
        report += """The evidence is **AMBIGUOUS**. Some structural differences exist, but not enough
to confidently separate apparatus-focused from batch-focused hazards.

The single-mechanism model (all hazards = opportunity-loss) remains viable.
"""
    else:
        report += """The hybrid model is **REJECTED**. Apparatus hazard classes do NOT show distinct
structural signatures from batch-focused hazards.

**Interpretation:** All 17 hazards operate through the same mechanism (opportunity-loss).
CONTAINMENT_TIMING and ENERGY_OVERSHOOT encode batch quality concerns, not equipment protection.
"""

    report += """
---

## Interpretive Boundary

This analysis evaluates structural signatures only. It does NOT:
- Identify specific apparatus or equipment
- Prove any historical claim
- Modify the frozen grammar model

---

*EXT-ECO-02 COMPLETE.*
"""

    with open(output_dir / 'EXT_ECO_02_REPORT.md', 'w', encoding='utf-8') as f:
        f.write(report)


def main():
    print("Phase EXT-ECO-02: Hazard Class Discrimination")
    print("=" * 60)

    # Load data
    print("\nLoading transcription data...")
    folios = load_transcription()
    print(f"  Loaded {len(folios)} folios")

    # Run tests
    print("\nRunning discrimination tests...")
    results = {}

    results['test_1'] = test_1_severity_distribution()
    results['test_2'] = test_2_link_proximity(folios)
    results['test_3'] = test_3_rapid_intervention(folios)
    results['test_4'] = test_4_token_frequency(folios)
    results['test_5'] = test_5_kernel_distance(folios)

    # Evaluate
    print("\nEvaluating results...")
    evaluation = evaluate_results(results)

    # Output
    output_dir = Path(__file__).parent

    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)

    for test_name, test_results in results.items():
        print(f"\n{test_name}:")
        for k, v in test_results.items():
            print(f"  {k}: {v}")

    print("\n" + "=" * 60)
    print("EVALUATION")
    print("=" * 60)
    for k, v in evaluation.items():
        print(f"  {k}: {v}")

    # Save outputs
    print("\nSaving outputs...")

    full_results = {
        'metadata': {
            'phase': 'EXT-ECO-02',
            'title': 'Hazard Class Discrimination',
            'timestamp': datetime.now().isoformat(),
            'tier': 3,
        },
        'classification': {
            'batch_focused': BATCH_FOCUSED,
            'apparatus_focused': APPARATUS_FOCUSED,
        },
        'test_results': results,
        'evaluation': evaluation,
    }

    with open(output_dir / 'ext_eco_02_results.json', 'w', encoding='utf-8') as f:
        json.dump(full_results, f, indent=2)
    print(f"  Written: {output_dir / 'ext_eco_02_results.json'}")

    generate_report(results, evaluation, output_dir)
    print(f"  Written: {output_dir / 'EXT_ECO_02_REPORT.md'}")

    print("\n" + "=" * 60)
    print("EXT-ECO-02 COMPLETE")
    print("=" * 60)

    return results, evaluation


if __name__ == '__main__':
    main()
