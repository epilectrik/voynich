"""
T4: HUB Compound and Position Analysis
========================================
Phase: HUB_ROLE_DECOMPOSITION

Tests whether compound structure, line position, and regime create
sub-roles within HUB_UNIVERSAL (Bin 6).

Tests:
  4a: Compound vs atomic HUB MIDDLEs — behavioral signature comparison
  4b: Position-dependent sub-roles (line-initial/final/mid)
  4c: Regime sub-clustering within HUB

Output: t4_hub_compound_position_analysis.json
"""

import sys
import json
import functools
from pathlib import Path
from collections import defaultdict, Counter
import numpy as np
from scipy import stats
from scipy.cluster.hierarchy import fcluster, linkage

PROJECT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(PROJECT))
from scripts.voynich import Transcript, Morphology

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)

RESULTS_DIR = Path(__file__).parent.parent / 'results'
RESULTS_DIR.mkdir(exist_ok=True)

HUB_BIN = 6
SIGNATURE_DIMS = [
    'length', 'k_ratio', 'e_ratio', 'h_ratio', 'is_compound',
    'qo_affinity', 'regime_1_enrichment', 'regime_2_enrichment',
    'regime_3_enrichment', 'regime_4_enrichment', 'regime_entropy',
    'initial_rate', 'final_rate', 'folio_spread',
]


def silhouette_score_manual(X, labels):
    """Simple silhouette score for small N (avoids sklearn dependency)."""
    n = len(labels)
    unique_labels = np.unique(labels)
    if len(unique_labels) < 2 or n < 3:
        return 0.0

    sil_vals = np.zeros(n)
    for i in range(n):
        same_mask = labels == labels[i]
        same_mask[i] = False
        if same_mask.sum() == 0:
            sil_vals[i] = 0.0
            continue
        a_i = np.mean(np.sqrt(np.sum((X[same_mask] - X[i]) ** 2, axis=1)))

        min_b = np.inf
        for lbl in unique_labels:
            if lbl == labels[i]:
                continue
            other_mask = labels == lbl
            if other_mask.sum() == 0:
                continue
            b_val = np.mean(np.sqrt(np.sum((X[other_mask] - X[i]) ** 2, axis=1)))
            min_b = min(min_b, b_val)

        if min_b == np.inf:
            sil_vals[i] = 0.0
        else:
            sil_vals[i] = (min_b - a_i) / max(a_i, min_b)

    return float(np.mean(sil_vals))


def main():
    morph = Morphology()

    # ── Load affordance table ──────────────────────────────
    with open(PROJECT / 'data' / 'middle_affordance_table.json') as f:
        aff = json.load(f)

    hub_middles = {}
    middle_to_bin = {}
    for mid, data in aff['middles'].items():
        middle_to_bin[mid] = data['affordance_bin']
        if data['affordance_bin'] == HUB_BIN:
            hub_middles[mid] = data

    # ── Load forbidden inventory for hazard-adjacent detection ──
    with open(PROJECT / 'phases' / '15-20_kernel_grammar' /
              'phase18a_forbidden_inventory.json') as f:
        inv = json.load(f)

    forbidden_set = set()
    for tr in inv['transitions']:
        forbidden_set.add((tr['source'], tr['target']))

    # ══════════════════════════════════════════════════════
    # TEST 4a: COMPOUND vs ATOMIC WITHIN HUB
    # ══════════════════════════════════════════════════════
    print(f"{'='*70}")
    print(f"T4a: COMPOUND vs ATOMIC HUB MIDDLEs")
    print(f"{'='*70}")

    compound_hub = []
    atomic_hub = []
    for mid, data in hub_middles.items():
        is_comp = data['behavioral_signature'].get('is_compound', 0.0)
        if is_comp >= 0.5:
            compound_hub.append(mid)
        else:
            atomic_hub.append(mid)

    print(f"\n  Compound HUB MIDDLEs ({len(compound_hub)}): {sorted(compound_hub)}")
    print(f"  Atomic HUB MIDDLEs ({len(atomic_hub)}): {sorted(atomic_hub)}")

    # Behavioral comparison
    comp_sigs = []
    for mid in compound_hub:
        bs = hub_middles[mid]['behavioral_signature']
        comp_sigs.append([bs.get(d, 0.0) for d in SIGNATURE_DIMS])
    atom_sigs = []
    for mid in atomic_hub:
        bs = hub_middles[mid]['behavioral_signature']
        atom_sigs.append([bs.get(d, 0.0) for d in SIGNATURE_DIMS])

    comp_arr = np.array(comp_sigs) if comp_sigs else np.empty((0, len(SIGNATURE_DIMS)))
    atom_arr = np.array(atom_sigs) if atom_sigs else np.empty((0, len(SIGNATURE_DIMS)))

    print(f"\n  {'Dimension':<24s} {'U':>8s} {'p':>10s} "
          f"{'Comp':>10s} {'Atom':>10s}")
    print(f"  {'-'*24} {'-'*8} {'-'*10} {'-'*10} {'-'*10}")

    compound_comparison = {}
    for i, dim in enumerate(SIGNATURE_DIMS):
        c_vals = comp_arr[:, i] if comp_arr.shape[0] > 0 else np.array([])
        a_vals = atom_arr[:, i] if atom_arr.shape[0] > 0 else np.array([])

        if len(c_vals) >= 1 and len(a_vals) >= 1:
            # Use exact permutation test for small N
            all_vals = np.concatenate([c_vals, a_vals])
            observed_diff = abs(np.mean(c_vals) - np.mean(a_vals))
            n_c = len(c_vals)
            rng = np.random.default_rng(42 + i)
            n_perm = 10000
            perm_diffs = np.zeros(n_perm)
            for p_idx in range(n_perm):
                perm = rng.permutation(all_vals)
                perm_diffs[p_idx] = abs(np.mean(perm[:n_c]) - np.mean(perm[n_c:]))
            p_val = float(np.mean(perm_diffs >= observed_diff))
            U_stat = 0.0  # Not meaningful for exact test
        else:
            U_stat, p_val = 0.0, 1.0

        c_mean = float(np.mean(c_vals)) if len(c_vals) > 0 else float('nan')
        a_mean = float(np.mean(a_vals)) if len(a_vals) > 0 else float('nan')

        compound_comparison[dim] = {
            'p_permutation': float(p_val),
            'compound_mean': c_mean,
            'atomic_mean': a_mean,
        }

        sig = '*' if p_val < 0.05 else ''
        print(f"  {dim:<22s} {'perm':>8s} {p_val:>10.4f} "
              f"{c_mean:>10.3f} {a_mean:>10.3f} {sig}")

    # ══════════════════════════════════════════════════════
    # TEST 4b: POSITION-DEPENDENT SUB-ROLES
    # ══════════════════════════════════════════════════════
    print(f"\n{'='*70}")
    print(f"T4b: POSITION-DEPENDENT SUB-ROLES WITHIN HUB")
    print(f"{'='*70}")

    # Pre-compute word -> middle
    tx = Transcript()
    unique_words = set()
    line_tokens_map = defaultdict(list)

    for token in tx.currier_b():
        w = token.word.strip()
        if not w or '*' in w:
            continue
        unique_words.add(w)
        line_tokens_map[(token.folio, token.line)].append(w)

    word_to_middle = {}
    for w in unique_words:
        m = morph.extract(w)
        word_to_middle[w] = m.middle or ''

    # Single corpus pass: collect position data for HUB tokens
    hub_set = set(hub_middles.keys())
    mid_positions = defaultdict(list)     # middle -> [normalized_positions]
    mid_pos_category = defaultdict(lambda: Counter())  # middle -> Counter{INITIAL/FINAL/MID}
    hub_hazard_adj_positions = []   # positions of HUB tokens adjacent to forbidden
    hub_non_hazard_positions = []   # positions of HUB tokens not adjacent

    for (folio, line_id), words in line_tokens_map.items():
        n = len(words)
        if n == 0:
            continue
        for pos, w in enumerate(words):
            mid = word_to_middle.get(w, '')
            if mid not in hub_set:
                continue

            norm_pos = pos / (n - 1) if n > 1 else 0.5
            mid_positions[mid].append(norm_pos)

            if pos == 0:
                mid_pos_category[mid]['INITIAL'] += 1
            elif pos == n - 1:
                mid_pos_category[mid]['FINAL'] += 1
            else:
                mid_pos_category[mid]['MID'] += 1

            # Check forbidden adjacency
            is_hazard_adj = False
            if pos > 0:
                left = words[pos - 1]
                if (left, w) in forbidden_set:
                    is_hazard_adj = True
            if pos < n - 1:
                right = words[pos + 1]
                if (w, right) in forbidden_set:
                    is_hazard_adj = True

            if is_hazard_adj:
                hub_hazard_adj_positions.append(norm_pos)
            else:
                hub_non_hazard_positions.append(norm_pos)

    # Position statistics per HUB MIDDLE
    print(f"\n  {'MIDDLE':<10s} {'N':>6s} {'Mean Pos':>10s} "
          f"{'Init%':>8s} {'Final%':>8s} {'Mid%':>8s}")
    print(f"  {'-'*10} {'-'*6} {'-'*10} {'-'*8} {'-'*8} {'-'*8}")

    per_middle_position = {}
    for mid in sorted(hub_middles.keys()):
        positions = mid_positions.get(mid, [])
        cat = mid_pos_category.get(mid, Counter())
        n_tok = len(positions)
        if n_tok == 0:
            continue
        mean_pos = float(np.mean(positions))
        init_pct = cat['INITIAL'] / n_tok * 100
        final_pct = cat['FINAL'] / n_tok * 100
        mid_pct = cat['MID'] / n_tok * 100

        per_middle_position[mid] = {
            'n_tokens': n_tok, 'mean_position': mean_pos,
            'initial_pct': init_pct, 'final_pct': final_pct,
            'mid_pct': mid_pct,
        }
        print(f"  {mid:<10s} {n_tok:>6d} {mean_pos:>10.3f} "
              f"{init_pct:>7.1f}% {final_pct:>7.1f}% {mid_pct:>7.1f}%")

    # Hazard-adjacent vs non-hazard position comparison
    hazard_pos_arr = np.array(hub_hazard_adj_positions) if hub_hazard_adj_positions else np.array([])
    non_hazard_pos_arr = np.array(hub_non_hazard_positions) if hub_non_hazard_positions else np.array([])

    if len(hazard_pos_arr) >= 2 and len(non_hazard_pos_arr) >= 2:
        U_pos, p_pos = stats.mannwhitneyu(hazard_pos_arr, non_hazard_pos_arr,
                                           alternative='two-sided')
    else:
        U_pos, p_pos = 0.0, 1.0

    hazard_mean = float(np.mean(hazard_pos_arr)) if len(hazard_pos_arr) > 0 else float('nan')
    nonhaz_mean = float(np.mean(non_hazard_pos_arr)) if len(non_hazard_pos_arr) > 0 else float('nan')

    print(f"\n  Hazard-adjacent HUB tokens: n={len(hazard_pos_arr)}, "
          f"mean_pos={hazard_mean:.3f}")
    print(f"  Non-hazard HUB tokens:     n={len(non_hazard_pos_arr)}, "
          f"mean_pos={nonhaz_mean:.3f}")
    print(f"  Mann-Whitney U: U={U_pos:.1f}, p={p_pos:.4f}")

    position_analysis = {
        'hazard_adjacent_n': len(hazard_pos_arr),
        'non_hazard_n': len(non_hazard_pos_arr),
        'hazard_adj_mean_pos': hazard_mean,
        'non_hazard_mean_pos': nonhaz_mean,
        'position_MW_U': float(U_pos),
        'position_p': float(p_pos),
        'per_middle_position': per_middle_position,
    }

    # ══════════════════════════════════════════════════════
    # TEST 4c: REGIME SUB-CLUSTERING WITHIN HUB
    # ══════════════════════════════════════════════════════
    print(f"\n{'='*70}")
    print(f"T4c: REGIME SUB-CLUSTERING WITHIN HUB")
    print(f"{'='*70}")

    # Build regime profile vectors for each HUB MIDDLE
    regime_dims = ['regime_1_enrichment', 'regime_2_enrichment',
                   'regime_3_enrichment', 'regime_4_enrichment']
    hub_regime_data = []
    hub_mid_order = []
    for mid in sorted(hub_middles.keys()):
        bs = hub_middles[mid]['behavioral_signature']
        vec = [bs.get(d, 0.0) for d in regime_dims]
        hub_regime_data.append(vec)
        hub_mid_order.append(mid)

    regime_arr = np.array(hub_regime_data)

    # Normalize for clustering
    regime_norm = regime_arr.copy()
    for col in range(regime_norm.shape[1]):
        std = np.std(regime_norm[:, col])
        if std > 0:
            regime_norm[:, col] = (regime_norm[:, col] - np.mean(regime_norm[:, col])) / std

    # Hierarchical clustering
    best_sil = -1.0
    best_k = 2
    best_labels = None
    cluster_results = {}

    if len(regime_norm) >= 4:
        Z = linkage(regime_norm, method='ward')
        for k in [2, 3, 4]:
            if k >= len(regime_norm):
                continue
            labels = fcluster(Z, t=k, criterion='maxclust')
            sil = silhouette_score_manual(regime_norm, labels)
            cluster_results[k] = {
                'silhouette': float(sil),
                'cluster_sizes': [int(np.sum(labels == c))
                                  for c in range(1, k + 1)],
            }
            if sil > best_sil:
                best_sil = sil
                best_k = k
                best_labels = labels

    print(f"\n  Clustering results (regime profiles):")
    for k, res in sorted(cluster_results.items()):
        print(f"    k={k}: silhouette={res['silhouette']:.3f}, "
              f"sizes={res['cluster_sizes']}")

    # Show best clustering
    cluster_assignments = {}
    if best_labels is not None:
        print(f"\n  Best: k={best_k} (silhouette={best_sil:.3f})")
        for i, mid in enumerate(hub_mid_order):
            cluster_assignments[mid] = int(best_labels[i])

        for c in range(1, best_k + 1):
            members = [mid for mid, cl in cluster_assignments.items() if cl == c]
            mean_regime = np.mean(regime_arr[[i for i, m in enumerate(hub_mid_order)
                                              if m in members]], axis=0)
            print(f"    Cluster {c}: {sorted(members)}")
            print(f"      Regime profile: "
                  f"R1={mean_regime[0]:.2f} R2={mean_regime[1]:.2f} "
                  f"R3={mean_regime[2]:.2f} R4={mean_regime[3]:.2f}")

    regime_clustering = {
        'best_k': best_k,
        'best_silhouette': float(best_sil),
        'cluster_results': cluster_results,
        'cluster_assignments': cluster_assignments,
    }

    # ── Verdict ────────────────────────────────────────────
    compound_sig = sum(1 for d in compound_comparison.values()
                       if d['p_permutation'] < 0.05)
    position_sig = p_pos < 0.05
    regime_sig = best_sil > 0.25

    signals = []
    if compound_sig >= 2:
        signals.append('COMPOUND')
    if position_sig:
        signals.append('POSITION')
    if regime_sig:
        signals.append('REGIME')

    if len(signals) >= 2:
        verdict = 'MULTI_SIGNAL_SUBROLES'
        detail = f"Multiple dimensions predict sub-roles: {', '.join(signals)}."
    elif len(signals) == 1:
        verdict = f'{signals[0]}_PREDICTS'
        detail = f"{signals[0]} creates partial sub-structure within HUB."
    else:
        verdict = 'NO_SUBROLE_STRUCTURE'
        detail = ('Neither compound status, position, nor regime creates '
                  'significant sub-structure within HUB.')

    print(f"\nVERDICT: {verdict}")
    print(f"  {detail}")

    # ── Output ─────────────────────────────────────────────
    output = {
        'metadata': {
            'phase': 'HUB_ROLE_DECOMPOSITION',
            'test': 'T4_COMPOUND_POSITION_ANALYSIS',
        },
        'compound_analysis': {
            'compound_hub': sorted(compound_hub),
            'atomic_hub': sorted(atomic_hub),
            'comparison': compound_comparison,
            'significant_dimensions': compound_sig,
        },
        'position_analysis': position_analysis,
        'regime_clustering': regime_clustering,
        'verdict': verdict,
        'verdict_detail': detail,
    }

    out_path = RESULTS_DIR / 't4_hub_compound_position_analysis.json'
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nOutput: {out_path}")


if __name__ == '__main__':
    main()
