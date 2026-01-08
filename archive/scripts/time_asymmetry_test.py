"""
TIME ASYMMETRY TEST

Core question: Is the grammar CAUSAL or merely RELATIONAL?

We compare:
- H(X | prev 2) = predictability from past context
- H(X | next 2) = predictability from future context

If forward >> backward: grammar encodes causality (time arrow)
If symmetric: abstract constraint system (no time direction)

This is a fundamental property of the notation system.
"""

import csv
from collections import defaultdict, Counter
from pathlib import Path
import numpy as np
from math import log2

BASE = Path(r"C:\git\voynich")
TRANSCRIPTION = BASE / "data" / "transcriptions" / "interlinear_full_words.txt"

def load_b_sequences():
    """Load Currier B token sequences by folio."""
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

def compute_entropy(counts, total):
    """Compute entropy of distribution."""
    entropy = 0
    for count in counts.values():
        if count > 0:
            p = count / total
            entropy -= p * log2(p)
    return entropy

def compute_conditional_entropy_forward(sequences, context_length):
    """Compute H(X | prev context_length tokens)."""
    # Count (context) -> next token
    context_counts = defaultdict(Counter)
    total_per_context = Counter()

    for folio, tokens in sequences.items():
        for i in range(context_length, len(tokens)):
            context = tuple(tokens[i-context_length:i])
            next_token = tokens[i]
            context_counts[context][next_token] += 1
            total_per_context[context] += 1

    # Compute weighted average entropy
    total = sum(total_per_context.values())
    conditional_entropy = 0

    for context, next_counts in context_counts.items():
        context_total = total_per_context[context]
        context_entropy = compute_entropy(next_counts, context_total)
        weight = context_total / total
        conditional_entropy += weight * context_entropy

    return conditional_entropy

def compute_conditional_entropy_backward(sequences, context_length):
    """Compute H(X | next context_length tokens)."""
    # Count (future context) -> prev token
    context_counts = defaultdict(Counter)
    total_per_context = Counter()

    for folio, tokens in sequences.items():
        for i in range(len(tokens) - context_length):
            context = tuple(tokens[i+1:i+1+context_length])
            prev_token = tokens[i]
            context_counts[context][prev_token] += 1
            total_per_context[context] += 1

    # Compute weighted average entropy
    total = sum(total_per_context.values())
    conditional_entropy = 0

    for context, prev_counts in context_counts.items():
        context_total = total_per_context[context]
        context_entropy = compute_entropy(prev_counts, context_total)
        weight = context_total / total
        conditional_entropy += weight * context_entropy

    return conditional_entropy

def analyze_asymmetry():
    """Run full asymmetry analysis."""
    print("="*70)
    print("TIME ASYMMETRY TEST")
    print("="*70)

    sequences = load_b_sequences()
    total_tokens = sum(len(s) for s in sequences.values())
    print(f"\nLoaded {len(sequences)} folios, {total_tokens} tokens")

    # Compute unconditional entropy
    all_tokens = []
    for tokens in sequences.values():
        all_tokens.extend(tokens)

    token_counts = Counter(all_tokens)
    h_unconditional = compute_entropy(token_counts, len(all_tokens))

    print(f"\nUnconditional entropy H(X): {h_unconditional:.3f} bits")

    # Compare forward and backward for different context lengths
    print("\n" + "-"*70)
    print("FORWARD vs BACKWARD PREDICTABILITY")
    print("-"*70)

    print(f"\n{'Context':<15} {'H(X|past)':>12} {'H(X|future)':>12} {'Asymmetry':>12} {'Direction':>12}")
    print("-" * 65)

    results = []

    for ctx_len in [1, 2, 3]:
        h_forward = compute_conditional_entropy_forward(sequences, ctx_len)
        h_backward = compute_conditional_entropy_backward(sequences, ctx_len)

        asymmetry = h_backward - h_forward
        direction = "FORWARD" if asymmetry > 0.1 else ("BACKWARD" if asymmetry < -0.1 else "SYMMETRIC")

        print(f"{ctx_len} token(s)      {h_forward:>12.3f} {h_backward:>12.3f} {asymmetry:>+12.3f} {direction:>12}")

        results.append({
            'context': ctx_len,
            'h_forward': h_forward,
            'h_backward': h_backward,
            'asymmetry': asymmetry
        })

    # Compute reduction percentages
    print("\n" + "-"*70)
    print("PREDICTABILITY REDUCTION FROM UNCONDITIONAL")
    print("-"*70)

    print(f"\n{'Context':<15} {'Past reduction':>15} {'Future reduction':>17}")
    print("-" * 50)

    for r in results:
        past_reduction = 100 * (h_unconditional - r['h_forward']) / h_unconditional
        future_reduction = 100 * (h_unconditional - r['h_backward']) / h_unconditional
        print(f"{r['context']} token(s)      {past_reduction:>14.1f}% {future_reduction:>16.1f}%")

    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)

    # Check if there's consistent asymmetry
    asymmetries = [r['asymmetry'] for r in results]
    mean_asymmetry = np.mean(asymmetries)

    if all(a > 0.05 for a in asymmetries):
        verdict = "FORWARD-CAUSAL"
        explanation = "Past predicts future better than future predicts past"
    elif all(a < -0.05 for a in asymmetries):
        verdict = "BACKWARD-CAUSAL"
        explanation = "Future predicts past better than past predicts future"
    else:
        verdict = "SYMMETRIC"
        explanation = "Past and future are equally predictive"

    print(f"\nVerdict: {verdict}")
    print(f"Explanation: {explanation}")
    print(f"Mean asymmetry: {mean_asymmetry:+.3f} bits")

    if verdict == "FORWARD-CAUSAL":
        print("\n-> The grammar encodes a TIME ARROW")
        print("   Reading direction matters; sequences are causally ordered")
    elif verdict == "SYMMETRIC":
        print("\n-> The grammar is RELATIONALLY CONSTRAINED")
        print("   No inherent time direction; abstract constraint satisfaction")

    # Ratio analysis
    print("\n" + "-"*70)
    print("ASYMMETRY RATIO ANALYSIS")
    print("-"*70)

    for r in results:
        if r['h_forward'] > 0:
            ratio = r['h_backward'] / r['h_forward']
            print(f"{r['context']}-token context: H(past)/H(future) ratio = {ratio:.3f}")

    return results

if __name__ == '__main__':
    analyze_asymmetry()
