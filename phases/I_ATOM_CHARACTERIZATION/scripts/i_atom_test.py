"""
I_ATOM_CHARACTERIZATION: Phase 427
===================================
Tests whether the i-atom (the second extensible atom alongside e) has
its own state dynamics, interacts with k/e, and varies by program.

Context:
  - C1197: Only e and i are extensible (1555 vs 1554 tokens)
  - C1200: k/e state carryover within lines (z=7.90)
  - C901: e stability gradient in Currier A
  - C777: i/ii = FL INITIAL state markers (pos 0.30-0.35)
  - C1195: i = "cycle/iterate" (LOCKED)
  - C557: daiin = 27.7% line-initial, dominant i-token

Tests:
  T1: i-extension gradient (parallel to C901)
  T2: i-state carryover (parallel to C1200)
  T3: i x k/e independence
  T4: i distribution by section/folio
  T5: daiin-controlled replication of T2/T3
"""
import json
import re
import sys
import math
import random
from collections import defaultdict, Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.voynich import Transcript, Morphology

RESULTS_DIR = Path("phases/I_ATOM_CHARACTERIZATION/results")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

N_PERMUTATIONS = 1000

SECTION_NAMES = {
    'S': 'STARS_RECIPE',
    'H': 'HERBAL',
    'B': 'BIO',
    'C': 'COSMO',
    'P': 'PHARMA',
    'T': 'TEXT',
}


# ============================================================
# DATA LOADING
# ============================================================

def load_data():
    """Load all Currier B tokens with morphological decomposition."""
    tx = Transcript()
    morph = Morphology()
    tokens = []
    for t in tx.currier_b():
        m = morph.extract(t.word)
        if m.middle and m.middle != '_EMPTY_':
            tokens.append({
                'word': t.word,
                'middle': m.middle,
                'prefix': m.prefix,
                'suffix': m.suffix,
                'folio': t.folio,
                'line': t.line,
                'section': t.section,
            })
    return tokens


def load_tokens_by_line():
    """Load Currier B tokens grouped by (folio, line), preserving order."""
    tx = Transcript()
    morph = Morphology()
    line_groups = defaultdict(list)
    for t in tx.currier_b():
        m = morph.extract(t.word)
        if m.middle and m.middle != '_EMPTY_':
            line_groups[(t.folio, t.line)].append({
                'word': t.word,
                'middle': m.middle,
                'prefix': m.prefix,
                'suffix': m.suffix,
                'folio': t.folio,
                'line': t.line,
                'section': t.section,
            })
    return line_groups


def max_consecutive_i(middle):
    """Count the maximum run of consecutive 'i' characters in a MIDDLE."""
    max_run = 0
    current = 0
    for ch in middle:
        if ch == 'i':
            current += 1
            max_run = max(max_run, current)
        else:
            current = 0
    return max_run


def has_i(token):
    """Check if token's MIDDLE contains i."""
    return 'i' in token['middle']


def i_count(token):
    """Count i characters in token's MIDDLE."""
    return token['middle'].count('i')


# ============================================================
# T1: I-EXTENSION GRADIENT
# ============================================================

def test_i_extension_gradient(tokens):
    """Map i-extension gradient and ratio families (parallel to C901)."""
    print("=" * 70)
    print("T1: I-EXTENSION GRADIENT (parallel to C901)")
    print("=" * 70)

    # Count consecutive i runs in MIDDLEs
    run_counts = Counter()  # max consecutive i count -> token count
    for t in tokens:
        run = max_consecutive_i(t['middle'])
        if run > 0:
            run_counts[run] += 1

    total_with_i = sum(run_counts.values())
    total_tokens = len(tokens)

    print(f"\n  Total tokens: {total_tokens}")
    print(f"  Tokens with i in MIDDLE: {total_with_i} ({total_with_i/total_tokens:.1%})")
    print(f"\n  {'Max consecutive i':<20} {'Count':<10} {'% of i-tokens':<15}")
    print(f"  {'-'*45}")
    for run_len in sorted(run_counts.keys()):
        ct = run_counts[run_len]
        pct = ct / total_with_i if total_with_i > 0 else 0
        print(f"  {run_len:<20} {ct:<10} {pct:.1%}")

    # Compare to e-extension gradient
    e_run_counts = Counter()
    for t in tokens:
        max_run = 0
        current = 0
        for ch in t['middle']:
            if ch == 'e':
                current += 1
                max_run = max(max_run, current)
            else:
                current = 0
        if max_run > 0:
            e_run_counts[max_run] += 1

    total_with_e = sum(e_run_counts.values())

    print(f"\n  Comparison: i-gradient vs e-gradient")
    print(f"  {'Run length':<12} {'i-count':<10} {'i-%':<10} {'e-count':<10} {'e-%':<10}")
    print(f"  {'-'*52}")
    max_run_len = max(max(run_counts.keys(), default=0), max(e_run_counts.keys(), default=0))
    for r in range(1, max_run_len + 1):
        i_ct = run_counts.get(r, 0)
        e_ct = e_run_counts.get(r, 0)
        i_pct = i_ct / total_with_i if total_with_i > 0 else 0
        e_pct = e_ct / total_with_e if total_with_e > 0 else 0
        print(f"  {r:<12} {i_ct:<10} {i_pct:<10.1%} {e_ct:<10} {e_pct:<10.1%}")

    # Map i-ratio families (MIDDLEs sharing same atoms but differing in i-count)
    print(f"\n  I-Ratio Families (top 15 by base frequency):")
    # Group MIDDLEs by their non-i skeleton
    families = defaultdict(lambda: defaultdict(int))
    for t in tokens:
        mid = t['middle']
        if 'i' not in mid:
            continue
        # Build skeleton: replace runs of i with marker
        skeleton = re.sub(r'i+', 'I', mid)
        i_run = max_consecutive_i(mid)
        families[skeleton][i_run] += 1

    # Sort by total family size
    family_totals = {skel: sum(runs.values()) for skel, runs in families.items()}
    top_families = sorted(family_totals.items(), key=lambda x: -x[1])[:15]

    print(f"  {'Skeleton':<15} {'i=1':<8} {'i=2':<8} {'i=3':<8} {'i=4+':<8} {'Total':<8}")
    print(f"  {'-'*55}")
    for skel, total in top_families:
        runs = families[skel]
        c1 = runs.get(1, 0)
        c2 = runs.get(2, 0)
        c3 = runs.get(3, 0)
        c4 = sum(v for k, v in runs.items() if k >= 4)
        print(f"  {skel:<15} {c1:<8} {c2:<8} {c3:<8} {c4:<8} {total:<8}")

    # Section concentration of higher extensions
    print(f"\n  i-extension by section:")
    section_ext = defaultdict(lambda: Counter())
    for t in tokens:
        run = max_consecutive_i(t['middle'])
        if run > 0:
            sec = SECTION_NAMES.get(t['section'], t['section'])
            section_ext[sec][run] += 1

    print(f"  {'Section':<16} {'i=1':<8} {'i=2':<8} {'i=3+':<8} {'Total':<8} {'ii+ %':<8}")
    print(f"  {'-'*56}")
    for sec in sorted(section_ext.keys()):
        counts = section_ext[sec]
        c1 = counts.get(1, 0)
        c2 = counts.get(2, 0)
        c3p = sum(v for k, v in counts.items() if k >= 3)
        total = sum(counts.values())
        ext_pct = (c2 + c3p) / total if total > 0 else 0
        print(f"  {sec:<16} {c1:<8} {c2:<8} {c3p:<8} {total:<8} {ext_pct:.1%}")

    return {
        'run_counts': dict(run_counts),
        'e_run_counts': dict(e_run_counts),
        'total_with_i': total_with_i,
        'total_with_e': total_with_e,
        'top_families': [(skel, dict(families[skel])) for skel, _ in top_families],
    }


# ============================================================
# T2: I-STATE CARRYOVER
# ============================================================

def test_i_carryover(line_groups, exclude_aiin=False):
    """Test if i-presence in token A predicts i in token B (within-line)."""
    label = "T2" if not exclude_aiin else "T5a"
    suffix = " (excluding aiin)" if exclude_aiin else ""
    print(f"\n{'='*70}")
    print(f"{label}: I-STATE CARRYOVER{suffix}")
    print("=" * 70)

    # Within-line pairs
    within_i_given_i = 0
    within_total_given_i = 0
    within_i_given_no_i = 0
    within_total_given_no_i = 0

    # Cross-line pairs (last token of line N, first token of line N+1)
    cross_i_given_i = 0
    cross_total_given_i = 0
    cross_i_given_no_i = 0
    cross_total_given_no_i = 0

    # Sort lines by folio and line for cross-line analysis
    sorted_keys = sorted(line_groups.keys())

    for idx, key in enumerate(sorted_keys):
        tokens = line_groups[key]
        if exclude_aiin:
            tokens = [t for t in tokens if 'aiin' not in t['middle']]

        # Within-line pairs
        for j in range(len(tokens) - 1):
            a, b = tokens[j], tokens[j + 1]
            a_has_i = has_i(a)
            b_has_i = has_i(b)
            if a_has_i:
                within_total_given_i += 1
                if b_has_i:
                    within_i_given_i += 1
            else:
                within_total_given_no_i += 1
                if b_has_i:
                    within_i_given_no_i += 1

        # Cross-line pair (last of this line -> first of next line, same folio)
        if idx + 1 < len(sorted_keys):
            next_key = sorted_keys[idx + 1]
            if key[0] == next_key[0]:  # same folio
                next_tokens = line_groups[next_key]
                if exclude_aiin:
                    next_tokens = [t for t in next_tokens if 'aiin' not in t['middle']]
                if tokens and next_tokens:
                    a = tokens[-1]
                    b = next_tokens[0]
                    a_has_i = has_i(a)
                    b_has_i = has_i(b)
                    if a_has_i:
                        cross_total_given_i += 1
                        if b_has_i:
                            cross_i_given_i += 1
                    else:
                        cross_total_given_no_i += 1
                        if b_has_i:
                            cross_i_given_no_i += 1

    # Compute rates
    p_i_given_i_w = within_i_given_i / within_total_given_i if within_total_given_i > 0 else 0
    p_i_given_no_i_w = within_i_given_no_i / within_total_given_no_i if within_total_given_no_i > 0 else 0
    delta_within = p_i_given_i_w - p_i_given_no_i_w

    p_i_given_i_c = cross_i_given_i / cross_total_given_i if cross_total_given_i > 0 else 0
    p_i_given_no_i_c = cross_i_given_no_i / cross_total_given_no_i if cross_total_given_no_i > 0 else 0
    delta_cross = p_i_given_i_c - p_i_given_no_i_c

    print(f"\n  WITHIN-LINE pairs:")
    print(f"    P(i in B | i in A)    = {within_i_given_i}/{within_total_given_i} = {p_i_given_i_w:.3f}")
    print(f"    P(i in B | no i in A) = {within_i_given_no_i}/{within_total_given_no_i} = {p_i_given_no_i_w:.3f}")
    print(f"    Delta (carryover):      {delta_within:+.3f}")

    print(f"\n  CROSS-LINE pairs (same folio):")
    print(f"    P(i in B | i in A)    = {cross_i_given_i}/{cross_total_given_i} = {p_i_given_i_c:.3f}")
    print(f"    P(i in B | no i in A) = {cross_i_given_no_i}/{cross_total_given_no_i} = {p_i_given_no_i_c:.3f}")
    print(f"    Delta (carryover):      {delta_cross:+.3f}")

    print(f"\n  Within-line vs cross-line: {delta_within:+.3f} vs {delta_cross:+.3f}")

    # Shuffle test (within-line only)
    print(f"\n  Running {N_PERMUTATIONS} within-line shuffle permutations...")
    random.seed(42)
    perm_count = 0
    for _ in range(N_PERMUTATIONS):
        perm_i_given_i = 0
        perm_total_given_i = 0
        perm_i_given_no_i = 0
        perm_total_given_no_i = 0
        for key in line_groups:
            tokens = line_groups[key]
            if exclude_aiin:
                tokens = [t for t in tokens if 'aiin' not in t['middle']]
            if len(tokens) < 2:
                continue
            middles = [t['middle'] for t in tokens]
            random.shuffle(middles)
            for j in range(len(middles) - 1):
                a_has = 'i' in middles[j]
                b_has = 'i' in middles[j + 1]
                if a_has:
                    perm_total_given_i += 1
                    if b_has:
                        perm_i_given_i += 1
                else:
                    perm_total_given_no_i += 1
                    if b_has:
                        perm_i_given_no_i += 1
        p_perm_i = perm_i_given_i / perm_total_given_i if perm_total_given_i > 0 else 0
        p_perm_no = perm_i_given_no_i / perm_total_given_no_i if perm_total_given_no_i > 0 else 0
        perm_delta = p_perm_i - p_perm_no
        if perm_delta >= delta_within:
            perm_count += 1

    p_value = perm_count / N_PERMUTATIONS
    print(f"  Shuffle p-value: {p_value:.4f}")

    # Compute z-score from permutation distribution
    # Re-run to collect distribution for z-score
    perm_deltas = []
    random.seed(42)
    for _ in range(N_PERMUTATIONS):
        pi_i = 0
        pt_i = 0
        pi_no = 0
        pt_no = 0
        for key in line_groups:
            tokens = line_groups[key]
            if exclude_aiin:
                tokens = [t for t in tokens if 'aiin' not in t['middle']]
            if len(tokens) < 2:
                continue
            middles = [t['middle'] for t in tokens]
            random.shuffle(middles)
            for j in range(len(middles) - 1):
                a_has = 'i' in middles[j]
                b_has = 'i' in middles[j + 1]
                if a_has:
                    pt_i += 1
                    if b_has:
                        pi_i += 1
                else:
                    pt_no += 1
                    if b_has:
                        pi_no += 1
        p1 = pi_i / pt_i if pt_i > 0 else 0
        p2 = pi_no / pt_no if pt_no > 0 else 0
        perm_deltas.append(p1 - p2)

    mean_perm = sum(perm_deltas) / len(perm_deltas)
    std_perm = (sum((d - mean_perm)**2 for d in perm_deltas) / len(perm_deltas))**0.5
    z_score = (delta_within - mean_perm) / std_perm if std_perm > 0 else 0

    print(f"  Permutation mean delta: {mean_perm:+.4f}, std: {std_perm:.4f}")
    print(f"  Z-score: {z_score:.2f}")

    verdict = "CARRYOVER DETECTED" if p_value < 0.05 and delta_within > 0 else "NO CARRYOVER"
    print(f"\n  Verdict: {verdict}")

    return {
        'within_p_i_given_i': round(p_i_given_i_w, 4),
        'within_p_i_given_no_i': round(p_i_given_no_i_w, 4),
        'within_delta': round(delta_within, 4),
        'cross_p_i_given_i': round(p_i_given_i_c, 4),
        'cross_p_i_given_no_i': round(p_i_given_no_i_c, 4),
        'cross_delta': round(delta_cross, 4),
        'shuffle_p': p_value,
        'z_score': round(z_score, 2),
        'verdict': verdict,
    }


# ============================================================
# T3: I x K/E INDEPENDENCE
# ============================================================

def test_i_ke_independence(tokens, exclude_aiin=False):
    """Test whether i-presence is independent of k/e composition."""
    label = "T3" if not exclude_aiin else "T5b"
    suffix = " (excluding aiin)" if exclude_aiin else ""
    print(f"\n{'='*70}")
    print(f"{label}: I x K/E INDEPENDENCE{suffix}")
    print("=" * 70)

    if exclude_aiin:
        tokens = [t for t in tokens if 'aiin' not in t['middle']]

    # Token level: k and e atom fractions in i-tokens vs non-i-tokens
    i_tokens = [t for t in tokens if has_i(t)]
    non_i_tokens = [t for t in tokens if not has_i(t)]

    def atom_fractions(token_list):
        total_chars = 0
        k_count = 0
        e_count = 0
        h_count = 0
        for t in token_list:
            mid = t['middle']
            total_chars += len(mid)
            k_count += mid.count('k')
            e_count += mid.count('e')
            h_count += mid.count('h')
        return {
            'k': k_count / total_chars if total_chars > 0 else 0,
            'e': e_count / total_chars if total_chars > 0 else 0,
            'h': h_count / total_chars if total_chars > 0 else 0,
            'total_chars': total_chars,
        }

    i_fracs = atom_fractions(i_tokens)
    non_i_fracs = atom_fractions(non_i_tokens)

    print(f"\n  Token-level atom fractions:")
    print(f"  {'Atom':<8} {'i-tokens':<15} {'non-i tokens':<15} {'Delta':<10}")
    print(f"  {'-'*48}")
    for atom in ['k', 'e', 'h']:
        delta = i_fracs[atom] - non_i_fracs[atom]
        print(f"  {atom:<8} {i_fracs[atom]:<15.3f} {non_i_fracs[atom]:<15.3f} {delta:+.3f}")

    print(f"\n  i-tokens: {len(i_tokens)} ({len(i_tokens)/len(tokens):.1%})")
    print(f"  non-i tokens: {len(non_i_tokens)} ({len(non_i_tokens)/len(tokens):.1%})")

    # Line level: lines with high i-fraction vs low i-fraction
    line_data = defaultdict(lambda: {'total': 0, 'i_count': 0, 'k_chars': 0, 'e_chars': 0, 'total_chars': 0})
    for t in tokens:
        key = (t['folio'], t['line'])
        line_data[key]['total'] += 1
        if has_i(t):
            line_data[key]['i_count'] += 1
        mid = t['middle']
        line_data[key]['k_chars'] += mid.count('k')
        line_data[key]['e_chars'] += mid.count('e')
        line_data[key]['total_chars'] += len(mid)

    # Split lines into high-i (above median) and low-i
    i_fractions = []
    for key, data in line_data.items():
        if data['total'] >= 3:  # minimum line length
            i_fractions.append((key, data['i_count'] / data['total'], data))

    i_fractions.sort(key=lambda x: x[1])
    median_idx = len(i_fractions) // 2
    low_i_lines = i_fractions[:median_idx]
    high_i_lines = i_fractions[median_idx:]

    def line_ke_balance(lines):
        k_total = sum(d['k_chars'] for _, _, d in lines)
        e_total = sum(d['e_chars'] for _, _, d in lines)
        total = sum(d['total_chars'] for _, _, d in lines)
        return k_total / total if total > 0 else 0, e_total / total if total > 0 else 0

    low_k, low_e = line_ke_balance(low_i_lines)
    high_k, high_e = line_ke_balance(high_i_lines)

    print(f"\n  Line-level (split at median i-fraction):")
    print(f"    Low-i lines ({len(low_i_lines)}):  k={low_k:.3f}, e={low_e:.3f}")
    print(f"    High-i lines ({len(high_i_lines)}): k={high_k:.3f}, e={high_e:.3f}")
    print(f"    Delta k: {high_k - low_k:+.3f}, Delta e: {high_e - low_e:+.3f}")

    # Folio level: correlation between i-fraction and k/e balance
    folio_data = defaultdict(lambda: {'total': 0, 'i_count': 0, 'k_chars': 0, 'e_chars': 0, 'total_chars': 0})
    for t in tokens:
        folio_data[t['folio']]['total'] += 1
        if has_i(t):
            folio_data[t['folio']]['i_count'] += 1
        mid = t['middle']
        folio_data[t['folio']]['k_chars'] += mid.count('k')
        folio_data[t['folio']]['e_chars'] += mid.count('e')
        folio_data[t['folio']]['total_chars'] += len(mid)

    # Pearson correlation: i-fraction vs k-fraction, i-fraction vs e-fraction
    folios = [(f, d['i_count'] / d['total'],
               d['k_chars'] / d['total_chars'],
               d['e_chars'] / d['total_chars'])
              for f, d in folio_data.items() if d['total'] >= 20]

    def pearson_r(xs, ys):
        n = len(xs)
        if n < 3:
            return 0.0
        mx = sum(xs) / n
        my = sum(ys) / n
        num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
        dx = sum((x - mx)**2 for x in xs)**0.5
        dy = sum((y - my)**2 for y in ys)**0.5
        return num / (dx * dy) if dx > 0 and dy > 0 else 0.0

    i_fracs_folio = [f[1] for f in folios]
    k_fracs_folio = [f[2] for f in folios]
    e_fracs_folio = [f[3] for f in folios]

    r_ik = pearson_r(i_fracs_folio, k_fracs_folio)
    r_ie = pearson_r(i_fracs_folio, e_fracs_folio)
    r_ke = pearson_r(k_fracs_folio, e_fracs_folio)

    print(f"\n  Folio-level correlations ({len(folios)} folios with 20+ tokens):")
    print(f"    r(i, k) = {r_ik:+.3f}")
    print(f"    r(i, e) = {r_ie:+.3f}")
    print(f"    r(k, e) = {r_ke:+.3f} (reference)")

    # Chi-squared: i-presence vs k/e dominance at token level
    # Classify each token as k-dominant, e-dominant, or neither
    chi2_table = {'i_k': 0, 'i_e': 0, 'i_neither': 0,
                  'no_i_k': 0, 'no_i_e': 0, 'no_i_neither': 0}
    for t in tokens:
        mid = t['middle']
        k_ct = mid.count('k')
        e_ct = mid.count('e')
        has_i_flag = 'i' in mid
        if k_ct > e_ct:
            dom = 'k'
        elif e_ct > k_ct:
            dom = 'e'
        else:
            dom = 'neither'

        if has_i_flag:
            chi2_table[f'i_{dom}'] += 1
        else:
            chi2_table[f'no_i_{dom}'] += 1

    print(f"\n  Token-level chi2 (i-presence x k/e dominance):")
    print(f"    i+k-dom: {chi2_table['i_k']}, i+e-dom: {chi2_table['i_e']}, i+neither: {chi2_table['i_neither']}")
    print(f"    no-i+k-dom: {chi2_table['no_i_k']}, no-i+e-dom: {chi2_table['no_i_e']}, no-i+neither: {chi2_table['no_i_neither']}")

    # Simple chi2 computation
    observed = [chi2_table['i_k'], chi2_table['i_e'], chi2_table['i_neither'],
                chi2_table['no_i_k'], chi2_table['no_i_e'], chi2_table['no_i_neither']]
    row_i = sum(observed[:3])
    row_no = sum(observed[3:])
    col_k = observed[0] + observed[3]
    col_e = observed[1] + observed[4]
    col_n = observed[2] + observed[5]
    total = row_i + row_no

    chi2 = 0
    for obs, row, col in [(observed[0], row_i, col_k), (observed[1], row_i, col_e),
                           (observed[2], row_i, col_n), (observed[3], row_no, col_k),
                           (observed[4], row_no, col_e), (observed[5], row_no, col_n)]:
        exp = row * col / total if total > 0 else 0
        if exp > 0:
            chi2 += (obs - exp)**2 / exp

    print(f"    Chi2 = {chi2:.1f} (df=2)")

    return {
        'i_token_fracs': {k: round(v, 4) for k, v in i_fracs.items() if k != 'total_chars'},
        'non_i_token_fracs': {k: round(v, 4) for k, v in non_i_fracs.items() if k != 'total_chars'},
        'n_i_tokens': len(i_tokens),
        'n_non_i_tokens': len(non_i_tokens),
        'line_high_i_ke': {'k': round(high_k, 4), 'e': round(high_e, 4)},
        'line_low_i_ke': {'k': round(low_k, 4), 'e': round(low_e, 4)},
        'folio_r_ik': round(r_ik, 3),
        'folio_r_ie': round(r_ie, 3),
        'folio_r_ke': round(r_ke, 3),
        'chi2': round(chi2, 1),
    }


# ============================================================
# T4: I DISTRIBUTION BY SECTION/FOLIO
# ============================================================

def test_i_distribution(tokens):
    """Map i-fraction across sections and folios."""
    print(f"\n{'='*70}")
    print("T4: I DISTRIBUTION BY SECTION/FOLIO")
    print("=" * 70)

    # By section
    section_data = defaultdict(lambda: {'total': 0, 'i_count': 0, 'k_chars': 0, 'e_chars': 0, 'i_chars': 0, 'total_chars': 0})
    for t in tokens:
        sec = SECTION_NAMES.get(t['section'], t['section'])
        section_data[sec]['total'] += 1
        if has_i(t):
            section_data[sec]['i_count'] += 1
        mid = t['middle']
        section_data[sec]['k_chars'] += mid.count('k')
        section_data[sec]['e_chars'] += mid.count('e')
        section_data[sec]['i_chars'] += mid.count('i')
        section_data[sec]['total_chars'] += len(mid)

    print(f"\n  By section:")
    print(f"  {'Section':<16} {'Tokens':<8} {'i-tokens':<10} {'i-frac':<8} {'k-frac':<8} {'e-frac':<8} {'i-char%':<8}")
    print(f"  {'-'*66}")
    for sec in sorted(section_data.keys()):
        d = section_data[sec]
        i_frac = d['i_count'] / d['total'] if d['total'] > 0 else 0
        k_frac = d['k_chars'] / d['total_chars'] if d['total_chars'] > 0 else 0
        e_frac = d['e_chars'] / d['total_chars'] if d['total_chars'] > 0 else 0
        i_char_frac = d['i_chars'] / d['total_chars'] if d['total_chars'] > 0 else 0
        print(f"  {sec:<16} {d['total']:<8} {d['i_count']:<10} {i_frac:.3f}   {k_frac:.3f}   {e_frac:.3f}   {i_char_frac:.3f}")

    # By folio: compute i-fraction, rank, show top/bottom
    folio_data = defaultdict(lambda: {'total': 0, 'i_count': 0, 'section': '', 'i_chars': 0, 'total_chars': 0})
    for t in tokens:
        folio_data[t['folio']]['total'] += 1
        folio_data[t['folio']]['section'] = t['section']
        if has_i(t):
            folio_data[t['folio']]['i_count'] += 1
        mid = t['middle']
        folio_data[t['folio']]['i_chars'] += mid.count('i')
        folio_data[t['folio']]['total_chars'] += len(mid)

    folio_fracs = []
    for f, d in folio_data.items():
        if d['total'] >= 20:
            folio_fracs.append((f, d['i_count'] / d['total'], d['section'], d['total']))

    folio_fracs.sort(key=lambda x: -x[1])

    print(f"\n  Top 10 i-heavy folios:")
    print(f"  {'Folio':<10} {'Section':<8} {'i-frac':<10} {'Tokens':<8}")
    print(f"  {'-'*36}")
    for f, frac, sec, total in folio_fracs[:10]:
        print(f"  {f:<10} {sec:<8} {frac:.3f}     {total:<8}")

    print(f"\n  Bottom 10 i-depleted folios:")
    print(f"  {'Folio':<10} {'Section':<8} {'i-frac':<10} {'Tokens':<8}")
    print(f"  {'-'*36}")
    for f, frac, sec, total in folio_fracs[-10:]:
        print(f"  {f:<10} {sec:<8} {frac:.3f}     {total:<8}")

    # Variance analysis: is i section-determined or program-specific?
    # Within-section variance vs between-section variance
    section_means = {}
    section_vars = {}
    for sec_code in set(t['section'] for t in tokens):
        sec_folios = [frac for _, frac, s, _ in folio_fracs if s == sec_code]
        if len(sec_folios) >= 3:
            mean = sum(sec_folios) / len(sec_folios)
            var = sum((f - mean)**2 for f in sec_folios) / len(sec_folios)
            sec_name = SECTION_NAMES.get(sec_code, sec_code)
            section_means[sec_name] = mean
            section_vars[sec_name] = var

    global_fracs = [f[1] for f in folio_fracs]
    global_mean = sum(global_fracs) / len(global_fracs) if global_fracs else 0
    global_var = sum((f - global_mean)**2 for f in global_fracs) / len(global_fracs) if global_fracs else 0

    # Within-section variance (average of section variances, weighted by n)
    within_var = sum(section_vars.values()) / len(section_vars) if section_vars else 0
    between_var = global_var - within_var if global_var > within_var else 0

    print(f"\n  Variance decomposition:")
    print(f"    Global variance:         {global_var:.6f}")
    print(f"    Mean within-section var: {within_var:.6f}")
    print(f"    Between-section var:     {between_var:.6f}")
    ratio = within_var / between_var if between_var > 0 else float('inf')
    print(f"    Within/Between ratio:    {ratio:.2f}")
    print(f"    {'PROGRAM-SPECIFIC' if ratio > 1.5 else 'SECTION-DETERMINED' if ratio < 0.5 else 'MIXED'}")

    # Per-section CV (coefficient of variation)
    print(f"\n  Per-section CV (coefficient of variation):")
    for sec in sorted(section_vars.keys()):
        mean = section_means[sec]
        cv = (section_vars[sec]**0.5) / mean if mean > 0 else 0
        print(f"    {sec}: CV={cv:.2f} (mean={mean:.3f})")

    return {
        'section_data': {k: {'total': v['total'], 'i_count': v['i_count'],
                             'i_frac': round(v['i_count']/v['total'], 4) if v['total'] > 0 else 0}
                        for k, v in section_data.items()},
        'n_folios': len(folio_fracs),
        'global_mean': round(global_mean, 4),
        'global_var': round(global_var, 6),
        'within_var': round(within_var, 6),
        'between_var': round(between_var, 6),
        'determination': 'PROGRAM_SPECIFIC' if ratio > 1.5 else 'SECTION_DETERMINED' if ratio < 0.5 else 'MIXED',
    }


# ============================================================
# T6a: I AS CARRYOVER INTERRUPTER
# ============================================================

def test_i_carryover_interrupt(line_groups):
    """Test if i-tokens break the k/e carryover chain (C1200)."""
    print(f"\n{'='*70}")
    print("T6a: I AS CARRYOVER INTERRUPTER")
    print("=" * 70)
    print("  Does an i-token between k-terminal and next token break k/e carryover?")

    # For triples A-B-C: A is k-terminal, measure P(C starts e)
    # Split by whether B has i in MIDDLE
    with_i = {'e_init': 0, 'k_init': 0, 'other': 0}
    without_i = {'e_init': 0, 'k_init': 0, 'other': 0}

    for key in sorted(line_groups.keys()):
        tokens = line_groups[key]
        for j in range(len(tokens) - 2):
            a, b, c = tokens[j], tokens[j + 1], tokens[j + 2]
            term_a = a['middle'][-1]
            if term_a != 'k':
                continue
            init_c = c['middle'][0]
            bucket = with_i if has_i(b) else without_i
            if init_c == 'e':
                bucket['e_init'] += 1
            elif init_c == 'k':
                bucket['k_init'] += 1
            else:
                bucket['other'] += 1

    # Also do same for e-terminal predecessors
    with_i_e = {'e_init': 0, 'k_init': 0, 'other': 0}
    without_i_e = {'e_init': 0, 'k_init': 0, 'other': 0}

    for key in sorted(line_groups.keys()):
        tokens = line_groups[key]
        for j in range(len(tokens) - 2):
            a, b, c = tokens[j], tokens[j + 1], tokens[j + 2]
            term_a = a['middle'][-1]
            if term_a != 'e':
                continue
            init_c = c['middle'][0]
            bucket = with_i_e if has_i(b) else without_i_e
            if init_c == 'e':
                bucket['e_init'] += 1
            elif init_c == 'k':
                bucket['k_init'] += 1
            else:
                bucket['other'] += 1

    # Compute rates for k-terminal
    wi_total = with_i['e_init'] + with_i['k_init'] + with_i['other']
    wo_total = without_i['e_init'] + without_i['k_init'] + without_i['other']
    wi_e_rate = with_i['e_init'] / wi_total if wi_total > 0 else 0
    wo_e_rate = without_i['e_init'] / wo_total if wo_total > 0 else 0

    print(f"\n  After k-terminal token A, through mediator B to token C:")
    print(f"    B has i:    P(C starts e) = {with_i['e_init']}/{wi_total} = {wi_e_rate:.3f}")
    print(f"    B no i:     P(C starts e) = {without_i['e_init']}/{wo_total} = {wo_e_rate:.3f}")
    print(f"    Delta: {wi_e_rate - wo_e_rate:+.3f}")
    if wi_total > 0 and wo_total > 0:
        if wi_e_rate < wo_e_rate:
            print(f"    -> i-mediator REDUCES k->e carryover (interruption)")
        elif wi_e_rate > wo_e_rate:
            print(f"    -> i-mediator INCREASES k->e carryover")
        else:
            print(f"    -> No effect")

    # Compute rates for e-terminal
    wie_total = with_i_e['e_init'] + with_i_e['k_init'] + with_i_e['other']
    woe_total = without_i_e['e_init'] + without_i_e['k_init'] + without_i_e['other']
    wie_e_rate = with_i_e['e_init'] / wie_total if wie_total > 0 else 0
    woe_e_rate = without_i_e['e_init'] / woe_total if woe_total > 0 else 0

    print(f"\n  After e-terminal token A, through mediator B to token C:")
    print(f"    B has i:    P(C starts e) = {with_i_e['e_init']}/{wie_total} = {wie_e_rate:.3f}")
    print(f"    B no i:     P(C starts e) = {without_i_e['e_init']}/{woe_total} = {woe_e_rate:.3f}")
    print(f"    Delta: {wie_e_rate - woe_e_rate:+.3f}")

    # Baseline: overall P(token starts e)
    all_inits = Counter()
    for key in line_groups:
        for t in line_groups[key]:
            all_inits[t['middle'][0]] += 1
    total_all = sum(all_inits.values())
    baseline_e = all_inits.get('e', 0) / total_all if total_all > 0 else 0
    baseline_k = all_inits.get('k', 0) / total_all if total_all > 0 else 0
    print(f"\n  Baseline P(starts e) = {baseline_e:.3f}, P(starts k) = {baseline_k:.3f}")

    # If i interrupts, the with-i rate should be closer to baseline
    if wi_total > 0 and wo_total > 0:
        dev_with = abs(wi_e_rate - baseline_e)
        dev_without = abs(wo_e_rate - baseline_e)
        print(f"\n  Deviation from baseline:")
        print(f"    With i-mediator:    |{wi_e_rate:.3f} - {baseline_e:.3f}| = {dev_with:.3f}")
        print(f"    Without i-mediator: |{wo_e_rate:.3f} - {baseline_e:.3f}| = {dev_without:.3f}")
        if dev_with < dev_without:
            print(f"    -> i-mediator moves rate TOWARD baseline (INTERRUPTION)")
        else:
            print(f"    -> i-mediator does NOT interrupt carryover")

    return {
        'k_terminal_with_i': dict(with_i),
        'k_terminal_without_i': dict(without_i),
        'k_term_wi_e_rate': round(wi_e_rate, 4),
        'k_term_wo_e_rate': round(wo_e_rate, 4),
        'e_terminal_with_i': dict(with_i_e),
        'e_terminal_without_i': dict(without_i_e),
        'baseline_e': round(baseline_e, 4),
    }


# ============================================================
# T6b: LINE-POSITION K/E/H DRIFT IN PARAGRAPHS
# ============================================================

def test_paragraph_drift(tokens):
    """Test kernel composition drift through paragraph body (extends C965)."""
    print(f"\n{'='*70}")
    print("T6b: LINE-POSITION K/E/H DRIFT IN PARAGRAPHS (extends C965)")
    print("=" * 70)
    print("  C965 baseline: h +0.10, e -0.086 through body. Does k shift?")

    # Group tokens by (folio, paragraph_line_index)
    # We need paragraph structure: group by folio, identify paragraphs
    # Use line number ordering within folio as proxy for paragraph position
    folio_lines = defaultdict(lambda: defaultdict(list))
    for t in tokens:
        folio_lines[t['folio']][t['line']].append(t)

    # For each folio, sort lines and assign position within folio
    # Split into quintiles (Q0=earliest, Q4=latest)
    quintile_data = {q: {'k_chars': 0, 'e_chars': 0, 'h_chars': 0, 'i_chars': 0,
                         'total_chars': 0, 'n_tokens': 0, 'n_lines': 0}
                     for q in range(5)}

    for folio, lines in folio_lines.items():
        sorted_line_nums = sorted(lines.keys())
        n_lines = len(sorted_line_nums)
        if n_lines < 5:
            continue  # need at least 5 lines for quintiles

        for idx, line_num in enumerate(sorted_line_nums):
            q = min(int(idx / n_lines * 5), 4)
            line_tokens = lines[line_num]
            quintile_data[q]['n_lines'] += 1
            for t in line_tokens:
                mid = t['middle']
                quintile_data[q]['k_chars'] += mid.count('k')
                quintile_data[q]['e_chars'] += mid.count('e')
                quintile_data[q]['h_chars'] += mid.count('h')
                quintile_data[q]['i_chars'] += mid.count('i')
                quintile_data[q]['total_chars'] += len(mid)
                quintile_data[q]['n_tokens'] += 1

    print(f"\n  {'Quintile':<10} {'Lines':<8} {'Tokens':<8} {'k-frac':<8} {'e-frac':<8} {'h-frac':<8} {'i-frac':<8} {'tok/line':<8}")
    print(f"  {'-'*66}")

    q_results = {}
    for q in range(5):
        d = quintile_data[q]
        tc = d['total_chars']
        k_f = d['k_chars'] / tc if tc > 0 else 0
        e_f = d['e_chars'] / tc if tc > 0 else 0
        h_f = d['h_chars'] / tc if tc > 0 else 0
        i_f = d['i_chars'] / tc if tc > 0 else 0
        tpl = d['n_tokens'] / d['n_lines'] if d['n_lines'] > 0 else 0
        print(f"  Q{q:<9} {d['n_lines']:<8} {d['n_tokens']:<8} {k_f:.4f}  {e_f:.4f}  {h_f:.4f}  {i_f:.4f}  {tpl:.1f}")
        q_results[f'Q{q}'] = {
            'k': round(k_f, 4), 'e': round(e_f, 4),
            'h': round(h_f, 4), 'i': round(i_f, 4),
            'n_lines': d['n_lines'], 'tok_per_line': round(tpl, 1),
        }

    # Compute gradients (Q4 - Q0)
    k_grad = q_results['Q4']['k'] - q_results['Q0']['k']
    e_grad = q_results['Q4']['e'] - q_results['Q0']['e']
    h_grad = q_results['Q4']['h'] - q_results['Q0']['h']
    i_grad = q_results['Q4']['i'] - q_results['Q0']['i']

    print(f"\n  Gradients (Q4 - Q0):")
    print(f"    k: {k_grad:+.4f}")
    print(f"    e: {e_grad:+.4f}")
    print(f"    h: {h_grad:+.4f} (C965 reports +0.10)")
    print(f"    i: {i_grad:+.4f}")

    # Pearson correlation with quintile index
    qs = [0, 1, 2, 3, 4]
    def corr_with_q(atom):
        vals = [q_results[f'Q{q}'][atom] for q in qs]
        n = 5
        mx = sum(qs) / n
        my = sum(vals) / n
        num = sum((x - mx) * (y - my) for x, y in zip(qs, vals))
        dx = sum((x - mx)**2 for x in qs)**0.5
        dy = sum((y - my)**2 for y in vals)**0.5
        return num / (dx * dy) if dx > 0 and dy > 0 else 0

    print(f"\n  Correlation with quintile position:")
    for atom in ['k', 'e', 'h', 'i']:
        r = corr_with_q(atom)
        print(f"    r({atom}, position) = {r:+.3f}")

    return {
        'quintiles': q_results,
        'gradients': {'k': round(k_grad, 4), 'e': round(e_grad, 4),
                      'h': round(h_grad, 4), 'i': round(i_grad, 4)},
    }


# ============================================================
# T6c: I-COUNT PREDICTS ENERGY PROFILE
# ============================================================

def test_i_count_energy(tokens):
    """Test if lines with ii have different k/e ratios than lines with single i."""
    print(f"\n{'='*70}")
    print("T6c: I-COUNT PREDICTS ENERGY PROFILE")
    print("=" * 70)

    # Group tokens by line, classify lines by max i-run
    line_data = defaultdict(lambda: {'tokens': [], 'max_i_run': 0})
    for t in tokens:
        key = (t['folio'], t['line'])
        line_data[key]['tokens'].append(t)
        run = max_consecutive_i(t['middle'])
        if run > line_data[key]['max_i_run']:
            line_data[key]['max_i_run'] = run

    # Classify lines: no-i, single-i, double-i+
    categories = {
        'no_i': {'k_chars': 0, 'e_chars': 0, 'h_chars': 0, 'total_chars': 0, 'n_lines': 0, 'n_tokens': 0},
        'single_i': {'k_chars': 0, 'e_chars': 0, 'h_chars': 0, 'total_chars': 0, 'n_lines': 0, 'n_tokens': 0},
        'double_i': {'k_chars': 0, 'e_chars': 0, 'h_chars': 0, 'total_chars': 0, 'n_lines': 0, 'n_tokens': 0},
    }

    for key, data in line_data.items():
        if len(data['tokens']) < 3:
            continue
        max_run = data['max_i_run']
        if max_run == 0:
            cat = 'no_i'
        elif max_run == 1:
            cat = 'single_i'
        else:
            cat = 'double_i'

        categories[cat]['n_lines'] += 1
        for t in data['tokens']:
            mid = t['middle']
            categories[cat]['k_chars'] += mid.count('k')
            categories[cat]['e_chars'] += mid.count('e')
            categories[cat]['h_chars'] += mid.count('h')
            categories[cat]['total_chars'] += len(mid)
            categories[cat]['n_tokens'] += 1

    print(f"\n  {'Category':<12} {'Lines':<8} {'Tokens':<8} {'k-frac':<8} {'e-frac':<8} {'h-frac':<8} {'tok/line':<8}")
    print(f"  {'-'*60}")

    cat_results = {}
    for cat in ['no_i', 'single_i', 'double_i']:
        d = categories[cat]
        tc = d['total_chars']
        k_f = d['k_chars'] / tc if tc > 0 else 0
        e_f = d['e_chars'] / tc if tc > 0 else 0
        h_f = d['h_chars'] / tc if tc > 0 else 0
        tpl = d['n_tokens'] / d['n_lines'] if d['n_lines'] > 0 else 0
        print(f"  {cat:<12} {d['n_lines']:<8} {d['n_tokens']:<8} {k_f:.4f}  {e_f:.4f}  {h_f:.4f}  {tpl:.1f}")
        cat_results[cat] = {
            'n_lines': d['n_lines'], 'n_tokens': d['n_tokens'],
            'k': round(k_f, 4), 'e': round(e_f, 4), 'h': round(h_f, 4),
        }

    # Compare: do ii-lines differ from i-lines?
    if cat_results['single_i']['n_lines'] > 0 and cat_results['double_i']['n_lines'] > 0:
        dk = cat_results['double_i']['k'] - cat_results['single_i']['k']
        de = cat_results['double_i']['e'] - cat_results['single_i']['e']
        dh = cat_results['double_i']['h'] - cat_results['single_i']['h']
        print(f"\n  double_i vs single_i:")
        print(f"    Delta k: {dk:+.4f}")
        print(f"    Delta e: {de:+.4f}")
        print(f"    Delta h: {dh:+.4f}")

    # Also compare: i-lines (any) vs no-i lines
    if cat_results['no_i']['n_lines'] > 0:
        # Combine single_i and double_i
        any_i_k = (categories['single_i']['k_chars'] + categories['double_i']['k_chars'])
        any_i_e = (categories['single_i']['e_chars'] + categories['double_i']['e_chars'])
        any_i_h = (categories['single_i']['h_chars'] + categories['double_i']['h_chars'])
        any_i_tc = (categories['single_i']['total_chars'] + categories['double_i']['total_chars'])

        any_i_kf = any_i_k / any_i_tc if any_i_tc > 0 else 0
        any_i_ef = any_i_e / any_i_tc if any_i_tc > 0 else 0
        any_i_hf = any_i_h / any_i_tc if any_i_tc > 0 else 0

        dk2 = any_i_kf - cat_results['no_i']['k']
        de2 = any_i_ef - cat_results['no_i']['e']
        dh2 = any_i_hf - cat_results['no_i']['h']
        print(f"\n  any-i lines vs no-i lines:")
        print(f"    Delta k: {dk2:+.4f}")
        print(f"    Delta e: {de2:+.4f}")
        print(f"    Delta h: {dh2:+.4f}")

    return cat_results


# ============================================================
# MAIN
# ============================================================

def main():
    print("I-ATOM CHARACTERIZATION -- Phase 427")
    print("=" * 70)

    print("\nLoading data...")
    tokens = load_data()
    line_groups = load_tokens_by_line()
    n_tokens = len(tokens)
    n_lines = len(line_groups)
    print(f"Loaded {n_tokens} tokens across {n_lines} lines")

    results = {}

    # T1: Extension gradient
    results['T1_extension_gradient'] = test_i_extension_gradient(tokens)

    # T2: State carryover
    results['T2_carryover'] = test_i_carryover(line_groups, exclude_aiin=False)

    # T3: i x k/e independence
    results['T3_ke_independence'] = test_i_ke_independence(tokens, exclude_aiin=False)

    # T4: Distribution by section/folio
    results['T4_distribution'] = test_i_distribution(tokens)

    # T5: daiin-controlled replication
    results['T5a_carryover_no_aiin'] = test_i_carryover(line_groups, exclude_aiin=True)
    results['T5b_independence_no_aiin'] = test_i_ke_independence(tokens, exclude_aiin=True)

    # T6: Nested iteration tests
    results['T6a_carryover_interrupt'] = test_i_carryover_interrupt(line_groups)
    results['T6b_paragraph_drift'] = test_paragraph_drift(tokens)
    results['T6c_i_count_energy'] = test_i_count_energy(tokens)

    # Save
    output_path = RESULTS_DIR / "i_atom_results.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\n{'='*70}")
    print(f"Results saved to {output_path}")
    print(f"{'='*70}")


if __name__ == '__main__':
    main()
