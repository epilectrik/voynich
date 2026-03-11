"""
T4: Continuous Landscape Model + Folio Classification
Phase 574 - COUNTERFEIT_CLOSURE_THRESHOLD_RECOVERY_GATE_MAP

Reinterprets folio accent and design freedom as distance from the
counterfeit-closure threshold.

Four parts:
  Part 1 - Per-folio distance to threshold surface
  Part 2 - Three-way classification (descriptive convenience overlays)
  Part 3 - Design freedom unification (F-axis correlations)
  Part 4 - Folio accent vector
"""

import json
import sys
import os
import math
import time
from pathlib import Path
from datetime import datetime, timezone
from collections import defaultdict, Counter

PROJECT_ROOT = str(Path(__file__).resolve().parents[3])
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

RESULTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'results')


def spearman_rank(x, y):
    """Pure-Python Spearman rank correlation."""
    n = len(x)
    if n < 3:
        return 0.0

    def rank_data(vals):
        indexed = sorted(range(n), key=lambda i: vals[i])
        ranks = [0.0] * n
        i = 0
        while i < n:
            j = i
            while j < n - 1 and vals[indexed[j]] == vals[indexed[j + 1]]:
                j += 1
            mean_rank = (i + j) / 2.0 + 1.0
            for k_idx in range(i, j + 1):
                ranks[indexed[k_idx]] = mean_rank
            i = j + 1
        return ranks

    rx = rank_data(x)
    ry = rank_data(y)

    mean_rx = sum(rx) / n
    mean_ry = sum(ry) / n

    num = sum((rx[i] - mean_rx) * (ry[i] - mean_ry) for i in range(n))
    den_x = sum((rx[i] - mean_rx) ** 2 for i in range(n))
    den_y = sum((ry[i] - mean_ry) ** 2 for i in range(n))

    den = math.sqrt(den_x * den_y)
    if den < 1e-12:
        return 0.0
    return num / den


def kruskal_wallis(groups):
    """Pure-Python Kruskal-Wallis H test. Returns (H, k_groups)."""
    all_vals = []
    for g_idx, g in enumerate(groups):
        for v in g:
            all_vals.append((v, g_idx))

    n_total = len(all_vals)
    if n_total < 3:
        return (0.0, len(groups))

    # Rank all values
    sorted_vals = sorted(range(n_total), key=lambda i: all_vals[i][0])
    ranks = [0.0] * n_total
    i = 0
    while i < n_total:
        j = i
        while j < n_total - 1 and all_vals[sorted_vals[j]][0] == all_vals[sorted_vals[j + 1]][0]:
            j += 1
        mean_rank = (i + j) / 2.0 + 1.0
        for ki in range(i, j + 1):
            ranks[sorted_vals[ki]] = mean_rank
        i = j + 1

    # Compute group rank sums
    group_rank_sums = defaultdict(float)
    group_counts = defaultdict(int)
    for idx in range(n_total):
        g_idx = all_vals[idx][1]
        group_rank_sums[g_idx] += ranks[idx]
        group_counts[g_idx] += 1

    # H statistic
    h = 0.0
    for g_idx in group_counts:
        ni = group_counts[g_idx]
        ri = group_rank_sums[g_idx]
        if ni > 0:
            h += (ri ** 2) / ni

    h = (12.0 / (n_total * (n_total + 1))) * h - 3.0 * (n_total + 1)
    return (round(h, 4), len(groups))


def main():
    t_start = time.time()
    print("=" * 70)
    print("T4: Continuous Landscape Model")
    print("Phase 574 - COUNTERFEIT_CLOSURE_THRESHOLD_RECOVERY_GATE_MAP")
    print("=" * 70)

    # ---- Load data ----
    print("\n--- Loading data ---")

    t0_path = os.path.join(RESULTS_DIR, 't0_event_feature_assembly.json')
    with open(t0_path, 'r', encoding='utf-8') as f:
        t0 = json.load(f)
    events = t0['m1_events']
    per_folio_summary = t0['per_folio_summary']

    t1_path = os.path.join(RESULTS_DIR, 't1_recovery_gate_decomposition.json')
    with open(t1_path, 'r', encoding='utf-8') as f:
        t1 = json.load(f)
    per_folio_sub_abl = t1['per_folio_sub_ablation']

    t2_path = os.path.join(RESULTS_DIR, 't2_counterfeit_threshold.json')
    with open(t2_path, 'r', encoding='utf-8') as f:
        t2 = json.load(f)
    threshold_estimates = t2['threshold_estimates']

    print(f"  Events: {len(events)}")
    print(f"  Folios with events: {len([f for f in per_folio_summary if per_folio_summary[f].get('n_events', 0) > 0])}")

    # Group events by folio
    folio_events = defaultdict(list)
    for ev in events:
        folio_events[ev['folio']].append(ev)

    profiles = sorted(set(e['profile'] for e in events))

    # ================================================================
    # PART 1: Per-folio distance to threshold surface
    # ================================================================
    print("\n--- Part 1: Per-folio distance to threshold ---")
    per_folio_landscape = {}

    for folio, summary in per_folio_summary.items():
        n_events = summary.get('n_events', 0)
        if n_events == 0:
            continue

        evts = folio_events.get(folio, [])
        if not evts:
            continue

        profile = summary['profile']
        section = summary['section']

        # Weighted mean DYE_adv, weighted by CTS (emphasizes high-CTS events)
        total_cts_w = sum(max(e['CTS'], 0.01) for e in evts)
        if total_cts_w > 0:
            margin = sum(e['DYE_adv_event'] * max(e['CTS'], 0.01) for e in evts) / total_cts_w
        else:
            margin = sum(e['DYE_adv_event'] for e in evts) / len(evts)

        # SD of per-event DYE_adv
        if len(evts) > 1:
            mean_adv = sum(e['DYE_adv_event'] for e in evts) / len(evts)
            margin_sd = math.sqrt(sum((e['DYE_adv_event'] - mean_adv) ** 2
                                       for e in evts) / (len(evts) - 1))
        else:
            margin_sd = 0.0

        # CTS vs threshold
        profile_threshold = threshold_estimates.get(profile, {}).get(
            'cts_threshold_magnitude', 0.5)
        if profile_threshold is None:
            profile_threshold = 0.5
        folio_mean_cts = summary.get('mean_CTS', 0.0)
        cts_vs_threshold = folio_mean_cts - profile_threshold

        # Positive event fraction
        n_pos = sum(1 for e in evts if e['DYE_adv_event'] > 0)
        positive_event_fraction = n_pos / len(evts)

        per_folio_landscape[folio] = {
            'margin': round(margin, 6),
            'margin_sd': round(margin_sd, 6),
            'cts_vs_threshold': round(cts_vs_threshold, 4),
            'positive_event_fraction': round(positive_event_fraction, 4),
            'n_events': n_events,
            'profile': profile,
            'section': section,
            'mean_CTS': round(folio_mean_cts, 4),
        }

    # Compute z-scores
    all_margins = [v['margin'] for v in per_folio_landscape.values()]
    global_mean = sum(all_margins) / len(all_margins) if all_margins else 0.0
    if len(all_margins) > 1:
        global_sd = math.sqrt(sum((m - global_mean) ** 2 for m in all_margins) /
                              (len(all_margins) - 1))
    else:
        global_sd = 1.0

    for folio, fl in per_folio_landscape.items():
        z = (fl['margin'] - global_mean) / max(global_sd, 1e-12)
        fl['z_margin'] = round(z, 4)

    print(f"  Folios in landscape: {len(per_folio_landscape)}")
    print(f"  Global margin mean: {global_mean:.4f}, sd: {global_sd:.4f}")

    # ================================================================
    # PART 2: Three-way classification (descriptive convenience overlays)
    # ================================================================
    print("\n--- Part 2: Three-way classification ---")
    print("  NOTE: These are descriptive convenience overlays on a continuous")
    print("  surface, NOT ontological folio species.")

    for folio, fl in per_folio_landscape.items():
        z = fl['z_margin']
        pef = fl['positive_event_fraction']

        if z > 0.5 and pef > 0.75:
            fl['classification'] = 'STABLE_AMPLIFIER'
        elif z < -0.5 and pef < 0.40:
            fl['classification'] = 'FORGIVING_RECIRCULATOR'
        else:
            fl['classification'] = 'THRESHOLD_DEPENDENT'

    # Cross-tabulation: profile x classification
    profile_x_classification = {}
    for profile in profiles:
        profile_x_classification[profile] = Counter()
    for fl in per_folio_landscape.values():
        profile_x_classification[fl['profile']][fl['classification']] += 1

    # Convert Counters to dicts
    for p in profile_x_classification:
        profile_x_classification[p] = dict(profile_x_classification[p])

    # Classification summary
    classification_summary = {}
    for cls in ['STABLE_AMPLIFIER', 'THRESHOLD_DEPENDENT', 'FORGIVING_RECIRCULATOR']:
        cls_folios = [fl for fl in per_folio_landscape.values()
                      if fl['classification'] == cls]
        n = len(cls_folios)
        if n == 0:
            classification_summary[cls] = {'n_folios': 0}
            continue

        prof_dist = Counter(fl['profile'] for fl in cls_folios)
        sect_dist = Counter(fl['section'] for fl in cls_folios)
        classification_summary[cls] = {
            'n_folios': n,
            'profile_distribution': dict(prof_dist),
            'section_distribution': dict(sect_dist),
            'mean_margin': round(sum(fl['margin'] for fl in cls_folios) / n, 6),
            'mean_z_margin': round(sum(fl['z_margin'] for fl in cls_folios) / n, 4),
        }

    # Print
    for cls, cs in classification_summary.items():
        print(f"  {cls}: n={cs['n_folios']}")
        if cs['n_folios'] > 0:
            print(f"    profiles: {cs.get('profile_distribution', {})}")

    print(f"\n  Profile x Classification:")
    for p in sorted(profile_x_classification.keys()):
        print(f"    {p}: {profile_x_classification[p]}")

    # ================================================================
    # PART 3: Design freedom unification
    # ================================================================
    print("\n--- Part 3: Design freedom unification ---")
    accent_correlations = {}

    # Get folio-level F-params from events (first event per folio)
    folio_params = {}
    for ev in events:
        if ev['folio'] not in folio_params:
            folio_params[ev['folio']] = {
                'F1': ev['F1'], 'F2': ev['F2'], 'F3': ev['F3'],
                'F4_raw': ev['F4_raw'], 'F5': ev['F5'],
            }

    active_folios = [f for f in per_folio_landscape
                     if f in folio_params]

    # F-axis correlations with margin
    margins = [per_folio_landscape[f]['margin'] for f in active_folios]

    for f_axis in ['F1', 'F2', 'F3', 'F4_raw', 'F5']:
        f_vals = [folio_params[f][f_axis] for f in active_folios]
        rho = spearman_rank(margins, f_vals)
        accent_correlations[f'margin_vs_{f_axis}'] = {
            'rho': round(rho, 4),
            'n': len(active_folios),
        }
        print(f"  margin vs {f_axis}: rho={rho:.4f}")

    # Sub-R sensitivity correlations with F-axes
    design_freedom_links = {}
    a2_folios = [f for f in active_folios
                 if per_folio_landscape[f]['profile'] == 'A2_SEALED_RECIRCULATION'
                 and f in per_folio_sub_abl]

    if len(a2_folios) >= 5:
        for f_axis in ['F1', 'F2', 'F5']:
            f_vals = [folio_params[f][f_axis] for f in a2_folios]
            design_freedom_links[f_axis] = {}

            for sa in ['NO_R1_C_ONLY', 'NO_R4_C_ONLY']:
                sa_vals = [per_folio_sub_abl[f]['sub_ablations'].get(sa, {}).get(
                    'delta_m4f_dye', 0) for f in a2_folios]
                rho = spearman_rank(f_vals, sa_vals)
                design_freedom_links[f_axis][sa] = {
                    'rho': round(rho, 4),
                    'n': len(a2_folios),
                }

            # Correlation with margin
            marg = [per_folio_landscape[f]['margin'] for f in a2_folios]
            rho_m = spearman_rank(f_vals, marg)
            design_freedom_links[f_axis]['corr_with_margin'] = round(rho_m, 4)
            print(f"  A2 {f_axis} vs margin: rho={rho_m:.4f}")

    # CCS1 correlation
    ccs1_vals = []
    margin_vals = []
    for f in active_folios:
        evts = folio_events.get(f, [])
        if evts:
            ccs1_vals.append(evts[0]['CCS1_folio'])
            margin_vals.append(per_folio_landscape[f]['margin'])
    if len(ccs1_vals) >= 5:
        rho = spearman_rank(ccs1_vals, margin_vals)
        accent_correlations['margin_vs_CCS1'] = {'rho': round(rho, 4), 'n': len(ccs1_vals)}
        print(f"  margin vs CCS1: rho={rho:.4f}")

    # NO_CLOSE_RECOVERY delta correlation
    no_cr_vals = []
    margin_cr = []
    for f in active_folios:
        evts = folio_events.get(f, [])
        if evts:
            no_cr_vals.append(evts[0].get('abl_NO_CLOSE_RECOVERY', 0))
            margin_cr.append(per_folio_landscape[f]['margin'])
    if len(no_cr_vals) >= 5:
        rho = spearman_rank(no_cr_vals, margin_cr)
        accent_correlations['margin_vs_NO_CR'] = {'rho': round(rho, 4), 'n': len(no_cr_vals)}
        print(f"  margin vs NO_CR: rho={rho:.4f}")

    # Kruskal-Wallis by profile and section
    profile_groups = defaultdict(list)
    section_groups = defaultdict(list)
    for f in active_folios:
        fl = per_folio_landscape[f]
        profile_groups[fl['profile']].append(fl['margin'])
        section_groups[fl['section']].append(fl['margin'])

    if len(profile_groups) >= 2:
        h, k = kruskal_wallis(list(profile_groups.values()))
        accent_correlations['kw_margin_by_profile'] = {'H': h, 'k': k}
        print(f"  Kruskal-Wallis margin by profile: H={h:.4f}")

    if len(section_groups) >= 2:
        h, k = kruskal_wallis(list(section_groups.values()))
        accent_correlations['kw_margin_by_section'] = {'H': h, 'k': k}
        print(f"  Kruskal-Wallis margin by section: H={h:.4f}")

    # ================================================================
    # PART 4: Folio accent vector
    # ================================================================
    print("\n--- Part 4: Folio accent vector ---")
    # Build accent vectors and compute profile centroids
    accent_dimensions = ['margin', 'cts_vs_threshold', 'mean_CTS']

    profile_centroids = {}
    for profile in profiles:
        pf = [per_folio_landscape[f] for f in per_folio_landscape
              if per_folio_landscape[f]['profile'] == profile]
        if not pf:
            continue
        centroid = {}
        for dim in accent_dimensions:
            centroid[dim] = sum(fl[dim] for fl in pf) / len(pf)
        profile_centroids[profile] = centroid

    # Compute distances from each folio to profile centroids
    for folio, fl in per_folio_landscape.items():
        distances = {}
        for profile, centroid in profile_centroids.items():
            dist = math.sqrt(sum((fl[dim] - centroid[dim]) ** 2
                                  for dim in accent_dimensions))
            distances[profile] = round(dist, 4)
        fl['centroid_distances'] = distances

    # Does three-way classification cross-cut profile assignment?
    cross_cut_score = 0
    total_classified = 0
    for folio, fl in per_folio_landscape.items():
        if fl['classification'] != 'THRESHOLD_DEPENDENT':
            total_classified += 1
            # Check if nearest centroid profile != actual profile
            if fl['centroid_distances']:
                nearest = min(fl['centroid_distances'].items(), key=lambda x: x[1])
                if nearest[0] != fl['profile']:
                    cross_cut_score += 1

    cross_cut_fraction = cross_cut_score / max(total_classified, 1)
    print(f"  Cross-cut fraction: {cross_cut_fraction:.4f} "
          f"({cross_cut_score}/{total_classified})")

    # ================================================================
    # Save output
    # ================================================================
    print("\n--- Saving output ---")
    os.makedirs(RESULTS_DIR, exist_ok=True)

    output = {
        'metadata': {
            'phase': '574',
            'script': 't4_landscape_model.py',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'elapsed_seconds': round(time.time() - t_start, 2),
            'n_folios': len(per_folio_landscape),
            'global_margin_mean': round(global_mean, 6),
            'global_margin_sd': round(global_sd, 6),
            'classification_note': 'Three-way classification is a DESCRIPTIVE CONVENIENCE OVERLAY on a continuous surface, NOT ontological folio species',
        },
        'per_folio_landscape': per_folio_landscape,
        'classification_summary': classification_summary,
        'profile_x_classification': profile_x_classification,
        'accent_correlations': accent_correlations,
        'design_freedom_links': design_freedom_links,
        'profile_centroids': {p: {k: round(v, 4) for k, v in c.items()}
                              for p, c in profile_centroids.items()},
        'cross_cut_fraction': round(cross_cut_fraction, 4),
    }

    out_path = os.path.join(RESULTS_DIR, 't4_landscape_model.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=1, default=str)
    print(f"  Written: {out_path}")
    print(f"  Size: {os.path.getsize(out_path):,} bytes")
    print(f"\nDone in {time.time() - t_start:.1f}s")


if __name__ == '__main__':
    main()
