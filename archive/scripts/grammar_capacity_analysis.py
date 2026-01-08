"""
GRAMMAR CAPACITY ANALYSIS — "MISSING TRANSITIONS"

Core question: Is the grammar defined by CONSTRAINTS or by HABIT?

We have:
- 17 forbidden transitions (hard constraint, 0 occurrences)
- 8 suppressed transitions (soft constraint, <0.5x expected)
- Many enriched transitions (preference)

But what about transitions that:
- Have ZERO occurrences
- Are NOT in the forbidden list?

These are "MISSING" — either:
- Hidden constraints we haven't documented
- Or just statistically absent (low expected frequency)

This probe audits the full transition space.
"""

import csv
import json
from collections import defaultdict, Counter
from pathlib import Path
import numpy as np

BASE = Path(r"C:\git\voynich")
TRANSCRIPTION = BASE / "data" / "transcriptions" / "interlinear_full_words.txt"
GRAMMAR_FILE = BASE / "results" / "canonical_grammar.json"

def load_grammar_classes():
    """Load the 49 grammar classes and their tokens."""
    with open(GRAMMAR_FILE, 'r', encoding='utf-8') as f:
        grammar = json.load(f)

    # Build token -> class mapping
    # Format: {"terminals": {"count": N, "list": [{"id": X, "symbol": "...", "role": "..."}]}}
    token_to_class = {}
    class_tokens = defaultdict(set)

    terminals = grammar.get('terminals', {}).get('list', [])
    for term in terminals:
        symbol = term.get('symbol')
        role = term.get('role')
        if symbol and role:
            token_to_class[symbol] = role
            class_tokens[role].add(symbol)

    return token_to_class, class_tokens, list(class_tokens.keys())

def load_b_sequences():
    """Load Currier B token sequences."""
    sequences = defaultdict(list)

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
            sequences[folio].append(token)

    return sequences

def analyze_grammar_capacity():
    """Analyze the full transition space."""
    print("="*70)
    print("GRAMMAR CAPACITY ANALYSIS")
    print("="*70)

    token_to_class, class_tokens, class_names = load_grammar_classes()
    sequences = load_b_sequences()

    n_classes = len(class_names)
    print(f"\nGrammar classes: {n_classes}")
    print(f"Theoretical transitions: {n_classes * n_classes} ({n_classes}x{n_classes})")

    # Build class-level transition counts
    class_transitions = Counter()
    class_unigrams = Counter()
    total_transitions = 0

    unclassified_tokens = Counter()

    for folio, tokens in sequences.items():
        for i, token in enumerate(tokens):
            cls = token_to_class.get(token)
            if cls:
                class_unigrams[cls] += 1
            else:
                unclassified_tokens[token] += 1

            if i > 0:
                prev_token = tokens[i-1]
                prev_cls = token_to_class.get(prev_token)
                curr_cls = token_to_class.get(token)

                if prev_cls and curr_cls:
                    class_transitions[(prev_cls, curr_cls)] += 1
                    total_transitions += 1

    print(f"\nTotal classified transitions: {total_transitions}")
    print(f"Unique class transitions observed: {len(class_transitions)}")
    print(f"Unclassified tokens: {len(unclassified_tokens)} types, {sum(unclassified_tokens.values())} occurrences")

    # Categorize all possible transitions
    print("\n" + "-"*70)
    print("TRANSITION SPACE ANALYSIS")
    print("-"*70)

    observed = set(class_transitions.keys())

    # Load forbidden transitions (if available)
    # For now, we'll identify them as zero-count with high expected

    # Compute expected frequencies
    total_unigrams = sum(class_unigrams.values())

    zero_count = []
    low_count = []  # 1-2 occurrences

    for c1 in class_names:
        for c2 in class_names:
            pair = (c1, c2)
            count = class_transitions.get(pair, 0)

            # Expected under independence
            p1 = class_unigrams.get(c1, 0) / total_unigrams if total_unigrams > 0 else 0
            p2 = class_unigrams.get(c2, 0) / total_unigrams if total_unigrams > 0 else 0
            expected = p1 * p2 * total_transitions

            if count == 0:
                zero_count.append({
                    'pair': pair,
                    'expected': expected,
                    'c1_freq': class_unigrams.get(c1, 0),
                    'c2_freq': class_unigrams.get(c2, 0)
                })
            elif count <= 2:
                low_count.append({
                    'pair': pair,
                    'count': count,
                    'expected': expected
                })

    print(f"\nTransition space breakdown:")
    print(f"  Total possible: {n_classes * n_classes}")
    print(f"  Observed (count > 0): {len(observed)}")
    print(f"  Zero-count: {len(zero_count)}")
    print(f"  Low-count (1-2): {len(low_count)}")

    # Analyze zero-count transitions
    print("\n" + "-"*70)
    print("ZERO-COUNT TRANSITION ANALYSIS")
    print("-"*70)

    # Categorize by expected frequency
    high_expected_zero = [z for z in zero_count if z['expected'] >= 5]
    medium_expected_zero = [z for z in zero_count if 1 <= z['expected'] < 5]
    low_expected_zero = [z for z in zero_count if z['expected'] < 1]

    print(f"\nZero-count transitions by expected frequency:")
    print(f"  High expected (>=5): {len(high_expected_zero)} <- LIKELY FORBIDDEN")
    print(f"  Medium expected (1-5): {len(medium_expected_zero)} <- POSSIBLY FORBIDDEN")
    print(f"  Low expected (<1): {len(low_expected_zero)} <- statistically absent")

    if high_expected_zero:
        print(f"\nHIGH-EXPECTED ZERO-COUNT (likely hidden constraints):")
        print(f"{'Class 1':<20} {'Class 2':<20} {'Expected':>10} {'C1 freq':>10} {'C2 freq':>10}")
        print("-" * 75)
        for z in sorted(high_expected_zero, key=lambda x: -x['expected'])[:30]:
            c1, c2 = z['pair']
            print(f"{c1:<20} {c2:<20} {z['expected']:>10.1f} {z['c1_freq']:>10} {z['c2_freq']:>10}")

    if medium_expected_zero:
        print(f"\nMEDIUM-EXPECTED ZERO-COUNT (possibly forbidden):")
        print(f"{'Class 1':<20} {'Class 2':<20} {'Expected':>10}")
        print("-" * 55)
        for z in sorted(medium_expected_zero, key=lambda x: -x['expected'])[:20]:
            c1, c2 = z['pair']
            print(f"{c1:<20} {c2:<20} {z['expected']:>10.2f}")

    # Check for systematic patterns
    print("\n" + "-"*70)
    print("SYSTEMATIC PATTERN ANALYSIS")
    print("-"*70)

    # Which classes have many zero-outgoing?
    zero_outgoing = defaultdict(int)
    zero_incoming = defaultdict(int)

    for z in zero_count:
        c1, c2 = z['pair']
        zero_outgoing[c1] += 1
        zero_incoming[c2] += 1

    print(f"\nClasses with most zero-outgoing transitions:")
    for cls, count in sorted(zero_outgoing.items(), key=lambda x: -x[1])[:10]:
        pct = 100 * count / n_classes
        print(f"  {cls}: {count}/{n_classes} ({pct:.1f}%)")

    print(f"\nClasses with most zero-incoming transitions:")
    for cls, count in sorted(zero_incoming.items(), key=lambda x: -x[1])[:10]:
        pct = 100 * count / n_classes
        print(f"  {cls}: {count}/{n_classes} ({pct:.1f}%)")

    # Self-transitions
    print("\n" + "-"*70)
    print("SELF-TRANSITION ANALYSIS")
    print("-"*70)

    self_trans_zero = [z for z in zero_count if z['pair'][0] == z['pair'][1]]
    self_trans_observed = [(c, class_transitions.get((c, c), 0))
                           for c in class_names if class_transitions.get((c, c), 0) > 0]

    print(f"\nSelf-transitions:")
    print(f"  Zero-count: {len(self_trans_zero)}")
    print(f"  Observed: {len(self_trans_observed)}")

    if self_trans_zero:
        print(f"\nClasses with NO self-transition:")
        for z in sorted(self_trans_zero, key=lambda x: -x['expected'])[:15]:
            c = z['pair'][0]
            print(f"  {c} (expected: {z['expected']:.2f}, freq: {z['c1_freq']})")

    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)

    coverage = len(observed) / (n_classes * n_classes) * 100
    print(f"\nGrammar coverage: {coverage:.1f}% of theoretical space")
    print(f"Observed transitions: {len(observed)}")
    print(f"Zero-count transitions: {len(zero_count)}")
    print(f"  - High-expected (likely forbidden): {len(high_expected_zero)}")
    print(f"  - Medium-expected (possibly forbidden): {len(medium_expected_zero)}")
    print(f"  - Low-expected (statistical): {len(low_expected_zero)}")

    if len(high_expected_zero) > 17:
        print(f"\n*** FINDING: {len(high_expected_zero)} high-expected zero-count transitions")
        print(f"    vs 17 documented forbidden transitions")
        print(f"    -> HIDDEN CONSTRAINTS likely exist")
    elif len(high_expected_zero) <= 17:
        print(f"\n*** FINDING: Only {len(high_expected_zero)} high-expected zero-count transitions")
        print(f"    -> Grammar is PERMISSIVE, preferences dominate over constraints")

    return {
        'n_classes': n_classes,
        'observed': len(observed),
        'zero_count': len(zero_count),
        'high_expected_zero': len(high_expected_zero),
        'coverage_pct': coverage
    }

if __name__ == '__main__':
    analyze_grammar_capacity()
