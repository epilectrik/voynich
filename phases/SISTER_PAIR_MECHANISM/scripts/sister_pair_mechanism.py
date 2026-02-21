"""
SISTER_PAIR_MECHANISM - Phase 420

Investigates whether the 52.9% unexplained variance in sister-pair choice (C639)
is genuine free variation or structured by unmeasured predictors.

8-test battery:
  SP-0: Slot equivalence sanity check (same MIDDLE+SUFFIX under both sisters)
  SP-1: Positional mediation of sister residual (C929 position absorbs C639?)
  SP-2: Dynamical consequence of sister residual (AXM, hazard, escape)
  SP-3: Concentration vs uniformity (ICC at folio vs paragraph level)
  SP-4: Bridge/dark pipeline coupling (C1146 link)
  SP-5: ok/ot parallel test (same mechanism or independent?)
  SP-6: Successor profile decomposition (matched position+section+role)
  SP-7: Boundary-divergence interaction (entry JSD, AXM return)

Critical framing: Any positive result = within-class control knob (C506.b, C1026),
NOT grammar reopening. C121 (49 classes) is Tier 0 FROZEN.

Depends on: C639, C408-C412, C929, C1146, C1157-C1168, C506.b, C1026
"""

import json
import sys
import math
from pathlib import Path
from collections import defaultdict, Counter
from itertools import combinations
import random

ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(ROOT))

from scripts.voynich import Transcript, Morphology


# ============================================================
# UTILITIES
# ============================================================

def round_floats(obj, digits=4):
    """Recursively round floats in nested structures."""
    if isinstance(obj, float):
        return round(obj, digits)
    if isinstance(obj, dict):
        return {k: round_floats(v, digits) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [round_floats(x, digits) for x in obj]
    return obj


def pearson_r(xs, ys):
    """Pearson correlation coefficient."""
    n = len(xs)
    if n < 3:
        return 0.0
    mx = sum(xs) / n
    my = sum(ys) / n
    sx = math.sqrt(sum((x - mx) ** 2 for x in xs) / (n - 1)) if n > 1 else 0
    sy = math.sqrt(sum((y - my) ** 2 for y in ys) / (n - 1)) if n > 1 else 0
    if sx == 0 or sy == 0:
        return 0.0
    cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / (n - 1)
    return cov / (sx * sy)


def _rank(vals):
    """Rank values with average ties."""
    indexed = sorted(enumerate(vals), key=lambda x: x[1])
    ranks = [0.0] * len(vals)
    i = 0
    while i < len(indexed):
        j = i
        while j < len(indexed) and indexed[j][1] == indexed[i][1]:
            j += 1
        avg_rank = (i + j + 1) / 2.0
        for k in range(i, j):
            ranks[indexed[k][0]] = avg_rank
        i = j
    return ranks


def spearman_r(xs, ys):
    """Spearman rank correlation with approximate p-value."""
    n = len(xs)
    if n < 3:
        return 0.0, 1.0
    rx = _rank(xs)
    ry = _rank(ys)
    rho = pearson_r(rx, ry)
    if n < 10:
        return rho, 1.0  # Too few for p-value
    t = rho * math.sqrt((n - 2) / (1 - rho ** 2 + 1e-15))
    # Approximate two-tailed p from t-distribution using normal approx
    p = 2 * (1 - _normal_cdf(abs(t)))
    return rho, p


def _normal_cdf(x):
    """Approximate standard normal CDF."""
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def partial_spearman(xs, ys, zs):
    """Partial Spearman: correlation of xs,ys controlling for zs."""
    n = len(xs)
    if n < 5:
        return 0.0, 1.0
    rx = _rank(xs)
    ry = _rank(ys)
    rz = _rank(zs)
    rxy = pearson_r(rx, ry)
    rxz = pearson_r(rx, rz)
    ryz = pearson_r(ry, rz)
    denom = math.sqrt((1 - rxz ** 2) * (1 - ryz ** 2) + 1e-15)
    partial = (rxy - rxz * ryz) / denom
    # Approximate p
    df = n - 3
    if df < 1:
        return partial, 1.0
    t = partial * math.sqrt(df / (1 - partial ** 2 + 1e-15))
    p = 2 * (1 - _normal_cdf(abs(t)))
    return partial, p


def jensen_shannon(p_counts, q_counts):
    """Jensen-Shannon divergence between two count distributions."""
    keys = set(p_counts.keys()) | set(q_counts.keys())
    if not keys:
        return 0.0
    total_p = sum(p_counts.values())
    total_q = sum(q_counts.values())
    if total_p == 0 or total_q == 0:
        return 0.0
    jsd = 0.0
    for k in keys:
        p = p_counts.get(k, 0) / total_p
        q = q_counts.get(k, 0) / total_q
        m = (p + q) / 2
        if p > 0 and m > 0:
            jsd += 0.5 * p * math.log2(p / m)
        if q > 0 and m > 0:
            jsd += 0.5 * q * math.log2(q / m)
    return max(0.0, jsd)


def chi_square_2xk(observed_2d):
    """Chi-square test on 2xK contingency table."""
    rows = observed_2d
    n_cols = len(rows[0])
    grand = sum(sum(r) for r in rows)
    if grand == 0:
        return {'chi2': 0, 'df': 0, 'p': 1.0}
    row_sums = [sum(r) for r in rows]
    col_sums = [sum(rows[i][j] for i in range(2)) for j in range(n_cols)]
    chi2 = 0.0
    for i in range(2):
        for j in range(n_cols):
            exp = row_sums[i] * col_sums[j] / grand
            if exp > 0:
                chi2 += (rows[i][j] - exp) ** 2 / exp
    df = n_cols - 1
    if df < 1:
        return {'chi2': chi2, 'df': 0, 'p': 1.0}
    # Approximate p from chi-square using Wilson-Hilferty
    if chi2 == 0:
        p = 1.0
    else:
        z = ((chi2 / df) ** (1.0 / 3) - (1 - 2.0 / (9 * df))) / math.sqrt(2.0 / (9 * df))
        p = 1 - _normal_cdf(z)
    return {'chi2': chi2, 'df': df, 'p': p}


def icc_one_way(groups):
    """ICC(1,1) one-way random effects.
    groups: list of lists, each inner list = observations within a group.
    Returns ICC value."""
    k = len(groups)
    if k < 2:
        return 0.0
    ns = [len(g) for g in groups if len(g) > 0]
    if len(ns) < 2:
        return 0.0
    grand_mean = sum(x for g in groups for x in g) / sum(ns)
    # Between-group MS
    ms_between = sum(len(g) * (sum(g) / len(g) - grand_mean) ** 2
                     for g in groups if len(g) > 0) / (k - 1)
    # Within-group MS
    ss_within = sum((x - sum(g) / len(g)) ** 2
                    for g in groups if len(g) > 0 for x in g)
    df_within = sum(ns) - k
    if df_within <= 0:
        return 0.0
    ms_within = ss_within / df_within
    # Average group size (harmonic mean for unbalanced)
    n0 = (sum(ns) - sum(n ** 2 for n in ns) / sum(ns)) / (k - 1) if k > 1 else 1
    if n0 == 0:
        return 0.0
    icc = (ms_between - ms_within) / (ms_between + (n0 - 1) * ms_within)
    return max(-1.0, min(1.0, icc))


def ols_r_squared(X, y):
    """Simple OLS R-squared. X = list of lists (predictors), y = list."""
    n = len(y)
    p = len(X[0]) if X else 0
    if n <= p + 1 or p == 0:
        return 0.0
    # Add intercept
    Xa = [[1.0] + list(row) for row in X]
    p1 = p + 1
    # Normal equations: (X'X)b = X'y
    XtX = [[sum(Xa[i][j] * Xa[i][k] for i in range(n)) for k in range(p1)] for j in range(p1)]
    Xty = [sum(Xa[i][j] * y[i] for i in range(n)) for j in range(p1)]
    # Solve via Gaussian elimination
    aug = [XtX[j][:] + [Xty[j]] for j in range(p1)]
    for col in range(p1):
        # Pivot
        max_row = max(range(col, p1), key=lambda r: abs(aug[r][col]))
        aug[col], aug[max_row] = aug[max_row], aug[col]
        if abs(aug[col][col]) < 1e-12:
            return 0.0
        for row in range(p1):
            if row != col:
                factor = aug[row][col] / aug[col][col]
                for c in range(p1 + 1):
                    aug[row][c] -= factor * aug[col][c]
    beta = [aug[j][p1] / aug[j][j] for j in range(p1)]
    # R-squared
    y_mean = sum(y) / n
    ss_tot = sum((yi - y_mean) ** 2 for yi in y)
    if ss_tot == 0:
        return 0.0
    y_pred = [sum(beta[j] * Xa[i][j] for j in range(p1)) for i in range(n)]
    ss_res = sum((y[i] - y_pred[i]) ** 2 for i in range(n))
    r2 = 1 - ss_res / ss_tot
    return max(0.0, r2)


def loo_r_squared(X, y):
    """Leave-one-out cross-validated R-squared."""
    n = len(y)
    if n < 5:
        return 0.0
    y_mean = sum(y) / n
    ss_tot = sum((yi - y_mean) ** 2 for yi in y)
    if ss_tot == 0:
        return 0.0
    ss_loo = 0.0
    for i in range(n):
        X_train = X[:i] + X[i + 1:]
        y_train = y[:i] + y[i + 1:]
        # Fit on n-1
        nt = len(y_train)
        p = len(X_train[0]) if X_train else 0
        if nt <= p + 1:
            ss_loo += (y[i] - y_mean) ** 2
            continue
        Xa = [[1.0] + list(row) for row in X_train]
        p1 = p + 1
        XtX = [[sum(Xa[k][j1] * Xa[k][j2] for k in range(nt)) for j2 in range(p1)] for j1 in range(p1)]
        Xty = [sum(Xa[k][j] * y_train[k] for k in range(nt)) for j in range(p1)]
        aug = [XtX[j][:] + [Xty[j]] for j in range(p1)]
        singular = False
        for col in range(p1):
            max_row = max(range(col, p1), key=lambda r: abs(aug[r][col]))
            aug[col], aug[max_row] = aug[max_row], aug[col]
            if abs(aug[col][col]) < 1e-12:
                singular = True
                break
            for row in range(p1):
                if row != col:
                    factor = aug[row][col] / aug[col][col]
                    for c in range(p1 + 1):
                        aug[row][c] -= factor * aug[col][c]
        if singular:
            ss_loo += (y[i] - y_mean) ** 2
            continue
        beta = [aug[j][p1] / aug[j][j] for j in range(p1)]
        xi = [1.0] + list(X[i])
        y_pred = sum(beta[j] * xi[j] for j in range(p1))
        ss_loo += (y[i] - y_pred) ** 2
    return 1 - ss_loo / ss_tot


def section_to_numeric(section_list):
    """Encode sections as dummy variables for regression."""
    unique = sorted(set(section_list))
    # Drop first as reference
    if len(unique) <= 1:
        return [[0.0] for _ in section_list]
    return [[1.0 if s == u else 0.0 for u in unique[1:]] for s in section_list]


# ============================================================
# DATA LOADING
# ============================================================

def load_data():
    """Build event table from single B-pass + load all required phase data."""
    print("Loading data...")

    # 1. Token-to-class mapping
    ctm_path = ROOT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
    with open(ctm_path, 'r', encoding='utf-8') as f:
        ctm = json.load(f)
    token_to_class = {t: int(c) for t, c in ctm['token_to_class'].items()}
    print(f"  Token-to-class: {len(token_to_class)} entries")

    # 2. Per-folio dynamical data from AXM residual decomposition
    axm_path = ROOT / 'phases' / 'AXM_RESIDUAL_DECOMPOSITION' / 'results' / 'axm_residual_decomposition.json'
    with open(axm_path, 'r', encoding='utf-8') as f:
        axm_data = json.load(f)
    folio_dynamics = axm_data.get('folio_data', {})
    print(f"  Folio dynamics: {len(folio_dynamics)} folios")

    # 3. REGIME mapping
    regime_path = ROOT / 'phases' / 'REGIME_SEMANTIC_INTERPRETATION' / 'results' / 'regime_folio_mapping.json'
    with open(regime_path, 'r', encoding='utf-8') as f:
        regime_data = json.load(f)
    folio_regime = {}
    for regime, folios in regime_data.items():
        for folio in folios:
            folio_regime[folio] = regime

    # 4. Bridge and dark MIDDLE sets
    bridge_path = ROOT / 'phases' / 'BRIDGE_MIDDLE_SELECTION_MECHANISM' / 'results' / 'bridge_selection.json'
    with open(bridge_path, 'r', encoding='utf-8') as f:
        bridge_data = json.load(f)
    bridge_middles = set(bridge_data['t5_structural_profile']['bridge_middles'])

    dark_path = ROOT / 'data' / 'dark_pipeline_middles.json'
    with open(dark_path, 'r', encoding='utf-8') as f:
        dark_data = json.load(f)
    dark_middles = set(dark_data['middles'] if isinstance(dark_data, dict) else dark_data)
    print(f"  Bridge MIDDLEs: {len(bridge_middles)}, Dark MIDDLEs: {len(dark_middles)}")

    # 5. Single B-pass: build event table
    tx = Transcript()
    morph = Morphology()

    # Collect tokens grouped by (folio, line) for position computation
    folio_line_tokens = defaultdict(list)
    for token in tx.currier_b():
        w = token.word
        if not w.strip() or '*' in w:
            continue
        folio_line_tokens[(token.folio, token.line)].append(token)

    # Build event table with position and class info
    events = []
    # Track prev_class per (folio, line) for successor analysis
    for (folio, line), tokens in folio_line_tokens.items():
        n_tok = len(tokens)
        prev_cls = None
        for idx, token in enumerate(tokens):
            w = token.word
            m = morph.extract(w)
            prefix = m.prefix if m else None
            middle = m.middle if m else None
            suffix = m.suffix if m else None

            # Sister type
            sister_type = 'other'
            if prefix in ('ch', 'sh', 'ok', 'ot'):
                sister_type = prefix
            elif prefix and prefix.endswith('ch'):
                sister_type = 'ch'  # Extended ch prefix (pch, tch, etc.)
            elif prefix and prefix.endswith('sh'):
                sister_type = 'sh'  # Extended sh prefix

            # Instruction class
            inst_class = token_to_class.get(w)

            # Position
            pos_norm = idx / max(n_tok - 1, 1)
            if n_tok <= 5:
                pos_bin = 'Q3'  # Short lines: all middle
            else:
                q = int(pos_norm * 5)
                q = min(q, 4)
                pos_bin = f'Q{q + 1}'

            event = {
                'folio': folio,
                'line': line,
                'pos_in_line': idx,
                'pos_norm': pos_norm,
                'pos_bin': pos_bin,
                'word': w,
                'prefix': prefix,
                'middle': middle,
                'suffix': suffix,
                'sister_type': sister_type,
                'inst_class': inst_class,
                'prev_class': prev_cls,
                'section': token.section,
                'is_opener': token.line_initial,
                'is_closer': token.line_final,
                'is_par_initial': token.par_initial,
            }
            events.append(event)
            prev_cls = inst_class

    print(f"  Event table: {len(events)} tokens")

    # 6. Build per-folio aggregates
    folio_agg = {}
    folio_events = defaultdict(list)
    for ev in events:
        folio_events[ev['folio']].append(ev)

    for folio, evs in folio_events.items():
        ch_n = sum(1 for e in evs if e['sister_type'] == 'ch')
        sh_n = sum(1 for e in evs if e['sister_type'] == 'sh')
        ok_n = sum(1 for e in evs if e['sister_type'] == 'ok')
        ot_n = sum(1 for e in evs if e['sister_type'] == 'ot')
        total_n = len(evs)

        # Sister preferences
        ch_pref = ch_n / (ch_n + sh_n) if (ch_n + sh_n) >= 5 else None
        ok_pref = ok_n / (ok_n + ot_n) if (ok_n + ot_n) >= 5 else None

        # Bridge/dark density
        bridge_n = sum(1 for e in evs if e['middle'] in bridge_middles)
        dark_n = sum(1 for e in evs if e['middle'] in dark_middles)
        bridge_density = bridge_n / total_n if total_n > 0 else 0
        dark_density = dark_n / total_n if total_n > 0 else 0

        # Section (majority vote)
        sec_counts = Counter(e['section'] for e in evs)
        section = sec_counts.most_common(1)[0][0] if sec_counts else ''

        # REGIME
        regime = folio_regime.get(folio, '')

        # Positional stats for ch/sh
        ch_positions = [e['pos_norm'] for e in evs if e['sister_type'] == 'ch']
        sh_positions = [e['pos_norm'] for e in evs if e['sister_type'] == 'sh']
        mean_ch_pos = sum(ch_positions) / len(ch_positions) if ch_positions else None
        mean_sh_pos = sum(sh_positions) / len(sh_positions) if sh_positions else None
        pos_gap = (mean_ch_pos - mean_sh_pos) if (mean_ch_pos is not None and mean_sh_pos is not None) else None

        # Opener ch/sh rates
        opener_ch = sum(1 for e in evs if e['is_opener'] and e['sister_type'] == 'ch')
        opener_sh = sum(1 for e in evs if e['is_opener'] and e['sister_type'] == 'sh')
        closer_ch = sum(1 for e in evs if e['is_closer'] and e['sister_type'] == 'ch')
        closer_sh = sum(1 for e in evs if e['is_closer'] and e['sister_type'] == 'sh')

        # Position bin distributions for ch/sh
        ch_bins = Counter(e['pos_bin'] for e in evs if e['sister_type'] == 'ch')
        sh_bins = Counter(e['pos_bin'] for e in evs if e['sister_type'] == 'sh')

        # Dynamical metrics (from AXM residual data)
        dyn = folio_dynamics.get(folio, {})

        # Entry divergence: compute from event table
        # Entry tokens = line_initial tokens; compute class distribution
        entry_classes = Counter(e['inst_class'] for e in evs if e['is_opener'] and e['inst_class'] is not None)
        interior_classes = Counter(e['inst_class'] for e in evs
                                   if not e['is_opener'] and not e['is_closer']
                                   and e['inst_class'] is not None)
        entry_jsd = jensen_shannon(entry_classes, interior_classes) if entry_classes and interior_classes else 0.0

        # AXM return rate: fraction of entry tokens in AXM macro state
        # AXM classes from C976
        axm_classes = {1, 2, 4, 6, 8, 15, 16, 17, 20, 21, 22, 24, 25, 26, 27, 28, 29,
                       31, 32, 33, 34, 35, 36, 37, 39, 41, 43, 44, 46, 47, 48, 49}
        entry_total = sum(entry_classes.values())
        entry_axm = sum(v for k, v in entry_classes.items() if k in axm_classes)
        axm_return_rate = entry_axm / entry_total if entry_total > 0 else None

        folio_agg[folio] = {
            'ch_n': ch_n, 'sh_n': sh_n, 'ok_n': ok_n, 'ot_n': ot_n,
            'ch_pref': ch_pref, 'ok_pref': ok_pref,
            'total_n': total_n,
            'bridge_density': bridge_density, 'dark_density': dark_density,
            'section': section, 'regime': regime,
            'archetype': dyn.get('archetype'),
            'mean_ch_pos': mean_ch_pos, 'mean_sh_pos': mean_sh_pos, 'pos_gap': pos_gap,
            'opener_ch': opener_ch, 'opener_sh': opener_sh,
            'closer_ch': closer_ch, 'closer_sh': closer_sh,
            'ch_bins': dict(ch_bins), 'sh_bins': dict(sh_bins),
            'entry_jsd': entry_jsd,
            'axm_return_rate': axm_return_rate,
            'axm_self': dyn.get('axm_self'),
            'c1017_residual': dyn.get('c1017_residual'),
            'hazard_density': dyn.get('hazard_density'),
            'qo_fraction': dyn.get('qo_fraction'),
            'bridge_pc1': dyn.get('bridge_pc1'),
        }

    # Filter to folios with valid ch_pref
    valid_folios = [f for f, a in folio_agg.items() if a['ch_pref'] is not None]
    print(f"  Folios with ch_pref: {len(valid_folios)}")

    return {
        'events': events,
        'folio_events': dict(folio_events),
        'folio_agg': folio_agg,
        'valid_folios': valid_folios,
        'token_to_class': token_to_class,
        'bridge_middles': bridge_middles,
        'dark_middles': dark_middles,
        'folio_dynamics': folio_dynamics,
    }


# ============================================================
# TEST 0: SLOT EQUIVALENCE SANITY CHECK
# ============================================================

def test0_slot_equivalence(data):
    """SP-0: For MIDDLE+SUFFIX available under both ch and sh,
    is sister choice random after section control?"""
    print("\n-- Test 0: Slot Equivalence Sanity Check --")

    events = data['events']

    # Collect (middle, suffix, section) -> {ch: count, sh: count}
    slot_counts = defaultdict(lambda: {'ch': 0, 'sh': 0})
    for e in events:
        if e['sister_type'] in ('ch', 'sh') and e['middle']:
            key = (e['middle'], e['suffix'] or '', e['section'])
            slot_counts[key][e['sister_type']] += 1

    # Filter to slots with both ch and sh present, min 5 total
    testable_slots = {}
    for key, counts in slot_counts.items():
        if counts['ch'] > 0 and counts['sh'] > 0 and (counts['ch'] + counts['sh']) >= 5:
            testable_slots[key] = counts

    print(f"  Testable slots (MIDDLE+SUFFIX+section, both sisters, n>=5): {len(testable_slots)}")

    if len(testable_slots) == 0:
        # Relax: don't require section stratification
        for key_full, counts in slot_counts.items():
            mid, suf, sec = key_full
            relaxed_key = (mid, suf)
            # Aggregate across sections
        slot_counts_nosec = defaultdict(lambda: {'ch': 0, 'sh': 0})
        for e in events:
            if e['sister_type'] in ('ch', 'sh') and e['middle']:
                key = (e['middle'], e['suffix'] or '')
                slot_counts_nosec[key][e['sister_type']] += 1
        testable_slots = {}
        for key, counts in slot_counts_nosec.items():
            if counts['ch'] > 0 and counts['sh'] > 0 and (counts['ch'] + counts['sh']) >= 5:
                testable_slots[key] = counts
        print(f"  Relaxed (no section): {len(testable_slots)} testable slots")

    if len(testable_slots) == 0:
        print("  Verdict: INSUFFICIENT_DATA")
        return {'testable_slots': 0, 'verdict': 'INSUFFICIENT_DATA'}

    # For each slot, compute chi-square (or binomial) deviation from 50/50
    # Aggregate: sum of chi-square statistics
    total_chi2 = 0.0
    total_df = 0
    n_significant = 0
    n_tested = 0
    slot_results = []

    for key, counts in testable_slots.items():
        ch = counts['ch']
        sh = counts['sh']
        total = ch + sh
        # Expected under H0 (equal probability): total/2 each
        expected = total / 2.0
        chi2 = (ch - expected) ** 2 / expected + (sh - expected) ** 2 / expected
        total_chi2 += chi2
        total_df += 1
        # Individual p
        z = (chi2) ** 0.5 if chi2 > 0 else 0
        p = 2 * (1 - _normal_cdf(z))
        bonferroni_threshold = 0.05 / len(testable_slots)
        if p < bonferroni_threshold:
            n_significant += 1
        n_tested += 1
        slot_results.append({
            'slot': str(key),
            'ch': ch, 'sh': sh, 'chi2': chi2, 'p': p,
        })

    # Overall: compare total_chi2 to chi-square(df=total_df)
    if total_df > 0:
        z_overall = ((total_chi2 / total_df) ** (1.0 / 3) - (1 - 2.0 / (9 * total_df))) / math.sqrt(
            2.0 / (9 * total_df))
        p_overall = 1 - _normal_cdf(z_overall)
    else:
        p_overall = 1.0

    # Also compute grand ch/sh ratio across all testable slots
    grand_ch = sum(c['ch'] for c in testable_slots.values())
    grand_sh = sum(c['sh'] for c in testable_slots.values())
    grand_ratio = grand_ch / (grand_ch + grand_sh) if (grand_ch + grand_sh) > 0 else 0.5

    print(f"  Testable slots: {n_tested}")
    print(f"  Grand ch/(ch+sh) in testable slots: {grand_ratio:.3f}")
    print(f"  Bonferroni-significant slots: {n_significant}/{n_tested}")
    print(f"  Aggregated chi2: {total_chi2:.1f}, df: {total_df}, p: {p_overall:.4f}")

    if p_overall < 0.05 or n_significant > 0.1 * n_tested:
        verdict = 'STRUCTURED_IN_SLOT'
    else:
        verdict = 'FREE_IN_SLOT'

    print(f"  Verdict: {verdict}")

    return {
        'testable_slots': n_tested,
        'grand_ch_ratio': grand_ratio,
        'n_bonferroni_significant': n_significant,
        'aggregated_chi2': total_chi2,
        'aggregated_df': total_df,
        'aggregated_p': p_overall,
        'top_slots': sorted(slot_results, key=lambda x: x['chi2'], reverse=True)[:10],
        'verdict': verdict,
    }


# ============================================================
# TEST 1: POSITIONAL MEDIATION
# ============================================================

def test1_positional_mediation(data):
    """SP-1: Does within-line position absorb C639 residual?"""
    print("\n-- Test 1: Positional Mediation of Sister Residual --")

    agg = data['folio_agg']
    valid = [f for f in data['valid_folios'] if agg[f]['section']]

    # Baseline: section-only R-squared (replicate C639 step 1)
    sections = [agg[f]['section'] for f in valid]
    ch_prefs = [agg[f]['ch_pref'] for f in valid]

    X_sec = section_to_numeric(sections)
    r2_baseline = ols_r_squared(X_sec, ch_prefs)
    loo_baseline = loo_r_squared(X_sec, ch_prefs)

    # Extended: section + positional variables
    # Positional vars: mean_ch_pos, mean_sh_pos, pos_gap, opener_ch_frac, closer_ch_frac
    X_ext = []
    valid_ext = []
    ch_prefs_ext = []
    for i, f in enumerate(valid):
        a = agg[f]
        if a['pos_gap'] is None:
            continue
        # Position features
        opener_total = a['opener_ch'] + a['opener_sh']
        opener_ch_frac = a['opener_ch'] / opener_total if opener_total > 0 else 0.5
        closer_total = a['closer_ch'] + a['closer_sh']
        closer_ch_frac = a['closer_ch'] / closer_total if closer_total > 0 else 0.5

        # Position bin divergence (ch vs sh bin distributions)
        all_bins = ['Q1', 'Q2', 'Q3', 'Q4', 'Q5']
        ch_bin_frac = []
        sh_bin_frac = []
        ch_total = sum(a['ch_bins'].get(b, 0) for b in all_bins)
        sh_total = sum(a['sh_bins'].get(b, 0) for b in all_bins)
        for b in all_bins:
            ch_bin_frac.append(a['ch_bins'].get(b, 0) / max(ch_total, 1))
            sh_bin_frac.append(a['sh_bins'].get(b, 0) / max(sh_total, 1))
        # Use early-bin ch excess (Q1+Q2 ch fraction - Q4+Q5 ch fraction) as position feature
        ch_early = ch_bin_frac[0] + ch_bin_frac[1]
        ch_late = ch_bin_frac[3] + ch_bin_frac[4]
        pos_asymmetry = ch_early - ch_late

        sec_dummies = X_sec[i]
        row = list(sec_dummies) + [a['pos_gap'], opener_ch_frac, pos_asymmetry]
        X_ext.append(row)
        valid_ext.append(f)
        ch_prefs_ext.append(a['ch_pref'])

    if len(valid_ext) < 20:
        print(f"  Too few folios with position data: {len(valid_ext)}")
        return {'verdict': 'INSUFFICIENT_DATA', 'n_folios': len(valid_ext)}

    # Recompute baseline on same subset
    sections_ext = [agg[f]['section'] for f in valid_ext]
    X_sec_ext = section_to_numeric(sections_ext)
    r2_sec_only = ols_r_squared(X_sec_ext, ch_prefs_ext)
    loo_sec_only = loo_r_squared(X_sec_ext, ch_prefs_ext)

    r2_extended = ols_r_squared(X_ext, ch_prefs_ext)
    loo_extended = loo_r_squared(X_ext, ch_prefs_ext)

    delta_r2 = r2_extended - r2_sec_only
    delta_loo = loo_extended - loo_sec_only

    # Also compute global ch/sh positional stats
    all_ch_pos = [e['pos_norm'] for e in data['events'] if e['sister_type'] == 'ch']
    all_sh_pos = [e['pos_norm'] for e in data['events'] if e['sister_type'] == 'sh']
    mean_ch = sum(all_ch_pos) / len(all_ch_pos) if all_ch_pos else 0
    mean_sh = sum(all_sh_pos) / len(all_sh_pos) if all_sh_pos else 0

    print(f"  Folios: {len(valid_ext)}")
    print(f"  Global ch mean pos: {mean_ch:.3f}, sh mean pos: {mean_sh:.3f}, gap: {mean_ch - mean_sh:.3f}")
    print(f"  Section-only R2: {r2_sec_only:.4f} (LOO: {loo_sec_only:.4f})")
    print(f"  Section+position R2: {r2_extended:.4f} (LOO: {loo_extended:.4f})")
    print(f"  Delta-R2: {delta_r2:.4f}, Delta-LOO: {delta_loo:.4f}")

    if delta_r2 > 0.10 and r2_sec_only - r2_baseline > 0.02:
        verdict = 'POSITIONAL_CONFOUND'
    elif delta_r2 > 0.05 and delta_loo > 0:
        verdict = 'POSITIONAL_MEDIATION'
    elif delta_r2 < 0.02:
        verdict = 'POSITIONAL_INDEPENDENT'
    else:
        verdict = 'POSITIONAL_WEAK'

    print(f"  Verdict: {verdict}")

    return {
        'n_folios': len(valid_ext),
        'global_ch_mean_pos': mean_ch,
        'global_sh_mean_pos': mean_sh,
        'global_pos_gap': mean_ch - mean_sh,
        'r2_section_only': r2_sec_only,
        'loo_section_only': loo_sec_only,
        'r2_section_plus_position': r2_extended,
        'loo_section_plus_position': loo_extended,
        'delta_r2': delta_r2,
        'delta_loo': delta_loo,
        'verdict': verdict,
    }


# ============================================================
# TEST 2: DYNAMICAL CONSEQUENCE
# ============================================================

def test2_dynamical_consequence(data):
    """SP-2: Do folios with extreme sister preference differ in dynamics?"""
    print("\n-- Test 2: Dynamical Consequence of Sister Residual --")

    agg = data['folio_agg']
    valid = data['valid_folios']

    metrics = ['axm_self', 'hazard_density', 'qo_fraction', 'c1017_residual', 'bridge_pc1']
    results = {}

    for metric in metrics:
        # Get folios with both ch_pref and metric
        pairs = [(agg[f]['ch_pref'], agg[f][metric], agg[f]['section'])
                 for f in valid
                 if agg[f][metric] is not None and agg[f]['section']]
        if len(pairs) < 10:
            results[metric] = {'n': len(pairs), 'rho': None, 'p': None, 'note': 'too few'}
            continue

        ch_vals = [p[0] for p in pairs]
        met_vals = [p[1] for p in pairs]
        sec_vals = [p[2] for p in pairs]

        # Raw Spearman
        rho_raw, p_raw = spearman_r(ch_vals, met_vals)

        # Partial Spearman controlling for section (encode as numeric)
        unique_secs = sorted(set(sec_vals))
        sec_numeric = [unique_secs.index(s) for s in sec_vals]
        rho_partial, p_partial = partial_spearman(ch_vals, met_vals, sec_numeric)

        # Within-section correlations
        within = {}
        for sec in unique_secs:
            idx = [i for i in range(len(pairs)) if pairs[i][2] == sec]
            if len(idx) >= 5:
                ch_s = [ch_vals[i] for i in idx]
                met_s = [met_vals[i] for i in idx]
                r, p = spearman_r(ch_s, met_s)
                within[sec] = {'n': len(idx), 'rho': r, 'p': p}

        results[metric] = {
            'n': len(pairs),
            'rho_raw': rho_raw, 'p_raw': p_raw,
            'rho_partial': rho_partial, 'p_partial': p_partial,
            'within_section': within,
        }
        print(f"  {metric}: raw rho={rho_raw:.3f} (p={p_raw:.4f}), partial rho={rho_partial:.3f} (p={p_partial:.4f})")

    # Check if c1017_residual correlation is substantial
    c1017_r = results.get('c1017_residual', {})
    c1017_partial = abs(c1017_r.get('rho_partial', 0) or 0)

    # Verdict
    max_partial = max(abs(r.get('rho_partial', 0) or 0) for r in results.values())
    any_consequential = max_partial > 0.25
    residual_extension = c1017_partial > 0.20  # More lenient for residual

    if residual_extension:
        verdict = 'RESIDUAL_EXTENSION'
    elif any_consequential:
        verdict = 'DYNAMICALLY_CONSEQUENTIAL'
    elif max_partial < 0.15:
        verdict = 'DYNAMICALLY_NEUTRAL'
    else:
        verdict = 'DYNAMICALLY_WEAK'

    print(f"  Max |partial rho|: {max_partial:.3f}")
    print(f"  Verdict: {verdict}")

    return {
        'metrics': results,
        'max_abs_partial_rho': max_partial,
        'c1017_residual_partial': c1017_partial,
        'verdict': verdict,
    }


# ============================================================
# TEST 3: CONCENTRATION (ICC)
# ============================================================

def test3_concentration_icc(data):
    """SP-3: Is the 52.9% residual uniform or concentrated?"""
    print("\n-- Test 3: Concentration vs Uniformity (ICC) --")

    events = data['events']

    # Build per-paragraph sister counts
    # Group events by (folio, paragraph)
    # Paragraph boundary: par_initial marks start of new paragraph
    para_data = defaultdict(lambda: {'ch': 0, 'sh': 0})
    current_folio = None
    current_para = 0

    # Group by folio, then track paragraph transitions
    folio_events = data['folio_events']
    para_sister = defaultdict(lambda: {'ch': 0, 'sh': 0})

    for folio, evs in folio_events.items():
        para_idx = 0
        for e in evs:
            if e['is_par_initial']:
                para_idx += 1
            if e['sister_type'] in ('ch', 'sh'):
                para_sister[(folio, para_idx)][e['sister_type']] += 1

    # Filter to paragraphs with >= 5 ch+sh tokens
    testable = {}
    for key, counts in para_sister.items():
        total = counts['ch'] + counts['sh']
        if total >= 5:
            testable[key] = counts['ch'] / total

    print(f"  Paragraphs with >= 5 sister tokens: {len(testable)}")

    # Group by folio
    folio_paras = defaultdict(list)
    for (folio, para_idx), ratio in testable.items():
        folio_paras[folio].append(ratio)

    # Filter to folios with >= 2 testable paragraphs
    multi_para_folios = {f: paras for f, paras in folio_paras.items() if len(paras) >= 2}
    print(f"  Folios with >= 2 testable paragraphs: {len(multi_para_folios)}")

    if len(multi_para_folios) < 5:
        print("  Verdict: INSUFFICIENT_DATA")
        return {'testable_paragraphs': len(testable),
                'multi_para_folios': len(multi_para_folios),
                'verdict': 'INSUFFICIENT_DATA'}

    # Compute ICC(1,1)
    groups = list(multi_para_folios.values())
    icc_val = icc_one_way(groups)

    # Also check bimodality of per-folio ratios
    agg = data['folio_agg']
    folio_ch_prefs = [agg[f]['ch_pref'] for f in data['valid_folios']]
    # Simple bimodality check: is the distribution more spread near 0 and 1 than near 0.5?
    n_extreme = sum(1 for x in folio_ch_prefs if x > 0.8 or x < 0.2)
    n_middle = sum(1 for x in folio_ch_prefs if 0.35 <= x <= 0.65)
    n_total = len(folio_ch_prefs)
    extreme_frac = n_extreme / n_total if n_total > 0 else 0
    middle_frac = n_middle / n_total if n_total > 0 else 0

    # Quartile analysis
    sorted_prefs = sorted(folio_ch_prefs)
    q25 = sorted_prefs[len(sorted_prefs) // 4] if sorted_prefs else 0
    q50 = sorted_prefs[len(sorted_prefs) // 2] if sorted_prefs else 0
    q75 = sorted_prefs[3 * len(sorted_prefs) // 4] if sorted_prefs else 0

    # Near-deterministic folios
    n_deterministic = sum(1 for x in folio_ch_prefs if x > 0.9 or x < 0.1)

    print(f"  ICC(1,1): {icc_val:.3f}")
    print(f"  Folio ch_pref: Q25={q25:.3f}, median={q50:.3f}, Q75={q75:.3f}")
    print(f"  Extreme (>0.8 or <0.2): {n_extreme}/{n_total} ({extreme_frac:.1%})")
    print(f"  Near-deterministic (>0.9 or <0.1): {n_deterministic}/{n_total}")

    if icc_val > 0.5:
        verdict = 'FOLIO_DETERMINED'
    elif icc_val < 0.2:
        verdict = 'PARAGRAPH_VARIABLE'
    elif extreme_frac > 0.3 and middle_frac < 0.3:
        verdict = 'BIMODAL'
    else:
        verdict = 'MODERATE_CONSISTENCY'

    print(f"  Verdict: {verdict}")

    return {
        'testable_paragraphs': len(testable),
        'multi_para_folios': len(multi_para_folios),
        'icc': icc_val,
        'folio_distribution': {
            'q25': q25, 'median': q50, 'q75': q75,
            'extreme_frac': extreme_frac,
            'middle_frac': middle_frac,
            'n_deterministic': n_deterministic,
        },
        'verdict': verdict,
    }


# ============================================================
# TEST 4: BRIDGE/DARK PIPELINE COUPLING
# ============================================================

def test4_bridge_dark_coupling(data):
    """SP-4: Does sister preference track bridge-dark balance?"""
    print("\n-- Test 4: Bridge/Dark Pipeline Coupling --")

    agg = data['folio_agg']
    valid = data['valid_folios']

    # Get folios with valid data
    triples = [(agg[f]['ch_pref'], agg[f]['bridge_density'], agg[f]['dark_density'],
                agg[f]['section'])
               for f in valid if agg[f]['section']]

    if len(triples) < 10:
        return {'verdict': 'INSUFFICIENT_DATA', 'n': len(triples)}

    ch_vals = [t[0] for t in triples]
    bridge_vals = [t[1] for t in triples]
    dark_vals = [t[2] for t in triples]
    sec_vals = [t[3] for t in triples]
    unique_secs = sorted(set(sec_vals))
    sec_numeric = [unique_secs.index(s) for s in sec_vals]

    # Raw correlations
    rho_bridge_raw, p_bridge_raw = spearman_r(ch_vals, bridge_vals)
    rho_dark_raw, p_dark_raw = spearman_r(ch_vals, dark_vals)

    # Partial (controlling section)
    rho_bridge_partial, p_bridge_partial = partial_spearman(ch_vals, bridge_vals, sec_numeric)
    rho_dark_partial, p_dark_partial = partial_spearman(ch_vals, dark_vals, sec_numeric)

    # Bridge-dark ratio
    bd_ratio = [b / (b + d + 1e-10) for b, d in zip(bridge_vals, dark_vals)]
    rho_ratio_raw, p_ratio_raw = spearman_r(ch_vals, bd_ratio)
    rho_ratio_partial, p_ratio_partial = partial_spearman(ch_vals, bd_ratio, sec_numeric)

    print(f"  n={len(triples)}")
    print(f"  ch_pref vs bridge: raw rho={rho_bridge_raw:.3f}, partial={rho_bridge_partial:.3f}")
    print(f"  ch_pref vs dark:   raw rho={rho_dark_raw:.3f}, partial={rho_dark_partial:.3f}")
    print(f"  ch_pref vs bridge/(bridge+dark): raw rho={rho_ratio_raw:.3f}, partial={rho_ratio_partial:.3f}")

    max_partial = max(abs(rho_bridge_partial), abs(rho_dark_partial), abs(rho_ratio_partial))
    max_raw = max(abs(rho_bridge_raw), abs(rho_dark_raw), abs(rho_ratio_raw))

    if max_partial > 0.25:
        verdict = 'BRIDGE_COUPLED'
    elif max_partial < 0.10:
        verdict = 'BRIDGE_INDEPENDENT'
    elif max_raw > 0.25 and max_partial < 0.15:
        verdict = 'SECTION_CONFOUNDED'
    else:
        verdict = 'BRIDGE_WEAK'

    print(f"  Verdict: {verdict}")

    return {
        'n': len(triples),
        'bridge_raw': {'rho': rho_bridge_raw, 'p': p_bridge_raw},
        'bridge_partial': {'rho': rho_bridge_partial, 'p': p_bridge_partial},
        'dark_raw': {'rho': rho_dark_raw, 'p': p_dark_raw},
        'dark_partial': {'rho': rho_dark_partial, 'p': p_dark_partial},
        'bd_ratio_raw': {'rho': rho_ratio_raw, 'p': p_ratio_raw},
        'bd_ratio_partial': {'rho': rho_ratio_partial, 'p': p_ratio_partial},
        'verdict': verdict,
    }


# ============================================================
# TEST 5: ok/ot PARALLEL TEST
# ============================================================

def test5_ok_ot_parallel(data):
    """SP-5: Does ok/ot show the same pattern as ch/sh?"""
    print("\n-- Test 5: ok/ot Parallel Test --")

    agg = data['folio_agg']

    # Folios with both ch_pref and ok_pref
    both_valid = [f for f in data['valid_folios']
                  if agg[f]['ok_pref'] is not None and agg[f]['section']]
    print(f"  Folios with both ch_pref and ok_pref: {len(both_valid)}")

    if len(both_valid) < 10:
        return {'verdict': 'INSUFFICIENT_DATA', 'n': len(both_valid)}

    ch_prefs = [agg[f]['ch_pref'] for f in both_valid]
    ok_prefs = [agg[f]['ok_pref'] for f in both_valid]
    sections = [agg[f]['section'] for f in both_valid]
    unique_secs = sorted(set(sections))
    sec_numeric = [unique_secs.index(s) for s in sections]

    # Raw correlation
    rho_raw, p_raw = spearman_r(ch_prefs, ok_prefs)

    # Partial (controlling section)
    rho_partial, p_partial = partial_spearman(ch_prefs, ok_prefs, sec_numeric)

    # ok_pref variance decomposition (section-only)
    X_sec = section_to_numeric(sections)
    r2_ok_sec = ols_r_squared(X_sec, ok_prefs)

    # ch_pref variance decomposition (section-only) on same subset
    r2_ch_sec = ols_r_squared(X_sec, ch_prefs)

    # ok/ot positional asymmetry
    all_ok_pos = [e['pos_norm'] for e in data['events'] if e['sister_type'] == 'ok']
    all_ot_pos = [e['pos_norm'] for e in data['events'] if e['sister_type'] == 'ot']
    mean_ok = sum(all_ok_pos) / len(all_ok_pos) if all_ok_pos else 0
    mean_ot = sum(all_ot_pos) / len(all_ot_pos) if all_ot_pos else 0
    ok_ot_gap = mean_ok - mean_ot

    # Global ok_pref stats
    ok_mean = sum(ok_prefs) / len(ok_prefs)
    ok_std = math.sqrt(sum((x - ok_mean) ** 2 for x in ok_prefs) / (len(ok_prefs) - 1))
    ch_mean = sum(ch_prefs) / len(ch_prefs)

    print(f"  ch_pref mean: {ch_mean:.3f}, ok_pref mean: {ok_mean:.3f} (std: {ok_std:.3f})")
    print(f"  ok/ot pos gap: {ok_ot_gap:.3f} (ok={mean_ok:.3f}, ot={mean_ot:.3f})")
    print(f"  R2 (section->ch_pref): {r2_ch_sec:.4f}")
    print(f"  R2 (section->ok_pref): {r2_ok_sec:.4f}")
    print(f"  ch_pref vs ok_pref: raw rho={rho_raw:.3f}, partial={rho_partial:.3f} (p={p_partial:.4f})")

    if rho_partial > 0.4:
        verdict = 'PARALLEL_MECHANISM'
    elif abs(rho_partial) < 0.15:
        verdict = 'INDEPENDENT_AXES'
    elif r2_ok_sec > 0.7:
        verdict = 'OK_OT_DETERMINISTIC'
    else:
        verdict = 'WEAK_COUPLING'

    print(f"  Verdict: {verdict}")

    return {
        'n': len(both_valid),
        'ch_pref_mean': ch_mean,
        'ok_pref_mean': ok_mean,
        'ok_pref_std': ok_std,
        'ok_ot_pos_gap': ok_ot_gap,
        'mean_ok_pos': mean_ok,
        'mean_ot_pos': mean_ot,
        'r2_section_ch': r2_ch_sec,
        'r2_section_ok': r2_ok_sec,
        'rho_raw': rho_raw,
        'p_raw': p_raw,
        'rho_partial': rho_partial,
        'p_partial': p_partial,
        'verdict': verdict,
    }


# ============================================================
# TEST 6: SUCCESSOR PROFILE DECOMPOSITION
# ============================================================

def test6_successor_decomposition(data):
    """SP-6: Do ch and sh drive different successor distributions
    at matched position + section + preceding role?

    Any positive result = within-class routing (C506.b, C1026),
    NOT grammar reopening."""
    print("\n-- Test 6: Successor Profile Decomposition --")

    events = data['events']

    # Build (middle, pos_bin, section) -> {ch: Counter(next_class), sh: Counter(next_class)}
    strata = defaultdict(lambda: {'ch': Counter(), 'sh': Counter()})

    for i, e in enumerate(events):
        if e['sister_type'] not in ('ch', 'sh'):
            continue
        if e['middle'] is None:
            continue
        # Need next token's class
        if i + 1 >= len(events):
            continue
        next_e = events[i + 1]
        # Must be same folio+line (don't cross line boundary)
        if next_e['folio'] != e['folio'] or next_e['line'] != e['line']:
            continue
        next_cls = next_e['inst_class']
        if next_cls is None:
            continue

        key = (e['middle'], e['pos_bin'], e['section'])
        strata[key][e['sister_type']][next_cls] += 1

    # Filter to strata with both ch and sh, min 3 tokens each
    testable_strata = {}
    for key, counts in strata.items():
        ch_total = sum(counts['ch'].values())
        sh_total = sum(counts['sh'].values())
        if ch_total >= 3 and sh_total >= 3:
            testable_strata[key] = counts

    print(f"  Testable strata (MIDDLE+pos+sec, both sisters, n>=3 each): {len(testable_strata)}")

    if len(testable_strata) == 0:
        # Relax: just MIDDLE + section
        strata_ms = defaultdict(lambda: {'ch': Counter(), 'sh': Counter()})
        for key, counts in strata.items():
            mid, pos, sec = key
            ms_key = (mid, sec)
            strata_ms[ms_key]['ch'] += counts['ch']
            strata_ms[ms_key]['sh'] += counts['sh']
        testable_strata = {}
        for key, counts in strata_ms.items():
            ch_total = sum(counts['ch'].values())
            sh_total = sum(counts['sh'].values())
            if ch_total >= 3 and sh_total >= 3:
                testable_strata[key] = counts
        print(f"  Relaxed (MIDDLE+section only): {len(testable_strata)} strata")

    if len(testable_strata) == 0:
        print("  Verdict: INSUFFICIENT_DATA")
        return {'testable_strata': 0, 'verdict': 'INSUFFICIENT_DATA'}

    # For each stratum, compute JSD(ch_successors, sh_successors)
    observed_jsds = []
    stratum_results = []
    for key, counts in testable_strata.items():
        jsd = jensen_shannon(counts['ch'], counts['sh'])
        ch_n = sum(counts['ch'].values())
        sh_n = sum(counts['sh'].values())
        observed_jsds.append(jsd)
        stratum_results.append({
            'stratum': str(key),
            'ch_n': ch_n, 'sh_n': sh_n,
            'jsd': jsd,
        })

    # Null distribution: random splits (permutation test)
    n_perms = 500
    random.seed(42)
    null_jsds = []
    for _ in range(n_perms):
        perm_jsds = []
        for key, counts in testable_strata.items():
            # Pool ch and sh tokens
            pooled = Counter()
            pooled += counts['ch']
            pooled += counts['sh']
            total = sum(pooled.values())
            ch_n = sum(counts['ch'].values())
            # Randomly assign ch_n tokens to "ch" group
            tokens = []
            for cls, cnt in pooled.items():
                tokens.extend([cls] * cnt)
            random.shuffle(tokens)
            fake_ch = Counter(tokens[:ch_n])
            fake_sh = Counter(tokens[ch_n:])
            perm_jsds.append(jensen_shannon(fake_ch, fake_sh))
        null_jsds.append(sum(perm_jsds) / len(perm_jsds) if perm_jsds else 0)

    observed_mean_jsd = sum(observed_jsds) / len(observed_jsds) if observed_jsds else 0
    null_mean = sum(null_jsds) / len(null_jsds) if null_jsds else 0
    null_95 = sorted(null_jsds)[int(0.95 * len(null_jsds))] if null_jsds else 0
    null_99 = sorted(null_jsds)[int(0.99 * len(null_jsds))] if null_jsds else 0

    # P-value: fraction of null >= observed
    p_value = sum(1 for n in null_jsds if n >= observed_mean_jsd) / len(null_jsds) if null_jsds else 1.0

    # Per-stratum significance (how many strata exceed their own null 95th?)
    per_stratum_sig = 0
    for key, counts in testable_strata.items():
        obs_jsd = jensen_shannon(counts['ch'], counts['sh'])
        stratum_null = []
        pooled = Counter()
        pooled += counts['ch']
        pooled += counts['sh']
        total = sum(pooled.values())
        ch_n = sum(counts['ch'].values())
        tokens = []
        for cls, cnt in pooled.items():
            tokens.extend([cls] * cnt)
        for _ in range(200):
            random.shuffle(tokens)
            fake_ch = Counter(tokens[:ch_n])
            fake_sh = Counter(tokens[ch_n:])
            stratum_null.append(jensen_shannon(fake_ch, fake_sh))
        stratum_95 = sorted(stratum_null)[int(0.95 * len(stratum_null))]
        if obs_jsd > stratum_95:
            per_stratum_sig += 1

    # Bonferroni threshold
    bonf_threshold = 0.05 / len(testable_strata) if testable_strata else 0.05

    print(f"  Observed mean JSD: {observed_mean_jsd:.4f}")
    print(f"  Null mean: {null_mean:.4f}, 95th: {null_95:.4f}, 99th: {null_99:.4f}")
    print(f"  Global p-value: {p_value:.4f}")
    print(f"  Per-stratum significant (p<0.05): {per_stratum_sig}/{len(testable_strata)}")

    if observed_mean_jsd > null_95 and p_value < 0.05:
        if per_stratum_sig > 0.3 * len(testable_strata):
            verdict = 'SISTER_SPECIFIC_DYNAMICS'
        else:
            verdict = 'MIDDLE_DEPENDENT'
    elif observed_mean_jsd < null_mean * 1.1:
        verdict = 'POSITIONALLY_EXPLAINED'
    else:
        verdict = 'AMBIGUOUS'

    print(f"  Verdict: {verdict}")

    return {
        'testable_strata': len(testable_strata),
        'observed_mean_jsd': observed_mean_jsd,
        'null_mean_jsd': null_mean,
        'null_95th': null_95,
        'null_99th': null_99,
        'p_value': p_value,
        'per_stratum_significant': per_stratum_sig,
        'top_strata': sorted(stratum_results, key=lambda x: x['jsd'], reverse=True)[:10],
        'verdict': verdict,
    }


# ============================================================
# TEST 7: BOUNDARY-DIVERGENCE INTERACTION
# ============================================================

def test7_boundary_divergence(data):
    """SP-7: Does sister preference correlate with entry divergence,
    AXM return rate, or opener routing?"""
    print("\n-- Test 7: Boundary-Divergence Interaction --")

    agg = data['folio_agg']
    valid = data['valid_folios']

    metrics = {
        'entry_jsd': 'Entry divergence (JSD entry vs interior)',
        'axm_return_rate': 'AXM return rate at entry',
    }

    results = {}
    for metric, desc in metrics.items():
        pairs = [(agg[f]['ch_pref'], agg[f][metric], agg[f]['section'])
                 for f in valid
                 if agg[f][metric] is not None and agg[f]['section']]
        if len(pairs) < 10:
            results[metric] = {'n': len(pairs), 'verdict': 'too few'}
            continue

        ch_vals = [p[0] for p in pairs]
        met_vals = [p[1] for p in pairs]
        sec_vals = [p[2] for p in pairs]
        unique_secs = sorted(set(sec_vals))
        sec_numeric = [unique_secs.index(s) for s in sec_vals]

        rho_raw, p_raw = spearman_r(ch_vals, met_vals)
        rho_partial, p_partial = partial_spearman(ch_vals, met_vals, sec_numeric)

        results[metric] = {
            'n': len(pairs),
            'description': desc,
            'rho_raw': rho_raw, 'p_raw': p_raw,
            'rho_partial': rho_partial, 'p_partial': p_partial,
        }
        print(f"  {metric}: raw rho={rho_raw:.3f}, partial={rho_partial:.3f} (p={p_partial:.4f})")

    # Also test: opener sister preference vs folio sister preference
    # (Is opener position driving the whole-folio ratio?)
    opener_pairs = []
    for f in valid:
        a = agg[f]
        opener_total = a['opener_ch'] + a['opener_sh']
        if opener_total >= 3 and a['section']:
            opener_ch_frac = a['opener_ch'] / opener_total
            opener_pairs.append((a['ch_pref'], opener_ch_frac, a['section']))

    if len(opener_pairs) >= 10:
        ch_vals = [p[0] for p in opener_pairs]
        op_vals = [p[1] for p in opener_pairs]
        sec_vals = [p[2] for p in opener_pairs]
        unique_secs = sorted(set(sec_vals))
        sec_numeric = [unique_secs.index(s) for s in sec_vals]
        rho_opener, p_opener = spearman_r(ch_vals, op_vals)
        rho_opener_partial, p_opener_partial = partial_spearman(ch_vals, op_vals, sec_numeric)
        results['opener_ch_frac'] = {
            'n': len(opener_pairs),
            'description': 'Opener ch fraction vs folio ch_pref',
            'rho_raw': rho_opener, 'p_raw': p_opener,
            'rho_partial': rho_opener_partial, 'p_partial': p_opener_partial,
        }
        print(f"  opener_ch_frac: raw rho={rho_opener:.3f}, partial={rho_opener_partial:.3f}")

    max_partial = max(abs(r.get('rho_partial', 0) or 0) for r in results.values()
                      if isinstance(r.get('rho_partial'), (int, float)))

    if max_partial > 0.25:
        verdict = 'BOUNDARY_COUPLED'
    elif max_partial < 0.15:
        verdict = 'BOUNDARY_INDEPENDENT'
    else:
        verdict = 'BOUNDARY_WEAK'

    print(f"  Verdict: {verdict}")

    return {
        'metrics': results,
        'max_abs_partial_rho': max_partial,
        'verdict': verdict,
    }


# ============================================================
# SYNTHESIS
# ============================================================

def synthesize(t0, t1, t2, t3, t4, t5, t6, t7):
    """Combine all verdicts into overall characterization."""
    print("\n" + "=" * 60)
    print("SYNTHESIS")
    print("=" * 60)

    verdicts = {
        'sp0': t0['verdict'],
        'sp1': t1['verdict'],
        'sp2': t2['verdict'],
        'sp3': t3['verdict'],
        'sp4': t4['verdict'],
        'sp5': t5['verdict'],
        'sp6': t6['verdict'],
        'sp7': t7['verdict'],
    }

    for k, v in verdicts.items():
        print(f"  {k}: {v}")

    # Determine overall
    v = verdicts

    if (v['sp0'] == 'FREE_IN_SLOT' and v['sp1'] == 'POSITIONAL_INDEPENDENT'
            and v['sp2'] == 'DYNAMICALLY_NEUTRAL'
            and v['sp6'] in ('POSITIONALLY_EXPLAINED', 'AMBIGUOUS')):
        overall = 'CONFIRMED_FREE_VARIATION'

    elif v['sp1'] == 'POSITIONAL_MEDIATION' and v['sp6'] == 'POSITIONALLY_EXPLAINED':
        overall = 'POSITIONAL_PROXY'

    elif v['sp2'] in ('DYNAMICALLY_CONSEQUENTIAL', 'RESIDUAL_EXTENSION') and v['sp3'] == 'FOLIO_DETERMINED':
        overall = 'PROGRAM_DESIGN_PARAMETER'

    elif v['sp4'] == 'BRIDGE_COUPLED' and v['sp5'] == 'PARALLEL_MECHANISM':
        overall = 'COMPOSITION_SIGNAL'

    elif v['sp6'] == 'SISTER_SPECIFIC_DYNAMICS' and v['sp0'] == 'STRUCTURED_IN_SLOT':
        overall = 'WITHIN_CLASS_ROUTING'

    elif v['sp7'] == 'BOUNDARY_COUPLED' and v['sp2'] in ('DYNAMICALLY_CONSEQUENTIAL', 'RESIDUAL_EXTENSION'):
        overall = 'BOUNDARY_CONTROL_KNOB'

    else:
        # Check if ANY test found structure
        structure_signals = []
        if v['sp0'] == 'STRUCTURED_IN_SLOT':
            structure_signals.append('slot')
        if v['sp1'] in ('POSITIONAL_MEDIATION', 'POSITIONAL_CONFOUND'):
            structure_signals.append('position')
        if v['sp2'] in ('DYNAMICALLY_CONSEQUENTIAL', 'RESIDUAL_EXTENSION'):
            structure_signals.append('dynamics')
        if v['sp4'] == 'BRIDGE_COUPLED':
            structure_signals.append('bridge')
        if v['sp6'] == 'SISTER_SPECIFIC_DYNAMICS':
            structure_signals.append('successor')
        if v['sp7'] == 'BOUNDARY_COUPLED':
            structure_signals.append('boundary')

        if len(structure_signals) >= 2:
            overall = 'PARTIAL_STRUCTURE'
        elif len(structure_signals) == 1:
            overall = f'WEAK_STRUCTURE_{structure_signals[0].upper()}'
        else:
            overall = 'CONFIRMED_FREE_VARIATION'

    print(f"\n  Overall: {overall}")

    return {
        'verdicts': verdicts,
        'overall': overall,
    }


# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 60)
    print("Phase 420: SISTER_PAIR_MECHANISM")
    print("=" * 60)

    data = load_data()

    t0 = test0_slot_equivalence(data)
    t1 = test1_positional_mediation(data)
    t2 = test2_dynamical_consequence(data)
    t3 = test3_concentration_icc(data)
    t4 = test4_bridge_dark_coupling(data)
    t5 = test5_ok_ot_parallel(data)
    t6 = test6_successor_decomposition(data)
    t7 = test7_boundary_divergence(data)

    syn = synthesize(t0, t1, t2, t3, t4, t5, t6, t7)

    results = {
        'phase': 'SISTER_PAIR_MECHANISM',
        'phase_number': 420,
        'depends_on': ['C639', 'C408', 'C409', 'C410', 'C929', 'C1146',
                        'C1157', 'C1158', 'C506', 'C1026'],
        'population': {
            'n_events': len(data['events']),
            'n_valid_folios': len(data['valid_folios']),
            'n_token_classes': len(data['token_to_class']),
        },
        'test0_slot_equivalence': t0,
        'test1_positional_mediation': t1,
        'test2_dynamical_consequence': t2,
        'test3_concentration_icc': t3,
        'test4_bridge_dark_coupling': t4,
        'test5_ok_ot_parallel': t5,
        'test6_successor_decomposition': t6,
        'test7_boundary_divergence': t7,
        'synthesis': syn,
    }

    results = round_floats(results)

    out_dir = ROOT / 'phases' / 'SISTER_PAIR_MECHANISM' / 'results'
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / 'sister_pair_mechanism.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nResults written to {out_path}")


if __name__ == '__main__':
    main()
