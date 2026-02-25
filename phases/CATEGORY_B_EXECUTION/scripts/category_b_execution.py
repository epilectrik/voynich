#!/usr/bin/env python3
"""Phase 454: CATEGORY_B_EXECUTION

8-test battery probing whether the 8-category operational system (C1250)
organizes Currier B's internal execution grammar.

Categories organize A (Phase 452, C1261-C1268) and AZC (Phase 453, C1269-C1276).
This phase tests whether they predict B behavior at token, line, and folio levels.

Tests:
  T1: THERMAL Escape Mediation (PREFIX routing analysis)
  T2: Category-Class Prediction (entropy reduction)
  T3: Mode A/B Category Differentiation
  T4: Category Hazard Proximity (HUB sub-roles)
  T5: TRANSITION Anti-Escape Mechanism
  T6: Category Section Prediction
  T7: Category Boundary Divergence (entry vs exit zones)
  T8: Kernel Calibration Check (consistency only, not discovery)
"""

import json
import sys
import time
from pathlib import Path
from collections import Counter, defaultdict
from math import log2

import numpy as np
from scipy import stats

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

# --- HUB_UNIVERSAL sub-roles (C1000) ---
HUB_SUB_ROLES = {
    'ar': 'HAZARD_SOURCE', 'dy': 'HAZARD_SOURCE', 'ey': 'HAZARD_SOURCE',
    'l': 'HAZARD_SOURCE', 'ol': 'HAZARD_SOURCE', 'or': 'HAZARD_SOURCE',
    'aiin': 'HAZARD_TARGET', 'al': 'HAZARD_TARGET', 'ee': 'HAZARD_TARGET',
    'o': 'HAZARD_TARGET', 'r': 'HAZARD_TARGET', 't': 'HAZARD_TARGET',
    'eol': 'SAFETY_BUFFER', 'k': 'SAFETY_BUFFER', 'od': 'SAFETY_BUFFER',
    'd': 'PURE_CONNECTOR', 'e': 'PURE_CONNECTOR', 'eey': 'PURE_CONNECTOR',
    'ek': 'PURE_CONNECTOR', 'eo': 'PURE_CONNECTOR', 'iin': 'PURE_CONNECTOR',
    's': 'PURE_CONNECTOR', 'y': 'PURE_CONNECTOR',
}

# --- B sections (from transcript) ---
B_SECTIONS = ['B', 'BA', 'BB', 'BS', 'P', 'S']

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


def entropy(counts):
    """Shannon entropy in bits."""
    total = sum(counts)
    if total == 0:
        return 0.0
    h = 0.0
    for c in counts:
        if c > 0:
            p = c / total
            h -= p * log2(p)
    return h


def conditional_entropy(joint_counts):
    """H(Y|X) from a dict {x: Counter(y: count)}."""
    total = sum(sum(c.values()) for c in joint_counts.values())
    if total == 0:
        return 0.0
    h = 0.0
    for x, ycounts in joint_counts.items():
        nx = sum(ycounts.values())
        if nx == 0:
            continue
        px = nx / total
        hx = entropy(list(ycounts.values()))
        h += px * hx
    return h


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


def verdict(p, effect=None, bonferroni=BONFERRONI_P, min_effect=None):
    """Return PASS/FAIL/WEAK verdict."""
    if p < bonferroni:
        return 'PASS'
    elif p < 0.05:
        return 'WEAK'
    return 'FAIL'


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


def extract_prefix(word, morph):
    """Extract PREFIX from a word."""
    m = morph.extract(word)
    return m.prefix or ''


def extract_middle(word, morph):
    """Extract MIDDLE from a word."""
    m = morph.extract(word)
    return m.middle or ''


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

    # B tokens
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
        })
    print(f"  B tokens: {len(b_tokens)}")

    # Token-to-class map
    ctm_path = ROOT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
    with open(ctm_path, encoding='utf-8') as f:
        ctm = json.load(f)
    token_to_class = {t: int(c) for t, c in ctm['token_to_class'].items()}
    class_to_role = {int(k): v for k, v in ctm['class_to_role'].items()}
    print(f"  Token-to-class map: {len(token_to_class)} tokens")

    # Assign class/role to B tokens
    n_classed = 0
    for tok in b_tokens:
        cls = token_to_class.get(tok['word'])
        tok['icc_class'] = cls
        tok['icc_role'] = class_to_role.get(cls) if cls else None
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

    # Folio sections
    folio_sections = {}
    for tok in b_tokens:
        folio_sections[tok['folio']] = tok['section']

    # Categorized count
    n_cat = sum(1 for t in b_tokens if t['category'])
    print(f"  B tokens with category: {n_cat} / {len(b_tokens)} ({100*n_cat/len(b_tokens):.1f}%)")

    print(f"  Data loaded in {time.time()-t0:.1f}s")
    return b_tokens, mid_to_cat, morph, token_to_class, class_to_role, forbidden_pairs, folio_sections


# ============================================================
# T1: THERMAL Escape Mediation
# ============================================================

def test_thermal_escape_mediation(b_tokens, mid_to_cat):
    """Formal mediation analysis: THERMAL -> qo-PREFIX -> escape."""
    print("\n=== T1: THERMAL Escape Mediation ===")

    # Step 1: Are THERMAL MIDDLEs disproportionately qo-prefixed?
    cat_prefix = defaultdict(Counter)  # category -> Counter(prefix_group)
    for tok in b_tokens:
        cat = tok['category']
        if not cat:
            continue
        pfx = tok['prefix']
        pfx_group = 'qo' if pfx.startswith('qo') else 'ch' if pfx.startswith('ch') else 'sh' if pfx.startswith('sh') else 'other'
        cat_prefix[cat][pfx_group] += 1

    # Build contingency: category x prefix_group
    pfx_groups = ['qo', 'ch', 'sh', 'other']
    contingency = []
    for cat in CATEGORIES:
        row = [cat_prefix[cat].get(g, 0) for g in pfx_groups]
        contingency.append(row)
    table = np.array(contingency, dtype=float)

    # Filter out rows/cols with all zeros
    row_mask = table.sum(axis=1) > 0
    col_mask = table.sum(axis=0) > 0
    table_f = table[row_mask][:, col_mask]

    if table_f.shape[0] >= 2 and table_f.shape[1] >= 2:
        chi2_cp, p_cp, _, _ = stats.chi2_contingency(table_f)
        v_cp = cramers_v(table_f.tolist())
    else:
        chi2_cp, p_cp, v_cp = 0, 1, 0

    # THERMAL qo rate vs other categories
    thermal_total = sum(cat_prefix.get('THERMAL', {}).values())
    thermal_qo = cat_prefix.get('THERMAL', {}).get('qo', 0)
    other_total = sum(sum(v.values()) for c, v in cat_prefix.items() if c != 'THERMAL')
    other_qo = sum(v.get('qo', 0) for c, v in cat_prefix.items() if c != 'THERMAL')

    thermal_qo_rate = thermal_qo / thermal_total if thermal_total else 0
    other_qo_rate = other_qo / other_total if other_total else 0
    print(f"  Step 1: THERMAL qo-rate={thermal_qo_rate:.3f} vs other={other_qo_rate:.3f}")
    print(f"  Category x PREFIX: chi2={chi2_cp:.1f} V={v_cp:.3f} p={p_cp:.6f}")

    # Print per-category qo rates
    for cat in CATEGORIES:
        total = sum(cat_prefix[cat].values())
        qo = cat_prefix[cat].get('qo', 0)
        print(f"    {cat:15s}: qo={qo}/{total} ({100*qo/total:.1f}%)" if total else f"    {cat:15s}: n=0")

    # Step 2: Folio-level correlation: THERMAL frac vs escape rate
    folio_cat_counts = defaultdict(Counter)
    folio_qo_counts = defaultdict(lambda: {'qo': 0, 'total': 0})
    for tok in b_tokens:
        f = tok['folio']
        folio_qo_counts[f]['total'] += 1
        if tok['prefix'].startswith('qo'):
            folio_qo_counts[f]['qo'] += 1
        if tok['category']:
            folio_cat_counts[f][tok['category']] += 1

    folios = sorted(f for f in folio_cat_counts if folio_qo_counts[f]['total'] >= 10)

    thermal_fracs = []
    escape_rates = []
    qo_fracs = []
    for f in folios:
        total_cat = sum(folio_cat_counts[f].values())
        thermal_fracs.append(folio_cat_counts[f].get('THERMAL', 0) / total_cat if total_cat else 0)
        info = folio_qo_counts[f]
        escape_rates.append(info['qo'] / info['total'])
        qo_fracs.append(info['qo'] / info['total'])

    thermal_fracs = np.array(thermal_fracs)
    escape_rates = np.array(escape_rates)
    qo_fracs = np.array(qo_fracs)

    rho_te, p_te = stats.spearmanr(thermal_fracs, escape_rates)
    print(f"  Step 2: THERMAL frac vs escape: rho={rho_te:+.3f} p={p_te:.6f} (n={len(folios)})")

    # Step 3: Mediation — partial correlation (THERMAL->escape controlling for qo frac)
    # Use rank-based partial correlation
    from scipy.stats import rankdata
    r_thermal = rankdata(thermal_fracs)
    r_escape = rankdata(escape_rates)
    r_qo = rankdata(qo_fracs)

    # Partial Spearman: regress out qo from both thermal and escape
    def partial_spearman(x, y, z):
        """Partial correlation of x,y controlling for z (rank-based)."""
        # Residualize x and y against z
        slope_xz = np.polyfit(z, x, 1)
        slope_yz = np.polyfit(z, y, 1)
        x_resid = x - np.polyval(slope_xz, z)
        y_resid = y - np.polyval(slope_yz, z)
        r, p = stats.spearmanr(x_resid, y_resid)
        return r, p

    rho_partial, p_partial = partial_spearman(r_thermal, r_escape, r_qo)
    print(f"  Step 3: Partial (control qo): rho={rho_partial:+.3f} p={p_partial:.6f}")

    mediation_collapsed = (abs(rho_partial) < 0.1 or p_partial > 0.05)
    print(f"  Mediation collapsed: {mediation_collapsed}")

    # Step 4: TRANSITION ch/sh rate
    transition_total = sum(cat_prefix.get('TRANSITION', {}).values())
    transition_chsh = cat_prefix.get('TRANSITION', {}).get('ch', 0) + cat_prefix.get('TRANSITION', {}).get('sh', 0)
    other_chsh_total = sum(v.get('ch', 0) + v.get('sh', 0) for c, v in cat_prefix.items() if c != 'TRANSITION')

    transition_chsh_rate = transition_chsh / transition_total if transition_total else 0
    other_chsh_rate = other_chsh_total / other_total if other_total else 0
    print(f"  Step 4: TRANSITION ch/sh-rate={transition_chsh_rate:.3f} vs other={other_chsh_rate:.3f}")

    p_overall = p_cp
    verd = verdict(p_overall)
    print(f"  Overall: chi2={chi2_cp:.1f} V={v_cp:.3f} p={p_cp:.6f} -> {verd}")

    return {
        'test': 'T1',
        'verdict': verd,
        'p_value': float(p_cp),
        'chi_squared_cat_prefix': float(chi2_cp),
        'cramers_v': float(v_cp),
        'thermal_qo_rate': float(thermal_qo_rate),
        'other_qo_rate': float(other_qo_rate),
        'rho_thermal_escape': float(rho_te),
        'p_thermal_escape': float(p_te),
        'rho_partial_controlling_qo': float(rho_partial),
        'p_partial': float(p_partial),
        'mediation_collapsed': bool(mediation_collapsed),
        'transition_chsh_rate': float(transition_chsh_rate),
        'other_chsh_rate': float(other_chsh_rate),
        'n_folios': len(folios),
        'per_category_qo_rate': {
            cat: {
                'qo': cat_prefix[cat].get('qo', 0),
                'total': sum(cat_prefix[cat].values()),
                'rate': cat_prefix[cat].get('qo', 0) / sum(cat_prefix[cat].values())
                        if sum(cat_prefix[cat].values()) > 0 else 0
            } for cat in CATEGORIES
        },
    }


# ============================================================
# T2: Category-Class Prediction (Entropy Reduction)
# ============================================================

def test_category_class_prediction(b_tokens):
    """Does category reduce entropy over instruction class?"""
    print("\n=== T2: Category-Class Prediction ===")

    # Only tokens with both category and class
    valid = [t for t in b_tokens if t['category'] and t['icc_class'] is not None]
    print(f"  Tokens with category + class: {len(valid)}")

    # H(CLASS)
    class_counts = Counter(t['icc_class'] for t in valid)
    h_class = entropy(list(class_counts.values()))
    print(f"  H(CLASS) = {h_class:.3f} bits")

    # H(CLASS | CATEGORY)
    cat_class = defaultdict(Counter)
    for t in valid:
        cat_class[t['category']][t['icc_class']] += 1
    h_class_given_cat = conditional_entropy(cat_class)
    print(f"  H(CLASS | CATEGORY) = {h_class_given_cat:.3f} bits")

    # H(CLASS | PREFIX)
    pfx_class = defaultdict(Counter)
    for t in valid:
        pfx_class[t['prefix']][t['icc_class']] += 1
    h_class_given_pfx = conditional_entropy(pfx_class)
    print(f"  H(CLASS | PREFIX) = {h_class_given_pfx:.3f} bits")

    # H(CLASS | CATEGORY, PREFIX)
    catpfx_class = defaultdict(Counter)
    for t in valid:
        key = (t['category'], t['prefix'])
        catpfx_class[key][t['icc_class']] += 1
    h_class_given_catpfx = conditional_entropy(catpfx_class)
    print(f"  H(CLASS | CATEGORY, PREFIX) = {h_class_given_catpfx:.3f} bits")

    # Information gain
    ig_cat = h_class - h_class_given_cat
    ig_pfx = h_class - h_class_given_pfx
    ig_catpfx = h_class - h_class_given_catpfx
    ig_cat_beyond_pfx = h_class_given_pfx - h_class_given_catpfx

    print(f"  IG(CATEGORY) = {ig_cat:.3f} bits ({100*ig_cat/h_class:.1f}%)")
    print(f"  IG(PREFIX) = {ig_pfx:.3f} bits ({100*ig_pfx/h_class:.1f}%)")
    print(f"  IG(CATEGORY+PREFIX) = {ig_catpfx:.3f} bits ({100*ig_catpfx/h_class:.1f}%)")
    print(f"  IG(CATEGORY beyond PREFIX) = {ig_cat_beyond_pfx:.3f} bits ({100*ig_cat_beyond_pfx/h_class:.1f}%)")

    # Permutation test: shuffle categories, recompute H(CLASS|CATEGORY)
    rng = np.random.RandomState(SEED)
    cats_arr = [t['category'] for t in valid]
    classes_arr = [t['icc_class'] for t in valid]
    null_igs = []
    for _ in range(N_PERM):
        perm = rng.permutation(len(cats_arr))
        perm_cat_class = defaultdict(Counter)
        for i, pi in enumerate(perm):
            perm_cat_class[cats_arr[pi]][classes_arr[i]] += 1
        h_null = conditional_entropy(perm_cat_class)
        null_igs.append(h_class - h_null)
    null_igs = np.array(null_igs)
    p_val = float(np.mean(null_igs >= ig_cat))
    if p_val == 0:
        p_val = 1.0 / (N_PERM + 1)
    d_effect = (ig_cat - np.mean(null_igs)) / np.std(null_igs) if np.std(null_igs) > 0 else 0

    verd = verdict(p_val)
    print(f"  Perm p={p_val:.6f} d={d_effect:.1f} -> {verd}")

    return {
        'test': 'T2',
        'verdict': verd,
        'p_value': p_val,
        'h_class': float(h_class),
        'h_class_given_cat': float(h_class_given_cat),
        'h_class_given_pfx': float(h_class_given_pfx),
        'h_class_given_catpfx': float(h_class_given_catpfx),
        'ig_category': float(ig_cat),
        'ig_prefix': float(ig_pfx),
        'ig_category_plus_prefix': float(ig_catpfx),
        'ig_category_beyond_prefix': float(ig_cat_beyond_pfx),
        'ig_pct_of_total': float(100 * ig_cat / h_class) if h_class > 0 else 0,
        'ig_beyond_pfx_pct': float(100 * ig_cat_beyond_pfx / h_class) if h_class > 0 else 0,
        'effect_d': float(d_effect),
        'n_tokens': len(valid),
    }


# ============================================================
# T3: Mode A/B Category Differentiation
# ============================================================

def test_mode_category(b_tokens, morph):
    """Do Mode A vs Mode B lines differ in category composition?"""
    print("\n=== T3: Mode A/B Category Differentiation ===")

    # Build line groups
    line_groups = defaultdict(list)
    for tok in b_tokens:
        line_groups[(tok['folio'], tok['line'])].append(tok)

    # Build paragraphs (group consecutive lines per folio)
    # For simplicity: classify all lines with 3+ tokens
    mode_cats = {'A': Counter(), 'B': Counter()}
    mode_line_count = {'A': 0, 'B': 0}

    for key, toks in line_groups.items():
        mode = classify_suffix_mode(toks, morph)
        if mode is None:
            continue
        mode_line_count[mode] += 1
        for tok in toks:
            if tok['category']:
                mode_cats[mode][tok['category']] += 1

    print(f"  Mode A lines: {mode_line_count['A']}, Mode B lines: {mode_line_count['B']}")

    # Contingency table: mode x category
    contingency = []
    for mode in ['A', 'B']:
        row = [mode_cats[mode].get(cat, 0) for cat in CATEGORIES]
        contingency.append(row)

    table = np.array(contingency, dtype=float)
    chi2, p_val, _, _ = stats.chi2_contingency(table)
    v = cramers_v(table.tolist())

    print(f"  Chi2={chi2:.1f} V={v:.3f} p={p_val:.6f}")

    # Per-category breakdown
    for cat in CATEGORIES:
        a_frac = mode_cats['A'].get(cat, 0) / sum(mode_cats['A'].values()) if sum(mode_cats['A'].values()) else 0
        b_frac = mode_cats['B'].get(cat, 0) / sum(mode_cats['B'].values()) if sum(mode_cats['B'].values()) else 0
        ratio = a_frac / b_frac if b_frac > 0 else float('inf')
        print(f"    {cat:15s}: A={a_frac:.3f} B={b_frac:.3f} ratio={ratio:.2f}")

    verd = verdict(p_val)
    print(f"  -> {verd}")

    return {
        'test': 'T3',
        'verdict': verd,
        'p_value': float(p_val),
        'chi_squared': float(chi2),
        'cramers_v': float(v),
        'mode_a_lines': mode_line_count['A'],
        'mode_b_lines': mode_line_count['B'],
        'mode_a_tokens': int(sum(mode_cats['A'].values())),
        'mode_b_tokens': int(sum(mode_cats['B'].values())),
        'per_category': {
            cat: {
                'mode_a_frac': mode_cats['A'].get(cat, 0) / sum(mode_cats['A'].values())
                               if sum(mode_cats['A'].values()) else 0,
                'mode_b_frac': mode_cats['B'].get(cat, 0) / sum(mode_cats['B'].values())
                               if sum(mode_cats['B'].values()) else 0,
            } for cat in CATEGORIES
        },
    }


# ============================================================
# T4: Category Hazard Proximity
# ============================================================

def test_category_hazard(b_tokens, mid_to_cat, forbidden_pairs):
    """Do categories predict hazard exposure?"""
    print("\n=== T4: Category Hazard Proximity ===")

    # Step 1: Classify HUB_UNIVERSAL MIDDLEs by category
    print("  Step 1: HUB sub-role category classification")
    hub_cat = {}
    for mid, role in HUB_SUB_ROLES.items():
        cat = mid_to_cat.get(mid)
        if not cat:
            cat = auto_assign_category(mid)
        hub_cat[mid] = {'role': role, 'category': cat or 'UNCATEGORIZED'}

    # Sub-role -> category distribution
    role_cats = defaultdict(Counter)
    for mid, info in hub_cat.items():
        role_cats[info['role']][info['category']] += 1

    for role in ['HAZARD_SOURCE', 'HAZARD_TARGET', 'SAFETY_BUFFER', 'PURE_CONNECTOR']:
        cats = role_cats[role]
        total = sum(cats.values())
        dist = ', '.join(f"{c}={n}" for c, n in sorted(cats.items(), key=lambda x: -x[1]))
        print(f"    {role}: {dist} (n={total})")

    # Step 2: Tokens in hazard-proximate positions
    # Build bigrams, classify tokens near forbidden transitions
    print("  Step 2: Hazard-proximate tokens")
    hazard_involved_words = set()
    for src, tgt in forbidden_pairs:
        hazard_involved_words.add(src)
        hazard_involved_words.add(tgt)

    # Count tokens whose MIDDLE is in the hazard set
    hazard_cat = Counter()
    safe_cat = Counter()
    for tok in b_tokens:
        if not tok['category']:
            continue
        mid = tok['middle']
        if mid in hazard_involved_words:
            hazard_cat[tok['category']] += 1
        else:
            safe_cat[tok['category']] += 1

    n_hazard = sum(hazard_cat.values())
    n_safe = sum(safe_cat.values())
    print(f"  Hazard-MIDDLE tokens: {n_hazard}, Safe-MIDDLE tokens: {n_safe}")

    # Contingency: hazard/safe x category
    contingency = []
    for group in [hazard_cat, safe_cat]:
        row = [group.get(cat, 0) for cat in CATEGORIES]
        contingency.append(row)
    table = np.array(contingency, dtype=float)

    # Filter zero columns
    col_mask = table.sum(axis=0) > 0
    table_f = table[:, col_mask]
    cats_f = [c for c, m in zip(CATEGORIES, col_mask) if m]

    if table_f.shape[1] >= 2:
        chi2_h, p_h, _, _ = stats.chi2_contingency(table_f)
        v_h = cramers_v(table_f.tolist())
    else:
        chi2_h, p_h, v_h = 0, 1, 0

    print(f"  Hazard vs Safe: chi2={chi2_h:.1f} V={v_h:.3f} p={p_h:.6f}")

    for cat in CATEGORIES:
        h_frac = hazard_cat.get(cat, 0) / n_hazard if n_hazard else 0
        s_frac = safe_cat.get(cat, 0) / n_safe if n_safe else 0
        print(f"    {cat:15s}: hazard={h_frac:.3f} safe={s_frac:.3f}")

    # Step 3: Folio-level hazard density vs category
    folio_hazard = defaultdict(lambda: {'hazard': 0, 'total': 0})
    folio_cat_frac = defaultdict(Counter)
    for tok in b_tokens:
        f = tok['folio']
        folio_hazard[f]['total'] += 1
        if tok['middle'] in hazard_involved_words:
            folio_hazard[f]['hazard'] += 1
        if tok['category']:
            folio_cat_frac[f][tok['category']] += 1

    folios = sorted(f for f in folio_hazard if folio_hazard[f]['total'] >= 10
                    and sum(folio_cat_frac[f].values()) >= 5)

    hazard_densities = np.array([folio_hazard[f]['hazard'] / folio_hazard[f]['total'] for f in folios])

    folio_correlations = {}
    for cat in CATEGORIES:
        cat_fracs = np.array([folio_cat_frac[f].get(cat, 0) / sum(folio_cat_frac[f].values())
                              if sum(folio_cat_frac[f].values()) > 0 else 0 for f in folios])
        if np.std(cat_fracs) > 0 and np.std(hazard_densities) > 0:
            rho, p = stats.spearmanr(cat_fracs, hazard_densities)
        else:
            rho, p = 0, 1
        folio_correlations[cat] = {'rho': float(rho), 'p': float(p)}
        sig = '**' if p < BONFERRONI_P else '*' if p < 0.05 else ''
        print(f"    {cat:15s}: rho={rho:+.3f} p={p:.4f} {sig}")

    verd = verdict(p_h)
    print(f"  -> {verd}")

    return {
        'test': 'T4',
        'verdict': verd,
        'p_value': float(p_h),
        'chi_squared': float(chi2_h),
        'cramers_v': float(v_h),
        'n_hazard_tokens': int(n_hazard),
        'n_safe_tokens': int(n_safe),
        'hub_category_classification': {m: info for m, info in hub_cat.items()},
        'role_category_distribution': {r: dict(c) for r, c in role_cats.items()},
        'folio_correlations': folio_correlations,
        'n_folios': len(folios),
    }


# ============================================================
# T5: TRANSITION Anti-Escape Mechanism
# ============================================================

def test_transition_anti_escape(b_tokens, mid_to_cat, forbidden_pairs):
    """Is TRANSITION anti-escape mediated by ch/sh-lane hazard participation?"""
    print("\n=== T5: TRANSITION Anti-Escape Mechanism ===")

    # Step 1: TRANSITION ch/sh rate
    cat_prefix = defaultdict(Counter)
    for tok in b_tokens:
        if not tok['category']:
            continue
        pfx = tok['prefix']
        pfx_group = 'chsh' if pfx.startswith('ch') or pfx.startswith('sh') else 'other'
        cat_prefix[tok['category']][pfx_group] += 1

    trans_total = sum(cat_prefix.get('TRANSITION', {}).values())
    trans_chsh = cat_prefix.get('TRANSITION', {}).get('chsh', 0)
    trans_chsh_rate = trans_chsh / trans_total if trans_total else 0

    non_trans_total = sum(sum(v.values()) for c, v in cat_prefix.items() if c != 'TRANSITION')
    non_trans_chsh = sum(v.get('chsh', 0) for c, v in cat_prefix.items() if c != 'TRANSITION')
    non_trans_chsh_rate = non_trans_chsh / non_trans_total if non_trans_total else 0

    print(f"  TRANSITION ch/sh rate: {trans_chsh_rate:.3f} ({trans_chsh}/{trans_total})")
    print(f"  Non-TRANSITION ch/sh rate: {non_trans_chsh_rate:.3f} ({non_trans_chsh}/{non_trans_total})")

    # Per category ch/sh rates
    for cat in CATEGORIES:
        total = sum(cat_prefix[cat].values())
        chsh = cat_prefix[cat].get('chsh', 0)
        rate = chsh / total if total else 0
        print(f"    {cat:15s}: ch/sh={rate:.3f} ({chsh}/{total})")

    # Step 2: Hazard participation by category
    hazard_mids = set()
    for src, tgt in forbidden_pairs:
        hazard_mids.add(src)
        hazard_mids.add(tgt)

    cat_hazard_rate = {}
    for cat in CATEGORIES:
        cat_toks = [t for t in b_tokens if t['category'] == cat]
        if not cat_toks:
            cat_hazard_rate[cat] = 0
            continue
        n_haz = sum(1 for t in cat_toks if t['middle'] in hazard_mids)
        cat_hazard_rate[cat] = n_haz / len(cat_toks)

    print(f"\n  Hazard MIDDLE rate by category:")
    for cat in sorted(cat_hazard_rate, key=cat_hazard_rate.get, reverse=True):
        print(f"    {cat:15s}: {cat_hazard_rate[cat]:.3f}")

    # Step 3: Folio-level partial correlation
    # TRANSITION frac vs escape, controlling for ch/sh frac
    folio_data = defaultdict(lambda: {'total': 0, 'qo': 0, 'chsh': 0, 'cat_counts': Counter()})
    for tok in b_tokens:
        f = tok['folio']
        folio_data[f]['total'] += 1
        if tok['prefix'].startswith('qo'):
            folio_data[f]['qo'] += 1
        if tok['prefix'].startswith('ch') or tok['prefix'].startswith('sh'):
            folio_data[f]['chsh'] += 1
        if tok['category']:
            folio_data[f]['cat_counts'][tok['category']] += 1

    folios = sorted(f for f in folio_data if folio_data[f]['total'] >= 10
                    and sum(folio_data[f]['cat_counts'].values()) >= 5)

    trans_fracs = np.array([
        folio_data[f]['cat_counts'].get('TRANSITION', 0) / sum(folio_data[f]['cat_counts'].values())
        if sum(folio_data[f]['cat_counts'].values()) > 0 else 0 for f in folios
    ])
    escape_rates = np.array([folio_data[f]['qo'] / folio_data[f]['total'] for f in folios])
    chsh_fracs = np.array([folio_data[f]['chsh'] / folio_data[f]['total'] for f in folios])

    rho_te, p_te = stats.spearmanr(trans_fracs, escape_rates)
    print(f"\n  TRANSITION frac vs escape: rho={rho_te:+.3f} p={p_te:.6f}")

    # Partial correlation controlling for ch/sh
    from scipy.stats import rankdata
    r_trans = rankdata(trans_fracs)
    r_escape = rankdata(escape_rates)
    r_chsh = rankdata(chsh_fracs)

    slope_xz = np.polyfit(r_chsh, r_trans, 1)
    slope_yz = np.polyfit(r_chsh, r_escape, 1)
    x_resid = r_trans - np.polyval(slope_xz, r_chsh)
    y_resid = r_escape - np.polyval(slope_yz, r_chsh)
    rho_partial, p_partial = stats.spearmanr(x_resid, y_resid)
    print(f"  Partial (control ch/sh): rho={rho_partial:+.3f} p={p_partial:.6f}")

    mediation_collapsed = (abs(rho_partial) < 0.1 or p_partial > 0.05)
    print(f"  Mediation collapsed: {mediation_collapsed}")

    # Verdict based on original correlation
    verd = verdict(p_te)
    print(f"  -> {verd}")

    return {
        'test': 'T5',
        'verdict': verd,
        'p_value': float(p_te),
        'rho_transition_escape': float(rho_te),
        'p_transition_escape': float(p_te),
        'rho_partial_controlling_chsh': float(rho_partial),
        'p_partial': float(p_partial),
        'mediation_collapsed': bool(mediation_collapsed),
        'transition_chsh_rate': float(trans_chsh_rate),
        'non_transition_chsh_rate': float(non_trans_chsh_rate),
        'hazard_rate_by_category': cat_hazard_rate,
        'n_folios': len(folios),
        'per_category_chsh_rate': {
            cat: {
                'chsh': cat_prefix[cat].get('chsh', 0),
                'total': sum(cat_prefix[cat].values()),
                'rate': cat_prefix[cat].get('chsh', 0) / sum(cat_prefix[cat].values())
                        if sum(cat_prefix[cat].values()) > 0 else 0
            } for cat in CATEGORIES
        },
    }


# ============================================================
# T6: Category Section Prediction
# ============================================================

def test_category_section(b_tokens, folio_sections):
    """Does category composition predict section membership?"""
    print("\n=== T6: Category Section Prediction ===")

    # Build folio-level category vectors
    folio_cat = defaultdict(Counter)
    for tok in b_tokens:
        if tok['category']:
            folio_cat[tok['folio']][tok['category']] += 1

    # Get section per folio
    folios_with_data = sorted(f for f in folio_cat if f in folio_sections
                              and sum(folio_cat[f].values()) >= 10)

    # Group by section
    section_folios = defaultdict(list)
    for f in folios_with_data:
        section_folios[folio_sections[f]].append(f)

    sections = sorted(s for s in section_folios if len(section_folios[s]) >= 3)
    print(f"  Sections with 3+ folios: {sections}")
    for s in sections:
        print(f"    {s}: {len(section_folios[s])} folios")

    # Aggregate category distribution per section
    section_cat = defaultdict(Counter)
    for s in sections:
        for f in section_folios[s]:
            for cat, cnt in folio_cat[f].items():
                section_cat[s][cat] += cnt

    # Contingency: section x category
    contingency = []
    for s in sections:
        row = [section_cat[s].get(cat, 0) for cat in CATEGORIES]
        contingency.append(row)
    table = np.array(contingency, dtype=float)

    col_mask = table.sum(axis=0) > 0
    table_f = table[:, col_mask]

    if table_f.shape[0] >= 2 and table_f.shape[1] >= 2:
        chi2, p_val, _, _ = stats.chi2_contingency(table_f)
        v = cramers_v(table_f.tolist())
    else:
        chi2, p_val, v = 0, 1, 0

    print(f"  Section x Category: chi2={chi2:.1f} V={v:.3f} p={p_val:.6f}")

    # Per section category profiles
    for s in sections:
        total = sum(section_cat[s].values())
        top3 = sorted(CATEGORIES, key=lambda c: section_cat[s].get(c, 0), reverse=True)[:3]
        profile = ', '.join(f"{c}={section_cat[s].get(c, 0)/total:.3f}" for c in top3)
        print(f"    {s}: {profile}")

    # Kruskal-Wallis per category across sections (folio-level)
    print(f"  KW per category (folio-level):")
    kw_results = {}
    for cat in CATEGORIES:
        groups = []
        for s in sections:
            cat_fracs = []
            for f in section_folios[s]:
                total = sum(folio_cat[f].values())
                cat_fracs.append(folio_cat[f].get(cat, 0) / total if total else 0)
            groups.append(cat_fracs)
        if len(groups) >= 2 and all(len(g) >= 1 for g in groups):
            H, p = stats.kruskal(*groups)
        else:
            H, p = 0, 1
        kw_results[cat] = {'H': float(H), 'p': float(p)}
        sig = '**' if p < BONFERRONI_P else '*' if p < 0.05 else ''
        print(f"    {cat:15s}: H={H:.1f} p={p:.4f} {sig}")

    n_sig = sum(1 for r in kw_results.values() if r['p'] < 0.05)
    n_bonf = sum(1 for r in kw_results.values() if r['p'] < BONFERRONI_P)

    verd = verdict(p_val)
    print(f"  -> {verd} ({n_sig} KW sig at 0.05, {n_bonf} at Bonferroni)")

    return {
        'test': 'T6',
        'verdict': verd,
        'p_value': float(p_val),
        'chi_squared': float(chi2),
        'cramers_v': float(v),
        'sections': sections,
        'n_folios': len(folios_with_data),
        'kruskal_wallis': kw_results,
        'n_kw_sig': n_sig,
        'n_kw_bonferroni': n_bonf,
    }


# ============================================================
# T7: Category Boundary Divergence
# ============================================================

def test_category_boundary(b_tokens):
    """Do categories differentiate entry-zone vs exit-zone tokens?"""
    print("\n=== T7: Category Boundary Divergence ===")

    # Group tokens by line
    line_groups = defaultdict(list)
    for i, tok in enumerate(b_tokens):
        line_groups[(tok['folio'], tok['line'])].append(tok)

    # Classify tokens as entry (positions 1-2) or exit (last 2)
    entry_cats = Counter()
    exit_cats = Counter()
    interior_cats = Counter()

    for key, toks in line_groups.items():
        n = len(toks)
        if n < 5:  # need enough tokens for meaningful entry/exit
            continue
        for i, tok in enumerate(toks):
            if not tok['category']:
                continue
            if i < 2:
                entry_cats[tok['category']] += 1
            elif i >= n - 2:
                exit_cats[tok['category']] += 1
            else:
                interior_cats[tok['category']] += 1

    n_entry = sum(entry_cats.values())
    n_exit = sum(exit_cats.values())
    n_interior = sum(interior_cats.values())
    print(f"  Entry tokens: {n_entry}, Exit tokens: {n_exit}, Interior: {n_interior}")

    # Contingency: position_zone x category
    contingency = []
    for zone in [entry_cats, exit_cats, interior_cats]:
        row = [zone.get(cat, 0) for cat in CATEGORIES]
        contingency.append(row)
    table = np.array(contingency, dtype=float)

    col_mask = table.sum(axis=0) > 0
    table_f = table[:, col_mask]

    if table_f.shape[0] >= 2 and table_f.shape[1] >= 2:
        chi2, p_val, _, _ = stats.chi2_contingency(table_f)
        v = cramers_v(table_f.tolist())
    else:
        chi2, p_val, v = 0, 1, 0

    print(f"  Entry vs Exit vs Interior: chi2={chi2:.1f} V={v:.3f} p={p_val:.6f}")

    # Entry vs exit only
    ee_contingency = [[entry_cats.get(cat, 0) for cat in CATEGORIES],
                      [exit_cats.get(cat, 0) for cat in CATEGORIES]]
    ee_table = np.array(ee_contingency, dtype=float)
    ee_col_mask = ee_table.sum(axis=0) > 0
    ee_f = ee_table[:, ee_col_mask]
    if ee_f.shape[1] >= 2:
        chi2_ee, p_ee, _, _ = stats.chi2_contingency(ee_f)
        v_ee = cramers_v(ee_f.tolist())
    else:
        chi2_ee, p_ee, v_ee = 0, 1, 0

    print(f"  Entry vs Exit only: chi2={chi2_ee:.1f} V={v_ee:.3f} p={p_ee:.6f}")

    # Per-category entry vs exit
    for cat in CATEGORIES:
        e_frac = entry_cats.get(cat, 0) / n_entry if n_entry else 0
        x_frac = exit_cats.get(cat, 0) / n_exit if n_exit else 0
        i_frac = interior_cats.get(cat, 0) / n_interior if n_interior else 0
        print(f"    {cat:15s}: entry={e_frac:.3f} exit={x_frac:.3f} interior={i_frac:.3f}")

    verd = verdict(p_val)
    print(f"  -> {verd}")

    return {
        'test': 'T7',
        'verdict': verd,
        'p_value': float(p_val),
        'chi_squared_3way': float(chi2),
        'cramers_v_3way': float(v),
        'chi_squared_entry_exit': float(chi2_ee),
        'p_entry_exit': float(p_ee),
        'cramers_v_entry_exit': float(v_ee),
        'n_entry': int(n_entry),
        'n_exit': int(n_exit),
        'n_interior': int(n_interior),
        'per_category': {
            cat: {
                'entry': entry_cats.get(cat, 0) / n_entry if n_entry else 0,
                'exit': exit_cats.get(cat, 0) / n_exit if n_exit else 0,
                'interior': interior_cats.get(cat, 0) / n_interior if n_interior else 0,
            } for cat in CATEGORIES
        },
    }


# ============================================================
# T8: Kernel Calibration Check (CALIBRATION ONLY)
# ============================================================

def test_kernel_calibration(b_tokens):
    """Do categories predict kernel usage? (Expected yes -- calibration only.)"""
    print("\n=== T8: Kernel Calibration Check (CALIBRATION, not discovery) ===")

    # Per-folio: kernel fracs and category fracs
    folio_data = defaultdict(lambda: {'k': 0, 'h': 0, 'e': 0, 'total': 0, 'cat_counts': Counter()})
    for tok in b_tokens:
        f = tok['folio']
        mid = tok['middle']
        folio_data[f]['total'] += 1
        if mid == 'k':
            folio_data[f]['k'] += 1
        elif mid == 'h' or mid == 'he':
            folio_data[f]['h'] += 1
        elif mid == 'e' or mid == 'ee':
            folio_data[f]['e'] += 1
        if tok['category']:
            folio_data[f]['cat_counts'][tok['category']] += 1

    folios = sorted(f for f in folio_data if folio_data[f]['total'] >= 20
                    and sum(folio_data[f]['cat_counts'].values()) >= 10)

    # Build arrays
    k_fracs = np.array([folio_data[f]['k'] / folio_data[f]['total'] for f in folios])
    h_fracs = np.array([folio_data[f]['h'] / folio_data[f]['total'] for f in folios])
    e_fracs = np.array([folio_data[f]['e'] / folio_data[f]['total'] for f in folios])

    correlations = {}
    print(f"  Category vs kernel (folio-level, n={len(folios)}):")
    for cat in CATEGORIES:
        cat_fracs = np.array([
            folio_data[f]['cat_counts'].get(cat, 0) / sum(folio_data[f]['cat_counts'].values())
            if sum(folio_data[f]['cat_counts'].values()) > 0 else 0 for f in folios
        ])
        rho_k, p_k = stats.spearmanr(cat_fracs, k_fracs) if np.std(cat_fracs) > 0 else (0, 1)
        rho_h, p_h = stats.spearmanr(cat_fracs, h_fracs) if np.std(cat_fracs) > 0 else (0, 1)
        rho_e, p_e = stats.spearmanr(cat_fracs, e_fracs) if np.std(cat_fracs) > 0 else (0, 1)
        correlations[cat] = {
            'k': {'rho': float(rho_k), 'p': float(p_k)},
            'h': {'rho': float(rho_h), 'p': float(p_h)},
            'e': {'rho': float(rho_e), 'p': float(p_e)},
        }
        print(f"    {cat:15s}: k={rho_k:+.3f} h={rho_h:+.3f} e={rho_e:+.3f}")

    # Count significant correlations
    n_sig = sum(1 for cat in correlations
                for kernel in ['k', 'h', 'e']
                if correlations[cat][kernel]['p'] < 0.05)

    print(f"  {n_sig}/24 correlations at p<0.05")
    print(f"  NOTE: This is a CALIBRATION check. Categories were partly defined by kernel profiles.")
    print(f"  -> CALIBRATION (not scored)")

    return {
        'test': 'T8',
        'verdict': 'CALIBRATION',
        'note': 'Not scored -- circularity risk (C1250 includes kernel features)',
        'n_sig': n_sig,
        'n_folios': len(folios),
        'correlations': correlations,
    }


# ============================================================
# Main
# ============================================================

def main():
    t0 = time.time()
    print("=" * 60)
    print("Phase 454: CATEGORY_B_EXECUTION")
    print("8-test battery: category system vs B execution grammar")
    print("=" * 60)

    print("\n--- Loading data ---")
    b_tokens, mid_to_cat, morph, token_to_class, class_to_role, forbidden_pairs, folio_sections = load_data()

    results = {
        'phase': 'CATEGORY_B_EXECUTION',
        'phase_number': 454,
        'n_perm': N_PERM,
        'bonferroni_p': BONFERRONI_P,
        'seed': SEED,
        'data_summary': {
            'n_b_tokens': len(b_tokens),
            'n_with_category': sum(1 for t in b_tokens if t['category']),
            'n_with_class': sum(1 for t in b_tokens if t['icc_class'] is not None),
            'n_with_both': sum(1 for t in b_tokens if t['category'] and t['icc_class'] is not None),
            'n_middles_with_category': len(mid_to_cat),
        },
        'tests': {},
    }

    # Run tests
    results['tests']['T1'] = test_thermal_escape_mediation(b_tokens, mid_to_cat)
    results['tests']['T2'] = test_category_class_prediction(b_tokens)
    results['tests']['T3'] = test_mode_category(b_tokens, morph)
    results['tests']['T4'] = test_category_hazard(b_tokens, mid_to_cat, forbidden_pairs)
    results['tests']['T5'] = test_transition_anti_escape(b_tokens, mid_to_cat, forbidden_pairs)
    results['tests']['T6'] = test_category_section(b_tokens, folio_sections)
    results['tests']['T7'] = test_category_boundary(b_tokens)
    results['tests']['T8'] = test_kernel_calibration(b_tokens)

    # Summary (exclude T8 calibration from scoring)
    scored = {k: v for k, v in results['tests'].items() if k != 'T8'}
    n_pass = sum(1 for v in scored.values() if v['verdict'] == 'PASS')
    n_weak = sum(1 for v in scored.values() if v['verdict'] == 'WEAK')
    n_fail = sum(1 for v in scored.values() if v['verdict'] == 'FAIL')

    if n_pass >= 5:
        overall = 'CATEGORY_EXECUTES'
    elif n_pass >= 3:
        overall = 'PARTIAL_EXECUTION'
    else:
        overall = 'CATEGORY_ORTHOGONAL'

    results['summary'] = {
        'pass': n_pass,
        'weak': n_weak,
        'fail': n_fail,
        'calibration': 1,
        'overall_verdict': overall,
    }
    results['runtime_seconds'] = round(time.time() - t0, 1)

    # Summary table
    print("\n" + "=" * 60)
    print("SUMMARY TABLE")
    print("=" * 60)
    print(f"{'Test':7s}{'Verdict':11s}{'p-value':13s}{'Effect':10s}")
    print("-" * 40)
    for tname in ['T1', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'T8']:
        t = results['tests'][tname]
        v = t['verdict']
        p = t.get('p_value', '-')
        eff = t.get('cramers_v', t.get('ig_category', t.get('effect_d', '-')))
        p_str = f"{p:.6f}" if isinstance(p, float) else str(p)
        eff_str = f"{eff:.3f}" if isinstance(eff, float) else str(eff)
        print(f"{tname:7s}{v:11s}{p_str:13s}{eff_str:10s}")

    print(f"\nPASS: {n_pass}, WEAK: {n_weak}, FAIL: {n_fail}, CALIBRATION: 1")
    print(f"OVERALL: {overall}")
    print(f"Runtime: {results['runtime_seconds']}s")

    # Save
    out_path = ROOT / 'phases' / 'CATEGORY_B_EXECUTION' / 'results' / 'category_b_execution.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, cls=NumpyEncoder)
    print(f"\nResults saved to {out_path}")


if __name__ == '__main__':
    main()
