#!/usr/bin/env python3
"""
Search for TRUE apparatus candidates.

Revised criteria based on failed s-prefix hypothesis:
1. Line-initial OR line-final (setup OR collection)
2. LOW energy follower rate (< 25% vs 35% baseline)
3. Zero kernel content
4. Stable across sections (apparatus is universal)

NOT: s-prefix tokens (these are energy triggers like daiin)
"""

import sys
from pathlib import Path
from collections import defaultdict, Counter
import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from voynich import Transcript

class_map_path = Path(__file__).parent.parent / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
with open(class_map_path) as f:
    import json
    class_data = json.load(f)
token_to_role = class_data.get('token_to_role', {})

tx = Transcript()

# Build line data
folio_lines = defaultdict(lambda: defaultdict(list))
folio_section = {}

for token in tx.currier_b():
    if '*' in token.word:
        continue
    folio_lines[token.folio][token.line].append(token.word)
    if token.folio not in folio_section:
        folio_section[token.folio] = token.section

# Analyze each token's properties
token_stats = {}

for folio in folio_lines:
    for line in folio_lines[folio]:
        words = folio_lines[folio][line]
        n = len(words)
        if n == 0:
            continue

        for i, word in enumerate(words):
            if word not in token_stats:
                token_stats[word] = {
                    'count': 0,
                    'sections': set(),
                    'initial': 0,
                    'final': 0,
                    'followers': [],
                    'kernel_k': 0,
                    'kernel_h': 0,
                    'kernel_e': 0,
                }

            stats = token_stats[word]
            stats['count'] += 1
            stats['sections'].add(folio_section.get(folio, '?'))
            stats['kernel_k'] += word.count('k')
            stats['kernel_h'] += word.count('h')
            stats['kernel_e'] += word.count('e')

            if i == 0:
                stats['initial'] += 1
            if i == n - 1:
                stats['final'] += 1

            # Follower
            if i + 1 < n:
                stats['followers'].append(words[i + 1])

print("="*70)
print("APPARATUS CANDIDATE SEARCH (REVISED)")
print("="*70)

# Calculate metrics and filter
candidates = []

for word, stats in token_stats.items():
    if stats['count'] < 15:  # Need enough data
        continue

    n = stats['count']
    initial_rate = stats['initial'] / n
    final_rate = stats['final'] / n

    # Kernel per occurrence
    kernel_per_occ = (stats['kernel_k'] + stats['kernel_h'] + stats['kernel_e']) / n

    # Energy follower rate
    if stats['followers']:
        en_followers = sum(1 for f in stats['followers'] if token_to_role.get(f) == 'ENERGY_OPERATOR')
        en_rate = en_followers / len(stats['followers'])
    else:
        en_rate = 0

    # Section spread
    n_sections = len(stats['sections'])

    candidates.append({
        'word': word,
        'count': n,
        'initial_rate': initial_rate,
        'final_rate': final_rate,
        'kernel': kernel_per_occ,
        'en_rate': en_rate,
        'n_sections': n_sections,
        'role': token_to_role.get(word, 'UNKNOWN'),
    })

# Apparatus score: high initial/final + low kernel + low EN + multi-section
for c in candidates:
    positional = max(c['initial_rate'], c['final_rate'])
    low_kernel = 1 - min(c['kernel'], 1)
    low_energy = 1 - c['en_rate']
    spread = c['n_sections'] / 5  # 5 sections

    c['apparatus_score'] = (
        0.3 * positional +
        0.2 * low_kernel +
        0.3 * low_energy +
        0.2 * spread
    )

# Sort by apparatus score
candidates.sort(key=lambda x: -x['apparatus_score'])

print(f"\nTOP APPARATUS CANDIDATES (low-energy, positional, multi-section):")
print(f"\n{'Token':<12} {'Score':<7} {'Count':<7} {'Init%':<8} {'Fin%':<8} {'Kern':<6} {'EN%':<7} {'Sect':<5} {'Role':<15}")
print("-"*90)

for c in candidates[:30]:
    print(f"{c['word']:<12} {c['apparatus_score']:<7.3f} {c['count']:<7} {100*c['initial_rate']:<8.1f} {100*c['final_rate']:<8.1f} {c['kernel']:<6.2f} {100*c['en_rate']:<7.1f} {c['n_sections']:<5} {c['role']:<15}")

# FOCUS: Tokens with <25% energy followers AND positional bias
print(f"\n{'='*70}")
print("BEST APPARATUS CANDIDATES: Low Energy (<25%) + High Position (>25%)")
print("="*70)

best = [c for c in candidates
        if c['en_rate'] < 0.25 and (c['initial_rate'] > 0.25 or c['final_rate'] > 0.25)]
best.sort(key=lambda x: -x['apparatus_score'])

print(f"\n{'Token':<12} {'EN%':<8} {'Init%':<8} {'Fin%':<8} {'Kernel':<8} {'Role':<15}")
print("-"*65)

for c in best[:20]:
    print(f"{c['word']:<12} {100*c['en_rate']:<8.1f} {100*c['initial_rate']:<8.1f} {100*c['final_rate']:<8.1f} {c['kernel']:<8.2f} {c['role']:<15}")

# Summary
print(f"\n{'='*70}")
print("APPARATUS INTERPRETATION")
print("="*70)

print("""
If apparatus tokens exist, they should have:
1. Positional bias (setup at start, collection at end)
2. Low energy followers (not triggering processing)
3. Zero kernel (no process state)
4. Multi-section presence (same equipment used everywhere)

Candidates matching these criteria are listed above.

NOTE: The absence of clear candidates might indicate:
- Apparatus specification is implicit (not encoded in tokens)
- The manuscript is purely operational (no equipment inventory)
- Equipment is encoded differently (illustrations, not text)
""")
