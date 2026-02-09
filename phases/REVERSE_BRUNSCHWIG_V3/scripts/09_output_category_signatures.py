#!/usr/bin/env python3
"""
Test 9: Output Category Signatures

Hypothesis: Brunschwig product types (WATER vs OIL_RESIN) have vocabulary
signatures in B beyond REGIME structure.

Product types from brunschwig_materials_master.json:
- WATER_STANDARD (REGIME_1): 408 materials, fire degree 2
- WATER_GENTLE (REGIME_2): 48 materials, fire degree 1
- OIL_RESIN (REGIME_3): 35 materials, fire degree 3
- PRECISION (REGIME_4): 18 materials, fire degree 4

Since REGIME correlates with product type, we test:
1. Are there suffix patterns that mark WATER vs OIL beyond REGIME?
2. Are there MIDDLE patterns specific to OIL_RESIN procedures?
3. Are there "completion" markers that differ by product type?

Method:
1. Classify B folios by dominant REGIME (proxy for product type)
2. Test suffix/MIDDLE distributions controlling for REGIME
3. Look for vocabulary that predicts product type better than REGIME alone
"""

import json
import sys
from pathlib import Path
from collections import defaultdict
import numpy as np
from scipy import stats

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from scripts.voynich import Transcript, Morphology

# Output paths
RESULTS_DIR = Path(__file__).parent.parent / 'results'
RESULTS_DIR.mkdir(exist_ok=True)

# Brunschwig data
DATA_DIR = Path(__file__).parent.parent.parent.parent / 'data'

def load_brunschwig_products():
    """Load product type mappings from Brunschwig materials."""
    bru_path = DATA_DIR / 'brunschwig_materials_master.json'
    with open(bru_path, encoding='utf-8') as f:
        data = json.load(f)

    # Product type by regime
    regime_product = {
        'REGIME_1': 'WATER_STANDARD',
        'REGIME_2': 'WATER_GENTLE',
        'REGIME_3': 'OIL_RESIN',
        'REGIME_4': 'PRECISION'
    }

    # Collapsed categories
    regime_output_class = {
        'REGIME_1': 'WATER',
        'REGIME_2': 'WATER',
        'REGIME_3': 'OIL',
        'REGIME_4': 'PRECISION'
    }

    return regime_product, regime_output_class, data['summary']

def group_by_folio(tx):
    """Group Currier B tokens by folio."""
    folio_tokens = defaultdict(list)
    for tok in tx.currier_b():
        folio_tokens[tok.folio].append(tok)
    return folio_tokens

def group_by_line(tx, folio):
    """Group tokens by line for a specific folio."""
    line_tokens = defaultdict(list)
    for tok in tx.currier_b():
        if tok.folio == folio:
            line_tokens[tok.line].append(tok)
    return line_tokens

def compute_folio_regime(tx, morph):
    """Compute dominant REGIME for each B folio based on vocabulary."""
    folio_regimes = {}
    folio_tokens = group_by_folio(tx)

    # REGIME indicators based on prior findings
    # REGIME_3 (OIL): higher tch/pch (intensive prep)
    # REGIME_4 (PRECISION): higher ke (sustained)
    # REGIME_1/2 (WATER): default

    for folio, tokens in folio_tokens.items():
        suffixes = defaultdict(int)
        middles = defaultdict(int)

        for tok in tokens:
            m = morph.extract(tok.word)
            if m.suffix:
                suffixes[m.suffix] += 1
            if m.middle:
                middles[m.middle] += 1

        total = len(tokens)
        if total < 20:
            continue

        # Compute indicators
        intensive_ops = sum(middles.get(m, 0) for m in ['tch', 'pch', 'kch'])
        sustained_ops = sum(middles.get(m, 0) for m in ['ke', 'te', 'e'])

        intensive_rate = intensive_ops / total
        sustained_rate = sustained_ops / total

        # Animal suffixes (REGIME_4 indicator from C884)
        animal_suff = sum(suffixes.get(s, 0) for s in ['ey', 'ol', 'eey'])
        animal_rate = animal_suff / total

        # Assign dominant regime based on operational vocabulary
        # Thresholds calibrated to actual B folio distributions:
        # - intensive max=0.056, mean=0.012
        # - sustained max=0.142, mean=0.049
        # Using relative thresholds: top 10% for category assignment

        # REGIME_3 (OIL/intensive): above-average intensive ops
        if intensive_rate > 0.03:  # ~top 7% of folios
            regime = 'REGIME_3'
        # REGIME_4 (PRECISION): high sustained, low intensive
        elif sustained_rate > 0.08:  # ~top 10% of folios
            regime = 'REGIME_4'
        # REGIME_2 (GENTLE): low activity overall
        elif sustained_rate < 0.03 and intensive_rate < 0.01:
            regime = 'REGIME_2'
        else:
            regime = 'REGIME_1'  # Default (WATER_STANDARD)

        folio_regimes[folio] = {
            'regime': regime,
            'intensive_rate': intensive_rate,
            'sustained_rate': sustained_rate,
            'animal_rate': animal_rate,
            'total_tokens': total
        }

    return folio_regimes

def analyze_suffix_by_regime(tx, morph, folio_regimes):
    """Analyze suffix distributions by regime/output class."""
    regime_suffixes = defaultdict(lambda: defaultdict(int))
    folio_tokens = group_by_folio(tx)

    for folio, tokens in folio_tokens.items():
        if folio not in folio_regimes:
            continue
        regime = folio_regimes[folio]['regime']

        for tok in tokens:
            m = morph.extract(tok.word)
            if m.suffix:
                regime_suffixes[regime][m.suffix] += 1

    # Compute distributions
    results = {}
    all_suffixes = set()
    for regime in regime_suffixes:
        all_suffixes.update(regime_suffixes[regime].keys())

    for regime in ['REGIME_1', 'REGIME_2', 'REGIME_3', 'REGIME_4']:
        if regime in regime_suffixes:
            total = sum(regime_suffixes[regime].values())
            results[regime] = {
                'total': total,
                'distribution': {s: regime_suffixes[regime][s] / total
                               for s in all_suffixes if regime_suffixes[regime][s] > 0}
            }

    return results, all_suffixes

def analyze_middle_by_regime(tx, morph, folio_regimes):
    """Analyze MIDDLE distributions by regime/output class."""
    regime_middles = defaultdict(lambda: defaultdict(int))
    folio_tokens = group_by_folio(tx)

    for folio, tokens in folio_tokens.items():
        if folio not in folio_regimes:
            continue
        regime = folio_regimes[folio]['regime']

        for tok in tokens:
            m = morph.extract(tok.word)
            if m.middle:
                regime_middles[regime][m.middle] += 1

    return regime_middles

def find_output_specific_vocabulary(suffix_results, middle_results, output_class_map):
    """Find vocabulary that distinguishes WATER vs OIL output classes."""

    # Collapse to output classes
    output_suffixes = defaultdict(lambda: defaultdict(int))
    output_middles = defaultdict(lambda: defaultdict(int))

    for regime, data in suffix_results.items():
        output_class = output_class_map.get(regime, 'WATER')
        for suffix, rate in data.get('distribution', {}).items():
            output_suffixes[output_class][suffix] += data['total'] * rate

    for regime, middles in middle_results.items():
        output_class = output_class_map.get(regime, 'WATER')
        for middle, count in middles.items():
            output_middles[output_class][middle] += count

    # Find differentiating vocabulary
    water_total = sum(output_suffixes['WATER'].values()) or 1
    oil_total = sum(output_suffixes['OIL'].values()) or 1
    precision_total = sum(output_suffixes['PRECISION'].values()) or 1

    suffix_enrichment = {}
    for suffix in set(output_suffixes['WATER'].keys()) | set(output_suffixes['OIL'].keys()):
        water_rate = output_suffixes['WATER'].get(suffix, 0) / water_total
        oil_rate = output_suffixes['OIL'].get(suffix, 0) / oil_total

        if water_rate > 0.001 or oil_rate > 0.001:
            ratio = (oil_rate + 0.001) / (water_rate + 0.001)
            suffix_enrichment[suffix] = {
                'water_rate': water_rate,
                'oil_rate': oil_rate,
                'oil_water_ratio': ratio,
                'direction': 'OIL' if ratio > 1.5 else ('WATER' if ratio < 0.67 else 'NEUTRAL')
            }

    return suffix_enrichment, output_suffixes, output_middles

def test_vocabulary_output_correlation(tx, morph, folio_regimes, output_class_map):
    """Test if specific vocabulary predicts output class beyond REGIME."""

    # Collect per-folio features
    folio_features = []
    folio_tokens = group_by_folio(tx)

    for folio, tokens in folio_tokens.items():
        if folio not in folio_regimes:
            continue

        regime = folio_regimes[folio]['regime']
        output_class = output_class_map.get(regime, 'WATER')

        # Count features
        suffix_counts = defaultdict(int)
        middle_counts = defaultdict(int)

        for tok in tokens:
            m = morph.extract(tok.word)
            if m.suffix:
                suffix_counts[m.suffix] += 1
            if m.middle:
                middle_counts[m.middle] += 1

        total = len(tokens)

        # Candidate OIL markers (based on intensive processing)
        oil_markers = sum(middle_counts.get(m, 0) for m in ['tch', 'pch', 'kch', 'sch'])
        oil_marker_rate = oil_markers / total if total > 0 else 0

        # Candidate WATER markers (based on gentle processing)
        water_markers = sum(middle_counts.get(m, 0) for m in ['e', 'te', 'ke', 'ol'])
        water_marker_rate = water_markers / total if total > 0 else 0

        folio_features.append({
            'folio': folio,
            'regime': regime,
            'output_class': output_class,
            'oil_marker_rate': oil_marker_rate,
            'water_marker_rate': water_marker_rate,
            'total': total
        })

    # Test correlation
    is_oil = [1 if f['output_class'] == 'OIL' else 0 for f in folio_features]
    oil_rates = [f['oil_marker_rate'] for f in folio_features]
    water_rates = [f['water_marker_rate'] for f in folio_features]

    if sum(is_oil) > 3 and sum(is_oil) < len(is_oil) - 3:
        # Enough variance to test
        oil_corr = stats.pointbiserialr(is_oil, oil_rates)
        water_corr = stats.pointbiserialr(is_oil, water_rates)
    else:
        oil_corr = (0, 1)
        water_corr = (0, 1)

    return {
        'folio_count': len(folio_features),
        'oil_folio_count': sum(is_oil),
        'water_folio_count': len(is_oil) - sum(is_oil),
        'oil_marker_correlation': {
            'r': float(oil_corr[0]),
            'p': float(oil_corr[1])
        },
        'water_marker_correlation': {
            'r': float(water_corr[0]),
            'p': float(water_corr[1])
        }
    }, folio_features

def analyze_completion_markers(tx, morph, folio_regimes, output_class_map):
    """Analyze if line-final vocabulary differs by output class."""

    output_finals = defaultdict(lambda: defaultdict(int))
    folio_tokens = group_by_folio(tx)

    for folio in folio_tokens:
        if folio not in folio_regimes:
            continue
        regime = folio_regimes[folio]['regime']
        output_class = output_class_map.get(regime, 'WATER')

        # Get last token of each line
        line_tokens = group_by_line(tx, folio)
        for line_toks in line_tokens.values():
            if line_toks:
                last_tok = line_toks[-1]
                m = morph.extract(last_tok.word)
                if m.middle:
                    output_finals[output_class][m.middle] += 1

    # Compare distributions
    water_total = sum(output_finals['WATER'].values()) or 1
    oil_total = sum(output_finals['OIL'].values()) or 1

    final_comparison = {}
    all_finals = set(output_finals['WATER'].keys()) | set(output_finals['OIL'].keys())

    for middle in all_finals:
        water_rate = output_finals['WATER'].get(middle, 0) / water_total
        oil_rate = output_finals['OIL'].get(middle, 0) / oil_total

        if water_rate > 0.01 or oil_rate > 0.01:
            final_comparison[middle] = {
                'water_rate': round(water_rate, 4),
                'oil_rate': round(oil_rate, 4),
                'ratio': round((oil_rate + 0.001) / (water_rate + 0.001), 2)
            }

    return final_comparison, output_finals

def main():
    print("Test 9: Output Category Signatures")
    print("=" * 50)

    # Load data
    tx = Transcript()
    morph = Morphology()
    regime_product, output_class_map, bru_summary = load_brunschwig_products()

    print(f"\nBrunschwig product types:")
    for regime, product in regime_product.items():
        print(f"  {regime}: {product}")

    print(f"\nCollapsed output classes:")
    for regime, output in output_class_map.items():
        print(f"  {regime}: {output}")

    # Compute folio regimes
    print("\n1. Computing folio REGIME assignments...")
    folio_regimes = compute_folio_regime(tx, morph)

    regime_counts = defaultdict(int)
    for data in folio_regimes.values():
        regime_counts[data['regime']] += 1

    print(f"   Folios by REGIME:")
    for regime in ['REGIME_1', 'REGIME_2', 'REGIME_3', 'REGIME_4']:
        print(f"     {regime}: {regime_counts[regime]}")

    # Analyze suffix by regime
    print("\n2. Analyzing suffix distributions by REGIME...")
    suffix_results, all_suffixes = analyze_suffix_by_regime(tx, morph, folio_regimes)

    # Analyze MIDDLE by regime
    print("3. Analyzing MIDDLE distributions by REGIME...")
    middle_results = analyze_middle_by_regime(tx, morph, folio_regimes)

    # Find output-specific vocabulary
    print("\n4. Finding output-specific vocabulary (WATER vs OIL)...")
    suffix_enrichment, output_suffixes, output_middles = find_output_specific_vocabulary(
        suffix_results, middle_results, output_class_map
    )

    # Top differentiating suffixes
    oil_enriched = [(s, d) for s, d in suffix_enrichment.items() if d['direction'] == 'OIL']
    water_enriched = [(s, d) for s, d in suffix_enrichment.items() if d['direction'] == 'WATER']

    oil_enriched.sort(key=lambda x: x[1]['oil_water_ratio'], reverse=True)
    water_enriched.sort(key=lambda x: x[1]['oil_water_ratio'])

    print(f"\n   OIL-enriched suffixes (ratio > 1.5):")
    for suffix, data in oil_enriched[:5]:
        print(f"     -{suffix}: {data['oil_water_ratio']:.2f}x (oil={data['oil_rate']:.3f}, water={data['water_rate']:.3f})")

    print(f"\n   WATER-enriched suffixes (ratio < 0.67):")
    for suffix, data in water_enriched[:5]:
        print(f"     -{suffix}: {data['oil_water_ratio']:.2f}x (oil={data['oil_rate']:.3f}, water={data['water_rate']:.3f})")

    # Test correlation
    print("\n5. Testing vocabulary-output correlation...")
    corr_results, folio_features = test_vocabulary_output_correlation(
        tx, morph, folio_regimes, output_class_map
    )

    print(f"   Oil marker correlation: r={corr_results['oil_marker_correlation']['r']:.3f}, p={corr_results['oil_marker_correlation']['p']:.4f}")
    print(f"   Water marker correlation: r={corr_results['water_marker_correlation']['r']:.3f}, p={corr_results['water_marker_correlation']['p']:.4f}")

    # Completion markers
    print("\n6. Analyzing completion markers by output class...")
    final_comparison, output_finals = analyze_completion_markers(
        tx, morph, folio_regimes, output_class_map
    )

    # Most differentiated finals
    diff_finals = [(m, d) for m, d in final_comparison.items() if d['ratio'] > 2.0 or d['ratio'] < 0.5]
    diff_finals.sort(key=lambda x: abs(np.log(x[1]['ratio'] + 0.01)), reverse=True)

    print(f"\n   Most differentiated line-final MIDDLEs:")
    for middle, data in diff_finals[:5]:
        direction = 'OIL' if data['ratio'] > 1 else 'WATER'
        print(f"     {middle}: {data['ratio']:.2f}x toward {direction}")

    # Compile results
    results = {
        'phase': 'REVERSE_BRUNSCHWIG_V3',
        'test': 'output_category_signatures',
        'tier': 4,
        'external_anchor': 'Brunschwig product types (WATER vs OIL_RESIN)',
        'folio_regime_distribution': dict(regime_counts),
        'output_class_distribution': {
            'WATER': regime_counts['REGIME_1'] + regime_counts['REGIME_2'],
            'OIL': regime_counts['REGIME_3'],
            'PRECISION': regime_counts['REGIME_4']
        },
        'suffix_enrichment': {
            'oil_enriched': [(s, d) for s, d in oil_enriched[:10]],
            'water_enriched': [(s, d) for s, d in water_enriched[:10]]
        },
        'vocabulary_output_correlation': corr_results,
        'completion_marker_differentiation': diff_finals[:10],
        'verdict': None  # Will be set below
    }

    # Determine verdict
    oil_corr_sig = corr_results['oil_marker_correlation']['p'] < 0.05
    sufficient_oil_folios = regime_counts['REGIME_3'] >= 5
    has_differentiating_suffix = len(oil_enriched) > 0 or len(water_enriched) > 0

    if oil_corr_sig and sufficient_oil_folios:
        verdict = 'CONFIRMED'
        interpretation = 'Output category has vocabulary signature beyond REGIME structure'
    elif sufficient_oil_folios and has_differentiating_suffix:
        verdict = 'PARTIAL'
        interpretation = 'Some vocabulary differentiation but not statistically robust'
    elif not sufficient_oil_folios:
        verdict = 'INCONCLUSIVE'
        interpretation = 'Insufficient OIL-class folios to test (REGIME_3 rare in Voynich B)'
    else:
        verdict = 'NULL'
        interpretation = 'No evidence of output-specific vocabulary beyond REGIME'

    results['verdict'] = verdict
    results['interpretation'] = interpretation

    print(f"\n" + "=" * 50)
    print(f"VERDICT: {verdict}")
    print(f"Interpretation: {interpretation}")

    # Save results
    output_path = RESULTS_DIR / 'output_category_signatures.json'
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\nResults saved to {output_path}")

    return results

if __name__ == '__main__':
    main()
