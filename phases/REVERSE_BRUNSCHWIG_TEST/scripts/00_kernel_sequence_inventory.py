"""
00_kernel_sequence_inventory.py

Test 1: Do actual B lines contain e->h->k sequences matching Brunschwig's procedure order?

From C873: Kernel positional ordering is e (0.404) < h (0.410) < k (0.443)
This represents "verify stability before applying heat" - a safety interlock pattern.

Brunschwig parallel:
- e = Check preparation is stable
- h = Ensure apparatus aligned/sealed
- k = Apply heat (degrees 1-3)

This script inventories actual kernel sequences in B lines to see if this ordering holds.
"""

import json
import pandas as pd
from pathlib import Path
from collections import Counter, defaultdict
import numpy as np

# Paths
results_dir = Path(__file__).parent.parent / "results"
results_dir.mkdir(exist_ok=True)

# Load transcript
df = pd.read_csv('data/voynich_transcript.csv')
df = df[df['transcriber'] == 'H']
df = df[df['language'] == 'B']
df = df[~df['word'].isna()]
df = df[~df['word'].str.contains(r'\*', na=False)]

print("="*70)
print("KERNEL SEQUENCE INVENTORY")
print("="*70)
print(f"Total B tokens: {len(df)}")

# Kernel characters
KERNELS = {'k', 'h', 'e'}

def extract_kernels(word):
    """Extract kernel characters from a word in order."""
    return [c for c in word if c in KERNELS]

def get_kernel_signature(kernels):
    """Get a signature for the kernel sequence."""
    if not kernels:
        return "NONE"
    return ''.join(kernels)

# Analyze by line
line_analysis = []

for (folio, line_num), group in df.groupby(['folio', 'line']):
    words = group['word'].tolist()

    # Extract kernels from each word and track positions
    line_kernels = []
    for i, word in enumerate(words):
        word_kernels = extract_kernels(word)
        for k in word_kernels:
            line_kernels.append({
                'kernel': k,
                'word_pos': i,
                'word': word
            })

    if not line_kernels:
        continue

    # Get kernel sequence
    kernel_seq = [k['kernel'] for k in line_kernels]

    # Analyze ordering - which kernel type appears first on average?
    kernel_positions = defaultdict(list)
    for i, k in enumerate(line_kernels):
        kernel_positions[k['kernel']].append(i)

    mean_positions = {}
    for kernel, positions in kernel_positions.items():
        mean_positions[kernel] = np.mean(positions)

    line_analysis.append({
        'folio': folio,
        'line': line_num,
        'n_words': len(words),
        'n_kernel_tokens': len(line_kernels),
        'kernel_sequence': ''.join(kernel_seq),
        'unique_kernels': set(kernel_seq),
        'has_e': 'e' in kernel_seq,
        'has_h': 'h' in kernel_seq,
        'has_k': 'k' in kernel_seq,
        'mean_positions': mean_positions,
        'section': group['section'].iloc[0] if 'section' in group.columns else 'unknown'
    })

print(f"Lines with kernels: {len(line_analysis)}")

# Analyze kernel ordering
print("\n" + "="*70)
print("KERNEL ORDERING ANALYSIS")
print("="*70)

# For lines with multiple kernel types, check ordering
ordering_counts = Counter()
ordering_details = []

for line in line_analysis:
    mp = line['mean_positions']
    if len(mp) >= 2:
        # Sort kernels by mean position
        sorted_kernels = sorted(mp.keys(), key=lambda x: mp[x])
        ordering = '->'.join(sorted_kernels)
        ordering_counts[ordering] += 1
        ordering_details.append({
            'folio': line['folio'],
            'line': line['line'],
            'ordering': ordering,
            'positions': mp
        })

print("\nKernel ordering distribution (lines with 2+ kernel types):")
total_multi = sum(ordering_counts.values())
for ordering, count in ordering_counts.most_common(20):
    pct = 100 * count / total_multi
    print(f"  {ordering}: {count} ({pct:.1f}%)")

# Check C873 prediction: e < h < k
print("\n" + "="*70)
print("C873 PREDICTION TEST: e < h < k")
print("="*70)

# For lines with all three kernels
all_three = [d for d in ordering_details if set(d['ordering'].replace('->', '')) == {'e', 'h', 'k'}]
print(f"\nLines with all three kernels (e, h, k): {len(all_three)}")

if all_three:
    ehk_orderings = Counter(d['ordering'] for d in all_three)
    print("\nOrdering distribution:")
    for ordering, count in ehk_orderings.most_common():
        pct = 100 * count / len(all_three)
        matches_c873 = ordering == 'e->h->k'
        marker = " <-- C873 prediction" if matches_c873 else ""
        print(f"  {ordering}: {count} ({pct:.1f}%){marker}")

# Analyze by section
print("\n" + "="*70)
print("KERNEL PATTERNS BY SECTION")
print("="*70)

section_patterns = defaultdict(lambda: defaultdict(int))
for line in line_analysis:
    section = line.get('section', 'unknown')
    for k in line['unique_kernels']:
        section_patterns[section][k] += 1

for section in sorted(section_patterns.keys()):
    counts = section_patterns[section]
    total = sum(counts.values())
    print(f"\n{section}:")
    for k in ['e', 'h', 'k']:
        if k in counts:
            pct = 100 * counts[k] / total
            print(f"  {k}: {counts[k]} ({pct:.1f}%)")

# Analyze common kernel combinations
print("\n" + "="*70)
print("COMMON KERNEL COMBINATIONS")
print("="*70)

combo_counts = Counter()
for line in line_analysis:
    combo = frozenset(line['unique_kernels'])
    combo_counts[combo] += 1

print("\nKernel combination frequency:")
for combo, count in combo_counts.most_common(10):
    pct = 100 * count / len(line_analysis)
    combo_str = '+'.join(sorted(combo)) if combo else 'none'
    print(f"  {combo_str}: {count} ({pct:.1f}%)")

# Check if e typically precedes k (the key Brunschwig prediction)
print("\n" + "="*70)
print("BRUNSCHWIG SAFETY INTERLOCK TEST: Does e precede k?")
print("="*70)

e_before_k = 0
k_before_e = 0
for line in line_analysis:
    mp = line['mean_positions']
    if 'e' in mp and 'k' in mp:
        if mp['e'] < mp['k']:
            e_before_k += 1
        else:
            k_before_e += 1

total_ek = e_before_k + k_before_e
if total_ek > 0:
    print(f"\nLines with both e and k: {total_ek}")
    print(f"  e before k: {e_before_k} ({100*e_before_k/total_ek:.1f}%)")
    print(f"  k before e: {k_before_e} ({100*k_before_e/total_ek:.1f}%)")

    if e_before_k > k_before_e:
        print("\n  RESULT: e typically precedes k (matches Brunschwig safety interlock)")
    else:
        print("\n  RESULT: k typically precedes e (does NOT match Brunschwig)")

# Save results
results = {
    'total_b_tokens': len(df),
    'lines_with_kernels': len(line_analysis),
    'ordering_distribution': dict(ordering_counts.most_common()),
    'lines_with_all_three': len(all_three),
    'ehk_orderings': dict(Counter(d['ordering'] for d in all_three)) if all_three else {},
    'e_before_k_count': e_before_k,
    'k_before_e_count': k_before_e,
    'e_before_k_rate': e_before_k / total_ek if total_ek > 0 else None,
    'section_patterns': {s: dict(c) for s, c in section_patterns.items()},
    'combo_counts': {'+'.join(sorted(c)): n for c, n in combo_counts.most_common()},
    'c873_prediction': 'e->h->k',
    'brunschwig_interpretation': 'verify stability (e) -> align apparatus (h) -> apply heat (k)'
}

output_path = results_dir / "kernel_sequences.json"
with open(output_path, 'w') as f:
    json.dump(results, f, indent=2)
print(f"\nSaved to {output_path}")
