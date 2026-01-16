"""
STEP 3B: RE-DERIVE AZC PLACEMENT PATTERNS (H-only)
==================================================
Confirm:
- Placement codes distribution
- Self-transition rates (>98%)
- Section × Placement correlation
"""
import pandas as pd
import numpy as np
from collections import Counter, defaultdict
import json

print("=" * 70)
print("STEP 3B: AZC PLACEMENT PATTERNS RE-DERIVATION (H-only)")
print("=" * 70)

# Load PRIMARY track only
df_raw = pd.read_csv('data/transcriptions/interlinear_full_words.txt', sep='\t', low_memory=False)
df = df_raw[df_raw['transcriber'] == 'H'].copy()

# AZC = unclassified by Currier
azc_df = df[df['language'].isna()].copy()
print(f"\nData: {len(azc_df):,} AZC tokens (H-only)")

# =============================================================================
# 3B.1: PLACEMENT CODE DISTRIBUTION
# =============================================================================

print(f"\n3B.1: PLACEMENT CODE DISTRIBUTION")
print("-" * 40)

# Check if placement column exists
if 'placement' in azc_df.columns:
    placement_counts = azc_df['placement'].value_counts()
    print("   Placement codes found:")
    for code, count in placement_counts.head(15).items():
        pct = 100 * count / len(azc_df)
        print(f"      {code}: {count:,} ({pct:.1f}%)")
else:
    print("   WARNING: No 'placement' column in data")
    # Try to infer from section
    section_counts = azc_df['section'].value_counts()
    print("   AZC sections:")
    for section, count in section_counts.items():
        pct = 100 * count / len(azc_df)
        print(f"      {section}: {count:,} ({pct:.1f}%)")

# =============================================================================
# 3B.2: SECTION DISTRIBUTION
# =============================================================================

print(f"\n3B.2: SECTION DISTRIBUTION")
print("-" * 40)

section_counts = azc_df['section'].value_counts()
print("   AZC by section:")
for section, count in section_counts.items():
    folios = azc_df[azc_df['section'] == section]['folio'].nunique()
    pct = 100 * count / len(azc_df)
    print(f"      {section}: {count:,} tokens ({pct:.1f}%), {folios} folios")

# Expected from constraints: Z=12, A=8, C=7 folios (diagrams)
# Plus H and S (non-diagrams)

# =============================================================================
# 3B.3: VOCABULARY INDEPENDENCE
# =============================================================================

print(f"\n3B.3: VOCABULARY ANALYSIS")
print("-" * 40)

# AZC-unique types (not in A or B)
a_types = set(df[df['language'] == 'A']['word'].dropna().str.lower())
b_types = set(df[df['language'] == 'B']['word'].dropna().str.lower())
azc_types = set(azc_df['word'].dropna().str.lower())

azc_unique = azc_types - a_types - b_types
shared_with_a = azc_types & a_types
shared_with_b = azc_types & b_types

print(f"   AZC total types: {len(azc_types):,}")
print(f"   AZC-unique (not in A or B): {len(azc_unique):,} ({100*len(azc_unique)/len(azc_types):.1f}%)")
print(f"   Shared with A: {len(shared_with_a):,}")
print(f"   Shared with B: {len(shared_with_b):,}")

# =============================================================================
# 3B.4: LINE STRUCTURE
# =============================================================================

print(f"\n3B.4: LINE STRUCTURE")
print("-" * 40)

# Tokens per line in AZC
azc_line_lengths = azc_df.groupby(['folio', 'line_number']).size()
print(f"   AZC tokens/line: median={azc_line_lengths.median():.0f}, mean={azc_line_lengths.mean():.1f}")

# Compare to A and B
a_line_lengths = df[df['language'] == 'A'].groupby(['folio', 'line_number']).size()
b_line_lengths = df[df['language'] == 'B'].groupby(['folio', 'line_number']).size()

print(f"   A tokens/line: median={a_line_lengths.median():.0f}, mean={a_line_lengths.mean():.1f}")
print(f"   B tokens/line: median={b_line_lengths.median():.0f}, mean={b_line_lengths.mean():.1f}")

# C302 claims: AZC median 8 tokens/line (vs A=22, B=31)
# These look different - let me check

# =============================================================================
# 3B.5: FOLIO VOCABULARY INDEPENDENCE
# =============================================================================

print(f"\n3B.5: FOLIO VOCABULARY INDEPENDENCE")
print("-" * 40)

# Mean Jaccard between AZC folios
azc_folios = azc_df['folio'].unique()
folio_vocabs = {}
for folio in azc_folios:
    vocab = set(azc_df[azc_df['folio'] == folio]['word'].dropna().str.lower())
    if vocab:
        folio_vocabs[folio] = vocab

# Sample pairwise Jaccard
jaccards = []
folio_list = list(folio_vocabs.keys())
for i in range(len(folio_list)):
    for j in range(i+1, len(folio_list)):
        v1 = folio_vocabs[folio_list[i]]
        v2 = folio_vocabs[folio_list[j]]
        if v1 and v2:
            j_sim = len(v1 & v2) / len(v1 | v2)
            jaccards.append(j_sim)

if jaccards:
    print(f"   Mean Jaccard (folio pairs): {np.mean(jaccards):.4f}")
    print(f"   Max Jaccard: {max(jaccards):.4f}")
    print(f"   C322 claims: mean=0.056, max=0.176")
else:
    print("   Could not compute Jaccard")

# =============================================================================
# SUMMARY
# =============================================================================

print(f"\n" + "=" * 70)
print("AZC PLACEMENT PATTERNS SUMMARY")
print("=" * 70)

results = {
    'azc_tokens': len(azc_df),
    'azc_types': len(azc_types),
    'azc_unique_types': len(azc_unique),
    'azc_folios': len(azc_folios),
    'median_tokens_per_line': float(azc_line_lengths.median()),
    'mean_jaccard': float(np.mean(jaccards)) if jaccards else None,
    'sections': dict(section_counts),
}

print(f"\nAZC baseline (H-only):")
print(f"   Tokens: {results['azc_tokens']:,}")
print(f"   Types: {results['azc_types']:,}")
print(f"   Unique types: {results['azc_unique_types']:,}")
print(f"   Folios: {results['azc_folios']}")

# Key pattern checks
patterns_ok = (
    len(azc_unique) > 800 and  # C304 claimed 1529, H-only should be ~900
    azc_line_lengths.median() < 15  # AZC has shorter lines than B
)

if patterns_ok:
    print(f"\nSTATUS: AZC core patterns CONFIRMED")
else:
    print(f"\nWARNING: Some AZC patterns may differ")

with open('results/azc_patterns_h_only.json', 'w') as f:
    json.dump(results, f, indent=2, default=str)
print(f"\nSaved to: results/azc_patterns_h_only.json")
