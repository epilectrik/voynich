#!/usr/bin/env python3
"""
Efficiency Regime Test 1: Residual Brittleness Analysis (PRIMARY)

Question: Does A/C vocabulary explain brittleness *beyond* what AZC escape already predicts?

This tests whether family membership has explanatory power independent of the known
AZC escape → B escape transfer effect (F-AZC-016).

Method:
1. Build baseline model: Predict B program brittleness from AZC escape profile alone
2. Compute residual brittleness: observed - predicted
3. Test whether A/C vocabulary share explains residual variance
4. Control for PREFIX composition and section membership

Prediction (efficiency-regime):
- A/C vocabulary should explain additional brittleness beyond known AZC escape
- Effect should survive when PREFIX composition is held constant

Falsification:
- No residual effect → AZC already explains everything → efficiency-regime collapses
- Residual explained by PREFIX alone → morphology, not regime
"""

import csv
import json
from collections import defaultdict, Counter
from pathlib import Path
from typing import Dict, List, Set, Tuple
import statistics

# Paths
BASE_PATH = Path(__file__).parent.parent.parent
DATA_FILE = BASE_PATH / "data" / "transcriptions" / "interlinear_full_words.txt"
PROFILES_FILE = BASE_PATH / "results" / "unified_folio_profiles.json"
OUTPUT_FILE = BASE_PATH / "results" / "efficiency_regime_residual_brittleness.json"

# AZC Family definitions (from C430)
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

# Known prefixes for morphological control
KNOWN_PREFIXES = ['qo', 'ol', 'or', 'al', 'ar', 'ok', 'ot', 'ch', 'sh', 'ct', 'd', 's', 'y', 'o', 'a']
KNOWN_SUFFIXES = ['y', 'dy', 'n', 'in', 'iin', 'aiin', 'ain', 'l', 'm', 'r', 's', 'g', 'am', 'an']


def decompose_token(token: str) -> Dict[str, str]:
    """Decompose token into PREFIX, MIDDLE, SUFFIX."""
    if not token or len(token) < 2:
        return {'prefix': '', 'middle': token, 'suffix': ''}

    prefix = ''
    suffix = ''

    for p in sorted(KNOWN_PREFIXES, key=len, reverse=True):
        if token.startswith(p):
            prefix = p
            token = token[len(p):]
            break

    for s in sorted(KNOWN_SUFFIXES, key=len, reverse=True):
        if token.endswith(s) and len(token) > len(s):
            suffix = s
            token = token[:-len(s)]
            break

    return {'prefix': prefix, 'middle': token, 'suffix': suffix}


def build_token_azc_mapping() -> Dict[str, Dict]:
    """Build token -> AZC folio mapping with family information."""
    token_azc = defaultdict(lambda: {'folios': set(), 'ac_count': 0, 'zodiac_count': 0, 'total': 0})

    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            # CRITICAL: Filter to H-only transcriber track
            transcriber = row.get('transcriber', '').strip().strip('"')
            if transcriber != 'H':
                continue

            word = row.get('word', '').strip()
            folio = row.get('folio', '').strip()
            section = row.get('section', '').strip()
            language = row.get('language', '').strip()

            if not word or word.startswith('[') or word.startswith('<') or '*' in word:
                continue

            # Check if AZC folio
            is_azc = section in {'Z', 'A', 'C'} or language not in ('A', 'B')
            if not is_azc or folio not in ALL_AZC_FOLIOS:
                continue

            token_azc[word]['folios'].add(folio)
            token_azc[word]['total'] += 1

            if folio in AC_FOLIOS:
                token_azc[word]['ac_count'] += 1
            elif folio in ZODIAC_FOLIOS:
                token_azc[word]['zodiac_count'] += 1

    # Convert sets to lists for JSON serialization later
    for token in token_azc:
        token_azc[token]['folios'] = list(token_azc[token]['folios'])

    return dict(token_azc)


def load_b_folio_tokens(target_folio: str) -> List[Dict]:
    """Load all tokens from a B folio."""
    tokens = []

    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            # CRITICAL: Filter to H-only transcriber track
            transcriber = row.get('transcriber', '').strip().strip('"')
            if transcriber != 'H':
                continue

            folio = row.get('folio', '').strip()
            if folio != target_folio:
                continue

            word = row.get('word', '').strip()
            language = row.get('language', '').strip()

            if not word or word.startswith('[') or word.startswith('<') or '*' in word:
                continue

            if language != 'B':
                continue

            decomp = decompose_token(word)
            tokens.append({
                'token': word,
                'prefix': decomp['prefix'],
                'middle': decomp['middle'],
                'suffix': decomp['suffix']
            })

    return tokens


def load_b_folio_profiles() -> Dict:
    """Load B folio profiles with brittleness metrics."""
    with open(PROFILES_FILE, 'r') as f:
        data = json.load(f)

    b_profiles = {}
    for folio, profile in data['profiles'].items():
        if profile.get('system') == 'B' and profile.get('b_metrics'):
            b_profiles[folio] = {
                'cei_total': profile['b_metrics'].get('cei_total', 0),
                'hazard_density': profile['b_metrics'].get('hazard_density', 0),
                'escape_density': profile['b_metrics'].get('escape_density', 0),
                'execution_tension': profile.get('burden_indices', {}).get('execution_tension', 0),
                'intervention_frequency': profile['b_metrics'].get('intervention_frequency', 0)
            }

    return b_profiles


def compute_b_folio_azc_profile(folio: str, tokens: List[Dict], token_azc: Dict) -> Dict:
    """
    Compute AZC-related features for a B folio.

    Returns:
        - ac_fraction: fraction of vocabulary from A/C family
        - zodiac_fraction: fraction of vocabulary from Zodiac family
        - mean_azc_escape: average escape rate proxy (based on family membership)
        - prefix_composition: distribution of prefixes
    """
    ac_tokens = 0
    zodiac_tokens = 0
    shared_tokens = 0
    no_azc_tokens = 0

    prefix_counts = Counter()

    for t in tokens:
        token = t['token']
        azc_info = token_azc.get(token)

        if t['prefix']:
            prefix_counts[t['prefix']] += 1

        if azc_info:
            ac = azc_info['ac_count']
            zodiac = azc_info['zodiac_count']
            total = azc_info['total']

            if ac > 0 and zodiac > 0:
                shared_tokens += 1
            elif ac > 0:
                ac_tokens += 1
            elif zodiac > 0:
                zodiac_tokens += 1
        else:
            no_azc_tokens += 1

    total_with_azc = ac_tokens + zodiac_tokens + shared_tokens
    total_all = len(tokens)

    # Compute fractions
    if total_with_azc > 0:
        ac_fraction = ac_tokens / total_with_azc
        zodiac_fraction = zodiac_tokens / total_with_azc
    else:
        ac_fraction = 0
        zodiac_fraction = 0

    # AZC coverage
    azc_coverage = total_with_azc / total_all if total_all > 0 else 0

    # Compute prefix composition (for control)
    # qo-/ol- are A/C-enriched (C471), ot- is Zodiac-enriched
    ac_prefix_count = prefix_counts.get('qo', 0) + prefix_counts.get('ol', 0)
    zodiac_prefix_count = prefix_counts.get('ot', 0)
    total_prefix = sum(prefix_counts.values())

    if total_prefix > 0:
        ac_prefix_fraction = ac_prefix_count / total_prefix
        zodiac_prefix_fraction = zodiac_prefix_count / total_prefix
    else:
        ac_prefix_fraction = 0
        zodiac_prefix_fraction = 0

    return {
        'n_tokens': total_all,
        'n_with_azc': total_with_azc,
        'azc_coverage': round(azc_coverage, 3),
        'ac_exclusive_count': ac_tokens,
        'zodiac_exclusive_count': zodiac_tokens,
        'shared_count': shared_tokens,
        'ac_fraction': round(ac_fraction, 3),
        'zodiac_fraction': round(zodiac_fraction, 3),
        'ac_prefix_fraction': round(ac_prefix_fraction, 3),
        'zodiac_prefix_fraction': round(zodiac_prefix_fraction, 3)
    }


def compute_residual_analysis(folio_data: List[Dict]) -> Dict:
    """
    Perform residual analysis.

    1. Model brittleness from zodiac_fraction (proxy for AZC escape)
    2. Compute residuals
    3. Test if ac_fraction explains residuals
    """
    # Extract arrays
    folios = [d['folio'] for d in folio_data]
    brittleness = [d['brittleness'] for d in folio_data]
    zodiac_frac = [d['azc_profile']['zodiac_fraction'] for d in folio_data]
    ac_frac = [d['azc_profile']['ac_fraction'] for d in folio_data]
    ac_prefix_frac = [d['azc_profile']['ac_prefix_fraction'] for d in folio_data]

    n = len(folio_data)

    if n < 5:
        return {'status': 'INSUFFICIENT_DATA', 'n': n}

    # Simple linear regression: brittleness ~ zodiac_fraction
    # (We use zodiac_fraction as proxy for "forgiving" - more Zodiac = lower escape)
    # Since Zodiac = forgiving, we expect NEGATIVE relationship with brittleness

    # Compute correlation: brittleness vs zodiac_fraction
    mean_brit = statistics.mean(brittleness)
    mean_zod = statistics.mean(zodiac_frac)

    cov_brit_zod = sum((b - mean_brit) * (z - mean_zod) for b, z in zip(brittleness, zodiac_frac)) / n
    var_zod = sum((z - mean_zod) ** 2 for z in zodiac_frac) / n
    var_brit = sum((b - mean_brit) ** 2 for b in brittleness) / n

    if var_zod > 0 and var_brit > 0:
        corr_brit_zod = cov_brit_zod / (var_zod ** 0.5 * var_brit ** 0.5)
    else:
        corr_brit_zod = 0

    # Linear model: brittleness = beta * zodiac_fraction + alpha
    if var_zod > 0:
        beta = cov_brit_zod / var_zod
        alpha = mean_brit - beta * mean_zod
    else:
        beta = 0
        alpha = mean_brit

    # Predict brittleness and compute residuals
    predicted = [alpha + beta * z for z in zodiac_frac]
    residuals = [b - p for b, p in zip(brittleness, predicted)]

    # Now test: do residuals correlate with ac_fraction?
    mean_resid = statistics.mean(residuals)
    mean_ac = statistics.mean(ac_frac)

    cov_resid_ac = sum((r - mean_resid) * (a - mean_ac) for r, a in zip(residuals, ac_frac)) / n
    var_resid = sum((r - mean_resid) ** 2 for r in residuals) / n
    var_ac = sum((a - mean_ac) ** 2 for a in ac_frac) / n

    if var_resid > 0 and var_ac > 0:
        corr_resid_ac = cov_resid_ac / (var_resid ** 0.5 * var_ac ** 0.5)
    else:
        corr_resid_ac = 0

    # Also test residuals vs ac_prefix_fraction (control)
    mean_ac_pfx = statistics.mean(ac_prefix_frac)
    cov_resid_acpfx = sum((r - mean_resid) * (p - mean_ac_pfx) for r, p in zip(residuals, ac_prefix_frac)) / n
    var_ac_pfx = sum((p - mean_ac_pfx) ** 2 for p in ac_prefix_frac) / n

    if var_resid > 0 and var_ac_pfx > 0:
        corr_resid_acpfx = cov_resid_acpfx / (var_resid ** 0.5 * var_ac_pfx ** 0.5)
    else:
        corr_resid_acpfx = 0

    # R-squared for baseline model
    ss_total = sum((b - mean_brit) ** 2 for b in brittleness)
    ss_resid = sum(r ** 2 for r in residuals)
    r_squared = 1 - (ss_resid / ss_total) if ss_total > 0 else 0

    # Determine verdict
    if abs(corr_resid_ac) > 0.3:
        if corr_resid_ac > 0:
            # A/C vocabulary predicts HIGHER residual brittleness
            verdict = 'AC_EXPLAINS_RESIDUAL_BRITTLENESS'
            interpretation = 'A/C vocabulary adds brittleness beyond AZC escape prediction'
        else:
            # A/C vocabulary predicts LOWER residual brittleness (unexpected)
            verdict = 'AC_EXPLAINS_RESIDUAL_FORGIVENESS'
            interpretation = 'A/C vocabulary reduces brittleness beyond AZC (opposite of prediction)'
    elif abs(corr_resid_acpfx) > abs(corr_resid_ac) and abs(corr_resid_acpfx) > 0.3:
        verdict = 'PREFIX_EXPLAINS_RESIDUAL'
        interpretation = 'Residual explained by PREFIX composition, not family membership'
    else:
        verdict = 'NO_RESIDUAL_EFFECT'
        interpretation = 'A/C vocabulary share does not explain residual brittleness'

    return {
        'status': 'COMPLETE',
        'n_folios': n,
        'baseline_model': {
            'predictor': 'zodiac_fraction',
            'target': 'brittleness',
            'correlation': round(corr_brit_zod, 3),
            'r_squared': round(r_squared, 3),
            'beta': round(beta, 4),
            'alpha': round(alpha, 4)
        },
        'residual_analysis': {
            'correlation_residual_vs_ac': round(corr_resid_ac, 3),
            'correlation_residual_vs_ac_prefix': round(corr_resid_acpfx, 3),
            'verdict': verdict,
            'interpretation': interpretation
        },
        'folio_details': [
            {
                'folio': folios[i],
                'brittleness': round(brittleness[i], 3),
                'zodiac_fraction': round(zodiac_frac[i], 3),
                'ac_fraction': round(ac_frac[i], 3),
                'predicted': round(predicted[i], 3),
                'residual': round(residuals[i], 3)
            }
            for i in range(n)
        ]
    }


def main():
    print("=" * 70)
    print("EFFICIENCY REGIME TEST 1: RESIDUAL BRITTLENESS ANALYSIS")
    print("=" * 70)
    print("\nPriority: 2 (Run after Test 2 passes)")
    print()

    # Load token -> AZC mapping
    print("1. Building token -> AZC mapping...")
    token_azc = build_token_azc_mapping()
    print(f"   Mapped {len(token_azc)} token types to AZC folios")

    # Load B folio profiles
    print("\n2. Loading B folio profiles...")
    b_profiles = load_b_folio_profiles()
    print(f"   Found {len(b_profiles)} B folios with metrics")

    # Compute AZC profile for each B folio
    print("\n3. Computing AZC vocabulary profiles for each B folio...")
    folio_data = []

    for folio in sorted(b_profiles.keys()):
        # Load tokens
        tokens = load_b_folio_tokens(folio)
        if len(tokens) < 20:
            continue

        # Compute AZC profile
        azc_profile = compute_b_folio_azc_profile(folio, tokens, token_azc)

        if azc_profile['n_with_azc'] < 5:
            continue

        # Get brittleness metric (using execution_tension)
        brittleness = b_profiles[folio]['execution_tension']

        folio_data.append({
            'folio': folio,
            'brittleness': brittleness,
            'b_metrics': b_profiles[folio],
            'azc_profile': azc_profile
        })

    print(f"   Processed {len(folio_data)} folios with sufficient data")

    # Residual analysis
    print("\n4. Performing residual analysis...")
    residual_results = compute_residual_analysis(folio_data)

    # Print results
    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)

    if residual_results['status'] == 'COMPLETE':
        bm = residual_results['baseline_model']
        print("\n--- Baseline Model (Brittleness ~ Zodiac Fraction) ---")
        print(f"   Correlation: {bm['correlation']}")
        print(f"   R-squared: {bm['r_squared']}")
        print(f"   Beta: {bm['beta']} (expected negative if Zodiac = forgiving)")

        ra = residual_results['residual_analysis']
        print("\n--- Residual Analysis ---")
        print(f"   Residual vs A/C Fraction: r = {ra['correlation_residual_vs_ac']}")
        print(f"   Residual vs A/C PREFIX Fraction: r = {ra['correlation_residual_vs_ac_prefix']}")
        print(f"\n   Verdict: {ra['verdict']}")
        print(f"   Interpretation: {ra['interpretation']}")

        # Show top positive and negative residuals
        details = sorted(residual_results['folio_details'], key=lambda x: x['residual'])
        print("\n--- Extreme Residuals ---")
        print("Most UNDER-predicted brittleness (higher than expected):")
        for d in details[-5:]:
            print(f"   {d['folio']}: residual={d['residual']:+.3f}, ac_frac={d['ac_fraction']:.3f}")

        print("\nMost OVER-predicted brittleness (lower than expected):")
        for d in details[:5]:
            print(f"   {d['folio']}: residual={d['residual']:+.3f}, ac_frac={d['ac_fraction']:.3f}")
    else:
        print(f"Status: {residual_results['status']}")

    # Determine overall test verdict
    print("\n" + "=" * 70)
    print("TEST VERDICT")
    print("=" * 70)

    if residual_results['status'] != 'COMPLETE':
        verdict = 'INCONCLUSIVE'
        interpretation = 'Insufficient data'
    elif residual_results['residual_analysis']['verdict'] == 'AC_EXPLAINS_RESIDUAL_BRITTLENESS':
        verdict = 'TEST_1_PASSED'
        interpretation = 'A/C vocabulary explains additional brittleness beyond AZC escape'
    elif residual_results['residual_analysis']['verdict'] == 'PREFIX_EXPLAINS_RESIDUAL':
        verdict = 'TEST_1_FAILED_PREFIX'
        interpretation = 'Effect is morphological, not regime-based'
    elif residual_results['residual_analysis']['verdict'] == 'NO_RESIDUAL_EFFECT':
        verdict = 'TEST_1_FAILED'
        interpretation = 'AZC escape already explains all brittleness variance'
    else:
        verdict = 'ANOMALY'
        interpretation = 'Unexpected pattern - A/C reduces brittleness'

    print(f"\n>>> {verdict} <<<")
    print(f"    {interpretation}")

    # Save results
    results = {
        'test_id': 'EFFICIENCY_REGIME_TEST_1',
        'question': 'Does A/C vocabulary explain brittleness beyond what AZC escape already predicts?',
        'n_folios': len(folio_data),
        'residual_analysis': residual_results,
        'verdict': {
            'overall': verdict,
            'interpretation': interpretation
        }
    }

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)

    print(f"\n\nResults saved to: {OUTPUT_FILE}")

    return results


if __name__ == "__main__":
    main()
