"""
Phase 579 T0: Pole Census — Data Assembly + Statistical Characterization

Assembles comprehensive profile cards for the 8 stubborn A2 forgiving folios
by gathering all existing data from Phases 572-578. No new simulation.

Statistical tests: Mann-Whitney U, Kolmogorov-Smirnov, Fisher's exact, z-scores.
"""

import json, time, math
from pathlib import Path
from collections import Counter

t_start = time.time()

BASE = Path('.')
PHASE_DIR = BASE / 'phases' / 'FORGIVING_POLE_RESIDUAL_AUDIT'
RESULTS_DIR = PHASE_DIR / 'results'
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# The 8 stubborn A2 forgiving folios (from Phase 574 landscape, confirmed through 576-578)
STUBBORN_8 = ['f39v', 'f40r', 'f50v', 'f55v', 'f85r2', 'f86v5', 'f86v6', 'f95r2']

ABLATION_NAMES = ['NO_CROSS_COUPLING', 'NO_CLOSE_RECOVERY', 'NO_CONTAINMENT', 'NO_TR_TO_Y', 'NO_Y_SENSITIVITY']
SUB_ABLATION_NAMES = ['NO_R1', 'NO_R2', 'NO_R3', 'NO_R4', 'NO_R5', 'NO_R1_C_ONLY', 'NO_R4_C_ONLY']

# -- Load all data sources --

print("Loading Phase 572 setup...")
with open(BASE / 'phases/PRODUCTIVE_DISRUPTION_EXPANSION/results/t1_full_scale_setup.json') as f:
    setup = json.load(f)
folio_configs = setup['folio_configs']

print("Loading Phase 573 mechanism ablation...")
with open(BASE / 'phases/A2_FORGIVINGNESS_MECHANISM_APPARATUS_FAMILIES/results/t1_mechanism_ablation.json') as f:
    ablation = json.load(f)
per_folio_abl = ablation['per_folio']

print("Loading Phase 573 A2 decomposition...")
with open(BASE / 'phases/A2_FORGIVINGNESS_MECHANISM_APPARATUS_FAMILIES/results/t4_a2_decomposition.json') as f:
    a2_decomp = json.load(f)

print("Loading Phase 574 event features...")
with open(BASE / 'phases/COUNTERFEIT_CLOSURE_THRESHOLD_RECOVERY_GATE_MAP/results/t0_event_feature_assembly.json') as f:
    event_assembly = json.load(f)
all_events = event_assembly['m1_events']

print("Loading Phase 574 R1-R5 sub-ablation...")
with open(BASE / 'phases/COUNTERFEIT_CLOSURE_THRESHOLD_RECOVERY_GATE_MAP/results/t1_recovery_gate_decomposition.json') as f:
    sub_abl = json.load(f)
per_folio_sub = sub_abl['per_folio_sub_ablation']

print("Loading Phase 574 landscape...")
with open(BASE / 'phases/COUNTERFEIT_CLOSURE_THRESHOLD_RECOVERY_GATE_MAP/results/t4_landscape_model.json') as f:
    landscape_574 = json.load(f)

print("Loading Phase 576 gated simulation...")
with open(BASE / 'phases/CLOSURE_REGIME_ADMISSION_GATE/results/t2_admission_simulation.json') as f:
    sim_576 = json.load(f)

print("Loading Phase 576 gated landscape...")
with open(BASE / 'phases/CLOSURE_REGIME_ADMISSION_GATE/results/t4_landscape_remap.json') as f:
    landscape_576 = json.load(f)

# -- Build index structures --

# A2 ranking from Phase 573
a2_ranking = {r['folio']: r for r in a2_decomp['a2_ranking']}
gap_analysis = {r['folio']: r for r in a2_decomp['gap_analysis']}
conformity_scores = {r['folio']: r for r in a2_decomp['conformity_scores']}

# Events by folio
events_by_folio = {}
for ev in all_events:
    events_by_folio.setdefault(ev['folio'], []).append(ev)

# AMB_PESSIMISTIC config from Phase 576
amb_pess = sim_576['per_config']['REGIME_AMB_PESSIMISTIC']

# All A2 folios
all_a2_folios = [r['folio'] for r in a2_decomp['a2_ranking']]
passing_a2 = [f for f in all_a2_folios if f not in STUBBORN_8]

print(f"\nA2 folios: {len(all_a2_folios)} total, {len(STUBBORN_8)} forgiving, {len(passing_a2)} passing")

# -- Step 1: Build profile cards --

print("\n-- Step 1: Building profile cards --")

profile_cards = {}
for folio in STUBBORN_8:
    fc = folio_configs[folio]
    abl_data = per_folio_abl[folio]
    ranking = a2_ranking.get(folio, {})
    gap = gap_analysis.get(folio, {})
    conf = conformity_scores.get(folio, {})
    land_574 = landscape_574['per_folio_landscape'].get(folio, {})
    land_576 = landscape_576['per_folio_gated_landscape'].get(folio, {})
    gated = amb_pess.get(folio, {})
    sub_data = per_folio_sub.get(folio, {})
    folio_events = events_by_folio.get(folio, [])

    # F-parameters
    f_params = {
        'F1': fc['F1'], 'F2': fc['F2'], 'F3': fc['F3'],
        'F4_raw': fc['F4_raw'], 'F5': fc['F5']
    }

    # 5-channel ablation profile
    ablation_profile = {}
    for abl_name in ABLATION_NAMES:
        abl_entry = abl_data['ablations'][abl_name]
        ablation_profile[abl_name] = {
            'delta_m1_dye': abl_entry['delta_m1_dye'],
            'delta_m4f_dye': abl_entry['delta_m4f_dye'],
            'delta_dye_advantage': abl_entry['delta_dye_advantage'],
        }

    # R1-R5 sub-ablation profile
    sub_ablation_profile = {}
    if sub_data:
        for sub_name in SUB_ABLATION_NAMES:
            sub_entry = sub_data.get('sub_ablations', {}).get(sub_name, {})
            sub_ablation_profile[sub_name] = {
                'delta_m1_dye': sub_entry.get('delta_m1_dye', 0),
                'delta_m4f_dye': sub_entry.get('delta_m4f_dye', 0),
                'delta_dye_advantage': sub_entry.get('delta_dye_advantage', 0),
            }

    # Per-event features
    per_event_summary = []
    for ev in folio_events:
        per_event_summary.append({
            'line_key': ev['line_key'],
            'CTS': ev['CTS'],
            'DYE': ev['DYE'],
            'DYE_adv_event': ev['DYE_adv_event'],
            'n_strong_signals': ev['n_strong_signals'],
            'grammar_band': ev['grammar_band'],
            'headless_involved': ev.get('headless_involved', False),
            'has_e_head_support': ev.get('has_e_head_support', False),
            'E_cts50': ev.get('E_cts50', False),
            'E_mcb': ev.get('E_mcb', False),
            'E_opaque': ev.get('E_opaque', False),
            'E_armed': ev.get('E_armed', False),
            'demanded': ev.get('demanded', False),
            'work_preceded': ev.get('work_preceded', False),
            'dv_magnitude': ev.get('dv_magnitude', 0),
            'y_gain': ev.get('y_gain', 0),
        })

    # Grammar band distribution
    band_counts = Counter(ev['grammar_band'] for ev in folio_events)

    card = {
        'folio': folio,
        'section': fc.get('section', ''),
        'profile': fc.get('profile', 'A2_SEALED_RECIRCULATION'),
        'f_params': f_params,
        'n_close_events': len(folio_events),
        'n_work_preceded': sum(1 for ev in folio_events if ev.get('work_preceded', False)),
        'n_demanded': sum(1 for ev in folio_events if ev.get('demanded', False)),
        # Phase 573 metrics
        'ccs1': abl_data['baseline_m4f_dye'],
        'm1_dye': abl_data['baseline_m1_dye'],
        'dye_advantage': abl_data['baseline_m1_dye'] - abl_data['baseline_m4f_dye'],
        'crr_m1': abl_data.get('crr_m1', 0),
        'crr_m4f': abl_data.get('crr_m4f', 0),
        'nri_m1': abl_data.get('nri_m1', 0),
        'nri_m4f': abl_data.get('nri_m4f', 0),
        'epv': ranking.get('epv', 0),
        'gap_to_passing': gap.get('gap_to_passing', 0),
        'conformity': conf.get('conformity', ''),
        # Phase 574 landscape
        'ungated_margin': land_574.get('margin', 0),
        'ungated_z_margin': land_574.get('z_margin', 0),
        'ungated_classification': land_574.get('classification', ''),
        'mean_CTS': land_574.get('mean_CTS', 0),
        'positive_event_fraction': land_574.get('positive_event_fraction', 0),
        # Phase 576 gated
        'gated_m1_dye': gated.get('gated_m1_dye', 0),
        'gated_m4f_dye': gated.get('gated_m4f_dye', 0),
        'gated_advantage': gated.get('gated_advantage', 0),
        'gated_margin': land_576.get('gated_margin', 0),
        'gated_z_margin': land_576.get('gated_z_margin', 0),
        'gated_classification': land_576.get('gated_classification', ''),
        'delta_advantage_576': gated.get('delta_advantage', 0),
        # Ablation profiles
        'ablation_profile': ablation_profile,
        'sub_ablation_profile': sub_ablation_profile,
        # Per-event
        'per_event_summary': per_event_summary,
        'grammar_band_distribution': dict(band_counts),
    }
    profile_cards[folio] = card
    print(f"  {folio}: section={card['section']}, CCS1={card['ccs1']:.4f}, "
          f"gap={card['gap_to_passing']:.4f}, events={card['n_close_events']}, "
          f"conformity={card['conformity']}")

# -- Step 2: Build passing A2 comparison data --

print("\n-- Step 2: Building passing A2 comparison data --")

passing_data = {}
for folio in passing_a2:
    fc = folio_configs.get(folio, {})
    abl_data = per_folio_abl.get(folio, {})
    ranking = a2_ranking.get(folio, {})
    gap = gap_analysis.get(folio, {})
    land_574 = landscape_574['per_folio_landscape'].get(folio, {})
    folio_events = events_by_folio.get(folio, [])

    passing_data[folio] = {
        'F1': fc.get('F1', 0), 'F2': fc.get('F2', 0), 'F3': fc.get('F3', 0),
        'F4_raw': fc.get('F4_raw', 0), 'F5': fc.get('F5', 0),
        'ccs1': abl_data.get('baseline_m4f_dye', 0),
        'm1_dye': abl_data.get('baseline_m1_dye', 0),
        'dye_advantage': abl_data.get('baseline_m1_dye', 0) - abl_data.get('baseline_m4f_dye', 0),
        'n_close_events': len(folio_events),
        'epv': ranking.get('epv', 0),
        'section': fc.get('section', ''),
        'ablation_deltas': {
            name: abl_data.get('ablations', {}).get(name, {}).get('delta_m4f_dye', 0)
            for name in ABLATION_NAMES
        },
    }

print(f"  Passing A2 folios loaded: {len(passing_data)}")

# -- Step 3: Statistical Tests --

print("\n-- Step 3: Statistical Tests --")

def mann_whitney_u(group1, group2):
    """Simple Mann-Whitney U implementation (no scipy dependency)."""
    n1, n2 = len(group1), len(group2)
    if n1 == 0 or n2 == 0:
        return {'U': 0, 'p_approx': 1.0, 'rank_biserial': 0.0}
    combined = [(v, 0) for v in group1] + [(v, 1) for v in group2]
    combined.sort(key=lambda x: x[0])
    # Assign ranks (handle ties)
    ranks = [0.0] * len(combined)
    i = 0
    while i < len(combined):
        j = i
        while j < len(combined) and combined[j][0] == combined[i][0]:
            j += 1
        avg_rank = (i + j + 1) / 2.0  # 1-based
        for k in range(i, j):
            ranks[k] = avg_rank
        i = j
    R1 = sum(ranks[k] for k in range(len(combined)) if combined[k][1] == 0)
    U1 = R1 - n1 * (n1 + 1) / 2
    U2 = n1 * n2 - U1
    U = min(U1, U2)
    # Normal approximation for p-value
    mu = n1 * n2 / 2
    sigma = math.sqrt(n1 * n2 * (n1 + n2 + 1) / 12)
    if sigma == 0:
        z = 0
    else:
        z = (U - mu) / sigma
    # Two-tailed p from z (approximate using error function)
    p_approx = 2 * (1 - 0.5 * (1 + math.erf(abs(z) / math.sqrt(2))))
    # Rank-biserial correlation
    rbc = 1 - (2 * U) / (n1 * n2) if n1 * n2 > 0 else 0
    return {'U': round(U, 2), 'z': round(z, 4), 'p_approx': round(p_approx, 6), 'rank_biserial': round(rbc, 4)}

def ks_two_sample(group1, group2):
    """Simple two-sample Kolmogorov-Smirnov test."""
    n1, n2 = len(group1), len(group2)
    if n1 == 0 or n2 == 0:
        return {'D': 0, 'p_approx': 1.0}
    s1 = sorted(group1)
    s2 = sorted(group2)
    all_vals = sorted(set(s1 + s2))
    max_d = 0.0
    for v in all_vals:
        f1 = sum(1 for x in s1 if x <= v) / n1
        f2 = sum(1 for x in s2 if x <= v) / n2
        max_d = max(max_d, abs(f1 - f2))
    # Asymptotic p-value
    en = math.sqrt(n1 * n2 / (n1 + n2))
    lam = (en + 0.12 + 0.11 / en) * max_d
    p = 2 * math.exp(-2 * lam * lam) if lam > 0 else 1.0
    p = min(max(p, 0), 1.0)
    return {'D': round(max_d, 4), 'p_approx': round(p, 6)}

def fisher_exact_2x2(a, b, c, d):
    """Fisher's exact test for 2x2 table [[a,b],[c,d]]. Returns p-value approximation."""
    # Use hypergeometric probability
    n = a + b + c + d
    def log_factorial(n):
        return sum(math.log(i) for i in range(1, n + 1))
    log_p_cutoff = (log_factorial(a+b) + log_factorial(c+d) + log_factorial(a+c) + log_factorial(b+d)
                    - log_factorial(n) - log_factorial(a) - log_factorial(b) - log_factorial(c) - log_factorial(d))
    # Sum over all tables at least as extreme
    p_sum = 0.0
    row1 = a + b
    row2 = c + d
    col1 = a + c
    for x in range(0, min(row1, col1) + 1):
        y = row1 - x
        z = col1 - x
        w = row2 - z
        if y < 0 or z < 0 or w < 0:
            continue
        log_p = (log_factorial(row1) + log_factorial(row2) + log_factorial(col1) + log_factorial(y + w)
                 - log_factorial(n) - log_factorial(x) - log_factorial(y) - log_factorial(z) - log_factorial(w))
        if log_p <= log_p_cutoff + 1e-10:
            p_sum += math.exp(log_p)
    return round(min(p_sum, 1.0), 6)

# 3a. Mann-Whitney on F-axes
forgiving_vals = {name: [] for name in ['F1', 'F2', 'F3', 'F4_raw', 'F5']}
passing_vals = {name: [] for name in ['F1', 'F2', 'F3', 'F4_raw', 'F5']}
for folio in STUBBORN_8:
    for name in forgiving_vals:
        forgiving_vals[name].append(profile_cards[folio]['f_params'][name])
for folio in passing_a2:
    for name in passing_vals:
        passing_vals[name].append(passing_data[folio][name])

f_axis_tests = {}
print("\nMann-Whitney U on F-axes (8 forgiving vs 10 passing):")
for name in ['F1', 'F2', 'F3', 'F4_raw', 'F5']:
    result = mann_whitney_u(forgiving_vals[name], passing_vals[name])
    f_axis_tests[name] = result
    fg_mean = sum(forgiving_vals[name]) / len(forgiving_vals[name])
    pg_mean = sum(passing_vals[name]) / len(passing_vals[name])
    sig = '*' if result['p_approx'] < 0.05 else ''
    print(f"  {name}: forg_mean={fg_mean:.3f}, pass_mean={pg_mean:.3f}, "
          f"U={result['U']}, p={result['p_approx']:.4f}{sig}, rbc={result['rank_biserial']:.3f}")

# 3b. Mann-Whitney on ablation channels
abl_tests = {}
print("\nMann-Whitney U on ablation channels (delta_m4f_dye):")
for abl_name in ABLATION_NAMES:
    fg = [profile_cards[f]['ablation_profile'][abl_name]['delta_m4f_dye'] for f in STUBBORN_8]
    pg = [passing_data[f]['ablation_deltas'][abl_name] for f in passing_a2]
    result = mann_whitney_u(fg, pg)
    abl_tests[abl_name] = result
    fg_mean = sum(fg) / len(fg)
    pg_mean = sum(pg) / len(pg)
    sig = '*' if result['p_approx'] < 0.05 else ''
    print(f"  {abl_name}: forg_mean={fg_mean:.4f}, pass_mean={pg_mean:.4f}, "
          f"p={result['p_approx']:.4f}{sig}, rbc={result['rank_biserial']:.3f}")

# 3c. KS test on CCS1
fg_ccs1 = [profile_cards[f]['ccs1'] for f in STUBBORN_8]
pg_ccs1 = [passing_data[f]['ccs1'] for f in passing_a2]
ks_result = ks_two_sample(fg_ccs1, pg_ccs1)
print(f"\nKS test on CCS1: D={ks_result['D']}, p={ks_result['p_approx']:.4f}")

# 3d. Fisher's exact on section composition (H vs C)
fg_h = sum(1 for f in STUBBORN_8 if profile_cards[f]['section'] == 'H')
fg_c = len(STUBBORN_8) - fg_h
pg_h = sum(1 for f in passing_a2 if passing_data[f]['section'] == 'H')
pg_c = len(passing_a2) - pg_h
fisher_p = fisher_exact_2x2(fg_h, fg_c, pg_h, pg_c)
print(f"\nFisher's exact on section (H/C): forgiving={fg_h}H/{fg_c}C, passing={pg_h}H/{pg_c}C, p={fisher_p:.4f}")

# 3e. Z-scores of the 8 against full A2 distribution
print("\nZ-scores (forgiving vs full A2):")
z_score_results = {}
for metric_name, get_val in [
    ('CCS1', lambda f: per_folio_abl[f]['baseline_m4f_dye']),
    ('DYE_advantage', lambda f: per_folio_abl[f]['baseline_m1_dye'] - per_folio_abl[f]['baseline_m4f_dye']),
    ('NO_CLOSE_RECOVERY', lambda f: per_folio_abl[f]['ablations']['NO_CLOSE_RECOVERY']['delta_m4f_dye']),
    ('NO_CONTAINMENT', lambda f: per_folio_abl[f]['ablations']['NO_CONTAINMENT']['delta_m4f_dye']),
]:
    all_a2_vals = [get_val(f) for f in all_a2_folios]
    mu = sum(all_a2_vals) / len(all_a2_vals)
    sd = math.sqrt(sum((v - mu)**2 for v in all_a2_vals) / len(all_a2_vals))
    if sd == 0:
        z_scores = {f: 0 for f in STUBBORN_8}
    else:
        z_scores = {f: (get_val(f) - mu) / sd for f in STUBBORN_8}
    n_extreme = sum(1 for z in z_scores.values() if abs(z) > 2)
    z_score_results[metric_name] = {
        'z_scores': {f: round(z, 3) for f, z in z_scores.items()},
        'n_extreme_2sigma': n_extreme,
        'a2_mean': round(mu, 6),
        'a2_sd': round(sd, 6),
    }
    print(f"  {metric_name}: {n_extreme}/8 beyond 2-sigma, A2 mean={mu:.4f}, sd={sd:.4f}")
    for f in STUBBORN_8:
        z = z_scores[f]
        marker = ' **' if abs(z) > 2 else ''
        print(f"    {f}: z={z:.3f}{marker}")

# -- Step 4: Summary statistics --

print("\n-- Step 4: Summary Statistics --")

fg_events = [profile_cards[f]['n_close_events'] for f in STUBBORN_8]
pg_events = [passing_data[f]['n_close_events'] for f in passing_a2]
event_test = mann_whitney_u(fg_events, pg_events)

print(f"Event counts: forgiving mean={sum(fg_events)/len(fg_events):.1f}, "
      f"passing mean={sum(pg_events)/len(pg_events):.1f}, "
      f"MW p={event_test['p_approx']:.4f}")

fg_ccs1_mean = sum(fg_ccs1) / len(fg_ccs1)
pg_ccs1_mean = sum(pg_ccs1) / len(pg_ccs1)
print(f"CCS1: forgiving mean={fg_ccs1_mean:.4f}, passing mean={pg_ccs1_mean:.4f}")

fg_gap = [profile_cards[f]['gap_to_passing'] for f in STUBBORN_8]
print(f"Gap to passing: min={min(fg_gap):.4f}, max={max(fg_gap):.4f}, "
      f"mean={sum(fg_gap)/len(fg_gap):.4f}")

# Count significant Mann-Whitney results
n_sig_f_axes = sum(1 for v in f_axis_tests.values() if v['p_approx'] < 0.05)
n_sig_abl = sum(1 for v in abl_tests.values() if v['p_approx'] < 0.05)
print(f"\nSignificant F-axis tests (p<0.05): {n_sig_f_axes}/5")
print(f"Significant ablation tests (p<0.05): {n_sig_abl}/5")

# -- Verification --

print("\n-- Verification --")
assert len(profile_cards) == 8, f"Expected 8 profile cards, got {len(profile_cards)}"
assert len(all_a2_folios) == 18, f"Expected 18 A2 folios, got {len(all_a2_folios)}"
assert len(passing_a2) == 10, f"Expected 10 passing A2, got {len(passing_a2)}"
for f in STUBBORN_8:
    fp = profile_cards[f]['f_params']
    assert 0.4 <= fp['F1'] <= 1.6, f"{f} F1 out of range: {fp['F1']}"
    assert 0.4 <= fp['F2'] <= 1.6, f"{f} F2 out of range: {fp['F2']}"
    assert 0 <= fp['F4_raw'] <= 1.0, f"{f} F4_raw out of range: {fp['F4_raw']}"
print("All verification checks passed.")

# -- Save results --

results = {
    'metadata': {
        'phase': 579,
        'script': 't0_pole_census',
        'n_stubborn': 8,
        'n_passing_a2': len(passing_a2),
        'n_all_a2': len(all_a2_folios),
        'stubborn_folios': STUBBORN_8,
        'passing_a2_folios': passing_a2,
        'runtime_s': round(time.time() - t_start, 2),
    },
    'profile_cards': profile_cards,
    'passing_a2_data': passing_data,
    'statistical_tests': {
        'f_axis_mann_whitney': f_axis_tests,
        'ablation_mann_whitney': abl_tests,
        'ccs1_ks_test': ks_result,
        'section_fisher_exact': {
            'forgiving_H': fg_h, 'forgiving_C': fg_c,
            'passing_H': pg_h, 'passing_C': pg_c,
            'p_value': fisher_p,
        },
        'z_scores': z_score_results,
        'event_count_test': event_test,
    },
    'summary': {
        'n_sig_f_axes': n_sig_f_axes,
        'n_sig_ablation': n_sig_abl,
        'ccs1_ks_significant': ks_result['p_approx'] < 0.05,
        'section_fisher_significant': fisher_p < 0.05,
        'forgiving_ccs1_mean': round(fg_ccs1_mean, 6),
        'passing_ccs1_mean': round(pg_ccs1_mean, 6),
        'forgiving_event_mean': round(sum(fg_events) / len(fg_events), 2),
        'passing_event_mean': round(sum(pg_events) / len(pg_events), 2),
        'gap_range': [round(min(fg_gap), 4), round(max(fg_gap), 4)],
    },
}

out_path = RESULTS_DIR / 't0_pole_census.json'
with open(out_path, 'w') as f:
    json.dump(results, f, indent=2)

elapsed = time.time() - t_start
print(f"\nT0 complete in {elapsed:.2f}s. Saved to {out_path}")
