"""
06_illustration_procedural_correlation.py - Tier 4 External Anchor Test

Test: Do illustration features correlate with procedural profiles?

External anchor logic (Tier 4):
- Brunschwig says: "POUND roots, STRIP leaves" (F-BRU-012)
- If root illustrations correlate with higher tch (POUND) density
- And leaf illustrations correlate with higher lch (STRIP) density
- This provides external semantic grounding

Data sources:
- Plant class assignments from PIAA_plant_illustration
- Procedural features from this phase (procedural_features.json)
"""
import sys
import json
from pathlib import Path
from collections import defaultdict
import numpy as np
from scipy import stats

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.voynich import Transcript, Morphology

tx = Transcript()
morph = Morphology()

print("="*70)
print("ILLUSTRATION-PROCEDURAL CORRELATION (TIER 4 EXTERNAL ANCHOR)")
print("="*70)

# ============================================================
# DEFINE PLANT CLASS DATA (from PIAA_plant_illustration)
# ============================================================
print("\n--- Loading Plant Class Assignments ---")

# From plant_class_assignments.md - manually encoded
PLANT_CLASS_DATA = {
    # Folio: (primary_class, secondary_class, confidence, root_emphasis, key_features)
    'f2r': ('ALH', 'MH', 'MEDIUM', True, 'palmate leaves, prominent root'),
    'f5r': ('AF', 'AQ', 'MEDIUM', True, 'bulbous base'),
    'f5v': ('AF', 'ALH', 'MEDIUM', False, 'ivy-like leaves, flowers'),
    'f9r': ('ALH', None, 'HIGH', True, 'feathery leaves, red root, umbellifer'),
    'f9v': ('AF', None, 'HIGH', False, 'blue/violet flowers'),
    'f11r': ('AS', 'ALH', 'MEDIUM', False, 'shrubby, thyme type'),
    'f11v': ('AS', 'RT', 'MEDIUM', False, 'tree-like, bay type'),
    'f17r': ('AF', 'MH', 'MEDIUM', True, 'blue flower spike, borage'),
    'f18r': ('MH', 'FP', 'LOW', False, 'fern-like, carrot family'),
    'f19r': ('ALH', None, 'HIGH', False, 'very fine feathery leaves'),
    'f21r': ('AF', 'MH', 'MEDIUM', True, 'basal leaves, flower spike'),
    'f22r': ('AF', 'ALH', 'MEDIUM', False, 'divided leaves, blue flowers'),
    'f22v': ('AF', 'MH', 'MEDIUM', False, 'scalloped leaves, blue flower'),
    'f24v': ('ALH', 'MH', 'MEDIUM', False, 'palmate/divided leaves'),
    'f25r': ('ALH', 'MH', 'MEDIUM', False, 'ivy-like leaves'),
    'f29v': ('AF', 'MH', 'MEDIUM', False, 'serrated leaves'),
    'f30v': ('RT', 'ALH', 'MEDIUM', False, 'conifer/juniper type'),
    'f32v': ('ALH', 'MH', 'MEDIUM', False, 'stellate leaves, seed pods'),
    'f35v': ('ALH', None, 'MEDIUM', False, 'stellate/palmate leaves'),
    'f36r': ('AF', 'MH', 'MEDIUM', False, 'clustered flower heads'),
    'f37v': ('AS', 'RT', 'MEDIUM', False, 'tree-like, bay type'),
    'f38r': ('AF', None, 'HIGH', True, 'iris type, connected roots, orris root'),
    'f38v': ('ALH', None, 'MEDIUM', False, 'oval leaves'),
    'f42r': ('AF', 'MH', 'MEDIUM', True, 'connected plants, extensive roots'),
    'f45v': ('MH', 'AF', 'MEDIUM', False, 'spiny leaves, thistle'),
    'f47v': ('ALH', None, 'LOW', False, 'leaf study page'),
    'f49v': ('AF', None, 'HIGH', False, 'large basal leaves, feathery flower'),
    'f51v': ('MH', None, 'MEDIUM', False, 'spiny/serrated'),
    'f56r': ('AF', 'ALH', 'MEDIUM', False, 'palmate leaves, blue flowers'),
    'f3v': ('AF', 'MH', 'MEDIUM', False, 'lobed leaves, blue flower'),
}

# Classify by root emphasis (73% per PIAA)
root_emphasized_folios = {f for f, data in PLANT_CLASS_DATA.items() if data[3]}
non_root_folios = {f for f, data in PLANT_CLASS_DATA.items() if not data[3]}

# Classify by primary class
class_folios = defaultdict(set)
for f, data in PLANT_CLASS_DATA.items():
    class_folios[data[0]].add(f)

print(f"Root-emphasized folios: {len(root_emphasized_folios)}")
print(f"Non-root folios: {len(non_root_folios)}")
print(f"Classes: {dict((k, len(v)) for k, v in class_folios.items())}")

# ============================================================
# COMPUTE PREPARATION MIDDLE DENSITY PER FOLIO
# ============================================================
print("\n--- Computing Prep MIDDLE Density Per Folio ---")

# Brunschwig preparation operation mapping (from F-BRU-012)
# te = GATHER, pch = CHOP, lch = STRIP, tch = POUND, ksh = BREAK
PREP_MIDDLES = {
    'te': 'GATHER',
    'pch': 'CHOP',
    'lch': 'STRIP',
    'tch': 'POUND',
    'ksh': 'BREAK'
}

# Brunschwig material-operation alignment (X.31 from fits_brunschwig.md)
# Roots -> POUND, CHOP (dense, need breaking)
# Leaves -> STRIP, GATHER (delicate, need separation)
ROOT_OPS = {'tch', 'pch'}  # POUND, CHOP
LEAF_OPS = {'lch', 'te'}   # STRIP, GATHER

folio_prep_counts = defaultdict(lambda: defaultdict(int))
folio_total_tokens = defaultdict(int)

# Only use Currier A (herbal section with illustrations)
for t in tx.currier_a():
    m = morph.extract(t.word)
    if not m or not m.middle:
        continue

    folio_total_tokens[t.folio] += 1

    middle = m.middle
    for prep in PREP_MIDDLES:
        if prep in middle:
            folio_prep_counts[t.folio][prep] += 1

# Compute densities
folio_prep_densities = {}
for folio in folio_prep_counts:
    if folio_total_tokens[folio] < 20:
        continue

    total = folio_total_tokens[folio]
    densities = {
        prep: count / total
        for prep, count in folio_prep_counts[folio].items()
    }

    # Compute root_ops vs leaf_ops ratio
    root_ops_count = sum(folio_prep_counts[folio].get(op, 0) for op in ROOT_OPS)
    leaf_ops_count = sum(folio_prep_counts[folio].get(op, 0) for op in LEAF_OPS)

    folio_prep_densities[folio] = {
        'prep_densities': densities,
        'root_ops_density': root_ops_count / total,
        'leaf_ops_density': leaf_ops_count / total,
        'root_leaf_ratio': root_ops_count / leaf_ops_count if leaf_ops_count > 0 else float('inf'),
        'total_tokens': total
    }

print(f"Computed prep densities for {len(folio_prep_densities)} folios")

# ============================================================
# CORRELATE ILLUSTRATION FEATURES WITH PREP PROFILES
# ============================================================
print("\n--- Correlating Illustration Features with Prep Profiles ---")

# Find folios in both datasets
common_folios = set(folio_prep_densities.keys()) & set(PLANT_CLASS_DATA.keys())
print(f"Folios with both illustration and text data: {len(common_folios)}")

# Separate by root emphasis
root_emphasis_densities = []
non_root_densities = []

for folio in common_folios:
    data = folio_prep_densities[folio]
    if folio in root_emphasized_folios:
        root_emphasis_densities.append(data)
    else:
        non_root_densities.append(data)

print(f"Root-emphasized folios with data: {len(root_emphasis_densities)}")
print(f"Non-root folios with data: {len(non_root_densities)}")

# ============================================================
# TEST 1: ROOT ILLUSTRATION -> ROOT OPS (tch, pch)
# ============================================================
print("\n--- Test 1: Root Illustration -> Root Ops (tch, pch) ---")

root_ill_root_ops = [d['root_ops_density'] for d in root_emphasis_densities]
nonroot_ill_root_ops = [d['root_ops_density'] for d in non_root_densities]

if root_ill_root_ops and nonroot_ill_root_ops:
    u_stat, p_val = stats.mannwhitneyu(root_ill_root_ops, nonroot_ill_root_ops, alternative='greater')

    print(f"Root-illustrated folios: mean root_ops = {np.mean(root_ill_root_ops):.4f} (n={len(root_ill_root_ops)})")
    print(f"Non-root folios: mean root_ops = {np.mean(nonroot_ill_root_ops):.4f} (n={len(nonroot_ill_root_ops)})")
    print(f"Mann-Whitney U (one-sided): p = {p_val:.4f}")

    # Effect size (rank-biserial correlation)
    n1, n2 = len(root_ill_root_ops), len(nonroot_ill_root_ops)
    effect_size = (2 * u_stat) / (n1 * n2) - 1
    print(f"Effect size (rank-biserial): r = {effect_size:.3f}")

    test1_significant = p_val < 0.05
    test1_direction_correct = np.mean(root_ill_root_ops) > np.mean(nonroot_ill_root_ops)
    print(f"Significant (p < 0.05): {test1_significant}")
    print(f"Direction correct (root > non-root): {test1_direction_correct}")

# ============================================================
# TEST 2: NON-ROOT ILLUSTRATION -> LEAF OPS (lch, te)
# ============================================================
print("\n--- Test 2: Non-Root Illustration -> Leaf Ops (lch, te) ---")

root_ill_leaf_ops = [d['leaf_ops_density'] for d in root_emphasis_densities]
nonroot_ill_leaf_ops = [d['leaf_ops_density'] for d in non_root_densities]

if root_ill_leaf_ops and nonroot_ill_leaf_ops:
    u_stat, p_val = stats.mannwhitneyu(nonroot_ill_leaf_ops, root_ill_leaf_ops, alternative='greater')

    print(f"Non-root folios: mean leaf_ops = {np.mean(nonroot_ill_leaf_ops):.4f} (n={len(nonroot_ill_leaf_ops)})")
    print(f"Root-illustrated folios: mean leaf_ops = {np.mean(root_ill_leaf_ops):.4f} (n={len(root_ill_leaf_ops)})")
    print(f"Mann-Whitney U (one-sided): p = {p_val:.4f}")

    n1, n2 = len(nonroot_ill_leaf_ops), len(root_ill_leaf_ops)
    effect_size = (2 * u_stat) / (n1 * n2) - 1
    print(f"Effect size (rank-biserial): r = {effect_size:.3f}")

    test2_significant = p_val < 0.05
    test2_direction_correct = np.mean(nonroot_ill_leaf_ops) > np.mean(root_ill_leaf_ops)
    print(f"Significant (p < 0.05): {test2_significant}")
    print(f"Direction correct (non-root > root): {test2_direction_correct}")

# ============================================================
# TEST 3: ROOT/LEAF RATIO BY ILLUSTRATION TYPE
# ============================================================
print("\n--- Test 3: Root/Leaf Ops Ratio by Illustration Type ---")

root_ill_ratio = [d['root_leaf_ratio'] for d in root_emphasis_densities if d['root_leaf_ratio'] != float('inf')]
nonroot_ill_ratio = [d['root_leaf_ratio'] for d in non_root_densities if d['root_leaf_ratio'] != float('inf')]

if root_ill_ratio and nonroot_ill_ratio:
    u_stat, p_val = stats.mannwhitneyu(root_ill_ratio, nonroot_ill_ratio, alternative='greater')

    print(f"Root-illustrated folios: mean ratio = {np.mean(root_ill_ratio):.3f} (n={len(root_ill_ratio)})")
    print(f"Non-root folios: mean ratio = {np.mean(nonroot_ill_ratio):.3f} (n={len(nonroot_ill_ratio)})")
    print(f"Mann-Whitney U (one-sided): p = {p_val:.4f}")

    n1, n2 = len(root_ill_ratio), len(nonroot_ill_ratio)
    effect_size = (2 * u_stat) / (n1 * n2) - 1
    print(f"Effect size (rank-biserial): r = {effect_size:.3f}")

    test3_significant = p_val < 0.05
    print(f"Significant (p < 0.05): {test3_significant}")

# ============================================================
# TEST 4: PLANT CLASS -> PROCEDURAL PROFILE
# ============================================================
print("\n--- Test 4: Plant Class -> Procedural Profile ---")

class_profiles = {}
for cls, folios in class_folios.items():
    cls_folios_with_data = [f for f in folios if f in folio_prep_densities]
    if len(cls_folios_with_data) >= 3:
        class_profiles[cls] = {
            'n': len(cls_folios_with_data),
            'root_ops_mean': np.mean([folio_prep_densities[f]['root_ops_density'] for f in cls_folios_with_data]),
            'leaf_ops_mean': np.mean([folio_prep_densities[f]['leaf_ops_density'] for f in cls_folios_with_data])
        }

print(f"\n{'Class':<10} {'N':>5} {'Root Ops':>12} {'Leaf Ops':>12} {'Ratio':>10}")
print("-" * 55)
for cls, profile in sorted(class_profiles.items(), key=lambda x: -x[1]['root_ops_mean']):
    ratio = profile['root_ops_mean'] / profile['leaf_ops_mean'] if profile['leaf_ops_mean'] > 0 else float('inf')
    print(f"{cls:<10} {profile['n']:>5} {profile['root_ops_mean']:>12.4f} {profile['leaf_ops_mean']:>12.4f} {ratio:>10.2f}")

# ============================================================
# PER-PREP-MIDDLE BREAKDOWN
# ============================================================
print("\n--- Per-Prep-MIDDLE Breakdown by Illustration Type ---")

print(f"\n{'MIDDLE':<8} {'Operation':<10} {'Root-Ill':>12} {'Non-Root':>12} {'Ratio':>8}")
print("-" * 55)

for prep, operation in PREP_MIDDLES.items():
    root_vals = [d['prep_densities'].get(prep, 0) for d in root_emphasis_densities]
    nonroot_vals = [d['prep_densities'].get(prep, 0) for d in non_root_densities]

    root_mean = np.mean(root_vals) if root_vals else 0
    nonroot_mean = np.mean(nonroot_vals) if nonroot_vals else 0
    ratio = root_mean / nonroot_mean if nonroot_mean > 0 else float('inf')

    print(f"{prep:<8} {operation:<10} {root_mean:>12.5f} {nonroot_mean:>12.5f} {ratio:>8.2f}")

# ============================================================
# SAVE RESULTS
# ============================================================
output = {
    'phase': 'PROCEDURAL_DIMENSION_EXTENSION',
    'test': 'illustration_procedural_correlation',
    'tier': 4,
    'external_anchor': 'Brunschwig material-operation mapping',
    'sample_sizes': {
        'root_emphasized_folios': len(root_emphasis_densities),
        'non_root_folios': len(non_root_densities),
        'total_common_folios': len(common_folios)
    },
    'test_1_root_ops': {
        'prediction': 'Root illustrations -> higher tch/pch density',
        'root_ill_mean': float(np.mean(root_ill_root_ops)) if root_ill_root_ops else None,
        'nonroot_ill_mean': float(np.mean(nonroot_ill_root_ops)) if nonroot_ill_root_ops else None,
        'p_value': float(p_val) if 'p_val' in dir() else None,
        'significant': bool(test1_significant) if 'test1_significant' in dir() else None,
        'direction_correct': bool(test1_direction_correct) if 'test1_direction_correct' in dir() else None
    },
    'class_profiles': class_profiles,
    'brunschwig_alignment': {
        'root_ops': list(ROOT_OPS),
        'leaf_ops': list(LEAF_OPS),
        'mapping': PREP_MIDDLES
    }
}

output_path = PROJECT_ROOT / 'phases' / 'PROCEDURAL_DIMENSION_EXTENSION' / 'results' / 'illustration_procedural_correlation.json'
output_path.parent.mkdir(parents=True, exist_ok=True)
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2)

print(f"\n\nResults saved to: {output_path}")

# ============================================================
# VERDICT
# ============================================================
print("\n" + "="*70)
print("VERDICT: ILLUSTRATION-PROCEDURAL CORRELATION (TIER 4)")
print("="*70)

print(f"""
TIER 4 EXTERNAL ANCHOR TEST
==========================

Question: Do illustration features correlate with procedural profiles
in a way consistent with Brunschwig material processing?

External logic:
  Brunschwig says: "POUND/CHOP roots (dense), STRIP/GATHER leaves (delicate)"
  Voynich MIDDLEs: tch=POUND, pch=CHOP, lch=STRIP, te=GATHER

  If illustrations mark material categories, then:
  - Root-emphasized illustrations should have higher tch+pch
  - Leaf/flower illustrations should have higher lch+te

Results:
  Test 1 (Root illustration -> Root ops): {'PASS' if test1_significant and test1_direction_correct else 'FAIL' if 'test1_significant' in dir() else 'N/A'}
  Test 2 (Non-root -> Leaf ops): {'PASS' if test2_significant and test2_direction_correct else 'FAIL' if 'test2_significant' in dir() else 'N/A'}
  Test 3 (Root/Leaf ratio): {'PASS' if test3_significant else 'FAIL' if 'test3_significant' in dir() else 'N/A'}

Overall verdict:
""")

if 'test1_significant' in dir() and 'test2_significant' in dir():
    passed_tests = sum([
        test1_significant and test1_direction_correct,
        test2_significant and test2_direction_correct,
        test3_significant if 'test3_significant' in dir() else False
    ])

    if passed_tests >= 2:
        print("  STRONG - Illustration features correlate with Brunschwig-predicted processing")
        print("  This provides EXTERNAL SEMANTIC ANCHOR for material categories")
    elif passed_tests >= 1:
        print("  MODERATE - Partial correlation detected")
        print("  Further investigation recommended")
    else:
        print("  WEAK - No significant correlation")
        print("  Illustrations may not encode processing-relevant material categories")
else:
    print("  INSUFFICIENT DATA - Cannot evaluate")
