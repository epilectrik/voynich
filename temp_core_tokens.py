"""Check core token counts (C364: 41 claimed)."""
import pandas as pd

df = pd.read_csv('data/transcriptions/interlinear_full_words.txt', sep='\t', low_memory=False)

# C364 is in "B-Folio Vocabulary" section, so it's B folios only
b_df = df[df['language'] == 'B']

# All transcribers
b_folios_all = b_df['folio'].nunique()
folio_counts_all = b_df.groupby('word')['folio'].nunique()
core_all = folio_counts_all[folio_counts_all >= b_folios_all * 0.5]
print(f"All transcribers (B folios = {b_folios_all}):")
print(f"  Core tokens (>=50% folios): {len(core_all)}")
print(f"  Total unique types: {len(folio_counts_all)}")

# H-only
b_h = b_df[b_df['transcriber'] == 'H']
b_folios_h = b_h['folio'].nunique()
folio_counts_h = b_h.groupby('word')['folio'].nunique()
core_h = folio_counts_h[folio_counts_h >= b_folios_h * 0.5]
print(f"\nH-only (B folios = {b_folios_h}):")
print(f"  Core tokens (>=50% folios): {len(core_h)}")
print(f"  Total unique types: {len(folio_counts_h)}")

print(f"\nC364 claims: 41 core, 3,368 unique")

# What threshold gives 41?
for thresh in [0.3, 0.4, 0.5, 0.6, 0.7]:
    count_all = len(folio_counts_all[folio_counts_all >= b_folios_all * thresh])
    count_h = len(folio_counts_h[folio_counts_h >= b_folios_h * thresh])
    print(f"  >={thresh*100:.0f}% folios: all={count_all}, H={count_h}")
