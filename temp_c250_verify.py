"""Verify C250: Does 64.1% block repetition hold with H-only?"""
import pandas as pd
from collections import defaultdict, Counter

df = pd.read_csv('data/transcriptions/interlinear_full_words.txt', sep='\t', low_memory=False)

def find_repeating_blocks(tokens):
    """Find the repeating block pattern (from original CAS code)."""
    n = len(tokens)
    if n < 2:
        return tokens, 1

    for block_size in range(1, n // 2 + 1):
        if n % block_size == 0:
            block = tokens[:block_size]
            count = n // block_size

            matches = True
            for i in range(1, count):
                chunk = tokens[i * block_size:(i + 1) * block_size]
                mismatches = sum(1 for a, b in zip(block, chunk) if a != b)
                if mismatches > len(block) * 0.2:
                    matches = False
                    break

            if matches and count >= 2:
                return block, count

    return tokens, 1


def analyze_repetition(df_subset, label):
    """Analyze block repetition for a subset."""
    lines = defaultdict(list)

    for _, row in df_subset.iterrows():
        if row['language'] == 'A':
            word = str(row['word']).lower().strip()
            folio = row['folio']
            line_num = row['line_number']

            if word and pd.notna(word) and word != 'nan':
                key = f"{folio}_{line_num}"
                lines[key].append(word)

    # Analyze each line for block repetition
    block_entries = 0
    total_entries = 0
    rep_counts = Counter()

    for key, tokens in lines.items():
        if len(tokens) >= 2:  # Need at least 2 tokens
            total_entries += 1
            block, count = find_repeating_blocks(tokens)
            if count >= 2:
                block_entries += 1
                rep_counts[count] += 1

    pct = 100 * block_entries / total_entries if total_entries > 0 else 0
    print(f"\n{label}:")
    print(f"  Total entries: {total_entries}")
    print(f"  Block entries (count >= 2): {block_entries} ({pct:.1f}%)")
    print(f"  Repetition distribution: {dict(rep_counts.most_common(10))}")

    return pct, total_entries, block_entries


# All transcribers
pct_all, total_all, blocks_all = analyze_repetition(df, "ALL TRANSCRIBERS")

# H-only
h_df = df[df['transcriber'] == 'H']
pct_h, total_h, blocks_h = analyze_repetition(h_df, "H-ONLY (correct)")

print("\n" + "=" * 60)
print("COMPARISON")
print("=" * 60)
print(f"C250 claims: 64.1% (1013/1580)")
print(f"All transcribers: {pct_all:.1f}% ({blocks_all}/{total_all})")
print(f"H-only: {pct_h:.1f}% ({blocks_h}/{total_h})")
print(f"\nVerdict: {'C250 VALIDATED' if 55 < pct_h < 75 else 'C250 NEEDS REVIEW'}")
