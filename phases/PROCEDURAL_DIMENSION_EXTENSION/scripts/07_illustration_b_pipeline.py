"""
07_illustration_b_pipeline.py - Corrected Tier 4 Test via A->B Pipeline

CORRECTION: Previous test looked for prep MIDDLEs in Currier A text.
But Currier A is the material REGISTRY - it identifies WHAT to process.
Processing operations appear in Currier B.

Correct test:
1. Identify A folios with root vs non-root illustrations
2. Extract PP bases that appear on those A folios
3. Find which B folios use those PP bases
4. Test if B folios receiving "root material" show higher tch/pch

External anchor logic (Tier 4):
- Brunschwig says: "POUND/CHOP roots (dense), STRIP/GATHER leaves (delicate)"
- Root illustrations mark materials that need root-processing
- B folios processing those materials should show root-processing operations
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
print("ILLUSTRATION-B PIPELINE (CORRECTED TIER 4 TEST)")
print("="*70)

# ============================================================
# PLANT CLASS DATA (from PIAA_plant_illustration)
# ============================================================
print("\n--- Loading Plant Class Assignments ---")

PLANT_CLASS_DATA = {
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

root_illustrated_folios = {f for f, data in PLANT_CLASS_DATA.items() if data[3]}
non_root_illustrated_folios = {f for f, data in PLANT_CLASS_DATA.items() if not data[3]}

print(f"Root-illustrated A folios: {len(root_illustrated_folios)}")
print(f"Non-root A folios: {len(non_root_illustrated_folios)}")

# ============================================================
# EXTRACT PP BASES FROM ILLUSTRATED A FOLIOS
# ============================================================
print("\n--- Extracting PP Bases from A Folios ---")

# Extract PP tokens from Currier A folios
root_pp_bases = set()
nonroot_pp_bases = set()

a_folio_pp = defaultdict(set)

for t in tx.currier_a():
    m = morph.extract(t.word)
    if not m or not m.middle:
        continue

    # Track PP bases (MIDDLE is the base)
    pp_base = m.middle

    a_folio_pp[t.folio].add(pp_base)

    if t.folio in root_illustrated_folios:
        root_pp_bases.add(pp_base)
    elif t.folio in non_root_illustrated_folios:
        nonroot_pp_bases.add(pp_base)

# Unique to root vs non-root
root_only_pp = root_pp_bases - nonroot_pp_bases
nonroot_only_pp = nonroot_pp_bases - root_pp_bases
shared_pp = root_pp_bases & nonroot_pp_bases

print(f"PP bases from root-illustrated folios: {len(root_pp_bases)}")
print(f"PP bases from non-root folios: {len(nonroot_pp_bases)}")
print(f"Root-only PP bases: {len(root_only_pp)}")
print(f"Non-root-only PP bases: {len(nonroot_only_pp)}")
print(f"Shared PP bases: {len(shared_pp)}")

# ============================================================
# FIND B FOLIOS USING THESE PP BASES
# ============================================================
print("\n--- Tracing PP Bases to B Folios ---")

# Build B folio -> PP base usage
b_folio_pp = defaultdict(set)
b_folio_tokens = defaultdict(list)

for t in tx.currier_b():
    m = morph.extract(t.word)
    if not m or not m.middle:
        continue

    b_folio_pp[t.folio].add(m.middle)
    b_folio_tokens[t.folio].append({'word': t.word, 'm': m})

# Compute overlap: which B folios use root-sourced vs non-root-sourced PP
b_folio_root_overlap = {}
b_folio_nonroot_overlap = {}

for b_folio, pp_set in b_folio_pp.items():
    root_overlap = len(pp_set & root_pp_bases) / len(root_pp_bases) if root_pp_bases else 0
    nonroot_overlap = len(pp_set & nonroot_pp_bases) / len(nonroot_pp_bases) if nonroot_pp_bases else 0

    b_folio_root_overlap[b_folio] = root_overlap
    b_folio_nonroot_overlap[b_folio] = nonroot_overlap

# Classify B folios by predominant source
HIGH_OVERLAP = 0.3  # Threshold for "uses these bases significantly"

b_root_sourced = {f for f, o in b_folio_root_overlap.items() if o > HIGH_OVERLAP and o > b_folio_nonroot_overlap.get(f, 0)}
b_nonroot_sourced = {f for f, o in b_folio_nonroot_overlap.items() if o > HIGH_OVERLAP and o > b_folio_root_overlap.get(f, 0)}

print(f"B folios predominantly using root-sourced PP: {len(b_root_sourced)}")
print(f"B folios predominantly using non-root-sourced PP: {len(b_nonroot_sourced)}")

# ============================================================
# COMPUTE PREP MIDDLE DENSITY IN B FOLIOS
# ============================================================
print("\n--- Computing Prep MIDDLEs in B Folios ---")

PREP_MIDDLES = {'te': 'GATHER', 'pch': 'CHOP', 'lch': 'STRIP', 'tch': 'POUND', 'ksh': 'BREAK'}
ROOT_OPS = {'tch', 'pch'}  # POUND, CHOP
LEAF_OPS = {'lch', 'te'}   # STRIP, GATHER

b_folio_prep = {}

for b_folio, tokens in b_folio_tokens.items():
    if len(tokens) < 20:
        continue

    total = len(tokens)
    prep_counts = defaultdict(int)

    for tok in tokens:
        middle = tok['m'].middle
        if middle:
            for prep in PREP_MIDDLES:
                if prep in middle:
                    prep_counts[prep] += 1

    root_ops_count = sum(prep_counts.get(op, 0) for op in ROOT_OPS)
    leaf_ops_count = sum(prep_counts.get(op, 0) for op in LEAF_OPS)

    b_folio_prep[b_folio] = {
        'root_ops_density': root_ops_count / total,
        'leaf_ops_density': leaf_ops_count / total,
        'root_leaf_ratio': root_ops_count / leaf_ops_count if leaf_ops_count > 0 else float('inf'),
        'prep_counts': dict(prep_counts),
        'total': total
    }

print(f"Computed prep profiles for {len(b_folio_prep)} B folios")

# ============================================================
# CORRELATION TEST: ROOT-SOURCED B vs ROOT OPS
# ============================================================
print("\n--- Test: Root-Sourced B Folios vs Root Ops Density ---")

# Get root_ops_density for root-sourced vs non-root-sourced B folios
root_sourced_densities = [b_folio_prep[f]['root_ops_density'] for f in b_root_sourced if f in b_folio_prep]
nonroot_sourced_densities = [b_folio_prep[f]['root_ops_density'] for f in b_nonroot_sourced if f in b_folio_prep]

# Also use overlap as continuous predictor
all_b_folios = [f for f in b_folio_prep.keys()]
root_overlap_values = [b_folio_root_overlap.get(f, 0) for f in all_b_folios]
root_ops_values = [b_folio_prep[f]['root_ops_density'] for f in all_b_folios]

print(f"\nContinuous correlation: root PP overlap vs root ops density")
if len(root_overlap_values) > 10:
    r, p = stats.pearsonr(root_overlap_values, root_ops_values)
    print(f"  Pearson r = {r:.4f}, p = {p:.4f}")

    rho, p_rho = stats.spearmanr(root_overlap_values, root_ops_values)
    print(f"  Spearman rho = {rho:.4f}, p = {p_rho:.4f}")

print(f"\nGroup comparison: root-sourced vs non-root-sourced B folios")
if root_sourced_densities and nonroot_sourced_densities:
    print(f"  Root-sourced B: mean root_ops = {np.mean(root_sourced_densities):.5f} (n={len(root_sourced_densities)})")
    print(f"  Non-root-sourced B: mean root_ops = {np.mean(nonroot_sourced_densities):.5f} (n={len(nonroot_sourced_densities)})")

    u_stat, p_val = stats.mannwhitneyu(root_sourced_densities, nonroot_sourced_densities, alternative='greater')
    print(f"  Mann-Whitney U (one-sided): p = {p_val:.4f}")

    if np.mean(root_sourced_densities) > np.mean(nonroot_sourced_densities):
        print("  Direction: CORRECT (root-sourced B has higher root ops)")
    else:
        print("  Direction: WRONG (root-sourced B has LOWER root ops)")

# ============================================================
# REGIME CORRELATION
# ============================================================
print("\n--- Alternative: Root PP -> REGIME Correlation ---")

# Load REGIME data if available
# Skip REGIME load for now - focus on main results
print("REGIME correlation deferred to integrated analysis")

# ============================================================
# DETAILED BREAKDOWN
# ============================================================
print("\n--- Prep MIDDLE Breakdown by B Folio Source ---")

print(f"\n{'MIDDLE':<8} {'Operation':<10} {'Root-Sourced':>14} {'NonRoot-Sourced':>16}")
print("-" * 55)

for prep, operation in PREP_MIDDLES.items():
    root_vals = [b_folio_prep[f]['prep_counts'].get(prep, 0) / b_folio_prep[f]['total']
                 for f in b_root_sourced if f in b_folio_prep]
    nonroot_vals = [b_folio_prep[f]['prep_counts'].get(prep, 0) / b_folio_prep[f]['total']
                    for f in b_nonroot_sourced if f in b_folio_prep]

    root_mean = np.mean(root_vals) if root_vals else 0
    nonroot_mean = np.mean(nonroot_vals) if nonroot_vals else 0

    print(f"{prep:<8} {operation:<10} {root_mean:>14.5f} {nonroot_mean:>16.5f}")

# ============================================================
# SAVE RESULTS
# ============================================================
output = {
    'phase': 'PROCEDURAL_DIMENSION_EXTENSION',
    'test': 'illustration_b_pipeline',
    'tier': 4,
    'methodology': 'A->B pipeline tracing',
    'sample_sizes': {
        'root_illustrated_a_folios': len(root_illustrated_folios),
        'nonroot_illustrated_a_folios': len(non_root_illustrated_folios),
        'root_pp_bases': len(root_pp_bases),
        'nonroot_pp_bases': len(nonroot_pp_bases),
        'b_root_sourced': len(b_root_sourced),
        'b_nonroot_sourced': len(b_nonroot_sourced)
    },
    'correlation': {
        'pearson_r': float(r) if 'r' in dir() and r is not None else None,
        'pearson_p': float(p) if 'p' in dir() and p is not None else None,
        'spearman_rho': float(rho) if 'rho' in dir() and rho is not None else None,
        'spearman_p': float(p_rho) if 'p_rho' in dir() and p_rho is not None else None
    }
}

output_path = PROJECT_ROOT / 'phases' / 'PROCEDURAL_DIMENSION_EXTENSION' / 'results' / 'illustration_b_pipeline.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2)

print(f"\n\nResults saved to: {output_path}")

# ============================================================
# VERDICT
# ============================================================
print("\n" + "="*70)
print("VERDICT: ILLUSTRATION-B PIPELINE (TIER 4)")
print("="*70)

print(f"""
CORRECTED TIER 4 TEST
=====================

Question: Do B folios that process root-illustrated materials
show higher root-processing operations (tch=POUND, pch=CHOP)?

Methodology:
  1. Identify root-illustrated A folios (n={len(root_illustrated_folios)})
  2. Extract PP bases appearing on those folios
  3. Find B folios with high overlap with root-sourced PP
  4. Test if those B folios have higher root ops density

Results:
""")

if 'r' in dir() and r is not None:
    print(f"  Continuous correlation (root PP overlap vs root ops):")
    print(f"    Pearson r = {r:.4f}, p = {p:.4f}")
    print(f"    Interpretation: {'SIGNIFICANT' if p < 0.05 else 'NOT significant'}")
    print(f"    Direction: {'CORRECT' if r > 0 else 'WRONG'}")

    if p < 0.05 and r > 0:
        print(f"""
VERDICT: MODERATE SUPPORT for external anchor
  - B folios that use more root-sourced vocabulary
    show {'higher' if r > 0 else 'lower'} root-processing operations
  - This is {'consistent' if r > 0 else 'inconsistent'} with Brunschwig's
    "POUND/CHOP roots" prescription
""")
    else:
        print(f"""
VERDICT: WEAK - No significant correlation
  - Illustration features do not predict B processing patterns
  - The A->B pipeline may not preserve material category information
""")
else:
    print("  INSUFFICIENT DATA for evaluation")
