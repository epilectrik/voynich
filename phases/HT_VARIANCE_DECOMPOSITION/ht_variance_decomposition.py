#!/usr/bin/env python3
"""
HT Variance Decomposition

Question: Can incompatibility degree explain HT density?

Independent Variables (A-only predictors):
1. Local incompatibility density - mean degree of MIDDLE nodes in folio
2. Marginal coverage novelty - delta coverage from this folio
3. Tail pressure - proportion of rare MIDDLEs (bottom 50%)
4. Hub suppression signal - inverse hub usage rate

Dependent Variable:
- HT density per folio

Models:
1. Linear regression (sanity check)
2. Leave-one-out ablation (what breaks HT prediction?)

Interpretation:
- R² ~ 0.25-0.40 → HT is partially predictive (coarse vigilance)
- R² ~ 0.50+ → HT strongly tied to discrimination pressure
- R² ~ 0 → HT signals something else entirely (major discovery)
"""

import csv
import json
import numpy as np
from collections import defaultdict, Counter
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# Paths
BASE_PATH = Path(__file__).parent.parent.parent
DATA_FILE = BASE_PATH / "data" / "transcriptions" / "interlinear_full_words.txt"
OUTPUT_FILE = BASE_PATH / "results" / "ht_variance_decomposition.json"

# PREFIX definitions
PREFIXES = ['ch', 'qo', 'sh', 'da', 'ok', 'ot', 'ct', 'ol']
SUFFIXES = [
    'aiin', 'aiiin', 'ain', 'iin', 'in',
    'ar', 'or', 'al', 'ol', 'am', 'an',
    'dy', 'edy', 'eedy', 'chy', 'shy', 'ty', 'ky', 'ly', 'ry', 'y',
    'r', 'l', 's', 'd', 'n', 'm'
]

# AZC folios
ZODIAC_FOLIOS = {
    'f57v', 'f70v1', 'f70v2', 'f71r', 'f71v',
    'f72r1', 'f72r2', 'f72r3', 'f72v1', 'f72v2', 'f72v3',
    'f73r', 'f73v'
}
AC_FOLIOS = {
    'f116v', 'f65r', 'f65v', 'f67r1', 'f67r2', 'f67v1', 'f67v2',
    'f68r1', 'f68r2', 'f68r3', 'f68v1', 'f68v2', 'f68v3',
    'f69r', 'f69v', 'f70r1', 'f70r2'
}
ALL_AZC_FOLIOS = ZODIAC_FOLIOS | AC_FOLIOS

# HT prefixes (from architecture doc)
HT_PREFIXES = {'yk', 'op', 'yt', 'sa', 'so', 'ka', 'dc', 'pc'}


def decompose_token(token: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """Decompose token into PREFIX, MIDDLE, SUFFIX."""
    if not token or len(token) < 2:
        return None, None, None
    if token.startswith('[') or token.startswith('<') or '*' in token:
        return None, None, None

    prefix = None
    rest = token
    for p in sorted(PREFIXES, key=len, reverse=True):
        if token.startswith(p):
            prefix = p
            rest = token[len(p):]
            break

    suffix = None
    middle = rest
    for s in sorted(SUFFIXES, key=len, reverse=True):
        if rest.endswith(s) and len(rest) > len(s):
            suffix = s
            middle = rest[:-len(s)]
            break

    if not middle:
        middle = None

    return prefix, middle, suffix


def is_ht_token(token: str) -> bool:
    """Check if token is HT (has HT prefix or doesn't decompose into standard grammar)."""
    if not token:
        return False

    # Check for HT prefixes
    for hp in HT_PREFIXES:
        if token.startswith(hp):
            return True

    # Check if it decomposes into standard grammar
    prefix, middle, suffix = decompose_token(token)

    # If no standard prefix and no standard suffix, it's likely HT
    if prefix is None and suffix is None:
        return True

    return False


def load_data() -> Tuple[Dict, Dict, Dict, List[str], Counter]:
    """
    Load all data and return:
    - folio_middles: {folio -> list of MIDDLEs in A entries}
    - folio_ht_density: {folio -> HT density}
    - compatible: {middle -> set of compatible middles}
    - all_middles: sorted list
    - middle_freq: Counter of MIDDLE frequencies
    """
    folio_middles = defaultdict(list)
    folio_total_tokens = defaultdict(int)
    folio_ht_tokens = defaultdict(int)
    middle_counts = Counter()

    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            word = row.get('"word"', row.get('word', '')).strip().strip('"')
            folio = row.get('"folio"', row.get('folio', '')).strip().strip('"')

            if folio not in ALL_AZC_FOLIOS:
                continue

            folio_total_tokens[folio] += 1

            # Check if HT
            if is_ht_token(word):
                folio_ht_tokens[folio] += 1
            else:
                # Parse A token
                _, middle, _ = decompose_token(word)
                if middle:
                    folio_middles[folio].append(middle)
                    middle_counts[middle] += 1

    # Compute HT density per folio
    folio_ht_density = {}
    for folio in ALL_AZC_FOLIOS:
        total = folio_total_tokens.get(folio, 0)
        ht = folio_ht_tokens.get(folio, 0)
        folio_ht_density[folio] = ht / total if total > 0 else 0

    # Build compatibility graph from co-occurrence
    compatible = defaultdict(set)
    line_data = defaultdict(list)

    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            word = row.get('"word"', row.get('word', '')).strip().strip('"')
            folio = row.get('"folio"', row.get('folio', '')).strip().strip('"')
            line = row.get('"line_number"', row.get('line_number', '')).strip().strip('"')

            if folio not in ALL_AZC_FOLIOS:
                continue

            _, middle, _ = decompose_token(word)
            if middle:
                line_data[(folio, line)].append(middle)

    for key, middles in line_data.items():
        for i, m1 in enumerate(middles):
            for m2 in middles[i+1:]:
                compatible[m1].add(m2)
                compatible[m2].add(m1)

    all_middles = sorted(middle_counts.keys())

    return dict(folio_middles), folio_ht_density, dict(compatible), all_middles, middle_counts


def compute_folio_metrics(
    folio_middles: Dict[str, List[str]],
    compatible: Dict[str, Set[str]],
    middle_freq: Counter,
    all_middles: List[str]
) -> Dict[str, Dict]:
    """
    Compute per-folio A metrics.
    """
    # Identify tail and hub MIDDLEs
    sorted_middles = sorted(middle_freq.items(), key=lambda x: x[1])
    cutoff_50 = int(len(sorted_middles) * 0.50)
    tail_middles = set(m for m, c in sorted_middles[:cutoff_50])
    top_5 = sorted(middle_freq.items(), key=lambda x: x[1], reverse=True)[:5]
    hub_middles = set(m for m, c in top_5)

    # Compute cumulative coverage for novelty calculation
    folio_order = sorted(folio_middles.keys())
    seen_before = set()
    folio_novelty = {}

    for folio in folio_order:
        middles = set(folio_middles.get(folio, []))
        new_middles = middles - seen_before
        folio_novelty[folio] = len(new_middles) / len(middles) if middles else 0
        seen_before.update(middles)

    # Compute per-folio metrics
    folio_metrics = {}

    for folio, middles in folio_middles.items():
        if not middles:
            folio_metrics[folio] = {
                'incompatibility_density': 0,
                'novelty': 0,
                'tail_pressure': 0,
                'hub_suppression': 1.0
            }
            continue

        # Incompatibility density: mean degree of MIDDLEs
        # (inverted: higher degree = MORE compatible = LESS discriminating)
        degrees = [len(compatible.get(m, set())) for m in middles]
        mean_degree = np.mean(degrees) if degrees else 0
        max_possible_degree = len(all_middles) - 1

        # Invert: low degree = high discrimination pressure
        incompatibility_density = 1 - (mean_degree / max_possible_degree) if max_possible_degree > 0 else 0

        # Tail pressure: fraction of rare MIDDLEs
        tail_count = sum(1 for m in middles if m in tail_middles)
        tail_pressure = tail_count / len(middles)

        # Hub usage and suppression
        hub_count = sum(1 for m in middles if m in hub_middles)
        hub_usage = hub_count / len(middles)
        hub_suppression = 1 - hub_usage

        folio_metrics[folio] = {
            'incompatibility_density': incompatibility_density,
            'novelty': folio_novelty.get(folio, 0),
            'tail_pressure': tail_pressure,
            'hub_suppression': hub_suppression,
            'n_tokens': len(middles),
            'mean_degree': mean_degree
        }

    return folio_metrics


def run_regression(X: np.ndarray, y: np.ndarray, feature_names: List[str]) -> Dict:
    """Run linear regression and return results."""
    from sklearn.linear_model import LinearRegression
    from sklearn.metrics import r2_score, mean_squared_error

    model = LinearRegression()
    model.fit(X, y)

    y_pred = model.predict(X)
    r2 = r2_score(y, y_pred)
    mse = mean_squared_error(y, y_pred)

    # Compute p-values for coefficients (approximation)
    n = len(y)
    p = X.shape[1]
    residuals = y - y_pred
    ss_res = np.sum(residuals**2)
    var_res = ss_res / (n - p - 1) if n > p + 1 else 1e-10

    # Standard errors of coefficients
    XtX_inv = np.linalg.pinv(X.T @ X)
    se = np.sqrt(np.diag(XtX_inv) * var_res)

    t_stats = model.coef_ / (se + 1e-10)
    p_values = 2 * (1 - stats.t.cdf(np.abs(t_stats), df=n-p-1))

    return {
        'r2': r2,
        'mse': mse,
        'intercept': model.intercept_,
        'coefficients': dict(zip(feature_names, model.coef_)),
        'p_values': dict(zip(feature_names, p_values)),
        'n': n
    }


def run_ablation(X: np.ndarray, y: np.ndarray, feature_names: List[str]) -> Dict:
    """Run leave-one-feature-out ablation."""
    from sklearn.linear_model import LinearRegression
    from sklearn.metrics import r2_score

    # Full model R²
    full_model = LinearRegression()
    full_model.fit(X, y)
    full_r2 = r2_score(y, full_model.predict(X))

    # Ablation: remove each feature
    ablation_results = {}

    for i, feature in enumerate(feature_names):
        X_ablated = np.delete(X, i, axis=1)
        ablated_model = LinearRegression()
        ablated_model.fit(X_ablated, y)
        ablated_r2 = r2_score(y, ablated_model.predict(X_ablated))

        r2_drop = full_r2 - ablated_r2
        ablation_results[feature] = {
            'ablated_r2': ablated_r2,
            'r2_drop': r2_drop,
            'importance': r2_drop / full_r2 if full_r2 > 0 else 0
        }

    return {
        'full_r2': full_r2,
        'ablations': ablation_results
    }


def main():
    print("=" * 70)
    print("HT VARIANCE DECOMPOSITION")
    print("=" * 70)
    print("\nQuestion: Can incompatibility degree explain HT density?")
    print()

    # Step 1: Load data
    print("1. Loading data...")
    folio_middles, folio_ht_density, compatible, all_middles, middle_freq = load_data()
    n_folios = len([f for f in ALL_AZC_FOLIOS if f in folio_middles])
    print(f"   Loaded {n_folios} AZC folios with A data")

    # Step 2: Compute per-folio metrics
    print("\n2. Computing per-folio A metrics...")
    folio_metrics = compute_folio_metrics(folio_middles, compatible, middle_freq, all_middles)

    # Step 3: Build regression data
    print("\n3. Building regression dataset...")

    # Filter to folios with both HT and A data
    valid_folios = [f for f in ALL_AZC_FOLIOS if f in folio_metrics and f in folio_ht_density]
    valid_folios = [f for f in valid_folios if folio_metrics[f]['n_tokens'] > 0]

    print(f"   Valid folios with both HT and A data: {len(valid_folios)}")

    # Extract features and target
    feature_names = ['incompatibility_density', 'novelty', 'tail_pressure', 'hub_suppression']

    X = np.array([[
        folio_metrics[f]['incompatibility_density'],
        folio_metrics[f]['novelty'],
        folio_metrics[f]['tail_pressure'],
        folio_metrics[f]['hub_suppression']
    ] for f in valid_folios])

    y = np.array([folio_ht_density[f] for f in valid_folios])

    print(f"   X shape: {X.shape}")
    print(f"   y shape: {y.shape}")
    print(f"   HT density range: {y.min():.3f} - {y.max():.3f}")

    # Step 4: Descriptive statistics
    print("\n4. Descriptive statistics...")
    for i, name in enumerate(feature_names):
        vals = X[:, i]
        print(f"   {name}: mean={vals.mean():.3f}, std={vals.std():.3f}")

    print(f"   HT density: mean={y.mean():.3f}, std={y.std():.3f}")

    # Step 5: Correlation analysis
    print("\n5. Correlation with HT density...")
    correlations = {}
    for i, name in enumerate(feature_names):
        r, p = stats.pearsonr(X[:, i], y)
        correlations[name] = {'r': r, 'p': p}
        print(f"   {name}: r={r:.3f}, p={p:.4f}")

    # Step 6: Linear regression
    print("\n6. Running linear regression...")
    regression_results = run_regression(X, y, feature_names)

    print(f"\n   R-squared: {regression_results['r2']:.4f}")
    print(f"   Intercept: {regression_results['intercept']:.4f}")
    print(f"   Coefficients:")
    for name, coef in regression_results['coefficients'].items():
        p_val = regression_results['p_values'][name]
        sig = "*" if p_val < 0.05 else ""
        print(f"      {name}: {coef:+.4f} (p={p_val:.4f}){sig}")

    # Step 7: Ablation analysis
    print("\n7. Running ablation analysis...")
    ablation_results = run_ablation(X, y, feature_names)

    print(f"\n   Full model R²: {ablation_results['full_r2']:.4f}")
    print(f"   Feature importance (R² drop when removed):")

    sorted_importance = sorted(
        ablation_results['ablations'].items(),
        key=lambda x: x[1]['r2_drop'],
        reverse=True
    )

    for name, vals in sorted_importance:
        print(f"      {name}: R² drops by {vals['r2_drop']:.4f} ({100*vals['importance']:.1f}%)")

    # Step 8: Interpretation
    print("\n" + "=" * 70)
    print("INTERPRETATION")
    print("=" * 70)

    r2 = regression_results['r2']

    if r2 >= 0.50:
        verdict = "STRONGLY_EXPLAINED"
        interpretation = "HT is strongly tied to discrimination pressure from A structure"
    elif r2 >= 0.25:
        verdict = "PARTIALLY_EXPLAINED"
        interpretation = "HT is partially predictable from A metrics - coarse vigilance signal"
    elif r2 >= 0.10:
        verdict = "WEAKLY_EXPLAINED"
        interpretation = "HT has weak but non-trivial connection to A structure"
    else:
        verdict = "NOT_EXPLAINED"
        interpretation = "HT signals something else entirely - major discovery potential"

    print(f"\n   >>> R² = {r2:.4f}: {verdict} <<<")
    print(f"   {interpretation}")

    # Identify dominant predictor
    if ablation_results['ablations']:
        dominant = max(ablation_results['ablations'].items(), key=lambda x: x[1]['r2_drop'])
        print(f"\n   Dominant predictor: {dominant[0]} (explains {100*dominant[1]['importance']:.1f}% of variance)")

    # Save results
    output = {
        'probe_id': 'HT_VARIANCE_DECOMPOSITION',
        'question': 'Can incompatibility degree explain HT density?',
        'configuration': {
            'scope': 'AZC folios only',
            'n_folios': len(valid_folios),
            'features': feature_names
        },
        'descriptive': {
            'ht_density_mean': float(y.mean()),
            'ht_density_std': float(y.std()),
            'feature_means': {name: float(X[:, i].mean()) for i, name in enumerate(feature_names)},
            'feature_stds': {name: float(X[:, i].std()) for i, name in enumerate(feature_names)}
        },
        'correlations': {name: {'r': float(v['r']), 'p': float(v['p'])} for name, v in correlations.items()},
        'regression': {
            'r2': float(regression_results['r2']),
            'mse': float(regression_results['mse']),
            'intercept': float(regression_results['intercept']),
            'coefficients': {k: float(v) for k, v in regression_results['coefficients'].items()},
            'p_values': {k: float(v) for k, v in regression_results['p_values'].items()}
        },
        'ablation': {
            'full_r2': float(ablation_results['full_r2']),
            'feature_importance': {
                name: {
                    'ablated_r2': float(vals['ablated_r2']),
                    'r2_drop': float(vals['r2_drop']),
                    'importance': float(vals['importance'])
                } for name, vals in ablation_results['ablations'].items()
            }
        },
        'verdict': {
            'status': verdict,
            'r2': float(r2),
            'interpretation': interpretation,
            'dominant_predictor': dominant[0] if ablation_results['ablations'] else None
        }
    }

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2)

    print(f"\n\nResults saved to: {OUTPUT_FILE}")

    return output


if __name__ == "__main__":
    main()
