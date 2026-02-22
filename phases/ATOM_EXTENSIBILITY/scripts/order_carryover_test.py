"""
ORDER CARRYOVER TEST: Does atom ordering encode procedural state?
================================================================
Extension to Phase 425 (ATOM_EXTENSIBILITY)

Hypothesis: If a step leaves material in a "hot" state (MIDDLE ends with k),
the next step should cool first (next MIDDLE starts with e). And vice versa.

This tests whether atom ORDER within MIDDLEs carries procedural information
that distributional profiles (C1198) cannot detect.

Tests:
  T6a: Terminal-to-initial transition bias (does last atom of MIDDLE N
       predict first atom of MIDDLE N+1?)
  T6b: k/e family ordering context (do ke vs ek tokens differ in what
       MIDDLE preceded them?)
  T6c: Full transition matrix for all atom pairs across MIDDLE boundaries
  T6d: Within-line vs across-line transitions (procedural state should
       carry within a line but reset at line boundaries)
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
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

N_PERMUTATIONS = 1000


def load_tokens_by_line():
    """Load Currier B tokens grouped by folio+line, preserving order."""
    tx = Transcript()
    morph = Morphology()

    # Group tokens by (folio, line) in order
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


def get_transitions(line_groups, within_line_only=True):
    """Extract consecutive MIDDLE pairs from lines.
    Returns list of (prev_middle, next_middle) tuples.
    """
    pairs = []
    if within_line_only:
        for key in sorted(line_groups.keys()):
            tokens = line_groups[key]
            for i in range(len(tokens) - 1):
                pairs.append((tokens[i]['middle'], tokens[i+1]['middle']))
    else:
        # All consecutive tokens across lines within same folio
        folio_groups = defaultdict(list)
        for key in sorted(line_groups.keys()):
            folio = key[0]
            folio_groups[folio].extend(line_groups[key])
        for folio in sorted(folio_groups.keys()):
            tokens = folio_groups[folio]
            for i in range(len(tokens) - 1):
                pairs.append((tokens[i]['middle'], tokens[i+1]['middle']))
    return pairs


# ============================================================
# T6a: TERMINAL-TO-INITIAL TRANSITION BIAS
# ============================================================

def test_terminal_initial_bias(pairs):
    """Test whether the last atom of MIDDLE N predicts the first atom of MIDDLE N+1."""
    print("=" * 70)
    print("T6a: TERMINAL-TO-INITIAL TRANSITION BIAS")
    print("=" * 70)

    # For each pair, extract (last char of prev, first char of next)
    transitions = []
    for prev, nxt in pairs:
        if prev and nxt:
            transitions.append((prev[-1], nxt[0]))

    n = len(transitions)
    print(f"\nTotal within-line MIDDLE transitions: {n}")

    # Count transition frequencies
    trans_counts = Counter(transitions)

    # Focus on k/e transitions
    ke_atoms = {'k', 'e'}
    ke_transitions = {(a, b): 0 for a in ke_atoms for b in ke_atoms}
    for (a, b), c in trans_counts.items():
        if a in ke_atoms and b in ke_atoms:
            ke_transitions[(a, b)] = c

    print(f"\n  k/e TERMINAL -> INITIAL transitions:")
    header = 'From / To'
    print(f"  {header:<12} {'-> k':<10} {'-> e':<10} {'Total':<10} {'% -> e':<10}")
    print(f"  {'-'*50}")

    for source in ['k', 'e']:
        to_k = ke_transitions[(source, 'k')]
        to_e = ke_transitions[(source, 'e')]
        total = to_k + to_e
        pct_e = to_e / total if total > 0 else 0
        print(f"  ends {source:<8} {to_k:<10} {to_e:<10} {total:<10} {pct_e:.1%}")

    # State carryover hypothesis:
    # If material is left hot (ends k), next should cool first (starts e)
    # If material is left cool (ends e), next should heat first (starts k)
    # This means: ends-k -> starts-e should be HIGHER than ends-e -> starts-e
    # And: ends-e -> starts-k should be HIGHER than ends-k -> starts-k

    total_ends_k = ke_transitions[('k', 'k')] + ke_transitions[('k', 'e')]
    total_ends_e = ke_transitions[('e', 'k')] + ke_transitions[('e', 'e')]

    if total_ends_k > 0 and total_ends_e > 0:
        p_e_after_k = ke_transitions[('k', 'e')] / total_ends_k
        p_e_after_e = ke_transitions[('e', 'e')] / total_ends_e
        p_k_after_e = ke_transitions[('e', 'k')] / total_ends_e
        p_k_after_k = ke_transitions[('k', 'k')] / total_ends_k

        print(f"\n  STATE CARRYOVER TEST:")
        print(f"  P(starts-e | ends-k) = {p_e_after_k:.3f}  (hot -> should cool)")
        print(f"  P(starts-e | ends-e) = {p_e_after_e:.3f}  (cool -> no urgency to cool)")
        print(f"  Difference: {p_e_after_k - p_e_after_e:+.3f}")
        print()
        print(f"  P(starts-k | ends-e) = {p_k_after_e:.3f}  (cool -> should heat)")
        print(f"  P(starts-k | ends-k) = {p_k_after_k:.3f}  (hot -> no urgency to heat)")
        print(f"  Difference: {p_k_after_e - p_k_after_k:+.3f}")

        # Carryover signal: both differences should be positive
        carryover_e = p_e_after_k - p_e_after_e
        carryover_k = p_k_after_e - p_k_after_k
        print(f"\n  Carryover signal (e): {carryover_e:+.3f} {'(SUPPORTS)' if carryover_e > 0 else '(AGAINST)'}")
        print(f"  Carryover signal (k): {carryover_k:+.3f} {'(SUPPORTS)' if carryover_k > 0 else '(AGAINST)'}")
    else:
        p_e_after_k = p_e_after_e = p_k_after_e = p_k_after_k = 0
        carryover_e = carryover_k = 0

    # Broader: all atoms — build full transition matrix
    all_atoms = sorted(set(a for a, _ in transitions) | set(b for _, b in transitions))

    # Compute expected frequencies under independence
    source_counts = Counter(a for a, _ in transitions)
    target_counts = Counter(b for _, b in transitions)

    # Chi-squared test for independence
    chi2 = 0
    df = 0
    for a in all_atoms:
        for b in all_atoms:
            obs = trans_counts.get((a, b), 0)
            exp = source_counts[a] * target_counts[b] / n if n > 0 else 0
            if exp > 5:  # Only count cells with sufficient expected
                chi2 += (obs - exp) ** 2 / exp
                df += 1
    df = max(df - len(all_atoms) * 2 + 1, 1)  # Approximate df

    print(f"\n  Full transition matrix chi-squared: {chi2:.1f} (df~{df})")
    print(f"  Transitions are {'DEPENDENT' if chi2 > 2 * df else 'INDEPENDENT'}")

    # Permutation test for k/e carryover specifically
    observed_carryover = carryover_e + carryover_k  # Combined signal

    perm_count = 0
    random.seed(42)
    transition_list = list(transitions)
    for _ in range(N_PERMUTATIONS):
        # Shuffle targets while keeping sources fixed
        sources = [a for a, _ in transition_list]
        targets = [b for _, b in transition_list]
        random.shuffle(targets)

        perm_ke = {(a, b): 0 for a in ke_atoms for b in ke_atoms}
        for a, b in zip(sources, targets):
            if a in ke_atoms and b in ke_atoms:
                perm_ke[(a, b)] += 1

        p_ek = perm_ke[('k', 'k')] + perm_ke[('k', 'e')]
        p_ee_total = perm_ke[('e', 'k')] + perm_ke[('e', 'e')]

        if p_ek > 0 and p_ee_total > 0:
            perm_e_after_k = perm_ke[('k', 'e')] / p_ek
            perm_e_after_e = perm_ke[('e', 'e')] / p_ee_total
            perm_k_after_e = perm_ke[('e', 'k')] / p_ee_total
            perm_k_after_k = perm_ke[('k', 'k')] / p_ek
            perm_signal = (perm_e_after_k - perm_e_after_e) + (perm_k_after_e - perm_k_after_k)
        else:
            perm_signal = 0

        if perm_signal >= observed_carryover:
            perm_count += 1

    p_value = perm_count / N_PERMUTATIONS
    print(f"\n  k/e carryover permutation test: p={p_value:.4f}")
    print(f"  Observed combined carryover: {observed_carryover:+.3f}")

    return {
        'n_transitions': n,
        'ke_transitions': {f"{a}->{b}": c for (a, b), c in ke_transitions.items()},
        'p_e_after_k': round(p_e_after_k, 4),
        'p_e_after_e': round(p_e_after_e, 4),
        'p_k_after_e': round(p_k_after_e, 4),
        'p_k_after_k': round(p_k_after_k, 4),
        'carryover_e': round(carryover_e, 4),
        'carryover_k': round(carryover_k, 4),
        'chi2': round(chi2, 1),
        'p_value': p_value,
    }


# ============================================================
# T6b: k/e ORDERING CONTEXT
# ============================================================

def test_ke_ordering_context(line_groups):
    """Test whether ke vs ek tokens differ in what MIDDLE preceded them."""
    print("\n" + "=" * 70)
    print("T6b: ke vs ek PRECEDING CONTEXT")
    print("=" * 70)

    # For every occurrence of ke and ek, what was the previous MIDDLE?
    ke_prev = []  # MIDDLEs that appear before 'ke'
    ek_prev = []  # MIDDLEs that appear before 'ek'

    # Also for kee vs eek
    kee_prev = []
    eek_prev = []

    for key in sorted(line_groups.keys()):
        tokens = line_groups[key]
        for i in range(1, len(tokens)):
            mid = tokens[i]['middle']
            prev_mid = tokens[i-1]['middle']
            if mid == 'ke':
                ke_prev.append(prev_mid)
            elif mid == 'ek':
                ek_prev.append(prev_mid)
            elif mid == 'kee':
                kee_prev.append(prev_mid)
            elif mid == 'eek':
                eek_prev.append(prev_mid)

    def analyze_preceding(middles_list, label):
        if not middles_list:
            print(f"\n  {label}: no preceding tokens found")
            return {}
        n = len(middles_list)

        # What fraction of predecessors end with k vs e?
        ends_k = sum(1 for m in middles_list if m and m[-1] == 'k')
        ends_e = sum(1 for m in middles_list if m and m[-1] == 'e')
        ends_other = n - ends_k - ends_e

        # What fraction contain k vs e at all?
        has_k = sum(1 for m in middles_list if 'k' in m)
        has_e = sum(1 for m in middles_list if 'e' in m)

        print(f"\n  {label} (n={n}):")
        print(f"    Predecessor ends with k: {ends_k} ({ends_k/n:.1%})")
        print(f"    Predecessor ends with e: {ends_e} ({ends_e/n:.1%})")
        print(f"    Predecessor ends other:  {ends_other} ({ends_other/n:.1%})")
        print(f"    Predecessor contains k:  {has_k} ({has_k/n:.1%})")
        print(f"    Predecessor contains e:  {has_e} ({has_e/n:.1%})")

        return {
            'n': n,
            'ends_k': ends_k,
            'ends_e': ends_e,
            'ends_other': ends_other,
            'pct_ends_k': round(ends_k / n, 4),
            'pct_ends_e': round(ends_e / n, 4),
        }

    print(f"\nDoes the previous MIDDLE's terminal state predict ke vs ek ordering?")
    print(f"Carryover hypothesis: predecessors ending in k -> next starts with e (=ek)")
    print(f"                      predecessors ending in e -> next starts with k (=ke)")

    ke_stats = analyze_preceding(ke_prev, "Before KE (starts with k)")
    ek_stats = analyze_preceding(ek_prev, "Before EK (starts with e)")
    kee_stats = analyze_preceding(kee_prev, "Before KEE (starts with k)")
    eek_stats = analyze_preceding(eek_prev, "Before EEK (starts with e)")

    # The carryover prediction:
    # Before ek (starts-e): predecessor should end in k more often
    # Before ke (starts-k): predecessor should end in e more often
    if ke_stats and ek_stats:
        print(f"\n  --- CARRYOVER PREDICTION ---")
        print(f"  Before EK (cool-first): {ek_stats.get('pct_ends_k', 0):.1%} predecessors end in k")
        print(f"  Before KE (heat-first): {ke_stats.get('pct_ends_k', 0):.1%} predecessors end in k")
        diff = ek_stats.get('pct_ends_k', 0) - ke_stats.get('pct_ends_k', 0)
        print(f"  Difference: {diff:+.3f} ({'SUPPORTS' if diff > 0 else 'AGAINST'} carryover)")

        print(f"\n  Before KE (heat-first): {ke_stats.get('pct_ends_e', 0):.1%} predecessors end in e")
        print(f"  Before EK (cool-first): {ek_stats.get('pct_ends_e', 0):.1%} predecessors end in e")
        diff2 = ke_stats.get('pct_ends_e', 0) - ek_stats.get('pct_ends_e', 0)
        print(f"  Difference: {diff2:+.3f} ({'SUPPORTS' if diff2 > 0 else 'AGAINST'} carryover)")

    return {
        'ke': ke_stats,
        'ek': ek_stats,
        'kee': kee_stats,
        'eek': eek_stats,
    }


# ============================================================
# T6c: FULL TRANSITION MATRIX (k/e focused)
# ============================================================

def test_transition_matrix(pairs):
    """Build and analyze the full k/e transition matrix across MIDDLE boundaries."""
    print("\n" + "=" * 70)
    print("T6c: FULL k/e TRANSITION MATRIX")
    print("=" * 70)

    # For each consecutive pair, classify by k/e content
    # Categories: K-dominant (more k than e), E-dominant (more e than k),
    #             Balanced (equal k and e), Neither (no k or e)
    def classify_ke(middle):
        k_count = middle.count('k')
        e_count = middle.count('e')
        if k_count == 0 and e_count == 0:
            return 'NEITHER'
        elif k_count > e_count:
            return 'K-DOM'
        elif e_count > k_count:
            return 'E-DOM'
        else:
            return 'BALANCED'

    trans = Counter()
    for prev, nxt in pairs:
        cat_prev = classify_ke(prev)
        cat_nxt = classify_ke(nxt)
        trans[(cat_prev, cat_nxt)] += 1

    categories = ['K-DOM', 'BALANCED', 'E-DOM', 'NEITHER']
    n = sum(trans.values())

    print(f"\n  Transition matrix (row=previous, col=next):")
    col_header = 'From / To'
    print(f"  {col_header:<12}", end='')
    for cat in categories:
        print(f"  {cat:<10}", end='')
    print(f"  {'Total':<8}  {'Self%':<8}")

    row_totals = {}
    for cat_from in categories:
        row_total = sum(trans.get((cat_from, cat_to), 0) for cat_to in categories)
        row_totals[cat_from] = row_total
        print(f"  {cat_from:<12}", end='')
        for cat_to in categories:
            c = trans.get((cat_from, cat_to), 0)
            pct = c / row_total if row_total > 0 else 0
            print(f"  {c:>5} {pct:>4.0%}", end='')
        self_c = trans.get((cat_from, cat_from), 0)
        self_pct = self_c / row_total if row_total > 0 else 0
        print(f"  {row_total:<8}  {self_pct:.1%}")

    # Key test: do K-DOM -> E-DOM transitions exceed K-DOM -> K-DOM?
    # (i.e., after a heat-heavy step, does the system preferentially cool?)
    k_to_e = trans.get(('K-DOM', 'E-DOM'), 0)
    k_to_k = trans.get(('K-DOM', 'K-DOM'), 0)
    e_to_k = trans.get(('E-DOM', 'K-DOM'), 0)
    e_to_e = trans.get(('E-DOM', 'E-DOM'), 0)

    k_total = row_totals.get('K-DOM', 0)
    e_total = row_totals.get('E-DOM', 0)

    print(f"\n  ALTERNATION TEST:")
    if k_total > 0 and e_total > 0:
        p_e_after_k = k_to_e / k_total
        p_k_after_k = k_to_k / k_total
        p_k_after_e = e_to_k / e_total
        p_e_after_e = e_to_e / e_total

        print(f"  After K-DOM: -> E-DOM={p_e_after_k:.1%}, -> K-DOM={p_k_after_k:.1%}")
        print(f"  After E-DOM: -> K-DOM={p_k_after_e:.1%}, -> E-DOM={p_e_after_e:.1%}")

        # Alternation ratio: does the system prefer switching over staying?
        alt_k = p_e_after_k / p_k_after_k if p_k_after_k > 0 else float('inf')
        alt_e = p_k_after_e / p_e_after_e if p_e_after_e > 0 else float('inf')
        print(f"  K-DOM alternation ratio (switch/stay): {alt_k:.2f}")
        print(f"  E-DOM alternation ratio (switch/stay): {alt_e:.2f}")
        print(f"  (>1 = prefers switching, <1 = prefers staying, =1 = indifferent)")

    return {
        'matrix': {f"{a}->{b}": c for (a, b), c in trans.items()},
        'n': n,
    }


# ============================================================
# T6d: WITHIN-LINE vs ACROSS-LINE COMPARISON
# ============================================================

def test_line_boundary_reset(line_groups):
    """Test whether carryover signal is stronger within lines vs across line boundaries."""
    print("\n" + "=" * 70)
    print("T6d: LINE BOUNDARY RESET TEST")
    print("=" * 70)

    within_transitions = []
    across_transitions = []

    # Within-line transitions
    for key in sorted(line_groups.keys()):
        tokens = line_groups[key]
        for i in range(len(tokens) - 1):
            m1 = tokens[i]['middle']
            m2 = tokens[i+1]['middle']
            if m1 and m2:
                within_transitions.append((m1[-1], m2[0]))

    # Across-line transitions (last token of line N -> first token of line N+1)
    folio_lines = defaultdict(list)
    for key in sorted(line_groups.keys()):
        folio = key[0]
        folio_lines[folio].append(key)

    for folio in sorted(folio_lines.keys()):
        lines = sorted(folio_lines[folio])
        for i in range(len(lines) - 1):
            curr_tokens = line_groups[lines[i]]
            next_tokens = line_groups[lines[i+1]]
            if curr_tokens and next_tokens:
                last_mid = curr_tokens[-1]['middle']
                first_mid = next_tokens[0]['middle']
                if last_mid and first_mid:
                    across_transitions.append((last_mid[-1], first_mid[0]))

    def compute_ke_carryover(transitions, label):
        n = len(transitions)
        ke_trans = Counter()
        for a, b in transitions:
            if a in ('k', 'e') and b in ('k', 'e'):
                ke_trans[(a, b)] += 1

        total_k = ke_trans[('k', 'k')] + ke_trans[('k', 'e')]
        total_e = ke_trans[('e', 'k')] + ke_trans[('e', 'e')]

        if total_k > 0 and total_e > 0:
            p_e_after_k = ke_trans[('k', 'e')] / total_k
            p_e_after_e = ke_trans[('e', 'e')] / total_e
            p_k_after_e = ke_trans[('e', 'k')] / total_e
            p_k_after_k = ke_trans[('k', 'k')] / total_k
            carryover = (p_e_after_k - p_e_after_e) + (p_k_after_e - p_k_after_k)
        else:
            p_e_after_k = p_e_after_e = p_k_after_e = p_k_after_k = 0
            carryover = 0

        print(f"\n  {label} (n={n}, k/e transitions={total_k + total_e}):")
        print(f"    P(e after k) = {p_e_after_k:.3f}")
        print(f"    P(e after e) = {p_e_after_e:.3f}")
        print(f"    P(k after e) = {p_k_after_e:.3f}")
        print(f"    P(k after k) = {p_k_after_k:.3f}")
        print(f"    Combined carryover signal: {carryover:+.3f}")

        return {
            'n': n,
            'carryover': round(carryover, 4),
            'p_e_after_k': round(p_e_after_k, 4),
            'p_e_after_e': round(p_e_after_e, 4),
        }

    within_stats = compute_ke_carryover(within_transitions, "WITHIN-LINE")
    across_stats = compute_ke_carryover(across_transitions, "ACROSS-LINE")

    diff = within_stats['carryover'] - across_stats['carryover']
    print(f"\n  --- COMPARISON ---")
    print(f"  Within-line carryover:  {within_stats['carryover']:+.3f}")
    print(f"  Across-line carryover:  {across_stats['carryover']:+.3f}")
    print(f"  Difference: {diff:+.3f}")

    if within_stats['carryover'] > 0 and across_stats['carryover'] <= 0:
        print(f"  Verdict: WITHIN_LINE_ONLY — carryover within lines, resets at boundaries")
    elif within_stats['carryover'] > 0 and across_stats['carryover'] > 0:
        if diff > 0.02:
            print(f"  Verdict: STRONGER_WITHIN — carryover exists everywhere but stronger within lines")
        else:
            print(f"  Verdict: UNIVERSAL — carryover across all boundaries equally")
    elif within_stats['carryover'] <= 0:
        print(f"  Verdict: NO_CARRYOVER — no evidence of state carry-over")

    return {
        'within': within_stats,
        'across': across_stats,
        'difference': round(diff, 4),
    }


# ============================================================
# MAIN
# ============================================================

def main():
    print("ORDER CARRYOVER TEST — Phase 425 Extension")
    print("=" * 70)

    print("\nLoading data...")
    line_groups = load_tokens_by_line()
    n_lines = len(line_groups)
    n_tokens = sum(len(v) for v in line_groups.values())
    print(f"Loaded {n_tokens} tokens across {n_lines} lines")

    # Build within-line transition pairs
    within_pairs = get_transitions(line_groups, within_line_only=True)
    print(f"Within-line consecutive pairs: {len(within_pairs)}")

    results = {}

    # T6a
    results['T6a_terminal_initial_bias'] = test_terminal_initial_bias(within_pairs)

    # T6b
    results['T6b_ke_ordering_context'] = test_ke_ordering_context(line_groups)

    # T6c
    results['T6c_transition_matrix'] = test_transition_matrix(within_pairs)

    # T6d
    results['T6d_line_boundary_reset'] = test_line_boundary_reset(line_groups)

    # Save
    output_path = RESULTS_DIR / "order_carryover_results.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n{'='*70}")
    print(f"Results saved to {output_path}")
    print(f"{'='*70}")


if __name__ == '__main__':
    main()
