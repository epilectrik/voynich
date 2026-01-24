#!/usr/bin/env python3
"""
Multi-Dimensional Triangulation
===============================

Enhanced pipeline using ALL available dimensions from constraint system:

B FOLIO CONSTRAINTS:
1. REGIME (fire degree) - C494
2. PREFIX profile (qo/ok/da) - C466, C467, C383
3. Sister ratio (ch vs sh) - C408, C412 (precision vs tolerance)
4. LINK density - C334, C366 (monitoring vs intervention)

A RECORD CONSTRAINTS:
5. PP convergence at record level
6. Material class priors - C499 (applied as FILTER, not just validation)
7. SUFFIX profile - C495 (REGIME breadth)

KEY INSIGHT (C498):
- Only 154 MIDDLEs (25%) truly participate in A→AZC→B pipeline
- 56.6% of A MIDDLEs are registry-internal (RI) - these encode material identity
- Animal materials cluster in RI tokens
"""

import json
import pandas as pd
from pathlib import Path
import sys
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

PROJECT_ROOT = Path('C:/git/voynich')

print("=" * 70)
print("MULTI-DIMENSIONAL TRIANGULATION")
print("=" * 70)
print()

# =============================================================================
# Load data
# =============================================================================
df = pd.read_csv(PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt',
                 sep='\t', low_memory=False)
df = df[df['transcriber'] == 'H']
df_a = df[df['language'] == 'A'].copy()
df_b = df[df['language'] == 'B'].copy()

print(f"Loaded: {len(df_a)} A tokens, {len(df_b)} B tokens")

# =============================================================================
# Morphology
# =============================================================================
PREFIXES = ['ch', 'sh', 'qo', 'da', 'ok', 'ot', 'ol', 'ct', 'pch', 'tch', 'kch', 'dch',
            'fch', 'rch', 'sch', 'lch', 'lk', 'lsh', 'yk', 'ke', 'te', 'se', 'de', 'pe',
            'so', 'ko', 'to', 'do', 'po', 'sa', 'ka', 'ta', 'al', 'ar', 'or']
ALL_PREFIXES = sorted(PREFIXES, key=len, reverse=True)
SUFFIXES = ['odaiin', 'edaiin', 'adaiin', 'daiin', 'kaiin', 'taiin', 'aiin',
            'chey', 'shey', 'key', 'chy', 'shy', 'ky', 'ty', 'dy', 'hy', 'ly', 'ry',
            'edy', 'eey', 'ey', 'iin', 'ain', 'oin', 'ein', 'in', 'an', 'on', 'en',
            'ol', 'or', 'ar', 'al', 'y', 'l', 'r', 'm', 'n', 's', 'g']

def extract_morphology(token):
    if pd.isna(token):
        return None, None, None
    token = str(token)
    prefix = None
    middle = None
    suffix = None

    # Extract prefix
    for p in ALL_PREFIXES:
        if token.startswith(p):
            prefix = p
            token = token[len(p):]
            break

    if prefix is None:
        return None, None, None

    # Extract suffix
    for s in sorted(SUFFIXES, key=len, reverse=True):
        if token.endswith(s):
            suffix = s
            token = token[:-len(s)]
            break

    middle = token or '_EMPTY_'
    return prefix, middle, suffix

# Apply to both datasets
df_a[['prefix', 'middle', 'suffix']] = df_a['word'].apply(
    lambda x: pd.Series(extract_morphology(x))
)
df_b[['prefix', 'middle', 'suffix']] = df_b['word'].apply(
    lambda x: pd.Series(extract_morphology(x))
)

# =============================================================================
# Compute vocabulary sets
# =============================================================================
a_middles = set(df_a['middle'].dropna().unique())
b_middles = set(df_b['middle'].dropna().unique())
shared_middles = a_middles & b_middles
ri_middles = a_middles - b_middles  # Registry-Internal (C498)

print(f"A middles: {len(a_middles)}")
print(f"B middles: {len(b_middles)}")
print(f"Shared (PP): {len(shared_middles)} ({len(shared_middles)/len(a_middles)*100:.1f}% of A)")
print(f"RI (A-only): {len(ri_middles)} ({len(ri_middles)/len(a_middles)*100:.1f}% of A)")
print()

# =============================================================================
# Load material class priors
# =============================================================================
priors_path = PROJECT_ROOT / 'phases' / 'BRUNSCHWIG_CANDIDATE_LABELING' / 'results' / 'material_class_priors.json'
with open(priors_path, 'r') as f:
    priors_data = json.load(f)
priors_lookup = {item['middle']: item.get('material_class_posterior', {})
                 for item in priors_data['results']}

# =============================================================================
# Load regime data
# =============================================================================
regime_path = PROJECT_ROOT / 'results' / 'regime_folio_mapping.json'
with open(regime_path, 'r') as f:
    regime_data = json.load(f)

# =============================================================================
# Define multi-dimensional profile computation
# =============================================================================
def compute_folio_profile(folio, df_section):
    """Compute full multi-dimensional profile for a folio."""
    folio_tokens = df_section[df_section['folio'] == folio]
    if len(folio_tokens) == 0:
        return None

    prefix_counts = folio_tokens['prefix'].value_counts().to_dict()
    suffix_counts = folio_tokens['suffix'].value_counts().to_dict()
    total = sum(prefix_counts.values())

    if total == 0:
        return None

    # PREFIX dimensions (C466, C467, C383)
    qo_ratio = prefix_counts.get('qo', 0) / total  # e_ESCAPE
    ok_ratio = prefix_counts.get('ok', 0) / total  # AUX
    ot_ratio = prefix_counts.get('ot', 0) / total  # AUX
    da_ratio = prefix_counts.get('da', 0) / total  # FLOW
    sa_ratio = prefix_counts.get('sa', 0) / total  # LINK-attracted
    ol_ratio = prefix_counts.get('ol', 0) / total  # LINK marker

    # Sister ratio (C408, C412) - precision vs tolerance
    ch_count = prefix_counts.get('ch', 0)
    sh_count = prefix_counts.get('sh', 0)
    sister_total = ch_count + sh_count
    ch_preference = ch_count / sister_total if sister_total > 0 else 0.5

    # LINK density approximation (C334, C366)
    # LINK = ol and related forms, plus da/sa attraction
    link_density = ol_ratio + (da_ratio + sa_ratio) * 0.5

    # SUFFIX dimensions (C495)
    suffix_total = sum(suffix_counts.values())
    r_ratio = suffix_counts.get('r', 0) / suffix_total if suffix_total > 0 else 0
    ar_ratio = suffix_counts.get('ar', 0) / suffix_total if suffix_total > 0 else 0
    or_ratio = suffix_counts.get('or', 0) / suffix_total if suffix_total > 0 else 0
    universal_suffix = r_ratio  # -r = universal REGIME
    restricted_suffix = ar_ratio + or_ratio  # -ar/-or = single-REGIME

    return {
        'total_tokens': total,
        # PREFIX
        'qo_ratio': qo_ratio,
        'ok_ratio': ok_ratio,
        'ot_ratio': ot_ratio,
        'aux_ratio': ok_ratio + ot_ratio,
        'da_ratio': da_ratio,
        'sa_ratio': sa_ratio,
        # Sister (C408)
        'ch_preference': ch_preference,
        # LINK (C334)
        'link_density': link_density,
        # SUFFIX (C495)
        'universal_suffix': universal_suffix,
        'restricted_suffix': restricted_suffix
    }

# =============================================================================
# Compute profiles for all B folios
# =============================================================================
print("-" * 70)
print("Computing multi-dimensional profiles for all B folios...")
print("-" * 70)
print()

b_folios = df_b['folio'].unique()
folio_profiles = {}
for folio in b_folios:
    profile = compute_folio_profile(folio, df_b)
    if profile:
        folio_profiles[folio] = profile

print(f"Computed profiles for {len(folio_profiles)} B folios")
print()

# Compute averages for each dimension
dim_avgs = {}
for dim in ['qo_ratio', 'aux_ratio', 'da_ratio', 'ch_preference', 'link_density',
            'universal_suffix', 'restricted_suffix']:
    values = [p[dim] for p in folio_profiles.values()]
    dim_avgs[dim] = sum(values) / len(values)

print("Dimension averages across B folios:")
for dim, avg in dim_avgs.items():
    print(f"  {dim}: {avg:.2%}")
print()

# =============================================================================
# Define recipe and run multi-dimensional conjunction
# =============================================================================
def run_triangulation(recipe):
    """Run full multi-dimensional triangulation for a recipe."""
    print("=" * 70)
    print(f"TRIANGULATING: {recipe['name']}")
    print("=" * 70)
    print()
    print(f"Fire degree: {recipe['fire_degree']} -> {recipe['regime']}")
    print(f"Instruction sequence: {recipe['instruction_sequence']}")
    print(f"Material class: {recipe['material_class']}")
    print()

    # ==========================================================================
    # STEP 1: REGIME filter
    # ==========================================================================
    regime_folios = set(regime_data.get(recipe['regime'], []))
    print(f"STEP 1: REGIME filter -> {len(regime_folios)} folios")

    if len(regime_folios) == 0:
        print("WARNING: No folios in target regime. Using all B folios.")
        regime_folios = set(folio_profiles.keys())

    # ==========================================================================
    # STEP 2: Multi-dimensional PREFIX conjunction
    # ==========================================================================
    seq = recipe['instruction_sequence']

    # Build constraints based on instruction sequence
    constraints = []

    if 'e_ESCAPE' in seq:
        constraints.append(('qo_ratio', '>=', dim_avgs['qo_ratio'], 'e_ESCAPE'))
    if 'AUX' in seq:
        constraints.append(('aux_ratio', '>=', dim_avgs['aux_ratio'], 'AUX'))
    if 'FLOW' in seq:
        constraints.append(('da_ratio', '>=', dim_avgs['da_ratio'], 'FLOW'))
    else:
        constraints.append(('da_ratio', '<=', dim_avgs['da_ratio'], 'NO_FLOW'))

    # Add precision/tolerance constraint based on material class (C408)
    if recipe['material_class'] in ['animal', 'animal_product']:
        # Animals typically need PRECISION mode (high ch preference)
        constraints.append(('ch_preference', '>=', 0.5, 'PRECISION_MODE'))

    # Add LINK constraint if LINK in sequence
    if 'LINK' in seq:
        constraints.append(('link_density', '>=', dim_avgs['link_density'], 'LINK'))

    print(f"\nSTEP 2: Multi-dimensional constraints:")
    for dim, op, thresh, label in constraints:
        print(f"  {label}: {dim} {op} {thresh:.2%}")

    # Apply conjunction
    candidate_folios = set()
    for folio in regime_folios:
        if folio not in folio_profiles:
            continue
        profile = folio_profiles[folio]
        passes = True
        for dim, op, thresh, label in constraints:
            val = profile[dim]
            if op == '>=' and val < thresh:
                passes = False
                break
            elif op == '<=' and val > thresh:
                passes = False
                break
        if passes:
            candidate_folios.add(folio)

    print(f"\n  CONJUNCTION result: {len(candidate_folios)} folios")
    print(f"  Folios: {sorted(candidate_folios)}")

    # Calculate synergy ratio
    if len(regime_folios) > 0:
        individual_passes = []
        for dim, op, thresh, label in constraints:
            count = sum(1 for f in regime_folios if f in folio_profiles and
                       (folio_profiles[f][dim] >= thresh if op == '>=' else folio_profiles[f][dim] <= thresh))
            individual_passes.append(count / len(regime_folios))
        expected_prob = 1.0
        for p in individual_passes:
            expected_prob *= p
        expected = expected_prob * len(regime_folios)
        ratio = len(candidate_folios) / expected if expected > 0 else float('inf')
        print(f"  Expected (independent): {expected:.1f}, Actual: {len(candidate_folios)}, Ratio: {ratio:.2f}")
    print()

    if len(candidate_folios) == 0:
        print("WARNING: No candidates. Relaxing constraints...")
        # Fall back to just REGIME + primary instruction constraint
        for folio in regime_folios:
            if folio in folio_profiles:
                candidate_folios.add(folio)
        print(f"  Using all REGIME folios: {len(candidate_folios)}")

    # ==========================================================================
    # STEP 3: Extract PP vocabulary
    # ==========================================================================
    candidate_middles = set()
    for folio in candidate_folios:
        folio_tokens = df_b[df_b['folio'] == folio]
        candidate_middles.update(folio_tokens['middle'].dropna().unique())

    infrastructure = {'a', 'o', 'e', 'ee', 'eo', 'ai', 'oi', 'ei', '_EMPTY_'}
    discriminative_pp = (candidate_middles & shared_middles) - infrastructure

    print(f"STEP 3: PP vocabulary -> {len(discriminative_pp)} discriminative PP tokens")

    # ==========================================================================
    # STEP 4: Find A records with PP convergence + material class filter (C499)
    # ==========================================================================
    print(f"\nSTEP 4: A record filtering (PP convergence + material class prior)")

    # Build A entries
    a_entries = df_a.groupby(['folio', 'line_number']).apply(
        lambda g: {
            'middles': set(g['middle'].dropna()),
            'prefixes': Counter(g['prefix'].dropna()),
            'suffixes': Counter(g['suffix'].dropna())
        }
    ).reset_index()
    a_entries.columns = ['folio', 'line', 'data']

    # Compute PP overlap
    a_entries['pp_overlap'] = a_entries['data'].apply(
        lambda x: len(x['middles'] & discriminative_pp)
    )

    # Compute RI tokens in each record
    a_entries['ri_tokens'] = a_entries['data'].apply(
        lambda x: x['middles'] & ri_middles
    )

    # Apply material class prior as FILTER (not just validation)
    # C499: Use P(material_class | token) to filter records
    target_class = recipe['material_class']
    if target_class == 'animal_product':
        target_class = 'animal'  # Use animal prior for animal products

    def has_class_prior(ri_set, target, threshold=0.2):
        """Check if any RI token has prior for target class."""
        for ri in ri_set:
            if ri in priors_lookup:
                if priors_lookup[ri].get(target, 0) >= threshold:
                    return True
        return False

    a_entries['has_class_match'] = a_entries['ri_tokens'].apply(
        lambda x: has_class_prior(x, target_class, 0.2)
    )

    # Filter: 3+ PP AND material class match
    filtered = a_entries[
        (a_entries['pp_overlap'] >= 3) &
        (a_entries['has_class_match'])
    ].copy()
    filtered = filtered.sort_values('pp_overlap', ascending=False)

    print(f"  Records with 3+ PP: {len(a_entries[a_entries['pp_overlap'] >= 3])}")
    print(f"  Records with class match (P({target_class})>=0.2): {len(a_entries[a_entries['has_class_match']])}")
    print(f"  CONJUNCTION (3+ PP AND class match): {len(filtered)}")
    print()

    if len(filtered) > 0:
        print("Top matching records:")
        for _, row in filtered.head(10).iterrows():
            pp = row['data']['middles'] & discriminative_pp
            ri = row['ri_tokens']
            ri_with_prior = [m for m in ri if m in priors_lookup and
                            priors_lookup[m].get(target_class, 0) >= 0.2]
            print(f"  {row['folio']}:{row['line']} - PP={row['pp_overlap']}")
            print(f"    RI with P({target_class})>=0.2: {ri_with_prior}")

    # ==========================================================================
    # STEP 5: Final candidate extraction
    # ==========================================================================
    print()
    print("-" * 70)
    print("FINAL CANDIDATES")
    print("-" * 70)

    if len(filtered) > 0:
        all_ri = set()
        for _, row in filtered.iterrows():
            all_ri.update(row['ri_tokens'])

        candidates = [(m, priors_lookup.get(m, {}).get(target_class, 0))
                     for m in all_ri if m in priors_lookup and
                     priors_lookup[m].get(target_class, 0) >= 0.3]
        candidates.sort(key=lambda x: -x[1])

        print(f"\nRI tokens with P({target_class})>=0.3:")
        for token, prob in candidates[:10]:
            print(f"  {token}: P({target_class})={prob:.2f}")

        return candidates
    else:
        print("No candidates found.")
        return []


# =============================================================================
# Run triangulations
# =============================================================================

# Recipe definitions
recipes = [
    {
        'name': 'Chicken (Hennen)',
        'fire_degree': 4,
        'regime': 'REGIME_4',
        'instruction_sequence': ['AUX', 'e_ESCAPE', 'FLOW', 'k_ENERGY'],
        'material_class': 'animal'
    },
    {
        'name': 'Honey (Hunig)',
        'fire_degree': 3,
        'regime': 'REGIME_3',
        'instruction_sequence': ['AUX', 'h_HAZARD', 'e_ESCAPE'],
        'material_class': 'animal_product'
    },
    {
        'name': 'Nettle (Nessel)',
        'fire_degree': 2,
        'regime': 'REGIME_2',
        'instruction_sequence': ['AUX', 'h_HAZARD', 'e_ESCAPE'],
        'material_class': 'herb'
    }
]

results = {}
for recipe in recipes:
    candidates = run_triangulation(recipe)
    results[recipe['name']] = candidates
    print()
    print()

# =============================================================================
# Comparison
# =============================================================================
print("=" * 70)
print("DISCRIMINATION ANALYSIS")
print("=" * 70)
print()

chicken_tokens = set(t for t, p in results.get('Chicken (Hennen)', []))
honey_tokens = set(t for t, p in results.get('Honey (Hunig)', []))
nettle_tokens = set(t for t, p in results.get('Nettle (Nessel)', []))

print("Chicken candidates:", chicken_tokens)
print("Honey candidates:", honey_tokens)
print("Nettle candidates:", nettle_tokens)
print()

overlap_ch_ho = chicken_tokens & honey_tokens
overlap_ch_ne = chicken_tokens & nettle_tokens
overlap_ho_ne = honey_tokens & nettle_tokens

print(f"Chicken ∩ Honey: {overlap_ch_ho}")
print(f"Chicken ∩ Nettle: {overlap_ch_ne}")
print(f"Honey ∩ Nettle: {overlap_ho_ne}")
print()

unique_chicken = chicken_tokens - honey_tokens - nettle_tokens
unique_honey = honey_tokens - chicken_tokens - nettle_tokens
unique_nettle = nettle_tokens - chicken_tokens - honey_tokens

print(f"UNIQUE to Chicken: {unique_chicken}")
print(f"UNIQUE to Honey: {unique_honey}")
print(f"UNIQUE to Nettle: {unique_nettle}")
