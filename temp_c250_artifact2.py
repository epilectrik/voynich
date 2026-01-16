"""Demonstrate how transcriber data creates false [BLOCK] × N pattern."""
import pandas as pd

df = pd.read_csv('data/transcriptions/interlinear_full_words.txt', sep='\t', low_memory=False)

# Find a Currier A line with multiple transcribers
a_df = df[df['language'] == 'A']
grouped = a_df.groupby(['folio', 'line_number'])

for (folio, line_num), group in grouped:
    if group['transcriber'].nunique() >= 3 and len(group) >= 15:
        print(f"{folio} line {line_num} - The False Block Repetition Artifact")
        print("=" * 70)

        # Show by transcriber
        print("\nBy transcriber:")
        for t in sorted(group['transcriber'].unique()):
            tokens = group[group['transcriber'] == t]['word'].tolist()
            print(f"  {t}: {tokens[:12]}{'...' if len(tokens) > 12 else ''}")

        # Show combined (what CAS analysis saw)
        print("\n" + "-" * 70)
        print("Combined (what CAS block analysis saw):")
        all_tokens = group['word'].tolist()
        print(f"  {len(all_tokens)} tokens total")
        print(f"  First 20: {all_tokens[:20]}...")

        # Show the false pattern
        h_tokens = group[group['transcriber'] == 'H']['word'].tolist()
        n_trans = group['transcriber'].nunique()
        print(f"\nH-only: {len(h_tokens)} tokens")
        print(f"Transcribers: {n_trans}")
        print(f"Combined appears as: [H-block of {len(h_tokens)}] × ~{n_trans}")

        print("\n" + "=" * 70)
        print("This is why C250 found '[BLOCK] × N' - it was seeing")
        print(f"{n_trans} transcriber copies, not actual repetition!")
        print("=" * 70)
        break
