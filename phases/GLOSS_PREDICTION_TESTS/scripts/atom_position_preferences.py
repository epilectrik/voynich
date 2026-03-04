"""
Atom Positional Preferences in Compound MIDDLEs
================================================
Tests whether individual atoms have positional preferences within compound MIDDLEs.
Do some atoms always appear first (heads), some always last (state-carriers),
some always in the middle (modifiers)?

Cross-references with C1209 (MIDDLE Positional Grammar), C1210 (MIDDLE Slot Syntax),
C1195 (Atom Gloss Confidence Tiers), and deep-dive atom profiles.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from scripts.voynich import Transcript, Morphology
from collections import Counter, defaultdict

tx = Transcript()
morph = Morphology()

# Known atoms from C1195
ATOMS = list('kehyinamdtlocpfsgrx')
ATOM_SET = set(ATOMS)

# Step 1: Collect all compound MIDDLEs from Currier B
middle_counts = Counter()
for token in tx.currier_b():
    w = token.word
    if not w.strip() or '*' in w:
        continue
    m = morph.extract(w)
    if m.middle:
        middle_counts[m.middle] += 1

# Step 2: For each compound MIDDLE, decompose into ordered atom sequence
# Use greedy left-to-right single-character atom extraction
def get_atom_sequence(middle):
    """Extract ordered atom sequence from a compound MIDDLE"""
    atoms_found = []
    for char in middle:
        if char in ATOM_SET:
            atoms_found.append(char)
    return atoms_found

# Step 3: For each atom, compute positional distribution
# Position types: FIRST, LAST, MIDDLE (for 3+ atom compounds)
# Also compute normalized position (0.0 = first, 1.0 = last)

atom_positions = defaultdict(list)  # atom -> list of (normalized_position, count)
atom_position_counts = defaultdict(Counter)  # atom -> Counter of {FIRST, LAST, MIDDLE}
atom_compound_counts = defaultdict(int)  # atom -> total appearances in compounds
atom_solo_counts = Counter()  # atom -> appearances as solo MIDDLE

compound_count = 0
compound_types = 0

for mid, count in middle_counts.items():
    seq = get_atom_sequence(mid)
    if len(seq) < 2:
        if len(seq) == 1:
            atom_solo_counts[seq[0]] += count
        continue

    compound_count += count
    compound_types += 1

    for i, atom in enumerate(seq):
        n = len(seq)
        norm_pos = i / (n - 1) if n > 1 else 0.5

        atom_positions[atom].append((norm_pos, count))
        atom_compound_counts[atom] += count

        if i == 0:
            atom_position_counts[atom]['FIRST'] += count
        elif i == n - 1:
            atom_position_counts[atom]['LAST'] += count
        else:
            atom_position_counts[atom]['MIDDLE'] += count

print(f"{'='*80}")
print(f"ATOM POSITIONAL PREFERENCES IN COMPOUND MIDDLES")
print(f"{'='*80}")
print()
print(f"Total compound MIDDLE types: {compound_types}")
print(f"Total compound MIDDLE tokens: {compound_count}")
print(f"Total solo MIDDLE tokens: {sum(atom_solo_counts.values())}")
print(f"Atoms found in compounds: {len(atom_compound_counts)}")
print()

# Step 4: Compute statistics per atom
print(f"{'Atom':<6} {'Solo':>6} {'Compound':>8} {'First%':>8} {'Middle%':>8} {'Last%':>8} {'Mean Pos':>9} {'Role':>12}")
print(f"{'-'*6} {'-'*6} {'-'*8} {'-'*8} {'-'*8} {'-'*8} {'-'*9} {'-'*12}")

atom_stats = []
for atom in sorted(ATOMS):
    if atom not in atom_compound_counts:
        continue

    total = atom_compound_counts[atom]
    first = atom_position_counts[atom]['FIRST']
    middle = atom_position_counts[atom]['MIDDLE']
    last = atom_position_counts[atom]['LAST']
    solo = atom_solo_counts.get(atom, 0)

    first_pct = 100 * first / total
    middle_pct = 100 * middle / total
    last_pct = 100 * last / total

    # Token-weighted mean position
    weighted_sum = sum(pos * cnt for pos, cnt in atom_positions[atom])
    weighted_total = sum(cnt for _, cnt in atom_positions[atom])
    mean_pos = weighted_sum / weighted_total if weighted_total > 0 else 0.5

    # Classify role
    if first_pct > 60:
        role = 'HEAD'
    elif last_pct > 60:
        role = 'TERMINAL'
    elif middle_pct > 40:
        role = 'MODIFIER'
    elif first_pct > 45:
        role = 'head-lean'
    elif last_pct > 45:
        role = 'term-lean'
    else:
        role = 'flexible'

    atom_stats.append({
        'atom': atom,
        'solo': solo,
        'compound': total,
        'first_pct': first_pct,
        'middle_pct': middle_pct,
        'last_pct': last_pct,
        'mean_pos': mean_pos,
        'role': role,
        'first': first,
        'middle': middle,
        'last': last
    })

    print(f"{atom:<6} {solo:>6} {total:>8} {first_pct:>7.1f}% {middle_pct:>7.1f}% {last_pct:>7.1f}% {mean_pos:>8.3f} {role:>12}")

# Step 5: Sort by mean position to show gradient
print(f"\n{'='*80}")
print(f"ATOMS SORTED BY MEAN POSITION (0=always first, 1=always last)")
print(f"{'='*80}")
print()

atom_stats.sort(key=lambda x: x['mean_pos'])
for s in atom_stats:
    bar_len = int(s['mean_pos'] * 40)
    bar = '.' * bar_len + '|' + '.' * (40 - bar_len)
    print(f"  {s['atom']}: {s['mean_pos']:.3f}  [{bar}]  {s['role']:<12} (F:{s['first_pct']:.0f}% M:{s['middle_pct']:.0f}% L:{s['last_pct']:.0f}%)")

# Step 6: Cross-reference with known atom properties
print(f"\n{'='*80}")
print(f"CROSS-REFERENCE WITH KNOWN ATOM PROPERTIES")
print(f"{'='*80}")
print()

# From C1195 and deep dives (C1385-C1392)
known = {
    'k': ('THERMAL', 'LOCKED', 'injector'),
    'e': ('THERMAL', 'LOCKED', 'injector'),
    'h': ('THERMAL', 'LOCKED', 'junction'),
    'y': ('THERMAL', 'LOCKED', 'boundary'),
    'i': ('FLOW', 'LOCKED', 'iterator'),
    'n': ('THERMAL', 'LOCKED', 'boundary'),
    'a': ('FLOW', 'LOCKED', 'gateway'),
    'm': ('THERMAL', 'LOCKED', 'boundary'),
    'd': ('MARKING', 'SOLID', 'marker'),
    't': ('FLOW', 'SOLID', 'transfer'),
    'l': ('STAGING', 'SOLID', 'state'),
    'o': ('STAGING', 'SOLID', 'arranger'),
    'c': ('MONITORING', 'SOLID', 'modifier'),
    'p': ('MARKING', 'SOLID', 'injector'),
    'f': ('MARKING', 'PLAUSIBLE', 'flag'),
    's': ('STAGING', 'PLAUSIBLE', 'modifier'),
    'r': ('FLOW', 'PLAUSIBLE', 'responder'),
    'g': ('unknown', 'PLAUSIBLE', 'unknown'),
    'x': ('unknown', 'PLAUSIBLE', 'unknown'),
}

print(f"  {'Atom':<6} {'MeanPos':>8} {'Role':<14} {'Category':<14} {'Tier':<10} {'Behavior':<12}")
print(f"  {'-'*6} {'-'*8} {'-'*14} {'-'*14} {'-'*10} {'-'*12}")
for s in atom_stats:
    atom = s['atom']
    if atom in known:
        cat, tier, behavior = known[atom]
        print(f"  {atom:<6} {s['mean_pos']:>7.3f} {s['role']:<14} {cat:<14} {tier:<10} {behavior}")

# Step 7: Compare with C1209 findings
print(f"\n{'='*80}")
print(f"COMPARISON WITH C1209 (MIDDLE Positional Grammar)")
print(f"{'='*80}")
print()

# C1209 established: INITIAL {a,q,e,o} 86-57%, MEDIAL {c,i,p,d,f,s}, TERMINAL {n,y,m,r,h,l}
c1209_initial = {'a', 'q', 'e', 'o'}
c1209_medial = {'c', 'i', 'p', 'd', 'f', 's'}
c1209_terminal = {'n', 'y', 'm', 'r', 'h', 'l'}

print(f"  C1209 INITIAL atoms:  {sorted(c1209_initial)}")
print(f"  C1209 MEDIAL atoms:   {sorted(c1209_medial)}")
print(f"  C1209 TERMINAL atoms: {sorted(c1209_terminal)}")
print()

matches = 0
mismatches = 0
for s in atom_stats:
    atom = s['atom']
    our_role = s['role']

    # Map our role to C1209 category
    if our_role in ('HEAD', 'head-lean'):
        our_cat = 'INITIAL'
    elif our_role in ('TERMINAL', 'term-lean'):
        our_cat = 'TERMINAL'
    elif our_role == 'MODIFIER':
        our_cat = 'MEDIAL'
    else:
        our_cat = 'FLEXIBLE'

    # What C1209 says
    if atom in c1209_initial:
        c1209_cat = 'INITIAL'
    elif atom in c1209_medial:
        c1209_cat = 'MEDIAL'
    elif atom in c1209_terminal:
        c1209_cat = 'TERMINAL'
    else:
        c1209_cat = 'FREE'

    match = 'MATCH' if our_cat == c1209_cat else ('PARTIAL' if our_cat == 'FLEXIBLE' else 'MISMATCH')
    if match == 'MATCH':
        matches += 1
    elif match == 'MISMATCH':
        mismatches += 1

    print(f"  {atom}: ours={our_cat:<10} C1209={c1209_cat:<10} -> {match}")

print(f"\n  Agreement: {matches}/{len(atom_stats)} match, {mismatches} mismatches")

# Step 8: Statistical test -- is position preference non-random?
from scipy.stats import chi2_contingency
import numpy as np

print(f"\n{'='*80}")
print(f"STATISTICAL TEST: ATOM x POSITION INDEPENDENCE")
print(f"{'='*80}")
print()

# Build contingency table for atoms with enough data
sufficient_atoms = [s for s in atom_stats if s['compound'] >= 50]
if sufficient_atoms:
    table = []
    labels = []
    for s in sufficient_atoms:
        table.append([s['first'], s['middle'], s['last']])
        labels.append(s['atom'])

    table = np.array(table)
    chi2, p, dof, expected = chi2_contingency(table)
    V = np.sqrt(chi2 / (table.sum() * (min(table.shape) - 1)))

    print(f"  Atoms tested (N>=50): {len(sufficient_atoms)}")
    print(f"  Total tokens in table: {table.sum()}")
    print(f"  Chi-squared = {chi2:.1f}, p = {p:.2e}, dof = {dof}")
    print(f"  Cramer's V = {V:.3f}")
    print(f"  {'SIGNIFICANT' if p < 0.001 else 'NOT SIGNIFICANT'}: atoms have {'non-random' if p < 0.001 else 'random'} positional preferences")

    # Per-atom contribution to chi-squared
    print(f"\n  Per-atom chi-squared contribution:")
    residuals = (table - expected) / np.sqrt(expected)
    for i, label in enumerate(labels):
        atom_chi2 = np.sum(residuals[i] ** 2)
        dominant_pos = ['FIRST', 'MIDDLE', 'LAST'][np.argmax(residuals[i])]
        print(f"    {label}: chi2_contrib={atom_chi2:>8.1f}  dominant_residual={dominant_pos}")
else:
    chi2, p, V = None, None, None
    print("  Insufficient data for chi-squared test")

# Step 9: Functional grouping
print(f"\n{'='*80}")
print(f"FUNCTIONAL POSITION GROUPS")
print(f"{'='*80}")
print()

heads = [s for s in atom_stats if s['role'] in ('HEAD', 'head-lean')]
terminals = [s for s in atom_stats if s['role'] in ('TERMINAL', 'term-lean')]
modifiers = [s for s in atom_stats if s['role'] == 'MODIFIER']
flexibles = [s for s in atom_stats if s['role'] == 'flexible']

print(f"  HEADS (first-biased):     {', '.join(s['atom'] for s in heads)} ({len(heads)} atoms)")
print(f"  TERMINALS (last-biased):  {', '.join(s['atom'] for s in terminals)} ({len(terminals)} atoms)")
print(f"  MODIFIERS (middle-biased):{', '.join(s['atom'] for s in modifiers)} ({len(modifiers)} atoms)")
print(f"  FLEXIBLE (no preference): {', '.join(s['atom'] for s in flexibles)} ({len(flexibles)} atoms)")

# Step 10: Interpretation
print(f"\n{'='*80}")
print(f"INTERPRETATION")
print(f"{'='*80}")
print()
print("  The positional gradient should reveal the MIDDLE's internal syntax:")
print("  - HEAD atoms set the operational domain (what kind of action)")
print("  - MODIFIER atoms transform the action (how it's done)")
print("  - TERMINAL atoms encode the resulting state (what condition)")
print()
print("  This maps to the instruction model: MIDDLE = [domain][modifier][state]")
print("  which parallels C1210 MIDDLE Slot Syntax: INITIAL + MEDIAL + TERMINAL")

# Save results
import json

output = {
    'summary': {
        'compound_types': compound_types,
        'compound_tokens': compound_count,
        'atoms_in_compounds': len(atom_compound_counts),
    },
    'atom_stats': [{k: v for k, v in s.items()} for s in atom_stats],
    'functional_groups': {
        'heads': [s['atom'] for s in heads],
        'terminals': [s['atom'] for s in terminals],
        'modifiers': [s['atom'] for s in modifiers],
        'flexibles': [s['atom'] for s in flexibles],
    },
    'chi2_test': {
        'chi2': float(chi2) if chi2 is not None else None,
        'p_value': float(p) if p is not None else None,
        'cramers_v': float(V) if V is not None else None,
        'n_atoms_tested': len(sufficient_atoms) if sufficient_atoms else 0,
    },
}

output_path = os.path.join(os.path.dirname(__file__), '..', 'results', 'atom_position_preferences.json')
with open(output_path, 'w') as f:
    json.dump(output, f, indent=2)
print(f"\nResults saved to {output_path}")
