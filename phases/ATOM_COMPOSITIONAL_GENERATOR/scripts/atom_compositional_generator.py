#!/usr/bin/env python3
"""
Phase 585: ATOM_COMPOSITIONAL_GENERATOR
F-BRU-003 Retest with Atom Architecture

Tests whether atom-compositional MIDDLE generation reproduces the
discrimination manifold (C982-C984). F-BRU-003 (v2.44, 2026-01-15)
tested a naive property generator BEFORE the atom architecture was
discovered. This phase retests with the full atom model.

Key question: Does atom composition → category assignment explain
the 0.873 clustering coefficient (C983)?
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
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)
warnings.filterwarnings('ignore', category=FutureWarning)

from scripts.voynich import Transcript, Morphology, CategoryClassifier, decompose_middle_hmt

RESULTS_DIR = Path(__file__).parent.parent / 'results'
RESULTS_DIR.mkdir(exist_ok=True)

# ============================================================
# ATOM ARCHITECTURE CONSTANTS (from C1475, C1479, C1472, etc.)
# ============================================================

HEADS = {'a', 'e', 'o', 'k', 't'}
MODIFIERS = {'p', 'f', 'i', 'c', 'd', 's'}
TERMINALS = {'y', 'l', 'r', 'h', 'm', 'n'}

ATOM_TO_CAT = CategoryClassifier.ATOM_TO_CATEGORY

# C1475: HEAD domain frequencies (token-level)
HEAD_FREQS = {'k': 0.134, 't': 0.040, 'a': 0.133, 'e': 0.303,
              'o': 0.118, None: 0.272}

# C1479: Per-HEAD modifier probability (any modifier at all)
HEAD_MOD_RATE = {'k': 0.135, 't': 0.205, 'a': 0.513, 'e': 0.446,
                 'o': 0.313, None: 0.578}

# C1479: Per-HEAD modifier selection weights (conditional on having a modifier)
# These are relative weights for which modifier is chosen given this HEAD
HEAD_MOD_WEIGHTS = {
    'k': {'c': 0.60, 's': 0.20, 'p': 0.05, 'f': 0.05, 'i': 0.05, 'd': 0.05},
    't': {'c': 0.65, 's': 0.15, 'p': 0.05, 'f': 0.05, 'i': 0.05, 'd': 0.05},
    'a': {'i': 0.785, 's': 0.08, 'c': 0.05, 'd': 0.04, 'p': 0.02, 'f': 0.025},
    'e': {'d': 0.381, 'c': 0.20, 's': 0.15, 'i': 0.10, 'p': 0.10, 'f': 0.069},
    'o': {'c': 0.30, 'p': 0.30, 'f': 0.15, 's': 0.15, 'd': 0.05, 'i': 0.05},
    None: {'i': 0.20, 'd': 0.20, 'c': 0.18, 's': 0.17, 'p': 0.13, 'f': 0.12},
}

# C1472: Forbidden modifier pairs (8 of 15)
FORBIDDEN_MOD_PAIRS = {
    frozenset({'p', 'f'}), frozenset({'p', 'i'}), frozenset({'p', 'c'}),
    frozenset({'p', 'd'}), frozenset({'f', 'c'}), frozenset({'f', 'd'}),
    frozenset({'i', 'c'}), frozenset({'i', 'd'}),
}

# C1487: Terminal frequencies (approximate from data)
TERM_FREQS = {'y': 0.22, 'h': 0.18, 'l': 0.13, 'n': 0.10,
              'r': 0.08, 'm': 0.04, 'bare': 0.25}

# C1484: Terminal-modifier exclusivity
# n pairs ONLY with i; y pairs ONLY with d; h takes {c,p,f,s}
TERM_MOD_ALLOWED = {
    'n': {'i'},
    'y': {'d'},
    'h': {'c', 'p', 'f', 's'},
    'l': MODIFIERS,  # no restriction
    'r': MODIFIERS,
    'm': MODIFIERS,
    'bare': MODIFIERS,
}

# C1210: Forbidden INITIAL-TERMINAL pairs (near-categorical)
FORBIDDEN_INIT_TERM = {
    ('a', 'y'), ('e', 'n'), ('i', 'y'), ('k', 'n'), ('c', 'n'),
    ('c', 'l'), ('d', 'n'), ('t', 'n'), ('p', 'n'),
}


# ============================================================
# STEP 0: REAL VOYNICH BASELINE
# ============================================================

def build_real_baseline():
    """Build compatibility matrix and compute all metrics from real data."""
    print("=" * 70)
    print("STEP 0: REAL VOYNICH BASELINE (H-filtered, canonical library)")
    print("=" * 70)

    tx = Transcript()
    morph = Morphology()

    # Group MIDDLEs by (folio, line) for co-occurrence
    line_middles = defaultdict(set)
    all_middles = set()
    middle_folio_counts = Counter()

    for tok in tx.currier_a():
        w = tok.word.strip()
        if not w or '*' in w:
            continue
        if tok.placement.startswith('L'):
            continue
        m = morph.extract(w)
        mid = m.middle
        if not mid or len(mid) < 1:
            continue
        key = (tok.folio, tok.line)
        line_middles[key].add(mid)
        all_middles.add(mid)
        middle_folio_counts[mid] += 1  # count lines, not folios

    # Track folio spread for hub/tail
    mid_folios = defaultdict(set)
    for tok in tx.currier_a():
        w = tok.word.strip()
        if not w or '*' in w or tok.placement.startswith('L'):
            continue
        m = morph.extract(w)
        mid = m.middle
        if mid and len(mid) >= 1:
            mid_folios[mid].add(tok.folio)

    middles = sorted(all_middles)
    N = len(middles)
    mid_to_idx = {m: i for i, m in enumerate(middles)}

    print(f"  Unique MIDDLEs: {N}")
    print(f"  Lines with co-occurrence data: {len(line_middles)}")

    # Build binary compatibility matrix
    compat = np.zeros((N, N), dtype=np.int8)
    for key, mids in line_middles.items():
        mids_list = [m for m in mids if m in mid_to_idx]
        for i in range(len(mids_list)):
            for j in range(i + 1, len(mids_list)):
                a, b = mid_to_idx[mids_list[i]], mid_to_idx[mids_list[j]]
                compat[a, b] = 1
                compat[b, a] = 1

    # Compute metrics
    metrics = compute_graph_metrics(compat, middles, mid_folios)
    metrics['N'] = N

    print(f"\n  Metrics:")
    for k, v in metrics.items():
        if isinstance(v, float):
            print(f"    {k}: {v:.4f}")
        elif isinstance(v, dict):
            pass  # skip sub-dicts
        else:
            print(f"    {k}: {v}")

    return compat, middles, mid_to_idx, mid_folios, metrics


def compute_graph_metrics(compat_matrix, middles=None, mid_folios=None):
    """Compute full metric suite on a compatibility matrix."""
    N = compat_matrix.shape[0]
    n_edges = compat_matrix.sum() // 2
    n_pairs = N * (N - 1) // 2
    density = n_edges / n_pairs if n_pairs > 0 else 0

    # NetworkX graph
    G = nx.from_numpy_array(compat_matrix)
    clustering = nx.average_clustering(G)
    transitivity = nx.transitivity(G)

    # Eigenvalue spectrum (top 50)
    mat = compat_matrix.copy().astype(np.float64)
    np.fill_diagonal(mat, 1)
    try:
        k_eig = min(50, N - 2)
        eigs = eigsh(csr_matrix(mat), k=k_eig, which='LM',
                     return_eigenvectors=False)
        eigs = np.sort(eigs)[::-1]
    except Exception:
        eigs = np.linalg.eigvalsh(mat)[::-1][:50]

    lambda_1 = float(eigs[0])
    n_eig_above_12 = int((eigs > 12).sum())
    pos_eigs = eigs[eigs > 0]
    if len(pos_eigs) > 0:
        normed = pos_eigs / pos_eigs.sum()
        entropy = -np.sum(normed * np.log(normed + 1e-15))
        eff_rank = float(np.exp(entropy))
    else:
        eff_rank = 0

    # Hub/tail ratio and uniqueness
    hub_tail = 0.0
    uniqueness = 0.0
    if middles is not None and mid_folios is not None:
        n_folios = len(set(f for fset in mid_folios.values() for f in fset))
        hubs = sum(1 for m in middles if len(mid_folios.get(m, set())) >= n_folios * 0.5)
        tails = sum(1 for m in middles if len(mid_folios.get(m, set())) <= 2)
        hub_tail = hubs / tails if tails > 0 else float('inf')
        unique = sum(1 for m in middles if len(mid_folios.get(m, set())) == 1)
        uniqueness = unique / len(middles) if middles else 0

    # Silhouette at key k values (spectral embedding in residual space)
    sil_scores = {}
    gap_stat = None
    try:
        np.fill_diagonal(mat, 0)
        eig_vals, eig_vecs = np.linalg.eigh(mat)
        idx = np.argsort(eig_vals)[::-1]
        eig_vals = eig_vals[idx]
        eig_vecs = eig_vecs[:, idx]
        # Residual embedding (remove hub eigenmode)
        K_EMBED = min(99, N - 2)
        emb = eig_vecs[:, 1:K_EMBED + 1] * np.sqrt(np.abs(eig_vals[1:K_EMBED + 1]))
        for k in [2, 3, 5, 8, 10, 15, 20]:
            if k >= N:
                continue
            km = KMeans(n_clusters=k, n_init=10, random_state=42)
            labels = km.fit_predict(emb)
            if len(set(labels)) > 1:
                sil_scores[k] = float(silhouette_score(emb, labels))
        # Gap statistic (simplified: compare k=5 inertia vs uniform)
        if 5 in sil_scores:
            km5 = KMeans(n_clusters=5, n_init=10, random_state=42).fit(emb)
            real_inertia = km5.inertia_
            null_inertias = []
            for s in range(20):
                rng = np.random.RandomState(s)
                null_emb = rng.uniform(emb.min(axis=0), emb.max(axis=0), emb.shape)
                null_km = KMeans(n_clusters=5, n_init=5, random_state=s).fit(null_emb)
                null_inertias.append(null_km.inertia_)
            gap_stat = float(np.mean(np.log(null_inertias)) - np.log(real_inertia))
    except Exception as e:
        print(f"    [silhouette/gap computation failed: {e}]")

    return {
        'density': float(density),
        'clustering': float(clustering),
        'transitivity': float(transitivity),
        'lambda_1': float(lambda_1),
        'n_eig_above_12': int(n_eig_above_12),
        'effective_rank': float(eff_rank),
        'hub_tail_ratio': float(hub_tail),
        'uniqueness': float(uniqueness),
        'n_edges': int(n_edges),
        'silhouette': sil_scores,
        'gap_statistic': gap_stat,
    }


# ============================================================
# STEP 1: COMPATIBILITY RULE DISCOVERY
# ============================================================

def fit_compatibility_model(compat_matrix, middles):
    """Fit logistic regression predicting compatibility from atom features."""
    print("\n" + "=" * 70)
    print("STEP 1: COMPATIBILITY RULE DISCOVERY")
    print("=" * 70)

    N = len(middles)

    # Decompose all MIDDLEs into atoms
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

    # Build features for all pairs (subsample negatives for tractability)
    print(f"  Building pair features for {N} MIDDLEs...")
    pos_pairs = []
    neg_pairs = []
    for i in range(N):
        for j in range(i + 1, N):
            if compat_matrix[i, j] == 1:
                pos_pairs.append((i, j))
            else:
                neg_pairs.append((i, j))

    print(f"  Compatible pairs: {len(pos_pairs)}")
    print(f"  Incompatible pairs: {len(neg_pairs)}")

    # Subsample negatives to 5:1 ratio for tractable logistic regression
    rng = np.random.RandomState(42)
    n_neg_sample = min(len(neg_pairs), len(pos_pairs) * 5)
    neg_sample_idx = rng.choice(len(neg_pairs), n_neg_sample, replace=False)
    neg_sample = [neg_pairs[i] for i in neg_sample_idx]

    all_pairs = pos_pairs + neg_sample
    labels = np.array([1] * len(pos_pairs) + [0] * len(neg_sample))

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
        # Shared modifiers
        m1 = set(d1['mods'])
        m2 = set(d2['mods'])
        shared_mods = len(m1 & m2)
        return [shared, jaccard, same_head, same_term, same_cat,
                len_diff, shared_mods]

    X = np.array([pair_features(i, j) for i, j in all_pairs])
    feature_names = ['shared_atoms', 'atom_jaccard', 'same_head', 'same_term',
                     'same_category', 'len_diff', 'shared_mods']

    # Fit logistic regression
    lr = LogisticRegression(max_iter=1000, class_weight='balanced', random_state=42)
    lr.fit(X, labels)

    # Evaluate on full data (compute AUC on all pairs)
    print("  Computing AUC on full pair space...")
    # Use mini-batches for prediction on full pair space
    all_scores = np.zeros(N * (N - 1) // 2)
    all_true = np.zeros(N * (N - 1) // 2, dtype=int)
    idx = 0
    batch_size = 50000
    batch_X = []
    batch_indices = []
    for i in range(N):
        for j in range(i + 1, N):
            batch_X.append(pair_features(i, j))
            all_true[idx] = compat_matrix[i, j]
            batch_indices.append(idx)
            idx += 1
            if len(batch_X) >= batch_size:
                bX = np.array(batch_X)
                scores = lr.predict_proba(bX)[:, 1]
                for bi, si in zip(batch_indices, scores):
                    all_scores[bi] = si
                batch_X = []
                batch_indices = []
    if batch_X:
        bX = np.array(batch_X)
        scores = lr.predict_proba(bX)[:, 1]
        for bi, si in zip(batch_indices, scores):
            all_scores[bi] = si

    auc = roc_auc_score(all_true, all_scores)

    print(f"\n  Logistic Regression Results:")
    print(f"    AUC: {auc:.4f}")
    print(f"    Coefficients:")
    for name, coef in zip(feature_names, lr.coef_[0]):
        print(f"      {name:20s}: {coef:+.4f}")
    print(f"    Intercept: {lr.intercept_[0]:+.4f}")

    return lr, feature_names, decomps, auc


# ============================================================
# STEP 2: GENERATORS
# ============================================================

def generate_middle_atoms(head, n_mods, mod_weights, term_freq, rng,
                          use_avoidance=True, use_selectivity=True,
                          use_term_gating=True, use_forbidden_pairs=True):
    """Generate a single synthetic MIDDLE from atom slots."""
    # Choose modifiers
    mods = []
    if n_mods > 0:
        available = list(MODIFIERS)
        if use_selectivity and mod_weights:
            weights = np.array([mod_weights.get(m, 0.1) for m in available])
        else:
            weights = np.ones(len(available))
        weights = weights / weights.sum()

        for _ in range(n_mods):
            if not available:
                break
            w = np.array([weights[list(MODIFIERS).index(m)] if m in available
                          else 0 for m in list(MODIFIERS)])
            w_avail = []
            avail_mods = []
            for m in available:
                idx_m = list(MODIFIERS).index(m)
                w_avail.append(weights[idx_m])
                avail_mods.append(m)
            if not avail_mods:
                break
            w_avail = np.array(w_avail)
            w_avail = w_avail / w_avail.sum()
            chosen = rng.choice(avail_mods, p=w_avail)
            mods.append(chosen)
            # Remove chosen and forbidden partners
            available.remove(chosen)
            if use_avoidance:
                to_remove = []
                for m in available:
                    if frozenset({chosen, m}) in FORBIDDEN_MOD_PAIRS:
                        to_remove.append(m)
                for m in to_remove:
                    available.remove(m)

    # Choose terminal
    term_options = list(TERM_FREQS.keys())
    term_weights = np.array([TERM_FREQS[t] for t in term_options])

    if use_term_gating and mods:
        # Filter terminals by modifier exclusivity
        valid_terms = []
        valid_weights = []
        for t, tw in zip(term_options, term_weights):
            if t == 'bare':
                valid_terms.append(t)
                valid_weights.append(tw)
            elif t in TERM_MOD_ALLOWED:
                # Check if any of our mods are allowed with this terminal
                if any(m in TERM_MOD_ALLOWED[t] for m in mods):
                    valid_terms.append(t)
                    valid_weights.append(tw)
                elif not TERM_MOD_ALLOWED[t].intersection(MODIFIERS):
                    valid_terms.append(t)
                    valid_weights.append(tw)
            else:
                valid_terms.append(t)
                valid_weights.append(tw)
        term_options = valid_terms
        term_weights = np.array(valid_weights)

    if use_forbidden_pairs and head:
        # Filter by slot syntax forbidden INITIAL-TERMINAL pairs
        init_char = head if head else (mods[0] if mods else None)
        if init_char:
            valid = []
            vw = []
            for t, tw in zip(term_options, term_weights):
                if t == 'bare':
                    valid.append(t)
                    vw.append(tw)
                elif (init_char, t) not in FORBIDDEN_INIT_TERM:
                    valid.append(t)
                    vw.append(tw)
            term_options = valid
            term_weights = np.array(vw)

    if len(term_options) == 0:
        term = 'bare'
    else:
        term_weights = term_weights / term_weights.sum()
        term = rng.choice(term_options, p=term_weights)

    # Assemble MIDDLE string
    s = ''
    if head:
        s += head
    s += ''.join(mods)
    if term != 'bare':
        s += term
    return s if s else 'e'  # fallback to simplest MIDDLE


def generate_empirical(N=972, seed=42):
    """2a: EMPIRICAL atom model (real frequencies + selectivity)."""
    rng = np.random.RandomState(seed)
    middles = set()
    attempts = 0
    while len(middles) < N and attempts < N * 20:
        attempts += 1
        # HEAD selection (C1475)
        heads = list(HEAD_FREQS.keys())
        hweights = np.array([HEAD_FREQS[h] for h in heads])
        head = rng.choice(heads, p=hweights / hweights.sum())
        if head is None:
            head_char = None
        else:
            head_char = head

        # Number of modifiers (0-3, geometric-ish distribution)
        mod_rate = HEAD_MOD_RATE.get(head_char, 0.3)
        n_mods = 0
        while rng.random() < mod_rate and n_mods < 3:
            n_mods += 1
            mod_rate *= 0.4  # decreasing probability of additional mods

        mod_weights = HEAD_MOD_WEIGHTS.get(head_char, {})
        mid = generate_middle_atoms(head_char, n_mods, mod_weights,
                                    TERM_FREQS, rng)
        middles.add(mid)

    return sorted(middles)[:N]


def generate_structured_random(N=972, seed=42):
    """2b: STRUCTURED-RANDOM (same architecture, uniform probabilities)."""
    rng = np.random.RandomState(seed)
    middles = set()
    attempts = 0
    heads = list(HEAD_FREQS.keys())
    uniform_head = np.ones(len(heads)) / len(heads)
    uniform_mod = {m: 1.0 / len(MODIFIERS) for m in MODIFIERS}

    while len(middles) < N and attempts < N * 20:
        attempts += 1
        head = rng.choice(heads, p=uniform_head)
        if head is None:
            head_char = None
        else:
            head_char = head

        n_mods = 0
        while rng.random() < 0.35 and n_mods < 3:
            n_mods += 1

        mid = generate_middle_atoms(head_char, n_mods, uniform_mod,
                                    TERM_FREQS, rng,
                                    use_avoidance=False, use_selectivity=False,
                                    use_term_gating=False, use_forbidden_pairs=False)
        middles.add(mid)

    return sorted(middles)[:N]


def generate_param_matched_independent(N=972, seed=42):
    """2c: Real marginal frequencies, no cross-slot dependencies."""
    rng = np.random.RandomState(seed)
    middles = set()
    attempts = 0

    # Use real HEAD frequencies but independent modifier/terminal selection
    all_mod_weights = Counter()
    for h, mw in HEAD_MOD_WEIGHTS.items():
        for m, w in mw.items():
            all_mod_weights[m] += w * HEAD_FREQS.get(h, 0.1)
    total = sum(all_mod_weights.values())
    marginal_mod = {m: all_mod_weights[m] / total for m in MODIFIERS}

    while len(middles) < N and attempts < N * 20:
        attempts += 1
        heads = list(HEAD_FREQS.keys())
        hweights = np.array([HEAD_FREQS[h] for h in heads])
        head = rng.choice(heads, p=hweights / hweights.sum())
        if head is None:
            head_char = None
        else:
            head_char = head

        mod_rate = 0.38  # average modifier rate
        n_mods = 0
        while rng.random() < mod_rate and n_mods < 3:
            n_mods += 1
            mod_rate *= 0.4

        # Use marginal weights, NO avoidance, NO selectivity, NO gating
        mid = generate_middle_atoms(head_char, n_mods, marginal_mod,
                                    TERM_FREQS, rng,
                                    use_avoidance=False, use_selectivity=False,
                                    use_term_gating=False, use_forbidden_pairs=False)
        middles.add(mid)

    return sorted(middles)[:N]


def generate_naive_property(N=972, seed=42):
    """2d: F-BRU-003 reproduction (random property bins)."""
    rng = np.random.RandomState(seed)
    n_props = 8
    all_mids = [f"m{i:04d}" for i in range(N)]
    props = {}
    for p in range(n_props):
        n_m = rng.randint(50, 100)
        props[p] = set(rng.choice(all_mids, n_m, replace=False))
    # Cross-cutting overlap
    for p in range(n_props - 1):
        shared = set(rng.choice(all_mids, 20, replace=False))
        props[p].update(shared)
        props[p + 1].update(shared)
    return all_mids


def build_compatibility_from_model(middles, lr_model, feature_names, target_density):
    """Apply logistic model to synthetic MIDDLEs to build compatibility graph."""
    N = len(middles)

    # Decompose all synthetic MIDDLEs
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

    def pair_features(m1, m2):
        d1, d2 = decomps[m1], decomps[m2]
        a1, a2 = d1['atoms'], d2['atoms']
        shared = len(a1 & a2)
        union = len(a1 | a2)
        jaccard = shared / union if union > 0 else 0
        same_head = 1 if d1['head'] == d2['head'] and d1['head'] is not None else 0
        same_term = 1 if d1['term'] == d2['term'] and d1['term'] != 'bare' else 0
        same_cat = 1 if d1['category'] == d2['category'] else 0
        len_diff = abs(d1['length'] - d2['length'])
        m1s, m2s = set(d1['mods']), set(d2['mods'])
        shared_mods = len(m1s & m2s)
        return [shared, jaccard, same_head, same_term, same_cat,
                len_diff, shared_mods]

    # Compute all pair scores
    scores = np.zeros((N, N))
    batch_X = []
    batch_idx = []
    for i in range(N):
        for j in range(i + 1, N):
            batch_X.append(pair_features(middles[i], middles[j]))
            batch_idx.append((i, j))
            if len(batch_X) >= 50000:
                bX = np.array(batch_X)
                probs = lr_model.predict_proba(bX)[:, 1]
                for (a, b), p in zip(batch_idx, probs):
                    scores[a, b] = p
                    scores[b, a] = p
                batch_X = []
                batch_idx = []
    if batch_X:
        bX = np.array(batch_X)
        probs = lr_model.predict_proba(bX)[:, 1]
        for (a, b), p in zip(batch_idx, probs):
            scores[a, b] = p
            scores[b, a] = p

    # Threshold to match target density
    upper = scores[np.triu_indices(N, k=1)]
    target_n = int(target_density * N * (N - 1) / 2)
    if target_n >= len(upper):
        threshold = 0
    else:
        threshold = np.sort(upper)[::-1][target_n]

    compat = (scores > threshold).astype(np.int8)
    np.fill_diagonal(compat, 0)
    return compat


def build_random_compatibility(N, target_density, seed=42):
    """Density-matched random compatibility graph (for naive model)."""
    rng = np.random.RandomState(seed)
    compat = np.zeros((N, N), dtype=np.int8)
    for i in range(N):
        for j in range(i + 1, N):
            if rng.random() < target_density:
                compat[i, j] = 1
                compat[j, i] = 1
    return compat


def build_independent_features(N, K, target_density, seed=42):
    """2e: Independent binary feature model (T9 reproduction)."""
    rng = np.random.RandomState(seed)
    from scipy.stats import binom

    # Find p and T for target density
    best = None
    best_diff = float('inf')
    for p_int in range(10, 95, 2):
        p = p_int / 100.0
        p_shared = p * p
        for T in range(0, K + 1):
            d = 1 - binom.cdf(T - 1, K, p_shared)
            diff = abs(d - target_density)
            if diff < best_diff:
                best_diff = diff
                best = (p, T, d)
            if d < target_density * 0.1:
                break

    p, T, _ = best
    features = (rng.random((N, K)) < p).astype(np.int32)
    shared = features @ features.T
    compat = (shared >= T).astype(np.int8)
    np.fill_diagonal(compat, 0)
    return compat


# ============================================================
# ABLATION GENERATOR
# ============================================================

def generate_ablated(N, seed, ablation='none'):
    """Generate with one architectural layer removed."""
    rng = np.random.RandomState(seed)
    middles = set()
    attempts = 0

    while len(middles) < N and attempts < N * 20:
        attempts += 1
        # HEAD selection
        if ablation == 'no_head_structure':
            heads = list(HEAD_FREQS.keys())
            head = rng.choice(heads)
        else:
            heads = list(HEAD_FREQS.keys())
            hweights = np.array([HEAD_FREQS[h] for h in heads])
            head = rng.choice(heads, p=hweights / hweights.sum())

        head_char = head if head is not None else None

        mod_rate = HEAD_MOD_RATE.get(head_char, 0.3)
        n_mods = 0
        while rng.random() < mod_rate and n_mods < 3:
            n_mods += 1
            mod_rate *= 0.4

        use_avoid = ablation != 'no_mod_avoidance'
        use_select = ablation != 'no_head_mod_selectivity'
        use_gate = ablation != 'no_terminal_gating'
        use_forbid = ablation != 'no_slot_syntax'

        mod_weights = HEAD_MOD_WEIGHTS.get(head_char, {}) if use_select else \
            {m: 1.0 / len(MODIFIERS) for m in MODIFIERS}

        mid = generate_middle_atoms(head_char, n_mods, mod_weights,
                                    TERM_FREQS, rng,
                                    use_avoidance=use_avoid,
                                    use_selectivity=use_select,
                                    use_term_gating=use_gate,
                                    use_forbidden_pairs=use_forbid)
        middles.add(mid)

    return sorted(middles)[:N]


# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 70)
    print("PHASE 585: ATOM COMPOSITIONAL GENERATOR")
    print("F-BRU-003 Retest with Atom Architecture")
    print("=" * 70)

    results = {'phase': 585, 'test': 'ATOM_COMPOSITIONAL_GENERATOR'}

    # ----------------------------------------------------------
    # STEP 0: Real baseline
    # ----------------------------------------------------------
    real_compat, real_middles, mid_to_idx, mid_folios, real_metrics = build_real_baseline()
    results['real'] = real_metrics
    target_density = real_metrics['density']
    N = real_metrics['N']

    # ----------------------------------------------------------
    # STEP 1: Compatibility rule
    # ----------------------------------------------------------
    lr_model, feat_names, real_decomps, lr_auc = fit_compatibility_model(
        real_compat, real_middles)
    results['compatibility_model'] = {
        'auc': lr_auc,
        'coefficients': {n: float(c) for n, c in zip(feat_names, lr_model.coef_[0])},
        'intercept': float(lr_model.intercept_[0]),
    }

    # ----------------------------------------------------------
    # STEP 2-3: Generators (10 seeds each)
    # ----------------------------------------------------------
    N_SEEDS = 10
    models = {}

    print("\n" + "=" * 70)
    print("STEP 2-3: GENERATORS (10 seeds each)")
    print("=" * 70)

    for model_name, gen_fn in [
        ('empirical', lambda s: generate_empirical(N, s)),
        ('structured_random', lambda s: generate_structured_random(N, s)),
        ('param_independent', lambda s: generate_param_matched_independent(N, s)),
    ]:
        print(f"\n  --- {model_name} ---")
        seed_metrics = []
        for seed in range(42, 42 + N_SEEDS):
            syn_middles = gen_fn(seed)
            syn_compat = build_compatibility_from_model(
                syn_middles, lr_model, feat_names, target_density)
            m = compute_graph_metrics(syn_compat)
            seed_metrics.append(m)
            if seed == 42:
                print(f"    seed=42: clustering={m['clustering']:.4f}, "
                      f"transitivity={m['transitivity']:.4f}, "
                      f"density={m['density']:.4f}")

        # Average across seeds
        avg = {}
        for key in seed_metrics[0]:
            if isinstance(seed_metrics[0][key], (int, float)):
                vals = [sm[key] for sm in seed_metrics]
                avg[key] = float(np.mean(vals))
                avg[f'{key}_std'] = float(np.std(vals))
        avg['silhouette'] = seed_metrics[0].get('silhouette', {})
        avg['gap_statistic'] = seed_metrics[0].get('gap_statistic')
        models[model_name] = avg
        print(f"    mean clustering: {avg['clustering']:.4f} +/- {avg.get('clustering_std', 0):.4f}")

    # Naive property model
    print(f"\n  --- naive_property ---")
    naive_metrics = []
    for seed in range(42, 42 + N_SEEDS):
        syn_middles = generate_naive_property(N, seed)
        syn_compat = build_random_compatibility(N, target_density, seed)
        m = compute_graph_metrics(syn_compat)
        naive_metrics.append(m)
    avg = {}
    for key in naive_metrics[0]:
        if isinstance(naive_metrics[0][key], (int, float)):
            vals = [sm[key] for sm in naive_metrics]
            avg[key] = float(np.mean(vals))
            avg[f'{key}_std'] = float(np.std(vals))
    models['naive_property'] = avg
    print(f"    mean clustering: {avg['clustering']:.4f} +/- {avg.get('clustering_std', 0):.4f}")

    # Independent binary features
    print(f"\n  --- independent_features ---")
    for K in [60, 100, 200]:
        feat_metrics = []
        for seed in range(42, 42 + N_SEEDS):
            syn_compat = build_independent_features(N, K, target_density, seed)
            m = compute_graph_metrics(syn_compat)
            feat_metrics.append(m)
        avg = {}
        for key in feat_metrics[0]:
            if isinstance(feat_metrics[0][key], (int, float)):
                vals = [sm[key] for sm in feat_metrics]
                avg[key] = float(np.mean(vals))
                avg[f'{key}_std'] = float(np.std(vals))
        models[f'indep_K{K}'] = avg
        print(f"    K={K}: mean clustering: {avg['clustering']:.4f} +/- {avg.get('clustering_std', 0):.4f}")

    results['models'] = models

    # ----------------------------------------------------------
    # STEP 4: Comparison table
    # ----------------------------------------------------------
    print("\n" + "=" * 70)
    print("STEP 4: COMPARISON TABLE")
    print("=" * 70)

    header = f"{'Metric':<20} {'Real':>10} {'Empirical':>10} {'Str-Rand':>10} {'Par-Ind':>10} {'Naive':>10} {'IF-K60':>10} {'IF-K200':>10}"
    print(f"\n  {header}")
    print(f"  {'-' * len(header)}")

    for metric in ['density', 'clustering', 'transitivity', 'lambda_1',
                    'n_eig_above_12', 'effective_rank']:
        rv = real_metrics.get(metric, 0)
        vals = [rv]
        for mname in ['empirical', 'structured_random', 'param_independent',
                       'naive_property', 'indep_K60', 'indep_K200']:
            vals.append(models.get(mname, {}).get(metric, 0))
        if metric == 'n_eig_above_12':
            fmt = f"  {metric:<20} " + " ".join(f"{v:>10.0f}" for v in vals)
        else:
            fmt = f"  {metric:<20} " + " ".join(f"{v:>10.4f}" for v in vals)
        print(fmt)

    # ----------------------------------------------------------
    # STEP 5: Ablation
    # ----------------------------------------------------------
    print("\n" + "=" * 70)
    print("STEP 5: ABLATION (Empirical model, remove one layer)")
    print("=" * 70)

    ablations = [
        ('full', 'none'),
        ('no_mod_avoidance', 'no_mod_avoidance'),
        ('no_head_mod_select', 'no_head_mod_selectivity'),
        ('no_terminal_gating', 'no_terminal_gating'),
        ('no_slot_syntax', 'no_slot_syntax'),
        ('no_head_structure', 'no_head_structure'),
    ]

    ablation_results = {}
    for label, ablation in ablations:
        abl_metrics = []
        for seed in range(42, 42 + 5):  # 5 seeds for ablation
            syn_middles = generate_ablated(N, seed, ablation)
            syn_compat = build_compatibility_from_model(
                syn_middles, lr_model, feat_names, target_density)
            m = compute_graph_metrics(syn_compat)
            abl_metrics.append(m)
        avg_cl = np.mean([m['clustering'] for m in abl_metrics])
        avg_tr = np.mean([m['transitivity'] for m in abl_metrics])
        ablation_results[label] = {
            'clustering': float(avg_cl),
            'transitivity': float(avg_tr),
        }
        print(f"  {label:25s}: clustering={avg_cl:.4f}, transitivity={avg_tr:.4f}")

    results['ablation'] = ablation_results

    # ----------------------------------------------------------
    # STEP 6: Scale sensitivity
    # ----------------------------------------------------------
    print("\n" + "=" * 70)
    print("STEP 6: SCALE SENSITIVITY (Empirical model)")
    print("=" * 70)

    scale_results = {}
    for n_test in [500, N, 1500]:
        syn_middles = generate_empirical(n_test, seed=42)
        syn_compat = build_compatibility_from_model(
            syn_middles, lr_model, feat_names, target_density)
        m = compute_graph_metrics(syn_compat)
        scale_results[n_test] = {'clustering': m['clustering'],
                                  'transitivity': m['transitivity'],
                                  'density': m['density']}
        print(f"  N={n_test:5d}: clustering={m['clustering']:.4f}, "
              f"transitivity={m['transitivity']:.4f}, density={m['density']:.4f}")

    results['scale_sensitivity'] = {str(k): v for k, v in scale_results.items()}

    # ----------------------------------------------------------
    # VERDICTS
    # ----------------------------------------------------------
    print("\n" + "=" * 70)
    print("VERDICTS")
    print("=" * 70)

    emp_cl = models['empirical']['clustering']
    sr_cl = models['structured_random']['clustering']
    pi_cl = models['param_independent']['clustering']
    naive_cl = models['naive_property']['clustering']
    real_cl = real_metrics['clustering']
    if60_cl = models['indep_K60']['clustering']

    # Primary verdict
    if emp_cl > 0.70:
        primary = 'COMPOSITIONAL_PROPERTIES_VIABLE'
        print(f"\n  PRIMARY: {primary}")
        print(f"    Empirical clustering {emp_cl:.4f} > 0.70 threshold")
        print(f"    F-BRU-003 should be DOWNGRADED to F2-SUPERSEDED")
    elif emp_cl > 0.49:
        primary = 'PARTIAL_COMPOSITIONAL'
        print(f"\n  PRIMARY: {primary}")
        print(f"    Empirical clustering {emp_cl:.4f} breaks independent feature ceiling (0.49)")
        print(f"    but does not reach 0.70. F-BRU-003 NARROWED.")
    else:
        primary = 'PROPERTY_KILL_CONFIRMED'
        print(f"\n  PRIMARY: {primary}")
        print(f"    Empirical clustering {emp_cl:.4f} <= 0.49 ceiling")
        print(f"    F-BRU-003 STRENGTHENED — atom composition does not help.")

    # Secondary verdicts
    if sr_cl > emp_cl * 0.80:
        arch = 'ARCHITECTURE_SUFFICIENT'
        print(f"\n  SECONDARY: {arch}")
        print(f"    Structured-Random {sr_cl:.4f} >= 80% of Empirical {emp_cl:.4f}")
    else:
        arch = 'PARAMETERS_MATTER'
        print(f"\n  SECONDARY: {arch}")
        print(f"    Structured-Random {sr_cl:.4f} < 80% of Empirical {emp_cl:.4f}")

    if pi_cl < emp_cl - 0.10:
        deps = 'CROSS_SLOT_DEPENDENCIES_DRIVE'
        print(f"\n  SECONDARY: {deps}")
        print(f"    Param-Independent {pi_cl:.4f} << Empirical {emp_cl:.4f}")
    else:
        deps = 'DEPENDENCIES_MARGINAL'
        print(f"\n  SECONDARY: {deps}")

    # Compatibility model verdict
    if lr_auc > 0.80:
        compat_v = 'ATOM_COMPATIBILITY_PREDICTABLE'
        print(f"\n  COMPATIBILITY: {compat_v} (AUC={lr_auc:.4f})")
    elif lr_auc > 0.70:
        compat_v = 'ATOM_COMPATIBILITY_PARTIAL'
        print(f"\n  COMPATIBILITY: {compat_v} (AUC={lr_auc:.4f})")
    else:
        compat_v = 'ATOM_COMPATIBILITY_WEAK'
        print(f"\n  COMPATIBILITY: {compat_v} (AUC={lr_auc:.4f})")

    results['verdicts'] = {
        'primary': primary,
        'empirical_clustering': float(emp_cl),
        'structured_random_clustering': float(sr_cl),
        'param_independent_clustering': float(pi_cl),
        'naive_clustering': float(naive_cl),
        'architecture': arch,
        'dependencies': deps,
        'compatibility': compat_v,
        'lr_auc': float(lr_auc),
    }

    # Save
    out_path = RESULTS_DIR / 'atom_compositional_generator.json'
    with open(out_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\n  Results saved to {out_path}")


if __name__ == '__main__':
    main()
