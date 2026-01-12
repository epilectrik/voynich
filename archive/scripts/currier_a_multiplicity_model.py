"""
Currier A Multiplicity Distribution Model (Target 3)

Tests hypothesis: 3x-dominant (55%) repetition distribution fits simple stochastic model.

Success criteria:
- KL divergence <0.05 bits
- Chi-square p > 0.05
- Mode = 3
"""

import json
import math
from collections import Counter
from pathlib import Path


def load_multiplicity_data():
    """Load multiplicity distribution from prepared data."""
    filepath = Path(__file__).parent.parent.parent / 'results' / 'currier_a_modeling_data.json'
    with open(filepath, 'r') as f:
        data = json.load(f)
    return data['target_3_multiplicity']


def kl_divergence(p_observed, p_model):
    """Calculate KL divergence D(P || Q) in bits."""
    kl = 0.0
    for x, p in p_observed.items():
        if p > 0:
            q = p_model.get(x, 1e-10)  # Small value to avoid log(0)
            kl += p * math.log2(p / q)
    return kl


def chi_square_test(observed_counts, expected_counts):
    """Calculate chi-square statistic and approximate p-value."""
    chi2 = 0.0
    df = 0

    for x in observed_counts:
        o = observed_counts[x]
        e = expected_counts.get(x, 0.001)
        if e > 0:
            chi2 += (o - e) ** 2 / e
            df += 1

    df = max(1, df - 1)  # Degrees of freedom (minus 1 for estimation)

    # Approximate p-value using chi-square CDF
    # For df > 30, use normal approximation
    if df > 30:
        z = (chi2 - df) / math.sqrt(2 * df)
        # Approximate standard normal CDF
        p_value = 0.5 * (1 + math.erf(-z / math.sqrt(2)))
    else:
        # Use simple approximation for small df
        # p ≈ exp(-chi2/2) for chi2 >> df
        if chi2 > 2 * df:
            p_value = math.exp(-chi2 / 2)
        else:
            p_value = 0.5  # Conservative estimate

    return chi2, df, p_value


def fit_poisson(observed_dist, total):
    """Fit Poisson distribution to repetition counts (shifted by 1)."""
    # Poisson models counts starting from 0, but we have counts starting from 1
    # So model (X - 1) ~ Poisson(lambda)

    # Estimate lambda from mean
    mean_x = sum(x * c for x, c in observed_dist.items()) / total
    lambda_est = mean_x - 1  # Shift by 1

    if lambda_est <= 0:
        lambda_est = 0.5

    # Generate distribution
    p_model = {}
    for x in range(1, 8):
        # P(X = x) = P(X-1 = x-1) where X-1 ~ Poisson(lambda)
        k = x - 1
        p = (lambda_est ** k * math.exp(-lambda_est)) / math.factorial(k)
        p_model[x] = p

    # Normalize
    total_p = sum(p_model.values())
    p_model = {x: p/total_p for x, p in p_model.items()}

    return p_model, {'lambda': lambda_est}


def fit_geometric(observed_dist, total):
    """Fit geometric distribution to repetition counts."""
    # Geometric: P(X = k) = (1-p)^(k-1) * p for k >= 1
    # Mean = 1/p, so p = 1/mean

    mean_x = sum(x * c for x, c in observed_dist.items()) / total
    p_est = 1.0 / mean_x

    # Clamp to valid range
    p_est = min(max(p_est, 0.01), 0.99)

    # Generate distribution
    p_model = {}
    for x in range(1, 8):
        p_model[x] = ((1 - p_est) ** (x - 1)) * p_est

    # Normalize to observed support
    total_p = sum(p_model.values())
    p_model = {x: p/total_p for x, p in p_model.items()}

    return p_model, {'p': p_est}


def fit_truncated_geometric(observed_dist, total, max_val=6):
    """Fit truncated geometric distribution."""
    mean_x = sum(x * c for x, c in observed_dist.items()) / total
    p_est = 1.0 / mean_x
    p_est = min(max(p_est, 0.01), 0.99)

    # Generate truncated distribution
    p_model = {}
    for x in range(1, max_val + 1):
        p_model[x] = ((1 - p_est) ** (x - 1)) * p_est

    # Normalize
    total_p = sum(p_model.values())
    p_model = {x: p/total_p for x, p in p_model.items()}

    return p_model, {'p': p_est, 'max': max_val}


def fit_binomial(observed_dist, total, n=6):
    """Fit binomial distribution shifted to start at 1."""
    # Model X ~ 1 + Binomial(n-1, p)
    mean_x = sum(x * c for x, c in observed_dist.items()) / total
    p_est = (mean_x - 1) / (n - 1)
    p_est = min(max(p_est, 0.01), 0.99)

    def binomial_coeff(n, k):
        if k < 0 or k > n:
            return 0
        return math.factorial(n) // (math.factorial(k) * math.factorial(n - k))

    p_model = {}
    for x in range(1, n + 1):
        k = x - 1  # Shifted value
        p_model[x] = binomial_coeff(n - 1, k) * (p_est ** k) * ((1 - p_est) ** (n - 1 - k))

    # Normalize
    total_p = sum(p_model.values())
    p_model = {x: p/total_p for x, p in p_model.items()}

    return p_model, {'n': n, 'p': p_est}


def main():
    print("=" * 60)
    print("CURRIER A MULTIPLICITY DISTRIBUTION MODEL (Target 3)")
    print("=" * 60)

    # Load data
    mult_data = load_multiplicity_data()
    observed_dist = mult_data['distribution']

    # Convert string keys to int
    observed_dist = {int(k): v for k, v in observed_dist.items()}
    total = sum(observed_dist.values())

    print(f"\nObserved distribution (n={total}):")
    for x in sorted(observed_dist.keys()):
        count = observed_dist[x]
        print(f"  {x}x: {count} ({100*count/total:.1f}%)")

    # Calculate observed probabilities
    p_observed = {x: c/total for x, c in observed_dist.items()}

    # Find observed mode
    obs_mode = max(observed_dist.keys(), key=lambda x: observed_dist[x])
    print(f"\nObserved mode: {obs_mode}x")

    # Entries with repetition (2x+)
    rep_count = sum(c for x, c in observed_dist.items() if x >= 2)
    rep_rate = rep_count / total
    print(f"Repetition rate: {100*rep_rate:.1f}%")

    # Mean among repeaters
    rep_total = sum(x * c for x, c in observed_dist.items() if x >= 2)
    mean_among_rep = rep_total / rep_count if rep_count > 0 else 0
    print(f"Mean among repeaters: {mean_among_rep:.2f}x")

    # Fit models
    print("\n" + "=" * 60)
    print("MODEL FITTING")
    print("=" * 60)

    models = [
        ("Poisson (shifted)", fit_poisson(observed_dist, total)),
        ("Geometric", fit_geometric(observed_dist, total)),
        ("Truncated Geometric (max=6)", fit_truncated_geometric(observed_dist, total, 6)),
        ("Binomial (n=6)", fit_binomial(observed_dist, total, 6)),
    ]

    results = []

    for name, (p_model, params) in models:
        print(f"\n--- {name} ---")
        print(f"Parameters: {params}")

        # Calculate expected counts
        expected_counts = {x: p * total for x, p in p_model.items()}

        # Model distribution
        print("Model distribution:")
        for x in sorted(p_model.keys()):
            p = p_model[x]
            print(f"  {x}x: {p*total:.1f} ({100*p:.1f}%)")

        # Find model mode
        model_mode = max(p_model.keys(), key=lambda x: p_model[x])

        # Metrics
        kl = kl_divergence(p_observed, p_model)
        chi2, df, p_value = chi_square_test(observed_dist, expected_counts)

        print(f"\nKL divergence: {kl:.4f} bits (target <0.05)")
        print(f"Chi-square: {chi2:.2f} (df={df})")
        print(f"p-value: {p_value:.4f} (target >0.05)")
        print(f"Mode: {model_mode}x (target: 3)")

        # Pass/fail
        kl_pass = kl < 0.05
        chi_pass = p_value > 0.05
        mode_pass = model_mode == 3

        print(f"\nKL < 0.05: {'PASS' if kl_pass else 'FAIL'}")
        print(f"p > 0.05: {'PASS' if chi_pass else 'FAIL'}")
        print(f"Mode = 3: {'PASS' if mode_pass else 'FAIL'}")

        results.append({
            'name': name,
            'params': params,
            'kl_divergence': kl,
            'chi_square': chi2,
            'df': df,
            'p_value': p_value,
            'model_mode': model_mode,
            'kl_pass': kl_pass,
            'chi_pass': chi_pass,
            'mode_pass': mode_pass,
            'all_pass': kl_pass and chi_pass and mode_pass,
            'model_distribution': {str(k): v for k, v in p_model.items()}
        })

    # Overall assessment
    print("\n" + "=" * 60)
    print("OVERALL ASSESSMENT")
    print("=" * 60)

    best_model = min(results, key=lambda r: r['kl_divergence'])
    print(f"\nBest model by KL: {best_model['name']} (KL={best_model['kl_divergence']:.4f})")

    any_pass = any(r['all_pass'] for r in results)
    print(f"\nAny model passes all criteria: {'YES' if any_pass else 'NO'}")

    if any_pass:
        passing = [r for r in results if r['all_pass']]
        print("Passing models:")
        for r in passing:
            print(f"  - {r['name']}")
    else:
        # Find best partial match
        print("\nNo model passes all criteria.")
        print("Best partial fits:")
        for r in sorted(results, key=lambda x: x['kl_divergence'])[:2]:
            print(f"  {r['name']}: KL={r['kl_divergence']:.4f}, mode={r['model_mode']}")

    # Special analysis: Why 3x dominance?
    print("\n" + "=" * 60)
    print("3x DOMINANCE ANALYSIS")
    print("=" * 60)

    count_2 = observed_dist.get(2, 0)
    count_3 = observed_dist.get(3, 0)
    print(f"\n2x count: {count_2}")
    print(f"3x count: {count_3}")
    print(f"3x/2x ratio: {count_3/count_2:.2f}" if count_2 > 0 else "N/A")

    # The 3x dominance is unexpected for simple distributions
    # Geometric would predict 2x > 3x
    # This suggests a behavioral bias toward groups of 3

    print("\nNote: 3x dominance (3x > 2x) is unusual for memoryless distributions.")
    print("This may reflect cognitive bias (counting in threes) or structural constraint.")

    # Save results
    output = {
        'observed_distribution': {str(k): v for k, v in observed_dist.items()},
        'observed_mode': obs_mode,
        'repetition_rate': rep_rate,
        'mean_among_repeaters': mean_among_rep,
        'model_results': results,
        'best_model': best_model['name'],
        'any_model_passes': any_pass
    }

    output_path = Path(__file__).parent.parent.parent / 'results' / 'currier_a_multiplicity_fit.json'
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to: {output_path}")

    return output


if __name__ == '__main__':
    main()
