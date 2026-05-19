"""
C475 audit: distribution of expected counts among "illegal" pairs.

C475 says: "Only 4.3% of MIDDLE pairs can legally co-occur; 95.7% are
statistically illegal." Methodology: pair is "illegal" if observed=0 AND
expected>0.5 under frequency-matched shuffle null (1000 permutations).

Audit question: what's the distribution of expected values among the 673,342
"illegal" pairs? If most have expected just-above-0.5 (e.g., 0.5-2 range),
the headline 95.7% is dominated by low-expectation "haven't seen yet at this
corpus size" pairs, not by robust forbidden pairs.

Crazy-expert prediction: real incompatibility under stricter threshold is
60-75%, not 95.7%.

Test design (no re-running the 1000-permutation null; use existing results):
  1. Replicate from the existing middle_incompatibility.json file
  2. For all "illegal" pairs, get the distribution of expected counts
  3. Recompute the "% illegal" rate at thresholds expected > 0.5, 1, 2, 5, 10
  4. Report how the headline number scales with threshold

If 95.7% drops dramatically at expected≥5 (the same N-floor we used in
PHASE_703 forbidden-bigram test), the constraint should be reframed:
  - "95.7% of pairs unattested" (descriptive, weak)
  - vs "X% of pairs have observed=0 but expected≥5 under frequency-matched
     null" (substantive, strong)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

ROOT = Path("C:/git/voynich")
INPUT = ROOT / 'phases' / 'MIDDLE_INCOMPATIBILITY' / 'results' / 'middle_incompatibility.json'
OUT = ROOT / 'phases' / 'C475_AUDIT' / 'results' / 'c475_audit.json'


def main():
    print("=" * 80)
    print("C475 AUDIT: Distribution of expected counts among 'illegal' pairs")
    print("=" * 80)

    d = json.load(open(INPUT, encoding='utf-8'))

    print("\nOriginal summary:")
    summary = d.get('summary', {})
    print(json.dumps(summary, indent=2))

    print("\nConfiguration:")
    config = d.get('configuration', {})
    print(json.dumps(config, indent=2))

    illegal_pairs = d.get('illegal_pairs', [])
    print(f"\nIllegal pairs in results JSON: {len(illegal_pairs)}")
    if illegal_pairs:
        sample = illegal_pairs[:5]
        print(f"Sample illegal pairs (first 5):")
        for p in sample:
            print(f"  {p}")

    # Look at expected value distribution
    expected_values = []
    for p in illegal_pairs:
        # Could be (pair_tuple, expected) or {pair, expected}
        if isinstance(p, dict):
            expected_values.append(p.get('expected', 0))
        elif isinstance(p, (list, tuple)) and len(p) >= 2:
            # last element is usually the expected count
            expected_values.append(p[-1] if isinstance(p[-1], (int, float)) else 0)

    print(f"\nIllegal pair expected-count distribution:")
    print(f"  Total illegal in JSON: {len(expected_values)}")
    if expected_values:
        thresholds = [0.5, 1.0, 2.0, 5.0, 10.0, 20.0, 50.0, 100.0]
        print(f"\n  {'Threshold':<12}{'N illegal at exp≥thr':>22}{'% of JSON illegal':>22}")
        print("  " + "-" * 60)
        for t in thresholds:
            count = sum(1 for e in expected_values if e >= t)
            pct = count / len(expected_values) * 100 if expected_values else 0
            print(f"  exp ≥ {t:<6}{count:>22}{pct:>21.2f}%")

    # The summary will tell us about total pairs vs illegal pairs
    summary_total_pairs = summary.get('total_pairs', 0)
    summary_illegal = summary.get('illegal_pairs_count',
                                   summary.get('illegal_pairs',
                                               summary.get('illegal', None)))
    if summary_total_pairs and summary_illegal:
        illegal_rate = summary_illegal / summary_total_pairs * 100
        print(f"\nFrom summary: {summary_illegal} illegal / {summary_total_pairs} total = {illegal_rate:.2f}%")

    # Pre-registered re-framing: what fraction of total possible pairs have
    # observed=0 AND expected ≥ 5 (our standard meaningful N-floor)?
    if expected_values and summary_total_pairs:
        n_robust = sum(1 for e in expected_values if e >= 5.0)
        robust_rate = n_robust / summary_total_pairs * 100
        n_at_05 = len(expected_values)
        rate_at_05 = n_at_05 / summary_total_pairs * 100
        print()
        print("=" * 80)
        print("RE-FRAMED METRIC (audit verdict)")
        print("=" * 80)
        print(f"\n  Original C475 claim: 95.7% pairs 'illegal' (obs=0 AND exp>0.5)")
        print(f"    -> Reproduces from JSON: {rate_at_05:.2f}% pairs with obs=0 + exp>0.5")
        print(f"\n  Audit metric: pairs with obs=0 AND exp ≥ 5 (robust N-floor)")
        print(f"    {n_robust} pairs / {summary_total_pairs} = {robust_rate:.2f}%")
        print(f"\n  Crazy-expert prediction: 60-75% under frequency-matched null")
        print(f"\n  Effect of stricter threshold: {rate_at_05:.1f}% -> {robust_rate:.1f}% "
              f"(reduction of {rate_at_05-robust_rate:.1f}pp)")

        if robust_rate < 50:
            verdict = (f"C475 LIKELY SPARSITY-DRIVEN: at exp≥5 threshold, only {robust_rate:.1f}% "
                       f"of pairs are robustly illegal. The 95.7% headline is dominated by "
                       "low-expectation pairs (haven't-seen-yet rather than forbidden). "
                       "Crazy-expert prediction confirmed: real incompatibility is much lower.")
        elif robust_rate < 75:
            verdict = (f"C475 PARTIALLY SPARSITY-DRIVEN: at exp≥5 threshold, {robust_rate:.1f}% "
                       f"of pairs are robustly illegal. The 95.7% headline overstates by "
                       f"{rate_at_05-robust_rate:.1f}pp. Reframe needed but not retract.")
        else:
            verdict = (f"C475 SURVIVES STRICTER THRESHOLD: at exp≥5, {robust_rate:.1f}% pairs "
                       "still illegal. Crazy-expert prediction NOT supported. The 95.7% "
                       "headline is methodologically defensible.")

        print(f"\n  VERDICT: {verdict}")
    else:
        verdict = "INSUFFICIENT data in JSON for verdict; full re-run needed"

    out = {
        "method": "C475 audit: distribution of expected counts among illegal pairs",
        "original_methodology_source": "phases/MIDDLE_INCOMPATIBILITY/middle_incompatibility.py",
        "original_threshold": 0.5,
        "audit_thresholds": [0.5, 1.0, 2.0, 5.0, 10.0, 20.0, 50.0, 100.0],
        "summary": summary,
        "config": config,
        "n_illegal_in_json": len(expected_values),
        "expected_distribution": {
            str(t): sum(1 for e in expected_values if e >= t) for t in [0.5, 1.0, 2.0, 5.0, 10.0, 20.0, 50.0, 100.0]
        },
        "verdict": verdict if isinstance(verdict, str) else None,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, indent=2, default=str), encoding='utf-8')
    print(f"\nResults written to {OUT.relative_to(ROOT)}")


if __name__ == '__main__':
    main()
