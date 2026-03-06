"""
Phase 545: Executive Atom Instability -- p/f/c Cross-System Analysis

C1509 identifies 3 UNSTABLE atoms {p,f,c} whose behavioral profiles shift most
between A's declarative register and B's execution grammar. This phase asks:
WHY are they unstable? What structural mechanism drives the cross-system shift?

Research Questions:
1. How do p/f/c distribute across A, B, AZC relative to stable MOD peers {i,d,s}?
2. What is the JSD decomposition -- which behavioral dimensions drive instability?
3. How do p/f/c interact with headed vs headless compounds?
4. Do p/f/c have different positional slot preferences in PREFIX vs MIDDLE?
5. How do p/f/c relate to suffix Mode A/B?
6. Do p/f/c interact differently with terminal atoms?
7. What is p/f/c's relationship to hazard classes?
8. Do p/f/c show different line-position profiles across systems?
9. Is the instability a frequency artifact or a genuine behavioral shift?
"""

import sys, os, json
import numpy as np
from collections import Counter, defaultdict
from itertools import combinations
from scipy.stats import chi2_contingency, spearmanr, fisher_exact
from scipy.spatial.distance import jensenshannon

sys.path.insert(0, 'C:/git/voynich')
from scripts.voynich import Transcript, Morphology

# ---------------------------------------------------------------------------
# 0.  Data Loading
# ---------------------------------------------------------------------------
tx = Transcript()
morph = Morphology()

HEAD_SET = {'a', 'e', 'o', 'k', 't'}
MOD_SET = {'p', 'i', 'c', 'f', 'd', 's'}
TERM_SET = {'y', 'l', 'r', 'h', 'm', 'n'}
UNSTABLE = {'p', 'f', 'c'}
STABLE_MODS = {'i', 'd', 's'}
ALL_ATOMS = set('aeoktpicfdsylrhmn')  # 18 atoms from C1394

def get_middle_head(middle):
    """Get HEAD atom (first char from HEAD set, None if headless)."""
    if not middle:
        return None
    if middle[0] in HEAD_SET:
        return middle[0]
    return None

def get_middle_terminal(middle):
    """Get terminal atom (last char)."""
    if not middle:
        return None
    return middle[-1]

def is_headless(middle):
    """True if MIDDLE has no HEAD atom at position 0."""
    if not middle:
        return True
    return middle[0] not in HEAD_SET

def get_middle_atoms(middle):
    """Get set of distinct atoms in a MIDDLE."""
    if not middle:
        return set()
    return set(middle)

def get_prefix_base(pfx):
    """Base = final character of PREFIX."""
    if not pfx:
        return None
    return pfx[-1]

def get_prefix_modifier(pfx):
    """Modifier = all characters before the base in PREFIX."""
    if not pfx or len(pfx) <= 1:
        return None
    return pfx[:-1]

def jsd(p, q):
    """Jensen-Shannon Divergence between two distributions (as dicts)."""
    all_keys = set(list(p.keys()) + list(q.keys()))
    p_arr = np.array([p.get(k, 0) for k in sorted(all_keys)], dtype=float)
    q_arr = np.array([q.get(k, 0) for k in sorted(all_keys)], dtype=float)
    p_sum = p_arr.sum()
    q_sum = q_arr.sum()
    if p_sum == 0 or q_sum == 0:
        return 1.0
    p_arr /= p_sum
    q_arr /= q_sum
    return float(jensenshannon(p_arr, q_arr) ** 2)  # squared to match C1509 convention

# ---------------------------------------------------------------------------
# 1.  Collect all tokens across all systems
# ---------------------------------------------------------------------------
records = []

def collect(token_iter, system_tag):
    for token in token_iter:
        w = token.word.strip()
        if not w or '*' in w:
            continue
        m = morph.extract(w)
        if m is None:
            continue
        middle = m.middle if m.middle else ''
        rec = {
            'word': w,
            'folio': token.folio,
            'line': token.line,
            'prefix': m.prefix,
            'middle': middle,
            'suffix': m.suffix,
            'articulator': m.articulator,
            'has_articulator': bool(m.has_articulator),
            'section': token.section,
            'system': system_tag,
            'line_initial': bool(token.line_initial),
            'line_final': bool(token.line_final),
            'par_initial': bool(token.par_initial),
            'par_final': bool(token.par_final),
            'head': get_middle_head(middle),
            'terminal': get_middle_terminal(middle),
            'is_headless': is_headless(middle),
            'middle_atoms': get_middle_atoms(middle),
            'prefix_base': get_prefix_base(m.prefix) if m.prefix else None,
            'prefix_mod': get_prefix_modifier(m.prefix) if m.prefix else None,
        }
        records.append(rec)

collect(tx.currier_a(), 'A')
collect(tx.currier_b(), 'B')
collect(tx.azc(), 'AZC')

print(f"Total tokens: {len(records)}")
sys_counts = Counter(r['system'] for r in records)
print(f"  A={sys_counts['A']}, B={sys_counts['B']}, AZC={sys_counts['AZC']}")

results = {}

# ---------------------------------------------------------------------------
# 2. DIMENSION 1: Cross-system atom frequency distribution
# ---------------------------------------------------------------------------
print("\n=== DIMENSION 1: Cross-System Frequency ===")

# Count atom occurrences in MIDDLE position across systems
def count_atoms_in_slot(records_list, slot='middle'):
    """Count each atom's frequency in a given slot across systems."""
    counts = defaultdict(lambda: Counter())  # atom -> Counter(system)
    for r in records_list:
        val = r.get(slot, '') or ''
        for ch in val:
            if ch in ALL_ATOMS:
                counts[ch][r['system']] += 1
    return counts

middle_atom_counts = count_atoms_in_slot(records, 'middle')

# For each atom, compute cross-system distribution
atom_sys_dist = {}
for atom in sorted(ALL_ATOMS):
    c = middle_atom_counts.get(atom, Counter())
    total = sum(c.values())
    if total == 0:
        continue
    dist = {s: c.get(s, 0) for s in ['A', 'B', 'AZC']}
    pcts = {s: round(v / total * 100, 1) for s, v in dist.items()}
    atom_sys_dist[atom] = {
        'counts': dist,
        'percentages': pcts,
        'total': total,
        'tier': 'UNSTABLE' if atom in UNSTABLE else ('STABLE_MOD' if atom in STABLE_MODS else 'OTHER'),
    }

# Compute system-level enrichment for unstable vs stable MODs
print("\nAtom system distribution (MIDDLE position):")
print(f"{'atom':>4} {'tier':>12} {'total':>6} {'A%':>6} {'B%':>6} {'AZC%':>6}")
for atom in sorted(atom_sys_dist.keys()):
    d = atom_sys_dist[atom]
    print(f"{atom:>4} {d['tier']:>12} {d['total']:>6} {d['percentages']['A']:>6} {d['percentages']['B']:>6} {d['percentages']['AZC']:>6}")

# Also count in PREFIX position
prefix_atom_counts = count_atoms_in_slot(records, 'prefix')
# And suffix position
suffix_atom_counts = count_atoms_in_slot(records, 'suffix')

# Build slot-by-system profiles for p/f/c
slot_profiles = {}
for atom in sorted(UNSTABLE | STABLE_MODS):
    profile = {}
    for slot_name, slot_counts in [('MIDDLE', middle_atom_counts), ('PREFIX', prefix_atom_counts), ('SUFFIX', suffix_atom_counts)]:
        c = slot_counts.get(atom, Counter())
        profile[slot_name] = {s: c.get(s, 0) for s in ['A', 'B', 'AZC']}
    slot_profiles[atom] = profile

print("\nSlot-by-system profiles for MOD atoms:")
for atom in sorted(slot_profiles.keys()):
    p = slot_profiles[atom]
    tag = 'UNSTABLE' if atom in UNSTABLE else 'STABLE'
    mid_total = sum(p['MIDDLE'].values())
    pfx_total = sum(p['PREFIX'].values())
    sfx_total = sum(p['SUFFIX'].values())
    print(f"  {atom} ({tag}): MIDDLE={mid_total}, PREFIX={pfx_total}, SUFFIX={sfx_total}")

results['dimension1_frequency'] = {
    'atom_system_distribution': atom_sys_dist,
    'slot_profiles': {k: {sk: dict(sv) for sk, sv in v.items()} for k, v in slot_profiles.items()},
}

# ---------------------------------------------------------------------------
# 3. DIMENSION 2: JSD Decomposition -- what dimensions drive instability?
# ---------------------------------------------------------------------------
print("\n=== DIMENSION 2: JSD Decomposition ===")

# For each atom, compute behavioral profile in A and B across multiple dimensions
# Then compute JSD between A and B profiles for each dimension

def build_profile(records_list, atom, system, dimension_fn):
    """Build distribution of dimension values for tokens containing `atom` in MIDDLE."""
    counts = Counter()
    for r in records_list:
        if r['system'] != system:
            continue
        middle = r.get('middle', '') or ''
        if atom not in middle:
            continue
        val = dimension_fn(r)
        if val is not None:
            counts[val] += 1
    return dict(counts)

# Dimension functions
def dim_head(r): return r['head'] if r['head'] else 'headless'
def dim_terminal(r): return r['terminal']
def dim_has_suffix(r): return 'suffixed' if r['suffix'] else 'bare'
def dim_prefix_base(r): return r['prefix_base'] if r['prefix_base'] else 'BARE'
def dim_line_pos(r):
    if r['line_initial']: return 'initial'
    if r['line_final']: return 'final'
    return 'medial'
def dim_par_pos(r):
    if r['par_initial']: return 'par_initial'
    if r['par_final']: return 'par_final'
    return 'par_body'
def dim_articulator(r): return 'yes' if r['has_articulator'] else 'no'
def dim_headless(r): return 'headless' if r['is_headless'] else 'headed'

dimensions = {
    'head': dim_head,
    'terminal': dim_terminal,
    'suffix_presence': dim_has_suffix,
    'prefix_base': dim_prefix_base,
    'line_position': dim_line_pos,
    'paragraph_position': dim_par_pos,
    'articulator': dim_articulator,
    'headed_status': dim_headless,
}

jsd_results = {}
for atom in sorted(ALL_ATOMS):
    atom_jsd = {}
    for dim_name, dim_fn in dimensions.items():
        prof_a = build_profile(records, atom, 'A', dim_fn)
        prof_b = build_profile(records, atom, 'B', dim_fn)
        j = jsd(prof_a, prof_b)
        atom_jsd[dim_name] = round(j, 4)
    mean_jsd = round(np.mean(list(atom_jsd.values())), 4)
    atom_jsd['mean'] = mean_jsd
    jsd_results[atom] = atom_jsd

print("\nJSD(A,B) by atom and dimension:")
dim_names = list(dimensions.keys())
header = f"{'atom':>4} {'tier':>10} " + " ".join(f"{d[:8]:>8}" for d in dim_names) + f" {'MEAN':>8}"
print(header)
for atom in sorted(jsd_results.keys()):
    d = jsd_results[atom]
    tier = 'UNSTABLE' if atom in UNSTABLE else ('STABLE_MOD' if atom in STABLE_MODS else 'OTHER')
    vals = " ".join(f"{d[dim]:>8.4f}" for dim in dim_names)
    print(f"{atom:>4} {tier:>10} {vals} {d['mean']:>8.4f}")

# Identify which dimensions maximally separate unstable from stable
print("\nDimension-level separation (mean JSD for UNSTABLE vs STABLE_MOD):")
for dim_name in dim_names:
    unstable_jsds = [jsd_results[a][dim_name] for a in UNSTABLE if a in jsd_results]
    stable_jsds = [jsd_results[a][dim_name] for a in STABLE_MODS if a in jsd_results]
    u_mean = np.mean(unstable_jsds) if unstable_jsds else 0
    s_mean = np.mean(stable_jsds) if stable_jsds else 0
    ratio = round(u_mean / s_mean, 2) if s_mean > 0 else float('inf')
    print(f"  {dim_name:>20}: UNSTABLE={u_mean:.4f}, STABLE_MOD={s_mean:.4f}, ratio={ratio}x")

results['dimension2_jsd'] = jsd_results

# ---------------------------------------------------------------------------
# 4. DIMENSION 3: Headed vs Headless interaction
# ---------------------------------------------------------------------------
print("\n=== DIMENSION 3: Headed vs Headless ===")

# For each MOD atom, compute headless rate in A vs B
headless_rates = {}
for atom in sorted(UNSTABLE | STABLE_MODS):
    rates = {}
    for sys in ['A', 'B', 'AZC']:
        headed, headless = 0, 0
        for r in records:
            if r['system'] != sys:
                continue
            middle = r.get('middle', '') or ''
            if atom not in middle:
                continue
            if r['is_headless']:
                headless += 1
            else:
                headed += 1
        total = headed + headless
        if total > 0:
            rates[sys] = {'headed': headed, 'headless': headless, 'headless_rate': round(headless / total, 4), 'total': total}
        else:
            rates[sys] = {'headed': 0, 'headless': 0, 'headless_rate': 0.0, 'total': 0}
    headless_rates[atom] = rates

print("\nHeadless rates by atom and system:")
print(f"{'atom':>4} {'tier':>10} {'A_rate':>8} {'A_n':>6} {'B_rate':>8} {'B_n':>6} {'AZC_rate':>8} {'AZC_n':>6} {'A-B_diff':>10}")
for atom in sorted(headless_rates.keys()):
    d = headless_rates[atom]
    tier = 'UNSTABLE' if atom in UNSTABLE else 'STABLE'
    a_rate = d['A']['headless_rate']
    b_rate = d['B']['headless_rate']
    diff = round(a_rate - b_rate, 4)
    print(f"{atom:>4} {tier:>10} {a_rate:>8.4f} {d['A']['total']:>6} {b_rate:>8.4f} {d['B']['total']:>6} {d['AZC']['headless_rate']:>8.4f} {d['AZC']['total']:>6} {diff:>10.4f}")

results['dimension3_headless'] = {k: {sk: dict(sv) for sk, sv in v.items()} for k, v in headless_rates.items()}

# ---------------------------------------------------------------------------
# 5. DIMENSION 4: PREFIX vs MIDDLE slot behavior
# ---------------------------------------------------------------------------
print("\n=== DIMENSION 4: Slot Position Preferences ===")

# For p/f/c, compare their behavior when appearing in PREFIX vs MIDDLE
# What HEAD atoms do they co-occur with in each position?
slot_head_cooccurrence = {}
for atom in sorted(UNSTABLE | STABLE_MODS):
    cooc = {}
    for sys in ['A', 'B', 'AZC']:
        # In MIDDLE: what HEAD does this atom appear with?
        mid_heads = Counter()
        for r in records:
            if r['system'] != sys:
                continue
            middle = r.get('middle', '') or ''
            if atom not in middle:
                continue
            h = r['head']
            mid_heads[h if h else 'headless'] += 1

        # In PREFIX: what MIDDLE HEAD does this atom's prefix co-occur with?
        pfx_heads = Counter()
        for r in records:
            if r['system'] != sys:
                continue
            pfx = r.get('prefix', '') or ''
            if atom not in pfx:
                continue
            h = r['head']
            pfx_heads[h if h else 'headless'] += 1

        cooc[sys] = {
            'in_middle': dict(mid_heads),
            'in_prefix': dict(pfx_heads),
        }
    slot_head_cooccurrence[atom] = cooc

# Print summary of HEAD co-occurrence shift between PREFIX and MIDDLE
print("\nHEAD co-occurrence: atom in PREFIX vs MIDDLE (B system only):")
for atom in sorted(UNSTABLE | STABLE_MODS):
    d = slot_head_cooccurrence[atom]['B']
    mid_total = sum(d['in_middle'].values())
    pfx_total = sum(d['in_prefix'].values())
    tier = 'UNSTABLE' if atom in UNSTABLE else 'STABLE'
    print(f"\n  {atom} ({tier}):")
    print(f"    In MIDDLE (n={mid_total}): {dict(sorted(d['in_middle'].items(), key=lambda x: -x[1]))}")
    print(f"    In PREFIX (n={pfx_total}): {dict(sorted(d['in_prefix'].items(), key=lambda x: -x[1]))}")

results['dimension4_slot_position'] = slot_head_cooccurrence

# ---------------------------------------------------------------------------
# 6. DIMENSION 5: Suffix Mode A/B interaction
# ---------------------------------------------------------------------------
print("\n=== DIMENSION 5: Suffix Mode Interaction ===")

# Mode A suffixes vs Mode B suffixes (from C1229, C1410, C1515)
# Mode A = {d, e, ee, h, y} THERMAL/MONITORING
# Mode B = {a, i, ii, l, m, n, o, r, s} STAGING/FLOW
MODE_A_SUFFIXES = {'d', 'e', 'ee', 'h', 'y', 'ey', 'edy', 'eey', 'dy', 'hy'}
MODE_B_SUFFIXES = {'a', 'i', 'ii', 'l', 'm', 'n', 'o', 'r', 's', 'al', 'ar', 'or', 'am', 'ol', 'aiin', 'ain', 'iin'}

# For each atom, compute Mode A/B ratio when atom is in MIDDLE
mode_results = {}
for atom in sorted(UNSTABLE | STABLE_MODS):
    mode_by_sys = {}
    for sys in ['A', 'B', 'AZC']:
        mode_a_count = 0
        mode_b_count = 0
        bare_count = 0
        other_count = 0
        for r in records:
            if r['system'] != sys:
                continue
            middle = r.get('middle', '') or ''
            if atom not in middle:
                continue
            sfx = r['suffix']
            if not sfx:
                bare_count += 1
            elif sfx in MODE_A_SUFFIXES:
                mode_a_count += 1
            elif sfx in MODE_B_SUFFIXES:
                mode_b_count += 1
            else:
                other_count += 1
        total = mode_a_count + mode_b_count + bare_count + other_count
        mode_by_sys[sys] = {
            'mode_a': mode_a_count,
            'mode_b': mode_b_count,
            'bare': bare_count,
            'other': other_count,
            'total': total,
            'mode_a_rate': round(mode_a_count / total, 4) if total > 0 else 0,
            'mode_b_rate': round(mode_b_count / total, 4) if total > 0 else 0,
        }
    mode_results[atom] = mode_by_sys

print("\nSuffix Mode rates (B system):")
print(f"{'atom':>4} {'tier':>10} {'modeA%':>8} {'modeB%':>8} {'bare%':>8} {'n':>6}")
for atom in sorted(mode_results.keys()):
    d = mode_results[atom]['B']
    tier = 'UNSTABLE' if atom in UNSTABLE else 'STABLE'
    ma = round(d['mode_a_rate'] * 100, 1)
    mb = round(d['mode_b_rate'] * 100, 1)
    bare = round(d['bare'] / d['total'] * 100, 1) if d['total'] > 0 else 0
    print(f"{atom:>4} {tier:>10} {ma:>8.1f} {mb:>8.1f} {bare:>8.1f} {d['total']:>6}")

# Cross-system Mode A rate shift for unstable vs stable
print("\nMode A rate shift (A vs B):")
for atom in sorted(UNSTABLE | STABLE_MODS):
    d_a = mode_results[atom]['A']
    d_b = mode_results[atom]['B']
    tier = 'UNSTABLE' if atom in UNSTABLE else 'STABLE'
    shift = round(d_b['mode_a_rate'] - d_a['mode_a_rate'], 4)
    print(f"  {atom} ({tier}): A_modeA={d_a['mode_a_rate']:.4f} -> B_modeA={d_b['mode_a_rate']:.4f}, shift={shift:+.4f}")

results['dimension5_suffix_mode'] = mode_results

# ---------------------------------------------------------------------------
# 7. DIMENSION 6: Terminal atom interaction
# ---------------------------------------------------------------------------
print("\n=== DIMENSION 6: Terminal Atom Interaction ===")

# For each MOD atom, what terminal atoms does it co-occur with in MIDDLE?
terminal_cooc = {}
for atom in sorted(UNSTABLE | STABLE_MODS):
    by_sys = {}
    for sys in ['A', 'B', 'AZC']:
        terms = Counter()
        for r in records:
            if r['system'] != sys:
                continue
            middle = r.get('middle', '') or ''
            if atom not in middle or len(middle) < 2:
                continue
            t = r['terminal']
            if t:
                terms[t] += 1
        by_sys[sys] = dict(terms)
    terminal_cooc[atom] = by_sys

    # Compute JSD between A and B terminal profiles
    j = jsd(by_sys.get('A', {}), by_sys.get('B', {}))
    terminal_cooc[atom]['jsd_a_b'] = round(j, 4)

print("\nTerminal co-occurrence in B (when atom in MIDDLE):")
for atom in sorted(terminal_cooc.keys()):
    d = terminal_cooc[atom]['B']
    tier = 'UNSTABLE' if atom in UNSTABLE else 'STABLE'
    j = terminal_cooc[atom]['jsd_a_b']
    total = sum(d.values())
    top3 = sorted(d.items(), key=lambda x: -x[1])[:3]
    top3_str = ", ".join(f"{k}:{v}" for k, v in top3)
    print(f"  {atom} ({tier}): n={total}, JSD(A,B)={j:.4f}, top3={top3_str}")

results['dimension6_terminal'] = {k: {sk: sv for sk, sv in v.items()} for k, v in terminal_cooc.items()}

# ---------------------------------------------------------------------------
# 8. DIMENSION 7: Hazard routing
# ---------------------------------------------------------------------------
print("\n=== DIMENSION 7: Hazard Routing ===")

# C1450: modifiers {c,d,f,p,s} quench hazard to 0%
# Check: do p/f/c appear in hazard-involved vs safe contexts differently across systems?

# Build per-atom hazard exposure profile in B
# Using forbidden pair concept: tokens participating in hazard transitions
# Simpler proxy: headless-y -> a-HEAD (PHASE_ORDERING) is the dominant hazard class (C1529)
# k-HEAD = immune (C1476), a-HEAD = carrier (C1477)

hazard_exposure = {}
for atom in sorted(UNSTABLE | STABLE_MODS):
    by_sys = {}
    for sys in ['A', 'B', 'AZC']:
        contexts = Counter()
        for r in records:
            if r['system'] != sys:
                continue
            middle = r.get('middle', '') or ''
            if atom not in middle:
                continue
            head = r['head']
            if head == 'k':
                contexts['k_immune'] += 1
            elif head == 'a':
                contexts['a_carrier'] += 1
            elif head == 'e':
                contexts['e_balanced'] += 1
            elif head == 'o':
                contexts['o_arrange'] += 1
            elif head == 't':
                contexts['t_flow'] += 1
            elif head is None:
                contexts['headless'] += 1
            else:
                contexts['other'] += 1
        total = sum(contexts.values())
        # Compute % in hazard-carrier (a-HEAD) vs immune (k-HEAD) contexts
        a_rate = round(contexts.get('a_carrier', 0) / total, 4) if total > 0 else 0
        k_rate = round(contexts.get('k_immune', 0) / total, 4) if total > 0 else 0
        by_sys[sys] = {
            'contexts': dict(contexts),
            'total': total,
            'a_carrier_rate': a_rate,
            'k_immune_rate': k_rate,
        }
    hazard_exposure[atom] = by_sys

print("\nHazard exposure (a-HEAD carrier rate, B system):")
print(f"{'atom':>4} {'tier':>10} {'a_rate':>8} {'k_rate':>8} {'n':>6} {'A_a%':>8} {'B_a%':>8} {'shift':>8}")
for atom in sorted(hazard_exposure.keys()):
    b = hazard_exposure[atom]['B']
    a = hazard_exposure[atom]['A']
    tier = 'UNSTABLE' if atom in UNSTABLE else 'STABLE'
    shift = round(b['a_carrier_rate'] - a['a_carrier_rate'], 4)
    print(f"{atom:>4} {tier:>10} {b['a_carrier_rate']:>8.4f} {b['k_immune_rate']:>8.4f} {b['total']:>6} {a['a_carrier_rate']:>8.4f} {b['a_carrier_rate']:>8.4f} {shift:>+8.4f}")

results['dimension7_hazard'] = {k: {sk: sv for sk, sv in v.items()} for k, v in hazard_exposure.items()}

# ---------------------------------------------------------------------------
# 9. DIMENSION 8: Bridge vs Dark Pipeline membership
# ---------------------------------------------------------------------------
print("\n=== DIMENSION 8: Bridge vs Dark Pipeline ===")

# Build bridge and dark pipeline MIDDLE sets from C1139-C1140
# Bridge = 85 MIDDLEs, Dark = 300 MIDDLEs
# We can approximate: bridge MIDDLEs are those appearing in both A and B
# Dark MIDDLEs are PP MIDDLEs appearing in B but not classified into 49 grammar classes

# Simplified: count atom frequency in B-only tokens (likely dark/HT) vs A+B shared tokens
a_middles = set()
b_middles = set()
for r in records:
    if r['system'] == 'A':
        a_middles.add(r['middle'])
    elif r['system'] == 'B':
        b_middles.add(r['middle'])

shared_middles = a_middles & b_middles
b_only_middles = b_middles - a_middles

bridge_dark_profile = {}
for atom in sorted(UNSTABLE | STABLE_MODS):
    shared_count = 0
    b_only_count = 0
    for r in records:
        if r['system'] != 'B':
            continue
        middle = r.get('middle', '') or ''
        if atom not in middle:
            continue
        if middle in shared_middles:
            shared_count += 1
        elif middle in b_only_middles:
            b_only_count += 1
    total = shared_count + b_only_count
    bridge_dark_profile[atom] = {
        'shared': shared_count,
        'b_only': b_only_count,
        'total': total,
        'shared_rate': round(shared_count / total, 4) if total > 0 else 0,
        'b_only_rate': round(b_only_count / total, 4) if total > 0 else 0,
    }

print("\nBridge/Dark pipeline affinity (B system):")
print(f"{'atom':>4} {'tier':>10} {'shared%':>8} {'b_only%':>8} {'n':>6}")
for atom in sorted(bridge_dark_profile.keys()):
    d = bridge_dark_profile[atom]
    tier = 'UNSTABLE' if atom in UNSTABLE else 'STABLE'
    print(f"{atom:>4} {tier:>10} {d['shared_rate']*100:>8.1f} {d['b_only_rate']*100:>8.1f} {d['total']:>6}")

results['dimension8_bridge_dark'] = bridge_dark_profile

# ---------------------------------------------------------------------------
# 10. COMPREHENSIVE INSTABILITY MECHANISM ANALYSIS
# ---------------------------------------------------------------------------
print("\n=== MECHANISM ANALYSIS ===")

# Q9: Is instability a frequency artifact?
# Compare: does the total count ratio (A/B) differ for unstable vs stable?
freq_ratio = {}
for atom in sorted(UNSTABLE | STABLE_MODS):
    a_n = sum(1 for r in records if r['system'] == 'A' and atom in (r.get('middle', '') or ''))
    b_n = sum(1 for r in records if r['system'] == 'B' and atom in (r.get('middle', '') or ''))
    ratio = round(a_n / b_n, 4) if b_n > 0 else float('inf')
    freq_ratio[atom] = {'A': a_n, 'B': b_n, 'ratio_A_over_B': ratio}

print("\nFrequency ratio A/B (MIDDLE atoms):")
for atom in sorted(freq_ratio.keys()):
    d = freq_ratio[atom]
    tier = 'UNSTABLE' if atom in UNSTABLE else 'STABLE'
    print(f"  {atom} ({tier}): A={d['A']}, B={d['B']}, ratio={d['ratio_A_over_B']:.4f}")

# Overall mean JSD by tier
tier_means = {}
for tier_name, atoms in [('UNSTABLE', UNSTABLE), ('STABLE_MOD', STABLE_MODS)]:
    jsds = [jsd_results[a]['mean'] for a in atoms if a in jsd_results]
    tier_means[tier_name] = round(np.mean(jsds), 4)

print(f"\nMean JSD by tier: UNSTABLE={tier_means.get('UNSTABLE', 0):.4f}, STABLE_MOD={tier_means.get('STABLE_MOD', 0):.4f}")
print(f"Ratio: {tier_means.get('UNSTABLE', 0) / tier_means.get('STABLE_MOD', 1):.2f}x")

results['mechanism'] = {
    'frequency_ratio': freq_ratio,
    'tier_mean_jsd': tier_means,
}

# ---------------------------------------------------------------------------
# 11. INDIVIDUAL ATOM DEEP PROFILES (p, f, c)
# ---------------------------------------------------------------------------
print("\n=== INDIVIDUAL ATOM PROFILES ===")

for target_atom in ['p', 'f', 'c']:
    print(f"\n--- {target_atom.upper()} ATOM ---")

    # Where does this atom appear? (MIDDLE position, initial/medial/terminal)
    position_in_middle = Counter()
    for r in records:
        if r['system'] != 'B':
            continue
        middle = r.get('middle', '') or ''
        if target_atom not in middle:
            continue
        idx = middle.index(target_atom)
        if idx == 0:
            position_in_middle['initial'] += 1
        elif idx == len(middle) - 1:
            position_in_middle['terminal'] += 1
        else:
            position_in_middle['medial'] += 1

    total_pos = sum(position_in_middle.values())
    print(f"  Position in MIDDLE (B): initial={position_in_middle.get('initial',0)} ({round(position_in_middle.get('initial',0)/total_pos*100,1) if total_pos else 0}%), " +
          f"medial={position_in_middle.get('medial',0)} ({round(position_in_middle.get('medial',0)/total_pos*100,1) if total_pos else 0}%), " +
          f"terminal={position_in_middle.get('terminal',0)} ({round(position_in_middle.get('terminal',0)/total_pos*100,1) if total_pos else 0}%)")

    # What MIDDLEs contain this atom? Top 10
    middle_with_atom = Counter()
    for r in records:
        if r['system'] != 'B':
            continue
        middle = r.get('middle', '') or ''
        if target_atom in middle:
            middle_with_atom[middle] += 1

    top10 = sorted(middle_with_atom.items(), key=lambda x: -x[1])[:10]
    print(f"  Top 10 MIDDLEs containing {target_atom} (B): {top10}")

    # Cross-system: what are the top MIDDLEs in A vs B?
    for sys in ['A', 'B']:
        mid_counts = Counter()
        for r in records:
            if r['system'] != sys:
                continue
            middle = r.get('middle', '') or ''
            if target_atom in middle:
                mid_counts[middle] += 1
        top5 = sorted(mid_counts.items(), key=lambda x: -x[1])[:5]
        print(f"  Top 5 MIDDLEs in {sys}: {top5}")

    # Category: what HEAD does this atom prefer in A vs B?
    for sys in ['A', 'B']:
        head_counts = Counter()
        for r in records:
            if r['system'] != sys:
                continue
            middle = r.get('middle', '') or ''
            if target_atom not in middle:
                continue
            h = r['head']
            head_counts[h if h else 'headless'] += 1
        total_h = sum(head_counts.values())
        print(f"  HEAD distribution in {sys} (n={total_h}): {dict(sorted(head_counts.items(), key=lambda x: -x[1]))}")

# ---------------------------------------------------------------------------
# 12. c-MODIFIER SPECIAL ANALYSIS (C1496: primary displacement context)
# ---------------------------------------------------------------------------
print("\n=== c-MODIFIER SPECIAL ANALYSIS ===")

# C1496: c-modifier at 87.1% is the primary displacement context
# C1389: c-atom main-loop modifier profile
# In headless compounds, c+k and c+t are the primary displaced-HEAD patterns

# Count ck, ct compounds and their system distribution
ck_ct_counts = Counter()
for r in records:
    middle = r.get('middle', '') or ''
    if 'ck' in middle or 'ct' in middle:
        # Determine if this is headless
        if r['is_headless']:
            if 'ck' in middle:
                ck_ct_counts[f"{r['system']}_ck_headless"] += 1
            if 'ct' in middle:
                ck_ct_counts[f"{r['system']}_ct_headless"] += 1
        else:
            if 'ck' in middle:
                ck_ct_counts[f"{r['system']}_ck_headed"] += 1
            if 'ct' in middle:
                ck_ct_counts[f"{r['system']}_ct_headed"] += 1

print("ck/ct compounds by system and headedness:")
for k in sorted(ck_ct_counts.keys()):
    print(f"  {k}: {ck_ct_counts[k]}")

# c in PREFIX vs c in MIDDLE: behavioral comparison
c_prefix_tokens = []
c_middle_tokens = []
for r in records:
    if r['system'] != 'B':
        continue
    pfx = r.get('prefix', '') or ''
    middle = r.get('middle', '') or ''
    if 'c' in pfx:
        c_prefix_tokens.append(r)
    if 'c' in middle:
        c_middle_tokens.append(r)

print(f"\nc in PREFIX (B): {len(c_prefix_tokens)} tokens")
print(f"c in MIDDLE (B): {len(c_middle_tokens)} tokens")

# Compare HEAD distributions
for label, tokens in [('c_in_PREFIX', c_prefix_tokens), ('c_in_MIDDLE', c_middle_tokens)]:
    heads = Counter(r['head'] if r['head'] else 'headless' for r in tokens)
    total = sum(heads.values())
    pcts = {k: round(v/total*100, 1) for k, v in sorted(heads.items(), key=lambda x: -x[1])}
    print(f"  {label} HEAD dist: {pcts}")

results['c_modifier_special'] = {
    'ck_ct_counts': dict(ck_ct_counts),
    'c_prefix_b_count': len(c_prefix_tokens),
    'c_middle_b_count': len(c_middle_tokens),
}

# ---------------------------------------------------------------------------
# 13. p/f REGISTER SENSITIVITY ANALYSIS
# ---------------------------------------------------------------------------
print("\n=== p/f REGISTER SENSITIVITY ===")

# C1390: p-atom marking pause profile
# C1392: f-atom marking flag profile
# Hypothesis: p and f are register-sensitive -- they shift from MARKING in A to
# different categories in B

# For p and f, check MARKING-related behavior
# Using proxy: da-prefix tokens (C1407: da is universal headless gateway)
# and section distribution (MARKING category tokens)

for target in ['p', 'f']:
    print(f"\n--- {target.upper()} register analysis ---")

    for sys in ['A', 'B']:
        # Get all tokens with target atom in MIDDLE
        tokens = [r for r in records if r['system'] == sys and target in (r.get('middle', '') or '')]
        if not tokens:
            print(f"  {sys}: 0 tokens")
            continue

        # da-prefix rate (headless gateway indicator)
        da_count = sum(1 for r in tokens if r.get('prefix') == 'da')
        da_rate = round(da_count / len(tokens) * 100, 1)

        # Headless rate
        hl_count = sum(1 for r in tokens if r['is_headless'])
        hl_rate = round(hl_count / len(tokens) * 100, 1)

        # Suffix rate
        sfx_count = sum(1 for r in tokens if r['suffix'])
        sfx_rate = round(sfx_count / len(tokens) * 100, 1)

        # Section distribution
        secs = Counter(r['section'] for r in tokens)

        print(f"  {sys} (n={len(tokens)}): da-pfx={da_rate}%, headless={hl_rate}%, suffixed={sfx_rate}%, sections={dict(sorted(secs.items(), key=lambda x: -x[1]))}")

results['pf_register'] = {}

# ---------------------------------------------------------------------------
# 14. CROSS-SYSTEM SUFFIX EXCLUSION VALIDATION
# ---------------------------------------------------------------------------
print("\n=== SUFFIX EXCLUSION CHECK (C1511) ===")

# C1511: suffix excludes {k,t,p,f,c} -- ACTION HEADs and EXECUTIVE MODs
suffix_atom_presence = defaultdict(lambda: Counter())
for r in records:
    sfx = r.get('suffix', '') or ''
    for ch in sfx:
        if ch in ALL_ATOMS:
            suffix_atom_presence[ch][r['system']] += 1

print("Atom presence in SUFFIX position:")
for atom in sorted(ALL_ATOMS):
    c = suffix_atom_presence.get(atom, Counter())
    total = sum(c.values())
    tier = 'UNSTABLE' if atom in UNSTABLE else ('STABLE_MOD' if atom in STABLE_MODS else 'OTHER')
    tag = ' ** EXCLUDED **' if atom in {'k', 't', 'p', 'f', 'c'} and total == 0 else ''
    print(f"  {atom} ({tier}): total={total} A={c.get('A',0)} B={c.get('B',0)} AZC={c.get('AZC',0)}{tag}")

results['suffix_exclusion'] = {atom: dict(suffix_atom_presence.get(atom, Counter())) for atom in ALL_ATOMS}

# ---------------------------------------------------------------------------
# 15. SYNTHESIS: Instability Mechanism Classification
# ---------------------------------------------------------------------------
print("\n=== SYNTHESIS ===")

# Compute aggregate instability metrics
synthesis = {}
for atom in sorted(UNSTABLE | STABLE_MODS):
    tier = 'UNSTABLE' if atom in UNSTABLE else 'STABLE'
    mean_jsd_val = jsd_results[atom]['mean']

    # Max dimension
    max_dim = max((d, jsd_results[atom][d]) for d in dimensions.keys() if d in jsd_results[atom] and isinstance(jsd_results[atom][d], float))

    # Headless shift
    a_hl = headless_rates[atom]['A']['headless_rate']
    b_hl = headless_rates[atom]['B']['headless_rate']
    hl_shift = round(b_hl - a_hl, 4)

    # Frequency ratio
    fr = freq_ratio[atom]

    # Bridge vs dark
    bd = bridge_dark_profile[atom]

    synthesis[atom] = {
        'tier': tier,
        'mean_jsd': mean_jsd_val,
        'max_jsd_dimension': max_dim[0],
        'max_jsd_value': round(max_dim[1], 4),
        'headless_shift_A_to_B': hl_shift,
        'frequency_ratio_A_B': fr['ratio_A_over_B'],
        'bridge_rate': bd['shared_rate'],
    }

print("\nSynthesis table:")
print(f"{'atom':>4} {'tier':>10} {'mean_JSD':>9} {'max_dim':>15} {'max_JSD':>8} {'hl_shift':>9} {'freq_A/B':>9} {'bridge%':>8}")
for atom in sorted(synthesis.keys()):
    s = synthesis[atom]
    print(f"{atom:>4} {s['tier']:>10} {s['mean_jsd']:>9.4f} {s['max_jsd_dimension']:>15} {s['max_jsd_value']:>8.4f} {s['headless_shift_A_to_B']:>+9.4f} {s['frequency_ratio_A_B']:>9.4f} {s['bridge_rate']*100:>8.1f}")

# Statistical tests
# Test 1: Are unstable atoms significantly more shifted than stable ones?
unstable_jsds = [synthesis[a]['mean_jsd'] for a in UNSTABLE]
stable_jsds = [synthesis[a]['mean_jsd'] for a in STABLE_MODS]
print(f"\nMean JSD: UNSTABLE={np.mean(unstable_jsds):.4f} vs STABLE_MOD={np.mean(stable_jsds):.4f}")
print(f"Ratio: {np.mean(unstable_jsds)/np.mean(stable_jsds):.2f}x")

# Test 2: Do unstable atoms have more extreme headless shift?
unstable_hl = [abs(synthesis[a]['headless_shift_A_to_B']) for a in UNSTABLE]
stable_hl = [abs(synthesis[a]['headless_shift_A_to_B']) for a in STABLE_MODS]
print(f"Mean |headless_shift|: UNSTABLE={np.mean(unstable_hl):.4f} vs STABLE_MOD={np.mean(stable_hl):.4f}")

results['synthesis'] = synthesis

# ---------------------------------------------------------------------------
# 16. Save results
# ---------------------------------------------------------------------------
output_path = 'C:/git/voynich/phases/EXECUTIVE_ATOM_INSTABILITY/results/executive_atom_instability.json'

# Convert any non-serializable types
def clean_for_json(obj):
    if isinstance(obj, dict):
        return {str(k): clean_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [clean_for_json(item) for item in obj]
    elif isinstance(obj, (np.integer,)):
        return int(obj)
    elif isinstance(obj, (np.floating,)):
        return float(obj)
    elif isinstance(obj, set):
        return sorted(list(obj))
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    return obj

with open(output_path, 'w') as f:
    json.dump(clean_for_json(results), f, indent=2)

print(f"\nResults saved to {output_path}")
print("\n=== PHASE 545 COMPLETE ===")
