#!/usr/bin/env python3
"""
T12: B-Side Embedding Concordance
DISCRIMINATION_SPACE_DERIVATION phase (Tier 2)

Test whether Currier B's execution respects the discrimination space
geometry derived from Currier A.

Key questions:
1. Do B-line MIDDLE co-occurrences respect A's compatibility boundaries?
2. Are B co-occurring pairs closer in A's embedding than non-co-occurring?
3. Does B structure (section, REGIME) appear in the RESIDUAL space?

Per expert warning: test in BOTH full and residual (hub-removed) space
to separate frequency effects from genuine structural concordance.
"""

import sys
import json
import functools
import numpy as np
from pathlib import Path
from collections import defaultdict, Counter

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scripts.voynich import Transcript, Morphology

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)

RESULTS_DIR = Path(__file__).parent.parent / 'results'
K_EMBED = 100


def reconstruct_middle_list():
    """Reconstruct the MIDDLE ordering from T1."""
    tx = Transcript()
    morph = Morphology()
    all_middles_set = set()
    for token in tx.currier_a():
        word = token.word.strip()
        if not word or '*' in word:
            continue
        m = morph.extract(word)
        if m.middle:
            all_middles_set.add(m.middle)
    all_middles = sorted(all_middles_set)
    mid_to_idx = {m: i for i, m in enumerate(all_middles)}
    return all_middles, mid_to_idx


def build_embeddings(compat_matrix):
    """Build full and residual embeddings."""
    eigenvalues, eigenvectors = np.linalg.eigh(compat_matrix.astype(np.float64))
    idx = np.argsort(eigenvalues)[::-1]
    eigenvalues = eigenvalues[idx]
    eigenvectors = eigenvectors[:, idx]

    # Full embedding (eigenvectors 1-100)
    full_evals = eigenvalues[:K_EMBED]
    full_evecs = eigenvectors[:, :K_EMBED]
    full_scaling = np.sqrt(np.maximum(full_evals, 0))
    full_emb = full_evecs * full_scaling[np.newaxis, :]

    # Residual embedding (eigenvectors 2-100, skip hub)
    res_evals = eigenvalues[1:K_EMBED]
    res_evecs = eigenvectors[:, 1:K_EMBED]
    res_scaling = np.sqrt(np.maximum(res_evals, 0))
    res_emb = res_evecs * res_scaling[np.newaxis, :]

    return full_emb, res_emb, eigenvalues


def build_b_cooccurrence(mid_to_idx):
    """Build MIDDLE co-occurrence from Currier B lines."""
    tx = Transcript()
    morph = Morphology()

    line_middles = defaultdict(set)
    line_meta = {}  # (folio, line) -> {section, ...}
    all_b_middles = set()

    for token in tx.currier_b():
        word = token.word.strip()
        if not word or '*' in word:
            continue
        m = morph.extract(word)
        if m.middle:
            key = (token.folio, token.line)
            line_middles[key].add(m.middle)
            all_b_middles.add(m.middle)
            if key not in line_meta:
                line_meta[key] = {
                    'folio': token.folio,
                    'section': getattr(token, 'section', None),
                }

    # Build co-occurrence pairs
    cooccur_pairs = set()
    for key, middles in line_middles.items():
        mid_list = sorted(middles)
        for i in range(len(mid_list)):
            for j in range(i + 1, len(mid_list)):
                cooccur_pairs.add((mid_list[i], mid_list[j]))

    return line_middles, cooccur_pairs, all_b_middles, line_meta


def build_b_section_middles(mid_to_idx):
    """Build per-section MIDDLE inventories from B."""
    tx = Transcript()
    morph = Morphology()

    section_middles = defaultdict(set)
    for token in tx.currier_b():
        word = token.word.strip()
        if not word or '*' in word:
            continue
        m = morph.extract(word)
        sec = getattr(token, 'section', None)
        if m.middle and sec and m.middle in mid_to_idx:
            section_middles[sec].add(m.middle)

    return dict(section_middles)


def run():
    print("=" * 70)
    print("T12: B-Side Embedding Concordance")
    print("DISCRIMINATION_SPACE_DERIVATION phase (Tier 2)")
    print("=" * 70)

    # Load A-space
    print("\n[1/6] Loading A-space discrimination geometry...")
    all_middles, mid_to_idx = reconstruct_middle_list()
    M = np.load(RESULTS_DIR / 't1_compat_matrix.npy')
    n = len(all_middles)

    full_emb, res_emb, eigenvalues = build_embeddings(M)
    print(f"  A-space: {n} MIDDLEs, full embedding {full_emb.shape}, residual {res_emb.shape}")

    # Build B co-occurrence
    print("\n[2/6] Building B-line MIDDLE co-occurrence...")
    b_line_middles, b_cooccur_pairs, all_b_middles, b_line_meta = build_b_cooccurrence(mid_to_idx)

    # Filter to MIDDLEs in A-space
    b_in_a = all_b_middles & set(all_middles)
    b_not_in_a = all_b_middles - set(all_middles)

    b_pairs_in_a = [(m1, m2) for m1, m2 in b_cooccur_pairs
                    if m1 in mid_to_idx and m2 in mid_to_idx]

    print(f"  B lines: {len(b_line_middles)}")
    print(f"  B unique MIDDLEs: {len(all_b_middles)}")
    print(f"  B MIDDLEs in A-space: {len(b_in_a)} ({100*len(b_in_a)/len(all_b_middles):.1f}%)")
    print(f"  B MIDDLEs NOT in A-space: {len(b_not_in_a)}")
    print(f"  B co-occurring pairs (total): {len(b_cooccur_pairs)}")
    print(f"  B co-occurring pairs (both in A-space): {len(b_pairs_in_a)}")

    # Step 3: Compatibility concordance
    print("\n[3/6] Compatibility concordance...")

    n_compatible = 0
    n_incompatible = 0
    for m1, m2 in b_pairs_in_a:
        i, j = mid_to_idx[m1], mid_to_idx[m2]
        if M[i, j] == 1:
            n_compatible += 1
        else:
            n_incompatible += 1

    total_b_pairs = n_compatible + n_incompatible
    b_compat_rate = n_compatible / total_b_pairs if total_b_pairs > 0 else 0

    # A-space baseline: overall compatibility rate
    a_total_pairs = n * (n - 1) // 2
    a_compat_count = (M.sum() - n) // 2
    a_compat_rate = a_compat_count / a_total_pairs

    enrichment = b_compat_rate / a_compat_rate if a_compat_rate > 0 else float('inf')

    print(f"  B co-occurring pairs that are A-compatible: {n_compatible} / {total_b_pairs} ({100*b_compat_rate:.1f}%)")
    print(f"  A-space baseline compatibility rate: {100*a_compat_rate:.1f}%")
    print(f"  Enrichment: {enrichment:.1f}x")
    print(f"  B pairs that VIOLATE A-compatibility: {n_incompatible} ({100*(1-b_compat_rate):.1f}%)")

    # Statistical test: is B's compatibility rate higher than random?
    from scipy.stats import binomtest
    binom_result = binomtest(n_compatible, total_b_pairs, a_compat_rate, alternative='greater')
    print(f"  Binomial test (B > A baseline): p = {binom_result.pvalue:.2e}")

    # Step 4: Embedding distance concordance
    print("\n[4/6] Embedding distance concordance...")

    # Sample B-compatible and B-incompatible pairs
    rng = np.random.RandomState(42)

    b_compat_indices = []
    b_incompat_indices = []
    for m1, m2 in b_pairs_in_a:
        i, j = mid_to_idx[m1], mid_to_idx[m2]
        if M[i, j] == 1:
            b_compat_indices.append((i, j))
        else:
            b_incompat_indices.append((i, j))

    # Also sample random non-co-occurring pairs from A-space
    b_middles_in_a = sorted([mid_to_idx[m] for m in b_in_a])
    random_pairs = []
    b_cooccur_set = set()
    for m1, m2 in b_pairs_in_a:
        i, j = mid_to_idx[m1], mid_to_idx[m2]
        b_cooccur_set.add((min(i,j), max(i,j)))

    n_random_needed = min(len(b_compat_indices), 5000)
    while len(random_pairs) < n_random_needed:
        i = rng.choice(b_middles_in_a)
        j = rng.choice(b_middles_in_a)
        if i != j and (min(i,j), max(i,j)) not in b_cooccur_set:
            random_pairs.append((i, j))

    def mean_pair_distance(pairs, embedding):
        if not pairs:
            return 0, 0
        dists = [np.linalg.norm(embedding[i] - embedding[j]) for i, j in pairs[:5000]]
        return float(np.mean(dists)), float(np.std(dists))

    def mean_pair_cosine(pairs, embedding):
        if not pairs:
            return 0, 0
        cosines = []
        for i, j in pairs[:5000]:
            vi, vj = embedding[i], embedding[j]
            ni, nj = np.linalg.norm(vi), np.linalg.norm(vj)
            if ni > 1e-10 and nj > 1e-10:
                cosines.append(float(np.dot(vi, vj) / (ni * nj)))
        return float(np.mean(cosines)), float(np.std(cosines))

    # Full embedding
    bc_dist_full, bc_dist_std = mean_pair_distance(b_compat_indices, full_emb)
    bi_dist_full, bi_dist_std = mean_pair_distance(b_incompat_indices, full_emb)
    rand_dist_full, rand_dist_std = mean_pair_distance(random_pairs, full_emb)

    bc_cos_full, _ = mean_pair_cosine(b_compat_indices, full_emb)
    bi_cos_full, _ = mean_pair_cosine(b_incompat_indices, full_emb)
    rand_cos_full, _ = mean_pair_cosine(random_pairs, full_emb)

    print(f"\n  FULL embedding (with hub):")
    print(f"    {'Category':<30} {'Distance':>10} {'Cosine':>10}")
    print(f"    {'-'*55}")
    print(f"    {'B co-occur + A-compat':<30} {bc_dist_full:>10.3f} {bc_cos_full:>10.4f}")
    print(f"    {'B co-occur + A-incompat':<30} {bi_dist_full:>10.3f} {bi_cos_full:>10.4f}")
    print(f"    {'Random B-MIDDLE pairs':<30} {rand_dist_full:>10.3f} {rand_cos_full:>10.4f}")

    # Residual embedding
    bc_dist_res, _ = mean_pair_distance(b_compat_indices, res_emb)
    bi_dist_res, _ = mean_pair_distance(b_incompat_indices, res_emb)
    rand_dist_res, _ = mean_pair_distance(random_pairs, res_emb)

    bc_cos_res, _ = mean_pair_cosine(b_compat_indices, res_emb)
    bi_cos_res, _ = mean_pair_cosine(b_incompat_indices, res_emb)
    rand_cos_res, _ = mean_pair_cosine(random_pairs, res_emb)

    print(f"\n  RESIDUAL embedding (hub removed):")
    print(f"    {'Category':<30} {'Distance':>10} {'Cosine':>10}")
    print(f"    {'-'*55}")
    print(f"    {'B co-occur + A-compat':<30} {bc_dist_res:>10.3f} {bc_cos_res:>10.4f}")
    print(f"    {'B co-occur + A-incompat':<30} {bi_dist_res:>10.3f} {bi_cos_res:>10.4f}")
    print(f"    {'Random B-MIDDLE pairs':<30} {rand_dist_res:>10.3f} {rand_cos_res:>10.4f}")

    # Step 5: B-section structure in residual space
    print("\n[5/6] B-section structure in residual space...")
    b_section_middles = build_b_section_middles(mid_to_idx)

    from scipy.spatial.distance import pdist, squareform

    section_list = sorted(b_section_middles.keys())
    print(f"  B sections: {section_list}")

    section_centroids_full = {}
    section_centroids_res = {}

    for sec in section_list:
        indices = [mid_to_idx[m] for m in b_section_middles[sec] if m in mid_to_idx]
        if len(indices) >= 5:
            section_centroids_full[sec] = full_emb[indices].mean(axis=0)
            section_centroids_res[sec] = res_emb[indices].mean(axis=0)
            print(f"    Section {sec}: {len(indices)} MIDDLEs in A-space")

    if len(section_centroids_res) >= 2:
        sec_keys = sorted(section_centroids_res.keys())
        print(f"\n  Section centroid cosine similarity (RESIDUAL):")
        print(f"  {'':>6}", end='')
        for s in sec_keys:
            print(f"  {s:>6}", end='')
        print()

        res_cent_mat = np.array([section_centroids_res[s] for s in sec_keys])
        norms = np.linalg.norm(res_cent_mat, axis=1, keepdims=True)
        norms = np.maximum(norms, 1e-10)
        normed = res_cent_mat / norms
        cos_mat = normed @ normed.T

        for i, si in enumerate(sec_keys):
            print(f"  {si:>6}", end='')
            for j, sj in enumerate(sec_keys):
                print(f"  {cos_mat[i,j]:>6.3f}", end='')
            print()

        # Within vs between section distances
        within_b = []
        between_b = []
        for sec in section_list:
            if sec not in section_centroids_res:
                continue
            indices = [mid_to_idx[m] for m in b_section_middles[sec] if m in mid_to_idx]
            vecs = res_emb[indices]
            # Within-section pairwise distances (sample if too many)
            if len(indices) > 100:
                sample_idx = np.random.RandomState(42).choice(len(indices), 100, replace=False)
                vecs_sample = vecs[sample_idx]
            else:
                vecs_sample = vecs
            if len(vecs_sample) >= 2:
                within_dists = pdist(vecs_sample, 'euclidean')
                within_b.extend(within_dists.tolist())

        # Between-section: sample pairs from different sections
        rng2 = np.random.RandomState(123)
        for _ in range(5000):
            s1, s2 = rng2.choice(section_list, 2, replace=False)
            if s1 not in section_centroids_res or s2 not in section_centroids_res:
                continue
            mids1 = [m for m in b_section_middles[s1] if m in mid_to_idx]
            mids2 = [m for m in b_section_middles[s2] if m in mid_to_idx]
            if mids1 and mids2:
                m1 = rng2.choice(mids1)
                m2 = rng2.choice(mids2)
                d = np.linalg.norm(res_emb[mid_to_idx[m1]] - res_emb[mid_to_idx[m2]])
                between_b.append(float(d))

        if within_b and between_b:
            from scipy.stats import mannwhitneyu
            mean_within_b = np.mean(within_b)
            mean_between_b = np.mean(between_b)
            ratio_b = mean_within_b / mean_between_b
            stat_b, p_b = mannwhitneyu(within_b[:5000], between_b[:5000], alternative='less')
            print(f"\n  B-section within/between (RESIDUAL):")
            print(f"    Within-section distance: {mean_within_b:.3f}")
            print(f"    Between-section distance: {mean_between_b:.3f}")
            print(f"    Ratio: {ratio_b:.3f}")
            print(f"    Mann-Whitney p: {p_b:.2e}")

    # Step 6: Violation analysis
    print("\n[6/6] Violation analysis — B pairs that break A-compatibility...")

    # Characterize the violations
    violation_freq_sum = []
    compat_freq_sum = []
    mid_freq = defaultdict(int)
    tx2 = Transcript()
    morph2 = Morphology()
    for token in tx2.currier_a():
        word = token.word.strip()
        if not word or '*' in word:
            continue
        m = morph2.extract(word)
        if m.middle:
            mid_freq[m.middle] += 1

    for m1, m2 in b_pairs_in_a:
        i, j = mid_to_idx[m1], mid_to_idx[m2]
        freq_sum = mid_freq.get(m1, 0) + mid_freq.get(m2, 0)
        if M[i, j] == 1:
            compat_freq_sum.append(freq_sum)
        else:
            violation_freq_sum.append(freq_sum)

    if violation_freq_sum and compat_freq_sum:
        print(f"  A-compatible B pairs: mean freq sum = {np.mean(compat_freq_sum):.1f}")
        print(f"  A-violating B pairs: mean freq sum = {np.mean(violation_freq_sum):.1f}")
        print(f"  Violation freq ratio: {np.mean(violation_freq_sum)/np.mean(compat_freq_sum):.3f}")

    # What fraction of B's vocabulary usage is compatible?
    b_token_pairs = 0
    b_token_compat = 0
    for key, middles in b_line_middles.items():
        mid_list_in_a = [m for m in middles if m in mid_to_idx]
        for i in range(len(mid_list_in_a)):
            for j in range(i + 1, len(mid_list_in_a)):
                idx_i = mid_to_idx[mid_list_in_a[i]]
                idx_j = mid_to_idx[mid_list_in_a[j]]
                b_token_pairs += 1
                if M[idx_i, idx_j] == 1:
                    b_token_compat += 1

    b_token_rate = b_token_compat / b_token_pairs if b_token_pairs > 0 else 0
    print(f"\n  Token-level (weighted by frequency):")
    print(f"    B line-pair instances: {b_token_pairs}")
    print(f"    A-compatible instances: {b_token_compat} ({100*b_token_rate:.1f}%)")
    print(f"    Token-level enrichment: {b_token_rate/a_compat_rate:.1f}x over A baseline")

    # Summary
    print(f"\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}")

    print(f"\n  Compatibility concordance:")
    print(f"    B co-occurring pairs A-compatible: {100*b_compat_rate:.1f}%")
    print(f"    A baseline: {100*a_compat_rate:.1f}%")
    print(f"    Enrichment: {enrichment:.1f}x (p={binom_result.pvalue:.2e})")
    print(f"    Token-weighted concordance: {100*b_token_rate:.1f}%")

    print(f"\n  Embedding distances (RESIDUAL — genuine structure):")
    print(f"    B+A-compat distance: {bc_dist_res:.3f}")
    print(f"    B+A-incompat distance: {bi_dist_res:.3f}")
    print(f"    Random distance: {rand_dist_res:.3f}")
    if bi_dist_res > 0:
        print(f"    Compat/Incompat ratio: {bc_dist_res/bi_dist_res:.3f}")

    # Verdict
    if b_compat_rate > 0.10 and enrichment > 3.0:
        if bc_dist_res < bi_dist_res:
            verdict = "STRONG_CONCORDANCE"
            explanation = (f"B strongly respects A's discrimination geometry. "
                          f"{100*b_compat_rate:.0f}% of B co-occurring pairs are A-compatible "
                          f"({enrichment:.0f}x enrichment). Compatible pairs are closer in "
                          f"residual space ({bc_dist_res:.3f} vs {bi_dist_res:.3f}).")
        else:
            verdict = "COMPATIBILITY_CONCORDANCE"
            explanation = (f"B respects A's compatibility boundaries ({100*b_compat_rate:.0f}%, "
                          f"{enrichment:.0f}x enrichment) but distance structure in residual "
                          f"space is not differentiated.")
    elif b_compat_rate > a_compat_rate * 2:
        verdict = "PARTIAL_CONCORDANCE"
        explanation = (f"B shows moderate A-compatibility enrichment ({enrichment:.1f}x) "
                      f"but not overwhelming.")
    else:
        verdict = "NO_CONCORDANCE"
        explanation = f"B does not preferentially respect A's compatibility structure."

    print(f"\n  VERDICT: {verdict}")
    print(f"  {explanation}")

    # Save
    results = {
        'test': 'T12_b_side_validation',
        'n_a_middles': n,
        'n_b_middles_total': len(all_b_middles),
        'n_b_in_a_space': len(b_in_a),
        'n_b_not_in_a': len(b_not_in_a),
        'b_coverage_of_a': float(len(b_in_a) / n),
        'n_b_cooccur_pairs': len(b_pairs_in_a),
        'compatibility': {
            'n_compatible': n_compatible,
            'n_incompatible': n_incompatible,
            'b_compat_rate': float(b_compat_rate),
            'a_baseline_rate': float(a_compat_rate),
            'enrichment': float(enrichment),
            'binomial_p': float(binom_result.pvalue),
            'token_level_rate': float(b_token_rate),
            'token_level_enrichment': float(b_token_rate / a_compat_rate) if a_compat_rate > 0 else 0,
        },
        'distances_full': {
            'b_compat': float(bc_dist_full),
            'b_incompat': float(bi_dist_full),
            'random': float(rand_dist_full),
            'b_compat_cos': float(bc_cos_full),
            'b_incompat_cos': float(bi_cos_full),
            'random_cos': float(rand_cos_full),
        },
        'distances_residual': {
            'b_compat': float(bc_dist_res),
            'b_incompat': float(bi_dist_res),
            'random': float(rand_dist_res),
            'b_compat_cos': float(bc_cos_res),
            'b_incompat_cos': float(bi_cos_res),
            'random_cos': float(rand_cos_res),
        },
        'verdict': verdict,
        'explanation': explanation,
    }

    with open(RESULTS_DIR / 't12_b_side_validation.json', 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved to {RESULTS_DIR / 't12_b_side_validation.json'}")


if __name__ == '__main__':
    run()
