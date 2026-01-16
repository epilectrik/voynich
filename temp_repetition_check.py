"""Check if transcriber interleaving creates false repetition patterns."""
import pandas as pd

df = pd.read_csv('data/transcriptions/interlinear_full_words.txt', sep='\t', low_memory=False)

# Pick a sample line: f1r line 3
sample = df[(df['folio'] == 'f1r') & (df['line_number'] == 3)].copy()

print("Raw row order for f1r line 3:")
print("-" * 50)
for i, (_, row) in enumerate(sample.iterrows()):
    print(f"  Row {i}: {row['word']:<15} transcriber={row['transcriber']}")

print("\n" + "=" * 50)
print("If analyzed sequentially WITHOUT filtering:")
print("=" * 50)
words = sample['word'].tolist()
# Check for apparent repetitions
for i in range(len(words) - 1):
    if words[i] == words[i+1]:
        print(f"  FALSE REPETITION: '{words[i]}' at positions {i}, {i+1}")

print("\n" + "=" * 50)
print("With H-only filtering (correct):")
print("=" * 50)
h_sample = sample[sample['transcriber'] == 'H']
h_words = h_sample['word'].tolist()
print(f"  Tokens: {h_words}")
reps = sum(1 for i in range(len(h_words)-1) if h_words[i] == h_words[i+1])
print(f"  Actual repetitions: {reps}")
