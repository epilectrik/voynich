"""
Phase 570a T1: Pilot Folio Selection and Proxy Extraction
=========================================================
Select 4 pilot folios from the canonical 20, extract structural proxy vectors,
and compute F1-F5 parameter values using monotone mappings.

Output: phases/FOLIO_SPECIFIC_APPARATUS_PILOT/results/t1_pilot_selection.json
"""

import json
import sys
import os
import numpy as np
from datetime import datetime

# ── paths ──────────────────────────────────────────────────────────────────
BASE = 'C:/git/voynich'
sys.path.insert(0, BASE)

DWELL_PATH      = os.path.join(BASE, 'phases/REGIME_DWELL_ARCHITECTURE/results/dwell_architecture.json')
BUDGETS_PATH    = os.path.join(BASE, 'phases/SECTION_TEMPLATE_TRACE_EXECUTOR/results/t2_folio_budgets.json')
APPARATUS_PATH  = os.path.join(BASE, 'phases/APPARATUS_VOCABULARY_CLASSIFICATION/results/apparatus_profiles.json')
ACCENT_PATH     = os.path.join(BASE, 'phases/FOLIO_ACCENT_VECTOR/results/folio_accent_vector.json')
EVENT_PATH      = os.path.join(BASE, 'phases/EVENTIVE_CLOSURE_PACKETS/results/t1_event_taxonomy.json')
REGIME_PATH     = os.path.join(BASE, 'data/regime_folio_mapping.json')
OUT_DIR         = os.path.join(BASE, 'phases/FOLIO_SPECIFIC_APPARATUS_PILOT/results')
OUT_PATH        = os.path.join(OUT_DIR, 't1_pilot_selection.json')

# ── canonical lists ────────────────────────────────────────────────────────
PILOT_FOLIOS = [
    'f78r', 'f84r', 'f79r', 'f81v', 'f55r', 'f40v', 'f43v', 'f34r',
    'f31r', 'f39v', 'f95r1', 'f104r', 'f111r', 'f116r', 'f105r',
    'f108v', 'f66r', 'f85r1', 'f86v5', 'f86v6'
]

PROPOSED_PILOT_4 = ['f108v', 'f86v6', 'f111r', 'f84r']

# ── profile assignment rules ──────────────────────────────────────────────
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


# ── helper functions ──────────────────────────────────────────────────────
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


# ── load data ─────────────────────────────────────────────────────────────
print("Loading data sources...")

with open(DWELL_PATH) as f:
    dwell_data = json.load(f)
# Build folio -> record lookup from flat array
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
pilot_summary = event_data['pilot_summary']

with open(REGIME_PATH) as f:
    regime_data = json.load(f)
regime_assignments = regime_data['regime_assignments']

print(f"  Dwell: {len(dwell_by_folio)} folios")
print(f"  Budgets: {len(folio_budgets)} folios")
print(f"  Apparatus: {len(apparatus_scores)} folios")
print(f"  Accent PCA: {len(accent_scores)} folios")
print(f"  Event taxonomy pilot summary: {len(pilot_summary)} folios")
print(f"  Regime assignments: {len(regime_assignments)} folios")

# ── extract proxies for all 20 pilot folios ───────────────────────────────
print("\nExtracting structural proxies for 20 pilot folios...")

all_proxies = {}
for folio in PILOT_FOLIOS:
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

    # Event taxonomy
    evt = pilot_summary.get(folio)
    if evt:
        proxy['n_close_lines'] = evt['n_close_lines']
        proxy['n_work_pred'] = evt['n_with_work_pred']
        n_tok = proxy['n_tokens'] if proxy['n_tokens'] > 0 else 1
        proxy['event_density'] = evt['n_close_lines'] / n_tok
        proxy['demanded_event_rate'] = (
            evt['n_with_work_pred'] / evt['n_close_lines']
            if evt['n_close_lines'] > 0 else 0.0
        )
    else:
        # Folios absent from event taxonomy (e.g. f40v, f81v) — 0 CLOSE lines
        proxy['n_close_lines'] = 0
        proxy['n_work_pred'] = 0
        proxy['event_density'] = 0.0
        proxy['demanded_event_rate'] = 0.0

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

# ── print proxy summary ──────────────────────────────────────────────────
print(f"\nProxy extraction complete for {len(all_proxies)} folios.")
print(f"{'Folio':<10} {'Sec':>3} {'Regime':>10} {'Profile':>28} {'Tok':>5} "
      f"{'CL':>3} {'WP':>3} {'AXM':>6} {'THRM':>6} {'HL':>6} {'CO':>6} {'SV':>6}")
print("-" * 110)
for folio in PILOT_FOLIOS:
    p = all_proxies[folio]
    axm = f"{p['axm_occ']:.3f}" if p['axm_occ'] is not None else "  N/A"
    thrm = f"{p['thermal_frac']:.3f}" if p['thermal_frac'] is not None else "  N/A"
    hl = f"{p['hl_rate']:.3f}" if p['hl_rate'] is not None else "  N/A"
    co = f"{p['close_opaque_frac']:.3f}" if p['close_opaque_frac'] is not None else "  N/A"
    sv = f"{p['sealed_vessel_score']:.3f}" if p['sealed_vessel_score'] is not None else "  N/A"
    print(f"{folio:<10} {p['section'] or 'N/A':>3} {p['regime'] or 'N/A':>10} "
          f"{p['profile']:>28} {p['n_tokens']:>5} "
          f"{p['n_close_lines']:>3} {p['n_work_pred']:>3} "
          f"{axm:>6} {thrm:>6} {hl:>6} {co:>6} {sv:>6}")

# ── compute normalization bounds (5th/95th percentile across all 20) ─────
print("\nComputing normalization bounds (5th/95th percentile across 20 pilot folios)...")

NORM_KEYS = [
    'axm_occ', 'thermal_frac', 'hl_rate', 'close_opaque_frac',
    'sealed_vessel_score', 'event_density', 'demanded_event_rate'
]

norm_bounds = {}
for key in NORM_KEYS:
    vals = [all_proxies[f][key] for f in PILOT_FOLIOS]
    p5, p95 = percentile_bounds(vals)
    norm_bounds[key] = {'p5': round(p5, 6), 'p95': round(p95, 6)}
    print(f"  {key:<25} p5={p5:.6f}  p95={p95:.6f}")

# ── compute F1-F5 for all 20 pilot folios ────────────────────────────────
print("\nComputing F1-F5 parameters for all 20 pilot folios...")

folio_parameters = {}
for folio in PILOT_FOLIOS:
    p = all_proxies[folio]
    params = {}

    # F1: Attractor / Forgiveness — from AXM occupancy
    if p['axm_occ'] is not None:
        n_axm = normalize(p['axm_occ'], norm_bounds['axm_occ']['p5'], norm_bounds['axm_occ']['p95'])
        params['F1'] = round(lerp(0.7, 1.4, n_axm), 4)
    else:
        params['F1'] = None

    # F2: Closure Exploitability — composite of 3 features
    if (p['close_opaque_frac'] is not None and
        p['event_density'] is not None and
        p['demanded_event_rate'] is not None):
        n_co = normalize(p['close_opaque_frac'],
                         norm_bounds['close_opaque_frac']['p5'],
                         norm_bounds['close_opaque_frac']['p95'])
        n_ed = normalize(p['event_density'],
                         norm_bounds['event_density']['p5'],
                         norm_bounds['event_density']['p95'])
        n_dr = normalize(p['demanded_event_rate'],
                         norm_bounds['demanded_event_rate']['p5'],
                         norm_bounds['demanded_event_rate']['p95'])
        F2_raw = 0.5 * n_co + 0.3 * n_ed + 0.2 * n_dr
        params['F2'] = round(lerp(0.7, 1.4, F2_raw), 4)
    else:
        params['F2'] = None

    # F3: Thermal Accent — from THERMAL fraction
    if p['thermal_frac'] is not None:
        n_th = normalize(p['thermal_frac'],
                         norm_bounds['thermal_frac']['p5'],
                         norm_bounds['thermal_frac']['p95'])
        params['F3'] = round(lerp(0.7, 1.4, n_th), 4)
    else:
        params['F3'] = None

    # F4: Continuous Headless Infrastructure — raw normalized (NOT lerp'd)
    if p['hl_rate'] is not None:
        params['F4_raw'] = round(
            normalize(p['hl_rate'],
                      norm_bounds['hl_rate']['p5'],
                      norm_bounds['hl_rate']['p95']),
            4)
    else:
        params['F4_raw'] = None

    # F5: Containment / Transition — from SEALED_VESSEL
    if p['sealed_vessel_score'] is not None:
        n_sv = normalize(p['sealed_vessel_score'],
                         norm_bounds['sealed_vessel_score']['p5'],
                         norm_bounds['sealed_vessel_score']['p95'])
        params['F5'] = round(lerp(0.7, 1.4, n_sv), 4)
    else:
        params['F5'] = None

    params['profile'] = p['profile']
    params['section'] = p['section']
    folio_parameters[folio] = params

# ── print F-parameter table ──────────────────────────────────────────────
print(f"\n{'Folio':<10} {'Profile':>28} {'Sec':>3} {'F1':>6} {'F2':>6} {'F3':>6} {'F4r':>6} {'F5':>6}")
print("-" * 80)
for folio in PILOT_FOLIOS:
    fp = folio_parameters[folio]
    f1 = f"{fp['F1']:.3f}" if fp['F1'] is not None else "  N/A"
    f2 = f"{fp['F2']:.3f}" if fp['F2'] is not None else "  N/A"
    f3 = f"{fp['F3']:.3f}" if fp['F3'] is not None else "  N/A"
    f4 = f"{fp['F4_raw']:.3f}" if fp['F4_raw'] is not None else "  N/A"
    f5 = f"{fp['F5']:.3f}" if fp['F5'] is not None else "  N/A"
    print(f"{folio:<10} {fp['profile']:>28} {fp['section'] or 'N/A':>3} "
          f"{f1:>6} {f2:>6} {f3:>6} {f4:>6} {f5:>6}")

# ── verify proposed 4 pilot folios ───────────────────────────────────────
print("\n" + "=" * 80)
print("SELECTION VERIFICATION: Proposed 4 pilot folios")
print("=" * 80)

sel = PROPOSED_PILOT_4
criteria = {}

# Criterion 1: At least 3/4 have >= 3 work_pred events
wp_counts = [(f, all_proxies[f]['n_work_pred']) for f in sel]
n_with_3wp = sum(1 for _, wp in wp_counts if wp >= 3)
criteria['demanded_event_coverage'] = n_with_3wp >= 3
print(f"\n1. Demanded event coverage (>= 3/4 with >= 3 work_pred):")
for f, wp in wp_counts:
    mark = "PASS" if wp >= 3 else "----"
    print(f"   {f}: {wp} work_pred  [{mark}]")
print(f"   Result: {n_with_3wp}/4 pass => {'PASS' if criteria['demanded_event_coverage'] else 'FAIL'}")

# Criterion 2: All 4 have >= 8 CLOSE lines (relax to >= 2 if needed)
cl_counts = [(f, all_proxies[f]['n_close_lines']) for f in sel]
n_with_8cl = sum(1 for _, cl in cl_counts if cl >= 8)
criteria['event_abundance'] = n_with_8cl == 4
relaxed = all(cl >= 2 for _, cl in cl_counts)
print(f"\n2. Event abundance (all 4 with >= 8 CLOSE lines):")
for f, cl in cl_counts:
    mark = "PASS" if cl >= 8 else "----"
    print(f"   {f}: {cl} CLOSE lines  [{mark}]")
print(f"   Result: {n_with_8cl}/4 pass => {'PASS' if criteria['event_abundance'] else 'FAIL (relaxed: ' + str(relaxed) + ')'}")

# Criterion 3: At least 2 profiles represented
profiles = set(all_proxies[f]['profile'] for f in sel)
criteria['profile_diversity'] = len(profiles) >= 2
print(f"\n3. Profile diversity (>= 2 profiles):")
for f in sel:
    print(f"   {f}: {all_proxies[f]['profile']}")
print(f"   Distinct profiles: {sorted(profiles)}")
print(f"   Result: {len(profiles)} profiles => {'PASS' if criteria['profile_diversity'] else 'FAIL'}")

# Criterion 4: At least 2 sections represented
sections = set(all_proxies[f]['section'] for f in sel)
criteria['section_diversity'] = len(sections) >= 2
print(f"\n4. Section diversity (>= 2 sections):")
for f in sel:
    print(f"   {f}: section {all_proxies[f]['section']}")
print(f"   Distinct sections: {sorted(sections)}")
print(f"   Result: {len(sections)} sections => {'PASS' if criteria['section_diversity'] else 'FAIL'}")

all_pass = all(criteria.values())
print(f"\n{'='*80}")
print(f"OVERALL: {'ALL CRITERIA MET' if all_pass else 'CRITERIA NOT FULLY MET'}")
print(f"{'='*80}")

# ── if verification fails, select alternatives algorithmically ────────────
selected_folios = list(PROPOSED_PILOT_4)
if not all_pass:
    print("\nAttempting algorithmic selection...")
    # Filter to folios with >= 2 CLOSE lines
    candidates = [f for f in PILOT_FOLIOS
                  if all_proxies[f]['n_close_lines'] >= 2]
    # Sort by (n_work_pred desc, n_close_lines desc) to prioritize event-rich folios
    candidates.sort(key=lambda f: (-all_proxies[f]['n_work_pred'],
                                    -all_proxies[f]['n_close_lines']))

    # Greedy: pick top candidate, then add folios that maximize diversity
    best = None
    best_score = -1
    from itertools import combinations
    for combo in combinations(candidates, 4):
        profs = set(all_proxies[f]['profile'] for f in combo)
        secs = set(all_proxies[f]['section'] for f in combo)
        wp3 = sum(1 for f in combo if all_proxies[f]['n_work_pred'] >= 3)
        cl8 = sum(1 for f in combo if all_proxies[f]['n_close_lines'] >= 8)
        if len(profs) < 2 or len(secs) < 2:
            continue
        score = wp3 * 10 + cl8 * 5 + len(profs) + len(secs)
        if score > best_score:
            best_score = score
            best = list(combo)
    if best:
        selected_folios = best
        print(f"  Algorithmically selected: {selected_folios}")
    else:
        print("  WARNING: Could not find a 4-folio set meeting all criteria.")
        print("  Keeping proposed set with relaxed criteria.")

# ── final summary for selected 4 ─────────────────────────────────────────
print("\n" + "=" * 80)
print("SELECTED 4 PILOT FOLIOS — F-PARAMETER SUMMARY")
print("=" * 80)
print(f"\n{'Folio':<10} {'Profile':>28} {'Sec':>3} {'CL':>3} {'WP':>3} "
      f"{'F1':>6} {'F2':>6} {'F3':>6} {'F4r':>6} {'F5':>6}")
print("-" * 90)
for folio in selected_folios:
    p = all_proxies[folio]
    fp = folio_parameters[folio]
    f1 = f"{fp['F1']:.3f}" if fp['F1'] is not None else "  N/A"
    f2 = f"{fp['F2']:.3f}" if fp['F2'] is not None else "  N/A"
    f3 = f"{fp['F3']:.3f}" if fp['F3'] is not None else "  N/A"
    f4 = f"{fp['F4_raw']:.3f}" if fp['F4_raw'] is not None else "  N/A"
    f5 = f"{fp['F5']:.3f}" if fp['F5'] is not None else "  N/A"
    print(f"{folio:<10} {fp['profile']:>28} {fp['section']:>3} "
          f"{p['n_close_lines']:>3} {p['n_work_pred']:>3} "
          f"{f1:>6} {f2:>6} {f3:>6} {f4:>6} {f5:>6}")

# ── build output ──────────────────────────────────────────────────────────
# Serialize proxies — convert None to null-compatible form
def clean_proxy(p):
    """Convert proxy dict for JSON output."""
    return {k: (None if v is None else v) for k, v in p.items()}

output = {
    'metadata': {
        'phase': '570a',
        'script': 't1_pilot_selection.py',
        'timestamp': datetime.now().isoformat(timespec='seconds'),
        'n_pilot_folios': 20,
        'n_selected': 4
    },
    'all_pilot_proxies': {f: clean_proxy(all_proxies[f]) for f in PILOT_FOLIOS},
    'normalization_bounds': norm_bounds,
    'selected_folios': selected_folios,
    'selection_criteria_met': criteria,
    'folio_parameters': folio_parameters
}

os.makedirs(OUT_DIR, exist_ok=True)
with open(OUT_PATH, 'w') as f:
    json.dump(output, f, indent=2)

print(f"\nResults written to: {OUT_PATH}")
print(f"JSON size: {os.path.getsize(OUT_PATH):,} bytes")
print("\nDone.")
