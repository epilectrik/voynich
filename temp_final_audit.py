"""Final audit: Check which constraints match H-only vs all-transcriber."""
import pandas as pd
from collections import Counter

df = pd.read_csv('data/transcriptions/interlinear_full_words.txt', sep='\t', low_memory=False)

print("=" * 70)
print("FINAL AUDIT: Which data source did each constraint use?")
print("=" * 70)

# H-only subsets
h = df[df['transcriber'] == 'H']

results = []

# C300: 9,401 AZC tokens
azc_all = len(df[df['language'].isna()])
azc_h = len(h[h['language'].isna()])
match = "ALL" if azc_all == 9401 else ("H" if azc_h == 9401 else "NEITHER")
results.append(("C300: AZC tokens", 9401, azc_all, azc_h, match))

# C304: 1,529 AZC-unique types
a_all = set(df[df['language'] == 'A']['word'].dropna())
b_all = set(df[df['language'] == 'B']['word'].dropna())
azc_t_all = set(df[df['language'].isna()]['word'].dropna())
unique_all = len(azc_t_all - a_all - b_all)
a_h = set(h[h['language'] == 'A']['word'].dropna())
b_h = set(h[h['language'] == 'B']['word'].dropna())
azc_t_h = set(h[h['language'].isna()]['word'].dropna())
unique_h = len(azc_t_h - a_h - b_h)
match = "ALL" if unique_all == 1529 else ("H" if unique_h == 1529 else "NEITHER")
results.append(("C304: AZC-unique types", 1529, unique_all, unique_h, match))

# C364: 41 core tokens
b_h = h[h['language'] == 'B']
b_all = df[df['language'] == 'B']
core_h = len(b_h.groupby('word')['folio'].nunique()[lambda x: x >= b_h['folio'].nunique() * 0.5])
core_all = len(b_all.groupby('word')['folio'].nunique()[lambda x: x >= b_all['folio'].nunique() * 0.5])
match = "ALL" if core_all == 41 else ("H" if core_h == 41 else "NEITHER")
results.append(("C364: Core tokens", 41, core_all, core_h, match))

# C364: 3,368 single-folio
single_h = len(b_h.groupby('word')['folio'].nunique()[lambda x: x == 1])
single_all = len(b_all.groupby('word')['folio'].nunique()[lambda x: x == 1])
match = "ALL" if single_all == 3368 else ("H" if single_h == 3368 else "NEITHER")
results.append(("C364: Single-folio types", 3368, single_all, single_h, match))

# C121: 480 top tokens (already verified)
results.append(("C121: Top 480 tokens", 480, 480, 480, "BOTH (frequency-based)"))

# C485: 75,545 B tokens
b_count_all = len(df[df['language'] == 'B'])
b_count_h = len(h[h['language'] == 'B'])
match = "ALL" if b_count_all == 75545 else ("H" if b_count_h == 75545 else "NEITHER")
results.append(("C485: B token count", 75545, b_count_all, b_count_h, match))

# Print results
print(f"\n{'Constraint':<30} {'Claimed':>10} {'All':>10} {'H-only':>10} {'Source':>15}")
print("-" * 80)
for name, claimed, all_val, h_val, source in results:
    print(f"{name:<30} {claimed:>10} {all_val:>10} {h_val:>10} {source:>15}")

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
all_count = sum(1 for r in results if r[4] == "ALL")
h_count = sum(1 for r in results if r[4] == "H")
both_count = sum(1 for r in results if "BOTH" in r[4])
print(f"  Used ALL transcribers: {all_count}")
print(f"  Used H-only: {h_count}")
print(f"  Works with both: {both_count}")
