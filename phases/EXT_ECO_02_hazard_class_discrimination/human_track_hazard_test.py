"""
Human-Track Behavior Near Hazard Classes

Tests whether human-track (residue) tokens behave differently near
batch-focused vs apparatus-focused hazards.

Hypothesis:
- Apparatus hazards have no LINK → no waiting → no time to write
- Batch hazards have LINK → waiting → time for attentional pacing marks

Predictions:
- Human-track density LOWER near apparatus hazards
- Human-track complexity LOWER near apparatus hazards (if present at all)
- SID-05 suppression signal driven by apparatus hazards
"""

import json
from collections import defaultdict, Counter
from pathlib import Path
from datetime import datetime

project_root = Path(__file__).parent.parent.parent

# Hazard token definitions
BATCH_HAZARD_TOKENS = {
    # PHASE_ORDERING
    'shey', 'aiin', 'al', 'c', 'chol', 'r', 'chedy', 'ee', 'chey', 'l',
    # COMPOSITION_JUMP
    'dy', 'or', 'dal', 'ar',
    # RATE_MISMATCH
    'dar', 'qokaiin',
}

APPARATUS_HAZARD_TOKENS = {
    # CONTAINMENT_TIMING
    'qo', 'shy', 'ok', 'shol', 'ol', 'shor',
    # ENERGY_OVERSHOOT
    'qokedy',
}

# High-frequency operational tokens (grammar layer)
# These are NOT human-track
OPERATIONAL_TOKENS = {
    'daiin', 'chedy', 'ol', 'shedy', 'aiin', 'chol', 'chey', 'or', 'dar',
    'qokaiin', 'qokeedy', 'ar', 'qokedy', 'qokeey', 'dy', 'shey', 'dal',
    'okaiin', 'qokain', 'cheey', 'qokal', 'sho', 'cho', 'chy', 'shy',
    'al', 'ol', 'or', 'ar', 'qo', 'ok', 'ot', 'od', 'oe', 'oy',
    'chol', 'chor', 'char', 'shor', 'shal', 'shol',
    'dain', 'chain', 'shain', 'rain', 'kain', 'taiin', 'saiin',
    'chkaiin', 'otaiin', 'oraiin', 'okaiin',
}


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
                # H-only transcriber filter (CRITICAL: avoids 3.2x token inflation)
                transcriber = parts[12].strip('"').strip() if len(parts) > 12 else ''
                if transcriber != 'H':
                    continue
                folio_id = parts[0].split('.')[0] if '.' in parts[0] else parts[0]
                raw_tokens = parts[1].split() if len(parts) > 1 else []
                tokens = [t.strip('"') for t in raw_tokens]
                folios[folio_id].extend(tokens)

    return folios


def is_human_track(token, token_counts, total_tokens):
    """
    Heuristic to identify human-track tokens.

    Human-track tokens are:
    - Not in the high-frequency operational set
    - Lower frequency (not top grammar tokens)
    - Often longer/more complex morphologically
    """
    if token in OPERATIONAL_TOKENS:
        return False

    # Low frequency threshold (less than 0.1% of corpus)
    freq = token_counts.get(token, 0) / total_tokens
    if freq > 0.001:  # Top operational tokens
        return False

    return True


def test_density_near_hazards(folios, token_counts, total_tokens):
    """
    Test 1: Human-track density near batch vs apparatus hazard tokens.

    Measure: Count of human-track tokens within window of each hazard type.
    """
    print("  Test 1: Human-track density near hazards")

    window_size = 3

    batch_ht_counts = []
    apparatus_ht_counts = []

    for folio_id, tokens in folios.items():
        for i, token in enumerate(tokens):
            # Get window around this token
            start = max(0, i - window_size)
            end = min(len(tokens), i + window_size + 1)
            window = tokens[start:end]

            # Count human-track tokens in window (excluding center)
            ht_count = sum(1 for j, t in enumerate(window)
                          if j != (i - start) and is_human_track(t, token_counts, total_tokens))

            if token in BATCH_HAZARD_TOKENS:
                batch_ht_counts.append(ht_count)
            elif token in APPARATUS_HAZARD_TOKENS:
                apparatus_ht_counts.append(ht_count)

    batch_mean = sum(batch_ht_counts) / len(batch_ht_counts) if batch_ht_counts else 0
    apparatus_mean = sum(apparatus_ht_counts) / len(apparatus_ht_counts) if apparatus_ht_counts else 0

    # Effect size
    if batch_ht_counts and apparatus_ht_counts:
        import statistics
        pooled = batch_ht_counts + apparatus_ht_counts
        if len(pooled) > 1:
            std = statistics.stdev(pooled)
            effect_size = (batch_mean - apparatus_mean) / std if std > 0 else 0
        else:
            effect_size = 0
    else:
        effect_size = 0

    return {
        'batch_mean_ht_nearby': round(batch_mean, 3),
        'apparatus_mean_ht_nearby': round(apparatus_mean, 3),
        'batch_observations': len(batch_ht_counts),
        'apparatus_observations': len(apparatus_ht_counts),
        'difference': round(batch_mean - apparatus_mean, 3),
        'effect_size': round(effect_size, 3),
        'batch_higher': batch_mean > apparatus_mean,
    }


def test_complexity_near_hazards(folios, token_counts, total_tokens):
    """
    Test 2: Human-track complexity near batch vs apparatus hazard tokens.

    Measure: Average character length of human-track tokens near each hazard type.
    """
    print("  Test 2: Human-track complexity near hazards")

    window_size = 3

    batch_lengths = []
    apparatus_lengths = []

    for folio_id, tokens in folios.items():
        for i, token in enumerate(tokens):
            # Get window around this token
            start = max(0, i - window_size)
            end = min(len(tokens), i + window_size + 1)
            window = tokens[start:end]

            # Get lengths of human-track tokens in window
            for j, t in enumerate(window):
                if j != (i - start) and is_human_track(t, token_counts, total_tokens):
                    if token in BATCH_HAZARD_TOKENS:
                        batch_lengths.append(len(t))
                    elif token in APPARATUS_HAZARD_TOKENS:
                        apparatus_lengths.append(len(t))

    batch_mean = sum(batch_lengths) / len(batch_lengths) if batch_lengths else 0
    apparatus_mean = sum(apparatus_lengths) / len(apparatus_lengths) if apparatus_lengths else 0

    return {
        'batch_mean_length': round(batch_mean, 3),
        'apparatus_mean_length': round(apparatus_mean, 3),
        'batch_ht_tokens': len(batch_lengths),
        'apparatus_ht_tokens': len(apparatus_lengths),
        'difference': round(batch_mean - apparatus_mean, 3),
        'batch_more_complex': batch_mean > apparatus_mean,
    }


def test_ht_presence_rate(folios, token_counts, total_tokens):
    """
    Test 3: Rate of human-track presence near each hazard type.

    Measure: What fraction of hazard token windows contain ANY human-track?
    """
    print("  Test 3: Human-track presence rate")

    window_size = 3

    batch_has_ht = 0
    batch_total = 0
    apparatus_has_ht = 0
    apparatus_total = 0

    for folio_id, tokens in folios.items():
        for i, token in enumerate(tokens):
            start = max(0, i - window_size)
            end = min(len(tokens), i + window_size + 1)
            window = tokens[start:end]

            has_ht = any(is_human_track(t, token_counts, total_tokens)
                        for j, t in enumerate(window) if j != (i - start))

            if token in BATCH_HAZARD_TOKENS:
                batch_total += 1
                if has_ht:
                    batch_has_ht += 1
            elif token in APPARATUS_HAZARD_TOKENS:
                apparatus_total += 1
                if has_ht:
                    apparatus_has_ht += 1

    batch_rate = batch_has_ht / batch_total if batch_total > 0 else 0
    apparatus_rate = apparatus_has_ht / apparatus_total if apparatus_total > 0 else 0

    return {
        'batch_presence_rate': round(batch_rate, 3),
        'apparatus_presence_rate': round(apparatus_rate, 3),
        'batch_with_ht': batch_has_ht,
        'batch_total': batch_total,
        'apparatus_with_ht': apparatus_has_ht,
        'apparatus_total': apparatus_total,
        'difference': round(batch_rate - apparatus_rate, 3),
        'batch_higher_presence': batch_rate > apparatus_rate,
    }


def test_immediate_adjacency(folios, token_counts, total_tokens):
    """
    Test 4: Human-track immediately adjacent (distance=1) to hazard tokens.

    Stricter test: Is there a human-track token RIGHT NEXT to the hazard?
    """
    print("  Test 4: Immediate adjacency")

    batch_adjacent = 0
    batch_total = 0
    apparatus_adjacent = 0
    apparatus_total = 0

    for folio_id, tokens in folios.items():
        for i, token in enumerate(tokens):
            # Check immediate neighbors only
            neighbors = []
            if i > 0:
                neighbors.append(tokens[i-1])
            if i < len(tokens) - 1:
                neighbors.append(tokens[i+1])

            has_adjacent_ht = any(is_human_track(t, token_counts, total_tokens) for t in neighbors)

            if token in BATCH_HAZARD_TOKENS:
                batch_total += 1
                if has_adjacent_ht:
                    batch_adjacent += 1
            elif token in APPARATUS_HAZARD_TOKENS:
                apparatus_total += 1
                if has_adjacent_ht:
                    apparatus_adjacent += 1

    batch_rate = batch_adjacent / batch_total if batch_total > 0 else 0
    apparatus_rate = apparatus_adjacent / apparatus_total if apparatus_total > 0 else 0

    return {
        'batch_adjacency_rate': round(batch_rate, 3),
        'apparatus_adjacency_rate': round(apparatus_rate, 3),
        'batch_adjacent': batch_adjacent,
        'apparatus_adjacent': apparatus_adjacent,
        'difference': round(batch_rate - apparatus_rate, 3),
        'batch_higher': batch_rate > apparatus_rate,
    }


def evaluate_results(results):
    """Evaluate whether apparatus hazards drive HT suppression."""

    supports_apparatus_drives_suppression = 0
    total_tests = 4

    # Test 1: Batch should have HIGHER HT density nearby
    if results['test_1']['batch_higher']:
        supports_apparatus_drives_suppression += 1

    # Test 2: Batch should have MORE COMPLEX HT nearby
    if results['test_2']['batch_more_complex']:
        supports_apparatus_drives_suppression += 1

    # Test 3: Batch should have HIGHER presence rate
    if results['test_3']['batch_higher_presence']:
        supports_apparatus_drives_suppression += 1

    # Test 4: Batch should have HIGHER immediate adjacency
    if results['test_4']['batch_higher']:
        supports_apparatus_drives_suppression += 1

    if supports_apparatus_drives_suppression >= 3:
        verdict = 'APPARATUS_DRIVES_SUPPRESSION'
        confidence = 'HIGH' if supports_apparatus_drives_suppression == 4 else 'MODERATE'
    elif supports_apparatus_drives_suppression >= 2:
        verdict = 'PARTIAL_SUPPORT'
        confidence = 'LOW'
    else:
        verdict = 'NO_DIFFERENCE'
        confidence = 'HIGH'

    return {
        'tests_supporting': supports_apparatus_drives_suppression,
        'total_tests': total_tests,
        'verdict': verdict,
        'confidence': confidence,
    }


def generate_report(results, evaluation, output_path):
    """Generate markdown report."""

    report = f"""# Human-Track Behavior Near Hazard Classes

**Date:** {datetime.now().strftime('%Y-%m-%d')}
**Extension of:** EXT-ECO-02

---

## Purpose

Test whether human-track (residue) tokens behave differently near
batch-focused vs apparatus-focused hazards.

**Hypothesis:** Apparatus hazards have no LINK (no waiting) → no time for attentional pacing marks.

---

## Test Results

### Test 1: Human-Track Density Near Hazards

| Metric | Value |
|--------|-------|
| batch_mean_ht_nearby | {results['test_1']['batch_mean_ht_nearby']} |
| apparatus_mean_ht_nearby | {results['test_1']['apparatus_mean_ht_nearby']} |
| difference | {results['test_1']['difference']} |
| effect_size | {results['test_1']['effect_size']} |

**Prediction:** Batch hazards should have HIGHER human-track density (time to write)
**Observed:** {'Batch HIGHER' if results['test_1']['batch_higher'] else 'No difference or apparatus higher'}
**Supports Hypothesis:** {'YES' if results['test_1']['batch_higher'] else 'NO'}

---

### Test 2: Human-Track Complexity Near Hazards

| Metric | Value |
|--------|-------|
| batch_mean_length | {results['test_2']['batch_mean_length']} |
| apparatus_mean_length | {results['test_2']['apparatus_mean_length']} |
| batch_ht_tokens | {results['test_2']['batch_ht_tokens']} |
| apparatus_ht_tokens | {results['test_2']['apparatus_ht_tokens']} |

**Prediction:** Batch hazards should have MORE COMPLEX human-track (time for elaborate marks)
**Observed:** {'Batch MORE COMPLEX' if results['test_2']['batch_more_complex'] else 'No difference or apparatus more complex'}
**Supports Hypothesis:** {'YES' if results['test_2']['batch_more_complex'] else 'NO'}

---

### Test 3: Human-Track Presence Rate

| Metric | Value |
|--------|-------|
| batch_presence_rate | {results['test_3']['batch_presence_rate']} |
| apparatus_presence_rate | {results['test_3']['apparatus_presence_rate']} |
| batch_with_ht / total | {results['test_3']['batch_with_ht']} / {results['test_3']['batch_total']} |
| apparatus_with_ht / total | {results['test_3']['apparatus_with_ht']} / {results['test_3']['apparatus_total']} |

**Prediction:** Batch hazards should have HIGHER presence rate (some HT nearby)
**Observed:** {'Batch HIGHER presence' if results['test_3']['batch_higher_presence'] else 'No difference or apparatus higher'}
**Supports Hypothesis:** {'YES' if results['test_3']['batch_higher_presence'] else 'NO'}

---

### Test 4: Immediate Adjacency

| Metric | Value |
|--------|-------|
| batch_adjacency_rate | {results['test_4']['batch_adjacency_rate']} |
| apparatus_adjacency_rate | {results['test_4']['apparatus_adjacency_rate']} |
| difference | {results['test_4']['difference']} |

**Prediction:** Batch hazards should have HIGHER immediate HT adjacency
**Observed:** {'Batch HIGHER' if results['test_4']['batch_higher'] else 'No difference or apparatus higher'}
**Supports Hypothesis:** {'YES' if results['test_4']['batch_higher'] else 'NO'}

---

## Summary

| Metric | Value |
|--------|-------|
| Tests supporting hypothesis | {evaluation['tests_supporting']}/{evaluation['total_tests']} |
| **Verdict** | **{evaluation['verdict']}** |
| **Confidence** | **{evaluation['confidence']}** |

---

## Interpretation

"""

    if evaluation['verdict'] == 'APPARATUS_DRIVES_SUPPRESSION':
        report += """The hypothesis is **CONFIRMED**. Human-track tokens are less dense and less present
near apparatus hazards compared to batch hazards.

**Refined SID-05 Interpretation:**

The z=22 "variability suppression near hazards" finding is now understood as a **composite signal**:

| Hazard Type | LINK Present | Time to Write | Human-Track Behavior |
|-------------|--------------|---------------|---------------------|
| Batch (71%) | YES | YES | Present but simpler (attention split) |
| Apparatus (29%) | NO | NO | **Absent** (no opportunity) |

The suppression near apparatus hazards is driven by **absence of opportunity** (no waiting time),
while suppression near batch hazards is driven by **divided attention** (monitoring while writing).
"""
    elif evaluation['verdict'] == 'PARTIAL_SUPPORT':
        report += """The hypothesis is **PARTIALLY SUPPORTED**. Some difference exists between hazard types,
but the effect is not strong enough to confidently conclude that apparatus hazards drive suppression.
"""
    else:
        report += """The hypothesis is **NOT SUPPORTED**. Human-track behavior does not differ significantly
between batch and apparatus hazard zones. The SID-05 suppression signal appears to be attention-based
regardless of hazard type.
"""

    report += """
---

*Analysis complete.*
"""

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report)


def main():
    print("Human-Track Behavior Near Hazard Classes")
    print("=" * 60)

    # Load data
    print("\nLoading transcription...")
    folios = load_transcription()

    # Build token counts
    print("Building token frequency table...")
    token_counts = Counter()
    total_tokens = 0
    for tokens in folios.values():
        for t in tokens:
            token_counts[t] += 1
            total_tokens += 1
    print(f"  {total_tokens} total tokens, {len(token_counts)} unique")

    # Run tests
    print("\nRunning tests...")
    results = {}

    results['test_1'] = test_density_near_hazards(folios, token_counts, total_tokens)
    results['test_2'] = test_complexity_near_hazards(folios, token_counts, total_tokens)
    results['test_3'] = test_ht_presence_rate(folios, token_counts, total_tokens)
    results['test_4'] = test_immediate_adjacency(folios, token_counts, total_tokens)

    # Evaluate
    print("\nEvaluating...")
    evaluation = evaluate_results(results)

    # Output
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
    print(f"  Verdict: {evaluation['verdict']}")
    print(f"  Confidence: {evaluation['confidence']}")
    print(f"  Tests supporting: {evaluation['tests_supporting']}/{evaluation['total_tests']}")

    # Save
    output_dir = Path(__file__).parent

    with open(output_dir / 'human_track_hazard_results.json', 'w') as f:
        json.dump({'results': results, 'evaluation': evaluation}, f, indent=2)
    print(f"\n  Written: {output_dir / 'human_track_hazard_results.json'}")

    generate_report(results, evaluation, output_dir / 'HUMAN_TRACK_HAZARD_REPORT.md')
    print(f"  Written: {output_dir / 'HUMAN_TRACK_HAZARD_REPORT.md'}")

    print("\n" + "=" * 60)
    print("COMPLETE")
    print("=" * 60)

    return results, evaluation


if __name__ == '__main__':
    main()
