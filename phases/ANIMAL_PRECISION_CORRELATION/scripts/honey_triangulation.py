#!/usr/bin/env python3
"""
Honey Triangulation Test
========================

DISCRIMINATION TEST: Honey (Hunig) has a DIFFERENT instruction sequence than chicken:
  [AUX, h_HAZARD, e_ESCAPE]

Key differences from chicken [AUX, e_ESCAPE, FLOW, k_ENERGY]:
  - h_HAZARD instead of FLOW/k_ENERGY
  - Fire degree 3 (not 4) -> REGIME_3
  - Animal product (not animal)

h_HAZARD maps to hazard-related operations (mixing with sand, buried in dung).
This should produce a DIFFERENT PREFIX profile and converge to DIFFERENT tokens.

Methodology Reference: context/SPECULATIVE/recipe_triangulation_methodology.md
"""

import json
import pandas as pd
from pathlib import Path
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

PROJECT_ROOT = Path('C:/git/voynich')

print("=" * 70)
print("HONEY TRIANGULATION TEST")
print("=" * 70)
print()
print("Honey (Hunig) #94 from brunschwig_complete.json")
print()
print("Instruction sequence: [AUX, h_HAZARD, e_ESCAPE]")
print("  - AUX: Mix honey with sand OR seal in glass")
print("  - h_HAZARD: Bury in horse dung 14 days (anaerobic fermentation)")
print("  - e_ESCAPE: Distill gently (clear then yellow water)")
print()
print("This DIFFERS from chicken - discrimination test.")
print("Fire degree 3 -> REGIME_3 (not REGIME_4)")
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
# STEP 1: Recipe Dimensions
# =============================================================================
print("-" * 70)
print("STEP 1: Recipe Dimensions")
print("-" * 70)
print()

recipe = {
    'name': 'Hunig (honey)',
    'fire_degree': 3,
    'regime': 'REGIME_3',
    'instruction_sequence': ['AUX', 'h_HAZARD', 'e_ESCAPE'],
    'material_class': 'animal_product'
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

# Use REGIME_3 for honey (fire degree 3)
regime3_folios = set(regime_data.get('REGIME_3', []))

print(f"REGIME_3 folios: {len(regime3_folios)}")
if len(regime3_folios) == 0:
    print("WARNING: No REGIME_3 folios found. Checking available regimes...")
    for k, v in regime_data.items():
        print(f"  {k}: {len(v)} folios")
    # Fall back to all B folios
    regime3_folios = set(df_b['folio'].unique())
    print(f"Using all B folios: {len(regime3_folios)}")
print()

# Instruction -> PREFIX mapping:
# - e_ESCAPE -> qo (escape/recovery)
# - AUX -> ok, ot (auxiliary)
# - h_HAZARD -> hazard-related prefixes (ch, sh, potentially others)

# Compute PREFIX profiles for REGIME_3 folios
folio_profiles = {}
for folio in regime3_folios:
    folio_tokens = df_b[df_b['folio'] == folio]
    prefix_counts = folio_tokens['prefix'].value_counts().to_dict()
    total = sum(prefix_counts.values())
    if total == 0:
        continue

    qo_ratio = prefix_counts.get('qo', 0) / total  # e_ESCAPE
    ok_ratio = prefix_counts.get('ok', 0) / total  # AUX
    ot_ratio = prefix_counts.get('ot', 0) / total  # AUX
    da_ratio = prefix_counts.get('da', 0) / total  # FLOW (should be LOW for honey)
    ch_ratio = prefix_counts.get('ch', 0) / total  # potential h_HAZARD
    sh_ratio = prefix_counts.get('sh', 0) / total  # potential h_HAZARD

    aux_score = ok_ratio + ot_ratio
    hazard_score = ch_ratio + sh_ratio  # h_HAZARD approximation

    folio_profiles[folio] = {
        'qo_ratio': qo_ratio,
        'aux_score': aux_score,
        'da_ratio': da_ratio,
        'hazard_score': hazard_score,
        'total_tokens': total
    }

if not folio_profiles:
    print("ERROR: No folio profiles computed. Exiting.")
    sys.exit(1)

# Compute averages
avg_qo = sum(p['qo_ratio'] for p in folio_profiles.values()) / len(folio_profiles)
avg_aux = sum(p['aux_score'] for p in folio_profiles.values()) / len(folio_profiles)
avg_da = sum(p['da_ratio'] for p in folio_profiles.values()) / len(folio_profiles)
avg_hazard = sum(p['hazard_score'] for p in folio_profiles.values()) / len(folio_profiles)

print(f"PREFIX averages in target folios:")
print(f"  qo (e_ESCAPE): {avg_qo:.2%}")
print(f"  ok+ot (AUX): {avg_aux:.2%}")
print(f"  da (FLOW): {avg_da:.2%}")
print(f"  ch+sh (h_HAZARD proxy): {avg_hazard:.2%}")
print()

# =============================================================================
# STEP 3: Multi-dimensional Conjunction
# =============================================================================
print("-" * 70)
print("STEP 3: Multi-dimensional Conjunction")
print("-" * 70)
print()

# Honey has: [AUX, h_HAZARD, e_ESCAPE]
# So we need:
# - High qo (e_ESCAPE present)
# - High aux (AUX present)
# - High hazard (h_HAZARD present)
# - LOW da (no FLOW) - key discriminator from chicken!

# Apply conjunction
candidate_folios = set()
for folio, profile in folio_profiles.items():
    if (profile['qo_ratio'] >= avg_qo and
        profile['aux_score'] >= avg_aux and
        profile['da_ratio'] <= avg_da and  # LOW flow - opposite of chicken!
        profile['hazard_score'] >= avg_hazard):
        candidate_folios.add(folio)

print(f"Target folios: {len(folio_profiles)}")
print(f"Folios with qo >= avg: {sum(1 for p in folio_profiles.values() if p['qo_ratio'] >= avg_qo)}")
print(f"Folios with aux >= avg: {sum(1 for p in folio_profiles.values() if p['aux_score'] >= avg_aux)}")
print(f"Folios with da <= avg (LOW FLOW): {sum(1 for p in folio_profiles.values() if p['da_ratio'] <= avg_da)}")
print(f"Folios with hazard >= avg: {sum(1 for p in folio_profiles.values() if p['hazard_score'] >= avg_hazard)}")
print()
print(f"4D CONJUNCTION (qo + aux + LOW_da + hazard): {len(candidate_folios)} folios")
print(f"  Candidate folios: {sorted(candidate_folios)[:20]}{'...' if len(candidate_folios) > 20 else ''}")
print()

# If no candidates, relax constraints
if len(candidate_folios) == 0:
    print("No candidates with strict 4D conjunction. Trying 3D (qo + aux + LOW_da)...")
    for folio, profile in folio_profiles.items():
        if (profile['qo_ratio'] >= avg_qo and
            profile['aux_score'] >= avg_aux and
            profile['da_ratio'] <= avg_da):
            candidate_folios.add(folio)
    print(f"3D CONJUNCTION: {len(candidate_folios)} folios")
    print(f"  Candidate folios: {sorted(candidate_folios)[:20]}")
    print()

if len(candidate_folios) == 0:
    print("Still no candidates. Using top folios by honey-like profile...")
    # Score folios by honey profile
    scored = []
    for folio, p in folio_profiles.items():
        # Honey wants: high escape, high aux, low flow, high hazard
        score = p['qo_ratio'] + p['aux_score'] - p['da_ratio'] + p['hazard_score']
        scored.append((score, folio))
    scored.sort(reverse=True)
    candidate_folios = set(f for _, f in scored[:10])
    print(f"Top 10 by honey profile: {sorted(candidate_folios)}")
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

# Compute PP profiles - honey wants escape + aux + hazard, NOT flow
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
    hazard = (prefix_counts.get('ch', 0) + prefix_counts.get('sh', 0)) / total if total > 0 else 0

    # Honey score: escape + aux + hazard - flow (penalize flow)
    score = escape + aux + hazard - flow
    pp_with_profile[middle] = {
        'escape': escape,
        'aux': aux,
        'flow': flow,
        'hazard': hazard,
        'score': score
    }

# Top PP by honey-like profile
sorted_pp = sorted(pp_with_profile.items(), key=lambda x: -x[1]['score'])[:15]
print("Top PP by honey-like PREFIX profile (escape+aux+hazard-flow):")
for middle, profile in sorted_pp:
    print(f"  {middle}: esc={profile['escape']:.0%}, aux={profile['aux']:.0%}, "
          f"haz={profile['hazard']:.0%}, flow={profile['flow']:.0%} -> score={profile['score']:.2f}")
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

# Require 3+ PP convergence
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
# STEP 6: Extract RI Tokens
# =============================================================================
print("-" * 70)
print("STEP 6: Extract RI Tokens from Converging Records")
print("-" * 70)
print()

# Load material class priors
priors_path = PROJECT_ROOT / 'phases' / 'BRUNSCHWIG_CANDIDATE_LABELING' / 'results' / 'material_class_priors.json'
with open(priors_path, 'r') as f:
    priors_data = json.load(f)
priors_lookup = {item['middle']: item.get('material_class_posterior', {})
                 for item in priors_data['results']}

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

    # For honey (animal_product), check both animal and herb priors
    ri_with_priors = []
    for m in ri_middles:
        if m in priors_lookup:
            p = priors_lookup[m]
            animal = p.get('animal', 0)
            herb = p.get('herb', 0)
            flower = p.get('flower', 0)
            if animal > 0 or herb > 0 or flower > 0:
                ri_with_priors.append((m, animal, herb, flower))

    print(f"RI tokens with material priors: {len(ri_with_priors)}")
    print()

    if ri_with_priors:
        print("*** CANDIDATE TOKENS (by material prior) ***")
        # Sort by animal prior (honey is animal_product)
        for m, animal, herb, flower in sorted(ri_with_priors, key=lambda x: -x[1])[:15]:
            print(f"  {m}: animal={animal:.2f}, herb={herb:.2f}, flower={flower:.2f}")
        print()

# =============================================================================
# STEP 7: PREFIX Profile Matching for Honey Pattern
# =============================================================================
print("-" * 70)
print("STEP 7: PREFIX Profile Matching (Honey Pattern)")
print("-" * 70)
print()

# Honey pattern: escape + aux + hazard, LOW flow
if len(converging_records) > 0:
    print("Checking converging records for honey-like PP profiles...")
    print("(high escape + aux + hazard, LOW flow)")
    print()

    honey_matches = []
    for _, row in converging_records.iterrows():
        pp_in_record = row['middles'] & discriminative_pp
        if len(pp_in_record) < 2:
            continue

        # Aggregate profile of PP tokens in this record
        total_escape = 0
        total_aux = 0
        total_flow = 0
        total_hazard = 0
        count = 0

        for pp in pp_in_record:
            if pp in pp_with_profile:
                total_escape += pp_with_profile[pp]['escape']
                total_aux += pp_with_profile[pp]['aux']
                total_flow += pp_with_profile[pp]['flow']
                total_hazard += pp_with_profile[pp]['hazard']
                count += 1

        if count > 0:
            avg_escape = total_escape / count
            avg_aux = total_aux / count
            avg_flow = total_flow / count
            avg_hazard = total_hazard / count

            # Honey score: escape + aux + hazard present, flow LOW
            has_escape = avg_escape > 0.1
            has_aux = avg_aux > 0.1
            has_hazard = avg_hazard > 0.05  # Lower threshold for hazard
            low_flow = avg_flow < 0.15  # Penalize high flow

            honey_score = has_escape + has_aux + has_hazard + low_flow

            if honey_score >= 3:  # At least 3 of 4 criteria
                ri_in_record = row['middles'] - b_middles
                honey_matches.append({
                    'record': f"{row['folio']}:{row['line']}",
                    'pp_count': len(pp_in_record),
                    'escape': avg_escape,
                    'aux': avg_aux,
                    'flow': avg_flow,
                    'hazard': avg_hazard,
                    'honey_score': honey_score,
                    'ri_tokens': ri_in_record
                })

    honey_matches.sort(key=lambda x: (-x['honey_score'], -x['pp_count']))

    print(f"Records matching honey profile (3+ criteria): {len(honey_matches)}")
    print()

    if honey_matches:
        print("Top honey-profile matches:")
        for match in honey_matches[:15]:
            print(f"  {match['record']}: PP={match['pp_count']}, "
                  f"esc={match['escape']:.0%}, aux={match['aux']:.0%}, "
                  f"haz={match['hazard']:.0%}, flow={match['flow']:.0%}")
            if match['ri_tokens']:
                # Check priors for RI
                ri_with_animal = [m for m in match['ri_tokens']
                                  if m in priors_lookup and priors_lookup[m].get('animal', 0) > 0.2]
                if ri_with_animal:
                    print(f"    -> RI with P(animal)>0.2: {ri_with_animal}")
        print()

# =============================================================================
# STEP 8: Comparison with Chicken
# =============================================================================
print("-" * 70)
print("STEP 8: Discrimination Check vs Chicken")
print("-" * 70)
print()

print("CHICKEN converged to: eoschso (f90r1:6)")
print("HONEY should converge to DIFFERENT token(s)")
print()

# Check if eoschso appears in honey matches
if len(converging_records) > 0:
    eoschso_in_honey = False
    for _, row in converging_records.iterrows():
        if 'eoschso' in row['middles']:
            eoschso_in_honey = True
            print(f"WARNING: eoschso found in honey-converging record {row['folio']}:{row['line']}")

    if not eoschso_in_honey:
        print("GOOD: eoschso NOT in honey-converging records")
        print()

    # Show honey-specific candidates (not eoschso)
    if honey_matches:
        honey_candidates = set()
        for match in honey_matches:
            for ri in match['ri_tokens']:
                if ri != 'eoschso' and ri in priors_lookup:
                    if priors_lookup[ri].get('animal', 0) > 0.2:
                        honey_candidates.add(ri)

        if honey_candidates:
            print(f"HONEY-SPECIFIC CANDIDATES (P(animal)>0.2, not eoschso):")
            for ri in sorted(honey_candidates):
                p = priors_lookup.get(ri, {}).get('animal', 0)
                print(f"  {ri}: P(animal)={p:.2f}")
            print()
            print("*** DISCRIMINATION SUCCESS: Honey candidates differ from Chicken ***")
        else:
            print("No honey-specific animal candidates found.")

# =============================================================================
# SUMMARY
# =============================================================================
print()
print("=" * 70)
print("SUMMARY")
print("=" * 70)
print()
print("Honey instruction pattern: [AUX, h_HAZARD, e_ESCAPE]")
print("  -> Different from chicken [AUX, e_ESCAPE, FLOW, k_ENERGY]")
print()
print(f"Candidate folios from conjunction: {len(candidate_folios)}")
print(f"A records with 3+ PP convergence: {len(converging_records)}")
print()
if 'honey_matches' in dir() and honey_matches:
    print(f"Records matching honey profile: {len(honey_matches)}")
