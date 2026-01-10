#!/usr/bin/env python3
"""
HT Temporal Dynamics

Treating HT as a dynamic signal over manuscript time rather than a static
property of pages.

Questions:
1. Does HT density show manuscript-level trends?
2. Are there "waves" or "pulses" of HT concentration?
3. Does HT correlate with position in quire or manuscript?
4. Are there distinct HT "eras" in the manuscript?

Output: results/ht_temporal_dynamics.json
"""

import json
import re
import numpy as np
from pathlib import Path
from collections import defaultdict
from scipy import stats, signal
from scipy.ndimage import uniform_filter1d
import warnings
warnings.filterwarnings('ignore')

BASE = Path(__file__).parent.parent.parent
RESULTS = BASE / "results"

# Input
UNIFIED_PROFILES = RESULTS / "unified_folio_profiles.json"

# Output
OUTPUT = RESULTS / "ht_temporal_dynamics.json"


def load_json(path):
    """Load JSON file."""
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_folio_order(unified):
    """Get manuscript order of folios."""
    folios = list(unified['profiles'].keys())

    def folio_sort_key(f):
        match = re.match(r'f(\d+)([rv]?)(\d*)', f)
        if match:
            num = int(match.group(1))
            side = 0 if match.group(2) == 'r' else 1 if match.group(2) == 'v' else 0
            sub = int(match.group(3)) if match.group(3) else 0
            return (num, side, sub)
        return (9999, 0, 0)

    return sorted(folios, key=folio_sort_key)


def build_ht_timeseries(unified, folio_order):
    """
    Build HT density timeseries in manuscript order.
    """
    positions = []
    ht_values = []
    systems = []
    quires = []
    folios_list = []

    for i, folio in enumerate(folio_order):
        profile = unified['profiles'].get(folio, {})
        ht = profile.get('ht_density', 0)
        if ht is not None:
            positions.append(i)
            ht_values.append(ht)
            systems.append(profile.get('system', 'UNKNOWN'))
            quires.append(profile.get('quire', 'UNKNOWN'))
            folios_list.append(folio)

    return {
        'positions': np.array(positions),
        'ht': np.array(ht_values),
        'systems': systems,
        'quires': quires,
        'folios': folios_list
    }


def test_global_trend(ts):
    """
    Test for global trend (monotonic increase/decrease over manuscript).
    """
    positions = ts['positions']
    ht = ts['ht']

    # Spearman correlation with position
    r, p = stats.spearmanr(positions, ht)

    # Linear regression
    slope, intercept, r_value, p_value, std_err = stats.linregress(positions, ht)

    return {
        'spearman_r': round(float(r), 3),
        'spearman_p': round(float(p), 4),
        'linear_slope': round(float(slope), 6),
        'linear_r_squared': round(float(r_value**2), 4),
        'linear_p': round(float(p_value), 4),
        'trend': 'INCREASING' if r > 0.1 and p < 0.05 else 'DECREASING' if r < -0.1 and p < 0.05 else 'NONE'
    }


def detect_changepoints(ts, window=10):
    """
    Detect changepoints (abrupt shifts in HT level).
    Uses running mean difference.
    """
    ht = ts['ht']
    n = len(ht)

    if n < window * 3:
        return {'changepoints': [], 'n_changes': 0}

    # Compute running mean
    smoothed = uniform_filter1d(ht, size=window)

    # Compute derivative (change rate)
    diff = np.abs(np.diff(smoothed))

    # Find peaks in derivative (= changepoints)
    threshold = np.mean(diff) + 2 * np.std(diff)
    changepoint_indices = np.where(diff > threshold)[0]

    # Convert to folio info
    changepoints = []
    for idx in changepoint_indices:
        if idx > 0 and idx < n - 1:
            before_mean = np.mean(ht[max(0, idx-window):idx])
            after_mean = np.mean(ht[idx:min(n, idx+window)])
            changepoints.append({
                'position': int(idx),
                'folio': ts['folios'][idx],
                'ht_before': round(float(before_mean), 4),
                'ht_after': round(float(after_mean), 4),
                'change': round(float(after_mean - before_mean), 4),
                'direction': 'UP' if after_mean > before_mean else 'DOWN'
            })

    return {
        'changepoints': changepoints,
        'n_changes': len(changepoints),
        'threshold': round(float(threshold), 4)
    }


def analyze_autocorrelation(ts, max_lag=20):
    """
    Analyze autocorrelation of HT signal.
    High autocorrelation = HT is locally clustered.
    """
    ht = ts['ht']

    # Compute autocorrelation
    n = len(ht)
    mean = np.mean(ht)
    var = np.var(ht)

    acf = []
    for lag in range(max_lag + 1):
        if var > 0:
            c = np.sum((ht[:n-lag] - mean) * (ht[lag:] - mean)) / (n * var)
        else:
            c = 0
        acf.append(round(float(c), 4))

    # Find first lag where autocorrelation drops below threshold
    threshold = 2 / np.sqrt(n)  # 95% confidence
    decay_lag = max_lag
    for lag, c in enumerate(acf[1:], 1):
        if abs(c) < threshold:
            decay_lag = lag
            break

    return {
        'acf': acf,
        'decay_lag': decay_lag,
        'interpretation': f'HT signal correlated over ~{decay_lag} folios',
        'clustering': 'STRONG' if decay_lag > 5 else 'MODERATE' if decay_lag > 2 else 'WEAK'
    }


def detect_waves(ts, min_period=5, max_period=50):
    """
    Detect periodic waves in HT signal using FFT.
    """
    ht = ts['ht']
    n = len(ht)

    if n < max_period * 2:
        return {'dominant_period': None, 'periodic': False}

    # Detrend
    detrended = ht - np.mean(ht)

    # FFT
    fft = np.fft.fft(detrended)
    freqs = np.fft.fftfreq(n)

    # Get power spectrum
    power = np.abs(fft) ** 2

    # Find dominant frequency (excluding DC component)
    valid_mask = (freqs > 1/max_period) & (freqs < 1/min_period)
    if not np.any(valid_mask):
        return {'dominant_period': None, 'periodic': False}

    valid_power = power.copy()
    valid_power[~valid_mask] = 0

    peak_idx = np.argmax(valid_power)
    peak_freq = freqs[peak_idx]
    peak_power = power[peak_idx]

    if peak_freq <= 0:
        return {'dominant_period': None, 'periodic': False}

    period = 1 / peak_freq

    # Test significance vs noise
    noise_power = np.median(power[valid_mask])
    snr = peak_power / noise_power if noise_power > 0 else 0

    return {
        'dominant_period': round(float(period), 1) if snr > 3 else None,
        'snr': round(float(snr), 2),
        'periodic': bool(snr > 3),
        'interpretation': f'~{round(period)}-folio cycle detected' if snr > 3 else 'No periodic pattern'
    }


def segment_by_ht_level(ts, n_segments=4):
    """
    Segment manuscript by HT level using running mean.
    """
    ht = ts['ht']
    n = len(ht)

    # Compute running mean with large window
    window = n // n_segments
    smoothed = uniform_filter1d(ht, size=window)

    # Find segment boundaries at local minima
    # Simple approach: split at quartile boundaries of smoothed signal
    thresholds = np.percentile(smoothed, [25, 50, 75])

    segments = []
    current_level = None
    segment_start = 0

    for i, s in enumerate(smoothed):
        if s < thresholds[0]:
            level = 'LOW'
        elif s < thresholds[1]:
            level = 'MED_LOW'
        elif s < thresholds[2]:
            level = 'MED_HIGH'
        else:
            level = 'HIGH'

        if level != current_level:
            if current_level is not None:
                segments.append({
                    'start': int(segment_start),
                    'end': int(i),
                    'start_folio': ts['folios'][segment_start],
                    'end_folio': ts['folios'][i-1] if i > 0 else ts['folios'][0],
                    'level': current_level,
                    'mean_ht': round(float(np.mean(ht[segment_start:i])), 4),
                    'length': i - segment_start
                })
            current_level = level
            segment_start = i

    # Final segment
    if current_level is not None:
        segments.append({
            'start': int(segment_start),
            'end': int(n),
            'start_folio': ts['folios'][segment_start],
            'end_folio': ts['folios'][n-1],
            'level': current_level,
            'mean_ht': round(float(np.mean(ht[segment_start:])), 4),
            'length': n - segment_start
        })

    # Merge tiny segments
    merged = []
    for seg in segments:
        if seg['length'] >= 5:
            merged.append(seg)
        elif merged:
            merged[-1]['end'] = seg['end']
            merged[-1]['end_folio'] = seg['end_folio']
            merged[-1]['length'] += seg['length']

    return {
        'n_segments': len(merged),
        'segments': merged
    }


def analyze_by_system_position(ts):
    """
    Does HT vary by position within each system's folios?
    """
    by_system = defaultdict(list)

    for i, (folio, ht, system) in enumerate(zip(ts['folios'], ts['ht'], ts['systems'])):
        by_system[system].append((i, ht))

    results = {}
    for system, data in sorted(by_system.items()):
        if len(data) < 10:
            continue

        positions = [d[0] for d in data]
        ht_values = [d[1] for d in data]

        # Correlation with absolute position
        r, p = stats.spearmanr(positions, ht_values)

        # Split into early/late halves
        mid = len(data) // 2
        early_ht = np.mean([d[1] for d in data[:mid]])
        late_ht = np.mean([d[1] for d in data[mid:]])

        results[system] = {
            'n_folios': len(data),
            'position_correlation': round(float(r), 3),
            'correlation_p': round(float(p), 4),
            'early_half_mean': round(float(early_ht), 4),
            'late_half_mean': round(float(late_ht), 4),
            'trend': 'INCREASING' if r > 0.2 and p < 0.05 else 'DECREASING' if r < -0.2 and p < 0.05 else 'FLAT'
        }

    return results


def find_local_extremes(ts, window=5):
    """
    Find local maxima and minima in HT signal.
    """
    ht = ts['ht']
    n = len(ht)

    # Smooth first
    smoothed = uniform_filter1d(ht, size=window)

    maxima = []
    minima = []

    for i in range(window, n - window):
        local = smoothed[i-window:i+window+1]
        if smoothed[i] == max(local):
            maxima.append({
                'position': int(i),
                'folio': ts['folios'][i],
                'ht': round(float(ht[i]), 4),
                'system': ts['systems'][i]
            })
        elif smoothed[i] == min(local):
            minima.append({
                'position': int(i),
                'folio': ts['folios'][i],
                'ht': round(float(ht[i]), 4),
                'system': ts['systems'][i]
            })

    return {
        'n_peaks': len(maxima),
        'n_valleys': len(minima),
        'peaks': sorted(maxima, key=lambda x: x['ht'], reverse=True)[:5],
        'valleys': sorted(minima, key=lambda x: x['ht'])[:5]
    }


def main():
    print("=" * 70)
    print("HT Temporal Dynamics")
    print("=" * 70)

    # Load data
    print("\n[1] Loading data...")
    unified = load_json(UNIFIED_PROFILES)
    folio_order = get_folio_order(unified)
    print(f"    Total folios in order: {len(folio_order)}")

    # Build timeseries
    print("\n[2] Building HT timeseries...")
    ts = build_ht_timeseries(unified, folio_order)
    print(f"    Folios with HT data: {len(ts['ht'])}")
    print(f"    HT range: {ts['ht'].min():.3f} - {ts['ht'].max():.3f}")
    print(f"    HT mean: {ts['ht'].mean():.3f}")

    # Test global trend
    print("\n[3] Testing global trend...")
    trend = test_global_trend(ts)
    print(f"    Spearman r: {trend['spearman_r']}, p: {trend['spearman_p']}")
    print(f"    Linear slope: {trend['linear_slope']}")
    print(f"    Trend: {trend['trend']}")

    # Detect changepoints
    print("\n[4] Detecting changepoints...")
    changepoints = detect_changepoints(ts)
    print(f"    Changepoints found: {changepoints['n_changes']}")
    for cp in changepoints['changepoints'][:5]:
        print(f"      {cp['folio']}: {cp['ht_before']:.3f} -> {cp['ht_after']:.3f} ({cp['direction']})")

    # Autocorrelation analysis
    print("\n[5] Analyzing autocorrelation...")
    acf = analyze_autocorrelation(ts)
    print(f"    Decay lag: {acf['decay_lag']} folios")
    print(f"    Clustering: {acf['clustering']}")

    # Detect waves
    print("\n[6] Detecting periodic waves...")
    waves = detect_waves(ts)
    print(f"    Periodic: {waves['periodic']}")
    if waves['dominant_period']:
        print(f"    Dominant period: {waves['dominant_period']} folios")
    print(f"    SNR: {waves['snr']}")

    # Segment by HT level
    print("\n[7] Segmenting manuscript by HT level...")
    segments = segment_by_ht_level(ts)
    print(f"    Segments found: {segments['n_segments']}")
    for seg in segments['segments']:
        print(f"      {seg['start_folio']}-{seg['end_folio']}: {seg['level']} (mean={seg['mean_ht']:.3f}, n={seg['length']})")

    # By-system position analysis
    print("\n[8] Analyzing by system position...")
    by_system = analyze_by_system_position(ts)
    for system, data in sorted(by_system.items()):
        print(f"    {system}: r={data['position_correlation']:.3f}, early={data['early_half_mean']:.3f}, late={data['late_half_mean']:.3f}")
        print(f"      Trend: {data['trend']}")

    # Local extremes
    print("\n[9] Finding local extremes...")
    extremes = find_local_extremes(ts)
    print(f"    Peaks: {extremes['n_peaks']}, Valleys: {extremes['n_valleys']}")
    print("    Top peaks:")
    for p in extremes['peaks'][:3]:
        print(f"      {p['folio']}: {p['ht']:.3f} ({p['system']})")
    print("    Lowest valleys:")
    for v in extremes['valleys'][:3]:
        print(f"      {v['folio']}: {v['ht']:.3f} ({v['system']})")

    # Key findings
    print("\n[10] Key findings...")
    findings = []

    if trend['trend'] != 'NONE':
        findings.append({
            'finding': f'Global {trend["trend"].lower()} trend in HT',
            'r': trend['spearman_r'],
            'p': trend['spearman_p'],
            'interpretation': f'HT {"rises" if trend["trend"] == "INCREASING" else "falls"} through manuscript'
        })

    if changepoints['n_changes'] > 0:
        findings.append({
            'finding': f'{changepoints["n_changes"]} HT changepoints detected',
            'locations': [cp['folio'] for cp in changepoints['changepoints'][:3]],
            'interpretation': 'Abrupt shifts in HT density at these boundaries'
        })

    if acf['clustering'] in ['STRONG', 'MODERATE']:
        findings.append({
            'finding': f'{acf["clustering"]} HT clustering',
            'decay_lag': acf['decay_lag'],
            'interpretation': f'HT correlated over ~{acf["decay_lag"]} consecutive folios'
        })

    if waves['periodic']:
        findings.append({
            'finding': 'Periodic HT signal detected',
            'period': waves['dominant_period'],
            'interpretation': f'HT oscillates with ~{waves["dominant_period"]:.0f}-folio period'
        })

    # System-specific trends
    for system, data in by_system.items():
        if data['trend'] != 'FLAT':
            findings.append({
                'finding': f'{system} shows {data["trend"].lower()} HT over manuscript',
                'r': data['position_correlation'],
                'interpretation': f'{system} folios become {"more" if data["trend"] == "INCREASING" else "less"} HT-dense later in manuscript'
            })

    for f in findings:
        print(f"\n    - {f['finding']}")
        if 'interpretation' in f:
            print(f"      {f['interpretation']}")

    if not findings:
        print("\n    - No significant temporal patterns detected")
        print("      HT appears stationary across manuscript time")

    # Save output
    print("\n[11] Saving output...")

    output = {
        'metadata': {
            'analysis': 'HT Temporal Dynamics',
            'description': 'HT as dynamic signal over manuscript time',
            'n_folios': len(ts['ht'])
        },
        'timeseries_stats': {
            'mean': round(float(ts['ht'].mean()), 4),
            'std': round(float(ts['ht'].std()), 4),
            'min': round(float(ts['ht'].min()), 4),
            'max': round(float(ts['ht'].max()), 4)
        },
        'global_trend': trend,
        'changepoints': changepoints,
        'autocorrelation': acf,
        'periodicity': waves,
        'segments': segments,
        'by_system_position': by_system,
        'local_extremes': extremes,
        'key_findings': findings
    }

    with open(OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2)

    print(f"    Saved to: {OUTPUT}")

    print("\n" + "=" * 70)
    print("HT TEMPORAL DYNAMICS COMPLETE")
    print("=" * 70)

    return output


if __name__ == "__main__":
    main()
