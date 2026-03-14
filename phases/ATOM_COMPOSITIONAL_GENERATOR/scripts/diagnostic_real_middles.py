#!/usr/bin/env python3
"""
Phase 585 Diagnostic: Apply logistic compatibility model to REAL MIDDLEs.

Isolates whether the 0.27 clustering gap is caused by:
  (a) weak compatibility prediction (logistic model can't predict real co-occurrence)
  (b) unrealistic synthetic MIDDLEs (model works on real atoms, fakes are wrong)

If predicted graph on real MIDDLEs has clustering ~0.60 → bottleneck is the model.
If predicted graph on real MIDDLEs has clustering ~0.87 → bottleneck is the MIDDLEs.
"""

import sys, json, functools, warnings
import numpy as np
import networkx as nx
from pathlib import Path
from collections import Counter, defaultdict
from scipy.sparse import csr_matrix
from scipy.sparse.linalg import eigsh
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)
warnings.filterwarnings('ignore', category=FutureWarning)

from scripts.voynich import Transcript, Morphology, decompose_middle_hmt, CategoryClassifier

ATOM_TO_CAT = CategoryClassifier.ATOM_TO_CATEGORY

# ============================================================
# Build real baseline (same as main script Step 0)
# ============================================================

print("=" * 70)
print("DIAGNOSTIC: Logistic model applied to REAL MIDDLEs")
print("=" * 70)

tx = Transcript()
morph = Morphology()

line_middles = defaultdict(set)
all_middles = set()

for tok in tx.currier_a():
    w = tok.word.strip()
    if not w or '*' in w or tok.placement.startswith('L'):
        continue
    m = morph.extract(w)
    mid = m.middle
    if not mid or len(mid) < 1:
        continue
    key = (tok.folio, tok.line)
    line_middles[key].add(mid)
    all_middles.add(mid)

middles = sorted(all_middles)
N = len(middles)
mid_to_idx = {m: i for i, m in enumerate(middles)}
print(f"  Unique MIDDLEs: {N}")

# Build REAL compatibility matrix
compat_real = np.zeros((N, N), dtype=np.int8)
for key, mids in line_middles.items():
    mids_list = [m for m in mids if m in mid_to_idx]
    for i in range(len(mids_list)):
        for j in range(i + 1, len(mids_list)):
            a, b = mid_to_idx[mids_list[i]], mid_to_idx[mids_list[j]]
            compat_real[a, b] = 1
            compat_real[b, a] = 1

real_edges = compat_real.sum() // 2
real_density = real_edges / (N * (N - 1) // 2)
G_real = nx.from_numpy_array(compat_real)
real_clustering = nx.average_clustering(G_real)
print(f"  Real edges: {real_edges}, density: {real_density:.4f}, clustering: {real_clustering:.4f}")

# ============================================================
# Decompose all real MIDDLEs into atoms
# ============================================================

decomps = {}
for mid in middles:
    head, mods, term, _ = decompose_middle_hmt(mid)
    atoms = set()
    if head:
        atoms.add(head)
    for c in mods:
        atoms.add(c)
    if term != 'bare':
        atoms.add(term)
    cat_votes = Counter()
    for c in mid:
        if c in ATOM_TO_CAT:
            cat_votes[ATOM_TO_CAT[c]] += 1
    cat = sorted(cat_votes, key=lambda x: (-cat_votes[x], x))[0] if cat_votes else 'UNKNOWN'
    decomps[mid] = {
        'head': head, 'mods': mods, 'term': term,
        'atoms': atoms, 'category': cat, 'length': len(mid),
    }

# ============================================================
# Fit logistic model (same as Step 1)
# ============================================================

print("\n  Fitting logistic model...")

pos_pairs = []
neg_pairs = []
for i in range(N):
    for j in range(i + 1, N):
        if compat_real[i, j] == 1:
            pos_pairs.append((i, j))
        else:
            neg_pairs.append((i, j))

rng = np.random.RandomState(42)
n_neg_sample = min(len(neg_pairs), len(pos_pairs) * 5)
neg_sample_idx = rng.choice(len(neg_pairs), n_neg_sample, replace=False)
neg_sample = [neg_pairs[i] for i in neg_sample_idx]

train_pairs = pos_pairs + neg_sample
train_labels = np.array([1] * len(pos_pairs) + [0] * len(neg_sample))

def pair_features(i, j):
    d1 = decomps[middles[i]]
    d2 = decomps[middles[j]]
    a1, a2 = d1['atoms'], d2['atoms']
    shared = len(a1 & a2)
    union = len(a1 | a2)
    jaccard = shared / union if union > 0 else 0
    same_head = 1 if d1['head'] == d2['head'] and d1['head'] is not None else 0
    same_term = 1 if d1['term'] == d2['term'] and d1['term'] != 'bare' else 0
    same_cat = 1 if d1['category'] == d2['category'] else 0
    len_diff = abs(d1['length'] - d2['length'])
    m1 = set(d1['mods'])
    m2 = set(d2['mods'])
    shared_mods = len(m1 & m2)
    return [shared, jaccard, same_head, same_term, same_cat, len_diff, shared_mods]

X_train = np.array([pair_features(i, j) for i, j in train_pairs])
lr = LogisticRegression(max_iter=1000, class_weight='balanced', random_state=42)
lr.fit(X_train, train_labels)

# ============================================================
# Predict compatibility for ALL real MIDDLE pairs
# ============================================================

print("  Predicting compatibility for all real MIDDLE pairs...")

# Get predicted probabilities for every pair
all_probs = np.zeros(N * (N - 1) // 2)
idx = 0
batch_X = []
batch_indices = []
batch_size = 50000

for i in range(N):
    for j in range(i + 1, N):
        batch_X.append(pair_features(i, j))
        batch_indices.append((i, j, idx))
        idx += 1
        if len(batch_X) >= batch_size:
            bX = np.array(batch_X)
            probs = lr.predict_proba(bX)[:, 1]
            for k, (ii, jj, bidx) in enumerate(batch_indices):
                all_probs[bidx] = probs[k]
            batch_X = []
            batch_indices = []

if batch_X:
    bX = np.array(batch_X)
    probs = lr.predict_proba(bX)[:, 1]
    for k, (ii, jj, bidx) in enumerate(batch_indices):
        all_probs[bidx] = probs[k]

# ============================================================
# Threshold sweep: find best threshold and density-matched threshold
# ============================================================

print("\n  Threshold sweep...")
print(f"  {'Threshold':>10s}  {'Edges':>7s}  {'Density':>8s}  {'Clustering':>11s}  {'Note':>20s}")
print(f"  {'-'*10}  {'-'*7}  {'-'*8}  {'-'*11}  {'-'*20}")

results = []
for threshold in [0.30, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60, 0.65, 0.70]:
    # Build predicted compatibility matrix at this threshold
    compat_pred = np.zeros((N, N), dtype=np.int8)
    idx = 0
    for i in range(N):
        for j in range(i + 1, N):
            if all_probs[idx] >= threshold:
                compat_pred[i, j] = 1
                compat_pred[j, i] = 1
            idx += 1

    pred_edges = compat_pred.sum() // 2
    pred_density = pred_edges / (N * (N - 1) // 2)
    G_pred = nx.from_numpy_array(compat_pred)
    pred_clustering = nx.average_clustering(G_pred)

    note = ""
    if abs(pred_density - real_density) < 0.003:
        note = "<-- density-matched"

    results.append({
        'threshold': threshold,
        'edges': pred_edges,
        'density': pred_density,
        'clustering': pred_clustering,
        'note': note,
    })
    print(f"  {threshold:10.2f}  {pred_edges:7d}  {pred_density:8.4f}  {pred_clustering:11.4f}  {note:>20s}")

# Also find the exact threshold that matches real density
print("\n  Finding exact density-matched threshold...")
# Binary search for threshold that gives closest density to real
lo, hi = 0.0, 1.0
for _ in range(50):
    mid_t = (lo + hi) / 2
    idx = 0
    n_edges_t = 0
    for i in range(N):
        for j in range(i + 1, N):
            if all_probs[idx] >= mid_t:
                n_edges_t += 1
            idx += 1
    density_t = n_edges_t / (N * (N - 1) // 2)
    if density_t > real_density:
        lo = mid_t
    else:
        hi = mid_t

best_threshold = (lo + hi) / 2
compat_matched = np.zeros((N, N), dtype=np.int8)
idx = 0
for i in range(N):
    for j in range(i + 1, N):
        if all_probs[idx] >= best_threshold:
            compat_matched[i, j] = 1
            compat_matched[j, i] = 1
        idx += 1

matched_edges = compat_matched.sum() // 2
matched_density = matched_edges / (N * (N - 1) // 2)
G_matched = nx.from_numpy_array(compat_matched)
matched_clustering = nx.average_clustering(G_matched)
matched_transitivity = nx.transitivity(G_matched)

print(f"\n  Density-matched threshold: {best_threshold:.4f}")
print(f"  Predicted edges: {matched_edges} (real: {real_edges})")
print(f"  Predicted density: {matched_density:.4f} (real: {real_density:.4f})")
print(f"  Predicted clustering: {matched_clustering:.4f} (real: {real_clustering:.4f})")
print(f"  Predicted transitivity: {matched_transitivity:.4f}")

# ============================================================
# Agreement analysis
# ============================================================

print("\n  Agreement between predicted and real compatibility:")
tp = fp = fn = tn = 0
idx = 0
for i in range(N):
    for j in range(i + 1, N):
        real = compat_real[i, j]
        pred = compat_matched[i, j]
        if real == 1 and pred == 1: tp += 1
        elif real == 0 and pred == 1: fp += 1
        elif real == 1 and pred == 0: fn += 1
        else: tn += 1
        idx += 1

precision = tp / (tp + fp) if (tp + fp) > 0 else 0
recall = tp / (tp + fn) if (tp + fn) > 0 else 0
f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
jaccard_overlap = tp / (tp + fp + fn) if (tp + fp + fn) > 0 else 0

print(f"  True Positives:  {tp:>7d}  (real=1, pred=1)")
print(f"  False Positives: {fp:>7d}  (real=0, pred=1)")
print(f"  False Negatives: {fn:>7d}  (real=1, pred=0)")
print(f"  True Negatives:  {tn:>7d}  (real=0, pred=0)")
print(f"  Precision: {precision:.4f}")
print(f"  Recall:    {recall:.4f}")
print(f"  F1:        {f1:.4f}")
print(f"  Edge Jaccard overlap: {jaccard_overlap:.4f}")

# ============================================================
# Verdict
# ============================================================

print("\n" + "=" * 70)
print("VERDICT")
print("=" * 70)

gap_from_model = real_clustering - matched_clustering
print(f"\n  Real clustering:           {real_clustering:.4f}")
print(f"  Predicted (real MIDDLEs):   {matched_clustering:.4f}")
print(f"  Predicted (synthetic):      ~0.60 (from Phase 585 main)")
print(f"  Gap (model bottleneck):     {gap_from_model:.4f}")
print(f"  Gap (MIDDLE bottleneck):    {matched_clustering - 0.60:.4f}")

if matched_clustering > 0.80:
    print(f"\n  DIAGNOSIS: MIDDLE GENERATION is the bottleneck.")
    print(f"  The logistic model reproduces clustering on real MIDDLEs.")
    print(f"  Synthetic MIDDLEs are too unlike real ones.")
elif matched_clustering < 0.65:
    print(f"\n  DIAGNOSIS: COMPATIBILITY MODEL is the bottleneck.")
    print(f"  Even with real MIDDLEs, atom features can't predict co-occurrence.")
    print(f"  The remaining clustering comes from non-compositional factors")
    print(f"  (line grammar, folio organization, paragraph structure).")
else:
    print(f"\n  DIAGNOSIS: MIXED — both contribute to the gap.")

# Save results
results_file = Path(__file__).parent.parent / 'results' / 'diagnostic_real_middles.json'
json.dump({  # convert numpy types
    'real_clustering': float(real_clustering),
    'real_density': float(real_density),
    'real_edges': int(real_edges),
    'matched_threshold': float(best_threshold),
    'matched_clustering': float(matched_clustering),
    'matched_transitivity': float(matched_transitivity),
    'matched_density': float(matched_density),
    'matched_edges': int(matched_edges),
    'agreement': {
        'tp': int(tp), 'fp': int(fp), 'fn': int(fn), 'tn': int(tn),
        'precision': float(precision), 'recall': float(recall), 'f1': float(f1),
        'jaccard_overlap': float(jaccard_overlap),
    },
    'threshold_sweep': [{k: (float(v) if isinstance(v, (np.floating, float)) else int(v) if isinstance(v, (np.integer, int)) else v) for k, v in r.items()} for r in results],
}, open(results_file, 'w'), indent=2)
print(f"\n  Saved to {results_file}")
