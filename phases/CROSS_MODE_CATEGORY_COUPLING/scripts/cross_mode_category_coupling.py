#!/usr/bin/env python3
"""Phase 460: CROSS_MODE_CATEGORY_COUPLING

8-test battery probing whether Mode A and Mode B lines show zig-zag
category coupling within paragraphs. C1229 established two suffix modes.
C1233 showed mode SEQUENCING is near-random. C1258 found cross-mode
vocabulary coupling (A->B rho=0.189, B->A rho=0.208). C1286 established
within-line category transition grammar. C360 says grammar is line-invariant.

This phase asks: does the 8-category system reveal structured coupling in
the A->B->A->B diagonal that was invisible to raw vocabulary measures?

Tests:
  T1: Cross-Line Category Profile Coupling by Mode-Pair Type
  T2: A Specification -> B Execution Category Prediction
  T3: B State -> A Re-Specification Prediction
  T4: Cross-Line Category Transition Grammar (Zig-Zag)
  T5: Zig-Zag Coupling vs Null (Permutation Control)
  T6: Cross-Line Hazard Avoidance in Zig-Zag
  T7: Thermal Handoff Asymmetry
  T8: Cross-Mode Category Divergence Comparison
"""

import json
import sys
import time
from pathlib import Path
from collections import Counter, defaultdict
from math import log2

import numpy as np
from scipy import stats
from scipy.spatial.distance import jensenshannon

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from scripts.voynich import Transcript, Morphology

# ============================================================
# Constants
# ============================================================

N_PERM = 1000
SEED = 42
BONFERRONI_P = 0.05 / 8  # 0.00625

CATEGORIES = ['CONTAINMENT', 'FLOW', 'MARKING', 'MONITORING',
              'OPERATION', 'STAGING', 'THERMAL', 'TRANSITION']
CAT_IDX = {c: i for i, c in enumerate(CATEGORIES)}

# --- Category assignment (from Phase 452) ---
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

# --- Suffix mode centroids (C1231) ---
MODE_A_CENTROID = np.array([0.430, 0.019, 0.086, 0.466])
MODE_B_CENTROID = np.array([0.155, 0.031, 0.072, 0.741])

TERMINAL_SUFFIXES = {'edy', 'dy', 'eey', 'ey', 'y', 'hy', 'iry', 'oly',
                     'ry', 'ky', 'ty', 'py', 'fy', 'my', 'ly', 'sy'}
CONNECTOR_SUFFIXES = {'o', 'or', 'os', 'oe'}
ITERATE_SUFFIXES = {'aiin', 'ain', 'aiiin', 'al', 'am', 'an'}

# QO PREFIXes for thermal analysis
QO_PREFIXES = {'qo', 'ok', 'ot', 'ko', 'to', 'po', 'so', 'do'}


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
    """Assign category via plurality vote over atoms."""
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
    """Build mid_to_category dict from middle_dictionary.json."""
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


def classify_suffix_mode(line_tokens, morph):
    """Classify line suffix mode as A or B using C1231 centroids."""
    if len(line_tokens) < 3:
        return None
    n = len(line_tokens)
    cats = [0, 0, 0, 0]  # terminal, connector, iterate, bare
    for tok in line_tokens:
        sfx = morph.extract(tok['word']).suffix or ''
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


def cramers_v(contingency):
    """Cramer's V from contingency table (list of lists)."""
    table = np.array(contingency, dtype=float)
    n = table.sum()
    if n == 0:
        return 0.0
    chi2 = stats.chi2_contingency(table)[0]
    k = min(table.shape) - 1
    if k == 0:
        return 0.0
    return np.sqrt(chi2 / (n * k))


def category_profile(tokens):
    """Compute 8-element category fraction vector for a list of tokens."""
    counts = Counter()
    for tok in tokens:
        if tok['category']:
            counts[tok['category']] += 1
    total = sum(counts.values())
    if total == 0:
        return None
    return np.array([counts.get(c, 0) / total for c in CATEGORIES])


def dominant_category(tokens):
    """Return the most frequent category among tokens."""
    counts = Counter()
    for tok in tokens:
        if tok['category']:
            counts[tok['category']] += 1
    if not counts:
        return None
    return counts.most_common(1)[0][0]


def thermal_state(tokens, morph):
    """Compute thermal state variables for a line (C1260 style)."""
    if not tokens:
        return None
    n = len(tokens)
    e_count = 0
    k_count = 0
    qo_count = 0
    ke_count = 0
    for tok in tokens:
        mid = tok['middle']
        pfx = tok['prefix']
        if mid and 'e' in mid:
            e_count += 1
        if mid and 'k' in mid:
            k_count += 1
        if pfx in QO_PREFIXES:
            qo_count += 1
        if mid and ('k' in mid or 'e' in mid):
            ke_count += 1
    e_frac = e_count / n
    k_frac = k_count / n
    qo_frac = qo_count / n
    ke_ratio = ke_count / n
    return {'e_frac': e_frac, 'k_frac': k_frac, 'qo_frac': qo_frac, 'ke_ratio': ke_ratio}


def verdict(p, bonferroni=BONFERRONI_P):
    """Return PASS/FAIL/WEAK verdict."""
    if p < bonferroni:
        return 'PASS'
    elif p < 0.05:
        return 'WEAK'
    return 'FAIL'


def safe_jsd(p, q):
    """Jensen-Shannon divergence, handling zeros."""
    p = np.array(p, dtype=float)
    q = np.array(q, dtype=float)
    # Add small epsilon to avoid log(0)
    eps = 1e-12
    p = p + eps
    q = q + eps
    p = p / p.sum()
    q = q / q.sum()
    return float(jensenshannon(p, q) ** 2)  # squared = JSD


# ============================================================
# Data Loading
# ============================================================

def load_data():
    """Load all data needed for the 8-test battery."""
    t0 = time.time()

    # Category map
    mid_to_cat = build_category_map()
    print(f"  Category map: {len(mid_to_cat)} MIDDLEs")

    # Transcript
    tx = Transcript()
    morph = Morphology()

    # B tokens with paragraph/line tracking
    b_tokens = []
    for tok in tx.currier_b():
        w = tok.word
        if not w.strip() or '*' in w:
            continue
        m = morph.extract(w)
        mid = m.middle or ''
        pfx = m.prefix or ''
        sfx = m.suffix or ''
        cat = mid_to_cat.get(mid)
        if not cat and mid:
            cat = auto_assign_category(mid)
        b_tokens.append({
            'word': w,
            'folio': tok.folio,
            'line': tok.line,
            'prefix': pfx,
            'middle': mid,
            'suffix': sfx,
            'category': cat,
            'section': tok.section,
            'par_initial': tok.par_initial,
            'par_final': tok.par_final,
        })
    print(f"  B tokens: {len(b_tokens)}")

    # Token-to-class map (for forbidden transitions)
    ctm_path = ROOT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
    with open(ctm_path, encoding='utf-8') as f:
        ctm = json.load(f)
    token_to_class = {t: int(c) for t, c in ctm['token_to_class'].items()}
    class_to_role = {int(k): v for k, v in ctm['class_to_role'].items()}
    print(f"  Token-to-class map: {len(token_to_class)} tokens")

    # Assign class to B tokens
    n_classed = 0
    for tok in b_tokens:
        cls = token_to_class.get(tok['word'])
        tok['icc_class'] = cls
        if cls is not None:
            n_classed += 1
    print(f"  B tokens with class: {n_classed} / {len(b_tokens)} ({100*n_classed/len(b_tokens):.1f}%)")

    # Forbidden transitions
    ft_path = ROOT / 'phases' / '15-20_kernel_grammar' / 'phase18a_forbidden_inventory.json'
    with open(ft_path, encoding='utf-8') as f:
        ft_data = json.load(f)
    forbidden_pairs = set()
    for tr in ft_data['transitions']:
        forbidden_pairs.add((tr['source'], tr['target']))
    print(f"  Forbidden pairs: {len(forbidden_pairs)}")

    # Categorized count
    n_cat = sum(1 for t in b_tokens if t['category'])
    print(f"  B tokens with category: {n_cat} / {len(b_tokens)} ({100*n_cat/len(b_tokens):.1f}%)")

    print(f"  Data loaded in {time.time()-t0:.1f}s")
    return b_tokens, mid_to_cat, morph, token_to_class, forbidden_pairs


# ============================================================
# Paragraph/Line Structure Builder
# ============================================================

def build_paragraph_lines(b_tokens, morph):
    """Build paragraph -> ordered body lines structure.

    Returns list of paragraphs, each a list of line dicts:
    [{'folio': str, 'line': int, 'tokens': [...], 'mode': 'A'|'B'|None, 'is_header': bool}, ...]

    Header lines (first line of each paragraph per C935) are included but flagged.
    """
    # Group tokens by (folio, line)
    line_groups = defaultdict(list)
    for tok in b_tokens:
        line_groups[(tok['folio'], tok['line'])].append(tok)

    # Identify paragraph boundaries from par_initial flags
    # Build ordered lines per folio
    folio_lines = defaultdict(list)
    for (folio, line), toks in sorted(line_groups.items()):
        folio_lines[folio].append({
            'folio': folio,
            'line': line,
            'tokens': toks,
            'has_par_initial': any(t['par_initial'] for t in toks),
            'has_par_final': any(t['par_final'] for t in toks),
        })

    # Build paragraphs: split at par_initial boundaries
    paragraphs = []
    for folio in sorted(folio_lines.keys()):
        lines = folio_lines[folio]
        current_para = []
        for li in lines:
            if li['has_par_initial'] and current_para:
                # Close previous paragraph
                paragraphs.append(current_para)
                current_para = []
            current_para.append(li)
        if current_para:
            paragraphs.append(current_para)

    # Now classify each line: header (first), body (rest), mode, category profile
    result = []
    for para in paragraphs:
        if len(para) < 2:
            # Need at least header + 1 body line
            continue
        para_lines = []
        for i, li in enumerate(para):
            is_header = (i == 0)
            mode = None
            if not is_header:
                mode = classify_suffix_mode(li['tokens'], morph)
            para_lines.append({
                'folio': li['folio'],
                'line': li['line'],
                'tokens': li['tokens'],
                'is_header': is_header,
                'mode': mode,
            })
        result.append(para_lines)

    return result


def get_body_line_pairs(paragraphs):
    """Extract consecutive body line pairs from paragraphs.

    Returns list of (line_N, line_N+1, mode_pair_type) tuples.
    mode_pair_type is 'AA', 'AB', 'BA', or 'BB'.
    Only includes pairs where both lines have valid modes.
    """
    pairs = []
    for para in paragraphs:
        body = [l for l in para if not l['is_header']]
        for i in range(len(body) - 1):
            l1 = body[i]
            l2 = body[i + 1]
            if l1['mode'] and l2['mode']:
                mp = l1['mode'] + l2['mode']
                pairs.append((l1, l2, mp))
    return pairs


# ============================================================
# T1: Cross-Line Category Profile Coupling by Mode-Pair Type
# ============================================================

def test_t1_profile_coupling(pairs):
    """Does category profile correlation differ by mode pair type?"""
    print("\n=== T1: Cross-Line Category Profile Coupling by Mode-Pair Type ===")

    corrs_by_type = defaultdict(list)
    for l1, l2, mp in pairs:
        p1 = category_profile(l1['tokens'])
        p2 = category_profile(l2['tokens'])
        if p1 is None or p2 is None:
            continue
        # Pearson correlation between the two 8-element profiles
        if np.std(p1) == 0 or np.std(p2) == 0:
            continue
        r, _ = stats.pearsonr(p1, p2)
        corrs_by_type[mp].append(r)

    for mp in ['AA', 'AB', 'BA', 'BB']:
        vals = corrs_by_type.get(mp, [])
        if vals:
            print(f"  {mp}: n={len(vals)}, mean_r={np.mean(vals):.4f}, median={np.median(vals):.4f}, std={np.std(vals):.4f}")
        else:
            print(f"  {mp}: n=0")

    # Kruskal-Wallis across all 4 types
    groups = [corrs_by_type.get(mp, []) for mp in ['AA', 'AB', 'BA', 'BB']]
    valid_groups = [g for g in groups if len(g) >= 2]
    if len(valid_groups) >= 2:
        kw_stat, kw_p = stats.kruskal(*valid_groups)
    else:
        kw_stat, kw_p = 0.0, 1.0
    print(f"  Kruskal-Wallis H={kw_stat:.2f} p={kw_p:.6f}")

    # Key comparison: zig-zag (AB+BA) vs same-mode (AA+BB)
    zigzag = corrs_by_type.get('AB', []) + corrs_by_type.get('BA', [])
    same = corrs_by_type.get('AA', []) + corrs_by_type.get('BB', [])
    if zigzag and same:
        mw_stat, mw_p = stats.mannwhitneyu(zigzag, same, alternative='greater')
        zigzag_mean = np.mean(zigzag)
        same_mean = np.mean(same)
        print(f"  Zig-zag mean={zigzag_mean:.4f} vs Same-mode mean={same_mean:.4f}")
        print(f"  Mann-Whitney (zigzag > same): U={mw_stat:.1f} p={mw_p:.6f}")
    else:
        mw_p = 1.0
        zigzag_mean = 0.0
        same_mean = 0.0

    verd = 'FAIL'
    if kw_p < BONFERRONI_P and zigzag_mean > same_mean:
        verd = 'PASS'
    elif kw_p < 0.05:
        verd = 'WEAK'
    print(f"  -> {verd}")

    return {
        'test': 'T1_profile_coupling',
        'verdict': verd,
        'kruskal_wallis_H': float(kw_stat),
        'kruskal_wallis_p': float(kw_p),
        'zigzag_mean_r': float(zigzag_mean),
        'same_mode_mean_r': float(same_mean),
        'mann_whitney_p': float(mw_p),
        'per_type': {
            mp: {
                'n': len(corrs_by_type.get(mp, [])),
                'mean_r': float(np.mean(corrs_by_type[mp])) if mp in corrs_by_type and corrs_by_type[mp] else None,
                'median_r': float(np.median(corrs_by_type[mp])) if mp in corrs_by_type and corrs_by_type[mp] else None,
            } for mp in ['AA', 'AB', 'BA', 'BB']
        },
    }


# ============================================================
# T2: A Specification -> B Execution Category Prediction
# ============================================================

def test_t2_a_predicts_b(pairs):
    """Does Mode A's dominant category predict the next Mode B's category?"""
    print("\n=== T2: A Specification -> B Execution Category Prediction ===")

    # Filter to AB pairs only
    ab_pairs = [(l1, l2) for l1, l2, mp in pairs if mp == 'AB']
    print(f"  AB pairs: {len(ab_pairs)}")

    if len(ab_pairs) < 20:
        print("  -> FAIL (insufficient AB pairs)")
        return {'test': 'T2_a_predicts_b', 'verdict': 'FAIL', 'reason': 'insufficient_pairs', 'n_pairs': len(ab_pairs)}

    # Build contingency: A_dominant_cat x B_dominant_cat
    joint = Counter()
    for l1, l2 in ab_pairs:
        a_dom = dominant_category(l1['tokens'])
        b_dom = dominant_category(l2['tokens'])
        if a_dom and b_dom:
            joint[(a_dom, b_dom)] += 1

    # Build 8x8 table
    table = np.zeros((8, 8), dtype=float)
    for (a_cat, b_cat), cnt in joint.items():
        if a_cat in CAT_IDX and b_cat in CAT_IDX:
            table[CAT_IDX[a_cat], CAT_IDX[b_cat]] = cnt

    # Remove empty rows/cols for chi2
    row_sums = table.sum(axis=1)
    col_sums = table.sum(axis=0)
    row_mask = row_sums > 0
    col_mask = col_sums > 0
    reduced = table[np.ix_(row_mask, col_mask)]

    if reduced.shape[0] < 2 or reduced.shape[1] < 2:
        print("  -> FAIL (degenerate contingency)")
        return {'test': 'T2_a_predicts_b', 'verdict': 'FAIL', 'reason': 'degenerate_table'}

    chi2, p_val, _, _ = stats.chi2_contingency(reduced)
    n = reduced.sum()
    k = min(reduced.shape) - 1
    v = np.sqrt(chi2 / (n * k)) if k > 0 and n > 0 else 0.0

    print(f"  Contingency: {reduced.shape[0]}x{reduced.shape[1]}, N={int(n)}")
    print(f"  Chi2={chi2:.1f} V={v:.3f} p={p_val:.6e}")

    # Permutation control: shuffle A dominant categories
    rng = np.random.default_rng(SEED)
    a_doms = [dominant_category(l1['tokens']) for l1, l2 in ab_pairs]
    b_doms = [dominant_category(l2['tokens']) for l1, l2 in ab_pairs]
    valid_mask = [(a is not None and b is not None) for a, b in zip(a_doms, b_doms)]
    a_valid = [a for a, m in zip(a_doms, valid_mask) if m]
    b_valid = [b for b, m in zip(b_doms, valid_mask) if m]

    perm_vs = []
    for _ in range(N_PERM):
        shuffled_a = list(a_valid)
        rng.shuffle(shuffled_a)
        perm_table = np.zeros((8, 8), dtype=float)
        for a_cat, b_cat in zip(shuffled_a, b_valid):
            if a_cat in CAT_IDX and b_cat in CAT_IDX:
                perm_table[CAT_IDX[a_cat], CAT_IDX[b_cat]] += 1
        rm = perm_table.sum(axis=1) > 0
        cm = perm_table.sum(axis=0) > 0
        pr = perm_table[np.ix_(rm, cm)]
        if pr.shape[0] >= 2 and pr.shape[1] >= 2:
            pc2, _, _, _ = stats.chi2_contingency(pr)
            pn = pr.sum()
            pk = min(pr.shape) - 1
            pv = np.sqrt(pc2 / (pn * pk)) if pk > 0 and pn > 0 else 0.0
            perm_vs.append(pv)

    perm_p = (sum(1 for pv in perm_vs if pv >= v) + 1) / (len(perm_vs) + 1)
    print(f"  Permutation p={perm_p:.4f} (observed V={v:.3f}, null mean={np.mean(perm_vs):.3f})")

    verd = 'FAIL'
    if p_val < BONFERRONI_P and v >= 0.05:
        verd = 'PASS'
    elif p_val < 0.05:
        verd = 'WEAK'
    print(f"  -> {verd}")

    return {
        'test': 'T2_a_predicts_b',
        'verdict': verd,
        'p_value': float(p_val),
        'chi_squared': float(chi2),
        'cramers_v': float(v),
        'n_pairs': int(n),
        'perm_p': float(perm_p),
        'perm_null_mean_v': float(np.mean(perm_vs)) if perm_vs else None,
    }


# ============================================================
# T3: B State -> A Re-Specification Prediction
# ============================================================

def test_t3_b_state_a_respec(pairs, morph):
    """Does B's thermal state predict the next A line's category profile?"""
    print("\n=== T3: B State -> A Re-Specification Prediction ===")

    # Filter to BA pairs
    ba_pairs = [(l1, l2) for l1, l2, mp in pairs if mp == 'BA']
    print(f"  BA pairs: {len(ba_pairs)}")

    if len(ba_pairs) < 20:
        print("  -> FAIL (insufficient BA pairs)")
        return {'test': 'T3_b_state_a_respec', 'verdict': 'FAIL', 'reason': 'insufficient_pairs', 'n_pairs': len(ba_pairs)}

    # For each BA pair: B line thermal state -> next A line category fractions
    b_thermal_vars = []
    a_cat_fracs = []
    for l1, l2 in ba_pairs:
        ts = thermal_state(l1['tokens'], morph)
        cp = category_profile(l2['tokens'])
        if ts is None or cp is None:
            continue
        b_thermal_vars.append(ts)
        a_cat_fracs.append(cp)

    n_valid = len(b_thermal_vars)
    print(f"  Valid BA pairs: {n_valid}")

    if n_valid < 20:
        print("  -> FAIL (insufficient valid pairs)")
        return {'test': 'T3_b_state_a_respec', 'verdict': 'FAIL', 'reason': 'insufficient_valid', 'n_valid': n_valid}

    # Correlate each thermal var with each category fraction
    thermal_keys = ['e_frac', 'k_frac', 'qo_frac', 'ke_ratio']
    target_cats = ['THERMAL', 'STAGING', 'CONTAINMENT', 'FLOW', 'MARKING']

    correlations = {}
    any_pass = False
    best_rho = 0
    best_pair = None

    for tk in thermal_keys:
        tv = [b[tk] for b in b_thermal_vars]
        for tc in target_cats:
            ci = CAT_IDX[tc]
            cv = [a[ci] for a in a_cat_fracs]
            if np.std(tv) == 0 or np.std(cv) == 0:
                rho, p = 0.0, 1.0
            else:
                rho, p = stats.spearmanr(tv, cv)
            correlations[f"{tk}_vs_{tc}"] = {'rho': float(rho), 'p': float(p)}
            if abs(rho) > abs(best_rho):
                best_rho = rho
                best_pair = f"{tk}_vs_{tc}"
            if abs(rho) > 0.10 and p < BONFERRONI_P:
                any_pass = True
            print(f"    {tk:10s} vs {tc:15s}: rho={rho:+.3f} p={p:.4f}")

    verd = 'PASS' if any_pass else 'FAIL'
    # Check for WEAK
    if not any_pass:
        for k, v in correlations.items():
            if abs(v['rho']) > 0.10 and v['p'] < 0.05:
                verd = 'WEAK'
                break
    print(f"  Best: {best_pair} rho={best_rho:+.3f}")
    print(f"  -> {verd}")

    return {
        'test': 'T3_b_state_a_respec',
        'verdict': verd,
        'n_pairs': n_valid,
        'correlations': correlations,
        'best_pair': best_pair,
        'best_rho': float(best_rho),
    }


# ============================================================
# T4: Cross-Line Category Transition Grammar (Zig-Zag)
# ============================================================

def test_t4_crossline_transition(pairs):
    """Does structured category transition grammar extend across line boundaries?"""
    print("\n=== T4: Cross-Line Category Transition Grammar (Zig-Zag) ===")

    # For each pair: last token category of line N -> first token category of line N+1
    trans_by_type = defaultdict(lambda: np.zeros((8, 8), dtype=float))
    counts_by_type = defaultdict(int)

    for l1, l2, mp in pairs:
        # Last token with category from l1
        last_cat = None
        for tok in reversed(l1['tokens']):
            if tok['category']:
                last_cat = tok['category']
                break
        # First token with category from l2
        first_cat = None
        for tok in l2['tokens']:
            if tok['category']:
                first_cat = tok['category']
                break
        if last_cat and first_cat and last_cat in CAT_IDX and first_cat in CAT_IDX:
            trans_by_type[mp][CAT_IDX[last_cat], CAT_IDX[first_cat]] += 1
            counts_by_type[mp] += 1

    results_per_type = {}
    for mp in ['AA', 'AB', 'BA', 'BB']:
        table = trans_by_type[mp]
        n = table.sum()
        print(f"\n  {mp}: N={int(n)} transitions")
        if n < 10:
            results_per_type[mp] = {'n': int(n), 'verdict': 'INSUFFICIENT'}
            continue

        # Remove empty rows/cols
        rm = table.sum(axis=1) > 0
        cm = table.sum(axis=0) > 0
        reduced = table[np.ix_(rm, cm)]
        if reduced.shape[0] < 2 or reduced.shape[1] < 2:
            results_per_type[mp] = {'n': int(n), 'verdict': 'DEGENERATE'}
            continue

        chi2, p, _, _ = stats.chi2_contingency(reduced)
        k = min(reduced.shape) - 1
        v = np.sqrt(chi2 / (reduced.sum() * k)) if k > 0 else 0.0
        verd = verdict(p)
        print(f"    Chi2={chi2:.1f} V={v:.3f} p={p:.6e} -> {verd}")
        results_per_type[mp] = {
            'n': int(n), 'chi_squared': float(chi2),
            'cramers_v': float(v), 'p_value': float(p), 'verdict': verd,
        }

    # Compare AB transition matrix to overall cross-line matrix
    all_trans = sum(trans_by_type[mp] for mp in ['AA', 'AB', 'BA', 'BB'])
    if all_trans.sum() > 0 and trans_by_type['AB'].sum() > 0:
        # Normalize to distributions (row-wise or flattened)
        all_flat = all_trans.flatten()
        ab_flat = trans_by_type['AB'].flatten()
        if all_flat.sum() > 0 and ab_flat.sum() > 0:
            jsd = safe_jsd(all_flat, ab_flat)
            print(f"\n  AB vs All cross-line JSD: {jsd:.4f}")
        else:
            jsd = None
    else:
        jsd = None

    # Overall verdict: any mode-pair shows structured cross-line transitions?
    any_pass = any(r.get('verdict') == 'PASS' for r in results_per_type.values())
    ab_pass = results_per_type.get('AB', {}).get('verdict') == 'PASS'
    ba_pass = results_per_type.get('BA', {}).get('verdict') == 'PASS'
    overall = 'PASS' if (ab_pass or ba_pass) else ('WEAK' if any_pass else 'FAIL')
    print(f"\n  Overall -> {overall}")

    return {
        'test': 'T4_crossline_transition',
        'verdict': overall,
        'per_type': results_per_type,
        'ab_vs_all_jsd': jsd,
    }


# ============================================================
# T5: Zig-Zag Coupling vs Null (Permutation Control)
# ============================================================

def test_t5_permutation_control(paragraphs, morph):
    """Is zig-zag coupling real or a paragraph-coherence artifact?"""
    print("\n=== T5: Zig-Zag Coupling vs Null (Permutation Control) ===")

    # Compute observed AB/BA profile correlations from actual mode labels
    rng = np.random.default_rng(SEED)

    # Prepare data: for each paragraph, body lines with modes and profiles
    para_data = []
    for para in paragraphs:
        body = [l for l in para if not l['is_header'] and l['mode']]
        if len(body) < 2:
            continue
        line_info = []
        for l in body:
            prof = category_profile(l['tokens'])
            if prof is not None:
                line_info.append({'mode': l['mode'], 'profile': prof})
        if len(line_info) >= 2:
            para_data.append(line_info)

    def compute_zigzag_corr(para_data_list):
        """Compute mean AB+BA profile correlation."""
        corrs = []
        for lines in para_data_list:
            for i in range(len(lines) - 1):
                mp = lines[i]['mode'] + lines[i+1]['mode']
                if mp in ('AB', 'BA'):
                    p1 = lines[i]['profile']
                    p2 = lines[i+1]['profile']
                    if np.std(p1) > 0 and np.std(p2) > 0:
                        r, _ = stats.pearsonr(p1, p2)
                        corrs.append(r)
        return np.mean(corrs) if corrs else 0.0

    observed = compute_zigzag_corr(para_data)
    print(f"  Observed zig-zag mean r: {observed:.4f}")

    # Permutation: shuffle mode labels within each paragraph
    null_corrs = []
    for perm_i in range(N_PERM):
        shuffled = []
        for lines in para_data:
            modes = [l['mode'] for l in lines]
            rng.shuffle(modes)
            shuffled_lines = [{'mode': m, 'profile': l['profile']} for m, l in zip(modes, lines)]
            shuffled.append(shuffled_lines)
        null_corrs.append(compute_zigzag_corr(shuffled))

    null_mean = np.mean(null_corrs) if null_corrs else 0.0
    null_std = np.std(null_corrs) if null_corrs else 1.0
    perm_p = (sum(1 for nc in null_corrs if nc >= observed) + 1) / (len(null_corrs) + 1)

    print(f"  Null mean={null_mean:.4f} std={null_std:.4f}")
    print(f"  Permutation p={perm_p:.4f}")
    print(f"  Z-score: {(observed - null_mean) / null_std:.2f}" if null_std > 0 else "  Z-score: N/A")

    verd = 'PASS' if perm_p < BONFERRONI_P else ('WEAK' if perm_p < 0.05 else 'FAIL')
    print(f"  -> {verd}")

    return {
        'test': 'T5_permutation_control',
        'verdict': verd,
        'observed_zigzag_r': float(observed),
        'null_mean_r': float(null_mean),
        'null_std_r': float(null_std),
        'perm_p': float(perm_p),
        'z_score': float((observed - null_mean) / null_std) if null_std > 0 else None,
        'n_paragraphs': len(para_data),
    }


# ============================================================
# T6: Cross-Line Hazard Avoidance in Zig-Zag
# ============================================================

def test_t6_crossline_hazard(pairs, forbidden_pairs):
    """Do forbidden transitions apply across line boundaries in zig-zag?"""
    print("\n=== T6: Cross-Line Hazard Avoidance in Zig-Zag ===")

    # For each pair: last token's class (line N) -> first token's class (line N+1)
    forbidden_rate_by_type = {}
    transitions_by_type = {}

    for mp_type in ['AA', 'AB', 'BA', 'BB']:
        type_pairs = [(l1, l2) for l1, l2, mp in pairs if mp == mp_type]
        n_trans = 0
        n_forbidden = 0
        for l1, l2 in type_pairs:
            # Last classed token from l1
            last_class = None
            for tok in reversed(l1['tokens']):
                if tok.get('icc_class') is not None:
                    last_class = tok['icc_class']
                    break
            # First classed token from l2
            first_class = None
            for tok in l2['tokens']:
                if tok.get('icc_class') is not None:
                    first_class = tok['icc_class']
                    break
            if last_class is not None and first_class is not None:
                n_trans += 1
                if (last_class, first_class) in forbidden_pairs:
                    n_forbidden += 1

        rate = n_forbidden / n_trans if n_trans > 0 else 0.0
        forbidden_rate_by_type[mp_type] = rate
        transitions_by_type[mp_type] = {'n_transitions': n_trans, 'n_forbidden': n_forbidden, 'rate': rate}
        print(f"  {mp_type}: {n_forbidden}/{n_trans} forbidden = {rate:.4f}")

    # Permutation test: shuffle mode pair assignments
    rng = np.random.default_rng(SEED)

    # Collect all cross-line transitions (class pairs)
    all_class_pairs = []
    all_mp_labels = []
    for l1, l2, mp in pairs:
        last_class = None
        for tok in reversed(l1['tokens']):
            if tok.get('icc_class') is not None:
                last_class = tok['icc_class']
                break
        first_class = None
        for tok in l2['tokens']:
            if tok.get('icc_class') is not None:
                first_class = tok['icc_class']
                break
        if last_class is not None and first_class is not None:
            is_forb = (last_class, first_class) in forbidden_pairs
            all_class_pairs.append(is_forb)
            all_mp_labels.append(mp)

    # Overall cross-line forbidden rate
    overall_rate = sum(all_class_pairs) / len(all_class_pairs) if all_class_pairs else 0.0
    print(f"  Overall cross-line forbidden rate: {overall_rate:.4f}")

    # Permutation: compute AB+BA forbidden rate under shuffled labels
    observed_zigzag_forb = sum(1 for f, mp in zip(all_class_pairs, all_mp_labels) if f and mp in ('AB', 'BA'))
    n_zigzag = sum(1 for mp in all_mp_labels if mp in ('AB', 'BA'))
    observed_zigzag_rate = observed_zigzag_forb / n_zigzag if n_zigzag > 0 else 0.0

    null_rates = []
    mp_arr = np.array(all_mp_labels)
    forb_arr = np.array(all_class_pairs)
    for _ in range(N_PERM):
        perm_mp = mp_arr.copy()
        rng.shuffle(perm_mp)
        zz_mask = (perm_mp == 'AB') | (perm_mp == 'BA')
        pn = zz_mask.sum()
        if pn > 0:
            null_rates.append(forb_arr[zz_mask].sum() / pn)

    perm_p = (sum(1 for nr in null_rates if nr <= observed_zigzag_rate) + 1) / (len(null_rates) + 1) if null_rates else 1.0
    null_mean = np.mean(null_rates) if null_rates else 0.0

    print(f"  Zig-zag forbidden rate: {observed_zigzag_rate:.4f} (null mean={null_mean:.4f})")
    print(f"  Permutation p (zigzag < null): {perm_p:.4f}")

    verd = 'PASS' if perm_p < BONFERRONI_P else ('WEAK' if perm_p < 0.05 else 'FAIL')
    print(f"  -> {verd}")

    return {
        'test': 'T6_crossline_hazard',
        'verdict': verd,
        'per_type': transitions_by_type,
        'overall_crossline_forbidden_rate': float(overall_rate),
        'zigzag_forbidden_rate': float(observed_zigzag_rate),
        'null_mean_rate': float(null_mean),
        'perm_p': float(perm_p),
        'n_zigzag_transitions': int(n_zigzag),
    }


# ============================================================
# T7: Thermal Handoff Asymmetry
# ============================================================

def test_t7_thermal_handoff(pairs, morph):
    """Is the A->B thermal handoff different from B->A?"""
    print("\n=== T7: Thermal Handoff Asymmetry ===")

    # AB: correlate A's qo_frac with B's THERMAL fraction
    ab_pairs_data = []
    for l1, l2, mp in pairs:
        if mp != 'AB':
            continue
        ts = thermal_state(l1['tokens'], morph)
        cp = category_profile(l2['tokens'])
        if ts and cp is not None:
            ab_pairs_data.append((ts, cp))

    # BA: correlate B's THERMAL fraction with A's qo_frac
    ba_pairs_data = []
    for l1, l2, mp in pairs:
        if mp != 'BA':
            continue
        cp = category_profile(l1['tokens'])
        ts = thermal_state(l2['tokens'], morph)
        if cp is not None and ts:
            ba_pairs_data.append((cp, ts))

    thermal_idx = CAT_IDX['THERMAL']

    # A->B: A's qo_frac -> B's THERMAL fraction
    ab_results = {}
    if len(ab_pairs_data) >= 20:
        a_qo = [ts['qo_frac'] for ts, _ in ab_pairs_data]
        b_thermal = [cp[thermal_idx] for _, cp in ab_pairs_data]
        if np.std(a_qo) > 0 and np.std(b_thermal) > 0:
            rho, p = stats.spearmanr(a_qo, b_thermal)
        else:
            rho, p = 0.0, 1.0
        ab_results = {'rho': float(rho), 'p': float(p), 'n': len(ab_pairs_data)}
        print(f"  A->B: A.qo_frac vs B.THERMAL_frac: rho={rho:+.3f} p={p:.4f} (n={len(ab_pairs_data)})")

        # Also: A's k_frac -> B's THERMAL
        a_k = [ts['k_frac'] for ts, _ in ab_pairs_data]
        if np.std(a_k) > 0 and np.std(b_thermal) > 0:
            rho2, p2 = stats.spearmanr(a_k, b_thermal)
        else:
            rho2, p2 = 0.0, 1.0
        ab_results['k_frac_rho'] = float(rho2)
        ab_results['k_frac_p'] = float(p2)
        print(f"  A->B: A.k_frac vs B.THERMAL_frac: rho={rho2:+.3f} p={p2:.4f}")
    else:
        print(f"  A->B: insufficient pairs ({len(ab_pairs_data)})")
        ab_results = {'n': len(ab_pairs_data), 'rho': None}

    # B->A: B's THERMAL fraction -> A's qo_frac
    ba_results = {}
    if len(ba_pairs_data) >= 20:
        b_thermal_ba = [cp[thermal_idx] for cp, _ in ba_pairs_data]
        a_qo_ba = [ts['qo_frac'] for _, ts in ba_pairs_data]
        if np.std(b_thermal_ba) > 0 and np.std(a_qo_ba) > 0:
            rho_ba, p_ba = stats.spearmanr(b_thermal_ba, a_qo_ba)
        else:
            rho_ba, p_ba = 0.0, 1.0
        ba_results = {'rho': float(rho_ba), 'p': float(p_ba), 'n': len(ba_pairs_data)}
        print(f"  B->A: B.THERMAL_frac vs A.qo_frac: rho={rho_ba:+.3f} p={p_ba:.4f} (n={len(ba_pairs_data)})")

        # Also: B's THERMAL fraction -> A's THERMAL fraction (category-to-category)
        # ba_pairs_data is (B_profile, A_thermal_state), but we need A's category profile
        # Rebuild with A profiles
        ba_cat_pairs = []
        for l1, l2, mp in pairs:
            if mp != 'BA':
                continue
            cp1 = category_profile(l1['tokens'])
            cp2 = category_profile(l2['tokens'])
            if cp1 is not None and cp2 is not None:
                ba_cat_pairs.append((cp1, cp2))
        if len(ba_cat_pairs) >= 20:
            b_thermal_fracs = [p1[thermal_idx] for p1, _ in ba_cat_pairs]
            a_thermal_fracs = [p2[thermal_idx] for _, p2 in ba_cat_pairs]
            if np.std(b_thermal_fracs) > 0 and np.std(a_thermal_fracs) > 0:
                rho_ba2, p_ba2 = stats.spearmanr(b_thermal_fracs, a_thermal_fracs)
            else:
                rho_ba2, p_ba2 = 0.0, 1.0
            ba_results['thermal_to_thermal_rho'] = float(rho_ba2)
            ba_results['thermal_to_thermal_p'] = float(p_ba2)
            print(f"  B->A: B.THERMAL_frac vs A.THERMAL_frac: rho={rho_ba2:+.3f} p={p_ba2:.4f}")
    else:
        print(f"  B->A: insufficient pairs ({len(ba_pairs_data)})")
        ba_results = {'n': len(ba_pairs_data), 'rho': None}

    # Asymmetry test: compare AB and BA coupling strengths
    asym = False
    ab_rho = abs(ab_results.get('rho') or 0)
    ba_rho = abs(ba_results.get('rho') or 0)
    if ab_rho > 0 or ba_rho > 0:
        ratio = max(ab_rho, ba_rho) / min(ab_rho, ba_rho) if min(ab_rho, ba_rho) > 0.001 else float('inf')
        asym = ratio > 2.0  # One direction 2x+ stronger
        print(f"  Asymmetry ratio: {ratio:.2f} ({'ASYMMETRIC' if asym else 'SYMMETRIC'})")

    # Verdict
    any_sig = False
    if ab_results.get('rho') is not None and ab_results.get('p', 1.0) < BONFERRONI_P and abs(ab_results['rho']) > 0.10:
        any_sig = True
    if ba_results.get('rho') is not None and ba_results.get('p', 1.0) < BONFERRONI_P and abs(ba_results['rho']) > 0.10:
        any_sig = True

    verd = 'PASS' if any_sig else 'FAIL'
    if not any_sig:
        # Check weak
        for res in [ab_results, ba_results]:
            if res.get('rho') is not None and res.get('p', 1.0) < 0.05 and abs(res.get('rho', 0)) > 0.10:
                verd = 'WEAK'
                break
    print(f"  -> {verd}")

    return {
        'test': 'T7_thermal_handoff',
        'verdict': verd,
        'ab_direction': ab_results,
        'ba_direction': ba_results,
        'asymmetric': asym,
    }


# ============================================================
# T8: Cross-Mode Category Divergence Comparison
# ============================================================

def test_t8_category_divergence(paragraphs):
    """Is A-B category divergence paragraph-specific or universal?"""
    print("\n=== T8: Cross-Mode Category Divergence Comparison ===")

    # Compute mode A and mode B mean category profiles (universal)
    all_a_profiles = []
    all_b_profiles = []

    para_jsds = []  # within-paragraph A-B JSD

    for para in paragraphs:
        body = [l for l in para if not l['is_header'] and l['mode']]
        a_lines = [l for l in body if l['mode'] == 'A']
        b_lines = [l for l in body if l['mode'] == 'B']

        a_profs = [category_profile(l['tokens']) for l in a_lines]
        b_profs = [category_profile(l['tokens']) for l in b_lines]
        a_profs = [p for p in a_profs if p is not None]
        b_profs = [p for p in b_profs if p is not None]

        if a_profs:
            all_a_profiles.extend(a_profs)
        if b_profs:
            all_b_profiles.extend(b_profs)

        # Within-paragraph: mean A profile vs mean B profile
        if a_profs and b_profs:
            mean_a = np.mean(a_profs, axis=0)
            mean_b = np.mean(b_profs, axis=0)
            jsd = safe_jsd(mean_a, mean_b)
            para_jsds.append(jsd)

    print(f"  Total A line profiles: {len(all_a_profiles)}")
    print(f"  Total B line profiles: {len(all_b_profiles)}")
    print(f"  Paragraphs with both modes: {len(para_jsds)}")

    if not all_a_profiles or not all_b_profiles:
        print("  -> FAIL (no profiles)")
        return {'test': 'T8_category_divergence', 'verdict': 'FAIL', 'reason': 'no_profiles'}

    # Universal A-B divergence
    global_a = np.mean(all_a_profiles, axis=0)
    global_b = np.mean(all_b_profiles, axis=0)
    global_jsd = safe_jsd(global_a, global_b)
    print(f"  Global A-B JSD: {global_jsd:.6f}")

    # Mean within-paragraph JSD
    if para_jsds:
        within_mean = np.mean(para_jsds)
        within_std = np.std(para_jsds)
        print(f"  Within-paragraph A-B JSD: mean={within_mean:.6f} std={within_std:.6f}")
    else:
        within_mean = 0.0
        within_std = 0.0

    # Cross-paragraph JSD: for each paragraph's A profile, compute JSD against
    # other paragraphs' B profiles (sample to keep tractable)
    rng = np.random.default_rng(SEED)
    cross_jsds = []
    # Get per-paragraph mean profiles
    para_a_means = []
    para_b_means = []
    for para in paragraphs:
        body = [l for l in para if not l['is_header'] and l['mode']]
        a_lines = [l for l in body if l['mode'] == 'A']
        b_lines = [l for l in body if l['mode'] == 'B']
        a_profs = [category_profile(l['tokens']) for l in a_lines]
        b_profs = [category_profile(l['tokens']) for l in b_lines]
        a_profs = [p for p in a_profs if p is not None]
        b_profs = [p for p in b_profs if p is not None]
        if a_profs:
            para_a_means.append(np.mean(a_profs, axis=0))
        if b_profs:
            para_b_means.append(np.mean(b_profs, axis=0))

    if len(para_a_means) >= 2 and len(para_b_means) >= 2:
        # Sample cross-paragraph pairs
        n_cross = min(len(para_a_means) * len(para_b_means), 5000)
        for _ in range(n_cross):
            i = rng.integers(len(para_a_means))
            j = rng.integers(len(para_b_means))
            # Exclude same-paragraph (approximate by index match)
            cross_jsds.append(safe_jsd(para_a_means[i], para_b_means[j]))

    if cross_jsds:
        cross_mean = np.mean(cross_jsds)
        cross_std = np.std(cross_jsds)
        print(f"  Cross-paragraph A-B JSD: mean={cross_mean:.6f} std={cross_std:.6f}")
    else:
        cross_mean = 0.0
        cross_std = 0.0

    # Paired test: within-paragraph < cross-paragraph?
    if para_jsds and cross_jsds and len(para_jsds) >= 5:
        # Compare within-para JSD distribution to cross-para JSD distribution
        mw_stat, mw_p = stats.mannwhitneyu(para_jsds, cross_jsds[:len(para_jsds)], alternative='less')
        print(f"  Mann-Whitney (within < cross): U={mw_stat:.1f} p={mw_p:.6f}")
    else:
        mw_p = 1.0

    verd = 'PASS' if mw_p < BONFERRONI_P else ('WEAK' if mw_p < 0.05 else 'FAIL')
    print(f"  -> {verd} (diagnostic)")

    # Show category breakdown
    print(f"\n  Category profiles:")
    print(f"  {'Category':15s} {'Mode A':>8s} {'Mode B':>8s} {'Ratio':>8s}")
    for i, cat in enumerate(CATEGORIES):
        a_val = global_a[i]
        b_val = global_b[i]
        ratio = a_val / b_val if b_val > 0 else float('inf')
        print(f"  {cat:15s} {a_val:8.3f} {b_val:8.3f} {ratio:8.2f}")

    return {
        'test': 'T8_category_divergence',
        'verdict': verd,
        'note': 'diagnostic_only',
        'global_jsd': float(global_jsd),
        'within_para_jsd_mean': float(within_mean),
        'within_para_jsd_std': float(within_std),
        'cross_para_jsd_mean': float(cross_mean),
        'cross_para_jsd_std': float(cross_std),
        'mann_whitney_p': float(mw_p),
        'n_paragraphs_both_modes': len(para_jsds),
        'global_a_profile': global_a.tolist(),
        'global_b_profile': global_b.tolist(),
    }


# ============================================================
# Main
# ============================================================

def main():
    print("Phase 460: CROSS_MODE_CATEGORY_COUPLING")
    print("=" * 60)

    # Load data
    print("\nLoading data...")
    b_tokens, mid_to_cat, morph, token_to_class, forbidden_pairs = load_data()

    # Build paragraph/line structure
    print("\nBuilding paragraph structure...")
    paragraphs = build_paragraph_lines(b_tokens, morph)
    n_body = sum(sum(1 for l in p if not l['is_header']) for p in paragraphs)
    n_with_mode = sum(sum(1 for l in p if not l['is_header'] and l['mode']) for p in paragraphs)
    print(f"  Paragraphs: {len(paragraphs)}")
    print(f"  Body lines: {n_body} (with mode: {n_with_mode})")

    # Mode distribution
    mode_counts = Counter()
    for para in paragraphs:
        for l in para:
            if not l['is_header'] and l['mode']:
                mode_counts[l['mode']] += 1
    print(f"  Mode A lines: {mode_counts['A']}, Mode B lines: {mode_counts['B']}")

    # Build pairs
    pairs = get_body_line_pairs(paragraphs)
    pair_type_counts = Counter(mp for _, _, mp in pairs)
    print(f"  Consecutive body pairs: {len(pairs)}")
    for mp in ['AA', 'AB', 'BA', 'BB']:
        print(f"    {mp}: {pair_type_counts.get(mp, 0)}")

    # Run test battery
    results = {}

    t0 = time.time()

    results['T1'] = test_t1_profile_coupling(pairs)
    results['T2'] = test_t2_a_predicts_b(pairs)
    results['T3'] = test_t3_b_state_a_respec(pairs, morph)
    results['T4'] = test_t4_crossline_transition(pairs)
    results['T5'] = test_t5_permutation_control(paragraphs, morph)
    results['T6'] = test_t6_crossline_hazard(pairs, forbidden_pairs)
    results['T7'] = test_t7_thermal_handoff(pairs, morph)
    results['T8'] = test_t8_category_divergence(paragraphs)

    elapsed = time.time() - t0
    print(f"\n{'=' * 60}")
    print(f"Tests completed in {elapsed:.1f}s")

    # Summary
    print(f"\n{'=' * 60}")
    print("SUMMARY")
    print(f"{'=' * 60}")
    print(f"{'Test':<45s} {'Verdict':<10s}")
    print("-" * 55)

    pass_count = 0
    weak_count = 0
    for tname in ['T1', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'T8']:
        r = results[tname]
        v = r['verdict']
        label = r['test']
        if v == 'PASS':
            pass_count += 1
        elif v == 'WEAK':
            weak_count += 1
        print(f"  {label:<43s} {v:<10s}")

    # Overall verdict
    print(f"\nPASS: {pass_count}/8, WEAK: {weak_count}/8, FAIL: {8-pass_count-weak_count}/8")

    if pass_count >= 5:
        overall = 'ZIGZAG_GRAMMAR_CONFIRMED'
    elif pass_count >= 3:
        overall = 'PARTIAL_ZIGZAG'
    elif pass_count >= 1:
        overall = 'WEAK_ZIGZAG'
    else:
        overall = 'LINE_INDEPENDENT'

    # Special verdicts
    t5_fail = results['T5']['verdict'] == 'FAIL'
    if t5_fail and pass_count > 0:
        overall += '_ARTIFACT_SUSPECT'

    print(f"Overall verdict: {overall}")

    # Save results
    output = {
        'phase': 'CROSS_MODE_CATEGORY_COUPLING',
        'phase_number': 460,
        'overall_verdict': overall,
        'pass_count': pass_count,
        'weak_count': weak_count,
        'fail_count': 8 - pass_count - weak_count,
        'n_paragraphs': len(paragraphs),
        'n_body_lines': n_body,
        'n_mode_classified': n_with_mode,
        'mode_a_lines': mode_counts['A'],
        'mode_b_lines': mode_counts['B'],
        'n_pairs': len(pairs),
        'pair_type_counts': dict(pair_type_counts),
        'runtime_seconds': float(elapsed),
        'tests': results,
    }

    out_path = ROOT / 'phases' / 'CROSS_MODE_CATEGORY_COUPLING' / 'results' / 'cross_mode_category_coupling.json'
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, cls=NumpyEncoder)
    print(f"\nResults saved to {out_path}")


if __name__ == '__main__':
    main()
