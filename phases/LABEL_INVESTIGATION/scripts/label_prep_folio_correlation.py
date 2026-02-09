"""
label_prep_folio_correlation.py - Check if prep-heavy B folios use more label vocabulary

Question: Do B folios with more preparation operations show higher label PP connectivity?
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
print("FOLIO-LEVEL: PREP OPERATIONS vs LABEL PP CONNECTIVITY")
print("="*70)

# Preparation MIDDLEs
PREP_MIDDLES = {'te', 'pch', 'lch', 'tch', 'ksh'}

# Load label PP bases
pipeline_path = PROJECT_ROOT / 'phases' / 'LABEL_INVESTIGATION' / 'results' / 'label_b_pipeline.json'
with open(pipeline_path, 'r', encoding='utf-8') as f:
    pipeline_data = json.load(f)

label_pp_bases = set()
for label in pipeline_data['label_details']:
    pp_base = label.get('pp_base')
    if pp_base and len(pp_base) >= 2:  # Only PP bases with 2+ chars
        label_pp_bases.add(pp_base)

print(f"Label PP bases (2+ chars): {len(label_pp_bases)}")

# ============================================================
# BUILD PER-FOLIO METRICS
# ============================================================
print("\n--- Building Per-Folio Metrics ---")

folio_data = defaultdict(lambda: {
    'total_tokens': 0,
    'prep_tokens': 0,
    'label_pp_tokens': 0,
    'unique_label_pps': set()
})

for t in tx.currier_b():
    m = morph.extract(t.word)
    if not m or not m.middle:
        continue

    fd = folio_data[t.folio]
    fd['total_tokens'] += 1

    # Check for prep MIDDLE
    for prep_m in PREP_MIDDLES:
        if prep_m in m.middle:
            fd['prep_tokens'] += 1
            break

    # Check for label PP base
    for pp in label_pp_bases:
        if pp in m.middle:
            fd['label_pp_tokens'] += 1
            fd['unique_label_pps'].add(pp)
            break

# Convert to rates
folio_metrics = []
for folio, data in folio_data.items():
    if data['total_tokens'] >= 50:  # Minimum sample
        folio_metrics.append({
            'folio': folio,
            'total': data['total_tokens'],
            'prep_rate': data['prep_tokens'] / data['total_tokens'],
            'label_pp_rate': data['label_pp_tokens'] / data['total_tokens'],
            'unique_label_pps': len(data['unique_label_pps'])
        })

print(f"Folios with sufficient tokens: {len(folio_metrics)}")

# ============================================================
# CORRELATION ANALYSIS
# ============================================================
print("\n--- Correlation: Prep Rate vs Label PP Rate ---")

prep_rates = [f['prep_rate'] for f in folio_metrics]
label_rates = [f['label_pp_rate'] for f in folio_metrics]

r, p = stats.pearsonr(prep_rates, label_rates)
rho, p_rho = stats.spearmanr(prep_rates, label_rates)

print(f"Pearson r: {r:.3f} (p={p:.4f})")
print(f"Spearman rho: {rho:.3f} (p={p_rho:.4f})")

# ============================================================
# HIGH-PREP vs LOW-PREP FOLIO COMPARISON
# ============================================================
print("\n--- High-Prep vs Low-Prep Folios ---")

# Split by median prep rate
median_prep = np.median(prep_rates)
high_prep = [f for f in folio_metrics if f['prep_rate'] >= median_prep]
low_prep = [f for f in folio_metrics if f['prep_rate'] < median_prep]

high_label_rate = np.mean([f['label_pp_rate'] for f in high_prep])
low_label_rate = np.mean([f['label_pp_rate'] for f in low_prep])

print(f"Median prep rate: {100*median_prep:.1f}%")
print(f"High-prep folios ({len(high_prep)}): mean label PP rate = {100*high_label_rate:.1f}%")
print(f"Low-prep folios ({len(low_prep)}): mean label PP rate = {100*low_label_rate:.1f}%")

# T-test
t, p_t = stats.ttest_ind(
    [f['label_pp_rate'] for f in high_prep],
    [f['label_pp_rate'] for f in low_prep]
)
print(f"T-test: t={t:.2f}, p={p_t:.4f}")

# ============================================================
# TOP/BOTTOM FOLIOS
# ============================================================
print("\n--- Top 10 High-Prep Folios ---")
sorted_by_prep = sorted(folio_metrics, key=lambda x: x['prep_rate'], reverse=True)

print(f"{'Folio':<10} {'Prep%':<8} {'LabelPP%':<10} {'Unique PPs'}")
print("-" * 40)
for f in sorted_by_prep[:10]:
    print(f"{f['folio']:<10} {100*f['prep_rate']:>5.1f}%  {100*f['label_pp_rate']:>6.1f}%    {f['unique_label_pps']}")

print("\n--- Bottom 10 Low-Prep Folios ---")
for f in sorted_by_prep[-10:]:
    print(f"{f['folio']:<10} {100*f['prep_rate']:>5.1f}%  {100*f['label_pp_rate']:>6.1f}%    {f['unique_label_pps']}")

# ============================================================
# VERDICT
# ============================================================
print("\n" + "="*70)
print("VERDICT")
print("="*70)

print(f"""
Folio-Level Correlation: Prep Operations vs Label PP Connectivity

Correlation:
  Pearson r = {r:.3f} (p = {p:.4f})
  Spearman rho = {rho:.3f} (p = {p_rho:.4f})

{'SIGNIFICANT' if p < 0.05 else 'NOT SIGNIFICANT'} correlation.

High-prep vs Low-prep Folios:
  High-prep mean label PP rate: {100*high_label_rate:.1f}%
  Low-prep mean label PP rate: {100*low_label_rate:.1f}%
  Difference: {100*(high_label_rate - low_label_rate):.1f} percentage points
  T-test p = {p_t:.4f}

Interpretation:
{'Folios with more preparation operations also have higher label PP connectivity.' if r > 0 and p < 0.05 else 'No clear relationship between preparation intensity and label PP connectivity.'}
""")
