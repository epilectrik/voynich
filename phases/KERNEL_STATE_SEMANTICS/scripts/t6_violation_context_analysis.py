#!/usr/bin/env python3
"""
Test 6: Disfavored Transition Violation Context Analysis

When the "forbidden" transitions DO occur (~35% of the time):
- What context allows the violation?
- Are violations clustered in specific folios/sections?
- Are violations associated with specific roles?
- Is there a "cost" visible in subsequent tokens?

Goal: Understand when disfavored transitions happen and whether they have consequences.
"""

import json
import sys
from pathlib import Path
from collections import defaultdict, Counter
import numpy as np
from scipy import stats

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "scripts"))
from voynich import Transcript


def get_kernel_signature(word: str) -> str:
    """Get kernel signature: k, h, e, or n (none)."""
    if 'k' in word:
        return 'k'
    if 'h' in word:
        return 'h'
    if 'e' in word:
        return 'e'
    return 'n'


def main():
    print("=" * 60)
    print("Test 6: Disfavored Transition Violation Context Analysis")
    print("=" * 60)

    tx = Transcript()

    # Collect all B tokens with metadata
    tokens_by_line = defaultdict(list)
    all_tokens = []

    for token in tx.currier_b():
        t = {
            'word': token.word,
            'folio': token.folio,
            'line': token.line,
            'section': getattr(token, 'section', 'unknown'),
        }
        key = (token.folio, token.line)
        tokens_by_line[key].append(t)
        all_tokens.append(t)

    print(f"\nTotal tokens: {len(all_tokens)}")
    print(f"Total lines: {len(tokens_by_line)}")

    # Build bigrams with context
    bigrams = []
    for key, line_toks in tokens_by_line.items():
        for i in range(len(line_toks) - 1):
            t1 = line_toks[i]
            t2 = line_toks[i + 1]

            k1 = get_kernel_signature(t1['word'])
            k2 = get_kernel_signature(t2['word'])

            # Get successor (if exists)
            successor = line_toks[i + 2] if i + 2 < len(line_toks) else None

            bigrams.append({
                'source': t1['word'],
                'target': t2['word'],
                'source_kernel': k1,
                'target_kernel': k2,
                'transition': f"{k1}->{k2}",
                'folio': t1['folio'],
                'section': t1['section'],
                'line': t1['line'],
                'position_in_line': i,
                'line_length': len(line_toks),
                'successor': successor['word'] if successor else None,
                'successor_kernel': get_kernel_signature(successor['word']) if successor else None,
            })

    print(f"Total bigrams: {len(bigrams)}")

    # Identify disfavored transitions based on C521/C109
    # Key disfavored: e->h, e->k, h->k
    disfavored_transitions = {'e->h', 'e->k', 'h->k'}

    # Count all and disfavored
    trans_counts = Counter(bg['transition'] for bg in bigrams)
    total_disfavored = sum(trans_counts[t] for t in disfavored_transitions)

    print(f"\nDisfavored transitions identified: {disfavored_transitions}")
    for t in disfavored_transitions:
        print(f"  {t}: {trans_counts[t]} occurrences")
    print(f"Total disfavored: {total_disfavored}")

    # Analyze violations
    violations = [bg for bg in bigrams if bg['transition'] in disfavored_transitions]
    non_violations = [bg for bg in bigrams if bg['transition'] not in disfavored_transitions]

    print(f"\nViolation rate: {len(violations)}/{len(bigrams)} ({100*len(violations)/len(bigrams):.1f}%)")

    results = {
        'total_bigrams': len(bigrams),
        'total_violations': len(violations),
        'violation_rate': len(violations) / len(bigrams),
    }

    # 1. Section distribution of violations
    print("\n" + "=" * 40)
    print("1. Section Distribution of Violations")
    print("=" * 40)

    violation_sections = Counter(bg['section'] for bg in violations)
    all_sections = Counter(bg['section'] for bg in bigrams)

    print("\nViolations by section:")
    for section in sorted(all_sections.keys()):
        viol_count = violation_sections.get(section, 0)
        total_count = all_sections[section]
        rate = viol_count / total_count if total_count > 0 else 0
        print(f"  {section}: {viol_count}/{total_count} ({100*rate:.1f}%)")

    results['section_violation_rates'] = {
        s: violation_sections.get(s, 0) / all_sections[s] for s in all_sections
    }

    # 2. Folio distribution of violations
    print("\n" + "=" * 40)
    print("2. Folio Distribution of Violations")
    print("=" * 40)

    violation_folios = Counter(bg['folio'] for bg in violations)
    all_folios = Counter(bg['folio'] for bg in bigrams)

    folio_rates = {}
    for folio in all_folios:
        viol = violation_folios.get(folio, 0)
        total = all_folios[folio]
        folio_rates[folio] = viol / total if total > 0 else 0

    # Find high-violation and low-violation folios
    sorted_folios = sorted(folio_rates.items(), key=lambda x: -x[1])

    print("\nTop 10 high-violation folios:")
    for folio, rate in sorted_folios[:10]:
        count = violation_folios.get(folio, 0)
        total = all_folios[folio]
        print(f"  {folio}: {100*rate:.1f}% ({count}/{total})")

    print("\nTop 10 low-violation folios:")
    for folio, rate in sorted_folios[-10:]:
        count = violation_folios.get(folio, 0)
        total = all_folios[folio]
        print(f"  {folio}: {100*rate:.1f}% ({count}/{total})")

    # Test if violation rate varies significantly by folio
    folio_rates_list = list(folio_rates.values())
    cv = np.std(folio_rates_list) / np.mean(folio_rates_list) if np.mean(folio_rates_list) > 0 else 0
    print(f"\nFolio rate coefficient of variation: {cv:.2f}")
    print(f"  (CV > 0.5 suggests meaningful variation)")

    results['folio_violation_cv'] = cv
    results['high_violation_folios'] = [f for f, r in sorted_folios[:5]]
    results['low_violation_folios'] = [f for f, r in sorted_folios[-5:]]

    # 3. Line position of violations
    print("\n" + "=" * 40)
    print("3. Line Position of Violations")
    print("=" * 40)

    violation_positions = [bg['position_in_line'] / (bg['line_length'] - 1)
                          for bg in violations if bg['line_length'] > 1]
    non_violation_positions = [bg['position_in_line'] / (bg['line_length'] - 1)
                               for bg in non_violations if bg['line_length'] > 1]

    if violation_positions and non_violation_positions:
        print(f"\nViolations: mean pos={np.mean(violation_positions):.3f}, n={len(violation_positions)}")
        print(f"Non-violations: mean pos={np.mean(non_violation_positions):.3f}, n={len(non_violation_positions)}")

        stat, p = stats.mannwhitneyu(violation_positions, non_violation_positions)
        print(f"Mann-Whitney U: p={p:.4f}")

        if p < 0.05:
            if np.mean(violation_positions) > np.mean(non_violation_positions):
                print("-> Violations occur LATER in lines (significant)")
            else:
                print("-> Violations occur EARLIER in lines (significant)")
        else:
            print("-> No significant position difference")

        results['violation_mean_position'] = float(np.mean(violation_positions))
        results['non_violation_mean_position'] = float(np.mean(non_violation_positions))
        results['position_p_value'] = float(p)

    # 4. What follows violations?
    print("\n" + "=" * 40)
    print("4. What Follows Violations?")
    print("=" * 40)

    # Successor kernel content after violations vs non-violations
    violation_successors = Counter(bg['successor_kernel'] for bg in violations if bg['successor_kernel'])
    non_violation_successors = Counter(bg['successor_kernel'] for bg in non_violations if bg['successor_kernel'])

    total_viol_succ = sum(violation_successors.values())
    total_nonviol_succ = sum(non_violation_successors.values())

    print("\nSuccessor kernel after violations:")
    for k in ['k', 'h', 'e', 'n']:
        viol_pct = 100 * violation_successors.get(k, 0) / total_viol_succ if total_viol_succ > 0 else 0
        nonviol_pct = 100 * non_violation_successors.get(k, 0) / total_nonviol_succ if total_nonviol_succ > 0 else 0
        diff = viol_pct - nonviol_pct
        print(f"  {k}: {viol_pct:.1f}% after violation vs {nonviol_pct:.1f}% normally (diff={diff:+.1f}%)")

    # Is 'e' (stability) more common after violations? (recovery)
    e_after_viol = violation_successors.get('e', 0) / total_viol_succ if total_viol_succ > 0 else 0
    e_after_nonviol = non_violation_successors.get('e', 0) / total_nonviol_succ if total_nonviol_succ > 0 else 0

    if e_after_viol > e_after_nonviol:
        print(f"\n-> 'e' (stability) is MORE common after violations ({100*e_after_viol:.1f}% vs {100*e_after_nonviol:.1f}%)")
        print("   This suggests violations trigger recovery (SUPPORTS hazard interpretation)")
    else:
        print(f"\n-> 'e' (stability) is NOT more common after violations")
        print("   No evidence of recovery pattern (CONTRADICTS hazard interpretation)")

    results['e_after_violation'] = e_after_viol
    results['e_after_non_violation'] = e_after_nonviol

    # 5. Specific violation analysis
    print("\n" + "=" * 40)
    print("5. Specific Violation Analysis")
    print("=" * 40)

    for trans in disfavored_transitions:
        trans_violations = [bg for bg in violations if bg['transition'] == trans]
        print(f"\n{trans} violations ({len(trans_violations)} total):")

        if trans_violations:
            # Most common source words
            source_words = Counter(bg['source'] for bg in trans_violations)
            print(f"  Top source words:")
            for word, count in source_words.most_common(5):
                print(f"    {word}: {count}")

            # Most common target words
            target_words = Counter(bg['target'] for bg in trans_violations)
            print(f"  Top target words:")
            for word, count in target_words.most_common(5):
                print(f"    {word}: {count}")

            # What follows?
            successors = Counter(bg['successor_kernel'] for bg in trans_violations if bg['successor_kernel'])
            print(f"  Successor distribution:")
            for k, count in successors.most_common():
                pct = 100 * count / sum(successors.values())
                print(f"    {k}: {count} ({pct:.1f}%)")

    # 6. Interpretation
    print("\n" + "=" * 60)
    print("INTERPRETATION")
    print("=" * 60)

    hazard_support = 0
    hazard_contradict = 0

    # If hazard: violations should trigger recovery (more e after)
    if e_after_viol > e_after_nonviol + 0.05:
        hazard_support += 1
        print("+ Violations trigger recovery (more e-successors): SUPPORTS HAZARD")
    else:
        hazard_contradict += 1
        print("- No recovery pattern after violations: CONTRADICTS HAZARD")

    # If hazard: violations should be rare and costly
    violation_rate = len(violations) / len(bigrams)
    if violation_rate < 0.1:
        hazard_support += 1
        print("+ Low violation rate (<10%): SUPPORTS HAZARD (rare events)")
    else:
        hazard_contradict += 1
        print(f"- High violation rate ({100*violation_rate:.1f}%): CONTRADICTS HAZARD (common, not exceptional)")

    # If hazard: violations should cluster (specific dangerous contexts)
    if cv > 0.5:
        hazard_support += 1
        print("+ High folio variation in violation rate: SUPPORTS HAZARD (context-dependent)")
    else:
        print("- Low folio variation: Violations evenly distributed (NEUTRAL)")

    print(f"\nHazard interpretation: {hazard_support} support, {hazard_contradict} contradict")

    if hazard_support > hazard_contradict:
        print("\n** VERDICT: Evidence SUPPORTS hazard interpretation **")
        print("   Violations appear to be meaningful events with recovery patterns")
    elif hazard_contradict > hazard_support:
        print("\n** VERDICT: Evidence CONTRADICTS hazard interpretation **")
        print("   Violations appear to be normal variation, not exceptional events")
    else:
        print("\n** VERDICT: Evidence is MIXED **")
        print("   Hazard interpretation neither strongly supported nor refuted")

    results['hazard_support'] = hazard_support
    results['hazard_contradict'] = hazard_contradict

    # Save results
    output_path = Path(__file__).parent.parent / "results" / "t6_violation_context_analysis.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to: {output_path}")

    return results


if __name__ == "__main__":
    main()
