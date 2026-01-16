"""Check single-folio tokens (C364: 3,368 claimed = 68%)."""
import pandas as pd

df = pd.read_csv('data/transcriptions/interlinear_full_words.txt', sep='\t', low_memory=False)

# B folios only
b_df = df[df['language'] == 'B']

# All transcribers
folio_counts_all = b_df.groupby('word')['folio'].nunique()
single_folio_all = folio_counts_all[folio_counts_all == 1]
print(f"All transcribers:")
print(f"  Single-folio tokens: {len(single_folio_all)} ({100*len(single_folio_all)/len(folio_counts_all):.1f}%)")
print(f"  Total unique: {len(folio_counts_all)}")

# H-only
b_h = b_df[b_df['transcriber'] == 'H']
folio_counts_h = b_h.groupby('word')['folio'].nunique()
single_folio_h = folio_counts_h[folio_counts_h == 1]
print(f"\nH-only:")
print(f"  Single-folio tokens: {len(single_folio_h)} ({100*len(single_folio_h)/len(folio_counts_h):.1f}%)")
print(f"  Total unique: {len(folio_counts_h)}")

print(f"\nC364 claims: 3,368 unique (68% single folio)")
