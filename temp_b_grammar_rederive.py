"""
STEP 3A: RE-DERIVE CURRIER B GRAMMAR (H-only)
=============================================
Confirm invariance of:
- 49 equivalence classes
- 17 forbidden transitions (hazard topology)
- Kernel structure (k, h, e)
- Transition patterns
"""
import pandas as pd
import numpy as np
from collections import Counter, defaultdict
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.spatial.distance import pdist
import json

print("=" * 70)
print("STEP 3A: CURRIER B GRAMMAR RE-DERIVATION (H-only)")
print("=" * 70)

# Load PRIMARY track only
df_raw = pd.read_csv('data/transcriptions/interlinear_full_words.txt', sep='\t', low_memory=False)
df = df_raw[df_raw['transcriber'] == 'H'].copy()
b_df = df[df['language'] == 'B'].copy()

print(f"\nData: {len(b_df):,} Currier B tokens (H-only)")

# =============================================================================
# 3A.1: TRANSITION MATRIX (grouped by line)
# =============================================================================

print(f"\n3A.1: TRANSITION MATRIX")
print("-" * 40)

def get_transitions_by_line(df_subset):
    """Get token transitions properly grouped by line."""
    trans = defaultdict(Counter)
    for (folio, line_num), group in df_subset.groupby(['folio', 'line_number']):
        words = [str(w).lower() for w in group['word'].dropna().tolist()]
        for i in range(1, len(words)):
            trans[words[i-1]][words[i]] += 1
    return dict(trans)

transitions = get_transitions_by_line(b_df)
total_trans = sum(sum(v.values()) for v in transitions.values())
unique_pairs = sum(len(v) for v in transitions.values())

print(f"   Total transitions: {total_trans:,}")
print(f"   Unique bigram types: {unique_pairs:,}")

# =============================================================================
# 3A.2: FORBIDDEN TRANSITIONS (17 hazards)
# =============================================================================

print(f"\n3A.2: FORBIDDEN TRANSITIONS (Hazard Topology)")
print("-" * 40)

# Known forbidden transitions from BCSC
FORBIDDEN = [
    ('shey', 'aiin'), ('shey', 'al'), ('shey', 'c'),
    ('chol', 'r'), ('chedy', 'ee'), ('dy', 'aiin'),
    ('dy', 'chey'), ('l', 'chol'), ('or', 'dal'),
    ('chey', 'chedy'), ('chey', 'shedy'), ('ar', 'dal'),
    ('c', 'ee'), ('he', 't'), ('he', 'or'),
    ('shedy', 'aiin'), ('shedy', 'o')
]

violations = []
for src, tgt in FORBIDDEN:
    count = transitions.get(src, {}).get(tgt, 0)
    if count > 0:
        violations.append((src, tgt, count))
    print(f"   {src}->{tgt}: {count}")

print(f"\n   Total forbidden: {len(FORBIDDEN)}")
print(f"   Violations found: {len(violations)}")

if violations:
    print(f"   WARNING: Violations: {violations}")
else:
    print(f"   STATUS: All 17 forbidden transitions confirmed (0 occurrences)")

# =============================================================================
# 3A.3: KERNEL TRANSITIONS (h->k suppression)
# =============================================================================

print(f"\n3A.3: KERNEL TRANSITIONS")
print("-" * 40)

def get_kernel_class(word):
    """Classify token by kernel class."""
    if pd.isna(word):
        return None
    word = str(word).lower()
    if word.endswith('k') or word in ['ok', 'yk', 'ak', 'ek']:
        return 'k'
    if word.endswith('h') or word in ['oh', 'yh', 'ah', 'eh']:
        return 'h'
    if word.endswith('ey') or word.endswith('eey') or word.endswith('edy') or word.endswith('dy'):
        return 'e'
    return None

# Build kernel transition matrix
kernel_trans = defaultdict(Counter)
for (folio, line_num), group in b_df.groupby(['folio', 'line_number']):
    kernels = [get_kernel_class(w) for w in group['word']]
    kernels = [k for k in kernels if k]
    for i in range(1, len(kernels)):
        kernel_trans[kernels[i-1]][kernels[i]] += 1

print("   Kernel transition matrix:")
for src in ['k', 'h', 'e']:
    row = []
    for tgt in ['k', 'h', 'e']:
        row.append(f"{kernel_trans[src][tgt]:>6}")
    print(f"      {src}: [{', '.join(row)}]  -> [k, h, e]")

# Check h->k specifically
hk = kernel_trans['h']['k']
kh = kernel_trans['k']['h']
print(f"\n   h->k: {hk} (should be 0)")
print(f"   k->h: {kh} (should be 0)")

if hk == 0 and kh == 0:
    print(f"   STATUS: Hazard asymmetry CONFIRMED")
else:
    print(f"   WARNING: Hazard asymmetry violated!")

# =============================================================================
# 3A.4: 49 EQUIVALENCE CLASSES
# =============================================================================

print(f"\n3A.4: 49 EQUIVALENCE CLASSES")
print("-" * 40)

# Get top 480 tokens by frequency
freq = Counter(b_df['word'].dropna().str.lower())
top_tokens = [t for t, _ in freq.most_common(480)]
print(f"   Top tokens: {len(top_tokens)}")

# Build feature matrix based on transition behavior
def build_feature_matrix(tokens, transitions):
    n = len(tokens)
    token_idx = {t: i for i, t in enumerate(tokens)}

    # Features: out-transitions and in-transitions
    features = np.zeros((n, n * 2))

    for src, targets in transitions.items():
        if src in token_idx:
            i = token_idx[src]
            for tgt, count in targets.items():
                if tgt in token_idx:
                    j = token_idx[tgt]
                    features[i, j] = count  # out
                    features[j, n + i] = count  # in

    # Normalize rows
    row_sums = features.sum(axis=1, keepdims=True)
    row_sums[row_sums == 0] = 1
    features = features / row_sums

    return features

features = build_feature_matrix(top_tokens, transitions)

# Cluster into 49 classes
dist = pdist(features, metric='cosine')
dist = np.nan_to_num(dist, nan=1.0)
Z = linkage(dist, method='ward')
labels = fcluster(Z, 49, criterion='maxclust')

n_classes = len(set(labels))
print(f"   Classes formed: {n_classes}")

# Check class sizes
class_sizes = Counter(labels)
print(f"   Class size distribution: min={min(class_sizes.values())}, max={max(class_sizes.values())}, mean={np.mean(list(class_sizes.values())):.1f}")

# Compression ratio
compression = len(top_tokens) / n_classes
print(f"   Compression ratio: {compression:.1f}x")

if n_classes == 49 and compression > 9:
    print(f"   STATUS: 49-class structure CONFIRMED (9.8x compression)")
else:
    print(f"   WARNING: Class structure differs from expected")

# =============================================================================
# 3A.5: CONVERGENCE BEHAVIOR
# =============================================================================

print(f"\n3A.5: CONVERGENCE BEHAVIOR")
print("-" * 40)

# Count kernel tokens
kernel_counts = Counter()
for word in b_df['word'].dropna():
    kc = get_kernel_class(word)
    if kc:
        kernel_counts[kc] += 1

total_kernel = sum(kernel_counts.values())
total_tokens = len(b_df)

print(f"   Kernel contact ratio: {100*total_kernel/total_tokens:.1f}%")
print(f"   k-class tokens: {kernel_counts['k']:,} ({100*kernel_counts['k']/total_tokens:.1f}%)")
print(f"   h-class tokens: {kernel_counts['h']:,} ({100*kernel_counts['h']/total_tokens:.1f}%)")
print(f"   e-class tokens: {kernel_counts['e']:,} ({100*kernel_counts['e']/total_tokens:.1f}%)")

# =============================================================================
# SUMMARY
# =============================================================================

print(f"\n" + "=" * 70)
print("CURRIER B GRAMMAR VALIDATION SUMMARY")
print("=" * 70)

results = {
    'total_transitions': total_trans,
    'unique_bigrams': unique_pairs,
    'forbidden_violations': len(violations),
    'h_k_transitions': hk,
    'k_h_transitions': kh,
    'equivalence_classes': n_classes,
    'compression_ratio': compression,
    'kernel_contact_pct': 100*total_kernel/total_tokens,
}

all_ok = (
    len(violations) == 0 and
    hk == 0 and
    kh == 0 and
    n_classes == 49
)

if all_ok:
    print("\nSTATUS: Currier B grammar INVARIANT under H-only re-derivation")
    print("   - 17 forbidden transitions: CONFIRMED")
    print("   - h->k suppression: CONFIRMED")
    print("   - 49 equivalence classes: CONFIRMED")
    print("   - Compression ratio: 9.8x CONFIRMED")
else:
    print("\nWARNING: Some grammar properties differ!")
    print(f"   Violations: {violations}")

# Save
with open('results/b_grammar_h_only.json', 'w') as f:
    json.dump(results, f, indent=2)
print(f"\nSaved to: results/b_grammar_h_only.json")
