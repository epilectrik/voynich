#!/usr/bin/env python3
"""
T9: Holdout Stability — Is the 6-state partition invariant across subsets?
MINIMAL_STATE_AUTOMATON phase

Randomly remove 5 folios, rebuild 49x49 transition matrix, re-run the
constraint-preserving merge, and compare the resulting partition to the
canonical one. Repeat 100 times. If the partition is stable, the 6-state
structure is a genuine property of the grammar, not a sampling artifact.
"""

import sys
import json
import time
import functools
import numpy as np
from pathlib import Path
from collections import defaultdict
from scipy.spatial.distance import jensenshannon
from sklearn.metrics import adjusted_rand_score

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from scripts.voynich import Transcript

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
RESULTS_DIR = Path(__file__).parent.parent / 'results'

N_HOLDOUT = 5
N_TRIALS = 100
RNG = np.random.default_rng(42)

# ============================================================
# CONSTRAINT DEFINITIONS (same as T3)
# ============================================================

DEPLETED_PAIRS = [
    (11, 36), (13, 40), (9, 33), (24, 30), (14, 46), (9, 27),
    (9, 32), (5, 34), (47, 11), (19, 33), (7, 32), (11, 14),
    (3, 33), (33, 38), (18, 28), (7, 47), (13, 5), (10, 28),
]

CC_CLASSES = {10, 11, 12}
FQ_CLASSES = {9, 13, 14, 23}
FL_HAZ = {7, 30}
FL_SAFE = {38, 40}


def get_role(c):
    if c in CC_CLASSES: return 'CC'
    if c in FQ_CLASSES: return 'FQ'
    if c in FL_HAZ: return 'FL_HAZ'
    if c in FL_SAFE: return 'FL_SAFE'
    en_set = ({8} | set(range(31, 50))) - {7, 30, 38, 40}
    if c in en_set: return 'EN'
    return 'AX'


def check_role_integrity(partition):
    for group in partition:
        roles = set(get_role(c) for c in group)
        if 'CC' in roles and len(roles) > 1: return False
        if 'FQ' in roles and len(roles) > 1: return False
        if 'FL_HAZ' in roles and 'FL_SAFE' in roles: return False
        if ('FL_HAZ' in roles or 'FL_SAFE' in roles):
            non_fl = roles - {'FL_HAZ', 'FL_SAFE'}
            if non_fl: return False
    return True


def check_depletion(partition, counts, all_classes):
    cls_to_idx = {c: i for i, c in enumerate(all_classes)}
    cls_to_part = {}
    for pi, group in enumerate(partition):
        for c in group:
            cls_to_part[c] = pi

    # Check depleted pairs don't merge into same state
    for src, tgt in DEPLETED_PAIRS:
        if src not in cls_to_part or tgt not in cls_to_part:
            continue
        if cls_to_part[src] == cls_to_part[tgt]:
            return False

    # Check asymmetry preservation
    n_p = len(partition)
    merged_counts = np.zeros((n_p, n_p), dtype=float)
    for i, gi in enumerate(partition):
        for j, gj in enumerate(partition):
            for ci in gi:
                for cj in gj:
                    merged_counts[i][j] += counts[cls_to_idx[ci]][cls_to_idx[cj]]

    row_sums = merged_counts.sum(axis=1)
    col_sums = merged_counts.sum(axis=0)
    total = merged_counts.sum()

    merged_depleted = set()
    for src, tgt in DEPLETED_PAIRS:
        if src in cls_to_part and tgt in cls_to_part:
            ps, pt = cls_to_part[src], cls_to_part[tgt]
            merged_depleted.add((ps, pt))

    for ps, pt in merged_depleted:
        rev_expected = row_sums[pt] * col_sums[ps] / total if total > 0 else 0
        if rev_expected >= 5:
            rev_ratio = merged_counts[pt][ps] / rev_expected
            if rev_ratio < 0.2:
                return False
    return True


def check_constraints(partition, counts, all_classes):
    return check_role_integrity(partition) and check_depletion(partition, counts, all_classes)


def run_merge(counts, probs, all_classes):
    """Run the constraint-preserving merge algorithm. Returns final partition."""
    n = len(all_classes)
    cls_to_idx = {c: i for i, c in enumerate(all_classes)}
    partition = [set([c]) for c in all_classes]

    max_rejects = 200
    consecutive_rejects = 0

    while len(partition) > 2 and consecutive_rejects < max_rejects:
        n_p = len(partition)

        # Compute aggregate profiles
        profiles = []
        for group in partition:
            total_out = 0
            profile = np.zeros(n)
            for c in group:
                idx = cls_to_idx[c]
                row_sum = probs[idx].sum()
                profile += probs[idx] * row_sum
                total_out += row_sum
            if total_out > 0:
                profile /= total_out
            else:
                profile = np.ones(n) / n
            profiles.append(profile)

        # Pairwise JSD
        candidates = []
        for i in range(n_p):
            for j in range(i + 1, n_p):
                jsd = jensenshannon(profiles[i], profiles[j])
                if np.isnan(jsd):
                    jsd = 1.0
                candidates.append((jsd, i, j))
        candidates.sort()

        merged = False
        for dist, i, j in candidates:
            new_group = partition[i] | partition[j]
            new_partition = [p for k, p in enumerate(partition) if k != i and k != j]
            new_partition.append(new_group)

            if check_constraints(new_partition, counts, all_classes):
                partition = new_partition
                consecutive_rejects = 0
                merged = True
                break
            else:
                consecutive_rejects += 1

        if not merged:
            break

    return [sorted(g) for g in partition]


def partition_to_labels(partition, all_classes):
    """Convert partition to per-class label vector for ARI computation."""
    labels = {}
    for si, group in enumerate(partition):
        for c in group:
            labels[c] = si
    return [labels.get(c, -1) for c in all_classes]


def partition_signature(partition):
    """Create a size-sorted signature for quick equality check."""
    sizes = tuple(sorted(len(g) for g in partition))
    return sizes


def run():
    t_start = time.time()
    print("=" * 70)
    print("T9: Holdout Stability Test")
    print("MINIMAL_STATE_AUTOMATON phase")
    print("=" * 70)

    # Load canonical partition
    print("\n[1/4] Loading canonical partition...")
    with open(RESULTS_DIR / 't3_merged_automaton.json') as f:
        t3 = json.load(f)
    canonical_partition = t3['final_partition']
    canonical_n = t3['n_final_states']
    print(f"  Canonical: {canonical_n} states")
    canonical_sig = partition_signature(canonical_partition)
    print(f"  Signature (state sizes): {canonical_sig}")

    # Load class-token map
    with open(PROJECT_ROOT / 'phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json') as f:
        ctm = json.load(f)
    token_to_class = {t: int(c) for t, c in ctm['token_to_class'].items()}

    # Build per-folio transition sequences
    print("\n[2/4] Building per-folio data...")
    tx = Transcript()
    folio_transitions = defaultdict(list)  # folio -> list of (cls_from, cls_to)
    all_classes = list(range(1, 50))
    cls_to_idx = {c: i for i, c in enumerate(all_classes)}
    n_cls = len(all_classes)

    current_key = None
    current_seq = []
    current_folio = None

    for token in tx.currier_b():
        w = token.word.strip()
        if not w or '*' in w:
            continue
        cls = token_to_class.get(w)
        if cls is None:
            continue
        key = (token.folio, token.line)
        if key != current_key:
            if current_seq and current_folio:
                for i in range(len(current_seq) - 1):
                    folio_transitions[current_folio].append((current_seq[i], current_seq[i+1]))
            current_seq = []
            current_key = key
            current_folio = token.folio
        current_seq.append(cls)

    if current_seq and current_folio:
        for i in range(len(current_seq) - 1):
            folio_transitions[current_folio].append((current_seq[i], current_seq[i+1]))

    all_folios = sorted(folio_transitions.keys())
    print(f"  {len(all_folios)} folios with transition data")
    total_trans = sum(len(v) for v in folio_transitions.values())
    print(f"  {total_trans} total transitions")

    # Run holdout trials
    print(f"\n[3/4] Running {N_TRIALS} holdout trials (removing {N_HOLDOUT} folios each)...")
    t0 = time.time()

    results_trials = []
    state_count_dist = defaultdict(int)
    ari_scores = []
    exact_matches = 0
    sig_matches = 0

    for trial in range(N_TRIALS):
        # Select holdout folios
        holdout_idx = RNG.choice(len(all_folios), N_HOLDOUT, replace=False)
        holdout_folios = set(all_folios[i] for i in holdout_idx)
        kept_folios = [f for f in all_folios if f not in holdout_folios]

        # Build transition matrix from kept folios
        counts = np.zeros((n_cls, n_cls), dtype=float)
        for folio in kept_folios:
            for src, tgt in folio_transitions[folio]:
                counts[cls_to_idx[src]][cls_to_idx[tgt]] += 1

        row_sums = counts.sum(axis=1, keepdims=True)
        probs = np.divide(counts, row_sums, where=row_sums > 0,
                          out=np.zeros_like(counts))

        # Run merge
        partition = run_merge(counts, probs, all_classes)
        n_states = len(partition)
        state_count_dist[n_states] += 1

        # Compare to canonical
        canon_labels = partition_to_labels(canonical_partition, all_classes)
        trial_labels = partition_to_labels(partition, all_classes)
        ari = adjusted_rand_score(canon_labels, trial_labels)
        ari_scores.append(ari)

        sig = partition_signature(partition)
        if sig == canonical_sig:
            sig_matches += 1
        if ari > 0.999:
            exact_matches += 1

        results_trials.append({
            'trial': trial,
            'holdout_folios': sorted(holdout_folios),
            'n_states': n_states,
            'ari': round(float(ari), 5),
            'sig_match': sig == canonical_sig,
        })

        if (trial + 1) % 10 == 0:
            elapsed = time.time() - t0
            rate = (trial + 1) / elapsed
            print(f"    {trial+1}/{N_TRIALS} ({rate:.1f}/s)  "
                  f"mean_ARI={np.mean(ari_scores):.4f}  "
                  f"exact={exact_matches}/{trial+1}")

    dt = time.time() - t0
    print(f"  Completed {N_TRIALS} trials in {dt:.1f}s")

    # =========================================================
    # 4. Analysis
    # =========================================================
    print(f"\n[4/4] Analysis")
    print(f"\n  State count distribution:")
    for k in sorted(state_count_dist):
        pct = state_count_dist[k] / N_TRIALS * 100
        bar = '#' * int(pct / 2)
        print(f"    {k} states: {state_count_dist[k]:>3}/{N_TRIALS} ({pct:.0f}%) {bar}")

    ari_arr = np.array(ari_scores)
    print(f"\n  Adjusted Rand Index (vs canonical partition):")
    print(f"    Mean:   {ari_arr.mean():.4f}")
    print(f"    Median: {np.median(ari_arr):.4f}")
    print(f"    Min:    {ari_arr.min():.4f}")
    print(f"    Max:    {ari_arr.max():.4f}")
    print(f"    Std:    {ari_arr.std():.4f}")

    print(f"\n  Exact partition recovery (ARI > 0.999): "
          f"{exact_matches}/{N_TRIALS} ({exact_matches/N_TRIALS:.0%})")
    print(f"  Same-signature recovery: "
          f"{sig_matches}/{N_TRIALS} ({sig_matches/N_TRIALS:.0%})")

    # Check which trials deviated most
    worst_trials = sorted(results_trials, key=lambda x: x['ari'])[:5]
    if worst_trials[0]['ari'] < 0.999:
        print(f"\n  Lowest-ARI trials:")
        for wt in worst_trials:
            if wt['ari'] < 0.999:
                print(f"    Trial {wt['trial']}: ARI={wt['ari']:.4f}, "
                      f"{wt['n_states']} states, "
                      f"holdout={wt['holdout_folios']}")

    # Verdict
    print(f"\n{'='*70}")
    print(f"HOLDOUT STABILITY VERDICT")
    print(f"{'='*70}")

    if exact_matches >= N_TRIALS * 0.90:
        verdict = "HIGHLY_STABLE"
        print(f"\n  VERDICT: {verdict}")
        print(f"  The 6-state partition is recovered in {exact_matches/N_TRIALS:.0%} of holdout trials.")
        print(f"  This is a robust structural property, not a sampling artifact.")
    elif exact_matches >= N_TRIALS * 0.70:
        verdict = "STABLE"
        print(f"\n  VERDICT: {verdict}")
        print(f"  The 6-state partition is recovered in {exact_matches/N_TRIALS:.0%} of holdout trials.")
        print(f"  Minor instability in edge cases, but the partition is robust.")
    elif ari_arr.mean() >= 0.85:
        verdict = "MOSTLY_STABLE"
        print(f"\n  VERDICT: {verdict}")
        print(f"  Mean ARI={ari_arr.mean():.4f}. Partition is approximately stable.")
        print(f"  Some merges are sensitive to holdout composition.")
    else:
        verdict = "UNSTABLE"
        print(f"\n  VERDICT: {verdict}")
        print(f"  Mean ARI={ari_arr.mean():.4f}. Partition is sensitive to data subset.")

    # Save
    results = {
        'test': 'T9_holdout_stability',
        'n_trials': N_TRIALS,
        'n_holdout_folios': N_HOLDOUT,
        'canonical_n_states': canonical_n,
        'canonical_signature': list(canonical_sig),
        'state_count_distribution': {str(k): v for k, v in sorted(state_count_dist.items())},
        'ari_mean': round(float(ari_arr.mean()), 5),
        'ari_median': round(float(np.median(ari_arr)), 5),
        'ari_min': round(float(ari_arr.min()), 5),
        'ari_max': round(float(ari_arr.max()), 5),
        'ari_std': round(float(ari_arr.std()), 5),
        'exact_match_count': exact_matches,
        'exact_match_rate': round(exact_matches / N_TRIALS, 4),
        'sig_match_count': sig_matches,
        'sig_match_rate': round(sig_matches / N_TRIALS, 4),
        'verdict': verdict,
        'worst_trials': worst_trials[:5],
        'elapsed_seconds': round(time.time() - t_start, 1),
    }

    with open(RESULTS_DIR / 't9_holdout_stability.json', 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved to {RESULTS_DIR / 't9_holdout_stability.json'}")
    print(f"Total time: {time.time() - t_start:.1f}s")


if __name__ == '__main__':
    run()
