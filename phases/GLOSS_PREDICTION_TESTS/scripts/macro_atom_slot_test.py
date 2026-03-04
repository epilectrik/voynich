"""
MACRO-ATOM SLOT OCCUPANCY TEST
Tests whether macro-atoms (ke/kee/keee, in/iin/iiin, ck, ch, etc.) occupy
a single slot in the three-slot composition grammar, or whether their
component atoms fill separate slots.

References: C1379, C1210, C1225, C1209, C1215
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from scripts.voynich import Transcript, Morphology
from collections import Counter, defaultdict
import json

ATOMS = set('kehyinamdtlocpfsgrx')

# Positional roles from C1209/C1210
HEAD_ATOMS = set('aeqo')       # INITIAL slot: a(86%), e(75%), q(72%), o(57%)
MODIFIER_ATOMS = set('cipdfs')  # MEDIAL slot: c, i, p, d, f, s
TERMINAL_ATOMS = set('nymlrh')  # TERMINAL slot: n(99%), y(97%), m(91%), l(82%), r(72%), h(71%)
FREE_ATOMS = set('kt')          # FREE: k, t (no positional preference per C1209)

# Atom categories from deep dives (C1195, C1250, C1388-C1392)
ATOM_CAT = {
    'k': 'THERMAL', 'e': 'THERMAL', 'h': 'MONITORING',
    'y': 'THERMAL', 'n': 'THERMAL', 'm': 'THERMAL',
    'a': 'FLOW', 'i': 'FLOW', 't': 'TRANSITION', 'r': 'FLOW',
    'o': 'STAGING', 'l': 'STAGING', 's': 'STAGING',
    'c': 'MONITORING', 'd': 'MARKING', 'p': 'MARKING', 'f': 'MARKING',
}

# Macro-atoms from C1379/C1210 (with e/i extensions)
# Ordered longest-first for greedy matching
MACRO_ATOMS_ORDERED = [
    ('keee', 'THERMAL'), ('kee', 'THERMAL'), ('ke', 'THERMAL'),
    ('iiin', 'FLOW'), ('iin', 'FLOW'), ('in', 'FLOW'),
    ('ck', 'MONITORING'), ('ch', 'MONITORING'), ('ct', 'MONITORING'),
    ('ph', 'MARKING'), ('am', 'FLOW'), ('an', 'FLOW'), ('dy', 'MARKING'),
]
MACRO_ATOMS = {name: cat for name, cat in MACRO_ATOMS_ORDERED}
MACRO_CAT = dict(MACRO_ATOMS)

tx = Transcript()
morph = Morphology()

# Collect all compound MIDDLEs with token counts
middle_counts = Counter()
for token in tx.currier_b():
    w = token.word
    if not w.strip() or '*' in w:
        continue
    m = morph.extract(w)
    if m.middle and len(m.middle) >= 2:
        middle_counts[m.middle] += 1

def get_atom_sequence(middle):
    return [ch for ch in middle if ch in ATOMS]

def find_macro_atoms(middle):
    """Greedy left-to-right macro-atom extraction (longest match first)"""
    result = []
    i = 0
    sorted_macros = sorted(MACRO_ATOMS.keys(), key=len, reverse=True)
    while i < len(middle):
        matched = False
        for macro in sorted_macros:
            if middle[i:i+len(macro)] == macro:
                result.append(('MACRO', macro))
                i += len(macro)
                matched = True
                break
        if not matched:
            if middle[i] in ATOMS:
                result.append(('ATOM', middle[i]))
            i += 1
    return result

# Also need PREFIX-based classification for Test D
prefix_by_middle = defaultdict(Counter)
for token in tx.currier_b():
    w = token.word
    if not w.strip() or '*' in w:
        continue
    m = morph.extract(w)
    if m.middle:
        pfx = m.prefix if m.prefix else '_NONE_'
        prefix_by_middle[m.middle][pfx] += 1

PREFIX_CATEGORY = {
    'qo': 'THERMAL', 'ok': 'THERMAL', 'qok': 'THERMAL',
    'ch': 'MONITORING', 'sh': 'MONITORING', 'cph': 'MONITORING', 'ot': 'MONITORING',
    'da': 'FLOW', 'ar': 'FLOW', 'or': 'FLOW',
    'sa': 'STAGING', 'ol': 'STAGING',
    'op': 'TRANSITION',
}

def classify_middle(mid):
    """Classify a MIDDLE by its most common PREFIX category"""
    pfx_counts = prefix_by_middle.get(mid, Counter())
    cat_counts = Counter()
    for pfx, count in pfx_counts.items():
        if pfx in PREFIX_CATEGORY:
            cat_counts[PREFIX_CATEGORY[pfx]] += count
    if not cat_counts:
        return None
    return cat_counts.most_common(1)[0][0]

print("=" * 70)
print("MACRO-ATOM SLOT OCCUPANCY TEST")
print("=" * 70)
print(f"\nCompound MIDDLEs analyzed: {len(middle_counts)} types, {sum(middle_counts.values())} tokens")

# ============================================================
# TEST A: Macro-atom positional preference in larger compounds
# ============================================================
print("\n" + "=" * 70)
print("TEST A: Macro-Atom Position in Larger Compounds")
print("=" * 70)
print("\nFor each macro-atom, when it appears WITH other units in a compound,")
print("where does it sit? FIRST = HEAD, MIDDLE = MODIFIER, LAST = TERMINAL\n")

macro_positions = defaultdict(lambda: Counter())  # macro -> {FIRST, MIDDLE, LAST}
macro_examples = defaultdict(lambda: defaultdict(list))

for mid, count in middle_counts.items():
    decomp = find_macro_atoms(mid)
    units = [x for x in decomp]
    if len(units) < 2:
        continue  # need at least 2 units (macro + something else)

    for i, (utype, uval) in enumerate(units):
        if utype == 'MACRO':
            if i == 0:
                pos = 'FIRST'
            elif i == len(units) - 1:
                pos = 'LAST'
            else:
                pos = 'MIDDLE'
            macro_positions[uval][pos] += count
            if count >= 5:
                macro_examples[uval][pos].append((mid, count))

print(f"{'Macro':<8} {'N':>6} {'FIRST%':>8} {'MID%':>8} {'LAST%':>8} {'Slot Role':>12}")
print(f"{'-'*8} {'-'*6} {'-'*8} {'-'*8} {'-'*8} {'-'*12}")

for macro in sorted(macro_positions.keys(), key=lambda m: -sum(macro_positions[m].values())):
    counts = macro_positions[macro]
    total = sum(counts.values())
    if total < 5:
        continue
    f_pct = 100 * counts['FIRST'] / total
    m_pct = 100 * counts['MIDDLE'] / total
    l_pct = 100 * counts['LAST'] / total

    if f_pct > 60: role = 'HEAD'
    elif l_pct > 60: role = 'TERMINAL'
    elif m_pct > 40: role = 'MODIFIER'
    else: role = 'flexible'

    print(f"{macro:<8} {total:>6} {f_pct:>7.1f}% {m_pct:>7.1f}% {l_pct:>7.1f}% {role:>12}")

    # Show examples for each position
    for pos_label in ['FIRST', 'MIDDLE', 'LAST']:
        examples = macro_examples[macro].get(pos_label, [])
        if examples:
            examples.sort(key=lambda x: -x[1])
            ex_str = ', '.join(f"{mid}({n})" for mid, n in examples[:3])
            print(f"  {pos_label}: {ex_str}")

# ============================================================
# Comparison: individual atom positions from C1209
# ============================================================
print("\n--- Validation against C1209 individual atom positions ---\n")
print("Expected: k=FREE(no pref), e=HEAD(75% initial), h=TERMINAL(71%),")
print("          d=MODIFIER, y=TERMINAL(97%), n=TERMINAL(99%)\n")
print("Macro-atom positions should be CONSISTENT with their leading atom's")
print("expected slot if the macro-atom occupies ONE slot.\n")

consistency_check = {
    'ke': ('k=FREE, but ke as unit should be HEAD', 'FIRST'),
    'kee': ('same', 'FIRST'),
    'keee': ('same', 'FIRST'),
    'dy': ('d=MODIFIER+y=TERMINAL => dy should be TERMINAL', 'LAST'),
    'am': ('a=HEAD+m=TERMINAL => am flexible', 'LAST'),
    'an': ('a=HEAD+n=TERMINAL => an flexible', 'LAST'),
    'in': ('i=MODIFIER+n=TERMINAL => in should be non-FIRST', 'LAST'),
    'iin': ('same', 'LAST'),
    'ch': ('c=MODIFIER+h=TERMINAL => ch should be non-FIRST', 'MIDDLE'),
    'ck': ('c=MODIFIER+k=FREE => ck could be MIDDLE', 'MIDDLE'),
    'ct': ('c=MODIFIER+t=FREE => ct could be MIDDLE', 'MIDDLE'),
    'ph': ('p=MODIFIER+h=TERMINAL => ph should be non-FIRST', 'LAST'),
}

for macro, (explanation, expected_pos) in consistency_check.items():
    counts = macro_positions.get(macro, Counter())
    total = sum(counts.values())
    if total < 5:
        continue
    actual_pct = 100 * counts.get(expected_pos, 0) / total
    verdict = 'CONSISTENT' if actual_pct > 40 else 'INCONSISTENT'
    print(f"  {macro:<6} expected={expected_pos:<8} actual={actual_pct:>5.1f}% [{verdict}]  ({explanation})")

# ============================================================
# TEST B: Remaining atoms follow slot rules after macro extraction
# ============================================================
print("\n" + "=" * 70)
print("TEST B: Remaining Atoms After Macro Extraction")
print("=" * 70)
print("\nAfter extracting macro-atoms, do remaining individual atoms")
print("follow MODIFIER/TERMINAL slot rules? Or do 'orphaned HEADs' appear?\n")

remaining_analysis = {'follows_rules': 0, 'violates': 0, 'violation_atoms': Counter(), 'details': []}

for mid, count in middle_counts.items():
    decomp = find_macro_atoms(mid)
    units = [x for x in decomp]

    # Need at least 1 macro + 1 other unit
    macros_in = [(i, uval) for i, (utype, uval) in enumerate(units) if utype == 'MACRO']
    atoms_in = [(i, uval) for i, (utype, uval) in enumerate(units) if utype == 'ATOM']

    if not macros_in or not atoms_in:
        continue

    # Determine where remaining atoms sit relative to macro
    # If macro is FIRST, remaining atoms should be MODIFIER or TERMINAL
    # If macro is LAST, remaining atoms should be HEAD or MODIFIER
    violations = []
    first_macro_pos = macros_in[0][0]

    for pos_idx, atom in atoms_in:
        if pos_idx > first_macro_pos:
            # Atoms after a HEAD macro should be MODIFIER or TERMINAL
            if atom in HEAD_ATOMS:
                violations.append(f"{atom}@{pos_idx} is HEAD after HEAD-macro")
                remaining_analysis['violation_atoms'][atom] += count
        elif pos_idx < first_macro_pos:
            # Atoms before macro — depends on macro's expected slot
            pass  # Less constrained

    if violations:
        remaining_analysis['violates'] += count
    else:
        remaining_analysis['follows_rules'] += count

    if count >= 10:
        remaining_analysis['details'].append({
            'middle': mid,
            'tokens': count,
            'decomp': [(t, v) for t, v in units],
            'violations': violations
        })

total_tested = remaining_analysis['follows_rules'] + remaining_analysis['violates']
print(f"Total tokens with macro + other atoms: {total_tested}")
print(f"Follows rules (no HEAD atom after HEAD-macro): {remaining_analysis['follows_rules']} ({100*remaining_analysis['follows_rules']/max(1,total_tested):.1f}%)")
print(f"Violations (HEAD atom after HEAD-macro): {remaining_analysis['violates']} ({100*remaining_analysis['violates']/max(1,total_tested):.1f}%)")

if remaining_analysis['violation_atoms']:
    print(f"\nViolation atoms: {dict(remaining_analysis['violation_atoms'].most_common(10))}")

# Show details
remaining_analysis['details'].sort(key=lambda x: -x['tokens'])
print(f"\nTop compounds with macro-atoms (N>=10):")
for d in remaining_analysis['details'][:20]:
    decomp_str = ' + '.join(f"[{v}]" if t == 'MACRO' else v for t, v in d['decomp'])
    v_str = ', '.join(d['violations']) if d['violations'] else 'OK'
    print(f"  {d['middle']:<14} N={d['tokens']:>4}  {decomp_str:<35} {v_str}")

# ============================================================
# Now compare: WITHOUT macro-atoms, how many "two HEAD" violations?
# ============================================================
print("\n--- Comparison: Individual atom model ---\n")

individual_violations = 0
individual_ok = 0
individual_two_heads = 0

for mid, count in middle_counts.items():
    atoms = get_atom_sequence(mid)
    if len(atoms) < 2:
        continue

    # Count HEAD atoms
    head_count = sum(1 for a in atoms if a in HEAD_ATOMS)
    if head_count > 1:
        individual_two_heads += count

    # In individual model, atoms after the first should be MODIFIER/TERMINAL
    has_violation = False
    for i, a in enumerate(atoms):
        if i > 0 and a in HEAD_ATOMS:
            has_violation = True

    if has_violation:
        individual_violations += count
    else:
        individual_ok += count

ind_total = individual_violations + individual_ok
print(f"Individual model - tokens with multiple HEAD atoms: {individual_two_heads}/{ind_total} = {100*individual_two_heads/max(1,ind_total):.1f}%")
print(f"Individual model - violations (HEAD after pos 0): {individual_violations}/{ind_total} = {100*individual_violations/max(1,ind_total):.1f}%")
print(f"Macro model - violations (HEAD after HEAD-macro): {remaining_analysis['violates']}/{total_tested} = {100*remaining_analysis['violates']/max(1,total_tested):.1f}%")
print(f"\nViolation reduction from macro-atom grouping: {100*individual_violations/max(1,ind_total):.1f}% -> {100*remaining_analysis['violates']/max(1,total_tested):.1f}%")

# ============================================================
# TEST C: E-depth doesn't change slot structure
# ============================================================
print("\n" + "=" * 70)
print("TEST C: E-Depth Slot Structure Invariance")
print("=" * 70)
print("\nFor ke-family compounds, do following atoms stay the same regardless")
print("of e-depth? If so, e-depth is an internal parameter, not a slot filler.\n")

# For ke-family compounds, group by e-depth and compare following atoms
ke_depth_following = defaultdict(Counter)  # depth -> Counter of following atoms
ke_depth_examples = defaultdict(list)

for mid, count in middle_counts.items():
    atoms = get_atom_sequence(mid)
    if len(atoms) < 3:
        continue

    # Find ke/kee/keee at the start
    if mid.startswith('keee'):
        depth = 3
        rest = mid[4:]
    elif mid.startswith('kee'):
        depth = 2
        rest = mid[3:]
    elif mid.startswith('ke'):
        depth = 1
        rest = mid[2:]
    else:
        continue

    rest_atoms = [ch for ch in rest if ch in ATOMS]
    for a in rest_atoms:
        ke_depth_following[depth][a] += count

    if count >= 3:
        ke_depth_examples[depth].append((mid, count, ''.join(rest_atoms)))

print(f"Atoms following ke-family macro-atom by e-depth:")
all_following = sorted(set().union(*[set(c.keys()) for c in ke_depth_following.values()]))
print(f"{'Depth':<8}", end='')
for a in all_following:
    print(f" {a:>6}", end='')
print(f" {'Total':>8}")

for depth in sorted(ke_depth_following.keys()):
    total = sum(ke_depth_following[depth].values())
    print(f"ke{'e'*(depth-1):<6}", end='')
    for a in all_following:
        cnt = ke_depth_following[depth].get(a, 0)
        pct = 100 * cnt / total if total > 0 else 0
        if pct > 0:
            print(f" {pct:>5.1f}%", end='')
        else:
            print(f" {'---':>6}", end='')
    print(f" {total:>7}")

# Show examples
print(f"\nExamples by e-depth:")
for depth in sorted(ke_depth_examples.keys()):
    examples = sorted(ke_depth_examples[depth], key=lambda x: -x[1])[:5]
    ex_str = ', '.join(f"{mid}({n})" for mid, n, rest in examples)
    print(f"  ke{'e'*(depth-1)}: {ex_str}")

# Check: are following atoms MODIFIER/TERMINAL?
print(f"\nFollowing atom slot classification:")
for depth in sorted(ke_depth_following.keys()):
    total = sum(ke_depth_following[depth].values())
    mod = sum(v for k, v in ke_depth_following[depth].items() if k in MODIFIER_ATOMS)
    term = sum(v for k, v in ke_depth_following[depth].items() if k in TERMINAL_ATOMS)
    head = sum(v for k, v in ke_depth_following[depth].items() if k in HEAD_ATOMS)
    free = sum(v for k, v in ke_depth_following[depth].items() if k in FREE_ATOMS)
    print(f"  ke{'e'*(depth-1)}: MODIFIER={100*mod/max(1,total):.1f}% TERMINAL={100*term/max(1,total):.1f}% HEAD={100*head/max(1,total):.1f}% FREE={100*free/max(1,total):.1f}%")

# Also do in-family
print(f"\n--- Same analysis for in-family ---")
in_depth_following = defaultdict(Counter)
for mid, count in middle_counts.items():
    atoms = get_atom_sequence(mid)
    if len(atoms) < 3:
        continue

    # Find trailing in/iin/iiin
    if mid.endswith('iiin'):
        depth = 3
        prefix_part = mid[:-4]
    elif mid.endswith('iin'):
        depth = 2
        prefix_part = mid[:-3]
    elif mid.endswith('in'):
        depth = 1
        prefix_part = mid[:-2]
    else:
        continue

    if not prefix_part:
        continue

    prefix_atoms = [ch for ch in prefix_part if ch in ATOMS]
    for a in prefix_atoms:
        in_depth_following[depth][a] += count

if in_depth_following:
    all_preceding = sorted(set().union(*[set(c.keys()) for c in in_depth_following.values()]))
    print(f"\nAtoms PRECEDING in-family macro-atom by i-depth:")
    print(f"{'Depth':<8}", end='')
    for a in all_preceding:
        print(f" {a:>6}", end='')
    print(f" {'Total':>8}")

    for depth in sorted(in_depth_following.keys()):
        total = sum(in_depth_following[depth].values())
        label = 'i' * depth + 'n'
        print(f"{label:<8}", end='')
        for a in all_preceding:
            cnt = in_depth_following[depth].get(a, 0)
            pct = 100 * cnt / total if total > 0 else 0
            if pct > 0:
                print(f" {pct:>5.1f}%", end='')
            else:
                print(f" {'---':>6}", end='')
        print(f" {total:>7}")

# ============================================================
# TEST D: Category prediction — macro vs individual
# ============================================================
print("\n" + "=" * 70)
print("TEST D: Category Prediction — Macro vs Individual First-Unit")
print("=" * 70)
print("\nDoes predicting category from the macro-atom unit beat predicting")
print("from the first individual atom?\n")

individual_correct = 0
macro_correct = 0
total_testable = 0
category_details = defaultdict(lambda: {'ind_right': 0, 'mac_right': 0, 'total': 0})

for mid, count in middle_counts.items():
    true_cat = classify_middle(mid)
    if not true_cat:
        continue
    if count < 3:
        continue

    atoms = get_atom_sequence(mid)
    if len(atoms) < 2:
        continue

    decomp = find_macro_atoms(mid)

    # Individual model: first atom's category
    first_atom = atoms[0]
    ind_pred = ATOM_CAT.get(first_atom)

    # Macro model: first unit's category (macro or atom)
    first_unit_type, first_unit_val = decomp[0]
    if first_unit_type == 'MACRO':
        mac_pred = MACRO_CAT.get(first_unit_val)
    else:
        mac_pred = ATOM_CAT.get(first_unit_val)

    if ind_pred and mac_pred:
        total_testable += 1
        if ind_pred == true_cat:
            individual_correct += 1
            category_details[true_cat]['ind_right'] += 1
        if mac_pred == true_cat:
            macro_correct += 1
            category_details[true_cat]['mac_right'] += 1
        category_details[true_cat]['total'] += 1

print(f"Testable compounds: {total_testable}")
print(f"Individual first-atom accuracy: {individual_correct}/{total_testable} = {100*individual_correct/max(1,total_testable):.1f}%")
print(f"Macro-atom first-unit accuracy: {macro_correct}/{total_testable} = {100*macro_correct/max(1,total_testable):.1f}%")
print(f"Difference: {100*(macro_correct-individual_correct)/max(1,total_testable):+.1f}pp")

print(f"\nBy category:")
for cat in sorted(category_details.keys()):
    d = category_details[cat]
    print(f"  {cat:<14} N={d['total']:>3}  ind={100*d['ind_right']/max(1,d['total']):.0f}%  macro={100*d['mac_right']/max(1,d['total']):.0f}%  delta={100*(d['mac_right']-d['ind_right'])/max(1,d['total']):+.0f}pp")

# ============================================================
# TEST E: Do macro-atom compounds show clean 3 slots?
# ============================================================
print("\n" + "=" * 70)
print("TEST E: Slot Count With vs Without Macro-Atoms")
print("=" * 70)
print("\nDo 4+ character compounds collapse to <=3 units with macro-atom")
print("grouping? If so, the 3-slot model survives with macro-atoms.\n")

slot_counts_individual = Counter()
slot_counts_macro = Counter()

for mid, count in middle_counts.items():
    atoms = get_atom_sequence(mid)
    if len(atoms) < 2:
        continue

    decomp = find_macro_atoms(mid)
    n_individual = len(atoms)
    n_macro = len(decomp)

    slot_counts_individual[n_individual] += count
    slot_counts_macro[n_macro] += count

print(f"Unit count distribution (token-weighted):")
print(f"{'Units':<8} {'Individual':>12} {'%':>7} {'Macro-decomp':>12} {'%':>7}")
total_ind = sum(slot_counts_individual.values())
total_mac = sum(slot_counts_macro.values())
for n in sorted(set(list(slot_counts_individual.keys()) + list(slot_counts_macro.keys()))):
    ind = slot_counts_individual.get(n, 0)
    mac = slot_counts_macro.get(n, 0)
    ind_pct = 100 * ind / total_ind if total_ind else 0
    mac_pct = 100 * mac / total_mac if total_mac else 0
    print(f"{n:<8} {ind:>12} {ind_pct:>6.1f}% {mac:>12} {mac_pct:>6.1f}%")

# How many 4+ atom compounds collapse to 3 units with macro decomposition?
collapsed_to_3 = 0
collapsed_to_2 = 0
total_4plus = 0
collapse_examples = []

for mid, count in middle_counts.items():
    atoms = get_atom_sequence(mid)
    if len(atoms) < 4:
        continue
    total_4plus += count
    decomp = find_macro_atoms(mid)
    if len(decomp) <= 3:
        collapsed_to_3 += count
    if len(decomp) <= 2:
        collapsed_to_2 += count
    if count >= 5:
        decomp_str = ' + '.join(f"[{v}]" if t == 'MACRO' else v for t, v in decomp)
        collapse_examples.append((mid, count, len(atoms), len(decomp), decomp_str))

print(f"\n4+ atom compounds: {total_4plus} tokens")
print(f"  Collapse to <=3 units: {collapsed_to_3} ({100*collapsed_to_3/max(1,total_4plus):.1f}%)")
print(f"  Collapse to <=2 units: {collapsed_to_2} ({100*collapsed_to_2/max(1,total_4plus):.1f}%)")

# Also: fraction at each atom count
print(f"\nCollapse rate by original atom count:")
by_orig_count = defaultdict(lambda: {'total': 0, 'collapsed': 0})
for mid, count in middle_counts.items():
    atoms = get_atom_sequence(mid)
    if len(atoms) < 4:
        continue
    decomp = find_macro_atoms(mid)
    by_orig_count[len(atoms)]['total'] += count
    if len(decomp) <= 3:
        by_orig_count[len(atoms)]['collapsed'] += count

for n_atoms in sorted(by_orig_count.keys()):
    d = by_orig_count[n_atoms]
    print(f"  {n_atoms} atoms -> <=3 units: {d['collapsed']}/{d['total']} = {100*d['collapsed']/max(1,d['total']):.1f}%")

# Show examples
collapse_examples.sort(key=lambda x: -x[1])
print(f"\nExamples of 4+ atom compounds (N>=5):")
print(f"{'MIDDLE':<16} {'N':>5} {'atoms':>5} {'units':>5} {'Decomposition'}")
for mid, n, n_atoms, n_units, decomp_str in collapse_examples[:20]:
    status = 'OK' if n_units <= 3 else 'OVERFLOW'
    print(f"  {mid:<14} {n:>5} {n_atoms:>5} {n_units:>5} {decomp_str} [{status}]")

# ============================================================
# SUMMARY
# ============================================================
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

# Test A summary
print(f"\nTest A — Macro-atom positional preferences:")
for macro in ['ke', 'kee', 'keee', 'dy', 'am', 'an', 'in', 'iin', 'ch', 'ck', 'ct', 'ph']:
    counts = macro_positions.get(macro, Counter())
    total = sum(counts.values())
    if total < 5:
        continue
    f_pct = 100 * counts['FIRST'] / total
    l_pct = 100 * counts['LAST'] / total
    dominant = 'FIRST' if f_pct > l_pct else 'LAST'
    dom_pct = max(f_pct, l_pct)
    print(f"  {macro:<6} -> {dominant} at {dom_pct:.0f}%")

print(f"\nTest B — Slot rule compliance after macro extraction:")
print(f"  Macro model violation rate: {100*remaining_analysis['violates']/max(1,total_tested):.1f}%")
print(f"  Individual model violation rate: {100*individual_violations/max(1,ind_total):.1f}%")
print(f"  Improvement: {100*individual_violations/max(1,ind_total) - 100*remaining_analysis['violates']/max(1,total_tested):.1f}pp")

print(f"\nTest C — E-depth invariance:")
depths_with_data = [d for d in ke_depth_following if sum(ke_depth_following[d].values()) >= 10]
if len(depths_with_data) >= 2:
    # Compare atom distributions across depths
    from scipy.stats import chi2_contingency
    try:
        # Build contingency table
        all_atoms_c = sorted(set().union(*[set(ke_depth_following[d].keys()) for d in depths_with_data]))
        contingency = []
        for d in sorted(depths_with_data):
            row = [ke_depth_following[d].get(a, 0) for a in all_atoms_c]
            contingency.append(row)
        if len(contingency) >= 2:
            chi2, p, dof, expected = chi2_contingency(contingency)
            print(f"  Chi-squared across e-depths: chi2={chi2:.1f}, p={p:.4f}")
            if p > 0.05:
                print(f"  PASS: No significant difference — e-depth is internal parameter")
            else:
                print(f"  FAIL: Significant difference — e-depth changes slot context")
    except Exception as e:
        print(f"  Could not compute chi-squared: {e}")
else:
    print(f"  Insufficient data for chi-squared test")

print(f"\nTest D — Category prediction:")
print(f"  Individual: {100*individual_correct/max(1,total_testable):.1f}%")
print(f"  Macro: {100*macro_correct/max(1,total_testable):.1f}%")
verdict_d = 'MACRO WINS' if macro_correct > individual_correct else ('TIE' if macro_correct == individual_correct else 'INDIVIDUAL WINS')
print(f"  Verdict: {verdict_d}")

print(f"\nTest E — 3-slot model survival:")
print(f"  4+ atom compounds collapsing to <=3 units: {100*collapsed_to_3/max(1,total_4plus):.1f}%")

# Overall verdict
print(f"\n{'=' * 70}")
print("OVERALL VERDICT")
print(f"{'=' * 70}")
a_pass = all(macro_positions.get(m, Counter()).get('FIRST', 0) > 0.5 * sum(macro_positions.get(m, Counter()).values())
             for m in ['ke', 'kee'] if sum(macro_positions.get(m, Counter()).values()) >= 10)
b_pass = remaining_analysis['violates'] / max(1, total_tested) < 0.20
d_pass = macro_correct >= individual_correct
e_pass = collapsed_to_3 / max(1, total_4plus) > 0.50

tests = [
    ('A', 'ke-family occupies HEAD slot', a_pass),
    ('B', 'Remaining atoms follow slot rules', b_pass),
    ('D', 'Macro improves category prediction', d_pass),
    ('E', '4+ atoms collapse to <=3 slots', e_pass),
]

for label, description, passed in tests:
    status = 'PASS' if passed else 'FAIL'
    print(f"  Test {label}: [{status}] {description}")

all_pass = all(p for _, _, p in tests)
print(f"\n  MACRO-ATOM SLOT MODEL: {'SUPPORTED' if all_pass else 'MIXED — see details above'}")

# Save results
output = {
    'test_a_macro_positions': {macro: dict(counts) for macro, counts in macro_positions.items()},
    'test_b_follows_rules_pct': round(100*remaining_analysis['follows_rules']/max(1,total_tested), 1),
    'test_b_violates_pct': round(100*remaining_analysis['violates']/max(1,total_tested), 1),
    'test_b_individual_violation_pct': round(100*individual_violations/max(1,ind_total), 1),
    'test_d_individual_acc': round(100*individual_correct/max(1,total_testable), 1),
    'test_d_macro_acc': round(100*macro_correct/max(1,total_testable), 1),
    'test_e_collapse_pct': round(100*collapsed_to_3/max(1,total_4plus), 1),
}

output_path = os.path.join(os.path.dirname(__file__), '..', 'results', 'macro_atom_slot_test.json')
os.makedirs(os.path.dirname(output_path), exist_ok=True)
with open(output_path, 'w') as f:
    json.dump(output, f, indent=2)
print(f"\nResults saved to {output_path}")
