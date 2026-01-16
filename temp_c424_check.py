"""Check if C424 adjacency findings hold with H-only."""
import pandas as pd
from collections import defaultdict
import numpy as np

df = pd.read_csv('data/transcriptions/interlinear_full_words.txt', sep='\t', low_memory=False)

def jaccard(set1, set2):
    if not set1 and not set2:
        return 0.0
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    return intersection / union if union > 0 else 0.0

def load_a_entries(df_subset):
    """Load Currier A entries."""
    a_df = df_subset[df_subset['language'] == 'A']
    entries = []
    for (folio, line_num), group in a_df.groupby(['folio', 'line_number']):
        tokens = set(group['word'].dropna().str.lower())
        if tokens:
            entries.append({
                'key': f"{folio}_{line_num}",
                'folio': folio,
                'tokens': tokens
            })
    return entries

def analyze_adjacency(entries):
    """Compute adjacency statistics."""
    if len(entries) < 2:
        return None

    # Compute adjacent pair similarities
    adjacent_J = []
    for i in range(len(entries) - 1):
        j = jaccard(entries[i]['tokens'], entries[i+1]['tokens'])
        adjacent_J.append(j)

    # Compute non-adjacent similarities (sample)
    nonadjacent_J = []
    np.random.seed(42)
    for _ in range(min(1000, len(entries) * 2)):
        i, j = np.random.choice(len(entries), 2, replace=False)
        if abs(i - j) > 1:  # Non-adjacent
            sim = jaccard(entries[i]['tokens'], entries[j]['tokens'])
            nonadjacent_J.append(sim)

    return {
        'n_entries': len(entries),
        'adjacent_mean_J': np.mean(adjacent_J),
        'nonadjacent_mean_J': np.mean(nonadjacent_J),
        'ratio': np.mean(adjacent_J) / np.mean(nonadjacent_J) if np.mean(nonadjacent_J) > 0 else float('inf'),
        'pct_zero_adjacent': 100 * sum(1 for j in adjacent_J if j == 0) / len(adjacent_J)
    }

print("C424 ADJACENCY CHECK: H-only vs All Transcribers")
print("=" * 70)

# All transcribers
entries_all = load_a_entries(df)
stats_all = analyze_adjacency(entries_all)

# H-only
h_df = df[df['transcriber'] == 'H']
entries_h = load_a_entries(h_df)
stats_h = analyze_adjacency(entries_h)

print("\n                        All Trans    H-only    C424 Claim")
print("-" * 60)
print(f"Entries                 {stats_all['n_entries']:>8}    {stats_h['n_entries']:>8}")
print(f"Adjacent mean J         {stats_all['adjacent_mean_J']:>8.4f}    {stats_h['adjacent_mean_J']:>8.4f}")
print(f"Non-adjacent mean J     {stats_all['nonadjacent_mean_J']:>8.4f}    {stats_h['nonadjacent_mean_J']:>8.4f}")
print(f"Ratio (adj/non-adj)     {stats_all['ratio']:>8.2f}x   {stats_h['ratio']:>8.2f}x    1.31x")
print(f"% zero adjacent         {stats_all['pct_zero_adjacent']:>8.1f}%   {stats_h['pct_zero_adjacent']:>8.1f}%    69.3%")

print("\n" + "=" * 70)
if stats_h['ratio'] > 1.1 and stats_h['pct_zero_adjacent'] > 50:
    print("VERDICT: C424 patterns HOLD with H-only (adjacency > non-adjacency)")
else:
    print("VERDICT: C424 patterns NEED REVIEW")
