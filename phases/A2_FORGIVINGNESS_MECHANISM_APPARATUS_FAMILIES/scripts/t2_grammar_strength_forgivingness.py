"""
T2: Grammar Strength Forgivingness
Phase 573 - A2_FORGIVINGNESS_MECHANISM_APPARATUS_FAMILIES

Tests whether A2 forgivingness is uniform or concentrated in specific CLOSE
event types, classified by both event taxonomy AND closure grammar strength.

Key discriminating question:
  - If A2 only forgives WEAKLY SEALED close packets -> soft closure acceptance
  - If A2 forgives even STRONGLY SEALED close packets -> general recirculatory
    conversion (containment physics rescue random disruption regardless)

Grammar strength features (from event taxonomy):
  - CTS band (E_cts50 flag -> high vs low)
  - m-terminal presence (E_mcb flag)
  - opaque terminal (E_opaque, E_opaque_decisive flags)
  - armed closure (E_armed flag)
  - compound events (E_compound flag)
  - demand qualification (work_preceded, demanded)
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

# Grammar strength categories
GRAMMAR_FEATURES = {
    'cts_high': lambda ptg: 'E_cts50' in ptg,
    'cts_low': lambda ptg: 'E_cts50' not in ptg,
    'm_terminal': lambda ptg: 'E_mcb' in ptg,
    'no_m_terminal': lambda ptg: 'E_mcb' not in ptg,
    'opaque': lambda ptg: 'E_opaque' in ptg,
    'no_opaque': lambda ptg: 'E_opaque' not in ptg,
    'opaque_decisive': lambda ptg: 'E_opaque_decisive' in ptg,
    'armed': lambda ptg: 'E_armed' in ptg,
    'compound': lambda ptg: 'E_compound' in ptg,
}

# Composite grammar strength bands
def grammar_strength_band(ptg):
    """Classify closure packet by composite grammar strength."""
    strong_signals = 0
    if 'E_cts50' in ptg:
        strong_signals += 1
    if 'E_mcb' in ptg:
        strong_signals += 1
    if 'E_opaque' in ptg:
        strong_signals += 1
    if 'E_armed' in ptg:
        strong_signals += 1

    if strong_signals >= 3:
        return 'STRONG'
    elif strong_signals >= 1:
        return 'MEDIUM'
    else:
        return 'WEAK'


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


def compute_event_dye(events, min_dv=0.001):
    """Compute mean DYE from list of event dicts."""
    dyes = []
    for ev in events:
        dv = ev.get('dv_magnitude_sum', 0.0)
        yg = ev.get('y_gain_event', 0.0)
        if dv > min_dv:
            dyes.append(yg / dv)
    return sum(dyes) / len(dyes) if dyes else None


def select_events(events):
    """Select events (work_preceded >= 2, else demanded >= 2, else all)."""
    wp = [e for e in events if 'work_preceded' in e.get('demand_qualifiers', [])]
    if len(wp) >= 2:
        return wp
    dem = [e for e in events if 'demanded' in e.get('demand_qualifiers', [])]
    if len(dem) >= 2:
        return dem
    return events


def main():
    t_start = time.time()
    print("=" * 70)
    print("T2: Grammar Strength Forgivingness")
    print("Phase 573 - A2_FORGIVINGNESS_MECHANISM_APPARATUS_FAMILIES")
    print("=" * 70)

    print("\n--- Loading Phase 572 data ---")
    t1, t2, t3 = load_phase572()

    eligible_folios = t1['eligible_folios']
    folio_configs = t1['folio_configs']
    primary_runs = t2['primary_runs']
    null_data = t3['m4f_demand_matched']

    # ================================================================
    # 1. Per-feature CCS1 by profile
    # ================================================================
    print("\n--- Computing per-feature CCS1 by profile ---")

    # Collect all events with grammar annotations
    # Structure: profile -> feature -> [M1_dyes], [M4f_dyes]
    feature_ccs = {}  # profile -> feature -> {m1_dyes: [], m4f_dyes: []}

    # Also compute per-band CCS
    band_ccs = {}  # profile -> band -> {m1_dyes: [], m4f_dyes: []}

    for folio in eligible_folios:
        fc = folio_configs[folio]
        profile = fc['profile']
        m1_events = primary_runs[folio]['M1']['per_event_detail']

        # M1 events with grammar annotations
        for ev in m1_events:
            ptg = ev.get('packet_types_global', [])
            dv = ev.get('dv_magnitude_sum', 0.0)
            yg = ev.get('y_gain_event', 0.0)
            if dv < 0.001:
                continue
            dye = yg / dv
            band = grammar_strength_band(ptg)

            if profile not in feature_ccs:
                feature_ccs[profile] = {f: {'m1_dyes': [], 'm4f_dyes': []}
                                        for f in GRAMMAR_FEATURES}
            if profile not in band_ccs:
                band_ccs[profile] = {b: {'m1_dyes': [], 'm4f_dyes': []}
                                     for b in ['STRONG', 'MEDIUM', 'WEAK']}

            for feat_name, feat_fn in GRAMMAR_FEATURES.items():
                if feat_fn(ptg):
                    feature_ccs[profile][feat_name]['m1_dyes'].append(dye)

            band_ccs[profile][band]['m1_dyes'].append(dye)

        # M4f null events
        null_perms = null_data.get(folio, {}).get('all_perms', [])
        for perm in null_perms:
            for ev in perm.get('matched_events', []):
                ptg = ev.get('packet_types_global', [])
                dv = ev.get('dv_magnitude_sum', 0.0)
                yg = ev.get('y_gain_event', 0.0)
                if dv < 0.001:
                    continue
                dye = yg / dv
                band = grammar_strength_band(ptg)

                if profile not in feature_ccs:
                    feature_ccs[profile] = {f: {'m1_dyes': [], 'm4f_dyes': []}
                                            for f in GRAMMAR_FEATURES}
                if profile not in band_ccs:
                    band_ccs[profile] = {b: {'m1_dyes': [], 'm4f_dyes': []}
                                         for b in ['STRONG', 'MEDIUM', 'WEAK']}

                for feat_name, feat_fn in GRAMMAR_FEATURES.items():
                    if feat_fn(ptg):
                        feature_ccs[profile][feat_name]['m4f_dyes'].append(dye)

                band_ccs[profile][band]['m4f_dyes'].append(dye)

    # ================================================================
    # 2. Within-A2 section decomposition
    # ================================================================
    print("\n--- Within-A2 section decomposition ---")

    section_profile_ccs = {}  # "section|profile" -> {m1_dyes, m4f_dyes, folios}

    for folio in eligible_folios:
        fc = folio_configs[folio]
        profile = fc['profile']
        section = fc['section']
        key = f"{section}|{profile}"

        if key not in section_profile_ccs:
            section_profile_ccs[key] = {'m1_dyes': [], 'm4f_dyes': [], 'folios': [],
                                        'folio_m1_dyes': [], 'folio_m4f_dyes': []}

        m1_events = select_events(primary_runs[folio]['M1']['per_event_detail'])
        m1_dye = compute_event_dye(m1_events)

        null_perms = null_data.get(folio, {}).get('all_perms', [])
        perm_dyes = []
        for perm in null_perms:
            sel = select_events(perm.get('matched_events', []))
            pd = compute_event_dye(sel)
            if pd is not None:
                perm_dyes.append(pd)
        m4f_dye = sum(perm_dyes) / len(perm_dyes) if perm_dyes else 0.0

        section_profile_ccs[key]['folios'].append(folio)
        if m1_dye is not None:
            section_profile_ccs[key]['folio_m1_dyes'].append(m1_dye)
        section_profile_ccs[key]['folio_m4f_dyes'].append(m4f_dye)

    # ================================================================
    # 3. Event-count matched comparison: A2 vs non-A2
    # ================================================================
    print("\n--- Event-count matched comparison ---")

    folio_summaries = {}
    for folio in eligible_folios:
        fc = folio_configs[folio]
        m1_events = primary_runs[folio]['M1']['per_event_detail']
        sel = select_events(m1_events)
        m1_dye = compute_event_dye(sel)

        null_perms = null_data.get(folio, {}).get('all_perms', [])
        perm_dyes = []
        for perm in null_perms:
            pd = compute_event_dye(select_events(perm.get('matched_events', [])))
            if pd is not None:
                perm_dyes.append(pd)
        m4f_dye = sum(perm_dyes) / len(perm_dyes) if perm_dyes else 0.0

        # Grammar strength distribution
        n_strong = sum(1 for e in m1_events
                       if grammar_strength_band(e.get('packet_types_global', [])) == 'STRONG')
        n_medium = sum(1 for e in m1_events
                       if grammar_strength_band(e.get('packet_types_global', [])) == 'MEDIUM')
        n_weak = sum(1 for e in m1_events
                     if grammar_strength_band(e.get('packet_types_global', [])) == 'WEAK')

        folio_summaries[folio] = {
            'profile': fc['profile'],
            'section': fc['section'],
            'n_events': len(m1_events),
            'n_strong': n_strong,
            'n_medium': n_medium,
            'n_weak': n_weak,
            'strong_frac': n_strong / len(m1_events) if m1_events else 0.0,
            'm1_dye': m1_dye if m1_dye is not None else 0.0,
            'm4f_dye': m4f_dye,
            'dye_advantage': (m1_dye - m4f_dye) if m1_dye is not None else 0.0,
        }

    # Bin by event count and compare A2 vs non-A2
    event_bins = {'1-3': (1, 3), '4-7': (4, 7), '8-15': (8, 15), '16+': (16, 999)}
    matched_comparison = {}

    for bin_name, (lo, hi) in event_bins.items():
        a2_folios = [f for f, s in folio_summaries.items()
                     if 'A2' in s['profile'] and lo <= s['n_events'] <= hi]
        non_a2_folios = [f for f, s in folio_summaries.items()
                         if 'A2' not in s['profile'] and lo <= s['n_events'] <= hi]

        a2_data = {
            'n': len(a2_folios),
            'mean_m4f_dye': (sum(folio_summaries[f]['m4f_dye'] for f in a2_folios) / len(a2_folios)
                             if a2_folios else 0.0),
            'mean_dye_adv': (sum(folio_summaries[f]['dye_advantage'] for f in a2_folios) / len(a2_folios)
                             if a2_folios else 0.0),
            'mean_strong_frac': (sum(folio_summaries[f]['strong_frac'] for f in a2_folios) / len(a2_folios)
                                 if a2_folios else 0.0),
        }
        non_a2_data = {
            'n': len(non_a2_folios),
            'mean_m4f_dye': (sum(folio_summaries[f]['m4f_dye'] for f in non_a2_folios) / len(non_a2_folios)
                             if non_a2_folios else 0.0),
            'mean_dye_adv': (sum(folio_summaries[f]['dye_advantage'] for f in non_a2_folios) / len(non_a2_folios)
                             if non_a2_folios else 0.0),
            'mean_strong_frac': (sum(folio_summaries[f]['strong_frac'] for f in non_a2_folios) / len(non_a2_folios)
                                 if non_a2_folios else 0.0),
        }
        matched_comparison[bin_name] = {'A2': a2_data, 'non_A2': non_a2_data}

    # ================================================================
    # Print results
    # ================================================================
    print(f"\n{'=' * 70}")
    print("CCS1 (mean null DYE) BY GRAMMAR STRENGTH BAND")
    print(f"{'=' * 70}")

    for profile in sorted(band_ccs):
        print(f"\n  {profile}:")
        for band in ['STRONG', 'MEDIUM', 'WEAK']:
            bd = band_ccs[profile].get(band, {'m1_dyes': [], 'm4f_dyes': []})
            m1_n = len(bd['m1_dyes'])
            m4f_n = len(bd['m4f_dyes'])
            m1_mean = sum(bd['m1_dyes']) / m1_n if m1_n else 0.0
            m4f_mean = sum(bd['m4f_dyes']) / m4f_n if m4f_n else 0.0
            adv = m1_mean - m4f_mean
            print(f"    {band:<8s}  M1 DYE={m1_mean:.4f} (n={m1_n:4d})  "
                  f"CCS1={m4f_mean:.4f} (n={m4f_n:4d})  adv={adv:+.4f}")

    print(f"\n{'=' * 70}")
    print("CCS1 BY INDIVIDUAL GRAMMAR FEATURE")
    print(f"{'=' * 70}")

    for profile in sorted(feature_ccs):
        print(f"\n  {profile}:")
        for feat in sorted(feature_ccs[profile]):
            fd = feature_ccs[profile][feat]
            m1_n = len(fd['m1_dyes'])
            m4f_n = len(fd['m4f_dyes'])
            m4f_mean = sum(fd['m4f_dyes']) / m4f_n if m4f_n else 0.0
            print(f"    {feat:<22s}  CCS1={m4f_mean:.4f} (n_null={m4f_n:4d})")

    print(f"\n{'=' * 70}")
    print("WITHIN-A2 SECTION DECOMPOSITION")
    print(f"{'=' * 70}")

    for key in sorted(section_profile_ccs):
        sp = section_profile_ccs[key]
        if not sp['folios']:
            continue
        n = len(sp['folios'])
        m1_mean = (sum(sp['folio_m1_dyes']) / len(sp['folio_m1_dyes'])
                   if sp['folio_m1_dyes'] else 0.0)
        m4f_mean = (sum(sp['folio_m4f_dyes']) / len(sp['folio_m4f_dyes'])
                    if sp['folio_m4f_dyes'] else 0.0)
        print(f"  {key:<30s}  n={n:3d}  M1 DYE={m1_mean:.4f}  "
              f"CCS1={m4f_mean:.4f}  adv={m1_mean - m4f_mean:+.4f}")

    print(f"\n{'=' * 70}")
    print("EVENT-COUNT MATCHED: A2 vs non-A2")
    print(f"{'=' * 70}")

    for bin_name in sorted(matched_comparison):
        mc = matched_comparison[bin_name]
        a2 = mc['A2']
        na2 = mc['non_A2']
        print(f"\n  Bin {bin_name}:")
        print(f"    A2     n={a2['n']:3d}  CCS1={a2['mean_m4f_dye']:.4f}  "
              f"adv={a2['mean_dye_adv']:+.4f}  strong%={a2['mean_strong_frac']:.1%}")
        print(f"    non-A2 n={na2['n']:3d}  CCS1={na2['mean_m4f_dye']:.4f}  "
              f"adv={na2['mean_dye_adv']:+.4f}  strong%={na2['mean_strong_frac']:.1%}")

    # ================================================================
    # Write output
    # ================================================================
    os.makedirs(RESULTS_DIR, exist_ok=True)

    # Serialize feature_ccs and band_ccs (means only, not raw lists)
    feature_summary = {}
    for profile in feature_ccs:
        feature_summary[profile] = {}
        for feat, fd in feature_ccs[profile].items():
            m1_n = len(fd['m1_dyes'])
            m4f_n = len(fd['m4f_dyes'])
            feature_summary[profile][feat] = {
                'n_m1': m1_n,
                'n_m4f': m4f_n,
                'mean_m1_dye': sum(fd['m1_dyes']) / m1_n if m1_n else 0.0,
                'mean_m4f_dye': sum(fd['m4f_dyes']) / m4f_n if m4f_n else 0.0,
            }

    band_summary = {}
    for profile in band_ccs:
        band_summary[profile] = {}
        for band, bd in band_ccs[profile].items():
            m1_n = len(bd['m1_dyes'])
            m4f_n = len(bd['m4f_dyes'])
            m1_mean = sum(bd['m1_dyes']) / m1_n if m1_n else 0.0
            m4f_mean = sum(bd['m4f_dyes']) / m4f_n if m4f_n else 0.0
            band_summary[profile][band] = {
                'n_m1': m1_n,
                'n_m4f': m4f_n,
                'mean_m1_dye': round(m1_mean, 6),
                'mean_m4f_dye': round(m4f_mean, 6),
                'dye_advantage': round(m1_mean - m4f_mean, 6),
            }

    section_summary = {}
    for key, sp in section_profile_ccs.items():
        if not sp['folios']:
            continue
        n = len(sp['folios'])
        section_summary[key] = {
            'n_folios': n,
            'folios': sp['folios'],
            'mean_m1_dye': (sum(sp['folio_m1_dyes']) / len(sp['folio_m1_dyes'])
                            if sp['folio_m1_dyes'] else 0.0),
            'mean_m4f_dye': (sum(sp['folio_m4f_dyes']) / len(sp['folio_m4f_dyes'])
                             if sp['folio_m4f_dyes'] else 0.0),
        }

    output = {
        'metadata': {
            'phase': '573',
            'script': 't2_grammar_strength_forgivingness.py',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'n_folios': len(eligible_folios),
            'elapsed_seconds': round(time.time() - t_start, 2),
        },
        'band_summary': band_summary,
        'feature_summary': feature_summary,
        'section_profile_decomposition': section_summary,
        'event_count_matched': matched_comparison,
        'per_folio': folio_summaries,
    }

    out_path = os.path.join(RESULTS_DIR, 't2_grammar_strength_forgivingness.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=1)

    print(f"\n  Output: {out_path}")
    print(f"  Size: {os.path.getsize(out_path):,} bytes")
    print(f"\n  Total time: {time.time() - t_start:.1f}s")
    print("  DONE")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
