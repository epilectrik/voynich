"""Check if 49 equivalence classes would be similar with H-only."""
import pandas as pd
from collections import Counter
import numpy as np
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.spatial.distance import pdist

df = pd.read_csv('data/transcriptions/interlinear_full_words.txt', sep='\t', low_memory=False)

def get_top_tokens(df_subset, n=480):
    """Get top N tokens by frequency."""
    b_df = df_subset[df_subset['language'] == 'B']
    freq = Counter(b_df['word'].dropna())
    return [t for t, _ in freq.most_common(n)]

def get_transitions(df_subset):
    """Get transition counts grouped by line."""
    trans = {}
    b_df = df_subset[df_subset['language'] == 'B']

    for (folio, line_num), group in b_df.groupby(['folio', 'line_number']):
        words = group['word'].dropna().tolist()
        for i in range(len(words) - 1):
            key = (words[i], words[i+1])
            trans[key] = trans.get(key, 0) + 1

    return trans

def build_feature_matrix(tokens, transitions):
    """Build behavioral feature matrix for tokens."""
    n = len(tokens)
    token_idx = {t: i for i, t in enumerate(tokens)}

    # Feature: transition profile (who follows, who precedes)
    features = np.zeros((n, n * 2))  # out-transitions + in-transitions

    for (src, tgt), count in transitions.items():
        if src in token_idx and tgt in token_idx:
            i = token_idx[src]
            j = token_idx[tgt]
            features[i, j] = count  # out-transition
            features[j, n + i] = count  # in-transition

    # Normalize
    row_sums = features.sum(axis=1, keepdims=True)
    row_sums[row_sums == 0] = 1
    features = features / row_sums

    return features

# Get data
h_df = df[df['transcriber'] == 'H']

tokens_all = get_top_tokens(df)
tokens_h = get_top_tokens(h_df)

print("49 EQUIVALENCE CLASS CHECK")
print("=" * 70)

# Token overlap
overlap = len(set(tokens_all) & set(tokens_h))
print(f"\nTop 480 token overlap: {overlap}/480 ({100*overlap/480:.1f}%)")

# Build feature matrices
trans_all = get_transitions(df)
trans_h = get_transitions(h_df)

feat_all = build_feature_matrix(tokens_all, trans_all)
feat_h = build_feature_matrix(tokens_h, trans_h)

# Cluster both
def cluster_and_count(features, n_clusters=49):
    if features.shape[0] < 2:
        return 0
    dist = pdist(features, metric='cosine')
    dist = np.nan_to_num(dist, nan=1.0)
    Z = linkage(dist, method='ward')
    labels = fcluster(Z, n_clusters, criterion='maxclust')
    return len(set(labels))

n_all = cluster_and_count(feat_all, 49)
n_h = cluster_and_count(feat_h, 49)

print(f"\nCluster counts at k=49:")
print(f"  All transcribers: {n_all} clusters")
print(f"  H-only: {n_h} clusters")

# Check cluster membership similarity
# (Are the same tokens grouped together?)
print("\n" + "-" * 70)
print("Checking if clustering pattern is similar...")

# Get cluster labels for both
dist_all = pdist(feat_all, metric='cosine')
dist_all = np.nan_to_num(dist_all, nan=1.0)
Z_all = linkage(dist_all, method='ward')
labels_all = fcluster(Z_all, 49, criterion='maxclust')

dist_h = pdist(feat_h, metric='cosine')
dist_h = np.nan_to_num(dist_h, nan=1.0)
Z_h = linkage(dist_h, method='ward')
labels_h = fcluster(Z_h, 49, criterion='maxclust')

# For tokens in both lists, check if they're in same cluster
common_tokens = set(tokens_all) & set(tokens_h)
idx_all = {t: i for i, t in enumerate(tokens_all)}
idx_h = {t: i for i, t in enumerate(tokens_h)}

# Count pairs that are clustered together in both
same_cluster_all = 0
same_cluster_h = 0
same_in_both = 0
total_pairs = 0

common_list = list(common_tokens)[:100]  # Sample 100 common tokens
for i in range(len(common_list)):
    for j in range(i+1, len(common_list)):
        t1, t2 = common_list[i], common_list[j]
        if t1 in idx_all and t2 in idx_all and t1 in idx_h and t2 in idx_h:
            total_pairs += 1
            same_all = labels_all[idx_all[t1]] == labels_all[idx_all[t2]]
            same_h = labels_h[idx_h[t1]] == labels_h[idx_h[t2]]
            if same_all:
                same_cluster_all += 1
            if same_h:
                same_cluster_h += 1
            if same_all == same_h:
                same_in_both += 1

agreement = 100 * same_in_both / total_pairs if total_pairs > 0 else 0
print(f"\nPairwise clustering agreement: {agreement:.1f}%")

print("\n" + "=" * 70)
if agreement > 70:
    print("VERDICT: 49-class structure LIKELY PRESERVED")
else:
    print("VERDICT: 49-class structure MAY DIFFER (but core patterns should hold)")
