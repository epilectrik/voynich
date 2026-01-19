"""
AXIS 4: A <-> AZC Micro-Interface

Questions:
1. Do certain A entry morphologies preferentially activate narrow AZC compatibility cones?
2. Is there asymmetry between universal vs tail MIDDLEs in AZC activation breadth?
3. Does A adjacency predict AZC choice diversity without predicting content?

No AZC grammar changes - characterization only.
All tests use order-robust methods where possible.
"""

import json
import numpy as np
from pathlib import Path
from collections import Counter, defaultdict
from scipy import stats
from typing import Dict, List, Set, Tuple
import random

from pcc_data_loader import (
    PCCDataLoader, permutation_test, bootstrap_ci
)


class AZCAnalyzer:
    """
    Analyzer for A <-> AZC interface properties.

    NOTE: AZC data is derived from Currier A morphology.
    We analyze how A entry vocabulary predicts AZC activation patterns.
    """

    def __init__(self, loader: PCCDataLoader):
        self.loader = loader
        self.entries = loader.get_entries()
        self.all_middles = loader.get_all_middles(self.entries)

        # Define MIDDLE categories
        self._categorize_middles()

    def _categorize_middles(self):
        """Categorize MIDDLEs by frequency tier."""
        total = sum(self.all_middles.values())
        sorted_middles = sorted(self.all_middles.items(), key=lambda x: x[1], reverse=True)

        # Hub = top 10%, Universal = next 40%, Tail = bottom 50%
        n = len(sorted_middles)
        hub_cutoff = n // 10
        universal_cutoff = n // 2

        self.hub_middles = {m for m, c in sorted_middles[:hub_cutoff]}
        self.universal_middles = {m for m, c in sorted_middles[hub_cutoff:universal_cutoff]}
        self.tail_middles = {m for m, c in sorted_middles[universal_cutoff:]}

    def get_entry_profile(self, entry: Dict) -> Dict:
        """Get AZC-relevant profile for an entry."""
        middles = entry['middles']

        hub_count = len(middles & self.hub_middles)
        universal_count = len(middles & self.universal_middles)
        tail_count = len(middles & self.tail_middles)

        total = len(middles)
        if total == 0:
            return {
                'hub_ratio': 0, 'universal_ratio': 0, 'tail_ratio': 0,
                'total_middles': 0, 'diversity': 0
            }

        return {
            'hub_ratio': hub_count / total,
            'universal_ratio': universal_count / total,
            'tail_ratio': tail_count / total,
            'total_middles': total,
            'diversity': len(middles)  # Number of unique MIDDLEs
        }

    def estimate_azc_breadth(self, entry: Dict) -> float:
        """
        Estimate AZC activation breadth from entry vocabulary.

        Heuristic: Entries with more hub MIDDLEs have broader compatibility.
        Entries with more tail MIDDLEs have narrower compatibility.

        This is a PROXY - actual AZC compatibility requires the full constraint system.

        ORDER SENSITIVITY: INVARIANT
        """
        profile = self.get_entry_profile(entry)

        # Breadth heuristic: hub-heavy = broad, tail-heavy = narrow
        # Scale: 0 (very narrow) to 1 (very broad)
        if profile['total_middles'] == 0:
            return 0.5  # Neutral

        breadth = (
            profile['hub_ratio'] * 1.0 +
            profile['universal_ratio'] * 0.5 +
            profile['tail_ratio'] * 0.1
        )

        return breadth


def test_morphology_azc_activation(analyzer: AZCAnalyzer) -> Dict:
    """
    Q1: Do certain A entry morphologies preferentially activate narrow AZC compatibility cones?

    Hypothesis: Entries with specific morphological patterns (e.g., high closure,
    specific PREFIX families) may correlate with narrower AZC activation.

    ORDER SENSITIVITY: INVARIANT
    """
    print("\n" + "-"*60)
    print("Q1: Entry Morphology vs AZC Activation Breadth")
    print("-"*60)

    entries = analyzer.entries

    # Group entries by morphological features
    results_by_closure = {'with_closure': [], 'without_closure': []}
    results_by_opener = {'with_opener': [], 'without_opener': []}
    results_by_length = {'short': [], 'medium': [], 'long': []}

    for entry in entries:
        breadth = analyzer.estimate_azc_breadth(entry)

        # By closure
        if entry['has_any_closure']:
            results_by_closure['with_closure'].append(breadth)
        else:
            results_by_closure['without_closure'].append(breadth)

        # By opener
        if entry['has_non_prefix_opener']:
            results_by_opener['with_opener'].append(breadth)
        else:
            results_by_opener['without_opener'].append(breadth)

        # By length
        n_tokens = entry['token_count']
        if n_tokens <= 4:
            results_by_length['short'].append(breadth)
        elif n_tokens <= 8:
            results_by_length['medium'].append(breadth)
        else:
            results_by_length['long'].append(breadth)

    # Analyze closure effect
    print("\n  AZC breadth by closure:")
    mean_with = np.mean(results_by_closure['with_closure'])
    mean_without = np.mean(results_by_closure['without_closure'])
    print(f"    With closure: {mean_with:.4f}")
    print(f"    Without closure: {mean_without:.4f}")

    if results_by_closure['without_closure']:
        u_closure, p_closure = stats.mannwhitneyu(
            results_by_closure['with_closure'],
            results_by_closure['without_closure'],
            alternative='two-sided'
        )
        print(f"    Mann-Whitney p = {p_closure:.4f}")
    else:
        p_closure = 1.0

    # Analyze opener effect
    print("\n  AZC breadth by opener:")
    mean_opener = np.mean(results_by_opener['with_opener'])
    mean_no_opener = np.mean(results_by_opener['without_opener'])
    print(f"    With non-prefix opener: {mean_opener:.4f}")
    print(f"    With prefix opener: {mean_no_opener:.4f}")

    if results_by_opener['without_opener']:
        u_opener, p_opener = stats.mannwhitneyu(
            results_by_opener['with_opener'],
            results_by_opener['without_opener'],
            alternative='two-sided'
        )
        print(f"    Mann-Whitney p = {p_opener:.4f}")
    else:
        p_opener = 1.0

    # Analyze length effect
    print("\n  AZC breadth by entry length:")
    for length_cat in ['short', 'medium', 'long']:
        vals = results_by_length[length_cat]
        print(f"    {length_cat}: {np.mean(vals):.4f} (n={len(vals)})")

    # Kruskal-Wallis test
    h_stat, p_length = stats.kruskal(
        results_by_length['short'],
        results_by_length['medium'],
        results_by_length['long']
    )
    print(f"    Kruskal-Wallis p = {p_length:.4f}")

    # Determine verdict
    significant_effects = []
    if p_closure < 0.05:
        significant_effects.append('closure')
    if p_opener < 0.05:
        significant_effects.append('opener')
    if p_length < 0.05:
        significant_effects.append('length')

    if len(significant_effects) >= 2:
        verdict = "YES"
        interpretation = f"Morphology predicts AZC breadth: {', '.join(significant_effects)}"
    elif len(significant_effects) == 1:
        verdict = "WEAK_YES"
        interpretation = f"Marginal effect from: {significant_effects[0]}"
    else:
        verdict = "NO"
        interpretation = "Entry morphology does not predict AZC activation breadth"

    print(f"\n  VERDICT: {verdict}")
    print(f"  {interpretation}")
    print(f"\n  ORDER SENSITIVITY: INVARIANT")

    return {
        'question': 'Entry Morphology vs AZC Activation Breadth',
        'order_sensitivity': 'INVARIANT',
        'closure_effect': {
            'mean_with': float(mean_with),
            'mean_without': float(mean_without),
            'p_value': float(p_closure)
        },
        'opener_effect': {
            'mean_with': float(mean_opener),
            'mean_without': float(mean_no_opener),
            'p_value': float(p_opener)
        },
        'length_effect': {
            'means': {k: float(np.mean(v)) for k, v in results_by_length.items()},
            'p_value': float(p_length)
        },
        'verdict': verdict,
        'interpretation': interpretation
    }


def test_universal_vs_tail_asymmetry(analyzer: AZCAnalyzer) -> Dict:
    """
    Q2: Is there asymmetry between universal vs tail MIDDLEs in AZC activation breadth?

    Hypothesis: Universal MIDDLEs should enable broader AZC activation
    than tail MIDDLEs (more compatible across contexts).

    ORDER SENSITIVITY: INVARIANT
    """
    print("\n" + "-"*60)
    print("Q2: Universal vs Tail MIDDLE Asymmetry")
    print("-"*60)

    entries = analyzer.entries

    print(f"\n  Hub MIDDLEs (top 10%): {len(analyzer.hub_middles)}")
    print(f"  Universal MIDDLEs (10-50%): {len(analyzer.universal_middles)}")
    print(f"  Tail MIDDLEs (bottom 50%): {len(analyzer.tail_middles)}")

    # Group entries by dominant MIDDLE category
    hub_dominant = []
    universal_dominant = []
    tail_dominant = []
    mixed = []

    for entry in entries:
        profile = analyzer.get_entry_profile(entry)

        if profile['total_middles'] == 0:
            continue

        # Determine dominant category
        max_ratio = max(profile['hub_ratio'], profile['universal_ratio'], profile['tail_ratio'])

        if profile['hub_ratio'] == max_ratio and max_ratio > 0.4:
            hub_dominant.append(analyzer.estimate_azc_breadth(entry))
        elif profile['universal_ratio'] == max_ratio and max_ratio > 0.4:
            universal_dominant.append(analyzer.estimate_azc_breadth(entry))
        elif profile['tail_ratio'] == max_ratio and max_ratio > 0.4:
            tail_dominant.append(analyzer.estimate_azc_breadth(entry))
        else:
            mixed.append(analyzer.estimate_azc_breadth(entry))

    print(f"\n  Entry categorization:")
    print(f"    Hub-dominant: {len(hub_dominant)}")
    print(f"    Universal-dominant: {len(universal_dominant)}")
    print(f"    Tail-dominant: {len(tail_dominant)}")
    print(f"    Mixed: {len(mixed)}")

    # Compare breadths
    print(f"\n  Mean AZC breadth by category:")
    if hub_dominant:
        print(f"    Hub-dominant: {np.mean(hub_dominant):.4f}")
    if universal_dominant:
        print(f"    Universal-dominant: {np.mean(universal_dominant):.4f}")
    if tail_dominant:
        print(f"    Tail-dominant: {np.mean(tail_dominant):.4f}")
    if mixed:
        print(f"    Mixed: {np.mean(mixed):.4f}")

    # Key comparison: Universal vs Tail
    if universal_dominant and tail_dominant:
        u_stat, p_value = stats.mannwhitneyu(
            universal_dominant, tail_dominant,
            alternative='greater'  # Universal should be broader
        )
        mean_diff = np.mean(universal_dominant) - np.mean(tail_dominant)

        print(f"\n  Universal vs Tail comparison:")
        print(f"    Difference: {mean_diff:.4f}")
        print(f"    Mann-Whitney (universal > tail) p = {p_value:.4f}")

        if p_value < 0.01 and mean_diff > 0.05:
            verdict = "YES"
            interpretation = "Strong asymmetry: universal MIDDLEs enable broader activation"
        elif p_value < 0.05:
            verdict = "WEAK_YES"
            interpretation = "Moderate asymmetry detected"
        else:
            verdict = "NO"
            interpretation = "No significant universal/tail asymmetry"
    else:
        verdict = "INCONCLUSIVE"
        interpretation = "Insufficient data for comparison"
        p_value = 1.0
        mean_diff = 0

    print(f"\n  VERDICT: {verdict}")
    print(f"  {interpretation}")
    print(f"\n  ORDER SENSITIVITY: INVARIANT")

    return {
        'question': 'Universal vs Tail MIDDLE Asymmetry',
        'order_sensitivity': 'INVARIANT',
        'n_hub_dominant': len(hub_dominant),
        'n_universal_dominant': len(universal_dominant),
        'n_tail_dominant': len(tail_dominant),
        'n_mixed': len(mixed),
        'mean_hub': float(np.mean(hub_dominant)) if hub_dominant else None,
        'mean_universal': float(np.mean(universal_dominant)) if universal_dominant else None,
        'mean_tail': float(np.mean(tail_dominant)) if tail_dominant else None,
        'mean_diff': float(mean_diff),
        'p_value': float(p_value),
        'verdict': verdict,
        'interpretation': interpretation
    }


def test_adjacency_azc_diversity(analyzer: AZCAnalyzer,
                                  loader: PCCDataLoader) -> Dict:
    """
    Q3: Does A adjacency predict AZC choice diversity without predicting content?

    Hypothesis: Adjacent entries may have similar AZC breadths (coordinated
    activation) even if they have different vocabulary content.

    ORDER SENSITIVITY: FOLIO_LOCAL_ORDER
    """
    print("\n" + "-"*60)
    print("Q3: Adjacency vs AZC Choice Diversity")
    print("-"*60)

    entries = analyzer.entries

    # Sort by folio and line
    sorted_entries = sorted(entries, key=lambda e: (e['folio'], e['line_number']))

    # Calculate breadth similarity for adjacent pairs
    adjacent_breadth_diffs = []
    adjacent_content_sims = []

    for i in range(len(sorted_entries) - 1):
        curr = sorted_entries[i]
        next_entry = sorted_entries[i + 1]

        if curr['folio'] != next_entry['folio']:
            continue

        # Breadth difference
        breadth_curr = analyzer.estimate_azc_breadth(curr)
        breadth_next = analyzer.estimate_azc_breadth(next_entry)
        breadth_diff = abs(breadth_curr - breadth_next)
        adjacent_breadth_diffs.append(breadth_diff)

        # Content similarity
        content_sim = loader.jaccard_similarity(
            curr['middles'], next_entry['middles']
        )
        adjacent_content_sims.append(content_sim)

    # Random baseline for breadth
    n_permutations = 500
    random_breadth_diffs = []

    all_breadths = [analyzer.estimate_azc_breadth(e) for e in entries]

    for _ in range(n_permutations):
        shuffled = random.sample(all_breadths, len(all_breadths))
        diffs = [abs(shuffled[i] - shuffled[i+1])
                 for i in range(len(shuffled) - 1)]
        random_breadth_diffs.append(np.mean(diffs))

    mean_adjacent = np.mean(adjacent_breadth_diffs)
    mean_random = np.mean(random_breadth_diffs)

    p_value = permutation_test(mean_adjacent, random_breadth_diffs, 'less')

    print(f"\n  Adjacent pairs analyzed: {len(adjacent_breadth_diffs)}")
    print(f"\n  AZC breadth difference:")
    print(f"    Adjacent pairs: {mean_adjacent:.4f}")
    print(f"    Random baseline: {mean_random:.4f}")
    print(f"    Permutation p (adjacent < random): {p_value:.4f}")

    # Check if breadth similarity is independent of content similarity
    if len(adjacent_breadth_diffs) > 10:
        corr, p_corr = stats.spearmanr(adjacent_breadth_diffs, adjacent_content_sims)
        print(f"\n  Breadth diff vs Content sim correlation:")
        print(f"    Spearman rho: {corr:.3f}")
        print(f"    p-value: {p_corr:.4f}")
    else:
        corr, p_corr = 0, 1.0

    # Verdict
    if p_value < 0.05:
        breadth_verdict = "YES"
    else:
        breadth_verdict = "NO"

    if abs(corr) < 0.2 or p_corr > 0.05:
        independence_verdict = "YES"
    else:
        independence_verdict = "NO"

    if breadth_verdict == "YES" and independence_verdict == "YES":
        verdict = "YES"
        interpretation = "Adjacent entries have coordinated AZC breadth, independent of content"
    elif breadth_verdict == "YES":
        verdict = "PARTIAL"
        interpretation = "Coordinated breadth, but correlated with content"
    else:
        verdict = "NO"
        interpretation = "No adjacency-AZC coordination detected"

    print(f"\n  VERDICT: {verdict}")
    print(f"  {interpretation}")
    print(f"\n  ORDER SENSITIVITY: FOLIO_LOCAL_ORDER")

    return {
        'question': 'Adjacency vs AZC Choice Diversity',
        'order_sensitivity': 'FOLIO_LOCAL_ORDER',
        'n_pairs': len(adjacent_breadth_diffs),
        'mean_adjacent_breadth_diff': float(mean_adjacent),
        'mean_random_breadth_diff': float(mean_random),
        'p_value': float(p_value),
        'breadth_content_correlation': float(corr),
        'p_correlation': float(p_corr),
        'breadth_verdict': breadth_verdict,
        'independence_verdict': independence_verdict,
        'verdict': verdict,
        'interpretation': interpretation
    }


def generate_axis4_report(results: Dict) -> str:
    """Generate formatted AXIS 4 report."""
    report = """
================================================================================
AXIS 4 REPORT: A <-> AZC Micro-Interface
================================================================================

PHASE: Post-Closure Characterization
TIER: 3 (Exploratory characterization)
REBINDING SENSITIVITY: MIXED (2 INVARIANT, 1 FOLIO_LOCAL_ORDER)

--------------------------------------------------------------------------------
IMPORTANT CAVEAT
--------------------------------------------------------------------------------

AZC activation breadth is ESTIMATED from vocabulary composition.
Actual AZC compatibility requires the full constraint system.
These findings characterize the A->AZC INTERFACE, not AZC itself.

--------------------------------------------------------------------------------
SUMMARY OF FINDINGS
--------------------------------------------------------------------------------

"""
    for q_num, (key, data) in enumerate(results.items(), 1):
        report += f"""
Q{q_num}: {data['question']}
    Order Sensitivity: {data['order_sensitivity']}
    Verdict: {data['verdict']}
    Interpretation: {data['interpretation']}
"""

    report += """
--------------------------------------------------------------------------------
WHAT THIS DOES NOT CHANGE
--------------------------------------------------------------------------------

- AZC grammar (C319-C433) unchanged
- AZC activation rules unchanged
- No new A->AZC correspondence proposed
- Interface is characterized, not redefined

--------------------------------------------------------------------------------
IMPLICATIONS
--------------------------------------------------------------------------------

"""
    verdicts = [r['verdict'] for r in results.values()]
    if 'YES' in verdicts:
        report += """
POSITIVE FINDINGS:
- A entry structure has measurable relationship to AZC activation breadth
- Some morphological features predict compatibility cone width
- This supports A as an AZC-facing interface layer
"""
    else:
        report += """
NULL/WEAK FINDINGS:
- A entry structure does not strongly predict AZC activation
- Or: the breadth proxy is too crude to detect the relationship
"""

    report += """
--------------------------------------------------------------------------------
NON-IMPLICATIONS
--------------------------------------------------------------------------------

- Does NOT mean A entries "select" specific AZC positions
- Does NOT imply entry-level A->B correspondence
- Does NOT change C384 (no A-B coupling)
- Interface characterization != interface grammar

================================================================================
"""
    return report


def main():
    print("="*70)
    print("AXIS 4: A <-> AZC Micro-Interface")
    print("="*70)

    # Load data
    print("\nLoading data...")
    loader = PCCDataLoader()
    analyzer = AZCAnalyzer(loader)
    print(f"Loaded {len(analyzer.entries)} entries")

    # Run all tests
    results = {}

    results['q1_morphology_activation'] = test_morphology_azc_activation(analyzer)
    results['q2_universal_tail_asymmetry'] = test_universal_vs_tail_asymmetry(analyzer)
    results['q3_adjacency_diversity'] = test_adjacency_azc_diversity(analyzer, loader)

    # Generate report
    report = generate_axis4_report(results)
    print(report)

    # Save results
    output_path = Path(__file__).parent / 'axis4_results.json'
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nResults saved to: {output_path}")

    # Save report
    report_path = Path(__file__).parent / 'AXIS4_REPORT.md'
    with open(report_path, 'w') as f:
        f.write(report)
    print(f"Report saved to: {report_path}")

    return results


if __name__ == '__main__':
    main()
