#!/usr/bin/env python3
"""Phase 457: PARAGRAPH_TERMINATION_TRIGGER

8-test battery probing what triggers paragraph termination.

C1237: -am is the termination signal (5.19x enriched). STOP rate is flat (no countdown).
C1239: Body length is section/REGIME-parameterized (~85% folio-specific).
C1240: Cooling-verified shutdown context (qo absent, e-MIDDLE enriched).
C1260: B-track thermal state propagates (e_frac rho=0.376) but no ordinal drift.
Phase 450 T5: Penultimate lines ARE distinguishable (2.45x). T6: No multi-line trajectory.

Tests:
  T1: Thermal level predicts last-line identity (length-controlled)
  T2: B-track terminal line thermal signature
  T3: Thermal step INTO final line
  T4: Within-section/folio thermal budget hypothesis
  T5: Mode A/B at termination
  T6: Category profile at termination
  T7: Folio termination rate extended prediction
  T8: Tail type category decomposition
"""

import json
import sys
import time
import functools
from pathlib import Path
from collections import Counter, defaultdict
from math import log2, log, sqrt, atanh, tanh

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parents[3]
RESULTS_DIR = Path(__file__).parent.parent / 'results'
sys.path.insert(0, str(ROOT))

from scripts.voynich import Transcript, Morphology

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)

# ============================================================
# Constants
# ============================================================

N_PERM = 1000
SEED = 42
BONFERRONI_P = 0.05 / 8  # 0.00625

CATEGORIES = ['CONTAINMENT', 'FLOW', 'MARKING', 'MONITORING',
              'OPERATION', 'STAGING', 'THERMAL', 'TRANSITION']
CAT_IDX = {c: i for i, c in enumerate(CATEGORIES)}
N_CATS = len(CATEGORIES)

# Suffix mode centroids (C1231)
MODE_A_CENTROID = np.array([0.430, 0.019, 0.086, 0.466])
MODE_B_CENTROID = np.array([0.155, 0.031, 0.072, 0.741])
TERMINAL_SUFFIXES = {'edy', 'dy', 'eey', 'ey', 'y', 'hy', 'iry', 'oly',
                     'ry', 'ky', 'ty', 'py', 'fy', 'my', 'ly', 'sy'}
CONNECTOR_SUFFIXES = {'o', 'or', 'os', 'oe'}
ITERATE_SUFFIXES = {'aiin', 'ain', 'aiiin', 'al', 'am', 'an'}

# Category assignment (from Phase 452)
GLOSS_TO_CATEGORY = {
    'heat': 'THERMAL', 'fire': 'THERMAL', 'cool': 'THERMAL',
    'sustain': 'THERMAL', 'pulse': 'THERMAL', 'steady': 'THERMAL',
    'extended': 'THERMAL', 'deep': 'THERMAL', 'long': 'THERMAL',
    'overnight': 'THERMAL',
    'seal': 'CONTAINMENT', 'hold': 'CONTAINMENT', 'lock': 'CONTAINMENT',
    'bind': 'CONTAINMENT', 'bond': 'CONTAINMENT', 'rigid': 'CONTAINMENT',
    'firm': 'CONTAINMENT', 'dense': 'CONTAINMENT',
    'transfer': 'FLOW', 'gather': 'FLOW', 'discharge': 'FLOW',
    'release': 'FLOW', 'vent': 'FLOW', 'route': 'FLOW',
    'portion': 'FLOW', 'input': 'FLOW', 'intake': 'FLOW',
    'watch': 'MONITORING', 'check': 'MONITORING', 'verify': 'MONITORING',
    'confirm': 'MONITORING', 'scan': 'MONITORING', 'measure': 'MONITORING',
    'control': 'MONITORING', 'regulate': 'MONITORING',
    'work': 'OPERATION', 'operate': 'OPERATION', 'batch': 'OPERATION',
    'pound': 'OPERATION', 'strip': 'OPERATION', 'exact': 'OPERATION',
    'precise': 'OPERATION', 'hard': 'OPERATION', 'wide': 'OPERATION',
    'start': 'TRANSITION', 'open': 'TRANSITION', 'close': 'TRANSITION',
    'end': 'TRANSITION', 'finish': 'TRANSITION', 'complete': 'TRANSITION',
    'finalize': 'TRANSITION', 'yield': 'TRANSITION', 'final': 'TRANSITION',
    'stand': 'TRANSITION', 'settle': 'TRANSITION', 'set': 'TRANSITION',
    'halt': 'TRANSITION',
    'frame': 'STAGING', 'step': 'STAGING', 'iterate': 'STAGING',
    'sequence': 'STAGING', 'continue': 'STAGING', 'repeat': 'STAGING',
    'cycle': 'STAGING', 'loop': 'STAGING', 'path': 'STAGING',
    'mark': 'MARKING', 'flag': 'MARKING', 'note': 'MARKING',
    'pause': 'MARKING', 'diagram': 'MARKING', 'hazard': 'MARKING',
    'danger': 'MARKING', 'link': 'MARKING', 'adjust': 'MARKING',
}
ATOM_GLOSSES = {
    'k': 'heat', 'e': 'cool', 'h': 'watch', 'y': 'end',
    'i': 'iterate', 'n': 'halt', 'a': 'yield', 'm': 'final',
    'd': 'mark', 't': 'transfer', 'c': 'adjust', 'p': 'pause',
    'f': 'flag', 's': 'sequence', 'g': 'complete', 'o': 'work',
    'l': 'frame', 'r': 'input',
}
ATOM_TO_CATEGORY = {a: GLOSS_TO_CATEGORY[g] for a, g in ATOM_GLOSSES.items()}

# Tail type features (from extraction_cycling_test.py)
ENERGY_PREFIX = {'qo'}
VESSEL_PREFIX = {'ok', 'ot', 'ol'}
PROCESS_PREFIX = {'ch', 'sh', 'sch'}
K_FAMILY_MIDDLES = {'k', 'ke', 'kch', 'ksh', 'ek'}
E_FAMILY_MIDDLES = {'e', 'ey', 'edy', 'eey', 'eok'}
PREP_FAMILY_MIDDLES = {'tch', 'pch', 'lch', 'dch', 'te', 'ksh'}


# ============================================================
# Utilities
# ============================================================

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, np.bool_):
            return bool(obj)
        return super().default(obj)


def auto_assign_category(atoms_str):
    if not atoms_str:
        return None
    votes = Counter()
    for atom in atoms_str:
        cat = ATOM_TO_CATEGORY.get(atom)
        if cat:
            votes[cat] += 1
    if not votes:
        return None
    max_count = max(votes.values())
    winners = [c for c, v in votes.items() if v == max_count]
    return sorted(winners)[0]


def build_category_map():
    with open(ROOT / 'data' / 'middle_dictionary.json', encoding='utf-8') as f:
        mid_dict = json.load(f)['middles']
    mid_to_cat = {}
    for mid, minfo in mid_dict.items():
        gloss = minfo.get('gloss')
        if gloss and gloss in GLOSS_TO_CATEGORY:
            mid_to_cat[mid] = GLOSS_TO_CATEGORY[gloss]
    for mid, minfo in mid_dict.items():
        if mid in mid_to_cat:
            continue
        atoms_str = minfo.get('autogloss_atoms', '')
        if atoms_str:
            cat = auto_assign_category(atoms_str)
            if cat:
                mid_to_cat[mid] = cat
    return mid_to_cat


def classify_suffix_mode(line_toks):
    """Classify line as Mode A or B using C1231 centroids."""
    if len(line_toks) < 3:
        return None
    n = len(line_toks)
    cats = [0, 0, 0, 0]  # terminal, connector, iterate, bare
    for tok in line_toks:
        sfx = tok.get('suffix', '') or ''
        if sfx in TERMINAL_SUFFIXES:
            cats[0] += 1
        elif sfx in CONNECTOR_SUFFIXES:
            cats[1] += 1
        elif sfx in ITERATE_SUFFIXES:
            cats[2] += 1
        else:
            cats[3] += 1
    vec = np.array(cats, dtype=float) / n
    dist_a = np.linalg.norm(vec - MODE_A_CENTROID)
    dist_b = np.linalg.norm(vec - MODE_B_CENTROID)
    return 'A' if dist_a < dist_b else 'B'


def extract_line_state(toks):
    """Extract thermal/compositional state from a line's tokens."""
    n = len(toks)
    if n == 0:
        return None
    k_count = sum(1 for t in toks if 'k' in t.get('kernels', []))
    e_count = sum(1 for t in toks if 'e' in t.get('kernels', []))
    return {
        'e_frac': e_count / n,
        'k_frac': k_count / n,
        'ke_ratio': k_count / max(e_count, 1),
        'qo_frac': sum(1 for t in toks if t.get('prefix') == 'qo') / n,
        'n_toks': n,
    }


def prefix_domain(prefix):
    if not prefix:
        return 'NONE'
    if prefix in ENERGY_PREFIX:
        return 'ENERGY'
    if prefix in VESSEL_PREFIX:
        return 'VESSEL'
    if prefix in PROCESS_PREFIX:
        return 'PROCESS'
    return 'OTHER'


def verdict(p, effect=None, bonferroni=BONFERRONI_P, min_effect=None):
    if p < bonferroni:
        return 'PASS'
    elif p < 0.05:
        return 'WEAK'
    return 'FAIL'


# OLS utilities (from residual_freedom_characterization.py)
def standardize(x):
    arr = np.array(x, dtype=float)
    return (arr - arr.mean()) / (arr.std() + 1e-10)

def ols_fit(X, y):
    beta = np.linalg.lstsq(X, y, rcond=None)[0]
    y_pred = X @ beta
    ss_res = np.sum((y - y_pred) ** 2)
    ss_tot = np.sum((y - y.mean()) ** 2)
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0
    return beta, y_pred, ss_res, r2

def loo_cv_r2(X, y):
    n = len(y)
    y_pred_loo = np.zeros(n)
    for i in range(n):
        mask = np.ones(n, dtype=bool)
        mask[i] = False
        beta = np.linalg.lstsq(X[mask], y[mask], rcond=None)[0]
        y_pred_loo[i] = float(X[i:i+1] @ beta)
    ss_res = np.sum((y - y_pred_loo) ** 2)
    ss_tot = np.sum((y - y.mean()) ** 2)
    return 1 - ss_res / ss_tot if ss_tot > 0 else 0

def build_dummies(labels):
    unique = sorted(set(labels))
    if len(unique) <= 1:
        return np.zeros((len(labels), 0))
    dummies = np.zeros((len(labels), len(unique) - 1))
    for i, label in enumerate(labels):
        idx = unique.index(label)
        if idx > 0:
            dummies[i, idx - 1] = 1
    return dummies

def f_test_increment(ss_res_reduced, ss_res_full, df_extra, n_obs, k_full):
    df_res = n_obs - k_full
    if df_res <= 0 or ss_res_full <= 0:
        return 0.0, 1.0
    f_stat = ((ss_res_reduced - ss_res_full) / df_extra) / (ss_res_full / df_res)
    p_val = 1 - stats.f.cdf(f_stat, df_extra, df_res)
    return float(f_stat), float(p_val)


# ============================================================
# Data Loading
# ============================================================

def load_data():
    print("Loading data...")
    t0 = time.time()

    mid_to_cat = build_category_map()
    morph = Morphology()

    # REGIME/section
    with open(ROOT / 'data' / 'regime_folio_mapping.json', encoding='utf-8') as f:
        regime_data = json.load(f)
    regime_assignments = regime_data['regime_assignments']

    with open(ROOT / 'phases' / 'AXM_RESIDUAL_DECOMPOSITION' / 'results' /
              'axm_residual_decomposition.json', encoding='utf-8') as f:
        axm_json = json.load(f)
    folio_data = axm_json['folio_data']

    # Build paragraph inventory
    folio_lines = defaultdict(lambda: defaultdict(list))
    for t in Transcript().currier_b():
        w = t.word.strip()
        if not w or '*' in w:
            continue
        if t.placement.startswith('L'):
            continue
        m = morph.extract(w)
        middle = m.middle if m else ''
        prefix = m.prefix if m else ''
        suffix = m.suffix if m else ''
        cat = mid_to_cat.get(middle) if middle else None
        kernels = [c for c in 'khe' if c in middle]

        tok = {
            'word': w, 'folio': t.folio, 'line': t.line,
            'middle': middle, 'prefix': prefix, 'suffix': suffix,
            'category': cat, 'kernels': kernels,
            'par_initial': t.par_initial,
        }
        folio_lines[t.folio][t.line].append(tok)

    # Build paragraphs
    paragraphs = []
    for folio in sorted(folio_lines.keys()):
        section = folio_data.get(folio, {}).get('section', 'UNKNOWN')
        regime = regime_assignments.get(folio, {}).get('regime', 'UNKNOWN')

        lines_dict = folio_lines[folio]
        line_nums = sorted(lines_dict.keys())

        current_lines = []
        for ln in line_nums:
            line_toks = lines_dict[ln]
            if line_toks[0]['par_initial'] and current_lines:
                # Close current paragraph
                paragraphs.append(_build_paragraph(current_lines, folio, section, regime))
                current_lines = []
            current_lines.append((ln, line_toks))
        if current_lines:
            paragraphs.append(_build_paragraph(current_lines, folio, section, regime))

    elapsed = time.time() - t0
    print(f"  Paragraphs: {len(paragraphs)}")
    print(f"  With 3+ body lines: {sum(1 for p in paragraphs if p['n_body'] >= 3)}")
    print(f"  Time: {elapsed:.1f}s")

    return paragraphs


def _build_paragraph(lines, folio, section, regime):
    """Build a paragraph dict from a list of (line_num, [tokens]) tuples."""
    all_lines = []
    for i, (ln, toks) in enumerate(lines):
        is_header = (i == 0)
        is_last = (i == len(lines) - 1)
        state = extract_line_state(toks)
        mode = classify_suffix_mode(toks)

        # Category counts for this line
        cat_counts = Counter()
        for tok in toks:
            if tok['category']:
                cat_counts[tok['category']] += 1

        # Tail type features
        prefixes = [tok['prefix'] for tok in toks if tok['prefix']]
        middles = [tok['middle'] for tok in toks if tok['middle']]

        all_lines.append({
            'line_num': ln,
            'tokens': toks,
            'state': state,
            'mode': mode,
            'is_header': is_header,
            'is_last_body': is_last and not is_header,
            'cat_counts': cat_counts,
            'prefixes': prefixes,
            'middles': middles,
            'n_toks': len(toks),
        })

    body_lines = [l for l in all_lines if not l['is_header']]
    if body_lines:
        body_lines[-1]['is_last_body'] = True

    return {
        'folio': folio,
        'section': section,
        'regime': regime,
        'all_lines': all_lines,
        'body_lines': body_lines,
        'n_body': len(body_lines),
        'n_total': len(all_lines),
    }


# ============================================================
# T1: Thermal Level Predicts Last-Line Identity
# ============================================================

def test_t1(paragraphs):
    print("\n=== T1: Thermal Level Predicts Last-Line Identity ===")
    rng = np.random.RandomState(SEED)

    # Collect all body lines with state
    last_efrac = []
    interior_efrac = []
    last_ntoks = []
    interior_ntoks = []

    for p in paragraphs:
        if p['n_body'] < 3:
            continue
        for bl in p['body_lines']:
            if bl['state'] is None:
                continue
            ef = bl['state']['e_frac']
            nt = bl['state']['n_toks']
            if bl['is_last_body']:
                last_efrac.append(ef)
                last_ntoks.append(nt)
            else:
                interior_efrac.append(ef)
                interior_ntoks.append(nt)

    last_efrac = np.array(last_efrac)
    interior_efrac = np.array(interior_efrac)

    # Raw comparison
    u_stat, p_raw = stats.mannwhitneyu(last_efrac, interior_efrac, alternative='two-sided')
    raw_effect = np.mean(last_efrac) - np.mean(interior_efrac)

    print(f"  Raw: last e_frac={np.mean(last_efrac):.4f}, interior={np.mean(interior_efrac):.4f}, "
          f"diff={raw_effect:+.4f}, p={p_raw:.4f}")
    print(f"  Raw: last n_toks={np.mean(last_ntoks):.1f}, interior={np.mean(interior_ntoks):.1f}")

    # Length-controlled: stratify by n_toks quartile
    all_efrac = np.concatenate([last_efrac, interior_efrac])
    all_ntoks = np.array(last_ntoks + interior_ntoks)
    all_is_last = np.array([1] * len(last_efrac) + [0] * len(interior_efrac))

    quartiles = np.percentile(all_ntoks, [25, 50, 75])
    bins = np.digitize(all_ntoks, quartiles)

    fisher_stat = 0.0
    fisher_dof = 0
    quartile_results = {}
    for q in range(4):
        mask = bins == q
        if mask.sum() < 10:
            continue
        q_last = all_efrac[mask & (all_is_last == 1)]
        q_int = all_efrac[mask & (all_is_last == 0)]
        if len(q_last) < 5 or len(q_int) < 5:
            continue
        u, p_q = stats.mannwhitneyu(q_last, q_int, alternative='two-sided')
        diff = np.mean(q_last) - np.mean(q_int)
        quartile_results[f'Q{q}'] = {
            'n_last': len(q_last), 'n_int': len(q_int),
            'mean_last': float(np.mean(q_last)), 'mean_int': float(np.mean(q_int)),
            'diff': float(diff), 'p': float(p_q),
        }
        if p_q > 0:
            fisher_stat += -2 * log(max(p_q, 1e-300))
            fisher_dof += 2

    fisher_p = 1 - stats.chi2.cdf(fisher_stat, fisher_dof) if fisher_dof > 0 else 1.0

    # Also test ke_ratio
    last_ke = np.array([bl['state']['ke_ratio'] for p in paragraphs if p['n_body'] >= 3
                        for bl in p['body_lines'] if bl['is_last_body'] and bl['state']])
    interior_ke = np.array([bl['state']['ke_ratio'] for p in paragraphs if p['n_body'] >= 3
                            for bl in p['body_lines'] if not bl['is_last_body'] and bl['state']])
    u_ke, p_ke = stats.mannwhitneyu(last_ke, interior_ke, alternative='two-sided')

    v_str = verdict(fisher_p)
    print(f"  Length-controlled Fisher: stat={fisher_stat:.1f}, dof={fisher_dof}, p={fisher_p:.4f}")
    for q, qr in sorted(quartile_results.items()):
        sig = "*" if qr['p'] < 0.05 else ""
        print(f"    {q}: last={qr['mean_last']:.4f}, int={qr['mean_int']:.4f}, "
              f"diff={qr['diff']:+.4f}, p={qr['p']:.4f}{sig}")
    print(f"  ke_ratio: last={np.mean(last_ke):.3f}, interior={np.mean(interior_ke):.3f}, p={p_ke:.4f}")
    print(f"  Verdict: {v_str}")

    return {
        'test': 'T1_thermal_level_last_line',
        'n_last': len(last_efrac), 'n_interior': len(interior_efrac),
        'raw_diff': float(raw_effect), 'raw_p': float(p_raw),
        'fisher_stat': float(fisher_stat), 'fisher_dof': fisher_dof,
        'fisher_p': float(fisher_p),
        'quartile_results': quartile_results,
        'ke_ratio_p': float(p_ke),
        'verdict': v_str,
    }


# ============================================================
# T2: B-Track Terminal Line Thermal Signature
# ============================================================

def test_t2(paragraphs):
    print("\n=== T2: B-Track Terminal Line Thermal Signature ===")

    terminal_b_efrac = []
    interior_b_efrac = []
    terminal_b_ntoks = []
    interior_b_ntoks = []

    for p in paragraphs:
        if p['n_body'] < 3:
            continue
        b_lines = [bl for bl in p['body_lines'] if bl['mode'] == 'B' and bl['state']]
        if len(b_lines) < 2:
            continue
        # Terminal B-line = last Mode B line in body
        for i, bl in enumerate(b_lines):
            ef = bl['state']['e_frac']
            nt = bl['state']['n_toks']
            if i == len(b_lines) - 1:
                terminal_b_efrac.append(ef)
                terminal_b_ntoks.append(nt)
            else:
                interior_b_efrac.append(ef)
                interior_b_ntoks.append(nt)

    terminal_b_efrac = np.array(terminal_b_efrac)
    interior_b_efrac = np.array(interior_b_efrac)

    if len(terminal_b_efrac) < 10 or len(interior_b_efrac) < 10:
        print("  SKIP: insufficient B-track data")
        return {'test': 'T2_b_track_thermal', 'verdict': 'SKIP'}

    u, p_raw = stats.mannwhitneyu(terminal_b_efrac, interior_b_efrac, alternative='two-sided')
    diff = np.mean(terminal_b_efrac) - np.mean(interior_b_efrac)

    # Length-controlled: stratify
    all_ef = np.concatenate([terminal_b_efrac, interior_b_efrac])
    all_nt = np.array(terminal_b_ntoks + interior_b_ntoks)
    all_is_term = np.array([1] * len(terminal_b_efrac) + [0] * len(interior_b_efrac))
    median_nt = np.median(all_nt)

    strat_results = {}
    fisher_stat = 0.0
    fisher_dof = 0
    for label, mask in [('short', all_nt <= median_nt), ('long', all_nt > median_nt)]:
        t_ef = all_ef[mask & (all_is_term == 1)]
        i_ef = all_ef[mask & (all_is_term == 0)]
        if len(t_ef) < 5 or len(i_ef) < 5:
            continue
        u_s, p_s = stats.mannwhitneyu(t_ef, i_ef, alternative='two-sided')
        strat_results[label] = {
            'n_term': len(t_ef), 'n_int': len(i_ef),
            'mean_term': float(np.mean(t_ef)), 'mean_int': float(np.mean(i_ef)),
            'p': float(p_s),
        }
        if p_s > 0:
            fisher_stat += -2 * log(max(p_s, 1e-300))
            fisher_dof += 2

    fisher_p = 1 - stats.chi2.cdf(fisher_stat, fisher_dof) if fisher_dof > 0 else 1.0

    v_str = verdict(fisher_p)
    print(f"  B-track: terminal e_frac={np.mean(terminal_b_efrac):.4f}, "
          f"interior={np.mean(interior_b_efrac):.4f}, diff={diff:+.4f}, raw p={p_raw:.4f}")
    print(f"  Length-controlled Fisher: p={fisher_p:.4f}")
    print(f"  Verdict: {v_str}")

    return {
        'test': 'T2_b_track_thermal',
        'n_terminal': len(terminal_b_efrac), 'n_interior': len(interior_b_efrac),
        'raw_diff': float(diff), 'raw_p': float(p_raw),
        'fisher_p': float(fisher_p),
        'stratified': strat_results,
        'verdict': v_str,
    }


# ============================================================
# T3: Thermal Step INTO Final Line
# ============================================================

def test_t3(paragraphs):
    print("\n=== T3: Thermal Step INTO Final Line ===")
    rng = np.random.RandomState(SEED)

    terminal_deltas = []
    interior_deltas = []

    for p in paragraphs:
        if p['n_body'] < 3:
            continue
        body = [bl for bl in p['body_lines'] if bl['state']]
        if len(body) < 3:
            continue
        for i in range(len(body) - 1):
            delta = body[i + 1]['state']['e_frac'] - body[i]['state']['e_frac']
            if i + 1 == len(body) - 1:
                terminal_deltas.append(delta)
            else:
                interior_deltas.append(delta)

    terminal_deltas = np.array(terminal_deltas)
    interior_deltas = np.array(interior_deltas)

    if len(terminal_deltas) < 10:
        print("  SKIP: insufficient data")
        return {'test': 'T3_thermal_step', 'verdict': 'SKIP'}

    u, p_raw = stats.mannwhitneyu(terminal_deltas, interior_deltas, alternative='two-sided')
    diff = np.mean(terminal_deltas) - np.mean(interior_deltas)

    # Permutation test
    observed_diff = diff
    combined = np.concatenate([terminal_deltas, interior_deltas])
    n_term = len(terminal_deltas)
    perm_count = 0
    for _ in range(N_PERM):
        perm = rng.permutation(combined)
        perm_diff = np.mean(perm[:n_term]) - np.mean(perm[n_term:])
        if abs(perm_diff) >= abs(observed_diff):
            perm_count += 1
    perm_p = (perm_count + 1) / (N_PERM + 1)

    # Also test ke_ratio delta
    term_ke_delta = []
    int_ke_delta = []
    for p in paragraphs:
        if p['n_body'] < 3:
            continue
        body = [bl for bl in p['body_lines'] if bl['state']]
        if len(body) < 3:
            continue
        for i in range(len(body) - 1):
            delta = body[i + 1]['state']['ke_ratio'] - body[i]['state']['ke_ratio']
            if i + 1 == len(body) - 1:
                term_ke_delta.append(delta)
            else:
                int_ke_delta.append(delta)
    u_ke, p_ke = stats.mannwhitneyu(term_ke_delta, int_ke_delta, alternative='two-sided')

    v_str = verdict(perm_p)
    print(f"  Terminal delta_e: mean={np.mean(terminal_deltas):+.4f} (n={len(terminal_deltas)})")
    print(f"  Interior delta_e: mean={np.mean(interior_deltas):+.4f} (n={len(interior_deltas)})")
    print(f"  Diff: {diff:+.4f}, MW p={p_raw:.4f}, Perm p={perm_p:.4f}")
    print(f"  ke_ratio delta: MW p={p_ke:.4f}")
    print(f"  Verdict: {v_str}")

    return {
        'test': 'T3_thermal_step',
        'n_terminal': len(terminal_deltas), 'n_interior': len(interior_deltas),
        'terminal_mean': float(np.mean(terminal_deltas)),
        'interior_mean': float(np.mean(interior_deltas)),
        'diff': float(diff), 'mw_p': float(p_raw), 'perm_p': float(perm_p),
        'ke_mw_p': float(p_ke),
        'verdict': v_str,
    }


# ============================================================
# T4: Within-Section Thermal Budget Hypothesis
# ============================================================

def test_t4(paragraphs):
    print("\n=== T4: Within-Section Thermal Budget Hypothesis ===")

    # Collect per-paragraph data
    para_data = []
    for p in paragraphs:
        if p['n_body'] < 2:
            continue
        body_efrac = [bl['state']['e_frac'] for bl in p['body_lines'] if bl['state']]
        if not body_efrac:
            continue
        para_data.append({
            'folio': p['folio'],
            'section': p['section'],
            'mean_e_frac': np.mean(body_efrac),
            'body_length': p['n_body'],
        })

    # Within-section analysis
    sections = sorted(set(d['section'] for d in para_data))
    section_results = {}
    fisher_z_sum = 0.0
    fisher_n_sum = 0
    for sec in sections:
        sec_data = [d for d in para_data if d['section'] == sec]
        if len(sec_data) < 30:
            continue
        ef = [d['mean_e_frac'] for d in sec_data]
        bl = [d['body_length'] for d in sec_data]
        rho, p = stats.spearmanr(ef, bl)
        section_results[sec] = {'n': len(sec_data), 'rho': float(rho), 'p': float(p)}
        # Fisher z-transform
        z = atanh(max(-0.999, min(0.999, rho)))
        fisher_z_sum += z * (len(sec_data) - 3)
        fisher_n_sum += len(sec_data) - 3

    if fisher_n_sum > 0:
        meta_z = fisher_z_sum / fisher_n_sum
        meta_rho = tanh(meta_z)
        se = 1.0 / sqrt(fisher_n_sum)
        meta_z_score = meta_z / se
        meta_p = 2 * (1 - stats.norm.cdf(abs(meta_z_score)))
    else:
        meta_rho, meta_p, meta_z_score = 0.0, 1.0, 0.0

    # Within-folio analysis (definitive)
    folio_rhos = []
    folio_ns = []
    for folio in sorted(set(d['folio'] for d in para_data)):
        f_data = [d for d in para_data if d['folio'] == folio]
        if len(f_data) < 3:
            continue
        ef = [d['mean_e_frac'] for d in f_data]
        bl = [d['body_length'] for d in f_data]
        if len(set(ef)) < 2 or len(set(bl)) < 2:
            continue
        rho, _ = stats.spearmanr(ef, bl)
        folio_rhos.append(rho)
        folio_ns.append(len(f_data))

    if folio_rhos:
        # Fisher z-transform for within-folio
        f_z_sum = 0.0
        f_n_sum = 0
        for rho, n in zip(folio_rhos, folio_ns):
            z = atanh(max(-0.999, min(0.999, rho)))
            f_z_sum += z * (n - 3)
            f_n_sum += n - 3
        if f_n_sum > 0:
            f_meta_z = f_z_sum / f_n_sum
            f_meta_rho = tanh(f_meta_z)
            f_se = 1.0 / sqrt(f_n_sum)
            f_meta_z_score = f_meta_z / f_se
            f_meta_p = 2 * (1 - stats.norm.cdf(abs(f_meta_z_score)))
        else:
            f_meta_rho, f_meta_p, f_meta_z_score = 0.0, 1.0, 0.0
    else:
        f_meta_rho, f_meta_p, f_meta_z_score = 0.0, 1.0, 0.0

    # Use the within-folio p as the definitive test
    v_str = verdict(f_meta_p)
    print(f"  Within-section (meta): rho={meta_rho:+.3f}, z={meta_z_score:.2f}, p={meta_p:.4f}")
    for sec, sr in sorted(section_results.items()):
        sig = "*" if sr['p'] < 0.05 else ""
        print(f"    {sec}: n={sr['n']}, rho={sr['rho']:+.3f}, p={sr['p']:.4f}{sig}")
    print(f"  Within-folio (meta, DEFINITIVE): rho={f_meta_rho:+.3f}, z={f_meta_z_score:.2f}, "
          f"p={f_meta_p:.4f} ({len(folio_rhos)} folios)")
    print(f"  Verdict: {v_str}")

    return {
        'test': 'T4_thermal_budget',
        'section_results': section_results,
        'meta_rho_section': float(meta_rho),
        'meta_p_section': float(meta_p),
        'n_folios_within': len(folio_rhos),
        'meta_rho_folio': float(f_meta_rho),
        'meta_p_folio': float(f_meta_p),
        'meta_z_folio': float(f_meta_z_score),
        'verdict': v_str,
    }


# ============================================================
# T5: Mode A/B at Termination
# ============================================================

def test_t5(paragraphs):
    print("\n=== T5: Mode A/B at Termination ===")

    last2_mode_a = 0
    last2_mode_b = 0
    earlier_mode_a = 0
    earlier_mode_b = 0

    for p in paragraphs:
        if p['n_body'] < 4:
            continue
        body = p['body_lines']
        for i, bl in enumerate(body):
            if bl['mode'] is None:
                continue
            is_last2 = (i >= len(body) - 2)
            if is_last2:
                if bl['mode'] == 'A':
                    last2_mode_a += 1
                else:
                    last2_mode_b += 1
            else:
                if bl['mode'] == 'A':
                    earlier_mode_a += 1
                else:
                    earlier_mode_b += 1

    table = np.array([[last2_mode_a, last2_mode_b],
                      [earlier_mode_a, earlier_mode_b]], dtype=float)
    if table.min() < 1:
        table += 0.5

    chi2, p_val, dof, _ = stats.chi2_contingency(table)
    total_last2 = last2_mode_a + last2_mode_b
    total_earlier = earlier_mode_a + earlier_mode_b
    pct_a_last2 = last2_mode_a / max(total_last2, 1)
    pct_a_earlier = earlier_mode_a / max(total_earlier, 1)

    v_str = verdict(p_val)
    print(f"  Last 2 lines: Mode A={last2_mode_a} ({pct_a_last2:.1%}), Mode B={last2_mode_b}")
    print(f"  Earlier lines: Mode A={earlier_mode_a} ({pct_a_earlier:.1%}), Mode B={earlier_mode_b}")
    print(f"  chi2={chi2:.2f}, p={p_val:.4f}")
    print(f"  Verdict: {v_str}")

    return {
        'test': 'T5_mode_at_termination',
        'last2_mode_a': last2_mode_a, 'last2_mode_b': last2_mode_b,
        'earlier_mode_a': earlier_mode_a, 'earlier_mode_b': earlier_mode_b,
        'pct_a_last2': float(pct_a_last2), 'pct_a_earlier': float(pct_a_earlier),
        'chi2': float(chi2), 'p': float(p_val),
        'verdict': v_str,
    }


# ============================================================
# T6: Category Profile at Termination
# ============================================================

def test_t6(paragraphs):
    print("\n=== T6: Category Profile at Termination ===")
    rng = np.random.RandomState(SEED)

    last2_cats = Counter()
    earlier_cats = Counter()

    for p in paragraphs:
        if p['n_body'] < 4:
            continue
        body = p['body_lines']
        for i, bl in enumerate(body):
            is_last2 = (i >= len(body) - 2)
            for cat, cnt in bl['cat_counts'].items():
                if is_last2:
                    last2_cats[cat] += cnt
                else:
                    earlier_cats[cat] += cnt

    # Build 2x8 table
    table = np.zeros((2, N_CATS), dtype=float)
    for ci, cat in enumerate(CATEGORIES):
        table[0, ci] = last2_cats.get(cat, 0)
        table[1, ci] = earlier_cats.get(cat, 0)

    chi2, p_val, dof, expected = stats.chi2_contingency(table)

    # Per-category enrichment
    total_last2 = table[0].sum()
    total_earlier = table[1].sum()
    enrichment = {}
    for ci, cat in enumerate(CATEGORIES):
        rate_last2 = table[0, ci] / max(total_last2, 1)
        rate_earlier = table[1, ci] / max(total_earlier, 1)
        ratio = rate_last2 / max(rate_earlier, 1e-6)
        enrichment[cat] = {'last2': float(rate_last2), 'earlier': float(rate_earlier),
                           'ratio': float(ratio)}

    # Permutation test
    # Collect per-paragraph line category vectors
    para_line_cats = []
    for p in paragraphs:
        if p['n_body'] < 4:
            continue
        body = p['body_lines']
        line_vecs = []
        for bl in body:
            vec = np.array([bl['cat_counts'].get(c, 0) for c in CATEGORIES])
            line_vecs.append(vec)
        para_line_cats.append(line_vecs)

    observed_chi2 = chi2
    perm_count = 0
    for _ in range(N_PERM):
        perm_last2 = np.zeros(N_CATS)
        perm_earlier = np.zeros(N_CATS)
        for line_vecs in para_line_cats:
            n = len(line_vecs)
            perm_idx = rng.permutation(n)
            for j, idx in enumerate(perm_idx):
                if j >= n - 2:
                    perm_last2 += line_vecs[idx]
                else:
                    perm_earlier += line_vecs[idx]
        perm_table = np.array([perm_last2, perm_earlier])
        if perm_table.min() < 0.5:
            perm_table += 0.5
        try:
            pc2, _, _, _ = stats.chi2_contingency(perm_table)
            if pc2 >= observed_chi2:
                perm_count += 1
        except ValueError:
            pass
    perm_p = (perm_count + 1) / (N_PERM + 1)

    v_str = verdict(perm_p)
    print(f"  chi2={chi2:.1f}, dof={dof}, analytic p={p_val:.4f}, perm p={perm_p:.4f}")
    print(f"  Enrichment at termination:")
    for cat in CATEGORIES:
        e = enrichment[cat]
        marker = "+" if e['ratio'] > 1.1 else ("-" if e['ratio'] < 0.9 else " ")
        print(f"    {marker} {cat}: {e['last2']:.1%} vs {e['earlier']:.1%} ({e['ratio']:.2f}x)")
    print(f"  Verdict: {v_str}")

    return {
        'test': 'T6_category_at_termination',
        'chi2': float(chi2), 'p_analytic': float(p_val), 'p_perm': float(perm_p),
        'enrichment': enrichment,
        'verdict': v_str,
    }


# ============================================================
# T7: Folio Termination Rate Extended Prediction
# ============================================================

def test_t7(paragraphs):
    print("\n=== T7: Folio Termination Rate Extended Prediction ===")

    # Aggregate per folio
    folio_data_agg = defaultdict(lambda: {'lengths': [], 'e_fracs': [], 'cat_counts': Counter()})
    folio_meta = {}
    for p in paragraphs:
        if p['n_body'] < 1:
            continue
        f = p['folio']
        folio_data_agg[f]['lengths'].append(p['n_body'])
        for bl in p['body_lines']:
            if bl['state']:
                folio_data_agg[f]['e_fracs'].append(bl['state']['e_frac'])
            for cat, cnt in bl['cat_counts'].items():
                folio_data_agg[f]['cat_counts'][cat] += cnt
        folio_meta[f] = {'section': p['section'], 'regime': p['regime']}

    # Build folio-level dataset
    folios = sorted(f for f in folio_data_agg if len(folio_data_agg[f]['lengths']) >= 2)
    n = len(folios)
    if n < 20:
        print("  SKIP: insufficient folios")
        return {'test': 'T7_folio_prediction', 'verdict': 'SKIP'}

    y = np.array([np.mean(folio_data_agg[f]['lengths']) for f in folios])
    sections = [folio_meta[f]['section'] for f in folios]
    regimes = [folio_meta[f]['regime'] for f in folios]

    # Baseline: section + REGIME
    intercept = np.ones((n, 1))
    sec_dum = build_dummies(sections)
    reg_dum = build_dummies(regimes)
    X_base = np.hstack([intercept, sec_dum, reg_dum])

    _, _, ss_base, r2_base = ols_fit(X_base, y)
    loo_base = loo_cv_r2(X_base, y)

    # Extended: + mean_e_frac + THERMAL_frac + TRANSITION_frac
    mean_ef = np.array([np.mean(folio_data_agg[f]['e_fracs']) if folio_data_agg[f]['e_fracs']
                        else 0.5 for f in folios])
    thermal_frac = np.array([folio_data_agg[f]['cat_counts'].get('THERMAL', 0) /
                             max(sum(folio_data_agg[f]['cat_counts'].values()), 1)
                             for f in folios])
    transition_frac = np.array([folio_data_agg[f]['cat_counts'].get('TRANSITION', 0) /
                                max(sum(folio_data_agg[f]['cat_counts'].values()), 1)
                                for f in folios])

    ef_z = standardize(mean_ef).reshape(-1, 1)
    th_z = standardize(thermal_frac).reshape(-1, 1)
    tr_z = standardize(transition_frac).reshape(-1, 1)

    X_ext = np.hstack([X_base, ef_z, th_z, tr_z])
    _, _, ss_ext, r2_ext = ols_fit(X_ext, y)
    loo_ext = loo_cv_r2(X_ext, y)

    delta_r2 = r2_ext - r2_base
    delta_loo = loo_ext - loo_base
    f_stat, f_p = f_test_increment(ss_base, ss_ext, 3, n, X_ext.shape[1])

    v_str = verdict(f_p)
    if v_str == 'PASS' and delta_loo < 0:
        v_str = 'WEAK'
        print("  NOTE: F-test significant but LOO decreased -- downgraded")

    print(f"  Baseline: R2={r2_base:.4f}, LOO={loo_base:.4f} (section+REGIME)")
    print(f"  Extended: R2={r2_ext:.4f}, LOO={loo_ext:.4f} (+e_frac, THERMAL, TRANSITION)")
    print(f"  Delta R2={delta_r2:+.4f}, Delta LOO={delta_loo:+.4f}")
    print(f"  F-test: F={f_stat:.2f}, p={f_p:.4f}")
    print(f"  Verdict: {v_str}")

    return {
        'test': 'T7_folio_prediction',
        'n_folios': n,
        'r2_base': float(r2_base), 'loo_base': float(loo_base),
        'r2_ext': float(r2_ext), 'loo_ext': float(loo_ext),
        'delta_r2': float(delta_r2), 'delta_loo': float(delta_loo),
        'f_stat': float(f_stat), 'f_p': float(f_p),
        'verdict': v_str,
    }


# ============================================================
# T8: Tail Type Category Decomposition
# ============================================================

def test_t8(paragraphs):
    print("\n=== T8: Tail Type Category Decomposition ===")
    from sklearn.cluster import KMeans
    from sklearn.metrics import silhouette_score
    rng_np = np.random.RandomState(SEED)

    qualifying = [p for p in paragraphs if p['n_body'] >= 3]
    print(f"  Paragraphs with 3+ body lines: {len(qualifying)}")

    # Extract tail features (last 2 body lines)
    tail_features = []
    tail_cat_counts = []
    for p in qualifying:
        body = p['body_lines']
        tail = body[-2:]
        all_prefixes = []
        all_middles = []
        cat_counts = Counter()
        for bl in tail:
            all_prefixes.extend(bl['prefixes'])
            all_middles.extend(bl['middles'])
            for cat, cnt in bl['cat_counts'].items():
                cat_counts[cat] += cnt

        n_pfx = max(len(all_prefixes), 1)
        n_mid = max(len(all_middles), 1)
        energy = sum(1 for p in all_prefixes if p in ENERGY_PREFIX) / n_pfx
        vessel = sum(1 for p in all_prefixes if p in VESSEL_PREFIX) / n_pfx
        process = sum(1 for p in all_prefixes if p in PROCESS_PREFIX) / n_pfx
        k_fam = sum(1 for m in all_middles if m in K_FAMILY_MIDDLES) / n_mid
        e_fam = sum(1 for m in all_middles if m in E_FAMILY_MIDDLES) / n_mid
        prep_fam = sum(1 for m in all_middles if m in PREP_FAMILY_MIDDLES) / n_mid

        tail_features.append([energy, vessel, process, k_fam, e_fam, prep_fam])
        tail_cat_counts.append(cat_counts)

    tail_arr = np.array(tail_features)
    if len(tail_arr) < 20:
        print("  SKIP: insufficient data")
        return {'test': 'T8_tail_category', 'verdict': 'SKIP'}

    # K-means k=3 (matching C1232)
    km = KMeans(n_clusters=3, n_init=10, random_state=SEED).fit(tail_arr)
    sil = silhouette_score(tail_arr, km.labels_)
    print(f"  Clustering: k=3, silhouette={sil:.4f}")
    cluster_sizes = [int(np.sum(km.labels_ == i)) for i in range(3)]
    print(f"  Cluster sizes: {cluster_sizes}")

    # Build 3x8 category table
    table = np.zeros((3, N_CATS), dtype=float)
    for i, cc in enumerate(tail_cat_counts):
        ci = km.labels_[i]
        for cat, cnt in cc.items():
            table[ci, CAT_IDX[cat]] += cnt

    # Remove empty rows/cols
    row_sums = table.sum(axis=1)
    col_sums = table.sum(axis=0)
    valid_rows = row_sums > 0
    valid_cols = col_sums > 0
    if valid_rows.sum() < 2 or valid_cols.sum() < 2:
        print("  SKIP: degenerate table")
        return {'test': 'T8_tail_category', 'verdict': 'SKIP'}

    table_clean = table[valid_rows][:, valid_cols]
    chi2, p_val, dof, _ = stats.chi2_contingency(table_clean)

    # Per-cluster category profiles
    cluster_profiles = {}
    for ci in range(3):
        total = table[ci].sum()
        if total > 0:
            profile = {CATEGORIES[j]: float(table[ci, j] / total) for j in range(N_CATS)}
            cluster_profiles[f'cluster_{ci}'] = profile

    # Permutation test
    observed_chi2 = chi2
    perm_count = 0
    for _ in range(N_PERM):
        perm_labels = rng_np.permutation(km.labels_)
        perm_table = np.zeros((3, N_CATS), dtype=float)
        for i, cc in enumerate(tail_cat_counts):
            ci = perm_labels[i]
            for cat, cnt in cc.items():
                perm_table[ci, CAT_IDX[cat]] += cnt
        pr = perm_table.sum(axis=1)
        pc = perm_table.sum(axis=0)
        vr = pr > 0
        vc = pc > 0
        if vr.sum() < 2 or vc.sum() < 2:
            continue
        try:
            pc2, _, _, _ = stats.chi2_contingency(perm_table[vr][:, vc])
            if pc2 >= observed_chi2:
                perm_count += 1
        except ValueError:
            pass
    perm_p = (perm_count + 1) / (N_PERM + 1)

    v_str = verdict(perm_p)
    print(f"  chi2={chi2:.1f}, analytic p={p_val:.4f}, perm p={perm_p:.4f}")
    for ci in range(3):
        if f'cluster_{ci}' in cluster_profiles:
            top = sorted(cluster_profiles[f'cluster_{ci}'].items(), key=lambda x: -x[1])[:3]
            top_str = ', '.join(f"{c}={v:.1%}" for c, v in top)
            print(f"    Cluster {ci} (n={cluster_sizes[ci]}): {top_str}")
    print(f"  Verdict: {v_str}")

    return {
        'test': 'T8_tail_category',
        'silhouette': float(sil),
        'cluster_sizes': cluster_sizes,
        'chi2': float(chi2), 'p_analytic': float(p_val), 'p_perm': float(perm_p),
        'cluster_profiles': cluster_profiles,
        'verdict': v_str,
    }


# ============================================================
# Main
# ============================================================

def main():
    print("=" * 60)
    print("Phase 457: PARAGRAPH_TERMINATION_TRIGGER")
    print("=" * 60)
    t_start = time.time()

    paragraphs = load_data()
    results = {
        'phase_name': 'PARAGRAPH_TERMINATION_TRIGGER',
        'phase_number': 457,
        'n_paragraphs': len(paragraphs),
        'n_with_3plus_body': sum(1 for p in paragraphs if p['n_body'] >= 3),
        'bonferroni_p': BONFERRONI_P,
    }

    r1 = test_t1(paragraphs)
    r2 = test_t2(paragraphs)
    r3 = test_t3(paragraphs)
    r4 = test_t4(paragraphs)
    r5 = test_t5(paragraphs)
    r6 = test_t6(paragraphs)
    r7 = test_t7(paragraphs)
    r8 = test_t8(paragraphs)

    tests = [r1, r2, r3, r4, r5, r6, r7, r8]
    results['tests'] = tests

    scored = [r for r in tests if r.get('verdict') not in ('SKIP', 'CALIBRATION')]
    n_pass = sum(1 for r in scored if r['verdict'] == 'PASS')
    n_weak = sum(1 for r in scored if r['verdict'] == 'WEAK')
    n_fail = sum(1 for r in scored if r['verdict'] == 'FAIL')

    if n_pass >= 5:
        overall = 'TERMINATION_TRIGGERED'
    elif n_pass >= 3:
        overall = 'TERMINATION_PARTIAL'
    else:
        overall = 'TERMINATION_MEMORYLESS'

    results['summary'] = {
        'n_pass': n_pass, 'n_weak': n_weak, 'n_fail': n_fail,
        'n_skip': sum(1 for r in tests if r.get('verdict') == 'SKIP'),
        'overall_verdict': overall,
    }

    elapsed = time.time() - t_start

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    for r in tests:
        v = r.get('verdict', '?')
        test_name = r.get('test', '?')
        p = r.get('p', r.get('fisher_p', r.get('perm_p', r.get('meta_p_folio',
            r.get('f_p', r.get('p_perm', None))))))
        p_str = f"p={p:.2e}" if p is not None else "N/A"
        print(f"  {test_name:45s} {v:12s} {p_str}")
    print(f"\n  PASS={n_pass} WEAK={n_weak} FAIL={n_fail}")
    print(f"  Overall: {overall}")
    print(f"  Elapsed: {elapsed:.1f}s")

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = RESULTS_DIR / 'paragraph_termination_trigger.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, cls=NumpyEncoder)
    print(f"\n  Results saved to: {out_path}")


if __name__ == '__main__':
    main()
