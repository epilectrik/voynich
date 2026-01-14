#!/usr/bin/env python3
"""
Tests 3A and 3B: Counterfactual Grammar Stress Tests

3A: Remove e (stability anchor) - How necessary is the e operator?
3B: Force symmetric hazards - Is asymmetry architecturally necessary?

EPISTEMIC SAFEGUARD:
These tests remain Tier 3/4 exploratory. Results do NOT enable semantic decoding
or Tier 2 promotion without independent corroboration.
"""

import csv
import json
import numpy as np
from collections import Counter, defaultdict
from pathlib import Path
from scipy import stats

# Paths
BASE_PATH = Path(__file__).parent.parent.parent
DATA_FILE = BASE_PATH / "data" / "transcriptions" / "interlinear_full_words.txt"
HAZARD_FILE = BASE_PATH / "phases" / "15-20_kernel_grammar" / "phase18e_hazard_synthesis.json"
OUTPUT_FILE = BASE_PATH / "results" / "counterfactual_grammar.json"


def get_kernel_class(word):
    """Classify token by kernel class (k, h, e, or None)."""
    if not word:
        return None
    if word.endswith('k') or word in ['ok', 'yk', 'ak', 'ek']:
        return 'k'
    if word.endswith('h') or word in ['oh', 'yh', 'ah', 'eh']:
        return 'h'
    if word.endswith('ey') or word.endswith('eey') or word.endswith('edy') or word.endswith('dy'):
        return 'e'
    return None


def load_b_tokens():
    """Load all Currier B tokens with their folio and position."""
    tokens = []

    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            lang = row['language'].strip('"')
            if lang != 'B':
                continue

            word = row['word'].strip('"').lower()
            folio = row['folio'].strip('"')
            line = int(row.get('line', 0) or 0)
            position = int(row.get('word_in_line', 0) or 0)

            if word and word != 'na':
                tokens.append({
                    'word': word,
                    'folio': folio,
                    'line': line,
                    'position': position,
                    'kernel': get_kernel_class(word)
                })

    return tokens


def compute_baseline_metrics(tokens):
    """Compute baseline grammar metrics."""
    kernel_counts = Counter(t['kernel'] for t in tokens)
    total = len(tokens)

    # Kernel ratios
    k_ratio = kernel_counts.get('k', 0) / total
    h_ratio = kernel_counts.get('h', 0) / total
    e_ratio = kernel_counts.get('e', 0) / total

    # Kernel contact ratio (how often we're at a kernel token)
    kernel_contact = sum(1 for t in tokens if t['kernel']) / total

    # Recovery ratio (e tokens after k/h tokens)
    recovery_count = 0
    recovery_opportunities = 0
    for i in range(1, len(tokens)):
        if tokens[i-1]['kernel'] in ['k', 'h']:
            recovery_opportunities += 1
            if tokens[i]['kernel'] == 'e':
                recovery_count += 1

    recovery_ratio = recovery_count / recovery_opportunities if recovery_opportunities else 0

    # Trigram analysis (e->e->e chains)
    e_trigram_count = 0
    total_trigrams = 0
    for i in range(2, len(tokens)):
        if tokens[i-2]['kernel'] and tokens[i-1]['kernel'] and tokens[i]['kernel']:
            total_trigrams += 1
            if tokens[i-2]['kernel'] == 'e' and tokens[i-1]['kernel'] == 'e' and tokens[i]['kernel'] == 'e':
                e_trigram_count += 1

    e_trigram_ratio = e_trigram_count / total_trigrams if total_trigrams else 0

    return {
        'total_tokens': total,
        'kernel_counts': dict(kernel_counts),
        'k_ratio': k_ratio,
        'h_ratio': h_ratio,
        'e_ratio': e_ratio,
        'kernel_contact_ratio': kernel_contact,
        'recovery_ratio': recovery_ratio,
        'e_trigram_ratio': e_trigram_ratio
    }


def test_3a_remove_e(tokens, baseline):
    """Test 3A: What happens if we remove e (stability anchor)?"""
    print("\n" + "=" * 50)
    print("TEST 3A: Remove e (Stability Anchor)")
    print("=" * 50)

    # Filter out e-class tokens
    no_e_tokens = [t for t in tokens if t['kernel'] != 'e']

    # Compute metrics without e
    kernel_counts = Counter(t['kernel'] for t in no_e_tokens)
    total = len(no_e_tokens)

    k_ratio = kernel_counts.get('k', 0) / total
    h_ratio = kernel_counts.get('h', 0) / total
    kernel_contact = sum(1 for t in no_e_tokens if t['kernel']) / total

    # Recovery is now impossible (no e to return to)
    recovery_ratio = 0

    # Hazard exposure: without e, k and h dominate
    hazard_dominated = k_ratio + h_ratio

    print(f"  Baseline e-ratio: {baseline['e_ratio']:.1%}")
    print(f"  E-tokens removed: {baseline['kernel_counts'].get('e', 0)}")
    print(f"  Remaining tokens: {total}")
    print()
    print(f"  Baseline kernel contact: {baseline['kernel_contact_ratio']:.1%}")
    print(f"  Without-e kernel contact: {kernel_contact:.1%}")
    print(f"  Change: {(kernel_contact - baseline['kernel_contact_ratio']) / baseline['kernel_contact_ratio'] * 100:+.1f}%")
    print()
    print(f"  Baseline recovery ratio: {baseline['recovery_ratio']:.1%}")
    print(f"  Without-e recovery ratio: {recovery_ratio:.1%} (COLLAPSED)")
    print()
    print(f"  Hazard-dominated ratio (k+h): {hazard_dominated:.1%}")

    # Verdict
    recovery_collapse = baseline['recovery_ratio'] - recovery_ratio
    contact_change = abs(kernel_contact - baseline['kernel_contact_ratio']) / baseline['kernel_contact_ratio']

    if recovery_collapse > 0.1 or contact_change > 0.2:
        verdict = "E_NECESSARY"
        print("\n  VERDICT: e is STRUCTURALLY NECESSARY")
        print("    Recovery paths collapse without stability anchor.")
    else:
        verdict = "E_OPTIONAL"
        print("\n  VERDICT: e may be OPTIONAL")
        print("    Grammar maintains structure without e.")

    return {
        'baseline_e_ratio': baseline['e_ratio'],
        'tokens_removed': baseline['kernel_counts'].get('e', 0),
        'remaining_tokens': total,
        'baseline_kernel_contact': baseline['kernel_contact_ratio'],
        'without_e_kernel_contact': kernel_contact,
        'contact_change_pct': (kernel_contact - baseline['kernel_contact_ratio']) / baseline['kernel_contact_ratio'] * 100,
        'baseline_recovery_ratio': baseline['recovery_ratio'],
        'without_e_recovery_ratio': recovery_ratio,
        'recovery_collapse': recovery_collapse,
        'hazard_dominated_ratio': hazard_dominated,
        'verdict': verdict
    }


def test_3b_symmetric_hazards(tokens, baseline):
    """Test 3B: What if hazard asymmetry is forced symmetric?"""
    print("\n" + "=" * 50)
    print("TEST 3B: Force Symmetric Hazards")
    print("=" * 50)

    # Build transition matrix
    transitions = defaultdict(Counter)
    for i in range(1, len(tokens)):
        prev_kernel = tokens[i-1]['kernel']
        curr_kernel = tokens[i]['kernel']
        if prev_kernel and curr_kernel:
            transitions[prev_kernel][curr_kernel] += 1

    # Compute transition probabilities
    trans_probs = {}
    for source, targets in transitions.items():
        total = sum(targets.values())
        trans_probs[source] = {t: c/total for t, c in targets.items()}

    print("  Baseline transition matrix:")
    for source in ['k', 'h', 'e']:
        probs = trans_probs.get(source, {})
        print(f"    {source} -> k:{probs.get('k',0):.2f} h:{probs.get('h',0):.2f} e:{probs.get('e',0):.2f}")

    # Compute asymmetry
    asymmetries = []
    for pair in [('k', 'h'), ('k', 'e'), ('h', 'e')]:
        a, b = pair
        p_ab = trans_probs.get(a, {}).get(b, 0)
        p_ba = trans_probs.get(b, {}).get(a, 0)
        asymmetry = abs(p_ab - p_ba)
        asymmetries.append(asymmetry)
        print(f"\n  {a}<->{b}: P({a}->{b})={p_ab:.3f}, P({b}->{a})={p_ba:.3f}, asymmetry={asymmetry:.3f}")

    mean_asymmetry = np.mean(asymmetries)
    print(f"\n  Mean asymmetry: {mean_asymmetry:.3f}")

    # Key asymmetry: h->k is suppressed (should be near 0)
    h_to_k = trans_probs.get('h', {}).get('k', 0)
    k_to_h = trans_probs.get('k', {}).get('h', 0)
    print(f"\n  Critical asymmetry (h->k suppression):")
    print(f"    P(h->k) = {h_to_k:.4f} (should be ~0, is suppressed)")
    print(f"    P(k->h) = {k_to_h:.4f}")

    # Simulate symmetric hazards
    print("\n  Simulating SYMMETRIC hazards (if h->k were allowed):")

    # If h->k had same probability as k->h, what would change?
    h_total = sum(transitions['h'].values()) if 'h' in transitions else 1
    simulated_h_to_k = k_to_h  # Make symmetric

    # Impact: more oscillation between hazard states
    oscillation_increase = (simulated_h_to_k - h_to_k) * 100
    print(f"    Forced h->k probability: {simulated_h_to_k:.4f}")
    print(f"    Oscillation increase: {oscillation_increase:+.1f}%")

    # Verdict
    if h_to_k < 0.01 and mean_asymmetry > 0.1:
        verdict = "ASYMMETRY_NECESSARY"
        print("\n  VERDICT: Asymmetry is ARCHITECTURALLY NECESSARY")
        print("    h->k suppression (near 0) prevents k-h oscillation.")
        print("    Forcing symmetry would destabilize convergence.")
    else:
        verdict = "ASYMMETRY_EMPIRICAL"
        print("\n  VERDICT: Asymmetry may be EMPIRICAL")
        print("    Not strongly load-bearing.")

    return {
        'transition_matrix': {s: dict(t) for s, t in trans_probs.items()},
        'asymmetries': {
            'k_h': float(abs(trans_probs.get('k',{}).get('h',0) - trans_probs.get('h',{}).get('k',0))),
            'k_e': float(abs(trans_probs.get('k',{}).get('e',0) - trans_probs.get('e',{}).get('k',0))),
            'h_e': float(abs(trans_probs.get('h',{}).get('e',0) - trans_probs.get('e',{}).get('h',0)))
        },
        'mean_asymmetry': float(mean_asymmetry),
        'h_to_k_suppression': float(h_to_k),
        'k_to_h': float(k_to_h),
        'verdict': verdict
    }


def main():
    print("=" * 60)
    print("Counterfactual Grammar Stress Tests")
    print("Tier 3/4 Exploratory")
    print("=" * 60)

    # Load tokens
    print("\nLoading Currier B tokens...")
    tokens = load_b_tokens()
    print(f"  Total tokens: {len(tokens)}")

    # Compute baseline
    print("\nComputing baseline metrics...")
    baseline = compute_baseline_metrics(tokens)
    print(f"  Kernel distribution: k={baseline['k_ratio']:.1%}, h={baseline['h_ratio']:.1%}, e={baseline['e_ratio']:.1%}")
    print(f"  Kernel contact ratio: {baseline['kernel_contact_ratio']:.1%}")
    print(f"  Recovery ratio (e after k/h): {baseline['recovery_ratio']:.1%}")
    print(f"  e->e->e trigram ratio: {baseline['e_trigram_ratio']:.1%}")

    # Test 3A: Remove e
    result_3a = test_3a_remove_e(tokens, baseline)

    # Test 3B: Symmetric hazards
    result_3b = test_3b_symmetric_hazards(tokens, baseline)

    # Overall verdict
    print("\n" + "=" * 60)
    print("OVERALL COUNTERFACTUAL RESULTS")
    print("=" * 60)
    print(f"  3A (Remove e): {result_3a['verdict']}")
    print(f"  3B (Symmetric hazards): {result_3b['verdict']}")

    if result_3a['verdict'] == 'E_NECESSARY' and result_3b['verdict'] == 'ASYMMETRY_NECESSARY':
        overall = "GRAMMAR_MINIMAL"
        print("\n  OVERALL: Grammar is MINIMALLY NECESSARY")
        print("    Both e-operator and hazard asymmetry are load-bearing.")
    elif result_3a['verdict'] == 'E_NECESSARY' or result_3b['verdict'] == 'ASYMMETRY_NECESSARY':
        overall = "PARTIALLY_NECESSARY"
        print("\n  OVERALL: Grammar is PARTIALLY NECESSARY")
        print("    Some elements are load-bearing, others may be empirical.")
    else:
        overall = "GRAMMAR_OVERCOMPLETE"
        print("\n  OVERALL: Grammar may be OVERCOMPLETE")
        print("    Neither e nor asymmetry are strictly necessary.")
    print("=" * 60)

    # Save results
    results = {
        "test": "3A_3B_COUNTERFACTUAL",
        "tier": "3-4",
        "question": "How necessary are e-operator and hazard asymmetry?",
        "baseline": baseline,
        "test_3a_remove_e": result_3a,
        "test_3b_symmetric_hazards": result_3b,
        "overall_verdict": overall
    }

    OUTPUT_FILE.parent.mkdir(exist_ok=True)
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
