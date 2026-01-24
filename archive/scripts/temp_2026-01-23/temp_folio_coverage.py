"""Check how many of the 479 instruction tokens appear per B folio."""
import pandas as pd
import json

# Load instruction classes
with open('results/phase20a_operator_equivalence.json', 'r') as f:
    classes = json.load(f)

# Get all instruction class tokens
all_class_tokens = set()
for cls in classes['classes']:
    all_class_tokens.update(cls['members'])

print(f"Total instruction class tokens: {len(all_class_tokens)}")

# Load transcript
df = pd.read_csv('data/transcriptions/interlinear_full_words.txt', sep='\t', low_memory=False)
df = df[(df['transcriber'] == 'H') & (df['language'] == 'B')]

# Get tokens per folio
folio_coverage = {}
for folio in df['folio'].unique():
    folio_tokens = set(df[df['folio'] == folio]['word'].dropna().unique())
    class_tokens_in_folio = folio_tokens & all_class_tokens
    folio_coverage[folio] = len(class_tokens_in_folio)

# Statistics
coverages = list(folio_coverage.values())
print(f"\nB folios analyzed: {len(coverages)}")
print(f"Min tokens per folio: {min(coverages)}")
print(f"Max tokens per folio: {max(coverages)}")
print(f"Mean tokens per folio: {sum(coverages)/len(coverages):.1f}")
print(f"Median: {sorted(coverages)[len(coverages)//2]}")

# Show distribution
print(f"\n--- Folios by coverage ---")
sorted_folios = sorted(folio_coverage.items(), key=lambda x: x[1])
print("Lowest coverage:")
for folio, count in sorted_folios[:10]:
    pct = count / len(all_class_tokens) * 100
    print(f"  {folio}: {count} tokens ({pct:.1f}%)")

print("\nHighest coverage:")
for folio, count in sorted_folios[-10:]:
    pct = count / len(all_class_tokens) * 100
    print(f"  {folio}: {count} tokens ({pct:.1f}%)")

# Check if ANY folio has all 479
full_coverage = [f for f, c in folio_coverage.items() if c == len(all_class_tokens)]
print(f"\nFolios with 100% coverage: {len(full_coverage)}")
