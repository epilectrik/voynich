#!/usr/bin/env python3
"""
RI Positional Bias Test: Are INPUT/OUTPUT preferences significant?

Key question: Is daiin's OUTPUT preference (3.3x) significant, or just noise?

If tokens have real positional preferences, that suggests:
- There IS positional semantics in A records
- But the "network" interpretation may be wrong
- It might just be: certain tokens mark beginnings, others mark endings
"""

import sys
import io
from pathlib import Path
from collections import defaultdict, Counter
import json
import numpy as np
from scipy import stats

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, str(Path(__file__).parent))
from voynich import Transcript

tx = Transcript()
GALLOWS = {'k', 't', 'p', 'f'}

print("="*70)
print("RI POSITIONAL BIAS TEST")
print("="*70)

# Build paragraph data
paragraphs = []
current_folio = None
current_para = []
current_line = None
para_idx = 0

for token in tx.currier_a():
    if '*' in token.word:
        continue

    if token.folio != current_folio:
        if current_para:
            paragraphs.append({
                'folio': current_folio,
                'para_idx': para_idx,
                'tokens': [t.word for t in current_para],
                'record_id': f"{current_folio}:{para_idx}"
            })
            para_idx += 1
        current_folio = token.folio
        current_para = [token]
        current_line = token.line
        para_idx = 0
        continue

    if token.line != current_line:
        first_word = token.word
        if first_word and first_word[0] in GALLOWS:
            paragraphs.append({
                'folio': current_folio,
                'para_idx': para_idx,
                'tokens': [t.word for t in current_para],
                'record_id': f"{current_folio}:{para_idx}"
            })
            para_idx += 1
            current_para = [token]
        else:
            current_para.append(token)
        current_line = token.line
    else:
        current_para.append(token)

if current_para:
    paragraphs.append({
        'folio': current_folio,
        'para_idx': para_idx,
        'tokens': [t.word for t in current_para],
        'record_id': f"{current_folio}:{para_idx}"
    })

# Collect positional data
input_tokens = []
output_tokens = []
all_tokens = []

for p in paragraphs:
    tokens = p['tokens']
    all_tokens.extend(tokens)
    if len(tokens) >= 4:
        input_tokens.extend(tokens[:3])
        output_tokens.extend(tokens[-3:])

input_freq = Counter(input_tokens)
output_freq = Counter(output_tokens)
total_freq = Counter(all_tokens)

n_input = len(input_tokens)
n_output = len(output_tokens)
n_total = len(all_tokens)

print(f"\nTotal tokens: {n_total}")
print(f"Input zone tokens: {n_input}")
print(f"Output zone tokens: {n_output}")

# Test each common token for positional bias
print("\n" + "="*70)
print("CHI-SQUARE TEST FOR POSITIONAL BIAS")
print("="*70)

print(f"\n{'Token':<12} {'Total':<8} {'Input':<8} {'Output':<8} {'Exp.IN':<8} {'Exp.OUT':<8} {'Chi2':<8} {'p-value':<10} {'Verdict':<10}")
print("-"*95)

results = []

for token, total_count in total_freq.most_common(30):
    if total_count < 20:  # Need enough data
        continue

    in_count = input_freq.get(token, 0)
    out_count = output_freq.get(token, 0)

    # Expected counts under null (uniform distribution across positions)
    # Proportion of total that is INPUT zone vs OUTPUT zone
    p_input = n_input / n_total
    p_output = n_output / n_total

    exp_input = total_count * p_input
    exp_output = total_count * p_output

    # Chi-square for this token's INPUT vs OUTPUT distribution
    # Observed: [in_count, out_count], Expected: [exp_input, exp_output]
    if exp_input > 0 and exp_output > 0:
        chi2 = ((in_count - exp_input)**2 / exp_input +
                (out_count - exp_output)**2 / exp_output)
        p_value = 1 - stats.chi2.cdf(chi2, df=1)

        if in_count > out_count:
            bias = "INPUT"
        elif out_count > in_count:
            bias = "OUTPUT"
        else:
            bias = "-"

        verdict = f"**{bias}**" if p_value < 0.05 else "-"

        print(f"{token:<12} {total_count:<8} {in_count:<8} {out_count:<8} {exp_input:<8.1f} {exp_output:<8.1f} {chi2:<8.2f} {p_value:<10.4f} {verdict:<10}")

        results.append({
            'token': token,
            'total': total_count,
            'input': in_count,
            'output': out_count,
            'chi2': chi2,
            'p_value': p_value,
            'bias': bias if p_value < 0.05 else 'none'
        })

# Summary
print("\n" + "="*70)
print("SUMMARY")
print("="*70)

sig_output = [r for r in results if r['bias'] == 'OUTPUT']
sig_input = [r for r in results if r['bias'] == 'INPUT']
not_sig = [r for r in results if r['bias'] == 'none']

print(f"\nSignificantly OUTPUT-biased tokens: {len(sig_output)}")
for r in sig_output:
    print(f"  {r['token']}: {r['output']}/{r['input']} (p={r['p_value']:.4f})")

print(f"\nSignificantly INPUT-biased tokens: {len(sig_input)}")
for r in sig_input:
    print(f"  {r['token']}: {r['input']}/{r['output']} (p={r['p_value']:.4f})")

print(f"\nNo significant bias: {len(not_sig)}")

# What does this mean?
print("\n" + "="*70)
print("INTERPRETATION")
print("="*70)

if len(sig_output) > 0 or len(sig_input) > 0:
    print(f"""
FINDING: Tokens DO have significant positional preferences.

OUTPUT-biased tokens ({len(sig_output)}): {[r['token'] for r in sig_output]}
INPUT-biased tokens ({len(sig_input)}): {[r['token'] for r in sig_input]}

This means:
1. A records have POSITIONAL SEMANTICS (start vs end matters)
2. Some tokens preferentially mark BEGINNINGS (input requirements?)
3. Some tokens preferentially mark ENDINGS (output states?)

However, this does NOT prove procedural chaining.
The "network" may be an artifact of:
- Common OUTPUT tokens linking to records that happen to INPUT them
- Not because of actual procedural dependencies
- But because of positional grammar rules

ALTERNATIVE INTERPRETATION:
- daiin/dy/chol = CLOSURE markers (grammatical function: "end of record")
- shol/sho = OPENER markers (grammatical function: "start of record")
- The "chains" are just grammar, not procedure
""")
else:
    print("No significant positional biases found.")

# Check if OUTPUT tokens link to INPUT occurrences of different folios
print("\n" + "="*70)
print("CROSS-FOLIO LINKING TEST")
print("="*70)

# For each OUTPUT-biased token, where do its INPUT occurrences come from?
for r in sig_output[:3]:
    token = r['token']

    # Find records that OUTPUT this token
    output_records = []
    input_records = []

    for p in paragraphs:
        tokens = p['tokens']
        if len(tokens) >= 4:
            if token in tokens[-3:]:
                output_records.append(p['folio'])
            if token in tokens[:3]:
                input_records.append(p['folio'])

    output_folios = set(output_records)
    input_folios = set(input_records)
    shared_folios = output_folios & input_folios

    print(f"\n{token}:")
    print(f"  Output in {len(output_folios)} folios: {sorted(output_folios)[:5]}...")
    print(f"  Input in {len(input_folios)} folios: {sorted(input_folios)[:5]}...")
    print(f"  Shared folios: {len(shared_folios)}")

    # If shared folios are few, links are cross-folio (more interesting)
    if len(output_folios) > 0 and len(input_folios) > 0:
        cross_folio_rate = 1 - len(shared_folios) / max(len(output_folios), len(input_folios))
        print(f"  Cross-folio potential: {cross_folio_rate:.1%}")

# Save results
output = {
    'output_biased': [r['token'] for r in sig_output],
    'input_biased': [r['token'] for r in sig_input],
    'not_significant': [r['token'] for r in not_sig],
    'detailed_results': results
}

output_path = Path(__file__).parent.parent / 'results' / 'ri_positional_bias.json'
with open(output_path, 'w') as f:
    json.dump(output, f, indent=2)

print(f"\nResults saved to {output_path}")
