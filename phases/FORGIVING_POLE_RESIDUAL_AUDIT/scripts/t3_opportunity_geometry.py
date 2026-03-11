"""
Phase 579 T3: Opportunity Geometry

Tests whether forgivingness is an artifact of low event counts, poor CTS,
bad spacing, or weak morphological features. Feeds C1665.

No new simulation - pure data analysis on existing results.
"""

import json, time, math
from pathlib import Path
from collections import Counter

t_start = time.time()

BASE = Path('.')
PHASE_DIR = BASE / 'phases' / 'FORGIVING_POLE_RESIDUAL_AUDIT'
RESULTS_DIR = PHASE_DIR / 'results'

# Load T0
print("Loading T0 census...")
with open(RESULTS_DIR / 't0_pole_census.json') as f:
    t0 = json.load(f)

cards = t0['profile_cards']
passing = t0['passing_a2_data']
STUBBORN_8 = t0['metadata']['stubborn_folios']
PASSING_A2 = t0['metadata']['passing_a2_folios']

# Load Phase 574 events
print("Loading Phase 574 events...")
with open(BASE / 'phases/COUNTERFEIT_CLOSURE_THRESHOLD_RECOVERY_GATE_MAP/results/t0_event_feature_assembly.json') as f:
    event_assembly = json.load(f)

# Load Phase 572 M4f null runs for per-permutation DYE variance
print("Loading Phase 573 ablation (for CCS1)...")
with open(BASE / 'phases/A2_FORGIVINGNESS_MECHANISM_APPARATUS_FAMILIES/results/t1_mechanism_ablation.json') as f:
    ablation = json.load(f)
per_folio_abl = ablation['per_folio']

# Build events by folio (A2 only)
all_a2 = STUBBORN_8 + PASSING_A2
events_by_folio = {}
for ev in event_assembly['m1_events']:
    if ev['folio'] in all_a2:
        events_by_folio.setdefault(ev['folio'], []).append(ev)


def mann_whitney_u(group1, group2):
    n1, n2 = len(group1), len(group2)
    if n1 == 0 or n2 == 0:
        return {'U': 0, 'p_approx': 1.0, 'rank_biserial': 0.0}
    combined = [(v, 0) for v in group1] + [(v, 1) for v in group2]
    combined.sort(key=lambda x: x[0])
    ranks = [0.0] * len(combined)
    i = 0
    while i < len(combined):
        j = i
        while j < len(combined) and combined[j][0] == combined[i][0]:
            j += 1
        avg_rank = (i + j + 1) / 2.0
        for k in range(i, j):
            ranks[k] = avg_rank
        i = j
    R1 = sum(ranks[k] for k in range(len(combined)) if combined[k][1] == 0)
    U1 = R1 - n1 * (n1 + 1) / 2
    U2 = n1 * n2 - U1
    U = min(U1, U2)
    mu = n1 * n2 / 2
    sigma = math.sqrt(n1 * n2 * (n1 + n2 + 1) / 12)
    z = (U - mu) / sigma if sigma > 0 else 0
    p = 2 * (1 - 0.5 * (1 + math.erf(abs(z) / math.sqrt(2))))
    rbc = 1 - (2 * U) / (n1 * n2) if n1 * n2 > 0 else 0
    return {'U': round(U, 2), 'p_approx': round(p, 6), 'rank_biserial': round(rbc, 4)}


def spearman_rho(x, y):
    n = len(x)
    if n < 3:
        return 0.0
    def rank_data(data):
        indexed = sorted(range(n), key=lambda i: data[i])
        ranks = [0.0] * n
        i = 0
        while i < n:
            j = i
            while j < n and data[indexed[j]] == data[indexed[i]]:
                j += 1
            avg = (i + j + 1) / 2.0
            for k in range(i, j):
                ranks[indexed[k]] = avg
            i = j
        return ranks
    rx = rank_data(x)
    ry = rank_data(y)
    d2 = sum((rx[i] - ry[i])**2 for i in range(n))
    rho = 1 - 6 * d2 / (n * (n * n - 1))
    return round(rho, 4)


# -- Step 1: Event count effect --
print("\n-- Step 1: Event count effect --")

fg_counts = [len(events_by_folio.get(f, [])) for f in STUBBORN_8]
pg_counts = [len(events_by_folio.get(f, [])) for f in PASSING_A2]
count_test = mann_whitney_u(fg_counts, pg_counts)

fg_mean_count = sum(fg_counts) / len(fg_counts)
pg_mean_count = sum(pg_counts) / len(pg_counts)
print(f"  Forgiving event counts: {fg_counts}, mean={fg_mean_count:.1f}")
print(f"  Passing event counts: {pg_counts}, mean={pg_mean_count:.1f}")
print(f"  MW test: p={count_test['p_approx']:.4f}, rbc={count_test['rank_biserial']:.3f}")

# -- Step 2: CTS distribution --
print("\n-- Step 2: CTS distribution --")

fg_cts = []
pg_cts = []
for f in STUBBORN_8:
    for ev in events_by_folio.get(f, []):
        fg_cts.append(ev['CTS'])
for f in PASSING_A2:
    for ev in events_by_folio.get(f, []):
        pg_cts.append(ev['CTS'])

fg_mean_cts = sum(fg_cts) / len(fg_cts) if fg_cts else 0
pg_mean_cts = sum(pg_cts) / len(pg_cts) if pg_cts else 0
cts_test = mann_whitney_u(fg_cts, pg_cts)

print(f"  Forgiving CTS: n={len(fg_cts)}, mean={fg_mean_cts:.4f}")
print(f"  Passing CTS: n={len(pg_cts)}, mean={pg_mean_cts:.4f}")
print(f"  MW test: p={cts_test['p_approx']:.4f}")

# Per-folio mean CTS
fg_folio_cts = [cards[f]['mean_CTS'] for f in STUBBORN_8]
pg_folio_cts = []
for f in PASSING_A2:
    evs = events_by_folio.get(f, [])
    pg_folio_cts.append(sum(ev['CTS'] for ev in evs) / len(evs) if evs else 0)
folio_cts_test = mann_whitney_u(fg_folio_cts, pg_folio_cts)
print(f"  Per-folio mean CTS: forgiving={sum(fg_folio_cts)/len(fg_folio_cts):.4f}, "
      f"passing={sum(pg_folio_cts)/len(pg_folio_cts):.4f}, p={folio_cts_test['p_approx']:.4f}")

# -- Step 3: Event spacing --
print("\n-- Step 3: Event spacing --")

fg_wp = sum(1 for f in STUBBORN_8 for ev in events_by_folio.get(f, []) if ev.get('work_preceded', False))
fg_total = sum(len(events_by_folio.get(f, [])) for f in STUBBORN_8)
pg_wp = sum(1 for f in PASSING_A2 for ev in events_by_folio.get(f, []) if ev.get('work_preceded', False))
pg_total = sum(len(events_by_folio.get(f, [])) for f in PASSING_A2)

fg_wp_frac = fg_wp / fg_total if fg_total > 0 else 0
pg_wp_frac = pg_wp / pg_total if pg_total > 0 else 0
print(f"  Work-preceded: forgiving={fg_wp}/{fg_total} ({fg_wp_frac:.1%}), "
      f"passing={pg_wp}/{pg_total} ({pg_wp_frac:.1%})")

fg_dem = sum(1 for f in STUBBORN_8 for ev in events_by_folio.get(f, []) if ev.get('demanded', False))
pg_dem = sum(1 for f in PASSING_A2 for ev in events_by_folio.get(f, []) if ev.get('demanded', False))
fg_dem_frac = fg_dem / fg_total if fg_total > 0 else 0
pg_dem_frac = pg_dem / pg_total if pg_total > 0 else 0
print(f"  Demanded: forgiving={fg_dem}/{fg_total} ({fg_dem_frac:.1%}), "
      f"passing={pg_dem}/{pg_total} ({pg_dem_frac:.1%})")

# -- Step 4: Morphological features --
print("\n-- Step 4: Morphological features --")

morph_features = ['headless_involved', 'has_e_head_support', 'E_cts50', 'E_mcb', 'E_opaque', 'E_armed']
fg_events_all = [ev for f in STUBBORN_8 for ev in events_by_folio.get(f, [])]
pg_events_all = [ev for f in PASSING_A2 for ev in events_by_folio.get(f, [])]

morph_comparison = {}
for feat in morph_features:
    fg_pos = sum(1 for ev in fg_events_all if ev.get(feat, False))
    pg_pos = sum(1 for ev in pg_events_all if ev.get(feat, False))
    fg_rate = fg_pos / len(fg_events_all) if fg_events_all else 0
    pg_rate = pg_pos / len(pg_events_all) if pg_events_all else 0
    morph_comparison[feat] = {
        'forgiving_rate': round(fg_rate, 4),
        'passing_rate': round(pg_rate, 4),
        'delta': round(fg_rate - pg_rate, 4),
    }
    print(f"  {feat}: forgiving={fg_rate:.1%}, passing={pg_rate:.1%}")

# Grammar band distribution
fg_bands = Counter(ev['grammar_band'] for ev in fg_events_all)
pg_bands = Counter(ev['grammar_band'] for ev in pg_events_all)
print(f"  Grammar bands forgiving: {dict(fg_bands)}")
print(f"  Grammar bands passing: {dict(pg_bands)}")

# -- Step 5: Confound analysis --
print("\n-- Step 5: Confound analysis --")

# R-squared of event count on CCS1 within all A2
all_counts = [len(events_by_folio.get(f, [])) for f in all_a2]
all_ccs1 = [per_folio_abl[f]['baseline_m4f_dye'] for f in all_a2]

# Simple linear regression: CCS1 = a + b * event_count
n = len(all_a2)
x_mean = sum(all_counts) / n
y_mean = sum(all_ccs1) / n
ss_xy = sum((all_counts[i] - x_mean) * (all_ccs1[i] - y_mean) for i in range(n))
ss_xx = sum((all_counts[i] - x_mean)**2 for i in range(n))
ss_yy = sum((all_ccs1[i] - y_mean)**2 for i in range(n))

if ss_xx > 0 and ss_yy > 0:
    r = ss_xy / math.sqrt(ss_xx * ss_yy)
    r_squared = r * r
else:
    r = 0
    r_squared = 0

rho_count_ccs1 = spearman_rho(all_counts, all_ccs1)

print(f"  Event count vs CCS1 (within A2, n={n}):")
print(f"    Pearson r={r:.4f}, R-sq={r_squared:.4f}")
print(f"    Spearman rho={rho_count_ccs1}")

# -- Step 6: Strong-close opportunity (expert revision) --
print("\n-- Step 6: Strong-close opportunity --")

strong_opp = {}
for folio in all_a2:
    evs = events_by_folio.get(folio, [])
    n_events = len(evs)
    n_strong = sum(1 for ev in evs if ev.get('n_strong_signals', 0) >= 3)
    n_medium = sum(1 for ev in evs if 1 <= ev.get('n_strong_signals', 0) < 3)
    n_weak = n_events - n_strong - n_medium
    mean_cts = sum(ev['CTS'] for ev in evs) / n_events if n_events > 0 else 0
    strong_frac = n_strong / n_events if n_events > 0 else 0
    strong_opp[folio] = {
        'n_events': n_events,
        'n_strong': n_strong,
        'n_medium': n_medium,
        'n_weak': n_weak,
        'strong_frac': round(strong_frac, 4),
        'mean_cts': round(mean_cts, 4),
    }

fg_strong_fracs = [strong_opp[f]['strong_frac'] for f in STUBBORN_8]
pg_strong_fracs = [strong_opp[f]['strong_frac'] for f in PASSING_A2]
strong_test = mann_whitney_u(fg_strong_fracs, pg_strong_fracs)

fg_n_strong = [strong_opp[f]['n_strong'] for f in STUBBORN_8]
pg_n_strong = [strong_opp[f]['n_strong'] for f in PASSING_A2]

print(f"  Strong-close fraction: forgiving mean={sum(fg_strong_fracs)/len(fg_strong_fracs):.3f}, "
      f"passing mean={sum(pg_strong_fracs)/len(pg_strong_fracs):.3f}, "
      f"MW p={strong_test['p_approx']:.4f}")
print(f"  Strong-close count: forgiving={fg_n_strong}, passing={pg_n_strong}")

# -- Step 7: Opportunity-adjusted forgivingness --
print("\n-- Step 7: Opportunity-adjusted forgivingness --")

# CCS1 normalized by event count
fg_ccs1_per_event = []
pg_ccs1_per_event = []
for f in STUBBORN_8:
    n_ev = len(events_by_folio.get(f, []))
    ccs1 = per_folio_abl[f]['baseline_m4f_dye']
    fg_ccs1_per_event.append(ccs1 / n_ev if n_ev > 0 else 0)
for f in PASSING_A2:
    n_ev = len(events_by_folio.get(f, []))
    ccs1 = per_folio_abl[f]['baseline_m4f_dye']
    pg_ccs1_per_event.append(ccs1 / n_ev if n_ev > 0 else 0)

adj_test = mann_whitney_u(fg_ccs1_per_event, pg_ccs1_per_event)
print(f"  CCS1/event: forgiving mean={sum(fg_ccs1_per_event)/len(fg_ccs1_per_event):.4f}, "
      f"passing mean={sum(pg_ccs1_per_event)/len(pg_ccs1_per_event):.4f}, "
      f"MW p={adj_test['p_approx']:.4f}")

# -- Step 8: Sparse-event volatility stratification --
print("\n-- Step 8: Sparse-event stratification --")

sparse_fg = [f for f in STUBBORN_8 if len(events_by_folio.get(f, [])) <= 3]
dense_fg = [f for f in STUBBORN_8 if len(events_by_folio.get(f, [])) > 3]

print(f"  Sparse forgiving (1-3 events): {sparse_fg} (n={len(sparse_fg)})")
print(f"  Dense forgiving (4+ events): {dense_fg} (n={len(dense_fg)})")

sparse_ccs1 = [per_folio_abl[f]['baseline_m4f_dye'] for f in sparse_fg]
dense_ccs1 = [per_folio_abl[f]['baseline_m4f_dye'] for f in dense_fg]
print(f"  Sparse CCS1: mean={sum(sparse_ccs1)/len(sparse_ccs1):.4f}" if sparse_ccs1 else "  Sparse: none")
print(f"  Dense CCS1: mean={sum(dense_ccs1)/len(dense_ccs1):.4f}" if dense_ccs1 else "  Dense: none")

sparse_gaps = [cards[f]['gap_to_passing'] for f in sparse_fg]
dense_gaps = [cards[f]['gap_to_passing'] for f in dense_fg]
print(f"  Sparse gaps: {[round(g,3) for g in sparse_gaps]}")
print(f"  Dense gaps: {[round(g,3) for g in dense_gaps]}")

# -- C1665 Assessment --
print("\n-- C1665 Assessment --")

if r_squared > 0.70:
    opp_verdict = 'OPPORTUNITY_DOMINATED'
elif r_squared > 0.30:
    opp_verdict = 'OPPORTUNITY_CONTRIBUTING'
else:
    opp_verdict = 'OPPORTUNITY_NEUTRAL'

print(f"  Event count -> CCS1 R-sq = {r_squared:.4f}")
print(f"  -> C1665 verdict: {opp_verdict}")

# -- Save results --

results = {
    'metadata': {
        'phase': 579,
        'script': 't3_opportunity_geometry',
        'runtime_s': round(time.time() - t_start, 2),
    },
    'event_count_analysis': {
        'forgiving_counts': fg_counts,
        'passing_counts': pg_counts,
        'mann_whitney': count_test,
    },
    'cts_analysis': {
        'forgiving_event_mean_cts': round(fg_mean_cts, 4),
        'passing_event_mean_cts': round(pg_mean_cts, 4),
        'event_level_test': cts_test,
        'folio_level_test': folio_cts_test,
    },
    'spacing_analysis': {
        'forgiving_work_preceded_frac': round(fg_wp_frac, 4),
        'passing_work_preceded_frac': round(pg_wp_frac, 4),
        'forgiving_demanded_frac': round(fg_dem_frac, 4),
        'passing_demanded_frac': round(pg_dem_frac, 4),
    },
    'morphological_comparison': morph_comparison,
    'grammar_bands': {
        'forgiving': dict(fg_bands),
        'passing': dict(pg_bands),
    },
    'confound_analysis': {
        'event_count_vs_ccs1_pearson_r': round(r, 4),
        'event_count_vs_ccs1_r_squared': round(r_squared, 4),
        'event_count_vs_ccs1_spearman_rho': rho_count_ccs1,
    },
    'strong_close_opportunity': {
        'per_folio': {f: strong_opp[f] for f in all_a2},
        'mann_whitney_strong_frac': strong_test,
    },
    'opportunity_adjusted': {
        'ccs1_per_event_test': adj_test,
    },
    'sparse_stratification': {
        'sparse_folios': sparse_fg,
        'dense_folios': dense_fg,
        'sparse_ccs1_mean': round(sum(sparse_ccs1) / len(sparse_ccs1), 4) if sparse_ccs1 else 0,
        'dense_ccs1_mean': round(sum(dense_ccs1) / len(dense_ccs1), 4) if dense_ccs1 else 0,
    },
    'c1665_inputs': {
        'event_count_r_squared': round(r_squared, 4),
        'opportunity_verdict': opp_verdict,
    },
}

out_path = RESULTS_DIR / 't3_opportunity_geometry.json'
with open(out_path, 'w') as f:
    json.dump(results, f, indent=2)

elapsed = time.time() - t_start
print(f"\nT3 complete in {elapsed:.2f}s. Saved to {out_path}")
