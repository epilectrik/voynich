"""
E4 - AZC Entry Orientation Trace

Question: When the manuscript is entered at an AZC folio, does the local
neighborhood show a characteristic human-burden signature distinct from
non-AZC entry points?

This test is HT-centric, NOT execution-centric. It respects:
- C313: AZC constrains legality, not behavior
- C454: AZC does not modulate B execution
- C458: Hazard is clamped elsewhere
- C459: HT reflects human burden

What we trace:
- HT density
- HT change (delta)
- HT percentile
- Boundary anchoring rate

What we do NOT trace:
- CEI, hazard, recovery (those are B-internal)
"""

import json
import re
import numpy as np
from scipy import stats
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


def classify_folios(unified, folio_order):
    """Classify folios by system type."""
    azc_folios = []
    azc_zodiac = []
    azc_non_zodiac = []
    a_folios = []
    b_folios = []

    for folio in folio_order:
        profile = unified['profiles'].get(folio, {})
        system = profile.get('system')

        if system == 'AZC':
            azc_folios.append(folio)
            # Check if zodiac (typically f70-f73)
            match = re.match(r'f(\d+)', folio)
            if match:
                num = int(match.group(1))
                if 70 <= num <= 73:
                    azc_zodiac.append(folio)
                else:
                    azc_non_zodiac.append(folio)
        elif system == 'A':
            a_folios.append(folio)
        elif system == 'B':
            b_folios.append(folio)

    return {
        'azc_all': azc_folios,
        'azc_zodiac': azc_zodiac,
        'azc_non_zodiac': azc_non_zodiac,
        'a': a_folios,
        'b': b_folios
    }


def extract_ht_timeseries(unified, folio_order):
    """Extract HT metrics in manuscript order."""
    ht_density = []
    boundary_anchor = []

    for folio in folio_order:
        profile = unified['profiles'].get(folio, {})
        ht = profile.get('ht_density', 0) or 0
        ba = profile.get('ht_boundary_anchor_rate', 0) or 0
        ht_density.append(ht)
        boundary_anchor.append(ba)

    return {
        'ht_density': np.array(ht_density),
        'boundary_anchor': np.array(boundary_anchor),
        'folio_order': folio_order
    }


def zscore_normalize(series):
    """Z-score normalize to control for global trends."""
    mean = np.nanmean(series)
    std = np.nanstd(series)
    if std == 0:
        return np.zeros_like(series)
    return (series - mean) / std


def get_window_trajectory(timeseries, center_idx, window_size):
    """
    Extract a trajectory window centered on an index.
    Returns array of length 2*window_size+1, with NaN for out-of-bounds.
    """
    n = len(timeseries)
    trajectory = np.full(2 * window_size + 1, np.nan)

    for offset in range(-window_size, window_size + 1):
        idx = center_idx + offset
        if 0 <= idx < n:
            trajectory[offset + window_size] = timeseries[idx]

    return trajectory


def compute_entry_trajectories(ht_data, folio_indices, window_size=10):
    """
    Compute averaged HT trajectories for a set of entry folios.

    Returns:
        - mean trajectory (aligned at entry point = 0)
        - individual trajectories
        - relative positions (-window to +window)
    """
    ht_z = zscore_normalize(ht_data['ht_density'])
    ba_z = zscore_normalize(ht_data['boundary_anchor'])

    ht_trajectories = []
    ba_trajectories = []

    for idx in folio_indices:
        ht_traj = get_window_trajectory(ht_z, idx, window_size)
        ba_traj = get_window_trajectory(ba_z, idx, window_size)
        ht_trajectories.append(ht_traj)
        ba_trajectories.append(ba_traj)

    positions = list(range(-window_size, window_size + 1))

    # Average trajectories (ignoring NaN)
    ht_trajectories = np.array(ht_trajectories)
    ba_trajectories = np.array(ba_trajectories)

    mean_ht = np.nanmean(ht_trajectories, axis=0)
    mean_ba = np.nanmean(ba_trajectories, axis=0)

    return {
        'positions': positions,
        'mean_ht': mean_ht.tolist(),
        'mean_ba': mean_ba.tolist(),
        'individual_ht': ht_trajectories.tolist(),
        'n_entries': len(folio_indices)
    }


def test_step_change(trajectories, window_size):
    """
    Test for step-change at entry point.
    Compares pre-entry mean to post-entry mean.
    """
    mean_ht = np.array(trajectories['mean_ht'])

    # Pre-entry: positions -window to -1
    pre_entry = mean_ht[:window_size]
    # Post-entry: positions +1 to +window
    post_entry = mean_ht[window_size + 1:]
    # At entry: position 0
    at_entry = mean_ht[window_size]

    # Clean NaN
    pre_clean = pre_entry[~np.isnan(pre_entry)]
    post_clean = post_entry[~np.isnan(post_entry)]

    if len(pre_clean) < 2 or len(post_clean) < 2:
        return {
            'pre_mean': None,
            'post_mean': None,
            'at_entry': at_entry if not np.isnan(at_entry) else None,
            'step_change': None,
            'p_value': None,
            'significant': False
        }

    pre_mean = np.mean(pre_clean)
    post_mean = np.mean(post_clean)
    step_change = post_mean - pre_mean

    # t-test
    stat, p = stats.ttest_ind(pre_clean, post_clean)

    return {
        'pre_mean': float(pre_mean),
        'post_mean': float(post_mean),
        'at_entry': float(at_entry) if not np.isnan(at_entry) else None,
        'step_change': float(step_change),
        't_statistic': float(stat),
        'p_value': float(p),
        'significant': p < 0.05
    }


def test_gradient(trajectories, window_size):
    """
    Test for gradient (trend) in trajectory.
    Uses linear regression on positions.
    """
    positions = np.array(trajectories['positions'])
    mean_ht = np.array(trajectories['mean_ht'])

    # Filter NaN
    valid = ~np.isnan(mean_ht)
    if np.sum(valid) < 5:
        return {
            'slope': None,
            'p_value': None,
            'significant': False
        }

    slope, intercept, r, p, se = stats.linregress(positions[valid], mean_ht[valid])

    return {
        'slope': float(slope),
        'intercept': float(intercept),
        'r_squared': float(r**2),
        'p_value': float(p),
        'significant': p < 0.05,
        'interpretation': 'pre-rise' if slope > 0 else 'decay' if slope < 0 else 'flat'
    }


def compare_entry_types(azc_traj, control_traj, label):
    """Compare AZC entry trajectories to a control group."""
    azc_ht = np.array(azc_traj['mean_ht'])
    control_ht = np.array(control_traj['mean_ht'])

    # Compare at entry point
    azc_at_entry = azc_ht[len(azc_ht) // 2]
    control_at_entry = control_ht[len(control_ht) // 2]

    # Compare overall patterns using correlation
    valid = ~(np.isnan(azc_ht) | np.isnan(control_ht))
    if np.sum(valid) < 5:
        return {
            'vs': label,
            'correlation': None,
            'p_value': None,
            'interpretation': 'insufficient data'
        }

    r, p = stats.pearsonr(azc_ht[valid], control_ht[valid])

    # Kolmogorov-Smirnov test for distribution difference
    ks_stat, ks_p = stats.ks_2samp(
        azc_ht[~np.isnan(azc_ht)],
        control_ht[~np.isnan(control_ht)]
    )

    return {
        'vs': label,
        'azc_at_entry': float(azc_at_entry) if not np.isnan(azc_at_entry) else None,
        'control_at_entry': float(control_at_entry) if not np.isnan(control_at_entry) else None,
        'trajectory_correlation': float(r),
        'correlation_p': float(p),
        'ks_statistic': float(ks_stat),
        'ks_p_value': float(ks_p),
        'patterns_differ': ks_p < 0.05
    }


def random_control_sample(folio_order, exclude_indices, n_samples, seed=42):
    """Generate random control indices excluding specified folios."""
    np.random.seed(seed)
    all_indices = set(range(len(folio_order)))
    valid_indices = list(all_indices - set(exclude_indices))
    return np.random.choice(valid_indices, size=min(n_samples, len(valid_indices)), replace=False).tolist()


def main():
    print("E4 - AZC Entry Orientation Trace")
    print("=" * 50)

    # Load data
    unified = load_data()
    folio_order = get_folio_order(unified)
    folio_to_idx = {f: i for i, f in enumerate(folio_order)}

    # Classify folios
    classified = classify_folios(unified, folio_order)
    print(f"\nFolio classification:")
    print(f"  AZC total: {len(classified['azc_all'])}")
    print(f"  AZC zodiac (f70-f73): {len(classified['azc_zodiac'])}")
    print(f"  AZC non-zodiac: {len(classified['azc_non_zodiac'])}")
    print(f"  Currier A: {len(classified['a'])}")
    print(f"  Currier B: {len(classified['b'])}")

    # Extract HT timeseries
    ht_data = extract_ht_timeseries(unified, folio_order)

    # Get indices for each group
    azc_indices = [folio_to_idx[f] for f in classified['azc_all'] if f in folio_to_idx]
    azc_zodiac_indices = [folio_to_idx[f] for f in classified['azc_zodiac'] if f in folio_to_idx]
    azc_nonzodiac_indices = [folio_to_idx[f] for f in classified['azc_non_zodiac'] if f in folio_to_idx]
    a_indices = [folio_to_idx[f] for f in classified['a'] if f in folio_to_idx]
    b_indices = [folio_to_idx[f] for f in classified['b'] if f in folio_to_idx]

    # Random control
    random_indices = random_control_sample(folio_order, azc_indices, len(azc_indices) * 2)

    # Compute trajectories for each window size
    results = {
        'metadata': {
            'analysis': 'E4 - AZC Entry Orientation Trace',
            'description': 'Testing if AZC folios show distinct HT patterns in local neighborhood',
            'n_folios': len(folio_order),
            'n_azc': len(azc_indices),
            'n_azc_zodiac': len(azc_zodiac_indices),
            'n_azc_non_zodiac': len(azc_nonzodiac_indices),
            'window_sizes_tested': [5, 10, 15]
        },
        'analyses': {}
    }

    for window_size in [5, 10, 15]:
        print(f"\n--- Window size: +/-{window_size} folios ---")

        # Compute trajectories
        azc_traj = compute_entry_trajectories(ht_data, azc_indices, window_size)
        azc_zodiac_traj = compute_entry_trajectories(ht_data, azc_zodiac_indices, window_size) if azc_zodiac_indices else None
        azc_nonzodiac_traj = compute_entry_trajectories(ht_data, azc_nonzodiac_indices, window_size) if azc_nonzodiac_indices else None
        a_traj = compute_entry_trajectories(ht_data, a_indices, window_size)
        b_traj = compute_entry_trajectories(ht_data, b_indices, window_size)
        random_traj = compute_entry_trajectories(ht_data, random_indices, window_size)

        # Test step change at AZC entry
        azc_step = test_step_change(azc_traj, window_size)
        print(f"\nAZC step-change test:")
        print(f"  Pre-entry HT (z): {azc_step['pre_mean']:.3f}" if azc_step['pre_mean'] else "  Pre-entry: N/A")
        print(f"  Post-entry HT (z): {azc_step['post_mean']:.3f}" if azc_step['post_mean'] else "  Post-entry: N/A")
        print(f"  Step change: {azc_step['step_change']:.3f}" if azc_step['step_change'] else "  Step change: N/A")
        print(f"  p-value: {azc_step['p_value']:.4f}" if azc_step['p_value'] else "  p-value: N/A")
        print(f"  Significant: {azc_step['significant']}")

        # Test gradient
        azc_gradient = test_gradient(azc_traj, window_size)
        print(f"\nAZC gradient test:")
        print(f"  Slope: {azc_gradient['slope']:.4f}" if azc_gradient['slope'] else "  Slope: N/A")
        print(f"  R^2: {azc_gradient['r_squared']:.4f}" if azc_gradient.get('r_squared') else "  R^2: N/A")
        print(f"  Interpretation: {azc_gradient.get('interpretation', 'N/A')}")

        # Compare AZC to controls
        comparisons = []

        vs_random = compare_entry_types(azc_traj, random_traj, 'random')
        comparisons.append(vs_random)
        print(f"\nAZC vs Random:")
        print(f"  Trajectory correlation: {vs_random['trajectory_correlation']:.3f}" if vs_random['trajectory_correlation'] else "  N/A")
        print(f"  KS test p-value: {vs_random['ks_p_value']:.4f}" if vs_random['ks_p_value'] else "  N/A")
        print(f"  Patterns differ: {vs_random['patterns_differ']}")

        vs_a = compare_entry_types(azc_traj, a_traj, 'currier_a')
        comparisons.append(vs_a)
        print(f"\nAZC vs Currier A:")
        print(f"  Trajectory correlation: {vs_a['trajectory_correlation']:.3f}" if vs_a['trajectory_correlation'] else "  N/A")
        print(f"  KS test p-value: {vs_a['ks_p_value']:.4f}" if vs_a['ks_p_value'] else "  N/A")
        print(f"  Patterns differ: {vs_a['patterns_differ']}")

        vs_b = compare_entry_types(azc_traj, b_traj, 'currier_b')
        comparisons.append(vs_b)
        print(f"\nAZC vs Currier B:")
        print(f"  Trajectory correlation: {vs_b['trajectory_correlation']:.3f}" if vs_b['trajectory_correlation'] else "  N/A")
        print(f"  KS test p-value: {vs_b['ks_p_value']:.4f}" if vs_b['ks_p_value'] else "  N/A")
        print(f"  Patterns differ: {vs_b['patterns_differ']}")

        # Zodiac vs non-zodiac comparison
        zodiac_comparison = None
        if azc_zodiac_traj and azc_nonzodiac_traj:
            zodiac_step = test_step_change(azc_zodiac_traj, window_size)
            nonzodiac_step = test_step_change(azc_nonzodiac_traj, window_size)

            zodiac_comparison = {
                'zodiac_step': zodiac_step,
                'non_zodiac_step': nonzodiac_step,
                'zodiac_trajectory': azc_zodiac_traj['mean_ht'],
                'non_zodiac_trajectory': azc_nonzodiac_traj['mean_ht']
            }

            print(f"\nZodiac vs Non-Zodiac AZC:")
            print(f"  Zodiac step: {zodiac_step['step_change']:.3f}" if zodiac_step['step_change'] else "  N/A")
            print(f"  Non-zodiac step: {nonzodiac_step['step_change']:.3f}" if nonzodiac_step['step_change'] else "  N/A")

        # Store results
        results['analyses'][f'window_{window_size}'] = {
            'azc_trajectory': {
                'positions': azc_traj['positions'],
                'mean_ht': azc_traj['mean_ht'],
                'mean_boundary_anchor': azc_traj['mean_ba'],
                'n_entries': azc_traj['n_entries']
            },
            'step_change_test': azc_step,
            'gradient_test': azc_gradient,
            'comparisons': comparisons,
            'zodiac_comparison': zodiac_comparison
        }

    # Synthesize findings
    print("\n" + "=" * 50)
    print("KEY FINDINGS")
    print("=" * 50)

    key_findings = []

    # Check for consistent patterns across window sizes
    step_changes = [results['analyses'][f'window_{w}']['step_change_test'] for w in [5, 10, 15]]
    significant_steps = sum(1 for s in step_changes if s.get('significant', False))

    if significant_steps >= 2:
        key_findings.append({
            'finding': f'AZC entry shows significant step-change in {significant_steps}/3 window sizes',
            'interpretation': 'AZC entry marks an HT transition point'
        })
    else:
        key_findings.append({
            'finding': f'AZC entry shows step-change in only {significant_steps}/3 window sizes',
            'interpretation': 'No robust step-change at AZC entry'
        })

    # Check for pattern differences vs controls
    window_10 = results['analyses']['window_10']
    diffs = [c for c in window_10['comparisons'] if c.get('patterns_differ', False)]
    if diffs:
        key_findings.append({
            'finding': f'AZC trajectory differs significantly from: {[d["vs"] for d in diffs]}',
            'interpretation': 'AZC entry has distinct HT pattern'
        })
    else:
        key_findings.append({
            'finding': 'AZC trajectory does not significantly differ from controls',
            'interpretation': 'AZC orientation may be strictly local to diagrams'
        })

    results['key_findings'] = key_findings

    for kf in key_findings:
        print(f"\n* {kf['finding']}")
        print(f"  -> {kf['interpretation']}")

    # Save results
    results_dir = Path(__file__).parent.parent.parent / "results"
    output_path = results_dir / "azc_entry_orientation_trace.json"

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
