#!/usr/bin/env python3
"""
T8: REGIME-Conditioned Automaton
MINIMAL_STATE_AUTOMATON phase

Test whether the 6-state transition probabilities vary by REGIME (C179).
Split the corpus by REGIME assignment, rebuild the 6-state transition
matrix for each REGIME, and test for significant differences.

Expert Q3: Does each REGIME correspond to variation in transition
probabilities between the 6 states?
"""

import sys
import json
import functools
import numpy as np
from pathlib import Path
from collections import Counter, defaultdict
from scipy.stats import chi2_contingency

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from scripts.voynich import Transcript

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
RESULTS_DIR = Path(__file__).parent.parent / 'results'

STATE_LABELS = ['FL_HAZ', 'FQ', 'CC', 'AXm', 'AXM', 'FL_SAFE']
SHORT = ['FL_H', 'FQ', 'CC', 'AXm', 'AXM', 'FL_S']
N_STATES = 6


def run():
    print("=" * 70)
    print("T8: REGIME-Conditioned Automaton")
    print("MINIMAL_STATE_AUTOMATON phase")
    print("=" * 70)

    # Load data
    print("\n[1/5] Loading data...")
    with open(RESULTS_DIR / 't3_merged_automaton.json') as f:
        t3 = json.load(f)
    with open(PROJECT_ROOT / 'phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json') as f:
        ctm = json.load(f)
    with open(PROJECT_ROOT / 'results/regime_folio_mapping.json') as f:
        regime_map = json.load(f)

    partition = t3['final_partition']
    token_to_class = {t: int(c) for t, c in ctm['token_to_class'].items()}

    # Build class→state mapping
    cls_to_state = {}
    for si, group in enumerate(partition):
        for c in group:
            cls_to_state[c] = si

    # Format is {REGIME_N: [list_of_folios]}
    folio_to_regime = {}
    for regime_key, folios in regime_map.items():
        regime_num = int(regime_key.split('_')[1])
        for folio in folios:
            folio_to_regime[folio] = regime_num

    print(f"  {len(folio_to_regime)} folios with REGIME assignments")
    regime_counts = Counter(folio_to_regime.values())
    for r in sorted(regime_counts):
        print(f"    REGIME_{r}: {regime_counts[r]} folios")

    # =========================================================
    # 2. Build per-REGIME transition counts
    # =========================================================
    print("\n[2/5] Building per-REGIME state transitions...")

    tx = Transcript()
    # Collect transitions per regime
    regime_transitions = defaultdict(lambda: np.zeros((N_STATES, N_STATES), dtype=float))
    regime_token_counts = Counter()

    current_key = None
    current_seq = []
    current_folio = None

    for token in tx.currier_b():
        w = token.word.strip()
        if not w or '*' in w:
            continue
        cls = token_to_class.get(w)
        if cls is None:
            continue
        state = cls_to_state.get(cls)
        if state is None:
            continue

        key = (token.folio, token.line)
        if key != current_key:
            # Process previous line
            if current_seq and current_folio:
                regime = folio_to_regime.get(current_folio)
                if regime is not None:
                    for i in range(len(current_seq) - 1):
                        regime_transitions[regime][current_seq[i]][current_seq[i+1]] += 1
                    regime_token_counts[regime] += len(current_seq)
            current_seq = []
            current_key = key
            current_folio = token.folio
        current_seq.append(state)

    # Process last line
    if current_seq and current_folio:
        regime = folio_to_regime.get(current_folio)
        if regime is not None:
            for i in range(len(current_seq) - 1):
                regime_transitions[regime][current_seq[i]][current_seq[i+1]] += 1
            regime_token_counts[regime] += len(current_seq)

    regimes = sorted(regime_transitions.keys())
    print(f"  Regimes found: {regimes}")
    for r in regimes:
        total_trans = regime_transitions[r].sum()
        print(f"    REGIME_{r}: {int(total_trans)} transitions, {regime_token_counts[r]} tokens")

    # =========================================================
    # 3. Per-REGIME transition matrices
    # =========================================================
    print("\n[3/5] Per-REGIME Transition Matrices")

    regime_probs = {}
    for r in regimes:
        counts = regime_transitions[r]
        row_sums = counts.sum(axis=1, keepdims=True)
        probs = np.divide(counts, row_sums, where=row_sums > 0,
                          out=np.zeros_like(counts))
        regime_probs[r] = probs

        print(f"\n  REGIME_{r} ({int(counts.sum())} transitions):")
        print(f"  {'':>6}", end='')
        for j in range(N_STATES):
            print(f"  {SHORT[j]:>5}", end='')
        print()
        for i in range(N_STATES):
            print(f"  {SHORT[i]:>5}", end='')
            for j in range(N_STATES):
                print(f"  {probs[i][j]:5.3f}", end='')
            print()

    # =========================================================
    # 4. Statistical tests
    # =========================================================
    print("\n[4/5] Statistical Tests: REGIME Independence")

    # Test 1: Per-row chi-squared across regimes
    # For each source state, test if the outgoing distribution differs by regime
    print(f"\n  Per-source-state chi-squared (outgoing distribution x REGIME):")
    row_tests = []
    for i in range(N_STATES):
        # Build contingency table: regimes x destination states
        contingency = np.zeros((len(regimes), N_STATES))
        for ri, r in enumerate(regimes):
            contingency[ri] = regime_transitions[r][i]

        # Only test if all rows have sufficient counts
        if contingency.sum() < 20:
            print(f"    {STATE_LABELS[i]:>8}: insufficient data")
            row_tests.append({'state': STATE_LABELS[i], 'chi2': 0, 'p': 1.0, 'significant': False})
            continue

        # Remove zero columns
        nonzero = contingency.sum(axis=0) > 0
        cont_reduced = contingency[:, nonzero]

        if cont_reduced.shape[1] < 2:
            print(f"    {STATE_LABELS[i]:>8}: degenerate (single destination)")
            row_tests.append({'state': STATE_LABELS[i], 'chi2': 0, 'p': 1.0, 'significant': False})
            continue

        chi2, p, dof, expected = chi2_contingency(cont_reduced)
        sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else ""
        print(f"    {STATE_LABELS[i]:>8}: chi2={chi2:>8.1f}  dof={dof:>2}  p={p:.4e}  {sig}")
        row_tests.append({
            'state': STATE_LABELS[i],
            'chi2': round(float(chi2), 2),
            'p': round(float(p), 6),
            'dof': int(dof),
            'significant': bool(p < 0.05),
        })

    # Test 2: Global test (all transitions together)
    print(f"\n  Global test (full 6x6 transition matrix x REGIME):")
    # Flatten: for each regime, the 36-element transition vector
    global_contingency = np.zeros((len(regimes), N_STATES * N_STATES))
    for ri, r in enumerate(regimes):
        global_contingency[ri] = regime_transitions[r].flatten()

    # Remove zero columns
    nonzero = global_contingency.sum(axis=0) > 0
    gc_reduced = global_contingency[:, nonzero]
    chi2_global, p_global, dof_global, _ = chi2_contingency(gc_reduced)
    print(f"    chi2={chi2_global:.1f}  dof={dof_global}  p={p_global:.4e}")

    # =========================================================
    # 5. Specific Transition Shifts
    # =========================================================
    print("\n[5/5] Most REGIME-Shifted Transitions")

    # For each transition (i,j), compute the max deviation across regimes
    # relative to the pooled rate
    pooled = sum(regime_transitions[r] for r in regimes)
    pooled_row_sums = pooled.sum(axis=1, keepdims=True)
    pooled_probs = np.divide(pooled, pooled_row_sums, where=pooled_row_sums > 0,
                             out=np.zeros_like(pooled))

    deviations = []
    for i in range(N_STATES):
        for j in range(N_STATES):
            if pooled_probs[i][j] < 0.005:
                continue  # Skip very rare transitions
            max_dev = 0
            regime_vals = {}
            for r in regimes:
                regime_vals[r] = regime_probs[r][i][j]
                dev = abs(regime_probs[r][i][j] - pooled_probs[i][j])
                max_dev = max(max_dev, dev)
            deviations.append((i, j, pooled_probs[i][j], max_dev, regime_vals))

    deviations.sort(key=lambda x: -x[3])

    print(f"\n  Top 15 most REGIME-shifted transitions:")
    print(f"  {'Transition':>15} {'Pooled':>7}", end='')
    for r in regimes:
        print(f"  {'R'+str(r):>5}", end='')
    print(f"  {'MaxDev':>7}")

    for i, j, pooled_p, max_dev, rvals in deviations[:15]:
        label = f"{SHORT[i]}->{SHORT[j]}"
        print(f"  {label:>15} {pooled_p:>7.3f}", end='')
        for r in regimes:
            diff = rvals[r] - pooled_p
            marker = "+" if diff > 0.02 else "-" if diff < -0.02 else " "
            print(f"  {rvals[r]:>4.3f}{marker}", end='')
        print(f"  {max_dev:>7.3f}")

    # =========================================================
    # Summary
    # =========================================================
    print(f"\n{'='*70}")
    print(f"REGIME-CONDITIONED AUTOMATON SUMMARY")
    print(f"{'='*70}")

    n_sig = sum(1 for rt in row_tests if rt['significant'])
    print(f"\n  Global chi2: {chi2_global:.1f} (p={p_global:.2e})")
    print(f"  Per-source-state: {n_sig}/{N_STATES} show significant REGIME dependence")
    for rt in row_tests:
        if rt['significant']:
            print(f"    {rt['state']:>8}: chi2={rt['chi2']:.1f}, p={rt['p']:.2e}")

    if p_global < 0.001:
        verdict = "REGIME_DEPENDENT"
        print(f"\n  VERDICT: {verdict}")
        print(f"  The 6-state automaton's transition probabilities ARE")
        print(f"  significantly conditioned by REGIME. The macro-state")
        print(f"  topology is shared, but the probability weights shift.")
    elif p_global < 0.05:
        verdict = "WEAKLY_REGIME_DEPENDENT"
        print(f"\n  VERDICT: {verdict}")
        print(f"  Marginal REGIME dependence detected.")
    else:
        verdict = "REGIME_INDEPENDENT"
        print(f"\n  VERDICT: {verdict}")
        print(f"  The 6-state automaton is REGIME-invariant.")

    # Save
    results = {
        'test': 'T8_regime_conditioned',
        'n_regimes': len(regimes),
        'regimes': regimes,
        'regime_token_counts': {str(r): int(regime_token_counts[r]) for r in regimes},
        'regime_transition_counts': {str(r): int(regime_transitions[r].sum()) for r in regimes},
        'per_regime_matrix': {str(r): regime_probs[r].tolist() for r in regimes},
        'global_chi2': round(float(chi2_global), 2),
        'global_p': float(p_global),
        'global_dof': int(dof_global),
        'per_source_tests': row_tests,
        'n_significant_sources': n_sig,
        'verdict': verdict,
        'top_shifted_transitions': [
            {
                'from': STATE_LABELS[i],
                'to': STATE_LABELS[j],
                'pooled': round(float(pooled_p), 4),
                'max_deviation': round(float(max_dev), 4),
                'per_regime': {str(r): round(float(v), 4) for r, v in rvals.items()},
            }
            for i, j, pooled_p, max_dev, rvals in deviations[:15]
        ],
    }

    with open(RESULTS_DIR / 't8_regime_conditioned.json', 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved to {RESULTS_DIR / 't8_regime_conditioned.json'}")


if __name__ == '__main__':
    run()
