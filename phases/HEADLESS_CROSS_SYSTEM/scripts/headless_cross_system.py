"""
Phase 542: Headless Compound Cross-System Distribution
=======================================================

Research question: Do headless compounds (MIDDLEs with no HEAD atom at
position 0) distribute differently across Currier A, Currier B, and AZC?

Context:
- C1488-C1493: Headless compounds are 20.5% of B, coherent sixth domain
- C1494-C1498: "Displaced HEAD" atoms function as TERMINALS, not HEADs
- C1499-C1509: Cross-system atom ontology shared substrate
- C1516-C1519: AZC zone HEAD differentiation (Phase 541)
- C1491: da-PREFIX near-exclusivity (2,284x enrichment in B headless)

Tests:
  T1  Headless rate by system (A, B, AZC)
  T2  Pseudo-HEAD first-atom differentiation per system
  T3  da-PREFIX exclusivity cross-system
  T4  Suffix rate bifurcation cross-system
  T5  AZC zone headless distribution
  T6  Bridge vs dark pipeline headless enrichment
  T7  Terminal profile comparison (headed vs headless per system)
  T8  Category profile comparison (headless per system)
  T9  Headless compound length by system
  T10 Cross-system headless MIDDLE overlap
"""

import json
import math
import os
import sys
import io
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from scipy import stats

# Force UTF-8 output on Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.voynich import Transcript, Morphology, CategoryClassifier, decompose_middle_hmt

# -- Output directory --
RESULTS_DIR = Path(__file__).resolve().parents[1] / 'results'
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
PROJECT_ROOT = Path(__file__).resolve().parents[3]

# -- Constants --
HEAD_ATOMS = {'a', 'e', 'o', 'k', 't'}
MOD_ATOMS = {'c', 'd', 'f', 'i', 'p', 's'}
TERM_ATOMS = {'h', 'l', 'm', 'n', 'r', 'y'}
MAJOR_ZONES = {'R', 'C', 'S', 'P', 'L'}

# Load bridge and dark pipeline MIDDLEs
bridge_path = PROJECT_ROOT / 'phases' / 'BRIDGE_MIDDLE_SELECTION_MECHANISM' / 'results' / 'bridge_selection.json'
with open(bridge_path) as f:
    bridge_data = json.load(f)
BRIDGE_MIDDLES = set(bridge_data['t5_structural_profile']['bridge_middles'])

dark_path = PROJECT_ROOT / 'data' / 'dark_pipeline_middles.json'
with open(dark_path) as f:
    dark_data = json.load(f)
DARK_MIDDLES = set(dark_data['middles'])


def classify_zone(placement):
    """Classify AZC placement into major zone."""
    if not placement:
        return 'UNKNOWN'
    first = placement[0]
    if first in MAJOR_ZONES:
        return first
    return 'OTHER'


def classify_pipeline(middle):
    """Classify MIDDLE as bridge, dark, or exclusive."""
    if middle in BRIDGE_MIDDLES:
        return 'bridge'
    elif middle in DARK_MIDDLES:
        return 'dark'
    else:
        return 'exclusive'


def cramers_v(contingency_table):
    """Compute Cramer's V from a contingency table."""
    chi2 = stats.chi2_contingency(contingency_table)[0]
    n = contingency_table.sum()
    r, k = contingency_table.shape
    return math.sqrt(chi2 / (n * min(r - 1, k - 1))) if n > 0 else 0


def jsd(p, q):
    """Jensen-Shannon Divergence between two distributions."""
    p = np.array(p, dtype=float)
    q = np.array(q, dtype=float)
    p = p / p.sum() if p.sum() > 0 else p
    q = q / q.sum() if q.sum() > 0 else q
    m = 0.5 * (p + q)
    # KL with zero protection
    def kl(a, b):
        mask = (a > 0) & (b > 0)
        return np.sum(a[mask] * np.log2(a[mask] / b[mask]))
    return 0.5 * kl(p, m) + 0.5 * kl(q, m)


# =====================================================================
# DATA LOADING
# =====================================================================
print("=" * 70)
print("Phase 542: Headless Compound Cross-System Distribution")
print("=" * 70)

tx = Transcript()
morph = Morphology()
cc = CategoryClassifier()

# Collect tokens with morphological decomposition by system
systems = {'A': [], 'B': [], 'AZC': []}

print("\nLoading Currier A tokens...")
for t in tx.currier_a():
    if not t.word or not t.word.strip():
        continue
    m = morph.extract(t.word)
    mid = m.middle
    if not mid:
        continue
    head, mods, term, frame = decompose_middle_hmt(mid)
    headless = head is None
    first_atom = mid[0] if mid else None
    systems['A'].append({
        'word': t.word,
        'folio': t.folio,
        'middle': mid,
        'prefix': m.prefix,
        'suffix': m.suffix,
        'articulator': m.articulator,
        'head': head,
        'mods': mods,
        'term': term,
        'frame': frame,
        'headless': headless,
        'first_atom': first_atom,
        'pipeline': classify_pipeline(mid),
        'placement': getattr(t, 'placement', None),
        'category': cc.classify(mid),
        'mid_len': len(mid),
    })

print(f"  A: {len(systems['A'])} tokens")

print("Loading Currier B tokens...")
for t in tx.currier_b():
    if not t.word or not t.word.strip():
        continue
    m = morph.extract(t.word)
    mid = m.middle
    if not mid:
        continue
    head, mods, term, frame = decompose_middle_hmt(mid)
    headless = head is None
    first_atom = mid[0] if mid else None
    systems['B'].append({
        'word': t.word,
        'folio': t.folio,
        'middle': mid,
        'prefix': m.prefix,
        'suffix': m.suffix,
        'articulator': m.articulator,
        'head': head,
        'mods': mods,
        'term': term,
        'frame': frame,
        'headless': headless,
        'first_atom': first_atom,
        'pipeline': classify_pipeline(mid),
        'placement': getattr(t, 'placement', None),
        'category': cc.classify(mid),
        'mid_len': len(mid),
    })

print(f"  B: {len(systems['B'])} tokens")

print("Loading AZC tokens...")
for t in tx.all():
    if t.language != 'NA':
        continue
    if not t.word or not t.word.strip():
        continue
    if '*' in t.word:
        continue
    m = morph.extract(t.word)
    mid = m.middle
    if not mid:
        continue
    head, mods, term, frame = decompose_middle_hmt(mid)
    headless = head is None
    first_atom = mid[0] if mid else None
    systems['AZC'].append({
        'word': t.word,
        'folio': t.folio,
        'middle': mid,
        'prefix': m.prefix,
        'suffix': m.suffix,
        'articulator': m.articulator,
        'head': head,
        'mods': mods,
        'term': term,
        'frame': frame,
        'headless': headless,
        'first_atom': first_atom,
        'pipeline': classify_pipeline(mid),
        'placement': getattr(t, 'placement', None),
        'zone': classify_zone(getattr(t, 'placement', None)),
        'category': cc.classify(mid),
        'mid_len': len(mid),
    })

print(f"  AZC: {len(systems['AZC'])} tokens")

results = {}

# =====================================================================
# T1: Headless rate by system
# =====================================================================
print("\n" + "=" * 70)
print("T1: Headless Rate by System")
print("=" * 70)

t1 = {}
for sys_name, tokens in systems.items():
    n = len(tokens)
    headless_n = sum(1 for t in tokens if t['headless'])
    headless_rate = headless_n / n if n > 0 else 0
    headed_n = n - headless_n
    t1[sys_name] = {
        'N': n,
        'headless_n': headless_n,
        'headless_rate': round(headless_rate, 4),
        'headed_n': headed_n,
    }
    print(f"  {sys_name}: {headless_n}/{n} = {headless_rate:.1%} headless")

# Chi-squared test for homogeneity across systems
table = np.array([[t1[s]['headless_n'], t1[s]['headed_n']] for s in ['A', 'B', 'AZC']])
chi2, p, dof, exp = stats.chi2_contingency(table)
t1['chi2'] = round(chi2, 2)
t1['p'] = p
t1['dof'] = int(dof)
print(f"  Chi2={chi2:.2f}, p={p:.2e}, dof={dof}")

# Pairwise comparisons
for s1, s2 in [('A', 'B'), ('A', 'AZC'), ('B', 'AZC')]:
    tab2 = np.array([[t1[s1]['headless_n'], t1[s1]['headed_n']],
                      [t1[s2]['headless_n'], t1[s2]['headed_n']]])
    chi2_pair, p_pair, _, _ = stats.chi2_contingency(tab2)
    ratio = t1[s1]['headless_rate'] / t1[s2]['headless_rate'] if t1[s2]['headless_rate'] > 0 else float('inf')
    print(f"  {s1} vs {s2}: chi2={chi2_pair:.2f}, p={p_pair:.2e}, ratio={ratio:.3f}")
    t1[f'{s1}_vs_{s2}'] = {'chi2': round(chi2_pair, 2), 'p': p_pair, 'ratio': round(ratio, 3)}

results['T1_headless_rate'] = t1

# =====================================================================
# T2: Pseudo-HEAD first-atom differentiation per system
# =====================================================================
print("\n" + "=" * 70)
print("T2: Pseudo-HEAD First-Atom Differentiation")
print("=" * 70)

t2 = {}
all_first_atoms = sorted(set(
    t['first_atom'] for tokens in systems.values() for t in tokens
    if t['headless'] and t['first_atom']
))

for sys_name, tokens in systems.items():
    headless = [t for t in tokens if t['headless']]
    first_atom_counts = Counter(t['first_atom'] for t in headless if t['first_atom'])
    total = sum(first_atom_counts.values())
    profile = {a: round(first_atom_counts.get(a, 0) / total, 4) if total > 0 else 0
               for a in all_first_atoms}
    # Top 5
    top5 = first_atom_counts.most_common(5)
    t2[sys_name] = {
        'N_headless': len(headless),
        'first_atom_counts': dict(first_atom_counts),
        'first_atom_profile': profile,
        'top5': [(a, c, round(c / total, 3)) for a, c in top5] if total > 0 else [],
    }
    print(f"\n  {sys_name} (N={len(headless)} headless):")
    for atom, count in sorted(first_atom_counts.items(), key=lambda x: -x[1])[:8]:
        print(f"    {atom}: {count} ({count/total:.1%})")

# Category profiles of headless tokens per system
for sys_name in ['A', 'B', 'AZC']:
    headless = [t for t in systems[sys_name] if t['headless']]
    headed = [t for t in systems[sys_name] if not t['headless']]

    cats_headless = Counter(t['category'] for t in headless if t['category'])
    cats_headed = Counter(t['category'] for t in headed if t['category'])

    total_hl = sum(cats_headless.values())
    total_hd = sum(cats_headed.values())

    all_cats = sorted(set(list(cats_headless.keys()) + list(cats_headed.keys())))
    cat_profile_hl = {c: round(cats_headless.get(c, 0) / total_hl, 4) if total_hl > 0 else 0
                      for c in all_cats}
    cat_profile_hd = {c: round(cats_headed.get(c, 0) / total_hd, 4) if total_hd > 0 else 0
                      for c in all_cats}
    t2[f'{sys_name}_cat_headless'] = cat_profile_hl
    t2[f'{sys_name}_cat_headed'] = cat_profile_hd

results['T2_pseudo_head'] = t2

# =====================================================================
# T3: da-PREFIX exclusivity cross-system
# =====================================================================
print("\n" + "=" * 70)
print("T3: da-PREFIX Exclusivity for Headless Tokens")
print("=" * 70)

t3 = {}
for sys_name, tokens in systems.items():
    headless = [t for t in tokens if t['headless']]
    headed = [t for t in tokens if not t['headless']]

    # da PREFIX rates
    da_headless = sum(1 for t in headless if t['prefix'] == 'da')
    da_headed = sum(1 for t in headed if t['prefix'] == 'da')

    n_headless = len(headless)
    n_headed = len(headed)

    da_rate_headless = da_headless / n_headless if n_headless > 0 else 0
    da_rate_headed = da_headed / n_headed if n_headed > 0 else 0
    enrichment = da_rate_headless / da_rate_headed if da_rate_headed > 0 else float('inf')

    # Broader PREFIX distribution for headless
    pfx_headless = Counter(t['prefix'] or 'BARE' for t in headless)
    pfx_headed = Counter(t['prefix'] or 'BARE' for t in headed)

    t3[sys_name] = {
        'da_headless_n': da_headless,
        'da_headless_rate': round(da_rate_headless, 4),
        'da_headed_n': da_headed,
        'da_headed_rate': round(da_rate_headed, 4),
        'da_enrichment': round(enrichment, 1) if enrichment != float('inf') else 'inf',
        'N_headless': n_headless,
        'N_headed': n_headed,
        'prefix_headless_top5': pfx_headless.most_common(5),
        'prefix_headed_top5': pfx_headed.most_common(5),
    }

    print(f"\n  {sys_name}:")
    print(f"    da in headless: {da_headless}/{n_headless} = {da_rate_headless:.1%}")
    print(f"    da in headed:   {da_headed}/{n_headed} = {da_rate_headed:.1%}")
    print(f"    Enrichment: {enrichment:.1f}x")
    print(f"    Headless PREFIX top5: {pfx_headless.most_common(5)}")

    # sa and ta (headless-exclusive in B per C1491)
    for pfx in ['sa', 'ta']:
        sa_hl = sum(1 for t in headless if t['prefix'] == pfx)
        sa_hd = sum(1 for t in headed if t['prefix'] == pfx)
        total_pfx = sa_hl + sa_hd
        hl_frac = sa_hl / total_pfx if total_pfx > 0 else 0
        print(f"    {pfx}: headless={sa_hl}, headed={sa_hd}, headless_frac={hl_frac:.1%}")
        t3[f'{sys_name}_{pfx}_headless'] = sa_hl
        t3[f'{sys_name}_{pfx}_headed'] = sa_hd
        t3[f'{sys_name}_{pfx}_headless_frac'] = round(hl_frac, 3)

results['T3_da_prefix'] = t3

# =====================================================================
# T4: Suffix rate bifurcation cross-system
# =====================================================================
print("\n" + "=" * 70)
print("T4: Suffix Rate Bifurcation (Headless vs Headed)")
print("=" * 70)

t4 = {}
for sys_name, tokens in systems.items():
    headless = [t for t in tokens if t['headless']]
    headed = [t for t in tokens if not t['headless']]

    sfx_headless = sum(1 for t in headless if t['suffix'])
    sfx_headed = sum(1 for t in headed if t['suffix'])

    n_hl = len(headless)
    n_hd = len(headed)

    rate_hl = sfx_headless / n_hl if n_hl > 0 else 0
    rate_hd = sfx_headed / n_hd if n_hd > 0 else 0

    # Chi-squared for suffix rate difference
    tab = np.array([[sfx_headless, n_hl - sfx_headless],
                     [sfx_headed, n_hd - sfx_headed]])
    if tab.min() >= 0 and n_hl > 0 and n_hd > 0:
        chi2_sfx, p_sfx, _, _ = stats.chi2_contingency(tab)
    else:
        chi2_sfx, p_sfx = 0, 1

    # Suffix type distribution
    sfx_types_hl = Counter(t['suffix'] for t in headless if t['suffix'])
    sfx_types_hd = Counter(t['suffix'] for t in headed if t['suffix'])

    t4[sys_name] = {
        'headless_suffix_rate': round(rate_hl, 4),
        'headed_suffix_rate': round(rate_hd, 4),
        'delta': round(rate_hl - rate_hd, 4),
        'ratio': round(rate_hl / rate_hd, 3) if rate_hd > 0 else 'inf',
        'chi2': round(chi2_sfx, 2),
        'p': p_sfx,
        'headless_suffix_n': sfx_headless,
        'headed_suffix_n': sfx_headed,
        'N_headless': n_hl,
        'N_headed': n_hd,
        'headless_suffix_top5': sfx_types_hl.most_common(5),
        'headed_suffix_top5': sfx_types_hd.most_common(5),
    }

    print(f"\n  {sys_name}:")
    print(f"    Headless suffix rate: {sfx_headless}/{n_hl} = {rate_hl:.1%}")
    print(f"    Headed suffix rate:   {sfx_headed}/{n_hd} = {rate_hd:.1%}")
    print(f"    Delta: {rate_hl - rate_hd:+.1%}, Ratio: {rate_hl / rate_hd:.2f}x" if rate_hd > 0 else "    Headed suffix rate is 0")
    print(f"    Chi2={chi2_sfx:.2f}, p={p_sfx:.2e}")

results['T4_suffix_bifurcation'] = t4

# =====================================================================
# T5: AZC zone headless distribution
# =====================================================================
print("\n" + "=" * 70)
print("T5: AZC Zone Headless Distribution")
print("=" * 70)

t5 = {}
azc_tokens = systems['AZC']
zone_headless = defaultdict(lambda: {'headless': 0, 'headed': 0})
for t in azc_tokens:
    zone = t.get('zone', 'UNKNOWN')
    if t['headless']:
        zone_headless[zone]['headless'] += 1
    else:
        zone_headless[zone]['headed'] += 1

print(f"  {'Zone':<8} {'N':>6} {'Headless':>10} {'Rate':>8}")
print(f"  {'-'*36}")

for zone in ['R', 'C', 'S', 'P', 'L', 'OTHER']:
    data = zone_headless[zone]
    n = data['headless'] + data['headed']
    rate = data['headless'] / n if n > 0 else 0
    t5[zone] = {
        'headless': data['headless'],
        'headed': data['headed'],
        'N': n,
        'rate': round(rate, 4),
    }
    print(f"  {zone:<8} {n:>6} {data['headless']:>10} {rate:>7.1%}")

# Chi-squared across major zones
major_zones_data = {z: zone_headless[z] for z in ['R', 'C', 'S', 'P']}
if all(v['headless'] + v['headed'] > 0 for v in major_zones_data.values()):
    table5 = np.array([[v['headless'], v['headed']] for v in major_zones_data.values()])
    chi2_5, p_5, dof_5, _ = stats.chi2_contingency(table5)
    v_5 = cramers_v(table5)
    t5['chi2'] = round(chi2_5, 2)
    t5['p'] = p_5
    t5['V'] = round(v_5, 4)
    print(f"\n  Homogeneity chi2={chi2_5:.2f}, p={p_5:.2e}, V={v_5:.4f}")

# Compare zone headless rates to B baseline
b_headless_rate = t1['B']['headless_rate']
for zone in ['R', 'C', 'S', 'P']:
    ratio_to_b = t5[zone]['rate'] / b_headless_rate if b_headless_rate > 0 else 0
    t5[zone]['ratio_to_B'] = round(ratio_to_b, 3)
    print(f"  {zone} vs B: {ratio_to_b:.2f}x")

results['T5_azc_zones'] = t5

# =====================================================================
# T6: Bridge vs dark pipeline headless enrichment
# =====================================================================
print("\n" + "=" * 70)
print("T6: Bridge vs Dark Pipeline Headless Enrichment")
print("=" * 70)

t6 = {}
for sys_name, tokens in systems.items():
    pipeline_headless = defaultdict(lambda: {'headless': 0, 'headed': 0})
    for t in tokens:
        pipe = t['pipeline']
        if t['headless']:
            pipeline_headless[pipe]['headless'] += 1
        else:
            pipeline_headless[pipe]['headed'] += 1

    print(f"\n  {sys_name}:")
    sys_data = {}
    for pipe in ['bridge', 'dark', 'exclusive']:
        data = pipeline_headless[pipe]
        n = data['headless'] + data['headed']
        rate = data['headless'] / n if n > 0 else 0
        sys_data[pipe] = {
            'headless': data['headless'],
            'headed': data['headed'],
            'N': n,
            'rate': round(rate, 4),
        }
        print(f"    {pipe:<12} {n:>6} tokens, {data['headless']:>5} headless = {rate:.1%}")

    # Bridge vs dark chi-squared
    if sys_data['bridge']['N'] > 0 and sys_data['dark']['N'] > 0:
        tab6 = np.array([
            [sys_data['bridge']['headless'], sys_data['bridge']['headed']],
            [sys_data['dark']['headless'], sys_data['dark']['headed']],
        ])
        chi2_6, p_6, _, _ = stats.chi2_contingency(tab6)
        ratio_6 = sys_data['dark']['rate'] / sys_data['bridge']['rate'] if sys_data['bridge']['rate'] > 0 else float('inf')
        sys_data['bridge_vs_dark_chi2'] = round(chi2_6, 2)
        sys_data['bridge_vs_dark_p'] = p_6
        sys_data['dark_bridge_ratio'] = round(ratio_6, 3)
        print(f"    Dark/Bridge ratio: {ratio_6:.2f}x, chi2={chi2_6:.2f}, p={p_6:.2e}")

    t6[sys_name] = sys_data

results['T6_pipeline'] = t6

# =====================================================================
# T7: Terminal profile comparison (headed vs headless per system)
# =====================================================================
print("\n" + "=" * 70)
print("T7: Terminal Profile (Headed vs Headless)")
print("=" * 70)

t7 = {}
term_labels = ['y', 'l', 'r', 'h', 'm', 'n', 'bare']

for sys_name, tokens in systems.items():
    headless = [t for t in tokens if t['headless']]
    headed = [t for t in tokens if not t['headless']]

    term_hl = Counter(t['term'] for t in headless)
    term_hd = Counter(t['term'] for t in headed)

    total_hl = sum(term_hl.values())
    total_hd = sum(term_hd.values())

    print(f"\n  {sys_name}:")
    print(f"  {'Term':<6} {'Headless':>10} {'Headed':>10} {'HL%':>8} {'HD%':>8} {'Ratio':>8}")

    term_data = {}
    for tl in term_labels:
        c_hl = term_hl.get(tl, 0)
        c_hd = term_hd.get(tl, 0)
        r_hl = c_hl / total_hl if total_hl > 0 else 0
        r_hd = c_hd / total_hd if total_hd > 0 else 0
        ratio = r_hl / r_hd if r_hd > 0 else float('inf')
        term_data[tl] = {
            'headless_n': c_hl, 'headed_n': c_hd,
            'headless_rate': round(r_hl, 4), 'headed_rate': round(r_hd, 4),
            'ratio': round(ratio, 3) if ratio != float('inf') else 'inf',
        }
        ratio_str = f"{ratio:.2f}x" if ratio != float('inf') else "inf"
        print(f"  {tl:<6} {c_hl:>10} {c_hd:>10} {r_hl:>7.1%} {r_hd:>7.1%} {ratio_str:>8}")

    # JSD between headless and headed terminal profiles
    vec_hl = np.array([term_hl.get(tl, 0) for tl in term_labels], dtype=float)
    vec_hd = np.array([term_hd.get(tl, 0) for tl in term_labels], dtype=float)
    j = jsd(vec_hl, vec_hd)
    term_data['jsd_hl_vs_hd'] = round(j, 4)
    print(f"  JSD(headless, headed) = {j:.4f}")

    t7[sys_name] = term_data

# Cross-system: compare headless terminal profiles
print("\n  Cross-system headless terminal JSD:")
for s1, s2 in [('A', 'B'), ('A', 'AZC'), ('B', 'AZC')]:
    vec1 = np.array([Counter(t['term'] for t in systems[s1] if t['headless']).get(tl, 0) for tl in term_labels], dtype=float)
    vec2 = np.array([Counter(t['term'] for t in systems[s2] if t['headless']).get(tl, 0) for tl in term_labels], dtype=float)
    j_cross = jsd(vec1, vec2)
    t7[f'jsd_{s1}_vs_{s2}_headless'] = round(j_cross, 4)
    print(f"  JSD({s1}, {s2}) headless terminals = {j_cross:.4f}")

results['T7_terminal'] = t7

# =====================================================================
# T8: Category profile comparison (headless per system)
# =====================================================================
print("\n" + "=" * 70)
print("T8: Category Profile (Headless vs Headed per System)")
print("=" * 70)

t8 = {}
all_cats = ['THERMAL', 'CONTAINMENT', 'FLOW', 'MONITORING',
            'OPERATION', 'STAGING', 'MARKING', 'TRANSITION']

for sys_name, tokens in systems.items():
    headless = [t for t in tokens if t['headless']]
    headed = [t for t in tokens if not t['headless']]

    cat_hl = Counter(t['category'] for t in headless if t['category'])
    cat_hd = Counter(t['category'] for t in headed if t['category'])

    total_hl = sum(cat_hl.values())
    total_hd = sum(cat_hd.values())

    print(f"\n  {sys_name} (headless N={total_hl}, headed N={total_hd}):")
    cat_data = {}
    for cat in all_cats:
        c_hl = cat_hl.get(cat, 0)
        c_hd = cat_hd.get(cat, 0)
        r_hl = c_hl / total_hl if total_hl > 0 else 0
        r_hd = c_hd / total_hd if total_hd > 0 else 0
        ratio = r_hl / r_hd if r_hd > 0 else (float('inf') if c_hl > 0 else 0)
        cat_data[cat] = {
            'headless_rate': round(r_hl, 4),
            'headed_rate': round(r_hd, 4),
            'ratio': round(ratio, 3) if ratio != float('inf') else 'inf',
        }
        ratio_str = f"{ratio:.2f}x" if ratio != float('inf') else "inf"
        print(f"    {cat:<14} HL={r_hl:.1%}  HD={r_hd:.1%}  {ratio_str}")

    # JSD headless vs headed category
    vec_hl = np.array([cat_hl.get(c, 0) for c in all_cats], dtype=float)
    vec_hd = np.array([cat_hd.get(c, 0) for c in all_cats], dtype=float)
    j = jsd(vec_hl, vec_hd)
    cat_data['jsd_hl_vs_hd'] = round(j, 4)
    print(f"    JSD(headless, headed) = {j:.4f}")

    t8[sys_name] = cat_data

# Cross-system headless category JSD
print("\n  Cross-system headless category JSD:")
for s1, s2 in [('A', 'B'), ('A', 'AZC'), ('B', 'AZC')]:
    cat1 = Counter(t['category'] for t in systems[s1] if t['headless'] and t['category'])
    cat2 = Counter(t['category'] for t in systems[s2] if t['headless'] and t['category'])
    vec1 = np.array([cat1.get(c, 0) for c in all_cats], dtype=float)
    vec2 = np.array([cat2.get(c, 0) for c in all_cats], dtype=float)
    j_cross = jsd(vec1, vec2)
    t8[f'jsd_{s1}_vs_{s2}_headless'] = round(j_cross, 4)
    print(f"  JSD({s1}, {s2}) headless categories = {j_cross:.4f}")

results['T8_category'] = t8

# =====================================================================
# T9: Headless compound length by system
# =====================================================================
print("\n" + "=" * 70)
print("T9: Headless MIDDLE Length by System")
print("=" * 70)

t9 = {}
for sys_name, tokens in systems.items():
    hl_lens = [t['mid_len'] for t in tokens if t['headless']]
    hd_lens = [t['mid_len'] for t in tokens if not t['headless']]

    mean_hl = np.mean(hl_lens) if hl_lens else 0
    mean_hd = np.mean(hd_lens) if hd_lens else 0
    median_hl = np.median(hl_lens) if hl_lens else 0
    median_hd = np.median(hd_lens) if hd_lens else 0

    # Mann-Whitney U test
    if len(hl_lens) > 0 and len(hd_lens) > 0:
        u_stat, u_p = stats.mannwhitneyu(hl_lens, hd_lens, alternative='two-sided')
    else:
        u_stat, u_p = 0, 1

    t9[sys_name] = {
        'headless_mean_len': round(mean_hl, 2),
        'headed_mean_len': round(mean_hd, 2),
        'headless_median_len': median_hl,
        'headed_median_len': median_hd,
        'headless_N': len(hl_lens),
        'headed_N': len(hd_lens),
        'U_stat': round(u_stat, 1),
        'U_p': u_p,
    }
    print(f"  {sys_name}: headless mean={mean_hl:.2f} median={median_hl:.0f} (N={len(hl_lens)})")
    print(f"  {sys_name}: headed   mean={mean_hd:.2f} median={median_hd:.0f} (N={len(hd_lens)})")
    print(f"  {sys_name}: U={u_stat:.1f}, p={u_p:.2e}")

results['T9_length'] = t9

# =====================================================================
# T10: Cross-system headless MIDDLE overlap
# =====================================================================
print("\n" + "=" * 70)
print("T10: Cross-System Headless MIDDLE Type Overlap")
print("=" * 70)

t10 = {}
# Get unique headless MIDDLE types per system
hl_types = {}
for sys_name in ['A', 'B', 'AZC']:
    hl_types[sys_name] = set(t['middle'] for t in systems[sys_name] if t['headless'])
    print(f"  {sys_name}: {len(hl_types[sys_name])} unique headless MIDDLE types")

# Pairwise Jaccard
for s1, s2 in [('A', 'B'), ('A', 'AZC'), ('B', 'AZC')]:
    inter = hl_types[s1] & hl_types[s2]
    union = hl_types[s1] | hl_types[s2]
    jaccard = len(inter) / len(union) if len(union) > 0 else 0
    print(f"  {s1} & {s2}: {len(inter)} shared, Jaccard={jaccard:.3f}")
    t10[f'{s1}_and_{s2}_shared'] = len(inter)
    t10[f'{s1}_and_{s2}_jaccard'] = round(jaccard, 4)
    # What are the shared headless MIDDLEs?
    if len(inter) <= 30:
        t10[f'{s1}_and_{s2}_shared_middles'] = sorted(inter)

# Triple overlap
triple = hl_types['A'] & hl_types['B'] & hl_types['AZC']
print(f"  A & B & AZC: {len(triple)} shared")
t10['triple_shared'] = len(triple)
if len(triple) <= 30:
    t10['triple_shared_middles'] = sorted(triple)

# Exclusive to each system
for sys_name in ['A', 'B', 'AZC']:
    others = set()
    for other in ['A', 'B', 'AZC']:
        if other != sys_name:
            others |= hl_types[other]
    excl = hl_types[sys_name] - others
    t10[f'{sys_name}_exclusive'] = len(excl)
    t10[f'{sys_name}_exclusive_frac'] = round(len(excl) / len(hl_types[sys_name]), 3) if hl_types[sys_name] else 0
    print(f"  {sys_name}-exclusive: {len(excl)} ({len(excl)/len(hl_types[sys_name]):.1%})")

# What proportion of headless tokens are in the shared pool?
for sys_name in ['A', 'B', 'AZC']:
    all_shared = hl_types['A'] & hl_types['B'] & hl_types['AZC']
    in_shared = sum(1 for t in systems[sys_name] if t['headless'] and t['middle'] in all_shared)
    total_hl = sum(1 for t in systems[sys_name] if t['headless'])
    frac = in_shared / total_hl if total_hl > 0 else 0
    t10[f'{sys_name}_triple_shared_token_frac'] = round(frac, 3)
    print(f"  {sys_name}: {in_shared}/{total_hl} ({frac:.1%}) tokens use triple-shared headless MIDDLEs")

results['T10_overlap'] = t10

# =====================================================================
# SUMMARY
# =====================================================================
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

summary = {
    'headless_rates': {s: t1[s]['headless_rate'] for s in ['A', 'B', 'AZC']},
    'homogeneity_chi2': t1['chi2'],
    'homogeneity_p': t1['p'],
    'da_enrichment': {s: t3[s]['da_enrichment'] for s in ['A', 'B', 'AZC']},
    'suffix_headless_rates': {s: t4[s]['headless_suffix_rate'] for s in ['A', 'B', 'AZC']},
    'suffix_headed_rates': {s: t4[s]['headed_suffix_rate'] for s in ['A', 'B', 'AZC']},
    'suffix_delta': {s: t4[s]['delta'] for s in ['A', 'B', 'AZC']},
}

print(f"\n  Headless rates: A={t1['A']['headless_rate']:.1%}, B={t1['B']['headless_rate']:.1%}, AZC={t1['AZC']['headless_rate']:.1%}")
print(f"  Homogeneity: chi2={t1['chi2']}, p={t1['p']:.2e}")
print(f"  da enrichment: A={t3['A']['da_enrichment']}x, B={t3['B']['da_enrichment']}x, AZC={t3['AZC']['da_enrichment']}x")
print(f"  Suffix headless: A={t4['A']['headless_suffix_rate']:.1%}, B={t4['B']['headless_suffix_rate']:.1%}, AZC={t4['AZC']['headless_suffix_rate']:.1%}")
print(f"  Suffix headed:   A={t4['A']['headed_suffix_rate']:.1%}, B={t4['B']['headed_suffix_rate']:.1%}, AZC={t4['AZC']['headed_suffix_rate']:.1%}")

results['summary'] = summary

# =====================================================================
# SAVE
# =====================================================================
out_path = RESULTS_DIR / 'headless_cross_system.json'

# Convert numpy/special types for JSON serialization
def sanitize(obj):
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        return float(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, dict):
        return {k: sanitize(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [sanitize(v) for v in obj]
    if isinstance(obj, tuple):
        return [sanitize(v) for v in obj]
    if isinstance(obj, float) and (math.isnan(obj) or math.isinf(obj)):
        return str(obj)
    return obj

with open(out_path, 'w') as f:
    json.dump(sanitize(results), f, indent=2)

print(f"\n  Results saved to {out_path}")
print("  DONE")
