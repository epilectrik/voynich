"""
PRIMARY TRACK VALIDATION
========================
Step 1: Re-tokenize from H (PRIMARY) transcriber only
Step 2: Validate token inventory, adjacency entropy, coverage

This establishes our clean baseline before re-deriving analyses.
"""
import pandas as pd
import numpy as np
from collections import Counter, defaultdict
from scipy.stats import entropy
import json

print("=" * 70)
print("PRIMARY TRACK (H) VALIDATION")
print("=" * 70)

# =============================================================================
# STEP 1: LOAD PRIMARY TRACK ONLY
# =============================================================================

df_raw = pd.read_csv('data/transcriptions/interlinear_full_words.txt', sep='\t', low_memory=False)

print(f"\n1. RAW DATA LOAD")
print("-" * 40)
print(f"   Total rows in transcript: {len(df_raw):,}")
print(f"   Transcribers present: {sorted(df_raw['transcriber'].dropna().unique())}")

# Filter to H only
df = df_raw[df_raw['transcriber'] == 'H'].copy()
print(f"\n   PRIMARY (H) rows: {len(df):,}")
print(f"   Reduction: {100*(1 - len(df)/len(df_raw)):.1f}%")

# =============================================================================
# STEP 2A: TOKEN INVENTORY SIZE
# =============================================================================

print(f"\n2A. TOKEN INVENTORY")
print("-" * 40)

# Overall
all_tokens = df['word'].dropna()
unique_all = len(all_tokens.unique())
print(f"   Total tokens: {len(all_tokens):,}")
print(f"   Unique types: {unique_all:,}")
print(f"   TTR (overall): {unique_all/len(all_tokens):.4f}")

# By Currier language
for lang in ['A', 'B']:
    subset = df[df['language'] == lang]['word'].dropna()
    unique = len(subset.unique())
    print(f"\n   Currier {lang}:")
    print(f"      Tokens: {len(subset):,}")
    print(f"      Unique types: {unique:,}")
    print(f"      TTR: {unique/len(subset):.4f}")

# AZC (unclassified)
azc = df[df['language'].isna()]['word'].dropna()
print(f"\n   AZC (unclassified):")
print(f"      Tokens: {len(azc):,}")
print(f"      Unique types: {len(azc.unique()):,}")

# =============================================================================
# STEP 2B: ADJACENCY ENTROPY
# =============================================================================

print(f"\n2B. ADJACENCY ENTROPY (Currier B)")
print("-" * 40)

def compute_adjacency_entropy(df_subset):
    """Compute bigram entropy grouped by line."""
    bigrams = []
    for (folio, line_num), group in df_subset.groupby(['folio', 'line_number']):
        words = group['word'].dropna().tolist()
        for i in range(len(words) - 1):
            bigrams.append((words[i], words[i+1]))

    if not bigrams:
        return 0, 0, 0

    # Bigram entropy
    bigram_counts = Counter(bigrams)
    total = sum(bigram_counts.values())
    probs = [c/total for c in bigram_counts.values()]
    bigram_ent = entropy(probs, base=2)

    # Unigram entropy for comparison
    unigram_counts = Counter(df_subset['word'].dropna())
    total_uni = sum(unigram_counts.values())
    probs_uni = [c/total_uni for c in unigram_counts.values()]
    unigram_ent = entropy(probs_uni, base=2)

    return len(bigrams), bigram_ent, unigram_ent

b_df = df[df['language'] == 'B']
n_bigrams, bigram_ent, unigram_ent = compute_adjacency_entropy(b_df)

print(f"   Bigram count: {n_bigrams:,}")
print(f"   Bigram entropy: {bigram_ent:.3f} bits")
print(f"   Unigram entropy: {unigram_ent:.3f} bits")
print(f"   Conditional entropy (H(Y|X)): {bigram_ent - unigram_ent:.3f} bits")

# =============================================================================
# STEP 2C: COVERAGE VS MANUSCRIPT SIZE
# =============================================================================

print(f"\n2C. COVERAGE")
print("-" * 40)

# Folios
folios = df['folio'].dropna().unique()
print(f"   Total folios: {len(folios)}")

# By section
section_counts = df.groupby('section')['folio'].nunique()
print(f"\n   Folios by section:")
for section in sorted(section_counts.index):
    print(f"      {section}: {section_counts[section]} folios")

# Lines
lines_per_folio = df.groupby('folio')['line_number'].nunique()
print(f"\n   Lines per folio: mean={lines_per_folio.mean():.1f}, total={df.groupby(['folio', 'line_number']).ngroups:,}")

# Tokens per line
tokens_per_line = df.groupby(['folio', 'line_number']).size()
print(f"   Tokens per line: mean={tokens_per_line.mean():.1f}, median={tokens_per_line.median():.1f}")

# =============================================================================
# STEP 2D: KEY METRICS COMPARISON
# =============================================================================

print(f"\n2D. KEY METRICS COMPARISON")
print("-" * 40)

# Expected values from constraints (with H-only)
expected = {
    'B_tokens': 23243,  # From our earlier check
    'A_tokens': 11415,  # From our earlier check
    'AZC_tokens': 3299,  # From our earlier check
    'unique_types_total': 8150,  # From our earlier check
    'B_folios': 83,  # From constraint system
    'core_tokens_B': 41,  # C364
    'single_folio_types_B': 3368,  # C364
}

actual = {
    'B_tokens': len(df[df['language'] == 'B']),
    'A_tokens': len(df[df['language'] == 'A']),
    'AZC_tokens': len(df[df['language'].isna()]),
    'unique_types_total': len(df['word'].dropna().unique()),
    'B_folios': df[df['language'] == 'B']['folio'].nunique(),
}

# Core tokens (>=50% of B folios)
b_folio_count = df[df['language'] == 'B']['folio'].nunique()
word_folio_counts = df[df['language'] == 'B'].groupby('word')['folio'].nunique()
actual['core_tokens_B'] = len(word_folio_counts[word_folio_counts >= b_folio_count * 0.5])
actual['single_folio_types_B'] = len(word_folio_counts[word_folio_counts == 1])

print(f"{'Metric':<25} {'Expected':>12} {'Actual':>12} {'Match':>8}")
print("-" * 60)
for key in expected:
    exp = expected[key]
    act = actual.get(key, 'N/A')
    if isinstance(act, int):
        match = 'OK' if abs(act - exp) / exp < 0.05 else 'DIFF'
        print(f"{key:<25} {exp:>12,} {act:>12,} {match:>8}")
    else:
        print(f"{key:<25} {exp:>12,} {'N/A':>12} {'?':>8}")

# =============================================================================
# SUMMARY
# =============================================================================

print(f"\n" + "=" * 70)
print("VALIDATION SUMMARY")
print("=" * 70)

results = {
    'primary_track': 'H',
    'total_tokens': len(df),
    'unique_types': len(df['word'].dropna().unique()),
    'currier_a_tokens': len(df[df['language'] == 'A']),
    'currier_b_tokens': len(df[df['language'] == 'B']),
    'azc_tokens': len(df[df['language'].isna()]),
    'total_folios': len(folios),
    'bigram_entropy': bigram_ent,
    'unigram_entropy': unigram_ent,
    'core_tokens_b': actual['core_tokens_B'],
    'single_folio_types_b': actual['single_folio_types_B'],
}

print(f"\nPrimary track baseline established:")
for k, v in results.items():
    if isinstance(v, float):
        print(f"   {k}: {v:.4f}")
    else:
        print(f"   {k}: {v}")

# Save results
with open('results/primary_track_baseline.json', 'w') as f:
    json.dump(results, f, indent=2)
print(f"\nSaved to: results/primary_track_baseline.json")

print(f"\n✓ Step 1-2 complete. Ready for Step 3 (re-derive core analyses).")
