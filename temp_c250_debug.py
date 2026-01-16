"""Debug: Why does H-only show 0% repetition?"""
import pandas as pd
from collections import defaultdict, Counter

df = pd.read_csv('data/transcriptions/interlinear_full_words.txt', sep='\t', low_memory=False)

# H-only Currier A
h_a = df[(df['transcriber'] == 'H') & (df['language'] == 'A')]

# Group by line
lines = defaultdict(list)
for _, row in h_a.iterrows():
    word = str(row['word']).lower().strip()
    if word and pd.notna(word) and word != 'nan':
        key = f"{row['folio']}_{row['line_number']}"
        lines[key].append(word)

# Line length distribution
lengths = [len(v) for v in lines.values()]
print("H-only Currier A line lengths:")
print(f"  Mean: {sum(lengths)/len(lengths):.1f}")
print(f"  Min: {min(lengths)}, Max: {max(lengths)}")
print(f"  Distribution: {Counter(lengths).most_common(10)}")

# Check for ANY consecutive repetition in H-only
print("\n" + "=" * 60)
print("Looking for ANY consecutive repetition in H-only:")
print("=" * 60)

consec_reps = []
for key, tokens in lines.items():
    for i in range(len(tokens) - 1):
        if tokens[i] == tokens[i+1]:
            consec_reps.append((key, tokens[i], i))

print(f"Found {len(consec_reps)} consecutive repetitions")
if consec_reps:
    print("Examples:")
    for key, token, pos in consec_reps[:20]:
        print(f"  {key}: '{token}' at positions {pos},{pos+1}")

# Check for daiin repetition specifically (mentioned in C243)
print("\n" + "=" * 60)
print("Checking for daiin repetition:")
print("=" * 60)

daiin_reps = 0
for key, tokens in lines.items():
    for i in range(len(tokens) - 1):
        if tokens[i] == 'daiin' and tokens[i+1] == 'daiin':
            daiin_reps += 1
            print(f"  {key}: daiin-daiin at {i},{i+1}")

print(f"\nTotal daiin-daiin: {daiin_reps}")

# Show some actual line contents
print("\n" + "=" * 60)
print("Sample H-only lines (to see actual structure):")
print("=" * 60)

for key in list(lines.keys())[:10]:
    tokens = lines[key]
    print(f"{key}: {tokens}")
