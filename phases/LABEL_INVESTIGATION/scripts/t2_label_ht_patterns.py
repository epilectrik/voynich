"""
t2_label_ht_patterns.py - HT Patterns in Label Contexts

Goal: Test if C926 (HT-RI anti-correlation) extends to label contexts.

C926 says: RI 0.48x in lines with HT at line level.
C914 says: Labels are 3.7x RI-enriched.

Prediction: Label regions should show ~0.48 × 3.7 = 1.78x HT suppression.

This test:
1. Identifies folios with both labels (L placement) and text (P placement)
2. Measures HT density in each region type
3. Tests if HT is suppressed near RI-heavy labels
"""
import sys
import json
from pathlib import Path
from collections import Counter, defaultdict
import pandas as pd
import numpy as np
from scipy import stats

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.voynich import Transcript, Morphology

morph = Morphology()

print("="*70)
print("TEST 2: HT PATTERNS IN LABEL CONTEXTS")
print("="*70)

# ============================================================
# STEP 1: LOAD TRANSCRIPT DATA
# ============================================================
print("\n--- Step 1: Loading Transcript ---")

df = pd.read_csv(PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt',
                 sep='\t', low_memory=False)
df = df[df['transcriber'] == 'H']

# HT prefixes (from constraint system)
ht_prefixes = {'yk', 'do', 'yt', 'sa', 'al', 'op', 'pc', 'ta', 'ok', 'ot',
               'ol', 'or', 'od', 'os', 'of', 'om', 'on', 'oe', 'oa'}

# ============================================================
# STEP 2: IDENTIFY FOLIOS WITH LABELS
# ============================================================
print("\n--- Step 2: Finding Folios with Labels ---")

# Label placement codes start with 'L'
df['is_label'] = df['placement'].astype(str).str.match(r'^L')
df['is_paragraph'] = df['placement'].astype(str).str.match(r'^P')

# Find folios with both
label_folios = df[df['is_label']]['folio'].unique()
paragraph_folios = df[df['is_paragraph']]['folio'].unique()

# Folios with both labels and paragraphs
mixed_folios = set(label_folios) & set(paragraph_folios)

print(f"Folios with labels: {len(label_folios)}")
print(f"Folios with paragraphs: {len(paragraph_folios)}")
print(f"Folios with BOTH: {len(mixed_folios)}")

if mixed_folios:
    print(f"Mixed folios: {sorted(mixed_folios)[:10]}...")

# ============================================================
# STEP 3: CLASSIFY TOKENS AS HT
# ============================================================
print("\n--- Step 3: Classifying HT Tokens ---")

def is_ht(word):
    """Check if token has HT prefix."""
    if pd.isna(word) or not isinstance(word, str):
        return False
    m = morph.extract(word)
    return m is not None and m.prefix in ht_prefixes

df['is_ht'] = df['word'].apply(is_ht)

print(f"Total HT tokens: {df['is_ht'].sum()}")

# ============================================================
# STEP 4: MEASURE HT DENSITY BY REGION
# ============================================================
print("\n--- Step 4: HT Density by Region ---")

# For each folio, calculate HT density in labels vs paragraphs
results = []

for folio in mixed_folios:
    folio_df = df[df['folio'] == folio]

    # Label region
    label_df = folio_df[folio_df['is_label']]
    label_total = len(label_df)
    label_ht = label_df['is_ht'].sum()
    label_ht_rate = label_ht / label_total if label_total > 0 else 0

    # Paragraph region
    para_df = folio_df[folio_df['is_paragraph']]
    para_total = len(para_df)
    para_ht = para_df['is_ht'].sum()
    para_ht_rate = para_ht / para_total if para_total > 0 else 0

    results.append({
        'folio': folio,
        'label_tokens': label_total,
        'label_ht': label_ht,
        'label_ht_rate': label_ht_rate,
        'para_tokens': para_total,
        'para_ht': para_ht,
        'para_ht_rate': para_ht_rate
    })

results_df = pd.DataFrame(results)

print(f"\nPer-folio HT rates:")
print(results_df.to_string())

# Aggregate
total_label_tokens = results_df['label_tokens'].sum()
total_label_ht = results_df['label_ht'].sum()
total_para_tokens = results_df['para_tokens'].sum()
total_para_ht = results_df['para_ht'].sum()

label_ht_overall = total_label_ht / total_label_tokens if total_label_tokens > 0 else 0
para_ht_overall = total_para_ht / total_para_tokens if total_para_tokens > 0 else 0

print(f"\n--- Aggregate HT Density ---")
print(f"Labels: {total_label_ht}/{total_label_tokens} = {100*label_ht_overall:.1f}%")
print(f"Paragraphs: {total_para_ht}/{total_para_tokens} = {100*para_ht_overall:.1f}%")

if para_ht_overall > 0:
    ratio = label_ht_overall / para_ht_overall
    print(f"Label/Para ratio: {ratio:.2f}x")
else:
    ratio = None
    print("Cannot compute ratio (para HT = 0)")

# ============================================================
# STEP 5: STATISTICAL TEST
# ============================================================
print("\n--- Step 5: Statistical Test ---")

# Contingency table: Label vs Para × HT vs non-HT
contingency = np.array([
    [total_label_ht, total_label_tokens - total_label_ht],
    [total_para_ht, total_para_tokens - total_para_ht]
])

print(f"\nContingency table:")
print(f"           HT     non-HT")
print(f"Labels    {contingency[0,0]:4d}   {contingency[0,1]:4d}")
print(f"Para      {contingency[1,0]:4d}   {contingency[1,1]:4d}")

# Chi-square
if contingency.min() >= 5:
    chi2, p_value, dof, expected = stats.chi2_contingency(contingency)
    test_type = "chi-square"
else:
    # Use Fisher's exact for small samples
    odds, p_value = stats.fisher_exact(contingency)
    chi2 = None
    test_type = "Fisher's exact"

print(f"\n{test_type} test:")
if chi2:
    print(f"  chi2 = {chi2:.2f}")
print(f"  p-value = {p_value:.4f}")

# ============================================================
# STEP 6: COMPARE TO C926 PREDICTION
# ============================================================
print("\n--- Step 6: C926 Prediction Comparison ---")

# C926 says: RI is 0.48x in lines with HT
# Inverse: HT suppressed in RI-rich contexts
# Labels are RI-rich (C914: 3.7x)
# Prediction: HT should be suppressed in labels

predicted_suppression = 0.48  # From C926
actual_suppression = ratio if ratio else 0

print(f"C926 predicts HT at {predicted_suppression:.2f}x in RI-rich contexts")
print(f"Observed label/para HT ratio: {actual_suppression:.2f}x")

# Is it consistent?
if ratio and ratio < 1.0:
    consistency = "CONSISTENT with C926 (HT suppressed in labels)"
elif ratio and ratio > 1.0:
    consistency = "INCONSISTENT with C926 (HT elevated in labels)"
else:
    consistency = "UNCLEAR (no clear pattern)"

print(f"Assessment: {consistency}")

# ============================================================
# STEP 7: CONTROL FOR SECTION
# ============================================================
print("\n--- Step 7: Section Control ---")

# Get section for each folio
section_map = {}
for _, row in df.drop_duplicates('folio').iterrows():
    section_map[row['folio']] = row.get('section', 'unknown')

# Add section to results
results_df['section'] = results_df['folio'].map(section_map)
print(f"Sections represented: {results_df['section'].value_counts().to_dict()}")

# ============================================================
# VERDICT
# ============================================================
print("\n" + "="*70)
print("VERDICT: HT-LABEL INTERACTION")
print("="*70)

print(f"""
HT Density Analysis in Label vs Paragraph Contexts:

Sample:
  - Mixed folios analyzed: {len(mixed_folios)}
  - Label tokens: {total_label_tokens}
  - Paragraph tokens: {total_para_tokens}

HT Density:
  - Labels: {100*label_ht_overall:.1f}%
  - Paragraphs: {100*para_ht_overall:.1f}%
  - Ratio: {ratio:.2f}x (label/para)

Statistical Test:
  - {test_type}: p = {p_value:.4f}
  - Significant (p<0.05): {p_value < 0.05}

C926 Consistency:
  - Predicted: HT suppressed in RI-rich (label) contexts
  - Observed: {consistency}

FINDING: {'HT is suppressed in label contexts' if (ratio and ratio < 1.0 and p_value < 0.05) else 'No clear HT suppression in labels' if (ratio and ratio >= 1.0) else 'Insufficient data'}
""")

# ============================================================
# SAVE RESULTS
# ============================================================
output = {
    'test': 'label_ht_patterns',
    'goal': 'Test if C926 extends to label contexts',
    'sample': {
        'mixed_folios': len(mixed_folios),
        'label_tokens': int(total_label_tokens),
        'para_tokens': int(total_para_tokens)
    },
    'ht_density': {
        'labels': float(label_ht_overall),
        'paragraphs': float(para_ht_overall),
        'ratio': float(ratio) if ratio else None
    },
    'statistics': {
        'test_type': test_type,
        'p_value': float(p_value),
        'significant': bool(p_value < 0.05)
    },
    'c926_consistency': consistency,
    'per_folio': results_df.to_dict('records')
}

output_path = PROJECT_ROOT / 'phases' / 'LABEL_INVESTIGATION' / 'results' / 'label_ht_patterns.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2)

print(f"\nResults saved to: {output_path}")
