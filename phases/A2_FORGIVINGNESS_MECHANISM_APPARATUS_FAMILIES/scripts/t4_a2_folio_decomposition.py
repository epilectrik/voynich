"""
T4: Within-A2 Structure + Boundary Analysis
Phase 573 - A2_FORGIVINGNESS_MECHANISM_APPARATUS_FAMILIES

Ranks individual A2 folios and tests whether A2 is monolithic or internally
structured.

Diagnostics:
  - CCS1 ranking within A2
  - Section-stratified analysis (C|A2, H|A2, T|A2)
  - A2 conformity score (distance to A2/A1/A3 centroids)
  - Grammar amplification score (real-minus-null DYE/YGA/NRI)
  - Gap-to-passing analysis
  - T|A2 anomaly investigation
"""

import json
import sys
import os
import math
import time
from pathlib import Path
from datetime import datetime, timezone

PROJECT_ROOT = str(Path(__file__).resolve().parents[3])
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

RESULTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'results')
P572_RESULTS = os.path.join(PROJECT_ROOT, 'phases', 'PRODUCTIVE_DISRUPTION_EXPANSION', 'results')

ABLATION_NAMES = [
    'NO_CROSS_COUPLING',
    'NO_CLOSE_RECOVERY',
    'NO_CONTAINMENT',
    'NO_TR_TO_Y',
    'NO_Y_SENSITIVITY',
]


def euclidean_dist(a, b):
    return math.sqrt(sum((ai - bi) ** 2 for ai, bi in zip(a, b)))


def load_data():
    """Load Phase 572 data + T1/T3 results."""
    print("  Loading Phase 572 T1 setup...")
    with open(os.path.join(P572_RESULTS, 't1_full_scale_setup.json'), 'r', encoding='utf-8') as f:
        t1_setup = json.load(f)

    print("  Loading Phase 572 T5 A2 audit...")
    with open(os.path.join(P572_RESULTS, 't5_a2_audit.json'), 'r', encoding='utf-8') as f:
        t5_audit = json.load(f)

    print("  Loading T1 mechanism ablation...")
    with open(os.path.join(RESULTS_DIR, 't1_mechanism_ablation.json'), 'r', encoding='utf-8') as f:
        t1_ablation = json.load(f)

    print("  Loading T3 clustering results...")
    t3_path = os.path.join(RESULTS_DIR, 't3_response_families.json')
    t3_clustering = None
    if os.path.exists(t3_path):
        with open(t3_path, 'r', encoding='utf-8') as f:
            t3_clustering = json.load(f)

    return t1_setup, t5_audit, t1_ablation, t3_clustering


def main():
    t_start = time.time()
    print("=" * 70)
    print("T4: Within-A2 Structure + Boundary Analysis")
    print("Phase 573 - A2_FORGIVINGNESS_MECHANISM_APPARATUS_FAMILIES")
    print("=" * 70)

    print("\n--- Loading data ---")
    t1_setup, t5_audit, t1_ablation, t3_clustering = load_data()

    eligible_folios = t1_setup['eligible_folios']
    folio_configs = t1_setup['folio_configs']
    per_folio_572 = t5_audit['per_folio_metrics']
    per_folio_abl = t1_ablation['per_folio']

    # ================================================================
    # Build response feature vectors for centroid computation
    # ================================================================
    print("\n--- Building response feature vectors ---")

    profile_vectors = {}  # profile -> list of (folio, feature_vec)
    all_vectors = {}  # folio -> feature_vec

    for folio in eligible_folios:
        abl = per_folio_abl.get(folio)
        if abl is None:
            continue

        m1_dye = abl['baseline_m1_dye']
        ccs1 = abl['baseline_m4f_dye']
        crr_m4f = abl['crr_m4f']
        nri_m4f = abl['nri_m4f']
        dye_adv = m1_dye - ccs1

        abl_shares = [abl['ablations'][a]['delta_m4f_dye'] for a in ABLATION_NAMES]

        vec = [m1_dye, ccs1, dye_adv, crr_m4f, nri_m4f] + abl_shares

        profile = folio_configs[folio]['profile']
        profile_vectors.setdefault(profile, []).append((folio, vec))
        all_vectors[folio] = vec

    # Compute profile centroids
    profile_centroids = {}
    for profile, pairs in profile_vectors.items():
        vecs = [p[1] for p in pairs]
        d = len(vecs[0])
        centroid = [sum(v[j] for v in vecs) / len(vecs) for j in range(d)]
        profile_centroids[profile] = centroid

    # ================================================================
    # 1. CCS1 ranking within A2
    # ================================================================
    print("\n--- A2 CCS1 Ranking ---")

    a2_folios = []
    for folio in eligible_folios:
        fc = folio_configs[folio]
        if 'A2' not in fc['profile']:
            continue
        abl = per_folio_abl.get(folio)
        p572 = per_folio_572.get(folio, {})
        if abl is None:
            continue

        a2_folios.append({
            'folio': folio,
            'section': fc['section'],
            'ccs1': abl['baseline_m4f_dye'],
            'm1_dye': abl['baseline_m1_dye'],
            'dye_advantage': abl['baseline_m1_dye'] - abl['baseline_m4f_dye'],
            'crr_m4f': abl['crr_m4f'],
            'nri_m4f': abl['nri_m4f'],
            'epv': p572.get('epv', 0.0),
            'n_events': p572.get('n_events_m1', 0),
            'F1': fc['F1'],
            'F2': fc['F2'],
            'F3': fc['F3'],
            'F4_raw': fc['F4_raw'],
            'F5': fc['F5'],
        })

    # Sort by CCS1 (highest = most forgiving)
    a2_folios.sort(key=lambda x: x['ccs1'], reverse=True)

    print(f"\n  {'Rank':<5s} {'Folio':<8s} {'Sect':<5s} {'CCS1':>7s} {'M1_DYE':>7s} "
          f"{'DYEadv':>7s} {'EPV':>5s} {'Events':>6s}")
    for rank, af in enumerate(a2_folios, 1):
        print(f"  {rank:<5d} {af['folio']:<8s} {af['section']:<5s} "
              f"{af['ccs1']:7.4f} {af['m1_dye']:7.4f} "
              f"{af['dye_advantage']:+7.4f} {af['epv']:5.2f} {af['n_events']:6d}")

    # ================================================================
    # 2. Section-stratified analysis
    # ================================================================
    print("\n--- Section-stratified A2 analysis ---")

    section_groups = {}
    for af in a2_folios:
        s = af['section']
        section_groups.setdefault(s, []).append(af)

    section_stats = {}
    for s in sorted(section_groups):
        group = section_groups[s]
        n = len(group)
        mean_ccs1 = sum(af['ccs1'] for af in group) / n
        mean_adv = sum(af['dye_advantage'] for af in group) / n
        mean_epv = sum(af['epv'] for af in group) / n
        section_stats[s] = {
            'n_folios': n,
            'folios': [af['folio'] for af in group],
            'mean_ccs1': round(mean_ccs1, 4),
            'mean_dye_advantage': round(mean_adv, 4),
            'mean_epv': round(mean_epv, 4),
        }
        print(f"  {s}|A2 (n={n}): CCS1={mean_ccs1:.4f}  adv={mean_adv:+.4f}  EPV={mean_epv:.2f}")

    # ================================================================
    # 3. A2 conformity score (centroid distances)
    # ================================================================
    print("\n--- A2 conformity scores ---")

    a2_centroid = profile_centroids.get('A2_SEALED_RECIRCULATION')
    conformity_scores = []

    for af in a2_folios:
        vec = all_vectors.get(af['folio'])
        if vec is None or a2_centroid is None:
            continue

        dist_a2 = euclidean_dist(vec, a2_centroid)
        dist_others = {}
        for profile, centroid in profile_centroids.items():
            if 'A2' not in profile:
                dist_others[profile] = euclidean_dist(vec, centroid)

        # Classification
        min_other_profile = min(dist_others, key=dist_others.get) if dist_others else None
        min_other_dist = dist_others.get(min_other_profile, float('inf'))

        if dist_a2 <= min_other_dist * 0.8:
            conformity = 'core_A2'
        elif min_other_dist < dist_a2:
            if 'A1' in min_other_profile:
                conformity = 'A2_to_A1_boundary'
            elif 'A3' in min_other_profile:
                conformity = 'A2_to_A3_boundary'
            else:
                conformity = 'anomalous_A2'
        else:
            conformity = 'marginal_A2'

        conformity_scores.append({
            'folio': af['folio'],
            'section': af['section'],
            'dist_a2': round(dist_a2, 4),
            'dist_others': {p: round(d, 4) for p, d in dist_others.items()},
            'closest_other': min_other_profile,
            'conformity': conformity,
            'ccs1': af['ccs1'],
        })

    print(f"\n  {'Folio':<8s} {'Sect':<5s} {'d_A2':>6s} {'d_other':>7s} {'Closest':>28s} {'Class':<20s}")
    for cs in conformity_scores:
        min_other = min(cs['dist_others'].values()) if cs['dist_others'] else 0
        print(f"  {cs['folio']:<8s} {cs['section']:<5s} {cs['dist_a2']:6.2f} "
              f"{min_other:7.2f} {cs['closest_other'] or '':>28s} {cs['conformity']:<20s}")

    # Conformity summary
    conformity_counts = {}
    for cs in conformity_scores:
        c = cs['conformity']
        conformity_counts[c] = conformity_counts.get(c, 0) + 1
    print(f"\n  Conformity distribution: {conformity_counts}")

    # ================================================================
    # 4. Grammar amplification score
    # ================================================================
    print("\n--- Grammar amplification scores ---")

    amplification_scores = []
    for af in a2_folios:
        abl = per_folio_abl.get(af['folio'])
        if abl is None:
            continue

        # Grammar amplification = real-minus-null metrics
        amp_dye = abl['baseline_m1_dye'] - abl['baseline_m4f_dye']
        amp_nri = abl['nri_m1'] - abl['nri_m4f']

        amplification_scores.append({
            'folio': af['folio'],
            'section': af['section'],
            'ccs1': af['ccs1'],
            'amp_dye': round(amp_dye, 4),
            'amp_nri': round(amp_nri, 4),
            'n_events': af['n_events'],
        })

    # Sort by amp_dye (highest = strongest grammar amplification despite A2)
    amplification_scores.sort(key=lambda x: x['amp_dye'], reverse=True)

    print(f"\n  {'Folio':<8s} {'Sect':<5s} {'CCS1':>7s} {'amp_DYE':>8s} "
          f"{'amp_NRI':>8s} {'Events':>6s}")
    for amp in amplification_scores:
        print(f"  {amp['folio']:<8s} {amp['section']:<5s} {amp['ccs1']:7.4f} "
              f"{amp['amp_dye']:+8.4f} {amp['amp_nri']:+8.4f} {amp['n_events']:6d}")

    # Identify strong-demand A2 subfamily
    mean_amp = sum(a['amp_dye'] for a in amplification_scores) / len(amplification_scores) if amplification_scores else 0
    strong_demand = [a for a in amplification_scores if a['amp_dye'] > mean_amp + 0.01]
    weak_demand = [a for a in amplification_scores if a['amp_dye'] <= mean_amp - 0.01]

    print(f"\n  Mean A2 amp_DYE: {mean_amp:.4f}")
    print(f"  Strong-demand A2 (amp_DYE > mean+0.01): {len(strong_demand)} folios")
    print(f"  Weak-demand A2 (amp_DYE < mean-0.01): {len(weak_demand)} folios")

    # ================================================================
    # 5. Gap-to-passing analysis
    # ================================================================
    print("\n--- Gap-to-passing analysis ---")

    gap_analysis = []
    for af in a2_folios:
        if af['epv'] >= 0.80:
            gap = 0.0  # Already passing
        else:
            # How much would CCS1 need to decrease?
            # EPV = fraction of 20 perms where null DYE < M1 DYE
            # To pass EPV >= 0.80, we'd need ~80% of null perms to have lower DYE
            # Approximate gap as distance from current DYE advantage to 0
            gap = max(0, -af['dye_advantage'])  # If advantage is negative, gap = |advantage|

        gap_analysis.append({
            'folio': af['folio'],
            'section': af['section'],
            'epv': af['epv'],
            'dye_advantage': af['dye_advantage'],
            'ccs1': af['ccs1'],
            'passing': af['epv'] >= 0.80,
            'gap_to_passing': round(gap, 4),
        })

    n_passing = sum(1 for g in gap_analysis if g['passing'])
    n_failing = len(gap_analysis) - n_passing
    print(f"  A2 folios passing EPV >= 0.80: {n_passing}/{len(gap_analysis)}")
    print(f"  A2 folios failing: {n_failing}")

    if n_failing > 0:
        failing = [g for g in gap_analysis if not g['passing']]
        failing.sort(key=lambda x: x['epv'], reverse=True)
        print(f"\n  Failing folios (closest to passing first):")
        for g in failing[:10]:
            print(f"    {g['folio']:<8s} sect={g['section']}  EPV={g['epv']:.2f}  "
                  f"adv={g['dye_advantage']:+.4f}  CCS1={g['ccs1']:.4f}")

    # ================================================================
    # 6. Feature-CCS1 correlation within A2
    # ================================================================
    print("\n--- Feature-CCS1 correlations within A2 ---")

    def spearman_rho(x, y):
        """Compute Spearman rank correlation."""
        n = len(x)
        if n < 3:
            return 0.0
        rx = [0] * n
        ry = [0] * n
        sx = sorted(range(n), key=lambda i: x[i])
        sy = sorted(range(n), key=lambda i: y[i])
        for rank, idx in enumerate(sx):
            rx[idx] = rank
        for rank, idx in enumerate(sy):
            ry[idx] = rank
        mean_rx = sum(rx) / n
        mean_ry = sum(ry) / n
        num = sum((rx[i] - mean_rx) * (ry[i] - mean_ry) for i in range(n))
        den_x = math.sqrt(sum((rx[i] - mean_rx) ** 2 for i in range(n)))
        den_y = math.sqrt(sum((ry[i] - mean_ry) ** 2 for i in range(n)))
        if den_x < 1e-10 or den_y < 1e-10:
            return 0.0
        return num / (den_x * den_y)

    ccs1_values = [af['ccs1'] for af in a2_folios]
    feature_correlations = {}

    for feat_name in ['F1', 'F2', 'F3', 'F4_raw', 'F5', 'n_events']:
        feat_values = [af[feat_name] for af in a2_folios]
        rho = spearman_rho(feat_values, ccs1_values)
        feature_correlations[feat_name] = round(rho, 4)
        print(f"  {feat_name:<10s} vs CCS1: rho = {rho:+.4f}")

    # Ablation channel correlations
    for abl_name in ABLATION_NAMES:
        abl_values = []
        for af in a2_folios:
            abl = per_folio_abl.get(af['folio'])
            if abl:
                abl_values.append(abl['ablations'][abl_name]['delta_m4f_dye'])
            else:
                abl_values.append(0.0)
        rho = spearman_rho(abl_values, ccs1_values)
        feature_correlations[f'abl_{abl_name}'] = round(rho, 4)
        print(f"  abl_{abl_name:<20s} vs CCS1: rho = {rho:+.4f}")

    # ================================================================
    # 7. Sub-profile test
    # ================================================================
    print("\n--- Sub-profile test ---")

    # Test if A2 should be split by conformity class
    conformity_groups = {}
    for cs in conformity_scores:
        c = cs['conformity']
        conformity_groups.setdefault(c, []).append(cs['ccs1'])

    print("  CCS1 by conformity class:")
    for c in sorted(conformity_groups):
        vals = conformity_groups[c]
        mean_v = sum(vals) / len(vals)
        print(f"    {c:<20s} n={len(vals):3d}  mean_CCS1={mean_v:.4f}")

    # Test if section explains within-A2 variance
    section_ccs1 = {}
    for af in a2_folios:
        s = af['section']
        section_ccs1.setdefault(s, []).append(af['ccs1'])

    # Simple between-group / within-group variance ratio
    overall_mean = sum(ccs1_values) / len(ccs1_values) if ccs1_values else 0
    between_var = sum(len(vals) * (sum(vals)/len(vals) - overall_mean) ** 2
                      for vals in section_ccs1.values()) / len(ccs1_values) if ccs1_values else 0
    within_var = sum(sum((v - sum(vals)/len(vals)) ** 2 for v in vals)
                     for vals in section_ccs1.values()) / len(ccs1_values) if ccs1_values else 1
    f_ratio = between_var / within_var if within_var > 1e-10 else 0

    print(f"\n  Section explains within-A2 CCS1 variance:")
    print(f"    Between-section variance: {between_var:.6f}")
    print(f"    Within-section variance:  {within_var:.6f}")
    print(f"    F-ratio: {f_ratio:.4f} ({'significant' if f_ratio > 3 else 'not significant'})")

    # ================================================================
    # Write output
    # ================================================================
    os.makedirs(RESULTS_DIR, exist_ok=True)

    output = {
        'metadata': {
            'phase': '573',
            'script': 't4_a2_folio_decomposition.py',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'n_a2_folios': len(a2_folios),
            'elapsed_seconds': round(time.time() - t_start, 2),
        },
        'a2_ranking': [{k: v for k, v in af.items()} for af in a2_folios],
        'section_stratification': section_stats,
        'conformity_scores': conformity_scores,
        'conformity_distribution': conformity_counts,
        'amplification_scores': amplification_scores,
        'gap_analysis': gap_analysis,
        'feature_ccs1_correlations': feature_correlations,
        'sub_profile_test': {
            'section_f_ratio': round(f_ratio, 4),
            'section_significant': f_ratio > 3,
            'conformity_groups': {c: {'n': len(vals), 'mean_ccs1': round(sum(vals)/len(vals), 4)}
                                  for c, vals in conformity_groups.items()},
        },
    }

    out_path = os.path.join(RESULTS_DIR, 't4_a2_decomposition.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=1)

    print(f"\n  Output: {out_path}")
    print(f"  Size: {os.path.getsize(out_path):,} bytes")
    print(f"\n  Total time: {time.time() - t_start:.1f}s")
    print("  DONE")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
