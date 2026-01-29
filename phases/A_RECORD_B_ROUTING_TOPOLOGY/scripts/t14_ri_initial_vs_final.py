"""
T14: Initial vs Final RI Comparison

RI shows bimodal distribution: 25% INITIAL, 31% FINAL
Are these the same tokens or different types?

Compare:
1. Token identity - same words or different?
2. Morphology - PREFIX/MIDDLE/SUFFIX patterns
3. Length
4. Frequency (singleton vs repeater)
"""

import sys
import json
from pathlib import Path
from collections import defaultdict, Counter
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))
from scripts.voynich import Transcript, Morphology

tx = Transcript()
morph = Morphology()

print("=" * 70)
print("T14: INITIAL vs FINAL RI COMPARISON")
print("=" * 70)

# Build B vocabulary for PP/RI classification
b_middles = set()
for token in tx.currier_b():
    w = token.word.strip()
    if not w or '*' in w:
        continue
    m = morph.extract(w)
    if m.middle:
        b_middles.add(m.middle)

# Collect A tokens by line with position info
initial_ri = []  # position < 0.2
final_ri = []    # position > 0.8
middle_ri = []   # 0.2 <= position <= 0.8

a_tokens_by_line = defaultdict(list)
for token in tx.currier_a():
    w = token.word.strip()
    if not w or '*' in w:
        continue
    m = morph.extract(w)
    is_ri = m.middle not in b_middles if m.middle else False
    a_tokens_by_line[(token.folio, token.line)].append({
        'word': w,
        'middle': m.middle,
        'prefix': m.prefix,
        'suffix': m.suffix,
        'is_ri': is_ri,
    })

# Classify RI by position
for (folio, line), tokens in a_tokens_by_line.items():
    n = len(tokens)
    if n < 2:
        continue

    for i, t in enumerate(tokens):
        if not t['is_ri']:
            continue

        rel_pos = i / (n - 1)
        t['rel_pos'] = rel_pos
        t['abs_pos'] = i
        t['line_len'] = n

        if rel_pos < 0.2:
            initial_ri.append(t)
        elif rel_pos > 0.8:
            final_ri.append(t)
        else:
            middle_ri.append(t)

print(f"\nRI by position:")
print(f"  INITIAL (pos < 0.2): {len(initial_ri)}")
print(f"  MIDDLE (0.2-0.8): {len(middle_ri)}")
print(f"  FINAL (pos > 0.8): {len(final_ri)}")

# Test 1: Token overlap
print("\n" + "=" * 70)
print("TEST 1: TOKEN IDENTITY OVERLAP")
print("=" * 70)

initial_words = set(t['word'] for t in initial_ri)
final_words = set(t['word'] for t in final_ri)
middle_words = set(t['word'] for t in middle_ri)

overlap_init_final = initial_words & final_words
overlap_init_mid = initial_words & middle_words
overlap_final_mid = final_words & middle_words

print(f"\nUnique words:")
print(f"  INITIAL: {len(initial_words)}")
print(f"  FINAL: {len(final_words)}")
print(f"  MIDDLE: {len(middle_words)}")

print(f"\nOverlap:")
print(f"  INITIAL & FINAL: {len(overlap_init_final)} ({len(overlap_init_final)/min(len(initial_words), len(final_words))*100:.1f}% of smaller)")
print(f"  INITIAL & MIDDLE: {len(overlap_init_mid)}")
print(f"  FINAL & MIDDLE: {len(overlap_final_mid)}")

# Jaccard similarity
def jaccard(a, b):
    if not a or not b:
        return 0
    return len(a & b) / len(a | b)

print(f"\nJaccard similarity:")
print(f"  INITIAL vs FINAL: {jaccard(initial_words, final_words):.3f}")
print(f"  INITIAL vs MIDDLE: {jaccard(initial_words, middle_words):.3f}")
print(f"  FINAL vs MIDDLE: {jaccard(final_words, middle_words):.3f}")

# Test 2: Morphological comparison
print("\n" + "=" * 70)
print("TEST 2: MORPHOLOGICAL PROFILE")
print("=" * 70)

def morph_profile(tokens):
    if not tokens:
        return {}
    prefixes = Counter(t['prefix'] for t in tokens if t['prefix'])
    suffixes = Counter(t['suffix'] for t in tokens if t['suffix'])
    middles = Counter(t['middle'] for t in tokens if t['middle'])

    has_prefix = sum(1 for t in tokens if t['prefix']) / len(tokens)
    has_suffix = sum(1 for t in tokens if t['suffix']) / len(tokens)
    mean_len = np.mean([len(t['word']) for t in tokens])

    return {
        'has_prefix': has_prefix,
        'has_suffix': has_suffix,
        'mean_len': mean_len,
        'top_prefixes': prefixes.most_common(5),
        'top_suffixes': suffixes.most_common(5),
        'top_middles': middles.most_common(5),
    }

init_prof = morph_profile(initial_ri)
final_prof = morph_profile(final_ri)
mid_prof = morph_profile(middle_ri)

print(f"\n{'Metric':<20} {'INITIAL':>12} {'FINAL':>12} {'MIDDLE':>12}")
print(f"{'-'*20} {'-'*12} {'-'*12} {'-'*12}")
print(f"{'Has PREFIX':<20} {init_prof['has_prefix']*100:>11.1f}% {final_prof['has_prefix']*100:>11.1f}% {mid_prof['has_prefix']*100:>11.1f}%")
print(f"{'Has SUFFIX':<20} {init_prof['has_suffix']*100:>11.1f}% {final_prof['has_suffix']*100:>11.1f}% {mid_prof['has_suffix']*100:>11.1f}%")
print(f"{'Mean length':<20} {init_prof['mean_len']:>12.1f} {final_prof['mean_len']:>12.1f} {mid_prof['mean_len']:>12.1f}")

# Test 3: Top tokens by position
print("\n" + "=" * 70)
print("TEST 3: TOP TOKENS BY POSITION")
print("=" * 70)

init_counts = Counter(t['word'] for t in initial_ri)
final_counts = Counter(t['word'] for t in final_ri)

print(f"\nTop 10 INITIAL RI:")
for word, count in init_counts.most_common(10):
    m = morph.extract(word)
    also_final = "* ALSO FINAL" if word in final_words else ""
    print(f"  {word:<18} x{count:<3} (pref={m.prefix}, mid={m.middle}, suf={m.suffix}) {also_final}")

print(f"\nTop 10 FINAL RI:")
for word, count in final_counts.most_common(10):
    m = morph.extract(word)
    also_init = "* ALSO INITIAL" if word in initial_words else ""
    print(f"  {word:<18} x{count:<3} (pref={m.prefix}, mid={m.middle}, suf={m.suffix}) {also_init}")

# Test 4: PREFIX distribution
print("\n" + "=" * 70)
print("TEST 4: PREFIX DISTRIBUTION BY POSITION")
print("=" * 70)

init_prefixes = Counter(t['prefix'] for t in initial_ri)
final_prefixes = Counter(t['prefix'] for t in final_ri)

all_prefixes = set(init_prefixes.keys()) | set(final_prefixes.keys())

print(f"\n{'PREFIX':<10} {'INITIAL':>10} {'FINAL':>10} {'RATIO':>10}")
print(f"{'-'*10} {'-'*10} {'-'*10} {'-'*10}")

for prefix in sorted(all_prefixes, key=lambda x: (x is None, x)):
    init_n = init_prefixes.get(prefix, 0)
    final_n = final_prefixes.get(prefix, 0)
    if init_n + final_n < 5:
        continue
    ratio = init_n / final_n if final_n > 0 else float('inf')
    pref_str = prefix if prefix else "(none)"
    print(f"{pref_str:<10} {init_n:>10} {final_n:>10} {ratio:>10.2f}")

# Test 5: SUFFIX distribution
print("\n" + "=" * 70)
print("TEST 5: SUFFIX DISTRIBUTION BY POSITION")
print("=" * 70)

init_suffixes = Counter(t['suffix'] for t in initial_ri)
final_suffixes = Counter(t['suffix'] for t in final_ri)

all_suffixes = set(init_suffixes.keys()) | set(final_suffixes.keys())

print(f"\n{'SUFFIX':<10} {'INITIAL':>10} {'FINAL':>10} {'RATIO':>10}")
print(f"{'-'*10} {'-'*10} {'-'*10} {'-'*10}")

for suffix in sorted(all_suffixes, key=lambda x: (x is None, x)):
    init_n = init_suffixes.get(suffix, 0)
    final_n = final_suffixes.get(suffix, 0)
    if init_n + final_n < 5:
        continue
    ratio = init_n / final_n if final_n > 0 else float('inf')
    suf_str = suffix if suffix else "(none)"
    print(f"{suf_str:<10} {init_n:>10} {final_n:>10} {ratio:>10.2f}")

# Test 6: Are INITIAL RI followed by specific patterns?
print("\n" + "=" * 70)
print("TEST 6: WHAT FOLLOWS INITIAL RI?")
print("=" * 70)

following_initial_ri = []
for (folio, line), tokens in a_tokens_by_line.items():
    n = len(tokens)
    if n < 3:
        continue

    for i, t in enumerate(tokens):
        if not t['is_ri']:
            continue
        rel_pos = i / (n - 1)
        if rel_pos < 0.2 and i + 1 < len(tokens):
            next_t = tokens[i + 1]
            following_initial_ri.append({
                'is_ri': next_t['is_ri'],
                'is_pp': not next_t['is_ri'] and next_t['middle'] is not None,
                'word': next_t['word'],
            })

if following_initial_ri:
    next_is_ri = sum(1 for t in following_initial_ri if t['is_ri'])
    next_is_pp = sum(1 for t in following_initial_ri if t['is_pp'])
    print(f"\nAfter INITIAL RI:")
    print(f"  Next is RI: {next_is_ri} ({next_is_ri/len(following_initial_ri)*100:.1f}%)")
    print(f"  Next is PP: {next_is_pp} ({next_is_pp/len(following_initial_ri)*100:.1f}%)")

# Test 7: What precedes FINAL RI?
print("\n" + "=" * 70)
print("TEST 7: WHAT PRECEDES FINAL RI?")
print("=" * 70)

preceding_final_ri = []
for (folio, line), tokens in a_tokens_by_line.items():
    n = len(tokens)
    if n < 3:
        continue

    for i, t in enumerate(tokens):
        if not t['is_ri']:
            continue
        rel_pos = i / (n - 1)
        if rel_pos > 0.8 and i > 0:
            prev_t = tokens[i - 1]
            preceding_final_ri.append({
                'is_ri': prev_t['is_ri'],
                'is_pp': not prev_t['is_ri'] and prev_t['middle'] is not None,
                'word': prev_t['word'],
            })

if preceding_final_ri:
    prev_is_ri = sum(1 for t in preceding_final_ri if t['is_ri'])
    prev_is_pp = sum(1 for t in preceding_final_ri if t['is_pp'])
    print(f"\nBefore FINAL RI:")
    print(f"  Prev is RI: {prev_is_ri} ({prev_is_ri/len(preceding_final_ri)*100:.1f}%)")
    print(f"  Prev is PP: {prev_is_pp} ({prev_is_pp/len(preceding_final_ri)*100:.1f}%)")

# Summary
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

print(f"""
INITIAL vs FINAL RI:

OVERLAP:
- Jaccard similarity: {jaccard(initial_words, final_words):.3f}
- {len(overlap_init_final)} words appear in BOTH positions

MORPHOLOGY:
- INITIAL: {init_prof['has_prefix']*100:.0f}% PREFIX, {init_prof['has_suffix']*100:.0f}% SUFFIX, len={init_prof['mean_len']:.1f}
- FINAL:   {final_prof['has_prefix']*100:.0f}% PREFIX, {final_prof['has_suffix']*100:.0f}% SUFFIX, len={final_prof['mean_len']:.1f}
""")

if jaccard(initial_words, final_words) < 0.1:
    print("FINDING: INITIAL and FINAL RI are DIFFERENT vocabularies")
elif jaccard(initial_words, final_words) > 0.3:
    print("FINDING: INITIAL and FINAL RI share substantial vocabulary")
else:
    print("FINDING: INITIAL and FINAL RI have moderate overlap")

if abs(init_prof['has_suffix'] - final_prof['has_suffix']) > 0.1:
    if init_prof['has_suffix'] > final_prof['has_suffix']:
        print("FINDING: INITIAL RI more likely to have SUFFIX")
    else:
        print("FINDING: FINAL RI more likely to have SUFFIX")

# Save results
results = {
    'initial_count': len(initial_ri),
    'final_count': len(final_ri),
    'overlap_count': len(overlap_init_final),
    'jaccard': float(jaccard(initial_words, final_words)),
    'initial_has_suffix': float(init_prof['has_suffix']),
    'final_has_suffix': float(final_prof['has_suffix']),
}

out_path = PROJECT_ROOT / 'phases' / 'A_RECORD_B_ROUTING_TOPOLOGY' / 'results' / 't14_ri_initial_vs_final.json'
with open(out_path, 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to {out_path.name}")
