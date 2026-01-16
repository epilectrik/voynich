"""
STEP 3C: RE-DERIVE A/B DISJOINTNESS (H-only)
============================================
Confirm:
- Vocabulary overlap
- TTR differences
- Structural separation
"""
import pandas as pd
import numpy as np
from collections import Counter
import json

print("=" * 70)
print("STEP 3C: A/B DISJOINTNESS RE-DERIVATION (H-only)")
print("=" * 70)

# Load PRIMARY track only
df_raw = pd.read_csv('data/transcriptions/interlinear_full_words.txt', sep='\t', low_memory=False)
df = df_raw[df_raw['transcriber'] == 'H'].copy()

a_df = df[df['language'] == 'A'].copy()
b_df = df[df['language'] == 'B'].copy()

print(f"\nData:")
print(f"   Currier A: {len(a_df):,} tokens")
print(f"   Currier B: {len(b_df):,} tokens")

# =============================================================================
# 3C.1: VOCABULARY OVERLAP
# =============================================================================

print(f"\n3C.1: VOCABULARY OVERLAP")
print("-" * 40)

a_types = set(a_df['word'].dropna().str.lower())
b_types = set(b_df['word'].dropna().str.lower())

overlap = a_types & b_types
a_only = a_types - b_types
b_only = b_types - a_types

print(f"   A types: {len(a_types):,}")
print(f"   B types: {len(b_types):,}")
print(f"   Overlap: {len(overlap):,} ({100*len(overlap)/len(a_types|b_types):.1f}% of union)")
print(f"   A-only: {len(a_only):,} ({100*len(a_only)/len(a_types):.1f}% of A)")
print(f"   B-only: {len(b_only):,} ({100*len(b_only)/len(b_types):.1f}% of B)")

# Jaccard similarity
jaccard = len(overlap) / len(a_types | b_types)
print(f"   Jaccard(A,B): {jaccard:.4f}")

# =============================================================================
# 3C.2: TTR COMPARISON
# =============================================================================

print(f"\n3C.2: TYPE-TOKEN RATIO")
print("-" * 40)

ttr_a = len(a_types) / len(a_df)
ttr_b = len(b_types) / len(b_df)

print(f"   TTR(A): {ttr_a:.4f}")
print(f"   TTR(B): {ttr_b:.4f}")
print(f"   Ratio: {ttr_a/ttr_b:.2f}x")

# C237 claims: TTR A=0.137, B=0.096
# Our values will be different with H-only

# =============================================================================
# 3C.3: TOKEN FREQUENCY DISTRIBUTIONS
# =============================================================================

print(f"\n3C.3: FREQUENCY DISTRIBUTIONS")
print("-" * 40)

a_freq = Counter(a_df['word'].dropna().str.lower())
b_freq = Counter(b_df['word'].dropna().str.lower())

# Top tokens
print("   Top A tokens:")
for t, c in a_freq.most_common(5):
    print(f"      {t}: {c} ({100*c/len(a_df):.1f}%)")

print("\n   Top B tokens:")
for t, c in b_freq.most_common(5):
    print(f"      {t}: {c} ({100*c/len(b_df):.1f}%)")

# Hapax legomena
a_hapax = sum(1 for c in a_freq.values() if c == 1)
b_hapax = sum(1 for c in b_freq.values() if c == 1)
print(f"\n   A hapax: {a_hapax} ({100*a_hapax/len(a_types):.1f}% of types)")
print(f"   B hapax: {b_hapax} ({100*b_hapax/len(b_types):.1f}% of types)")

# =============================================================================
# 3C.4: LINE STRUCTURE
# =============================================================================

print(f"\n3C.4: LINE STRUCTURE")
print("-" * 40)

a_lines = a_df.groupby(['folio', 'line_number']).size()
b_lines = b_df.groupby(['folio', 'line_number']).size()

print(f"   A tokens/line: mean={a_lines.mean():.1f}, median={a_lines.median():.0f}")
print(f"   B tokens/line: mean={b_lines.mean():.1f}, median={b_lines.median():.0f}")

# =============================================================================
# 3C.5: STRUCTURAL SEPARATION
# =============================================================================

print(f"\n3C.5: STRUCTURAL SEPARATION")
print("-" * 40)

# Do A tokens appear in B contexts (transition to B-only tokens)?
# This tests whether A and B are truly disjoint systems

# Tokens that appear in both but with different behavior
common_tokens = list(overlap)[:20]

print(f"   Sample shared tokens: {common_tokens[:10]}")

# For a few shared tokens, check frequency ratio
print(f"\n   Frequency ratio (A/B) for shared tokens:")
for t in common_tokens[:5]:
    a_ct = a_freq.get(t, 0)
    b_ct = b_freq.get(t, 0)
    if b_ct > 0:
        ratio = a_ct / b_ct
        print(f"      {t}: {a_ct}/{b_ct} = {ratio:.2f}")

# =============================================================================
# SUMMARY
# =============================================================================

print(f"\n" + "=" * 70)
print("A/B DISJOINTNESS SUMMARY")
print("=" * 70)

results = {
    'a_tokens': len(a_df),
    'b_tokens': len(b_df),
    'a_types': len(a_types),
    'b_types': len(b_types),
    'overlap_types': len(overlap),
    'jaccard': jaccard,
    'ttr_a': ttr_a,
    'ttr_b': ttr_b,
    'a_hapax_pct': 100*a_hapax/len(a_types),
    'b_hapax_pct': 100*b_hapax/len(b_types),
}

# C229 claims: A and B are grammatically disjoint
# Key indicators:
# - Low Jaccard (vocabulary mostly separate)
# - Different TTR (A more repetitive)
# - Different line structures

disjoint = (
    jaccard < 0.5 and  # Less than 50% overlap
    abs(ttr_a - ttr_b) > 0.05  # Different TTR
)

if disjoint:
    print(f"\nSTATUS: A/B disjointness CONFIRMED")
    print(f"   Jaccard: {jaccard:.3f} (low = mostly separate)")
    print(f"   TTR difference: {abs(ttr_a-ttr_b):.3f}")
else:
    print(f"\nWARNING: A/B disjointness may need review")

with open('results/ab_disjointness_h_only.json', 'w') as f:
    json.dump(results, f, indent=2)
print(f"\nSaved to: results/ab_disjointness_h_only.json")
