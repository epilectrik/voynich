"""
05_regime_procedural_profiles.py - Test if REGIMEs differ on procedural dimensions

Expected patterns:
- REGIME_4 (precision): Higher kch, lower ke
- REGIME_2 (gentle): Higher ke, balanced prep
- REGIME_3 (intense): Higher prep diversity
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
print("REGIME PROCEDURAL PROFILES")
print("="*70)

# ============================================================
# LOAD PROCEDURAL FEATURES
# ============================================================
print("\n--- Loading Procedural Features ---")

proc_path = PROJECT_ROOT / 'phases' / 'PROCEDURAL_DIMENSION_EXTENSION' / 'results' / 'procedural_features.json'
with open(proc_path, 'r', encoding='utf-8') as f:
    proc_data = json.load(f)

proc_features = proc_data['folio_features']
print(f"Loaded procedural features for {len(proc_features)} folios")

# ============================================================
# ASSIGN REGIMES TO FOLIOS
# ============================================================
print("\n--- Assigning REGIMEs to Folios ---")

# Build REGIME assignment based on kernel profiles (simplified from existing work)
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

# Assign REGIME based on kernel dominance
folio_regimes = {}
for folio, profile in folio_profiles.items():
    total = profile['total']
    if total == 0:
        continue

    k_rate = profile['k'] / total
    e_rate = profile['e'] / total
    h_rate = profile['h'] / total

    # REGIME assignment logic (from existing work)
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
# GROUP PROCEDURAL FEATURES BY REGIME
# ============================================================
print("\n--- Grouping Features by REGIME ---")

regime_features = defaultdict(list)

for folio, features in proc_features.items():
    regime = folio_regimes.get(folio)
    if regime:
        regime_features[regime].append(features)

for r in sorted(regime_features.keys()):
    print(f"  REGIME_{r}: {len(regime_features[r])} folios with procedural features")

# ============================================================
# COMPARE PROCEDURAL PROFILES BY REGIME
# ============================================================
print("\n--- Procedural Profiles by REGIME ---")

feature_names = [
    'prep_density', 'thermo_density', 'extended_density',
    'prep_thermo_ratio', 'ke_kch_ratio',
    'prep_mean_position', 'thermo_mean_position', 'extended_mean_position',
    'tier_spread', 'prep_diversity', 'qo_chsh_early_ratio', 'kernel_order_compliance'
]

regime_means = {}
for r in sorted(regime_features.keys()):
    regime_means[r] = {}
    for feat in feature_names:
        values = [f[feat] for f in regime_features[r]]
        regime_means[r][feat] = {
            'mean': np.mean(values),
            'std': np.std(values),
            'n': len(values)
        }

# Print comparison table
print(f"\n{'Feature':<25} {'R1':>10} {'R2':>10} {'R3':>10} {'R4':>10}")
print("-" * 70)

for feat in feature_names:
    row = f"{feat:<25}"
    for r in [1, 2, 3, 4]:
        if r in regime_means:
            mean = regime_means[r][feat]['mean']
            row += f" {mean:>9.3f}"
        else:
            row += f" {'N/A':>9}"
    print(row)

# ============================================================
# STATISTICAL TESTS
# ============================================================
print("\n--- Statistical Tests (Kruskal-Wallis) ---")

kw_results = {}

print(f"\n{'Feature':<25} {'H-stat':>10} {'p-value':>12} {'Significant'}")
print("-" * 60)

for feat in feature_names:
    groups = []
    for r in sorted(regime_features.keys()):
        values = [f[feat] for f in regime_features[r]]
        if len(values) >= 3:  # Need at least 3 for test
            groups.append(values)

    if len(groups) >= 2:
        h_stat, p_value = stats.kruskal(*groups)
        significant = p_value < 0.05
        kw_results[feat] = {
            'h_stat': float(h_stat),
            'p_value': float(p_value),
            'significant': significant
        }
        sig_marker = "***" if p_value < 0.001 else "**" if p_value < 0.01 else "*" if p_value < 0.05 else ""
        print(f"{feat:<25} {h_stat:>10.2f} {p_value:>12.4f} {sig_marker}")
    else:
        print(f"{feat:<25} {'N/A':>10} {'N/A':>12}")

# ============================================================
# KEY REGIME DIFFERENCES
# ============================================================
print("\n--- Key REGIME Differences ---")

# Test specific hypotheses
print("\n1. REGIME_4 (precision) vs others: ke_kch_ratio")
if 4 in regime_features:
    r4_ke_kch = [f['ke_kch_ratio'] for f in regime_features[4]]
    others_ke_kch = []
    for r in [1, 2, 3]:
        if r in regime_features:
            others_ke_kch.extend([f['ke_kch_ratio'] for f in regime_features[r]])

    if r4_ke_kch and others_ke_kch:
        u_stat, p_val = stats.mannwhitneyu(r4_ke_kch, others_ke_kch, alternative='two-sided')
        print(f"   REGIME_4 mean: {np.mean(r4_ke_kch):.3f}")
        print(f"   Others mean: {np.mean(others_ke_kch):.3f}")
        print(f"   Mann-Whitney U: p = {p_val:.4f}")
        print(f"   {'REGIME_4 has LOWER ke_kch (more kch/precision)' if np.mean(r4_ke_kch) < np.mean(others_ke_kch) else 'REGIME_4 has HIGHER ke_kch (more ke/sustained)'}")

print("\n2. REGIME_2 (gentle) vs REGIME_3 (intense): prep_diversity")
if 2 in regime_features and 3 in regime_features:
    r2_prep = [f['prep_diversity'] for f in regime_features[2]]
    r3_prep = [f['prep_diversity'] for f in regime_features[3]]

    u_stat, p_val = stats.mannwhitneyu(r2_prep, r3_prep, alternative='two-sided')
    print(f"   REGIME_2 mean: {np.mean(r2_prep):.3f}")
    print(f"   REGIME_3 mean: {np.mean(r3_prep):.3f}")
    print(f"   Mann-Whitney U: p = {p_val:.4f}")

print("\n3. REGIME_1 (standard) vs REGIME_4 (precision): tier_spread")
if 1 in regime_features and 4 in regime_features:
    r1_spread = [f['tier_spread'] for f in regime_features[1]]
    r4_spread = [f['tier_spread'] for f in regime_features[4]]

    u_stat, p_val = stats.mannwhitneyu(r1_spread, r4_spread, alternative='two-sided')
    print(f"   REGIME_1 mean: {np.mean(r1_spread):.3f}")
    print(f"   REGIME_4 mean: {np.mean(r4_spread):.3f}")
    print(f"   Mann-Whitney U: p = {p_val:.4f}")

print("\n4. Early qo ratio by REGIME (C863 validation):")
for r in sorted(regime_features.keys()):
    qo_ratios = [f['qo_chsh_early_ratio'] for f in regime_features[r]]
    print(f"   REGIME_{r}: qo_early_ratio = {np.mean(qo_ratios):.3f} (n={len(qo_ratios)})")

# ============================================================
# EFFECT SIZES
# ============================================================
print("\n--- Effect Sizes (Eta-squared) ---")

for feat in feature_names:
    groups = []
    all_values = []
    for r in sorted(regime_features.keys()):
        values = [f[feat] for f in regime_features[r]]
        if values:
            groups.append(values)
            all_values.extend(values)

    if len(groups) >= 2 and all_values:
        # Compute eta-squared
        grand_mean = np.mean(all_values)
        ss_between = sum(len(g) * (np.mean(g) - grand_mean)**2 for g in groups)
        ss_total = sum((v - grand_mean)**2 for v in all_values)
        eta_sq = ss_between / ss_total if ss_total > 0 else 0

        if feat in kw_results and kw_results[feat]['significant']:
            print(f"  {feat:<25} eta² = {eta_sq:.3f} {'(LARGE)' if eta_sq > 0.14 else '(MEDIUM)' if eta_sq > 0.06 else '(SMALL)'}")

# ============================================================
# SAVE RESULTS
# ============================================================
output = {
    'phase': 'PROCEDURAL_DIMENSION_EXTENSION',
    'test': 'regime_procedural_profiles',
    'regime_counts': dict(regime_counts),
    'regime_means': {
        str(r): {
            feat: regime_means[r][feat]
            for feat in feature_names
        }
        for r in regime_means.keys()
    },
    'kruskal_wallis': kw_results,
    'significant_features': [f for f, r in kw_results.items() if r['significant']]
}

output_path = PROJECT_ROOT / 'phases' / 'PROCEDURAL_DIMENSION_EXTENSION' / 'results' / 'regime_procedural_profiles.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2)

print(f"\n\nResults saved to: {output_path}")

# ============================================================
# VERDICT
# ============================================================
print("\n" + "="*70)
print("VERDICT: REGIME PROCEDURAL PROFILES")
print("="*70)

significant_count = sum(1 for r in kw_results.values() if r['significant'])
total_features = len(kw_results)

print(f"""
Do REGIMEs differ on procedural dimensions?

Significant features: {significant_count}/{total_features}

Significant differences (p < 0.05):
""")

for feat, result in kw_results.items():
    if result['significant']:
        print(f"  - {feat}: H = {result['h_stat']:.2f}, p = {result['p_value']:.4f}")

print(f"""
Key findings:
""")

# Summarize key findings
if 4 in regime_means and 1 in regime_means:
    r4_kch = regime_means[4]['ke_kch_ratio']['mean']
    r1_kch = regime_means[1]['ke_kch_ratio']['mean']
    print(f"  - REGIME_4 ke_kch_ratio: {r4_kch:.3f} vs REGIME_1: {r1_kch:.3f}")
    if r4_kch < r1_kch:
        print(f"    -> REGIME_4 uses MORE kch (precision mode) as expected")

if 3 in regime_means and 2 in regime_means:
    r3_prep = regime_means[3]['prep_diversity']['mean']
    r2_prep = regime_means[2]['prep_diversity']['mean']
    print(f"  - REGIME_3 prep_diversity: {r3_prep:.3f} vs REGIME_2: {r2_prep:.3f}")

print(f"""
Verdict: {'STRONG - REGIMEs show distinct procedural profiles' if significant_count >= 4 else 'MODERATE - Some REGIME differentiation' if significant_count >= 2 else 'WEAK - Limited REGIME differentiation'}
""")
