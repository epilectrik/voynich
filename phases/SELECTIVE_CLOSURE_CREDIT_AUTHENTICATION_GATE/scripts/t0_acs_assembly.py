"""
T0: ACS Assembly + Empirical Threshold Calibration
Phase 575 - SELECTIVE_CLOSURE_CREDIT_AUTHENTICATION_GATE

Computes per-event Authentication Closure Score (ACS) using configuration-based
scoring with C1645 signature offset table + additive morphology fallback.
Validates ACS is not redundant with CTS. Derives empirical gate thresholds
from ACS distributions rather than hardcoded values.
"""

import json
import sys
import os
import math
import time
from pathlib import Path
from datetime import datetime, timezone
from collections import defaultdict

PROJECT_ROOT = str(Path(__file__).resolve().parents[3])
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

RESULTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'results')

# ============================================================================
# ACS Configuration: Signature Offset Table (from C1645)
# ============================================================================
# Normalized from Phase 574 T3 A2 DYE_adv values to [0.05, 0.90]
# min_adv = -0.134 (has_e_head_support+headless_involved+high_opaque)
# max_adv = +0.122 (armed+has_e_head_support+headless_involved+high_cts+m_terminal_present)
# normalized = 0.05 + 0.85 * (adv - min_adv) / (max_adv - min_adv)

SIGNATURE_OFFSET_TABLE = {
    # RESISTANT signatures -> high scores
    'armed+has_e_head_support+headless_involved+high_cts+m_terminal_present': 0.90,
    'armed+has_e_head_support+headless_involved': 0.85,
    'has_e_head_support+headless_involved+high_cts+m_terminal_present': 0.80,
    'armed+has_e_head_support+headless_involved+high_cts+high_opaque+m_terminal_present': 0.72,
    'has_e_head_support+headless_involved': 0.70,
    # A2_COUNTERFEITABLE signatures -> low scores
    'headless_involved': 0.30,
    'has_e_head_support+headless_involved+m_terminal_present': 0.28,
    'armed+has_e_head_support+headless_involved+high_opaque': 0.25,
    'has_e_head_support': 0.10,
    'has_e_head_support+headless_involved+high_opaque': 0.05,
}

SIGNATURE_CLASSES = {
    'armed+has_e_head_support+headless_involved+high_cts+m_terminal_present': 'RESISTANT',
    'armed+has_e_head_support+headless_involved': 'RESISTANT',
    'has_e_head_support+headless_involved+high_cts+m_terminal_present': 'RESISTANT',
    'armed+has_e_head_support+headless_involved+high_cts+high_opaque+m_terminal_present': 'RESISTANT',
    'has_e_head_support+headless_involved': 'RESISTANT',
    'headless_involved': 'A2_COUNTERFEITABLE',
    'has_e_head_support+headless_involved+m_terminal_present': 'A2_COUNTERFEITABLE',
    'armed+has_e_head_support+headless_involved+high_opaque': 'A2_COUNTERFEITABLE',
    'has_e_head_support': 'A2_COUNTERFEITABLE',
    'has_e_head_support+headless_involved+high_opaque': 'A2_COUNTERFEITABLE',
}

# Additive morphology weights (from Phase 574 T3 protection ranking)
MORPH_WEIGHTS = {
    'headless_involved': 0.126,
    'high_cts': 0.107,
    'armed': 0.092,
    'compound_packet': 0.088,
    'm_terminal_present': 0.063,
    'high_opaque': 0.006,
    'has_e_head_support': 0.005,
}

ALPHA = 0.60  # CTS weight in ACS composite

# Packet features for signature building (must match T3 logic)
STRENGTH_FEATURES = ['m_terminal_present', 'high_opaque', 'high_cts', 'armed']


def extract_packet_features(ev):
    """Extract binary packet features from an enriched event (matches T3 logic)."""
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
    """Build compound signature string from packet features (matches T3 logic)."""
    active = [k for k in STRENGTH_FEATURES + ['headless_involved', 'has_e_head_support']
              if pf.get(k, False)]
    if not active:
        return 'bare'
    return '+'.join(sorted(active))


def additive_fallback(pf):
    """Compute additive morphology score for unknown signatures."""
    score = sum(w for feat, w in MORPH_WEIGHTS.items() if pf.get(feat, False))
    max_possible = sum(MORPH_WEIGHTS.values())
    return min(1.0, score / max_possible) if max_possible > 0 else 0.5


def compute_acs(cts, signature, packet_features):
    """Compute Authentication Closure Score.

    ACS = alpha * CTS + (1 - alpha) * config_score
    config_score from signature table or additive fallback.
    """
    if signature in SIGNATURE_OFFSET_TABLE:
        config_score = SIGNATURE_OFFSET_TABLE[signature]
        source = 'table'
    else:
        config_score = additive_fallback(packet_features)
        source = 'fallback'
    acs = ALPHA * min(1.0, max(0.0, cts)) + (1 - ALPHA) * config_score
    return acs, config_score, source


def spearman_rank(x, y):
    """Compute Spearman rank correlation (pure Python)."""
    n = len(x)
    if n < 3:
        return 0.0

    def rank_data(vals):
        indexed = sorted(range(n), key=lambda i: vals[i])
        ranks = [0.0] * n
        i = 0
        while i < n:
            j = i
            while j < n - 1 and vals[indexed[j + 1]] == vals[indexed[j]]:
                j += 1
            avg_rank = (i + j) / 2.0 + 1
            for k in range(i, j + 1):
                ranks[indexed[k]] = avg_rank
            i = j + 1
        return ranks

    rx = rank_data(x)
    ry = rank_data(y)

    mean_rx = sum(rx) / n
    mean_ry = sum(ry) / n
    num = sum((rx[i] - mean_rx) * (ry[i] - mean_ry) for i in range(n))
    den_x = math.sqrt(sum((rx[i] - mean_rx) ** 2 for i in range(n)))
    den_y = math.sqrt(sum((ry[i] - mean_ry) ** 2 for i in range(n)))
    if den_x < 1e-12 or den_y < 1e-12:
        return 0.0
    return num / (den_x * den_y)


def running_mean(values, window):
    """Compute running mean with given window size."""
    n = len(values)
    result = []
    for i in range(n):
        lo = max(0, i - window // 2)
        hi = min(n, lo + window)
        if hi - lo < window:
            lo = max(0, hi - window)
        segment = values[lo:hi]
        result.append(sum(segment) / len(segment) if segment else 0.0)
    return result


def main():
    t0 = time.time()
    os.makedirs(RESULTS_DIR, exist_ok=True)

    # ================================================================
    # Load Phase 574 T0 events
    # ================================================================
    t0_path = os.path.join(PROJECT_ROOT,
        'phases/COUNTERFEIT_CLOSURE_THRESHOLD_RECOVERY_GATE_MAP/results/t0_event_feature_assembly.json')
    with open(t0_path) as f:
        t0_data = json.load(f)

    events = t0_data['m1_events']
    print(f"Loaded {len(events)} M1 events")

    # ================================================================
    # Part 1: Compute ACS for each event
    # ================================================================
    n_table = 0
    n_fallback = 0

    for ev in events:
        pf = extract_packet_features(ev)
        sig = build_signature_string(pf)
        acs, config_score, source = compute_acs(ev.get('CTS', 0), sig, pf)

        ev['ACS'] = round(acs, 6)
        ev['config_score'] = round(config_score, 6)
        ev['signature'] = sig
        ev['signature_source'] = source
        ev['packet_features'] = pf

        if source == 'table':
            n_table += 1
        else:
            n_fallback += 1

    coverage_pct = n_table / len(events) * 100 if events else 0
    print(f"Signature coverage: {n_table} table ({coverage_pct:.1f}%), {n_fallback} fallback")

    # ================================================================
    # Part 2: CTS-ACS correlation check
    # ================================================================
    cts_values = [ev.get('CTS', 0) for ev in events]
    acs_values = [ev['ACS'] for ev in events]
    rho = spearman_rank(cts_values, acs_values)
    print(f"CTS-ACS Spearman rho: {rho:.4f}")

    # ================================================================
    # Part 3: Incremental discrimination check (A2 only)
    # ================================================================
    a2_events = [ev for ev in events if 'A2' in ev.get('profile', '')]

    # Mean CTS and ACS for RESISTANT vs A2_COUNTERFEITABLE in A2
    resistant_cts = []
    resistant_acs = []
    counterfeit_cts = []
    counterfeit_acs = []

    for ev in a2_events:
        sig_class = SIGNATURE_CLASSES.get(ev['signature'])
        if sig_class == 'RESISTANT':
            resistant_cts.append(ev.get('CTS', 0))
            resistant_acs.append(ev['ACS'])
        elif sig_class == 'A2_COUNTERFEITABLE':
            counterfeit_cts.append(ev.get('CTS', 0))
            counterfeit_acs.append(ev['ACS'])

    cts_gap = 0.0
    acs_gap = 0.0
    if resistant_cts and counterfeit_cts:
        cts_gap = (sum(resistant_cts) / len(resistant_cts)) - (sum(counterfeit_cts) / len(counterfeit_cts))
        acs_gap = (sum(resistant_acs) / len(resistant_acs)) - (sum(counterfeit_acs) / len(counterfeit_acs))

    print(f"Discrimination: CTS gap={cts_gap:.4f}, ACS gap={acs_gap:.4f}, ACS better={acs_gap > cts_gap}")

    # ================================================================
    # Part 4: ACS distribution per profile
    # ================================================================
    profile_acs = defaultdict(list)
    for ev in events:
        profile_acs[ev.get('profile', 'unknown')].append(ev['ACS'])

    acs_distribution = {}
    for prof, vals in sorted(profile_acs.items()):
        sv = sorted(vals)
        n = len(sv)
        acs_distribution[prof] = {
            'mean': round(sum(sv) / n, 6),
            'median': round(sv[n // 2], 6),
            'q25': round(sv[max(0, n // 4)], 6),
            'q75': round(sv[min(n - 1, 3 * n // 4)], 6),
            'n': n,
        }
        print(f"  {prof}: mean={acs_distribution[prof]['mean']:.4f}, "
              f"median={acs_distribution[prof]['median']:.4f}, n={n}")

    # ================================================================
    # Part 5: Empirical threshold calibration
    # ================================================================
    empirical_thresholds = {}

    # A2 threshold: find ACS zero-crossing of DYE_adv
    if a2_events:
        a2_sorted = sorted(a2_events, key=lambda e: e['ACS'])
        window = max(5, len(a2_sorted) // 5)
        indicators = [1.0 if e.get('DYE_adv_event', 0) > 0 else 0.0 for e in a2_sorted]
        rm = running_mean(indicators, window)
        acs_vals_sorted = [e['ACS'] for e in a2_sorted]

        zero_crossing = None
        for i in range(1, len(rm)):
            if rm[i - 1] < 0.5 <= rm[i]:
                frac = (0.5 - rm[i - 1]) / max(rm[i] - rm[i - 1], 1e-12)
                zero_crossing = acs_vals_sorted[i - 1] + frac * (acs_vals_sorted[i] - acs_vals_sorted[i - 1])
                break

        if zero_crossing is None:
            # Fallback: use median ACS
            zero_crossing = acs_distribution.get('A2_SEALED_RECIRCULATION', {}).get('median', 0.35)

        a2_acs_sorted = sorted(e['ACS'] for e in a2_events)
        n_a2 = len(a2_acs_sorted)

        empirical_thresholds['CONSERVATIVE'] = {
            'A2': round(a2_acs_sorted[max(0, int(0.4 * n_a2))], 6),
        }
        empirical_thresholds['MODERATE'] = {
            'A2': round(zero_crossing, 6),
        }
        empirical_thresholds['AGGRESSIVE'] = {
            'A2': round(a2_acs_sorted[min(n_a2 - 1, int(0.6 * n_a2))], 6),
        }

        print(f"\nA2 empirical thresholds:")
        print(f"  CONSERVATIVE (40th pctile): {empirical_thresholds['CONSERVATIVE']['A2']:.4f}")
        print(f"  MODERATE (zero-crossing):   {empirical_thresholds['MODERATE']['A2']:.4f}")
        print(f"  AGGRESSIVE (60th pctile):   {empirical_thresholds['AGGRESSIVE']['A2']:.4f}")

    # Non-A2 thresholds: near-floor (5th/10th percentile)
    non_a2_events = [ev for ev in events if 'A2' not in ev.get('profile', '')]
    if non_a2_events:
        non_a2_acs = sorted(e['ACS'] for e in non_a2_events)
        n_na2 = len(non_a2_acs)
        a1_thresh = round(non_a2_acs[max(0, int(0.05 * n_na2))], 6)
        a3_thresh = round(non_a2_acs[max(0, int(0.10 * n_na2))], 6)
        for level in empirical_thresholds:
            empirical_thresholds[level]['A1'] = a1_thresh
            empirical_thresholds[level]['A3'] = a3_thresh
        print(f"  A1 threshold (5th pctile):  {a1_thresh:.4f}")
        print(f"  A3 threshold (10th pctile): {a3_thresh:.4f}")

    # ================================================================
    # Part 6: Gate activation rates per profile per setting
    # ================================================================
    gate_activation_rates = {}
    for setting_name, thresholds in empirical_thresholds.items():
        gate_activation_rates[setting_name] = {}
        for prof, vals in profile_acs.items():
            # Determine which threshold to use
            if 'A1' in prof:
                thresh = thresholds.get('A1', 0.05)
            elif 'A2' in prof:
                thresh = thresholds.get('A2', 0.35)
            else:
                thresh = thresholds.get('A3', 0.10)

            auth_mults = [max(0.0, min(1.0, v / thresh)) if thresh > 0 else 1.0
                          for v in vals]
            below_half = sum(1 for m in auth_mults if m < 0.5)
            below_quarter = sum(1 for m in auth_mults if m < 0.25)
            mean_am = sum(auth_mults) / len(auth_mults) if auth_mults else 1.0

            gate_activation_rates[setting_name][prof] = {
                'frac_below_half': round(below_half / len(vals), 4) if vals else 0,
                'frac_below_quarter': round(below_quarter / len(vals), 4) if vals else 0,
                'mean_auth_mult': round(mean_am, 4),
                'threshold_used': thresh,
            }

    # ================================================================
    # Part 7: Build per-line ACS lookup (for T1/T2 apparatus injection)
    # ================================================================
    # Group events by line_key, take mean ACS per line
    line_acs = {}
    line_morphology = {}
    line_groups = defaultdict(list)
    for ev in events:
        lk = ev.get('line_key', '')
        line_groups[lk].append(ev)

    for lk, evs in line_groups.items():
        line_acs[lk] = round(sum(e['ACS'] for e in evs) / len(evs), 6)
        # Store morphology features for the line (from first event)
        ev0 = evs[0]
        line_morphology[lk] = {
            'headless_involved': ev0.get('headless_involved', False),
            'compound': ev0.get('E_compound', False),
            'm_terminal': ev0.get('m_terminal_present', False),
            'has_e_head': ev0.get('has_e_head_support', False),
            'cts': ev0.get('CTS', 0),
        }

    # ================================================================
    # Output
    # ================================================================
    per_event_acs = []
    for ev in events:
        per_event_acs.append({
            'folio': ev['folio'],
            'line_key': ev['line_key'],
            'profile': ev['profile'],
            'ACS': ev['ACS'],
            'CTS': ev.get('CTS', 0),
            'config_score': ev['config_score'],
            'signature': ev['signature'],
            'source': ev['signature_source'],
            'DYE_adv_event': ev.get('DYE_adv_event', 0),
            'n_strong_signals': ev.get('n_strong_signals', 0),
            'grammar_band': ev.get('grammar_band', 'UNKNOWN'),
        })

    output = {
        'metadata': {
            'phase': '575',
            'script': 't0_acs_assembly.py',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'elapsed_seconds': round(time.time() - t0, 2),
            'n_events': len(events),
            'alpha': ALPHA,
        },
        'per_event_acs': per_event_acs,
        'per_line_acs': line_acs,
        'per_line_morphology': line_morphology,
        'empirical_thresholds': empirical_thresholds,
        'acs_distribution': acs_distribution,
        'cts_acs_correlation': {
            'rho': round(rho, 6),
            'n': len(events),
        },
        'discrimination_check': {
            'cts_gap': round(cts_gap, 6),
            'acs_gap': round(acs_gap, 6),
            'acs_better': acs_gap > cts_gap,
            'n_resistant': len(resistant_acs),
            'n_counterfeitable': len(counterfeit_acs),
        },
        'signature_coverage': {
            'n_table': n_table,
            'n_fallback': n_fallback,
            'coverage_pct': round(coverage_pct, 2),
        },
        'gate_activation_rates': gate_activation_rates,
    }

    out_path = os.path.join(RESULTS_DIR, 't0_acs_assembly.json')
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=1)
    print(f"\nWrote {out_path}")


if __name__ == '__main__':
    main()
