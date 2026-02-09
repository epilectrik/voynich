#!/usr/bin/env python3
"""
E_EXTENSION_ROUTING_TEST - Script 02: Direct Routing Correlation

Test direct correlations (Tier A tests - expect null per C522):
1. A-folio e-extension index -> B folio lane balance
2. A-folio e-extension -> REGIME distribution
3. Late Currier A (f100-f102) routing distinctiveness

These test the hypothesis that e-extension in A predicts execution
characteristics in B. C522 predicts these will be null.
"""

import sys
import json
from pathlib import Path
from collections import defaultdict
import numpy as np
from scipy import stats

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'scripts'))
from voynich import Transcript, Morphology

def load_e_extension_index():
    """Load results from script 01."""
    path = Path(__file__).parent.parent / 'results' / '01_e_extension_index.json'
    with open(path) as f:
        return json.load(f)

def compute_b_folio_metrics():
    """Compute B folio metrics: lane balance, REGIME indicators, kernel content."""
    tx = Transcript()
    morph = Morphology()

    folio_data = defaultdict(lambda: {
        'tokens': [],
        'chsh_count': 0,
        'qo_count': 0,
        'e_count': 0,
        'k_count': 0,
        'h_count': 0,
        'kernel_tokens': 0
    })

    for token in tx.currier_b():
        folio = token.folio
        word = token.word
        m = morph.extract(word)
        prefix = m.prefix or ''

        folio_data[folio]['tokens'].append(word)

        # Lane classification by prefix
        if prefix in ['ch', 'sh']:
            folio_data[folio]['chsh_count'] += 1
        elif prefix == 'qo':
            folio_data[folio]['qo_count'] += 1

        # Kernel character content
        if 'e' in word:
            folio_data[folio]['e_count'] += 1
        if 'k' in word:
            folio_data[folio]['k_count'] += 1
        if 'h' in word:
            folio_data[folio]['h_count'] += 1
        if any(c in word for c in ['e', 'k', 'h']):
            folio_data[folio]['kernel_tokens'] += 1

    # Compute derived metrics
    results = {}
    for folio, data in folio_data.items():
        n = len(data['tokens'])
        if n == 0:
            continue

        chsh = data['chsh_count']
        qo = data['qo_count']
        lane_total = chsh + qo

        results[folio] = {
            'n_tokens': n,
            'chsh_count': chsh,
            'qo_count': qo,
            'chsh_fraction': chsh / n if n > 0 else 0,
            'qo_fraction': qo / n if n > 0 else 0,
            'lane_balance': chsh / lane_total if lane_total > 0 else 0.5,  # CHSH/(CHSH+QO)
            'e_fraction': data['e_count'] / n,
            'k_fraction': data['k_count'] / n,
            'h_fraction': data['h_count'] / n,
            'kernel_fraction': data['kernel_tokens'] / n
        }

    return results

def compute_a_to_b_coverage():
    """Compute which B folios each A folio's vocabulary can reach."""
    tx = Transcript()
    morph = Morphology()

    # Build A folio -> MIDDLE sets
    a_folio_middles = defaultdict(set)
    for token in tx.currier_a():
        m = morph.extract(token.word)
        if m.middle:
            a_folio_middles[token.folio].add(m.middle)

    # Build B folio -> MIDDLE sets
    b_folio_middles = defaultdict(set)
    for token in tx.currier_b():
        m = morph.extract(token.word)
        if m.middle:
            b_folio_middles[token.folio].add(m.middle)

    # For each A folio, compute coverage of each B folio
    coverage = {}
    for a_folio, a_middles in a_folio_middles.items():
        coverage[a_folio] = {}
        for b_folio, b_middles in b_folio_middles.items():
            if len(b_middles) == 0:
                continue
            overlap = len(a_middles & b_middles)
            coverage[a_folio][b_folio] = overlap / len(b_middles)

    return coverage

def main():
    print("=" * 70)
    print("DIRECT ROUTING CORRELATION TESTS")
    print("Testing C522: Construction-Execution Layer Independence")
    print("=" * 70)

    # Load e-extension index
    e_index = load_e_extension_index()

    # Compute B folio metrics
    print("\nComputing B folio metrics...")
    b_metrics = compute_b_folio_metrics()

    # Compute A->B coverage
    print("Computing A->B vocabulary coverage...")
    coverage = compute_a_to_b_coverage()

    results = {
        'test_1_lane_balance': {},
        'test_2_kernel_content': {},
        'test_3_late_a_distinctiveness': {},
        'summary': {}
    }

    # ===========================================
    # TEST 1: A e-extension -> B lane balance
    # ===========================================
    print("\n" + "-" * 50)
    print("TEST 1: A e-extension -> B lane balance")
    print("-" * 50)

    # For each A folio, compute weighted average of receiving B folio lane balance
    a_e_scores = []
    a_weighted_lane_balance = []

    for a_folio in sorted(e_index['folios'].keys()):
        if a_folio not in coverage:
            continue

        e_score = e_index['folios'][a_folio]['mean_max_consecutive_e']

        # Weighted average of B folio lane balance (weighted by coverage)
        total_weight = 0
        weighted_lb = 0
        for b_folio, cov in coverage[a_folio].items():
            if b_folio in b_metrics and cov > 0:
                weighted_lb += cov * b_metrics[b_folio]['lane_balance']
                total_weight += cov

        if total_weight > 0:
            a_e_scores.append(e_score)
            a_weighted_lane_balance.append(weighted_lb / total_weight)

    if len(a_e_scores) > 2:
        rho, p = stats.spearmanr(a_e_scores, a_weighted_lane_balance)
        results['test_1_lane_balance'] = {
            'n_folios': len(a_e_scores),
            'spearman_rho': round(rho, 4),
            'p_value': round(p, 6),
            'significant': bool(p < 0.05),
            'interpretation': 'POSITIVE' if rho > 0 else 'NEGATIVE' if rho < 0 else 'NEUTRAL'
        }
        print(f"  A folios tested: {len(a_e_scores)}")
        print(f"  Spearman rho: {rho:.4f}")
        print(f"  p-value: {p:.6f}")
        print(f"  Significant (p<0.05): {p < 0.05}")
        if p < 0.05:
            print(f"  ** UNEXPECTED: Significant correlation found! **")
        else:
            print(f"  Result: NULL (as predicted by C522)")

    # ===========================================
    # TEST 2: A e-extension -> B kernel content
    # ===========================================
    print("\n" + "-" * 50)
    print("TEST 2: A e-extension -> B e-content (kernel)")
    print("-" * 50)

    a_e_scores = []
    a_weighted_e_content = []

    for a_folio in sorted(e_index['folios'].keys()):
        if a_folio not in coverage:
            continue

        e_score = e_index['folios'][a_folio]['mean_max_consecutive_e']

        # Weighted average of B folio e-fraction
        total_weight = 0
        weighted_e = 0
        for b_folio, cov in coverage[a_folio].items():
            if b_folio in b_metrics and cov > 0:
                weighted_e += cov * b_metrics[b_folio]['e_fraction']
                total_weight += cov

        if total_weight > 0:
            a_e_scores.append(e_score)
            a_weighted_e_content.append(weighted_e / total_weight)

    if len(a_e_scores) > 2:
        rho, p = stats.spearmanr(a_e_scores, a_weighted_e_content)
        results['test_2_kernel_content'] = {
            'n_folios': len(a_e_scores),
            'spearman_rho': round(rho, 4),
            'p_value': round(p, 6),
            'significant': bool(p < 0.05),
            'interpretation': 'POSITIVE' if rho > 0 else 'NEGATIVE' if rho < 0 else 'NEUTRAL'
        }
        print(f"  A folios tested: {len(a_e_scores)}")
        print(f"  Spearman rho: {rho:.4f}")
        print(f"  p-value: {p:.6f}")
        print(f"  Significant (p<0.05): {p < 0.05}")
        if p < 0.05:
            print(f"  ** UNEXPECTED: Significant correlation found! **")
        else:
            print(f"  Result: NULL (as predicted by C522)")

    # ===========================================
    # TEST 3: Late A (f100-f102) distinctiveness
    # ===========================================
    print("\n" + "-" * 50)
    print("TEST 3: Late Currier A (f100-f102) routing distinctiveness")
    print("-" * 50)

    late_a_folios = [f for f in e_index['folios'].keys() if f.startswith('f10')]
    other_a_folios = [f for f in e_index['folios'].keys() if not f.startswith('f10')]

    # Compare mean lane balance of B folios reached
    late_lb = []
    other_lb = []

    for a_folio in late_a_folios:
        if a_folio not in coverage:
            continue
        total_weight = 0
        weighted_lb = 0
        for b_folio, cov in coverage[a_folio].items():
            if b_folio in b_metrics and cov > 0:
                weighted_lb += cov * b_metrics[b_folio]['lane_balance']
                total_weight += cov
        if total_weight > 0:
            late_lb.append(weighted_lb / total_weight)

    for a_folio in other_a_folios:
        if a_folio not in coverage:
            continue
        total_weight = 0
        weighted_lb = 0
        for b_folio, cov in coverage[a_folio].items():
            if b_folio in b_metrics and cov > 0:
                weighted_lb += cov * b_metrics[b_folio]['lane_balance']
                total_weight += cov
        if total_weight > 0:
            other_lb.append(weighted_lb / total_weight)

    if len(late_lb) > 1 and len(other_lb) > 1:
        u_stat, p = stats.mannwhitneyu(late_lb, other_lb, alternative='two-sided')
        effect_size = np.mean(late_lb) - np.mean(other_lb)

        results['test_3_late_a_distinctiveness'] = {
            'late_a_folios': len(late_lb),
            'other_a_folios': len(other_lb),
            'late_a_mean_lane_balance': round(np.mean(late_lb), 4),
            'other_a_mean_lane_balance': round(np.mean(other_lb), 4),
            'effect_size': round(effect_size, 4),
            'mann_whitney_u': float(u_stat),
            'p_value': round(p, 6),
            'significant': bool(p < 0.05)
        }
        print(f"  Late A folios (f10x): {len(late_lb)}")
        print(f"  Other A folios: {len(other_lb)}")
        print(f"  Late A mean lane balance: {np.mean(late_lb):.4f}")
        print(f"  Other A mean lane balance: {np.mean(other_lb):.4f}")
        print(f"  Effect size: {effect_size:.4f}")
        print(f"  Mann-Whitney U p-value: {p:.6f}")
        print(f"  Significant (p<0.05): {p < 0.05}")
        if p < 0.05:
            print(f"  ** Late A routes differently! **")
        else:
            print(f"  Result: NULL - Late A routes same as other A")

    # ===========================================
    # SUMMARY
    # ===========================================
    print("\n" + "=" * 70)
    print("TIER A SUMMARY (Direct Correlation Tests)")
    print("=" * 70)

    null_count = sum([
        1 if not results['test_1_lane_balance'].get('significant', True) else 0,
        1 if not results['test_2_kernel_content'].get('significant', True) else 0,
        1 if not results['test_3_late_a_distinctiveness'].get('significant', True) else 0
    ])

    results['summary'] = {
        'tests_run': 3,
        'null_results': null_count,
        'c522_confirmed': null_count == 3,
        'verdict': 'C522 CONFIRMED - Construction and execution layers are independent' if null_count == 3
                   else f'PARTIAL - {3 - null_count}/3 tests showed unexpected correlation'
    }

    print(f"\n  Tests run: 3")
    print(f"  Null results: {null_count}/3")
    print(f"  C522 Confirmed: {null_count == 3}")
    print(f"\n  VERDICT: {results['summary']['verdict']}")

    # Save results
    output_path = Path(__file__).parent.parent / 'results' / '02_direct_routing_correlation.json'
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to: {output_path}")

if __name__ == '__main__':
    main()
