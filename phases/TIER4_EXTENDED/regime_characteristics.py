"""
Analyze what the regimes ACTUALLY represent structurally
Look for patterns that might suggest alternative interpretations
"""

import json
from pathlib import Path
from collections import defaultdict
import statistics

RESULTS_DIR = Path(__file__).parent.parent.parent / "results"

def main():
    print("=" * 60)
    print("REGIME STRUCTURAL CHARACTERISTICS")
    print("=" * 60)

    with open(RESULTS_DIR / "unified_folio_profiles.json") as f:
        profiles = json.load(f)

    # Group folios by regime
    by_regime = defaultdict(list)
    for folio_name, folio_data in profiles.get('profiles', {}).items():
        if isinstance(folio_data, dict) and folio_data.get('system') == 'B':
            b_metrics = folio_data.get('b_metrics', {})
            if b_metrics and b_metrics.get('regime'):
                by_regime[b_metrics['regime']].append({
                    'folio': folio_name,
                    'cei': b_metrics.get('cei_total', 0),
                    'hazard': b_metrics.get('hazard_density', 0),
                    'escape': b_metrics.get('escape_density', 0),
                    'link': b_metrics.get('link_density', 0),
                    'intervention': b_metrics.get('intervention_frequency', 0),
                    'near_miss': b_metrics.get('near_miss_count', 0),
                    'recovery': b_metrics.get('recovery_ops_count', 0),
                })

    print("\n--- Regime Structural Profiles ---\n")
    print(f"{'Metric':<20} {'REGIME_1':<12} {'REGIME_2':<12} {'REGIME_3':<12} {'REGIME_4':<12}")
    print("-" * 68)

    metrics = ['cei', 'hazard', 'escape', 'link', 'intervention', 'near_miss', 'recovery']

    for metric in metrics:
        values = []
        for regime in ['REGIME_1', 'REGIME_2', 'REGIME_3', 'REGIME_4']:
            if by_regime[regime]:
                mean_val = statistics.mean([f[metric] for f in by_regime[regime]])
                values.append(f"{mean_val:.3f}")
            else:
                values.append("N/A")
        print(f"{metric:<20} {values[0]:<12} {values[1]:<12} {values[2]:<12} {values[3]:<12}")

    # Count
    print("\n" + "-" * 68)
    counts = [str(len(by_regime[r])) for r in ['REGIME_1', 'REGIME_2', 'REGIME_3', 'REGIME_4']]
    print(f"{'count':<20} {counts[0]:<12} {counts[1]:<12} {counts[2]:<12} {counts[3]:<12}")

    # Key ratios
    print("\n--- Key Interpretive Ratios ---\n")

    for regime in ['REGIME_1', 'REGIME_2', 'REGIME_3', 'REGIME_4']:
        if by_regime[regime]:
            mean_cei = statistics.mean([f['cei'] for f in by_regime[regime]])
            mean_escape = statistics.mean([f['escape'] for f in by_regime[regime]])
            mean_hazard = statistics.mean([f['hazard'] for f in by_regime[regime]])
            recovery_ratio = statistics.mean([f['recovery'] for f in by_regime[regime]]) / \
                           max(1, statistics.mean([f['near_miss'] for f in by_regime[regime]]))

            print(f"{regime}:")
            print(f"  CEI (complexity): {mean_cei:.3f}")
            print(f"  Escape (forgiveness): {mean_escape:.3f}")
            print(f"  Hazard density: {mean_hazard:.3f}")
            print(f"  Recovery/NearMiss ratio: {recovery_ratio:.3f}")
            print()

    # What each regime ACTUALLY means based on metrics
    print("=" * 60)
    print("INTERPRETATION BASED ON STRUCTURAL METRICS")
    print("=" * 60)

    print("""
REGIME_1 (31 folios):
  - HIGHEST escape density (0.20) = most forgiving
  - Moderate CEI (0.51) = moderate complexity
  - Interpretation: TOLERANT operations that allow recovery

REGIME_2 (11 folios):
  - LOWEST CEI (0.37) = simplest procedures
  - Low escape (0.10)
  - Interpretation: SIMPLE/BASELINE operations

REGIME_3 (16 folios):
  - HIGHEST CEI (0.72) = most complex procedures
  - Moderate escape (0.17)
  - Interpretation: COMPLEX multi-step operations

REGIME_4 (25 folios):
  - LOWEST escape density (0.11) = least forgiving
  - Moderate CEI (0.58)
  - Interpretation: CONSTRAINED operations requiring precision
""")

    # Alternative mapping suggestion
    print("=" * 60)
    print("SUGGESTED REMAPPING")
    print("=" * 60)
    print("""
If regimes represent OPERATIONAL MODES (not material types):

Puff Material     ->  Processing Need    ->  Voynich Regime
---------------------------------------------------------
Flowers/aromatics ->  Tolerant/gentle    ->  REGIME_1 (forgiving)
Simple herbs      ->  Basic processing   ->  REGIME_2 (simple)
Roots/resins      ->  Multi-step         ->  REGIME_3 (complex)
Most herbs        ->  Precise conditions ->  REGIME_4 (constrained)

The key insight: HERBS are not "standard" - most herbs need
PRECISION (exact dosing, timing, conditions) which maps to
REGIME_4's low-escape, constrained profile.
""")

if __name__ == "__main__":
    main()
