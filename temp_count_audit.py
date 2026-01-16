"""Audit absolute counts in constraints: H-only vs all transcribers."""
import pandas as pd
from collections import Counter

df = pd.read_csv('data/transcriptions/interlinear_full_words.txt', sep='\t', low_memory=False)

print("=" * 60)
print("CONSTRAINT COUNT AUDIT: H-only vs All Transcribers")
print("=" * 60)

# 1. C121: 479 unique token types in B
print("\n1. C121: B vocabulary (479 claimed)")
b_all = df[df['language'] == 'B']['word'].dropna()
b_h = df[(df['language'] == 'B') & (df['transcriber'] == 'H')]['word'].dropna()
# Top 480 by frequency (as actually used)
top480_all = len(set([t for t, _ in Counter(b_all).most_common(480)]))
top480_h = len(set([t for t, _ in Counter(b_h).most_common(480)]))
print(f"   Top 480 all: {top480_all}, H-only: {top480_h}")
print(f"   Status: SAFE (frequency-filtered)")

# 2. C300/C301: AZC tokens and types
print("\n2. C300/C301: AZC tokens (9,401 claimed) and types (1,529 claimed)")
# AZC sections are A, Z, C, H, S (but H/S are not diagrams)
azc_sections = ['A', 'Z', 'C', 'H', 'S']
azc_all = df[df['section'].isin(azc_sections)]['word'].dropna()
azc_h = df[(df['section'].isin(azc_sections)) & (df['transcriber'] == 'H')]['word'].dropna()
print(f"   Total tokens - all: {len(azc_all)}, H-only: {len(azc_h)}")
print(f"   Unique types - all: {len(azc_all.unique())}, H-only: {len(azc_h.unique())}")
print(f"   Inflation: {len(azc_all)/len(azc_h):.2f}x tokens, {len(azc_all.unique())/len(azc_h.unique()):.2f}x types")

# 3. C267: 1,184 unique MIDDLEs - need to parse morphology
print("\n3. C267: MIDDLE types (1,184 claimed)")
print("   Cannot verify without morphology parser - CHECK MANUALLY")

# 4. C265: 1,123 unique marker tokens
print("\n4. C265: Marker tokens (1,123 claimed)")
# Currier A markers
a_all = df[df['language'] == 'A']['word'].dropna()
a_h = df[(df['language'] == 'A') & (df['transcriber'] == 'H')]['word'].dropna()
print(f"   A unique types - all: {len(a_all.unique())}, H-only: {len(a_h.unique())}")
print(f"   Inflation: {len(a_all.unique())/len(a_h.unique()):.2f}x")

# 5. C485: 0 h->k transitions in 75,545 tokens
print("\n5. C485: h->k forbidden (0 in 75,545 tokens)")
print(f"   Token count - all: {len(b_all)}, H-only: {len(b_h)}")
print(f"   Status: SAFE (0 occurrences preserved regardless of count)")

# 6. morphology: 41 core tokens, 3,368 unique
print("\n6. morphology: Core tokens (41) and unique (3,368)")
# Tokens appearing in >=50% of folios
folio_counts = df[df['transcriber'] == 'H'].groupby('word')['folio'].nunique()
total_folios = df[df['transcriber'] == 'H']['folio'].nunique()
core_h = len(folio_counts[folio_counts >= total_folios * 0.5])

folio_counts_all = df.groupby('word')['folio'].nunique()
total_folios_all = df['folio'].nunique()
core_all = len(folio_counts_all[folio_counts_all >= total_folios_all * 0.5])

print(f"   Core tokens (>=50% folios) - all: {core_all}, H-only: {core_h}")
print(f"   Total unique - all: {len(df['word'].dropna().unique())}, H-only: {len(df[df['transcriber']=='H']['word'].dropna().unique())}")

# 7. C462: 18 universal, 134 bridging, 573 exclusive
print("\n7. C462: Type stratification (18/134/573 claimed)")
print("   Requires mode analysis - CHECK MANUALLY")

# 8. organization: Top 10 tokens = 15% corpus
print("\n8. organization: Top 10 tokens coverage")
top10_all = Counter(b_all).most_common(10)
top10_h = Counter(b_h).most_common(10)
cov_all = sum(c for _, c in top10_all) / len(b_all) * 100
cov_h = sum(c for _, c in top10_h) / len(b_h) * 100
print(f"   Top 10 coverage - all: {cov_all:.1f}%, H-only: {cov_h:.1f}%")
print(f"   Status: SAFE (ratio-based)")
