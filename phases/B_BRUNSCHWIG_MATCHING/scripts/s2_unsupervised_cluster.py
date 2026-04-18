"""
Phase 642, Script 2: Unsupervised clustering of all 82 B folios.

CRITICAL DESIGN: Do NOT use f55r's values as a cluster center or reference point.
Compute standardized feature vectors and cluster unsupervised. Only AFTER clusters
emerge, check whether f55r is an isolated outlier or genuine cluster member.

Features (all structural, no sensory-judgment interpretation per C1056):
  Prefix distribution: qo, ch, sh, ok, ot, lch, lk, da, ol, so, sa, pch
  HEAD atom distribution: k, e, o, a, t, d, l, c, h, r, i, n
  TERM atom distribution: y, n, m, l, s, a
  Suffix distribution: -aiin, -ain, -dy, -y, -am, -al, -ar, -or, -ol
  e-depth profile: rate of depth=0, depth=1, depth=2, depth=3+
  Opaque terminal rate
  qot-compound rate (apparatus-mediated operation marker)
  Mean tokens per paragraph
  Vocabulary diversity (unique-types / total-tokens)

Method:
  1. Compute 30+ dimensional feature vector per folio
  2. Standardize each dimension (z-score across folios)
  3. PCA to reduce dimensionality; visualize first 3 PCs
  4. k-means clustering with k=2,3,4; silhouette analysis
  5. Hierarchical clustering (Ward linkage)
  6. Check where matched-Testamentum folios land
  7. Check where f55r lands
  8. Decision gate: if matched-Testamentum folios AND f55r in same cluster
     → pharmaceutical regime hypothesis weakens, PHASE STOP
"""
import sys, io, os, json
from collections import Counter, defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, ROOT)

from scripts.voynich import Transcript, Morphology

tx = Transcript()
morph = Morphology()

# Matched Testamentum folios (for marker purposes — NOT used as cluster reference)
MATCHED = {
    'f75r', 'f76r', 'f84r', 'f79r', 'f82r', 'f103r', 'f76v',
    'f77v', 'f81v', 'f82v', 'f112r', 'f112v', 'f116r', 'f107r',
    'f80r', 'f83r',
}

# Also marker: f55r is the hand-picked candidate
MARKER = {'f55r'}

# ============================================================
# Build per-folio feature vectors
# ============================================================
folio_tokens = defaultdict(list)
for t in tx.currier_b():
    if not t.word.strip() or '*' in t.word: continue
    folio_tokens[t.folio].append(t)

print(f"Processing {len(folio_tokens)} folios...")

PREFIX_KEYS = ['qo', 'ch', 'sh', 'ok', 'ot', 'lch', 'lk', 'da', 'ol', 'so', 'sa', 'pch', 'po', 'or']
HEAD_KEYS = ['k', 'e', 'o', 'a', 't', 'd', 'l', 'c', 'h', 'r', 'i', 'n', 's', 'y']
TERM_KEYS = ['y', 'n', 'm', 'l', 'a']
SUFFIX_KEYS = ['iin', 'ain', 'dy', 'y', 'am', 'al', 'ar', 'or', 'ol']

def folio_features(folio):
    tokens = folio_tokens[folio]
    n = len(tokens)
    if n == 0: return None

    prefixes = Counter()
    heads = Counter()
    terms = Counter()
    suffixes = Counter()
    e_depth = Counter()
    opaque = 0
    term_tot = 0
    qot_count = 0
    par_count = 0

    unique_words = set()

    for t in tokens:
        unique_words.add(t.word)
        if t.par_initial: par_count += 1
        m = morph.extract(t.word)
        a = morph.atomize(t.word)
        prefixes[(m.prefix if m else None) or 'BARE'] += 1
        if m and m.suffix:
            suffixes[m.suffix] += 1
        if a and a.atoms:
            heads[a.atoms[0][0]] += 1
            terms[a.atoms[-1][0]] += 1
            term_tot += 1
            if a.terminal_opacity == 'OPAQUE': opaque += 1
            if a.e_depth is not None: e_depth[a.e_depth] += 1
            if m and m.prefix == 'qo' and a.atoms[0][0] == 't':
                qot_count += 1

    feats = {}
    # Prefix rates
    for px in PREFIX_KEYS:
        feats[f'px_{px}'] = prefixes[px] / n
    feats['px_BARE'] = prefixes['BARE'] / n
    # Head atom rates
    for h in HEAD_KEYS:
        feats[f'head_{h}'] = heads[h] / n
    # Term atom rates
    for t_k in TERM_KEYS:
        feats[f'term_{t_k}'] = terms[t_k] / n
    # Suffix rates
    for s in SUFFIX_KEYS:
        feats[f'suf_{s}'] = suffixes[s] / n
    # e-depth profile
    for d in [0, 1, 2, 3]:
        feats[f'edepth_{d}'] = e_depth[d] / n
    # Opaque rate
    feats['opaque_rate'] = opaque / max(1, term_tot)
    # qot compound rate
    feats['qot_rate'] = qot_count / n
    # Paragraph density
    feats['par_per_100tok'] = par_count / n * 100
    # Vocabulary diversity
    feats['vocab_diversity'] = len(unique_words) / n
    # Token count (log-transformed)
    import math
    feats['log_tokens'] = math.log(n)

    return feats

# Build feature matrix
folio_list = sorted(folio_tokens.keys())
feature_names = None
feat_matrix = []
for folio in folio_list:
    feats = folio_features(folio)
    if feats is None: continue
    if feature_names is None:
        feature_names = sorted(feats.keys())
    feat_matrix.append([feats[name] for name in feature_names])

# Filter out too-small folios (noise)
min_tokens = 30
kept_indices = [i for i, folio in enumerate(folio_list) if len(folio_tokens[folio]) >= min_tokens]
folio_list_kept = [folio_list[i] for i in kept_indices]
feat_matrix_kept = [feat_matrix[i] for i in kept_indices]

print(f"Folios retained (≥{min_tokens} tokens): {len(folio_list_kept)}/{len(folio_list)}")
print(f"Features per folio: {len(feature_names)}")

# Standardize each feature (z-score)
import statistics as stats
n_folios = len(feat_matrix_kept)
n_feats = len(feature_names)

# Compute means and stdevs per feature
means = [sum(row[j] for row in feat_matrix_kept) / n_folios for j in range(n_feats)]
stdevs = []
for j in range(n_feats):
    vals = [row[j] for row in feat_matrix_kept]
    s = stats.stdev(vals) if len(vals) > 1 else 1.0
    stdevs.append(s if s > 0 else 1.0)

# Z-score standardization
z_matrix = []
for row in feat_matrix_kept:
    z = [(row[j] - means[j]) / stdevs[j] for j in range(n_feats)]
    z_matrix.append(z)

# ============================================================
# Pairwise Euclidean distances
# ============================================================
def euclidean(a, b):
    return sum((a[i]-b[i])**2 for i in range(len(a))) ** 0.5

print("\nComputing pairwise distances...")
dist_matrix = [[0.0]*n_folios for _ in range(n_folios)]
for i in range(n_folios):
    for j in range(i+1, n_folios):
        d = euclidean(z_matrix[i], z_matrix[j])
        dist_matrix[i][j] = d
        dist_matrix[j][i] = d

# ============================================================
# PCA (manual: covariance -> eigendecomp via power iteration)
# ============================================================
# Simple PCA via covariance matrix and numpy would be cleaner.
# Let me try to use numpy if available.
try:
    import numpy as np
    has_numpy = True
except ImportError:
    has_numpy = False

print(f"\nNumpy available: {has_numpy}")

if has_numpy:
    Z = np.array(z_matrix)
    # Cov matrix
    cov = np.cov(Z.T)
    eigvals, eigvecs = np.linalg.eigh(cov)
    # Sort descending
    order = np.argsort(eigvals)[::-1]
    eigvals = eigvals[order]
    eigvecs = eigvecs[:, order]

    print(f"\nTop 5 PC variance ratios:")
    var_total = sum(max(0, v) for v in eigvals)
    for pc in range(5):
        pct = 100 * eigvals[pc] / var_total if var_total else 0
        print(f"  PC{pc+1}: {eigvals[pc]:.2f} ({pct:.1f}%)")

    # Project all folios onto first 3 PCs
    pcs = Z @ eigvecs[:, :3]

    print(f"\nPC1-PC3 loadings (top 10 features for PC1):")
    pc1_loadings = list(zip(feature_names, eigvecs[:, 0]))
    pc1_loadings.sort(key=lambda x: -abs(x[1]))
    for feat, load in pc1_loadings[:10]:
        print(f"  {feat:<20s}: {load:+.3f}")

    # Print PC scores for marker folios (matched Testamentum + f55r)
    print("\nPC1-PC3 scores for MATCHED folios (should cluster if method works):")
    matched_pcs = []
    for i, folio in enumerate(folio_list_kept):
        if folio in MATCHED:
            matched_pcs.append(pcs[i])
            print(f"  {folio:<7s} PC1={pcs[i,0]:+.2f}  PC2={pcs[i,1]:+.2f}  PC3={pcs[i,2]:+.2f}")

    print("\nPC1-PC3 scores for MARKER folio (f55r):")
    for i, folio in enumerate(folio_list_kept):
        if folio in MARKER:
            print(f"  {folio:<7s} PC1={pcs[i,0]:+.2f}  PC2={pcs[i,1]:+.2f}  PC3={pcs[i,2]:+.2f}")

    # ============================================================
    # K-means clustering (k=2, 3, 4) + silhouette scores
    # ============================================================
    def kmeans(X, k, n_iter=100, seed=42):
        np.random.seed(seed)
        n = len(X)
        # Initialize cluster centers from random folio points
        idx = np.random.choice(n, k, replace=False)
        centers = X[idx].copy()
        for _ in range(n_iter):
            # Assign
            distances = np.linalg.norm(X[:, None, :] - centers[None, :, :], axis=2)
            labels = distances.argmin(axis=1)
            # Update
            new_centers = np.array([X[labels == c].mean(axis=0) if (labels == c).any() else centers[c] for c in range(k)])
            if np.allclose(new_centers, centers): break
            centers = new_centers
        return labels, centers

    def silhouette(X, labels):
        n = len(X)
        scores = []
        for i in range(n):
            own_cluster = X[labels == labels[i]]
            if len(own_cluster) <= 1:
                scores.append(0)
                continue
            a = np.mean(np.linalg.norm(own_cluster - X[i], axis=1))
            others = [c for c in set(labels) if c != labels[i]]
            b = min(np.mean(np.linalg.norm(X[labels == c] - X[i], axis=1)) for c in others) if others else a
            scores.append((b - a) / max(a, b) if max(a, b) > 0 else 0)
        return np.mean(scores)

    print("\n" + "="*80)
    print("K-MEANS CLUSTERING")
    print("="*80)

    # Use first 5 PCs for clustering (reduces noise from high-dim)
    X_reduced = (Z @ eigvecs[:, :5])

    results_by_k = {}
    for k in [2, 3, 4]:
        best_labels = None
        best_sil = -1
        for seed in range(10):  # multi-restart
            labels, _ = kmeans(X_reduced, k, seed=seed)
            sil = silhouette(X_reduced, labels)
            if sil > best_sil:
                best_sil = sil
                best_labels = labels
        results_by_k[k] = (best_labels, best_sil)
        print(f"\nk={k}: silhouette = {best_sil:.3f}")
        cluster_sizes = Counter(best_labels)
        print(f"  Cluster sizes: {dict(cluster_sizes)}")
        # Check where matched + f55r land
        matched_clusters = Counter()
        f55r_cluster = None
        for i, folio in enumerate(folio_list_kept):
            if folio in MATCHED:
                matched_clusters[int(best_labels[i])] += 1
            if folio in MARKER:
                f55r_cluster = int(best_labels[i])
        print(f"  Matched Testamentum folios distribution: {dict(matched_clusters)}")
        print(f"  f55r cluster: {f55r_cluster}")
        if f55r_cluster is not None and matched_clusters:
            same_cluster = matched_clusters.get(f55r_cluster, 0)
            total_matched = sum(matched_clusters.values())
            pct = 100 * same_cluster / total_matched
            if pct >= 50:
                print(f"  *** f55r is in the MAJORITY matched cluster ({same_cluster}/{total_matched} matched folios there) ***")
                print(f"  *** Pharmaceutical-regime hypothesis WEAKENED for k={k} ***")
            else:
                print(f"  f55r is in a MINORITY cluster ({same_cluster}/{total_matched} matched folios there)")
                print(f"  Pharmaceutical-regime hypothesis SUPPORTED for k={k}")

    # Print nearest-neighbors of f55r
    print("\n" + "="*80)
    print("f55r NEAREST NEIGHBORS (top-20 by Euclidean distance)")
    print("="*80)
    f55r_idx = None
    for i, folio in enumerate(folio_list_kept):
        if folio == 'f55r':
            f55r_idx = i
            break
    if f55r_idx is not None:
        dists = [(folio_list_kept[j], dist_matrix[f55r_idx][j]) for j in range(n_folios) if j != f55r_idx]
        dists.sort(key=lambda x: x[1])
        for rank, (folio, d) in enumerate(dists[:20], 1):
            marker = ' [MATCHED]' if folio in MATCHED else ''
            print(f"  {rank:2d}. {folio:<7s} d={d:.2f}{marker}")

        # Also the 20 FARTHEST
        print("\nf55r FARTHEST neighbors (top-20):")
        for rank, (folio, d) in enumerate(dists[-20:][::-1], 1):
            marker = ' [MATCHED]' if folio in MATCHED else ''
            print(f"  {rank:2d}. {folio:<7s} d={d:.2f}{marker}")

    # ============================================================
    # DECISION GATE
    # ============================================================
    print("\n" + "="*80)
    print("DECISION GATE")
    print("="*80)

    # Check best k
    best_k = max(results_by_k.keys(), key=lambda k: results_by_k[k][1])
    best_labels, best_sil = results_by_k[best_k]

    print(f"\nBest clustering: k={best_k} (silhouette={best_sil:.3f})")

    # Where does f55r land?
    f55r_cluster = int(best_labels[f55r_idx])
    matched_in_f55r = sum(1 for i, folio in enumerate(folio_list_kept)
                         if folio in MATCHED and int(best_labels[i]) == f55r_cluster)
    total_matched_found = sum(1 for f in folio_list_kept if f in MATCHED)
    matched_frac_in_f55r = matched_in_f55r / total_matched_found if total_matched_found else 0

    f55r_cluster_size = sum(1 for l in best_labels if int(l) == f55r_cluster)

    print(f"\nf55r in cluster {f55r_cluster} (size {f55r_cluster_size})")
    print(f"{matched_in_f55r}/{total_matched_found} matched-Testamentum folios in f55r's cluster ({100*matched_frac_in_f55r:.1f}%)")

    if matched_frac_in_f55r >= 0.5:
        print("\n*** VERDICT: PHARMACEUTICAL-REGIME HYPOTHESIS WEAKENED ***")
        print("    f55r clusters with the majority of Testamentum-matched folios.")
        print("    The 'second regime' is NOT structurally distinguishable at this feature resolution.")
        print("    Phase 642 full pipeline is PREMATURE.")
    elif f55r_cluster_size == 1:
        print("\n*** VERDICT: f55r is a CLUSTER OF ONE ***")
        print("    f55r doesn't group with any other folios even at finer structure.")
        print("    'Pharmaceutical regime' hypothesis is based on a SINGLE DATA POINT.")
        print("    Phase 642 full pipeline is PREMATURE.")
    elif f55r_cluster_size < 5:
        print(f"\n*** VERDICT: TINY COHORT (n={f55r_cluster_size}) ***")
        print("    f55r is in a small cluster. Look at cluster members to see if they share plant IDs.")
        print("    Proceed with caution; phase may be worthwhile on this small cohort only.")
    else:
        print(f"\n*** VERDICT: POTENTIAL REGIME CLUSTER (n={f55r_cluster_size}) ***")
        print(f"    f55r is in a moderate cluster ({f55r_cluster_size} folios) mostly separate from matched-Testamentum ({matched_frac_in_f55r*100:.1f}% overlap).")
        print("    Phase 642 full pipeline JUSTIFIED. Proceed to Brunschwig segmentation + matching.")

    # Print folios in f55r's cluster
    print(f"\nFolios in f55r's cluster (k={best_k}, cluster {f55r_cluster}):")
    for i, folio in enumerate(folio_list_kept):
        if int(best_labels[i]) == f55r_cluster:
            marker = ' [MATCHED]' if folio in MATCHED else ' [f55r]' if folio == 'f55r' else ''
            print(f"  {folio:<7s} PC1={pcs[i,0]:+.2f}  PC2={pcs[i,1]:+.2f}{marker}")

    # Save
    out = {
        'metadata': {
            'phase': 642, 'script': 's2_unsupervised_cluster',
            'n_folios': n_folios, 'n_features': n_feats,
            'min_tokens': min_tokens,
        },
        'feature_names': feature_names,
        'best_k': best_k, 'best_silhouette': float(best_sil),
        'cluster_assignments': {folio_list_kept[i]: int(best_labels[i]) for i in range(n_folios)},
        'f55r_cluster': f55r_cluster,
        'matched_testamentum_distribution': dict(Counter(
            int(best_labels[i]) for i, folio in enumerate(folio_list_kept) if folio in MATCHED
        )),
        'matched_in_f55r_cluster': int(matched_in_f55r),
        'total_matched': int(total_matched_found),
        'f55r_cluster_size': int(f55r_cluster_size),
        'f55r_nearest_20': [f for f, d in dists[:20]] if f55r_idx is not None else [],
    }
    out_path = os.path.join(os.path.dirname(__file__), '..', 'results', 'unsupervised_cluster.json')
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(out, f, indent=2)
    print(f"\nWrote {out_path}")

else:
    print("numpy not available, skipping PCA/clustering")
