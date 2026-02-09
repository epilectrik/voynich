"""
08_herb_regime2_pathway.py - Test herb-suffix -> REGIME_2 -> B pathway

Parallel to animal pathway (C884, C536):
  Animal: suffix -ey/-ol -> REGIME_4 -> k+e >> h kernel

This test:
  Herb: suffix -y/-dy -> REGIME_2 -> gentle B signature (ke elevated, low tch/pch)

External anchor (Brunschwig):
  - Herbs require gentle processing (fire degree 1-2)
  - REGIME_2 = "gentle" handling mode
  - Gentle processing = sustained heat (ke), minimal mechanical prep (low tch/pch)
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
print("HERB-SUFFIX -> REGIME_2 -> B PATHWAY TEST")
print("="*70)

# ============================================================
# STEP 1: IDENTIFY HERB VS ANIMAL PP TOKENS IN CURRIER A
# ============================================================
print("\n--- Step 1: Classifying A Tokens by Suffix Pattern ---")

# From C527: Animal PP: 78% -ey/-ol; Herb PP: 41% -y/-dy
ANIMAL_SUFFIXES = {'ey', 'ol', 'or', 'eey'}  # High-fire indicators
HERB_SUFFIXES = {'y', 'dy', 'edy'}  # Low-fire indicators (gentle processing)

# Collect PP tokens from Currier A
a_tokens_by_suffix_class = {'HERB': [], 'ANIMAL': [], 'MIXED': []}
a_folio_suffix_profile = defaultdict(lambda: {'herb': 0, 'animal': 0, 'total': 0})

for t in tx.currier_a():
    m = morph.extract(t.word)
    if not m or not m.middle:
        continue

    suffix = m.suffix or ''

    # Classify by suffix
    is_herb = any(suffix.endswith(s) for s in HERB_SUFFIXES)
    is_animal = any(suffix.endswith(s) for s in ANIMAL_SUFFIXES)

    if is_herb and not is_animal:
        a_tokens_by_suffix_class['HERB'].append({
            'word': t.word, 'folio': t.folio, 'middle': m.middle, 'suffix': suffix
        })
        a_folio_suffix_profile[t.folio]['herb'] += 1
    elif is_animal and not is_herb:
        a_tokens_by_suffix_class['ANIMAL'].append({
            'word': t.word, 'folio': t.folio, 'middle': m.middle, 'suffix': suffix
        })
        a_folio_suffix_profile[t.folio]['animal'] += 1
    else:
        a_tokens_by_suffix_class['MIXED'].append({
            'word': t.word, 'folio': t.folio, 'middle': m.middle, 'suffix': suffix
        })

    a_folio_suffix_profile[t.folio]['total'] += 1

print(f"HERB-suffix tokens: {len(a_tokens_by_suffix_class['HERB'])}")
print(f"ANIMAL-suffix tokens: {len(a_tokens_by_suffix_class['ANIMAL'])}")
print(f"MIXED/other tokens: {len(a_tokens_by_suffix_class['MIXED'])}")

# Compute herb ratio per A folio
a_folio_herb_ratio = {}
for folio, counts in a_folio_suffix_profile.items():
    if counts['total'] >= 10:
        a_folio_herb_ratio[folio] = counts['herb'] / counts['total']

print(f"\nA folios with sufficient tokens: {len(a_folio_herb_ratio)}")
print(f"Mean herb ratio: {np.mean(list(a_folio_herb_ratio.values())):.3f}")

# ============================================================
# STEP 2: EXTRACT PP BASES FROM HERB-DOMINANT A FOLIOS
# ============================================================
print("\n--- Step 2: Extracting PP Bases from Herb-Dominant A Folios ---")

# Classify A folios by herb dominance
HERB_THRESHOLD = 0.30  # Folios with >30% herb-suffix tokens
herb_dominant_folios = {f for f, r in a_folio_herb_ratio.items() if r > HERB_THRESHOLD}
animal_dominant_folios = {f for f, r in a_folio_herb_ratio.items() if r < 0.10}  # <10% herb = animal-leaning

print(f"Herb-dominant A folios (>{HERB_THRESHOLD*100:.0f}% herb suffix): {len(herb_dominant_folios)}")
print(f"Animal-dominant A folios (<10% herb suffix): {len(animal_dominant_folios)}")

# Extract PP bases (MIDDLEs) from each category
herb_pp_bases = set()
animal_pp_bases = set()

for t in tx.currier_a():
    m = morph.extract(t.word)
    if not m or not m.middle:
        continue

    if t.folio in herb_dominant_folios:
        herb_pp_bases.add(m.middle)
    elif t.folio in animal_dominant_folios:
        animal_pp_bases.add(m.middle)

herb_only_pp = herb_pp_bases - animal_pp_bases
animal_only_pp = animal_pp_bases - herb_pp_bases
shared_pp = herb_pp_bases & animal_pp_bases

print(f"\nPP bases from herb-dominant folios: {len(herb_pp_bases)}")
print(f"PP bases from animal-dominant folios: {len(animal_pp_bases)}")
print(f"Herb-only PP bases: {len(herb_only_pp)}")
print(f"Animal-only PP bases: {len(animal_only_pp)}")
print(f"Shared PP bases: {len(shared_pp)}")

# ============================================================
# STEP 3: ASSIGN REGIMES TO B FOLIOS
# ============================================================
print("\n--- Step 3: Assigning REGIMEs to B Folios ---")

# Build REGIME assignment based on kernel profiles
folio_profiles = defaultdict(lambda: {'k': 0, 'e': 0, 'h': 0, 'total': 0})

for t in tx.currier_b():
    m = morph.extract(t.word)
    if not m or not m.middle:
        continue

    folio_profiles[t.folio]['total'] += 1
    middle = m.middle

    if 'k' in middle:
        folio_profiles[t.folio]['k'] += 1
    if 'e' in middle:
        folio_profiles[t.folio]['e'] += 1
    if 'h' in middle or 'ch' in middle or 'sh' in middle:
        folio_profiles[t.folio]['h'] += 1

# Assign REGIME
folio_regimes = {}
for folio, profile in folio_profiles.items():
    total = profile['total']
    if total == 0:
        continue

    k_rate = profile['k'] / total
    e_rate = profile['e'] / total
    h_rate = profile['h'] / total

    # REGIME assignment logic
    if k_rate > 0.15:  # High k
        if h_rate < 0.10:
            folio_regimes[folio] = 4  # Precision
        else:
            folio_regimes[folio] = 3  # Intense
    elif e_rate > 0.12:  # High e
        folio_regimes[folio] = 2  # Gentle
    else:
        folio_regimes[folio] = 1  # Standard

regime_counts = defaultdict(int)
for r in folio_regimes.values():
    regime_counts[r] += 1

print("REGIME distribution:")
for r in sorted(regime_counts.keys()):
    print(f"  REGIME_{r}: {regime_counts[r]} folios")

# ============================================================
# STEP 4: COMPUTE B FOLIO OVERLAP WITH HERB PP BASES
# ============================================================
print("\n--- Step 4: Computing B Folio Overlap with Herb PP Bases ---")

b_folio_pp = defaultdict(set)
b_folio_tokens = defaultdict(list)

for t in tx.currier_b():
    m = morph.extract(t.word)
    if not m or not m.middle:
        continue

    b_folio_pp[t.folio].add(m.middle)
    b_folio_tokens[t.folio].append({'word': t.word, 'm': m})

# Compute overlap scores
b_folio_herb_overlap = {}
b_folio_animal_overlap = {}

for b_folio, pp_set in b_folio_pp.items():
    herb_overlap = len(pp_set & herb_pp_bases) / len(herb_pp_bases) if herb_pp_bases else 0
    animal_overlap = len(pp_set & animal_pp_bases) / len(animal_pp_bases) if animal_pp_bases else 0

    b_folio_herb_overlap[b_folio] = herb_overlap
    b_folio_animal_overlap[b_folio] = animal_overlap

print(f"B folios analyzed: {len(b_folio_herb_overlap)}")

# ============================================================
# STEP 5: TEST HERB OVERLAP -> REGIME_2 CORRELATION
# ============================================================
print("\n--- Step 5: Testing Herb Overlap -> REGIME Correlation ---")

# Get herb overlap values grouped by REGIME
regime_herb_overlaps = defaultdict(list)
for b_folio, overlap in b_folio_herb_overlap.items():
    regime = folio_regimes.get(b_folio)
    if regime:
        regime_herb_overlaps[regime].append(overlap)

print("\nHerb PP overlap by REGIME:")
for r in sorted(regime_herb_overlaps.keys()):
    overlaps = regime_herb_overlaps[r]
    print(f"  REGIME_{r}: mean = {np.mean(overlaps):.4f}, n = {len(overlaps)}")

# Test: Is REGIME_2 enriched for herb overlap?
if 2 in regime_herb_overlaps:
    r2_overlaps = regime_herb_overlaps[2]
    other_overlaps = []
    for r in [1, 3, 4]:
        if r in regime_herb_overlaps:
            other_overlaps.extend(regime_herb_overlaps[r])

    if r2_overlaps and other_overlaps:
        u_stat, p_val = stats.mannwhitneyu(r2_overlaps, other_overlaps, alternative='greater')
        print(f"\nREGIME_2 vs others (herb overlap):")
        print(f"  REGIME_2 mean: {np.mean(r2_overlaps):.4f}")
        print(f"  Others mean: {np.mean(other_overlaps):.4f}")
        print(f"  Mann-Whitney U (one-sided): p = {p_val:.4f}")
        print(f"  Direction: {'CORRECT (R2 > others)' if np.mean(r2_overlaps) > np.mean(other_overlaps) else 'WRONG'}")

# Kruskal-Wallis across all REGIMEs
groups = [regime_herb_overlaps[r] for r in sorted(regime_herb_overlaps.keys()) if len(regime_herb_overlaps[r]) >= 3]
if len(groups) >= 2:
    h_stat, kw_p = stats.kruskal(*groups)
    print(f"\nKruskal-Wallis (herb overlap by REGIME):")
    print(f"  H = {h_stat:.2f}, p = {kw_p:.4f}")

# ============================================================
# STEP 6: COMPUTE B FOLIO GENTLE SIGNATURES
# ============================================================
print("\n--- Step 6: Computing Gentle Processing Signatures in B ---")

# Gentle processing indicators:
# - ke elevated (sustained heat)
# - Low tch/pch (minimal mechanical prep)
# - High e relative to k (equilibration > intense heat)

GENTLE_OPS = {'ke', 'te', 'e'}  # Sustained/gentle operations
INTENSIVE_OPS = {'tch', 'pch', 'kch'}  # Intensive preparation/precision

b_folio_gentle_profile = {}

for b_folio, tokens in b_folio_tokens.items():
    if len(tokens) < 20:
        continue

    total = len(tokens)
    gentle_count = 0
    intensive_count = 0
    ke_count = 0
    e_count = 0
    k_count = 0

    for tok in tokens:
        middle = tok['m'].middle
        if not middle:
            continue

        # Count gentle vs intensive
        for g in GENTLE_OPS:
            if g in middle:
                gentle_count += 1
                break

        for i in INTENSIVE_OPS:
            if i in middle:
                intensive_count += 1
                break

        # Specific counts
        if 'ke' in middle and 'kch' not in middle:
            ke_count += 1
        if middle == 'e' or (middle.startswith('e') and 'k' not in middle):
            e_count += 1
        if 'k' in middle and 'e' not in middle:
            k_count += 1

    b_folio_gentle_profile[b_folio] = {
        'gentle_density': gentle_count / total,
        'intensive_density': intensive_count / total,
        'gentle_intensive_ratio': gentle_count / intensive_count if intensive_count > 0 else float('inf'),
        'ke_density': ke_count / total,
        'e_k_ratio': e_count / k_count if k_count > 0 else float('inf'),
        'total': total
    }

print(f"Computed gentle profiles for {len(b_folio_gentle_profile)} B folios")

# ============================================================
# STEP 7: TEST HERB OVERLAP -> GENTLE SIGNATURE CORRELATION
# ============================================================
print("\n--- Step 7: Testing Herb Overlap -> Gentle Signature Correlation ---")

# Get folios with both herb overlap and gentle profile
common_folios = set(b_folio_herb_overlap.keys()) & set(b_folio_gentle_profile.keys())
print(f"Common folios: {len(common_folios)}")

# Continuous correlation: herb overlap vs gentle metrics
herb_overlaps = [b_folio_herb_overlap[f] for f in common_folios]
gentle_densities = [b_folio_gentle_profile[f]['gentle_density'] for f in common_folios]
intensive_densities = [b_folio_gentle_profile[f]['intensive_density'] for f in common_folios]
ke_densities = [b_folio_gentle_profile[f]['ke_density'] for f in common_folios]

print("\nCorrelations (herb PP overlap vs B signatures):")

# Herb overlap vs gentle density (should be positive)
r_gentle, p_gentle = stats.pearsonr(herb_overlaps, gentle_densities)
print(f"  Herb overlap vs gentle_density: r = {r_gentle:.4f}, p = {p_gentle:.4f}")

# Herb overlap vs intensive density (should be negative)
r_intensive, p_intensive = stats.pearsonr(herb_overlaps, intensive_densities)
print(f"  Herb overlap vs intensive_density: r = {r_intensive:.4f}, p = {p_intensive:.4f}")

# Herb overlap vs ke density (should be positive - sustained gentle heat)
r_ke, p_ke = stats.pearsonr(herb_overlaps, ke_densities)
print(f"  Herb overlap vs ke_density: r = {r_ke:.4f}, p = {p_ke:.4f}")

# Spearman for robustness
rho_gentle, sp_gentle = stats.spearmanr(herb_overlaps, gentle_densities)
rho_intensive, sp_intensive = stats.spearmanr(herb_overlaps, intensive_densities)
print(f"\nSpearman correlations:")
print(f"  Herb overlap vs gentle_density: rho = {rho_gentle:.4f}, p = {sp_gentle:.4f}")
print(f"  Herb overlap vs intensive_density: rho = {rho_intensive:.4f}, p = {sp_intensive:.4f}")

# ============================================================
# STEP 8: COMPARE TO ANIMAL PATHWAY (CONTROL)
# ============================================================
print("\n--- Step 8: Animal Pathway Control Comparison ---")

animal_overlaps = [b_folio_animal_overlap[f] for f in common_folios]

# Animal overlap vs intensive (should be positive - animals need intensive processing)
r_animal_intensive, p_animal_intensive = stats.pearsonr(animal_overlaps, intensive_densities)
print(f"Animal overlap vs intensive_density: r = {r_animal_intensive:.4f}, p = {p_animal_intensive:.4f}")

# Animal overlap vs gentle (should be negative or zero)
r_animal_gentle, p_animal_gentle = stats.pearsonr(animal_overlaps, gentle_densities)
print(f"Animal overlap vs gentle_density: r = {r_animal_gentle:.4f}, p = {p_animal_gentle:.4f}")

# ============================================================
# STEP 9: REGIME_2 GENTLE SIGNATURE VALIDATION
# ============================================================
print("\n--- Step 9: REGIME_2 Gentle Signature Validation ---")

regime_gentle_profiles = defaultdict(list)
for b_folio in common_folios:
    regime = folio_regimes.get(b_folio)
    if regime:
        regime_gentle_profiles[regime].append(b_folio_gentle_profile[b_folio])

print("\nGentle metrics by REGIME:")
print(f"{'REGIME':<10} {'N':>5} {'Gentle':>10} {'Intensive':>12} {'ke':>10}")
print("-" * 50)
for r in sorted(regime_gentle_profiles.keys()):
    profiles = regime_gentle_profiles[r]
    n = len(profiles)
    gentle = np.mean([p['gentle_density'] for p in profiles])
    intensive = np.mean([p['intensive_density'] for p in profiles])
    ke = np.mean([p['ke_density'] for p in profiles])
    print(f"REGIME_{r:<3} {n:>5} {gentle:>10.4f} {intensive:>12.4f} {ke:>10.4f}")

# Test: Does REGIME_2 have highest gentle/lowest intensive?
if 2 in regime_gentle_profiles:
    r2_gentle = [p['gentle_density'] for p in regime_gentle_profiles[2]]
    r2_intensive = [p['intensive_density'] for p in regime_gentle_profiles[2]]

    other_gentle = []
    other_intensive = []
    for r in [1, 3, 4]:
        if r in regime_gentle_profiles:
            other_gentle.extend([p['gentle_density'] for p in regime_gentle_profiles[r]])
            other_intensive.extend([p['intensive_density'] for p in regime_gentle_profiles[r]])

    if r2_gentle and other_gentle:
        _, p_g = stats.mannwhitneyu(r2_gentle, other_gentle, alternative='greater')
        _, p_i = stats.mannwhitneyu(r2_intensive, other_intensive, alternative='less')
        print(f"\nREGIME_2 vs others:")
        print(f"  Gentle density higher? p = {p_g:.4f} {'*' if p_g < 0.05 else ''}")
        print(f"  Intensive density lower? p = {p_i:.4f} {'*' if p_i < 0.05 else ''}")

# ============================================================
# SAVE RESULTS
# ============================================================
output = {
    'phase': 'REVERSE_BRUNSCHWIG_V3',
    'test': 'herb_regime2_pathway',
    'tier': 4,
    'external_anchor': 'Brunschwig gentle processing (fire degree 1-2)',
    'sample_sizes': {
        'herb_suffix_tokens': len(a_tokens_by_suffix_class['HERB']),
        'animal_suffix_tokens': len(a_tokens_by_suffix_class['ANIMAL']),
        'herb_dominant_a_folios': len(herb_dominant_folios),
        'animal_dominant_a_folios': len(animal_dominant_folios),
        'herb_pp_bases': len(herb_pp_bases),
        'common_b_folios': len(common_folios)
    },
    'herb_overlap_regime_correlation': {
        'regime_means': {str(r): float(np.mean(regime_herb_overlaps[r])) for r in regime_herb_overlaps},
        'kruskal_wallis_p': float(kw_p) if 'kw_p' in dir() else None
    },
    'herb_gentle_correlations': {
        'herb_vs_gentle': {'r': float(r_gentle), 'p': float(p_gentle)},
        'herb_vs_intensive': {'r': float(r_intensive), 'p': float(p_intensive)},
        'herb_vs_ke': {'r': float(r_ke), 'p': float(p_ke)}
    },
    'animal_control': {
        'animal_vs_intensive': {'r': float(r_animal_intensive), 'p': float(p_animal_intensive)},
        'animal_vs_gentle': {'r': float(r_animal_gentle), 'p': float(p_animal_gentle)}
    }
}

output_path = PROJECT_ROOT / 'phases' / 'REVERSE_BRUNSCHWIG_V3' / 'results' / 'herb_regime2_pathway.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2)

print(f"\n\nResults saved to: {output_path}")

# ============================================================
# VERDICT
# ============================================================
print("\n" + "="*70)
print("VERDICT: HERB-SUFFIX -> REGIME_2 -> B PATHWAY")
print("="*70)

print(f"""
TIER 4 EXTERNAL ANCHOR TEST
===========================

Question: Do herb-suffix PP tokens route through REGIME_2 to B folios
with gentle processing signatures?

External anchor (Brunschwig):
  - Herbs require gentle processing (fire degree 1-2)
  - Gentle = sustained heat (ke), minimal mechanical prep (low tch/pch)

Parallel to animal pathway:
  Animal: -ey/-ol suffix -> REGIME_4 -> k+e >> h
  Herb:   -y/-dy suffix  -> REGIME_2 -> gentle signature?

Results:
""")

# Evaluate results
tests_passed = 0
total_tests = 4

# Test 1: Herb overlap correlates with gentle density
if p_gentle < 0.05 and r_gentle > 0:
    tests_passed += 1
    print(f"  1. Herb overlap -> gentle density: PASS (r={r_gentle:.3f}, p={p_gentle:.4f})")
else:
    print(f"  1. Herb overlap -> gentle density: FAIL (r={r_gentle:.3f}, p={p_gentle:.4f})")

# Test 2: Herb overlap anti-correlates with intensive density
if p_intensive < 0.05 and r_intensive < 0:
    tests_passed += 1
    print(f"  2. Herb overlap -> low intensive: PASS (r={r_intensive:.3f}, p={p_intensive:.4f})")
else:
    print(f"  2. Herb overlap -> low intensive: FAIL (r={r_intensive:.3f}, p={p_intensive:.4f})")

# Test 3: Herb overlap correlates with ke density
if p_ke < 0.05 and r_ke > 0:
    tests_passed += 1
    print(f"  3. Herb overlap -> ke density: PASS (r={r_ke:.3f}, p={p_ke:.4f})")
else:
    print(f"  3. Herb overlap -> ke density: FAIL (r={r_ke:.3f}, p={p_ke:.4f})")

# Test 4: Animal shows opposite pattern (control)
if p_animal_intensive < 0.05 and r_animal_intensive > 0:
    tests_passed += 1
    print(f"  4. Animal -> intensive (control): PASS (r={r_animal_intensive:.3f}, p={p_animal_intensive:.4f})")
else:
    print(f"  4. Animal -> intensive (control): FAIL (r={r_animal_intensive:.3f}, p={p_animal_intensive:.4f})")

print(f"""
Tests passed: {tests_passed}/4

Overall verdict: {'STRONG' if tests_passed >= 3 else 'MODERATE' if tests_passed >= 2 else 'WEAK' if tests_passed >= 1 else 'NULL'}
""")

if tests_passed >= 2:
    print("""This establishes the herb pathway parallel to animals:

  ANIMAL: suffix -ey/-ol -> REGIME_4 (precision) -> k+e >> h (tight tolerance)
  HERB:   suffix -y/-dy  -> REGIME_2 (gentle)    -> ke elevated (sustained gentle heat)

Both pathways are externally anchored via Brunschwig fire-degree protocols.
""")
