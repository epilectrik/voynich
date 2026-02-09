"""
label_b_role_stats.py - Statistical validation of label PP base AX enrichment

Addresses expert requirements:
1. Chi-square test with p-value and effect size
2. Section-matched baseline (Pharma B baseline)
3. Per-folio variance check
4. Jar-only analysis with separate stats
"""
import sys
import json
from pathlib import Path
from collections import defaultdict, Counter
import numpy as np
from scipy import stats

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.voynich import Transcript, Morphology

tx = Transcript()
morph = Morphology()

print("="*70)
print("STATISTICAL VALIDATION: LABEL PP BASE AX ENRICHMENT")
print("="*70)

# Role classification by prefix (from C570-C571)
EN_PREFIXES = {'ch', 'sh', 'qo'}
AX_MED_PREFIXES = {'ok', 'ot'}

def classify_role(prefix):
    if prefix in EN_PREFIXES:
        return 'EN'
    elif prefix in AX_MED_PREFIXES:
        return 'AX_MED'
    elif prefix is None or prefix == '' or prefix == 'o':
        return 'AX_FINAL'
    else:
        return 'OTHER'

def is_ax(role):
    return role in ['AX_MED', 'AX_FINAL', 'AX_INIT']

# ============================================================
# STEP 1: LOAD LABEL DATA
# ============================================================
print("\n--- Step 1: Loading Label Data ---")

pipeline_path = PROJECT_ROOT / 'phases' / 'LABEL_INVESTIGATION' / 'results' / 'label_b_pipeline.json'
with open(pipeline_path, 'r', encoding='utf-8') as f:
    pipeline_data = json.load(f)

# Classify labels
label_pp_bases = set()
jar_pp_bases = set()
content_pp_bases = set()
pp_base_to_labels = defaultdict(list)

for label in pipeline_data['label_details']:
    pp_base = label.get('pp_base')
    if pp_base:
        label_pp_bases.add(pp_base)
        pp_base_to_labels[pp_base].append(label)
        if label['type'] == 'jar':
            jar_pp_bases.add(pp_base)
        elif label['type'] in ['root', 'leaf']:
            content_pp_bases.add(pp_base)

print(f"Total unique PP bases: {len(label_pp_bases)}")
print(f"Jar PP bases: {len(jar_pp_bases)}")
print(f"Content PP bases: {len(content_pp_bases)}")

# ============================================================
# STEP 2: BUILD SECTION-SPECIFIC BASELINES
# ============================================================
print("\n--- Step 2: Building Section Baselines ---")

# Get Pharma B tokens specifically
pharma_roles = Counter()
pharma_total = 0

global_roles = Counter()
global_total = 0

# Also track per-folio for label folios
folio_roles = defaultdict(Counter)

for t in tx.currier_b():
    m = morph.extract(t.word)
    if not m:
        continue

    role = classify_role(m.prefix)
    global_roles[role] += 1
    global_total += 1

    # Check if Pharma section
    if hasattr(t, 'section') and t.section == 'P':
        pharma_roles[role] += 1
        pharma_total += 1

    folio_roles[t.folio][role] += 1

print(f"Global B tokens: {global_total}")
print(f"Pharma B tokens: {pharma_total}")

print(f"\nGlobal B role distribution:")
for role in ['EN', 'AX_MED', 'AX_FINAL', 'OTHER']:
    pct = 100 * global_roles[role] / global_total if global_total > 0 else 0
    print(f"  {role}: {pct:.1f}%")

print(f"\nPharma B role distribution:")
for role in ['EN', 'AX_MED', 'AX_FINAL', 'OTHER']:
    pct = 100 * pharma_roles[role] / pharma_total if pharma_total > 0 else 0
    print(f"  {role}: {pct:.1f}%")

# ============================================================
# STEP 3: LABEL PP BASE ROLE DISTRIBUTION
# ============================================================
print("\n--- Step 3: Label PP Base Role Distribution ---")

label_roles = Counter()
label_total = 0

jar_roles = Counter()
jar_total = 0

content_roles = Counter()
content_total = 0

# Per-folio for label PP bases
label_pp_folio_roles = defaultdict(lambda: {'ax': 0, 'non_ax': 0})

for t in tx.currier_b():
    m = morph.extract(t.word)
    if not m or not m.middle:
        continue

    role = classify_role(m.prefix)

    # Check if MIDDLE contains any label PP base
    for pp_base in label_pp_bases:
        if pp_base in m.middle:
            label_roles[role] += 1
            label_total += 1

            if is_ax(role):
                label_pp_folio_roles[t.folio]['ax'] += 1
            else:
                label_pp_folio_roles[t.folio]['non_ax'] += 1

            if pp_base in jar_pp_bases:
                jar_roles[role] += 1
                jar_total += 1

            if pp_base in content_pp_bases:
                content_roles[role] += 1
                content_total += 1

            break  # Count each token once

print(f"\nLabel PP base role distribution (n={label_total}):")
for role in ['EN', 'AX_MED', 'AX_FINAL', 'OTHER']:
    pct = 100 * label_roles[role] / label_total if label_total > 0 else 0
    print(f"  {role}: {pct:.1f}%")

# ============================================================
# STEP 4: CHI-SQUARE TESTS
# ============================================================
print("\n--- Step 4: Statistical Tests ---")

def chi_square_ax_enrichment(observed_roles, expected_roles, obs_total, exp_total):
    """Test AX vs non-AX enrichment."""
    obs_ax = observed_roles.get('AX_MED', 0) + observed_roles.get('AX_FINAL', 0) + observed_roles.get('AX_INIT', 0)
    obs_non_ax = obs_total - obs_ax

    exp_ax = expected_roles.get('AX_MED', 0) + expected_roles.get('AX_FINAL', 0) + expected_roles.get('AX_INIT', 0)
    exp_non_ax = exp_total - exp_ax

    # Expected rates
    exp_ax_rate = exp_ax / exp_total if exp_total > 0 else 0
    exp_non_ax_rate = exp_non_ax / exp_total if exp_total > 0 else 0

    # Observed rates
    obs_ax_rate = obs_ax / obs_total if obs_total > 0 else 0

    # Contingency table
    # [label_ax, label_non_ax]
    # [baseline_ax, baseline_non_ax]
    contingency = np.array([
        [obs_ax, obs_non_ax],
        [exp_ax, exp_non_ax]
    ])

    chi2, p, dof, expected = stats.chi2_contingency(contingency)

    # Cramer's V
    n = contingency.sum()
    cramers_v = np.sqrt(chi2 / (n * (min(contingency.shape) - 1)))

    return {
        'obs_ax': obs_ax,
        'obs_non_ax': obs_non_ax,
        'obs_ax_rate': obs_ax_rate,
        'exp_ax_rate': exp_ax_rate,
        'enrichment': obs_ax_rate / exp_ax_rate if exp_ax_rate > 0 else 0,
        'chi2': chi2,
        'p': p,
        'cramers_v': cramers_v
    }

# Test 1: Label PP vs Global B baseline
print("\n=== Test 1: Label PP vs Global B Baseline ===")
result1 = chi_square_ax_enrichment(label_roles, global_roles, label_total, global_total)
print(f"  Label PP AX rate: {100*result1['obs_ax_rate']:.1f}%")
print(f"  Global B AX rate: {100*result1['exp_ax_rate']:.1f}%")
print(f"  Enrichment: {result1['enrichment']:.2f}x")
print(f"  Chi-square: {result1['chi2']:.2f}")
print(f"  p-value: {result1['p']:.2e}")
print(f"  Cramer's V: {result1['cramers_v']:.3f}")

# Test 2: Label PP vs Pharma B baseline
print("\n=== Test 2: Label PP vs Pharma B Baseline ===")
if pharma_total > 0:
    result2 = chi_square_ax_enrichment(label_roles, pharma_roles, label_total, pharma_total)
    print(f"  Label PP AX rate: {100*result2['obs_ax_rate']:.1f}%")
    print(f"  Pharma B AX rate: {100*result2['exp_ax_rate']:.1f}%")
    print(f"  Enrichment: {result2['enrichment']:.2f}x")
    print(f"  Chi-square: {result2['chi2']:.2f}")
    print(f"  p-value: {result2['p']:.2e}")
    print(f"  Cramer's V: {result2['cramers_v']:.3f}")
else:
    print("  No Pharma B tokens found - using global baseline")
    result2 = result1

# Test 3: Jar PP only vs Global B baseline
print("\n=== Test 3: Jar PP Only vs Global B Baseline ===")
result3 = chi_square_ax_enrichment(jar_roles, global_roles, jar_total, global_total)
print(f"  Jar PP AX rate: {100*result3['obs_ax_rate']:.1f}%")
print(f"  Global B AX rate: {100*result3['exp_ax_rate']:.1f}%")
print(f"  Enrichment: {result3['enrichment']:.2f}x")
print(f"  Chi-square: {result3['chi2']:.2f}")
print(f"  p-value: {result3['p']:.2e}")
print(f"  Cramer's V: {result3['cramers_v']:.3f}")

# Test 4: Content PP only vs Global B baseline
print("\n=== Test 4: Content PP Only vs Global B Baseline ===")
result4 = chi_square_ax_enrichment(content_roles, global_roles, content_total, global_total)
print(f"  Content PP AX rate: {100*result4['obs_ax_rate']:.1f}%")
print(f"  Global B AX rate: {100*result4['exp_ax_rate']:.1f}%")
print(f"  Enrichment: {result4['enrichment']:.2f}x")
print(f"  Chi-square: {result4['chi2']:.2f}")
print(f"  p-value: {result4['p']:.2e}")
print(f"  Cramer's V: {result4['cramers_v']:.3f}")

# ============================================================
# STEP 5: PER-FOLIO VARIANCE
# ============================================================
print("\n--- Step 5: Per-Folio Variance ---")

folio_ax_rates = []
for folio, counts in label_pp_folio_roles.items():
    total = counts['ax'] + counts['non_ax']
    if total >= 10:  # Minimum sample
        rate = counts['ax'] / total
        folio_ax_rates.append((folio, rate, total))

folio_ax_rates.sort(key=lambda x: x[1], reverse=True)

print(f"\nFolios with label PP bases (n>=10):")
print(f"{'Folio':<10} {'AX Rate':<10} {'Count'}")
print("-" * 30)
for folio, rate, total in folio_ax_rates[:10]:
    print(f"{folio:<10} {100*rate:>6.1f}%    {total}")

if folio_ax_rates:
    rates = [x[1] for x in folio_ax_rates]
    print(f"\nAX rate across folios:")
    print(f"  Mean: {100*np.mean(rates):.1f}%")
    print(f"  Std:  {100*np.std(rates):.1f}%")
    print(f"  Range: {100*min(rates):.1f}% - {100*max(rates):.1f}%")

# ============================================================
# STEP 6: JAR AX_FINAL SPECIFIC TEST
# ============================================================
print("\n--- Step 6: Jar AX_FINAL Specific Analysis ---")

jar_ax_final = jar_roles.get('AX_FINAL', 0)
jar_ax_final_rate = jar_ax_final / jar_total if jar_total > 0 else 0

global_ax_final = global_roles.get('AX_FINAL', 0)
global_ax_final_rate = global_ax_final / global_total if global_total > 0 else 0

content_ax_final = content_roles.get('AX_FINAL', 0)
content_ax_final_rate = content_ax_final / content_total if content_total > 0 else 0

print(f"AX_FINAL rates:")
print(f"  Jar PP bases: {100*jar_ax_final_rate:.1f}%")
print(f"  Content PP bases: {100*content_ax_final_rate:.1f}%")
print(f"  Global B baseline: {100*global_ax_final_rate:.1f}%")

# Jar vs baseline for AX_FINAL specifically
contingency_jar_axf = np.array([
    [jar_ax_final, jar_total - jar_ax_final],
    [global_ax_final, global_total - global_ax_final]
])
chi2_jar, p_jar, _, _ = stats.chi2_contingency(contingency_jar_axf)
print(f"\nJar AX_FINAL vs baseline:")
print(f"  Enrichment: {jar_ax_final_rate / global_ax_final_rate:.2f}x")
print(f"  Chi-square: {chi2_jar:.2f}")
print(f"  p-value: {p_jar:.2e}")

# ============================================================
# SAVE RESULTS
# ============================================================
output = {
    'test1_global': {
        'obs_ax_rate': result1['obs_ax_rate'],
        'exp_ax_rate': result1['exp_ax_rate'],
        'enrichment': result1['enrichment'],
        'chi2': result1['chi2'],
        'p': result1['p'],
        'cramers_v': result1['cramers_v']
    },
    'test2_pharma': {
        'obs_ax_rate': result2['obs_ax_rate'],
        'exp_ax_rate': result2['exp_ax_rate'],
        'enrichment': result2['enrichment'],
        'chi2': result2['chi2'],
        'p': result2['p'],
        'cramers_v': result2['cramers_v']
    },
    'test3_jar': {
        'obs_ax_rate': result3['obs_ax_rate'],
        'exp_ax_rate': result3['exp_ax_rate'],
        'enrichment': result3['enrichment'],
        'chi2': result3['chi2'],
        'p': result3['p'],
        'cramers_v': result3['cramers_v']
    },
    'test4_content': {
        'obs_ax_rate': result4['obs_ax_rate'],
        'exp_ax_rate': result4['exp_ax_rate'],
        'enrichment': result4['enrichment'],
        'chi2': result4['chi2'],
        'p': result4['p'],
        'cramers_v': result4['cramers_v']
    },
    'jar_ax_final': {
        'rate': jar_ax_final_rate,
        'baseline': global_ax_final_rate,
        'enrichment': jar_ax_final_rate / global_ax_final_rate if global_ax_final_rate > 0 else 0,
        'chi2': chi2_jar,
        'p': p_jar
    },
    'folio_variance': {
        'mean_ax_rate': float(np.mean(rates)) if rates else 0,
        'std_ax_rate': float(np.std(rates)) if rates else 0
    }
}

output_path = PROJECT_ROOT / 'phases' / 'LABEL_INVESTIGATION' / 'results' / 'label_b_role_stats.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2)

print(f"\n\nResults saved to: {output_path}")

# ============================================================
# VERDICT
# ============================================================
print("\n" + "="*70)
print("STATISTICAL VERDICT")
print("="*70)

sig_threshold = 0.01
effect_threshold = 0.1

verdicts = []

if result1['p'] < sig_threshold and result1['cramers_v'] > effect_threshold:
    verdicts.append("Global baseline: SIGNIFICANT")
else:
    verdicts.append(f"Global baseline: NOT SIGNIFICANT (p={result1['p']:.2e}, V={result1['cramers_v']:.3f})")

if result3['p'] < sig_threshold:
    verdicts.append("Jar PP bases: SIGNIFICANT")
else:
    verdicts.append(f"Jar PP bases: NOT SIGNIFICANT (p={result3['p']:.2e})")

if p_jar < sig_threshold:
    verdicts.append(f"Jar AX_FINAL enrichment: SIGNIFICANT ({jar_ax_final_rate/global_ax_final_rate:.1f}x)")
else:
    verdicts.append(f"Jar AX_FINAL enrichment: NOT SIGNIFICANT")

print("\n".join(verdicts))

print(f"""

SUMMARY:
- Label PP bases show {100*result1['obs_ax_rate']:.1f}% AX roles vs {100*result1['exp_ax_rate']:.1f}% baseline
- Enrichment: {result1['enrichment']:.2f}x
- Chi-square: {result1['chi2']:.2f}, p = {result1['p']:.2e}
- Cramer's V: {result1['cramers_v']:.3f}

JAR SPECIFIC:
- Jar PP bases: {100*result3['obs_ax_rate']:.1f}% AX (enrichment {result3['enrichment']:.2f}x)
- Jar AX_FINAL: {100*jar_ax_final_rate:.1f}% vs {100*global_ax_final_rate:.1f}% baseline ({jar_ax_final_rate/global_ax_final_rate:.1f}x)

TIER RECOMMENDATION:
- {'Tier 2 (STRUCTURAL)' if result1['p'] < sig_threshold else 'Tier 3 (SPECULATIVE)'} for overall AX enrichment
- {'Tier 2 (STRUCTURAL)' if p_jar < sig_threshold else 'Tier 3 (SPECULATIVE)'} for jar AX_FINAL concentration
""")
