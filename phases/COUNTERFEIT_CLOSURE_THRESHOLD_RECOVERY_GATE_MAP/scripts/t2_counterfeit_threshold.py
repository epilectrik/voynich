"""
T2: Counterfeit Threshold Curves
Phase 574 - COUNTERFEIT_CLOSURE_THRESHOLD_RECOVERY_GATE_MAP

Models when DYE advantage crosses zero as function of closure grammar
quality.  Answers: under what closure-packet conditions does a folio/profile
cross from counterfeit-closure susceptibility into genuine grammar
amplification?

Five parts:
  Part 1 - Binned threshold display (CTS bins x profile)
  Part 2 - Empirical threshold estimation (binary AND magnitude)
  Part 3 - Transition sharpness (sigmoid fit)
  Part 4 - Minimum grammar strength per profile
  Part 5 - Counterfeit susceptibility curve
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

CTS_BINS = [(0.0, 0.2), (0.2, 0.4), (0.4, 0.6), (0.6, 0.8), (0.8, 1.01)]
CTS_BIN_LABELS = ['[0.0,0.2)', '[0.2,0.4)', '[0.4,0.6)', '[0.6,0.8)', '[0.8,1.0]']


def cts_bin_label(cts):
    for (lo, hi), label in zip(CTS_BINS, CTS_BIN_LABELS):
        if lo <= cts < hi:
            return label
    return CTS_BIN_LABELS[-1]


def running_mean(values, window):
    """Running mean with centered window."""
    n = len(values)
    result = []
    half = window // 2
    for i in range(n):
        lo = max(0, i - half)
        hi = min(n, i + half + 1)
        result.append(sum(values[lo:hi]) / (hi - lo))
    return result


def fit_sigmoid(x_vals, y_vals, max_iter=200, lr=0.01):
    """Fit sigmoid P = 1 / (1 + exp(-k*(x - mid))) via gradient descent.
    Returns (mid, k, r_squared)."""
    if len(x_vals) < 3:
        return (0.5, 1.0, 0.0)

    # Initialize
    mid = sum(x_vals) / len(x_vals)
    k = 5.0

    for _ in range(max_iter):
        grad_mid = 0.0
        grad_k = 0.0
        for x, y in zip(x_vals, y_vals):
            z = k * (x - mid)
            z = max(-20, min(20, z))  # clip for numerical stability
            sig = 1.0 / (1.0 + math.exp(-z))
            err = sig - y
            dsig = sig * (1.0 - sig)
            grad_mid += err * dsig * (-k)
            grad_k += err * dsig * (x - mid)

        n = len(x_vals)
        mid -= lr * grad_mid / n
        k -= lr * grad_k / n
        k = max(0.1, min(50.0, k))

    # Compute R-squared
    y_mean = sum(y_vals) / len(y_vals)
    ss_tot = sum((y - y_mean) ** 2 for y in y_vals) + 1e-12
    ss_res = 0.0
    for x, y in zip(x_vals, y_vals):
        z = k * (x - mid)
        z = max(-20, min(20, z))
        pred = 1.0 / (1.0 + math.exp(-z))
        ss_res += (y - pred) ** 2

    r_sq = 1.0 - ss_res / ss_tot
    return (round(mid, 4), round(k, 4), round(r_sq, 4))


def main():
    t_start = time.time()
    print("=" * 70)
    print("T2: Counterfeit Threshold Curves")
    print("Phase 574 - COUNTERFEIT_CLOSURE_THRESHOLD_RECOVERY_GATE_MAP")
    print("=" * 70)

    # ---- Load T0 event matrix ----
    print("\n--- Loading T0 event matrix ---")
    t0_path = os.path.join(RESULTS_DIR, 't0_event_feature_assembly.json')
    with open(t0_path, 'r', encoding='utf-8') as f:
        t0 = json.load(f)
    events = t0['m1_events']
    print(f"  Events loaded: {len(events)}")

    profiles = sorted(set(e['profile'] for e in events))
    print(f"  Profiles: {profiles}")

    # ================================================================
    # PART 1: Binned threshold display
    # ================================================================
    print("\n--- Part 1: Binned threshold display ---")
    binned_display = {}
    for profile in profiles:
        prof_events = [e for e in events if e['profile'] == profile]
        binned_display[profile] = {}

        for bin_label in CTS_BIN_LABELS:
            bin_evts = [e for e in prof_events if cts_bin_label(e['CTS']) == bin_label]
            n = len(bin_evts)
            if n == 0:
                binned_display[profile][bin_label] = {
                    'mean_dye': 0.0, 'mean_ccs1': 0.0, 'dye_adv': 0.0,
                    'n_events': 0, 'n_positive': 0
                }
                continue
            mean_dye = sum(e['DYE'] for e in bin_evts) / n
            mean_ccs1 = sum(e['CCS1_folio'] for e in bin_evts) / n
            n_pos = sum(1 for e in bin_evts if e['DYE_adv_event'] > 0)
            binned_display[profile][bin_label] = {
                'mean_dye': round(mean_dye, 6),
                'mean_ccs1': round(mean_ccs1, 6),
                'dye_adv': round(mean_dye - mean_ccs1, 6),
                'n_events': n,
                'n_positive': n_pos,
            }

    # Print summary
    for profile in profiles:
        print(f"\n  {profile}:")
        for bl in CTS_BIN_LABELS:
            d = binned_display[profile][bl]
            print(f"    {bl}: n={d['n_events']}, DYE={d['mean_dye']:.4f}, "
                  f"CCS1={d['mean_ccs1']:.4f}, adv={d['dye_adv']:.4f}")

    # Strong signal display
    print("\n--- Strong signal display ---")
    strong_signal_display = {}
    for profile in profiles:
        prof_events = [e for e in events if e['profile'] == profile]
        strong_signal_display[profile] = {}
        for ns in range(5):  # 0, 1, 2, 3, 4
            ns_evts = [e for e in prof_events if e['n_strong_signals'] == ns]
            n = len(ns_evts)
            if n == 0:
                strong_signal_display[profile][str(ns)] = {
                    'mean_dye': 0.0, 'dye_adv': 0.0, 'n_events': 0
                }
                continue
            mean_dye = sum(e['DYE'] for e in ns_evts) / n
            mean_ccs1 = sum(e['CCS1_folio'] for e in ns_evts) / n
            strong_signal_display[profile][str(ns)] = {
                'mean_dye': round(mean_dye, 6),
                'dye_adv': round(mean_dye - mean_ccs1, 6),
                'n_events': n,
            }

    # Cross-tabulation: CTS_bin x grammar_band x profile
    cross_tab = {}
    for profile in profiles:
        prof_events = [e for e in events if e['profile'] == profile]
        cross_tab[profile] = {}
        for bl in CTS_BIN_LABELS:
            cross_tab[profile][bl] = {}
            for band in ['STRONG', 'MEDIUM', 'WEAK']:
                band_evts = [e for e in prof_events
                             if cts_bin_label(e['CTS']) == bl and e['grammar_band'] == band]
                n = len(band_evts)
                if n == 0:
                    cross_tab[profile][bl][band] = {'dye_adv': 0.0, 'n': 0}
                    continue
                adv = sum(e['DYE_adv_event'] for e in band_evts) / n
                cross_tab[profile][bl][band] = {
                    'dye_adv': round(adv, 6), 'n': n
                }

    # ================================================================
    # PART 2: Empirical threshold estimation (binary AND magnitude)
    # ================================================================
    print("\n--- Part 2: Empirical threshold estimation ---")
    threshold_estimates = {}

    for profile in profiles:
        prof_events = [e for e in events if e['profile'] == profile]
        # Sort by CTS
        prof_events.sort(key=lambda e: e['CTS'])
        n = len(prof_events)
        if n < 5:
            threshold_estimates[profile] = {
                'cts_threshold_binary': None,
                'cts_threshold_magnitude': None,
                'transition_width': None,
                'n_events': n,
            }
            continue

        window = max(5, int(0.2 * n))

        # Binary threshold: running mean of indicator DYE_adv > 0
        indicators = [1.0 if e['DYE_adv_event'] > 0 else 0.0 for e in prof_events]
        rm_binary = running_mean(indicators, window)

        # Find where running mean crosses 0.5
        cts_values = [e['CTS'] for e in prof_events]
        binary_threshold = None
        for i in range(1, len(rm_binary)):
            if rm_binary[i - 1] < 0.5 <= rm_binary[i]:
                # Linear interpolation
                frac = (0.5 - rm_binary[i - 1]) / max(rm_binary[i] - rm_binary[i - 1], 1e-12)
                binary_threshold = cts_values[i - 1] + frac * (cts_values[i] - cts_values[i - 1])
                break

        # If no crossing found, check if always above or below
        if binary_threshold is None:
            if rm_binary[-1] >= 0.5:
                binary_threshold = cts_values[0]  # always above
            else:
                binary_threshold = 1.0  # never crosses

        # Magnitude threshold: running mean of DYE_adv itself crossing 0
        magnitudes = [e['DYE_adv_event'] for e in prof_events]
        rm_mag = running_mean(magnitudes, window)

        mag_threshold = None
        for i in range(1, len(rm_mag)):
            if rm_mag[i - 1] < 0.0 <= rm_mag[i]:
                frac = (0.0 - rm_mag[i - 1]) / max(rm_mag[i] - rm_mag[i - 1], 1e-12)
                mag_threshold = cts_values[i - 1] + frac * (cts_values[i] - cts_values[i - 1])
                break

        if mag_threshold is None:
            if rm_mag[-1] >= 0.0:
                mag_threshold = cts_values[0]
            else:
                mag_threshold = 1.0

        # Transition width: CTS range where binary running mean goes from 0.3 to 0.7
        cts_03 = None
        cts_07 = None
        for i in range(1, len(rm_binary)):
            if cts_03 is None and rm_binary[i - 1] < 0.3 <= rm_binary[i]:
                frac = (0.3 - rm_binary[i - 1]) / max(rm_binary[i] - rm_binary[i - 1], 1e-12)
                cts_03 = cts_values[i - 1] + frac * (cts_values[i] - cts_values[i - 1])
            if cts_07 is None and rm_binary[i - 1] < 0.7 <= rm_binary[i]:
                frac = (0.7 - rm_binary[i - 1]) / max(rm_binary[i] - rm_binary[i - 1], 1e-12)
                cts_07 = cts_values[i - 1] + frac * (cts_values[i] - cts_values[i - 1])

        tw = None
        if cts_03 is not None and cts_07 is not None:
            tw = round(cts_07 - cts_03, 4)

        threshold_estimates[profile] = {
            'cts_threshold_binary': round(binary_threshold, 4),
            'cts_threshold_magnitude': round(mag_threshold, 4),
            'transition_width': tw,
            'n_events': n,
        }
        print(f"  {profile}: binary={binary_threshold:.4f}, "
              f"magnitude={mag_threshold:.4f}, width={tw}")

    # ================================================================
    # PART 3: Transition sharpness (sigmoid fit)
    # ================================================================
    print("\n--- Part 3: Transition sharpness ---")
    transition_sharpness = {}

    for profile in profiles:
        prof_events = [e for e in events if e['profile'] == profile]
        # Compute success rate in 10 CTS bins
        n_bins = 10
        bin_width = 1.0 / n_bins
        x_centers = []
        y_rates = []
        for i in range(n_bins):
            lo = i * bin_width
            hi = (i + 1) * bin_width + (0.01 if i == n_bins - 1 else 0.0)
            bin_evts = [e for e in prof_events if lo <= e['CTS'] < hi]
            if len(bin_evts) < 2:
                continue
            success = sum(1 for e in bin_evts if e['DYE_adv_event'] > 0)
            x_centers.append(lo + bin_width / 2)
            y_rates.append(success / len(bin_evts))

        if len(x_centers) >= 3:
            mid, k, r_sq = fit_sigmoid(x_centers, y_rates)
            transition_sharpness[profile] = {
                'sigmoid_midpoint': mid,
                'sigmoid_steepness': k,
                'r_squared': r_sq,
                'n_bins_used': len(x_centers),
            }
            print(f"  {profile}: midpoint={mid:.4f}, steepness={k:.4f}, R²={r_sq:.4f}")
        else:
            transition_sharpness[profile] = {
                'sigmoid_midpoint': None,
                'sigmoid_steepness': None,
                'r_squared': None,
                'n_bins_used': len(x_centers),
            }

    # ================================================================
    # PART 4: Minimum grammar strength per profile
    # ================================================================
    print("\n--- Part 4: Minimum grammar strength ---")
    min_grammar_strength = {}
    for profile in profiles:
        prof_events = [e for e in events if e['profile'] == profile]
        min_n = None
        min_adv = None
        for ns in range(5):
            ns_evts = [e for e in prof_events if e['n_strong_signals'] == ns]
            if len(ns_evts) < 2:
                continue
            adv = sum(e['DYE_adv_event'] for e in ns_evts) / len(ns_evts)
            if adv > 0:
                min_n = ns
                min_adv = round(adv, 6)
                break

        min_grammar_strength[profile] = {
            'min_n_strong_for_positive_adv': min_n,
            'DYE_adv_at_min': min_adv,
        }
        print(f"  {profile}: min_n_strong={min_n}, adv={min_adv}")

    # ================================================================
    # PART 5: Counterfeit susceptibility curve
    # ================================================================
    print("\n--- Part 5: Counterfeit susceptibility ---")
    counterfeit_susceptibility = {}
    for profile in profiles:
        prof_events = [e for e in events if e['profile'] == profile]
        counterfeit_susceptibility[profile] = {}
        for bl in CTS_BIN_LABELS:
            bin_evts = [e for e in prof_events if cts_bin_label(e['CTS']) == bl]
            n = len(bin_evts)
            if n == 0:
                counterfeit_susceptibility[profile][bl] = 0.0
                continue
            p_null_wins = sum(1 for e in bin_evts if e['DYE'] < e['CCS1_folio']) / n
            counterfeit_susceptibility[profile][bl] = round(p_null_wins, 4)

    # Print summary
    for profile in profiles:
        vals = [counterfeit_susceptibility[profile][bl] for bl in CTS_BIN_LABELS]
        print(f"  {profile}: {[f'{v:.2f}' for v in vals]}")

    # ================================================================
    # Profile shifts
    # ================================================================
    print("\n--- Profile shifts ---")
    profile_shifts = {}
    a2_key = [p for p in profiles if 'A2' in p]
    a1_key = [p for p in profiles if 'A1' in p]
    a3_key = [p for p in profiles if 'A3' in p]

    if a2_key and a1_key:
        a2t = threshold_estimates[a2_key[0]]
        a1t = threshold_estimates[a1_key[0]]
        profile_shifts['A2_vs_A1'] = {
            'binary_shift': round(
                (a2t['cts_threshold_binary'] or 0) - (a1t['cts_threshold_binary'] or 0), 4),
            'magnitude_shift': round(
                (a2t['cts_threshold_magnitude'] or 0) - (a1t['cts_threshold_magnitude'] or 0), 4),
        }
        print(f"  A2 vs A1: binary_shift={profile_shifts['A2_vs_A1']['binary_shift']:.4f}, "
              f"magnitude_shift={profile_shifts['A2_vs_A1']['magnitude_shift']:.4f}")

    if a2_key and a3_key:
        a2t = threshold_estimates[a2_key[0]]
        a3t = threshold_estimates[a3_key[0]]
        profile_shifts['A2_vs_A3'] = {
            'binary_shift': round(
                (a2t['cts_threshold_binary'] or 0) - (a3t['cts_threshold_binary'] or 0), 4),
            'magnitude_shift': round(
                (a2t['cts_threshold_magnitude'] or 0) - (a3t['cts_threshold_magnitude'] or 0), 4),
        }
        print(f"  A2 vs A3: binary_shift={profile_shifts['A2_vs_A3']['binary_shift']:.4f}, "
              f"magnitude_shift={profile_shifts['A2_vs_A3']['magnitude_shift']:.4f}")

    # ================================================================
    # Save output
    # ================================================================
    print("\n--- Saving output ---")
    os.makedirs(RESULTS_DIR, exist_ok=True)
    output = {
        'metadata': {
            'phase': '574',
            'script': 't2_counterfeit_threshold.py',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'elapsed_seconds': round(time.time() - t_start, 2),
            'n_events': len(events),
            'profiles': profiles,
        },
        'binned_display': binned_display,
        'strong_signal_display': strong_signal_display,
        'cross_tabulation': cross_tab,
        'threshold_estimates': threshold_estimates,
        'transition_sharpness': transition_sharpness,
        'min_grammar_strength': min_grammar_strength,
        'counterfeit_susceptibility': counterfeit_susceptibility,
        'profile_shifts': profile_shifts,
    }

    out_path = os.path.join(RESULTS_DIR, 't2_counterfeit_threshold.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=1, default=str)
    print(f"  Written: {out_path}")
    print(f"  Size: {os.path.getsize(out_path):,} bytes")
    print(f"\nDone in {time.time() - t_start:.1f}s")


if __name__ == '__main__':
    main()
