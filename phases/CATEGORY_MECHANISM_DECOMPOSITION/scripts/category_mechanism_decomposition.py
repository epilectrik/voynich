#!/usr/bin/env python3
"""Phase 455: CATEGORY_MECHANISM_DECOMPOSITION

8-test battery probing THREE open questions from Phase 454 results:

Tier 1 - TRANSITION Anti-Escape Mechanism:
  T1: TRANSITION Successor Role Enrichment (EN self-loop hypothesis)
  T2: TRANSITION Sequential Persistence (clustering within lines)

Tier 2 - Category-Conditioned Forbidden Transitions:
  T3: Forbidden Transition Category Structure
  T4: Category Transition Matrix Structure (asymmetry)

Tier 3 - Paragraph-Level Category Dynamics:
  T5: Paragraph Header vs Body Category Divergence
  T6: Within-Folio Paragraph Category Independence
  T7: Category Composition Predicts AXM Self-Transition Rate
  T8: Paragraph Category Composition Predicts Mode
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

ROLES = ['AUXILIARY', 'CORE_CONTROL', 'ENERGY_OPERATOR', 'FLOW_OPERATOR',
         'FREQUENT_OPERATOR']

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

# --- 6-state macro partition (C1010) ---
MACRO_STATE_PARTITION = {
    'AXM':     {1, 2, 4, 6, 8, 15, 16, 17, 20, 21, 22, 24, 25, 26, 27, 28,
                29, 31, 32, 33, 34, 35, 36, 37, 39, 41, 43, 44, 45, 46, 47, 48, 49},
    'AXm':     {3, 5, 18, 19, 42},
    'FL_HAZ':  {7, 30},
    'FQ':      {9, 13, 14, 23},
    'CC':      {10, 11, 12},
    'FL_SAFE': {38, 40},
}
STATE_ORDER = ['AXM', 'AXm', 'FL_HAZ', 'FQ', 'CC', 'FL_SAFE']
STATE_IDX = {s: i for i, s in enumerate(STATE_ORDER)}
N_STATES = len(STATE_ORDER)

# Build class -> state lookup
CLASS_TO_STATE = {}
for state, classes in MACRO_STATE_PARTITION.items():
    for c in classes:
        CLASS_TO_STATE[c] = state


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


def cramers_v(table):
    """Cramer's V from numpy contingency table."""
    n = table.sum()
    if n == 0:
        return 0.0
    chi2 = stats.chi2_contingency(table)[0]
    k = min(table.shape) - 1
    if k == 0:
        return 0.0
    return np.sqrt(chi2 / (n * k))


def jsd(p, q):
    """Jensen-Shannon divergence between two distributions."""
    p = np.array(p, dtype=float)
    q = np.array(q, dtype=float)
    ps = p.sum()
    qs = q.sum()
    if ps == 0 or qs == 0:
        return 1.0
    p = p / ps
    q = q / qs
    m = 0.5 * (p + q)
    d = 0.0
    for i in range(len(p)):
        if p[i] > 0 and m[i] > 0:
            d += 0.5 * p[i] * log2(p[i] / m[i])
        if q[i] > 0 and m[i] > 0:
            d += 0.5 * q[i] * log2(q[i] / m[i])
    return d


def verdict(p, effect=None, bonferroni=BONFERRONI_P, min_effect=None):
    """Return PASS/FAIL/WEAK verdict."""
    if p < bonferroni:
        return 'PASS'
    elif p < 0.05:
        return 'WEAK'
    return 'FAIL'


def classify_suffix_mode(tokens_list, morph):
    """Classify a group of tokens as Mode A or Mode B using C1231 centroids."""
    if len(tokens_list) < 3:
        return None
    n = len(tokens_list)
    cats = [0, 0, 0, 0]  # terminal, connector, iterate, bare
    for tok in tokens_list:
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

    # B tokens with full metadata
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
            'line_initial': tok.line_initial,
            'line_final': tok.line_final,
        })
    print(f"  B tokens: {len(b_tokens)}")

    # Token-to-class map
    ctm_path = ROOT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
    with open(ctm_path, encoding='utf-8') as f:
        ctm = json.load(f)
    token_to_class = {t: int(c) for t, c in ctm['token_to_class'].items()}
    class_to_role = {int(k): v for k, v in ctm['class_to_role'].items()}
    print(f"  Token-to-class map: {len(token_to_class)} tokens")

    # Assign class/role/state to B tokens
    n_classed = 0
    for tok in b_tokens:
        cls = token_to_class.get(tok['word'])
        tok['icc_class'] = cls
        tok['icc_role'] = class_to_role.get(cls) if cls else None
        tok['macro_state'] = CLASS_TO_STATE.get(cls) if cls else None
        if cls is not None:
            n_classed += 1
    print(f"  B tokens with class: {n_classed} / {len(b_tokens)} ({100*n_classed/len(b_tokens):.1f}%)")

    # Forbidden transitions
    ft_path = ROOT / 'phases' / '15-20_kernel_grammar' / 'phase18a_forbidden_inventory.json'
    with open(ft_path, encoding='utf-8') as f:
        ft_data = json.load(f)
    forbidden_list = [(tr['source'], tr['target']) for tr in ft_data['transitions']]
    print(f"  Forbidden pairs: {len(forbidden_list)}")

    # Group by line for bigram extraction
    line_groups = defaultdict(list)
    for tok in b_tokens:
        line_groups[(tok['folio'], tok['line'])].append(tok)
    print(f"  Line groups: {len(line_groups)}")

    # Group by paragraph
    paragraphs = []
    current_par = []
    current_folio = None
    par_id = 0
    for tok in b_tokens:
        if tok['par_initial'] and current_par:
            paragraphs.append({
                'folio': current_folio,
                'par_id': par_id,
                'tokens': current_par,
            })
            par_id += 1
            current_par = []
        current_folio = tok['folio']
        current_par.append(tok)
    if current_par:
        paragraphs.append({
            'folio': current_folio,
            'par_id': par_id,
            'tokens': current_par,
        })
    print(f"  Paragraphs: {len(paragraphs)}")

    # Categorized count
    n_cat = sum(1 for t in b_tokens if t['category'])
    print(f"  B tokens with category: {n_cat} / {len(b_tokens)} ({100*n_cat/len(b_tokens):.1f}%)")

    print(f"  Data loaded in {time.time()-t0:.1f}s")
    return (b_tokens, mid_to_cat, morph, token_to_class, class_to_role,
            forbidden_list, line_groups, paragraphs)


# ============================================================
# T1: TRANSITION Successor Role Enrichment
# ============================================================

def test_transition_successor_role(b_tokens, line_groups):
    """Test whether TRANSITION-category sources feed into EN roles."""
    print("\n=== T1: TRANSITION Successor Role Enrichment ===")

    # Build bigrams within lines
    trans_successor_roles = Counter()
    other_successor_roles = Counter()
    en_en_trans = 0
    en_en_total = 0
    total_bigrams = 0

    for key, tokens in line_groups.items():
        for i in range(len(tokens) - 1):
            src = tokens[i]
            tgt = tokens[i + 1]
            src_cat = src['category']
            tgt_role = tgt['icc_role']
            if not src_cat or not tgt_role:
                continue
            total_bigrams += 1

            if src_cat == 'TRANSITION':
                trans_successor_roles[tgt_role] += 1
            else:
                other_successor_roles[tgt_role] += 1

            # Track EN->EN specifically
            src_role = src['icc_role']
            if src_role == 'ENERGY_OPERATOR' and tgt_role == 'ENERGY_OPERATOR':
                en_en_total += 1
                if src_cat == 'TRANSITION':
                    en_en_trans += 1

    print(f"  Total bigrams with category+role: {total_bigrams}")
    print(f"  TRANSITION-sourced: {sum(trans_successor_roles.values())}")
    print(f"  Other-sourced: {sum(other_successor_roles.values())}")

    # Build 2x5 contingency table
    contingency = np.zeros((2, len(ROLES)), dtype=float)
    for j, role in enumerate(ROLES):
        contingency[0, j] = trans_successor_roles.get(role, 0)
        contingency[1, j] = other_successor_roles.get(role, 0)

    # Print role distributions
    trans_total = contingency[0].sum()
    other_total = contingency[1].sum()
    print("\n  Successor role distribution:")
    print(f"  {'Role':22s}  TRANSITION   Other    Ratio")
    for j, role in enumerate(ROLES):
        t_frac = contingency[0, j] / trans_total if trans_total else 0
        o_frac = contingency[1, j] / other_total if other_total else 0
        ratio = t_frac / o_frac if o_frac > 0 else float('inf')
        print(f"  {role:22s}  {t_frac:8.3f}    {o_frac:8.3f}  {ratio:6.2f}x")

    # Chi-squared
    col_mask = contingency.sum(axis=0) > 0
    table_f = contingency[:, col_mask]
    if table_f.shape[1] >= 2:
        chi2, p, _, _ = stats.chi2_contingency(table_f)
        v = cramers_v(table_f)
    else:
        chi2, p, v = 0, 1, 0

    # EN->EN rate for TRANSITION vs all
    trans_en_total = sum(1 for key, tokens in line_groups.items()
                        for i in range(len(tokens) - 1)
                        if tokens[i]['category'] == 'TRANSITION'
                        and tokens[i]['icc_role'] == 'ENERGY_OPERATOR'
                        and tokens[i + 1]['icc_role'] is not None)
    trans_en_to_en = sum(1 for key, tokens in line_groups.items()
                        for i in range(len(tokens) - 1)
                        if tokens[i]['category'] == 'TRANSITION'
                        and tokens[i]['icc_role'] == 'ENERGY_OPERATOR'
                        and tokens[i + 1]['icc_role'] == 'ENERGY_OPERATOR')

    all_en_total = sum(1 for key, tokens in line_groups.items()
                       for i in range(len(tokens) - 1)
                       if tokens[i]['icc_role'] == 'ENERGY_OPERATOR'
                       and tokens[i + 1]['icc_role'] is not None)
    all_en_to_en = sum(1 for key, tokens in line_groups.items()
                       for i in range(len(tokens) - 1)
                       if tokens[i]['icc_role'] == 'ENERGY_OPERATOR'
                       and tokens[i + 1]['icc_role'] == 'ENERGY_OPERATOR')

    trans_en_en_rate = trans_en_to_en / trans_en_total if trans_en_total else 0
    all_en_en_rate = all_en_to_en / all_en_total if all_en_total else 0

    print(f"\n  EN->EN self-loop rate:")
    print(f"    TRANSITION EN sources: {trans_en_to_en}/{trans_en_total} = {trans_en_en_rate:.3f}")
    print(f"    All EN sources:        {all_en_to_en}/{all_en_total} = {all_en_en_rate:.3f}")
    if all_en_en_rate > 0:
        print(f"    Ratio: {trans_en_en_rate / all_en_en_rate:.2f}x")

    verd = verdict(p)
    print(f"\n  chi2={chi2:.1f} V={v:.3f} p={p:.6f} -> {verd}")

    return {
        'test': 'T1_transition_successor_role',
        'chi2': float(chi2),
        'p': float(p),
        'cramers_v': float(v),
        'trans_n': int(trans_total),
        'other_n': int(other_total),
        'en_en_rate_transition': float(trans_en_en_rate),
        'en_en_rate_all': float(all_en_en_rate),
        'successor_distribution': {
            'TRANSITION': {role: int(contingency[0, j]) for j, role in enumerate(ROLES)},
            'OTHER': {role: int(contingency[1, j]) for j, role in enumerate(ROLES)},
        },
        'verdict': verd,
    }


# ============================================================
# T2: TRANSITION Sequential Persistence
# ============================================================

def test_transition_persistence(b_tokens, line_groups):
    """Test whether TRANSITION tokens cluster within lines."""
    print("\n=== T2: TRANSITION Sequential Persistence ===")

    rng = np.random.RandomState(SEED)

    # Compute run lengths per category per line
    def compute_run_lengths(line_tokens):
        """Return dict: category -> list of run lengths in this line."""
        cats = [t['category'] for t in line_tokens if t['category']]
        if len(cats) < 3:
            return {}
        runs = defaultdict(list)
        current_cat = cats[0]
        current_len = 1
        for c in cats[1:]:
            if c == current_cat:
                current_len += 1
            else:
                runs[current_cat].append(current_len)
                current_cat = c
                current_len = 1
        runs[current_cat].append(current_len)
        return runs

    # Observed: mean run length per category across all lines
    all_runs = defaultdict(list)
    qualifying_lines = []
    for key, tokens in line_groups.items():
        cats = [t['category'] for t in tokens if t['category']]
        if len(cats) < 3:
            continue
        qualifying_lines.append(cats)
        runs = compute_run_lengths(tokens)
        for cat, lengths in runs.items():
            all_runs[cat].extend(lengths)

    print(f"  Qualifying lines (3+ categorized tokens): {len(qualifying_lines)}")
    obs_mean_runs = {}
    for cat in CATEGORIES:
        if all_runs[cat]:
            obs_mean_runs[cat] = np.mean(all_runs[cat])
        else:
            obs_mean_runs[cat] = 0

    print(f"\n  Observed mean run lengths:")
    for cat in CATEGORIES:
        n_runs = len(all_runs[cat])
        print(f"    {cat:15s}: {obs_mean_runs[cat]:.3f} ({n_runs} runs)")

    # Null: permute category assignments within each line
    null_means = {cat: [] for cat in CATEGORIES}
    for perm_i in range(N_PERM):
        perm_runs = defaultdict(list)
        for line_cats in qualifying_lines:
            shuffled = list(line_cats)
            rng.shuffle(shuffled)
            # Compute runs
            current = shuffled[0]
            length = 1
            for c in shuffled[1:]:
                if c == current:
                    length += 1
                else:
                    perm_runs[current].append(length)
                    current = c
                    length = 1
            perm_runs[current].append(length)

        for cat in CATEGORIES:
            if perm_runs[cat]:
                null_means[cat].append(np.mean(perm_runs[cat]))
            else:
                null_means[cat].append(0)

    # Compute z-scores and p-values
    print(f"\n  Category clustering (observed vs null):")
    results_per_cat = {}
    for cat in CATEGORIES:
        null_arr = np.array(null_means[cat])
        null_mean = null_arr.mean()
        null_std = null_arr.std()
        obs = obs_mean_runs[cat]
        if null_std > 0:
            z = (obs - null_mean) / null_std
            p_val = np.mean(null_arr >= obs)  # one-tailed: clustering
        else:
            z = 0
            p_val = 1.0
        results_per_cat[cat] = {'obs': obs, 'null_mean': null_mean, 'null_std': null_std, 'z': z, 'p': p_val}
        marker = '***' if p_val < BONFERRONI_P else '**' if p_val < 0.01 else '*' if p_val < 0.05 else ''
        print(f"    {cat:15s}: obs={obs:.3f} null={null_mean:.3f}+/-{null_std:.3f} z={z:+.2f} p={p_val:.4f} {marker}")

    # Focus on TRANSITION
    trans_result = results_per_cat.get('TRANSITION', {})
    trans_p = trans_result.get('p', 1.0)
    trans_z = trans_result.get('z', 0)

    verd = verdict(trans_p)
    print(f"\n  TRANSITION persistence: z={trans_z:+.2f} p={trans_p:.4f} -> {verd}")

    return {
        'test': 'T2_transition_persistence',
        'n_qualifying_lines': len(qualifying_lines),
        'per_category': {cat: {
            'obs_mean_run': float(r['obs']),
            'null_mean_run': float(r['null_mean']),
            'null_std': float(r['null_std']),
            'z': float(r['z']),
            'p': float(r['p']),
        } for cat, r in results_per_cat.items()},
        'transition_z': float(trans_z),
        'transition_p': float(trans_p),
        'verdict': verd,
    }


# ============================================================
# T3: Forbidden Transition Category Structure
# ============================================================

def test_forbidden_category_structure(forbidden_list, mid_to_cat, line_groups):
    """Test whether forbidden transitions are category-organized."""
    print("\n=== T3: Forbidden Transition Category Structure ===")

    # Classify forbidden transition MIDDLEs
    print("  Classifying forbidden MIDDLEs:")
    forbidden_cats = []
    for src, tgt in forbidden_list:
        src_cat = mid_to_cat.get(src) or auto_assign_category(src)
        tgt_cat = mid_to_cat.get(tgt) or auto_assign_category(tgt)
        forbidden_cats.append((src, tgt, src_cat, tgt_cat))
        print(f"    {src:8s} -> {tgt:8s}:  {str(src_cat):12s} -> {str(tgt_cat):12s}  "
              f"{'SAME' if src_cat == tgt_cat else 'CROSS' if src_cat and tgt_cat else 'UNK'}")

    # Count within-category vs cross-category
    n_same = sum(1 for _, _, sc, tc in forbidden_cats if sc and tc and sc == tc)
    n_cross = sum(1 for _, _, sc, tc in forbidden_cats if sc and tc and sc != tc)
    n_unk = sum(1 for _, _, sc, tc in forbidden_cats if not sc or not tc)
    n_classified = n_same + n_cross
    same_frac = n_same / n_classified if n_classified else 0
    print(f"\n  Within-category: {n_same}/{n_classified} ({same_frac:.1%})")
    print(f"  Cross-category:  {n_cross}/{n_classified}")
    print(f"  Unclassified:    {n_unk}")

    # Compute baseline same-category rate from all observed bigrams
    baseline_same = 0
    baseline_total = 0
    cat_pair_obs = Counter()
    for key, tokens in line_groups.items():
        for i in range(len(tokens) - 1):
            sc = tokens[i]['category']
            tc = tokens[i + 1]['category']
            if sc and tc:
                baseline_total += 1
                cat_pair_obs[(sc, tc)] += 1
                if sc == tc:
                    baseline_same += 1

    baseline_same_rate = baseline_same / baseline_total if baseline_total else 0
    print(f"\n  Baseline same-category bigram rate: {baseline_same_rate:.3f} ({baseline_same}/{baseline_total})")
    print(f"  Forbidden same-category rate:       {same_frac:.3f}")

    # Build forbidden category-pair profile vs expected from baseline
    forbidden_pair_counts = Counter()
    for _, _, sc, tc in forbidden_cats:
        if sc and tc:
            forbidden_pair_counts[(sc, tc)] += 1

    # Fisher exact / binomial test: same_frac vs baseline_same_rate
    # Using binomial: p(same >= n_same | n_classified, baseline_same_rate)
    if n_classified > 0:
        btest = stats.binomtest(n_same, n_classified, baseline_same_rate, alternative='two-sided')
        p_binom = btest.pvalue
    else:
        p_binom = 1.0
    print(f"  Binomial test (same-cat enrichment): p={p_binom:.4f}")

    # Print forbidden category pair distribution
    print(f"\n  Forbidden category pairs:")
    for (sc, tc), count in sorted(forbidden_pair_counts.items()):
        print(f"    {sc:12s} -> {tc:12s}: {count}")

    verd = verdict(p_binom)
    # With only 17 pairs, Bonferroni is strict. Also report descriptive stats.
    print(f"\n  p={p_binom:.4f} -> {verd}")
    print(f"  NOTE: Small sample (n={n_classified}). Descriptive profile may be more informative than p-value.")

    return {
        'test': 'T3_forbidden_category_structure',
        'n_forbidden': len(forbidden_list),
        'n_classified': n_classified,
        'n_same_category': n_same,
        'n_cross_category': n_cross,
        'same_category_rate': float(same_frac),
        'baseline_same_rate': float(baseline_same_rate),
        'p_binom': float(p_binom),
        'forbidden_pairs': [(s, t, sc, tc) for s, t, sc, tc in forbidden_cats],
        'verdict': verd,
    }


# ============================================================
# T4: Category Transition Matrix Structure
# ============================================================

def test_category_transition_matrix(line_groups):
    """Test whether category->category transitions are structured."""
    print("\n=== T4: Category Transition Matrix Structure ===")

    # Build 8x8 transition matrix
    cat_idx = {c: i for i, c in enumerate(CATEGORIES)}
    obs_matrix = np.zeros((8, 8), dtype=float)

    for key, tokens in line_groups.items():
        for i in range(len(tokens) - 1):
            sc = tokens[i]['category']
            tc = tokens[i + 1]['category']
            if sc and tc:
                obs_matrix[cat_idx[sc], cat_idx[tc]] += 1

    total = obs_matrix.sum()
    print(f"  Total categorized bigrams: {int(total)}")

    # Chi-squared vs independence
    row_mask = obs_matrix.sum(axis=1) > 0
    col_mask = obs_matrix.sum(axis=0) > 0
    table_f = obs_matrix[row_mask][:, col_mask]
    if table_f.shape[0] >= 2 and table_f.shape[1] >= 2:
        chi2, p, _, expected = stats.chi2_contingency(table_f)
        v = cramers_v(table_f)

        # Compute standardized residuals for full matrix
        _, _, _, expected_full = stats.chi2_contingency(obs_matrix + 1e-10)
        residuals = (obs_matrix - expected_full) / np.sqrt(expected_full + 1e-10)
    else:
        chi2, p, v = 0, 1, 0
        residuals = np.zeros_like(obs_matrix)

    print(f"  Chi2={chi2:.1f} V={v:.3f} p={p:.2e}")

    # Print transition matrix (row % form)
    print(f"\n  Category transition matrix (row %):")
    print(f"  {'SRC/TGT':15s}", end='')
    for c in CATEGORIES:
        print(f"  {c[:5]:>5s}", end='')
    print()
    for i, sc in enumerate(CATEGORIES):
        row_total = obs_matrix[i].sum()
        print(f"  {sc:15s}", end='')
        for j, tc in enumerate(CATEGORIES):
            pct = 100 * obs_matrix[i, j] / row_total if row_total else 0
            print(f"  {pct:5.1f}", end='')
        print(f"   (n={int(row_total)})")

    # Asymmetry analysis
    print(f"\n  Asymmetry (|A->B - B->A| / max):")
    asymmetries = []
    for i in range(8):
        for j in range(i + 1, 8):
            ab = obs_matrix[i, j]
            ba = obs_matrix[j, i]
            mx = max(ab, ba)
            if mx > 10:  # Only report pairs with enough data
                asym = abs(ab - ba) / mx
                asymmetries.append((CATEGORIES[i], CATEGORIES[j], ab, ba, asym))
    asymmetries.sort(key=lambda x: -x[4])
    for sc, tc, ab, ba, asym in asymmetries[:10]:
        arrow = '->' if ab > ba else '<-'
        print(f"    {sc:12s} <-> {tc:12s}: {int(ab)} vs {int(ba)} asym={asym:.2f} ({arrow})")

    # Top enriched/depleted transitions (by residual)
    print(f"\n  Top enriched transitions (std residual > 3):")
    for i in range(8):
        for j in range(8):
            if residuals[i, j] > 3.0:
                print(f"    {CATEGORIES[i]:12s} -> {CATEGORIES[j]:12s}: residual={residuals[i,j]:+.1f}")
    print(f"  Top depleted transitions (std residual < -3):")
    for i in range(8):
        for j in range(8):
            if residuals[i, j] < -3.0:
                print(f"    {CATEGORIES[i]:12s} -> {CATEGORIES[j]:12s}: residual={residuals[i,j]:+.1f}")

    verd = verdict(p)
    print(f"\n  chi2={chi2:.1f} V={v:.3f} p={p:.2e} -> {verd}")

    return {
        'test': 'T4_category_transition_matrix',
        'chi2': float(chi2),
        'p': float(p),
        'cramers_v': float(v),
        'total_bigrams': int(total),
        'transition_matrix': obs_matrix.tolist(),
        'top_asymmetries': [(sc, tc, int(ab), int(ba), float(asym))
                            for sc, tc, ab, ba, asym in asymmetries[:10]],
        'verdict': verd,
    }


# ============================================================
# T5: Paragraph Header vs Body Category Divergence
# ============================================================

def test_paragraph_header_body(paragraphs):
    """Test whether paragraph headers differ from bodies in category."""
    print("\n=== T5: Paragraph Header vs Body Category Divergence ===")

    header_cats = Counter()
    body_cats = Counter()

    for par in paragraphs:
        tokens = par['tokens']
        if len(tokens) < 2:
            continue
        # Header = first token; body = rest
        h_cat = tokens[0]['category']
        if h_cat:
            header_cats[h_cat] += 1
        for tok in tokens[1:]:
            if tok['category']:
                body_cats[tok['category']] += 1

    print(f"  Header tokens (categorized): {sum(header_cats.values())}")
    print(f"  Body tokens (categorized): {sum(body_cats.values())}")

    # Build 2x8 contingency
    contingency = np.zeros((2, len(CATEGORIES)), dtype=float)
    for j, cat in enumerate(CATEGORIES):
        contingency[0, j] = header_cats.get(cat, 0)
        contingency[1, j] = body_cats.get(cat, 0)

    # Print enrichment
    h_total = contingency[0].sum()
    b_total = contingency[1].sum()
    print(f"\n  Category  Header%   Body%   Ratio")
    for j, cat in enumerate(CATEGORIES):
        h_frac = contingency[0, j] / h_total if h_total else 0
        b_frac = contingency[1, j] / b_total if b_total else 0
        ratio = h_frac / b_frac if b_frac > 0 else float('inf')
        print(f"  {cat:15s}  {h_frac:6.3f}  {b_frac:6.3f}  {ratio:5.2f}x")

    col_mask = contingency.sum(axis=0) > 0
    table_f = contingency[:, col_mask]
    if table_f.shape[1] >= 2:
        chi2, p, _, _ = stats.chi2_contingency(table_f)
        v = cramers_v(table_f)
    else:
        chi2, p, v = 0, 1, 0

    verd = verdict(p)
    print(f"\n  chi2={chi2:.1f} V={v:.3f} p={p:.6f} -> {verd}")

    return {
        'test': 'T5_paragraph_header_body',
        'chi2': float(chi2),
        'p': float(p),
        'cramers_v': float(v),
        'n_headers': int(h_total),
        'n_body': int(b_total),
        'header_profile': {cat: int(header_cats.get(cat, 0)) for cat in CATEGORIES},
        'body_profile': {cat: int(body_cats.get(cat, 0)) for cat in CATEGORIES},
        'verdict': verd,
    }


# ============================================================
# T6: Within-Folio Paragraph Category Independence
# ============================================================

def test_paragraph_independence(paragraphs):
    """Test whether within-folio paragraphs are more category-similar than across-folio."""
    print("\n=== T6: Within-Folio Paragraph Category Independence ===")

    rng = np.random.RandomState(SEED)

    # Compute category distribution per paragraph (min 5 categorized tokens)
    MIN_TOKENS = 5
    par_profiles = []
    for par in paragraphs:
        cats = Counter(t['category'] for t in par['tokens'] if t['category'])
        if sum(cats.values()) < MIN_TOKENS:
            continue
        profile = np.array([cats.get(c, 0) for c in CATEGORIES], dtype=float)
        par_profiles.append({
            'folio': par['folio'],
            'profile': profile,
        })

    print(f"  Qualifying paragraphs (>={MIN_TOKENS} categorized tokens): {len(par_profiles)}")

    # Group by folio
    folio_pars = defaultdict(list)
    for pp in par_profiles:
        folio_pars[pp['folio']].append(pp['profile'])

    folios_with_multi = {f: profs for f, profs in folio_pars.items() if len(profs) >= 2}
    print(f"  Folios with 2+ qualifying paragraphs: {len(folios_with_multi)}")

    if len(folios_with_multi) < 5:
        print("  Insufficient data for test")
        return {
            'test': 'T6_paragraph_independence',
            'verdict': 'FAIL',
            'note': 'insufficient data',
        }

    # Compute within-folio mean JSD
    within_jsds = []
    for f, profs in folios_with_multi.items():
        for i in range(len(profs)):
            for j in range(i + 1, len(profs)):
                within_jsds.append(jsd(profs[i], profs[j]))
    obs_within = np.mean(within_jsds)

    # Compute across-folio mean JSD (sample to keep tractable)
    all_profiles = [pp['profile'] for pp in par_profiles]
    all_folios = [pp['folio'] for pp in par_profiles]
    across_jsds = []
    n_sample = min(5000, len(all_profiles) * (len(all_profiles) - 1) // 2)
    for _ in range(n_sample):
        i, j = rng.choice(len(all_profiles), 2, replace=False)
        if all_folios[i] != all_folios[j]:
            across_jsds.append(jsd(all_profiles[i], all_profiles[j]))
    obs_across = np.mean(across_jsds) if across_jsds else 0

    print(f"  Within-folio mean JSD: {obs_within:.4f} (n={len(within_jsds)} pairs)")
    print(f"  Across-folio mean JSD: {obs_across:.4f} (n={len(across_jsds)} pairs)")
    print(f"  Ratio: {obs_within / obs_across:.3f}" if obs_across > 0 else "  Ratio: N/A")

    # Permutation test: shuffle folio assignments
    null_within = []
    for perm_i in range(N_PERM):
        shuffled_folios = list(all_folios)
        rng.shuffle(shuffled_folios)

        # Regroup by shuffled folio
        perm_folio_pars = defaultdict(list)
        for idx, sf in enumerate(shuffled_folios):
            perm_folio_pars[sf].append(all_profiles[idx])

        perm_within = []
        for f, profs in perm_folio_pars.items():
            if len(profs) >= 2:
                for i in range(len(profs)):
                    for j in range(i + 1, len(profs)):
                        perm_within.append(jsd(profs[i], profs[j]))
        if perm_within:
            null_within.append(np.mean(perm_within))

    null_arr = np.array(null_within)
    null_mean = null_arr.mean()
    null_std = null_arr.std()
    # One-tailed: within < null (more similar within folio)
    p_val = np.mean(null_arr <= obs_within)

    print(f"  Null within-folio JSD: {null_mean:.4f} +/- {null_std:.4f}")
    print(f"  Observed:              {obs_within:.4f}")
    z = (obs_within - null_mean) / null_std if null_std > 0 else 0
    print(f"  z = {z:+.2f}  p = {p_val:.4f}")

    direction = "COHERENT" if obs_within < null_mean else "INDEPENDENT"
    print(f"  Direction: {direction} (within {'<' if obs_within < null_mean else '>='} null)")

    verd = verdict(p_val)
    print(f"\n  -> {verd}")

    return {
        'test': 'T6_paragraph_independence',
        'n_qualifying_paragraphs': len(par_profiles),
        'n_folios_multi': len(folios_with_multi),
        'obs_within_jsd': float(obs_within),
        'obs_across_jsd': float(obs_across),
        'null_within_mean': float(null_mean),
        'null_within_std': float(null_std),
        'z': float(z),
        'p': float(p_val),
        'direction': direction,
        'verdict': verd,
    }


# ============================================================
# T7: Category Predicts AXM Self-Transition Rate
# ============================================================

def test_category_axm_prediction(b_tokens, line_groups):
    """Test whether category composition predicts AXM self-transition rate."""
    print("\n=== T7: Category Predicts AXM Self-Transition Rate ===")

    # Compute per-folio: category composition + AXM self-transition rate
    folio_cats = defaultdict(Counter)
    folio_transitions = defaultdict(lambda: np.zeros((N_STATES, N_STATES), dtype=float))

    for tok in b_tokens:
        if tok['category']:
            folio_cats[tok['folio']][tok['category']] += 1

    for key, tokens in line_groups.items():
        folio = key[0]
        for i in range(len(tokens) - 1):
            s1 = tokens[i]['macro_state']
            s2 = tokens[i + 1]['macro_state']
            if s1 and s2:
                folio_transitions[folio][STATE_IDX[s1], STATE_IDX[s2]] += 1

    # AXM self-transition rate per folio
    axm_idx = STATE_IDX['AXM']
    folios = sorted(f for f in folio_cats if f in folio_transitions)
    print(f"  Folios with both category and transition data: {len(folios)}")

    folio_data = []
    for f in folios:
        axm_row = folio_transitions[f][axm_idx]
        axm_total = axm_row.sum()
        if axm_total < 10:
            continue
        axm_self_rate = axm_row[axm_idx] / axm_total

        cat_total = sum(folio_cats[f].values())
        cat_profile = {c: folio_cats[f].get(c, 0) / cat_total for c in CATEGORIES}

        folio_data.append({
            'folio': f,
            'axm_self_rate': axm_self_rate,
            'cat_profile': cat_profile,
        })

    print(f"  Folios with sufficient AXM data (>=10): {len(folio_data)}")

    if len(folio_data) < 10:
        print("  Insufficient data for correlation analysis")
        return {
            'test': 'T7_category_axm_prediction',
            'verdict': 'FAIL',
            'note': 'insufficient data',
        }

    # Spearman correlations
    axm_rates = np.array([d['axm_self_rate'] for d in folio_data])
    print(f"  AXM self-rate: mean={axm_rates.mean():.3f} std={axm_rates.std():.3f}")

    print(f"\n  Category fraction vs AXM self-transition:")
    print(f"  {'Category':15s}  rho      p")
    results_per_cat = {}
    n_significant = 0
    for cat in CATEGORIES:
        cat_fracs = np.array([d['cat_profile'][cat] for d in folio_data])
        rho, p = stats.spearmanr(cat_fracs, axm_rates)
        results_per_cat[cat] = {'rho': float(rho), 'p': float(p)}
        marker = '***' if p < BONFERRONI_P else '**' if p < 0.01 else '*' if p < 0.05 else ''
        print(f"  {cat:15s}  {rho:+.3f}   {p:.4f} {marker}")
        if p < BONFERRONI_P:
            n_significant += 1

    # Overall: how many survive Bonferroni?
    any_significant = n_significant > 0
    # Use best p-value for overall verdict
    best_cat = min(results_per_cat, key=lambda c: results_per_cat[c]['p'])
    best_p = results_per_cat[best_cat]['p']
    best_rho = results_per_cat[best_cat]['rho']

    verd = verdict(best_p)
    print(f"\n  Best: {best_cat} rho={best_rho:+.3f} p={best_p:.6f}")
    print(f"  Categories significant at Bonferroni: {n_significant}/8")
    print(f"  -> {verd}")

    return {
        'test': 'T7_category_axm_prediction',
        'n_folios': len(folio_data),
        'axm_self_rate_mean': float(axm_rates.mean()),
        'axm_self_rate_std': float(axm_rates.std()),
        'correlations': results_per_cat,
        'best_category': best_cat,
        'best_rho': float(best_rho),
        'best_p': float(best_p),
        'n_bonferroni_significant': n_significant,
        'verdict': verd,
    }


# ============================================================
# T8: Paragraph Category Predicts Mode
# ============================================================

def test_paragraph_category_mode(paragraphs, morph):
    """Test whether paragraph category composition predicts Mode A vs B."""
    print("\n=== T8: Paragraph Category Predicts Mode ===")

    # Classify each paragraph by mode and compute category profile
    MIN_TOKENS = 5
    mode_a_cats = Counter()
    mode_b_cats = Counter()
    n_a = 0
    n_b = 0

    for par in paragraphs:
        tokens = par['tokens']
        if len(tokens) < MIN_TOKENS:
            continue

        mode = classify_suffix_mode(tokens, morph)
        if mode is None:
            continue

        cats = Counter(t['category'] for t in tokens if t['category'])
        if sum(cats.values()) < MIN_TOKENS:
            continue

        if mode == 'A':
            n_a += 1
            for cat, count in cats.items():
                mode_a_cats[cat] += count
        else:
            n_b += 1
            for cat, count in cats.items():
                mode_b_cats[cat] += count

    print(f"  Mode A paragraphs: {n_a}")
    print(f"  Mode B paragraphs: {n_b}")

    if n_a < 5 or n_b < 5:
        print("  Insufficient paragraphs in one mode")
        return {
            'test': 'T8_paragraph_category_mode',
            'verdict': 'FAIL',
            'note': 'insufficient data',
        }

    # Build 2x8 contingency
    contingency = np.zeros((2, len(CATEGORIES)), dtype=float)
    for j, cat in enumerate(CATEGORIES):
        contingency[0, j] = mode_a_cats.get(cat, 0)
        contingency[1, j] = mode_b_cats.get(cat, 0)

    a_total = contingency[0].sum()
    b_total = contingency[1].sum()

    print(f"\n  Category   ModeA%   ModeB%   Ratio")
    for j, cat in enumerate(CATEGORIES):
        a_frac = contingency[0, j] / a_total if a_total else 0
        b_frac = contingency[1, j] / b_total if b_total else 0
        ratio = a_frac / b_frac if b_frac > 0 else float('inf')
        print(f"  {cat:15s}  {a_frac:6.3f}  {b_frac:6.3f}  {ratio:5.2f}x")

    col_mask = contingency.sum(axis=0) > 0
    table_f = contingency[:, col_mask]
    if table_f.shape[1] >= 2:
        chi2, p, _, _ = stats.chi2_contingency(table_f)
        v = cramers_v(table_f)
    else:
        chi2, p, v = 0, 1, 0

    verd = verdict(p)
    print(f"\n  chi2={chi2:.1f} V={v:.3f} p={p:.6f} -> {verd}")

    return {
        'test': 'T8_paragraph_category_mode',
        'chi2': float(chi2),
        'p': float(p),
        'cramers_v': float(v),
        'n_mode_a': n_a,
        'n_mode_b': n_b,
        'mode_a_profile': {cat: int(mode_a_cats.get(cat, 0)) for cat in CATEGORIES},
        'mode_b_profile': {cat: int(mode_b_cats.get(cat, 0)) for cat in CATEGORIES},
        'verdict': verd,
    }


# ============================================================
# Main
# ============================================================

if __name__ == '__main__':
    print("=" * 60)
    print("Phase 455: CATEGORY_MECHANISM_DECOMPOSITION")
    print("=" * 60)

    print("\n--- Loading data ---")
    (b_tokens, mid_to_cat, morph, token_to_class, class_to_role,
     forbidden_list, line_groups, paragraphs) = load_data()

    results = {
        'phase': 'CATEGORY_MECHANISM_DECOMPOSITION',
        'phase_number': 455,
        'timestamp': time.strftime('%Y-%m-%dT%H:%M:%S'),
        'bonferroni_threshold': BONFERRONI_P,
        'tests': {},
    }

    # Tier 1: TRANSITION mechanism
    t1 = test_transition_successor_role(b_tokens, line_groups)
    results['tests']['T1'] = t1

    t2 = test_transition_persistence(b_tokens, line_groups)
    results['tests']['T2'] = t2

    # Tier 2: Forbidden transitions
    t3 = test_forbidden_category_structure(forbidden_list, mid_to_cat, line_groups)
    results['tests']['T3'] = t3

    t4 = test_category_transition_matrix(line_groups)
    results['tests']['T4'] = t4

    # Tier 3: Paragraph dynamics
    t5 = test_paragraph_header_body(paragraphs)
    results['tests']['T5'] = t5

    t6 = test_paragraph_independence(paragraphs)
    results['tests']['T6'] = t6

    t7 = test_category_axm_prediction(b_tokens, line_groups)
    results['tests']['T7'] = t7

    t8 = test_paragraph_category_mode(paragraphs, morph)
    results['tests']['T8'] = t8

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    verdicts = []
    print(f"\n  {'Test':45s}  {'Verdict':8s}  {'Key Metric'}")
    print(f"  {'-'*45}  {'-'*8}  {'-'*30}")

    for tid, tdata in sorted(results['tests'].items()):
        v = tdata['verdict']
        verdicts.append(v)
        name = tdata['test']
        if 'chi2' in tdata and 'cramers_v' in tdata:
            metric = f"chi2={tdata['chi2']:.1f} V={tdata['cramers_v']:.3f} p={tdata.get('p', 1):.2e}"
        elif 'transition_z' in tdata:
            metric = f"z={tdata['transition_z']:+.2f} p={tdata['transition_p']:.4f}"
        elif 'best_rho' in tdata:
            metric = f"rho={tdata['best_rho']:+.3f} p={tdata['best_p']:.2e} ({tdata['best_category']})"
        elif 'z' in tdata:
            metric = f"z={tdata['z']:+.2f} p={tdata.get('p', 1):.4f}"
        else:
            metric = tdata.get('note', '')
        print(f"  {name:45s}  {v:8s}  {metric}")

    n_pass = verdicts.count('PASS')
    n_weak = verdicts.count('WEAK')
    n_fail = verdicts.count('FAIL')

    if n_pass >= 6:
        overall = 'CATEGORY_MECHANISM_PERVASIVE'
    elif n_pass >= 3:
        overall = 'CATEGORY_MECHANISM_CONFIRMED'
    else:
        overall = 'CATEGORY_MECHANISM_PARTIAL'

    results['summary'] = {
        'n_pass': n_pass,
        'n_weak': n_weak,
        'n_fail': n_fail,
        'overall_verdict': overall,
    }

    print(f"\n  PASS: {n_pass}  WEAK: {n_weak}  FAIL: {n_fail}")
    print(f"  Overall: {overall}")

    # Save results
    out_path = ROOT / 'phases' / 'CATEGORY_MECHANISM_DECOMPOSITION' / 'results' / 'category_mechanism_decomposition.json'
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, cls=NumpyEncoder)
    print(f"\n  Results saved to {out_path}")
