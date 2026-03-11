"""
T0: Corpus-Wide Tiered Classification + Burden Calibration
Phase 576 - CLOSURE_REGIME_ADMISSION_GATE

Classifies every line in 76 eligible folios using the 3-tier system:
  Layer 1: Exact signature match (10 known + 1 threshold from Phase 574 T3)
  Layer 2: Family rule (protective pair, prone pattern)
  Layer 3: Fallback (AUTH_AMBIGUOUS)

Also computes:
  - Intrinsic armedness proxy for ALL lines (Q4 opaque + m-terminal)
  - Burden calibration from 12 representative folios
  - M1 agreement with Phase 574 T0 signatures
"""

import json
import sys
import os
import time
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter, defaultdict

PROJECT_ROOT = str(Path(__file__).resolve().parents[3])
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

RESULTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'results')

# ---------------------------------------------------------------------------
# Imports from apparatus hierarchy
# ---------------------------------------------------------------------------
from phases.FOLIO_SPECIFIC_APPARATUS_PILOT.scripts.t2_folio_apparatus import (
    FolioSpecificApparatus, SV_INDEX, EQUILIBRIUM, N_VARS,
)
from phases.DEMAND_SPECIFIC_RECOVERY_METRIC_REFACTOR.scripts.t1_enhanced_event_trace import (
    run_enhanced_event_trace, sort_key, compute_infra_scores,
)

# ---------------------------------------------------------------------------
# Signature tables from Phase 574 T3 + Phase 575 T0
# ---------------------------------------------------------------------------
KNOWN_RESISTANT = {
    'armed+has_e_head_support+headless_involved',
    'armed+has_e_head_support+headless_involved+high_cts+high_opaque+m_terminal_present',
    'armed+has_e_head_support+headless_involved+high_cts+m_terminal_present',
    'has_e_head_support+headless_involved',
    'has_e_head_support+headless_involved+high_cts+m_terminal_present',
}

KNOWN_COUNTERFEITABLE = {
    'armed+has_e_head_support+headless_involved+high_opaque',
    'has_e_head_support',
    'has_e_head_support+headless_involved+high_opaque',
    'has_e_head_support+headless_involved+m_terminal_present',
    'headless_involved',
}

KNOWN_THRESHOLD = {
    'armed+has_e_head_support+headless_involved+high_cts',  # INSUFFICIENT_DATA
}

# Packet signature features (binary) — matches Phase 574 T3 logic
STRENGTH_FEATURES = ['m_terminal_present', 'high_opaque', 'high_cts', 'armed']
SIGNATURE_FEATURES = STRENGTH_FEATURES + ['headless_involved', 'has_e_head_support']


def classify_line(signature, features):
    """Tiered legitimacy classifier (6 classes).

    Layer 1: Exact signature match
    Layer 2: Family rule
    Layer 3: Fallback
    """
    if signature in KNOWN_RESISTANT:
        return 'AUTH_RESISTANT'
    if signature in KNOWN_COUNTERFEITABLE:
        return 'AUTH_COUNTERFEITABLE'
    if signature in KNOWN_THRESHOLD:
        return 'AUTH_THRESHOLD'
    # Layer 2: family rules
    if features.get('headless_involved') and features.get('has_e_head_support'):
        return 'AUTH_PROTECTIVE'
    if features.get('high_opaque') and not features.get('high_cts'):
        return 'AUTH_PRONE'
    return 'AUTH_AMBIGUOUS'


def build_signature_string(features):
    """Build compound signature string from binary features."""
    active = [k for k in SIGNATURE_FEATURES if features.get(k, False)]
    if not active:
        return 'bare'
    return '+'.join(sorted(active))


def main():
    t_start = time.time()
    print("=" * 70)
    print("T0: Corpus-Wide Tiered Classification + Burden Calibration")
    print("Phase 576 - CLOSURE_REGIME_ADMISSION_GATE")
    print("=" * 70)

    # ---- Load data ----
    print("\n--- Loading data ---")

    dd_path = os.path.join(PROJECT_ROOT, 'phases',
                           'WITHIN_DOMAIN_COMPOSITIONAL_CONTROL', 'results',
                           't1_domain_decomposition.json')
    with open(dd_path, 'r', encoding='utf-8') as f:
        dd = json.load(f)
    domain_tokens = dd['corpus_tokens']
    print(f"  Domain tokens: {len(domain_tokens)}")

    setup_path = os.path.join(PROJECT_ROOT,
        'phases/PRODUCTIVE_DISRUPTION_EXPANSION/results/t1_full_scale_setup.json')
    with open(setup_path) as f:
        setup = json.load(f)
    eligible_folios = setup['eligible_folios']
    folio_configs = setup['folio_configs']
    print(f"  Eligible folios: {len(eligible_folios)}")

    cts_path = os.path.join(PROJECT_ROOT, 'phases', 'SECTION_TEMPLATE_TRACE_EXECUTOR',
                            'results', 't7_closure_cts.json')
    with open(cts_path) as f:
        cts_raw = json.load(f)
    cts_data = {}
    if 'line_cts' in cts_raw:
        for key, val in cts_raw['line_cts'].items():
            cts_data[key] = val.get('cts', 0.0) if isinstance(val, dict) else float(val)
    elif 'cts_scores' in cts_raw:
        for key, val in cts_raw['cts_scores'].items():
            cts_data[key] = (val.get('cts', val.get('score', 0.0))
                             if isinstance(val, dict) else float(val))

    # Load Phase 574 T0 events (for M1 agreement validation)
    p574_t0_path = os.path.join(PROJECT_ROOT,
        'phases/COUNTERFEIT_CLOSURE_THRESHOLD_RECOVERY_GATE_MAP/results/t0_event_feature_assembly.json')
    with open(p574_t0_path) as f:
        p574_t0 = json.load(f)
    m1_events = p574_t0['m1_events']
    print(f"  Phase 574 M1 events: {len(m1_events)}")

    # Load event taxonomy + line packets + tokens (for burden calibration)
    phases_dir = os.path.join(PROJECT_ROOT, 'phases')
    with open(os.path.join(phases_dir, 'SECTION_TEMPLATE_TRACE_EXECUTOR',
                           'results', 't3_line_packets.json')) as f:
        line_packets = json.load(f)['line_packets']
    with open(os.path.join(phases_dir, 'VIRTUAL_APPARATUS_COUPLING',
                           'results', 't2b_supervisory_interface_unrouted.json')) as f:
        all_tokens = json.load(f)['token_signals']
    with open(os.path.join(phases_dir, 'EVENTIVE_CLOSURE_PACKETS',
                           'results', 't1_event_taxonomy.json')) as f:
        event_map = json.load(f)['event_map']

    # ---- Build per-line morphology index ----
    print("\n--- Building per-line morphology index ---")
    eligible_set = set(eligible_folios)

    # Group domain tokens by (folio, line)
    line_token_groups = defaultdict(list)
    for tok in domain_tokens:
        if tok['folio'] in eligible_set:
            key = f"{tok['folio']}|{tok['line']}"
            line_token_groups[key].append(tok)

    print(f"  Lines in index: {len(line_token_groups)}")

    # ---- Compute intrinsic armedness proxy for ALL lines ----
    print("\n--- Computing intrinsic armedness proxy ---")

    # Group lines by section for section-relative medians
    section_q4_rates = defaultdict(list)
    line_q4_data = {}

    for line_key, tokens in line_token_groups.items():
        folio = line_key.split('|')[0]
        section = folio_configs.get(folio, {}).get('section', 'unknown')
        n = len(tokens)
        if n == 0:
            continue

        # Q4: last quintile
        q4_start = max(0, n - max(1, n // 5))
        q4_tokens = tokens[q4_start:]

        # Q4 opaque-terminal fraction
        n_q4 = len(q4_tokens)
        n_opaque = sum(1 for t in q4_tokens if t.get('terminal_opacity') == 'OPAQUE')
        q4_opaque_rate = n_opaque / n_q4 if n_q4 > 0 else 0.0

        # m-terminal in Q4
        m_in_q4 = any(t.get('term') == 'm' for t in q4_tokens)

        line_q4_data[line_key] = {
            'q4_opaque_rate': q4_opaque_rate,
            'm_in_q4': m_in_q4,
            'section': section,
        }
        section_q4_rates[section].append(q4_opaque_rate)

    # Compute section medians
    section_medians = {}
    for section, rates in section_q4_rates.items():
        sr = sorted(rates)
        section_medians[section] = sr[len(sr) // 2]
        print(f"  Section {section}: median Q4 opaque rate = {section_medians[section]:.4f} (n={len(sr)})")

    # Assign armedness proxy
    n_armed = 0
    n_unarmed = 0
    for line_key, q4d in line_q4_data.items():
        median = section_medians.get(q4d['section'], 0.5)
        armed = (q4d['q4_opaque_rate'] > median) or q4d['m_in_q4']
        q4d['armed_proxy'] = armed
        if armed:
            n_armed += 1
        else:
            n_unarmed += 1

    print(f"  Armed: {n_armed}, Unarmed: {n_unarmed}")

    # ---- Compute morphological features for ALL lines ----
    print("\n--- Computing per-line morphological features ---")

    per_line_classification = {}
    class_counter = Counter()

    for line_key, tokens in line_token_groups.items():
        folio = line_key.split('|')[0]
        n = len(tokens)
        if n == 0:
            continue

        # Binary features
        headless_involved = any(t.get('headless_subtype') is not None for t in tokens)
        has_e_head_support = any(t.get('head') == 'e' for t in tokens)
        m_terminal_present = any(t.get('term') == 'm' for t in tokens)

        # Opacity
        n_opaque = sum(1 for t in tokens if t.get('terminal_opacity') == 'OPAQUE')
        opacity_frac = n_opaque / n
        high_opaque = opacity_frac >= 0.5

        # CTS
        cts = cts_data.get(line_key, 0.0)
        high_cts = cts > 0.5

        # Armedness proxy
        q4d = line_q4_data.get(line_key, {})
        armed_proxy = q4d.get('armed_proxy', False)

        features = {
            'headless_involved': headless_involved,
            'has_e_head_support': has_e_head_support,
            'm_terminal_present': m_terminal_present,
            'high_opaque': high_opaque,
            'high_cts': high_cts,
            'armed': armed_proxy,
        }

        signature = build_signature_string(features)
        legit_class = classify_line(signature, features)
        class_counter[legit_class] += 1

        per_line_classification[line_key] = {
            'class': legit_class,
            'signature': signature,
            'features': features,
            'armed_proxy': armed_proxy,
            'cts': round(cts, 4),
            'opacity_frac': round(opacity_frac, 4),
            'n_tokens': n,
        }

    print(f"\n  Lines classified: {len(per_line_classification)}")
    print(f"  Class distribution:")
    for cls, cnt in sorted(class_counter.items()):
        pct = cnt / len(per_line_classification) * 100
        print(f"    {cls}: {cnt} ({pct:.1f}%)")

    # ---- Profile breakdown ----
    profile_class_counts = defaultdict(lambda: Counter())
    for line_key, info in per_line_classification.items():
        folio = line_key.split('|')[0]
        profile = folio_configs.get(folio, {}).get('profile', 'unknown')
        profile_class_counts[profile][info['class']] += 1

    class_distribution = {}
    for cls in sorted(class_counter.keys()):
        profile_breakdown = {}
        for profile in sorted(profile_class_counts.keys()):
            profile_breakdown[profile] = profile_class_counts[profile].get(cls, 0)
        class_distribution[cls] = {
            'n_lines': class_counter[cls],
            'pct': round(class_counter[cls] / len(per_line_classification) * 100, 2),
            'profile_breakdown': profile_breakdown,
        }

    # ---- M1 agreement validation ----
    print("\n--- M1 agreement validation ---")
    # Compare T0 classifications against Phase 574 T3 signatures
    n_matched = 0
    n_total = 0
    mismatches = []

    for ev in m1_events:
        line_key = ev.get('line_key', '')
        if line_key not in per_line_classification:
            continue
        n_total += 1

        # Build Phase 574's signature for this event
        pf_574 = {
            'm_terminal_present': ev.get('m_terminal_present', False),
            'high_opaque': ev.get('opacity_opaque_frac', 0) >= 0.5,
            'high_cts': ev.get('CTS', 0) > 0.5,
            'armed': ev.get('E_armed', False),
            'headless_involved': ev.get('headless_involved', False),
            'has_e_head_support': ev.get('has_e_head_support', False),
        }
        sig_574 = build_signature_string(pf_574)

        # Our T0 signature
        sig_576 = per_line_classification[line_key]['signature']

        if sig_574 == sig_576:
            n_matched += 1
        else:
            mismatches.append({
                'line_key': line_key,
                'sig_574': sig_574,
                'sig_576': sig_576,
            })

    agreement_pct = n_matched / n_total * 100 if n_total > 0 else 0
    print(f"  M1 events checked: {n_total}")
    print(f"  Signature agreement: {n_matched}/{n_total} ({agreement_pct:.1f}%)")
    if mismatches:
        print(f"  Mismatches (first 5): {mismatches[:5]}")

    # ---- Burden calibration ----
    print("\n--- Burden calibration ---")
    # Run 12 representative folios through ungated event trace to capture
    # pre-close burden (max(|C-0.5|, |X-0.5|) at CLOSE line boundaries)

    all_folios_data = setup.get('all_folios', eligible_folios)
    folio_infra = compute_infra_scores(all_folios_data)

    # Pick 4 folios per profile
    profile_folios = defaultdict(list)
    for f in eligible_folios:
        p = folio_configs[f]['profile']
        profile_folios[p].append(f)

    calibration_folios = []
    for profile in sorted(profile_folios.keys()):
        pf = profile_folios[profile]
        calibration_folios.extend(pf[:4])
    calibration_folios = calibration_folios[:12]
    print(f"  Calibration folios: {calibration_folios}")

    tokens_by_folio = defaultdict(list)
    for tok in all_tokens:
        if tok['folio'] in eligible_set:
            tokens_by_folio[tok['folio']].append(tok)

    burden_values = []
    burden_by_class = defaultdict(list)

    for folio in calibration_folios:
        fc = folio_configs[folio]
        config_mode = folio_infra.get(folio, {}).get('config_mode', 'H1_MEDIUM_INFRA')
        tokens = tokens_by_folio.get(folio, [])
        if not tokens:
            continue

        app = FolioSpecificApparatus(
            profile=fc['profile'], config_mode=config_mode, folio=folio,
            f1=fc['F1'], f2=fc['F2'], f3=fc['F3'], f4_raw=fc['F4_raw'], f5=fc['F5'])

        sorted_toks = sorted(tokens, key=sort_key)
        result = run_enhanced_event_trace(app, sorted_toks, line_packets, cts_data, event_map)

        # Extract pre-close burden from CLOSE events
        for ev in result.get('per_event_detail', []):
            cps = ev.get('close_pre_state')
            if cps is None:
                continue
            c_dev = abs(cps[SV_INDEX['C']] - EQUILIBRIUM)
            x_dev = abs(cps[SV_INDEX['X']] - EQUILIBRIUM)
            burden = max(c_dev, x_dev)
            burden_values.append(burden)

            lk = ev.get('line_key', '')
            cls = per_line_classification.get(lk, {}).get('class', 'AUTH_AMBIGUOUS')
            burden_by_class[cls].append(burden)

    if burden_values:
        sv = sorted(burden_values)
        n_b = len(sv)
        q1_burden = sv[n_b // 4]
        median_burden = sv[n_b // 2]
        q3_burden = sv[3 * n_b // 4]
        mean_burden = sum(sv) / n_b

        # Recommended threshold: between Q1 and 2*Q1
        recommended_threshold = round((q1_burden + 2 * q1_burden) / 2, 4)
        # Clamp to [0.05, 0.20]
        recommended_threshold = max(0.05, min(0.20, recommended_threshold))

        print(f"  Burden distribution (n={n_b}):")
        print(f"    Q1={q1_burden:.4f}, median={median_burden:.4f}, Q3={q3_burden:.4f}, mean={mean_burden:.4f}")
        print(f"    Recommended threshold: {recommended_threshold}")

        burden_calibration = {
            'n_events': n_b,
            'q1': round(q1_burden, 6),
            'median': round(median_burden, 6),
            'q3': round(q3_burden, 6),
            'mean': round(mean_burden, 6),
            'recommended_threshold': recommended_threshold,
            'by_class': {
                cls: {
                    'n': len(vals),
                    'mean': round(sum(vals) / len(vals), 6) if vals else 0,
                    'median': round(sorted(vals)[len(vals) // 2], 6) if vals else 0,
                }
                for cls, vals in burden_by_class.items()
            },
        }
    else:
        print("  WARNING: No burden data collected!")
        recommended_threshold = 0.10
        burden_calibration = {
            'n_events': 0,
            'recommended_threshold': 0.10,
        }

    # ---- Verification ----
    print("\n--- Verification ---")
    n_classified = len(per_line_classification)
    v_lines = n_classified >= 2300
    v_agreement = agreement_pct >= 90
    v_all_classes = len(class_counter) == 6
    v_ambiguous = class_counter.get('AUTH_AMBIGUOUS', 0) / n_classified < 0.30 if n_classified > 0 else False

    print(f"  Lines classified >= 2300: {v_lines} ({n_classified})")
    print(f"  M1 agreement >= 90%: {v_agreement} ({agreement_pct:.1f}%)")
    print(f"  All 6 classes populated: {v_all_classes} ({len(class_counter)} classes)")
    print(f"  AUTH_AMBIGUOUS < 30%: {v_ambiguous}")

    # ---- Save output ----
    print("\n--- Saving output ---")
    os.makedirs(RESULTS_DIR, exist_ok=True)

    output = {
        'metadata': {
            'phase': '576',
            'script': 't0_corpus_classification.py',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'elapsed_seconds': round(time.time() - t_start, 2),
            'n_eligible_folios': len(eligible_folios),
            'n_lines_classified': n_classified,
        },
        'per_line_classification': per_line_classification,
        'class_distribution': class_distribution,
        'armedness_stats': {
            'n_armed': n_armed,
            'n_unarmed': n_unarmed,
            'section_medians': {k: round(v, 6) for k, v in section_medians.items()},
        },
        'burden_calibration': burden_calibration,
        'm1_agreement': {
            'n_matched': n_matched,
            'n_total': n_total,
            'pct': round(agreement_pct, 2),
            'n_mismatches': len(mismatches),
            'mismatch_samples': mismatches[:10],
        },
        'verification': {
            'lines_ge_2300': v_lines,
            'agreement_ge_90': v_agreement,
            'all_6_classes': v_all_classes,
            'ambiguous_lt_30': v_ambiguous,
            'all_passed': v_lines and v_agreement and v_all_classes and v_ambiguous,
        },
    }

    out_path = os.path.join(RESULTS_DIR, 't0_corpus_classification.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=1, default=str)
    print(f"  Written: {out_path}")
    print(f"  Size: {os.path.getsize(out_path):,} bytes")
    print(f"\nDone in {time.time() - t_start:.1f}s")


if __name__ == '__main__':
    main()
