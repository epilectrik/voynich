"""
Phase 572 T1: Full-Scale Folio-Specific Apparatus Setup
========================================================
Compute F1-F5 folio-specific apparatus parameters for ALL 82 Currier B folios
(extending the 20-pilot-only computation from Phase 570a).

Identifies eligible folios (~76 with CLOSE lines) and classifies them
by demand eligibility.

Output: phases/PRODUCTIVE_DISRUPTION_EXPANSION/results/t1_full_scale_setup.json
"""

import json
import sys
import os
import numpy as np
from datetime import datetime

# -- paths ---------------------------------------------------------------
BASE = 'C:/git/voynich'
sys.path.insert(0, BASE)

DWELL_PATH      = os.path.join(BASE, 'phases/REGIME_DWELL_ARCHITECTURE/results/dwell_architecture.json')
BUDGETS_PATH    = os.path.join(BASE, 'phases/SECTION_TEMPLATE_TRACE_EXECUTOR/results/t2_folio_budgets.json')
APPARATUS_PATH  = os.path.join(BASE, 'phases/APPARATUS_VOCABULARY_CLASSIFICATION/results/apparatus_profiles.json')
ACCENT_PATH     = os.path.join(BASE, 'phases/FOLIO_ACCENT_VECTOR/results/folio_accent_vector.json')
EVENT_PATH      = os.path.join(BASE, 'phases/EVENTIVE_CLOSURE_PACKETS/results/t1_event_taxonomy.json')
REGIME_PATH     = os.path.join(BASE, 'data/regime_folio_mapping.json')
PILOT_570A_PATH = os.path.join(BASE, 'phases/FOLIO_SPECIFIC_APPARATUS_PILOT/results/t1_pilot_selection.json')
REF_571_PATH    = os.path.join(BASE, 'phases/PROCESS_QUALITY_GENERALIZATION/results/t4_metrics.json')
OUT_DIR         = os.path.join(BASE, 'phases/PRODUCTIVE_DISRUPTION_EXPANSION/results')
OUT_PATH        = os.path.join(OUT_DIR, 't1_full_scale_setup.json')


# -- profile assignment rules --------------------------------------------
def assign_profile(section, regime):
    """Assign apparatus profile from section + regime."""
    if section == 'B':
        return 'A1_BATH_REFLUX'
    if section == 'H':
        if regime == 'REGIME_1':
            return 'A1_BATH_REFLUX'
        elif regime == 'REGIME_2':
            return 'A2_SEALED_RECIRCULATION'
        else:  # REGIME_3, REGIME_4
            return 'A3_DISTILL_COLLECT'
    if section in ('C', 'T'):
        return 'A2_SEALED_RECIRCULATION'
    if section == 'S':
        return 'A3_DISTILL_COLLECT'
    return 'UNKNOWN'


# -- helper functions ----------------------------------------------------
def normalize(x, lo, hi):
    """Normalize x to [0,1] with clipping at lo/hi (5th/95th percentile)."""
    if hi == lo:
        return 0.5
    clipped = max(lo, min(hi, x))
    return (clipped - lo) / (hi - lo)


def lerp(a, b, t):
    """Linear interpolation: a + t*(b-a)."""
    return a + t * (b - a)


def percentile_bounds(values, p_lo=5, p_hi=95):
    """Return p_lo and p_hi percentile of a list of floats."""
    arr = np.array([v for v in values if v is not None and not np.isnan(v)])
    if len(arr) == 0:
        return 0.0, 1.0
    return float(np.percentile(arr, p_lo)), float(np.percentile(arr, p_hi))


# -- load data -----------------------------------------------------------
print("=" * 90)
print("Phase 572 T1: Full-Scale Folio-Specific Apparatus Setup")
print("=" * 90)
print("\nLoading data sources...")

with open(DWELL_PATH) as f:
    dwell_data = json.load(f)
dwell_by_folio = {rec['folio']: rec for rec in dwell_data['folio_details']}

with open(BUDGETS_PATH) as f:
    budgets_data = json.load(f)
folio_budgets = budgets_data['folio_budgets']

with open(APPARATUS_PATH) as f:
    apparatus_data = json.load(f)
apparatus_scores = apparatus_data['folio_scores']

with open(ACCENT_PATH) as f:
    accent_data = json.load(f)
accent_scores = accent_data['T1_pca']['folio_scores']

with open(EVENT_PATH) as f:
    event_data = json.load(f)
event_map = event_data['event_map']

with open(REGIME_PATH) as f:
    regime_data = json.load(f)
regime_assignments = regime_data['regime_assignments']

with open(PILOT_570A_PATH) as f:
    pilot_570a = json.load(f)
norm_bounds_20 = pilot_570a['normalization_bounds']

with open(REF_571_PATH) as f:
    ref_571 = json.load(f)
phase_571_folios = sorted(ref_571['per_folio'].keys())

print(f"  Dwell:       {len(dwell_by_folio)} folios")
print(f"  Budgets:     {len(folio_budgets)} folios")
print(f"  Apparatus:   {len(apparatus_scores)} folios")
print(f"  Accent PCA:  {len(accent_scores)} folios")
print(f"  Event map:   {len(event_map)} entries")
print(f"  Regime:      {len(regime_assignments)} folios")
print(f"  Pilot 570a:  normalization bounds loaded (20-folio)")
print(f"  Ref 571:     {len(phase_571_folios)} folios")

# -- aggregate event_map per folio ---------------------------------------
print("\nAggregating event_map per folio...")
folio_event_stats = {}
for key, entry in event_map.items():
    folio = key.split('|')[0]
    if folio not in folio_event_stats:
        folio_event_stats[folio] = {'n_close_lines': 0, 'n_work_pred': 0}
    folio_event_stats[folio]['n_close_lines'] += 1
    if entry.get('has_work_predecessor'):
        folio_event_stats[folio]['n_work_pred'] += 1

print(f"  Folios with CLOSE lines: {len(folio_event_stats)}")
total_close = sum(s['n_close_lines'] for s in folio_event_stats.values())
total_wp = sum(s['n_work_pred'] for s in folio_event_stats.values())
print(f"  Total CLOSE lines: {total_close}")
print(f"  Total work-preceded: {total_wp}")

# -- extract proxies for ALL 82 folios ----------------------------------
ALL_FOLIOS = sorted(folio_budgets.keys())
print(f"\nExtracting structural proxies for {len(ALL_FOLIOS)} folios...")

all_proxies = {}
for folio in ALL_FOLIOS:
    proxy = {}

    # Section and regime
    budget = folio_budgets.get(folio)
    regime_rec = regime_assignments.get(folio)

    proxy['section'] = budget['section'] if budget else None
    proxy['regime'] = regime_rec['regime'] if regime_rec else None
    proxy['profile'] = assign_profile(proxy['section'], proxy['regime'])
    proxy['n_tokens'] = budget['n_tokens'] if budget else 0

    # AXM occupancy from dwell architecture
    dwell_rec = dwell_by_folio.get(folio)
    proxy['axm_occ'] = dwell_rec['occupancy']['AXM'] if dwell_rec else None

    # THERMAL fraction from domain budget
    if budget and 'domain_budget' in budget:
        proxy['thermal_frac'] = budget['domain_budget']['fracs'].get('THERMAL', 0.0)
    else:
        proxy['thermal_frac'] = None

    # Headless rate
    if budget and 'headless_regime' in budget:
        proxy['hl_rate'] = budget['headless_regime']['hl_rate']
    else:
        proxy['hl_rate'] = None

    # CLOSE_OPAQUE fraction
    if budget and 'closure_class_dist' in budget:
        proxy['close_opaque_frac'] = budget['closure_class_dist'].get('CLOSE_OPAQUE', 0.0)
    else:
        proxy['close_opaque_frac'] = None

    # SEALED_VESSEL score from apparatus profiles
    app_rec = apparatus_scores.get(folio)
    proxy['sealed_vessel_score'] = app_rec['SEALED_VESSEL'] if app_rec else None

    # Event taxonomy — derived from event_map aggregation
    stats = folio_event_stats.get(folio, {'n_close_lines': 0, 'n_work_pred': 0})
    proxy['n_close_lines'] = stats['n_close_lines']
    proxy['n_work_pred'] = stats['n_work_pred']
    n_tok = proxy['n_tokens'] if proxy['n_tokens'] > 0 else 1
    proxy['event_density'] = stats['n_close_lines'] / n_tok
    proxy['demanded_event_rate'] = (
        stats['n_work_pred'] / stats['n_close_lines']
        if stats['n_close_lines'] > 0 else 0.0
    )

    # Accent PCA
    acc = accent_scores.get(folio)
    if acc:
        proxy['accent_PC1'] = acc['PC1']
        proxy['accent_PC2'] = acc['PC2']
        proxy['accent_PC3'] = acc['PC3']
    else:
        proxy['accent_PC1'] = None
        proxy['accent_PC2'] = None
        proxy['accent_PC3'] = None

    all_proxies[folio] = proxy

# -- print proxy summary ------------------------------------------------
print(f"\nProxy extraction complete for {len(all_proxies)} folios.")
print(f"\n{'Folio':<10} {'Sec':>3} {'Regime':>10} {'Profile':>28} {'Tok':>5} "
      f"{'CL':>3} {'WP':>3} {'AXM':>6} {'THRM':>6} {'HL':>6} {'CO':>6} {'SV':>6}")
print("-" * 115)
for folio in ALL_FOLIOS:
    p = all_proxies[folio]
    axm  = f"{p['axm_occ']:.3f}"            if p['axm_occ'] is not None            else "  N/A"
    thrm = f"{p['thermal_frac']:.3f}"        if p['thermal_frac'] is not None        else "  N/A"
    hl   = f"{p['hl_rate']:.3f}"             if p['hl_rate'] is not None             else "  N/A"
    co   = f"{p['close_opaque_frac']:.3f}"   if p['close_opaque_frac'] is not None   else "  N/A"
    sv   = f"{p['sealed_vessel_score']:.3f}" if p['sealed_vessel_score'] is not None else "  N/A"
    print(f"{folio:<10} {p['section'] or 'N/A':>3} {p['regime'] or 'N/A':>10} "
          f"{p['profile']:>28} {p['n_tokens']:>5} "
          f"{p['n_close_lines']:>3} {p['n_work_pred']:>3} "
          f"{axm:>6} {thrm:>6} {hl:>6} {co:>6} {sv:>6}")

# -- compute normalization bounds (82-folio) -----------------------------
print("\n" + "=" * 90)
print("Computing normalization bounds (5th/95th percentile across ALL 82 folios)...")

NORM_KEYS = [
    'axm_occ', 'thermal_frac', 'hl_rate', 'close_opaque_frac',
    'sealed_vessel_score', 'event_density', 'demanded_event_rate'
]

norm_bounds_82 = {}
for key in NORM_KEYS:
    vals = [all_proxies[f][key] for f in ALL_FOLIOS]
    p5, p95 = percentile_bounds(vals)
    norm_bounds_82[key] = {'p5': round(p5, 6), 'p95': round(p95, 6)}
    print(f"  {key:<25} p5={p5:.6f}  p95={p95:.6f}")

# -- compare 82-folio vs 20-folio bounds --------------------------------
print("\nBounds comparison (82-folio vs 20-folio pilot):")
print(f"  {'Key':<25} {'82-p5':>10} {'82-p95':>10} {'20-p5':>10} {'20-p95':>10} {'Shift':>8}")
print("  " + "-" * 80)
for key in NORM_KEYS:
    b82 = norm_bounds_82[key]
    b20 = norm_bounds_20[key]
    shift_lo = b82['p5'] - b20['p5']
    shift_hi = b82['p95'] - b20['p95']
    print(f"  {key:<25} {b82['p5']:>10.6f} {b82['p95']:>10.6f} "
          f"{b20['p5']:>10.6f} {b20['p95']:>10.6f} "
          f"{shift_lo:>+.4f}/{shift_hi:>+.4f}")

# -- compute F1-F5 for all 82 folios ------------------------------------
print("\n" + "=" * 90)
print("Computing F1-F5 parameters for all 82 folios...")

folio_parameters = {}
for folio in ALL_FOLIOS:
    p = all_proxies[folio]
    params = {}

    # F1: Attractor / Forgiveness -- from AXM occupancy
    if p['axm_occ'] is not None:
        n_axm = normalize(p['axm_occ'], norm_bounds_82['axm_occ']['p5'],
                          norm_bounds_82['axm_occ']['p95'])
        params['F1'] = round(lerp(0.7, 1.4, n_axm), 4)
    else:
        params['F1'] = None

    # F2: Closure Exploitability -- composite of 3 features
    if (p['close_opaque_frac'] is not None and
        p['event_density'] is not None and
        p['demanded_event_rate'] is not None):
        n_co = normalize(p['close_opaque_frac'],
                         norm_bounds_82['close_opaque_frac']['p5'],
                         norm_bounds_82['close_opaque_frac']['p95'])
        n_ed = normalize(p['event_density'],
                         norm_bounds_82['event_density']['p5'],
                         norm_bounds_82['event_density']['p95'])
        n_dr = normalize(p['demanded_event_rate'],
                         norm_bounds_82['demanded_event_rate']['p5'],
                         norm_bounds_82['demanded_event_rate']['p95'])
        F2_raw = 0.5 * n_co + 0.3 * n_ed + 0.2 * n_dr
        params['F2'] = round(lerp(0.7, 1.4, F2_raw), 4)
    else:
        params['F2'] = None

    # F3: Thermal Accent -- from THERMAL fraction
    if p['thermal_frac'] is not None:
        n_th = normalize(p['thermal_frac'],
                         norm_bounds_82['thermal_frac']['p5'],
                         norm_bounds_82['thermal_frac']['p95'])
        params['F3'] = round(lerp(0.7, 1.4, n_th), 4)
    else:
        params['F3'] = None

    # F4: Continuous Headless Infrastructure -- raw normalized (NOT lerp'd)
    if p['hl_rate'] is not None:
        params['F4_raw'] = round(
            normalize(p['hl_rate'],
                      norm_bounds_82['hl_rate']['p5'],
                      norm_bounds_82['hl_rate']['p95']),
            4)
    else:
        params['F4_raw'] = None

    # F5: Containment / Transition -- from SEALED_VESSEL
    if p['sealed_vessel_score'] is not None:
        n_sv = normalize(p['sealed_vessel_score'],
                         norm_bounds_82['sealed_vessel_score']['p5'],
                         norm_bounds_82['sealed_vessel_score']['p95'])
        params['F5'] = round(lerp(0.7, 1.4, n_sv), 4)
    else:
        params['F5'] = None

    params['profile'] = p['profile']
    params['section'] = p['section']
    folio_parameters[folio] = params

# -- print F-parameter table --------------------------------------------
print(f"\n{'Folio':<10} {'Profile':>28} {'Sec':>3} {'F1':>6} {'F2':>6} {'F3':>6} {'F4r':>6} {'F5':>6}")
print("-" * 85)
for folio in ALL_FOLIOS:
    fp = folio_parameters[folio]
    f1 = f"{fp['F1']:.3f}" if fp['F1'] is not None else "  N/A"
    f2 = f"{fp['F2']:.3f}" if fp['F2'] is not None else "  N/A"
    f3 = f"{fp['F3']:.3f}" if fp['F3'] is not None else "  N/A"
    f4 = f"{fp['F4_raw']:.3f}" if fp['F4_raw'] is not None else "  N/A"
    f5 = f"{fp['F5']:.3f}" if fp['F5'] is not None else "  N/A"
    print(f"{folio:<10} {fp['profile']:>28} {fp['section'] or 'N/A':>3} "
          f"{f1:>6} {f2:>6} {f3:>6} {f4:>6} {f5:>6}")

# -- eligibility classification ------------------------------------------
print("\n" + "=" * 90)
print("Eligibility classification...")

eligible_folios = []
excluded_folios = []
folio_configs = {}

for folio in ALL_FOLIOS:
    p = all_proxies[folio]
    fp = folio_parameters[folio]

    n_close_lines = p['n_close_lines']
    n_work_pred = p['n_work_pred']

    if n_close_lines == 0:
        selection_tier = None
        eligibility_class = None
        excluded_folios.append(folio)
    elif n_close_lines <= 2:
        eligibility_class = 'sparse_close'
        selection_tier = 'E_any'
        eligible_folios.append(folio)
    elif n_work_pred >= 2:
        selection_tier = 'work_preceded'
        if n_work_pred >= 3:
            eligibility_class = 'demand_strong'
        else:
            eligibility_class = 'demand_eligible'
        eligible_folios.append(folio)
    else:
        selection_tier = 'E_any'
        eligibility_class = 'fallback_only'
        eligible_folios.append(folio)

    folio_configs[folio] = {
        'F1': fp['F1'],
        'F2': fp['F2'],
        'F3': fp['F3'],
        'F4_raw': fp['F4_raw'],
        'F5': fp['F5'],
        'profile': fp['profile'],
        'section': fp['section'],
        'n_close_lines': n_close_lines,
        'n_work_pred': n_work_pred,
        'eligibility_class': eligibility_class,
        'selection_tier': selection_tier
    }

print(f"\n  Total folios:    {len(ALL_FOLIOS)}")
print(f"  Eligible:        {len(eligible_folios)}")
print(f"  Excluded:        {len(excluded_folios)}")

# -- print eligibility table --------------------------------------------
print(f"\n{'Folio':<10} {'Sec':>3} {'CL':>3} {'WP':>3} {'Eligibility':>16} {'Tier':>16} "
      f"{'F1':>6} {'F2':>6} {'F3':>6} {'F4r':>6} {'F5':>6}")
print("-" * 100)
for folio in ALL_FOLIOS:
    cfg = folio_configs[folio]
    ec = cfg['eligibility_class'] or 'EXCLUDED'
    st = cfg['selection_tier'] or '---'
    f1 = f"{cfg['F1']:.3f}" if cfg['F1'] is not None else "  N/A"
    f2 = f"{cfg['F2']:.3f}" if cfg['F2'] is not None else "  N/A"
    f3 = f"{cfg['F3']:.3f}" if cfg['F3'] is not None else "  N/A"
    f4 = f"{cfg['F4_raw']:.3f}" if cfg['F4_raw'] is not None else "  N/A"
    f5 = f"{cfg['F5']:.3f}" if cfg['F5'] is not None else "  N/A"
    print(f"{folio:<10} {cfg['section'] or 'N/A':>3} {cfg['n_close_lines']:>3} {cfg['n_work_pred']:>3} "
          f"{ec:>16} {st:>16} {f1:>6} {f2:>6} {f3:>6} {f4:>6} {f5:>6}")

# -- build summary -------------------------------------------------------
print("\n" + "=" * 90)
print("Summary breakdowns")
print("=" * 90)

# By section
sections_summary = {}
for folio in ALL_FOLIOS:
    sec = folio_configs[folio]['section'] or 'UNKNOWN'
    sections_summary.setdefault(sec, []).append(folio)

print("\nBy section:")
for sec in sorted(sections_summary.keys()):
    folios = sections_summary[sec]
    n_elig = sum(1 for f in folios if f in eligible_folios)
    print(f"  {sec}: {len(folios)} folios ({n_elig} eligible)")

# By profile
profiles_summary = {}
for folio in ALL_FOLIOS:
    prof = folio_configs[folio]['profile']
    profiles_summary.setdefault(prof, []).append(folio)

print("\nBy profile:")
for prof in sorted(profiles_summary.keys()):
    folios = profiles_summary[prof]
    n_elig = sum(1 for f in folios if f in eligible_folios)
    print(f"  {prof}: {len(folios)} folios ({n_elig} eligible)")

# By eligibility class
elig_summary = {}
for folio in ALL_FOLIOS:
    ec = folio_configs[folio]['eligibility_class'] or 'EXCLUDED'
    elig_summary.setdefault(ec, []).append(folio)

print("\nBy eligibility class:")
for ec in sorted(elig_summary.keys()):
    folios = elig_summary[ec]
    print(f"  {ec}: {len(folios)} folios  {folios}")

# Phase 571 reference folios overlap
print(f"\nPhase 571 reference folios ({len(phase_571_folios)}):")
for f in phase_571_folios:
    cfg = folio_configs.get(f)
    if cfg:
        ec = cfg['eligibility_class'] or 'EXCLUDED'
        print(f"  {f}: {ec} (CL={cfg['n_close_lines']}, WP={cfg['n_work_pred']})")
    else:
        print(f"  {f}: NOT IN 82 FOLIO SET")

# Excluded folios detail
print(f"\nExcluded folios ({len(excluded_folios)}):")
for f in excluded_folios:
    p = all_proxies[f]
    print(f"  {f}: section={p['section']}, n_tokens={p['n_tokens']}, "
          f"n_close_lines={p['n_close_lines']}")

# -- build output JSON ---------------------------------------------------
print("\n" + "=" * 90)
print("Writing output...")

output = {
    'metadata': {
        'phase': '572',
        'script': 't1_full_scale_setup.py',
        'timestamp': datetime.now().isoformat(timespec='seconds'),
        'n_all_folios': len(ALL_FOLIOS),
        'n_eligible': len(eligible_folios),
        'n_excluded': len(excluded_folios)
    },
    'all_folios': ALL_FOLIOS,
    'eligible_folios': eligible_folios,
    'excluded_folios': excluded_folios,
    'folio_configs': folio_configs,
    'normalization_bounds_82': norm_bounds_82,
    'normalization_bounds_20': norm_bounds_20,
    'phase_571_reference_folios': phase_571_folios,
    'summary': {
        'sections': {sec: sorted(folios) for sec, folios in sections_summary.items()},
        'profiles': {prof: sorted(folios) for prof, folios in profiles_summary.items()},
        'eligibility_classes': {ec: sorted(folios) for ec, folios in elig_summary.items()}
    }
}

os.makedirs(OUT_DIR, exist_ok=True)
with open(OUT_PATH, 'w') as f:
    json.dump(output, f, indent=2)

print(f"\nResults written to: {OUT_PATH}")
print(f"JSON size: {os.path.getsize(OUT_PATH):,} bytes")

# -- final verification --------------------------------------------------
print("\n" + "=" * 90)
print("VERIFICATION")
print("=" * 90)
print(f"  Total folios:        {len(ALL_FOLIOS)} (expected 82)")
print(f"  Eligible:            {len(eligible_folios)} (expected ~76)")
print(f"  Excluded:            {len(excluded_folios)} (expected ~6)")
print(f"  Eligible + Excluded: {len(eligible_folios) + len(excluded_folios)} (should = 82)")
print(f"  F-params computed:   {len(folio_parameters)}")
print(f"  Folio configs:       {len(folio_configs)}")

# Sanity: all eligible have n_close_lines > 0
bad_elig = [f for f in eligible_folios if folio_configs[f]['n_close_lines'] == 0]
if bad_elig:
    print(f"  WARNING: Eligible folios with 0 CLOSE lines: {bad_elig}")
else:
    print(f"  All eligible folios have n_close_lines > 0: OK")

# Sanity: all excluded have n_close_lines == 0
bad_excl = [f for f in excluded_folios if folio_configs[f]['n_close_lines'] > 0]
if bad_excl:
    print(f"  WARNING: Excluded folios with CLOSE lines: {bad_excl}")
else:
    print(f"  All excluded folios have n_close_lines == 0: OK")

# Sanity: no None F-params in eligible (except potentially missing data)
n_none_f1 = sum(1 for f in eligible_folios if folio_configs[f]['F1'] is None)
n_none_f2 = sum(1 for f in eligible_folios if folio_configs[f]['F2'] is None)
n_none_f5 = sum(1 for f in eligible_folios if folio_configs[f]['F5'] is None)
print(f"  Eligible with F1=None: {n_none_f1}")
print(f"  Eligible with F2=None: {n_none_f2}")
print(f"  Eligible with F5=None: {n_none_f5}")

print("\nDone.")
