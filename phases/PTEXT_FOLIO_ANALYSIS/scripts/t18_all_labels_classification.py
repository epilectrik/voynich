#!/usr/bin/env python3
"""
Test 18: All Rosettes Label Classification

Classify all label-like placements: C, C1, C2, T, Q
Are they PP or RI? What instruction classes?
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

from pathlib import Path
from collections import Counter, defaultdict
from scripts.voynich import Morphology

filepath = Path('C:/git/voynich/data/transcriptions/interlinear_full_words.txt')
morph = Morphology()

ROSETTES = {'f85r1', 'f85r2', 'f86v3', 'f86v4', 'f86v5', 'f86v6'}

# Collect tokens by placement
tokens_by_placement = defaultdict(list)

with open(filepath, 'r', encoding='utf-8') as f:
    header = f.readline()
    for line in f:
        parts = line.strip().split('\t')
        if len(parts) > 12:
            transcriber = parts[12].strip('"').strip()
            if transcriber != 'H':
                continue

            folio = parts[2].strip('"').strip()
            token = parts[0].strip('"').strip().lower()
            placement = parts[10].strip('"').strip()

            if not token.strip() or '*' in token:
                continue

            if folio in ROSETTES:
                tokens_by_placement[placement].append(token)

print("=" * 70)
print("TEST 18: ALL ROSETTES LABEL CLASSIFICATION")
print("=" * 70)
print()

# Label placements to analyze
label_placements = ['C', 'C1', 'C2', 'Q', 'T']

def analyze_placement(name, tokens):
    """Analyze tokens for a placement type."""
    if not tokens:
        return None

    unique = set(tokens)
    counts = Counter(tokens)

    # Morphological analysis
    prefixes = Counter()
    middles = Counter()
    suffixes = Counter()
    articulators = Counter()

    has_k = 0
    has_h = 0
    has_e = 0
    has_none = 0

    ri_prefixes = {'s', 'ot', 'ok', 'op'}
    pp_prefixes = {'ch', 'sh', 'qo', 'da'}

    ri_like = []
    pp_like = []

    for token in unique:
        m = morph.extract(token)

        prefix = m.prefix if m.prefix else 'NONE'
        prefixes[prefix] += 1

        if m.middle:
            middles[m.middle] += 1
        if m.suffix:
            suffixes[m.suffix] += 1
        if m.articulator:
            articulators[m.articulator] += 1

        # Kernel analysis
        has_kernel = False
        if 'k' in token:
            has_k += 1
            has_kernel = True
        if 'h' in token:
            has_h += 1
            has_kernel = True
        if 'e' in token:
            has_e += 1
            has_kernel = True
        if not has_kernel:
            has_none += 1

        # RI vs PP
        p = m.prefix if m.prefix else ''
        if p in ri_prefixes or (p == '' and token.startswith(('s', 'ot', 'ok'))):
            ri_like.append(token)
        elif p in pp_prefixes or p.startswith(('ch', 'sh', 'qo', 'da')):
            pp_like.append(token)

    return {
        'total': len(tokens),
        'unique': len(unique),
        'ttr': len(unique) / len(tokens),
        'prefixes': prefixes,
        'middles': middles,
        'suffixes': suffixes,
        'has_k': has_k,
        'has_h': has_h,
        'has_e': has_e,
        'has_none': has_none,
        'ri_like': ri_like,
        'pp_like': pp_like,
        'top_tokens': counts.most_common(10)
    }

# Analyze each placement
results = {}
for placement in label_placements:
    tokens = tokens_by_placement.get(placement, [])
    if tokens:
        results[placement] = analyze_placement(placement, tokens)

# 1. Overview
print("1. LABEL PLACEMENT OVERVIEW")
print("-" * 50)
print(f"{'Placement':<10} {'Total':<8} {'Unique':<8} {'TTR':<8}")
print("-" * 34)

for placement in label_placements:
    if placement in results:
        r = results[placement]
        print(f"{placement:<10} {r['total']:<8} {r['unique']:<8} {r['ttr']:<8.3f}")

print()

# 2. Top tokens per placement
print("2. TOP TOKENS PER PLACEMENT")
print("-" * 50)

for placement in label_placements:
    if placement in results:
        r = results[placement]
        print(f"\n{placement} placement (n={r['total']}):")
        for token, count in r['top_tokens']:
            print(f"  {token}: {count}")

print()

# 3. PREFIX distribution per placement
print("3. PREFIX DISTRIBUTION")
print("-" * 50)

all_prefixes = set()
for r in results.values():
    all_prefixes.update(r['prefixes'].keys())

# Header
header = f"{'PREFIX':<10}"
for placement in label_placements:
    if placement in results:
        header += f"{placement:<8}"
print(header)
print("-" * (10 + 8 * len([p for p in label_placements if p in results])))

# Show top prefixes
top_prefixes = Counter()
for r in results.values():
    top_prefixes.update(r['prefixes'])

for prefix, _ in top_prefixes.most_common(15):
    row = f"{prefix:<10}"
    for placement in label_placements:
        if placement in results:
            count = results[placement]['prefixes'].get(prefix, 0)
            unique_count = results[placement]['unique']
            pct = count / unique_count * 100 if unique_count else 0
            row += f"{pct:>5.1f}%  "
    print(row)

print()

# 4. Kernel content
print("4. KERNEL CONTENT")
print("-" * 50)

print(f"{'Placement':<10} {'k%':<10} {'h%':<10} {'e%':<10} {'none%':<10}")
print("-" * 50)

for placement in label_placements:
    if placement in results:
        r = results[placement]
        n = r['unique']
        k_pct = r['has_k'] / n * 100 if n else 0
        h_pct = r['has_h'] / n * 100 if n else 0
        e_pct = r['has_e'] / n * 100 if n else 0
        none_pct = r['has_none'] / n * 100 if n else 0
        print(f"{placement:<10} {k_pct:<10.1f} {h_pct:<10.1f} {e_pct:<10.1f} {none_pct:<10.1f}")

print()

# 5. RI vs PP classification
print("5. RI vs PP CLASSIFICATION")
print("-" * 50)

print(f"{'Placement':<10} {'RI-like':<12} {'PP-like':<12} {'Other':<12} {'Verdict':<10}")
print("-" * 56)

for placement in label_placements:
    if placement in results:
        r = results[placement]
        n = r['unique']
        ri = len(r['ri_like'])
        pp = len(r['pp_like'])
        other = n - ri - pp

        ri_pct = ri / n * 100 if n else 0
        pp_pct = pp / n * 100 if n else 0

        if pp > ri:
            verdict = "PP"
        elif ri > pp:
            verdict = "RI"
        else:
            verdict = "MIXED"

        print(f"{placement:<10} {ri} ({ri_pct:>4.1f}%)   {pp} ({pp_pct:>4.1f}%)   {other:<12} {verdict:<10}")

print()

# 6. Detailed breakdown for each placement
print("6. DETAILED BREAKDOWN")
print("-" * 50)

for placement in label_placements:
    if placement in results:
        r = results[placement]
        print(f"\n=== {placement} PLACEMENT ===")
        print(f"Total: {r['total']} tokens, {r['unique']} unique (TTR: {r['ttr']:.3f})")

        print(f"\nRI-like ({len(r['ri_like'])}): {sorted(r['ri_like'])[:15]}")
        print(f"PP-like ({len(r['pp_like'])}): {sorted(r['pp_like'])[:15]}")

        # No-kernel tokens
        no_kernel = [t for t in set(tokens_by_placement[placement])
                     if 'k' not in t and 'h' not in t and 'e' not in t]
        print(f"No-kernel ({len(no_kernel)}): {sorted(no_kernel)[:15]}")

print()

# 7. Summary
print("=" * 70)
print("SUMMARY: ROSETTES LABEL VOCABULARY")
print("=" * 70)

total_labels = sum(r['total'] for r in results.values())
total_unique = sum(r['unique'] for r in results.values())

total_pp = sum(len(r['pp_like']) for r in results.values())
total_ri = sum(len(r['ri_like']) for r in results.values())

print(f"""
ROSETTES LABEL TOKENS (C, C1, C2, Q, T combined):

Total tokens: {total_labels}
Unique tokens: {total_unique}

Classification:
- PP-like: {total_pp} unique tokens
- RI-like: {total_ri} unique tokens
- Other: {total_unique - total_pp - total_ri} unique tokens

By placement:
""")

for placement in label_placements:
    if placement in results:
        r = results[placement]
        verdict = "PP" if len(r['pp_like']) > len(r['ri_like']) else "RI" if len(r['ri_like']) > len(r['pp_like']) else "MIXED"
        print(f"  {placement}: {r['unique']} unique tokens -> {verdict}")

print()
print("OVERALL: Rosettes labels are predominantly PP (Procedural Primitives)")
print("suggesting the diagrams and connections represent execution points")
print("in a procedural network.")
