"""Simulate what currier_a_block_analysis.py actually saw."""
import pandas as pd
from collections import defaultdict

df = pd.read_csv('data/transcriptions/interlinear_full_words.txt', sep='\t', low_memory=False)

# Simulate the load_currier_a_lines() function
lines_all = defaultdict(list)
lines_h = defaultdict(list)

for _, row in df.iterrows():
    if row['language'] == 'A':
        word = str(row['word']).lower().strip()
        folio = row['folio']
        line_num = row['line_number']
        transcriber = row['transcriber']

        if word and pd.notna(word):
            key = f"{folio}_{line_num}"
            lines_all[key].append(word)
            if transcriber == 'H':
                lines_h[key].append(word)

# Compare a few lines
print("Sample lines showing ALL vs H-only:")
print("=" * 70)

sample_keys = list(lines_all.keys())[:5]
for key in sample_keys:
    all_tokens = lines_all[key]
    h_tokens = lines_h[key]

    print(f"\n{key}:")
    print(f"  ALL ({len(all_tokens)} tokens): {all_tokens[:15]}...")
    print(f"  H-only ({len(h_tokens)} tokens): {h_tokens}")

    # Check for false repetitions in ALL
    false_reps = 0
    for i in range(len(all_tokens) - 1):
        if all_tokens[i] == all_tokens[i+1]:
            false_reps += 1
    if false_reps > 0:
        print(f"  FALSE CONSECUTIVE REPEATS in ALL: {false_reps}")

# Overall stats
print("\n" + "=" * 70)
print("OVERALL STATISTICS")
print("=" * 70)
all_sizes = [len(v) for v in lines_all.values()]
h_sizes = [len(v) for v in lines_h.values()]
print(f"Mean tokens per line (ALL): {sum(all_sizes)/len(all_sizes):.1f}")
print(f"Mean tokens per line (H-only): {sum(h_sizes)/len(h_sizes):.1f}")
print(f"Inflation factor: {sum(all_sizes)/sum(h_sizes):.2f}x")

# Count false consecutive repetitions
total_false_reps = 0
for tokens in lines_all.values():
    for i in range(len(tokens) - 1):
        if tokens[i] == tokens[i+1]:
            total_false_reps += 1

print(f"\nTotal false consecutive repetitions (ALL): {total_false_reps}")
