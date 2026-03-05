"""
Phase 516: Cross-Slot Interaction Grammar
==========================================

Tests how PREFIX, MIDDLE, and SUFFIX constrain each other within a token.
Each slot has been independently decomposed:
  - PREFIX = modifier + base (C1218-C1219)
  - MIDDLE = HEAD + MOD* + TERM (C1393-C1394)
  - SUFFIX = HEAD + TERM with 16-atom subset (C1408-C1410)

This phase tests cross-slot dependencies: what does each slot predict about the others?

Tests T1-T9 (see REPORT.md for details).

Output: phases/CROSS_SLOT_INTERACTION/results/cross_slot_interaction.json
"""

import sys
import os
import io
import json
import math
from pathlib import Path
from collections import Counter, defaultdict
from itertools import combinations

import numpy as np
from scipy.stats import chi2_contingency, entropy as sp_entropy

# Force UTF-8 output on Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.voynich import Transcript, Morphology, CategoryClassifier

RESULTS_DIR = Path(__file__).resolve().parents[1] / 'results'
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================
# ATOM AND SLOT DEFINITIONS (from C1393, C1394, C1408)
# ============================================================

# MIDDLE atom roles (C1393)
MID_HEAD = {'a', 'e', 'o'}
MID_MOD = {'p', 'c', 'i', 'f', 'd', 's'}
MID_TERM = {'l', 'r', 'h', 'y', 'm', 'n'}
MID_FREE = {'k', 't'}
MID_HEAD_SET = MID_HEAD | MID_FREE | {'e'}
MID_TERM_SET = MID_TERM | MID_FREE
MID_EXTENSIBLE = {'e', 'i'}

# Suffix atom inventory (C1408) - 16-atom subset
SUF_HEAD = {'a', 'e', 'o'}
SUF_MOD = {'d', 's', 'i'}   # ii also but we handle extensibility
SUF_TERM = {'y', 'l', 'r', 'n', 'm', 'h'}
SUF_ABSENT = {'k', 't', 'p', 'f', 'c'}

# Mode A/B partition (C1410)
MODE_A_ATOMS = {'d', 'e', 'ee', 'h', 'y'}
MODE_B_ATOMS = {'a', 'i', 'ii', 'l', 'm', 'n', 'o', 'r', 's'}

# PREFIX base/modifier decomposition (C1218)
# Modifier chars at POS-0 (96-100% initial): q, d, f, p, y, s
# Base chars at POS-1+ (dedicated): h, e
# Dual-role chars that can be either: o, k, l, t, c, a, r
PREFIX_MODIFIERS = {'q', 'd', 'f', 'p', 'y', 's'}
PREFIX_BASES_DEDICATED = {'h', 'e'}

# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def atomize_middle(middle):
    """Split MIDDLE into individual atoms, respecting extensibility."""
    atoms = []
    i = 0
    while i < len(middle):
        ch = middle[i]
        if ch in MID_EXTENSIBLE:
            run = ch
            while i + 1 < len(middle) and middle[i + 1] == ch:
                run += ch
                i += 1
            atoms.append(run)
        else:
            atoms.append(ch)
        i += 1
    return atoms


def decompose_middle(middle):
    """Decompose MIDDLE into (head, mod_stack, term). Returns base chars."""
    atoms = atomize_middle(middle)
    if not atoms:
        return None, [], None
    if len(atoms) == 1:
        return atoms[0], [], None

    head = None
    head_base = atoms[0][0]
    if head_base in MID_HEAD_SET or head_base in MID_FREE:
        head = atoms[0]
    else:
        return None, atoms, None

    term = None
    if len(atoms) >= 2:
        term_base = atoms[-1][0]
        if term_base in MID_TERM_SET:
            term = atoms[-1]

    if term is not None:
        mod_stack = atoms[1:-1]
    else:
        mod_stack = atoms[1:]

    return head, mod_stack, term


def decompose_suffix(suffix):
    """Decompose suffix into atoms using same approach."""
    if not suffix:
        return []
    atoms = []
    i = 0
    while i < len(suffix):
        ch = suffix[i]
        if ch in MID_EXTENSIBLE:
            run = ch
            while i + 1 < len(suffix) and suffix[i + 1] == ch:
                run += ch
                i += 1
            atoms.append(run)
        else:
            atoms.append(ch)
        i += 1
    return atoms


def get_suffix_head(suffix):
    """Get first atom of suffix (HEAD if applicable)."""
    atoms = decompose_suffix(suffix)
    if not atoms:
        return None
    base = atoms[0][0]
    if base in SUF_HEAD:
        return atoms[0]
    return None


def get_suffix_term(suffix):
    """Get last atom of suffix (TERM if applicable)."""
    atoms = decompose_suffix(suffix)
    if not atoms:
        return None
    return atoms[-1]


def get_prefix_base_modifier(prefix):
    """Decompose PREFIX into (modifier, base) per C1218.

    Base = last character (the operational domain selector).
    Modifier = everything before the base (if present).
    """
    if not prefix or len(prefix) == 0:
        return None, None
    if len(prefix) == 1:
        return None, prefix
    # Last char is the base
    base = prefix[-1]
    modifier = prefix[:-1] if len(prefix) > 1 else None
    return modifier, base


def cramers_v(contingency_table):
    """Compute Cramér's V from a contingency table (2D numpy array)."""
    if contingency_table.sum() == 0:
        return 0.0
    try:
        chi2, p, dof, expected = chi2_contingency(contingency_table)
    except ValueError:
        return 0.0
    n = contingency_table.sum()
    min_dim = min(contingency_table.shape) - 1
    if min_dim == 0 or n == 0:
        return 0.0
    return math.sqrt(chi2 / (n * min_dim))


def mutual_information(x_vals, y_vals):
    """Compute mutual information I(X;Y) in bits."""
    joint = Counter(zip(x_vals, y_vals))
    x_counts = Counter(x_vals)
    y_counts = Counter(y_vals)
    n = len(x_vals)
    if n == 0:
        return 0.0

    mi = 0.0
    for (x, y), count in joint.items():
        p_xy = count / n
        p_x = x_counts[x] / n
        p_y = y_counts[y] / n
        if p_xy > 0 and p_x > 0 and p_y > 0:
            mi += p_xy * math.log2(p_xy / (p_x * p_y))
    return mi


def conditional_entropy(target_vals, given_vals):
    """Compute H(target | given) in bits."""
    h_target = entropy_bits(target_vals)
    mi = mutual_information(target_vals, given_vals)
    return h_target - mi


def entropy_bits(vals):
    """Compute entropy in bits."""
    counts = Counter(vals)
    n = sum(counts.values())
    if n == 0:
        return 0.0
    h = 0.0
    for c in counts.values():
        p = c / n
        if p > 0:
            h -= p * math.log2(p)
    return h


def chi2_test(x_vals, y_vals):
    """Run chi-square test on two categorical variables. Returns (chi2, p, V, n)."""
    labels_x = sorted(set(x_vals))
    labels_y = sorted(set(y_vals))
    if len(labels_x) < 2 or len(labels_y) < 2:
        return 0.0, 1.0, 0.0, len(x_vals)

    x_idx = {v: i for i, v in enumerate(labels_x)}
    y_idx = {v: i for i, v in enumerate(labels_y)}

    table = np.zeros((len(labels_x), len(labels_y)), dtype=float)
    for x, y in zip(x_vals, y_vals):
        table[x_idx[x], y_idx[y]] += 1

    # Remove zero-sum rows/cols
    table = table[table.sum(axis=1) > 0]
    if table.shape[0] < 2:
        return 0.0, 1.0, 0.0, len(x_vals)
    table = table[:, table.sum(axis=0) > 0]
    if table.shape[1] < 2:
        return 0.0, 1.0, 0.0, len(x_vals)

    try:
        chi2, p, dof, expected = chi2_contingency(table)
    except ValueError:
        return 0.0, 1.0, 0.0, len(x_vals)

    n = table.sum()
    min_dim = min(table.shape) - 1
    v = math.sqrt(chi2 / (n * min_dim)) if min_dim > 0 and n > 0 else 0.0
    return chi2, p, v, int(n)


# ============================================================
# DATA LOADING
# ============================================================

def load_data():
    """Load all Currier B tokens with full morphological decomposition."""
    tx = Transcript()
    morph = Morphology()
    cc = CategoryClassifier()

    records = []
    for tok in tx.currier_b():
        if '*' in tok.word or not tok.word.strip():
            continue

        m = morph.extract(tok.word)
        if not m.middle:
            continue

        mid_head, mid_mods, mid_term = decompose_middle(m.middle)

        suf_atoms = decompose_suffix(m.suffix) if m.suffix else []
        suf_head = get_suffix_head(m.suffix) if m.suffix else None
        suf_term = get_suffix_term(m.suffix) if m.suffix else None

        pfx_modifier, pfx_base = get_prefix_base_modifier(m.prefix) if m.prefix else (None, None)

        category = cc.classify(m.middle) or 'UNKNOWN'

        # Determine suffix mode from C1410
        suf_mode = None
        if m.suffix:
            suf_a_count = sum(1 for a in suf_atoms if a in MODE_A_ATOMS)
            suf_b_count = sum(1 for a in suf_atoms if a in MODE_B_ATOMS)
            if suf_a_count > suf_b_count:
                suf_mode = 'A'
            elif suf_b_count > suf_a_count:
                suf_mode = 'B'
            else:
                suf_mode = 'MIXED'

        records.append({
            'word': tok.word,
            'folio': tok.folio,
            'section': tok.section,
            'line': tok.line,
            'prefix': m.prefix,
            'pfx_base': pfx_base,
            'pfx_modifier': pfx_modifier,
            'middle': m.middle,
            'mid_head': mid_head[0] if mid_head else None,  # base char of HEAD
            'mid_head_full': mid_head,
            'mid_mods': mid_mods,
            'mid_term': mid_term[0] if mid_term else None,  # base char of TERM
            'mid_term_full': mid_term,
            'suffix': m.suffix,
            'suf_head': suf_head[0] if suf_head else None,  # base char
            'suf_term': suf_term[0] if suf_term else None,  # base char
            'suf_mode': suf_mode,
            'suf_atoms': suf_atoms,
            'category': category,
            'has_suffix': m.suffix is not None,
            'line_pos': None,  # not needed for this analysis
        })

    print(f"Loaded {len(records)} Currier B tokens")
    return records


# ============================================================
# TEST IMPLEMENTATIONS
# ============================================================

def test_T1_prefix_middle_atom_selectivity(records):
    """T1: Does PREFIX predict MIDDLE HEAD and MIDDLE TERMINAL atoms?"""
    print("\n=== T1: PREFIX -> MIDDLE Atom Selectivity ===")

    # Filter to tokens with both PREFIX and MIDDLE HEAD/TERM
    pfx_head = [(r['prefix'], r['mid_head']) for r in records
                if r['prefix'] and r['mid_head']]
    pfx_term = [(r['prefix'], r['mid_term']) for r in records
                if r['prefix'] and r['mid_term']]

    # PREFIX -> MIDDLE HEAD
    prefixes_h, heads_h = zip(*pfx_head)
    chi2_h, p_h, v_h, n_h = chi2_test(list(prefixes_h), list(heads_h))
    mi_h = mutual_information(list(prefixes_h), list(heads_h))

    # PREFIX -> MIDDLE TERM
    prefixes_t, terms_t = zip(*pfx_term)
    chi2_t, p_t, v_t, n_t = chi2_test(list(prefixes_t), list(terms_t))
    mi_t = mutual_information(list(prefixes_t), list(terms_t))

    print(f"  PREFIX -> MIDDLE HEAD: chi2={chi2_h:.1f}, p={p_h:.2e}, V={v_h:.4f}, MI={mi_h:.4f} bits, N={n_h}")
    print(f"  PREFIX -> MIDDLE TERM: chi2={chi2_t:.1f}, p={p_t:.2e}, V={v_t:.4f}, MI={mi_t:.4f} bits, N={n_t}")

    # Sister pair comparison (ch vs sh, ok vs ot)
    sister_results = {}
    for s1, s2 in [('ch', 'sh'), ('ok', 'ot')]:
        for target, label in [('mid_head', 'HEAD'), ('mid_term', 'TERM')]:
            s1_vals = [r[target] for r in records if r['prefix'] == s1 and r[target]]
            s2_vals = [r[target] for r in records if r['prefix'] == s2 and r[target]]
            s1_dist = Counter(s1_vals)
            s2_dist = Counter(s2_vals)
            # Compute JSD between distributions
            all_keys = sorted(set(s1_dist.keys()) | set(s2_dist.keys()))
            n1, n2 = sum(s1_dist.values()), sum(s2_dist.values())
            if n1 > 0 and n2 > 0:
                p1 = np.array([s1_dist.get(k, 0) / n1 for k in all_keys])
                p2 = np.array([s2_dist.get(k, 0) / n2 for k in all_keys])
                m_dist = (p1 + p2) / 2
                jsd = 0.5 * sp_entropy(p1, m_dist, base=2) + 0.5 * sp_entropy(p2, m_dist, base=2)
            else:
                jsd = 0.0
            key = f"{s1}_vs_{s2}_{label}"
            sister_results[key] = {
                f'{s1}_dist': dict(s1_dist), f'{s2}_dist': dict(s2_dist),
                f'{s1}_n': n1, f'{s2}_n': n2, 'JSD': round(jsd, 4)
            }
            print(f"  {s1} vs {s2} MIDDLE {label}: JSD={jsd:.4f}, N=({n1},{n2})")

    return {
        'prefix_to_mid_head': {
            'chi2': round(chi2_h, 1), 'p': p_h, 'V': round(v_h, 4),
            'MI_bits': round(mi_h, 4), 'N': n_h
        },
        'prefix_to_mid_term': {
            'chi2': round(chi2_t, 1), 'p': p_t, 'V': round(v_t, 4),
            'MI_bits': round(mi_t, 4), 'N': n_t
        },
        'sister_comparisons': sister_results
    }


def test_T2_prefix_suffix_selectivity(records):
    """T2: Does PREFIX predict suffix presence/absence and suffix mode?"""
    print("\n=== T2: PREFIX -> SUFFIX Selectivity ===")

    prefixed = [r for r in records if r['prefix']]

    # PREFIX -> suffix presence
    pfx_list = [r['prefix'] for r in prefixed]
    has_suf = ['YES' if r['has_suffix'] else 'NO' for r in prefixed]
    chi2_pres, p_pres, v_pres, n_pres = chi2_test(pfx_list, has_suf)
    mi_pres = mutual_information(pfx_list, has_suf)

    print(f"  PREFIX -> suffix presence: chi2={chi2_pres:.1f}, p={p_pres:.2e}, V={v_pres:.4f}, N={n_pres}")

    # Per-PREFIX suffix rate
    pfx_counts = Counter(pfx_list)
    pfx_suf_counts = Counter(r['prefix'] for r in prefixed if r['has_suffix'])
    pfx_suf_rates = {}
    for pfx in sorted(pfx_counts.keys(), key=lambda x: -pfx_counts[x])[:15]:
        rate = pfx_suf_counts.get(pfx, 0) / pfx_counts[pfx]
        pfx_suf_rates[pfx] = round(rate, 3)
        print(f"    {pfx}: {rate:.3f} ({pfx_suf_counts.get(pfx, 0)}/{pfx_counts[pfx]})")

    # PREFIX -> suffix mode (A/B)
    suffixed = [r for r in prefixed if r['suf_mode'] and r['suf_mode'] != 'MIXED']
    pfx_mode = [(r['prefix'], r['suf_mode']) for r in suffixed]
    if pfx_mode:
        pfx_m, mode_m = zip(*pfx_mode)
        chi2_mode, p_mode, v_mode, n_mode = chi2_test(list(pfx_m), list(mode_m))
        mi_mode = mutual_information(list(pfx_m), list(mode_m))
        print(f"  PREFIX -> suffix mode: chi2={chi2_mode:.1f}, p={p_mode:.2e}, V={v_mode:.4f}, MI={mi_mode:.4f} bits, N={n_mode}")
    else:
        chi2_mode, p_mode, v_mode, n_mode, mi_mode = 0, 1, 0, 0, 0

    # Per-PREFIX mode A fraction
    pfx_mode_a = {}
    for pfx in sorted(pfx_counts.keys(), key=lambda x: -pfx_counts[x])[:15]:
        mode_vals = [r['suf_mode'] for r in suffixed if r['prefix'] == pfx]
        if mode_vals:
            a_frac = sum(1 for m in mode_vals if m == 'A') / len(mode_vals)
            pfx_mode_a[pfx] = round(a_frac, 3)

    return {
        'prefix_to_suffix_presence': {
            'chi2': round(chi2_pres, 1), 'p': p_pres, 'V': round(v_pres, 4),
            'MI_bits': round(mi_pres, 4), 'N': n_pres
        },
        'per_prefix_suffix_rate': pfx_suf_rates,
        'prefix_to_suffix_mode': {
            'chi2': round(chi2_mode, 1), 'p': p_mode, 'V': round(v_mode, 4),
            'MI_bits': round(mi_mode, 4), 'N': n_mode
        },
        'per_prefix_mode_a_fraction': pfx_mode_a
    }


def test_T3_middle_suffix_selectivity(records):
    """T3: Does MIDDLE HEAD/TERM predict suffix mode?"""
    print("\n=== T3: MIDDLE -> SUFFIX Selectivity ===")

    suffixed = [r for r in records if r['suf_mode'] and r['suf_mode'] != 'MIXED']

    # MIDDLE HEAD -> suffix mode
    head_mode = [(r['mid_head'], r['suf_mode']) for r in suffixed if r['mid_head']]
    if head_mode:
        heads, modes = zip(*head_mode)
        chi2_h, p_h, v_h, n_h = chi2_test(list(heads), list(modes))
        mi_h = mutual_information(list(heads), list(modes))
        print(f"  MIDDLE HEAD -> suffix mode: chi2={chi2_h:.1f}, p={p_h:.2e}, V={v_h:.4f}, MI={mi_h:.4f} bits, N={n_h}")
    else:
        chi2_h, p_h, v_h, n_h, mi_h = 0, 1, 0, 0, 0

    # MIDDLE TERM -> suffix mode
    term_mode = [(r['mid_term'], r['suf_mode']) for r in suffixed if r['mid_term']]
    if term_mode:
        terms, modes = zip(*term_mode)
        chi2_t, p_t, v_t, n_t = chi2_test(list(terms), list(modes))
        mi_t = mutual_information(list(terms), list(modes))
        print(f"  MIDDLE TERM -> suffix mode: chi2={chi2_t:.1f}, p={p_t:.2e}, V={v_t:.4f}, MI={mi_t:.4f} bits, N={n_t}")
    else:
        chi2_t, p_t, v_t, n_t, mi_t = 0, 1, 0, 0, 0

    # Full MIDDLE -> suffix mode
    mid_mode = [(r['middle'], r['suf_mode']) for r in suffixed]
    if mid_mode:
        mids, modes = zip(*mid_mode)
        chi2_m, p_m, v_m, n_m = chi2_test(list(mids), list(modes))
        mi_m = mutual_information(list(mids), list(modes))
        print(f"  Full MIDDLE -> suffix mode: chi2={chi2_m:.1f}, p={p_m:.2e}, V={v_m:.4f}, MI={mi_m:.4f} bits, N={n_m}")
    else:
        chi2_m, p_m, v_m, n_m, mi_m = 0, 1, 0, 0, 0

    # MIDDLE HEAD -> suffix presence
    head_pres = [(r['mid_head'], 'YES' if r['has_suffix'] else 'NO')
                 for r in records if r['mid_head']]
    if head_pres:
        hs, ps = zip(*head_pres)
        chi2_hp, p_hp, v_hp, n_hp = chi2_test(list(hs), list(ps))
        print(f"  MIDDLE HEAD -> suffix presence: chi2={chi2_hp:.1f}, p={p_hp:.2e}, V={v_hp:.4f}, N={n_hp}")
    else:
        chi2_hp, p_hp, v_hp, n_hp = 0, 1, 0, 0

    # Per-HEAD mode A fraction
    head_mode_a = {}
    for head_val in sorted(set(r['mid_head'] for r in suffixed if r['mid_head'])):
        mode_vals = [r['suf_mode'] for r in suffixed if r['mid_head'] == head_val]
        if len(mode_vals) >= 10:
            a_frac = sum(1 for m in mode_vals if m == 'A') / len(mode_vals)
            head_mode_a[head_val] = {'mode_a_frac': round(a_frac, 3), 'n': len(mode_vals)}

    return {
        'mid_head_to_suf_mode': {
            'chi2': round(chi2_h, 1), 'p': p_h, 'V': round(v_h, 4),
            'MI_bits': round(mi_h, 4), 'N': n_h
        },
        'mid_term_to_suf_mode': {
            'chi2': round(chi2_t, 1), 'p': p_t, 'V': round(v_t, 4),
            'MI_bits': round(mi_t, 4), 'N': n_t
        },
        'full_middle_to_suf_mode': {
            'chi2': round(chi2_m, 1), 'p': p_m, 'V': round(v_m, 4),
            'MI_bits': round(mi_m, 4), 'N': n_m
        },
        'mid_head_to_suf_presence': {
            'chi2': round(chi2_hp, 1), 'p': p_hp, 'V': round(v_hp, 4), 'N': n_hp
        },
        'per_head_mode_a': head_mode_a
    }


def test_T4_three_way_interaction(records):
    """T4: PREFIX x MIDDLE -> SUFFIX: joint vs sum of individual effects."""
    print("\n=== T4: Three-Way Interaction (PREFIX x MIDDLE -> SUFFIX) ===")

    suffixed = [r for r in records if r['suf_mode'] and r['suf_mode'] != 'MIXED'
                and r['prefix'] and r['middle']]

    if not suffixed:
        return {}

    prefixes = [r['prefix'] for r in suffixed]
    middles = [r['middle'] for r in suffixed]
    suf_modes = [r['suf_mode'] for r in suffixed]

    # Individual MIs
    mi_prefix_suf = mutual_information(prefixes, suf_modes)
    mi_middle_suf = mutual_information(middles, suf_modes)

    # Joint MI: I(SUFFIX; PREFIX, MIDDLE) using concatenated key
    joint_keys = [f"{p}|{m}" for p, m in zip(prefixes, middles)]
    mi_joint = mutual_information(joint_keys, suf_modes)

    # Synergy = joint - (individual sum)
    sum_individual = mi_prefix_suf + mi_middle_suf
    synergy = mi_joint - sum_individual

    # Redundancy = sum_individual - joint (positive = redundant, negative = synergistic)
    redundancy = -synergy  # positive when synergy is negative

    h_suf = entropy_bits(suf_modes)

    print(f"  I(SUF_MODE; PREFIX) = {mi_prefix_suf:.4f} bits")
    print(f"  I(SUF_MODE; MIDDLE) = {mi_middle_suf:.4f} bits")
    print(f"  I(SUF_MODE; PREFIX,MIDDLE) = {mi_joint:.4f} bits")
    print(f"  Sum of individuals = {sum_individual:.4f} bits")
    print(f"  Synergy = {synergy:.4f} bits (positive=synergistic, negative=redundant)")
    print(f"  H(SUF_MODE) = {h_suf:.4f} bits")
    print(f"  Joint explains {mi_joint/h_suf*100:.1f}% of suffix mode entropy")

    # Also test with suffix identity (not just mode)
    suffixes = [r['suffix'] for r in suffixed]
    mi_pfx_suf_id = mutual_information(prefixes, suffixes)
    mi_mid_suf_id = mutual_information(middles, suffixes)
    mi_joint_suf_id = mutual_information(joint_keys, suffixes)
    h_suf_id = entropy_bits(suffixes)
    synergy_id = mi_joint_suf_id - (mi_pfx_suf_id + mi_mid_suf_id)

    print(f"\n  With full suffix identity:")
    print(f"  I(SUF; PREFIX) = {mi_pfx_suf_id:.4f} bits")
    print(f"  I(SUF; MIDDLE) = {mi_mid_suf_id:.4f} bits")
    print(f"  I(SUF; PREFIX,MIDDLE) = {mi_joint_suf_id:.4f} bits")
    print(f"  Synergy = {synergy_id:.4f} bits")
    print(f"  H(SUF) = {h_suf_id:.4f} bits")

    return {
        'suffix_mode': {
            'MI_prefix': round(mi_prefix_suf, 4),
            'MI_middle': round(mi_middle_suf, 4),
            'MI_joint': round(mi_joint, 4),
            'sum_individual': round(sum_individual, 4),
            'synergy': round(synergy, 4),
            'H_suffix_mode': round(h_suf, 4),
            'joint_explains_pct': round(mi_joint / h_suf * 100, 1) if h_suf > 0 else 0,
            'N': len(suffixed)
        },
        'suffix_identity': {
            'MI_prefix': round(mi_pfx_suf_id, 4),
            'MI_middle': round(mi_mid_suf_id, 4),
            'MI_joint': round(mi_joint_suf_id, 4),
            'synergy': round(synergy_id, 4),
            'H_suffix': round(h_suf_id, 4),
            'N': len(suffixed)
        }
    }


def test_T5_slot_independence(records):
    """T5: Mutual information between all slot pairs."""
    print("\n=== T5: Slot Independence (Pairwise MI) ===")

    # Use tokens with all three slots
    complete = [r for r in records if r['prefix'] and r['middle'] and r['suffix']]

    prefixes = [r['prefix'] for r in complete]
    middles = [r['middle'] for r in complete]
    suffixes = [r['suffix'] for r in complete]

    mi_pm = mutual_information(prefixes, middles)
    mi_ps = mutual_information(prefixes, suffixes)
    mi_ms = mutual_information(middles, suffixes)

    h_p = entropy_bits(prefixes)
    h_m = entropy_bits(middles)
    h_s = entropy_bits(suffixes)

    # Normalized MI (0-1 scale)
    nmi_pm = mi_pm / min(h_p, h_m) if min(h_p, h_m) > 0 else 0
    nmi_ps = mi_ps / min(h_p, h_s) if min(h_p, h_s) > 0 else 0
    nmi_ms = mi_ms / min(h_m, h_s) if min(h_m, h_s) > 0 else 0

    print(f"  N (tokens with all 3 slots) = {len(complete)}")
    print(f"  H(PREFIX)={h_p:.3f} H(MIDDLE)={h_m:.3f} H(SUFFIX)={h_s:.3f}")
    print(f"  I(PREFIX;MIDDLE) = {mi_pm:.4f} bits (NMI={nmi_pm:.4f})")
    print(f"  I(PREFIX;SUFFIX) = {mi_ps:.4f} bits (NMI={nmi_ps:.4f})")
    print(f"  I(MIDDLE;SUFFIX) = {mi_ms:.4f} bits (NMI={nmi_ms:.4f})")

    # Shuffle null models (100 permutations)
    np.random.seed(42)
    null_pm, null_ps, null_ms = [], [], []
    for _ in range(100):
        shuf_p = list(prefixes)
        np.random.shuffle(shuf_p)
        shuf_m = list(middles)
        np.random.shuffle(shuf_m)
        shuf_s = list(suffixes)
        np.random.shuffle(shuf_s)
        null_pm.append(mutual_information(shuf_p, middles))
        null_ps.append(mutual_information(shuf_p, suffixes))
        null_ms.append(mutual_information(shuf_m, shuf_s))

    z_pm = (mi_pm - np.mean(null_pm)) / np.std(null_pm) if np.std(null_pm) > 0 else 0
    z_ps = (mi_ps - np.mean(null_ps)) / np.std(null_ps) if np.std(null_ps) > 0 else 0
    z_ms = (mi_ms - np.mean(null_ms)) / np.std(null_ms) if np.std(null_ms) > 0 else 0

    print(f"  Null MI (shuffled): PM={np.mean(null_pm):.4f} PS={np.mean(null_ps):.4f} MS={np.mean(null_ms):.4f}")
    print(f"  Z-scores: PM={z_pm:.1f} PS={z_ps:.1f} MS={z_ms:.1f}")

    # Also compute for all tokens (not just complete)
    all_with_pm = [r for r in records if r['prefix'] and r['middle']]
    all_with_ps = [r for r in records if r['prefix'] and r['suffix']]
    all_with_ms = [r for r in records if r['middle'] and r['suffix']]

    mi_pm_all = mutual_information([r['prefix'] for r in all_with_pm],
                                    [r['middle'] for r in all_with_pm])
    mi_ps_all = mutual_information([r['prefix'] for r in all_with_ps],
                                    [r['suffix'] for r in all_with_ps])
    mi_ms_all = mutual_information([r['middle'] for r in all_with_ms],
                                    [r['suffix'] for r in all_with_ms])

    print(f"\n  All available pairs:")
    print(f"  I(PREFIX;MIDDLE) = {mi_pm_all:.4f} bits (N={len(all_with_pm)})")
    print(f"  I(PREFIX;SUFFIX) = {mi_ps_all:.4f} bits (N={len(all_with_ps)})")
    print(f"  I(MIDDLE;SUFFIX) = {mi_ms_all:.4f} bits (N={len(all_with_ms)})")

    return {
        'complete_tokens_N': len(complete),
        'entropies': {'H_prefix': round(h_p, 3), 'H_middle': round(h_m, 3), 'H_suffix': round(h_s, 3)},
        'pairwise_MI': {
            'prefix_middle': round(mi_pm, 4), 'prefix_suffix': round(mi_ps, 4),
            'middle_suffix': round(mi_ms, 4)
        },
        'normalized_MI': {
            'prefix_middle': round(nmi_pm, 4), 'prefix_suffix': round(nmi_ps, 4),
            'middle_suffix': round(nmi_ms, 4)
        },
        'z_scores': {
            'prefix_middle': round(z_pm, 1), 'prefix_suffix': round(z_ps, 1),
            'middle_suffix': round(z_ms, 1)
        },
        'all_pairs_MI': {
            'prefix_middle': round(mi_pm_all, 4), 'prefix_suffix': round(mi_ps_all, 4),
            'middle_suffix': round(mi_ms_all, 4)
        },
        'all_pairs_N': {
            'prefix_middle': len(all_with_pm), 'prefix_suffix': len(all_with_ps),
            'middle_suffix': len(all_with_ms)
        }
    }


def test_T6_cross_slot_atom_cooccurrence(records):
    """T6: When atom X in MIDDLE, does atom X appear in SUFFIX? (self-attraction/repulsion)"""
    print("\n=== T6: Cross-Slot Atom Co-occurrence ===")

    # 12 shared atoms (from C1409): a, d, e, h, i, l, m, n, o, r, s, y
    shared_atoms = sorted(set('adehilmnorsy'))

    suffixed = [r for r in records if r['suffix'] and r['middle']]

    results = {}
    for atom in shared_atoms:
        mid_has = []
        suf_has = []
        for r in suffixed:
            # Check if atom's base char is in the middle
            m_atoms = set(atomize_middle(r['middle']))
            m_has_atom = any(a[0] == atom for a in m_atoms)

            # Check if atom's base char is in the suffix
            s_atoms = set(decompose_suffix(r['suffix']))
            s_has_atom = any(a[0] == atom for a in s_atoms)

            mid_has.append(m_has_atom)
            suf_has.append(s_has_atom)

        # 2x2 contingency table
        both = sum(1 for m, s in zip(mid_has, suf_has) if m and s)
        mid_only = sum(1 for m, s in zip(mid_has, suf_has) if m and not s)
        suf_only = sum(1 for m, s in zip(mid_has, suf_has) if not m and s)
        neither = sum(1 for m, s in zip(mid_has, suf_has) if not m and not s)

        n = len(suffixed)
        mid_rate = (both + mid_only) / n if n > 0 else 0
        suf_rate = (both + suf_only) / n if n > 0 else 0
        expected_both = mid_rate * suf_rate * n

        if expected_both > 0:
            obs_exp_ratio = both / expected_both
        else:
            obs_exp_ratio = 0

        # Chi-square on 2x2
        table = np.array([[both, mid_only], [suf_only, neither]], dtype=float)
        if table.min() >= 0 and table.sum() > 0:
            try:
                chi2, p, _, _ = chi2_contingency(table, correction=True)
            except ValueError:
                chi2, p = 0, 1
        else:
            chi2, p = 0, 1

        direction = 'ATTRACT' if obs_exp_ratio > 1 else 'REPEL' if obs_exp_ratio < 1 else 'NEUTRAL'

        results[atom] = {
            'both': both, 'mid_only': mid_only, 'suf_only': suf_only,
            'neither': neither, 'expected_both': round(expected_both, 1),
            'obs_exp_ratio': round(obs_exp_ratio, 3),
            'chi2': round(chi2, 1), 'p': p, 'direction': direction,
            'mid_rate': round(mid_rate, 3), 'suf_rate': round(suf_rate, 3)
        }

        sig = '*' if p < 0.05 / len(shared_atoms) else ''
        print(f"  {atom}: O/E={obs_exp_ratio:.3f} {direction}{sig} (both={both}, exp={expected_both:.0f}, chi2={chi2:.1f}, p={p:.2e})")

    return results


def test_T7_prefix_base_vs_modifier(records):
    """T7: Does PREFIX base predict MIDDLE better than modifier? And vice versa for SUFFIX."""
    print("\n=== T7: PREFIX Base vs Modifier Decomposition ===")

    # Tokens with PREFIX that has both base and modifier (i.e., multi-char prefix)
    multi_pfx = [r for r in records if r['pfx_base'] and r['pfx_modifier'] and r['middle']]

    if not multi_pfx:
        print("  No multi-character prefixes found")
        return {}

    bases = [r['pfx_base'] for r in multi_pfx]
    modifiers = [r['pfx_modifier'] for r in multi_pfx]

    # BASE -> MIDDLE HEAD
    with_head = [(r['pfx_base'], r['mid_head']) for r in multi_pfx if r['mid_head']]
    if with_head:
        b, h = zip(*with_head)
        chi2_bh, p_bh, v_bh, n_bh = chi2_test(list(b), list(h))
        mi_bh = mutual_information(list(b), list(h))
        print(f"  BASE -> MIDDLE HEAD: V={v_bh:.4f}, MI={mi_bh:.4f} bits, N={n_bh}")
    else:
        v_bh, mi_bh, n_bh = 0, 0, 0

    # MODIFIER -> MIDDLE HEAD
    with_head_m = [(r['pfx_modifier'], r['mid_head']) for r in multi_pfx if r['mid_head']]
    if with_head_m:
        m, h = zip(*with_head_m)
        chi2_mh, p_mh, v_mh, n_mh = chi2_test(list(m), list(h))
        mi_mh = mutual_information(list(m), list(h))
        print(f"  MODIFIER -> MIDDLE HEAD: V={v_mh:.4f}, MI={mi_mh:.4f} bits, N={n_mh}")
    else:
        v_mh, mi_mh, n_mh = 0, 0, 0

    # BASE -> SUFFIX MODE
    with_suf = [(r['pfx_base'], r['suf_mode']) for r in multi_pfx
                if r['suf_mode'] and r['suf_mode'] != 'MIXED']
    if with_suf:
        b, s = zip(*with_suf)
        chi2_bs, p_bs, v_bs, n_bs = chi2_test(list(b), list(s))
        mi_bs = mutual_information(list(b), list(s))
        print(f"  BASE -> SUFFIX MODE: V={v_bs:.4f}, MI={mi_bs:.4f} bits, N={n_bs}")
    else:
        v_bs, mi_bs, n_bs = 0, 0, 0

    # MODIFIER -> SUFFIX MODE
    with_suf_m = [(r['pfx_modifier'], r['suf_mode']) for r in multi_pfx
                  if r['suf_mode'] and r['suf_mode'] != 'MIXED']
    if with_suf_m:
        m, s = zip(*with_suf_m)
        chi2_ms, p_ms, v_ms, n_ms = chi2_test(list(m), list(s))
        mi_ms = mutual_information(list(m), list(s))
        print(f"  MODIFIER -> SUFFIX MODE: V={v_ms:.4f}, MI={mi_ms:.4f} bits, N={n_ms}")
    else:
        v_ms, mi_ms, n_ms = 0, 0, 0

    # BASE -> SUFFIX identity
    with_suf_id = [(r['pfx_base'], r['suffix']) for r in multi_pfx if r['suffix']]
    if with_suf_id:
        b, s = zip(*with_suf_id)
        mi_bs_id = mutual_information(list(b), list(s))
        print(f"  BASE -> SUFFIX identity: MI={mi_bs_id:.4f} bits, N={len(with_suf_id)}")
    else:
        mi_bs_id = 0

    # MODIFIER -> SUFFIX identity
    with_suf_id_m = [(r['pfx_modifier'], r['suffix']) for r in multi_pfx if r['suffix']]
    if with_suf_id_m:
        m, s = zip(*with_suf_id_m)
        mi_ms_id = mutual_information(list(m), list(s))
        print(f"  MODIFIER -> SUFFIX identity: MI={mi_ms_id:.4f} bits, N={len(with_suf_id_m)}")
    else:
        mi_ms_id = 0

    return {
        'base_to_mid_head': {'V': round(v_bh, 4), 'MI': round(mi_bh, 4), 'N': n_bh},
        'modifier_to_mid_head': {'V': round(v_mh, 4), 'MI': round(mi_mh, 4), 'N': n_mh},
        'base_to_suf_mode': {'V': round(v_bs, 4), 'MI': round(mi_bs, 4), 'N': n_bs},
        'modifier_to_suf_mode': {'V': round(v_ms, 4), 'MI': round(mi_ms, 4), 'N': n_ms},
        'base_to_suf_identity': {'MI': round(mi_bs_id, 4)},
        'modifier_to_suf_identity': {'MI': round(mi_ms_id, 4)},
        'N_multi_prefix_tokens': len(multi_pfx)
    }


def test_T8_conditional_entropy_chain(records):
    """T8: Full conditional entropy decomposition."""
    print("\n=== T8: Conditional Entropy Chain ===")

    # Tokens with all slots
    complete = [r for r in records if r['prefix'] and r['middle'] and r['suffix']]

    prefixes = [r['prefix'] for r in complete]
    middles = [r['middle'] for r in complete]
    suffixes = [r['suffix'] for r in complete]

    # Entropy chain for SUFFIX
    h_s = entropy_bits(suffixes)
    h_s_given_p = conditional_entropy(suffixes, prefixes)
    h_s_given_m = conditional_entropy(suffixes, middles)

    # H(SUFFIX | MIDDLE, PREFIX) via joint key
    joint_pm = [f"{p}|{m}" for p, m in zip(prefixes, middles)]
    h_s_given_pm = conditional_entropy(suffixes, joint_pm)

    print(f"  H(SUFFIX) = {h_s:.4f} bits")
    print(f"  H(SUFFIX | PREFIX) = {h_s_given_p:.4f} bits  (PREFIX reduces by {h_s - h_s_given_p:.4f})")
    print(f"  H(SUFFIX | MIDDLE) = {h_s_given_m:.4f} bits  (MIDDLE reduces by {h_s - h_s_given_m:.4f})")
    print(f"  H(SUFFIX | PREFIX, MIDDLE) = {h_s_given_pm:.4f} bits  (both reduce by {h_s - h_s_given_pm:.4f})")

    # MIDDLE entropy given PREFIX
    h_m = entropy_bits(middles)
    h_m_given_p = conditional_entropy(middles, prefixes)
    print(f"\n  H(MIDDLE) = {h_m:.4f} bits")
    print(f"  H(MIDDLE | PREFIX) = {h_m_given_p:.4f} bits  (PREFIX reduces by {h_m - h_m_given_p:.4f})")

    # SUFFIX given MIDDLE HEAD vs MIDDLE TERM
    mid_heads = [r['mid_head'] for r in complete]
    mid_terms = [r['mid_term'] for r in complete]

    # Filter to tokens with both head and term
    with_both = [(s, h, t) for s, h, t in zip(suffixes, mid_heads, mid_terms) if h and t]
    if with_both:
        s_b, h_b, t_b = zip(*with_both)
        h_s_given_mh = conditional_entropy(list(s_b), list(h_b))
        h_s_given_mt = conditional_entropy(list(s_b), list(t_b))
        ht_joint = [f"{h}|{t}" for h, t in zip(h_b, t_b)]
        h_s_given_mht = conditional_entropy(list(s_b), ht_joint)
        h_s_b = entropy_bits(list(s_b))

        print(f"\n  Within tokens having HEAD+TERM (N={len(with_both)}):")
        print(f"  H(SUFFIX) = {h_s_b:.4f}")
        print(f"  H(SUFFIX | MID_HEAD) = {h_s_given_mh:.4f}  (reduces by {h_s_b - h_s_given_mh:.4f})")
        print(f"  H(SUFFIX | MID_TERM) = {h_s_given_mt:.4f}  (reduces by {h_s_b - h_s_given_mt:.4f})")
        print(f"  H(SUFFIX | MID_HEAD, MID_TERM) = {h_s_given_mht:.4f}  (reduces by {h_s_b - h_s_given_mht:.4f})")
    else:
        h_s_given_mh, h_s_given_mt, h_s_given_mht, h_s_b = 0, 0, 0, 0

    # Also: H(PREFIX) and H(PREFIX | SUFFIX)
    h_p = entropy_bits(prefixes)
    h_p_given_s = conditional_entropy(prefixes, suffixes)
    h_p_given_m = conditional_entropy(prefixes, middles)
    print(f"\n  H(PREFIX) = {h_p:.4f} bits")
    print(f"  H(PREFIX | SUFFIX) = {h_p_given_s:.4f}  (SUFFIX reduces by {h_p - h_p_given_s:.4f})")
    print(f"  H(PREFIX | MIDDLE) = {h_p_given_m:.4f}  (MIDDLE reduces by {h_p - h_p_given_m:.4f})")

    return {
        'suffix_chain': {
            'H_suffix': round(h_s, 4),
            'H_suffix_given_prefix': round(h_s_given_p, 4),
            'H_suffix_given_middle': round(h_s_given_m, 4),
            'H_suffix_given_both': round(h_s_given_pm, 4),
            'prefix_reduction': round(h_s - h_s_given_p, 4),
            'middle_reduction': round(h_s - h_s_given_m, 4),
            'both_reduction': round(h_s - h_s_given_pm, 4)
        },
        'middle_chain': {
            'H_middle': round(h_m, 4),
            'H_middle_given_prefix': round(h_m_given_p, 4),
            'prefix_reduction': round(h_m - h_m_given_p, 4)
        },
        'suffix_given_mid_atoms': {
            'H_suffix_base': round(h_s_b, 4),
            'H_suffix_given_mid_head': round(h_s_given_mh, 4),
            'H_suffix_given_mid_term': round(h_s_given_mt, 4),
            'H_suffix_given_mid_head_term': round(h_s_given_mht, 4),
            'N': len(with_both)
        },
        'prefix_chain': {
            'H_prefix': round(h_p, 4),
            'H_prefix_given_suffix': round(h_p_given_s, 4),
            'H_prefix_given_middle': round(h_p_given_m, 4)
        },
        'N': len(complete)
    }


def test_T9_forbidden_combinations(records):
    """T9: Forbidden cross-slot atom combinations."""
    print("\n=== T9: Forbidden Cross-Slot Combinations ===")

    # PREFIX x MIDDLE HEAD: observed vs expected
    pfx_head_pairs = Counter()
    pfx_counts = Counter()
    head_counts = Counter()
    for r in records:
        if r['prefix'] and r['mid_head']:
            pfx_head_pairs[(r['prefix'], r['mid_head'])] += 1
            pfx_counts[r['prefix']] += 1
            head_counts[r['mid_head']] += 1

    n_ph = sum(pfx_head_pairs.values())

    # Find forbidden: observed=0 where expected>=5
    forbidden_pfx_head = []
    for pfx in sorted(pfx_counts.keys(), key=lambda x: -pfx_counts[x])[:20]:
        for head in sorted(head_counts.keys(), key=lambda x: -head_counts[x]):
            expected = pfx_counts[pfx] * head_counts[head] / n_ph
            observed = pfx_head_pairs.get((pfx, head), 0)
            if expected >= 5 and observed == 0:
                forbidden_pfx_head.append({
                    'prefix': pfx, 'head': head,
                    'expected': round(expected, 1), 'observed': 0
                })
            elif expected >= 5 and observed < expected * 0.1:
                forbidden_pfx_head.append({
                    'prefix': pfx, 'head': head,
                    'expected': round(expected, 1), 'observed': observed,
                    'ratio': round(observed / expected, 3) if expected > 0 else 0
                })

    print(f"  PREFIX x MIDDLE HEAD: {len(forbidden_pfx_head)} forbidden/depleted (top 20 PREFIXes)")
    for f in forbidden_pfx_head[:10]:
        print(f"    {f['prefix']} x {f['head']}: obs={f['observed']}, exp={f['expected']}")

    # MIDDLE TERM x SUFFIX HEAD
    term_sufh_pairs = Counter()
    term_counts = Counter()
    sufh_counts = Counter()
    for r in records:
        if r['mid_term'] and r['suf_head']:
            term_sufh_pairs[(r['mid_term'], r['suf_head'])] += 1
            term_counts[r['mid_term']] += 1
            sufh_counts[r['suf_head']] += 1

    n_ts = sum(term_sufh_pairs.values())

    forbidden_term_sufh = []
    for term in sorted(term_counts.keys()):
        for sh in sorted(sufh_counts.keys()):
            expected = term_counts[term] * sufh_counts[sh] / n_ts if n_ts > 0 else 0
            observed = term_sufh_pairs.get((term, sh), 0)
            if expected >= 5 and observed == 0:
                forbidden_term_sufh.append({
                    'mid_term': term, 'suf_head': sh,
                    'expected': round(expected, 1), 'observed': 0
                })
            elif expected >= 5 and observed < expected * 0.1:
                forbidden_term_sufh.append({
                    'mid_term': term, 'suf_head': sh,
                    'expected': round(expected, 1), 'observed': observed,
                    'ratio': round(observed / expected, 3) if expected > 0 else 0
                })

    print(f"\n  MIDDLE TERM x SUFFIX HEAD: {len(forbidden_term_sufh)} forbidden/depleted")
    for f in forbidden_term_sufh:
        print(f"    {f['mid_term']} x {f['suf_head']}: obs={f['observed']}, exp={f['expected']}")

    # PREFIX x SUFFIX (full) forbidden
    pfx_suf_pairs = Counter()
    suf_counts = Counter()
    pfx_counts2 = Counter()
    for r in records:
        if r['prefix'] and r['suffix']:
            pfx_suf_pairs[(r['prefix'], r['suffix'])] += 1
            pfx_counts2[r['prefix']] += 1
            suf_counts[r['suffix']] += 1

    n_ps = sum(pfx_suf_pairs.values())

    forbidden_pfx_suf = []
    for pfx in sorted(pfx_counts2.keys(), key=lambda x: -pfx_counts2[x])[:15]:
        for suf in sorted(suf_counts.keys(), key=lambda x: -suf_counts[x])[:15]:
            expected = pfx_counts2[pfx] * suf_counts[suf] / n_ps if n_ps > 0 else 0
            observed = pfx_suf_pairs.get((pfx, suf), 0)
            if expected >= 5 and observed == 0:
                forbidden_pfx_suf.append({
                    'prefix': pfx, 'suffix': suf,
                    'expected': round(expected, 1), 'observed': 0
                })

    print(f"\n  PREFIX x SUFFIX: {len(forbidden_pfx_suf)} forbidden (top 15 each)")
    for f in forbidden_pfx_suf[:10]:
        print(f"    {f['prefix']} x {f['suffix']}: obs=0, exp={f['expected']}")

    return {
        'prefix_x_mid_head': {
            'forbidden_count': len(forbidden_pfx_head),
            'items': forbidden_pfx_head,
            'N': n_ph
        },
        'mid_term_x_suf_head': {
            'forbidden_count': len(forbidden_term_sufh),
            'items': forbidden_term_sufh,
            'N': n_ts
        },
        'prefix_x_suffix': {
            'forbidden_count': len(forbidden_pfx_suf),
            'items': forbidden_pfx_suf,
            'N': n_ps
        }
    }


# ============================================================
# MAIN
# ============================================================

def main():
    print("Phase 516: Cross-Slot Interaction Grammar")
    print("=" * 60)

    records = load_data()

    # Summary stats
    n_total = len(records)
    n_prefixed = sum(1 for r in records if r['prefix'])
    n_suffixed = sum(1 for r in records if r['suffix'])
    n_both = sum(1 for r in records if r['prefix'] and r['suffix'])
    print(f"\nTotal tokens: {n_total}")
    print(f"Prefixed: {n_prefixed} ({n_prefixed/n_total*100:.1f}%)")
    print(f"Suffixed: {n_suffixed} ({n_suffixed/n_total*100:.1f}%)")
    print(f"Both: {n_both} ({n_both/n_total*100:.1f}%)")

    results = {
        'metadata': {
            'phase': 516,
            'total_tokens': n_total,
            'prefixed': n_prefixed,
            'suffixed': n_suffixed,
            'both_prefix_suffix': n_both
        }
    }

    # Run all tests
    results['T1_prefix_middle_selectivity'] = test_T1_prefix_middle_atom_selectivity(records)
    results['T2_prefix_suffix_selectivity'] = test_T2_prefix_suffix_selectivity(records)
    results['T3_middle_suffix_selectivity'] = test_T3_middle_suffix_selectivity(records)
    results['T4_three_way_interaction'] = test_T4_three_way_interaction(records)
    results['T5_slot_independence'] = test_T5_slot_independence(records)
    results['T6_cross_slot_atom_cooccurrence'] = test_T6_cross_slot_atom_cooccurrence(records)
    results['T7_prefix_base_vs_modifier'] = test_T7_prefix_base_vs_modifier(records)
    results['T8_conditional_entropy_chain'] = test_T8_conditional_entropy_chain(records)
    results['T9_forbidden_combinations'] = test_T9_forbidden_combinations(records)

    # Save results
    output_path = RESULTS_DIR / 'cross_slot_interaction.json'

    # Convert numpy/float types for JSON serialization
    def convert(obj):
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating, float)):
            if math.isnan(obj) or math.isinf(obj):
                return str(obj)
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return obj

    class NumpyEncoder(json.JSONEncoder):
        def default(self, obj):
            converted = convert(obj)
            if converted is not obj:
                return converted
            return super().default(obj)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, cls=NumpyEncoder)

    print(f"\n\nResults saved to {output_path}")
    print("Done.")


if __name__ == '__main__':
    main()
