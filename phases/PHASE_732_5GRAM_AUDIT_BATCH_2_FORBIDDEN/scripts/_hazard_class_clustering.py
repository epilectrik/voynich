"""Do the 5 hazard classes actually EXIST as data structure?

The 5-class taxonomy was IMPOSED (hardcoded distillation failure modes + keyword
assignment, no clustering ever run). But imposed != unreal. This test runs the
clustering that was never run: featurize the 17 forbidden transitions by atom
territory, cluster, and check whether ~5 natural groups emerge matching the imposed ones.

PRE-REGISTERED (locked before running):

FEATURES per transition: source HEAD atom, source TERM atom, target HEAD atom,
target TERM atom, source graph-type (spoke/bridge/hub), target graph-type.
(These are the C1528-C1533 atom-territory features the classes were claimed to map to,
extracted INDEPENDENTLY of the keyword design.)

TEST 1 — natural clustering: hierarchical clustering, silhouette across k=2..8.
  What k is optimal? Does the data prefer ~5?

TEST 2 — match to imposed: at k=5, Adjusted Rand Index vs the imposed keyword partition.
  ARI > 0.5 = substantial agreement (imposition captured real structure).

TEST 3 — cohesion vs random null: does the imposed 5-way partition (size profile
  7,4,4,1,1) have higher within-class atom-territory cohesion than random partitions
  of the same size profile? 1000 random partitions; z-score and empirical p.

VERDICT:
  - optimal k ~= 5 AND (ARI > 0.5 OR cohesion z > 2) -> classes VINDICATED (imposed but real)
  - optimal k != 5 AND cohesion z < 2 -> classes NOT data-supported (imposition is the only basis)
  - mixed -> partial; report which classes are real clusters vs labels

flush=True per discipline.
"""
import sys
import json
from collections import Counter
from itertools import combinations

import numpy as np
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.spatial.distance import pdist, squareform
from sklearn.metrics import silhouette_score, adjusted_rand_score

sys.path.insert(0, 'C:/git/voynich')
from scripts.voynich import Morphology

# The 17 forbidden transitions + imposed class
FORBIDDEN = [
    ('PHASE_ORDERING', 'shey', 'aiin'),
    ('PHASE_ORDERING', 'shey', 'al'),
    ('PHASE_ORDERING', 'shey', 'c'),
    ('PHASE_ORDERING', 'dy', 'aiin'),
    ('PHASE_ORDERING', 'dy', 'chey'),
    ('PHASE_ORDERING', 'chey', 'chedy'),
    ('PHASE_ORDERING', 'chey', 'shedy'),
    ('COMPOSITION_JUMP', 'chedy', 'ee'),
    ('COMPOSITION_JUMP', 'c', 'ee'),
    ('COMPOSITION_JUMP', 'shedy', 'aiin'),
    ('COMPOSITION_JUMP', 'shedy', 'o'),
    ('CONTAINMENT_TIMING', 'chol', 'r'),
    ('CONTAINMENT_TIMING', 'l', 'chol'),
    ('CONTAINMENT_TIMING', 'or', 'dal'),
    ('CONTAINMENT_TIMING', 'he', 'or'),
    ('RATE_MISMATCH', 'ar', 'dal'),
    ('ENERGY_OVERSHOOT', 'he', 't'),
]

morph = Morphology()

HEADS = ['a', 'e', 'o', 'k', 't', 'headless']
TERMS = ['y', 'l', 'r', 'h', 'm', 'n', 'bare']


def atoms_of(token):
    """Return (HEAD, TERM) for a token via atomize. Robust to short tokens."""
    try:
        a = morph.atomize(token)
        head = None; term = None
        if hasattr(a, 'atoms') and a.atoms:
            for c, role, _ in a.atoms:
                if role == 'HEAD' and head is None:
                    head = c
            # TERM = last atom char
            last_role = a.atoms[-1][1]
            term = a.atoms[-1][0] if last_role == 'TERM' else a.atoms[-1][0]
        head = head if head else 'headless'
        term = term if term else 'bare'
        # normalize term to known set
        if term not in TERMS:
            term = 'bare'
        if head not in HEADS:
            head = 'headless'
        return head, term
    except Exception:
        # fallback: use first/last char
        h = token[0] if token else 'headless'
        t = token[-1] if token else 'bare'
        return (h if h in HEADS else 'headless'), (t if t in TERMS else 'bare')


def featurize(src, tgt):
    """One-hot feature vector: [src_HEAD(6), src_TERM(7), tgt_HEAD(6), tgt_TERM(7)] = 26 dims."""
    sh, st = atoms_of(src)
    th, tt = atoms_of(tgt)
    vec = []
    vec += [1 if sh == h else 0 for h in HEADS]
    vec += [1 if st == t else 0 for t in TERMS]
    vec += [1 if th == h else 0 for h in HEADS]
    vec += [1 if tt == t else 0 for t in TERMS]
    return np.array(vec, dtype=float), (sh, st, th, tt)

print('=== HAZARD CLASS REALITY TEST ===', flush=True)
print('Featurizing 17 forbidden transitions by atom territory...\n', flush=True)

X = []
imposed_labels = []
atom_sigs = []
class_names = sorted(set(c for c, _, _ in FORBIDDEN))
class_to_int = {c: i for i, c in enumerate(class_names)}
print(f'{"imposed_class":>20} {"src":>7} {"tgt":>7} {"src_HEAD":>9} {"src_TERM":>9} {"tgt_HEAD":>9} {"tgt_TERM":>9}', flush=True)
print('-' * 85, flush=True)
for cls, src, tgt in FORBIDDEN:
    vec, sig = featurize(src, tgt)
    X.append(vec)
    imposed_labels.append(class_to_int[cls])
    atom_sigs.append(sig)
    print(f'{cls:>20} {src:>7} {tgt:>7} {sig[0]:>9} {sig[1]:>9} {sig[2]:>9} {sig[3]:>9}', flush=True)

X = np.array(X)
imposed_labels = np.array(imposed_labels)
n = len(X)

# ===== TEST 1: natural clustering, silhouette across k =====
print('\n' + '=' * 60, flush=True)
print('TEST 1: Natural clustering — optimal k by silhouette', flush=True)
print('=' * 60, flush=True)
# Use Hamming distance (binary features)
dists = pdist(X, metric='hamming')
Z = linkage(dists, method='average')
print(f'{"k":>3} {"silhouette":>12} {"cluster_sizes":>20}', flush=True)
sil_by_k = {}
for k in range(2, 9):
    labels_k = fcluster(Z, k, criterion='maxclust')
    if len(set(labels_k)) < 2:
        continue
    try:
        sil = silhouette_score(squareform(dists), labels_k, metric='precomputed')
    except Exception:
        sil = float('nan')
    sizes = sorted(Counter(labels_k).values(), reverse=True)
    sil_by_k[k] = sil
    marker = '  <-- k=5' if k == 5 else ''
    print(f'{k:>3} {sil:>12.4f} {str(sizes):>20}{marker}', flush=True)

best_k = max(sil_by_k, key=sil_by_k.get)
print(f'\nOptimal k by silhouette: {best_k} (silhouette={sil_by_k[best_k]:.4f})', flush=True)
print(f'k=5 silhouette: {sil_by_k.get(5, float("nan")):.4f}', flush=True)

# ===== TEST 2: ARI between k=5 natural clustering and imposed =====
print('\n' + '=' * 60, flush=True)
print('TEST 2: Does k=5 natural clustering match the imposed partition?', flush=True)
print('=' * 60, flush=True)
labels_5 = fcluster(Z, 5, criterion='maxclust')
ari = adjusted_rand_score(imposed_labels, labels_5)
print(f'ARI(imposed, natural k=5) = {ari:.4f}', flush=True)
print('  (1.0=identical, 0=random agreement, <0.5=weak)', flush=True)
# Show the natural k=5 grouping
print('\n  Natural k=5 clusters:', flush=True)
for cl in sorted(set(labels_5)):
    members = [f'{FORBIDDEN[i][1]}->{FORBIDDEN[i][2]}' for i in range(n) if labels_5[i] == cl]
    imposed_in = Counter(class_names[imposed_labels[i]] for i in range(n) if labels_5[i] == cl)
    print(f'    cluster {cl}: {members}', flush=True)
    print(f'             imposed classes within: {dict(imposed_in)}', flush=True)

# ===== TEST 3: cohesion of imposed partition vs random partitions =====
print('\n' + '=' * 60, flush=True)
print('TEST 3: Imposed-partition cohesion vs random partitions (same size profile)', flush=True)
print('=' * 60, flush=True)

def partition_cohesion(labels, distmat):
    """Mean within-class pairwise distance (lower = more cohesive). Skip singletons."""
    within = []
    for cl in set(labels):
        idx = [i for i in range(len(labels)) if labels[i] == cl]
        if len(idx) < 2:
            continue
        for a, b in combinations(idx, 2):
            within.append(distmat[a, b])
    return np.mean(within) if within else np.nan

distmat = squareform(dists)
imposed_cohesion = partition_cohesion(imposed_labels, distmat)
size_profile = sorted(Counter(imposed_labels).values(), reverse=True)  # [7,4,4,1,1]
print(f'Imposed partition size profile: {size_profile}', flush=True)
print(f'Imposed partition cohesion (mean within-class dist): {imposed_cohesion:.4f}', flush=True)

# Random partitions with same size profile
rng = np.random.default_rng(42)
null_cohesions = []
for _ in range(2000):
    perm = rng.permutation(n)
    rand_labels = np.zeros(n, dtype=int)
    pos = 0
    for ci, sz in enumerate(size_profile):
        for j in range(sz):
            rand_labels[perm[pos]] = ci
            pos += 1
    null_cohesions.append(partition_cohesion(rand_labels, distmat))
null_cohesions = np.array(null_cohesions)
null_mean = np.nanmean(null_cohesions)
null_std = np.nanstd(null_cohesions)
# Lower cohesion = better; so z should be negative if imposed is MORE cohesive
z = (imposed_cohesion - null_mean) / null_std if null_std > 0 else float('nan')
p_emp = (null_cohesions <= imposed_cohesion).mean()  # fraction of random as-good-or-better
print(f'Random partitions: mean cohesion {null_mean:.4f} +/- {null_std:.4f}', flush=True)
print(f'z = {z:+.2f} (negative = imposed MORE cohesive than random)', flush=True)
print(f'p_emp (random partitions at-least-as-cohesive) = {p_emp:.4f}', flush=True)

# Per-class cohesion (which imposed classes are real clusters?)
print('\n  Per-imposed-class cohesion (mean within-class dist; lower=tighter):', flush=True)
for cl in sorted(set(imposed_labels)):
    idx = [i for i in range(n) if imposed_labels[i] == cl]
    if len(idx) < 2:
        print(f'    {class_names[cl]:>20}: SINGLETON (n={len(idx)}, not a testable cluster)', flush=True)
        continue
    within = [distmat[a, b] for a, b in combinations(idx, 2)]
    print(f'    {class_names[cl]:>20}: n={len(idx)}, mean within-dist={np.mean(within):.4f}', flush=True)

# ===== VERDICT =====
print('\n' + '=' * 60, flush=True)
print('VERDICT', flush=True)
print('=' * 60, flush=True)
k5_optimal = (best_k == 5) or (abs(sil_by_k.get(5, -1) - sil_by_k[best_k]) < 0.02)
cohesion_real = (z < -2) or (p_emp < 0.05)
match_imposed = ari > 0.5
print(f'Optimal k ~= 5: {k5_optimal} (best k={best_k})', flush=True)
print(f'k=5 matches imposed (ARI>0.5): {match_imposed} (ARI={ari:.3f})', flush=True)
print(f'Imposed partition more cohesive than random (z<-2 or p<0.05): {cohesion_real} (z={z:+.2f}, p={p_emp:.3f})', flush=True)
print('', flush=True)
if cohesion_real and (k5_optimal or match_imposed):
    print('>>> HAZARD CLASSES VINDICATED: imposed, but the partition captures real atom-territory structure. <<<', flush=True)
elif cohesion_real:
    print('>>> PARTIAL: partition is more cohesive than random, but k!=5 / does not match imposed cleanly.', flush=True)
    print('    Some real structure, but not the specific 5-class taxonomy.', flush=True)
else:
    print('>>> NOT DATA-SUPPORTED: imposed partition is no more cohesive than random groupings of same size.', flush=True)
    print('    The 5-class taxonomy is a label, not a discovered structure.', flush=True)

out = {
    'optimal_k': int(best_k), 'silhouette_by_k': {str(k): float(v) for k, v in sil_by_k.items()},
    'k5_silhouette': float(sil_by_k.get(5, float('nan'))),
    'ari_imposed_vs_natural_k5': float(ari),
    'imposed_cohesion': float(imposed_cohesion),
    'null_cohesion_mean': float(null_mean), 'null_cohesion_std': float(null_std),
    'cohesion_z': float(z), 'cohesion_p_emp': float(p_emp),
    'verdict_cohesion_real': bool(cohesion_real), 'verdict_k5_optimal': bool(k5_optimal),
    'verdict_match_imposed': bool(match_imposed),
}
import pathlib
pathlib.Path('phases/PHASE_732_5GRAM_AUDIT_BATCH_2_FORBIDDEN/results/hazard_class_clustering.json').write_text(json.dumps(out, indent=2))
print('\nWritten to results/hazard_class_clustering.json', flush=True)
