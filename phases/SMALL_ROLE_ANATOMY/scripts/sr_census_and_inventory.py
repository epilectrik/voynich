"""
Script 1: Small Role Census Reconciliation and MIDDLE Inventory

Resolves census discrepancies for CC, FL, FQ by reconciling ICC, BCSC,
AX-phase, and CLASS_SEMANTIC_VALIDATION taxonomies.

Produces: definitive role memberships, per-class token counts,
MIDDLE PP/RI/B-exclusive inventory, cross-role 5x5 Jaccard matrix.
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

import json
from pathlib import Path
from collections import defaultdict
from scripts.voynich import Transcript, Morphology

BASE = Path('C:/git/voynich')
CLASS_MAP = BASE / 'phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json'
MIDDLE_CLASSES = BASE / 'phases/A_INTERNAL_STRATIFICATION/results/middle_classes.json'
AX_CENSUS = BASE / 'phases/AUXILIARY_STRATIFICATION/results/ax_census.json'
EN_CENSUS = BASE / 'phases/EN_ANATOMY/results/en_census.json'
RESULTS = BASE / 'phases/SMALL_ROLE_ANATOMY/results'

# Load data
tx = Transcript()
morph = Morphology()
tokens = list(tx.currier_b())

with open(CLASS_MAP) as f:
    class_data = json.load(f)
with open(MIDDLE_CLASSES) as f:
    mc = json.load(f)
with open(AX_CENSUS) as f:
    ax_data = json.load(f)
with open(EN_CENSUS) as f:
    en_data = json.load(f)

ri_middles = set(mc['a_exclusive_middles'])
pp_middles = set(mc['a_shared_middles'])

token_to_class = {tok: int(cls) for tok, cls in class_data['token_to_class'].items()}
ALL_CLASSES = set(token_to_class.values())

# Invert: class -> token types
class_to_tokens = defaultdict(list)
for tok, cls in token_to_class.items():
    class_to_tokens[cls].append(tok)

# ============================================================
print("=" * 70)
print("SMALL ROLE CENSUS RECONCILIATION AND MIDDLE INVENTORY")
print("=" * 70)

# ============================================================
# 1. TAXONOMY COMPARISON
# ============================================================
print("\n" + "-" * 70)
print("1. TAXONOMY COMPARISON: ALL SOURCES")
print("-" * 70)

# Source 1: ICC README (original systematic characterization)
ICC_CC_orig = {10, 11, 12}          # 3 classes
ICC_EN_raw = {8} | set(range(31,50)) # 8 + 31-49
ICC_FL_orig = {7, 30, 38, 40}       # 4 classes
ICC_FQ_orig = {9, 13, 14, 23}       # 4 classes (from ICC README)
# ICC AX = everything else

# Source 2: BCSC contract counts
BCSC_CC = 'not enumerated'
BCSC_EN = 11  # (wrong per C573, should be 18)
BCSC_FL = 2   # (undercounted vs ICC's 4)
BCSC_FQ = 4
BCSC_AX = 20

# Source 3: CLASS_SEMANTIC_VALIDATION phase scripts
CSV_CC = {10, 11, 17}               # Uses 17 instead of 12
CSV_EN = {8, 31, 32, 33, 34, 36}    # Only 6 core
CSV_FL = {7, 30, 38, 40}            # Same as ICC
CSV_FQ = {9, 20, 21, 23}            # Different: 20,21 instead of 13,14

# Source 4: AX_STRATIFICATION phase (hardcoded AX_CLASSES)
AX_phase = {1, 2, 3, 4, 5, 6, 14, 15, 16, 18, 19, 20, 21, 22, 24, 25, 26, 27, 28, 29}

# Source 5: EN_ANATOMY confirmed (C573)
EN_confirmed = set(en_data['definitive_en_classes'])  # 18 classes

# Source 6: EN census script role assignments
EN_script_CC = {10, 11, 12}
EN_script_FQ = {9, 13, 23}

print("\n--- CONFLICTING ASSIGNMENTS ---")
print(f"\nCC membership:")
print(f"  ICC README:           {sorted(ICC_CC_orig)} (3 classes)")
print(f"  CLASS_SEMANTIC_VAL:   {sorted(CSV_CC)} (3 classes) -- uses 17, drops 12")
print(f"  EN_ANATOMY scripts:   {sorted(EN_script_CC)} (3 classes)")
print(f"  AX scripts:           CC={{10,11,12,17}} (4 classes)")

print(f"\nFQ membership:")
print(f"  ICC README:           {sorted(ICC_FQ_orig)} (4 classes) -- has 13, 14")
print(f"  C559 / CSV phase:     {sorted(CSV_FQ)} (4 classes) -- has 20, 21")
print(f"  EN_ANATOMY scripts:   {{9, 13, 23}} (3 classes)")

print(f"\nDisputed classes:")
print(f"  Class 12: ICC->CC, CSV drops it (never standalone, C540)")
print(f"  Class 13: ICC->FQ, EN_scripts->FQ, CSV->unassigned")
print(f"  Class 14: ICC->FQ, AX_phase->AX")
print(f"  Class 17: CSV->CC, AX_phase->unassigned (not in AX set)")
print(f"  Class 20: CSV->FQ, AX_phase->AX (C563 AX_FINAL)")
print(f"  Class 21: CSV->FQ, AX_phase->AX (C563 AX_FINAL)")

# ============================================================
# 2. RESOLUTION: DATA-DRIVEN APPROACH
# ============================================================
print("\n" + "-" * 70)
print("2. RESOLUTION: ANCHORED COMPUTATION")
print("-" * 70)

# Step 1: EN is fully resolved (C573 = 18 classes)
# Step 2: FL is consistent across all sources = {7, 30, 38, 40}
# Step 3: Remaining = ALL_CLASSES - EN - FL
EN_FINAL = EN_confirmed
FL_FINAL = {7, 30, 38, 40}
REMAINING = ALL_CLASSES - EN_FINAL - FL_FINAL

print(f"\nAnchors:")
print(f"  EN (C573): {len(EN_FINAL)} classes = {sorted(EN_FINAL)}")
print(f"  FL (all agree): {len(FL_FINAL)} classes = {sorted(FL_FINAL)}")
print(f"  Remaining ({len(REMAINING)}): {sorted(REMAINING)}")

# Step 4: AX is well-established with 20 classes from the AX phase
# But we need to verify against ICC assignments for disputed classes
# ICC says AX = {everything} - CC - EN - FL - FQ
# ICC: CC={10,11,12}, FQ={9,13,14,23}
# Then ICC_AX = REMAINING - {10,11,12} - {9,13,14,23} = 20 classes
ICC_AX_computed = REMAINING - ICC_CC_orig - ICC_FQ_orig
print(f"\nICC-derived AX ({len(ICC_AX_computed)}): {sorted(ICC_AX_computed)}")
print(f"AX phase set   ({len(AX_phase)}): {sorted(AX_phase)}")
print(f"Match: {ICC_AX_computed == AX_phase}")

# Differences
if ICC_AX_computed != AX_phase:
    in_icc_not_phase = ICC_AX_computed - AX_phase
    in_phase_not_icc = AX_phase - ICC_AX_computed
    print(f"  In ICC-AX but not AX-phase: {sorted(in_icc_not_phase)}")
    print(f"  In AX-phase but not ICC-AX: {sorted(in_phase_not_icc)}")

# Empirical check: token count for disputed classes
print(f"\n--- DISPUTED CLASS PROFILES ---")
disputed = {12, 13, 14, 17, 20, 21}
for cls in sorted(disputed):
    toks = sorted(class_to_tokens.get(cls, []))
    # Count corpus occurrences
    count = sum(1 for t in tokens if token_to_class.get(t.word) == cls)
    print(f"  Class {cls}: {len(toks)} types, {count} corpus tokens")
    print(f"    Types: {toks[:10]}{'...' if len(toks) > 10 else ''}")
    # Morphological profile
    for tok in toks[:5]:
        m = morph.extract(tok)
        print(f"      {tok}: pfx={m.prefix}, mid={m.middle}, sfx={m.suffix}, art={m.articulator}")

# RESOLUTION DECISION
# ICC is the original systematic characterization (49 classes, C121)
# Use ICC assignments as authoritative:
#   CC = {10, 11, 12}
#   FQ = {9, 13, 14, 23}
#   AX = ICC_AX_computed (which includes 17, 20, 21)
# Note: Class 12 (k) never appears standalone (C540) but is still a defined class
# Note: C559 used different FQ set {9, 20, 21, 23} -- its statistical findings
#   about positional patterns may need re-evaluation with correct membership

CC_FINAL = ICC_CC_orig & REMAINING
FQ_FINAL = ICC_FQ_orig & REMAINING
AX_FINAL = REMAINING - CC_FINAL - FQ_FINAL

print(f"\n--- RESOLVED ASSIGNMENTS ---")
print(f"CC: {sorted(CC_FINAL)} ({len(CC_FINAL)} classes)")
print(f"FL: {sorted(FL_FINAL)} ({len(FL_FINAL)} classes)")
print(f"FQ: {sorted(FQ_FINAL)} ({len(FQ_FINAL)} classes)")
print(f"EN: {sorted(EN_FINAL)} ({len(EN_FINAL)} classes)")
print(f"AX: {sorted(AX_FINAL)} ({len(AX_FINAL)} classes)")
print(f"Total: {len(CC_FINAL) + len(FL_FINAL) + len(FQ_FINAL) + len(EN_FINAL) + len(AX_FINAL)}")
print(f"Expected: {len(ALL_CLASSES)}")

# Verify completeness and disjointness
all_assigned = CC_FINAL | FL_FINAL | FQ_FINAL | EN_FINAL | AX_FINAL
assert all_assigned == ALL_CLASSES, f"Not all assigned! Missing: {ALL_CLASSES - all_assigned}"
assert len(all_assigned) == len(CC_FINAL) + len(FL_FINAL) + len(FQ_FINAL) + len(EN_FINAL) + len(AX_FINAL), "Overlap detected!"

# Conflict notes
print(f"\n--- CONFLICT NOTES ---")
print(f"C559 used FQ={{9,20,21,23}} but ICC gives FQ={{9,13,14,23}}")
print(f"  C559 findings about FQ behavior may apply to a mixed AX/FQ set")
print(f"  Classes 20,21 are AX per ICC; C563 AX_FINAL confirms their AX membership")
print(f"C563 AX phase used AX with 14 (ICC->FQ) and without 17 (ICC->AX)")
print(f"  Class 14 AX positional data may be misattributed (should be FQ)")
print(f"  Class 17 was missing from AX phase analysis")

# Role mapper function
def get_role(cls_id):
    if cls_id in CC_FINAL: return 'CC'
    if cls_id in FL_FINAL: return 'FL'
    if cls_id in FQ_FINAL: return 'FQ'
    if cls_id in EN_FINAL: return 'EN'
    if cls_id in AX_FINAL: return 'AX'
    return 'UNKNOWN'

# ============================================================
# 3. PER-CLASS TOKEN COUNTS (CC, FL, FQ only)
# ============================================================
print("\n" + "-" * 70)
print("3. PER-CLASS TOKEN COUNTS")
print("-" * 70)

class_corpus_counts = defaultdict(int)
for t in tokens:
    cls = token_to_class.get(t.word)
    if cls is not None:
        class_corpus_counts[cls] += 1

b_total = len(tokens)
small_roles = {'CC': CC_FINAL, 'FL': FL_FINAL, 'FQ': FQ_FINAL}
role_details = {}

for role_name, role_classes in small_roles.items():
    role_total = sum(class_corpus_counts[c] for c in role_classes)
    role_pct = role_total / b_total * 100

    print(f"\n{role_name}: {role_total} tokens ({role_pct:.1f}% of B), {len(role_classes)} classes")
    print(f"  {'Class':>6} {'Types':>6} {'Tokens':>7} {'Pct':>6} {'Examples'}")
    print(f"  {'-'*50}")

    per_class = {}
    for cls in sorted(role_classes):
        types = sorted(class_to_tokens.get(cls, []))
        count = class_corpus_counts[cls]
        pct = count / role_total * 100 if role_total > 0 else 0
        examples = ', '.join(types[:5])
        print(f"  {cls:>6} {len(types):>6} {count:>7} {pct:>5.1f}% {examples}")
        per_class[str(cls)] = {
            'types': len(types),
            'tokens': count,
            'pct_of_role': round(pct, 2),
            'examples': types[:10]
        }

    role_details[role_name] = {
        'classes': sorted(role_classes),
        'total_tokens': role_total,
        'pct_of_b': round(role_pct, 2),
        'per_class': per_class
    }

# ============================================================
# 4. MIDDLE INVENTORY PER ROLE
# ============================================================
print("\n" + "-" * 70)
print("4. MIDDLE INVENTORY (PP/RI/B-exclusive)")
print("-" * 70)

# Build class -> middles mapping for ALL roles
class_to_middles = defaultdict(set)
for tok, cls in token_to_class.items():
    m = morph.extract(tok)
    mid = m.middle if m.middle else None
    if mid:
        class_to_middles[cls].add(mid)

# Per-role MIDDLE sets
role_middles = {}
for role_name, role_classes in [('CC', CC_FINAL), ('FL', FL_FINAL), ('FQ', FQ_FINAL),
                                  ('EN', EN_FINAL), ('AX', AX_FINAL)]:
    middles = set()
    for cls in role_classes:
        middles |= class_to_middles[cls]
    role_middles[role_name] = middles

middle_inventory = {}
for role_name in ['CC', 'FL', 'FQ']:
    middles = role_middles[role_name]
    n_mid = len(middles)
    pp = middles & pp_middles
    ri = middles & ri_middles
    bex = middles - pp_middles - ri_middles
    pp_pct = len(pp) / n_mid * 100 if n_mid > 0 else 0
    ri_pct = len(ri) / n_mid * 100 if n_mid > 0 else 0
    bex_pct = len(bex) / n_mid * 100 if n_mid > 0 else 0

    print(f"\n{role_name}: {n_mid} unique MIDDLEs")
    print(f"  PP (pipeline-participating): {len(pp)} ({pp_pct:.1f}%)")
    print(f"  RI (registry-internal):      {len(ri)} ({ri_pct:.1f}%)")
    print(f"  B-exclusive:                 {len(bex)} ({bex_pct:.1f}%)")
    if bex:
        print(f"  B-exclusive list: {sorted(bex)}")

    middle_inventory[role_name] = {
        'total_middles': n_mid,
        'pp_count': len(pp),
        'pp_pct': round(pp_pct, 2),
        'pp_middles': sorted(pp),
        'ri_count': len(ri),
        'ri_pct': round(ri_pct, 2),
        'ri_middles': sorted(ri),
        'b_exclusive_count': len(bex),
        'b_exclusive_pct': round(bex_pct, 2),
        'b_exclusive_middles': sorted(bex),
        'all_middles': sorted(middles)
    }

# Pipeline purity comparison
print(f"\n--- PIPELINE PURITY COMPARISON ---")
print(f"  AX: {en_data.get('middle_inventory', {}).get('pp_pct', 'N/A')}% PP [from AX phase: ~98.2%]")
print(f"  EN: {en_data['middle_inventory']['pp_pct']}% PP")
for rn in ['CC', 'FL', 'FQ']:
    print(f"  {rn}: {middle_inventory[rn]['pp_pct']}% PP")

# ============================================================
# 5. CROSS-ROLE MIDDLE SHARING (5x5 Jaccard)
# ============================================================
print("\n" + "-" * 70)
print("5. CROSS-ROLE MIDDLE SHARING (5x5 Jaccard)")
print("-" * 70)

role_names = ['CC', 'EN', 'FL', 'FQ', 'AX']
jaccard_matrix = {}

print(f"\n{'':>4}", end='')
for rn in role_names:
    print(f"  {rn:>6}", end='')
print()

for r1 in role_names:
    print(f"{r1:>4}", end='')
    row = {}
    for r2 in role_names:
        s1 = role_middles[r1]
        s2 = role_middles[r2]
        inter = len(s1 & s2)
        union = len(s1 | s2)
        j = inter / union if union > 0 else 0
        row[r2] = round(j, 4)
        print(f"  {j:6.3f}", end='')
    jaccard_matrix[r1] = row
    print()

# Role-exclusive MIDDLEs
print(f"\n--- ROLE-EXCLUSIVE MIDDLEs ---")
exclusive_counts = {}
for rn in role_names:
    exclusive = role_middles[rn].copy()
    for other in role_names:
        if other != rn:
            exclusive -= role_middles[other]
    exclusive_counts[rn] = len(exclusive)
    total = len(role_middles[rn])
    pct = len(exclusive) / total * 100 if total > 0 else 0
    print(f"  {rn}: {len(exclusive)}/{total} exclusive ({pct:.1f}%)")
    if rn in ['CC', 'FL', 'FQ'] and exclusive:
        print(f"    {sorted(exclusive)[:15]}")

# ============================================================
# 6. MORPHOLOGICAL PROFILE PER CLASS
# ============================================================
print("\n" + "-" * 70)
print("6. MORPHOLOGICAL PROFILE (CC, FL, FQ)")
print("-" * 70)

morph_profiles = {}
for role_name, role_classes in small_roles.items():
    print(f"\n{role_name}:")
    print(f"  {'Cls':>4} {'Types':>5} {'MIDs':>5} {'Pfx%':>6} {'Sfx%':>6} {'Art%':>6} {'AvgLen':>6} {'DomPfx'}")
    for cls in sorted(role_classes):
        types = class_to_tokens.get(cls, [])
        n = len(types)
        if n == 0:
            continue
        pfx_count = 0
        sfx_count = 0
        art_count = 0
        total_len = 0
        prefix_dist = defaultdict(int)
        suffix_dist = defaultdict(int)
        for t in types:
            m = morph.extract(t)
            if m.prefix:
                pfx_count += 1
                prefix_dist[m.prefix] += 1
            if m.suffix:
                sfx_count += 1
                suffix_dist[m.suffix or 'NONE'] += 1
            if m.has_articulator:
                art_count += 1
            total_len += len(t)

        pfx_rate = pfx_count / n * 100
        sfx_rate = sfx_count / n * 100
        art_rate = art_count / n * 100
        avg_len = total_len / n
        dom_pfx = max(prefix_dist, key=prefix_dist.get) if prefix_dist else 'NONE'
        dom_sfx = max(suffix_dist, key=suffix_dist.get) if suffix_dist else 'NONE'

        n_mid = len(class_to_middles.get(cls, set()))
        print(f"  {cls:>4} {n:>5} {n_mid:>5} {pfx_rate:>5.1f} {sfx_rate:>5.1f} {art_rate:>5.1f} {avg_len:>5.1f}  {dom_pfx}")

        morph_profiles[str(cls)] = {
            'role': role_name,
            'n_types': n,
            'n_middles': n_mid,
            'prefix_rate': round(pfx_rate, 2),
            'suffix_rate': round(sfx_rate, 2),
            'articulator_rate': round(art_rate, 2),
            'avg_token_length': round(avg_len, 2),
            'dominant_prefix': dom_pfx,
            'dominant_suffix': dom_sfx,
            'prefix_distribution': dict(prefix_dist),
            'suffix_distribution': dict(suffix_dist)
        }

# ============================================================
# SAVE RESULTS
# ============================================================

# Conflict documentation
conflict_notes = {
    'C559_vs_ICC': {
        'description': 'C559 used FQ={9,20,21,23} but ICC gives FQ={9,13,14,23}',
        'resolution': 'Using ICC as authoritative (original systematic characterization)',
        'impact': 'C559 findings about Classes 20/21 may describe AX behavior, not FQ',
    },
    'Class_12': {
        'description': 'ICC assigns to CC but never appears standalone (C540)',
        'resolution': 'Keep in CC per ICC -- defined class even if zero corpus tokens',
    },
    'Class_14': {
        'description': 'ICC->FQ but AX phase included it in AX',
        'resolution': 'Using ICC: Class 14 is FQ',
        'impact': 'C563 AX positional data included Class 14 (should be FQ)',
    },
    'Class_17': {
        'description': 'Not in ICC CC set, not in hardcoded AX set, CSV puts in CC',
        'resolution': 'ICC remainder assigns to AX',
    },
    'AX_phase_discrepancy': {
        'description': 'AX phase used {14} as AX and omitted {17}',
        'icc_ax': sorted(ICC_AX_computed) if ICC_AX_computed != AX_phase else 'matches',
        'phase_ax': sorted(AX_phase),
    }
}

results = {
    'resolved_roles': {
        'CC': {'classes': sorted(CC_FINAL), 'count': len(CC_FINAL)},
        'FL': {'classes': sorted(FL_FINAL), 'count': len(FL_FINAL)},
        'FQ': {'classes': sorted(FQ_FINAL), 'count': len(FQ_FINAL)},
        'EN': {'classes': sorted(EN_FINAL), 'count': len(EN_FINAL)},
        'AX': {'classes': sorted(AX_FINAL), 'count': len(AX_FINAL)},
    },
    'total_classes': len(ALL_CLASSES),
    'b_total_tokens': b_total,
    'role_details': role_details,
    'middle_inventory': middle_inventory,
    'jaccard_matrix': jaccard_matrix,
    'exclusive_middles': exclusive_counts,
    'morphological_profiles': morph_profiles,
    'conflict_notes': conflict_notes,
    'taxonomy_sources': {
        'ICC_CC': sorted(ICC_CC_orig),
        'ICC_FQ': sorted(ICC_FQ_orig),
        'ICC_FL': sorted(ICC_FL_orig),
        'CSV_CC': sorted(CSV_CC),
        'CSV_FQ': sorted(CSV_FQ),
        'AX_phase_set': sorted(AX_phase),
    }
}

RESULTS.mkdir(parents=True, exist_ok=True)
with open(RESULTS / 'sr_census.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to {RESULTS / 'sr_census.json'}")
