#!/usr/bin/env python3
"""
Reverse Brunschwig Triangulation: Earthworm (Regen würm)

Recipe #159 has UNIQUE instruction sequence among all 203 recipes:
[AUX, FLOW, h_HAZARD, LINK, e_ESCAPE]

Procedure from OCR:
1. Soak onions overnight in water (LINK)
2. Pour water on manured earth (h_HAZARD + FLOW)
3. Worms emerge and are collected (FLOW)
4. Clean worms in tree moss (AUX)
5. Distill (e_ESCAPE)

Dimensions:
- fire_degree: 4 (animal)
- material_class: animal
- instruction_sequence: [AUX, FLOW, h_HAZARD, LINK, e_ESCAPE]

Expected PREFIX profile:
- High qo (e_ESCAPE present)
- High ok/ot (AUX present)
- High da (FLOW present)
- LINK operations (monitoring)
"""

import json
import sys
from pathlib import Path
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

PROJECT_ROOT = Path('C:/git/voynich')

# Load transcript
import pandas as pd
df = pd.read_csv(PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt',
                 sep='\t', low_memory=False)
df = df[df['transcriber'] == 'H']  # H track only

# Load regime mapping
with open(PROJECT_ROOT / 'results' / 'regime_folio_mapping.json', 'r') as f:
    regime_data = json.load(f)

# Earthworm parameters
RECIPE = {
    'id': 159,
    'name_german': 'Regen würm',
    'name_english': 'earthworm',
    'fire_degree': 4,
    'material_class': 'animal',
    'instruction_sequence': ['AUX', 'FLOW', 'h_HAZARD', 'LINK', 'e_ESCAPE']
}

print("=" * 70)
print("EARTHWORM TRIANGULATION")
print("=" * 70)
print(f"Recipe: #{RECIPE['id']} {RECIPE['name_german']} ({RECIPE['name_english']})")
print(f"Fire degree: {RECIPE['fire_degree']}")
print(f"Material class: {RECIPE['material_class']}")
print(f"Instruction sequence: {RECIPE['instruction_sequence']}")
print(f"  - This is UNIQUE among all 203 Brunschwig recipes")
print()

# Step 1: Get REGIME_4 folios (fire_degree=4 = animal)
regime_4_folios = set(regime_data.get('REGIME_4', []))
print(f"Step 1: REGIME_4 folios (animal fire degree): {len(regime_4_folios)}")

# Step 2: Split A vs B
df_a = df[df['language'] == 'A']
df_b = df[df['language'] == 'B']

# Exclude labels from analysis
df_a = df_a[~df_a['placement'].str.startswith('L', na=False)]
df_b = df_b[~df_b['placement'].str.startswith('L', na=False)]

print(f"Currier A tokens: {len(df_a)}")
print(f"Currier B tokens: {len(df_b)}")
print()

# Step 3: Extract MIDDLE from tokens
def extract_middle(word):
    if pd.isna(word) or not word.strip():
        return None
    w = str(word).strip()
    # Simple heuristic: strip common prefixes/suffixes
    prefixes = ['qo', 'ok', 'ot', 'da', 'ch', 'sh', 'ol', 'or', 'al', 'ar']
    suffixes = ['y', 'dy', 'ey', 'aiy', 'oiy', 'm', 'n', 'l', 'r', 'g', 's', 'in', 'iin']

    middle = w
    for p in sorted(prefixes, key=len, reverse=True):
        if middle.startswith(p) and len(middle) > len(p):
            middle = middle[len(p):]
            break
    for s in sorted(suffixes, key=len, reverse=True):
        if middle.endswith(s) and len(middle) > len(s):
            middle = middle[:-len(s)]
            break
    return middle if middle else None

df_b['middle'] = df_b['word'].apply(extract_middle)

# Step 4: Compute folio-level PREFIX profiles for B
print("Step 4: Computing folio-level PREFIX profiles...")

b_folios = df_b['folio'].unique()
folio_profiles = {}

for folio in b_folios:
    folio_tokens = df_b[df_b['folio'] == folio]
    total = len(folio_tokens)
    if total == 0:
        continue

    words = folio_tokens['word'].dropna()

    # Count prefixes
    qo_count = sum(1 for w in words if str(w).startswith('qo'))
    ok_count = sum(1 for w in words if str(w).startswith('ok'))
    ot_count = sum(1 for w in words if str(w).startswith('ot'))
    da_count = sum(1 for w in words if str(w).startswith('da'))
    ch_count = sum(1 for w in words if str(w).startswith('ch'))
    sh_count = sum(1 for w in words if str(w).startswith('sh'))

    # LINK indicators (monitoring words)
    # Words with specific LINK-associated patterns
    link_patterns = ['ol', 'or', 'al', 'ar']  # observation/monitoring prefixes
    link_count = sum(1 for w in words if any(str(w).startswith(p) for p in link_patterns))

    folio_profiles[folio] = {
        'total': total,
        'qo_ratio': qo_count / total,  # e_ESCAPE
        'aux_ratio': (ok_count + ot_count) / total,  # AUX
        'da_ratio': da_count / total,  # FLOW
        'link_ratio': link_count / total,  # LINK
        'ch_count': ch_count,
        'sh_count': sh_count,
        'sister_pref': 'ch' if ch_count > sh_count else ('sh' if sh_count > ch_count else 'neutral')
    }

# Compute averages across B folios
avg_qo = sum(p['qo_ratio'] for p in folio_profiles.values()) / len(folio_profiles)
avg_aux = sum(p['aux_ratio'] for p in folio_profiles.values()) / len(folio_profiles)
avg_da = sum(p['da_ratio'] for p in folio_profiles.values()) / len(folio_profiles)
avg_link = sum(p['link_ratio'] for p in folio_profiles.values()) / len(folio_profiles)

print(f"  Average qo_ratio (e_ESCAPE): {avg_qo:.4f}")
print(f"  Average aux_ratio (AUX): {avg_aux:.4f}")
print(f"  Average da_ratio (FLOW): {avg_da:.4f}")
print(f"  Average link_ratio (LINK): {avg_link:.4f}")
print()

# Step 5: Multi-dimensional conjunction
# Earthworm has ALL dimensions high: e_ESCAPE, AUX, FLOW, LINK, h_HAZARD
print("Step 5: Multi-dimensional conjunction...")
print("  Earthworm needs: high qo (escape) + high aux + high da (flow) + high link")
print()

# Apply constraints
candidate_folios = []
for folio, profile in folio_profiles.items():
    # Must be in REGIME_4
    if folio not in regime_4_folios:
        continue

    # Earthworm profile: ALL instruction types present
    # High escape (e_ESCAPE)
    has_escape = profile['qo_ratio'] >= avg_qo * 0.8
    # High aux (AUX)
    has_aux = profile['aux_ratio'] >= avg_aux * 0.8
    # High flow (FLOW)
    has_flow = profile['da_ratio'] >= avg_da * 0.8
    # Link present
    has_link = profile['link_ratio'] >= avg_link * 0.5

    # Score by how many dimensions match
    score = sum([has_escape, has_aux, has_flow, has_link])

    if score >= 3:  # Need at least 3 of 4 dimensions
        candidate_folios.append({
            'folio': folio,
            'score': score,
            'qo': profile['qo_ratio'],
            'aux': profile['aux_ratio'],
            'da': profile['da_ratio'],
            'link': profile['link_ratio'],
            'escape': has_escape,
            'aux_match': has_aux,
            'flow_match': has_flow,
            'link_match': has_link
        })

candidate_folios.sort(key=lambda x: (-x['score'], -x['da']))

print(f"Candidate B folios (3+ dimensions matched): {len(candidate_folios)}")
print()

if candidate_folios:
    print("Top candidates:")
    for c in candidate_folios[:10]:
        flags = []
        if c['escape']: flags.append('ESC')
        if c['aux_match']: flags.append('AUX')
        if c['flow_match']: flags.append('FLOW')
        if c['link_match']: flags.append('LINK')
        print(f"  {c['folio']:8s} score={c['score']} qo={c['qo']:.3f} aux={c['aux']:.3f} da={c['da']:.3f} link={c['link']:.3f} [{','.join(flags)}]")
    print()

# Step 6: Get PP vocabulary from candidate folios
print("Step 6: Extracting PP vocabulary from candidate folios...")

# Get B middles from candidates
b_middles_set = set()
for c in candidate_folios:
    folio_tokens = df_b[df_b['folio'] == c['folio']]
    b_middles_set.update(folio_tokens['middle'].dropna().unique())

# Get all A middles
df_a['middle'] = df_a['word'].apply(extract_middle)
a_middles_set = set(df_a['middle'].dropna().unique())

# PP = shared between A and B
pp_middles = a_middles_set & b_middles_set

# Remove infrastructure
infrastructure = {'a', 'o', 'e', 'ee', 'eo', 'ai', 'oi', 'ei', '', '_EMPTY_', 'k', 'l', 't', 'd'}
discriminative_pp = pp_middles - infrastructure

print(f"  Total B middles in candidates: {len(b_middles_set)}")
print(f"  Shared PP middles: {len(pp_middles)}")
print(f"  Discriminative PP (minus infrastructure): {len(discriminative_pp)}")
print()

# Step 7: Find A records with multiple PP convergence
print("Step 7: Finding A records with PP convergence to earthworm folios...")

# Group A by record (folio:line)
a_records = df_a.groupby(['folio', 'line_number']).agg({
    'middle': lambda x: set(x.dropna()),
    'word': list
}).reset_index()

a_records['pp_overlap'] = a_records['middle'].apply(lambda x: len(x & discriminative_pp))
a_records['pp_tokens'] = a_records['middle'].apply(lambda x: x & discriminative_pp)

# Require 2+ PP convergence
converging = a_records[a_records['pp_overlap'] >= 2].copy()
converging = converging.sort_values('pp_overlap', ascending=False)

print(f"A records with 2+ PP overlap: {len(converging)}")
print()

# Step 8: Extract RI tokens from converging records
print("Step 8: Extracting RI tokens (animal candidates)...")

# RI = in A but not in B
all_b_middles = set(df_b['middle'].dropna().unique())

ri_candidates = []
for _, row in converging.head(20).iterrows():
    record_middles = row['middle']
    ri_tokens = record_middles - all_b_middles - infrastructure

    if ri_tokens:
        ri_candidates.append({
            'folio': row['folio'],
            'line': row['line_number'],
            'pp_overlap': row['pp_overlap'],
            'pp_tokens': row['pp_tokens'],
            'ri_tokens': ri_tokens,
            'words': row['word']
        })

print(f"Records with RI tokens: {len(ri_candidates)}")
print()

if ri_candidates:
    print("RI candidates from high-overlap records:")
    print("-" * 70)
    for r in ri_candidates[:15]:
        print(f"  {r['folio']}:{r['line']} (PP overlap: {r['pp_overlap']})")
        print(f"    PP tokens: {r['pp_tokens']}")
        print(f"    RI tokens: {r['ri_tokens']}")
        print()

# Step 9: Score RI tokens by PP context PREFIX profiles
print("=" * 70)
print("Step 9: Scoring RI tokens by PP context")
print("=" * 70)
print()
print("Earthworm profile: HIGH escape + HIGH aux + HIGH flow + LINK")
print("RI tokens scored by PREFIX profiles of co-occurring PP tokens in B")
print()

# Collect all unique RI tokens (filter out damaged tokens with ***)
all_ri = set()
for r in ri_candidates:
    for ri in r['ri_tokens']:
        if '***' not in ri and '*' not in ri:  # Skip damaged tokens
            all_ri.add(ri)

print(f"Clean RI tokens (no damage markers): {len(all_ri)}")
print(f"RI tokens found: {all_ri}")
print()

# Score each RI token by its PP associations
ri_scores = []
for ri in all_ri:
    # Find PP tokens that co-occur with this RI in A records
    pp_associations = set()
    record_count = 0
    for r in ri_candidates:
        if ri in r['ri_tokens']:
            pp_associations.update(r['pp_tokens'])
            record_count += 1

    # Clean PP associations (remove damaged)
    pp_associations = {pp for pp in pp_associations if '*' not in pp}

    # Score PP associations by their B prefix profiles
    escape_score = 0
    aux_score = 0
    flow_score = 0

    for pp in pp_associations:
        pp_in_b = df_b[df_b['middle'] == pp]
        if len(pp_in_b) == 0:
            continue
        words = pp_in_b['word'].dropna()
        total = len(words)
        if total == 0:
            continue

        qo = sum(1 for w in words if str(w).startswith('qo')) / total
        aux = sum(1 for w in words if str(w).startswith('ok') or str(w).startswith('ot')) / total
        da = sum(1 for w in words if str(w).startswith('da')) / total

        escape_score += qo
        aux_score += aux
        flow_score += da

    # Earthworm needs ALL dimensions - composite score
    # Unique: has FLOW (da) unlike chicken which is low-da
    # Weight flow x2 since it's earthworm's distinctive feature
    composite = escape_score + aux_score + flow_score * 2

    ri_scores.append({
        'ri': ri,
        'escape': escape_score,
        'aux': aux_score,
        'flow': flow_score,
        'composite': composite,
        'pp_count': len(pp_associations),
        'records': record_count,
        'pp_tokens': pp_associations
    })

ri_scores.sort(key=lambda x: (-x['composite'], -x['pp_count']))

print("RI tokens ranked by earthworm profile match:")
print("(Earthworm unique for HIGH FLOW - distinguishes from chicken)")
print()
print(f"{'RI Token':<20} {'Escape':<8} {'Aux':<8} {'Flow':<8} {'Composite':<10} {'PP#':<5} {'Records'}")
print("-" * 75)
for r in ri_scores[:15]:
    print(f"{r['ri']:<20} {r['escape']:<8.2f} {r['aux']:<8.2f} {r['flow']:<8.2f} {r['composite']:<10.2f} {r['pp_count']:<5} {r['records']}")

print()

# Detailed analysis of top candidates
print("=" * 70)
print("DETAILED ANALYSIS OF TOP CANDIDATES")
print("=" * 70)
for r in ri_scores[:3]:
    print(f"\n{r['ri']}:")
    print(f"  PP context: {r['pp_tokens']}")
    print(f"  Appears in {r['records']} A records")
    print(f"  Profile: escape={r['escape']:.2f} aux={r['aux']:.2f} flow={r['flow']:.2f}")

print()
print("=" * 70)
print("CONCLUSION")
print("=" * 70)
if ri_scores:
    top = ri_scores[0]
    print(f"Top candidate for EARTHWORM: {top['ri']}")
    print(f"  - Composite score: {top['composite']:.2f}")
    print(f"  - Escape (qo): {top['escape']:.2f}")
    print(f"  - Aux (ok/ot): {top['aux']:.2f}")
    print(f"  - Flow (da): {top['flow']:.2f} (earthworm's distinctive feature)")
    print()
    print("COMPARISON with known identifications:")
    print("  - Chicken (eoschso): HIGH escape + HIGH aux + LOW flow")
    print("  - Earthworm should be: HIGH escape + HIGH aux + HIGH flow + LINK")
    print()
    if top['flow'] > 0.5:
        print(f"RESULT: {top['ri']} has HIGH flow ({top['flow']:.2f})")
        print("  This is consistent with earthworm's [FLOW] in sequence!")
    else:
        print(f"RESULT: {top['ri']} has LOW flow ({top['flow']:.2f})")
        print("  May not be distinct from chicken - need more discrimination")
else:
    print("No clean RI candidates found - may need to relax constraints")
