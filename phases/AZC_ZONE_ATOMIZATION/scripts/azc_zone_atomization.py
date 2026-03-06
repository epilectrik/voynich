"""
Phase 541: AZC Zone-Level Atomization

Research question: Do AZC internal zones differ at the atom level?
Is o-HEAD uniformly enriched or zone-specific? What does zone-level
atomization tell us about AZC's classification function?

Context:
- C1502: AZC o-HEAD enrichment 2.70x overall
- C1269-C1273: AZC category specialization by zone
- C1499: Atom ontology manuscript-wide shared substrate
- C1381: o-initial MIDDLE enrichment in AZC
"""

import json
import math
import os
import sys
from collections import Counter, defaultdict
from scipy import stats
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from scripts.voynich import Transcript, Morphology, decompose_middle_hmt

# -- Output directory --
RESULTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'results')
os.makedirs(RESULTS_DIR, exist_ok=True)

# -- Constants --
HEAD_ATOMS = {'a', 'e', 'o', 'k', 't'}
MOD_ATOMS = {'c', 'd', 'f', 'i', 'p', 's'}
TERM_ATOMS = {'h', 'l', 'm', 'n', 'r', 'y'}
LOCKED_TERMINALS = {'r', 'm'}
CHANNELED_TERMINALS = {'l', 'y', 'n'}
DIFFUSE_TERMINALS = {'h'}

# Zodiac folios
ZODIAC_FOLIOS = {
    'f57v', 'f70r1', 'f70r2', 'f70v1', 'f70v2',
    'f71r', 'f71v', 'f72r1', 'f72r2', 'f72r3',
    'f72v1', 'f72v2', 'f72v3', 'f73r', 'f73v'
}

# Zone classification:
# Major zones: R (ring), C (center), S (star/series), P (p-text), L (label)
# Minor zones: Y, X, O, I, B, Z, U, W, F, T (folio-specific, small counts)
# For analysis, group minor zones into 'OTHER'
MAJOR_ZONES = {'R', 'C', 'S', 'P', 'L'}

# R-series subscripts
R_SERIES = {'R1', 'R2', 'R3', 'R4'}


def classify_zone(placement):
    """Classify a placement code into a major zone."""
    if not placement:
        return 'UNKNOWN'
    first = placement[0]
    if first in MAJOR_ZONES:
        return first
    return 'OTHER'


def classify_zone_detailed(placement):
    """More detailed zone classification including R/S/C subscripts."""
    if not placement:
        return 'UNKNOWN'
    # Check for R-series with subscripts
    if placement in R_SERIES:
        return placement
    if placement.startswith('R'):
        return 'R_unsub'
    # S-series
    if placement in {'S0', 'S1', 'S2', 'S3'}:
        return placement
    if placement.startswith('S'):
        return 'S_unsub'
    # C-series
    if placement in {'C1', 'C2'}:
        return placement
    if placement.startswith('C'):
        return 'C_unsub'
    first = placement[0]
    if first in MAJOR_ZONES:
        return first
    return 'OTHER'


def jsd(p, q):
    """Jensen-Shannon divergence between two probability distributions."""
    # Get all keys
    all_keys = set(p.keys()) | set(q.keys())
    if not all_keys:
        return 0.0
    p_arr = np.array([p.get(k, 0) for k in sorted(all_keys)], dtype=float)
    q_arr = np.array([q.get(k, 0) for k in sorted(all_keys)], dtype=float)
    # Normalize
    p_sum = p_arr.sum()
    q_sum = q_arr.sum()
    if p_sum == 0 or q_sum == 0:
        return 1.0
    p_arr /= p_sum
    q_arr /= q_sum
    # Add small epsilon to avoid log(0)
    eps = 1e-12
    m = (p_arr + q_arr) / 2
    kl_pm = np.sum(p_arr * np.log2((p_arr + eps) / (m + eps)))
    kl_qm = np.sum(q_arr * np.log2((q_arr + eps) / (m + eps)))
    return (kl_pm + kl_qm) / 2


def normalize_dist(counter):
    """Normalize a counter to a probability distribution dict."""
    total = sum(counter.values())
    if total == 0:
        return {}
    return {k: v / total for k, v in counter.items()}


def cramers_v(contingency_table):
    """Compute Cramer's V from a contingency table (list of lists)."""
    table = np.array(contingency_table)
    if table.shape[0] < 2 or table.shape[1] < 2:
        return 0.0, 1.0
    chi2, p, dof, expected = stats.chi2_contingency(table)
    n = table.sum()
    min_dim = min(table.shape[0] - 1, table.shape[1] - 1)
    if min_dim == 0 or n == 0:
        return 0.0, 1.0
    v = math.sqrt(chi2 / (n * min_dim))
    return v, p


# -- Load data --
print("Loading data...")
tx = Transcript()
morph = Morphology()

# Load bridge and dark pipeline MIDDLEs
with open(os.path.join(os.path.dirname(__file__), '..', '..', '..',
          'phases/BRIDGE_MIDDLE_SELECTION_MECHANISM/results/bridge_selection.json')) as f:
    bridge_data = json.load(f)
BRIDGE_MIDDLES = set(bridge_data['t5_structural_profile']['bridge_middles'])

with open(os.path.join(os.path.dirname(__file__), '..', '..', '..',
          'data/dark_pipeline_middles.json')) as f:
    dark_data = json.load(f)
DARK_MIDDLES = set(dark_data['middles'])

# Get AZC tokens
azc_tokens = list(tx.azc())
print(f"Total AZC tokens: {len(azc_tokens)}")

# Filter out empty/uncertain
azc_clean = [t for t in azc_tokens if t.word and t.word.strip() and '*' not in t.word]
print(f"Clean AZC tokens: {len(azc_clean)}")

# Get B tokens for comparison
b_tokens = list(tx.currier_b())
b_clean = [t for t in b_tokens if t.word and t.word.strip() and '*' not in t.word]
print(f"Clean B tokens: {len(b_clean)}")

# Get A tokens for comparison
a_tokens = list(tx.currier_a())
a_clean = [t for t in a_tokens if t.word and t.word.strip() and '*' not in t.word]
print(f"Clean A tokens: {len(a_clean)}")

# -- Extract morphology and atom decomposition for all tokens --
print("\nExtracting morphology...")

def extract_token_atoms(token):
    """Extract HEAD, MOD, TERM from a token's MIDDLE."""
    m = morph.extract(token.word)
    if not m or not m.middle:
        return None
    mid = m.middle
    head, mod_str, term, frame = decompose_middle_hmt(mid)

    # Extract individual modifier atoms
    mods = []
    if mod_str:
        for c in mod_str:
            if c in 'abcdefghijklmnopqrstuvwxyz':
                mods.append(c)

    # Initial atom (first character of MIDDLE)
    initial = mid[0] if mid else None
    # Terminal atom (last character of MIDDLE for non-bare)
    terminal = mid[-1] if mid and len(mid) > 1 else (mid[0] if mid and term == 'bare' else None)

    return {
        'middle': mid,
        'head': head,
        'mods': mods,
        'term': term,
        'frame': frame,
        'initial': initial,
        'terminal': terminal if term != 'bare' else None,
        'prefix': m.prefix,
        'suffix': m.suffix,
        'is_headless': head is None,
        'is_headed': head is not None,
    }

# Pre-compute all token atoms
azc_atoms = []
for t in azc_clean:
    atoms = extract_token_atoms(t)
    if atoms:
        atoms['folio'] = t.folio
        atoms['placement'] = t.placement
        atoms['zone'] = classify_zone(t.placement)
        atoms['zone_detail'] = classify_zone_detailed(t.placement)
        atoms['family'] = 'zodiac' if t.folio in ZODIAC_FOLIOS else 'ac'
        atoms['word'] = t.word
        # Pipeline classification
        mid = atoms['middle']
        if mid in BRIDGE_MIDDLES:
            atoms['pipeline'] = 'bridge'
        elif mid in DARK_MIDDLES:
            atoms['pipeline'] = 'dark'
        else:
            atoms['pipeline'] = 'exclusive'
        azc_atoms.append(atoms)

print(f"Decomposed AZC tokens: {len(azc_atoms)}")

# Pre-compute B atoms for comparison
b_atoms = []
for t in b_clean:
    atoms = extract_token_atoms(t)
    if atoms:
        b_atoms.append(atoms)
print(f"Decomposed B tokens: {len(b_atoms)}")

# Pre-compute A atoms for comparison
a_atom_list = []
for t in a_clean:
    atoms = extract_token_atoms(t)
    if atoms:
        a_atom_list.append(atoms)
print(f"Decomposed A tokens: {len(a_atom_list)}")

results = {
    'phase': 541,
    'name': 'AZC_ZONE_ATOMIZATION',
    'n_azc_total': len(azc_tokens),
    'n_azc_clean': len(azc_clean),
    'n_azc_decomposed': len(azc_atoms),
}

# ===============================================================
# Test 1: Population Census by Zone
# ===============================================================
print("\n" + "=" * 70)
print("TEST 1: AZC Population Census by Zone")
print("=" * 70)

zone_counts = Counter(a['zone'] for a in azc_atoms)
zone_family = defaultdict(lambda: Counter())
for a in azc_atoms:
    zone_family[a['zone']][a['family']] += 1

print(f"\n{'Zone':<8} {'Total':>6} {'Zodiac':>8} {'A/C':>6} {'%Total':>8}")
print("-" * 40)
total = len(azc_atoms)
for zone in ['R', 'C', 'S', 'P', 'L', 'OTHER']:
    n = zone_counts[zone]
    z = zone_family[zone]['zodiac']
    ac = zone_family[zone]['ac']
    print(f"{zone:<8} {n:>6} {z:>8} {ac:>6} {n/total*100:>7.1f}%")

# Detailed R-series breakdown
print(f"\n{'R-detail':<10} {'Total':>6} {'Zodiac':>8} {'A/C':>6}")
print("-" * 35)
r_detail = Counter()
r_detail_family = defaultdict(lambda: Counter())
for a in azc_atoms:
    if a['zone'] == 'R':
        r_detail[a['zone_detail']] += 1
        r_detail_family[a['zone_detail']][a['family']] += 1

for rd in sorted(r_detail.keys()):
    n = r_detail[rd]
    z = r_detail_family[rd]['zodiac']
    ac = r_detail_family[rd]['ac']
    print(f"{rd:<10} {n:>6} {z:>8} {ac:>6}")

results['T1_census'] = {
    'zone_counts': dict(zone_counts),
    'zone_family': {z: dict(c) for z, c in zone_family.items()},
    'r_detail': dict(r_detail),
}

# ===============================================================
# Test 2: HEAD Domain Profile by Zone
# ===============================================================
print("\n" + "=" * 70)
print("TEST 2: HEAD Domain Profile by Zone")
print("=" * 70)

head_labels = ['a', 'e', 'o', 'k', 't', 'headless']

# Compute HEAD distribution per zone
zone_head = defaultdict(Counter)
for a in azc_atoms:
    h = a['head'] if a['head'] else 'headless'
    zone_head[a['zone']][h] += 1

# Also compute overall AZC, B, and A profiles for reference
azc_head_all = Counter()
for a in azc_atoms:
    h = a['head'] if a['head'] else 'headless'
    azc_head_all[h] += 1

b_head_all = Counter()
for a in b_atoms:
    h = a['head'] if a['head'] else 'headless'
    b_head_all[h] += 1

a_head_all = Counter()
for a in a_atom_list:
    h = a['head'] if a['head'] else 'headless'
    a_head_all[h] += 1

print(f"\n{'Zone':<8} {'N':>5}", end='')
for h in head_labels:
    print(f" {h:>9}", end='')
print()
print("-" * 70)

head_profiles = {}
for zone in ['R', 'C', 'S', 'P', 'L', 'OTHER', 'AZC_all', 'B_all', 'A_all']:
    if zone == 'AZC_all':
        counts = azc_head_all
        n = len(azc_atoms)
    elif zone == 'B_all':
        counts = b_head_all
        n = len(b_atoms)
    elif zone == 'A_all':
        counts = a_head_all
        n = len(a_atom_list)
    else:
        counts = zone_head[zone]
        n = zone_counts[zone]

    if n == 0:
        continue

    profile = {}
    print(f"{zone:<8} {n:>5}", end='')
    for h in head_labels:
        frac = counts[h] / n if n > 0 else 0
        profile[h] = frac
        print(f" {frac:>8.1%}", end='')
    print()
    head_profiles[zone] = profile

# Compute o-HEAD enrichment by zone relative to B
print(f"\no-HEAD enrichment by zone (relative to B {head_profiles['B_all']['o']:.1%}):")
b_o_rate = head_profiles['B_all']['o']
for zone in ['R', 'C', 'S', 'P', 'L', 'OTHER', 'AZC_all']:
    if zone in head_profiles:
        o_rate = head_profiles[zone]['o']
        ratio = o_rate / b_o_rate if b_o_rate > 0 else float('inf')
        print(f"  {zone:<8}: {o_rate:.1%} ({ratio:.2f}x B)")

# Chi-squared test: is HEAD distribution zone-dependent?
zones_for_test = [z for z in ['R', 'C', 'S', 'P'] if zone_counts[z] >= 30]
if len(zones_for_test) >= 2:
    contingency = []
    for zone in zones_for_test:
        row = [zone_head[zone].get(h, 0) for h in head_labels]
        contingency.append(row)
    v, p = cramers_v(contingency)
    chi2, chi_p, dof, _ = stats.chi2_contingency(contingency)
    print(f"\nHEAD x Zone chi2={chi2:.1f}, p={chi_p:.2e}, V={v:.3f} (zones: {zones_for_test})")

results['T2_head_profile'] = {
    'zone_head_counts': {z: dict(c) for z, c in zone_head.items()},
    'head_profiles': head_profiles,
    'o_enrichment_vs_B': {z: head_profiles[z]['o'] / b_o_rate if z in head_profiles and b_o_rate > 0 else None
                          for z in ['R', 'C', 'S', 'P', 'L', 'OTHER', 'AZC_all']},
    'chi2_head_zone': {'chi2': chi2, 'p': chi_p, 'V': v, 'dof': dof, 'zones_tested': zones_for_test} if len(zones_for_test) >= 2 else None,
}

# ===============================================================
# Test 3: TERMINAL Profile by Zone
# ===============================================================
print("\n" + "=" * 70)
print("TEST 3: TERMINAL Profile by Zone")
print("=" * 70)

term_labels = sorted(set(a['term'] for a in azc_atoms if a['term']))

zone_term = defaultdict(Counter)
for a in azc_atoms:
    if a['term']:
        zone_term[a['zone']][a['term']] += 1

# Overall profiles
azc_term_all = Counter(a['term'] for a in azc_atoms if a['term'])
b_term_all = Counter(a['term'] for a in b_atoms if a['term'])

# Compute terminal tier proportions
def terminal_tier_fracs(term_counter):
    total = sum(term_counter.values())
    if total == 0:
        return {}
    locked = sum(term_counter.get(t, 0) for t in LOCKED_TERMINALS)
    channeled = sum(term_counter.get(t, 0) for t in CHANNELED_TERMINALS)
    diffuse = sum(term_counter.get(t, 0) for t in DIFFUSE_TERMINALS)
    bare = term_counter.get('bare', 0)
    return {
        'LOCKED': locked / total,
        'CHANNELED': channeled / total,
        'DIFFUSE': diffuse / total,
        'bare': bare / total,
    }

print(f"\n{'Zone':<8} {'N':>5}", end='')
for t in ['bare', 'h', 'l', 'y', 'n', 'r', 'm']:
    print(f" {t:>7}", end='')
print()
print("-" * 70)

term_profiles = {}
for zone in ['R', 'C', 'S', 'P', 'L', 'OTHER', 'AZC_all', 'B_all']:
    if zone == 'AZC_all':
        counts = azc_term_all
        n = sum(azc_term_all.values())
    elif zone == 'B_all':
        counts = b_term_all
        n = sum(b_term_all.values())
    else:
        counts = zone_term[zone]
        n = sum(counts.values())

    if n == 0:
        continue

    profile = {}
    print(f"{zone:<8} {n:>5}", end='')
    for t in ['bare', 'h', 'l', 'y', 'n', 'r', 'm']:
        frac = counts.get(t, 0) / n if n > 0 else 0
        profile[t] = frac
        print(f" {frac:>6.1%}", end='')
    print()
    term_profiles[zone] = profile

# Terminal tier summary
print(f"\nTerminal tier proportions:")
print(f"{'Zone':<8} {'LOCKED':>8} {'CHANNEL':>8} {'DIFFUSE':>8} {'bare':>8}")
print("-" * 40)
tier_data = {}
for zone in ['R', 'C', 'S', 'P', 'AZC_all', 'B_all']:
    if zone == 'AZC_all':
        tiers = terminal_tier_fracs(azc_term_all)
    elif zone == 'B_all':
        tiers = terminal_tier_fracs(b_term_all)
    else:
        tiers = terminal_tier_fracs(zone_term[zone])

    if not tiers:
        continue
    tier_data[zone] = tiers
    print(f"{zone:<8} {tiers.get('LOCKED', 0):>7.1%} {tiers.get('CHANNELED', 0):>7.1%} "
          f"{tiers.get('DIFFUSE', 0):>7.1%} {tiers.get('bare', 0):>7.1%}")

results['T3_terminal_profile'] = {
    'term_profiles': term_profiles,
    'tier_proportions': tier_data,
}

# ===============================================================
# Test 4: Modifier Profile by Zone
# ===============================================================
print("\n" + "=" * 70)
print("TEST 4: Modifier Profile by Zone")
print("=" * 70)

zone_mods = defaultdict(Counter)
for a in azc_atoms:
    for m in a['mods']:
        zone_mods[a['zone']][m] += 1

azc_mods_all = Counter()
for a in azc_atoms:
    for m in a['mods']:
        azc_mods_all[m] += 1

b_mods_all = Counter()
for a in b_atoms:
    for m in a['mods']:
        b_mods_all[m] += 1

mod_chars = sorted(set(azc_mods_all.keys()) | set(b_mods_all.keys()))

print(f"\n{'Zone':<8}", end='')
for m in ['c', 'd', 'f', 'i', 'p', 's']:
    print(f" {m:>7}", end='')
print(f" {'total':>7}")
print("-" * 60)

mod_profiles = {}
for zone in ['R', 'C', 'S', 'P', 'AZC_all', 'B_all']:
    if zone == 'AZC_all':
        counts = azc_mods_all
    elif zone == 'B_all':
        counts = b_mods_all
    else:
        counts = zone_mods[zone]

    total_mods = sum(counts.values())
    n_tokens = zone_counts.get(zone, len(azc_atoms) if zone == 'AZC_all' else len(b_atoms))

    profile = {}
    print(f"{zone:<8}", end='')
    for m in ['c', 'd', 'f', 'i', 'p', 's']:
        rate = counts.get(m, 0) / n_tokens if n_tokens > 0 else 0
        profile[m] = rate
        print(f" {rate:>6.1%}", end='')
    print(f" {total_mods / n_tokens:>6.1%}" if n_tokens > 0 else "    N/A")
    mod_profiles[zone] = profile

results['T4_modifier_profile'] = {
    'zone_mod_counts': {z: dict(c) for z, c in zone_mods.items()},
    'mod_profiles': mod_profiles,
}

# ===============================================================
# Test 5: Headless Abundance by Zone
# ===============================================================
print("\n" + "=" * 70)
print("TEST 5: Headless Abundance by Zone")
print("=" * 70)

zone_headless = defaultdict(lambda: [0, 0])  # [headless_count, total]
for a in azc_atoms:
    zone_headless[a['zone']][1] += 1
    if a['is_headless']:
        zone_headless[a['zone']][0] += 1

# Overall rates
azc_headless_rate = sum(1 for a in azc_atoms if a['is_headless']) / len(azc_atoms)
b_headless_rate = sum(1 for a in b_atoms if a['is_headless']) / len(b_atoms)

print(f"\n{'Zone':<8} {'Headless':>10} {'Total':>8} {'Rate':>8} {'vs B':>8}")
print("-" * 45)
headless_data = {}
for zone in ['R', 'C', 'S', 'P', 'L', 'OTHER', 'AZC_all', 'B_all']:
    if zone == 'AZC_all':
        hl = sum(1 for a in azc_atoms if a['is_headless'])
        tot = len(azc_atoms)
    elif zone == 'B_all':
        hl = sum(1 for a in b_atoms if a['is_headless'])
        tot = len(b_atoms)
    else:
        hl, tot = zone_headless[zone]

    if tot == 0:
        continue

    rate = hl / tot
    ratio = rate / b_headless_rate if b_headless_rate > 0 else float('inf')
    print(f"{zone:<8} {hl:>10} {tot:>8} {rate:>7.1%} {ratio:>7.2f}x")
    headless_data[zone] = {'count': hl, 'total': tot, 'rate': rate, 'vs_B': ratio}

results['T5_headless'] = headless_data

# ===============================================================
# Test 6: Zodiac vs A/C Family Comparison
# ===============================================================
print("\n" + "=" * 70)
print("TEST 6: Zodiac vs A/C Family Atom Profiles")
print("=" * 70)

family_head = defaultdict(Counter)
family_term = defaultdict(Counter)
family_mods = defaultdict(Counter)
family_headless = defaultdict(lambda: [0, 0])

for a in azc_atoms:
    fam = a['family']
    h = a['head'] if a['head'] else 'headless'
    family_head[fam][h] += 1
    if a['term']:
        family_term[fam][a['term']] += 1
    for m in a['mods']:
        family_mods[fam][m] += 1
    family_headless[fam][1] += 1
    if a['is_headless']:
        family_headless[fam][0] += 1

# HEAD comparison
print(f"\nHEAD distribution by family:")
print(f"{'Family':<10} {'N':>5}", end='')
for h in head_labels:
    print(f" {h:>9}", end='')
print()
print("-" * 72)
family_head_profiles = {}
for fam in ['zodiac', 'ac']:
    n = sum(family_head[fam].values())
    profile = {}
    print(f"{fam:<10} {n:>5}", end='')
    for h in head_labels:
        frac = family_head[fam][h] / n if n > 0 else 0
        profile[h] = frac
        print(f" {frac:>8.1%}", end='')
    print()
    family_head_profiles[fam] = profile

# JSD between families
family_jsd_head = jsd(
    normalize_dist(family_head['zodiac']),
    normalize_dist(family_head['ac'])
)
print(f"\nHEAD JSD(zodiac, ac) = {family_jsd_head:.4f}")

# Terminal comparison
family_term_profiles = {}
print(f"\nTerminal distribution by family:")
print(f"{'Family':<10} {'N':>5}", end='')
for t in ['bare', 'h', 'l', 'y', 'n', 'r', 'm']:
    print(f" {t:>7}", end='')
print()
for fam in ['zodiac', 'ac']:
    n = sum(family_term[fam].values())
    profile = {}
    print(f"{fam:<10} {n:>5}", end='')
    for t in ['bare', 'h', 'l', 'y', 'n', 'r', 'm']:
        frac = family_term[fam].get(t, 0) / n if n > 0 else 0
        profile[t] = frac
        print(f" {frac:>6.1%}", end='')
    print()
    family_term_profiles[fam] = profile

family_jsd_term = jsd(
    normalize_dist(family_term['zodiac']),
    normalize_dist(family_term['ac'])
)
print(f"Terminal JSD(zodiac, ac) = {family_jsd_term:.4f}")

# Headless rates
for fam in ['zodiac', 'ac']:
    hl, tot = family_headless[fam]
    print(f"{fam} headless: {hl}/{tot} = {hl/tot:.1%}")

# Intra-family atom diversity (within zodiac, within A/C)
zodiac_folio_heads = defaultdict(Counter)
ac_folio_heads = defaultdict(Counter)
for a in azc_atoms:
    h = a['head'] if a['head'] else 'headless'
    if a['family'] == 'zodiac':
        zodiac_folio_heads[a['folio']][h] += 1
    else:
        ac_folio_heads[a['folio']][h] += 1

# Compute mean pairwise JSD within each family
def mean_pairwise_jsd(folio_profiles):
    folios = list(folio_profiles.keys())
    if len(folios) < 2:
        return 0.0
    jsds = []
    for i in range(len(folios)):
        for j in range(i + 1, len(folios)):
            p = normalize_dist(folio_profiles[folios[i]])
            q = normalize_dist(folio_profiles[folios[j]])
            jsds.append(jsd(p, q))
    return np.mean(jsds) if jsds else 0.0

zodiac_internal_jsd = mean_pairwise_jsd(zodiac_folio_heads)
ac_internal_jsd = mean_pairwise_jsd(ac_folio_heads)
print(f"\nIntra-family HEAD JSD:")
print(f"  Zodiac: {zodiac_internal_jsd:.4f} (uniform = low JSD)")
print(f"  A/C:    {ac_internal_jsd:.4f} (diverse = high JSD)")

results['T6_family_comparison'] = {
    'family_head_profiles': family_head_profiles,
    'family_term_profiles': family_term_profiles,
    'head_jsd': family_jsd_head,
    'term_jsd': family_jsd_term,
    'zodiac_internal_jsd': zodiac_internal_jsd,
    'ac_internal_jsd': ac_internal_jsd,
    'headless_rates': {fam: family_headless[fam][0] / family_headless[fam][1]
                       for fam in ['zodiac', 'ac']},
}

# ===============================================================
# Test 7: R-series Progression (R1->R2->R3->R4)
# ===============================================================
print("\n" + "=" * 70)
print("TEST 7: R-series Atom Progression")
print("=" * 70)

r_head = defaultdict(Counter)
r_term = defaultdict(Counter)
r_headless = defaultdict(lambda: [0, 0])
r_mods = defaultdict(Counter)

for a in azc_atoms:
    zd = a['zone_detail']
    if zd in {'R1', 'R2', 'R3', 'R4'}:
        h = a['head'] if a['head'] else 'headless'
        r_head[zd][h] += 1
        if a['term']:
            r_term[zd][a['term']] += 1
        r_headless[zd][1] += 1
        if a['is_headless']:
            r_headless[zd][0] += 1
        for m in a['mods']:
            r_mods[zd][m] += 1

print(f"\nHEAD distribution across R-series:")
print(f"{'R-pos':<6} {'N':>5}", end='')
for h in head_labels:
    print(f" {h:>9}", end='')
print()
print("-" * 68)
r_head_profiles = {}
for r in ['R1', 'R2', 'R3', 'R4']:
    n = sum(r_head[r].values())
    if n == 0:
        continue
    profile = {}
    print(f"{r:<6} {n:>5}", end='')
    for h in head_labels:
        frac = r_head[r][h] / n if n > 0 else 0
        profile[h] = frac
        print(f" {frac:>8.1%}", end='')
    print()
    r_head_profiles[r] = profile

# Test for monotonic trends
r_positions = [1, 2, 3, 4]
r_ns = [sum(r_head[f'R{p}'].values()) for p in r_positions]
for h in ['o', 'e', 'k', 'headless']:
    values = [r_head_profiles.get(f'R{p}', {}).get(h, 0) for p in r_positions]
    if len([v for v in values if v > 0]) >= 3:
        rho, p = stats.spearmanr(r_positions[:len(values)], values)
        sig = '*' if p < 0.05 else ''
        print(f"  {h} gradient rho={rho:+.3f} p={p:.3f} {sig}")

# Headless across R-series
print(f"\nHeadless across R-series:")
for r in ['R1', 'R2', 'R3', 'R4']:
    hl, tot = r_headless[r]
    if tot > 0:
        print(f"  {r}: {hl}/{tot} = {hl/tot:.1%}")

# Pairwise JSD across R-series
print(f"\nR-series pairwise HEAD JSD:")
for i, r1 in enumerate(['R1', 'R2', 'R3', 'R4']):
    for r2 in ['R1', 'R2', 'R3', 'R4'][i+1:]:
        if r1 in r_head_profiles and r2 in r_head_profiles:
            d = jsd(r_head_profiles[r1], r_head_profiles[r2])
            print(f"  {r1}-{r2}: {d:.4f}")

results['T7_r_series'] = {
    'r_head_profiles': r_head_profiles,
    'r_headless': {r: {'count': r_headless[r][0], 'total': r_headless[r][1],
                       'rate': r_headless[r][0] / r_headless[r][1] if r_headless[r][1] > 0 else 0}
                   for r in ['R1', 'R2', 'R3', 'R4']},
}

# ===============================================================
# Test 8: Zone x Category Interaction (HEAD mediation)
# ===============================================================
print("\n" + "=" * 70)
print("TEST 8: Zone-Category Interaction via HEAD Mediation")
print("=" * 70)

# C1269 says zones predict category. Is this BECAUSE zones predict HEAD?
# We need the category assignments. Use atom-based category voting.
# From C1250: 8 categories mapped from atom profiles

# Use HEAD as proxy for category domain:
# k-HEAD -> THERMAL, t-HEAD -> FLOW, a-HEAD -> iteration-related,
# e-HEAD -> balanced, o-HEAD -> arrangement/STAGING/OPERATION
# headless -> infrastructure

# Since we don't have per-token category labels in AZC directly,
# test whether HEAD distribution fully explains zone differences
# If zone has no signal beyond HEAD, then HEAD mediates zone->category

# Approach: compute zone-zone JSD at HEAD level vs at initial-atom level
# If HEAD JSD ~= initial-atom JSD, HEAD captures zone differences

zone_initial = defaultdict(Counter)
for a in azc_atoms:
    if a['initial']:
        zone_initial[a['zone']][a['initial']] += 1

print("Zone pairwise JSD comparison (HEAD vs initial atom):")
print(f"{'Pair':<12} {'HEAD_JSD':>10} {'Initial_JSD':>12}")
print("-" * 36)
zones_test = [z for z in ['R', 'C', 'S', 'P'] if zone_counts[z] >= 30]
zone_jsd_data = {}
for i, z1 in enumerate(zones_test):
    for z2 in zones_test[i+1:]:
        h_jsd = jsd(normalize_dist(zone_head[z1]), normalize_dist(zone_head[z2]))
        i_jsd = jsd(normalize_dist(zone_initial[z1]), normalize_dist(zone_initial[z2]))
        pair = f"{z1}-{z2}"
        print(f"{pair:<12} {h_jsd:>9.4f} {i_jsd:>11.4f}")
        zone_jsd_data[pair] = {'head_jsd': h_jsd, 'initial_jsd': i_jsd}

# Also compare HEAD JSD to TERMINAL JSD (are zones differentiated more by HEAD or TERM?)
print(f"\n{'Pair':<12} {'HEAD_JSD':>10} {'TERM_JSD':>10}")
print("-" * 34)
for i, z1 in enumerate(zones_test):
    for z2 in zones_test[i+1:]:
        h_jsd = jsd(normalize_dist(zone_head[z1]), normalize_dist(zone_head[z2]))
        t_jsd = jsd(normalize_dist(zone_term[z1]), normalize_dist(zone_term[z2]))
        pair = f"{z1}-{z2}"
        print(f"{pair:<12} {h_jsd:>9.4f} {t_jsd:>9.4f}")

results['T8_zone_category'] = {
    'zone_jsd_comparisons': zone_jsd_data,
}

# ===============================================================
# Test 9: Bridge vs Dark vs AZC-Exclusive by Zone
# ===============================================================
print("\n" + "=" * 70)
print("TEST 9: Pipeline Classification by Zone")
print("=" * 70)

zone_pipeline = defaultdict(Counter)
for a in azc_atoms:
    zone_pipeline[a['zone']][a['pipeline']] += 1

# Overall
azc_pipeline_all = Counter(a['pipeline'] for a in azc_atoms)

print(f"\n{'Zone':<8} {'N':>5} {'bridge':>8} {'dark':>8} {'excl':>8}")
print("-" * 42)
pipeline_data = {}
for zone in ['R', 'C', 'S', 'P', 'L', 'OTHER', 'AZC_all']:
    if zone == 'AZC_all':
        counts = azc_pipeline_all
        n = len(azc_atoms)
    else:
        counts = zone_pipeline[zone]
        n = zone_counts[zone]

    if n == 0:
        continue

    b_rate = counts.get('bridge', 0) / n
    d_rate = counts.get('dark', 0) / n
    e_rate = counts.get('exclusive', 0) / n
    print(f"{zone:<8} {n:>5} {b_rate:>7.1%} {d_rate:>7.1%} {e_rate:>7.1%}")
    pipeline_data[zone] = {'bridge': b_rate, 'dark': d_rate, 'exclusive': e_rate,
                           'bridge_n': counts.get('bridge', 0),
                           'dark_n': counts.get('dark', 0),
                           'exclusive_n': counts.get('exclusive', 0)}

# HEAD profiles within pipeline types within zones
print(f"\no-HEAD rate by pipeline type within zone:")
print(f"{'Zone':<8} {'bridge_o':>10} {'dark_o':>10} {'excl_o':>10}")
print("-" * 42)
for zone in ['R', 'C', 'S', 'P', 'AZC_all']:
    bridge_o = sum(1 for a in azc_atoms if (a['zone'] == zone or zone == 'AZC_all')
                   and a['pipeline'] == 'bridge' and a['head'] == 'o')
    bridge_n = sum(1 for a in azc_atoms if (a['zone'] == zone or zone == 'AZC_all')
                   and a['pipeline'] == 'bridge')
    dark_o = sum(1 for a in azc_atoms if (a['zone'] == zone or zone == 'AZC_all')
                 and a['pipeline'] == 'dark' and a['head'] == 'o')
    dark_n = sum(1 for a in azc_atoms if (a['zone'] == zone or zone == 'AZC_all')
                 and a['pipeline'] == 'dark')
    excl_o = sum(1 for a in azc_atoms if (a['zone'] == zone or zone == 'AZC_all')
                 and a['pipeline'] == 'exclusive' and a['head'] == 'o')
    excl_n = sum(1 for a in azc_atoms if (a['zone'] == zone or zone == 'AZC_all')
                 and a['pipeline'] == 'exclusive')

    b_r = bridge_o / bridge_n if bridge_n > 0 else 0
    d_r = dark_o / dark_n if dark_n > 0 else 0
    e_r = excl_o / excl_n if excl_n > 0 else 0
    print(f"{zone:<8} {b_r:>9.1%} {d_r:>9.1%} {e_r:>9.1%}")

results['T9_pipeline_by_zone'] = pipeline_data

# ===============================================================
# Test 10: Comparison to B and A Atom Profiles (JSD)
# ===============================================================
print("\n" + "=" * 70)
print("TEST 10: AZC Zone Distance to B and A Atom Profiles")
print("=" * 70)

# HEAD-level JSD
b_head_profile = normalize_dist(b_head_all)
a_head_profile = normalize_dist(a_head_all)

print(f"\nHEAD JSD from each AZC zone to B and A:")
print(f"{'Zone':<8} {'vs_B':>8} {'vs_A':>8} {'closer_to':>10}")
print("-" * 38)
jsd_data = {}
for zone in ['R', 'C', 'S', 'P', 'L', 'AZC_all']:
    if zone == 'AZC_all':
        zone_profile = normalize_dist(azc_head_all)
    else:
        zone_profile = normalize_dist(zone_head[zone])

    if not zone_profile:
        continue

    d_b = jsd(zone_profile, b_head_profile)
    d_a = jsd(zone_profile, a_head_profile)
    closer = 'B' if d_b < d_a else 'A'
    print(f"{zone:<8} {d_b:>7.4f} {d_a:>7.4f} {closer:>10}")
    jsd_data[zone] = {'vs_B': d_b, 'vs_A': d_a, 'closer_to': closer}

# Initial atom level JSD
b_initial_all = Counter(a['initial'] for a in b_atoms if a['initial'])
a_initial_all = Counter(a['initial'] for a in a_atom_list if a['initial'])

print(f"\nInitial-atom JSD from each AZC zone to B and A:")
print(f"{'Zone':<8} {'vs_B':>8} {'vs_A':>8} {'closer_to':>10}")
print("-" * 38)
for zone in ['R', 'C', 'S', 'P', 'L', 'AZC_all']:
    if zone == 'AZC_all':
        zone_profile = normalize_dist(Counter(a['initial'] for a in azc_atoms if a['initial']))
    else:
        zone_profile = normalize_dist(Counter(a['initial'] for a in azc_atoms
                                              if a['zone'] == zone and a['initial']))

    if not zone_profile:
        continue

    d_b = jsd(zone_profile, normalize_dist(b_initial_all))
    d_a = jsd(zone_profile, normalize_dist(a_initial_all))
    closer = 'B' if d_b < d_a else 'A'
    print(f"{zone:<8} {d_b:>7.4f} {d_a:>7.4f} {closer:>10}")

results['T10_jsd_comparison'] = jsd_data

# ===============================================================
# Test 11: Label vs Text Atoms
# ===============================================================
print("\n" + "=" * 70)
print("TEST 11: Label vs Text Atom Profiles")
print("=" * 70)

# Labels (L placement) vs P-text (P placement)
label_atoms = [a for a in azc_atoms if a['zone'] == 'L']
ptext_atoms = [a for a in azc_atoms if a['zone'] == 'P']

if label_atoms and ptext_atoms:
    label_head = Counter(a['head'] if a['head'] else 'headless' for a in label_atoms)
    ptext_head = Counter(a['head'] if a['head'] else 'headless' for a in ptext_atoms)

    print(f"\nHEAD distribution:")
    print(f"{'Type':<8} {'N':>5}", end='')
    for h in head_labels:
        print(f" {h:>9}", end='')
    print()
    for name, counts, n in [('Label', label_head, len(label_atoms)),
                              ('P-text', ptext_head, len(ptext_atoms))]:
        print(f"{name:<8} {n:>5}", end='')
        for h in head_labels:
            frac = counts[h] / n if n > 0 else 0
            print(f" {frac:>8.1%}", end='')
        print()

    lp_jsd = jsd(normalize_dist(label_head), normalize_dist(ptext_head))
    print(f"\nLabel-Ptext HEAD JSD: {lp_jsd:.4f}")

    # Pipeline comparison
    label_pipeline = Counter(a['pipeline'] for a in label_atoms)
    ptext_pipeline = Counter(a['pipeline'] for a in ptext_atoms)
    print(f"\nPipeline distribution:")
    print(f"{'Type':<8} {'bridge':>8} {'dark':>8} {'excl':>8}")
    for name, counts, n in [('Label', label_pipeline, len(label_atoms)),
                              ('P-text', ptext_pipeline, len(ptext_atoms))]:
        print(f"{name:<8} {counts.get('bridge', 0)/n:>7.1%} {counts.get('dark', 0)/n:>7.1%} "
              f"{counts.get('exclusive', 0)/n:>7.1%}")

    results['T11_label_vs_text'] = {
        'label_head': dict(label_head),
        'ptext_head': dict(ptext_head),
        'label_n': len(label_atoms),
        'ptext_n': len(ptext_atoms),
        'head_jsd': lp_jsd,
    }
else:
    print("Insufficient data for label vs text comparison.")
    results['T11_label_vs_text'] = {'insufficient_data': True}

# ===============================================================
# Test 12: Atom-Level o-Enrichment Deep Dive
# ===============================================================
print("\n" + "=" * 70)
print("TEST 12: o-Domain Enrichment Deep Dive")
print("=" * 70)

# Where does o appear? As HEAD, as modifier, as terminal?
zone_o_position = defaultdict(Counter)  # zone -> {head, mod, term, initial, any_pos}
for a in azc_atoms:
    mid = a['middle']
    zone = a['zone']
    if 'o' in mid:
        zone_o_position[zone]['any'] += 1
        if a['head'] == 'o':
            zone_o_position[zone]['head'] += 1
        # Check if o in modifier position
        for m in a['mods']:
            if m == 'o':
                zone_o_position[zone]['mod'] += 1
                break
        # Check if o in terminal
        if a['term'] == 'o' or (a['terminal'] == 'o'):
            zone_o_position[zone]['term'] += 1

print(f"\no-atom position distribution by zone:")
print(f"{'Zone':<8} {'N':>5} {'o_any':>7} {'o_HEAD':>7} {'o_MOD':>7} {'o_TERM':>7}")
print("-" * 45)
o_deep = {}
for zone in ['R', 'C', 'S', 'P', 'AZC_all']:
    if zone == 'AZC_all':
        n = len(azc_atoms)
        any_o = sum(zone_o_position[z]['any'] for z in zone_o_position)
        head_o = sum(zone_o_position[z]['head'] for z in zone_o_position)
        mod_o = sum(zone_o_position[z]['mod'] for z in zone_o_position)
        term_o = sum(zone_o_position[z]['term'] for z in zone_o_position)
    else:
        n = zone_counts[zone]
        any_o = zone_o_position[zone]['any']
        head_o = zone_o_position[zone]['head']
        mod_o = zone_o_position[zone]['mod']
        term_o = zone_o_position[zone]['term']

    if n == 0:
        continue

    print(f"{zone:<8} {n:>5} {any_o/n:>6.1%} {head_o/n:>6.1%} {mod_o/n:>6.1%} {term_o/n:>6.1%}")
    o_deep[zone] = {
        'n': n,
        'o_any_rate': any_o / n,
        'o_head_rate': head_o / n,
        'o_mod_rate': mod_o / n,
        'o_term_rate': term_o / n,
    }

# Compare to B
b_o_any = sum(1 for a in b_atoms if 'o' in a['middle'])
b_o_head = sum(1 for a in b_atoms if a['head'] == 'o')
n_b = len(b_atoms)
print(f"{'B_all':<8} {n_b:>5} {b_o_any/n_b:>6.1%} {b_o_head/n_b:>6.1%}")

results['T12_o_deep_dive'] = o_deep

# ===============================================================
# SYNTHESIS
# ===============================================================
print("\n" + "=" * 70)
print("SYNTHESIS")
print("=" * 70)

# 1. Is o-HEAD uniformly enriched or zone-specific?
print("\n1. o-HEAD Distribution:")
o_rates = {z: head_profiles[z]['o'] for z in ['R', 'C', 'S', 'P'] if z in head_profiles}
o_min_zone = min(o_rates, key=o_rates.get)
o_max_zone = max(o_rates, key=o_rates.get)
o_range = o_rates[o_max_zone] - o_rates[o_min_zone]
print(f"   Range: {o_rates[o_min_zone]:.1%} ({o_min_zone}) to {o_rates[o_max_zone]:.1%} ({o_max_zone})")
print(f"   Spread: {o_range:.1%}")
if o_range < 0.05:
    print(f"   VERDICT: o-HEAD is UNIFORMLY enriched across zones")
else:
    print(f"   VERDICT: o-HEAD shows ZONE-SPECIFIC variation")

# 2. Are zones atom-differentiated?
print("\n2. Zone Atom Differentiation:")
if results.get('T2_head_profile', {}).get('chi2_head_zone'):
    chi_result = results['T2_head_profile']['chi2_head_zone']
    print(f"   HEAD x Zone: chi2={chi_result['chi2']:.1f}, V={chi_result['V']:.3f}, p={chi_result['p']:.2e}")
    if chi_result['p'] < 0.001:
        print(f"   VERDICT: Zones are SIGNIFICANTLY differentiated at HEAD level")
    else:
        print(f"   VERDICT: Zones show WEAK/NULL HEAD differentiation")

# 3. Zodiac vs A/C
print("\n3. Family Comparison:")
print(f"   HEAD JSD: {family_jsd_head:.4f}")
print(f"   Internal JSD - Zodiac: {zodiac_internal_jsd:.4f}, A/C: {ac_internal_jsd:.4f}")
if ac_internal_jsd > zodiac_internal_jsd * 1.5:
    print(f"   A/C is {ac_internal_jsd/zodiac_internal_jsd:.1f}x more internally diverse than Zodiac")

# 4. R-series gradient
print("\n4. R-series Gradient:")
if r_head_profiles:
    for h in ['o', 'headless', 'e']:
        vals = [r_head_profiles.get(f'R{p}', {}).get(h, 0) for p in [1, 2, 3, 4]]
        if any(v > 0 for v in vals):
            r, p = stats.spearmanr([1, 2, 3, 4], vals)
            print(f"   {h}: R1={vals[0]:.1%} R2={vals[1]:.1%} R3={vals[2]:.1%} R4={vals[3]:.1%} "
                  f"rho={r:+.3f} p={p:.3f}")

# 5. Pipeline distribution
print("\n5. Pipeline by Zone:")
for zone in ['R', 'C', 'S', 'P']:
    if zone in pipeline_data:
        pd = pipeline_data[zone]
        print(f"   {zone}: bridge={pd['bridge']:.1%}, dark={pd['dark']:.1%}, exclusive={pd['exclusive']:.1%}")

# 6. AZC position in A-B space
print("\n6. AZC Position in A-B Space:")
for zone in ['R', 'C', 'S', 'P', 'AZC_all']:
    if zone in jsd_data:
        d = jsd_data[zone]
        print(f"   {zone}: vs_B={d['vs_B']:.4f}, vs_A={d['vs_A']:.4f} -> closer to {d['closer_to']}")

# -- Save results --
output_path = os.path.join(RESULTS_DIR, 'azc_zone_atomization.json')
with open(output_path, 'w') as f:
    json.dump(results, f, indent=2, default=str)
print(f"\nResults saved to {output_path}")
