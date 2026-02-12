#!/usr/bin/env python3
"""
T1: Transition Structure Null Model (F2, F3, F4)
FINGERPRINT_UNIQUENESS phase

Tests: How rare is the Voynich class-to-class transition structure
among random sparse directed graphs on 49 nodes?

F2: Significantly depleted transitions (obs/exp < 0.2, expected >= 5)
    and their asymmetry (one-way depletion)
F3: Forbidden-pair clustering (concentrated in few source/target nodes)
F4: One-way kernel (depleted edge with enriched reverse, ratio > 3.0)

METHODOLOGY NOTE: C789 documents ~65% compliance for forbidden transitions,
meaning they occur at ~35% of expected rate. We use depletion ratio (obs/exp)
with a fixed threshold of 0.2, not zero-count. This identifies strongly
disfavored transitions without requiring absolute zeros.

Three null ensembles:
  NULL-A: Density-matched (per-row non-zero count preserved)
  NULL-B: Degree-matched (row totals exact, column totals approximate)
  NULL-C: Fully random (uniform Dirichlet per row)
"""

import sys
import json
import time
import numpy as np
from pathlib import Path
from collections import defaultdict, Counter

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from scripts.voynich import Transcript

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
RESULTS_DIR = Path(__file__).parent.parent / 'results'
N_SAMPLES = 10000
MIN_EXPECTED = 5.0
DEPLETION_THRESHOLD = 0.2   # obs/exp < this = "significantly depleted"
ENRICHMENT_THRESHOLD = 3.0  # reverse ratio > this = "strong one-way"
RNG = np.random.default_rng(42)


# ============================================================
# DATA LOADING
# ============================================================

def load_class_map():
    path = PROJECT_ROOT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
    with open(path) as f:
        ctm = json.load(f)
    token_to_class = {t: int(c) for t, c in ctm['token_to_class'].items()}
    class_to_role = {int(k): v for k, v in ctm['class_to_role'].items()}
    class_to_role[17] = 'CORE_CONTROL'  # C560/C581 correction
    all_classes = sorted(set(token_to_class.values()))
    return token_to_class, class_to_role, all_classes


def build_lines(token_to_class):
    """Build line-organized class sequences from Currier B."""
    tx = Transcript()
    lines = defaultdict(list)
    for token in tx.currier_b():
        w = token.word.strip()
        if not w or '*' in w:
            continue
        cls = token_to_class.get(w)
        if cls is not None:
            lines[(token.folio, token.line)].append(cls)
    return lines


def build_count_matrix(lines, all_classes):
    """Build NxN transition count matrix from consecutive class pairs within lines."""
    n = len(all_classes)
    cls_to_idx = {c: i for i, c in enumerate(all_classes)}
    counts = np.zeros((n, n), dtype=int)
    for seq in lines.values():
        for i in range(len(seq) - 1):
            a = cls_to_idx.get(seq[i])
            b = cls_to_idx.get(seq[i + 1])
            if a is not None and b is not None:
                counts[a][b] += 1
    return counts, cls_to_idx


# ============================================================
# FINGERPRINT METRICS (depletion-based)
# ============================================================

def compute_expected(counts):
    """Compute expected counts under independence."""
    row_totals = counts.sum(axis=1).astype(float)
    col_totals = counts.sum(axis=0).astype(float)
    grand = counts.sum()
    if grand == 0:
        return np.zeros_like(counts, dtype=float)
    return np.outer(row_totals, col_totals) / grand


def find_depleted(counts, expected, depl_thresh=DEPLETION_THRESHOLD, min_exp=MIN_EXPECTED):
    """Find significantly depleted transitions: obs/exp < threshold, expected >= min."""
    n = counts.shape[0]
    depleted = []
    for i in range(n):
        for j in range(n):
            if expected[i][j] >= min_exp:
                ratio = counts[i][j] / expected[i][j]
                if ratio < depl_thresh:
                    depleted.append((i, j, ratio))
    return depleted


def measure_asymmetry(depleted, counts, expected, depl_thresh=DEPLETION_THRESHOLD, min_exp=MIN_EXPECTED):
    """Among depleted pairs (i,j), fraction where reverse (j,i) is NOT depleted."""
    if not depleted:
        return 0.0
    depl_set = set((i, j) for i, j, _ in depleted)
    n_asym = 0
    for (i, j, _) in depleted:
        if expected[j][i] >= min_exp:
            rev_ratio = counts[j][i] / expected[j][i] if expected[j][i] > 0 else float('inf')
            if rev_ratio >= depl_thresh:  # Reverse is NOT depleted
                n_asym += 1
        # If reverse doesn't have enough expected, skip (don't count)
    measurable = sum(1 for (i, j, _) in depleted if expected[j][i] >= min_exp)
    if measurable == 0:
        return 0.0
    return n_asym / measurable


def measure_clustering(depleted, n):
    """How concentrated are depleted pairs among a few source/target nodes?"""
    if not depleted:
        return 0, 0, 0.0
    sources = set(i for i, j, _ in depleted)
    targets = set(j for i, j, _ in depleted)
    n_src, n_tgt = len(sources), len(targets)
    coeff = len(depleted) / (n_src * n_tgt) if (n_src * n_tgt) > 0 else 0.0
    return n_src, n_tgt, coeff


def check_one_way(depleted, counts, expected, enrich_thresh=ENRICHMENT_THRESHOLD, min_exp=MIN_EXPECTED):
    """Among depleted pairs (i,j), check if reverse (j,i) is enriched > threshold.
    This is the one-way kernel signature: blocked in one direction, amplified in reverse.
    """
    best = 0.0
    n_one_way = 0
    for (i, j, depl_ratio) in depleted:
        if expected[j][i] >= min_exp:
            rev_ratio = counts[j][i] / expected[j][i]
            if rev_ratio > enrich_thresh:
                n_one_way += 1
                if rev_ratio > best:
                    best = rev_ratio
    return n_one_way > 0, n_one_way, best


def compute_fingerprint(counts):
    """Compute full transition fingerprint (F2, F3, F4)."""
    n = counts.shape[0]
    expected = compute_expected(counts)
    depleted = find_depleted(counts, expected)
    asym = measure_asymmetry(depleted, counts, expected)
    n_src, n_tgt, clust = measure_clustering(depleted, n)
    has_oneway, n_oneway, best_enrich = check_one_way(depleted, counts, expected)

    return {
        'n_depleted': len(depleted),
        'asymmetry': asym,
        'n_sources': n_src,
        'n_targets': n_tgt,
        'clustering': clust,
        'has_one_way': has_oneway,
        'n_one_way': n_oneway,
        'best_enrichment': best_enrich,
    }


# ============================================================
# NULL ENSEMBLE GENERATORS
# ============================================================

def generate_null_a(row_totals, nonzero_per_row, n, rng):
    """NULL-A: Density-matched. Same per-row non-zero count, random columns."""
    counts = np.zeros((n, n), dtype=int)
    for i in range(n):
        if row_totals[i] == 0:
            continue
        k = max(1, min(nonzero_per_row[i], n))
        cols = rng.choice(n, size=k, replace=False)
        probs = rng.dirichlet(np.ones(k))
        rc = rng.multinomial(int(row_totals[i]), probs)
        for c_idx, j in enumerate(cols):
            counts[i][j] = rc[c_idx]
    return counts


def generate_null_b(row_totals, col_totals, n, rng):
    """NULL-B: Degree-matched. Row totals exact, column-proportional."""
    counts = np.zeros((n, n), dtype=int)
    total = col_totals.sum()
    if total == 0:
        return counts
    base_probs = col_totals / total
    base_probs = np.clip(base_probs, 1e-10, None)
    base_probs /= base_probs.sum()
    for i in range(n):
        if row_totals[i] == 0:
            continue
        counts[i] = rng.multinomial(int(row_totals[i]), base_probs)
    return counts


def generate_null_c(row_totals, n, rng):
    """NULL-C: Fully random. Uniform Dirichlet per row."""
    counts = np.zeros((n, n), dtype=int)
    for i in range(n):
        if row_totals[i] == 0:
            continue
        probs = rng.dirichlet(np.ones(n))
        counts[i] = rng.multinomial(int(row_totals[i]), probs)
    return counts


# ============================================================
# BOOTSTRAP HOLDOUT VALIDATION (Trap 2)
# ============================================================

def bootstrap_holdout(lines, all_classes, n_splits=20):
    """Validate depletion threshold stability across train/test splits."""
    folios = list(set(k[0] for k in lines.keys()))
    results = []

    for _ in range(n_splits):
        RNG.shuffle(folios)
        mid = len(folios) // 2
        train_f = set(folios[:mid])
        test_f = set(folios[mid:])

        train_lines = {k: v for k, v in lines.items() if k[0] in train_f}
        test_lines = {k: v for k, v in lines.items() if k[0] in test_f}

        train_counts, _ = build_count_matrix(train_lines, all_classes)
        test_counts, _ = build_count_matrix(test_lines, all_classes)

        train_exp = compute_expected(train_counts)
        test_exp = compute_expected(test_counts)

        # Use halved min_expected for half-sample
        train_depl = find_depleted(train_counts, train_exp, min_exp=MIN_EXPECTED / 2)
        test_depl = find_depleted(test_counts, test_exp, min_exp=MIN_EXPECTED / 2)

        train_set = set((i, j) for i, j, _ in train_depl)
        test_set = set((i, j) for i, j, _ in test_depl)
        union = train_set | test_set
        overlap = train_set & test_set
        jaccard = len(overlap) / len(union) if union else 0.0

        results.append({
            'train_n': len(train_depl),
            'test_n': len(test_depl),
            'overlap': len(overlap),
            'jaccard': round(jaccard, 4),
        })

    return results


# ============================================================
# MAIN
# ============================================================

def run():
    t_start = time.time()
    print("=" * 70)
    print("T1: Transition Structure Null Model (F2, F3, F4)")
    print("FINGERPRINT_UNIQUENESS phase")
    print(f"Depletion threshold: obs/exp < {DEPLETION_THRESHOLD}")
    print(f"Min expected: {MIN_EXPECTED}")
    print("=" * 70)

    # 1. Load data
    print("\n[1/6] Loading data...")
    token_to_class, class_to_role, all_classes = load_class_map()
    n = len(all_classes)
    idx_to_cls = {i: c for i, c in enumerate(all_classes)}
    print(f"  Classes: {n}, Tokens in map: {len(token_to_class)}")

    lines = build_lines(token_to_class)
    print(f"  Lines in B: {len(lines)}")

    counts, cls_to_idx = build_count_matrix(lines, all_classes)
    row_totals = counts.sum(axis=1)
    col_totals = counts.sum(axis=0)
    n_trans = int(counts.sum())
    print(f"  Total transitions: {n_trans}")

    # Per-row non-zero counts (for NULL-A)
    nonzero_per_row = [(counts[i] > 0).sum() for i in range(n)]

    # Count eligible pairs (expected >= 5)
    expected = compute_expected(counts)
    n_eligible = int((expected >= MIN_EXPECTED).sum())
    print(f"  Eligible pairs (expected >= {MIN_EXPECTED}): {n_eligible}/{n * n}")

    # 2. Observed fingerprint
    print("\n[2/6] Computing observed fingerprint...")
    obs = compute_fingerprint(counts)

    print(f"  F2 - Depleted pairs (obs/exp < {DEPLETION_THRESHOLD}): {obs['n_depleted']}")
    print(f"  F2 - Asymmetry: {obs['asymmetry']:.1%}")
    print(f"  F3 - Clustering: {obs['n_sources']} sources x {obs['n_targets']} targets "
          f"= {obs['clustering']:.3f}")
    print(f"  F4 - One-way pairs: {obs['n_one_way']} "
          f"(best enrichment: {obs['best_enrichment']:.2f}x)")

    # Detail the depleted pairs
    depleted = find_depleted(counts, expected)
    depleted_detail = []
    print(f"\n  Depleted pairs detail:")
    for (i, j, ratio) in sorted(depleted, key=lambda x: x[2]):
        sc, tc = idx_to_cls[i], idx_to_cls[j]
        sr = class_to_role.get(sc, '?')[:4]
        tr = class_to_role.get(tc, '?')[:4]
        # Check reverse
        rev_ratio = counts[j][i] / expected[j][i] if expected[j][i] >= MIN_EXPECTED else None
        rev_str = f"rev={rev_ratio:.2f}" if rev_ratio is not None else "rev=N/A"
        print(f"    ({sc:2d},{tc:2d}) {sr}->{tr}  ratio={ratio:.3f}  {rev_str}")
        depleted_detail.append({
            'src_class': sc, 'tgt_class': tc,
            'src_role': class_to_role.get(sc, '?'),
            'tgt_role': class_to_role.get(tc, '?'),
            'depletion_ratio': round(ratio, 4),
            'reverse_ratio': round(rev_ratio, 4) if rev_ratio is not None else None,
        })

    # Role-pair distribution
    role_pairs = Counter()
    for d in depleted_detail:
        role_pairs[(d['src_role'][:4], d['tgt_role'][:4])] += 1
    print(f"\n  By role pair:")
    for (sr, tr), cnt in role_pairs.most_common():
        print(f"    {sr} -> {tr}: {cnt}")

    # 3. Bootstrap holdout
    print("\n[3/6] Bootstrap holdout validation (20 splits)...")
    holdout = bootstrap_holdout(lines, all_classes)
    avg_j = np.mean([h['jaccard'] for h in holdout])
    avg_train = np.mean([h['train_n'] for h in holdout])
    avg_test = np.mean([h['test_n'] for h in holdout])
    print(f"  Avg train depleted: {avg_train:.1f}")
    print(f"  Avg test depleted: {avg_test:.1f}")
    print(f"  Avg Jaccard stability: {avg_j:.3f}")
    if avg_j >= 0.3:
        print("  OK: Depleted set is reasonably stable across splits")
    elif avg_j >= 0.15:
        print("  MARGINAL: Depleted set shows moderate instability")
    else:
        print("  WARNING: Low holdout stability — depleted set is sample-dependent")

    # 4-6. Null ensembles
    ensemble_results = {}
    generators = [
        ('NULL_A_density', lambda rng: generate_null_a(row_totals, nonzero_per_row, n, rng)),
        ('NULL_B_degree', lambda rng: generate_null_b(row_totals, col_totals, n, rng)),
        ('NULL_C_random', lambda rng: generate_null_c(row_totals, n, rng)),
    ]

    for step, (label, gen_fn) in enumerate(generators, 4):
        print(f"\n[{step}/6] Running {label} ({N_SAMPLES} samples)...")
        t_ens = time.time()

        null_depleted = np.zeros(N_SAMPLES, dtype=int)
        null_asymmetry = np.zeros(N_SAMPLES)
        null_clustering = np.zeros(N_SAMPLES)
        null_oneway = np.zeros(N_SAMPLES, dtype=bool)
        null_n_oneway = np.zeros(N_SAMPLES, dtype=int)

        for s in range(N_SAMPLES):
            nc = gen_fn(RNG)
            fp = compute_fingerprint(nc)
            null_depleted[s] = fp['n_depleted']
            null_asymmetry[s] = fp['asymmetry']
            null_clustering[s] = fp['clustering']
            null_oneway[s] = fp['has_one_way']
            null_n_oneway[s] = fp['n_one_way']

            if (s + 1) % 2500 == 0:
                elapsed = time.time() - t_ens
                rate = (s + 1) / elapsed
                eta = (N_SAMPLES - s - 1) / rate
                print(f"    {s + 1}/{N_SAMPLES} ({rate:.0f}/s, ETA {eta:.0f}s)")

        dt = time.time() - t_ens

        # P-values
        p_depl = float(np.mean(null_depleted >= obs['n_depleted']))

        # Conditional: given >= obs depleted, what's the asymmetry?
        mask_depl = null_depleted >= obs['n_depleted']
        if mask_depl.sum() > 0:
            p_asym = float(np.mean(null_asymmetry[mask_depl] >= obs['asymmetry']))
            p_clust = float(np.mean(null_clustering[mask_depl] >= obs['clustering']))
        else:
            p_asym = 0.0
            p_clust = 0.0

        p_oneway = float(np.mean(null_oneway))

        # Joint: depleted >= obs AND asymmetry >= obs AND one-way present
        joint_mask = mask_depl & (null_asymmetry >= obs['asymmetry']) & null_oneway
        p_joint = float(np.mean(joint_mask))

        ensemble_results[label] = {
            'p_depleted': p_depl,
            'p_asymmetry_given_depleted': p_asym,
            'p_clustering_given_depleted': p_clust,
            'p_one_way': p_oneway,
            'p_joint_F2_F3_F4': p_joint,
            'null_depleted_mean': round(float(np.mean(null_depleted)), 2),
            'null_depleted_std': round(float(np.std(null_depleted)), 2),
            'null_depleted_max': int(np.max(null_depleted)),
            'null_asymmetry_mean': round(float(np.mean(null_asymmetry)), 3),
            'null_oneway_fraction': round(float(np.mean(null_oneway)), 4),
            'n_with_depleted_ge_obs': int(mask_depl.sum()),
            'time_seconds': round(dt, 1),
        }

        print(f"  Completed in {dt:.1f}s")
        print(f"  P(depleted >= {obs['n_depleted']}): {p_depl:.4f} "
              f"[null mean={np.mean(null_depleted):.1f} +/- {np.std(null_depleted):.1f}]")
        print(f"  P(asymmetry >= {obs['asymmetry']:.1%} | depleted): {p_asym:.4f}")
        print(f"  P(clustering >= {obs['clustering']:.3f} | depleted): {p_clust:.4f}")
        print(f"  P(one-way): {p_oneway:.4f}")
        print(f"  P(joint F2 AND F3 AND F4): {p_joint:.6f}")

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    print(f"\nObserved fingerprint:")
    print(f"  Depleted pairs:   {obs['n_depleted']} (obs/exp < {DEPLETION_THRESHOLD})")
    print(f"  Asymmetry:        {obs['asymmetry']:.1%}")
    print(f"  Clustering:       {obs['clustering']:.3f} ({obs['n_sources']}x{obs['n_targets']})")
    print(f"  One-way pairs:    {obs['n_one_way']} (best {obs['best_enrichment']:.2f}x)")

    print(f"\nPer-ensemble joint p-values:")
    for label, res in ensemble_results.items():
        p = res['p_joint_F2_F3_F4']
        print(f"  {label}: {p:.6f}")

    best_p = min(r['p_joint_F2_F3_F4'] for r in ensemble_results.values())
    worst_p = max(r['p_joint_F2_F3_F4'] for r in ensemble_results.values())
    print(f"\nBest (most rare): {best_p:.6f}")
    print(f"Worst (least rare): {worst_p:.6f}")

    if worst_p < 0.01:
        verdict = "RARE"
    elif worst_p < 0.05:
        verdict = "UNCOMMON"
    else:
        verdict = "NOT_RARE"
    print(f"\nT1 Verdict (using worst-case p): {verdict}")

    # Save
    results = {
        'test': 'T1_transition_structure',
        'properties': ['F2_depleted_asymmetry', 'F3_clustering', 'F4_one_way_kernel'],
        'methodology': {
            'depletion_threshold': DEPLETION_THRESHOLD,
            'min_expected': MIN_EXPECTED,
            'enrichment_threshold': ENRICHMENT_THRESHOLD,
            'note': 'C789: forbidden transitions are ~65% compliant, not absolute zeros. '
                    'Depletion ratio (obs/exp) used instead of zero-count criterion.',
        },
        'observed': {
            'n_depleted': obs['n_depleted'],
            'asymmetry': obs['asymmetry'],
            'clustering_coefficient': obs['clustering'],
            'clustering_sources': obs['n_sources'],
            'clustering_targets': obs['n_targets'],
            'has_one_way': obs['has_one_way'],
            'n_one_way': obs['n_one_way'],
            'best_enrichment': obs['best_enrichment'],
            'depleted_pairs': depleted_detail,
        },
        'holdout_validation': {
            'n_splits': len(holdout),
            'avg_jaccard': round(float(avg_j), 4),
            'avg_train_depleted': round(float(avg_train), 1),
            'avg_test_depleted': round(float(avg_test), 1),
            'splits': holdout,
        },
        'ensembles': ensemble_results,
        'verdict': verdict,
        'best_joint_p': best_p,
        'worst_joint_p': worst_p,
        'n_samples_per_ensemble': N_SAMPLES,
        'n_classes': n,
        'n_transitions': n_trans,
        'n_eligible_pairs': n_eligible,
        'elapsed_seconds': round(time.time() - t_start, 1),
    }

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = RESULTS_DIR / 't1_transition.json'
    with open(out_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {out_path}")
    print(f"Total time: {time.time() - t_start:.1f}s")

    return results


if __name__ == '__main__':
    run()
