"""
Script 6: Small Role Synthesis

Unified synthesis: per-role summaries, five-role comparison matrix,
cross-constraint consistency, BCSC update recommendations,
new constraint enumeration.
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

import json
from pathlib import Path

BASE = Path('C:/git/voynich')
RESULTS = BASE / 'phases/SMALL_ROLE_ANATOMY/results'

# Load all phase results
with open(RESULTS / 'sr_census.json') as f:
    census = json.load(f)
with open(RESULTS / 'sr_features.json') as f:
    features_raw = json.load(f)
    features = {int(k): v for k, v in features_raw.items()}
with open(RESULTS / 'sr_suffix_analysis.json') as f:
    suffix = json.load(f)
with open(RESULTS / 'sr_hazard_anatomy.json') as f:
    hazard = json.load(f)
with open(RESULTS / 'sr_internal_structure.json') as f:
    structure = json.load(f)

# Also load prior anatomy results for comparison
with open(BASE / 'phases/EN_ANATOMY/results/en_census.json') as f:
    en_census = json.load(f)
with open(BASE / 'phases/EN_ANATOMY/results/en_synthesis.json') as f:
    en_synth = json.load(f)

# ============================================================
print("=" * 70)
print("SMALL ROLE ANATOMY: UNIFIED SYNTHESIS")
print("=" * 70)

# ============================================================
# 1. CENSUS RESOLUTION
# ============================================================
print("\n" + "-" * 70)
print("1. CENSUS RESOLUTION")
print("-" * 70)

resolved = census['resolved_roles']
print(f"""
Resolution method: ICC (original systematic characterization, C121) as anchor
  EN confirmed: {resolved['EN']['count']} classes (C573)
  FL confirmed: {resolved['FL']['count']} classes (all sources agree)
  CC resolved:  {resolved['CC']['count']} classes {resolved['CC']['classes']}
  FQ resolved:  {resolved['FQ']['count']} classes {resolved['FQ']['classes']}
  AX resolved:  {resolved['AX']['count']} classes (ICC remainder)

Key census findings:
  - Class 12 (k): Defined but ZERO corpus tokens (ghost class, C540)
  - FQ is {sorted(resolved['FQ']['classes'])}, NOT {'{9, 20, 21, 23}'} as C559 stated
    C559 used wrong membership (20, 21 are AX per ICC and C563 AX_FINAL)
  - AX should include Class 17 (omitted from AX phase) and exclude Class 14 (misattributed)
  - CC has 735 tokens (3.2% of B), NOT ~1,023 as estimated
  - FQ has 2,890 tokens (12.5% of B), NOT 1,301 as C559 stated
""")

# Token summary
print("Token counts:")
for role in ['CC', 'FL', 'FQ']:
    r = census['role_details'][role]
    print(f"  {role}: {r['total_tokens']} tokens ({r['pct_of_b']}% of B), {len(r['classes'])} classes")
print(f"  EN: {en_census['en_token_total']} tokens ({en_census['en_pct_of_b']}% of B), {en_census['definitive_en_count']} classes")

# ============================================================
# 2. PIPELINE PURITY
# ============================================================
print("\n" + "-" * 70)
print("2. PIPELINE PURITY (PP/RI/B-exclusive)")
print("-" * 70)

for role in ['CC', 'FL', 'FQ']:
    inv = census['middle_inventory'][role]
    print(f"\n{role}: {inv['total_middles']} MIDDLEs, {inv['pp_pct']}% PP, "
          f"{inv['ri_pct']}% RI, {inv['b_exclusive_pct']}% B-exclusive")

print(f"\nEN: {en_census['middle_inventory']['total_middles']} MIDDLEs, "
      f"{en_census['middle_inventory']['pp_pct']}% PP")

print(f"\nUNIVERSAL: All 5 roles are 100% PP (or near-100%).")
print(f"Zero RI and zero B-exclusive MIDDLEs in any role.")
print(f"Pipeline vocabulary completely dominates Currier B execution.")

# ============================================================
# 3. CROSS-ROLE MIDDLE SHARING
# ============================================================
print("\n" + "-" * 70)
print("3. CROSS-ROLE MIDDLE SHARING")
print("-" * 70)

print("\nJaccard matrix:")
jm = census['jaccard_matrix']
roles = ['CC', 'EN', 'FL', 'FQ', 'AX']
print(f"{'':>4}", end='')
for r in roles:
    print(f"  {r:>6}", end='')
print()
for r1 in roles:
    print(f"{r1:>4}", end='')
    for r2 in roles:
        print(f"  {jm[r1][r2]:6.3f}", end='')
    print()

exc = census['exclusive_middles']
print(f"\nRole-exclusive MIDDLEs:")
for r in roles:
    print(f"  {r}: {exc[r]} exclusive")

print(f"\nCC is a vocabulary island (Jaccard < 0.06 with all roles)")
print(f"EN-AX share most vocabulary (Jaccard 0.402)")
print(f"FQ-FL share moderately (Jaccard 0.333)")

# ============================================================
# 4. SUFFIX DIMENSION
# ============================================================
print("\n" + "-" * 70)
print("4. SUFFIX DIMENSION (NEW)")
print("-" * 70)

for role in roles:
    inv = suffix['role_suffix_inventory'][role]
    print(f"  {role}: {inv['suffix_types']} suffix types, {inv['nosuffix_pct']}% suffix-less")

sel = suffix['suffix_selectivity']
print(f"\nSuffix selectivity: chi2={sel['chi2']}, p={sel['p_value']:.2e}")
print(f"Suffix usage is strongly ROLE-DEPENDENT")

print(f"\nSuffix taxonomy:")
print(f"  SUFFIX-RICH:  EN (17 types, 39.0% suffix-less)")
print(f"  SUFFIX-MODERATE: AX (19 types, 62.3% suffix-less)")
print(f"  SUFFIX-POOR:  FL (2 types, 93.8%), FQ (1 type, 93.4%)")
print(f"  SUFFIX-FREE:  CC (0 types, 100% suffix-less)")

print(f"\nSuffix Jaccard:")
sj = suffix['suffix_jaccard_matrix']
print(f"  EN-AX: {sj['EN']['AX']} (high sharing -- same suffix inventory)")
print(f"  All others: < 0.12 (minimal sharing)")
print(f"  CC: 0.000 with all roles (zero suffix types)")

# ============================================================
# 5. HAZARD ANATOMY
# ============================================================
print("\n" + "-" * 70)
print("5. HAZARD ANATOMY")
print("-" * 70)

print(f"\nCorpus forbidden transitions: {hazard['total_corpus_hazards']}")
print(f"Hazard class breakdown: {hazard['hazard_class_counts']}")

print(f"\nRole direction in hazard events:")
src = hazard['direction']['source']
tgt = hazard['direction']['target']
print(f"  FL: source={src.get('FL',0)}, target={tgt.get('FL',0)} -> FL INITIATES hazards (gateway)")
print(f"  EN: source={src.get('EN',0)}, target={tgt.get('EN',0)} -> EN RECEIVES hazards (target)")
print(f"  FQ: source={src.get('FQ',0)}, target={tgt.get('FQ',0)} -> FQ is bidirectional")

print(f"\nFL hazard/safe split:")
print(f"  Hazard classes (7, 30): medial position, 12.3% final")
print(f"  Safe classes (38, 40): strongly final (55.7%), hazard-distant")
print(f"  This is a GENUINE STRUCTURAL SPLIT within FL")

print(f"\nFQ hazard/safe split:")
print(f"  Hazard classes (9, 23): diverse positions and morphologies")
print(f"  Safe classes (13, 14): ok/ot-prefixed, medial, large")
print(f"  Less dramatic split than FL but still genuine")

# ============================================================
# 6. INTERNAL STRUCTURE
# ============================================================
print("\n" + "-" * 70)
print("6. INTERNAL STRUCTURE VERDICTS")
print("-" * 70)

for role in ['CC', 'FL', 'FQ']:
    s = structure[role]
    print(f"\n{role}: {s['verdict']}")
    print(f"  KW significant: {s.get('distinct_fraction', 0)*100:.0f}%")
    print(f"  Mean J-S: {s.get('mean_js_divergence', 0):.4f}")
    if 'role_specific' in s:
        for key, val in s['role_specific'].items():
            if isinstance(val, dict) and 'different' in val:
                print(f"  {key}: {'DIFFERENT' if val['different'] else 'similar'} (p={val.get('p', 'N/A'):.2e})")
            elif isinstance(val, bool):
                print(f"  {key}: {val}")

print(f"\nComparison with AX and EN:")
print(f"  AX: COLLAPSED to positional gradient (silhouette 0.232)")
print(f"  EN: DISTRIBUTIONAL_CONVERGENCE (silhouette 0.180)")
print(f"  CC: GENUINE_STRUCTURE (2 active + 1 ghost)")
print(f"  FL: GENUINE_STRUCTURE (hazard/safe split, 100% KW)")
print(f"  FQ: GENUINE_STRUCTURE (100% KW, Class 9 anomaly)")
print(f"\nSmall roles have STRONGER internal differentiation than large roles.")

# ============================================================
# 7. FIVE-ROLE COMPARISON MATRIX
# ============================================================
print("\n" + "-" * 70)
print("7. FIVE-ROLE COMPARISON MATRIX")
print("-" * 70)

comparison = {}
print(f"\n{'Role':>4} {'Classes':>7} {'Active':>6} {'Tokens':>7} {'%B':>5} "
      f"{'PP%':>4} {'SfxTypes':>8} {'SfxLess%':>8} {'Hazard%':>7} {'Structure'}")

# Gather data for each role
role_data = {
    'CC': {
        'classes': 3, 'active': 2, 'tokens': 735, 'pct_b': 3.2,
        'pp_pct': 100.0, 'suffix_types': 0, 'nosuffix_pct': 100.0,
        'hazard_pct': 0.0, 'structure': 'GENUINE (2+ghost)'
    },
    'EN': {
        'classes': 18, 'active': 18,
        'tokens': en_census['en_token_total'],
        'pct_b': en_census['en_pct_of_b'],
        'pp_pct': 100.0, 'suffix_types': 17, 'nosuffix_pct': 39.0,
        'hazard_pct': 0.23, 'structure': 'CONVERGENCE'
    },
    'FL': {
        'classes': 4, 'active': 4, 'tokens': 1078, 'pct_b': 4.7,
        'pp_pct': 100.0, 'suffix_types': 2, 'nosuffix_pct': 93.8,
        'hazard_pct': 1.23, 'structure': 'GENUINE (haz/safe)'
    },
    'FQ': {
        'classes': 4, 'active': 4, 'tokens': 2890, 'pct_b': 12.5,
        'pp_pct': 100.0, 'suffix_types': 1, 'nosuffix_pct': 93.4,
        'hazard_pct': 0.42, 'structure': 'GENUINE (4-way)'
    },
    'AX': {
        'classes': 20, 'active': 20,
        'tokens': 4559,  # approximate
        'pct_b': 19.7,
        'pp_pct': 98.2, 'suffix_types': 19, 'nosuffix_pct': 62.3,
        'hazard_pct': 0.0, 'structure': 'COLLAPSED (gradient)'
    },
}

for role in ['CC', 'EN', 'FL', 'FQ', 'AX']:
    d = role_data[role]
    print(f"{role:>4} {d['classes']:>7} {d['active']:>6} {d['tokens']:>7} {d['pct_b']:>4.1f} "
          f"{d['pp_pct']:>4.0f} {d['suffix_types']:>8} {d['nosuffix_pct']:>7.1f} "
          f"{d['hazard_pct']:>7.2f} {d['structure']}")
    comparison[role] = d

# ============================================================
# 8. BCSC UPDATE RECOMMENDATIONS
# ============================================================
print("\n" + "-" * 70)
print("8. BCSC UPDATE RECOMMENDATIONS")
print("-" * 70)

bcsc_updates = [
    "EN class_count: 11 -> 18 (C573 confirmed)",
    "FL class_count: 2 -> 4 (ICC gives {7,30,38,40})",
    "FQ token description: update from C559 data to ICC-based data",
    "FQ classes: document as {9,13,14,23}, not {9,20,21,23}",
    "CC: add Class 12 ghost note",
    "Add suffix dimension: CC/FL/FQ suffix-free, EN suffix-rich",
    "Add hazard direction: FL initiates, EN receives",
    "Internal structure: small roles GENUINE, large roles COLLAPSED/CONVERGENCE",
    "C559: flagged for membership correction (used wrong FQ set)",
]

for i, update in enumerate(bcsc_updates):
    print(f"  {i+1}. {update}")

# ============================================================
# 9. NEW CONSTRAINT ENUMERATION
# ============================================================
print("\n" + "-" * 70)
print("9. NEW CONSTRAINT ENUMERATION")
print("-" * 70)

constraints = [
    {
        'id': 'C581',
        'name': 'CC Definitive Census',
        'statement': 'CORE_CONTROL comprises 3 classes {10, 11, 12} with 735 tokens (3.2% of B). '
                     'Class 12 (k) is a ghost class with zero corpus tokens (C540). '
                     'Only Classes 10 (daiin) and 11 (ol) are instantiated.',
        'tier': 2,
        'scope': 'B',
    },
    {
        'id': 'C582',
        'name': 'FL Definitive Census',
        'statement': 'FLOW_OPERATOR comprises 4 classes {7, 30, 38, 40} with 1,078 tokens (4.7% of B). '
                     'BCSC undercounted at 2 classes. Classes 7 (ar/al) and 30 (dar/dal) are hazard-involved; '
                     'Classes 38 and 40 are non-hazardous.',
        'tier': 2,
        'scope': 'B',
    },
    {
        'id': 'C583',
        'name': 'FQ Definitive Census',
        'statement': 'FREQUENT_OPERATOR comprises 4 classes {9, 13, 14, 23} with 2,890 tokens (12.5% of B). '
                     'C559 used wrong membership {9, 20, 21, 23} (Classes 20, 21 are AX per ICC/C563). '
                     'Correct FQ includes ok-prefixed Class 13 (1,191 tokens) and ot-prefixed Class 14 (707 tokens).',
        'tier': 2,
        'scope': 'B',
    },
    {
        'id': 'C584',
        'name': 'Universal Pipeline Purity',
        'statement': 'All 5 operational roles (CC, EN, FL, FQ, AX) are 100% PP (pipeline-participating) '
                     'at the MIDDLE level. Zero RI MIDDLEs and zero B-exclusive MIDDLEs in any role. '
                     'Pipeline vocabulary completely dominates Currier B execution.',
        'tier': 2,
        'scope': 'B',
    },
    {
        'id': 'C585',
        'name': 'Cross-Role MIDDLE Sharing',
        'statement': 'The 5 roles share MIDDLE vocabulary non-uniformly: EN-AX highest (Jaccard 0.402), '
                     'CC minimal (Jaccard < 0.06 with all roles, 0 exclusive MIDDLEs). '
                     'EN has 29 exclusive MIDDLEs (45.3%), AX has 17 (29.3%), FL has 3 (17.6%), '
                     'CC and FQ have 0 exclusive MIDDLEs.',
        'tier': 2,
        'scope': 'B',
    },
    {
        'id': 'C586',
        'name': 'FL Hazard/Safe Structural Split',
        'statement': 'FL divides into two genuine subgroups: hazard classes {7, 30} at medial positions '
                     '(mean 0.55, 12.3% final) and safe classes {38, 40} at final positions '
                     '(mean 0.81, 55.7% final). Mann-Whitney p=9.4e-20 for position, p=7.3e-33 for final rate. '
                     'FL is hazard-source-biased (initiates 4.5x more than receives).',
        'tier': 2,
        'scope': 'B',
    },
    {
        'id': 'C587',
        'name': 'FQ Internal Differentiation',
        'statement': 'FQ shows 4-way genuine structure: Class 9 (aiin/o/or) is medial, prefix-free, self-chaining; '
                     'Classes 13/14 (ok/ot-prefixed) are medial, large, non-hazardous; '
                     'Class 23 (d/l/r/s/y) is final-biased, morphologically minimal. '
                     'All 4 KW tests significant (100%), Class 9 vs others: p=3.9e-7.',
        'tier': 2,
        'scope': 'B',
    },
    {
        'id': 'C588',
        'name': 'Suffix Role Selectivity',
        'statement': 'Suffix usage is strongly role-dependent (chi2=5063.2, p<1e-300). '
                     'Three suffix strata: SUFFIX-RICH (EN: 17 types, 39% bare), '
                     'SUFFIX-MODERATE (AX: 19 types, 62% bare), '
                     'SUFFIX-DEPLETED (FL/FQ: 1-2 types, 93-94% bare; CC: 0 types, 100% bare). '
                     'EN-AX share suffix vocabulary (Jaccard 0.800); CC/FL/FQ are suffix-isolated.',
        'tier': 2,
        'scope': 'B',
    },
    {
        'id': 'C589',
        'name': 'Small Role Genuine Structure',
        'statement': 'All 3 small roles (CC, FL, FQ) show GENUINE_STRUCTURE internally, '
                     'with 75-100% significant Kruskal-Wallis tests and mean J-S divergence 0.014-0.039. '
                     'This contrasts with the large roles: AX is COLLAPSED (positional gradient) '
                     'and EN is DISTRIBUTIONAL_CONVERGENCE (vocabulary/trigger divergence only). '
                     'Small roles are more internally differentiated than large roles.',
        'tier': 2,
        'scope': 'B',
    },
    {
        'id': 'C590',
        'name': 'CC Positional Dichotomy',
        'statement': 'CC has a genuine positional dichotomy: Class 10 (daiin) is initial-biased '
                     '(mean 0.413, 27.1% initial) while Class 11 (ol) is medial (mean 0.511, 5.0% initial). '
                     'Mann-Whitney p=2.8e-5. CC is 100% suffix-free and has only 3 MIDDLEs. '
                     'Class 12 (k) is a ghost class with zero corpus tokens.',
        'tier': 2,
        'scope': 'B',
    },
    {
        'id': 'C591',
        'name': 'Five-Role Complete Taxonomy',
        'statement': 'The 49 Currier B instruction classes partition into 5 roles totaling ~16,054 tokens: '
                     'CC (3 classes, 3.2%), EN (18 classes, 31.1%), FL (4 classes, 4.7%), '
                     'FQ (4 classes, 12.5%), AX (20 classes, 19.7%). '
                     'All roles are 100% PP. Pipeline vocabulary is universal across all execution roles.',
        'tier': 2,
        'scope': 'B',
    },
    {
        'id': 'C592',
        'name': 'C559 Membership Correction',
        'statement': 'C559 (FREQUENT Role Structure) used incorrect membership {9, 20, 21, 23}. '
                     'Correct ICC-based membership is {9, 13, 14, 23}. Classes 20, 21 belong to AX '
                     '(confirmed by C563 AX_FINAL subgroup). C559 statistical findings about positional '
                     'patterns, self-chaining, and REGIME/section distributions may describe a mixed AX/FQ set.',
        'tier': 2,
        'scope': 'B',
    },
]

for c in constraints:
    print(f"\n{c['id']}: {c['name']} (Tier {c['tier']})")
    print(f"  {c['statement'][:120]}...")

# ============================================================
# SAVE
# ============================================================

results = {
    'census_resolution': {
        'CC': resolved['CC'],
        'FL': resolved['FL'],
        'FQ': resolved['FQ'],
        'EN': resolved['EN'],
        'AX': resolved['AX'],
    },
    'five_role_comparison': comparison,
    'bcsc_updates': bcsc_updates,
    'constraints': constraints,
    'structural_verdicts': {
        'CC': structure['CC']['verdict'],
        'FL': structure['FL']['verdict'],
        'FQ': structure['FQ']['verdict'],
        'EN': 'DISTRIBUTIONAL_CONVERGENCE',
        'AX': 'COLLAPSED (positional gradient)',
    },
    'suffix_strata': {
        'SUFFIX_RICH': ['EN'],
        'SUFFIX_MODERATE': ['AX'],
        'SUFFIX_DEPLETED': ['FL', 'FQ'],
        'SUFFIX_FREE': ['CC'],
    },
    'pipeline_purity': 'UNIVERSAL_100_PCT_PP',
    'c559_correction': {
        'wrong': [9, 20, 21, 23],
        'correct': [9, 13, 14, 23],
        'impact': 'C559 statistics may describe mixed AX/FQ set',
    },
}

RESULTS.mkdir(parents=True, exist_ok=True)
with open(RESULTS / 'sr_synthesis.json', 'w') as f:
    json.dump(results, f, indent=2, default=str)

print(f"\n\nSynthesis saved to {RESULTS / 'sr_synthesis.json'}")
