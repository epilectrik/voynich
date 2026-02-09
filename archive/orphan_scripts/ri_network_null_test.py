#!/usr/bin/env python3
"""
RI Network Null Test: Is the procedural network just a frequency artifact?

The user points out: daiin is common everywhere in Currier A.
If common tokens just happen to appear in both INPUT and OUTPUT positions,
the "network" is meaningless.

Null hypothesis: The observed network structure is what we'd expect
from random token placement given observed frequencies.

Test: Shuffle INPUT/OUTPUT assignments and compare network properties.
"""

import sys
import io
from pathlib import Path
from collections import defaultdict, Counter
import json
import numpy as np
from random import shuffle, seed

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, str(Path(__file__).parent))
from voynich import Transcript

tx = Transcript()
GALLOWS = {'k', 't', 'p', 'f'}

print("="*70)
print("RI NETWORK NULL TEST: Is this just frequency artifact?")
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

# First: How common IS daiin?
print("\n" + "="*70)
print("TOKEN FREQUENCY CHECK")
print("="*70)

all_tokens = []
for p in paragraphs:
    all_tokens.extend(p['tokens'])

token_freq = Counter(all_tokens)
total_tokens = len(all_tokens)

print(f"\nTotal tokens in A paragraphs: {total_tokens}")
print(f"\nTop 10 most common tokens:")
for token, count in token_freq.most_common(10):
    pct = 100 * count / total_tokens
    print(f"  {token}: {count} ({pct:.1f}%)")

# How often does daiin appear in INPUT vs OUTPUT positions?
print("\n" + "="*70)
print("POSITIONAL ANALYSIS: INPUT vs OUTPUT")
print("="*70)

input_tokens = []
output_tokens = []
middle_tokens = []

for p in paragraphs:
    tokens = p['tokens']
    if len(tokens) >= 4:
        input_tokens.extend(tokens[:3])
        output_tokens.extend(tokens[-3:])
        if len(tokens) > 6:
            middle_tokens.extend(tokens[3:-3])

input_freq = Counter(input_tokens)
output_freq = Counter(output_tokens)
middle_freq = Counter(middle_tokens)

print(f"\nTokens in INPUT position (first 3): {len(input_tokens)}")
print(f"Tokens in OUTPUT position (last 3): {len(output_tokens)}")
print(f"Tokens in MIDDLE position: {len(middle_tokens)}")

# Compare daiin's positional distribution
print(f"\n{'Token':<12} {'INPUT %':<12} {'OUTPUT %':<12} {'MIDDLE %':<12} {'Ratio OUT/IN':<12}")
print("-"*60)

for token in ['daiin', 'chor', 'chol', 'shol', 'dy', 'cheor', 'cthor', 'ol']:
    in_pct = 100 * input_freq.get(token, 0) / len(input_tokens) if input_tokens else 0
    out_pct = 100 * output_freq.get(token, 0) / len(output_tokens) if output_tokens else 0
    mid_pct = 100 * middle_freq.get(token, 0) / len(middle_tokens) if middle_tokens else 0
    ratio = output_freq.get(token, 0) / input_freq.get(token, 1)
    print(f"{token:<12} {in_pct:<12.2f} {out_pct:<12.2f} {mid_pct:<12.2f} {ratio:<12.2f}")

# Now the key test: NULL MODEL
print("\n" + "="*70)
print("NULL MODEL TEST")
print("="*70)

def compute_network_stats(paragraphs):
    """Compute network statistics from paragraph data."""
    output_to_records = defaultdict(list)
    input_to_records = defaultdict(list)

    for para in paragraphs:
        tokens = para['tokens']
        if len(tokens) < 4:
            continue
        record_id = para['record_id']

        for token in tokens[:3]:
            input_to_records[token].append(record_id)
        for token in tokens[-3:]:
            output_to_records[token].append(record_id)

    # Count linking tokens and edges
    linking_tokens = set(output_to_records.keys()) & set(input_to_records.keys())

    edges = 0
    for token in linking_tokens:
        sources = len(output_to_records[token])
        targets = len(input_to_records[token])
        edges += sources * targets  # Exclude self-loops approximately

    return {
        'linking_tokens': len(linking_tokens),
        'edges': edges
    }

# Observed stats
observed = compute_network_stats(paragraphs)
print(f"\nOBSERVED:")
print(f"  Linking tokens: {observed['linking_tokens']}")
print(f"  Edges: {observed['edges']}")

# Null model: shuffle token assignments within each position class
# This preserves: (1) paragraph structure, (2) position frequencies
# But breaks: any meaningful INPUT→OUTPUT correspondence

print(f"\nRunning null model (1000 shuffles)...")

null_linking = []
null_edges = []

seed(42)
for i in range(1000):
    # Shuffle: for each paragraph, independently shuffle INPUT and OUTPUT tokens
    shuffled_paras = []

    # Collect all input and output token lists
    all_inputs = [p['tokens'][:3] for p in paragraphs if len(p['tokens']) >= 4]
    all_outputs = [p['tokens'][-3:] for p in paragraphs if len(p['tokens']) >= 4]

    # Shuffle the assignments
    shuffle(all_inputs)
    shuffle(all_outputs)

    # Rebuild paragraphs with shuffled IO
    idx = 0
    for p in paragraphs:
        if len(p['tokens']) >= 4:
            new_para = {
                'record_id': p['record_id'],
                'tokens': all_inputs[idx] + p['tokens'][3:-3] + all_outputs[idx]
            }
            shuffled_paras.append(new_para)
            idx += 1

    stats = compute_network_stats(shuffled_paras)
    null_linking.append(stats['linking_tokens'])
    null_edges.append(stats['edges'])

null_linking = np.array(null_linking)
null_edges = np.array(null_edges)

print(f"\nNULL MODEL DISTRIBUTION:")
print(f"  Linking tokens: mean={np.mean(null_linking):.1f}, std={np.std(null_linking):.1f}")
print(f"  Edges: mean={np.mean(null_edges):.1f}, std={np.std(null_edges):.1f}")

# Z-scores
z_linking = (observed['linking_tokens'] - np.mean(null_linking)) / np.std(null_linking)
z_edges = (observed['edges'] - np.mean(null_edges)) / np.std(null_edges)

print(f"\nZ-SCORES (observed vs null):")
print(f"  Linking tokens: z = {z_linking:.2f}")
print(f"  Edges: z = {z_edges:.2f}")

# P-values (two-tailed)
p_linking = 2 * min(np.mean(null_linking >= observed['linking_tokens']),
                    np.mean(null_linking <= observed['linking_tokens']))
p_edges = 2 * min(np.mean(null_edges >= observed['edges']),
                  np.mean(null_edges <= observed['edges']))

print(f"\nP-VALUES:")
print(f"  Linking tokens: p = {p_linking:.4f}")
print(f"  Edges: p = {p_edges:.4f}")

# Interpretation
print("\n" + "="*70)
print("INTERPRETATION")
print("="*70)

if abs(z_linking) < 2 and abs(z_edges) < 2:
    print("""
RESULT: Network is CONSISTENT WITH NULL MODEL

The observed network structure is what we'd expect from random
token placement given the frequency distribution.

The "procedural network" is likely a FREQUENCY ARTIFACT:
- Common tokens (daiin, chol) appear in both positions by chance
- This creates apparent connections that have no procedural meaning
- The network structure tells us nothing beyond token frequency

IMPLICATION: C898 may need to be REVISED or RETRACTED.
""")
else:
    print(f"""
RESULT: Network DIFFERS from null model

Observed structure is {'MORE' if z_edges > 0 else 'LESS'} connected than expected.
Z-score for edges: {z_edges:.2f}

This suggests the INPUT→OUTPUT correspondence is NOT just frequency.
There may be real procedural structure, but we need to understand what.
""")

# Additional check: Are specific tokens more positionally biased?
print("\n" + "="*70)
print("POSITIONAL BIAS CHECK")
print("="*70)

print("\nTokens with strong INPUT vs OUTPUT bias:")
print(f"{'Token':<15} {'IN count':<10} {'OUT count':<10} {'Bias':<15}")
print("-"*50)

biased_tokens = []
for token in set(input_freq.keys()) | set(output_freq.keys()):
    in_c = input_freq.get(token, 0)
    out_c = output_freq.get(token, 0)
    if in_c + out_c >= 10:  # Only tokens with enough data
        if in_c > 0 and out_c > 0:
            ratio = out_c / in_c
            if ratio > 2 or ratio < 0.5:
                biased_tokens.append((token, in_c, out_c, ratio))

biased_tokens.sort(key=lambda x: -abs(np.log(x[3])))

for token, in_c, out_c, ratio in biased_tokens[:15]:
    bias = "OUTPUT" if ratio > 1 else "INPUT"
    print(f"{token:<15} {in_c:<10} {out_c:<10} {ratio:.2f}x {bias}")

print("""
If tokens have strong positional bias (appear mostly in INPUT or OUTPUT),
that suggests positional semantics, not just frequency.
""")

# Save results
output = {
    'observed_linking_tokens': observed['linking_tokens'],
    'observed_edges': observed['edges'],
    'null_mean_linking': float(np.mean(null_linking)),
    'null_std_linking': float(np.std(null_linking)),
    'null_mean_edges': float(np.mean(null_edges)),
    'null_std_edges': float(np.std(null_edges)),
    'z_linking': float(z_linking),
    'z_edges': float(z_edges),
    'p_linking': float(p_linking),
    'p_edges': float(p_edges)
}

output_path = Path(__file__).parent.parent / 'results' / 'ri_network_null_test.json'
with open(output_path, 'w') as f:
    json.dump(output, f, indent=2)

print(f"\nResults saved to {output_path}")
