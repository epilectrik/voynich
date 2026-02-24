"""
EN_LANE_CROSS_PREDICTION: Stage 1
==================================
Tests whether the specific MIDDLE content of a QO token predicts the specific
MIDDLE content of the adjacent CHSH token (and vice versa).

Core question: Is QO-CHSH interleaving (C544/C549, 56.3%, z=10.27) just
binary lane-switching, or does the specific content of one lane predict
the specific content of the other?

Context:
  - C544/C549: QO-CHSH interleave at 56.3% (z=10.27)
  - C574: Grammatically equivalent, lexically divergent (Jaccard=0.133)
  - C576: PREFIX gates MIDDLE subvocabulary (25 QO vs 43 CHSH MIDDLEs)
  - C579: CHSH-first ordering 53.9% (p=0.010)
  - C961: Same-role WORK tokens unordered (but didn't test cross-lane)
  - C966: Lane oscillation is first-order Markov
  - C1200: Within-line atom carryover (+0.247)
  - C1208: k positive carryover, e anti-clustering
  - C1212: Cross-token chaining genuine but weak (V=0.0709, z=19.74)
  - C1217: QO k-heavy (38%), CHSH e-heavy (32%)

Tests:
  T1:  Cross-lane MIDDLE mutual information (+ shuffle control)
  T1a: Same-lane control (QO-QO, CHSH-CHSH)
  T3:  Directional asymmetry (QO->CHSH vs CHSH->QO)
  T4:  Kernel state routing at lane boundaries
"""
import json
import math
import random
import sys
from collections import defaultdict, Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.voynich import Transcript, Morphology

RESULTS_DIR = Path("phases/EN_LANE_CROSS_PREDICTION/results")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

N_SHUFFLES = 1000

# Lane classification (canonical mapping from voynich.py _get_prefix_lane)
QO_PREFIXES = {'qo', 'ok', 'ot', 'o', 'ko', 'to', 'po'}
CHSH_PREFIXES = {'ch', 'sh', 'lsh'}

KERNEL_ATOMS = {'k', 'e', 'h'}


# ============================================================
# STATISTICAL FUNCTIONS (from chaining_test.py pattern)
# ============================================================

def mutual_info(contingency):
    """Compute MI in bits from Counter with (row, col) keys."""
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
    v = (chi2 / (n * max(k - 1, 1))) ** 0.5 if n > 0 else 0
    return chi2, v, n


def enrichment_ratios(contingency, min_expected=5):
    """Compute obs/expected ratios for contingency cells."""
    rows = sorted(set(r for r, c in contingency))
    cols = sorted(set(c for r, c in contingency))
    n = sum(contingency.values())
    if n == 0:
        return {}
    row_totals = {r: sum(contingency.get((r, c), 0) for c in cols) for r in rows}
    col_totals = {c: sum(contingency.get((r, c), 0) for r in rows) for c in cols}
    ratios = {}
    for r in rows:
        for c in cols:
            obs = contingency.get((r, c), 0)
            exp = row_totals[r] * col_totals[c] / n
            if exp >= min_expected:
                ratios[(r, c)] = {
                    'obs': obs, 'exp': round(exp, 1),
                    'ratio': round(obs / exp, 2) if exp > 0 else 0
                }
    return ratios


def shuffle_mi_permutation(line_en_sequences, pair_filter, n_shuffles=N_SHUFFLES):
    """Compute shuffle distribution of MI using column permutation.

    Correct control for cross-lane MI: extract all pairs, then permute one
    column (first element) across all pairs while keeping the other fixed.
    This preserves both marginal distributions and tests whether the joint
    distribution differs from independence.

    The previous approach (shuffling MIDDLEs within lines across lanes) was
    invalid because QO and CHSH have 87% non-overlapping MIDDLE vocabularies
    (C576). Mixing MIDDLEs across lanes inflated shuffle MI artificially.

    Returns (obs_mi, shuf_mean, shuf_std, z_score).
    """
    # Collect all pairs
    pairs = []
    for seq in line_en_sequences:
        for i in range(len(seq) - 1):
            pair = pair_filter(seq[i], seq[i + 1])
            if pair is not None:
                pairs.append(pair)

    if not pairs:
        return 0.0, 0.0, 0.0, 0.0

    # Observed MI
    obs_cont = Counter(pairs)
    obs_mi = mutual_info(obs_cont)

    # Shuffle: permute first element across all pairs
    random.seed(42)
    first_elements = [p[0] for p in pairs]
    second_elements = [p[1] for p in pairs]

    shuffle_mis = []
    for _ in range(n_shuffles):
        shuf_first = first_elements.copy()
        random.shuffle(shuf_first)
        shuf_cont = Counter(zip(shuf_first, second_elements))
        shuffle_mis.append(mutual_info(shuf_cont))

    shuf_mean = sum(shuffle_mis) / len(shuffle_mis)
    shuf_std = (sum((m - shuf_mean) ** 2 for m in shuffle_mis) / len(shuffle_mis)) ** 0.5
    z = (obs_mi - shuf_mean) / shuf_std if shuf_std > 0 else 0
    return obs_mi, shuf_mean, shuf_std, z


def shuffle_mi_within_lane(line_en_sequences, pair_filter, n_shuffles=N_SHUFFLES):
    """Compute shuffle distribution by shuffling MIDDLEs within-lane within-line.

    For each line: shuffle QO MIDDLEs among QO positions, CHSH MIDDLEs among
    CHSH positions. This preserves lane-MIDDLE binding while randomizing
    within-lane sequential order. Tests whether the specific ordering within
    each lane matters for cross-lane pairing.

    Returns (obs_mi, shuf_mean, shuf_std, z_score).
    """
    # Observed MI
    obs_cont = Counter()
    for seq in line_en_sequences:
        for i in range(len(seq) - 1):
            pair = pair_filter(seq[i], seq[i + 1])
            if pair is not None:
                obs_cont[pair] += 1
    obs_mi = mutual_info(obs_cont)

    random.seed(42)
    shuffle_mis = []
    for _ in range(n_shuffles):
        shuf_cont = Counter()
        for seq in line_en_sequences:
            if len(seq) < 2:
                continue
            # Separate by lane, shuffle MIDDLEs within each lane
            qo_indices = [j for j, t in enumerate(seq) if t['lane'] == 'QO']
            chsh_indices = [j for j, t in enumerate(seq) if t['lane'] == 'CHSH']

            qo_middles = [seq[j]['middle'] for j in qo_indices]
            chsh_middles = [seq[j]['middle'] for j in chsh_indices]
            random.shuffle(qo_middles)
            random.shuffle(chsh_middles)

            # Rebuild sequence with shuffled MIDDLEs
            shuf_seq = [dict(t) for t in seq]  # shallow copy each token
            for idx, j in enumerate(qo_indices):
                shuf_seq[j]['middle'] = qo_middles[idx]
                shuf_seq[j]['initial'] = qo_middles[idx][0] if qo_middles[idx] else ''
                shuf_seq[j]['terminal'] = qo_middles[idx][-1] if qo_middles[idx] else ''
            for idx, j in enumerate(chsh_indices):
                shuf_seq[j]['middle'] = chsh_middles[idx]
                shuf_seq[j]['initial'] = chsh_middles[idx][0] if chsh_middles[idx] else ''
                shuf_seq[j]['terminal'] = chsh_middles[idx][-1] if chsh_middles[idx] else ''

            for i in range(len(shuf_seq) - 1):
                pair = pair_filter(shuf_seq[i], shuf_seq[i + 1])
                if pair is not None:
                    shuf_cont[pair] += 1
        shuffle_mis.append(mutual_info(shuf_cont))

    shuf_mean = sum(shuffle_mis) / len(shuffle_mis)
    shuf_std = (sum((m - shuf_mean) ** 2 for m in shuffle_mis) / len(shuffle_mis)) ** 0.5
    z = (obs_mi - shuf_mean) / shuf_std if shuf_std > 0 else 0
    return obs_mi, shuf_mean, shuf_std, z


# ============================================================
# DATA LOADING
# ============================================================

def classify_lane(prefix):
    """Classify prefix into QO, CHSH, or OTHER."""
    if prefix in QO_PREFIXES:
        return 'QO'
    elif prefix in CHSH_PREFIXES:
        return 'CHSH'
    else:
        return 'OTHER'


def load_en_sequences():
    """Load EN-lane tokens grouped by line, in positional order.

    Returns list of lists, where each inner list is one line's EN-lane
    tokens (QO or CHSH only) in their original positional order.
    Also returns metadata counts.
    """
    tx = Transcript()
    morph = Morphology()

    line_groups = defaultdict(list)
    n_total = 0
    n_en = 0

    for t in tx.currier_b():
        w = t.word.strip()
        if not w or '*' in w:
            continue
        m = morph.extract(w)
        if not m.middle or m.middle == '_EMPTY_':
            continue

        n_total += 1
        pfx = m.prefix or ''
        lane = classify_lane(pfx)

        if lane in ('QO', 'CHSH'):
            n_en += 1
            line_groups[(t.folio, t.line)].append({
                'word': w,
                'middle': m.middle,
                'suffix': m.suffix or '',
                'prefix': pfx,
                'lane': lane,
                'folio': t.folio,
                'line': t.line,
                'section': t.section,
                'initial': m.middle[0],
                'terminal': m.middle[-1],
            })

    # Convert to list of sequences (drop the keys)
    sequences = [line_groups[k] for k in sorted(line_groups.keys()) if len(line_groups[k]) >= 2]

    return sequences, len(line_groups), n_en, n_total


# ============================================================
# PAIR FILTERS
# ============================================================

def cross_lane_middle_pair(t1, t2):
    """Return (qo_middle, chsh_middle) for cross-lane pairs, None otherwise."""
    if t1['lane'] == 'QO' and t2['lane'] == 'CHSH':
        return (t1['middle'], t2['middle'])
    elif t1['lane'] == 'CHSH' and t2['lane'] == 'QO':
        return (t2['middle'], t1['middle'])  # normalize: always (QO, CHSH)
    return None


def qo_to_chsh_pair(t1, t2):
    """Return (qo_middle, chsh_middle) for QO->CHSH direction only."""
    if t1['lane'] == 'QO' and t2['lane'] == 'CHSH':
        return (t1['middle'], t2['middle'])
    return None


def chsh_to_qo_pair(t1, t2):
    """Return (chsh_middle, qo_middle) for CHSH->QO direction only."""
    if t1['lane'] == 'CHSH' and t2['lane'] == 'QO':
        return (t1['middle'], t2['middle'])
    return None


def same_lane_qo_pair(t1, t2):
    """Return (middle1, middle2) for QO->QO pairs."""
    if t1['lane'] == 'QO' and t2['lane'] == 'QO':
        return (t1['middle'], t2['middle'])
    return None


def same_lane_chsh_pair(t1, t2):
    """Return (middle1, middle2) for CHSH->CHSH pairs."""
    if t1['lane'] == 'CHSH' and t2['lane'] == 'CHSH':
        return (t1['middle'], t2['middle'])
    return None


def cross_lane_kernel_pair(t1, t2):
    """Return (terminal_atom, initial_atom) for cross-lane kernel routing."""
    if t1['lane'] != t2['lane'] and t1['lane'] in ('QO', 'CHSH') and t2['lane'] in ('QO', 'CHSH'):
        return (t1['terminal'], t2['initial'])
    return None


def cross_lane_kernel_qc(t1, t2):
    """Kernel routing for QO->CHSH direction."""
    if t1['lane'] == 'QO' and t2['lane'] == 'CHSH':
        return (t1['terminal'], t2['initial'])
    return None


def cross_lane_kernel_cq(t1, t2):
    """Kernel routing for CHSH->QO direction."""
    if t1['lane'] == 'CHSH' and t2['lane'] == 'QO':
        return (t1['terminal'], t2['initial'])
    return None


# ============================================================
# PAIR COUNTING
# ============================================================

def count_pairs(sequences):
    """Count pair types across all line sequences."""
    counts = Counter()
    for seq in sequences:
        for i in range(len(seq) - 1):
            a, b = seq[i]['lane'], seq[i + 1]['lane']
            counts[f"{a}_{b}"] += 1
    return dict(counts)


def build_contingency(sequences, pair_filter):
    """Build contingency table from sequences using a pair filter."""
    cont = Counter()
    for seq in sequences:
        for i in range(len(seq) - 1):
            pair = pair_filter(seq[i], seq[i + 1])
            if pair is not None:
                cont[pair] += 1
    return cont


# ============================================================
# TESTS
# ============================================================

def run_t1(sequences):
    """T1: Cross-lane MIDDLE mutual information."""
    print("\nT1: Cross-Lane MIDDLE MI")
    print("-" * 40)

    cont = build_contingency(sequences, cross_lane_middle_pair)
    n = sum(cont.values())
    chi2, v, _ = cramers_v(cont)

    # Two shuffle controls:
    # 1. Column permutation (tests joint distribution vs independence)
    mi_obs, shuf_mean_p, shuf_std_p, z_perm = shuffle_mi_permutation(
        sequences, cross_lane_middle_pair)
    # 2. Within-lane shuffle (tests sequential ordering within lanes)
    _, shuf_mean_wl, shuf_std_wl, z_wl = shuffle_mi_within_lane(
        sequences, cross_lane_middle_pair)

    print(f"  N pairs:      {n}")
    print(f"  Chi2:         {chi2:.1f}")
    print(f"  Cramer's V:   {v:.4f}")
    print(f"  Observed MI:  {mi_obs:.4f} bits")
    print(f"  Permutation shuffle mean: {shuf_mean_p:.4f} bits (z={z_perm:.2f})")
    print(f"  Within-lane shuffle mean: {shuf_mean_wl:.4f} bits (z={z_wl:.2f})")

    verdict = "GENUINE" if z_perm > 3 else "MARGINAL" if z_perm > 2 else "NULL"
    print(f"  -> {verdict} cross-lane content prediction (permutation test)")
    if z_wl > 3:
        print(f"  -> GENUINE within-lane ordering effect (z={z_wl:.2f})")
    elif z_wl > 2:
        print(f"  -> MARGINAL within-lane ordering effect (z={z_wl:.2f})")
    else:
        print(f"  -> NULL within-lane ordering effect (z={z_wl:.2f})")

    # Enrichment analysis
    ratios = enrichment_ratios(cont, min_expected=5)
    enriched = sorted(ratios.items(), key=lambda x: x[1]['ratio'], reverse=True)[:10]
    depleted = sorted(ratios.items(), key=lambda x: x[1]['ratio'])[:10]

    if enriched:
        print(f"\n  Top enriched (QO_MID, CHSH_MID):")
        for (qm, cm), info in enriched:
            print(f"    ({qm}, {cm}): {info['obs']}/{info['exp']} = {info['ratio']}x")
    if depleted:
        print(f"\n  Top depleted (QO_MID, CHSH_MID):")
        for (qm, cm), info in depleted:
            print(f"    ({qm}, {cm}): {info['obs']}/{info['exp']} = {info['ratio']}x")

    return {
        'n_pairs': n,
        'chi2': round(chi2, 1),
        'cramers_v': round(v, 4),
        'mi_observed': round(mi_obs, 4),
        'mi_shuffle_mean_perm': round(shuf_mean_p, 4),
        'mi_shuffle_std_perm': round(shuf_std_p, 4),
        'z_score_perm': round(z_perm, 2),
        'mi_shuffle_mean_within_lane': round(shuf_mean_wl, 4),
        'z_score_within_lane': round(z_wl, 2),
        'verdict': verdict,
        'enriched_top10': [
            {'qo_middle': k[0], 'chsh_middle': k[1], **v}
            for k, v in enriched
        ],
        'depleted_top10': [
            {'qo_middle': k[0], 'chsh_middle': k[1], **v}
            for k, v in depleted
        ],
    }


def run_t1a(sequences):
    """T1a: Same-lane control (QO-QO and CHSH-CHSH)."""
    print("\nT1a: Same-Lane Control")
    print("-" * 40)

    results = {}
    for label, pair_fn in [('QO_QO', same_lane_qo_pair), ('CHSH_CHSH', same_lane_chsh_pair)]:
        cont = build_contingency(sequences, pair_fn)
        n = sum(cont.values())
        mi_obs, shuf_mean, shuf_std, z = shuffle_mi_permutation(sequences, pair_fn)
        print(f"  {label}: N={n}, MI={mi_obs:.4f} bits, z={z:.2f}")
        results[label] = {
            'n_pairs': n,
            'mi_observed': round(mi_obs, 4),
            'mi_shuffle_mean': round(shuf_mean, 4),
            'mi_shuffle_std': round(shuf_std, 4),
            'z_score': round(z, 2),
        }

    return results


def run_t3(sequences):
    """T3: Directional asymmetry (QO->CHSH vs CHSH->QO)."""
    print("\nT3: Directional Asymmetry")
    print("-" * 40)

    results = {}
    for label, pair_fn in [('QO_to_CHSH', qo_to_chsh_pair), ('CHSH_to_QO', chsh_to_qo_pair)]:
        cont = build_contingency(sequences, pair_fn)
        n = sum(cont.values())
        chi2, v, _ = cramers_v(cont)
        mi_obs, shuf_mean, shuf_std, z = shuffle_mi_permutation(sequences, pair_fn)
        print(f"  {label}: N={n}, MI={mi_obs:.4f} bits, V={v:.4f}, z={z:.2f}")
        results[label] = {
            'n_pairs': n,
            'chi2': round(chi2, 1),
            'cramers_v': round(v, 4),
            'mi_observed': round(mi_obs, 4),
            'mi_shuffle_mean': round(shuf_mean, 4),
            'mi_shuffle_std': round(shuf_std, 4),
            'z_score': round(z, 2),
        }

    # Direction comparison
    mi_qc = results['QO_to_CHSH']['mi_observed']
    mi_cq = results['CHSH_to_QO']['mi_observed']
    if mi_cq > 0:
        ratio = round(mi_qc / mi_cq, 3)
    else:
        ratio = float('inf') if mi_qc > 0 else 1.0

    stronger = 'QO_to_CHSH' if mi_qc > mi_cq else 'CHSH_to_QO' if mi_cq > mi_qc else 'SYMMETRIC'
    print(f"  Direction ratio (QC/CQ): {ratio}")
    print(f"  Stronger direction: {stronger}")

    results['direction_ratio'] = ratio
    results['stronger_direction'] = stronger
    return results


def run_t4(sequences):
    """T4: Kernel state routing at lane boundaries."""
    print("\nT4: Kernel State Routing at Lane Boundaries")
    print("-" * 40)

    # Overall cross-lane kernel routing
    cont = build_contingency(sequences, cross_lane_kernel_pair)
    n = sum(cont.values())
    chi2, v, _ = cramers_v(cont)
    mi_obs, shuf_mean, shuf_std, z = shuffle_mi_permutation(
        sequences, cross_lane_kernel_pair)

    print(f"  N pairs:      {n}")
    print(f"  Chi2:         {chi2:.1f}")
    print(f"  Cramer's V:   {v:.4f}")
    print(f"  Observed MI:  {mi_obs:.4f} bits")
    print(f"  Shuffle mean: {shuf_mean:.4f} bits")
    print(f"  Z-score:      {z:.2f}")

    # Carryover matrix (all atoms, not just kernel)
    ratios = enrichment_ratios(cont, min_expected=3)
    print(f"\n  Carryover matrix (obs/exp ratios, min_exp>=3):")
    # Get all atoms that appear
    all_terminals = sorted(set(r for r, c in cont))
    all_initials = sorted(set(c for r, c in cont))
    # Header
    header = "  terminal\\initial  " + "  ".join(f"{a:>5s}" for a in all_initials)
    print(header)
    for t_atom in all_terminals:
        row_parts = []
        for i_atom in all_initials:
            info = ratios.get((t_atom, i_atom))
            if info:
                row_parts.append(f"{info['ratio']:5.2f}")
            else:
                cnt = cont.get((t_atom, i_atom), 0)
                row_parts.append(f"  ({cnt})" if cnt > 0 else "    -")
        print(f"  {t_atom:>17s}  " + "  ".join(row_parts))

    # Kernel-specific carryover (k, e, h only)
    print(f"\n  Kernel carryover (k/e/h only):")
    kernel_cont = Counter()
    for (t_atom, i_atom), count in cont.items():
        if t_atom in KERNEL_ATOMS and i_atom in KERNEL_ATOMS:
            kernel_cont[(t_atom, i_atom)] += count
    kernel_ratios = enrichment_ratios(kernel_cont, min_expected=3)
    for (t_atom, i_atom) in sorted(kernel_cont.keys()):
        obs = kernel_cont[(t_atom, i_atom)]
        info = kernel_ratios.get((t_atom, i_atom))
        ratio_str = f"{info['ratio']}x" if info else "n/a"
        print(f"    {t_atom}->{i_atom}: obs={obs}, ratio={ratio_str}")

    # Directional stratification
    dir_results = {}
    for label, pair_fn in [('QO_to_CHSH', cross_lane_kernel_qc),
                           ('CHSH_to_QO', cross_lane_kernel_cq)]:
        d_cont = build_contingency(sequences, pair_fn)
        d_n = sum(d_cont.values())
        d_mi_obs, d_shuf_mean, d_shuf_std, d_z = shuffle_mi_permutation(
            sequences, pair_fn)
        print(f"\n  {label} kernel routing: N={d_n}, MI={d_mi_obs:.4f}, z={d_z:.2f}")
        dir_results[label] = {
            'n_pairs': d_n,
            'mi_observed': round(d_mi_obs, 4),
            'z_score': round(d_z, 2),
        }

    # C1200 comparison
    c1200_within = 0.247
    print(f"\n  C1200 within-line carryover baseline: {c1200_within}")
    # Note: C1200 used a different metric (carryover signal, not MI)
    # Direct comparison is approximate
    comparison = "PRESENT" if z > 3 else "ABSENT"
    print(f"  Lane-boundary kernel routing: {comparison}")

    return {
        'n_pairs': n,
        'chi2': round(chi2, 1),
        'cramers_v': round(v, 4),
        'mi_observed': round(mi_obs, 4),
        'mi_shuffle_mean': round(shuf_mean, 4),
        'mi_shuffle_std': round(shuf_std, 4),
        'z_score': round(z, 2),
        'carryover_matrix': {
            f"{t}->{i}": {'obs': cont.get((t, i), 0),
                          'ratio': ratios.get((t, i), {}).get('ratio', None)}
            for t in all_terminals for i in all_initials
        },
        'kernel_only': {
            f"{t}->{i}": kernel_cont.get((t, i), 0)
            for t in sorted(KERNEL_ATOMS) for i in sorted(KERNEL_ATOMS)
        },
        'directional': dir_results,
        'c1200_comparison': comparison,
    }


# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 60)
    print("EN_LANE_CROSS_PREDICTION: Stage 1")
    print("=" * 60)

    # Load data
    print("\nLoading data...")
    sequences, n_lines, n_en, n_total = load_en_sequences()
    print(f"  Total B tokens (filtered): {n_total}")
    print(f"  EN-lane tokens (QO+CHSH):  {n_en}")
    print(f"  Lines with 2+ EN tokens:   {len(sequences)}")

    # Count pair types
    pair_counts = count_pairs(sequences)
    print(f"\n  Pair counts:")
    for pt in sorted(pair_counts.keys()):
        print(f"    {pt}: {pair_counts[pt]}")

    total_cross = pair_counts.get('QO_CHSH', 0) + pair_counts.get('CHSH_QO', 0)
    total_same = pair_counts.get('QO_QO', 0) + pair_counts.get('CHSH_CHSH', 0)
    total_all = total_cross + total_same
    if total_all > 0:
        interleave_rate = total_cross / total_all
        print(f"\n  Interleave rate: {interleave_rate:.3f} (cf. C549: 0.563)")

    # Run tests
    t1_results = run_t1(sequences)
    t1a_results = run_t1a(sequences)
    t3_results = run_t3(sequences)
    t4_results = run_t4(sequences)

    # Cross vs same-lane comparison
    cross_mi = t1_results['mi_observed']
    qoqo_mi = t1a_results['QO_QO']['mi_observed']
    chch_mi = t1a_results['CHSH_CHSH']['mi_observed']
    same_avg = (qoqo_mi + chch_mi) / 2 if (qoqo_mi + chch_mi) > 0 else 0
    cross_same_ratio = round(cross_mi / same_avg, 3) if same_avg > 0 else float('inf')
    t1a_results['cross_vs_same_ratio'] = cross_same_ratio

    print(f"\n{'=' * 60}")
    print(f"SUMMARY")
    print(f"{'=' * 60}")
    print(f"  Cross-lane MIDDLE MI: {cross_mi:.4f} bits (z_perm={t1_results['z_score_perm']:.2f}, z_wl={t1_results['z_score_within_lane']:.2f}) -> {t1_results['verdict']}")
    print(f"  Same-lane avg MI:     {same_avg:.4f} bits")
    print(f"  Cross/Same ratio:     {cross_same_ratio}")
    print(f"  QO->CHSH MI:          {t3_results['QO_to_CHSH']['mi_observed']:.4f} (z={t3_results['QO_to_CHSH']['z_score']:.2f})")
    print(f"  CHSH->QO MI:          {t3_results['CHSH_to_QO']['mi_observed']:.4f} (z={t3_results['CHSH_to_QO']['z_score']:.2f})")
    print(f"  Stronger direction:   {t3_results['stronger_direction']}")
    print(f"  Kernel routing:       z={t4_results['z_score']:.2f} -> {t4_results['c1200_comparison']}")

    # Save results
    results = {
        'phase': 'EN_LANE_CROSS_PREDICTION',
        'stage': 1,
        'n_lines_with_2plus_en': len(sequences),
        'n_en_tokens': n_en,
        'n_total_tokens': n_total,
        'pair_counts': pair_counts,
        'interleave_rate': round(interleave_rate, 4) if total_all > 0 else None,
        'T1_cross_lane_middle_mi': t1_results,
        'T1a_same_lane_control': t1a_results,
        'T3_directional_asymmetry': t3_results,
        'T4_kernel_routing': t4_results,
    }

    out_path = RESULTS_DIR / 'lane_cross_prediction.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nResults saved to {out_path}")


if __name__ == '__main__':
    main()
