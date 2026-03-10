"""
T0: Opportunity Normalization — Setup + Covariate Audit
Phase 573 - A2_FORGIVINGNESS_MECHANISM_APPARATUS_FAMILIES

Computes per-folio opportunity covariates carried through all downstream
scripts.  Prevents Phase 573 from accidentally re-importing dilution
artifacts (C1608, C1635, C1636).

Covariates computed:
  - eligible_close_count  : number of CLOSE events available
  - strong_close_count    : CLOSE events with E_cts50 flag
  - opaque_close_count    : CLOSE events with E_opaque flag
  - mcb_close_count       : CLOSE events with E_mcb flag
  - strong_close_fraction : strong / eligible (0 if no events)
  - opaque_close_fraction : opaque / eligible
  - mcb_close_fraction    : mcb / eligible
  - mean_dv_magnitude     : mean dv_magnitude_sum across M1 events
  - mean_y_gain           : mean y_gain_event across M1 events
  - demanded_event_density: demanded events per line (from 572 T1)
  - demand_tier           : eligibility_class from 572 T1
  - profile               : apparatus profile
  - section               : manuscript section
"""

import json
import sys
import os
import time
from pathlib import Path
from datetime import datetime, timezone

PROJECT_ROOT = str(Path(__file__).resolve().parents[3])
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

RESULTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'results')
P572_RESULTS = os.path.join(PROJECT_ROOT, 'phases', 'PRODUCTIVE_DISRUPTION_EXPANSION', 'results')


def load_phase572():
    """Load Phase 572 T1 + T2 + T3 outputs."""
    print("  Loading Phase 572 T1 setup...")
    with open(os.path.join(P572_RESULTS, 't1_full_scale_setup.json'), 'r', encoding='utf-8') as f:
        t1 = json.load(f)

    print("  Loading Phase 572 T2 model runs...")
    with open(os.path.join(P572_RESULTS, 't2_full_model_runs.json'), 'r', encoding='utf-8') as f:
        t2 = json.load(f)

    print("  Loading Phase 572 T3 null runs...")
    with open(os.path.join(P572_RESULTS, 't3_null_runs.json'), 'r', encoding='utf-8') as f:
        t3 = json.load(f)

    return t1, t2, t3


def compute_opportunity_covariates(t1, t2, t3):
    """Compute per-folio opportunity covariates from Phase 572 data."""
    eligible = t1['eligible_folios']
    configs = t1['folio_configs']
    primary = t2['primary_runs']
    null_data = t3['m4f_demand_matched']

    covariates = {}

    for folio in eligible:
        fc = configs[folio]
        m1_events = primary[folio]['M1']['per_event_detail']

        # Event counts by type
        n_events = len(m1_events)
        n_strong = 0
        n_opaque = 0
        n_mcb = 0
        total_dv = 0.0
        total_yg = 0.0

        for ev in m1_events:
            ptg = ev.get('packet_types_global', [])
            if 'E_cts50' in ptg:
                n_strong += 1
            if 'E_opaque' in ptg:
                n_opaque += 1
            if 'E_mcb' in ptg:
                n_mcb += 1
            total_dv += ev.get('dv_magnitude_sum', 0.0)
            total_yg += ev.get('y_gain_event', 0.0)

        # M4f mean null DYE (= CCS1 = FI)
        null_perms = null_data.get(folio, {}).get('all_perms', [])
        perm_dyes = []
        for perm in null_perms:
            matched = perm.get('matched_events', [])
            ev_dyes = []
            for ev in matched:
                dv = ev.get('dv_magnitude_sum', 0.0)
                yg = ev.get('y_gain_event', 0.0)
                if dv > 0.001:
                    ev_dyes.append(yg / dv)
            if ev_dyes:
                perm_dyes.append(sum(ev_dyes) / len(ev_dyes))
        mean_null_dye = sum(perm_dyes) / len(perm_dyes) if perm_dyes else 0.0

        covariates[folio] = {
            'eligible_close_count': n_events,
            'strong_close_count': n_strong,
            'opaque_close_count': n_opaque,
            'mcb_close_count': n_mcb,
            'strong_close_fraction': n_strong / n_events if n_events > 0 else 0.0,
            'opaque_close_fraction': n_opaque / n_events if n_events > 0 else 0.0,
            'mcb_close_fraction': n_mcb / n_events if n_events > 0 else 0.0,
            'mean_dv_magnitude': total_dv / n_events if n_events > 0 else 0.0,
            'mean_y_gain': total_yg / n_events if n_events > 0 else 0.0,
            'mean_null_dye': mean_null_dye,
            'demand_tier': fc.get('eligibility_class', 'unknown'),
            'profile': fc['profile'],
            'section': fc['section'],
            'n_close_lines': fc['n_close_lines'],
            'n_work_pred': fc['n_work_pred'],
            'F1': fc['F1'],
            'F2': fc['F2'],
            'F3': fc['F3'],
            'F4_raw': fc['F4_raw'],
            'F5': fc['F5'],
        }

    return covariates


def summarize(covariates):
    """Print summary statistics."""
    profiles = {}
    sections = {}
    tiers = {}

    for folio, cv in covariates.items():
        p = cv['profile']
        s = cv['section']
        t = cv['demand_tier']
        profiles.setdefault(p, []).append(cv)
        sections.setdefault(s, []).append(cv)
        tiers.setdefault(t, []).append(cv)

    print(f"\n{'=' * 70}")
    print("OPPORTUNITY COVARIATES BY PROFILE")
    print(f"{'=' * 70}")
    for p in sorted(profiles):
        cvs = profiles[p]
        n = len(cvs)
        mean_events = sum(c['eligible_close_count'] for c in cvs) / n
        mean_strong = sum(c['strong_close_fraction'] for c in cvs) / n
        mean_opaque = sum(c['opaque_close_fraction'] for c in cvs) / n
        mean_mcb = sum(c['mcb_close_fraction'] for c in cvs) / n
        mean_dv = sum(c['mean_dv_magnitude'] for c in cvs) / n
        mean_yg = sum(c['mean_y_gain'] for c in cvs) / n
        mean_null_dye = sum(c['mean_null_dye'] for c in cvs) / n
        print(f"\n  {p} (n={n}):")
        print(f"    mean_events    = {mean_events:.1f}")
        print(f"    strong_frac    = {mean_strong:.3f}")
        print(f"    opaque_frac    = {mean_opaque:.3f}")
        print(f"    mcb_frac       = {mean_mcb:.3f}")
        print(f"    mean_dv_mag    = {mean_dv:.4f}")
        print(f"    mean_y_gain    = {mean_yg:.4f}")
        print(f"    mean_null_dye  = {mean_null_dye:.4f} (CCS1)")

    print(f"\n{'=' * 70}")
    print("OPPORTUNITY COVARIATES BY DEMAND TIER")
    print(f"{'=' * 70}")
    for t in sorted(tiers):
        cvs = tiers[t]
        n = len(cvs)
        mean_events = sum(c['eligible_close_count'] for c in cvs) / n
        mean_strong = sum(c['strong_close_fraction'] for c in cvs) / n
        print(f"  {t:<20s} n={n:3d}  mean_events={mean_events:.1f}  strong_frac={mean_strong:.3f}")

    print(f"\n{'=' * 70}")
    print("PER-FOLIO SUMMARY")
    print(f"{'=' * 70}")
    print(f"\n  {'Folio':<8s} {'Profile':<28s} {'Sect':<5s} {'Tier':<16s} "
          f"{'Events':>6s} {'Strong%':>7s} {'Opaque%':>7s} {'MCB%':>5s} "
          f"{'CCS1':>7s}")
    for folio in sorted(covariates):
        cv = covariates[folio]
        print(f"  {folio:<8s} {cv['profile']:<28s} {cv['section']:<5s} "
              f"{cv['demand_tier']:<16s} {cv['eligible_close_count']:6d} "
              f"{cv['strong_close_fraction']:7.1%} {cv['opaque_close_fraction']:7.1%} "
              f"{cv['mcb_close_fraction']:5.1%} {cv['mean_null_dye']:7.4f}")


def main():
    t0 = time.time()
    print("=" * 70)
    print("T0: Opportunity Normalization — Setup + Covariate Audit")
    print("Phase 573 - A2_FORGIVINGNESS_MECHANISM_APPARATUS_FAMILIES")
    print("=" * 70)

    print("\n--- Loading Phase 572 data ---")
    t1, t2, t3 = load_phase572()
    print(f"  Eligible folios: {len(t1['eligible_folios'])}")

    print("\n--- Computing opportunity covariates ---")
    covariates = compute_opportunity_covariates(t1, t2, t3)
    print(f"  Computed for {len(covariates)} folios")

    summarize(covariates)

    # Write output
    os.makedirs(RESULTS_DIR, exist_ok=True)
    output = {
        'metadata': {
            'phase': '573',
            'script': 't0_opportunity_normalization.py',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'n_folios': len(covariates),
        },
        'covariates': covariates,
    }
    out_path = os.path.join(RESULTS_DIR, 't0_opportunity_normalization.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=1)
    print(f"\n  Output: {out_path}")
    print(f"  Size: {os.path.getsize(out_path):,} bytes")

    elapsed = time.time() - t0
    print(f"\n  Total time: {elapsed:.1f}s")
    print("  DONE")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
