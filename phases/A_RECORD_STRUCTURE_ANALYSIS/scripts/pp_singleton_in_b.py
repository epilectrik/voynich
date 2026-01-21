#!/usr/bin/env python3
"""Check if singleton PP MIDDLEs actually appear in Currier B."""

import json
from collections import Counter
import pandas as pd

# Load A token data
with open('phases/A_INTERNAL_STRATIFICATION/results/token_data.json') as f:
    a_tokens = json.load(f)

with open('phases/A_INTERNAL_STRATIFICATION/results/middle_classes.json') as f:
    mc = json.load(f)

ri_middles = set(mc['a_exclusive_middles'])

# Count PP MIDDLE frequencies in A
pp_middle_counts_a = Counter()
for t in a_tokens:
    if t['middle'] not in ri_middles:
        pp_middle_counts_a[t['middle']] += 1

singleton_pp_middles = set(m for m, c in pp_middle_counts_a.items() if c == 1)
print(f"Singleton PP MIDDLEs in A: {len(singleton_pp_middles)}")

# Load B corpus
df = pd.read_csv('data/transcriptions/interlinear_full_words.txt', sep='\t')
df = df[df['transcriber'] == 'H']  # PRIMARY track only

# Get Currier B folios
b_folios = df[df['currier_language'] == 'B']['folio_id'].unique()
df_b = df[df['folio_id'].isin(b_folios)]

print(f"B corpus size: {len(df_b)} tokens")
print(f"B folios: {len(b_folios)}")
print()

# Extract MIDDLEs from B (need to parse tokens)
# This is approximate - using the middle_classes.json approach
# The shared MIDDLEs are those that appear in BOTH A and B

# Actually, let's check what the middle_classes classification is based on
print("=" * 60)
print("CHECKING CLASSIFICATION BASIS")
print("=" * 60)
print()

# The a_exclusive_middles are MIDDLEs that appear in A but NOT in B
# So by definition, non-exclusive (PP) MIDDLEs DO appear in B
# But let's verify the singleton ones specifically

# We need to check if these specific MIDDLEs appear in B tokens
# Get all B tokens
b_tokens = df_b['token_transcript'].dropna().tolist()

# Check each singleton PP MIDDLE
found_in_b = 0
not_found_in_b = 0
found_examples = []
not_found_examples = []

for middle in singleton_pp_middles:
    # Search for this middle in B tokens (substring search)
    found = False
    for token in b_tokens:
        if middle in str(token):
            found = True
            found_examples.append((middle, token))
            break

    if found:
        found_in_b += 1
    else:
        not_found_in_b += 1
        not_found_examples.append(middle)

print(f"Singleton PP MIDDLEs found in B: {found_in_b} ({100*found_in_b/len(singleton_pp_middles):.1f}%)")
print(f"Singleton PP MIDDLEs NOT found in B: {not_found_in_b} ({100*not_found_in_b/len(singleton_pp_middles):.1f}%)")
print()

if not_found_examples:
    print("SINGLETON PP MIDDLEs NOT APPEARING IN B:")
    for m in not_found_examples[:20]:
        print(f"  {m}")
    print()

if found_examples:
    print("EXAMPLES FOUND IN B:")
    for m, token in found_examples[:15]:
        print(f"  MIDDLE={m:<8} -> B token: {token}")
print()

# Now let's be more rigorous - use the actual morphology parsing
# Check the summary in middle_classes.json
print("=" * 60)
print("MIDDLE_CLASSES.JSON SUMMARY")
print("=" * 60)
print()

print(f"Total A MIDDLEs: {mc['summary']['a_total_middles']}")
print(f"A-exclusive (RI): {mc['summary']['a_exclusive_count']} ({mc['summary']['a_exclusive_pct']:.1f}%)")
print(f"A-shared (PP): {mc['summary']['a_shared_count']}")
print()

# The shared count should be those appearing in BOTH A and B
# So ALL PP MIDDLEs should by definition appear in B
print("By definition, PP MIDDLEs are those that appear in BOTH A and B.")
print("If a MIDDLE is PP, it MUST appear in B (that's how it was classified).")
print()

# Let's double-check by looking at what makes something 'shared'
# Check if we have B middle data
print("Checking B corpus for MIDDLE extraction...")

# We need the morphology parser to properly extract MIDDLEs from B
# For now, let's check the classification logic
