"""
EXT-FILTER-01: External Alignment Conditioning via Human-Track Removal

Tests whether prior external alignment signals were artifacts of human
attentional behavior or properties of the executable grammar itself.

TIER 3 ONLY - No interpretation, no new hypotheses.
"""

import sys
import math
import random
from collections import defaultdict, Counter
import numpy as np
from scipy import stats as scipy_stats

sys.path.insert(0, r'C:\git\voynich')

# Grammar patterns (from SID-04/SID-05)
GRAMMAR_PREFIXES = {'qo', 'ch', 'sh', 'ok', 'da', 'ot', 'ct', 'kc', 'pc', 'fc'}
GRAMMAR_SUFFIXES = {'aiin', 'dy', 'ol', 'or', 'ar', 'ain', 'ey', 'edy', 'eey'}

# Hazard tokens (from prior phases)
HAZARD_TOKENS = {'shey', 'aiin', 'al', 'c', 'chol', 'r', 'chedy', 'ee', 'chey',
                 'l', 'dy', 'or', 'dal', 'ar', 'qo', 'shy', 'ok', 'shol',
                 'ol', 'shor', 'dar', 'qokaiin', 'qokedy'}

# LINK tokens (waiting operators) - tokens associated with non-intervention
LINK_PATTERNS = {'ol', 'or', 'ar', 'al', 'aiin', 'ain'}


def load_data():
    """Load corpus with folio/section information."""
    filepath = r'C:\git\voynich\data\transcriptions\interlinear_full_words.txt'

    tokens = []
    folios = []
    sections = []

    with open(filepath, 'r', encoding='utf-8') as f:
        next(f)  # Skip header
        for line in f:
            parts = line.split('\t')
            if len(parts) >= 4:
                word = parts[0].strip('"').lower()
                folio = parts[2].strip('"') if len(parts) > 2 else ''
                section = parts[3].strip('"') if len(parts) > 3 else ''
                if word and not word.startswith('*'):
                    tokens.append(word)
                    folios.append(folio)
                    sections.append(section)

    return tokens, folios, sections


def is_grammar(t):
    """Check if token belongs to executable grammar."""
    for p in GRAMMAR_PREFIXES:
        if t.startswith(p): return True
    for s in GRAMMAR_SUFFIXES:
        if t.endswith(s): return True
    return False


def is_hazard_adjacent(tokens, pos, window=3):
    """Check if position is within window of a hazard token."""
    start = max(0, pos - window)
    end = min(len(tokens), pos + window + 1)
    for i in range(start, end):
        if i != pos and tokens[i] in HAZARD_TOKENS:
            return True
    return False


def is_link_token(t):
    """Check if token is LINK-associated (waiting/non-intervention)."""
    for pattern in LINK_PATTERNS:
        if t.endswith(pattern):
            return True
    return False


def compute_metrics(tokens, folios, sections, label=""):
    """Compute external alignment metrics."""
    print(f"\n{'='*60}")
    print(f"METRICS: {label}")
    print(f"{'='*60}")

    metrics = {}
    n = len(tokens)
    print(f"  Token count: {n}")
    metrics['token_count'] = n

    # 1. PROCESS RHYTHM METRICS
    print("\n--- Process Rhythm Metrics ---")

    # Intervention frequency (grammar tokens per folio)
    folio_counts = defaultdict(lambda: {'grammar': 0, 'total': 0})
    for t, f in zip(tokens, folios):
        folio_counts[f]['total'] += 1
        if is_grammar(t):
            folio_counts[f]['grammar'] += 1

    intervention_rates = [c['grammar']/c['total'] if c['total'] > 0 else 0
                         for c in folio_counts.values()]
    mean_intervention = np.mean(intervention_rates)
    std_intervention = np.std(intervention_rates)
    print(f"  Mean intervention rate per folio: {mean_intervention:.4f}")
    print(f"  Std intervention rate: {std_intervention:.4f}")
    metrics['mean_intervention_rate'] = mean_intervention
    metrics['std_intervention_rate'] = std_intervention

    # Waiting interval distribution (runs of LINK tokens)
    link_runs = []
    current_run = 0
    for t in tokens:
        if is_link_token(t):
            current_run += 1
        else:
            if current_run > 0:
                link_runs.append(current_run)
            current_run = 0
    if current_run > 0:
        link_runs.append(current_run)

    if link_runs:
        mean_wait = np.mean(link_runs)
        max_wait = max(link_runs)
        median_wait = np.median(link_runs)
    else:
        mean_wait = max_wait = median_wait = 0
    print(f"  Mean LINK run length: {mean_wait:.2f}")
    print(f"  Max LINK run length: {max_wait}")
    print(f"  Median LINK run length: {median_wait:.2f}")
    metrics['mean_link_run'] = mean_wait
    metrics['max_link_run'] = max_wait
    metrics['median_link_run'] = median_wait

    # Hazard spacing statistics
    hazard_positions = [i for i, t in enumerate(tokens) if t in HAZARD_TOKENS]
    if len(hazard_positions) > 1:
        hazard_gaps = [hazard_positions[i+1] - hazard_positions[i]
                       for i in range(len(hazard_positions)-1)]
        mean_hazard_gap = np.mean(hazard_gaps)
        std_hazard_gap = np.std(hazard_gaps)
        cv_hazard_gap = std_hazard_gap / mean_hazard_gap if mean_hazard_gap > 0 else 0
    else:
        mean_hazard_gap = std_hazard_gap = cv_hazard_gap = 0
    print(f"  Mean hazard spacing: {mean_hazard_gap:.2f}")
    print(f"  CV hazard spacing: {cv_hazard_gap:.3f}")
    metrics['mean_hazard_spacing'] = mean_hazard_gap
    metrics['cv_hazard_spacing'] = cv_hazard_gap

    # 2. HAZARD PROFILE SHAPE
    print("\n--- Hazard Profile Shape ---")

    hazard_count = len(hazard_positions)
    hazard_density = hazard_count / n if n > 0 else 0
    print(f"  Hazard token count: {hazard_count}")
    print(f"  Hazard density: {hazard_density:.4f}")
    metrics['hazard_count'] = hazard_count
    metrics['hazard_density'] = hazard_density

    # Hazard class breakdown (simplified)
    hazard_tokens_found = Counter(t for t in tokens if t in HAZARD_TOKENS)
    phase_ordering = sum(hazard_tokens_found.get(t, 0) for t in ['chol', 'shol', 'chedy', 'chey', 'shor', 'shey', 'shy'])
    other_hazards = hazard_count - phase_ordering
    phase_ratio = phase_ordering / hazard_count if hazard_count > 0 else 0
    print(f"  Phase-ordering hazards: {phase_ordering} ({phase_ratio:.1%})")
    print(f"  Other hazards: {other_hazards}")
    metrics['phase_ordering_ratio'] = phase_ratio

    # 3. LINK FRACTION VS SAFETY
    print("\n--- LINK Fraction vs Safety ---")

    link_count = sum(1 for t in tokens if is_link_token(t))
    link_density = link_count / n if n > 0 else 0
    print(f"  LINK token count: {link_count}")
    print(f"  LINK density: {link_density:.4f}")
    metrics['link_count'] = link_count
    metrics['link_density'] = link_density

    # LINK proximity to hazards
    link_near_hazard = 0
    link_far_hazard = 0
    for i, t in enumerate(tokens):
        if is_link_token(t):
            if is_hazard_adjacent(tokens, i, window=5):
                link_near_hazard += 1
            else:
                link_far_hazard += 1

    link_hazard_prox = link_near_hazard / link_count if link_count > 0 else 0
    print(f"  LINK near hazard (within 5): {link_near_hazard}")
    print(f"  LINK far from hazard: {link_far_hazard}")
    print(f"  LINK-hazard proximity ratio: {link_hazard_prox:.3f}")
    metrics['link_hazard_proximity'] = link_hazard_prox

    # Safety margin (non-hazard tokens between hazards, normalized)
    if len(hazard_gaps) > 0:
        safety_margin = np.percentile(hazard_gaps, 25)  # 25th percentile gap
    else:
        safety_margin = 0
    print(f"  Safety margin (25th pctl gap): {safety_margin:.1f}")
    metrics['safety_margin'] = safety_margin

    # 4. CLOSED-LOOP / BATCH COMPATIBILITY
    print("\n--- Closed-Loop vs Batch Compatibility ---")

    # Measure recurrence patterns (tokens that repeat)
    token_counts = Counter(tokens)
    repeating_tokens = sum(1 for c in token_counts.values() if c > 1)
    repeat_ratio = repeating_tokens / len(token_counts) if len(token_counts) > 0 else 0
    print(f"  Unique tokens: {len(token_counts)}")
    print(f"  Repeating tokens: {repeating_tokens} ({repeat_ratio:.1%})")
    metrics['repeat_ratio'] = repeat_ratio

    # Circular pattern indicator (first-last similarity within folios)
    folio_circularity = []
    folio_tokens = defaultdict(list)
    for t, f in zip(tokens, folios):
        folio_tokens[f].append(t)

    for f, toks in folio_tokens.items():
        if len(toks) >= 10:
            first5 = set(toks[:5])
            last5 = set(toks[-5:])
            overlap = len(first5 & last5) / 5
            folio_circularity.append(overlap)

    mean_circularity = np.mean(folio_circularity) if folio_circularity else 0
    print(f"  Mean folio circularity (first/last 5 overlap): {mean_circularity:.3f}")
    metrics['circularity'] = mean_circularity

    # Convergence indicator (how often we see common ending patterns)
    ending_suffixes = Counter(t[-3:] if len(t) >= 3 else t for t in tokens)
    top3_endings = sum(c for _, c in ending_suffixes.most_common(3))
    ending_concentration = top3_endings / n if n > 0 else 0
    print(f"  Ending suffix concentration (top 3): {ending_concentration:.3f}")
    metrics['ending_concentration'] = ending_concentration

    return metrics


def compare_metrics(baseline, filtered):
    """Compare baseline vs filtered metrics and compute deltas."""
    print("\n" + "="*60)
    print("COMPARISON: BASELINE vs FILTERED")
    print("="*60)

    deltas = {}

    print(f"\n{'Metric':<35} {'Baseline':>12} {'Filtered':>12} {'Delta':>12} {'Change':>10}")
    print("-" * 85)

    for key in baseline:
        b = baseline[key]
        f = filtered[key]

        if isinstance(b, (int, float)) and isinstance(f, (int, float)):
            delta = f - b
            if b != 0:
                pct_change = (delta / abs(b)) * 100
                pct_str = f"{pct_change:+.1f}%"
            else:
                pct_str = "N/A"

            deltas[key] = {'baseline': b, 'filtered': f, 'delta': delta, 'pct': pct_str}
            print(f"{key:<35} {b:>12.4f} {f:>12.4f} {delta:>+12.4f} {pct_str:>10}")

    return deltas


def classify_outcome(deltas):
    """Classify the outcome based on delta magnitudes."""
    print("\n" + "="*60)
    print("OUTCOME CLASSIFICATION")
    print("="*60)

    # Key metrics for classification
    key_metrics = ['mean_intervention_rate', 'link_density', 'hazard_density',
                   'phase_ordering_ratio', 'link_hazard_proximity', 'circularity']

    significant_changes = 0
    collapsed = 0
    sharpened = 0

    for m in key_metrics:
        if m in deltas:
            pct = deltas[m]['pct']
            if pct != "N/A":
                pct_val = float(pct.replace('%', '').replace('+', ''))
                if abs(pct_val) > 25:
                    significant_changes += 1
                    if pct_val < -25:
                        collapsed += 1
                    elif pct_val > 25:
                        sharpened += 1

    print(f"\n  Key metrics with >25% change: {significant_changes}/6")
    print(f"  Metrics collapsed (>25% decrease): {collapsed}")
    print(f"  Metrics sharpened (>25% increase): {sharpened}")

    # Outcome classification
    if significant_changes <= 1:
        outcome = "ALIGNMENT_UNCHANGED"
        interpretation = "Prior external matches were grammar-driven"
    elif collapsed >= 2:
        outcome = "ALIGNMENT_WEAKENED"
        interpretation = "Prior matches were likely human-behavior artifacts"
    elif sharpened >= 2:
        outcome = "ALIGNMENT_SHARPENED"
        interpretation = "Human-track layer was masking executable differences"
    else:
        outcome = "ALIGNMENT_UNCHANGED"
        interpretation = "No clear directional change; prior alignments remain consistent"

    print(f"\n  OUTCOME: {outcome}")
    print(f"  Justification: {interpretation}")

    return outcome, interpretation


def main():
    print("="*60)
    print("EXT-FILTER-01: External Alignment Conditioning")
    print("="*60)
    print("\nMethod: Remove human-track tokens, compare alignment metrics")
    print("Confirmation: No grammar changes - filtering only\n")

    random.seed(42)
    np.random.seed(42)

    # Load data
    print("Loading corpus...")
    tokens, folios, sections = load_data()
    print(f"  Total tokens: {len(tokens)}")

    # Classify tokens
    grammar_mask = [is_grammar(t) for t in tokens]
    grammar_count = sum(grammar_mask)
    human_track_count = len(tokens) - grammar_count
    print(f"  Grammar tokens: {grammar_count} ({grammar_count/len(tokens):.1%})")
    print(f"  Human-track tokens: {human_track_count} ({human_track_count/len(tokens):.1%})")

    # BASELINE: Full corpus (including human-track)
    baseline_metrics = compute_metrics(tokens, folios, sections, "BASELINE (Full Corpus)")

    # FILTERED: Grammar-only corpus
    filtered_tokens = [t for t, g in zip(tokens, grammar_mask) if g]
    filtered_folios = [f for f, g in zip(folios, grammar_mask) if g]
    filtered_sections = [s for s, g in zip(sections, grammar_mask) if g]

    filtered_metrics = compute_metrics(filtered_tokens, filtered_folios, filtered_sections,
                                       "FILTERED (Grammar Only)")

    # Compare
    deltas = compare_metrics(baseline_metrics, filtered_metrics)

    # Classify outcome
    outcome, interpretation = classify_outcome(deltas)

    # Interpretive boundary statement
    print("\n" + "="*60)
    print("INTERPRETIVE BOUNDARY")
    print("="*60)
    print("""
This result does not imply materials, substances, instructions,
meanings, or historical identification. EXT-FILTER-01 is a
conditioning pass that removes a known confound (human attentional
behavior) and checks whether prior external alignments survive
that removal. It is a hygiene pass, not an interpretive phase.
""")

    print("="*60)
    print("EXT-FILTER-01 COMPLETE")
    print("="*60)

    return outcome, deltas


if __name__ == "__main__":
    main()
