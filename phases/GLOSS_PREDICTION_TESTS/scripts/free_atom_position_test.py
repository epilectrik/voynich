"""
FREE Atom Position Independence Test
=====================================
Tests whether k and t (the only FREE-position atoms per C1209) genuinely
behave the same regardless of where they appear in compound MIDDLEs.

Controls: e (HEAD atom, should be position-dependent) and h (TERMINAL atom,
should be position-dependent).

Method:
  For each atom, split compound MIDDLEs by atom position (FIRST/MIDDLE/LAST),
  classify each compound by its dominant operational category (via PREFIX
  distribution), then compare category distributions across positions using
  chi-squared test and Jensen-Shannon divergence.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from scripts.voynich import Transcript, Morphology
from collections import Counter, defaultdict
from scipy.stats import chi2_contingency
from scipy.spatial.distance import jensenshannon
import numpy as np
import json

ATOMS = set('kehyinamdtlocpfsgrx')

CATEGORIES = ['THERMAL', 'FLOW', 'STAGING', 'MONITORING', 'MARKING',
              'CONTAINMENT', 'OPERATION', 'TRANSITION']

# PREFIX -> category mapping (from C1297, C1300, C1298, C1299, C1302)
PREFIX_CATEGORY = {
    'qo': 'THERMAL', 'ok': 'THERMAL', 'qok': 'THERMAL',
    'ch': 'MONITORING', 'sh': 'MONITORING', 'cph': 'MONITORING',
    'ot': 'MONITORING',
    'da': 'FLOW', 'ar': 'FLOW', 'or': 'FLOW',
    'sa': 'STAGING', 'ol': 'STAGING',
    'op': 'OPERATION',
    'pch': 'MARKING', 'po': 'MARKING',
    'tch': 'TRANSITION', 'te': 'TRANSITION',
    'al': 'FLOW',
    'lch': 'CONTAINMENT', 'lk': 'CONTAINMENT',
}

tx = Transcript()
morph = Morphology()

# Build PREFIX distributions per MIDDLE
prefix_by_middle = defaultdict(Counter)
for token in tx.currier_b():
    w = token.word
    if not w.strip() or '*' in w:
        continue
    m = morph.extract(w)
    if not m.middle:
        continue
    pfx = m.prefix if m.prefix else '_NONE_'
    prefix_by_middle[m.middle][pfx] += 1

def classify_middle(mid):
    """Classify a MIDDLE by its dominant PREFIX category."""
    pfx_counts = prefix_by_middle.get(mid, Counter())
    if not pfx_counts:
        return None
    cat_counts = Counter()
    for pfx, count in pfx_counts.items():
        if pfx in PREFIX_CATEGORY:
            cat_counts[PREFIX_CATEGORY[pfx]] += count
    if not cat_counts:
        return None
    return cat_counts.most_common(1)[0][0]

def get_category_distribution(mid):
    """Get full category distribution for a MIDDLE."""
    pfx_counts = prefix_by_middle.get(mid, Counter())
    if not pfx_counts:
        return Counter()
    cat_counts = Counter()
    for pfx, count in pfx_counts.items():
        if pfx in PREFIX_CATEGORY:
            cat_counts[PREFIX_CATEGORY[pfx]] += count
    return cat_counts

def get_atom_sequence(middle):
    """Extract the ordered sequence of atoms from a MIDDLE."""
    return [ch for ch in middle if ch in ATOMS]

# ============================================================
# Collect compounds by atom position
# Test atoms: k, t (FREE), e (HEAD control), h (TERMINAL control)
# ============================================================
test_atoms = ['k', 't', 'e', 'h']

results = {}

for target in test_atoms:
    position_cats = {'FIRST': Counter(), 'MIDDLE': Counter(), 'LAST': Counter()}
    position_examples = {'FIRST': [], 'MIDDLE': [], 'LAST': []}
    position_middles = {'FIRST': set(), 'MIDDLE': set(), 'LAST': set()}

    for mid in prefix_by_middle:
        seq = get_atom_sequence(mid)
        if len(seq) < 2 or target not in seq:
            continue

        cat = classify_middle(mid)
        if not cat:
            continue

        token_count = sum(prefix_by_middle[mid].values())

        # Find position(s) of target atom
        for i, atom in enumerate(seq):
            if atom != target:
                continue
            n = len(seq)
            if i == 0:
                pos = 'FIRST'
            elif i == n - 1:
                pos = 'LAST'
            else:
                pos = 'MIDDLE'

            position_cats[pos][cat] += token_count
            position_middles[pos].add(mid)
            if len(position_examples[pos]) < 5:
                position_examples[pos].append((mid, cat, token_count))

    # Print results for this atom
    atype = 'FREE' if target in 'kt' else ('HEAD' if target == 'e' else 'TERMINAL')
    print(f"\n{'='*60}")
    print(f"ATOM: {target} ({atype})")
    print(f"{'='*60}")

    for pos in ['FIRST', 'MIDDLE', 'LAST']:
        total = sum(position_cats[pos].values())
        n_types = len(position_middles[pos])
        if total == 0:
            print(f"  {pos}: no data")
            continue
        print(f"\n  {pos} (N={total} tokens, {n_types} MIDDLE types):")
        for cat in CATEGORIES:
            cnt = position_cats[pos].get(cat, 0)
            if cnt > 0:
                pct = 100 * cnt / total
                bar = '#' * int(pct / 2)
                print(f"    {cat:<14} {cnt:>5} ({pct:>5.1f}%) {bar}")
        if position_examples[pos]:
            print(f"    Examples: {', '.join(f'{m}({c})' for m,c,n in position_examples[pos][:5])}")

    # Chi-squared test: FIRST vs LAST
    first_total = sum(position_cats['FIRST'].values())
    last_total = sum(position_cats['LAST'].values())

    chi2, p, jsd_val = None, None, None

    if first_total >= 20 and last_total >= 20:
        all_cats = sorted(set(list(position_cats['FIRST'].keys()) +
                              list(position_cats['LAST'].keys())))
        table = []
        for pos_label in ['FIRST', 'LAST']:
            row = [position_cats[pos_label].get(c, 0) for c in all_cats]
            table.append(row)
        table = np.array(table)

        # Remove zero columns
        nonzero = table.sum(axis=0) > 0
        table = table[:, nonzero]
        cats_used = [c for c, nz in zip(all_cats, nonzero) if nz]

        if table.shape[1] >= 2:
            chi2, p, dof, expected = chi2_contingency(table)
            print(f"\n  FIRST vs LAST chi2={chi2:.1f}, p={p:.2e}, dof={dof}")
            print(f"  Verdict: {'POSITION-DEPENDENT' if p < 0.01 else 'POSITION-INDEPENDENT'}")
        else:
            print(f"\n  Not enough category diversity for chi2 test")

        # JSD
        p_first = np.array([position_cats['FIRST'].get(c, 0) for c in all_cats],
                           dtype=float)
        p_last = np.array([position_cats['LAST'].get(c, 0) for c in all_cats],
                          dtype=float)
        p_first /= p_first.sum()
        p_last /= p_last.sum()
        jsd_val = float(jensenshannon(p_first, p_last))
        print(f"  JSD(FIRST, LAST) = {jsd_val:.4f}")
    else:
        print(f"\n  Insufficient data for chi2 (FIRST={first_total}, LAST={last_total})")

    # Also test FIRST vs MIDDLE if we have data
    mid_total = sum(position_cats['MIDDLE'].values())
    chi2_fm, p_fm, jsd_fm = None, None, None
    if first_total >= 20 and mid_total >= 20:
        all_cats_fm = sorted(set(list(position_cats['FIRST'].keys()) +
                                 list(position_cats['MIDDLE'].keys())))
        table_fm = []
        for pos_label in ['FIRST', 'MIDDLE']:
            row = [position_cats[pos_label].get(c, 0) for c in all_cats_fm]
            table_fm.append(row)
        table_fm = np.array(table_fm)
        nonzero_fm = table_fm.sum(axis=0) > 0
        table_fm = table_fm[:, nonzero_fm]

        if table_fm.shape[1] >= 2:
            chi2_fm, p_fm, dof_fm, _ = chi2_contingency(table_fm)
            print(f"\n  FIRST vs MIDDLE chi2={chi2_fm:.1f}, p={p_fm:.2e}, dof={dof_fm}")

        p_f = np.array([position_cats['FIRST'].get(c, 0) for c in all_cats_fm],
                       dtype=float)
        p_m = np.array([position_cats['MIDDLE'].get(c, 0) for c in all_cats_fm],
                       dtype=float)
        p_f /= p_f.sum()
        p_m /= p_m.sum()
        jsd_fm = float(jensenshannon(p_f, p_m))
        print(f"  JSD(FIRST, MIDDLE) = {jsd_fm:.4f}")

    results[target] = {
        'type': atype,
        'position_cats': {pos: dict(cats) for pos, cats in position_cats.items()},
        'position_n_types': {pos: len(mids) for pos, mids in position_middles.items()},
        'first_vs_last': {
            'chi2': float(chi2) if chi2 is not None else None,
            'p_value': float(p) if p is not None else None,
            'jsd': jsd_val,
        },
        'first_vs_middle': {
            'chi2': float(chi2_fm) if chi2_fm is not None else None,
            'p_value': float(p_fm) if p_fm is not None else None,
            'jsd': jsd_fm,
        },
    }

# ============================================================
# Summary comparison
# ============================================================
print(f"\n{'='*60}")
print(f"SUMMARY: POSITION INDEPENDENCE TEST")
print(f"{'='*60}")
print(f"{'Atom':<6} {'Type':<12} {'Chi2':>8} {'p-value':>12} {'JSD':>8} {'Verdict':<20}")
print(f"{'-'*6} {'-'*12} {'-'*8} {'-'*12} {'-'*8} {'-'*20}")

for target in test_atoms:
    r = results[target]
    fl = r['first_vs_last']
    chi2_str = f"{fl['chi2']:.1f}" if fl['chi2'] is not None else 'N/A'
    p_str = f"{fl['p_value']:.2e}" if fl['p_value'] is not None else 'N/A'
    jsd_str = f"{fl['jsd']:.4f}" if fl['jsd'] is not None else 'N/A'

    if fl['p_value'] is not None:
        verdict = 'POS-INDEPENDENT' if fl['p_value'] > 0.01 else 'POS-DEPENDENT'
    else:
        verdict = 'INSUFFICIENT DATA'

    print(f"{target:<6} {r['type']:<12} {chi2_str:>8} {p_str:>12} {jsd_str:>8} {verdict:<20}")

print(f"\nExpected: k,t = POS-INDEPENDENT (FREE); e = POS-DEPENDENT (HEAD); h = POS-DEPENDENT (TERMINAL)")

# ============================================================
# Additional: Cross-position MIDDLE overlap check
# ============================================================
print(f"\n{'='*60}")
print(f"CROSS-POSITION OVERLAP (MIDDLEs appearing in multiple positions)")
print(f"{'='*60}")

for target in test_atoms:
    r = results[target]
    f_set = set()
    m_set = set()
    l_set = set()

    for mid in prefix_by_middle:
        seq = get_atom_sequence(mid)
        if len(seq) < 2 or target not in seq:
            continue
        for i, atom in enumerate(seq):
            if atom != target:
                continue
            n = len(seq)
            if i == 0:
                f_set.add(mid)
            elif i == n - 1:
                l_set.add(mid)
            else:
                m_set.add(mid)

    # Check if same MIDDLE can have the atom in different positions
    # (this would mean the atom appears multiple times)
    fl_overlap = f_set & l_set
    fm_overlap = f_set & m_set
    ml_overlap = m_set & l_set
    all_overlap = f_set & m_set & l_set

    print(f"\n  {target} ({r['type']}):")
    print(f"    FIRST: {len(f_set)} types, MIDDLE: {len(m_set)} types, LAST: {len(l_set)} types")
    print(f"    FIRST&LAST overlap: {len(fl_overlap)} (multi-occurrence MIDDLEs)")
    if fl_overlap:
        print(f"      e.g.: {list(fl_overlap)[:5]}")

# Save
output_path = os.path.join(os.path.dirname(__file__), '..', 'results',
                           'free_atom_position_test.json')
with open(output_path, 'w') as f:
    json.dump(results, f, indent=2)
print(f"\nResults saved to {output_path}")
