#!/usr/bin/env python3
"""
S2b: Length-confound check on T2 per-folio z_mu.

Expert-advisor flagged: 'Larger folios have more tokens and can generate
stronger z scores. The mean z=-1.27 doesn't account for folio size variance.
A regression of z_mu on log(n_tokens) would tell you whether the per-folio
effect is genuine or scale-driven.'

This script regresses z_mu on log(n_tokens). If the slope is significantly
negative, larger folios drive more negative z; the question becomes whether
residuals (after removing log-length effect) still have mean significantly < 0.
"""
import sys
import json
import math
import statistics
from pathlib import Path

RESULTS = Path(__file__).resolve().parent.parent / 'results'
t2 = json.loads((RESULTS / 't2_per_folio_zscores.json').read_text())


def linreg(xs, ys):
    """Simple OLS regression. Returns (slope, intercept, r, residuals)."""
    n = len(xs)
    mean_x = sum(xs) / n
    mean_y = sum(ys) / n
    sxx = sum((x - mean_x) ** 2 for x in xs)
    sxy = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
    slope = sxy / sxx
    intercept = mean_y - slope * mean_x
    fitted = [slope * x + intercept for x in xs]
    residuals = [y - f for y, f in zip(ys, fitted)]
    syy = sum((y - mean_y) ** 2 for y in ys)
    sse = sum(r ** 2 for r in residuals)
    r2 = 1 - sse / syy if syy > 0 else 0
    r = math.copysign(math.sqrt(abs(r2)), slope)

    # Standard error of slope, t-stat
    se_slope = math.sqrt(sse / (n - 2) / sxx) if sxx > 0 else 0
    t_slope = slope / se_slope if se_slope > 0 else 0

    # Approx p-value via normal approx (n large)
    p_two = 2 * (1 - 0.5 * (1 + math.erf(abs(t_slope) / math.sqrt(2))))
    return slope, intercept, r, r2, residuals, t_slope, p_two


def one_sample_t(values, mu0=0.0):
    n = len(values)
    mean_v = statistics.mean(values)
    std_v = statistics.stdev(values)
    se = std_v / math.sqrt(n)
    t = (mean_v - mu0) / se
    p = 0.5 * (1 + math.erf(t / math.sqrt(2)))  # one-sided lower
    return t, mean_v, std_v, p


def main():
    folios = t2['per_folio']
    log_n = [math.log(f['n_tokens']) for f in folios]
    z_mu = [f['z_mu'] for f in folios]

    print("Length-confound regression: z_mu ~ log(n_tokens)")
    print(f"  N folios: {len(folios)}")
    print(f"  log(n_tokens) range: [{min(log_n):.2f}, {max(log_n):.2f}]")
    print(f"  n_tokens range: [{min(f['n_tokens'] for f in folios)}, "
          f"{max(f['n_tokens'] for f in folios)}]")

    slope, intercept, r, r2, residuals, t_slope, p_slope = linreg(log_n, z_mu)
    print(f"\n  Regression z_mu = {slope:.3f} * log(n_tokens) + {intercept:.3f}")
    print(f"    slope t-stat = {t_slope:.2f}, two-sided p = {p_slope:.4f}")
    print(f"    r = {r:.3f}, R^2 = {r2:.3f}")

    if slope < 0 and p_slope < 0.05:
        print(f"\n  Length confound CONFIRMED: larger folios show more negative z_mu.")
    elif slope > 0 and p_slope < 0.05:
        print(f"\n  Length effect REVERSED: larger folios show LESS negative z_mu (smaller folios more constrained).")
    else:
        print(f"\n  No significant length effect.")

    # Residual analysis: after removing log-length effect, do residuals still have mean < 0?
    # This is the key test: if the per-folio order constraint is genuine (not size-driven),
    # then z_mu - fitted should have mean significantly less than the OVERALL mean,
    # but more importantly, the partial effect after controlling for size matters.
    #
    # Actually: residuals from regression have mean 0 by construction. The question is
    # whether the z_mu values themselves are below 0 even when controlling for size.
    # That is captured by the intercept term: at log(n_tokens) of typical folio,
    # what is the predicted z_mu?

    typical_log_n = statistics.median(log_n)
    typical_n = math.exp(typical_log_n)
    pred_zmu_typical = slope * typical_log_n + intercept
    print(f"\n  Typical folio (median n_tokens = {typical_n:.0f}): predicted z_mu = {pred_zmu_typical:.3f}")

    # Counterfactual: if we project to a folio with hypothetical 100 tokens (the cutoff)
    log_n_100 = math.log(100)
    pred_zmu_100 = slope * log_n_100 + intercept
    print(f"  Folio at cutoff (n=100): predicted z_mu = {pred_zmu_100:.3f}")

    # And at maximum
    log_n_max = max(log_n)
    pred_zmu_max = slope * log_n_max + intercept
    print(f"  Folio at maximum (n={int(math.exp(log_n_max))}): predicted z_mu = {pred_zmu_max:.3f}")

    # Test if the intercept-projected z_mu at small folios is still negative
    # If pred_zmu_100 < 0 by a meaningful margin, the effect is genuine even at small sizes
    print(f"\n  Interpretation:")
    if pred_zmu_100 < -0.5:
        print(f"    Even small folios (n=100) project to z_mu = {pred_zmu_100:.2f}")
        print(f"    Order constraint is genuine, not purely size-driven.")
    elif pred_zmu_100 < 0:
        print(f"    Small folios (n=100) project to weakly negative z_mu = {pred_zmu_100:.2f}")
        print(f"    Some order constraint at small sizes; effect amplified at larger sizes.")
    else:
        print(f"    Small folios project to positive z_mu; order constraint is size-amplified.")

    # Save to JSON
    out = {
        'test': 'T2-supplement: length confound',
        'n_folios': len(folios),
        'regression': {
            'slope': slope,
            'intercept': intercept,
            'r': r,
            'r_squared': r2,
            't_slope': t_slope,
            'p_two_sided': p_slope,
        },
        'predicted_zmu_at_n100': pred_zmu_100,
        'predicted_zmu_at_median': pred_zmu_typical,
        'predicted_zmu_at_max': pred_zmu_max,
        'median_n_tokens': typical_n,
        'min_n_tokens': min(f['n_tokens'] for f in folios),
        'max_n_tokens': max(f['n_tokens'] for f in folios),
        'interpretation': (
            'genuine_not_size_driven' if pred_zmu_100 < -0.5
            else 'genuine_with_size_amplification' if pred_zmu_100 < 0
            else 'size_driven'
        ),
    }
    out_path = RESULTS / 't2b_length_confound.json'
    with open(out_path, 'w') as f:
        json.dump(out, f, indent=2)
    print(f"\nResults written to {out_path}")


if __name__ == '__main__':
    main()
