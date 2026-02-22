"""
MIDDLE_SLOT_INTERACTION: Phase 429
====================================
Tests whether the positional slots within MIDDLEs (INITIAL, MEDIAL, TERMINAL)
interact -- i.e., does the INITIAL atom constrain which TERMINAL atom appears?

Context:
  - C1209: MIDDLEs have ordered [INITIAL-MEDIAL-TERMINAL] positional grammar
  - C1190: Atoms compose additively (behavioral profiles)
  - C1003: No three-way synergy at PREFIX x MIDDLE x SUFFIX level
  - C1065: 21 atom bigram pairs with >80% directional dominance
  - C1198: ke/ek distributionally equivalent (order irrelevance for behavior)
  - C521: Kernel directional asymmetry (e->h blocked, h->k suppressed)

Tests:
  T1:  INITIAL x TERMINAL pairwise compatibility (stratified by length)
  T2:  INITIAL x MEDIAL and MEDIAL x TERMINAL compatibility (3+ char only)
  T3:  Three-way synergy test: does INITIAL+MEDIAL predict TERMINAL
       better than either alone? (3+ char only)
"""
import json
import math
import sys
from collections import defaultdict, Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.voynich import Transcript, Morphology

RESULTS_DIR = Path("phases/MIDDLE_SLOT_INTERACTION/results")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# C1209 positional classification
INITIAL_ATOMS = set('aqeo')
MEDIAL_ATOMS = set('cipdfs')
TERMINAL_ATOMS = set('nmrhly')
FREE_ATOMS = set('kt')

# All classified atoms
ALL_CLASSIFIED = INITIAL_ATOMS | MEDIAL_ATOMS | TERMINAL_ATOMS | FREE_ATOMS

FDR_ALPHA = 0.05


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
                'folio': t.folio,
                'line': t.line,
                'section': t.section,
            })
    return tokens


def classify_positions(middle):
    """Classify each character in a MIDDLE by its actual position.

    Returns dict with 'initial', 'terminal', 'medial' characters.
    For 1-char MIDDLEs, returns None (not applicable).
    For 2-char: initial + terminal only.
    For 3+: initial + medial(s) + terminal.
    """
    n = len(middle)
    if n < 2:
        return None
    return {
        'initial': middle[0],
        'terminal': middle[-1],
        'medial': list(middle[1:-1]) if n > 2 else [],
        'length': n,
    }


def cramers_v(contingency):
    """Compute Cramer's V from a contingency dict {(row, col): count}."""
    rows = sorted(set(r for r, c in contingency))
    cols = sorted(set(c for r, c in contingency))
    n = sum(contingency.values())
    if n == 0:
        return 0.0, 0.0, 0

    # Row and column totals
    row_totals = {r: sum(contingency.get((r, c), 0) for c in cols) for r in rows}
    col_totals = {c: sum(contingency.get((r, c), 0) for r in rows) for c in cols}

    # Chi-squared
    chi2 = 0.0
    for r in rows:
        for c in cols:
            obs = contingency.get((r, c), 0)
            exp = row_totals[r] * col_totals[c] / n if n > 0 else 0
            if exp > 0:
                chi2 += (obs - exp) ** 2 / exp

    k = min(len(rows), len(cols))
    v = (chi2 / (n * (k - 1))) ** 0.5 if k > 1 and n > 0 else 0
    df = (len(rows) - 1) * (len(cols) - 1)

    return chi2, v, df


def mutual_information(contingency):
    """Compute mutual information in bits from contingency dict."""
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


def enrichment_ratios(contingency):
    """Compute enrichment ratios (observed/expected) for all cells."""
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
            if exp >= 5:  # only report if expected >= 5
                ratios[(r, c)] = {
                    'obs': obs,
                    'exp': round(exp, 1),
                    'ratio': round(obs / exp, 2) if exp > 0 else 0,
                }
    return ratios


def conditional_entropy(target_counts, joint_counts):
    """H(Target | Condition) = sum over conditions of P(cond) * H(Target|cond)."""
    total = sum(target_counts.values())
    if total == 0:
        return 0.0

    # Group joint by condition
    cond_groups = defaultdict(Counter)
    for (cond, tgt), count in joint_counts.items():
        cond_groups[cond][tgt] += count

    cond_totals = {cond: sum(counts.values()) for cond, counts in cond_groups.items()}
    grand_total = sum(cond_totals.values())

    h = 0.0
    for cond, counts in cond_groups.items():
        p_cond = cond_totals[cond] / grand_total
        cond_total = cond_totals[cond]
        for tgt, count in counts.items():
            p = count / cond_total
            if p > 0:
                h -= p_cond * p * math.log2(p)
    return h


# ============================================================
# T1: INITIAL x TERMINAL PAIRWISE COMPATIBILITY
# ============================================================

def test_initial_terminal(tokens):
    """Test INITIAL x TERMINAL slot interaction, stratified by length."""
    print(f"\n{'='*70}")
    print("T1: INITIAL x TERMINAL PAIRWISE COMPATIBILITY")
    print("=" * 70)

    # Classify all multi-char MIDDLEs
    records = []
    for t in tokens:
        pos = classify_positions(t['middle'])
        if pos is None:
            continue
        records.append(pos)

    print(f"  Multi-char MIDDLEs: {len(records)}")

    # Stratify by length
    strata = {'all': [], 'len2': [], 'len3': [], 'len4+': []}
    for r in records:
        strata['all'].append(r)
        if r['length'] == 2:
            strata['len2'].append(r)
        elif r['length'] == 3:
            strata['len3'].append(r)
        else:
            strata['len4+'].append(r)

    print(f"  Length 2: {len(strata['len2'])}, Length 3: {len(strata['len3'])}, Length 4+: {len(strata['len4+'])}")

    results = {}

    for stratum_name, stratum_records in strata.items():
        if len(stratum_records) < 50:
            print(f"\n  [{stratum_name}] Too few records ({len(stratum_records)}), skipping")
            continue

        print(f"\n  [{stratum_name}] n={len(stratum_records)}")

        # Build contingency table
        contingency = Counter()
        for r in stratum_records:
            contingency[(r['initial'], r['terminal'])] += 1

        chi2, v, df = cramers_v(contingency)
        mi = mutual_information(contingency)

        print(f"    Chi2={chi2:.1f}, df={df}, Cramer's V={v:.3f}, MI={mi:.3f} bits")

        # Print contingency matrix
        init_atoms = sorted(set(r['initial'] for r in stratum_records))
        term_atoms = sorted(set(r['terminal'] for r in stratum_records))

        # Print header
        header = "    " + " " * 4 + "".join(f"{a:>6}" for a in term_atoms) + "  Total"
        print(header)

        for ia in init_atoms:
            row = f"    {ia:>2}  "
            row_total = 0
            for ta in term_atoms:
                ct = contingency.get((ia, ta), 0)
                row_total += ct
                row += f"{ct:>6}"
            row += f"  {row_total:>5}"
            print(row)

        # Enrichment ratios
        ratios = enrichment_ratios(contingency)
        enriched = [(k, v) for k, v in ratios.items() if v['ratio'] >= 2.0 and v['obs'] >= 10]
        depleted = [(k, v) for k, v in ratios.items() if v['ratio'] <= 0.5 and v['exp'] >= 10]

        enriched.sort(key=lambda x: -x[1]['ratio'])
        depleted.sort(key=lambda x: x[1]['ratio'])

        if enriched:
            print(f"\n    Enriched pairs (ratio >= 2x, obs >= 10):")
            for (ia, ta), info in enriched[:15]:
                i_class = 'I' if ia in INITIAL_ATOMS else 'M' if ia in MEDIAL_ATOMS else 'T' if ia in TERMINAL_ATOMS else 'F'
                t_class = 'I' if ta in INITIAL_ATOMS else 'M' if ta in MEDIAL_ATOMS else 'T' if ta in TERMINAL_ATOMS else 'F'
                print(f"      {ia}({i_class})->{ta}({t_class}): {info['obs']}/{info['exp']} = {info['ratio']}x")

        if depleted:
            print(f"\n    Depleted pairs (ratio <= 0.5x, exp >= 10):")
            for (ia, ta), info in depleted[:15]:
                i_class = 'I' if ia in INITIAL_ATOMS else 'M' if ia in MEDIAL_ATOMS else 'T' if ia in TERMINAL_ATOMS else 'F'
                t_class = 'I' if ta in INITIAL_ATOMS else 'M' if ta in MEDIAL_ATOMS else 'T' if ta in TERMINAL_ATOMS else 'F'
                print(f"      {ia}({i_class})->{ta}({t_class}): {info['obs']}/{info['exp']} = {info['ratio']}x")

        results[stratum_name] = {
            'n': len(stratum_records),
            'chi2': round(chi2, 1),
            'cramers_v': round(v, 4),
            'mutual_info_bits': round(mi, 4),
            'df': df,
            'enriched_pairs': [{'pair': f"{k[0]}->{k[1]}", 'obs': v['obs'], 'exp': v['exp'], 'ratio': v['ratio']}
                               for k, v in enriched[:20]],
            'depleted_pairs': [{'pair': f"{k[0]}->{k[1]}", 'obs': v['obs'], 'exp': v['exp'], 'ratio': v['ratio']}
                               for k, v in depleted[:20]],
        }

    # Compare V across strata to assess length effect
    if 'len2' in results and 'len3' in results:
        v2 = results['len2']['cramers_v']
        v3 = results['len3']['cramers_v']
        v4 = results.get('len4+', {}).get('cramers_v', 0)
        print(f"\n  Length comparison:")
        print(f"    Length 2: V={v2:.3f}")
        print(f"    Length 3: V={v3:.3f}")
        if v4:
            print(f"    Length 4+: V={v4:.3f}")
        if v3 > v2:
            print(f"    -> Interaction STRENGTHENS with distance (genuine slot syntax)")
        elif v3 < v2 * 0.5:
            print(f"    -> Interaction weakens with distance (likely C1065 adjacency effect)")
        else:
            print(f"    -> Interaction comparable across lengths")

    return results


# ============================================================
# T2: INITIAL x MEDIAL and MEDIAL x TERMINAL (3+ char only)
# ============================================================

def test_medial_interactions(tokens):
    """Test INITIAL x MEDIAL and MEDIAL x TERMINAL for 3+ char MIDDLEs."""
    print(f"\n{'='*70}")
    print("T2: MEDIAL SLOT INTERACTIONS (3+ char MIDDLEs only)")
    print("=" * 70)

    records = []
    for t in tokens:
        mid = t['middle']
        if len(mid) < 3:
            continue
        # For 3+ char MIDDLEs, take first medial character
        # (simplification: use first medial for consistency)
        records.append({
            'initial': mid[0],
            'medial_first': mid[1],
            'medial_all': list(mid[1:-1]),
            'terminal': mid[-1],
            'length': len(mid),
        })

    print(f"  MIDDLEs with 3+ chars: {len(records)}")

    results = {}

    # INITIAL x MEDIAL (first medial char)
    print(f"\n  INITIAL x MEDIAL_FIRST:")
    im_cont = Counter()
    for r in records:
        im_cont[(r['initial'], r['medial_first'])] += 1

    chi2_im, v_im, df_im = cramers_v(im_cont)
    mi_im = mutual_information(im_cont)
    print(f"    Chi2={chi2_im:.1f}, df={df_im}, V={v_im:.3f}, MI={mi_im:.3f} bits")

    # Show enrichments
    ratios_im = enrichment_ratios(im_cont)
    enriched_im = [(k, v) for k, v in ratios_im.items() if v['ratio'] >= 2.0 and v['obs'] >= 10]
    enriched_im.sort(key=lambda x: -x[1]['ratio'])
    if enriched_im:
        print(f"    Top enriched INITIAL->MEDIAL:")
        for (ia, ma), info in enriched_im[:10]:
            print(f"      {ia}->{ma}: {info['obs']}/{info['exp']} = {info['ratio']}x")

    results['initial_x_medial'] = {
        'n': len(records),
        'chi2': round(chi2_im, 1),
        'cramers_v': round(v_im, 4),
        'mutual_info_bits': round(mi_im, 4),
    }

    # MEDIAL x TERMINAL (first medial char)
    print(f"\n  MEDIAL_FIRST x TERMINAL:")
    mt_cont = Counter()
    for r in records:
        mt_cont[(r['medial_first'], r['terminal'])] += 1

    chi2_mt, v_mt, df_mt = cramers_v(mt_cont)
    mi_mt = mutual_information(mt_cont)
    print(f"    Chi2={chi2_mt:.1f}, df={df_mt}, V={v_mt:.3f}, MI={mi_mt:.3f} bits")

    ratios_mt = enrichment_ratios(mt_cont)
    enriched_mt = [(k, v) for k, v in ratios_mt.items() if v['ratio'] >= 2.0 and v['obs'] >= 10]
    enriched_mt.sort(key=lambda x: -x[1]['ratio'])
    if enriched_mt:
        print(f"    Top enriched MEDIAL->TERMINAL:")
        for (ma, ta), info in enriched_mt[:10]:
            print(f"      {ma}->{ta}: {info['obs']}/{info['exp']} = {info['ratio']}x")

    results['medial_x_terminal'] = {
        'n': len(records),
        'chi2': round(chi2_mt, 1),
        'cramers_v': round(v_mt, 4),
        'mutual_info_bits': round(mi_mt, 4),
    }

    # Compare I-M vs M-T interaction strength
    print(f"\n  Interaction strength comparison:")
    print(f"    INITIAL x MEDIAL:   V={v_im:.3f}, MI={mi_im:.3f}")
    print(f"    MEDIAL x TERMINAL:  V={v_mt:.3f}, MI={mi_mt:.3f}")

    return results


# ============================================================
# T3: THREE-WAY SYNERGY TEST
# ============================================================

def test_three_way_synergy(tokens):
    """Test if INITIAL+MEDIAL predict TERMINAL better than either alone."""
    print(f"\n{'='*70}")
    print("T3: THREE-WAY SYNERGY TEST (extends C1003 to sub-MIDDLE level)")
    print("=" * 70)

    records = []
    for t in tokens:
        mid = t['middle']
        if len(mid) < 3:
            continue
        records.append({
            'initial': mid[0],
            'medial': mid[1],  # first medial
            'terminal': mid[-1],
        })

    print(f"  3+ char MIDDLEs: {len(records)}")

    if len(records) < 100:
        print("  Too few records for three-way test")
        return {'verdict': 'INSUFFICIENT_DATA'}

    # H(Terminal) -- unconditional entropy
    term_counts = Counter(r['terminal'] for r in records)
    total = len(records)
    h_term = 0
    for count in term_counts.values():
        p = count / total
        if p > 0:
            h_term -= p * math.log2(p)

    # H(Terminal | Initial) -- conditional on initial alone
    init_term = Counter((r['initial'], r['terminal']) for r in records)
    h_term_given_init = conditional_entropy(term_counts, init_term)

    # H(Terminal | Medial) -- conditional on medial alone
    med_term = Counter((r['medial'], r['terminal']) for r in records)
    h_term_given_med = conditional_entropy(term_counts, med_term)

    # H(Terminal | Initial, Medial) -- conditional on both
    init_med_term = Counter()
    for r in records:
        init_med_term[((r['initial'], r['medial']), r['terminal'])] += 1

    # Compute H(T | I,M)
    joint_groups = defaultdict(Counter)
    for (im, t), count in init_med_term.items():
        joint_groups[im][t] += count

    joint_totals = {im: sum(counts.values()) for im, counts in joint_groups.items()}
    grand_total = sum(joint_totals.values())

    h_term_given_both = 0
    for im, counts in joint_groups.items():
        p_im = joint_totals[im] / grand_total
        im_total = joint_totals[im]
        for t, count in counts.items():
            p = count / im_total
            if p > 0:
                h_term_given_both -= p_im * p * math.log2(p)

    # Information measures
    mi_init = h_term - h_term_given_init   # I(T; I)
    mi_med = h_term - h_term_given_med     # I(T; M)
    mi_both = h_term - h_term_given_both   # I(T; I,M)

    # Synergy = I(T; I,M) - I(T; I) - I(T; M) + I(T; I intersection M)
    # Simplified: if I(T; I,M) > I(T; I) + I(T; M), there IS three-way synergy
    # If I(T; I,M) <= I(T; I) + I(T; M), pairwise is sufficient
    additive_prediction = mi_init + mi_med
    synergy = mi_both - additive_prediction

    print(f"\n  Entropy analysis:")
    print(f"    H(Terminal)            = {h_term:.4f} bits")
    print(f"    H(Terminal | Initial)  = {h_term_given_init:.4f} bits")
    print(f"    H(Terminal | Medial)   = {h_term_given_med:.4f} bits")
    print(f"    H(Terminal | I, M)     = {h_term_given_both:.4f} bits")
    print(f"\n  Mutual information:")
    print(f"    I(Terminal; Initial)   = {mi_init:.4f} bits")
    print(f"    I(Terminal; Medial)    = {mi_med:.4f} bits")
    print(f"    I(Terminal; I+M)       = {mi_both:.4f} bits")
    print(f"    Additive prediction    = {additive_prediction:.4f} bits")
    print(f"    Synergy (excess)       = {synergy:+.4f} bits")

    # Interpretation
    if synergy > 0.05:
        verdict = "THREE_WAY_SYNERGY"
        print(f"\n  -> THREE-WAY SYNERGY DETECTED: knowing both Initial and Medial")
        print(f"     predicts Terminal {synergy:.4f} bits better than sum of individual predictions")
    elif synergy < -0.05:
        verdict = "REDUNDANCY"
        print(f"\n  -> REDUNDANCY: Initial and Medial share {-synergy:.4f} bits of")
        print(f"     overlapping information about Terminal")
    else:
        verdict = "PAIRWISE_SUFFICIENT"
        print(f"\n  -> PAIRWISE SUFFICIENT: no significant three-way synergy")
        print(f"     (extends C1003 to sub-MIDDLE level)")

    # Percentage of terminal entropy explained
    pct_init = mi_init / h_term * 100 if h_term > 0 else 0
    pct_med = mi_med / h_term * 100 if h_term > 0 else 0
    pct_both = mi_both / h_term * 100 if h_term > 0 else 0

    print(f"\n  Terminal entropy explained:")
    print(f"    By Initial alone:  {pct_init:.1f}%")
    print(f"    By Medial alone:   {pct_med:.1f}%")
    print(f"    By both together:  {pct_both:.1f}%")

    return {
        'n': len(records),
        'h_terminal': round(h_term, 4),
        'h_terminal_given_initial': round(h_term_given_init, 4),
        'h_terminal_given_medial': round(h_term_given_med, 4),
        'h_terminal_given_both': round(h_term_given_both, 4),
        'mi_initial': round(mi_init, 4),
        'mi_medial': round(mi_med, 4),
        'mi_both': round(mi_both, 4),
        'synergy': round(synergy, 4),
        'verdict': verdict,
    }


# ============================================================
# T4: SENSITIVITY -- AMBIGUOUS ATOMS AND FREE ATOMS
# ============================================================

def test_sensitivity(tokens):
    """Sensitivity analysis: exclude ambiguous atoms, handle FREE atoms."""
    print(f"\n{'='*70}")
    print("T4: SENSITIVITY ANALYSIS")
    print("=" * 70)

    # Identify tokens where initial or terminal atom is ambiguous
    # 'o' is 57% initial (ambiguous), 'k' and 't' are FREE
    records = []
    for t in tokens:
        mid = t['middle']
        if len(mid) < 2:
            continue
        records.append({
            'initial': mid[0],
            'terminal': mid[-1],
            'length': len(mid),
        })

    # Analysis 1: Exclude MIDDLEs starting with 'o' or FREE atoms
    strict = [r for r in records
              if r['initial'] in (INITIAL_ATOMS - {'o'})
              and r['terminal'] in TERMINAL_ATOMS]

    print(f"\n  Strict filter (INITIAL={INITIAL_ATOMS - {'o'}}, TERMINAL={TERMINAL_ATOMS}):")
    print(f"  Records: {len(strict)} of {len(records)} ({len(strict)/len(records)*100:.1f}%)")

    if len(strict) >= 50:
        contingency = Counter()
        for r in strict:
            contingency[(r['initial'], r['terminal'])] += 1
        chi2, v, df = cramers_v(contingency)
        mi = mutual_information(contingency)
        print(f"  Chi2={chi2:.1f}, V={v:.3f}, MI={mi:.3f} bits")
    else:
        chi2, v, mi = 0, 0, 0
        print(f"  Too few records")

    # Analysis 2: Only tokens with unambiguous atoms (>70% in dominant slot)
    # a(86%), q(85%), e(67%) initial; exclude e as <70%
    high_conf_initial = set('aq')
    high_conf_terminal = set('nmyrhl')  # all >71%

    strict2 = [r for r in records
               if r['initial'] in high_conf_initial
               and r['terminal'] in high_conf_terminal]

    print(f"\n  High-confidence filter (INITIAL={{a,q}}, TERMINAL={{n,m,y,r,h,l}}):")
    print(f"  Records: {len(strict2)} of {len(records)} ({len(strict2)/len(records)*100:.1f}%)")

    if len(strict2) >= 50:
        contingency2 = Counter()
        for r in strict2:
            contingency2[(r['initial'], r['terminal'])] += 1
        chi2_2, v_2, df_2 = cramers_v(contingency2)
        mi_2 = mutual_information(contingency2)
        print(f"  Chi2={chi2_2:.1f}, V={v_2:.3f}, MI={mi_2:.3f} bits")

        # Print table
        init_atoms = sorted(set(r['initial'] for r in strict2))
        term_atoms = sorted(set(r['terminal'] for r in strict2))
        header = "  " + " " * 4 + "".join(f"{a:>6}" for a in term_atoms)
        print(header)
        for ia in init_atoms:
            row = f"  {ia:>2}  "
            for ta in term_atoms:
                ct = contingency2.get((ia, ta), 0)
                row += f"{ct:>6}"
            print(row)
    else:
        chi2_2, v_2, mi_2 = 0, 0, 0
        print(f"  Too few records")

    # Analysis 3: FREE atoms as separate category
    free_initial = [r for r in records if r['initial'] in FREE_ATOMS]
    free_terminal = [r for r in records if r['terminal'] in FREE_ATOMS]

    print(f"\n  FREE atom analysis:")
    print(f"    MIDDLEs starting with k or t: {len(free_initial)} ({len(free_initial)/len(records)*100:.1f}%)")
    print(f"    MIDDLEs ending with k or t: {len(free_terminal)} ({len(free_terminal)/len(records)*100:.1f}%)")

    # What terminals follow k-initial vs t-initial?
    for fa in ['k', 't']:
        fa_recs = [r for r in records if r['initial'] == fa]
        if len(fa_recs) >= 20:
            term_dist = Counter(r['terminal'] for r in fa_recs)
            total_fa = len(fa_recs)
            print(f"\n    After {fa}-initial (n={total_fa}):")
            for ta, ct in term_dist.most_common(8):
                print(f"      -> {ta}: {ct} ({ct/total_fa:.1%})")

    return {
        'strict_filter': {
            'n': len(strict),
            'chi2': round(chi2, 1),
            'cramers_v': round(v, 4),
            'mi': round(mi, 4),
        },
        'high_confidence': {
            'n': len(strict2),
            'chi2': round(chi2_2, 1),
            'cramers_v': round(v_2, 4),
            'mi': round(mi_2, 4),
        },
        'free_initial_count': len(free_initial),
        'free_terminal_count': len(free_terminal),
    }


# ============================================================
# MAIN
# ============================================================

def main():
    print("MIDDLE SLOT INTERACTION -- Phase 429")
    print("=" * 70)

    print("\nLoading data...")
    tokens = load_data()
    print(f"Loaded {len(tokens)} tokens")

    multi = [t for t in tokens if len(t['middle']) >= 2]
    print(f"Multi-char MIDDLEs: {len(multi)}")
    three_plus = [t for t in tokens if len(t['middle']) >= 3]
    print(f"3+ char MIDDLEs: {len(three_plus)}")

    results = {}

    # T1: INITIAL x TERMINAL
    results['T1_initial_terminal'] = test_initial_terminal(tokens)

    # T2: MEDIAL interactions (3+ char)
    results['T2_medial_interactions'] = test_medial_interactions(tokens)

    # T3: Three-way synergy
    results['T3_three_way_synergy'] = test_three_way_synergy(tokens)

    # T4: Sensitivity
    results['T4_sensitivity'] = test_sensitivity(tokens)

    # Save
    output_path = RESULTS_DIR / "slot_interaction_results.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\n{'='*70}")
    print(f"Results saved to {output_path}")
    print(f"{'='*70}")


if __name__ == '__main__':
    main()
