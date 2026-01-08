"""
REGIME × ROLE DIFFERENTIATION PROBE

Question: Do aggressive/conservative programs use different role mixtures?

We classify programs by intensity and check if role composition differs.

Intensity proxies from control_signatures:
- link_density: HIGH = conservative (more waiting)
- hazard_density: HIGH = aggressive (more risk)
- kernel_contact_ratio: HIGH = active intervention
"""

import csv
import json
from collections import defaultdict, Counter
from pathlib import Path
import numpy as np
from scipy.stats import spearmanr, kruskal

BASE = Path(r"C:\git\voynich")
TRANSCRIPTION = BASE / "data" / "transcriptions" / "interlinear_full_words.txt"
SIGNATURES = BASE / "results" / "control_signatures.json"
GRAMMAR = BASE / "results" / "canonical_grammar.json"

def load_signatures():
    """Load control signatures for each folio."""
    with open(SIGNATURES, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data.get('signatures', {})

def load_grammar_roles():
    """Load token -> role mapping."""
    with open(GRAMMAR, 'r', encoding='utf-8') as f:
        data = json.load(f)

    token_to_role = {}
    terminals = data.get('terminals', {}).get('list', [])
    for term in terminals:
        token_to_role[term['symbol']] = term['role']

    return token_to_role

def load_b_tokens_by_folio():
    """Load B tokens grouped by folio."""
    tokens_by_folio = defaultdict(list)

    with open(TRANSCRIPTION, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t', quotechar='"')
        for row in reader:
            if row.get('transcriber') != 'H':
                continue
            if row.get('language') != 'B':
                continue
            token = row.get('word', '')
            if not token or '*' in token:
                continue

            folio = row['folio']
            tokens_by_folio[folio].append(token)

    return tokens_by_folio

def classify_intensity(signatures):
    """Classify folios into intensity groups."""
    # Use multiple metrics
    intensities = {}

    link_densities = [s['link_density'] for s in signatures.values()]
    hazard_densities = [s['hazard_density'] for s in signatures.values()]
    kernel_ratios = [s['kernel_contact_ratio'] for s in signatures.values()]

    link_median = np.median(link_densities)
    hazard_median = np.median(hazard_densities)
    kernel_median = np.median(kernel_ratios)

    for folio, sig in signatures.items():
        # Conservative: high LINK, low hazard, low kernel
        # Aggressive: low LINK, high hazard, high kernel

        score = 0
        if sig['link_density'] < link_median:
            score += 1  # Less waiting = more aggressive
        if sig['hazard_density'] > hazard_median:
            score += 1  # More hazard = more aggressive
        if sig['kernel_contact_ratio'] > kernel_median:
            score += 1  # More kernel = more aggressive

        if score >= 2:
            intensities[folio] = 'AGGRESSIVE'
        elif score <= 0:
            intensities[folio] = 'CONSERVATIVE'
        else:
            intensities[folio] = 'MODERATE'

    return intensities

def compute_role_distributions(tokens_by_folio, token_to_role):
    """Compute role distribution for each folio."""
    role_dists = {}

    for folio, tokens in tokens_by_folio.items():
        role_counts = Counter()
        for token in tokens:
            role = token_to_role.get(token)
            if role:
                role_counts[role] += 1

        total = sum(role_counts.values())
        if total > 0:
            role_dists[folio] = {
                'counts': dict(role_counts),
                'fractions': {r: c/total for r, c in role_counts.items()},
                'total_classified': total,
                'total_tokens': len(tokens)
            }

    return role_dists

def analyze_regime_role_correlation():
    """Main analysis."""
    print("="*70)
    print("REGIME × ROLE DIFFERENTIATION ANALYSIS")
    print("="*70)

    signatures = load_signatures()
    token_to_role = load_grammar_roles()
    tokens_by_folio = load_b_tokens_by_folio()

    print(f"\nLoaded {len(signatures)} signatures, {len(token_to_role)} role mappings")
    print(f"Roles: {set(token_to_role.values())}")

    # Classify intensity
    intensities = classify_intensity(signatures)

    intensity_counts = Counter(intensities.values())
    print(f"\nIntensity classification:")
    for intensity, count in sorted(intensity_counts.items()):
        print(f"  {intensity}: {count} folios")

    # Compute role distributions
    role_dists = compute_role_distributions(tokens_by_folio, token_to_role)

    # Analyze by intensity group
    print("\n" + "-"*70)
    print("ROLE COMPOSITION BY INTENSITY GROUP")
    print("-"*70)

    roles = ['ENERGY_OPERATOR', 'CORE_CONTROL', 'FREQUENT_OPERATOR',
             'FLOW_OPERATOR', 'AUXILIARY', 'HIGH_IMPACT']

    group_role_fractions = defaultdict(lambda: defaultdict(list))

    for folio in intensities:
        if folio in role_dists:
            intensity = intensities[folio]
            for role in roles:
                frac = role_dists[folio]['fractions'].get(role, 0)
                group_role_fractions[intensity][role].append(frac)

    print(f"\n{'Role':<20}", end="")
    for intensity in ['CONSERVATIVE', 'MODERATE', 'AGGRESSIVE']:
        print(f"{intensity:>15}", end="")
    print()
    print("-" * 65)

    for role in roles:
        print(f"{role:<20}", end="")
        for intensity in ['CONSERVATIVE', 'MODERATE', 'AGGRESSIVE']:
            fracs = group_role_fractions[intensity][role]
            if fracs:
                mean = np.mean(fracs)
                print(f"{mean:>14.1%}", end="")
            else:
                print(f"{'N/A':>15}", end="")
        print()

    # Statistical tests
    print("\n" + "-"*70)
    print("STATISTICAL TESTS (Kruskal-Wallis)")
    print("-"*70)

    for role in roles:
        groups = []
        for intensity in ['CONSERVATIVE', 'MODERATE', 'AGGRESSIVE']:
            fracs = group_role_fractions[intensity][role]
            if len(fracs) >= 3:
                groups.append(fracs)

        if len(groups) >= 2:
            stat, p = kruskal(*groups)
            sig = "***" if p < 0.001 else ("**" if p < 0.01 else ("*" if p < 0.05 else ""))
            print(f"{role:<20}: H={stat:>7.2f}, p={p:.4f} {sig}")

    # Correlation with continuous metrics
    print("\n" + "-"*70)
    print("ROLE FRACTION × INTENSITY METRIC CORRELATIONS")
    print("-"*70)

    metrics = ['link_density', 'hazard_density', 'kernel_contact_ratio', 'intervention_frequency']

    print(f"\n{'Role':<20}", end="")
    for metric in metrics:
        short = metric[:12]
        print(f"{short:>14}", end="")
    print()
    print("-" * 80)

    for role in roles:
        print(f"{role:<20}", end="")
        for metric in metrics:
            role_fracs = []
            metric_vals = []

            for folio in signatures:
                if folio in role_dists:
                    role_fracs.append(role_dists[folio]['fractions'].get(role, 0))
                    metric_vals.append(signatures[folio][metric])

            if len(role_fracs) >= 10:
                rho, p = spearmanr(role_fracs, metric_vals)
                sig = "*" if p < 0.05 else ""
                print(f"{rho:>+13.3f}{sig}", end="")
            else:
                print(f"{'N/A':>14}", end="")
        print()

    # Deep dive on key findings
    print("\n" + "-"*70)
    print("KEY PATTERN ANALYSIS")
    print("-"*70)

    # Which roles differentiate most?
    print("\nRoles with strongest intensity differentiation:")

    for role in roles:
        cons = group_role_fractions['CONSERVATIVE'][role]
        agg = group_role_fractions['AGGRESSIVE'][role]

        if cons and agg:
            cons_mean = np.mean(cons)
            agg_mean = np.mean(agg)
            diff = agg_mean - cons_mean
            ratio = agg_mean / cons_mean if cons_mean > 0 else float('inf')

            if abs(diff) > 0.02 or ratio > 1.2 or ratio < 0.8:
                print(f"  {role}:")
                print(f"    Conservative: {cons_mean:.1%}")
                print(f"    Aggressive: {agg_mean:.1%}")
                print(f"    Difference: {diff:+.1%} (ratio: {ratio:.2f}x)")

def main():
    analyze_regime_role_correlation()

    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print("""
If roles differentiate by intensity:
  -> Different operational modes use different instruction mixes
  -> Supports "families = different processes" theory

If roles are uniform:
  -> Same grammar applied at different intensities
  -> Intensity is parametric, not categorical
""")

if __name__ == '__main__':
    main()
