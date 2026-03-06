"""
Phase 544: PREFIX Atom Taxonomy
Decomposes PREFIX morphology at the individual atom (character) level,
paralleling what Phases 523-540 did for MIDDLE and suffix.

Research Questions:
1. Does PREFIX decompose into atoms with consistent positional preferences?
2. What is the base inventory and do bases have functional domains?
3. Are PREFIX modifiers analogous to MIDDLE modifiers?
4. How do sister pairs compare at atom resolution?
5. What is the cross-system PREFIX distribution?
6. How does PREFIX map to hazard classes at atom level?
7. How do articulators interact with PREFIX atoms?
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

# Collect all tokens with morphological decomposition
records_a, records_b, records_azc = [], [], []

def collect(token_iter, target_list, system_tag):
    for token in token_iter:
        m = morph.extract(token.word)
        if m is None or m.prefix is None:
            continue
        rec = {
            'word': token.word,
            'folio': token.folio,
            'line': token.line,
            'prefix': m.prefix,
            'middle': m.middle,
            'suffix': m.suffix,
            'articulator': m.articulator,
            'has_articulator': m.has_articulator,
            'section': token.section,
            'system': system_tag,
            'line_initial': token.line_initial,
            'line_final': token.line_final,
            'par_initial': token.par_initial,
            'par_final': token.par_final,
        }
        target_list.append(rec)

collect(tx.currier_a(), records_a, 'A')
collect(tx.currier_b(), records_b, 'B')
collect(tx.azc(), records_azc, 'AZC')

print(f"Prefixed tokens: A={len(records_a)}, B={len(records_b)}, AZC={len(records_azc)}")

# Merge all for global analysis
all_records = records_a + records_b + records_azc

# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------
HEAD_SET = {'a', 'e', 'o', 'k', 't'}
TERM_SET = {'y', 'l', 'r', 'h', 'm', 'n'}
MIDDLE_MODS = {'p', 'i', 'c', 'f', 'd', 's'}

def get_base(pfx):
    """Get the base character of a PREFIX (final char for multi, only char for single)."""
    return pfx[-1] if pfx else None

def get_modifier(pfx):
    """Get the modifier string of a PREFIX (all chars except final for multi, None for single)."""
    if not pfx or len(pfx) <= 1:
        return None
    return pfx[:-1]

def get_middle_head(middle):
    """Get HEAD atom of MIDDLE (first char from HEAD set, or None if headless)."""
    if not middle:
        return None
    for ch in middle:
        if ch in HEAD_SET:
            return ch
    return None

def get_middle_terminal(middle):
    """Get terminal atom of MIDDLE (last char)."""
    if not middle:
        return None
    return middle[-1]

def jaccard(s1, s2):
    if not s1 and not s2:
        return 1.0
    return len(s1 & s2) / len(s1 | s2) if (s1 | s2) else 0

# ---------------------------------------------------------------------------
# 1. PREFIX Inventory
# ---------------------------------------------------------------------------
print("\n=== STEP 1: PREFIX Inventory ===")

pfx_counts_b = Counter(r['prefix'] for r in records_b)
pfx_counts_a = Counter(r['prefix'] for r in records_a)
pfx_counts_azc = Counter(r['prefix'] for r in records_azc)
pfx_counts_all = Counter(r['prefix'] for r in all_records)

print(f"Unique PREFIX types: B={len(pfx_counts_b)}, A={len(pfx_counts_a)}, AZC={len(pfx_counts_azc)}, ALL={len(pfx_counts_all)}")

# Character inventory
all_pfx_chars = set()
for pfx in pfx_counts_all:
    all_pfx_chars.update(pfx)
print(f"Unique PREFIX characters: {sorted(all_pfx_chars)} ({len(all_pfx_chars)} chars)")

# Character frequency
char_freq = Counter()
for pfx, cnt in pfx_counts_all.items():
    for ch in pfx:
        char_freq[ch] += cnt
total_char_occ = sum(char_freq.values())
print(f"\nCharacter frequency in PREFIX position:")
for ch, cnt in char_freq.most_common():
    print(f"  {ch}: {cnt} ({100*cnt/total_char_occ:.1f}%)")

# PREFIX length distribution
pfx_lengths = Counter()
for pfx, cnt in pfx_counts_all.items():
    pfx_lengths[len(pfx)] += cnt
total_pfx_tokens = sum(pfx_lengths.values())
print(f"\nPREFIX length distribution:")
for length in sorted(pfx_lengths):
    print(f"  {length}-char: {pfx_lengths[length]} tokens ({100*pfx_lengths[length]/total_pfx_tokens:.1f}%)")

# Top prefixes
print(f"\nTop 30 PREFIX types (all systems):")
for pfx, cnt in pfx_counts_all.most_common(30):
    print(f"  {pfx}: {cnt} ({100*cnt/len(all_records):.1f}%)")

prefix_inventory = {
    'unique_types': {'B': len(pfx_counts_b), 'A': len(pfx_counts_a),
                     'AZC': len(pfx_counts_azc), 'ALL': len(pfx_counts_all)},
    'character_inventory': sorted(all_pfx_chars),
    'character_count': len(all_pfx_chars),
    'character_frequency': {ch: cnt for ch, cnt in char_freq.most_common()},
    'length_distribution': {str(k): v for k, v in sorted(pfx_lengths.items())},
    'top_30': [(pfx, cnt) for pfx, cnt in pfx_counts_all.most_common(30)],
}

# ---------------------------------------------------------------------------
# 2. Positional Analysis
# ---------------------------------------------------------------------------
print("\n=== STEP 2: Positional Analysis ===")

char_abs_pos_counts = defaultdict(lambda: Counter())
char_rel_pos_counts = defaultdict(lambda: Counter())

for pfx, cnt in pfx_counts_all.items():
    if len(pfx) == 1:
        char_abs_pos_counts[pfx[0]][0] += cnt
        char_rel_pos_counts[pfx[0]]['singleton'] += cnt
    else:
        for i, ch in enumerate(pfx):
            char_abs_pos_counts[ch][i] += cnt
            if i == 0:
                char_rel_pos_counts[ch]['initial'] += cnt
            elif i == len(pfx) - 1:
                char_rel_pos_counts[ch]['final'] += cnt
            else:
                char_rel_pos_counts[ch]['medial'] += cnt

print("\nCharacter positional classification:")
positional_classification = {}
for ch in sorted(all_pfx_chars):
    total = sum(char_abs_pos_counts[ch].values())
    pos0 = char_abs_pos_counts[ch].get(0, 0)
    pos0_pct = 100 * pos0 / total if total > 0 else 0

    rel = char_rel_pos_counts[ch]
    init = rel.get('initial', 0)
    final = rel.get('final', 0)
    medial = rel.get('medial', 0)
    single = rel.get('singleton', 0)

    # Determine role considering singleton vs multi-char usage
    # For multi-char prefixes: initial = modifier, final = base
    # Singletons function as base (they ARE the base character)
    multi_total = init + final + medial
    if total < 10:
        role = 'RARE'
    elif multi_total == 0:
        role = 'SINGLETON_ONLY'  # only appears as single-char prefix
    elif single == 0 and init > 0 and final == 0:
        role = 'MODIFIER'  # only appears as modifier in multi-char
    elif single == 0 and final > 0 and init == 0:
        role = 'BASE'  # only appears as base in multi-char
    elif (init + single) / total >= 0.90:
        role = 'MODIFIER'  # predominantly modifier or singleton
    elif (final + single) / total >= 0.90:
        role = 'BASE'  # predominantly base or singleton
    else:
        role = 'DUAL'

    positional_classification[ch] = {
        'role': role, 'total': total,
        'pos0_pct': round(pos0_pct, 1),
        'initial_pct': round(100 * init / total, 1) if total else 0,
        'final_pct': round(100 * final / total, 1) if total else 0,
        'singleton_pct': round(100 * single / total, 1) if total else 0,
        'medial_pct': round(100 * medial / total, 1) if total else 0,
    }
    print(f"  {ch}: {role:15s} total={total:6d}  pos0={pos0_pct:5.1f}%  "
          f"init={100*init/total if total else 0:5.1f}%  "
          f"final={100*final/total if total else 0:5.1f}%  "
          f"single={100*single/total if total else 0:5.1f}%")

# ---------------------------------------------------------------------------
# 3. Base → MIDDLE HEAD Selection
# ---------------------------------------------------------------------------
print("\n=== STEP 3: Base -> MIDDLE HEAD Selection ===")

base_head_counts = defaultdict(lambda: Counter())
base_headless_counts = Counter()

for r in records_b:
    base = get_base(r['prefix'])
    head = get_middle_head(r['middle'])
    if base:
        if head:
            base_head_counts[base][head] += 1
        else:
            base_headless_counts[base] += 1

all_heads = sorted(HEAD_SET)
print("\nBase -> MIDDLE HEAD selection (B tokens):")
for base in sorted(base_head_counts.keys()):
    total = sum(base_head_counts[base].values()) + base_headless_counts.get(base, 0)
    if total < 10:
        continue
    headless_pct = 100 * base_headless_counts.get(base, 0) / total
    parts = []
    for h in all_heads:
        cnt = base_head_counts[base].get(h, 0)
        pct = 100 * cnt / total
        if pct > 0.5:
            parts.append(f"{h}={pct:.1f}%")
    parts.append(f"HL={headless_pct:.1f}%")
    print(f"  base={base}: N={total:5d}  {', '.join(parts)}")

# Chi-squared test
bases_for_test = [b for b in base_head_counts if sum(base_head_counts[b].values()) + base_headless_counts.get(b, 0) >= 30]
chi2_bh, p_bh, V_bh = None, None, None
if len(bases_for_test) >= 2:
    cols = all_heads + ['headless']
    matrix = []
    for b in bases_for_test:
        row = [base_head_counts[b].get(h, 0) for h in all_heads]
        row.append(base_headless_counts.get(b, 0))
        matrix.append(row)
    matrix = np.array(matrix)
    col_sums = matrix.sum(axis=0)
    mask = col_sums > 0
    if mask.sum() >= 2:
        chi2_bh, p_bh, dof_bh, _ = chi2_contingency(matrix[:, mask])
        n_bh = matrix[:, mask].sum()
        V_bh = np.sqrt(chi2_bh / (n_bh * (min(matrix[:, mask].shape) - 1))) if n_bh > 0 else 0
        print(f"\nBase x HEAD chi2={chi2_bh:.1f}, p={p_bh:.2e}, V={V_bh:.3f} (dof={dof_bh})")

base_head_results = {
    'base_head_profiles': {},
    'chi2': round(chi2_bh, 1) if chi2_bh else None,
    'p_value': float(p_bh) if p_bh is not None else None,
    'cramers_v': round(V_bh, 3) if V_bh is not None else None,
}
for base in sorted(base_head_counts.keys()):
    total = sum(base_head_counts[base].values()) + base_headless_counts.get(base, 0)
    if total < 10:
        continue
    profile = {}
    for h in all_heads:
        profile[h] = round(100 * base_head_counts[base].get(h, 0) / total, 1)
    profile['headless'] = round(100 * base_headless_counts.get(base, 0) / total, 1)
    profile['total'] = total
    base_head_results['base_head_profiles'][base] = profile

# ---------------------------------------------------------------------------
# 4. Modifier Analysis
# ---------------------------------------------------------------------------
print("\n=== STEP 4: Modifier Analysis ===")

pfx_modifier_counts = Counter()
mod_base_pairs = Counter()

for pfx, cnt in pfx_counts_all.items():
    if len(pfx) > 1:
        mod = pfx[:-1]
        base = pfx[-1]
        for ch in mod:
            pfx_modifier_counts[ch] += cnt
        mod_base_pairs[(mod, base)] += cnt

print("PREFIX modifier character frequency:")
for ch, cnt in pfx_modifier_counts.most_common():
    is_mid_mod = ch in MIDDLE_MODS
    print(f"  {ch}: {cnt:6d}  {'(also MIDDLE MOD)' if is_mid_mod else '(PREFIX-specific)'}")

pfx_mod_chars = set(pfx_modifier_counts.keys())
overlap = pfx_mod_chars & MIDDLE_MODS
pfx_only = pfx_mod_chars - MIDDLE_MODS
mid_only = MIDDLE_MODS - pfx_mod_chars
print(f"\nModifier overlap: shared={sorted(overlap)}, PREFIX-only={sorted(pfx_only)}, MIDDLE-only={sorted(mid_only)}")

# Modifier → base co-occurrence
print("\nModifier -> Base co-occurrence:")
mod_base_matrix = defaultdict(lambda: Counter())
for pfx, cnt in pfx_counts_all.items():
    if len(pfx) > 1:
        mod_ch = pfx[0]
        base_ch = pfx[-1]
        mod_base_matrix[mod_ch][base_ch] += cnt

for mod_ch in sorted(pfx_modifier_counts.keys(), key=lambda x: -pfx_modifier_counts[x]):
    total = sum(mod_base_matrix[mod_ch].values())
    bases_str = ', '.join(f"{b}={100*mod_base_matrix[mod_ch][b]/total:.0f}%"
                          for b, _ in mod_base_matrix[mod_ch].most_common(5) if mod_base_matrix[mod_ch][b] > 0)
    print(f"  {mod_ch}: N={total:5d}  bases: {bases_str}")

modifier_results = {
    'modifier_frequency': {ch: cnt for ch, cnt in pfx_modifier_counts.most_common()},
    'overlap_with_middle_mods': sorted(overlap),
    'prefix_only_mods': sorted(pfx_only),
    'middle_only_mods': sorted(mid_only),
}

# ---------------------------------------------------------------------------
# 5. Sister Pair Atom-Level Comparison
# ---------------------------------------------------------------------------
print("\n=== STEP 5: Sister Pair Atom-Level Comparison ===")

sister_pairs = [('ch', 'sh'), ('ok', 'ot'), ('da', 'sa')]
sister_results = {}

for s1, s2 in sister_pairs:
    print(f"\n--- {s1} vs {s2} ---")

    # Decomposition
    s1_mod, s1_base = (s1[:-1], s1[-1]) if len(s1) > 1 else (None, s1)
    s2_mod, s2_base = (s2[:-1], s2[-1]) if len(s2) > 1 else (None, s2)

    shared_base = s1_base == s2_base
    shared_mod = s1_mod == s2_mod if (s1_mod and s2_mod) else False

    kind = 'SAME_BASE' if shared_base else ('SAME_MOD' if shared_mod else 'NEITHER')
    print(f"  {s1}: mod={s1_mod}, base={s1_base}")
    print(f"  {s2}: mod={s2_mod}, base={s2_base}")
    print(f"  Structure: {kind}")

    tokens_s1 = [r for r in records_b if r['prefix'] == s1]
    tokens_s2 = [r for r in records_b if r['prefix'] == s2]

    # HEAD profiles
    heads_s1 = Counter(get_middle_head(r['middle']) or 'HL' for r in tokens_s1)
    heads_s2 = Counter(get_middle_head(r['middle']) or 'HL' for r in tokens_s2)

    n1, n2 = len(tokens_s1), len(tokens_s2)
    print(f"  {s1} HEAD (N={n1}): {', '.join(f'{h}={100*c/n1:.1f}%' for h, c in heads_s1.most_common(6))}")
    print(f"  {s2} HEAD (N={n2}): {', '.join(f'{h}={100*c/n2:.1f}%' for h, c in heads_s2.most_common(6))}")

    # JSD between HEAD profiles
    all_h_keys = sorted(set(heads_s1.keys()) | set(heads_s2.keys()))
    p1 = np.array([heads_s1.get(h, 0) / n1 for h in all_h_keys]) + 1e-10
    p2 = np.array([heads_s2.get(h, 0) / n2 for h in all_h_keys]) + 1e-10
    p1 /= p1.sum(); p2 /= p2.sum()
    jsd = jensenshannon(p1, p2) ** 2
    print(f"  HEAD JSD = {jsd:.4f}")

    # Suffix rates
    suf1 = 100 * sum(1 for r in tokens_s1 if r['suffix']) / n1 if n1 else 0
    suf2 = 100 * sum(1 for r in tokens_s2 if r['suffix']) / n2 if n2 else 0
    print(f"  Suffix rate: {s1}={suf1:.1f}%, {s2}={suf2:.1f}%")

    # Headless rates
    hl1 = 100 * sum(1 for r in tokens_s1 if get_middle_head(r['middle']) is None) / n1 if n1 else 0
    hl2 = 100 * sum(1 for r in tokens_s2 if get_middle_head(r['middle']) is None) / n2 if n2 else 0
    print(f"  Headless rate: {s1}={hl1:.1f}%, {s2}={hl2:.1f}%")

    # Articulator rates
    art1 = 100 * sum(1 for r in tokens_s1 if r['has_articulator']) / n1 if n1 else 0
    art2 = 100 * sum(1 for r in tokens_s2 if r['has_articulator']) / n2 if n2 else 0
    print(f"  Articulator rate: {s1}={art1:.1f}%, {s2}={art2:.1f}%")

    # Terminal profiles
    terms_s1 = Counter(get_middle_terminal(r['middle']) for r in tokens_s1 if r['middle'])
    terms_s2 = Counter(get_middle_terminal(r['middle']) for r in tokens_s2 if r['middle'])

    sister_results[f"{s1}_{s2}"] = {
        's1_mod': s1_mod, 's1_base': s1_base,
        's2_mod': s2_mod, 's2_base': s2_base,
        'structure': kind,
        'head_jsd': round(jsd, 4),
        's1_n': n1, 's2_n': n2,
        'suffix_rate': {s1: round(suf1, 1), s2: round(suf2, 1)},
        'headless_rate': {s1: round(hl1, 1), s2: round(hl2, 1)},
        'articulator_rate': {s1: round(art1, 1), s2: round(art2, 1)},
    }

# ---------------------------------------------------------------------------
# 6. PREFIX → Category Routing at Atom Level
# ---------------------------------------------------------------------------
print("\n=== STEP 6: PREFIX Base -> Category Routing ===")

HEAD_CATEGORY = {
    'k': 'THERMAL', 'e': 'STABILITY', 't': 'FLOW',
    'a': 'CONTAINMENT', 'o': 'ARRANGEMENT',
}

print("\nBase -> category via HEAD (B tokens):")
base_category_profiles = {}
for base in sorted(base_head_counts.keys()):
    total = sum(base_head_counts[base].values()) + base_headless_counts.get(base, 0)
    if total < 20:
        continue
    cat_counts = Counter()
    for h, cnt in base_head_counts[base].items():
        cat = HEAD_CATEGORY.get(h, 'OTHER')
        cat_counts[cat] += cnt
    cat_counts['HEADLESS'] = base_headless_counts.get(base, 0)
    top = cat_counts.most_common(4)
    top_str = ', '.join(f"{c}={100*n/total:.1f}%" for c, n in top)
    print(f"  base={base}: N={total:5d}  {top_str}")
    base_category_profiles[base] = {c: round(100*n/total, 1) for c, n in cat_counts.items()}
    base_category_profiles[base]['total'] = total

# Modifier effect on HEAD (within same base)
print("\nModifier effect on HEAD selection (within same base, B tokens):")
modifier_effects = {}
for base in ['h', 'o', 'a', 'k', 'e']:
    mods_for_base = defaultdict(lambda: Counter())

    # Bare
    bare_tokens = [r for r in records_b if r['prefix'] == base]
    bare_heads = Counter(get_middle_head(r['middle']) or 'HL' for r in bare_tokens)

    # Modified
    for pfx in pfx_counts_b:
        if len(pfx) > 1 and pfx[-1] == base:
            mod = pfx[:-1]
            toks = [r for r in records_b if r['prefix'] == pfx]
            for r in toks:
                head = get_middle_head(r['middle']) or 'HL'
                mods_for_base[mod][head] += 1

    if bare_heads or mods_for_base:
        print(f"\n  Base '{base}':")
        base_effects = {}
        if bare_heads:
            total = len(bare_tokens)
            head_str = ', '.join(f"{h}={100*c/total:.1f}%" for h, c in bare_heads.most_common(5))
            print(f"    bare ({base}): N={total}  {head_str}")
            base_effects['bare'] = {h: round(100*c/total, 1) for h, c in bare_heads.items()}
            base_effects['bare']['N'] = total

        for mod in sorted(mods_for_base.keys()):
            total = sum(mods_for_base[mod].values())
            if total < 10:
                continue
            head_str = ', '.join(f"{h}={100*c/total:.1f}%" for h, c in mods_for_base[mod].most_common(5))
            print(f"    mod={mod} ({mod}{base}): N={total}  {head_str}")
            base_effects[mod] = {h: round(100*c/total, 1) for h, c in mods_for_base[mod].items()}
            base_effects[mod]['N'] = total

            # JSD vs bare
            if bare_heads and total >= 10:
                all_h_keys = sorted(set(bare_heads.keys()) | set(mods_for_base[mod].keys()))
                p1 = np.array([bare_heads.get(h, 0) / len(bare_tokens) for h in all_h_keys]) + 1e-10
                p2 = np.array([mods_for_base[mod].get(h, 0) / total for h in all_h_keys]) + 1e-10
                p1 /= p1.sum(); p2 /= p2.sum()
                jsd = jensenshannon(p1, p2) ** 2
                print(f"      JSD(bare, {mod}{base}) = {jsd:.4f}")
                base_effects[mod]['jsd_vs_bare'] = round(jsd, 4)

        modifier_effects[base] = base_effects

# ---------------------------------------------------------------------------
# 7. Cross-System PREFIX Distribution
# ---------------------------------------------------------------------------
print("\n=== STEP 7: Cross-System PREFIX Distribution ===")

base_by_system = {}
for sys_name, records in [('A', records_a), ('B', records_b), ('AZC', records_azc)]:
    base_counts = Counter()
    for r in records:
        base = get_base(r['prefix'])
        if base:
            base_counts[base] += 1
    base_by_system[sys_name] = base_counts

all_base_chars = sorted(set().union(*[set(bc.keys()) for bc in base_by_system.values()]))
print("Base character distribution by system:")
for base_ch in all_base_chars:
    parts = []
    for sys_name in ['A', 'B', 'AZC']:
        total = sum(base_by_system[sys_name].values())
        cnt = base_by_system[sys_name].get(base_ch, 0)
        pct = 100 * cnt / total if total > 0 else 0
        parts.append(f"{sys_name}={pct:.1f}%")
    print(f"  {base_ch}: {', '.join(parts)}")

# Cross-system JSD for base profiles
systems = ['A', 'B', 'AZC']
jsd_cross = {}
for i, s1 in enumerate(systems):
    for s2 in systems[i+1:]:
        total1 = sum(base_by_system[s1].values()) or 1
        total2 = sum(base_by_system[s2].values()) or 1
        p1 = np.array([base_by_system[s1].get(ch, 0) / total1 for ch in all_base_chars]) + 1e-10
        p2 = np.array([base_by_system[s2].get(ch, 0) / total2 for ch in all_base_chars]) + 1e-10
        p1 /= p1.sum(); p2 /= p2.sum()
        jsd = jensenshannon(p1, p2) ** 2
        jsd_cross[f"{s1}_{s2}"] = round(jsd, 4)
        print(f"  Base JSD({s1}, {s2}) = {jsd:.4f}")

# Modifier by system
mod_by_system = {}
for sys_name, records in [('A', records_a), ('B', records_b), ('AZC', records_azc)]:
    mod_counts = Counter()
    for r in records:
        mod = get_modifier(r['prefix'])
        if mod:
            for ch in mod:
                mod_counts[ch] += 1
    mod_by_system[sys_name] = mod_counts

all_mod_chars = sorted(set().union(*[set(mc.keys()) for mc in mod_by_system.values()]))
print("\nModifier character distribution by system:")
for mod_ch in all_mod_chars:
    parts = []
    for sys_name in ['A', 'B', 'AZC']:
        total = sum(mod_by_system[sys_name].values()) or 1
        cnt = mod_by_system[sys_name].get(mod_ch, 0)
        pct = 100 * cnt / total
        parts.append(f"{sys_name}={pct:.1f}%")
    print(f"  {mod_ch}: {', '.join(parts)}")

jsd_mod_cross = {}
for i, s1 in enumerate(systems):
    for s2 in systems[i+1:]:
        total1 = sum(mod_by_system[s1].values()) or 1
        total2 = sum(mod_by_system[s2].values()) or 1
        p1 = np.array([mod_by_system[s1].get(ch, 0) / total1 for ch in all_mod_chars]) + 1e-10
        p2 = np.array([mod_by_system[s2].get(ch, 0) / total2 for ch in all_mod_chars]) + 1e-10
        p1 /= p1.sum(); p2 /= p2.sum()
        jsd = jensenshannon(p1, p2) ** 2
        jsd_mod_cross[f"{s1}_{s2}"] = round(jsd, 4)
        print(f"  Mod JSD({s1}, {s2}) = {jsd:.4f}")

# ---------------------------------------------------------------------------
# 8. PREFIX -> Headless Rate
# ---------------------------------------------------------------------------
print("\n=== STEP 8: PREFIX -> Headless Rate ===")

pfx_headless = defaultdict(lambda: [0, 0])
for r in records_b:
    head = get_middle_head(r['middle'])
    pfx_headless[r['prefix']][1] += 1
    if head is None:
        pfx_headless[r['prefix']][0] += 1

print("PREFIX headless rate (B tokens, N>=30):")
headless_data = []
for pfx in sorted(pfx_headless.keys(), key=lambda x: -pfx_headless[x][1]):
    hl, total = pfx_headless[pfx]
    if total >= 30:
        rate = 100 * hl / total
        headless_data.append((pfx, round(rate, 1), hl, total))
        print(f"  {pfx}: {rate:.1f}% headless ({hl}/{total})")

# ---------------------------------------------------------------------------
# 9. PREFIX Base x MIDDLE Terminal Interaction
# ---------------------------------------------------------------------------
print("\n=== STEP 9: Base x Terminal Interaction ===")

base_term_counts = defaultdict(lambda: Counter())
for r in records_b:
    base = get_base(r['prefix'])
    mid = r['middle']
    if base and mid:
        term = mid[-1]
        base_term_counts[base][term] += 1

all_terms = sorted(TERM_SET)
print("Base x MIDDLE Terminal (B tokens, N>=30):")
for base in sorted(base_term_counts.keys()):
    total = sum(base_term_counts[base].values())
    if total < 30:
        continue
    parts = ', '.join(f"{t}={100*base_term_counts[base].get(t,0)/total:.1f}%" for t in all_terms if base_term_counts[base].get(t,0) > 0)
    print(f"  base={base}: N={total:5d}  {parts}")

# Chi-squared
bases_bt = [b for b in base_term_counts if sum(base_term_counts[b].values()) >= 30]
chi2_bt, p_bt, V_bt = None, None, None
if len(bases_bt) >= 2:
    all_term_chars = sorted(set(t for b in bases_bt for t in base_term_counts[b].keys()))
    matrix_bt = []
    for b in bases_bt:
        row = [base_term_counts[b].get(t, 0) for t in all_term_chars]
        matrix_bt.append(row)
    matrix_bt = np.array(matrix_bt)
    col_sums = matrix_bt.sum(axis=0)
    mask = col_sums > 0
    if mask.sum() >= 2:
        chi2_bt, p_bt, dof_bt, _ = chi2_contingency(matrix_bt[:, mask])
        n_bt = matrix_bt[:, mask].sum()
        V_bt = np.sqrt(chi2_bt / (n_bt * (min(matrix_bt[:, mask].shape) - 1))) if n_bt > 0 else 0
        print(f"\nBase x Terminal chi2={chi2_bt:.1f}, p={p_bt:.2e}, V={V_bt:.3f}")

# ---------------------------------------------------------------------------
# 10. Shared Substrate Test
# ---------------------------------------------------------------------------
print("\n=== STEP 10: Shared Substrate Test ===")

pfx_chars_a = set()
pfx_chars_b = set()
pfx_chars_azc = set()
for r in records_a:
    pfx_chars_a.update(r['prefix'])
for r in records_b:
    pfx_chars_b.update(r['prefix'])
for r in records_azc:
    pfx_chars_azc.update(r['prefix'])

j_ab = jaccard(pfx_chars_a, pfx_chars_b)
j_a_azc = jaccard(pfx_chars_a, pfx_chars_azc)
j_b_azc = jaccard(pfx_chars_b, pfx_chars_azc)

print(f"PREFIX character inventory:")
print(f"  A: {sorted(pfx_chars_a)} ({len(pfx_chars_a)} chars)")
print(f"  B: {sorted(pfx_chars_b)} ({len(pfx_chars_b)} chars)")
print(f"  AZC: {sorted(pfx_chars_azc)} ({len(pfx_chars_azc)} chars)")
print(f"\nJaccard:")
print(f"  J(A, B) = {j_ab:.3f}")
print(f"  J(A, AZC) = {j_a_azc:.3f}")
print(f"  J(B, AZC) = {j_b_azc:.3f}")

shared_all = pfx_chars_a & pfx_chars_b & pfx_chars_azc
print(f"\nShared across all 3: {sorted(shared_all)} ({len(shared_all)})")
a_only = pfx_chars_a - pfx_chars_b - pfx_chars_azc
b_only = pfx_chars_b - pfx_chars_a - pfx_chars_azc
azc_only = pfx_chars_azc - pfx_chars_a - pfx_chars_b
print(f"  A-only: {sorted(a_only)}")
print(f"  B-only: {sorted(b_only)}")
print(f"  AZC-only: {sorted(azc_only)}")

# ---------------------------------------------------------------------------
# 11. PREFIX Atom x Line Position
# ---------------------------------------------------------------------------
print("\n=== STEP 11: PREFIX Atom x Line Position ===")

# Base character vs line position
base_pos_counts = defaultdict(lambda: Counter())
for r in records_b:
    base = get_base(r['prefix'])
    if not base:
        continue
    if r['line_initial']:
        base_pos_counts[base]['initial'] += 1
    elif r['line_final']:
        base_pos_counts[base]['final'] += 1
    else:
        base_pos_counts[base]['medial'] += 1

print("Base x Line Position (B tokens):")
for base in sorted(base_pos_counts.keys()):
    total = sum(base_pos_counts[base].values())
    if total < 30:
        continue
    init = base_pos_counts[base].get('initial', 0)
    final = base_pos_counts[base].get('final', 0)
    medial = base_pos_counts[base].get('medial', 0)
    print(f"  base={base}: N={total:5d}  init={100*init/total:.1f}%  med={100*medial/total:.1f}%  final={100*final/total:.1f}%")

# ---------------------------------------------------------------------------
# 12. Articulator x PREFIX Interaction
# ---------------------------------------------------------------------------
print("\n=== STEP 12: Articulator x PREFIX Interaction ===")

art_base_counts = defaultdict(lambda: Counter())
for r in records_b:
    if r['has_articulator'] and r['articulator']:
        base = get_base(r['prefix'])
        if base:
            art_base_counts[r['articulator']][base] += 1

print("Articulator -> PREFIX base (B tokens):")
for art in sorted(art_base_counts.keys()):
    total = sum(art_base_counts[art].values())
    parts = ', '.join(f"{b}={100*c/total:.1f}%" for b, c in art_base_counts[art].most_common(5))
    print(f"  art={art}: N={total:5d}  bases: {parts}")

# Articulator rate by PREFIX (N>=50)
print("\nArticulator rate by PREFIX (B, N>=50, rate>0):")
pfx_art_rates = {}
for pfx in sorted(pfx_counts_b.keys(), key=lambda x: -pfx_counts_b[x]):
    tokens = [r for r in records_b if r['prefix'] == pfx]
    if len(tokens) >= 50:
        art_count = sum(1 for r in tokens if r['has_articulator'])
        rate = 100 * art_count / len(tokens)
        pfx_art_rates[pfx] = round(rate, 1)
        if rate > 0:
            print(f"  {pfx}: {rate:.1f}% ({art_count}/{len(tokens)})")

# ---------------------------------------------------------------------------
# 13. PREFIX Atom vs MIDDLE Atom Inventory Comparison
# ---------------------------------------------------------------------------
print("\n=== STEP 13: PREFIX vs MIDDLE Atom Inventory ===")

# Get MIDDLE atom inventory
mid_chars = set()
for r in records_b:
    if r['middle']:
        mid_chars.update(r['middle'])

# Get suffix atom inventory
suf_chars = set()
for r in records_b:
    if r['suffix']:
        suf_chars.update(r['suffix'])

print(f"Atom inventories:")
print(f"  PREFIX: {sorted(all_pfx_chars)} ({len(all_pfx_chars)} chars)")
print(f"  MIDDLE: {sorted(mid_chars)} ({len(mid_chars)} chars)")
print(f"  SUFFIX: {sorted(suf_chars)} ({len(suf_chars)} chars)")

pfx_mid_j = jaccard(all_pfx_chars, mid_chars)
pfx_suf_j = jaccard(all_pfx_chars, suf_chars)
mid_suf_j = jaccard(mid_chars, suf_chars)

print(f"\nCross-slot Jaccard:")
print(f"  J(PREFIX, MIDDLE) = {pfx_mid_j:.3f}")
print(f"  J(PREFIX, SUFFIX) = {pfx_suf_j:.3f}")
print(f"  J(MIDDLE, SUFFIX) = {mid_suf_j:.3f}")

pfx_exclusive = all_pfx_chars - mid_chars - suf_chars
mid_exclusive = mid_chars - all_pfx_chars - suf_chars
suf_exclusive = suf_chars - all_pfx_chars - mid_chars
all_shared = all_pfx_chars & mid_chars & suf_chars

print(f"\n  Shared by all 3 slots: {sorted(all_shared)} ({len(all_shared)})")
print(f"  PREFIX-exclusive: {sorted(pfx_exclusive)}")
print(f"  MIDDLE-exclusive: {sorted(mid_exclusive)}")
print(f"  SUFFIX-exclusive: {sorted(suf_exclusive)}")

# ---------------------------------------------------------------------------
# COMPILE RESULTS
# ---------------------------------------------------------------------------
print("\n=== COMPILING RESULTS ===")

results = {
    'phase': 'Phase 544: PREFIX Atom Taxonomy',
    'date': '2026-03-06',
    'token_counts': {'A': len(records_a), 'B': len(records_b), 'AZC': len(records_azc)},
    'prefix_inventory': prefix_inventory,
    'positional_classification': positional_classification,
    'base_head_selection': base_head_results,
    'modifier_analysis': modifier_results,
    'sister_pair_decomposition': sister_results,
    'cross_system': {
        'base_jsd': jsd_cross,
        'modifier_jsd': jsd_mod_cross,
        'character_jaccard': {'A_B': round(j_ab, 3), 'A_AZC': round(j_a_azc, 3), 'B_AZC': round(j_b_azc, 3)},
        'shared_all': sorted(shared_all),
    },
    'base_category_profiles': base_category_profiles,
    'modifier_effects': {k: {mk: {kk: vv for kk, vv in mv.items()} for mk, mv in v.items()} for k, v in modifier_effects.items()},
    'base_terminal': {
        'chi2': round(chi2_bt, 1) if chi2_bt else None,
        'p_value': float(p_bt) if p_bt is not None else None,
        'cramers_v': round(V_bt, 3) if V_bt is not None else None,
    },
    'headless_by_prefix': headless_data,
    'pfx_art_rates': pfx_art_rates,
    'cross_slot_inventory': {
        'prefix_chars': sorted(all_pfx_chars),
        'middle_chars': sorted(mid_chars),
        'suffix_chars': sorted(suf_chars),
        'jaccard_pfx_mid': round(pfx_mid_j, 3),
        'jaccard_pfx_suf': round(pfx_suf_j, 3),
        'jaccard_mid_suf': round(mid_suf_j, 3),
        'all_shared': sorted(all_shared),
        'pfx_exclusive': sorted(pfx_exclusive),
    },
}

out_path = 'C:/git/voynich/phases/PREFIX_ATOM_TAXONOMY/results/prefix_atom_taxonomy.json'
with open(out_path, 'w') as f:
    json.dump(results, f, indent=2, default=str)
print(f"Results saved to {out_path}")

print("\n=== PHASE 544 COMPLETE ===")
