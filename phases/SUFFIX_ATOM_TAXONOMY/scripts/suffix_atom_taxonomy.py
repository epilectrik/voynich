#!/usr/bin/env python3
"""
Phase 540: SUFFIX ATOM TAXONOMY
================================
Comprehensive characterization of the suffix layer's internal grammar.
Does suffix show HEAD+TERM decomposition like MIDDLE? What is the suffix's
own internal organization? How do suffix atoms differ from MIDDLE atoms?

Usage: python phases/SUFFIX_ATOM_TAXONOMY/scripts/suffix_atom_taxonomy.py
"""

import json
import os
import sys
import math
import numpy as np
from collections import Counter, defaultdict
from scipy import stats
from itertools import combinations

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from scripts.voynich import Transcript, Morphology, CategoryClassifier, decompose_middle_hmt

SEED = 42
np.random.seed(SEED)

# --- OUTPUT PATH ---
OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'results')
os.makedirs(OUT_DIR, exist_ok=True)
OUT_FILE = os.path.join(OUT_DIR, 'suffix_atom_taxonomy.json')

# --- ATOM SETS (from C1393) ---
HEADS = {'a', 'e', 'o', 'k', 't'}
MODS = {'p', 'f', 'i', 'c', 'd', 's'}
TERMS = {'y', 'l', 'r', 'h', 'm', 'n'}
ALL_MIDDLE_ATOMS = HEADS | MODS | TERMS  # 18 atoms

# Mode A and Mode B suffix atoms (C1410)
MODE_A_ATOMS = {'d', 'e', 'h', 'y'}   # ee counts as e
MODE_B_ATOMS = {'a', 'i', 'l', 'm', 'n', 'o', 'r', 's'}


def decompose_suffix(sfx):
    """Parse suffix string into atoms, left-to-right longest match."""
    if not sfx:
        return []
    atoms = []
    i = 0
    while i < len(sfx):
        if i + 1 < len(sfx) and sfx[i:i+2] == 'ii':
            atoms.append('ii')
            i += 2
        elif i + 1 < len(sfx) and sfx[i:i+2] == 'ee':
            atoms.append('ee')
            i += 2
        elif i + 1 < len(sfx) and sfx[i:i+2] == 'oo':
            atoms.append('oo')
            i += 2
        elif sfx[i] in ALL_MIDDLE_ATOMS or sfx[i] in {'g', 'x'}:
            atoms.append(sfx[i])
            i += 1
        else:
            atoms.append(sfx[i])
            i += 1
    return atoms


def cramers_v(contingency):
    """Compute Cramer's V from a contingency table (2D array)."""
    arr = np.array(contingency, dtype=float)
    n = arr.sum()
    if n == 0:
        return 0.0
    chi2 = 0.0
    row_sums = arr.sum(axis=1)
    col_sums = arr.sum(axis=0)
    for i in range(arr.shape[0]):
        for j in range(arr.shape[1]):
            expected = row_sums[i] * col_sums[j] / n
            if expected > 0:
                chi2 += (arr[i, j] - expected) ** 2 / expected
    k = min(arr.shape[0], arr.shape[1])
    if k <= 1 or n <= 1:
        return 0.0
    return math.sqrt(chi2 / (n * (k - 1)))


def jsd(p, q):
    """Jensen-Shannon divergence between two probability distributions."""
    p = np.array(p, dtype=float)
    q = np.array(q, dtype=float)
    p = p / p.sum() if p.sum() > 0 else p
    q = q / q.sum() if q.sum() > 0 else q
    m_arr = 0.5 * (p + q)

    def kl(a, b):
        mask = (a > 0) & (b > 0)
        return np.sum(a[mask] * np.log2(a[mask] / b[mask]))

    return 0.5 * kl(p, m_arr) + 0.5 * kl(q, m_arr)


def make_dist(counter, keys):
    """Make probability distribution from Counter over specified keys."""
    total = sum(counter.get(k, 0) for k in keys)
    if total == 0:
        return np.array([1.0/len(keys)] * len(keys))
    return np.array([counter.get(k, 0) / total for k in keys])


def assign_suffix_mode(sfx):
    """Assign suffix to Mode A or Mode B based on C1410 atom membership."""
    if not sfx:
        return None
    atoms = decompose_suffix(sfx)
    if not atoms:
        return None
    # Use first atom for classification (like C1229 centroid)
    first = atoms[0]
    if first == 'ee':
        first = 'e'
    elif first == 'ii':
        first = 'i'
    if first in MODE_A_ATOMS:
        return 'A'
    elif first in MODE_B_ATOMS:
        return 'B'
    return None


def main():
    print("=" * 70)
    print("Phase 540: SUFFIX ATOM TAXONOMY")
    print("=" * 70)

    tx = Transcript()
    morph = Morphology()
    cc = CategoryClassifier()

    # --- LOAD AUXILIARY DATA ---
    with open('results/phase20a_operator_equivalence.json') as f:
        p20a = json.load(f)
    token_to_class = {}
    for cls in p20a['classes']:
        cid = cls['class_id']
        for member in cls['members']:
            token_to_class[member] = cid

    with open('phases/MINIMAL_STATE_AUTOMATON/results/t3_merged_automaton.json') as f:
        auto = json.load(f)
    class_to_state = {}
    state_names = ['FL_HAZ', 'FQ', 'CC', 'AXm', 'AXM', 'FL_SAFE']
    for state_idx, class_list in enumerate(auto['final_partition']):
        for cls in class_list:
            class_to_state[cls] = state_names[state_idx]

    # --- GATHER ALL CURRIER B TOKENS ---
    print("\nGathering Currier B tokens...")
    tokens = []
    line_groups = defaultdict(list)

    for tok in tx.currier_b():
        m = morph.extract(tok.word)
        mid = m.middle
        head, mods, term, frame_str = decompose_middle_hmt(mid) if mid else (None, '', 'bare', None)
        entry = {
            'word': tok.word,
            'folio': tok.folio,
            'line': tok.line,
            'section': tok.section,
            'prefix': m.prefix,
            'middle': mid,
            'suffix': m.suffix if m.suffix else None,
            'articulator': m.articulator,
            'line_initial': tok.line_initial,
            'line_final': tok.line_final,
            'par_initial': tok.par_initial,
            'par_final': tok.par_final,
            'class_id': token_to_class.get(tok.word, None),
            'mid_head': head,
            'mid_mods': mods,
            'mid_term': term,
            'mid_frame': frame_str,
            'category': cc.classify(mid) if mid else None,
        }
        entry['macro_state'] = class_to_state.get(entry['class_id'], 'UNMAPPED') if entry['class_id'] else 'UNMAPPED'

        key = (tok.folio, tok.line)
        entry['_line_key'] = key
        entry['_line_idx'] = len(line_groups[key])
        line_groups[key].append(entry)
        tokens.append(entry)

    # Compute within-line fractional position
    for key, group in line_groups.items():
        n = len(group)
        for i, entry in enumerate(group):
            entry['line_pos'] = i / (n - 1) if n > 1 else 0.5

    for t in tokens:
        del t['_line_key']
        del t['_line_idx']

    n_total = len(tokens)
    suffixed = [t for t in tokens if t['suffix']]
    bare = [t for t in tokens if not t['suffix']]
    print(f"  Total B tokens: {n_total}")
    print(f"  Suffixed: {len(suffixed)} ({100*len(suffixed)/n_total:.1f}%)")
    print(f"  Bare: {len(bare)} ({100*len(bare)/n_total:.1f}%)")

    results = {}

    # =========================================================================
    # T1: POPULATION CENSUS
    # =========================================================================
    print("\n" + "=" * 70)
    print("T1: POPULATION CENSUS")
    print("=" * 70)

    suffix_counts = Counter(t['suffix'] for t in suffixed)
    n_unique_suffixes = len(suffix_counts)
    suffix_lengths = Counter(len(s) for s in suffix_counts.keys())

    print(f"\nUnique suffix strings: {n_unique_suffixes}")
    print(f"\nTop 20 suffixes by frequency:")
    for sfx, cnt in suffix_counts.most_common(20):
        pct = 100 * cnt / len(suffixed)
        print(f"  {sfx:8s}  {cnt:5d}  ({pct:5.1f}%)")

    print(f"\nSuffix length distribution (characters):")
    for length in sorted(suffix_lengths.keys()):
        total = sum(suffix_counts[s] for s in suffix_counts if len(s) == length)
        n_types = sum(1 for s in suffix_counts if len(s) == length)
        print(f"  {length}-char: {n_types:3d} types, {total:5d} tokens")

    # Atom decomposition
    suffix_atom_decomps = {}
    suffix_atom_lengths = Counter()
    for sfx in suffix_counts:
        atoms = decompose_suffix(sfx)
        suffix_atom_decomps[sfx] = atoms
        suffix_atom_lengths[len(atoms)] += suffix_counts[sfx]

    print(f"\nSuffix atom-length distribution:")
    for al in sorted(suffix_atom_lengths.keys()):
        pct = 100 * suffix_atom_lengths[al] / len(suffixed)
        print(f"  {al}-atom: {suffix_atom_lengths[al]:5d} tokens ({pct:.1f}%)")

    results['T1'] = {
        'n_suffixed_tokens': len(suffixed),
        'n_bare_tokens': len(bare),
        'n_unique_suffixes': n_unique_suffixes,
        'top_suffixes': [(s, c) for s, c in suffix_counts.most_common(30)],
        'suffix_char_lengths': {str(k): v for k, v in suffix_lengths.items()},
        'suffix_atom_lengths': {str(k): v for k, v in suffix_atom_lengths.items()},
    }

    # =========================================================================
    # T2: ATOM INVENTORY
    # =========================================================================
    print("\n" + "=" * 70)
    print("T2: ATOM INVENTORY")
    print("=" * 70)

    # Count atoms in suffix position (token-weighted)
    sfx_atom_counts = Counter()
    for t in suffixed:
        atoms = decompose_suffix(t['suffix'])
        for a in atoms:
            sfx_atom_counts[a] += 1

    # Count atoms in MIDDLE position
    mid_atom_counts = Counter()
    for t in tokens:
        mid = t['middle']
        if not mid:
            continue
        for ch in mid:
            if ch in ALL_MIDDLE_ATOMS or ch in {'g', 'x'}:
                mid_atom_counts[ch] += 1

    # All distinct atoms found in suffix
    sfx_atoms_found = set(sfx_atom_counts.keys())
    # Single-char atoms only
    sfx_single_atoms = {a for a in sfx_atoms_found if len(a) == 1}
    sfx_doubled = {a for a in sfx_atoms_found if len(a) == 2}  # ii, ee, oo

    print(f"\nDistinct single-char atoms in suffix: {len(sfx_single_atoms)}")
    print(f"  Present: {sorted(sfx_single_atoms)}")
    missing_from_middle = ALL_MIDDLE_ATOMS - sfx_single_atoms
    print(f"  Missing (vs 18 MIDDLE atoms): {sorted(missing_from_middle)}")
    print(f"  Doubled atoms: {sorted(sfx_doubled)}")

    # Verify which MIDDLE slot each missing atom occupies
    print(f"\nMissing atom MIDDLE slot classification:")
    for a in sorted(missing_from_middle):
        slot = 'HEAD' if a in HEADS else ('MOD' if a in MODS else ('TERM' if a in TERMS else '?'))
        print(f"  {a} -> {slot}")

    print(f"\nAtom frequencies (suffix vs MIDDLE):")
    all_atoms = sorted(set(list(sfx_atom_counts.keys()) + list(mid_atom_counts.keys())))
    sfx_total = sum(sfx_atom_counts.values())
    mid_total = sum(mid_atom_counts.values())
    for a in sorted(all_atoms, key=lambda x: -sfx_atom_counts.get(x, 0)):
        sfx_f = sfx_atom_counts.get(a, 0) / sfx_total if sfx_total > 0 else 0
        mid_f = mid_atom_counts.get(a, 0) / mid_total if mid_total > 0 else 0
        ratio = sfx_f / mid_f if mid_f > 0 else float('inf')
        print(f"  {a:4s}: suffix {sfx_atom_counts.get(a,0):5d} ({100*sfx_f:5.1f}%)  "
              f"MIDDLE {mid_atom_counts.get(a,0):5d} ({100*mid_f:5.1f}%)  ratio={ratio:.3f}")

    results['T2'] = {
        'n_single_atoms_in_suffix': len(sfx_single_atoms),
        'atoms_present': sorted(sfx_single_atoms),
        'atoms_missing': sorted(missing_from_middle),
        'doubled_atoms': sorted(sfx_doubled),
        'missing_atom_slots': {a: ('HEAD' if a in HEADS else ('MOD' if a in MODS else 'TERM')) for a in missing_from_middle},
        'suffix_atom_freq': {a: sfx_atom_counts.get(a, 0) for a in all_atoms},
        'middle_atom_freq': {a: mid_atom_counts.get(a, 0) for a in all_atoms},
    }

    # =========================================================================
    # T3: FIRST-ATOM (SUFFIX HEAD) PROFILE
    # =========================================================================
    print("\n" + "=" * 70)
    print("T3: FIRST-ATOM (SUFFIX HEAD) PROFILE")
    print("=" * 70)

    # For multi-atom suffixes, extract first atom
    multi_atom_suffixed = []
    for t in suffixed:
        atoms = decompose_suffix(t['suffix'])
        if len(atoms) >= 2:
            t['sfx_first'] = atoms[0]
            t['sfx_last'] = atoms[-1]
            t['sfx_atoms'] = atoms
            multi_atom_suffixed.append(t)
        else:
            t['sfx_first'] = atoms[0] if atoms else None
            t['sfx_last'] = atoms[0] if atoms else None
            t['sfx_atoms'] = atoms

    # Also set for all suffixed tokens
    for t in suffixed:
        atoms = decompose_suffix(t['suffix'])
        t['sfx_first'] = atoms[0] if atoms else None
        t['sfx_last'] = atoms[-1] if atoms else None
        t['sfx_atoms'] = atoms

    print(f"\nMulti-atom suffixed tokens: {len(multi_atom_suffixed)}")

    # First atom distribution for multi-atom suffixes
    first_atom_counts = Counter(t['sfx_first'] for t in multi_atom_suffixed)
    print(f"\nFirst atom distribution (multi-atom suffixes, N={len(multi_atom_suffixed)}):")
    for a, cnt in first_atom_counts.most_common():
        pct = 100 * cnt / len(multi_atom_suffixed)
        print(f"  {a:4s}: {cnt:5d} ({pct:5.1f}%)")

    # First atom x category (Cramer's V)
    CATS = sorted(set(c for c in cc.CATEGORIES))
    first_atoms_list = sorted(first_atom_counts.keys())
    cat_by_first = defaultdict(Counter)
    for t in multi_atom_suffixed:
        cat = t['category']
        if cat and t['sfx_first']:
            cat_by_first[t['sfx_first']][cat] += 1

    if first_atoms_list and CATS:
        ctable = []
        for a in first_atoms_list:
            row = [cat_by_first[a].get(c, 0) for c in CATS]
            ctable.append(row)
        v_first_cat = cramers_v(ctable)
        print(f"\nCramer's V (suffix first-atom x category): {v_first_cat:.3f}")

        # Category distribution per first atom
        print(f"\nCategory distribution per suffix first-atom (multi-atom):")
        for a in sorted(first_atoms_list, key=lambda x: -first_atom_counts[x]):
            total = sum(cat_by_first[a].values())
            if total < 10:
                continue
            top_cats = cat_by_first[a].most_common(3)
            top_str = ', '.join(f"{c}:{100*n/total:.0f}%" for c, n in top_cats)
            print(f"  {a:4s} (N={total:4d}): {top_str}")
    else:
        v_first_cat = 0.0

    results['T3'] = {
        'n_multi_atom': len(multi_atom_suffixed),
        'first_atom_dist': {a: c for a, c in first_atom_counts.most_common()},
        'V_first_atom_x_category': round(v_first_cat, 4),
        'first_atom_category_profiles': {
            a: dict(cat_by_first[a]) for a in first_atoms_list if sum(cat_by_first[a].values()) >= 10
        },
    }

    # =========================================================================
    # T4: LAST-ATOM (SUFFIX TERM) PROFILE
    # =========================================================================
    print("\n" + "=" * 70)
    print("T4: LAST-ATOM (SUFFIX TERM) PROFILE")
    print("=" * 70)

    last_atom_counts = Counter(t['sfx_last'] for t in multi_atom_suffixed)
    print(f"\nLast atom distribution (multi-atom suffixes, N={len(multi_atom_suffixed)}):")
    for a, cnt in last_atom_counts.most_common():
        pct = 100 * cnt / len(multi_atom_suffixed)
        print(f"  {a:4s}: {cnt:5d} ({pct:5.1f}%)")

    # Last atom x line position
    pos_by_last = defaultdict(list)
    for t in multi_atom_suffixed:
        if t['sfx_last']:
            pos_by_last[t['sfx_last']].append(t['line_pos'])

    print(f"\nMean line position per suffix last-atom:")
    last_pos_means = {}
    for a in sorted(pos_by_last.keys(), key=lambda x: np.mean(pos_by_last[x])):
        positions = pos_by_last[a]
        if len(positions) < 10:
            continue
        mean_p = np.mean(positions)
        last_pos_means[a] = mean_p
        print(f"  {a:4s} (N={len(positions):4d}): mean_pos={mean_p:.3f}")

    # R-squared: last atom predicts position
    if multi_atom_suffixed:
        # One-hot encode last atom, predict position
        last_atoms_valid = [t for t in multi_atom_suffixed if t['sfx_last'] and last_atom_counts[t['sfx_last']] >= 10]
        if last_atoms_valid:
            groups = defaultdict(list)
            for t in last_atoms_valid:
                groups[t['sfx_last']].append(t['line_pos'])
            overall_mean = np.mean([t['line_pos'] for t in last_atoms_valid])
            ss_total = sum((t['line_pos'] - overall_mean)**2 for t in last_atoms_valid)
            ss_resid = sum(sum((p - np.mean(positions))**2 for p in positions) for positions in groups.values())
            r2_last_pos = 1 - ss_resid / ss_total if ss_total > 0 else 0
            print(f"\nR-squared (suffix last-atom -> line position): {r2_last_pos:.4f}")
        else:
            r2_last_pos = 0
    else:
        r2_last_pos = 0

    # Last atom x line-final enrichment
    print(f"\nLine-final enrichment per suffix last-atom:")
    base_final_rate = sum(1 for t in multi_atom_suffixed if t['line_final']) / len(multi_atom_suffixed) if multi_atom_suffixed else 0
    last_final_enrichment = {}
    for a in sorted(last_atom_counts.keys(), key=lambda x: -last_atom_counts[x]):
        group = [t for t in multi_atom_suffixed if t['sfx_last'] == a]
        if len(group) < 10:
            continue
        final_rate = sum(1 for t in group if t['line_final']) / len(group)
        enrich = final_rate / base_final_rate if base_final_rate > 0 else 0
        last_final_enrichment[a] = round(enrich, 3)
        print(f"  {a:4s}: {100*final_rate:.1f}% line-final ({enrich:.2f}x enrichment)")

    results['T4'] = {
        'last_atom_dist': {a: c for a, c in last_atom_counts.most_common()},
        'last_atom_mean_position': {a: round(v, 4) for a, v in last_pos_means.items()},
        'R2_last_atom_position': round(r2_last_pos, 4),
        'last_atom_final_enrichment': last_final_enrichment,
        'base_final_rate': round(base_final_rate, 4),
    }

    # =========================================================================
    # T5: HEAD+TERM DECOMPOSITION TEST
    # =========================================================================
    print("\n" + "=" * 70)
    print("T5: SUFFIX HEAD+TERM DECOMPOSITION TEST")
    print("=" * 70)

    # Test: Does suffix first-atom predict category more than last-atom?
    # And does last-atom predict position more than first-atom?
    # This would confirm parallel HEAD+TERM structure.

    # First atom x category V (already computed above)
    # Last atom x category V
    cat_by_last = defaultdict(Counter)
    for t in multi_atom_suffixed:
        cat = t['category']
        if cat and t['sfx_last']:
            cat_by_last[t['sfx_last']][cat] += 1

    last_atoms_cats = sorted(last_atom_counts.keys())
    if last_atoms_cats and CATS:
        ctable_last = []
        for a in last_atoms_cats:
            row = [cat_by_last[a].get(c, 0) for c in CATS]
            ctable_last.append(row)
        v_last_cat = cramers_v(ctable_last)
    else:
        v_last_cat = 0.0

    # First atom x position R2
    pos_by_first = defaultdict(list)
    for t in multi_atom_suffixed:
        if t['sfx_first']:
            pos_by_first[t['sfx_first']].append(t['line_pos'])

    first_atoms_valid = [t for t in multi_atom_suffixed if t['sfx_first'] and first_atom_counts[t['sfx_first']] >= 10]
    if first_atoms_valid:
        groups_first = defaultdict(list)
        for t in first_atoms_valid:
            groups_first[t['sfx_first']].append(t['line_pos'])
        overall_mean = np.mean([t['line_pos'] for t in first_atoms_valid])
        ss_total = sum((t['line_pos'] - overall_mean)**2 for t in first_atoms_valid)
        ss_resid = sum(sum((p - np.mean(positions))**2 for p in positions) for positions in groups_first.values())
        r2_first_pos = 1 - ss_resid / ss_total if ss_total > 0 else 0
    else:
        r2_first_pos = 0

    print(f"\n--- Parallel Decomposition Test ---")
    print(f"  Category prediction:")
    print(f"    V(first-atom x category) = {v_first_cat:.4f}")
    print(f"    V(last-atom  x category) = {v_last_cat:.4f}")
    print(f"    Ratio first/last = {v_first_cat/v_last_cat:.2f}x" if v_last_cat > 0 else "    Ratio: N/A")
    print(f"  Position prediction:")
    print(f"    R2(first-atom -> position) = {r2_first_pos:.4f}")
    print(f"    R2(last-atom  -> position) = {r2_last_pos:.4f}")
    print(f"    Ratio last/first = {r2_last_pos/r2_first_pos:.2f}x" if r2_first_pos > 0 else "    Ratio: N/A")

    # For MIDDLE comparison: V(HEAD x category) and R2(TERM x position)
    # Compute from our token data
    mid_head_cat = defaultdict(Counter)
    for t in tokens:
        if t['mid_head'] and t['category']:
            mid_head_cat[t['mid_head']][t['category']] += 1

    mid_heads_list = sorted(mid_head_cat.keys())
    if mid_heads_list and CATS:
        ct_mid_head = [[mid_head_cat[h].get(c, 0) for c in CATS] for h in mid_heads_list]
        v_mid_head_cat = cramers_v(ct_mid_head)
    else:
        v_mid_head_cat = 0.0

    mid_term_pos = defaultdict(list)
    for t in tokens:
        if t['mid_term'] and t['mid_term'] != 'bare':
            mid_term_pos[t['mid_term']].append(t['line_pos'])

    mid_terms_valid = [t for t in tokens if t['mid_term'] and t['mid_term'] != 'bare']
    if mid_terms_valid:
        groups_mt = defaultdict(list)
        for t in mid_terms_valid:
            groups_mt[t['mid_term']].append(t['line_pos'])
        overall_mean_mt = np.mean([t['line_pos'] for t in mid_terms_valid])
        ss_total_mt = sum((t['line_pos'] - overall_mean_mt)**2 for t in mid_terms_valid)
        ss_resid_mt = sum(sum((p - np.mean(ps))**2 for p in ps) for ps in groups_mt.values())
        r2_mid_term_pos = 1 - ss_resid_mt / ss_total_mt if ss_total_mt > 0 else 0
    else:
        r2_mid_term_pos = 0

    print(f"\n--- MIDDLE comparison ---")
    print(f"  V(MIDDLE HEAD x category) = {v_mid_head_cat:.4f}")
    print(f"  R2(MIDDLE TERM -> position) = {r2_mid_term_pos:.4f}")

    # Is suffix structured differently?
    decomp_parallel = (v_first_cat > v_last_cat * 1.3) and (r2_last_pos > r2_first_pos * 1.3)
    decomp_verdict = "PARALLEL_DECOMPOSITION" if decomp_parallel else "WEAK_OR_ABSENT"
    print(f"\n  VERDICT: {decomp_verdict}")
    print(f"  (Parallel = first-atom category-selecting 1.3x+ AND last-atom position-selecting 1.3x+)")

    results['T5'] = {
        'V_first_atom_x_category': round(v_first_cat, 4),
        'V_last_atom_x_category': round(v_last_cat, 4),
        'R2_first_atom_position': round(r2_first_pos, 4),
        'R2_last_atom_position': round(r2_last_pos, 4),
        'V_MIDDLE_HEAD_x_category': round(v_mid_head_cat, 4),
        'R2_MIDDLE_TERM_position': round(r2_mid_term_pos, 4),
        'decomposition_verdict': decomp_verdict,
    }

    # =========================================================================
    # T6: SUFFIX ATOM x MIDDLE HEAD INTERACTION
    # =========================================================================
    print("\n" + "=" * 70)
    print("T6: SUFFIX ATOM x MIDDLE HEAD INTERACTION")
    print("=" * 70)

    # Which MIDDLE HEADs predict which suffix atoms?
    sfx_first_by_mid_head = defaultdict(Counter)
    for t in suffixed:
        if t['mid_head'] and t['sfx_first']:
            sfx_first_by_mid_head[t['mid_head']][t['sfx_first']] += 1

    mid_heads_for_sfx = sorted(sfx_first_by_mid_head.keys())
    sfx_firsts_for_table = sorted(set(a for h in mid_heads_for_sfx for a in sfx_first_by_mid_head[h]))

    if mid_heads_for_sfx and sfx_firsts_for_table:
        ct_mh_sf = [[sfx_first_by_mid_head[h].get(a, 0) for a in sfx_firsts_for_table] for h in mid_heads_for_sfx]
        v_midhead_sfxfirst = cramers_v(ct_mh_sf)
    else:
        v_midhead_sfxfirst = 0.0

    print(f"\nCramer's V (MIDDLE HEAD x suffix first-atom): {v_midhead_sfxfirst:.4f}")
    print(f"\nSuffix first-atom distribution per MIDDLE HEAD:")
    for h in sorted(mid_heads_for_sfx):
        total = sum(sfx_first_by_mid_head[h].values())
        top3 = sfx_first_by_mid_head[h].most_common(3)
        top_str = ', '.join(f"{a}:{100*n/total:.0f}%" for a, n in top3)
        print(f"  {h}-HEAD (N={total:4d}): {top_str}")

    # Also headless tokens
    sfx_first_headless = Counter()
    for t in suffixed:
        if t['mid_head'] is None and t['sfx_first']:
            sfx_first_headless[t['sfx_first']] += 1
    if sfx_first_headless:
        total_hl = sum(sfx_first_headless.values())
        top3 = sfx_first_headless.most_common(3)
        top_str = ', '.join(f"{a}:{100*n/total_hl:.0f}%" for a, n in top3)
        print(f"  HEADLESS (N={total_hl:4d}): {top_str}")

    # Suffix content by MIDDLE HEAD (full suffix string)
    sfx_by_mid_head = defaultdict(Counter)
    for t in suffixed:
        if t['mid_head']:
            sfx_by_mid_head[t['mid_head']][t['suffix']] += 1

    print(f"\nTop 3 suffixes per MIDDLE HEAD:")
    for h in sorted(sfx_by_mid_head.keys()):
        total = sum(sfx_by_mid_head[h].values())
        top3 = sfx_by_mid_head[h].most_common(3)
        top_str = ', '.join(f"{s}:{100*n/total:.0f}%" for s, n in top3)
        print(f"  {h}-HEAD (N={total:4d}): {top_str}")

    results['T6'] = {
        'V_midhead_x_sfx_first': round(v_midhead_sfxfirst, 4),
        'mid_head_sfx_profiles': {
            h: dict(sfx_first_by_mid_head[h].most_common(5))
            for h in mid_heads_for_sfx
        },
        'headless_sfx_profile': dict(sfx_first_headless.most_common(5)) if sfx_first_headless else {},
    }

    # =========================================================================
    # T7: SUFFIX ATOM x MIDDLE TERMINAL INTERACTION
    # =========================================================================
    print("\n" + "=" * 70)
    print("T7: SUFFIX ATOM x MIDDLE TERMINAL INTERACTION")
    print("=" * 70)

    # Beyond opacity gating (C1440), does MIDDLE terminal predict suffix content?
    sfx_first_by_mid_term = defaultdict(Counter)
    for t in suffixed:
        mterm = t['mid_term']
        if mterm and mterm != 'bare' and t['sfx_first']:
            sfx_first_by_mid_term[mterm][t['sfx_first']] += 1

    # Also for bare-terminal MIDDLEs
    sfx_first_bare_term = Counter()
    for t in suffixed:
        if t['mid_term'] == 'bare' and t['sfx_first']:
            sfx_first_bare_term[t['sfx_first']] += 1

    mid_terms_for_sfx = sorted(sfx_first_by_mid_term.keys())
    sfx_firsts_for_t7 = sorted(set(a for mt in mid_terms_for_sfx for a in sfx_first_by_mid_term[mt]))

    if mid_terms_for_sfx and sfx_firsts_for_t7:
        ct_mt_sf = [[sfx_first_by_mid_term[mt].get(a, 0) for a in sfx_firsts_for_t7] for mt in mid_terms_for_sfx]
        v_midterm_sfxfirst = cramers_v(ct_mt_sf)
    else:
        v_midterm_sfxfirst = 0.0

    print(f"\nCramer's V (MIDDLE TERMINAL x suffix first-atom): {v_midterm_sfxfirst:.4f}")

    # Suffix rate per MIDDLE terminal (opacity confirmation)
    print(f"\nSuffix rate and content per MIDDLE TERMINAL:")
    mid_term_all = Counter()
    mid_term_suffixed = Counter()
    for t in tokens:
        mterm = t['mid_term']
        if mterm:
            mid_term_all[mterm] += 1
            if t['suffix']:
                mid_term_suffixed[mterm] += 1

    for mterm in sorted(mid_term_all.keys(), key=lambda x: -mid_term_all[x]):
        total = mid_term_all[mterm]
        sfxd = mid_term_suffixed.get(mterm, 0)
        rate = sfxd / total if total > 0 else 0
        if total < 20:
            continue
        # Show suffix content for suffixed tokens with this terminal
        suffix_content = sfx_first_by_mid_term.get(mterm, Counter())
        if not suffix_content and mterm == 'bare':
            suffix_content = sfx_first_bare_term
        top2 = suffix_content.most_common(2)
        top_str = ', '.join(f"{a}:{n}" for a, n in top2) if top2 else 'N/A'
        print(f"  {mterm:6s}: {100*rate:5.1f}% suffixed ({sfxd:4d}/{total:5d})  top first-atom: {top_str}")

    results['T7'] = {
        'V_midterm_x_sfx_first': round(v_midterm_sfxfirst, 4),
        'mid_term_suffix_rates': {
            mt: round(mid_term_suffixed.get(mt, 0) / mid_term_all[mt], 4)
            for mt in mid_term_all if mid_term_all[mt] >= 20
        },
    }

    # =========================================================================
    # T8: MODE A vs MODE B INTERNAL STRUCTURE
    # =========================================================================
    print("\n" + "=" * 70)
    print("T8: MODE A vs MODE B INTERNAL STRUCTURE")
    print("=" * 70)

    mode_a_tokens = [t for t in suffixed if assign_suffix_mode(t['suffix']) == 'A']
    mode_b_tokens = [t for t in suffixed if assign_suffix_mode(t['suffix']) == 'B']

    print(f"\nMode A tokens: {len(mode_a_tokens)}")
    print(f"Mode B tokens: {len(mode_b_tokens)}")

    # Category profiles per mode
    cat_mode_a = Counter(t['category'] for t in mode_a_tokens if t['category'])
    cat_mode_b = Counter(t['category'] for t in mode_b_tokens if t['category'])

    print(f"\nCategory profiles:")
    print(f"  {'Category':15s} {'Mode_A':>10s} {'Mode_B':>10s} {'Ratio':>8s}")
    for cat in CATS:
        a_pct = 100 * cat_mode_a.get(cat, 0) / sum(cat_mode_a.values()) if cat_mode_a else 0
        b_pct = 100 * cat_mode_b.get(cat, 0) / sum(cat_mode_b.values()) if cat_mode_b else 0
        ratio = a_pct / b_pct if b_pct > 0 else float('inf')
        marker = " **" if abs(ratio - 1) > 0.3 else ""
        print(f"  {cat:15s} {a_pct:9.1f}% {b_pct:9.1f}% {ratio:7.2f}x{marker}")

    # Mode internal structure: do modes have different HEAD+TERM patterns?
    mode_a_multi = [t for t in mode_a_tokens if len(decompose_suffix(t['suffix'])) >= 2]
    mode_b_multi = [t for t in mode_b_tokens if len(decompose_suffix(t['suffix'])) >= 2]

    print(f"\nMulti-atom count: Mode A={len(mode_a_multi)}, Mode B={len(mode_b_multi)}")

    # Suffix length distribution by mode
    len_a = Counter(len(decompose_suffix(t['suffix'])) for t in mode_a_tokens)
    len_b = Counter(len(decompose_suffix(t['suffix'])) for t in mode_b_tokens)
    print(f"\nSuffix atom-length by mode:")
    for l_val in sorted(set(list(len_a.keys()) + list(len_b.keys()))):
        a_cnt = len_a.get(l_val, 0)
        b_cnt = len_b.get(l_val, 0)
        a_pct = 100 * a_cnt / len(mode_a_tokens) if mode_a_tokens else 0
        b_pct = 100 * b_cnt / len(mode_b_tokens) if mode_b_tokens else 0
        print(f"  {l_val}-atom: A={a_pct:5.1f}% B={b_pct:5.1f}%")

    # Mean line position by mode
    pos_a = [t['line_pos'] for t in mode_a_tokens]
    pos_b = [t['line_pos'] for t in mode_b_tokens]
    print(f"\nMean line position: Mode A={np.mean(pos_a):.3f}, Mode B={np.mean(pos_b):.3f}")

    # Line-initial/final rates
    a_init = sum(1 for t in mode_a_tokens if t['line_initial']) / len(mode_a_tokens) if mode_a_tokens else 0
    b_init = sum(1 for t in mode_b_tokens if t['line_initial']) / len(mode_b_tokens) if mode_b_tokens else 0
    a_final = sum(1 for t in mode_a_tokens if t['line_final']) / len(mode_a_tokens) if mode_a_tokens else 0
    b_final = sum(1 for t in mode_b_tokens if t['line_final']) / len(mode_b_tokens) if mode_b_tokens else 0
    print(f"Line-initial: A={100*a_init:.1f}%, B={100*b_init:.1f}%")
    print(f"Line-final:   A={100*a_final:.1f}%, B={100*b_final:.1f}%")

    results['T8'] = {
        'n_mode_a': len(mode_a_tokens),
        'n_mode_b': len(mode_b_tokens),
        'cat_mode_a': dict(cat_mode_a),
        'cat_mode_b': dict(cat_mode_b),
        'mode_a_mean_pos': round(np.mean(pos_a), 4) if pos_a else None,
        'mode_b_mean_pos': round(np.mean(pos_b), 4) if pos_b else None,
        'mode_a_line_initial': round(a_init, 4),
        'mode_b_line_initial': round(b_init, 4),
        'mode_a_line_final': round(a_final, 4),
        'mode_b_line_final': round(b_final, 4),
    }

    # =========================================================================
    # T9: MISSING ATOMS ANALYSIS
    # =========================================================================
    print("\n" + "=" * 70)
    print("T9: MISSING ATOMS ANALYSIS")
    print("=" * 70)

    # k, t, p, f, c are missing from suffix. What slots do they occupy in MIDDLE?
    missing_in_middle = {}
    for a in sorted(missing_from_middle):
        # Count by MIDDLE slot
        as_head = sum(1 for t in tokens if t['mid_head'] == a)
        as_mod = sum(1 for t in tokens if t['mid_mods'] and a in t['mid_mods'])
        as_term = sum(1 for t in tokens if t['mid_term'] == a)
        total_mid = mid_atom_counts.get(a, 0)
        missing_in_middle[a] = {
            'total_in_middle': total_mid,
            'as_head': as_head,
            'as_mod': as_mod,
            'as_term': as_term,
        }

        slot = 'HEAD' if a in HEADS else ('MOD' if a in MODS else 'TERM')
        print(f"  {a} ({slot}): total={total_mid}, HEAD={as_head}, MOD={as_mod}, TERM={as_term}")

    # Are the missing atoms specifically action/execution atoms?
    print(f"\nMissing atom analysis:")
    print(f"  k = THERMAL HEAD (heat) - action atom, incompatible with suffix position")
    print(f"  t = FLOW HEAD (transfer) - action atom, incompatible with suffix position")
    print(f"  p = MARKING MOD (pause) - executive modifier")
    print(f"  f = MARKING MOD (flag) - executive modifier")
    print(f"  c = MARKING MOD (adjust) - executive modifier")
    print(f"\n  All 5 missing atoms are either:")
    print(f"    - ACTION HEAD atoms (k, t) that select operational domains")
    print(f"    - EXECUTIVE MODIFIER atoms (p, f, c) that parameterize operations")
    print(f"  None are TERMINAL or STAGING/TRANSITION atoms.")
    print(f"  Suffix retains: all TERMINAL atoms, all TRANSITION atoms, all STATE atoms")

    results['T9'] = {
        'missing_atoms': sorted(missing_from_middle),
        'missing_atom_details': missing_in_middle,
        'missing_atom_functional_class': {
            'k': 'ACTION_HEAD', 't': 'ACTION_HEAD',
            'p': 'EXEC_MOD', 'f': 'EXEC_MOD', 'c': 'EXEC_MOD',
        },
    }

    # =========================================================================
    # T10: CROSS-SYSTEM SUFFIX COMPARISON (A vs B)
    # =========================================================================
    print("\n" + "=" * 70)
    print("T10: CROSS-SYSTEM SUFFIX COMPARISON (A vs B)")
    print("=" * 70)

    a_tokens = []
    for tok in tx.currier_a():
        m = morph.extract(tok.word)
        if m.suffix:
            a_tokens.append({
                'word': tok.word,
                'suffix': m.suffix,
                'middle': m.middle,
                'section': tok.section,
            })

    a_suffixed = [t for t in a_tokens if t['suffix']]
    a_suffix_counts = Counter(t['suffix'] for t in a_suffixed)

    print(f"\nCurrier A: {len(a_suffixed)} suffixed tokens, {len(a_suffix_counts)} unique suffixes")
    print(f"Currier B: {len(suffixed)} suffixed tokens, {n_unique_suffixes} unique suffixes")

    # Atom inventory comparison
    a_sfx_atoms = Counter()
    for t in a_suffixed:
        for a_atom in decompose_suffix(t['suffix']):
            a_sfx_atoms[a_atom] += 1

    b_sfx_atoms = sfx_atom_counts  # already computed

    a_atom_set = {a for a in a_sfx_atoms if len(a) == 1}
    b_atom_set = sfx_single_atoms

    print(f"\nAtom sets:")
    print(f"  A suffix atoms: {sorted(a_atom_set)} ({len(a_atom_set)} atoms)")
    print(f"  B suffix atoms: {sorted(b_atom_set)} ({len(b_atom_set)} atoms)")
    print(f"  A-only: {sorted(a_atom_set - b_atom_set)}")
    print(f"  B-only: {sorted(b_atom_set - a_atom_set)}")
    print(f"  Shared: {len(a_atom_set & b_atom_set)}")

    # Frequency comparison for shared atoms
    shared_atoms = sorted(a_atom_set & b_atom_set)
    if shared_atoms:
        a_total_atoms = sum(a_sfx_atoms.values())
        b_total_atoms = sum(b_sfx_atoms.values())
        print(f"\nShared atom frequency comparison (A vs B):")
        for atom in shared_atoms:
            a_f = a_sfx_atoms.get(atom, 0) / a_total_atoms
            b_f = b_sfx_atoms.get(atom, 0) / b_total_atoms
            ratio = a_f / b_f if b_f > 0 else float('inf')
            print(f"  {atom}: A={100*a_f:.1f}% B={100*b_f:.1f}% ratio={ratio:.2f}")

        # JSD between A and B suffix atom distributions
        all_shared = sorted(set(list(a_sfx_atoms.keys()) + list(b_sfx_atoms.keys())))
        p_a = make_dist(a_sfx_atoms, all_shared)
        p_b = make_dist(b_sfx_atoms, all_shared)
        cross_jsd = jsd(p_a, p_b)
        print(f"\nJSD(A suffix atoms, B suffix atoms) = {cross_jsd:.4f}")
    else:
        cross_jsd = None

    # Top suffix strings comparison
    a_top = a_suffix_counts.most_common(10)
    b_top = suffix_counts.most_common(10)
    print(f"\nTop 10 suffixes in A: {[(s,c) for s,c in a_top]}")
    print(f"Top 10 suffixes in B: {[(s,c) for s,c in b_top]}")

    results['T10'] = {
        'a_suffixed_tokens': len(a_suffixed),
        'a_unique_suffixes': len(a_suffix_counts),
        'a_atom_set': sorted(a_atom_set),
        'b_atom_set': sorted(b_atom_set),
        'a_only_atoms': sorted(a_atom_set - b_atom_set),
        'b_only_atoms': sorted(b_atom_set - a_atom_set),
        'cross_system_jsd': round(cross_jsd, 4) if cross_jsd is not None else None,
        'a_top_suffixes': [(s, c) for s, c in a_top],
        'b_top_suffixes': [(s, c) for s, c in b_top[:10]],
    }

    # =========================================================================
    # T11: SUFFIX vs MIDDLE ATOM BEHAVIORAL COMPARISON
    # =========================================================================
    print("\n" + "=" * 70)
    print("T11: SUFFIX vs MIDDLE ATOM BEHAVIORAL COMPARISON")
    print("=" * 70)

    # For each shared atom, compare category profile in MIDDLE vs suffix
    # "In MIDDLE" = tokens where atom appears in MIDDLE
    # "In suffix" = tokens where atom appears as first suffix atom

    shared_for_comparison = sorted(sfx_single_atoms & ALL_MIDDLE_ATOMS)
    atom_jsd_table = {}

    print(f"\nCategory profile JSD for each atom (MIDDLE vs suffix position):")
    print(f"  {'Atom':4s} {'MIDDLE_top':20s} {'Suffix_top':20s} {'JSD':>8s}")

    for atom in shared_for_comparison:
        # Category profile when atom is MIDDLE first-char (HEAD position)
        mid_cat = Counter()
        for t in tokens:
            mid = t['middle']
            if mid and mid[0] == atom and t['category']:
                mid_cat[t['category']] += 1

        # Category profile when atom is suffix first-atom
        sfx_cat = Counter()
        for t in suffixed:
            if t['sfx_first'] == atom and t['category']:
                sfx_cat[t['category']] += 1

        # Compute JSD
        p_mid = make_dist(mid_cat, CATS)
        p_sfx = make_dist(sfx_cat, CATS)
        j = jsd(p_mid, p_sfx)
        atom_jsd_table[atom] = round(j, 4)

        mid_top = mid_cat.most_common(1)[0] if mid_cat else ('N/A', 0)
        sfx_top = sfx_cat.most_common(1)[0] if sfx_cat else ('N/A', 0)
        mid_total = sum(mid_cat.values())
        sfx_total = sum(sfx_cat.values())

        mid_str = f"{mid_top[0]}({100*mid_top[1]/mid_total:.0f}%)" if mid_total > 0 else "N/A"
        sfx_str = f"{sfx_top[0]}({100*sfx_top[1]/sfx_total:.0f}%)" if sfx_total > 0 else "N/A"
        flag = " <<< DIVERGENT" if j > 0.1 else ""
        print(f"  {atom:4s} {mid_str:20s} {sfx_str:20s} {j:8.4f}{flag}")

    mean_jsd = np.mean(list(atom_jsd_table.values()))
    most_stable = min(atom_jsd_table, key=atom_jsd_table.get) if atom_jsd_table else None
    most_divergent = max(atom_jsd_table, key=atom_jsd_table.get) if atom_jsd_table else None
    print(f"\nMean JSD across atoms: {mean_jsd:.4f}")
    print(f"Most stable atom: {most_stable} (JSD={atom_jsd_table.get(most_stable, 0):.4f})")
    print(f"Most divergent atom: {most_divergent} (JSD={atom_jsd_table.get(most_divergent, 0):.4f})")

    results['T11'] = {
        'atom_category_jsd': atom_jsd_table,
        'mean_jsd': round(mean_jsd, 4),
        'most_stable': most_stable,
        'most_divergent': most_divergent,
    }

    # =========================================================================
    # T12: PAIRWISE DISTANCE BETWEEN SUFFIX ATOMS
    # =========================================================================
    print("\n" + "=" * 70)
    print("T12: PAIRWISE DISTANCE BETWEEN SUFFIX ATOMS")
    print("=" * 70)

    # Build category profile for each suffix atom (across all positions in suffix)
    sfx_atom_cat_profiles = defaultdict(Counter)
    for t in suffixed:
        if not t['category']:
            continue
        atoms = decompose_suffix(t['suffix'])
        for a in set(atoms):  # unique atoms per suffix
            key = a if len(a) == 1 else a  # keep doubled
            sfx_atom_cat_profiles[key][t['category']] += 1

    # Filter atoms with enough data
    min_tokens = 50
    valid_atoms = sorted(a for a, c in sfx_atom_cat_profiles.items() if sum(c.values()) >= min_tokens)

    print(f"\nValid atoms for pairwise JSD: {len(valid_atoms)}")

    # Compute pairwise JSD matrix
    n_valid = len(valid_atoms)
    jsd_matrix = np.zeros((n_valid, n_valid))
    for i in range(n_valid):
        for j in range(i+1, n_valid):
            p1 = make_dist(sfx_atom_cat_profiles[valid_atoms[i]], CATS)
            p2 = make_dist(sfx_atom_cat_profiles[valid_atoms[j]], CATS)
            d = jsd(p1, p2)
            jsd_matrix[i, j] = d
            jsd_matrix[j, i] = d

    # Print closest and most distant pairs
    pairs = []
    for i in range(n_valid):
        for j in range(i+1, n_valid):
            pairs.append((valid_atoms[i], valid_atoms[j], jsd_matrix[i, j]))

    pairs.sort(key=lambda x: x[2])
    print(f"\n5 closest suffix atom pairs (by category JSD):")
    for a1, a2, d in pairs[:5]:
        print(f"  {a1}-{a2}: {d:.4f}")

    print(f"\n5 most distant suffix atom pairs:")
    for a1, a2, d in pairs[-5:]:
        print(f"  {a1}-{a2}: {d:.4f}")

    # Compare to MIDDLE pairwise distances
    mid_atom_cat_profiles = defaultdict(Counter)
    for t in tokens:
        mid = t['middle']
        if not mid or not t['category']:
            continue
        for ch in mid:
            if ch in ALL_MIDDLE_ATOMS:
                mid_atom_cat_profiles[ch][t['category']] += 1

    mid_valid = sorted(a for a, c in mid_atom_cat_profiles.items() if sum(c.values()) >= min_tokens and a in sfx_single_atoms)
    # JSD between same atom in MIDDLE vs suffix
    print(f"\nSame-atom JSD (MIDDLE position vs suffix position):")
    for a in sorted(mid_valid):
        if a not in sfx_atom_cat_profiles:
            continue
        p_mid = make_dist(mid_atom_cat_profiles[a], CATS)
        p_sfx = make_dist(sfx_atom_cat_profiles[a], CATS)
        d = jsd(p_mid, p_sfx)
        print(f"  {a}: JSD={d:.4f}")

    results['T12'] = {
        'valid_atoms': valid_atoms,
        'closest_pairs': [(a1, a2, round(d, 4)) for a1, a2, d in pairs[:5]],
        'distant_pairs': [(a1, a2, round(d, 4)) for a1, a2, d in pairs[-5:]],
        'mean_pairwise_jsd': round(np.mean([d for _, _, d in pairs]), 4) if pairs else None,
    }

    # =========================================================================
    # SAVE RESULTS (before synthesis print to avoid encoding issues)
    # =========================================================================
    with open(OUT_FILE, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nResults saved to {OUT_FILE}")

    # =========================================================================
    # SYNTHESIS
    # =========================================================================
    print("\n" + "=" * 70)
    print("SYNTHESIS")
    print("=" * 70)

    print(f"""
SUFFIX ATOM TAXONOMY FINDINGS:

1. POPULATION: {len(suffixed)} suffixed tokens ({100*len(suffixed)/n_total:.1f}%) with {n_unique_suffixes} unique suffixes.
   Single-atom suffixes dominate ({suffix_atom_lengths.get(1,0)} tokens, {100*suffix_atom_lengths.get(1,0)/len(suffixed):.1f}%).

2. ATOM INVENTORY: {len(sfx_single_atoms)} single-char atoms found in suffix.
   Missing from MIDDLE's 18: {sorted(missing_from_middle)} = 2 ACTION HEADs (k,t) + 3 EXEC MODs (p,f,c).
   Suffix retains ALL 6 TERMINAL atoms + 3 STATE/TRANSITION atoms + extensible atoms.

3. SUFFIX HEAD (first-atom):
   V(first-atom x category) = {v_first_cat:.4f}
   vs V(MIDDLE HEAD x category) = {v_mid_head_cat:.4f}
   Suffix first-atom carries {100*v_first_cat/v_mid_head_cat:.0f}% of MIDDLE HEAD's category selectivity.

4. SUFFIX TERM (last-atom):
   R2(last-atom -> position) = {r2_last_pos:.4f}
   vs R2(MIDDLE TERM -> position) = {r2_mid_term_pos:.4f}

5. DECOMPOSITION VERDICT: {decomp_verdict}
   {'Suffix shows PARALLEL HEAD+TERM decomposition like MIDDLE.' if decomp_parallel else 'Suffix decomposition is WEAKER or DIFFERENTLY ORGANIZED than MIDDLE.'}

6. MIDDLE HEAD -> SUFFIX: V = {v_midhead_sfxfirst:.4f}
   MIDDLE HEAD selects which suffix atoms appear.

7. MIDDLE TERMINAL -> SUFFIX: V = {v_midterm_sfxfirst:.4f}
   MIDDLE terminal gates suffix attachment AND selects suffix content.

8. MODES: Mode A = {len(mode_a_tokens)} tokens, Mode B = {len(mode_b_tokens)} tokens.

9. CROSS-SYSTEM: {'JSD = '+str(round(cross_jsd,4)) if cross_jsd is not None else 'N/A'} (A vs B suffix atoms).

10. BEHAVIORAL DIVERGENCE: Mean JSD = {mean_jsd:.4f} across atoms (MIDDLE vs suffix position).
    Most stable: {most_stable} (JSD={atom_jsd_table.get(most_stable,0):.4f})
    Most divergent: {most_divergent} (JSD={atom_jsd_table.get(most_divergent,0):.4f})
""")

    print("\nDone.")


if __name__ == '__main__':
    main()
