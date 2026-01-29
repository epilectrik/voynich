"""
T11: RI vs HT Structural Comparison

Is RI (A-exclusive vocabulary) structurally analogous to HT (B unclassified vocabulary)?

Both are "outside the pipeline":
- RI: A-exclusive MIDDLEs that don't participate in A->B filtering
- HT: B tokens outside the 49-class operational grammar

Test structural parallels:
1. Singleton rate (hapax frequency)
2. Repetition behavior (within-line)
3. Position bias
4. Morphological profile
5. Frequency distribution (Zipf)
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
print("T11: RI vs HT STRUCTURAL COMPARISON")
print("=" * 70)

# Load classified token set for HT identification
ctm_path = PROJECT_ROOT / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
with open(ctm_path, 'r', encoding='utf-8') as f:
    ctm = json.load(f)
classified_tokens = set(ctm['token_to_class'].keys())

# Build B vocabulary for PP/RI classification
b_middles = set()
b_tokens_all = []
for token in tx.currier_b():
    w = token.word.strip()
    if not w or '*' in w:
        continue
    m = morph.extract(w)
    if m.middle:
        b_middles.add(m.middle)
    is_ht = w not in classified_tokens
    b_tokens_all.append({
        'word': w,
        'folio': token.folio,
        'line': token.line,
        'middle': m.middle,
        'prefix': m.prefix,
        'suffix': m.suffix,
        'is_ht': is_ht,
    })

# Build A data
a_tokens_all = []
for token in tx.currier_a():
    w = token.word.strip()
    if not w or '*' in w:
        continue
    m = morph.extract(w)
    is_ri = m.middle not in b_middles if m.middle else False
    a_tokens_all.append({
        'word': w,
        'folio': token.folio,
        'line': token.line,
        'middle': m.middle,
        'prefix': m.prefix,
        'suffix': m.suffix,
        'is_ri': is_ri,
    })

# Separate populations
ri_tokens = [t for t in a_tokens_all if t['is_ri']]
pp_tokens = [t for t in a_tokens_all if not t['is_ri'] and t['middle']]
ht_tokens = [t for t in b_tokens_all if t['is_ht']]
op_tokens = [t for t in b_tokens_all if not t['is_ht']]  # Operational (classified)

print(f"\nPopulation sizes:")
print(f"  A-RI tokens: {len(ri_tokens)} ({len(ri_tokens)/len(a_tokens_all)*100:.1f}% of A)")
print(f"  A-PP tokens: {len(pp_tokens)} ({len(pp_tokens)/len(a_tokens_all)*100:.1f}% of A)")
print(f"  B-HT tokens: {len(ht_tokens)} ({len(ht_tokens)/len(b_tokens_all)*100:.1f}% of B)")
print(f"  B-OP tokens: {len(op_tokens)} ({len(op_tokens)/len(b_tokens_all)*100:.1f}% of B)")

# Test 1: Singleton (hapax) rate
print("\n" + "=" * 70)
print("TEST 1: SINGLETON (HAPAX) RATE")
print("=" * 70)

def hapax_rate(tokens):
    word_counts = Counter(t['word'] for t in tokens)
    singletons = sum(1 for c in word_counts.values() if c == 1)
    return singletons / len(word_counts) if word_counts else 0

ri_hapax = hapax_rate(ri_tokens)
pp_hapax = hapax_rate(pp_tokens)
ht_hapax = hapax_rate(ht_tokens)
op_hapax = hapax_rate(op_tokens)

print(f"\nHapax (singleton) rate by type:")
print(f"  A-RI: {ri_hapax:.1%}")
print(f"  A-PP: {pp_hapax:.1%}")
print(f"  B-HT: {ht_hapax:.1%}")
print(f"  B-OP: {op_hapax:.1%}")
print(f"\n  RI vs HT: {'SIMILAR' if abs(ri_hapax - ht_hapax) < 0.1 else 'DIFFERENT'}")

# Test 2: Within-line repetition
print("\n" + "=" * 70)
print("TEST 2: WITHIN-LINE REPETITION RATE")
print("=" * 70)

def within_line_repeat_rate(tokens):
    by_line = defaultdict(list)
    for t in tokens:
        by_line[(t['folio'], t['line'])].append(t['word'])

    total = 0
    repeats = 0
    for words in by_line.values():
        total += len(words)
        seen = set()
        for w in words:
            if w in seen:
                repeats += 1
            seen.add(w)
    return repeats / total if total > 0 else 0

ri_repeat = within_line_repeat_rate(ri_tokens)
pp_repeat = within_line_repeat_rate(pp_tokens)
ht_repeat = within_line_repeat_rate(ht_tokens)
op_repeat = within_line_repeat_rate(op_tokens)

print(f"\nWithin-line repetition rate:")
print(f"  A-RI: {ri_repeat:.2%}")
print(f"  A-PP: {pp_repeat:.2%}")
print(f"  B-HT: {ht_repeat:.2%}")
print(f"  B-OP: {op_repeat:.2%}")
print(f"\n  RI vs HT: {'SIMILAR' if abs(ri_repeat - ht_repeat) < 0.01 else 'DIFFERENT'}")

# Test 3: Position bias
print("\n" + "=" * 70)
print("TEST 3: POSITION BIAS (WITHIN LINE)")
print("=" * 70)

def mean_relative_position(tokens):
    by_line = defaultdict(list)
    for t in tokens:
        by_line[(t['folio'], t['line'])].append(t)

    positions = []
    for (f, l), line_tokens in by_line.items():
        # Get all tokens in this line (need full line for position calc)
        pass

    # Simplified: use token index in its own population
    # This isn't ideal but gives rough position tendency
    return None  # Skip for now

# Alternative: look at which fraction of line tokens are RI/HT
def line_position_profile(tokens, all_tokens_by_line):
    """Where in the line do these tokens tend to appear?"""
    positions = []
    for t in tokens:
        line_key = (t['folio'], t['line'])
        if line_key in all_tokens_by_line:
            line_words = [x['word'] for x in all_tokens_by_line[line_key]]
            if t['word'] in line_words:
                idx = line_words.index(t['word'])
                rel_pos = idx / max(1, len(line_words) - 1) if len(line_words) > 1 else 0.5
                positions.append(rel_pos)
    return np.mean(positions) if positions else 0.5

a_by_line = defaultdict(list)
for t in a_tokens_all:
    a_by_line[(t['folio'], t['line'])].append(t)

b_by_line = defaultdict(list)
for t in b_tokens_all:
    b_by_line[(t['folio'], t['line'])].append(t)

# For each RI/HT token, find its position in its line
ri_positions = []
for t in ri_tokens:
    line_tokens = a_by_line[(t['folio'], t['line'])]
    for i, lt in enumerate(line_tokens):
        if lt['word'] == t['word'] and lt is t:
            rel_pos = i / max(1, len(line_tokens) - 1) if len(line_tokens) > 1 else 0.5
            ri_positions.append(rel_pos)
            break

ht_positions = []
for t in ht_tokens:
    line_tokens = b_by_line[(t['folio'], t['line'])]
    for i, lt in enumerate(line_tokens):
        if lt['word'] == t['word'] and lt is t:
            rel_pos = i / max(1, len(line_tokens) - 1) if len(line_tokens) > 1 else 0.5
            ht_positions.append(rel_pos)
            break

print(f"\nMean relative position (0=start, 1=end):")
print(f"  A-RI: {np.mean(ri_positions):.3f}")
print(f"  B-HT: {np.mean(ht_positions):.3f}")
print(f"\n  RI vs HT: {'SIMILAR' if abs(np.mean(ri_positions) - np.mean(ht_positions)) < 0.05 else 'DIFFERENT'}")

# Test 4: Morphological profile
print("\n" + "=" * 70)
print("TEST 4: MORPHOLOGICAL PROFILE")
print("=" * 70)

def morph_profile(tokens):
    has_prefix = sum(1 for t in tokens if t['prefix']) / len(tokens) if tokens else 0
    has_suffix = sum(1 for t in tokens if t['suffix']) / len(tokens) if tokens else 0
    mean_len = np.mean([len(t['word']) for t in tokens]) if tokens else 0
    return has_prefix, has_suffix, mean_len

ri_pref, ri_suf, ri_len = morph_profile(ri_tokens)
pp_pref, pp_suf, pp_len = morph_profile(pp_tokens)
ht_pref, ht_suf, ht_len = morph_profile(ht_tokens)
op_pref, op_suf, op_len = morph_profile(op_tokens)

print(f"\nMorphological features:")
print(f"  {'Type':<8} {'PREFIX%':>8} {'SUFFIX%':>8} {'MeanLen':>8}")
print(f"  {'-'*8} {'-'*8} {'-'*8} {'-'*8}")
print(f"  {'A-RI':<8} {ri_pref*100:>7.1f}% {ri_suf*100:>7.1f}% {ri_len:>8.1f}")
print(f"  {'A-PP':<8} {pp_pref*100:>7.1f}% {pp_suf*100:>7.1f}% {pp_len:>8.1f}")
print(f"  {'B-HT':<8} {ht_pref*100:>7.1f}% {ht_suf*100:>7.1f}% {ht_len:>8.1f}")
print(f"  {'B-OP':<8} {op_pref*100:>7.1f}% {op_suf*100:>7.1f}% {op_len:>8.1f}")

# Test 5: Type/token ratio (vocabulary diversity)
print("\n" + "=" * 70)
print("TEST 5: TYPE/TOKEN RATIO (VOCABULARY DIVERSITY)")
print("=" * 70)

def type_token_ratio(tokens):
    types = len(set(t['word'] for t in tokens))
    return types / len(tokens) if tokens else 0

ri_ttr = type_token_ratio(ri_tokens)
pp_ttr = type_token_ratio(pp_tokens)
ht_ttr = type_token_ratio(ht_tokens)
op_ttr = type_token_ratio(op_tokens)

print(f"\nType/Token ratio (higher = more diverse vocabulary):")
print(f"  A-RI: {ri_ttr:.3f} ({len(set(t['word'] for t in ri_tokens))} types / {len(ri_tokens)} tokens)")
print(f"  A-PP: {pp_ttr:.3f} ({len(set(t['word'] for t in pp_tokens))} types / {len(pp_tokens)} tokens)")
print(f"  B-HT: {ht_ttr:.3f} ({len(set(t['word'] for t in ht_tokens))} types / {len(ht_tokens)} tokens)")
print(f"  B-OP: {op_ttr:.3f} ({len(set(t['word'] for t in op_tokens))} types / {len(op_tokens)} tokens)")

# Summary
print("\n" + "=" * 70)
print("SUMMARY: IS RI THE 'HT OF CURRIER A'?")
print("=" * 70)

similarities = 0
differences = 0

# Check each metric
if abs(ri_hapax - ht_hapax) < 0.1:
    print(f"  [SIMILAR] Hapax rate: RI {ri_hapax:.1%} vs HT {ht_hapax:.1%}")
    similarities += 1
else:
    print(f"  [DIFFERENT] Hapax rate: RI {ri_hapax:.1%} vs HT {ht_hapax:.1%}")
    differences += 1

if abs(ri_repeat - ht_repeat) < 0.01:
    print(f"  [SIMILAR] Within-line repeat: RI {ri_repeat:.2%} vs HT {ht_repeat:.2%}")
    similarities += 1
else:
    print(f"  [DIFFERENT] Within-line repeat: RI {ri_repeat:.2%} vs HT {ht_repeat:.2%}")
    differences += 1

if abs(np.mean(ri_positions) - np.mean(ht_positions)) < 0.05:
    print(f"  [SIMILAR] Position bias: RI {np.mean(ri_positions):.3f} vs HT {np.mean(ht_positions):.3f}")
    similarities += 1
else:
    print(f"  [DIFFERENT] Position bias: RI {np.mean(ri_positions):.3f} vs HT {np.mean(ht_positions):.3f}")
    differences += 1

if abs(ri_ttr - ht_ttr) < 0.1:
    print(f"  [SIMILAR] Type/token ratio: RI {ri_ttr:.3f} vs HT {ht_ttr:.3f}")
    similarities += 1
else:
    print(f"  [DIFFERENT] Type/token ratio: RI {ri_ttr:.3f} vs HT {ht_ttr:.3f}")
    differences += 1

if abs(ri_len - ht_len) < 1.0:
    print(f"  [SIMILAR] Mean length: RI {ri_len:.1f} vs HT {ht_len:.1f}")
    similarities += 1
else:
    print(f"  [DIFFERENT] Mean length: RI {ri_len:.1f} vs HT {ht_len:.1f}")
    differences += 1

print(f"\n  Score: {similarities} similar, {differences} different")

if similarities >= 4:
    print(f"\n  VERDICT: RI and HT are STRUCTURALLY ANALOGOUS")
    print(f"           RI is plausibly 'HT in Currier A'")
elif similarities >= 2:
    print(f"\n  VERDICT: RI and HT share SOME structural properties")
    print(f"           Partial analogy, different functions possible")
else:
    print(f"\n  VERDICT: RI and HT are STRUCTURALLY DIFFERENT")
    print(f"           Different phenomena despite both being 'outside pipeline'")

# Save results
results = {
    'ri_hapax': float(ri_hapax),
    'ht_hapax': float(ht_hapax),
    'ri_repeat': float(ri_repeat),
    'ht_repeat': float(ht_repeat),
    'ri_position': float(np.mean(ri_positions)),
    'ht_position': float(np.mean(ht_positions)),
    'ri_ttr': float(ri_ttr),
    'ht_ttr': float(ht_ttr),
    'ri_length': float(ri_len),
    'ht_length': float(ht_len),
    'similarities': similarities,
    'differences': differences,
}

out_path = PROJECT_ROOT / 'phases' / 'A_RECORD_B_ROUTING_TOPOLOGY' / 'results' / 't11_ri_ht_comparison.json'
with open(out_path, 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to {out_path.name}")
