#!/usr/bin/env python3
"""
Capon Triangulation Test
========================

VALIDATION TEST: Capon (Kappen) has the SAME instruction sequence as Chicken:
  [AUX, e_ESCAPE, FLOW, k_ENERGY]

If our methodology works, capon should either:
1. Converge to the same token as chicken (eoschso) - indicating shared registry entry
2. Converge to a closely related token - indicating they're distinguished

This tests the discriminative power of the methodology.

Methodology Reference: context/SPECULATIVE/recipe_triangulation_methodology.md
"""

import json
import pandas as pd
from pathlib import Path
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

PROJECT_ROOT = Path('C:/git/voynich')

print("=" * 70)
print("CAPON TRIANGULATION TEST")
print("=" * 70)
print()
print("Capon (Kappen) #125 from brunschwig_complete.json")
print()
print("Instruction sequence: [AUX, e_ESCAPE, FLOW, k_ENERGY]")
print("  - AUX: prepare (strangle, pluck WITHOUT scalding, remove fat)")
print("  - e_ESCAPE: distill per alembicum in balneum mariae")
print("  - FLOW: collect distillate")
print("  - k_ENERGY: redistill in balneum mariae")
print()
print("This is IDENTICAL to chicken (hennen) - validation test.")
print("=" * 70)
print()

# =============================================================================
# Load transcript data
# =============================================================================
df = pd.read_csv(PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt',
                 sep='\t', low_memory=False)
df = df[df['transcriber'] == 'H']  # PRIMARY track only
df_a = df[df['language'] == 'A'].copy()
df_b = df[df['language'] == 'B'].copy()

print(f"Loaded: {len(df_a)} A tokens, {len(df_b)} B tokens")

# =============================================================================
# Morphology extraction
# =============================================================================
PREFIXES = ['ch', 'sh', 'qo', 'da', 'ok', 'ot', 'ol', 'ct', 'pch', 'tch', 'kch', 'dch',
            'fch', 'rch', 'sch', 'lch', 'lk', 'lsh', 'yk', 'ke', 'te', 'se', 'de', 'pe',
            'so', 'ko', 'to', 'do', 'po', 'sa', 'ka', 'ta', 'al', 'ar', 'or']
ALL_PREFIXES = sorted(PREFIXES, key=len, reverse=True)
SUFFIXES = ['odaiin', 'edaiin', 'adaiin', 'daiin', 'kaiin', 'taiin', 'aiin',
            'chey', 'shey', 'key', 'chy', 'shy', 'ky', 'ty', 'dy', 'hy', 'ly', 'ry',
            'edy', 'eey', 'ey', 'iin', 'ain', 'oin', 'ein', 'in', 'an', 'on', 'en',
            'ol', 'or', 'ar', 'al', 'y', 'l', 'r', 'm', 'n', 's', 'g']

def extract_middle(token):
    if pd.isna(token): return None
    token = str(token)
    for p in ALL_PREFIXES:
        if token.startswith(p):
            remainder = token[len(p):]
            for s in sorted(SUFFIXES, key=len, reverse=True):
                if remainder.endswith(s):
                    return remainder[:-len(s)] or '_EMPTY_'
            return remainder or '_EMPTY_'
    return None

def extract_prefix(token):
    if pd.isna(token): return None
    token = str(token)
    for p in ALL_PREFIXES:
        if token.startswith(p):
            return p
    return None

df_a['middle'] = df_a['word'].apply(extract_middle)
df_b['middle'] = df_b['word'].apply(extract_middle)
df_b['prefix'] = df_b['word'].apply(extract_prefix)

# Get vocabulary sets
a_middles = set(df_a['middle'].dropna().unique())
b_middles = set(df_b['middle'].dropna().unique())
shared_middles = a_middles & b_middles

print(f"A middles: {len(a_middles)}, B middles: {len(b_middles)}, Shared: {len(shared_middles)}")
print()

# =============================================================================
# STEP 1: Extract Recipe Dimensions
# =============================================================================
print("-" * 70)
print("STEP 1: Recipe Dimensions")
print("-" * 70)
print()

recipe = {
    'name': 'Kappen (capon)',
    'fire_degree': 4,
    'regime': 'REGIME_4',
    'instruction_sequence': ['AUX', 'e_ESCAPE', 'FLOW', 'k_ENERGY'],
    'material_class': 'animal'
}

print(f"Material: {recipe['name']}")
print(f"Fire degree: {recipe['fire_degree']} -> {recipe['regime']}")
print(f"Instruction sequence: {recipe['instruction_sequence']}")
print(f"Material class: {recipe['material_class']}")
print()

# =============================================================================
# STEP 2: Map to B Folio Constraints
# =============================================================================
print("-" * 70)
print("STEP 2: Map to B Folio Constraints")
print("-" * 70)
print()

# Load regime data
regime_path = PROJECT_ROOT / 'results' / 'regime_folio_mapping.json'
with open(regime_path, 'r') as f:
    regime_data = json.load(f)
regime4_folios = set(regime_data['REGIME_4'])

print(f"REGIME_4 folios: {len(regime4_folios)}")
print()

# Instruction -> PREFIX mapping:
# - e_ESCAPE -> qo (escape/recovery)
# - AUX -> ok, ot (auxiliary)
# - FLOW -> da (direct action)
# - k_ENERGY -> energy operations

# Compute PREFIX profiles for all REGIME_4 folios
folio_profiles = {}
for folio in regime4_folios:
    folio_tokens = df_b[df_b['folio'] == folio]
    prefix_counts = folio_tokens['prefix'].value_counts().to_dict()
    total = sum(prefix_counts.values())
    if total == 0:
        continue

    qo_ratio = prefix_counts.get('qo', 0) / total  # e_ESCAPE
    ok_ratio = prefix_counts.get('ok', 0) / total  # AUX
    ot_ratio = prefix_counts.get('ot', 0) / total  # AUX
    da_ratio = prefix_counts.get('da', 0) / total  # FLOW
    ke_ratio = prefix_counts.get('ke', 0) / total  # k_ENERGY (approximation)

    aux_score = ok_ratio + ot_ratio

    folio_profiles[folio] = {
        'qo_ratio': qo_ratio,
        'aux_score': aux_score,
        'da_ratio': da_ratio,
        'ke_ratio': ke_ratio,
        'total_tokens': total
    }

# Compute averages
avg_qo = sum(p['qo_ratio'] for p in folio_profiles.values()) / len(folio_profiles)
avg_aux = sum(p['aux_score'] for p in folio_profiles.values()) / len(folio_profiles)
avg_da = sum(p['da_ratio'] for p in folio_profiles.values()) / len(folio_profiles)

print(f"REGIME_4 PREFIX averages:")
print(f"  qo (e_ESCAPE): {avg_qo:.2%}")
print(f"  ok+ot (AUX): {avg_aux:.2%}")
print(f"  da (FLOW): {avg_da:.2%}")
print()

# =============================================================================
# STEP 3: Multi-dimensional Conjunction
# =============================================================================
print("-" * 70)
print("STEP 3: Multi-dimensional Conjunction")
print("-" * 70)
print()

# Capon has: [AUX, e_ESCAPE, FLOW, k_ENERGY]
# So we need:
# - High qo (e_ESCAPE present)
# - High aux (AUX present)
# - High da (FLOW present)

# Apply conjunction
candidate_folios = set()
for folio, profile in folio_profiles.items():
    if (profile['qo_ratio'] >= avg_qo and
        profile['aux_score'] >= avg_aux and
        profile['da_ratio'] >= avg_da):  # Include FLOW!
        candidate_folios.add(folio)

print(f"Folios with REGIME_4: {len(regime4_folios)}")
print(f"Folios with qo >= avg: {sum(1 for p in folio_profiles.values() if p['qo_ratio'] >= avg_qo)}")
print(f"Folios with aux >= avg: {sum(1 for p in folio_profiles.values() if p['aux_score'] >= avg_aux)}")
print(f"Folios with da >= avg: {sum(1 for p in folio_profiles.values() if p['da_ratio'] >= avg_da)}")
print()
print(f"4D CONJUNCTION (REGIME_4 + qo + aux + da): {len(candidate_folios)} folios")
print(f"  Candidate folios: {sorted(candidate_folios)}")
print()

# Expected vs actual
independent_prob = (len([p for p in folio_profiles.values() if p['qo_ratio'] >= avg_qo]) / len(folio_profiles) *
                    len([p for p in folio_profiles.values() if p['aux_score'] >= avg_aux]) / len(folio_profiles) *
                    len([p for p in folio_profiles.values() if p['da_ratio'] >= avg_da]) / len(folio_profiles))
expected = independent_prob * len(regime4_folios)
ratio = len(candidate_folios) / expected if expected > 0 else float('inf')
print(f"Expected (if independent): {expected:.1f}")
print(f"Actual/Expected ratio: {ratio:.2f} (<1 = synergistic narrowing)")
print()

# =============================================================================
# STEP 4: Extract PP Vocabulary
# =============================================================================
print("-" * 70)
print("STEP 4: Extract PP Vocabulary from Candidate Folios")
print("-" * 70)
print()

# Get MIDDLEs from candidate folios
candidate_middles = set()
for folio in candidate_folios:
    folio_tokens = df_b[df_b['folio'] == folio]
    candidate_middles.update(folio_tokens['middle'].dropna().unique())

# PP = shared middles (in both A and B)
infrastructure = {'a', 'o', 'e', 'ee', 'eo', 'ai', 'oi', 'ei', '_EMPTY_'}
discriminative_pp = (candidate_middles & shared_middles) - infrastructure

print(f"MIDDLEs in candidate folios: {len(candidate_middles)}")
print(f"Shared with A: {len(candidate_middles & shared_middles)}")
print(f"Discriminative PP (minus infrastructure): {len(discriminative_pp)}")
print()

# Also compute which PP have the right PREFIX profile
# Capon pattern wants: escape (qo) + aux (ok/ot) + flow (da)
pp_with_profile = {}
for middle in discriminative_pp:
    b_tokens = df_b[df_b['middle'] == middle]
    if len(b_tokens) == 0:
        continue
    prefix_counts = b_tokens['prefix'].value_counts().to_dict()
    total = sum(prefix_counts.values())

    escape = prefix_counts.get('qo', 0) / total if total > 0 else 0
    aux = (prefix_counts.get('ok', 0) + prefix_counts.get('ot', 0)) / total if total > 0 else 0
    flow = prefix_counts.get('da', 0) / total if total > 0 else 0

    # Score: capon wants escape + aux + flow
    score = escape + aux + flow
    pp_with_profile[middle] = {
        'escape': escape,
        'aux': aux,
        'flow': flow,
        'score': score
    }

# Top PP by capon-like profile
sorted_pp = sorted(pp_with_profile.items(), key=lambda x: -x[1]['score'])[:15]
print("Top PP by capon-like PREFIX profile (escape+aux+flow):")
for middle, profile in sorted_pp:
    print(f"  {middle}: escape={profile['escape']:.0%}, aux={profile['aux']:.0%}, flow={profile['flow']:.0%} -> score={profile['score']:.2f}")
print()

# =============================================================================
# STEP 5: Find A RECORDS with Multiple PP Convergence
# =============================================================================
print("-" * 70)
print("STEP 5: Find A Records with Multiple PP Convergence")
print("-" * 70)
print()

# Build A entries at RECORD level (folio:line)
a_entries = df_a.groupby(['folio', 'line_number'])['middle'].apply(
    lambda x: set(x.dropna())
).reset_index()
a_entries.columns = ['folio', 'line', 'middles']

# Count PP overlap
a_entries['pp_overlap'] = a_entries['middles'].apply(
    lambda x: len(x & discriminative_pp) if x else 0
)

# Require 3+ PP convergence (methodology threshold)
converging_records = a_entries[a_entries['pp_overlap'] >= 3].copy()
converging_records = converging_records.sort_values('pp_overlap', ascending=False)

print(f"Total A records: {len(a_entries)}")
print(f"Records with 3+ PP convergence: {len(converging_records)}")
print()

if len(converging_records) > 0:
    print("Top converging A records:")
    for _, row in converging_records.head(15).iterrows():
        overlap = row['middles'] & discriminative_pp
        print(f"  {row['folio']}:{row['line']} - PP overlap={row['pp_overlap']}: {overlap}")
    print()

# =============================================================================
# STEP 6: Extract RI Tokens from Converging Records
# =============================================================================
print("-" * 70)
print("STEP 6: Extract RI Tokens from Converging Records")
print("-" * 70)
print()

if len(converging_records) > 0:
    # Collect all MIDDLEs from converging records
    converging_middles = set()
    for _, row in converging_records.iterrows():
        if row['middles']:
            converging_middles.update(row['middles'])

    # RI = in A but NOT in B
    ri_middles = converging_middles - b_middles

    print(f"Total MIDDLEs in converging records: {len(converging_middles)}")
    print(f"RI tokens (not in B): {len(ri_middles)}")
    print()

    # Load material class priors
    priors_path = PROJECT_ROOT / 'phases' / 'BRUNSCHWIG_CANDIDATE_LABELING' / 'results' / 'material_class_priors.json'
    with open(priors_path, 'r') as f:
        priors_data = json.load(f)
    priors_lookup = {item['middle']: item.get('material_class_posterior', {})
                     for item in priors_data['results']}

    # Filter to RI with animal prior > 0
    ri_animal = [(m, priors_lookup[m].get('animal', 0)) for m in ri_middles
                 if m in priors_lookup and priors_lookup[m].get('animal', 0) > 0]

    print(f"RI tokens with P(animal) > 0: {len(ri_animal)}")
    print()

    if ri_animal:
        print("*** CANDIDATE ANIMAL TOKENS (by P(animal)) ***")
        for m, p in sorted(ri_animal, key=lambda x: -x[1]):
            print(f"  {m}: P(animal) = {p:.2f}")
        print()

        high_animal = [(m, p) for m, p in ri_animal if p >= 0.5]
        if high_animal:
            print(f"High-confidence (P>=0.5): {[m for m, p in high_animal]}")
            print()

# =============================================================================
# STEP 7: Match PREFIX Profiles to Instruction Patterns
# =============================================================================
print("-" * 70)
print("STEP 7: PREFIX Profile Matching")
print("-" * 70)
print()

# For capon with [AUX, e_ESCAPE, FLOW, k_ENERGY], we expect:
# - High escape (qo) presence
# - High aux (ok/ot) presence
# - High flow (da) presence

if len(converging_records) > 0:
    # For each converging record, check if its PP tokens match the expected profile
    print("Checking converging records for capon-like PP profiles...")
    print()

    capon_matches = []
    for _, row in converging_records.iterrows():
        pp_in_record = row['middles'] & discriminative_pp
        if len(pp_in_record) < 2:
            continue

        # Aggregate profile of PP tokens in this record
        total_escape = 0
        total_aux = 0
        total_flow = 0
        count = 0

        for pp in pp_in_record:
            if pp in pp_with_profile:
                total_escape += pp_with_profile[pp]['escape']
                total_aux += pp_with_profile[pp]['aux']
                total_flow += pp_with_profile[pp]['flow']
                count += 1

        if count > 0:
            avg_escape = total_escape / count
            avg_aux = total_aux / count
            avg_flow = total_flow / count

            # Capon score: requires escape + aux + flow
            capon_score = (avg_escape > 0.1) + (avg_aux > 0.1) + (avg_flow > 0.1)

            if capon_score >= 2:  # At least 2 of 3 profile components
                ri_in_record = row['middles'] - b_middles
                capon_matches.append({
                    'record': f"{row['folio']}:{row['line']}",
                    'pp_count': len(pp_in_record),
                    'escape': avg_escape,
                    'aux': avg_aux,
                    'flow': avg_flow,
                    'capon_score': capon_score,
                    'ri_tokens': ri_in_record
                })

    capon_matches.sort(key=lambda x: (-x['capon_score'], -x['pp_count']))

    print(f"Records matching capon profile (2+ of escape/aux/flow): {len(capon_matches)}")
    print()

    if capon_matches:
        print("Top profile matches:")
        for match in capon_matches[:10]:
            print(f"  {match['record']}: PP={match['pp_count']}, "
                  f"escape={match['escape']:.0%}, aux={match['aux']:.0%}, flow={match['flow']:.0%}")
            if match['ri_tokens']:
                # Check animal priors for RI
                ri_with_animal = [m for m in match['ri_tokens']
                                  if m in priors_lookup and priors_lookup[m].get('animal', 0) > 0.3]
                if ri_with_animal:
                    print(f"    -> RI with P(animal)>0.3: {ri_with_animal}")
        print()

# =============================================================================
# STEP 8: Compare with Chicken Results
# =============================================================================
print("-" * 70)
print("STEP 8: Comparison with Chicken (eoschso)")
print("-" * 70)
print()

# Known chicken result from validated triangulation
print("VALIDATED: Chicken -> eoschso (f90r1:6)")
print()

# Check if eoschso appears in our converging records
if len(converging_records) > 0:
    eoschso_found = False
    for _, row in converging_records.iterrows():
        if 'eoschso' in row['middles']:
            eoschso_found = True
            print(f"*** eoschso FOUND in {row['folio']}:{row['line']} ***")
            print(f"    PP overlap: {row['pp_overlap']}")
            print(f"    MIDDLEs: {row['middles']}")
            print()

    if not eoschso_found:
        print("eoschso NOT found in converging records.")
        print()

        # Check if f90r1 line 6 is in our data
        f90r1_records = a_entries[(a_entries['folio'] == 'f90r1')]
        if len(f90r1_records) > 0:
            print(f"f90r1 records in A: {len(f90r1_records)}")
            for _, row in f90r1_records.iterrows():
                has_eoschso = 'eoschso' in row['middles'] if row['middles'] else False
                print(f"  f90r1:{row['line']} - PP overlap={row['pp_overlap']}, has_eoschso={has_eoschso}")
            print()

# =============================================================================
# SUMMARY
# =============================================================================
print("=" * 70)
print("SUMMARY")
print("=" * 70)
print()
print("Capon instruction pattern: [AUX, e_ESCAPE, FLOW, k_ENERGY]")
print("  -> Same as chicken")
print()
print(f"4D conjunction narrowed to: {len(candidate_folios)} folios")
print(f"A records with 3+ PP convergence: {len(converging_records)}")
print()

if len(converging_records) > 0 and capon_matches:
    print("Capon-profile matching records found candidate tokens.")
    print()

    # Collect all RI with animal priors from matches
    all_candidate_ri = set()
    for match in capon_matches:
        for ri in match['ri_tokens']:
            if ri in priors_lookup and priors_lookup[ri].get('animal', 0) > 0.3:
                all_candidate_ri.add(ri)

    if all_candidate_ri:
        print(f"CANDIDATE CAPON TOKENS (P(animal)>0.3 in profile-matching records):")
        for ri in sorted(all_candidate_ri):
            p = priors_lookup.get(ri, {}).get('animal', 0)
            is_chicken = " <- CHICKEN (eoschso)" if ri == 'eoschso' else ""
            print(f"  {ri}: P(animal)={p:.2f}{is_chicken}")
        print()

        if 'eoschso' in all_candidate_ri:
            print("*** VALIDATION SUCCESS: Capon converges to same token as Chicken (eoschso) ***")
            print("This suggests chicken/capon may share a registry entry, OR")
            print("the methodology cannot distinguish between similar procedures.")
        else:
            print("Capon candidates differ from chicken (eoschso).")
            print("This suggests they may have distinct registry entries.")
