#!/usr/bin/env python3
"""
Test 2: Disfavored Transition Decomposition

Analyze the 17 "forbidden" transitions without assuming hazard interpretation.
For each disfavored pair:
- What kernel characters are involved?
- What is the directional pattern?
- What roles are source and target?
- What MIDDLEs are involved?
- Is the disfavor consistent across contexts?

Goal: Find common thread without assuming hazard semantics.
"""

import json
import sys
from pathlib import Path
from collections import defaultdict, Counter
import numpy as np
from scipy import stats

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "scripts"))
from voynich import Transcript, Morphology

# The 17 disfavored transitions from C109
# These are class-level transitions. We need to identify them in the corpus.
# Based on C109, they cluster into 5 groups:
# - PHASE_ORDERING (7): wrong sequence
# - COMPOSITION_JUMP (4): incompatible composition
# - CONTAINMENT_TIMING (4): timing violation
# - RATE_MISMATCH (1): flow imbalance
# - ENERGY_OVERSHOOT (1): energy too high

def get_kernel_signature(word: str) -> str:
    """Get kernel signature: which kernel chars present."""
    sig = ''
    if 'k' in word:
        sig += 'k'
    if 'h' in word:
        sig += 'h'
    if 'e' in word:
        sig += 'e'
    return sig if sig else 'none'


def get_kernel_counts(word: str) -> dict:
    """Count kernel characters in word."""
    return {
        'k': word.count('k'),
        'h': word.count('h'),
        'e': word.count('e'),
    }


def main():
    print("=" * 60)
    print("Test 2: Disfavored Transition Decomposition")
    print("=" * 60)

    tx = Transcript()
    morph = Morphology()

    # Collect all B tokens
    tokens = []
    for token in tx.currier_b():
        tokens.append({
            'word': token.word,
            'folio': token.folio,
            'line': token.line,
        })

    print(f"\nTotal B tokens: {len(tokens)}")

    # Build bigrams within lines
    line_groups = defaultdict(list)
    for i, t in enumerate(tokens):
        key = (t['folio'], t['line'])
        line_groups[key].append(t)

    bigrams = []
    for key, line_toks in line_groups.items():
        for i in range(len(line_toks) - 1):
            bigrams.append({
                'source': line_toks[i]['word'],
                'target': line_toks[i + 1]['word'],
                'folio': key[0],
                'line': key[1],
            })

    print(f"Total bigrams: {len(bigrams)}")

    # Analyze bigrams by kernel signature transition
    kernel_transitions = defaultdict(list)

    for bg in bigrams:
        src_sig = get_kernel_signature(bg['source'])
        tgt_sig = get_kernel_signature(bg['target'])
        trans = f"{src_sig}->{tgt_sig}"
        kernel_transitions[trans].append(bg)

    # Count transitions
    print("\n" + "=" * 40)
    print("Kernel Signature Transitions")
    print("=" * 40)

    trans_counts = {k: len(v) for k, v in kernel_transitions.items()}
    total_bigrams = len(bigrams)

    # Sort by frequency
    for trans, count in sorted(trans_counts.items(), key=lambda x: -x[1])[:20]:
        pct = 100 * count / total_bigrams
        print(f"  {trans}: {count} ({pct:.2f}%)")

    # Character-level transition matrix
    print("\n" + "=" * 40)
    print("Character-Level Transition Analysis")
    print("=" * 40)

    # For each bigram, analyze character-level flow
    char_transitions = defaultdict(int)

    for bg in bigrams:
        src_chars = set(bg['source'])
        tgt_chars = set(bg['target'])

        for sc in ['k', 'h', 'e']:
            for tc in ['k', 'h', 'e']:
                if sc in src_chars and tc in tgt_chars:
                    char_transitions[f"{sc}->{tc}"] += 1

    # Normalize by source frequency
    src_totals = defaultdict(int)
    for bg in bigrams:
        for c in ['k', 'h', 'e']:
            if c in bg['source']:
                src_totals[c] += 1

    print("\nTransition probabilities (P(target_char | source_char)):")
    for sc in ['k', 'h', 'e']:
        print(f"  From '{sc}' (n={src_totals[sc]}):")
        for tc in ['k', 'h', 'e']:
            trans = f"{sc}->{tc}"
            count = char_transitions[trans]
            prob = count / src_totals[sc] if src_totals[sc] > 0 else 0
            print(f"    -> '{tc}': {count} ({prob:.3f})")

    # Identify disfavored patterns
    print("\n" + "=" * 40)
    print("Identifying Disfavored Patterns")
    print("=" * 40)

    # Calculate expected vs observed for each transition
    # Expected = P(src_has_X) * P(tgt_has_Y) * total_bigrams

    src_probs = {}
    tgt_probs = {}

    for c in ['k', 'h', 'e', 'none']:
        src_count = sum(1 for bg in bigrams if get_kernel_signature(bg['source']) == c or
                        (c != 'none' and c in bg['source']))
        tgt_count = sum(1 for bg in bigrams if get_kernel_signature(bg['target']) == c or
                        (c != 'none' and c in bg['target']))
        src_probs[c] = src_count / len(bigrams)
        tgt_probs[c] = tgt_count / len(bigrams)

    # For character pairs
    char_observed = {}
    char_expected = {}
    char_ratio = {}

    for sc in ['k', 'h', 'e']:
        for tc in ['k', 'h', 'e']:
            trans = f"{sc}->{tc}"
            observed = char_transitions[trans]
            # Expected if independent: P(src has sc) * P(tgt has tc) * total
            src_has = sum(1 for bg in bigrams if sc in bg['source'])
            tgt_has = sum(1 for bg in bigrams if tc in bg['target'])
            expected = (src_has / len(bigrams)) * (tgt_has / len(bigrams)) * len(bigrams)

            char_observed[trans] = observed
            char_expected[trans] = expected
            char_ratio[trans] = observed / expected if expected > 0 else 0

    print("\nObserved/Expected ratios (values < 1.0 are DISFAVORED):")
    for trans in sorted(char_ratio.keys(), key=lambda x: char_ratio[x]):
        ratio = char_ratio[trans]
        obs = char_observed[trans]
        exp = char_expected[trans]
        status = "DISFAVORED" if ratio < 0.5 else "ELEVATED" if ratio > 1.5 else "NEUTRAL"
        print(f"  {trans}: {ratio:.2f}x (obs={obs}, exp={exp:.0f}) [{status}]")

    # Deep dive into h->k (most suppressed per C521)
    print("\n" + "=" * 40)
    print("Deep Dive: h->k Transition")
    print("=" * 40)

    h_to_k_bigrams = [bg for bg in bigrams if 'h' in bg['source'] and 'k' in bg['target']]
    print(f"h->k bigrams found: {len(h_to_k_bigrams)}")

    if h_to_k_bigrams:
        print("\nExamples:")
        for bg in h_to_k_bigrams[:10]:
            print(f"  {bg['source']} -> {bg['target']} ({bg['folio']}:{bg['line']})")

        # What contexts allow h->k?
        h_to_k_folios = Counter(bg['folio'] for bg in h_to_k_bigrams)
        print(f"\nFolios with h->k: {len(h_to_k_folios)}")
        print("Top folios:")
        for folio, count in h_to_k_folios.most_common(5):
            print(f"  {folio}: {count}")

    # Deep dive into e->h and e->k (blocked per C521)
    print("\n" + "=" * 40)
    print("Deep Dive: e->h and e->k Transitions")
    print("=" * 40)

    e_to_h_bigrams = [bg for bg in bigrams if 'e' in bg['source'] and 'h' in bg['target'] and 'e' not in bg['target']]
    e_to_k_bigrams = [bg for bg in bigrams if 'e' in bg['source'] and 'k' in bg['target'] and 'e' not in bg['target']]

    print(f"e->h (pure, no e in target): {len(e_to_h_bigrams)}")
    print(f"e->k (pure, no e in target): {len(e_to_k_bigrams)}")

    # Analyze what makes a transition "disfavored"
    print("\n" + "=" * 40)
    print("ANALYSIS: What Makes Transitions Disfavored?")
    print("=" * 40)

    disfavored = [(t, r) for t, r in char_ratio.items() if r < 0.7]
    elevated = [(t, r) for t, r in char_ratio.items() if r > 1.3]

    print("\nDISFAVORED transitions (ratio < 0.7):")
    for trans, ratio in sorted(disfavored, key=lambda x: x[1]):
        print(f"  {trans}: {ratio:.2f}x")

    print("\nELEVATED transitions (ratio > 1.3):")
    for trans, ratio in sorted(elevated, key=lambda x: -x[1]):
        print(f"  {trans}: {ratio:.2f}x")

    # Pattern analysis
    print("\n" + "=" * 40)
    print("Pattern Analysis")
    print("=" * 40)

    # Check if disfavored = "leaving e" or "entering k from h"
    leaving_e = [t for t in disfavored if t[0].startswith('e->')]
    entering_from_h = [t for t in disfavored if t[0].startswith('h->') and 'e' not in t[0].split('->')[1]]

    print(f"\nDisfavored patterns involving 'leaving e': {len(leaving_e)}")
    for t, r in leaving_e:
        print(f"  {t}: {r:.2f}x")

    print(f"\nDisfavored patterns involving 'h -> non-e': {len(entering_from_h)}")
    for t, r in entering_from_h:
        print(f"  {t}: {r:.2f}x")

    # Interpretation
    print("\n" + "=" * 60)
    print("INTERPRETATION")
    print("=" * 60)

    # Test alternative framings
    print("\nAlternative Framing Test:")

    # Energy flow: k=high, h=mid, e=low
    # If true: k->e should be elevated (energy dissipation)
    #          e->k should be disfavored (energy injection blocked)
    k_to_e_ratio = char_ratio.get('k->e', 0)
    e_to_k_ratio = char_ratio.get('e->k', 0)

    print(f"\n1. ENERGY FLOW interpretation:")
    print(f"   k->e (high->low): {k_to_e_ratio:.2f}x {'FITS' if k_to_e_ratio > 1.0 else 'CONTRADICTS'}")
    print(f"   e->k (low->high): {e_to_k_ratio:.2f}x {'FITS' if e_to_k_ratio < 1.0 else 'CONTRADICTS'}")

    # Sequential: k->h->e is the "correct" order
    # If true: forward transitions elevated, backward disfavored
    k_to_h_ratio = char_ratio.get('k->h', 0)
    h_to_e_ratio = char_ratio.get('h->e', 0)
    h_to_k_ratio = char_ratio.get('h->k', 0)
    e_to_h_ratio = char_ratio.get('e->h', 0)

    print(f"\n2. SEQUENTIAL (k->h->e) interpretation:")
    print(f"   k->h (forward): {k_to_h_ratio:.2f}x")
    print(f"   h->e (forward): {h_to_e_ratio:.2f}x")
    print(f"   h->k (backward): {h_to_k_ratio:.2f}x")
    print(f"   e->h (backward): {e_to_h_ratio:.2f}x")

    forward_elevated = k_to_h_ratio > 1.0 and h_to_e_ratio > 1.0
    backward_suppressed = h_to_k_ratio < 1.0 and e_to_h_ratio < 1.0
    print(f"   Forward elevated: {forward_elevated}")
    print(f"   Backward suppressed: {backward_suppressed}")

    # Hazard: h is danger, e is safety
    # If true: h->e elevated (escape), h->h suppressed (avoid lingering in danger)
    h_to_h_ratio = char_ratio.get('h->h', 0)

    print(f"\n3. HAZARD interpretation:")
    print(f"   h->e (escape to safety): {h_to_e_ratio:.2f}x {'FITS' if h_to_e_ratio > 1.0 else 'CONTRADICTS'}")
    print(f"   h->h (lingering in danger): {h_to_h_ratio:.2f}x {'FITS' if h_to_h_ratio < 1.0 else 'CONTRADICTS'}")
    print(f"   h->k (danger to energy): {h_to_k_ratio:.2f}x {'FITS' if h_to_k_ratio < 1.0 else 'CONTRADICTS'}")

    # Save results
    results = {
        'total_bigrams': len(bigrams),
        'char_transitions': dict(char_transitions),
        'char_observed': char_observed,
        'char_expected': {k: round(v, 1) for k, v in char_expected.items()},
        'char_ratio': {k: round(v, 3) for k, v in char_ratio.items()},
        'h_to_k_count': len(h_to_k_bigrams),
        'e_to_h_count': len(e_to_h_bigrams),
        'e_to_k_count': len(e_to_k_bigrams),
        'disfavored_transitions': [t for t, r in disfavored],
        'elevated_transitions': [t for t, r in elevated],
    }

    output_path = Path(__file__).parent.parent / "results" / "t2_disfavored_transition_decomposition.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to: {output_path}")

    return results


if __name__ == "__main__":
    main()
