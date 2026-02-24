"""
Phase 440 (round 4): PREFIX modifier characterization.
Goal: Derive modifier-specific glosses for the PREFIX atom table.

For each modifier, compare the MIDDLE content it selects vs the base-only average.
This reveals what the modifier ADDS or SHIFTS.
"""
import sys
from collections import Counter, defaultdict
from pathlib import Path
import math

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from scripts.voynich import Transcript, Morphology

tx = Transcript()
morph = Morphology()
b_tokens = list(tx.currier_b())

morphs = []
for tok in b_tokens:
    if not tok.word.strip() or '*' in tok.word:
        continue
    m = morph.extract(tok.word)
    if m.prefix and m.middle:
        morphs.append((tok, m))

# Axis classification for MIDDLE atoms (from C1207)
AXIS = {
    'a': 'ITER', 'i': 'ITER', 'n': 'ITER', 'r': 'ITER',
    'k': 'ENRG', 'l': 'ENRG',
    'e': 'STAB', 'h': 'STAB',
    'd': 'CLOS', 'y': 'CLOS',
    'o': 'FREE', 'c': 'STRC', 's': 'STRC',
    'm': 'CLOS', 't': 'STRC', 'p': 'STRC', 'f': 'STRC', 'g': 'STRC',
}
AXES = ['ITER', 'ENRG', 'STAB', 'CLOS', 'STRC', 'FREE']

def axis_profile(middle_str):
    """Compute axis fractions for a MIDDLE string."""
    counts = Counter(AXIS.get(c, 'UNK') for c in middle_str)
    total = sum(counts.values())
    if total == 0:
        return {a: 0 for a in AXES}
    return {a: counts.get(a, 0) / total for a in AXES}

def mean_profile(profiles):
    """Average a list of axis profiles."""
    if not profiles:
        return {a: 0 for a in AXES}
    result = {a: 0 for a in AXES}
    for p in profiles:
        for a in AXES:
            result[a] += p[a]
    return {a: v / len(profiles) for a, v in result.items()}

# Group by prefix
prefix_profiles = defaultdict(list)
for tok, m in morphs:
    prefix_profiles[m.prefix].append(axis_profile(m.middle))

# Only prefixes with 30+ tokens
prefix_means = {}
for pfx, profiles in prefix_profiles.items():
    if len(profiles) >= 30:
        prefix_means[pfx] = (mean_profile(profiles), len(profiles))

# Decompose each prefix into modifier + base
def decompose(pfx):
    if len(pfx) == 1:
        return None, pfx  # single char = base only
    elif len(pfx) == 2:
        return pfx[0], pfx[1]
    elif len(pfx) == 3:
        return pfx[0], pfx[1:]  # e.g., pch -> p, ch (but ch is actually base h with sub-modifier c)
        # Actually for 3-char: pos0=modifier, pos1=sub, pos2=base(h)
        # Let's just use first char as modifier, last char as base
        return pfx[0], pfx[-1]
    return pfx[0], pfx[-1]

# For 3-char prefixes, modifier=first char, base=last char
def get_mod_base(pfx):
    if len(pfx) == 1:
        return None, pfx
    return pfx[0], pfx[-1]

# Group prefixes by base character
base_groups = defaultdict(list)
for pfx, (profile, n) in prefix_means.items():
    mod, base = get_mod_base(pfx)
    base_groups[base].append((pfx, mod, profile, n))

print("=" * 80)
print("PREFIX MODIFIER ANALYSIS")
print("=" * 80)

# For each base, show all modifiers and their profiles
for base in sorted(base_groups.keys(), key=lambda b: -sum(n for _, _, _, n in base_groups[b])):
    group = base_groups[base]
    total_n = sum(n for _, _, _, n in group)

    # Base average (all prefixes with this base)
    all_profiles = []
    for pfx in prefix_profiles:
        m, b = get_mod_base(pfx)
        if b == base and len(prefix_profiles[pfx]) >= 30:
            all_profiles.extend(prefix_profiles[pfx])
    base_avg = mean_profile([axis_profile(''.join([])) for _ in range(1)])  # placeholder

    # Actually compute base average from all tokens with this base
    base_token_profiles = []
    for pfx, mod, profile, n in group:
        base_token_profiles.extend(prefix_profiles[pfx])
    base_avg = mean_profile(base_token_profiles)

    print(f"\n{'-' * 80}")
    print(f"BASE '{base}' -- {total_n} tokens, {len(group)} prefixes")
    print(f"  Base average: {' '.join(f'{a}:{base_avg[a]:.1%}' for a in AXES)}")
    print()

    for pfx, mod, profile, n in sorted(group, key=lambda x: -x[3]):
        # Compute delta from base average
        delta = {a: profile[a] - base_avg[a] for a in AXES}
        delta_str = ' '.join(f'{a}:{delta[a]:+.1%}' for a in AXES if abs(delta[a]) > 0.02)

        mod_label = mod if mod else '(bare)'
        print(f"  {pfx:6s} (mod={mod_label}, n={n:4d}): {' '.join(f'{a}:{profile[a]:.1%}' for a in AXES)}")
        if delta_str:
            print(f"         DELTA from base avg: {delta_str}")

# ============================================================
# Now analyze each MODIFIER across all bases
# ============================================================
print(f"\n\n{'=' * 80}")
print("MODIFIER ANALYSIS -- cross-base behavior")
print("=" * 80)

mod_groups = defaultdict(list)
for pfx, (profile, n) in prefix_means.items():
    mod, base = get_mod_base(pfx)
    if mod:
        mod_groups[mod].append((pfx, base, profile, n))

for mod in sorted(mod_groups.keys(), key=lambda m: -sum(n for _, _, _, n in mod_groups[m])):
    group = mod_groups[mod]
    total_n = sum(n for _, _, _, n in group)
    bases_used = [base for _, base, _, _ in group]

    print(f"\n{'-' * 80}")
    print(f"MODIFIER '{mod}' -- {total_n} tokens across {len(group)} bases: {', '.join(bases_used)}")

    # For each prefix with this modifier, compute delta vs base average (without this modifier)
    for pfx, base, profile, n in sorted(group, key=lambda x: -x[3]):
        # Get base average
        base_grp = base_groups.get(base, [])
        if len(base_grp) > 1:
            # Average of OTHER modifiers in this base
            other_profiles = []
            for opfx, omod, oprofile, on in base_grp:
                if opfx != pfx:
                    other_profiles.extend(prefix_profiles[opfx])
            other_avg = mean_profile(other_profiles)
            delta = {a: profile[a] - other_avg[a] for a in AXES}
            delta_str = ' '.join(f'{a}:{delta[a]:+.1%}' for a in AXES if abs(delta[a]) > 0.02)
        else:
            delta_str = "(only modifier for this base)"

        print(f"  {pfx:6s} (base={base}, n={n:4d}): {' '.join(f'{a}:{profile[a]:.1%}' for a in AXES)}")
        if delta_str:
            print(f"         vs other {base}-base: {delta_str}")

    # Cross-base consistency summary
    if len(group) >= 2:
        # What direction does this modifier consistently shift?
        shift_sums = {a: 0 for a in AXES}
        shift_count = 0
        for pfx, base, profile, n in group:
            base_grp = base_groups.get(base, [])
            if len(base_grp) > 1:
                other_profiles = []
                for opfx, omod, oprofile, on in base_grp:
                    if opfx != pfx:
                        other_profiles.extend(prefix_profiles[opfx])
                other_avg = mean_profile(other_profiles)
                for a in AXES:
                    shift_sums[a] += profile[a] - other_avg[a]
                shift_count += 1

        if shift_count > 0:
            avg_shift = {a: shift_sums[a] / shift_count for a in AXES}
            sig_shifts = [(a, avg_shift[a]) for a in AXES if abs(avg_shift[a]) > 0.02]
            sig_shifts.sort(key=lambda x: -abs(x[1]))
            if sig_shifts:
                print(f"  CONSISTENT SHIFT: {' '.join(f'{a}:{v:+.1%}' for a, v in sig_shifts)}")
            else:
                print(f"  CONSISTENT SHIFT: none significant (base-dependent)")

# ============================================================
# Special analysis: q modifier (only qo exists)
# ============================================================
print(f"\n\n{'=' * 80}")
print("SPECIAL: q modifier (dedicated, only pairs with o-base)")
print("=" * 80)

qo_profile = prefix_means.get('qo', (None, 0))
if qo_profile[0]:
    print(f"\n  qo (n={qo_profile[1]}): {' '.join(f'{a}:{qo_profile[0][a]:.1%}' for a in AXES)}")

    # Compare to all other o-base prefixes
    o_group = base_groups.get('o', [])
    other_o = [(pfx, profile, n) for pfx, mod, profile, n in o_group if pfx != 'qo']

    print(f"\n  Other o-base prefixes:")
    for pfx, profile, n in sorted(other_o, key=lambda x: -x[2]):
        delta = {a: qo_profile[0][a] - profile[a] for a in AXES}
        delta_str = ' '.join(f'{a}:{delta[a]:+.1%}' for a in AXES if abs(delta[a]) > 0.03)
        print(f"    vs {pfx:6s} (n={n:4d}): {delta_str}")

    # qo vs average of all other o-base
    if other_o:
        all_other_o_profiles = []
        for pfx, _, _ in other_o:
            all_other_o_profiles.extend(prefix_profiles[pfx])
        other_o_avg = mean_profile(all_other_o_profiles)
        delta = {a: qo_profile[0][a] - other_o_avg[a] for a in AXES}
        sig = [(a, delta[a]) for a in AXES if abs(delta[a]) > 0.02]
        sig.sort(key=lambda x: -abs(x[1]))
        print(f"\n  qo vs all-other-o: {' '.join(f'{a}:{v:+.1%}' for a, v in sig)}")
        print(f"  qo is {'MORE' if delta['ENRG'] > 0 else 'LESS'} energy-focused than other o-base prefixes")

# ============================================================
# Dedicated modifier summary
# ============================================================
print(f"\n\n{'=' * 80}")
print("DEDICATED MODIFIER SUMMARY (never appear as base)")
print("=" * 80)

dedicated = ['q', 'd', 'f', 'p', 'y', 's']
for mod in dedicated:
    if mod in mod_groups:
        group = mod_groups[mod]
        total_n = sum(n for _, _, _, n in group)
        bases = [(base, n) for _, base, _, n in group]
        print(f"\n  {mod}: {total_n} tokens, bases: {bases}")

        # Overall profile of all tokens with this modifier
        all_mod_profiles = []
        for pfx, base, profile, n in group:
            all_mod_profiles.extend(prefix_profiles[pfx])
        mod_avg = mean_profile(all_mod_profiles)
        print(f"     avg profile: {' '.join(f'{a}:{mod_avg[a]:.1%}' for a in AXES)}")

print(f"\n{'=' * 80}")
print("Analysis complete.")
print(f"{'=' * 80}")
