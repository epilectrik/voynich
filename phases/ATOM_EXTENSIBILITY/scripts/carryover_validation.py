"""
CARRYOVER VALIDATION: Is the state carry-over signal real?
==========================================================
Validates C1200 against potential confounds.

Possible false positives:
  1. Base rate artifact — e is common as initial, k as terminal; independence baseline
  2. High-frequency MIDDLE dominance — a few common bigrams drive the whole signal
  3. Section confound — sections have different k/e balances
  4. Distance decay — real state should decay with token distance
  5. Line position confound — initial/final tokens have special properties
  6. Within-MIDDLE autocorrelation — MIDDLEs containing both k and e create self-transitions

Validation tests:
  V1: Independence baseline (marginal rates vs observed)
  V2: Per-line shuffle test (break sequence, preserve composition)
  V3: Section-stratified carryover (compute per section)
  V4: Distance decay (adjacent, skip-1, skip-2)
  V5: Frequency control (remove top-N MIDDLEs, retest)
  V6: Interior-only test (exclude line-initial and line-final tokens)
"""
import json
import sys
import math
import random
from collections import defaultdict, Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.voynich import Transcript, Morphology

RESULTS_DIR = Path("phases/ATOM_EXTENSIBILITY/results")
N_PERMUTATIONS = 2000


def load_tokens_by_line():
    """Load Currier B tokens grouped by folio+line, preserving order."""
    tx = Transcript()
    morph = Morphology()
    line_groups = defaultdict(list)
    for t in tx.currier_b():
        m = morph.extract(t.word)
        if m.middle and m.middle != '_EMPTY_':
            key = (t.folio, t.line)
            line_groups[key].append({
                'word': t.word,
                'middle': m.middle,
                'folio': t.folio,
                'line': t.line,
                'section': t.section,
            })
    return line_groups


def compute_carryover(transitions):
    """Compute k/e carryover signal from a list of (terminal_char, initial_char) pairs."""
    ke_trans = Counter()
    for a, b in transitions:
        if a in ('k', 'e') and b in ('k', 'e'):
            ke_trans[(a, b)] += 1

    total_k = ke_trans[('k', 'k')] + ke_trans[('k', 'e')]
    total_e = ke_trans[('e', 'k')] + ke_trans[('e', 'e')]

    if total_k < 5 or total_e < 5:
        return None

    p_e_after_k = ke_trans[('k', 'e')] / total_k
    p_e_after_e = ke_trans[('e', 'e')] / total_e
    p_k_after_e = ke_trans[('e', 'k')] / total_e
    p_k_after_k = ke_trans[('k', 'k')] / total_k

    carryover = (p_e_after_k - p_e_after_e) + (p_k_after_e - p_k_after_k)
    return {
        'carryover': carryover,
        'p_e_after_k': p_e_after_k,
        'p_e_after_e': p_e_after_e,
        'p_k_after_e': p_k_after_e,
        'p_k_after_k': p_k_after_k,
        'n_ke_transitions': total_k + total_e,
    }


def get_within_line_transitions(line_groups, skip=0):
    """Get transitions with optional skip distance."""
    transitions = []
    for key in sorted(line_groups.keys()):
        tokens = line_groups[key]
        for i in range(len(tokens) - 1 - skip):
            m1 = tokens[i]['middle']
            m2 = tokens[i + 1 + skip]['middle']
            if m1 and m2:
                transitions.append((m1[-1], m2[0]))
    return transitions


# ============================================================
# V1: INDEPENDENCE BASELINE
# ============================================================

def validate_independence(line_groups):
    """Test if carryover exceeds what marginal rates predict."""
    print("=" * 70)
    print("V1: INDEPENDENCE BASELINE")
    print("=" * 70)

    transitions = get_within_line_transitions(line_groups)
    terminals = [a for a, _ in transitions]
    initials = [b for _, b in transitions]

    # Marginal rates
    term_counts = Counter(terminals)
    init_counts = Counter(initials)
    n = len(transitions)

    p_term_k = term_counts.get('k', 0) / n
    p_term_e = term_counts.get('e', 0) / n
    p_init_k = init_counts.get('k', 0) / n
    p_init_e = init_counts.get('e', 0) / n

    print(f"\n  Marginal rates:")
    print(f"    P(terminal=k) = {p_term_k:.3f}  ({term_counts.get('k', 0)} of {n})")
    print(f"    P(terminal=e) = {p_term_e:.3f}  ({term_counts.get('e', 0)} of {n})")
    print(f"    P(initial=k)  = {p_init_k:.3f}  ({init_counts.get('k', 0)} of {n})")
    print(f"    P(initial=e)  = {p_init_e:.3f}  ({init_counts.get('e', 0)} of {n})")

    # Under independence, P(init=e | term=k) = P(init=e) = p_init_e
    # Observed: P(init=e | term=k) from compute_carryover
    result = compute_carryover(transitions)

    print(f"\n  Under INDEPENDENCE:")
    print(f"    P(starts-e | ends-k) should = P(starts-e) = {p_init_e:.3f}")
    print(f"    P(starts-e | ends-e) should = P(starts-e) = {p_init_e:.3f}")

    print(f"\n  OBSERVED:")
    print(f"    P(starts-e | ends-k) = {result['p_e_after_k']:.3f} (expected {p_init_e:.3f})")
    print(f"    P(starts-e | ends-e) = {result['p_e_after_e']:.3f} (expected {p_init_e:.3f})")

    excess_k = result['p_e_after_k'] - p_init_e
    excess_e = result['p_e_after_e'] - p_init_e

    print(f"\n  Excess over independence:")
    print(f"    After k: {excess_k:+.3f} ({'MORE e than expected' if excess_k > 0 else 'LESS e than expected'})")
    print(f"    After e: {excess_e:+.3f} ({'MORE e than expected' if excess_e > 0 else 'LESS e than expected'})")

    if excess_k > 0 and excess_e < 0:
        print(f"  VERDICT: GENUINE — after k, e appears more than baseline; after e, e appears less.")
    elif excess_k > 0 and excess_e > 0:
        print(f"  VERDICT: PARTIALLY CONFOUNDED — both exceed baseline, but k more so.")
    else:
        print(f"  VERDICT: SUSPICIOUS — pattern doesn't match carryover prediction.")

    return {
        'p_term_k': round(p_term_k, 4),
        'p_term_e': round(p_term_e, 4),
        'p_init_e': round(p_init_e, 4),
        'excess_after_k': round(excess_k, 4),
        'excess_after_e': round(excess_e, 4),
        'observed': result,
    }


# ============================================================
# V2: PER-LINE SHUFFLE TEST
# ============================================================

def validate_shuffle(line_groups):
    """Shuffle MIDDLEs within each line, preserving composition but breaking sequence."""
    print("\n" + "=" * 70)
    print("V2: PER-LINE SHUFFLE TEST")
    print("=" * 70)

    # Observed carryover
    obs_transitions = get_within_line_transitions(line_groups)
    obs_result = compute_carryover(obs_transitions)
    obs_signal = obs_result['carryover']

    print(f"\n  Observed carryover: {obs_signal:+.3f}")
    print(f"  Running {N_PERMUTATIONS} within-line shuffles...")

    # Shuffle: within each line, randomize order of MIDDLEs
    perm_signals = []
    random.seed(42)
    for perm_i in range(N_PERMUTATIONS):
        transitions = []
        for key in sorted(line_groups.keys()):
            tokens = list(line_groups[key])
            middles = [t['middle'] for t in tokens]
            random.shuffle(middles)
            for i in range(len(middles) - 1):
                m1, m2 = middles[i], middles[i+1]
                if m1 and m2:
                    transitions.append((m1[-1], m2[0]))
        result = compute_carryover(transitions)
        if result:
            perm_signals.append(result['carryover'])

    p_value = sum(1 for s in perm_signals if s >= obs_signal) / len(perm_signals)
    mean_perm = sum(perm_signals) / len(perm_signals)
    std_perm = (sum((s - mean_perm)**2 for s in perm_signals) / len(perm_signals))**0.5
    z_score = (obs_signal - mean_perm) / std_perm if std_perm > 0 else 0

    print(f"  Permutation null: mean={mean_perm:+.4f}, std={std_perm:.4f}")
    print(f"  Observed: {obs_signal:+.4f}")
    print(f"  Z-score: {z_score:.2f}")
    print(f"  p-value: {p_value:.4f}")

    if p_value < 0.01:
        print(f"  VERDICT: SIGNAL SURVIVES SHUFFLE (p={p_value:.4f}) — not a composition artifact")
    elif p_value < 0.05:
        print(f"  VERDICT: MARGINAL (p={p_value:.4f}) — weak evidence")
    else:
        print(f"  VERDICT: FAILS SHUFFLE (p={p_value:.4f}) — could be composition artifact")

    return {
        'observed': round(obs_signal, 4),
        'perm_mean': round(mean_perm, 4),
        'perm_std': round(std_perm, 4),
        'z_score': round(z_score, 2),
        'p_value': p_value,
    }


# ============================================================
# V3: SECTION-STRATIFIED CARRYOVER
# ============================================================

def validate_section_stratified(line_groups):
    """Compute carryover per section to check if signal is universal or section-specific."""
    print("\n" + "=" * 70)
    print("V3: SECTION-STRATIFIED CARRYOVER")
    print("=" * 70)

    section_lines = defaultdict(dict)
    for key, tokens in line_groups.items():
        if tokens:
            sec = tokens[0]['section']
            section_lines[sec][key] = tokens

    print(f"\n  {'Section':<12} {'Lines':<8} {'k/e trans':<12} {'Carryover':<12} {'Verdict'}")
    print(f"  {'-'*60}")

    section_results = {}
    for sec in sorted(section_lines):
        transitions = get_within_line_transitions(section_lines[sec])
        result = compute_carryover(transitions)
        n_lines = len(section_lines[sec])

        if result:
            verdict = "SUPPORTS" if result['carryover'] > 0.05 else "WEAK" if result['carryover'] > 0 else "AGAINST"
            print(f"  {sec:<12} {n_lines:<8} {result['n_ke_transitions']:<12} "
                  f"{result['carryover']:+.3f}       {verdict}")
            section_results[sec] = {
                'n_lines': n_lines,
                'carryover': round(result['carryover'], 4),
                'n_ke_transitions': result['n_ke_transitions'],
            }
        else:
            print(f"  {sec:<12} {n_lines:<8} insufficient")

    # Is it universal?
    positive = sum(1 for v in section_results.values() if v['carryover'] > 0)
    total = len(section_results)
    print(f"\n  Sections with positive carryover: {positive}/{total}")
    if positive == total:
        print(f"  VERDICT: UNIVERSAL — carryover present in every section")
    elif positive >= total * 0.75:
        print(f"  VERDICT: NEAR-UNIVERSAL — present in most sections")
    else:
        print(f"  VERDICT: SECTION-SPECIFIC — not universal, may be confound")

    return section_results


# ============================================================
# V4: DISTANCE DECAY
# ============================================================

def validate_distance_decay(line_groups):
    """Test if carryover decays with token distance (adjacent > skip-1 > skip-2)."""
    print("\n" + "=" * 70)
    print("V4: DISTANCE DECAY")
    print("=" * 70)

    distances = {}
    for skip in range(5):
        transitions = get_within_line_transitions(line_groups, skip=skip)
        result = compute_carryover(transitions)
        if result:
            distances[skip] = {
                'carryover': round(result['carryover'], 4),
                'n_transitions': result['n_ke_transitions'],
            }

    print(f"\n  {'Distance':<12} {'k/e trans':<12} {'Carryover':<12}")
    print(f"  {'-'*40}")
    for skip in sorted(distances):
        d = distances[skip]
        label = "adjacent" if skip == 0 else f"skip-{skip}"
        print(f"  {label:<12} {d['n_transitions']:<12} {d['carryover']:+.4f}")

    # Check monotonic decay
    signals = [distances[s]['carryover'] for s in sorted(distances)]
    monotonic = all(signals[i] >= signals[i+1] for i in range(len(signals)-1))
    decay_ratio = signals[-1] / signals[0] if signals[0] != 0 else 0

    print(f"\n  Monotonically decaying: {monotonic}")
    print(f"  Decay ratio (skip-4 / adjacent): {decay_ratio:.2f}")

    if monotonic and signals[0] > 0.1 and decay_ratio < 0.5:
        print(f"  VERDICT: CLEAN DECAY — signal strongest at adjacent, fades with distance")
    elif signals[0] > 0.1 and not monotonic:
        print(f"  VERDICT: NON-MONOTONIC — signal present but doesn't decay cleanly")
    else:
        print(f"  VERDICT: WEAK/ABSENT — no clear distance effect")

    return distances


# ============================================================
# V5: FREQUENCY CONTROL
# ============================================================

def validate_frequency_control(line_groups):
    """Remove top-N most common MIDDLEs and retest."""
    print("\n" + "=" * 70)
    print("V5: FREQUENCY CONTROL")
    print("=" * 70)

    # Count all MIDDLEs
    all_middles = Counter()
    for tokens in line_groups.values():
        for t in tokens:
            all_middles[t['middle']] += 1

    top_middles = [m for m, _ in all_middles.most_common(20)]
    print(f"\n  Top 20 MIDDLEs: {', '.join(f'{m}({all_middles[m]})' for m in top_middles[:10])}...")

    for n_remove in [0, 5, 10, 20, 50]:
        excluded = set(m for m, _ in all_middles.most_common(n_remove)) if n_remove > 0 else set()

        transitions = []
        for key in sorted(line_groups.keys()):
            tokens = line_groups[key]
            # Filter out excluded MIDDLEs but preserve adjacency
            filtered = [t for t in tokens if t['middle'] not in excluded]
            for i in range(len(filtered) - 1):
                m1, m2 = filtered[i]['middle'], filtered[i+1]['middle']
                if m1 and m2:
                    transitions.append((m1[-1], m2[0]))

        result = compute_carryover(transitions)
        if result:
            print(f"  Exclude top-{n_remove:>2}: carryover={result['carryover']:+.3f} "
                  f"({result['n_ke_transitions']} k/e transitions)")
        else:
            print(f"  Exclude top-{n_remove:>2}: insufficient k/e transitions")

    # Also test: exclude all MIDDLEs that are purely k or purely e
    # (to see if signal comes from mixed vs pure MIDDLEs)
    pure_ke = set()
    for m in all_middles:
        chars = set(m)
        if chars <= {'k', 'e'}:
            pure_ke.add(m)

    transitions_no_pure = []
    for key in sorted(line_groups.keys()):
        tokens = line_groups[key]
        filtered = [t for t in tokens if t['middle'] not in pure_ke]
        for i in range(len(filtered) - 1):
            m1, m2 = filtered[i]['middle'], filtered[i+1]['middle']
            if m1 and m2:
                transitions_no_pure.append((m1[-1], m2[0]))

    result_no_pure = compute_carryover(transitions_no_pure)
    if result_no_pure:
        print(f"\n  Exclude ALL pure k/e MIDDLEs ({len(pure_ke)} types): "
              f"carryover={result_no_pure['carryover']:+.3f} "
              f"({result_no_pure['n_ke_transitions']} k/e transitions)")
        print(f"  (Signal from k/e as terminal/initial atoms in NON-k/e MIDDLEs)")

    return {}


# ============================================================
# V6: INTERIOR-ONLY TEST
# ============================================================

def validate_interior_only(line_groups):
    """Exclude line-initial and line-final tokens to control for boundary effects."""
    print("\n" + "=" * 70)
    print("V6: INTERIOR-ONLY TEST (exclude line boundaries)")
    print("=" * 70)

    # Full signal
    full_transitions = get_within_line_transitions(line_groups)
    full_result = compute_carryover(full_transitions)

    # Interior only: exclude first and last token of each line
    interior_transitions = []
    for key in sorted(line_groups.keys()):
        tokens = line_groups[key]
        if len(tokens) < 4:  # Need at least 4 tokens for 2 interior tokens
            continue
        interior = tokens[1:-1]  # Exclude first and last
        for i in range(len(interior) - 1):
            m1, m2 = interior[i]['middle'], interior[i+1]['middle']
            if m1 and m2:
                interior_transitions.append((m1[-1], m2[0]))

    int_result = compute_carryover(interior_transitions)

    # Boundary-only: transitions involving line-initial or line-final tokens
    boundary_transitions = []
    for key in sorted(line_groups.keys()):
        tokens = line_groups[key]
        if len(tokens) < 2:
            continue
        # First pair (line-initial -> second)
        m1, m2 = tokens[0]['middle'], tokens[1]['middle']
        if m1 and m2:
            boundary_transitions.append((m1[-1], m2[0]))
        # Last pair (penultimate -> line-final)
        if len(tokens) >= 2:
            m1, m2 = tokens[-2]['middle'], tokens[-1]['middle']
            if m1 and m2:
                boundary_transitions.append((m1[-1], m2[0]))

    bnd_result = compute_carryover(boundary_transitions)

    print(f"\n  {'Zone':<18} {'k/e trans':<12} {'Carryover':<12}")
    print(f"  {'-'*45}")
    if full_result:
        print(f"  {'Full line':<18} {full_result['n_ke_transitions']:<12} "
              f"{full_result['carryover']:+.3f}")
    if int_result:
        print(f"  {'Interior only':<18} {int_result['n_ke_transitions']:<12} "
              f"{int_result['carryover']:+.3f}")
    if bnd_result:
        print(f"  {'Boundary only':<18} {bnd_result['n_ke_transitions']:<12} "
              f"{bnd_result['carryover']:+.3f}")

    if int_result and full_result:
        if int_result['carryover'] > 0.1:
            print(f"\n  VERDICT: INTERIOR SIGNAL STRONG — not a boundary artifact")
        elif int_result['carryover'] > 0.05:
            print(f"\n  VERDICT: INTERIOR SIGNAL PRESENT but weaker — partial boundary effect")
        else:
            print(f"\n  VERDICT: BOUNDARY-DOMINATED — signal may be a line-position artifact")

    return {
        'full': {'carryover': round(full_result['carryover'], 4),
                 'n': full_result['n_ke_transitions']} if full_result else None,
        'interior': {'carryover': round(int_result['carryover'], 4),
                     'n': int_result['n_ke_transitions']} if int_result else None,
        'boundary': {'carryover': round(bnd_result['carryover'], 4),
                     'n': bnd_result['n_ke_transitions']} if bnd_result else None,
    }


# ============================================================
# MAIN
# ============================================================

def main():
    print("CARRYOVER VALIDATION — Is C1200 Real?")
    print("=" * 70)

    print("\nLoading data...")
    line_groups = load_tokens_by_line()
    n_tokens = sum(len(v) for v in line_groups.values())
    print(f"Loaded {n_tokens} tokens across {len(line_groups)} lines")

    results = {}
    results['V1_independence'] = validate_independence(line_groups)
    results['V2_shuffle'] = validate_shuffle(line_groups)
    results['V3_section_stratified'] = validate_section_stratified(line_groups)
    results['V4_distance_decay'] = validate_distance_decay(line_groups)
    results['V5_frequency_control'] = validate_frequency_control(line_groups)
    results['V6_interior_only'] = validate_interior_only(line_groups)

    # Final verdict
    print("\n" + "=" * 70)
    print("FINAL VALIDATION SUMMARY")
    print("=" * 70)

    checks = []
    # V1
    v1 = results['V1_independence']
    v1_pass = v1['excess_after_k'] > 0 and v1['excess_after_e'] < 0
    checks.append(('V1 Independence', v1_pass))

    # V2
    v2 = results['V2_shuffle']
    v2_pass = v2['p_value'] < 0.01
    checks.append(('V2 Shuffle', v2_pass))

    # V3
    v3 = results['V3_section_stratified']
    v3_positive = sum(1 for v in v3.values() if isinstance(v, dict) and v.get('carryover', 0) > 0)
    v3_pass = v3_positive >= len(v3) * 0.75
    checks.append(('V3 Section-universal', v3_pass))

    # V4
    v4 = results['V4_distance_decay']
    if 0 in v4 and max(v4.keys()) in v4:
        v4_pass = v4[0]['carryover'] > v4[max(v4.keys())]['carryover'] and v4[0]['carryover'] > 0.1
    else:
        v4_pass = False
    checks.append(('V4 Distance decay', v4_pass))

    # V6
    v6 = results['V6_interior_only']
    v6_pass = v6.get('interior', {}).get('carryover', 0) > 0.1
    checks.append(('V6 Interior signal', v6_pass))

    print()
    passed = 0
    for name, ok in checks:
        status = "PASS" if ok else "FAIL"
        print(f"  [{status}] {name}")
        if ok:
            passed += 1

    print(f"\n  Result: {passed}/{len(checks)} validation checks passed")
    if passed == len(checks):
        print(f"  CONCLUSION: C1200 is VALIDATED — carryover signal is real")
    elif passed >= len(checks) - 1:
        print(f"  CONCLUSION: C1200 is LIKELY REAL — one check marginal")
    elif passed >= len(checks) // 2:
        print(f"  CONCLUSION: C1200 is UNCERTAIN — mixed evidence")
    else:
        print(f"  CONCLUSION: C1200 is LIKELY ARTIFACT — most checks fail")

    output_path = RESULTS_DIR / "carryover_validation.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\n  Results saved to {output_path}")


if __name__ == '__main__':
    main()
