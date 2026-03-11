"""
T3: Closure Packet Morphology x Response
Phase 574 - COUNTERFEIT_CLOSURE_THRESHOLD_RECOVERY_GATE_MAP

Identifies which closure packet **shapes** are counterfeitable in A2.
Uses packet-level morphology signatures (not crude per-line majority labels).

Four parts:
  Part 1 - Individual feature x profile (exploratory)
  Part 2 - Closure packet morphology signatures (MAIN ANALYSIS)
  Part 3 - Feature protection ranking
  Part 4 - Morphology x sub-R ablation correlation
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

# Packet signature features (binary)
PACKET_FEATURES = [
    'm_terminal_present',
    'high_opaque',       # opacity_opaque_frac >= 0.5
    'high_q4_hazard',    # q4_hazard_band == 'HIGH'
    'headless_involved',
    'has_e_head_support',
    'has_k_head_support',
    'has_a_head_closure',
    'high_cts',          # CTS > 0.5
    'armed',             # E_armed
    'compound_packet',   # E_compound
]

# Subset for packet strength score (matching grammar_band logic)
STRENGTH_FEATURES = ['m_terminal_present', 'high_opaque', 'high_cts', 'armed']


def extract_packet_features(ev):
    """Extract binary packet features from an enriched event."""
    return {
        'm_terminal_present': ev.get('m_terminal_present', False),
        'high_opaque': ev.get('opacity_opaque_frac', 0) >= 0.5,
        'high_q4_hazard': ev.get('q4_hazard_band', 'LOW') == 'HIGH',
        'headless_involved': ev.get('headless_involved', False),
        'has_e_head_support': ev.get('has_e_head_support', False),
        'has_k_head_support': ev.get('has_k_head_support', False),
        'has_a_head_closure': ev.get('has_a_head_closure', False),
        'high_cts': ev.get('CTS', 0) > 0.5,
        'armed': ev.get('E_armed', False),
        'compound_packet': ev.get('E_compound', False),
    }


def build_signature_string(pf):
    """Build a compound signature string from packet features."""
    active = [k for k in STRENGTH_FEATURES + ['headless_involved', 'has_e_head_support']
              if pf.get(k, False)]
    if not active:
        return 'bare'
    return '+'.join(sorted(active))


def weighted_mean(events, key, weight_key='event_confidence'):
    """Confidence-weighted mean of a field."""
    total_w = sum(e.get(weight_key, 1.0) for e in events)
    if total_w < 1e-12:
        return 0.0
    return sum(e[key] * e.get(weight_key, 1.0) for e in events) / total_w


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
            for k in range(i, j + 1):
                ranks[indexed[k]] = mean_rank
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


def main():
    t_start = time.time()
    print("=" * 70)
    print("T3: Closure Packet Morphology x Response")
    print("Phase 574 - COUNTERFEIT_CLOSURE_THRESHOLD_RECOVERY_GATE_MAP")
    print("=" * 70)

    # ---- Load T0 event matrix ----
    print("\n--- Loading T0 event matrix ---")
    t0_path = os.path.join(RESULTS_DIR, 't0_event_feature_assembly.json')
    with open(t0_path, 'r', encoding='utf-8') as f:
        t0 = json.load(f)
    events = t0['m1_events']
    per_folio_summary = t0['per_folio_summary']
    print(f"  Events loaded: {len(events)}")

    # ---- Load T1 sub-ablation results ----
    print("  Loading T1 sub-ablation results...")
    t1_path = os.path.join(RESULTS_DIR, 't1_recovery_gate_decomposition.json')
    with open(t1_path, 'r', encoding='utf-8') as f:
        t1 = json.load(f)
    per_folio_sub_abl = t1['per_folio_sub_ablation']

    profiles = sorted(set(e['profile'] for e in events))
    print(f"  Profiles: {profiles}")

    # Enrich events with packet features
    for ev in events:
        pf = extract_packet_features(ev)
        ev['_packet_features'] = pf
        ev['_signature'] = build_signature_string(pf)
        ev['_strength_score'] = sum(1 for f in STRENGTH_FEATURES if pf.get(f, False))

    # ================================================================
    # PART 1: Individual feature x profile (exploratory)
    # ================================================================
    print("\n--- Part 1: Individual feature x profile ---")
    feature_x_profile = {}

    explore_features = [
        ('dominant_terminal', lambda e: e.get('dominant_terminal', 'unknown')),
        ('dominant_head', lambda e: e.get('dominant_head', 'unknown')),
        ('opaque_frac_band', lambda e: e.get('opaque_frac_band', 'LOW')),
    ]

    for feat_name, feat_fn in explore_features:
        feature_x_profile[feat_name] = {}
        for profile in profiles:
            prof_events = [e for e in events if e['profile'] == profile]
            groups = defaultdict(list)
            for e in prof_events:
                groups[feat_fn(e)].append(e)

            feature_x_profile[feat_name][profile] = {}
            for val, grp in sorted(groups.items()):
                n = len(grp)
                if n < 3:
                    continue
                mean_dye = sum(e['DYE'] for e in grp) / n
                mean_ccs1 = sum(e['CCS1_folio'] for e in grp) / n
                w_adv = weighted_mean(grp, 'DYE_adv_event')
                feature_x_profile[feat_name][profile][str(val)] = {
                    'mean_dye': round(mean_dye, 6),
                    'mean_ccs1': round(mean_ccs1, 6),
                    'dye_adv': round(mean_dye - mean_ccs1, 6),
                    'weighted_dye_adv': round(w_adv, 6),
                    'n_events': n,
                }

    # ================================================================
    # PART 2: Packet morphology signatures (MAIN ANALYSIS)
    # ================================================================
    print("\n--- Part 2: Packet morphology signatures ---")

    # Individual packet feature x profile
    packet_feature_profile = {}
    for feat in PACKET_FEATURES:
        packet_feature_profile[feat] = {}
        for profile in profiles:
            prof_events = [e for e in events if e['profile'] == profile]
            present = [e for e in prof_events if e['_packet_features'].get(feat, False)]
            absent = [e for e in prof_events if not e['_packet_features'].get(feat, False)]

            p_adv = weighted_mean(present, 'DYE_adv_event') if len(present) >= 2 else None
            a_adv = weighted_mean(absent, 'DYE_adv_event') if len(absent) >= 2 else None

            packet_feature_profile[feat][profile] = {
                'n_present': len(present),
                'n_absent': len(absent),
                'present_weighted_adv': round(p_adv, 6) if p_adv is not None else None,
                'absent_weighted_adv': round(a_adv, 6) if a_adv is not None else None,
            }

    # Compound signature classification
    print("\n  Packet signature classification:")
    sig_groups = defaultdict(lambda: defaultdict(list))
    for e in events:
        sig_groups[e['_signature']][e['profile']].append(e)

    packet_signature_classification = {}
    for sig in sorted(sig_groups.keys()):
        total_n = sum(len(v) for v in sig_groups[sig].values())
        if total_n < 5:
            continue

        sig_result = {'n_total': total_n}
        profile_advs = {}
        for profile in profiles:
            evts = sig_groups[sig].get(profile, [])
            n = len(evts)
            if n >= 2:
                adv = weighted_mean(evts, 'DYE_adv_event')
                profile_advs[profile] = adv
                sig_result[profile] = {
                    'n': n,
                    'weighted_dye_adv': round(adv, 6),
                }
            else:
                sig_result[profile] = {'n': n, 'weighted_dye_adv': None}

        # Classify
        a2_adv = None
        non_a2_advs = []
        for p, adv in profile_advs.items():
            if 'A2' in p:
                a2_adv = adv
            else:
                non_a2_advs.append(adv)

        if a2_adv is not None and non_a2_advs:
            non_a2_mean = sum(non_a2_advs) / len(non_a2_advs)
            if a2_adv > 0 and non_a2_mean > 0:
                classification = 'RESISTANT'
            elif a2_adv < 0 and non_a2_mean < 0:
                classification = 'UNIVERSALLY_WEAK'
            elif a2_adv < 0 and non_a2_mean > 0:
                classification = 'A2_COUNTERFEITABLE'
            elif a2_adv > 0 and non_a2_mean <= 0:
                classification = 'A2_ONLY_POSITIVE'
            else:
                classification = 'MIXED'
        elif a2_adv is not None:
            classification = 'A2_COUNTERFEITABLE' if a2_adv < 0 else 'RESISTANT'
        else:
            classification = 'INSUFFICIENT_DATA'

        sig_result['classification'] = classification
        packet_signature_classification[sig] = sig_result
        print(f"    {sig}: {classification} (n={total_n})")

    # ================================================================
    # PART 3: Feature protection ranking
    # ================================================================
    print("\n--- Part 3: Feature protection ranking ---")
    feature_protection_ranking = {}

    for feat in PACKET_FEATURES:
        prot = {}
        for profile in profiles:
            prof_events = [e for e in events if e['profile'] == profile]
            present = [e for e in prof_events if e['_packet_features'].get(feat, False)]
            absent = [e for e in prof_events if not e['_packet_features'].get(feat, False)]

            if len(present) >= 2 and len(absent) >= 2:
                p_adv = weighted_mean(present, 'DYE_adv_event')
                a_adv = weighted_mean(absent, 'DYE_adv_event')
                prot[profile] = round(p_adv - a_adv, 6)
            else:
                prot[profile] = None

        feature_protection_ranking[feat] = prot

    # Sort by A2 protection
    a2_profile = [p for p in profiles if 'A2' in p]
    if a2_profile:
        a2p = a2_profile[0]
        sorted_features = sorted(PACKET_FEATURES,
                                  key=lambda f: feature_protection_ranking[f].get(a2p) or 0,
                                  reverse=True)
        print(f"\n  Feature protection ranking (by A2):")
        for feat in sorted_features:
            vals = feature_protection_ranking[feat]
            a2_val = vals.get(a2p, None)
            print(f"    {feat}: A2={a2_val}")

    # ================================================================
    # PART 4: Morphology x sub-R ablation correlation
    # ================================================================
    print("\n--- Part 4: Morphology x sub-R ablation correlation ---")
    morphology_ablation_correlations = {}

    # Build per-folio vectors
    a2_folios = [f for f in per_folio_summary
                 if per_folio_summary[f].get('profile') == 'A2_SEALED_RECIRCULATION'
                 and per_folio_summary[f].get('n_events', 0) > 0]

    morph_features_folio = ['mean_CTS', 'strong_frac', 'opacity_frac',
                            'm_terminal_frac', 'headless_frac', 'k_head_frac']
    sub_abl_keys = ['NO_R1_C_ONLY', 'NO_R4_C_ONLY', 'NO_R1', 'NO_R4']

    if len(a2_folios) >= 5:
        for mf in morph_features_folio:
            morphology_ablation_correlations[mf] = {}
            morph_vals = [per_folio_summary[f].get(mf, 0) for f in a2_folios]

            for sa in sub_abl_keys:
                abl_vals = []
                for f in a2_folios:
                    abl_data = per_folio_sub_abl.get(f, {}).get('sub_ablations', {})
                    abl_vals.append(abl_data.get(sa, {}).get('delta_m4f_dye', 0))

                rho = spearman_rank(morph_vals, abl_vals)
                morphology_ablation_correlations[mf][sa] = {
                    'rho': round(rho, 4),
                    'n': len(a2_folios),
                }

        print(f"  A2 folios used: {len(a2_folios)}")
        for mf in morph_features_folio:
            corrs = morphology_ablation_correlations[mf]
            r1c = corrs.get('NO_R1_C_ONLY', {}).get('rho', 0)
            r4c = corrs.get('NO_R4_C_ONLY', {}).get('rho', 0)
            print(f"    {mf}: R1_C rho={r1c:.3f}, R4_C rho={r4c:.3f}")
    else:
        print(f"  Insufficient A2 folios ({len(a2_folios)}) for correlation analysis")

    # ================================================================
    # Save output
    # ================================================================
    print("\n--- Saving output ---")
    os.makedirs(RESULTS_DIR, exist_ok=True)

    # Count classifications
    class_counts = Counter(v['classification']
                           for v in packet_signature_classification.values())
    print(f"\n  Signature classifications: {dict(class_counts)}")

    output = {
        'metadata': {
            'phase': '574',
            'script': 't3_morphology_response.py',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'elapsed_seconds': round(time.time() - t_start, 2),
            'n_events': len(events),
            'n_signatures': len(packet_signature_classification),
            'signature_classification_counts': dict(class_counts),
        },
        'feature_x_profile': feature_x_profile,
        'packet_feature_profile': packet_feature_profile,
        'packet_signature_classification': packet_signature_classification,
        'feature_protection_ranking': feature_protection_ranking,
        'morphology_ablation_correlations': morphology_ablation_correlations,
    }

    out_path = os.path.join(RESULTS_DIR, 't3_morphology_response.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=1, default=str)
    print(f"  Written: {out_path}")
    print(f"  Size: {os.path.getsize(out_path):,} bytes")
    print(f"\nDone in {time.time() - t_start:.1f}s")


if __name__ == '__main__':
    main()
