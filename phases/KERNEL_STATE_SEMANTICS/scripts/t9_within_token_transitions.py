#!/usr/bin/env python3
"""
Test 9: Within-Token Character Transitions

C521 claims directional asymmetry for k, h, e at the CHARACTER LEVEL
(within-token composition), NOT between-token transitions.

This test verifies C521 by measuring character bigrams WITHIN tokens.

Expected from C521:
- e→h: 0.00 (blocked)
- h→k: 0.22 (suppressed)
- e→k: 0.27 (suppressed)
- h→e: 7.00x (elevated)
- k→e: 4.32x (elevated)
"""

import json
import sys
from pathlib import Path
from collections import Counter
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "scripts"))
from voynich import Transcript


def main():
    print("=" * 60)
    print("Test 9: Within-Token Character Transitions")
    print("=" * 60)
    print("\nThis tests C521's claim about WITHIN-TOKEN character bigrams")
    print("(different from between-token transitions tested in T1-T6)")

    tx = Transcript()

    # Collect all B tokens
    tokens = [token.word for token in tx.currier_b()]
    print(f"\nTotal B tokens: {len(tokens)}")

    # Count within-token character bigrams
    bigram_counts = Counter()
    char_counts = Counter()

    for token in tokens:
        for char in token:
            char_counts[char] += 1
        for i in range(len(token) - 1):
            bigram = (token[i], token[i + 1])
            bigram_counts[bigram] += 1

    total_bigrams = sum(bigram_counts.values())
    total_chars = sum(char_counts.values())

    print(f"Total within-token character bigrams: {total_bigrams}")

    # Calculate expected frequency under independence
    expected = {}
    for (c1, c2), obs in bigram_counts.items():
        p1 = char_counts[c1] / total_chars
        p2 = char_counts[c2] / total_chars
        expected[(c1, c2)] = p1 * p2 * total_bigrams

    # Calculate O/E ratios
    ratios = {}
    for (c1, c2), obs in bigram_counts.items():
        exp = expected[(c1, c2)]
        ratios[(c1, c2)] = obs / exp if exp > 0 else 0

    # Focus on kernel character transitions
    print("\n" + "=" * 50)
    print("KERNEL CHARACTER WITHIN-TOKEN TRANSITIONS")
    print("=" * 50)

    kernel_pairs = [
        ('k', 'k'), ('k', 'h'), ('k', 'e'),
        ('h', 'k'), ('h', 'h'), ('h', 'e'),
        ('e', 'k'), ('e', 'h'), ('e', 'e'),
    ]

    print("\n" + "-" * 60)
    print(f"{'Transition':<12} {'Observed':<10} {'Expected':<10} {'Ratio':<10} {'C521 Claim':<15}")
    print("-" * 60)

    c521_claims = {
        ('e', 'h'): ('0.00', 'blocked'),
        ('h', 'k'): ('0.22', 'suppressed'),
        ('e', 'k'): ('0.27', 'suppressed'),
        ('h', 'e'): ('7.00x', 'elevated'),
        ('k', 'e'): ('4.32x', 'elevated'),
        ('k', 'h'): ('1.10x', 'neutral'),
    }

    results = {}
    for pair in kernel_pairs:
        obs = bigram_counts.get(pair, 0)
        exp = expected.get(pair, 0)
        ratio = ratios.get(pair, 0)

        claim = c521_claims.get(pair, ('--', '--'))
        claim_str = f"{claim[0]} ({claim[1]})"

        # Determine status
        if ratio < 0.3:
            status = "SUPPRESSED"
        elif ratio > 3.0:
            status = "ELEVATED"
        elif ratio < 0.7:
            status = "weak-suppress"
        elif ratio > 1.5:
            status = "weak-elevate"
        else:
            status = "neutral"

        print(f"{pair[0]}->{pair[1]:<8} {obs:<10} {exp:<10.1f} {ratio:<10.2f} {claim_str:<15} [{status}]")

        results[f"{pair[0]}->{pair[1]}"] = {
            'observed': obs,
            'expected': round(exp, 1),
            'ratio': round(ratio, 3),
            'c521_claim': claim[0],
        }

    # Compare to C521 claims
    print("\n" + "=" * 50)
    print("C521 VALIDATION")
    print("=" * 50)

    validations = []

    # e->h: should be 0.00 (blocked)
    e_h_ratio = ratios.get(('e', 'h'), 0)
    if e_h_ratio < 0.1:
        validations.append(("e->h blocked", True, f"{e_h_ratio:.2f} < 0.1"))
    else:
        validations.append(("e->h blocked", False, f"{e_h_ratio:.2f} >= 0.1"))

    # h->k: should be 0.22 (suppressed)
    h_k_ratio = ratios.get(('h', 'k'), 0)
    if h_k_ratio < 0.5:
        validations.append(("h->k suppressed", True, f"{h_k_ratio:.2f} < 0.5"))
    else:
        validations.append(("h->k suppressed", False, f"{h_k_ratio:.2f} >= 0.5"))

    # e->k: should be 0.27 (suppressed)
    e_k_ratio = ratios.get(('e', 'k'), 0)
    if e_k_ratio < 0.5:
        validations.append(("e->k suppressed", True, f"{e_k_ratio:.2f} < 0.5"))
    else:
        validations.append(("e->k suppressed", False, f"{e_k_ratio:.2f} >= 0.5"))

    # h->e: should be 7.00x (elevated)
    h_e_ratio = ratios.get(('h', 'e'), 0)
    if h_e_ratio > 3.0:
        validations.append(("h->e elevated", True, f"{h_e_ratio:.2f} > 3.0"))
    else:
        validations.append(("h->e elevated", False, f"{h_e_ratio:.2f} <= 3.0"))

    # k->e: should be 4.32x (elevated)
    k_e_ratio = ratios.get(('k', 'e'), 0)
    if k_e_ratio > 2.0:
        validations.append(("k->e elevated", True, f"{k_e_ratio:.2f} > 2.0"))
    else:
        validations.append(("k->e elevated", False, f"{k_e_ratio:.2f} <= 2.0"))

    print("\nC521 Claim Validation:")
    passed = 0
    for claim, valid, evidence in validations:
        status = "CONFIRMED" if valid else "NOT CONFIRMED"
        print(f"  {claim}: {status} ({evidence})")
        if valid:
            passed += 1

    print(f"\nC521 claims confirmed: {passed}/{len(validations)}")

    # Compare within-token to between-token
    print("\n" + "=" * 50)
    print("WITHIN-TOKEN vs BETWEEN-TOKEN COMPARISON")
    print("=" * 50)

    # Between-token ratios from T2 (approximate)
    between_token_ratios = {
        'e->h': 0.87,
        'h->h': 0.96,
        'h->e': 0.97,
        'k->h': 1.03,
        'k->e': 1.04,
        'e->e': 1.11,
        'h->k': 1.15,
        'k->k': 1.15,
        'e->k': 1.21,
    }

    print("\n" + "-" * 50)
    print(f"{'Transition':<12} {'Within-Token':<15} {'Between-Token':<15} {'Same?'}")
    print("-" * 50)

    for pair in kernel_pairs:
        key = f"{pair[0]}->{pair[1]}"
        within = ratios.get(pair, 0)
        between = between_token_ratios.get(key, 1.0)

        # Are they in same category?
        within_cat = "suppress" if within < 0.7 else ("elevate" if within > 1.5 else "neutral")
        between_cat = "suppress" if between < 0.7 else ("elevate" if between > 1.5 else "neutral")
        same = "YES" if within_cat == between_cat else "NO"

        print(f"{key:<12} {within:<15.2f} {between:<15.2f} {same}")

    # Interpretation
    print("\n" + "=" * 60)
    print("INTERPRETATION")
    print("=" * 60)

    if passed >= 4:
        print("\n** C521 IS CONFIRMED **")
        print("   Within-token character transitions show the directional asymmetry claimed.")
        print("   k, h, e have construction-level constraints (how tokens are built).")
    elif passed >= 2:
        print("\n** C521 IS PARTIALLY CONFIRMED **")
        print("   Some within-token patterns match, others don't.")
    else:
        print("\n** C521 IS NOT CONFIRMED **")
        print("   Within-token patterns don't match C521 claims.")

    print("\n** KEY INSIGHT **")
    print("   C521 (within-token) and our T1-T6 (between-token) measure DIFFERENT things.")
    print("   C522 correctly states these layers are independent.")
    print("   The 'kernel' operates at CONSTRUCTION level, not EXECUTION level.")

    # Save results
    output = {
        'total_bigrams': total_bigrams,
        'kernel_transitions': results,
        'validations': [(c, v, e) for c, v, e in validations],
        'passed': passed,
        'total_claims': len(validations),
    }

    output_path = Path(__file__).parent.parent / "results" / "t9_within_token_transitions.json"
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to: {output_path}")

    return output


if __name__ == "__main__":
    main()
