"""
Compound Head Position Test
============================
Tests WHERE the "head" atom is in compound MIDDLEs — first position, last position, or neither.

H1: LAST atom's default category dominates (last atom = head/outcome)
H2: FIRST atom's default category dominates (first atom = head/frame)
H3: Neither dominates (distributed)

Two approaches:
  A) PREFIX-based category classification (empirical from co-occurrence)
  B) Direct atom→category mapping from deep-dive constraints (C1385-C1392)
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from scripts.voynich import Transcript, Morphology, MiddleAnalyzer
from collections import Counter, defaultdict
import json

tx = Transcript()
morph = Morphology()
mid_analyzer = MiddleAnalyzer()
mid_analyzer.build_inventory('B')

# ============================================================
# Step 1: Build PREFIX→MIDDLE co-occurrence for all B tokens
# ============================================================
prefix_by_middle = defaultdict(Counter)
middle_token_count = Counter()

for token in tx.currier_b():
    w = token.word
    if not w.strip() or '*' in w:
        continue
    m = morph.extract(w)
    if not m.middle:
        continue
    mid = m.middle
    pfx = m.prefix if m.prefix else '_NONE_'
    prefix_by_middle[mid][pfx] += 1
    middle_token_count[mid] += 1

# ============================================================
# Step 2A: PREFIX-based category classification
# ============================================================
# Extended PREFIX→category mappings from BCSC constraints
# C1300: qo near-pure THERMAL
# C1298: ok/ot divergence
# C1299: ch/sh category divergence
# C1297: PREFIX-category structured association
# C1302: BARE distinctive profile
PREFIX_CATEGORY = {
    'qo': 'THERMAL',
    'ok': 'CONTAINMENT',
    'ot': 'MONITORING',
    'ch': 'MONITORING',
    'sh': 'MONITORING',
    'cph': 'MONITORING',
    'da': 'STAGING',
    'ol': 'STAGING',
    'sa': 'STAGING',
    'ar': 'FLOW',
    'or': 'FLOW',
    'al': 'FLOW',
    'op': 'OPERATION',
    'po': 'MARKING',
    'pch': 'MARKING',
    'tch': 'MARKING',
    'dch': 'MARKING',
    'te': 'MARKING',
    'lch': 'STAGING',
    'lk': 'THERMAL',
    'ke': 'THERMAL',
    'ot': 'MONITORING',
    'qok': 'THERMAL',
    'dol': 'STAGING',
    'sol': 'STAGING',
    'ych': 'MONITORING',
    'ysh': 'MONITORING',
    'fch': 'MARKING',
}

def classify_middle_by_prefix(mid):
    """Classify a MIDDLE by its PREFIX distribution."""
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

# ============================================================
# Step 2B: Direct atom→category mapping from deep-dive constraints
# ============================================================
# From C1385-C1392, C1195, C1207, C1250, C1388, C1389, C1390, C1391, C1392
ATOM_CATEGORY_DIRECT = {
    'k': 'THERMAL',      # C103 ENERGY_MODULATOR
    'e': 'THERMAL',      # C105 STABILITY_ANCHOR
    'h': 'MONITORING',   # C104 PHASE_MANAGER -> monitors
    'o': 'STAGING',      # C1388 arrangement/domain marker
    'c': 'MONITORING',   # C1389 main-loop modifier
    'p': 'MARKING',      # C1390 marking pause
    's': 'STAGING',      # C1391 staging sequence
    'f': 'MARKING',      # C1392 marking flag
    'd': 'TRANSITION',   # seal/end-class (C919)
    't': 'TRANSITION',   # transfer (C1195)
    'l': 'STAGING',      # C1385 state/condition marker
    'n': 'THERMAL',      # binding (thermal context per C1383)
    'a': 'FLOW',         # into/intake
    'm': 'THERMAL',      # batch-close (C1235)
    'i': 'FLOW',         # cycle/iterate (C1234)
    'y': 'TRANSITION',   # end (closure)
    'r': 'FLOW',         # C1387 hazard-response
    'g': None,           # unknown
    'x': None,           # unknown
    'q': None,           # only in PREFIX
}

def classify_middle_by_atoms_direct(mid):
    """Classify a MIDDLE by majority vote of its atoms' direct categories."""
    cat_counts = Counter()
    for ch in mid:
        cat = ATOM_CATEGORY_DIRECT.get(ch)
        if cat:
            cat_counts[cat] += 1
    if not cat_counts:
        return None
    return cat_counts.most_common(1)[0][0]

# ============================================================
# Step 3: Get all atoms (single-char MIDDLEs)
# ============================================================
atoms = set()
for mid in prefix_by_middle:
    if len(mid) == 1 and mid.isalpha():
        atoms.add(mid)

print(f"Single-char atoms found in B corpus: {sorted(atoms)}")
print(f"Total unique MIDDLEs in B: {len(prefix_by_middle)}")

# Atom default categories by PREFIX method
atom_cat_prefix = {}
for atom in sorted(atoms):
    cat = classify_middle_by_prefix(atom)
    if cat:
        atom_cat_prefix[atom] = cat

# Atom default categories by direct method
atom_cat_direct = {}
for atom in sorted(atoms):
    cat = ATOM_CATEGORY_DIRECT.get(atom)
    if cat:
        atom_cat_direct[atom] = cat

print(f"\nAtom categories comparison:")
print(f"  {'Atom':<5} {'PREFIX-method':<15} {'Direct-method':<15} {'Match?'}")
for a in sorted(atoms):
    p_cat = atom_cat_prefix.get(a, '???')
    d_cat = atom_cat_direct.get(a, '???')
    match = 'YES' if p_cat == d_cat else 'NO'
    print(f"  {a:<5} {p_cat:<15} {d_cat:<15} {match}")

# ============================================================
# Step 4: Identify compound MIDDLEs and their first/last atoms
# ============================================================
def find_atoms_in_middle(mid, atom_set):
    """Find atoms in a MIDDLE by position, handling overlaps.
    Returns list of (position, atom) sorted by position.
    """
    positions = []
    used = set()
    # Find all single-char atoms at each position
    for i, ch in enumerate(mid):
        if ch in atom_set and i not in used:
            positions.append((i, ch))
            used.add(i)
    return positions

def run_head_test(atom_categories, method_name, classify_fn):
    """Run the head position test with a given atom→category mapping."""

    results = {
        'method': method_name,
        'first_match': 0,
        'last_match': 0,
        'both_match': 0,
        'neither_match': 0,
        'first_only': 0,
        'last_only': 0,
        'total_testable': 0,
        'details': []
    }

    all_middles = set(prefix_by_middle.keys())

    for mid in sorted(all_middles):
        if len(mid) < 2:
            continue

        # Find atom positions
        positions = find_atoms_in_middle(mid, atoms)
        if len(positions) < 2:
            continue

        first_atom = positions[0][1]
        last_atom = positions[-1][1]

        if first_atom == last_atom:
            continue  # skip if same atom at first and last

        # Get categories
        compound_cat = classify_fn(mid)
        first_cat = atom_categories.get(first_atom)
        last_cat = atom_categories.get(last_atom)

        if not compound_cat or not first_cat or not last_cat:
            continue

        token_count = middle_token_count.get(mid, 0)
        if token_count < 3:
            continue  # skip very rare compounds

        first_matches = (compound_cat == first_cat)
        last_matches = (compound_cat == last_cat)

        results['total_testable'] += 1
        if first_matches and last_matches:
            results['both_match'] += 1
        elif first_matches:
            results['first_only'] += 1
        elif last_matches:
            results['last_only'] += 1
        else:
            results['neither_match'] += 1

        if first_matches:
            results['first_match'] += 1
        if last_matches:
            results['last_match'] += 1

        results['details'].append({
            'middle': mid,
            'tokens': token_count,
            'atom_positions': [(p, a) for p, a in positions],
            'first_atom': first_atom,
            'last_atom': last_atom,
            'compound_cat': compound_cat,
            'first_atom_cat': first_cat,
            'last_atom_cat': last_cat,
            'first_match': first_matches,
            'last_match': last_matches
        })

    # Sort by token count
    results['details'].sort(key=lambda x: -x['tokens'])

    # Token-weighted analysis
    w_first = sum(d['tokens'] for d in results['details'] if d['first_match'])
    w_last = sum(d['tokens'] for d in results['details'] if d['last_match'])
    w_total = sum(d['tokens'] for d in results['details'])
    results['token_weighted_first_pct'] = round(100 * w_first / max(1, w_total), 1)
    results['token_weighted_last_pct'] = round(100 * w_last / max(1, w_total), 1)

    return results

# ============================================================
# Run both methods
# ============================================================
print(f"\n{'='*70}")
print(f"APPROACH A: PREFIX-based category classification")
print(f"{'='*70}")

results_a = run_head_test(atom_cat_prefix, 'PREFIX-based', classify_middle_by_prefix)

print(f"Total testable compounds (2+ atoms, N>=3): {results_a['total_testable']}")
print(f"\nFirst atom matches compound category: {results_a['first_match']} ({100*results_a['first_match']/max(1,results_a['total_testable']):.1f}%)")
print(f"Last atom matches compound category:  {results_a['last_match']} ({100*results_a['last_match']/max(1,results_a['total_testable']):.1f}%)")
print(f"\nExclusive breakdown:")
print(f"  First ONLY matches:  {results_a['first_only']} ({100*results_a['first_only']/max(1,results_a['total_testable']):.1f}%)")
print(f"  Last ONLY matches:   {results_a['last_only']} ({100*results_a['last_only']/max(1,results_a['total_testable']):.1f}%)")
print(f"  BOTH match:          {results_a['both_match']} ({100*results_a['both_match']/max(1,results_a['total_testable']):.1f}%)")
print(f"  NEITHER matches:     {results_a['neither_match']} ({100*results_a['neither_match']/max(1,results_a['total_testable']):.1f}%)")
print(f"\nToken-weighted:")
print(f"  First atom match rate: {results_a['token_weighted_first_pct']}% of tokens")
print(f"  Last atom match rate:  {results_a['token_weighted_last_pct']}% of tokens")

print(f"\n--- Top 20 compounds by token count (PREFIX method) ---")
for d in results_a['details'][:20]:
    first_mark = 'F' if d['first_match'] else '.'
    last_mark = 'L' if d['last_match'] else '.'
    atoms_str = '->'.join(a for _, a in d['atom_positions'])
    print(f"  {d['middle']:<12} N={d['tokens']:>4}  atoms={atoms_str:<10}  cat={d['compound_cat']:<12} "
          f"first={d['first_atom']}({d['first_atom_cat']:<12}) last={d['last_atom']}({d['last_atom_cat']:<12}) [{first_mark}{last_mark}]")


print(f"\n{'='*70}")
print(f"APPROACH B: Direct atom->category mapping (C1385-C1392)")
print(f"{'='*70}")

results_b = run_head_test(atom_cat_direct, 'Direct-mapping', classify_middle_by_atoms_direct)

print(f"Total testable compounds (2+ atoms, N>=3): {results_b['total_testable']}")
print(f"\nFirst atom matches compound category: {results_b['first_match']} ({100*results_b['first_match']/max(1,results_b['total_testable']):.1f}%)")
print(f"Last atom matches compound category:  {results_b['last_match']} ({100*results_b['last_match']/max(1,results_b['total_testable']):.1f}%)")
print(f"\nExclusive breakdown:")
print(f"  First ONLY matches:  {results_b['first_only']} ({100*results_b['first_only']/max(1,results_b['total_testable']):.1f}%)")
print(f"  Last ONLY matches:   {results_b['last_only']} ({100*results_b['last_only']/max(1,results_b['total_testable']):.1f}%)")
print(f"  BOTH match:          {results_b['both_match']} ({100*results_b['both_match']/max(1,results_b['total_testable']):.1f}%)")
print(f"  NEITHER matches:     {results_b['neither_match']} ({100*results_b['neither_match']/max(1,results_b['total_testable']):.1f}%)")
print(f"\nToken-weighted:")
print(f"  First atom match rate: {results_b['token_weighted_first_pct']}% of tokens")
print(f"  Last atom match rate:  {results_b['token_weighted_last_pct']}% of tokens")

print(f"\n--- Top 20 compounds by token count (Direct method) ---")
for d in results_b['details'][:20]:
    first_mark = 'F' if d['first_match'] else '.'
    last_mark = 'L' if d['last_match'] else '.'
    atoms_str = '->'.join(a for _, a in d['atom_positions'])
    print(f"  {d['middle']:<12} N={d['tokens']:>4}  atoms={atoms_str:<10}  cat={d['compound_cat']:<12} "
          f"first={d['first_atom']}({d['first_atom_cat']:<12}) last={d['last_atom']}({d['last_atom_cat']:<12}) [{first_mark}{last_mark}]")

# ============================================================
# Detailed category-pair breakdown (Approach B only — more reliable)
# ============================================================
print(f"\n{'='*70}")
print(f"CATEGORY PAIR BREAKDOWN (Direct method)")
print(f"{'='*70}")

pair_stats = defaultdict(lambda: {'first_wins': 0, 'last_wins': 0, 'both': 0, 'neither': 0, 'total': 0, 'tokens': 0})

for d in results_b['details']:
    key = f"{d['first_atom_cat']} -> {d['last_atom_cat']}"
    pair_stats[key]['total'] += 1
    pair_stats[key]['tokens'] += d['tokens']
    if d['first_match'] and d['last_match']:
        pair_stats[key]['both'] += 1
    elif d['first_match']:
        pair_stats[key]['first_wins'] += 1
    elif d['last_match']:
        pair_stats[key]['last_wins'] += 1
    else:
        pair_stats[key]['neither'] += 1

print(f"{'Pair':<30} {'N':>4} {'Tokens':>6}  {'First%':>7} {'Last%':>7} {'Both%':>7} {'Neither%':>8}")
print(f"{'-'*80}")
for key in sorted(pair_stats, key=lambda k: -pair_stats[k]['tokens']):
    s = pair_stats[key]
    n = s['total']
    if n < 2:
        continue
    print(f"{key:<30} {n:>4} {s['tokens']:>6}  "
          f"{100*s['first_wins']/n:>6.1f}% {100*s['last_wins']/n:>6.1f}% "
          f"{100*s['both']/n:>6.1f}% {100*s['neither']/n:>7.1f}%")

# ============================================================
# Position-specific analysis: does position 0 vs position -1
# matter more than just first/last atom identity?
# ============================================================
print(f"\n{'='*70}")
print(f"POSITION SPECIFICITY (Direct method)")
print(f"{'='*70}")

# For 3+ atom compounds, check middle atoms too
multi_atom_details = []
for d in results_b['details']:
    if len(d['atom_positions']) >= 3:
        # Check each atom position
        compound_cat = d['compound_cat']
        for pos_idx, (str_pos, atom) in enumerate(d['atom_positions']):
            atom_cat = ATOM_CATEGORY_DIRECT.get(atom)
            if atom_cat:
                multi_atom_details.append({
                    'middle': d['middle'],
                    'tokens': d['tokens'],
                    'position_index': pos_idx,
                    'total_atoms': len(d['atom_positions']),
                    'atom': atom,
                    'atom_cat': atom_cat,
                    'compound_cat': compound_cat,
                    'matches': atom_cat == compound_cat
                })

if multi_atom_details:
    # Normalize position to 0.0 (first) - 1.0 (last)
    from collections import defaultdict
    pos_match = defaultdict(lambda: {'match': 0, 'total': 0, 'tokens_match': 0, 'tokens_total': 0})

    for md in multi_atom_details:
        if md['total_atoms'] <= 1:
            continue
        norm_pos = md['position_index'] / (md['total_atoms'] - 1)
        bucket = round(norm_pos, 1)
        pos_match[bucket]['total'] += 1
        pos_match[bucket]['tokens_total'] += md['tokens']
        if md['matches']:
            pos_match[bucket]['match'] += 1
            pos_match[bucket]['tokens_match'] += md['tokens']

    print(f"\nMatch rate by normalized position (0=first, 1=last) in 3+ atom compounds:")
    print(f"{'Position':>10} {'N':>5} {'Match%':>8} {'Token-wtd%':>12}")
    for pos in sorted(pos_match):
        s = pos_match[pos]
        print(f"{pos:>10.1f} {s['total']:>5} {100*s['match']/max(1,s['total']):>7.1f}% "
              f"{100*s['tokens_match']/max(1,s['tokens_total']):>11.1f}%")

    print(f"\n3+ atom compounds tested: {len(set(md['middle'] for md in multi_atom_details))}")
else:
    print("No 3+ atom compounds found for position analysis.")

# ============================================================
# SYNTHESIS
# ============================================================
print(f"\n{'='*70}")
print(f"SYNTHESIS")
print(f"{'='*70}")

for label, res in [("PREFIX-based (A)", results_a), ("Direct-mapping (B)", results_b)]:
    n = res['total_testable']
    if n == 0:
        continue
    first_pct = 100 * res['first_match'] / n
    last_pct = 100 * res['last_match'] / n

    if first_pct > last_pct + 10:
        verdict = "H2 SUPPORTED: FIRST atom dominates (initial = head)"
    elif last_pct > first_pct + 10:
        verdict = "H1 SUPPORTED: LAST atom dominates (terminal = head)"
    else:
        verdict = "H3 SUPPORTED: Neither position clearly dominates"

    print(f"\n{label}:")
    print(f"  First match: {first_pct:.1f}%, Last match: {last_pct:.1f}%, Delta: {abs(first_pct-last_pct):.1f}pp")
    print(f"  Token-weighted: First={res['token_weighted_first_pct']}%, Last={res['token_weighted_last_pct']}%")
    print(f"  Verdict: {verdict}")

# ============================================================
# Save results
# ============================================================
output_dir = os.path.join(os.path.dirname(__file__), '..', 'results')
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, 'compound_head_position_test.json')

save_data = {
    'approach_a_prefix': {k: v for k, v in results_a.items() if k != 'details'},
    'approach_a_top50': [{k: v for k, v in d.items() if k != 'atom_positions'} for d in results_a['details'][:50]],
    'approach_b_direct': {k: v for k, v in results_b.items() if k != 'details'},
    'approach_b_top50': [{k: v for k, v in d.items() if k != 'atom_positions'} for d in results_b['details'][:50]],
}

with open(output_path, 'w') as f:
    json.dump(save_data, f, indent=2)
print(f"\nResults saved to {output_path}")
