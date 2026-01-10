"""
E5 - AZC Internal Oscillation Test

Question: Does the AZC block (30 folios) show internal HT micro-oscillations
that mirror the manuscript-wide ~10-folio rhythm?

This tests whether AZC is internally structured with the same attention
dynamics we see globally, or whether it's internally flat/monotonic.
"""

import json
import re
import numpy as np
from scipy import stats, signal
from pathlib import Path


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


def load_data():
    """Load unified folio profiles."""
    results_dir = Path(__file__).parent.parent.parent / "results"
    with open(results_dir / "unified_folio_profiles.json") as f:
        return json.load(f)


def extract_azc_sequence(unified, folio_order):
    """Extract AZC folios in manuscript order with their HT metrics."""
    azc_sequence = []

    for idx, folio in enumerate(folio_order):
        profile = unified['profiles'].get(folio, {})
        if profile.get('system') == 'AZC':
            azc_sequence.append({
                'folio': folio,
                'position': idx,
                'ht_density': profile.get('ht_density', 0) or 0,
                'ht_boundary_anchor': profile.get('ht_boundary_anchor_rate', 0) or 0
            })

    return azc_sequence


def test_autocorrelation(ht_series, max_lag=10):
    """Test for autocorrelation in HT series."""
    n = len(ht_series)
    if n < max_lag + 2:
        return {'error': 'insufficient data'}

    # Normalize
    ht_z = (ht_series - np.mean(ht_series)) / (np.std(ht_series) + 1e-10)

    autocorrs = []
    for lag in range(1, min(max_lag + 1, n // 2)):
        if len(ht_z[:-lag]) > 2:
            r, p = stats.pearsonr(ht_z[:-lag], ht_z[lag:])
            autocorrs.append({
                'lag': lag,
                'correlation': float(r),
                'p_value': float(p),
                'significant': p < 0.05
            })

    return autocorrs


def test_periodicity(ht_series):
    """Test for periodic oscillation using FFT."""
    n = len(ht_series)
    if n < 6:
        return {'error': 'insufficient data for FFT'}

    # Detrend
    detrended = signal.detrend(ht_series)

    # FFT
    fft = np.fft.rfft(detrended)
    power = np.abs(fft) ** 2
    freqs = np.fft.rfftfreq(n)

    # Find dominant frequency (excluding DC)
    if len(power) > 1:
        dominant_idx = np.argmax(power[1:]) + 1
        dominant_freq = freqs[dominant_idx]
        dominant_period = 1 / dominant_freq if dominant_freq > 0 else np.inf
        dominant_power = power[dominant_idx]

        # Signal-to-noise ratio
        noise_power = np.mean(power[1:])
        snr = dominant_power / noise_power if noise_power > 0 else 0
    else:
        dominant_period = np.inf
        snr = 0

    return {
        'dominant_period': float(dominant_period) if not np.isinf(dominant_period) else None,
        'snr': float(snr),
        'n_samples': n
    }


def test_trend(ht_series, positions):
    """Test for monotonic trend within AZC block."""
    if len(ht_series) < 3:
        return {'error': 'insufficient data'}

    slope, intercept, r, p, se = stats.linregress(positions, ht_series)

    return {
        'slope': float(slope),
        'r_squared': float(r ** 2),
        'p_value': float(p),
        'direction': 'increasing' if slope > 0 else 'decreasing',
        'significant': p < 0.05
    }


def test_changepoints(ht_series, threshold=1.5):
    """Detect HT changepoints within AZC block."""
    if len(ht_series) < 4:
        return {'error': 'insufficient data'}

    # Compute differences
    diffs = np.diff(ht_series)

    # Z-score the differences
    mean_diff = np.mean(np.abs(diffs))
    std_diff = np.std(np.abs(diffs))

    if std_diff == 0:
        return {'n_changepoints': 0, 'positions': []}

    z_scores = np.abs(diffs - np.mean(diffs)) / std_diff

    # Find changepoints
    changepoint_indices = np.where(z_scores > threshold)[0]

    return {
        'n_changepoints': len(changepoint_indices),
        'positions': changepoint_indices.tolist(),
        'threshold_used': threshold
    }


def compare_to_global_rhythm(azc_period, global_period=10):
    """Compare AZC internal rhythm to manuscript-wide rhythm."""
    if azc_period is None:
        return {'comparison': 'no_azc_period_detected'}

    ratio = azc_period / global_period

    if 0.8 <= ratio <= 1.2:
        interpretation = 'MATCHES_GLOBAL'
    elif ratio < 0.5:
        interpretation = 'FASTER_THAN_GLOBAL'
    elif ratio > 2.0:
        interpretation = 'SLOWER_THAN_GLOBAL'
    else:
        interpretation = 'DIFFERENT_FROM_GLOBAL'

    return {
        'azc_period': azc_period,
        'global_period': global_period,
        'ratio': ratio,
        'interpretation': interpretation
    }


def analyze_zodiac_vs_nonzodiac(azc_sequence):
    """Compare oscillation patterns in Zodiac vs non-Zodiac AZC."""
    zodiac = []
    non_zodiac = []

    for item in azc_sequence:
        match = re.match(r'f(\d+)', item['folio'])
        if match:
            num = int(match.group(1))
            if 70 <= num <= 73:
                zodiac.append(item)
            else:
                non_zodiac.append(item)

    results = {}

    for name, group in [('zodiac', zodiac), ('non_zodiac', non_zodiac)]:
        if len(group) >= 4:
            ht = np.array([x['ht_density'] for x in group])
            pos = np.array([x['position'] for x in group])

            results[name] = {
                'n_folios': len(group),
                'mean_ht': float(np.mean(ht)),
                'std_ht': float(np.std(ht)),
                'cv': float(np.std(ht) / np.mean(ht)) if np.mean(ht) > 0 else 0,
                'range': float(np.max(ht) - np.min(ht)),
                'trend': test_trend(ht, pos),
                'autocorr': test_autocorrelation(ht, max_lag=min(5, len(ht) // 2))
            }
        else:
            results[name] = {'error': f'insufficient data ({len(group)} folios)'}

    return results


def main():
    print("E5 - AZC Internal Oscillation Test")
    print("=" * 50)

    # Load data
    unified = load_data()
    folio_order = get_folio_order(unified)

    # Extract AZC sequence
    azc_sequence = extract_azc_sequence(unified, folio_order)

    print(f"\nAZC block: {len(azc_sequence)} folios")
    print(f"First: {azc_sequence[0]['folio']} (position {azc_sequence[0]['position']})")
    print(f"Last: {azc_sequence[-1]['folio']} (position {azc_sequence[-1]['position']})")

    # Extract HT series
    ht_series = np.array([x['ht_density'] for x in azc_sequence])
    positions = np.array([i for i in range(len(azc_sequence))])  # Internal positions
    ms_positions = np.array([x['position'] for x in azc_sequence])  # Manuscript positions

    print(f"\nHT statistics:")
    print(f"  Mean: {np.mean(ht_series):.4f}")
    print(f"  Std: {np.std(ht_series):.4f}")
    print(f"  CV: {np.std(ht_series) / np.mean(ht_series):.4f}")
    print(f"  Range: {np.min(ht_series):.4f} - {np.max(ht_series):.4f}")

    # Test for internal trend
    print("\n--- Internal Trend Test ---")
    trend = test_trend(ht_series, positions)
    print(f"  Slope: {trend['slope']:.4f}")
    print(f"  R^2: {trend['r_squared']:.4f}")
    print(f"  Direction: {trend['direction']}")
    print(f"  p-value: {trend['p_value']:.4f}")
    print(f"  Significant: {trend['significant']}")

    # Test for autocorrelation
    print("\n--- Autocorrelation Test ---")
    autocorr = test_autocorrelation(ht_series, max_lag=8)
    if isinstance(autocorr, list):
        for ac in autocorr[:5]:  # Show first 5 lags
            sig_marker = "*" if ac['significant'] else ""
            print(f"  Lag {ac['lag']}: r={ac['correlation']:.3f}, p={ac['p_value']:.4f} {sig_marker}")
    else:
        print(f"  {autocorr}")

    # Test for periodicity
    print("\n--- Periodicity Test (FFT) ---")
    period_result = test_periodicity(ht_series)
    if 'error' not in period_result:
        print(f"  Dominant period: {period_result['dominant_period']:.2f} folios" if period_result['dominant_period'] else "  No clear period")
        print(f"  SNR: {period_result['snr']:.2f}")
    else:
        print(f"  {period_result['error']}")

    # Compare to global rhythm
    print("\n--- Comparison to Global Rhythm ---")
    global_comparison = compare_to_global_rhythm(
        period_result.get('dominant_period'),
        global_period=10
    )
    print(f"  Global period: ~10 folios")
    if global_comparison.get('azc_period'):
        print(f"  AZC period: {global_comparison['azc_period']:.2f} folios")
        print(f"  Ratio: {global_comparison['ratio']:.2f}")
    print(f"  Interpretation: {global_comparison['interpretation']}")

    # Test for changepoints
    print("\n--- Changepoint Detection ---")
    changepoints = test_changepoints(ht_series)
    if 'error' not in changepoints:
        print(f"  Changepoints detected: {changepoints['n_changepoints']}")
        if changepoints['n_changepoints'] > 0:
            cp_folios = [azc_sequence[i+1]['folio'] for i in changepoints['positions'] if i+1 < len(azc_sequence)]
            print(f"  At positions: {cp_folios}")
    else:
        print(f"  {changepoints['error']}")

    # Zodiac vs Non-Zodiac comparison
    print("\n--- Zodiac vs Non-Zodiac ---")
    subgroup = analyze_zodiac_vs_nonzodiac(azc_sequence)

    for name, data in subgroup.items():
        if 'error' not in data:
            print(f"\n  {name.upper()}:")
            print(f"    N: {data['n_folios']}")
            print(f"    Mean HT: {data['mean_ht']:.4f}")
            print(f"    CV: {data['cv']:.4f}")
            print(f"    Trend: {data['trend']['direction']} (p={data['trend']['p_value']:.4f})")
        else:
            print(f"\n  {name.upper()}: {data['error']}")

    # HT trajectory visualization (text-based)
    print("\n--- HT Trajectory (text visualization) ---")
    max_bar = 40
    max_ht = max(ht_series)
    for i, item in enumerate(azc_sequence):
        bar_len = int((item['ht_density'] / max_ht) * max_bar)
        bar = "#" * bar_len
        print(f"  {item['folio']:8s} |{bar}")

    # Compile results
    results = {
        'metadata': {
            'analysis': 'E5 - AZC Internal Oscillation Test',
            'description': 'Testing for micro-oscillations within AZC block',
            'n_azc_folios': len(azc_sequence),
            'manuscript_span': (azc_sequence[0]['position'], azc_sequence[-1]['position'])
        },
        'statistics': {
            'mean_ht': float(np.mean(ht_series)),
            'std_ht': float(np.std(ht_series)),
            'cv': float(np.std(ht_series) / np.mean(ht_series)),
            'range': (float(np.min(ht_series)), float(np.max(ht_series)))
        },
        'trend_test': trend,
        'autocorrelation': autocorr if isinstance(autocorr, list) else [autocorr],
        'periodicity': period_result,
        'global_comparison': global_comparison,
        'changepoints': changepoints,
        'subgroup_analysis': subgroup,
        'folio_sequence': [
            {'folio': x['folio'], 'position': x['position'], 'ht_density': x['ht_density']}
            for x in azc_sequence
        ]
    }

    # Key findings
    print("\n" + "=" * 50)
    print("KEY FINDINGS")
    print("=" * 50)

    key_findings = []

    # Check for significant oscillation
    sig_autocorr = [ac for ac in autocorr if isinstance(ac, dict) and ac.get('significant')]
    if sig_autocorr:
        key_findings.append({
            'finding': f'Significant autocorrelation at lag {sig_autocorr[0]["lag"]}',
            'interpretation': 'AZC block has internal oscillation structure'
        })
    else:
        key_findings.append({
            'finding': 'No significant autocorrelation detected',
            'interpretation': 'AZC block HT is not strongly oscillatory'
        })

    # Check trend
    if trend['significant']:
        key_findings.append({
            'finding': f'Significant {trend["direction"]} trend (p={trend["p_value"]:.4f})',
            'interpretation': 'HT changes systematically through AZC block'
        })
    else:
        key_findings.append({
            'finding': 'No significant internal trend',
            'interpretation': 'HT is relatively flat within AZC'
        })

    # Check rhythm match
    if global_comparison['interpretation'] == 'MATCHES_GLOBAL':
        key_findings.append({
            'finding': 'AZC internal rhythm matches global ~10-folio rhythm',
            'interpretation': 'Same attention dynamics at micro and macro scale'
        })
    elif global_comparison.get('azc_period'):
        key_findings.append({
            'finding': f'AZC rhythm ({global_comparison["azc_period"]:.1f}) differs from global (10)',
            'interpretation': f'{global_comparison["interpretation"]}'
        })

    results['key_findings'] = key_findings

    for kf in key_findings:
        print(f"\n* {kf['finding']}")
        print(f"  -> {kf['interpretation']}")

    # Save results
    results_dir = Path(__file__).parent.parent.parent / "results"
    output_path = results_dir / "azc_internal_oscillation.json"

    def convert_numpy(obj):
        """Convert numpy types to native Python types for JSON serialization."""
        if isinstance(obj, np.bool_):
            return bool(obj)
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return obj

    def sanitize_for_json(obj):
        """Recursively sanitize a nested structure for JSON."""
        if isinstance(obj, dict):
            return {k: sanitize_for_json(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [sanitize_for_json(v) for v in obj]
        else:
            return convert_numpy(obj)

    with open(output_path, 'w') as f:
        json.dump(sanitize_for_json(results), f, indent=2)

    print(f"\n\nResults saved to: {output_path}")


if __name__ == "__main__":
    main()
