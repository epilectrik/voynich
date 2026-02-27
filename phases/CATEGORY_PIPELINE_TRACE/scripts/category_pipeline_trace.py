#!/usr/bin/env python3
"""
Phase 483: END-TO-END CATEGORY PIPELINE TRACE (A→AZC→B)
========================================================
Traces how 8-category frequency distributions shift across pipeline stages
using the 85 bridge MIDDLEs as tracers. Tests whether categories preserve,
transform, or filter as they flow through A→AZC→B.

Tests:
  T1: Bridge category profile by system context (A, AZC, B)
  T2: Per-category pipeline amplification/attenuation
  T3: AZC zone mediation of category flow
  T4: Section-conditioned pipeline trace (B sections vs uniform A)
  T5: Per-MIDDLE category stability vs usage shift
  T6: Dark pipeline as control group

Pre-registered predictions:
  P1: Significant A-to-B category redistribution (JS > 0.05)
  P2: AZC profile intermediate between A and B
  P3: THERMAL amplified A→B; MARKING and STAGING attenuated
  P4: Zone S enriched for TRANSITION relative to zone R
  P5: BIO shows largest THERMAL amplification; HERBAL closest to A baseline
  P6: Bridge MIDDLEs show moderate rank disruption (rho 0.5-0.7)
  P7: Dark pipeline shows LESS category redistribution than bridge

Depends on: C1250, C1347, C1272, C1139, C1136, C1134, C1282
"""

import json
import sys
import math
import functools
import numpy as np
from pathlib import Path
from collections import Counter, defaultdict
from scipy.stats import spearmanr
from scipy.spatial.distance import jensenshannon

PROJECT = Path(__file__).resolve().parents[3]
RESULTS_DIR = Path(__file__).parent.parent / 'results'
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(PROJECT))
from scripts.voynich import Transcript, Morphology, CategoryClassifier

sys.stdout.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)

CATEGORIES = ['THERMAL', 'FLOW', 'CONTAINMENT', 'STAGING',
              'OPERATION', 'TRANSITION', 'MARKING', 'MONITORING']

AZC_ZONES = {'R', 'C', 'S', 'P'}

# Section mapping for B folios
SECTION_MAP = {
    'B': 'BIO', 'H': 'HERBAL', 'S': 'STARS', 'C': 'COSMO', 'T': 'T_OTHER'
}


def round_floats(obj, digits=6):
    if isinstance(obj, float) or isinstance(obj, np.floating):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return round(float(obj), digits)
    if isinstance(obj, (np.integer, np.int64)):
        return int(obj)
    if isinstance(obj, np.bool_):
        return bool(obj)
    if isinstance(obj, dict):
        return {k: round_floats(v, digits) for k, v in obj.items()}
    if isinstance(obj, list):
        return [round_floats(v, digits) for v in obj]
    if isinstance(obj, tuple):
        return [round_floats(v, digits) for v in obj]
    return obj


def counts_to_distribution(counts, categories=CATEGORIES):
    """Convert category counts to probability distribution."""
    total = sum(counts.get(c, 0) for c in categories)
    if total == 0:
        return {c: 0.0 for c in categories}
    return {c: counts.get(c, 0) / total for c in categories}


def js_divergence(dist1, dist2, categories=CATEGORIES):
    """Jensen-Shannon divergence between two category distributions."""
    p = np.array([dist1.get(c, 0) for c in categories])
    q = np.array([dist2.get(c, 0) for c in categories])
    # Add small epsilon to avoid zeros
    eps = 1e-10
    p = p + eps
    q = q + eps
    p = p / p.sum()
    q = q / q.sum()
    return float(jensenshannon(p, q) ** 2)  # squared JS divergence


def extract_zone(placement):
    """Extract major AZC zone from placement code."""
    if not placement:
        return None
    first = placement[0].upper()
    return first if first in AZC_ZONES else None


# ── Data Loading ─────────────────────────────────────────────────────

def load_data():
    """Load bridge/dark MIDDLE lists and count tokens by system context."""
    print("Loading data...")

    morph = Morphology()
    cc = CategoryClassifier()

    # Load bridge MIDDLEs (85)
    with open(PROJECT / 'phases' / 'BRIDGE_MIDDLE_SELECTION_MECHANISM' / 'results' /
              'bridge_selection.json', encoding='utf-8') as f:
        bridge_data = json.load(f)
    bridge_set = set(bridge_data['t5_structural_profile']['bridge_middles'])
    print(f"  Bridge MIDDLEs: {len(bridge_set)}")

    # Load dark pipeline MIDDLEs (300)
    with open(PROJECT / 'phases' / 'A_TO_B_ROLE_PROJECTION' / 'results' /
              'pp_role_foundation.json', encoding='utf-8') as f:
        pp_role_data = json.load(f)
    with open(PROJECT / 'phases' / 'CROSS_SYSTEM_VOCABULARY_FLOW' / 'results' /
              'ab_vocabulary_flow.json', encoding='utf-8') as f:
        vocab_flow = json.load(f)
    unmatched_pp = set(pp_role_data['unmatched_pp'])
    b_absent = set(vocab_flow['b1']['b_absent_middles'])
    dark_set = unmatched_pp - b_absent
    print(f"  Dark pipeline MIDDLEs: {len(dark_set)}")

    # Load section assignments for B folios (from Phase 479)
    with open(PROJECT / 'phases' / 'GENERATIVE_GAP_CHARACTERIZATION' / 'results' /
              'generative_gap_characterization.json', encoding='utf-8') as f:
        p479 = json.load(f)
    folio_section = {f: d.get('section', 'UNK') for f, d in p479['per_folio'].items()}

    # Single-pass token counting
    tx = Transcript()

    # Counts: {system: {category: count}} for bridge and dark
    bridge_counts = {'A': Counter(), 'AZC': Counter(), 'B': Counter()}
    dark_counts = {'A': Counter(), 'AZC': Counter(), 'B': Counter()}

    # Per-MIDDLE counts in A and B (for T5 rank analysis)
    bridge_middle_a_counts = Counter()  # MIDDLE → count in A
    bridge_middle_b_counts = Counter()  # MIDDLE → count in B

    # AZC zone counts for bridge (T3)
    bridge_zone_counts = defaultdict(Counter)  # zone → {category: count}

    # B section counts for bridge (T4)
    bridge_section_counts = defaultdict(Counter)  # section → {category: count}

    # Process all tokens
    print("  Counting tokens across pipeline stages...")

    # Currier A tokens
    for token in tx.currier_a():
        if token.placement.startswith('L'):
            continue
        if not token.word or not token.word.strip() or '*' in token.word:
            continue
        m = morph.extract(token.word)
        mid = m.middle if m else token.word

        cat = cc.classify(mid)
        if not cat:
            continue

        if mid in bridge_set:
            bridge_counts['A'][cat] += 1
            bridge_middle_a_counts[mid] += 1
        elif mid in dark_set:
            dark_counts['A'][cat] += 1

    # AZC tokens
    for token in tx.azc():
        if not token.word or not token.word.strip() or '*' in token.word:
            continue
        m = morph.extract(token.word)
        mid = m.middle if m else token.word

        cat = cc.classify(mid)
        if not cat:
            continue

        zone = extract_zone(token.placement)

        if mid in bridge_set:
            bridge_counts['AZC'][cat] += 1
            if zone:
                bridge_zone_counts[zone][cat] += 1
        elif mid in dark_set:
            dark_counts['AZC'][cat] += 1

    # Currier B tokens
    for token in tx.currier_b():
        if token.placement.startswith('L'):
            continue
        if not token.word or not token.word.strip() or '*' in token.word:
            continue
        m = morph.extract(token.word)
        mid = m.middle if m else token.word

        cat = cc.classify(mid)
        if not cat:
            continue

        section = folio_section.get(token.folio, 'UNK')

        if mid in bridge_set:
            bridge_counts['B'][cat] += 1
            bridge_middle_b_counts[mid] += 1
            if section != 'UNK':
                bridge_section_counts[section][cat] += 1
        elif mid in dark_set:
            dark_counts['B'][cat] += 1

    # Summary
    for sys_name in ['A', 'AZC', 'B']:
        bt = sum(bridge_counts[sys_name].values())
        dt = sum(dark_counts[sys_name].values())
        print(f"  {sys_name}: bridge={bt}, dark={dt}")

    return {
        'bridge_counts': bridge_counts,
        'dark_counts': dark_counts,
        'bridge_middle_a_counts': bridge_middle_a_counts,
        'bridge_middle_b_counts': bridge_middle_b_counts,
        'bridge_zone_counts': dict(bridge_zone_counts),
        'bridge_section_counts': dict(bridge_section_counts),
        'bridge_set': bridge_set,
        'dark_set': dark_set,
        'cc': cc,
    }


# ── Test Functions ───────────────────────────────────────────────────

def test1_system_profiles(data):
    """T1: Bridge category profile by system context."""
    print("\n=== T1: Bridge Category Profile by System Context ===")

    profiles = {}
    for sys_name in ['A', 'AZC', 'B']:
        dist = counts_to_distribution(data['bridge_counts'][sys_name])
        profiles[sys_name] = dist
        total = sum(data['bridge_counts'][sys_name].values())
        print(f"  {sys_name} (n={total}):")
        for cat in CATEGORIES:
            print(f"    {cat:15s} {dist[cat]:.3f} ({data['bridge_counts'][sys_name].get(cat, 0)})")

    # JS divergences
    js_a_b = js_divergence(profiles['A'], profiles['B'])
    js_a_azc = js_divergence(profiles['A'], profiles['AZC'])
    js_azc_b = js_divergence(profiles['AZC'], profiles['B'])

    print(f"\n  JS divergence: A↔B={js_a_b:.4f}, A↔AZC={js_a_azc:.4f}, AZC↔B={js_azc_b:.4f}")

    # P1: Significant redistribution (JS > 0.05)?
    p1 = js_a_b > 0.05
    print(f"  P1 (A↔B JS > 0.05): {'CONFIRMED' if p1 else 'FALSIFIED'} (JS={js_a_b:.4f})")

    # P2: AZC intermediate?
    azc_intermediate = js_a_azc < js_a_b and js_azc_b < js_a_b
    # Also check: is AZC closer to A than to B?
    azc_closer_to_a = js_a_azc < js_azc_b
    print(f"  P2 (AZC intermediate): {'CONFIRMED' if azc_intermediate else 'FALSIFIED'} "
          f"(closer to {'A' if azc_closer_to_a else 'B'})")

    return {
        'profiles': profiles,
        'totals': {s: sum(data['bridge_counts'][s].values()) for s in ['A', 'AZC', 'B']},
        'js_a_b': js_a_b,
        'js_a_azc': js_a_azc,
        'js_azc_b': js_azc_b,
        'P1_significant_redistribution': p1,
        'P2_azc_intermediate': azc_intermediate,
        'P2_azc_closer_to': 'A' if azc_closer_to_a else 'B',
    }


def test2_amplification(data):
    """T2: Per-category pipeline amplification/attenuation."""
    print("\n=== T2: Per-Category Pipeline Amplification ===")

    dist_a = counts_to_distribution(data['bridge_counts']['A'])
    dist_azc = counts_to_distribution(data['bridge_counts']['AZC'])
    dist_b = counts_to_distribution(data['bridge_counts']['B'])

    results = {}
    print(f"  {'Category':15s} {'A':>6s} {'AZC':>6s} {'B':>6s} {'A→B ratio':>10s}")

    for cat in CATEGORIES:
        a_frac = dist_a[cat]
        azc_frac = dist_azc[cat]
        b_frac = dist_b[cat]
        ratio_ab = b_frac / max(a_frac, 1e-10)

        print(f"  {cat:15s} {a_frac:6.3f} {azc_frac:6.3f} {b_frac:6.3f} {ratio_ab:10.3f}")

        results[cat] = {
            'A': float(a_frac),
            'AZC': float(azc_frac),
            'B': float(b_frac),
            'A_to_B_ratio': float(ratio_ab),
            'amplified': ratio_ab > 1.1,
            'attenuated': ratio_ab < 0.9,
        }

    # P3: THERMAL amplified, MARKING and STAGING attenuated
    thermal_amp = results['THERMAL']['A_to_B_ratio'] > 1.1
    marking_att = results['MARKING']['A_to_B_ratio'] < 0.9
    staging_att = results['STAGING']['A_to_B_ratio'] < 0.9
    p3 = thermal_amp and marking_att and staging_att
    print(f"\n  P3 (THERMAL amp, MARKING+STAGING att): {'CONFIRMED' if p3 else 'FALSIFIED'}")
    print(f"    THERMAL ratio={results['THERMAL']['A_to_B_ratio']:.3f}, "
          f"MARKING ratio={results['MARKING']['A_to_B_ratio']:.3f}, "
          f"STAGING ratio={results['STAGING']['A_to_B_ratio']:.3f}")

    results['P3_thermal_amp_marking_staging_att'] = p3
    return results


def test3_azc_zone_mediation(data):
    """T3: AZC zone mediation of category flow."""
    print("\n=== T3: AZC Zone Mediation ===")

    zone_profiles = {}
    for zone in sorted(data['bridge_zone_counts'].keys()):
        counts = data['bridge_zone_counts'][zone]
        total = sum(counts.values())
        if total < 10:
            continue
        dist = counts_to_distribution(counts)
        zone_profiles[zone] = dist

        print(f"  Zone {zone} (n={total}):")
        for cat in CATEGORIES:
            print(f"    {cat:15s} {dist[cat]:.3f} ({counts.get(cat, 0)})")

    # P4: Zone S enriched for TRANSITION relative to zone R
    if 'S' in zone_profiles and 'R' in zone_profiles:
        s_trans = zone_profiles['S'].get('TRANSITION', 0)
        r_trans = zone_profiles['R'].get('TRANSITION', 0)
        p4 = s_trans > r_trans
        print(f"\n  P4 (Zone S TRANSITION > Zone R): {'CONFIRMED' if p4 else 'FALSIFIED'} "
              f"(S={s_trans:.3f}, R={r_trans:.3f})")
    else:
        p4 = None
        print(f"\n  P4: Insufficient zone data")

    # JS divergence between zones
    zone_js = {}
    zones = sorted(zone_profiles.keys())
    for i in range(len(zones)):
        for j in range(i + 1, len(zones)):
            js = js_divergence(zone_profiles[zones[i]], zone_profiles[zones[j]])
            key = f"{zones[i]}↔{zones[j]}"
            zone_js[key] = js
            print(f"  JS({key}) = {js:.4f}")

    return {
        'zone_profiles': zone_profiles,
        'zone_js': zone_js,
        'P4_s_transition_enrichment': p4,
    }


def test4_section_conditioned(data):
    """T4: Section-conditioned pipeline trace."""
    print("\n=== T4: Section-Conditioned Pipeline Trace ===")

    dist_a = counts_to_distribution(data['bridge_counts']['A'])

    section_profiles = {}
    section_js_from_a = {}

    for section in sorted(data['bridge_section_counts'].keys()):
        counts = data['bridge_section_counts'][section]
        total = sum(counts.values())
        if total < 20:
            continue
        dist = counts_to_distribution(counts)
        section_profiles[section] = dist
        js = js_divergence(dist_a, dist)
        section_js_from_a[section] = js

        section_name = SECTION_MAP.get(section, section)
        print(f"  Section {section_name} (n={total}): JS from A={js:.4f}")
        for cat in CATEGORIES:
            ratio = dist[cat] / max(dist_a[cat], 1e-10)
            marker = '↑' if ratio > 1.2 else '↓' if ratio < 0.8 else ' '
            print(f"    {cat:15s} {dist[cat]:.3f} (ratio={ratio:.2f}) {marker}")

    # P5: BIO largest THERMAL amplification, HERBAL closest to A
    bio_thermal = section_profiles.get('B', {}).get('THERMAL', 0) / max(dist_a['THERMAL'], 1e-10)
    herbal_js = section_js_from_a.get('H', 999)
    min_js_section = min(section_js_from_a.items(), key=lambda x: x[1]) if section_js_from_a else (None, None)

    # Check if BIO has highest THERMAL ratio among all sections
    thermal_ratios = {}
    for s, d in section_profiles.items():
        thermal_ratios[s] = d.get('THERMAL', 0) / max(dist_a['THERMAL'], 1e-10)

    bio_highest_thermal = (thermal_ratios.get('B', 0) == max(thermal_ratios.values())) if thermal_ratios else False
    herbal_closest = min_js_section[0] == 'H' if min_js_section[0] else False

    p5 = bio_highest_thermal and herbal_closest
    print(f"\n  P5 (BIO highest THERMAL amp, HERBAL closest to A):")
    print(f"    THERMAL ratios: {', '.join(f'{SECTION_MAP.get(s,s)}={r:.2f}' for s, r in sorted(thermal_ratios.items()))}")
    print(f"    JS from A: {', '.join(f'{SECTION_MAP.get(s,s)}={j:.4f}' for s, j in sorted(section_js_from_a.items()))}")
    print(f"    BIO highest THERMAL: {bio_highest_thermal}")
    print(f"    HERBAL closest to A: {herbal_closest} (closest={SECTION_MAP.get(min_js_section[0], min_js_section[0]) if min_js_section[0] else 'N/A'})")
    print(f"    P5: {'CONFIRMED' if p5 else 'FALSIFIED'}")

    return {
        'section_profiles': section_profiles,
        'section_js_from_a': section_js_from_a,
        'thermal_ratios_by_section': thermal_ratios,
        'closest_to_a': min_js_section[0] if min_js_section[0] else None,
        'P5_bio_thermal_herbal_closest': p5,
    }


def test5_per_middle_stability(data):
    """T5: Per-MIDDLE category stability vs usage shift."""
    print("\n=== T5: Per-MIDDLE Rank Stability ===")

    cc = data['cc']
    bridge_set = data['bridge_set']

    # MIDDLEs present in both A and B
    shared_middles = [m for m in bridge_set
                      if data['bridge_middle_a_counts'][m] > 0
                      and data['bridge_middle_b_counts'][m] > 0]
    print(f"  Bridge MIDDLEs in both A and B: {len(shared_middles)}")

    if len(shared_middles) < 5:
        print("  Insufficient shared MIDDLEs for rank analysis")
        return {'n_shared': len(shared_middles), 'test_possible': False}

    # Rank by frequency in A and B
    a_ranks = sorted(shared_middles, key=lambda m: data['bridge_middle_a_counts'][m], reverse=True)
    b_ranks = sorted(shared_middles, key=lambda m: data['bridge_middle_b_counts'][m], reverse=True)

    a_rank_map = {m: i for i, m in enumerate(a_ranks)}
    b_rank_map = {m: i for i, m in enumerate(b_ranks)}

    a_rank_arr = [a_rank_map[m] for m in shared_middles]
    b_rank_arr = [b_rank_map[m] for m in shared_middles]

    rho, p = spearmanr(a_rank_arr, b_rank_arr)
    print(f"  Overall rank correlation: rho={rho:.3f}, p={p:.6f}")

    # P6: Moderate rank disruption (rho 0.5-0.7)
    p6 = 0.5 <= rho <= 0.7
    print(f"  P6 (rho 0.5-0.7): {'CONFIRMED' if p6 else 'FALSIFIED'} (rho={rho:.3f})")

    # Per-category rank changes
    cat_rank_changes = defaultdict(list)
    for m in shared_middles:
        cat = cc.classify(m)
        if cat:
            rank_change = b_rank_map[m] - a_rank_map[m]  # negative = gained rank
            cat_rank_changes[cat].append(rank_change)

    print(f"\n  Per-category mean rank change (negative = gained rank in B):")
    cat_mean_changes = {}
    for cat in CATEGORIES:
        changes = cat_rank_changes.get(cat, [])
        if changes:
            mean_change = float(np.mean(changes))
            cat_mean_changes[cat] = mean_change
            print(f"    {cat:15s} mean_change={mean_change:+.1f} (n={len(changes)})")

    # Top gainers and losers
    rank_diffs = [(m, b_rank_map[m] - a_rank_map[m], cc.classify(m)) for m in shared_middles]
    rank_diffs.sort(key=lambda x: x[1])

    print(f"\n  Top 5 rank gainers (A→B):")
    for m, diff, cat in rank_diffs[:5]:
        print(f"    {m:15s} change={diff:+d} ({cat}), A_count={data['bridge_middle_a_counts'][m]}, B_count={data['bridge_middle_b_counts'][m]}")

    print(f"  Top 5 rank losers (A→B):")
    for m, diff, cat in rank_diffs[-5:]:
        print(f"    {m:15s} change={diff:+d} ({cat}), A_count={data['bridge_middle_a_counts'][m]}, B_count={data['bridge_middle_b_counts'][m]}")

    return {
        'n_shared': len(shared_middles),
        'rank_correlation_rho': float(rho),
        'rank_correlation_p': float(p),
        'P6_moderate_disruption': p6,
        'per_category_mean_rank_change': cat_mean_changes,
        'test_possible': True,
    }


def test6_dark_control(data):
    """T6: Dark pipeline as control group."""
    print("\n=== T6: Dark Pipeline Control Group ===")

    # Dark category profiles
    dark_profiles = {}
    for sys_name in ['A', 'AZC', 'B']:
        total = sum(data['dark_counts'][sys_name].values())
        if total > 0:
            dist = counts_to_distribution(data['dark_counts'][sys_name])
            dark_profiles[sys_name] = dist
            print(f"  Dark {sys_name} (n={total}):")
            for cat in CATEGORIES:
                print(f"    {cat:15s} {dist[cat]:.3f}")
        else:
            print(f"  Dark {sys_name}: NO TOKENS")
            dark_profiles[sys_name] = {c: 0.0 for c in CATEGORIES}

    # JS divergences for dark
    js_dark_a_b = js_divergence(dark_profiles.get('A', {}), dark_profiles.get('B', {}))
    js_dark_a_azc = js_divergence(dark_profiles.get('A', {}), dark_profiles.get('AZC', {}))

    # Compare to bridge JS
    bridge_dist_a = counts_to_distribution(data['bridge_counts']['A'])
    bridge_dist_b = counts_to_distribution(data['bridge_counts']['B'])
    js_bridge_a_b = js_divergence(bridge_dist_a, bridge_dist_b)

    print(f"\n  Dark A↔B JS: {js_dark_a_b:.4f}")
    print(f"  Bridge A↔B JS: {js_bridge_a_b:.4f}")

    # P7: Dark shows LESS redistribution than bridge
    p7 = js_dark_a_b < js_bridge_a_b
    print(f"  P7 (dark JS < bridge JS): {'CONFIRMED' if p7 else 'FALSIFIED'}")

    return {
        'dark_profiles': dark_profiles,
        'dark_totals': {s: sum(data['dark_counts'][s].values()) for s in ['A', 'AZC', 'B']},
        'js_dark_a_b': js_dark_a_b,
        'js_dark_a_azc': js_dark_a_azc,
        'js_bridge_a_b': js_bridge_a_b,
        'P7_dark_less_redistribution': p7,
    }


# ── Main ─────────────────────────────────────────────────────────────

def main():
    import time
    t0 = time.time()

    data = load_data()

    t1 = test1_system_profiles(data)
    t2 = test2_amplification(data)
    t3 = test3_azc_zone_mediation(data)
    t4 = test4_section_conditioned(data)
    t5 = test5_per_middle_stability(data)
    t6 = test6_dark_control(data)

    # ── Verdict ──────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print("PRE-REGISTERED PREDICTION RESULTS:")

    predictions = {
        'P1': t1.get('P1_significant_redistribution'),
        'P2': t1.get('P2_azc_intermediate'),
        'P3': t2.get('P3_thermal_amp_marking_staging_att'),
        'P4': t3.get('P4_s_transition_enrichment'),
        'P5': t4.get('P5_bio_thermal_herbal_closest'),
        'P6': t5.get('P6_moderate_disruption'),
        'P7': t6.get('P7_dark_less_redistribution'),
    }

    for p_id, result in predictions.items():
        status = 'CONFIRMED' if result is True else 'FALSIFIED' if result is False else 'INCONCLUSIVE'
        print(f"  {p_id}: {status}")

    confirmed = sum(1 for v in predictions.values() if v is True)
    falsified = sum(1 for v in predictions.values() if v is False)
    print(f"\n  Score: {confirmed}/7 confirmed, {falsified}/7 falsified")

    # Overall pipeline characterization
    js_ab = t1['js_a_b']
    if js_ab < 0.01:
        pipeline_type = 'PRESERVED'
    elif js_ab < 0.05:
        pipeline_type = 'WEAKLY_RESHAPED'
    else:
        pipeline_type = 'SIGNIFICANTLY_RESHAPED'

    verdict = (f"Pipeline type: {pipeline_type} (A↔B JS={js_ab:.4f}). "
               f"AZC closer to {t1['P2_azc_closer_to']}. "
               f"{confirmed}/7 predictions confirmed.")
    print(f"\nVERDICT: {verdict}")
    print(f"{'='*60}")

    elapsed = time.time() - t0
    print(f"\nCompleted in {elapsed:.1f}s")

    # Save results
    results = {
        'metadata': {
            'phase': 483,
            'name': 'CATEGORY_PIPELINE_TRACE',
            'n_bridge': len(data['bridge_set']),
            'n_dark': len(data['dark_set']),
            'elapsed_seconds': elapsed,
        },
        'T1_system_profiles': t1,
        'T2_amplification': t2,
        'T3_azc_zone': t3,
        'T4_section_conditioned': t4,
        'T5_rank_stability': t5,
        'T6_dark_control': t6,
        'predictions': predictions,
        'pipeline_type': pipeline_type,
        'verdict': verdict,
    }

    out_path = RESULTS_DIR / 'category_pipeline_trace.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(round_floats(results), f, indent=2, ensure_ascii=False)
    print(f"\nResults saved to {out_path}")


if __name__ == '__main__':
    main()
