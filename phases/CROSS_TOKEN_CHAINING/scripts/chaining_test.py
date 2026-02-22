"""
CROSS_TOKEN_CHAINING: Phase 430
=================================
Tests whether the TERMINAL atom of token N's MIDDLE predicts the INITIAL
atom of token N+1's MIDDLE, creating a pipeline where each instruction's
output feeds the next instruction's input.

Context:
  - C1209: MIDDLE positional grammar: INITIAL/MEDIAL/TERMINAL/FREE slots
  - C1210: Within-MIDDLE slot syntax with forbidden combinations
  - C1200: k/e terminal-to-initial carryover (within-line +0.247)
  - C1208: Atom carryover classification (9 positive, 4 negative)
  - C1207: 5-6 correlation axes

Tests:
  T1:  Cross-token TERMINAL->INITIAL contingency (+ daiin control + shuffle)
  T2:  Cross-token vs within-MIDDLE comparison
  T3:  Axis continuity vs axis switching
  T4:  Cross-line boundary comparison
"""
import json
import math
import random
import sys
from collections import defaultdict, Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.voynich import Transcript, Morphology

RESULTS_DIR = Path("phases/CROSS_TOKEN_CHAINING/results")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# C1207 axis classification
AXIS_MAP = {
    'a': 'ITERATION', 'i': 'ITERATION', 'n': 'ITERATION', 'r': 'ITERATION',
    'c': 'MONITORING', 'h': 'MONITORING',
    'k': 'ENERGY', 'l': 'ENERGY',
    'd': 'CLOSURE', 'y': 'CLOSURE',
    'o': 'STRUCTURAL', 'p': 'STRUCTURAL',
    'e': 'STABILITY',
    't': 'FREE_T', 'f': 'OTHER', 's': 'OTHER', 'm': 'OTHER',
    'q': 'OTHER', 'g': 'OTHER', 'x': 'OTHER',
}

N_SHUFFLES = 1000


# ============================================================
# DATA LOADING
# ============================================================

def load_tokens_by_line():
    """Load Currier B tokens grouped by (folio, line), preserving order."""
    tx = Transcript()
    morph = Morphology()
    line_groups = defaultdict(list)
    for t in tx.currier_b():
        m = morph.extract(t.word)
        if m.middle and m.middle != '_EMPTY_' and len(m.middle) >= 2:
            line_groups[(t.folio, t.line)].append({
                'word': t.word,
                'middle': m.middle,
                'folio': t.folio,
                'line': t.line,
                'section': t.section,
                'initial': m.middle[0],
                'terminal': m.middle[-1],
            })
    return line_groups


def cramers_v(contingency):
    """Compute chi2 and Cramer's V from contingency Counter."""
    rows = sorted(set(r for r, c in contingency))
    cols = sorted(set(c for r, c in contingency))
    n = sum(contingency.values())
    if n == 0:
        return 0.0, 0.0, 0

    row_totals = {r: sum(contingency.get((r, c), 0) for c in cols) for r in rows}
    col_totals = {c: sum(contingency.get((r, c), 0) for r in rows) for c in cols}

    chi2 = 0.0
    for r in rows:
        for c in cols:
            obs = contingency.get((r, c), 0)
            exp = row_totals[r] * col_totals[c] / n if n > 0 else 0
            if exp > 0:
                chi2 += (obs - exp) ** 2 / exp

    k = min(len(rows), len(cols))
    v = (chi2 / (n * (k - 1))) ** 0.5 if k > 1 and n > 0 else 0
    return chi2, v, n


def mutual_info(contingency):
    """Compute MI in bits."""
    n = sum(contingency.values())
    if n == 0:
        return 0.0
    rows = set(r for r, c in contingency)
    cols = set(c for r, c in contingency)
    row_totals = {r: sum(contingency.get((r, c), 0) for c in cols) for r in rows}
    col_totals = {c: sum(contingency.get((r, c), 0) for r in rows) for c in cols}
    mi = 0.0
    for r in rows:
        for c in cols:
            obs = contingency.get((r, c), 0)
            if obs == 0:
                continue
            p_rc = obs / n
            p_r = row_totals[r] / n
            p_c = col_totals[c] / n
            if p_r > 0 and p_c > 0:
                mi += p_rc * math.log2(p_rc / (p_r * p_c))
    return mi


def enrichment_ratios(contingency, min_expected=5):
    """Compute obs/expected ratios."""
    rows = sorted(set(r for r, c in contingency))
    cols = sorted(set(c for r, c in contingency))
    n = sum(contingency.values())
    row_totals = {r: sum(contingency.get((r, c), 0) for c in cols) for r in rows}
    col_totals = {c: sum(contingency.get((r, c), 0) for r in rows) for c in cols}
    ratios = {}
    for r in rows:
        for c in cols:
            obs = contingency.get((r, c), 0)
            exp = row_totals[r] * col_totals[c] / n if n > 0 else 0
            if exp >= min_expected:
                ratios[(r, c)] = {'obs': obs, 'exp': round(exp, 1),
                                  'ratio': round(obs / exp, 2) if exp > 0 else 0}
    return ratios


def print_contingency(contingency, label=""):
    """Print contingency table."""
    rows = sorted(set(r for r, c in contingency))
    cols = sorted(set(c for r, c in contingency))
    header = f"  {label:>4}  " + "".join(f"{c:>6}" for c in cols) + "  Total"
    print(header)
    for r in rows:
        row_str = f"  {r:>4}  "
        row_total = 0
        for c in cols:
            ct = contingency.get((r, c), 0)
            row_total += ct
            row_str += f"{ct:>6}"
        row_str += f"  {row_total:>5}"
        print(row_str)


# ============================================================
# T1: CROSS-TOKEN TERMINAL -> INITIAL CONTINGENCY
# ============================================================

def test_cross_token(line_groups, exclude_singletons=False):
    """Build TERMINAL(N) -> INITIAL(N+1) contingency for within-line pairs."""
    label = "T1" if not exclude_singletons else "T1b"
    suffix = " (excl daiin/ol)" if exclude_singletons else ""
    print(f"\n{'='*70}")
    print(f"{label}: CROSS-TOKEN TERMINAL -> INITIAL{suffix}")
    print("=" * 70)

    contingency = Counter()
    n_pairs = 0

    for key in sorted(line_groups.keys()):
        tokens = line_groups[key]
        if exclude_singletons:
            tokens = [t for t in tokens if t['middle'] not in ('iin', 'ol')]
        for j in range(len(tokens) - 1):
            term = tokens[j]['terminal']
            init = tokens[j + 1]['initial']
            contingency[(term, init)] += 1
            n_pairs += 1

    chi2, v, _ = cramers_v(contingency)
    mi = mutual_info(contingency)
    print(f"  Pairs: {n_pairs}")
    print(f"  Chi2={chi2:.1f}, Cramer's V={v:.4f}, MI={mi:.4f} bits")

    print(f"\n  Contingency (TERMINAL of N -> INITIAL of N+1):")
    print_contingency(contingency, "T\\I")

    # Enrichment
    ratios = enrichment_ratios(contingency)
    enriched = [(k, v) for k, v in ratios.items() if v['ratio'] >= 1.5 and v['obs'] >= 20]
    depleted = [(k, v) for k, v in ratios.items() if v['ratio'] <= 0.5 and v['exp'] >= 20]
    enriched.sort(key=lambda x: -x[1]['ratio'])
    depleted.sort(key=lambda x: x[1]['ratio'])

    if enriched:
        print(f"\n  Enriched cross-token pairs (>= 1.5x, obs >= 20):")
        for (t, i), info in enriched[:20]:
            t_axis = AXIS_MAP.get(t, '?')
            i_axis = AXIS_MAP.get(i, '?')
            same = "SAME" if t_axis == i_axis else "SWITCH"
            print(f"    {t}({t_axis[:4]})->{i}({i_axis[:4]}): {info['obs']}/{info['exp']} = {info['ratio']}x [{same}]")

    if depleted:
        print(f"\n  Depleted cross-token pairs (<= 0.5x, exp >= 20):")
        for (t, i), info in depleted[:20]:
            t_axis = AXIS_MAP.get(t, '?')
            i_axis = AXIS_MAP.get(i, '?')
            same = "SAME" if t_axis == i_axis else "SWITCH"
            print(f"    {t}({t_axis[:4]})->{i}({i_axis[:4]}): {info['obs']}/{info['exp']} = {info['ratio']}x [{same}]")

    # Shuffle control: permute token order within lines
    print(f"\n  Running {N_SHUFFLES} within-line shuffle permutations...")
    random.seed(42)
    shuffle_mis = []
    for s in range(N_SHUFFLES):
        shuf_cont = Counter()
        for key in line_groups:
            tokens = line_groups[key]
            if exclude_singletons:
                tokens = [t for t in tokens if t['middle'] not in ('iin', 'ol')]
            if len(tokens) < 2:
                continue
            indices = list(range(len(tokens)))
            random.shuffle(indices)
            for j in range(len(indices) - 1):
                term = tokens[indices[j]]['terminal']
                init = tokens[indices[j + 1]]['initial']
                shuf_cont[(term, init)] += 1
        shuffle_mis.append(mutual_info(shuf_cont))

    shuf_mean = sum(shuffle_mis) / len(shuffle_mis)
    shuf_std = (sum((m - shuf_mean)**2 for m in shuffle_mis) / len(shuffle_mis)) ** 0.5
    z = (mi - shuf_mean) / shuf_std if shuf_std > 0 else 0

    print(f"  Observed MI:  {mi:.4f} bits")
    print(f"  Shuffle mean: {shuf_mean:.4f} bits")
    print(f"  Shuffle std:  {shuf_std:.4f}")
    print(f"  Z-score:      {z:.2f}")
    if z > 2:
        print(f"  -> GENUINE sequential structure (beyond co-occurrence)")
    else:
        print(f"  -> Signal may be vocabulary co-occurrence, not sequential")

    return {
        'n_pairs': n_pairs,
        'chi2': round(chi2, 1),
        'cramers_v': round(v, 4),
        'mutual_info': round(mi, 4),
        'shuffle_mean_mi': round(shuf_mean, 4),
        'shuffle_std_mi': round(shuf_std, 4),
        'z_score': round(z, 2),
        'enriched': [{'pair': f"{k[0]}->{k[1]}", 'obs': v['obs'], 'exp': v['exp'],
                      'ratio': v['ratio']} for k, v in enriched[:20]],
        'depleted': [{'pair': f"{k[0]}->{k[1]}", 'obs': v['obs'], 'exp': v['exp'],
                      'ratio': v['ratio']} for k, v in depleted[:20]],
    }


# ============================================================
# T2: CROSS-TOKEN vs WITHIN-MIDDLE COMPARISON
# ============================================================

def test_cross_vs_within(line_groups):
    """Compare cross-token TERMINAL->INITIAL to within-MIDDLE INITIAL->TERMINAL."""
    print(f"\n{'='*70}")
    print("T2: CROSS-TOKEN vs WITHIN-MIDDLE COMPARISON")
    print("=" * 70)

    # Within-MIDDLE: INITIAL->TERMINAL of same token
    within = Counter()
    # Cross-token: TERMINAL(N)->INITIAL(N+1)
    cross = Counter()

    for key in sorted(line_groups.keys()):
        tokens = line_groups[key]
        for j, t in enumerate(tokens):
            within[(t['initial'], t['terminal'])] += 1
            if j + 1 < len(tokens):
                cross[(t['terminal'], tokens[j + 1]['initial'])] += 1

    chi2_w, v_w, _ = cramers_v(within)
    chi2_c, v_c, _ = cramers_v(cross)
    mi_w = mutual_info(within)
    mi_c = mutual_info(cross)

    print(f"  Within-MIDDLE (INITIAL->TERMINAL): V={v_w:.4f}, MI={mi_w:.4f} bits")
    print(f"  Cross-token (TERMINAL->INITIAL):   V={v_c:.4f}, MI={mi_c:.4f} bits")
    print(f"  Ratio (cross/within):              V={v_c/v_w:.3f}, MI={mi_c/mi_w:.3f}")

    # Compare enrichment patterns
    ratios_w = enrichment_ratios(within)
    ratios_c = enrichment_ratios(cross)

    # Find pairs present in both
    common_pairs = set(ratios_w.keys()) & set(ratios_c.keys())
    if common_pairs:
        # For pairs that are enriched within-MIDDLE, are they also enriched cross-token?
        within_enriched = {k for k, v in ratios_w.items() if v['ratio'] >= 1.5}
        cross_enriched = {k for k, v in ratios_c.items() if v['ratio'] >= 1.5}

        # Note: within is (INITIAL, TERMINAL), cross is (TERMINAL, INITIAL)
        # To compare, we need to reverse cross pairs
        cross_enriched_reversed = {(c, r) for r, c in cross_enriched}

        overlap = within_enriched & cross_enriched_reversed
        within_only = within_enriched - cross_enriched_reversed
        cross_only = cross_enriched_reversed - within_enriched

        print(f"\n  Enriched pair comparison (same atom pair, reversed direction):")
        print(f"    Within-MIDDLE enriched: {len(within_enriched)}")
        print(f"    Cross-token enriched (reversed): {len(cross_enriched_reversed)}")
        print(f"    Overlap (both): {len(overlap)}")

        if overlap:
            print(f"    Pairs enriched in BOTH directions:")
            for init, term in sorted(overlap):
                w_r = ratios_w.get((init, term), {}).get('ratio', 0)
                c_r = ratios_c.get((term, init), {}).get('ratio', 0)
                print(f"      {init}<->{term}: within={w_r}x, cross={c_r}x")

    return {
        'within_v': round(v_w, 4),
        'within_mi': round(mi_w, 4),
        'cross_v': round(v_c, 4),
        'cross_mi': round(mi_c, 4),
        'v_ratio': round(v_c / v_w, 4) if v_w > 0 else 0,
        'mi_ratio': round(mi_c / mi_w, 4) if mi_w > 0 else 0,
    }


# ============================================================
# T3: AXIS CONTINUITY vs SWITCHING
# ============================================================

def test_axis_transitions(line_groups):
    """Classify cross-token transitions by axis: same-axis vs switch."""
    print(f"\n{'='*70}")
    print("T3: AXIS CONTINUITY vs SWITCHING")
    print("=" * 70)

    axis_trans = Counter()  # (terminal_axis, initial_axis) -> count
    same_count = 0
    switch_count = 0
    total = 0

    for key in sorted(line_groups.keys()):
        tokens = line_groups[key]
        for j in range(len(tokens) - 1):
            t_axis = AXIS_MAP.get(tokens[j]['terminal'], 'OTHER')
            i_axis = AXIS_MAP.get(tokens[j + 1]['initial'], 'OTHER')
            axis_trans[(t_axis, i_axis)] += 1
            total += 1
            if t_axis == i_axis:
                same_count += 1
            else:
                switch_count += 1

    same_rate = same_count / total if total > 0 else 0
    print(f"  Total transitions: {total}")
    print(f"  Same-axis: {same_count} ({same_rate:.1%})")
    print(f"  Axis-switch: {switch_count} ({1 - same_rate:.1%})")

    # Compute expected same-axis rate under independence
    t_totals = Counter()
    i_totals = Counter()
    for (t, i), ct in axis_trans.items():
        t_totals[t] += ct
        i_totals[i] += ct

    expected_same = 0
    for axis in set(list(t_totals.keys()) + list(i_totals.keys())):
        p_t = t_totals.get(axis, 0) / total
        p_i = i_totals.get(axis, 0) / total
        expected_same += p_t * p_i

    print(f"  Expected same-axis (independence): {expected_same:.1%}")
    print(f"  Observed / Expected: {same_rate / expected_same:.2f}x" if expected_same > 0 else "")

    # Print axis transition matrix
    all_axes = sorted(set(list(t_totals.keys()) + list(i_totals.keys())))
    print(f"\n  Axis transition matrix (TERMINAL axis -> INITIAL axis):")
    header = "  " + " " * 12 + "".join(f"{a[:8]:>10}" for a in all_axes)
    print(header)
    for ta in all_axes:
        row = f"  {ta[:10]:>10}  "
        for ia in all_axes:
            ct = axis_trans.get((ta, ia), 0)
            pct = ct / t_totals[ta] * 100 if t_totals.get(ta, 0) > 0 else 0
            row += f"{pct:>9.1f}%"
        print(row)

    # Section stratification
    print(f"\n  Same-axis rate by section:")
    section_data = defaultdict(lambda: {'same': 0, 'total': 0})
    for key in sorted(line_groups.keys()):
        tokens = line_groups[key]
        sec = tokens[0]['section'] if tokens else '?'
        for j in range(len(tokens) - 1):
            t_axis = AXIS_MAP.get(tokens[j]['terminal'], 'OTHER')
            i_axis = AXIS_MAP.get(tokens[j + 1]['initial'], 'OTHER')
            section_data[sec]['total'] += 1
            if t_axis == i_axis:
                section_data[sec]['same'] += 1

    for sec in sorted(section_data.keys()):
        d = section_data[sec]
        rate = d['same'] / d['total'] if d['total'] > 0 else 0
        print(f"    {sec}: {rate:.1%} ({d['same']}/{d['total']})")

    return {
        'same_axis_rate': round(same_rate, 4),
        'expected_same': round(expected_same, 4),
        'enrichment': round(same_rate / expected_same, 4) if expected_same > 0 else 0,
        'axis_matrix': {f"{t}->{i}": ct for (t, i), ct in axis_trans.items()},
    }


# ============================================================
# T4: CROSS-LINE BOUNDARY COMPARISON
# ============================================================

def test_cross_line(line_groups):
    """Compare within-line vs cross-line TERMINAL->INITIAL transitions."""
    print(f"\n{'='*70}")
    print("T4: CROSS-LINE BOUNDARY COMPARISON")
    print("=" * 70)

    within_cont = Counter()
    cross_cont = Counter()

    sorted_keys = sorted(line_groups.keys())

    for idx, key in enumerate(sorted_keys):
        tokens = line_groups[key]

        # Within-line pairs
        for j in range(len(tokens) - 1):
            within_cont[(tokens[j]['terminal'], tokens[j + 1]['initial'])] += 1

        # Cross-line pair (last of this line -> first of next, same folio)
        if idx + 1 < len(sorted_keys):
            next_key = sorted_keys[idx + 1]
            if key[0] == next_key[0]:  # same folio
                next_tokens = line_groups[next_key]
                if tokens and next_tokens:
                    cross_cont[(tokens[-1]['terminal'], next_tokens[0]['initial'])] += 1

    chi2_w, v_w, n_w = cramers_v(within_cont)
    chi2_c, v_c, n_c = cramers_v(cross_cont)
    mi_w = mutual_info(within_cont)
    mi_c = mutual_info(cross_cont)

    print(f"  Within-line:  n={sum(within_cont.values())}, V={v_w:.4f}, MI={mi_w:.4f} bits")
    print(f"  Cross-line:   n={sum(cross_cont.values())}, V={v_c:.4f}, MI={mi_c:.4f} bits")
    print(f"  MI ratio (cross/within): {mi_c / mi_w:.3f}" if mi_w > 0 else "")

    # Print both tables side by side (summary)
    print(f"\n  Within-line enriched (top 10):")
    ratios_w = enrichment_ratios(within_cont)
    top_w = sorted([(k, v) for k, v in ratios_w.items() if v['ratio'] >= 1.3 and v['obs'] >= 20],
                   key=lambda x: -x[1]['ratio'])[:10]
    for (t, i), info in top_w:
        print(f"    {t}->{i}: {info['ratio']}x ({info['obs']})")

    print(f"\n  Cross-line enriched (top 10):")
    ratios_c = enrichment_ratios(cross_cont, min_expected=3)
    top_c = sorted([(k, v) for k, v in ratios_c.items() if v['ratio'] >= 1.3 and v['obs'] >= 5],
                   key=lambda x: -x[1]['ratio'])[:10]
    for (t, i), info in top_c:
        print(f"    {t}->{i}: {info['ratio']}x ({info['obs']})")

    return {
        'within_v': round(v_w, 4),
        'within_mi': round(mi_w, 4),
        'within_n': sum(within_cont.values()),
        'cross_v': round(v_c, 4),
        'cross_mi': round(mi_c, 4),
        'cross_n': sum(cross_cont.values()),
        'mi_ratio': round(mi_c / mi_w, 4) if mi_w > 0 else 0,
    }


# ============================================================
# MAIN
# ============================================================

def main():
    print("CROSS-TOKEN CHAINING -- Phase 430")
    print("=" * 70)

    print("\nLoading data (multi-char MIDDLEs only)...")
    line_groups = load_tokens_by_line()
    n_tokens = sum(len(v) for v in line_groups.values())
    n_lines = len(line_groups)
    print(f"Loaded {n_tokens} tokens across {n_lines} lines")

    results = {}

    # T1: Cross-token contingency
    results['T1_cross_token'] = test_cross_token(line_groups, exclude_singletons=False)

    # T1b: Without daiin/ol
    results['T1b_no_singletons'] = test_cross_token(line_groups, exclude_singletons=True)

    # T2: Cross vs within comparison
    results['T2_cross_vs_within'] = test_cross_vs_within(line_groups)

    # T3: Axis transitions
    results['T3_axis_transitions'] = test_axis_transitions(line_groups)

    # T4: Cross-line boundary
    results['T4_cross_line'] = test_cross_line(line_groups)

    # Save
    output_path = RESULTS_DIR / "chaining_results.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\n{'='*70}")
    print(f"Results saved to {output_path}")
    print(f"{'='*70}")


if __name__ == '__main__':
    main()
