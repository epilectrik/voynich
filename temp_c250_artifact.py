"""Demonstrate how transcriber data creates false [BLOCK] × N pattern."""
import pandas as pd

df = pd.read_csv('data/transcriptions/interlinear_full_words.txt', sep='\t', low_memory=False)

# f1r line 1 as example
line = df[(df['folio'] == 'f1r') & (df['line_number'] == 1) & (df['language'] == 'A')]

print("f1r line 1 - The False Block Repetition Artifact")
print("=" * 70)

# Show by transcriber
print("\nBy transcriber:")
for t in sorted(line['transcriber'].unique()):
    tokens = line[line['transcriber'] == t]['word'].tolist()
    print(f"  {t}: {tokens}")

# Show combined (what CAS analysis saw)
print("\n" + "-" * 70)
print("Combined (what CAS block analysis saw):")
all_tokens = line['word'].tolist()
print(f"  {len(all_tokens)} tokens: {all_tokens}")

# Show the false pattern
h_tokens = line[line['transcriber'] == 'H']['word'].tolist()
print(f"\nH-only block: {h_tokens} ({len(h_tokens)} tokens)")
print(f"Number of transcribers: {line['transcriber'].nunique()}")
print(f"Combined looks like: [H-block] × {line['transcriber'].nunique()}")

print("\n" + "=" * 70)
print("CONCLUSION: The [BLOCK] × N pattern was an ARTIFACT of")
print("transcriber data, NOT actual manuscript repetition!")
print("=" * 70)
