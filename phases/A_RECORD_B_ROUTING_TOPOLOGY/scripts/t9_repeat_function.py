"""
T9: Repeated Token Function Analysis

What ARE the repeated tokens in A-records? What purpose could they serve?

Tests:
1. Identity: What specific tokens repeat most?
2. Morphology: Are repeats PP or RI? What MIDDLEs?
3. Position: Where do repeats occur (initial, medial, final)?
4. Pipeline participation: Do repeated MIDDLEs appear in B?
5. Concentration: Are repeats concentrated in certain folios/lines?
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
print("T9: REPEATED TOKEN FUNCTION ANALYSIS")
print("=" * 70)

# Build B vocabulary for pipeline check
print("\nBuilding B vocabulary...")
b_middles = set()
for token in tx.currier_b():
    w = token.word.strip()
    if not w or '*' in w:
        continue
    m = morph.extract(w)
    if m.middle:
        b_middles.add(m.middle)

print(f"  B MIDDLEs: {len(b_middles)}")

# Collect all A tokens and identify repeats
print("\nCollecting A tokens and repeats...")

a_tokens_by_line = defaultdict(list)
all_a_tokens = []

for token in tx.currier_a():
    w = token.word.strip()
    if not w or '*' in w:
        continue

    m = morph.extract(w)
    t = {
        'word': w,
        'folio': token.folio,
        'line': token.line,
        'prefix': m.prefix,
        'middle': m.middle,
        'suffix': m.suffix,
    }
    a_tokens_by_line[(token.folio, token.line)].append(t)
    all_a_tokens.append(t)

# Identify within-line repeats
within_line_repeats = []
non_repeats = []

for (folio, line), tokens in a_tokens_by_line.items():
    seen = set()
    for i, t in enumerate(tokens):
        t['position'] = i
        t['line_length'] = len(tokens)
        t['relative_pos'] = i / max(1, len(tokens) - 1) if len(tokens) > 1 else 0.5

        if t['word'] in seen:
            within_line_repeats.append(t)
        else:
            non_repeats.append(t)
        seen.add(t['word'])

print(f"  Total A tokens: {len(all_a_tokens)}")
print(f"  Within-line repeats: {len(within_line_repeats)}")
print(f"  Non-repeats: {len(non_repeats)}")

# Test 1: What specific tokens repeat?
print("\n" + "=" * 70)
print("TEST 1: MOST FREQUENT REPEATED TOKENS")
print("=" * 70)

repeat_counts = Counter(t['word'] for t in within_line_repeats)
print(f"\nTop 20 repeated tokens:")
for word, count in repeat_counts.most_common(20):
    m = morph.extract(word)
    in_b = "PP" if m.middle in b_middles else "RI"
    print(f"  {word:15} x{count:3}  MIDDLE={m.middle or 'None':10}  {in_b}")

# Test 2: PP vs RI distribution
print("\n" + "=" * 70)
print("TEST 2: PP vs RI DISTRIBUTION")
print("=" * 70)

def classify_pp_ri(middle):
    if not middle:
        return 'NO_MIDDLE'
    return 'PP' if middle in b_middles else 'RI'

repeat_pp_ri = Counter(classify_pp_ri(t['middle']) for t in within_line_repeats)
nonrep_pp_ri = Counter(classify_pp_ri(t['middle']) for t in non_repeats)

print(f"\nRepeated tokens:")
for cat, count in repeat_pp_ri.most_common():
    print(f"  {cat}: {count} ({count/len(within_line_repeats)*100:.1f}%)")

print(f"\nNon-repeated tokens:")
for cat, count in nonrep_pp_ri.most_common():
    print(f"  {cat}: {count} ({count/len(non_repeats)*100:.1f}%)")

# Chi-squared test
from scipy.stats import chi2_contingency
pp_repeat = repeat_pp_ri.get('PP', 0)
ri_repeat = repeat_pp_ri.get('RI', 0)
pp_nonrep = nonrep_pp_ri.get('PP', 0)
ri_nonrep = nonrep_pp_ri.get('RI', 0)

if pp_repeat + ri_repeat > 0 and pp_nonrep + ri_nonrep > 0:
    table = [[pp_repeat, ri_repeat], [pp_nonrep, ri_nonrep]]
    chi2, p, dof, expected = chi2_contingency(table)
    print(f"\nChi-squared: {chi2:.1f}, p={p:.2e}")

    repeat_pp_rate = pp_repeat / (pp_repeat + ri_repeat)
    nonrep_pp_rate = pp_nonrep / (pp_nonrep + ri_nonrep)
    print(f"PP rate in repeats: {repeat_pp_rate:.1%}")
    print(f"PP rate in non-repeats: {nonrep_pp_rate:.1%}")

# Test 3: Position analysis
print("\n" + "=" * 70)
print("TEST 3: POSITIONAL DISTRIBUTION")
print("=" * 70)

repeat_positions = [t['relative_pos'] for t in within_line_repeats]
nonrep_positions = [t['relative_pos'] for t in non_repeats]

print(f"\nMean relative position (0=start, 1=end):")
print(f"  Repeats: {np.mean(repeat_positions):.3f}")
print(f"  Non-repeats: {np.mean(nonrep_positions):.3f}")

# Position buckets
def bucket_position(pos):
    if pos < 0.2:
        return 'INITIAL'
    elif pos > 0.8:
        return 'FINAL'
    else:
        return 'MEDIAL'

repeat_buckets = Counter(bucket_position(p) for p in repeat_positions)
nonrep_buckets = Counter(bucket_position(p) for p in nonrep_positions)

print(f"\nPosition distribution:")
print(f"  {'Position':<10} {'Repeats':>10} {'Non-rep':>10} {'Rep Rate':>10}")
for pos in ['INITIAL', 'MEDIAL', 'FINAL']:
    rep = repeat_buckets.get(pos, 0)
    non = nonrep_buckets.get(pos, 0)
    rate = rep / (rep + non) * 100 if (rep + non) > 0 else 0
    print(f"  {pos:<10} {rep:>10} {non:>10} {rate:>9.1f}%")

# Test 4: MIDDLE frequency analysis
print("\n" + "=" * 70)
print("TEST 4: MIDDLE CHARACTERISTICS")
print("=" * 70)

# Get overall MIDDLE frequencies in A
all_a_middles = Counter(t['middle'] for t in all_a_tokens if t['middle'])
repeat_middles = Counter(t['middle'] for t in within_line_repeats if t['middle'])

# Are repeated MIDDLEs more common or rare?
repeat_middle_freqs = []
nonrep_middle_freqs = []

for t in within_line_repeats:
    if t['middle']:
        repeat_middle_freqs.append(all_a_middles[t['middle']])

for t in non_repeats:
    if t['middle']:
        nonrep_middle_freqs.append(all_a_middles[t['middle']])

print(f"\nMIDDLE frequency in corpus:")
print(f"  Repeated tokens' MIDDLEs: mean freq = {np.mean(repeat_middle_freqs):.1f}")
print(f"  Non-repeat tokens' MIDDLEs: mean freq = {np.mean(nonrep_middle_freqs):.1f}")
print(f"  Ratio: {np.mean(repeat_middle_freqs)/np.mean(nonrep_middle_freqs):.2f}x")

from scipy.stats import mannwhitneyu
stat, p = mannwhitneyu(repeat_middle_freqs, nonrep_middle_freqs)
print(f"  Mann-Whitney p={p:.2e}")

# Test 5: Are repeats the SAME token or same MIDDLE different token?
print("\n" + "=" * 70)
print("TEST 5: EXACT vs MIDDLE-ONLY REPETITION")
print("=" * 70)

# For each line, check if repeats are exact tokens or just same MIDDLE
exact_repeats = 0
middle_only_repeats = 0

for (folio, line), tokens in a_tokens_by_line.items():
    seen_words = set()
    seen_middles = {}  # middle -> first word with that middle

    for t in tokens:
        if t['word'] in seen_words:
            exact_repeats += 1
        elif t['middle'] and t['middle'] in seen_middles:
            # Same MIDDLE, different word
            middle_only_repeats += 1

        seen_words.add(t['word'])
        if t['middle'] and t['middle'] not in seen_middles:
            seen_middles[t['middle']] = t['word']

print(f"  Exact word repeats: {exact_repeats}")
print(f"  Same-MIDDLE different-word: {middle_only_repeats}")
print(f"  Ratio: {exact_repeats/max(1,middle_only_repeats):.1f}x")

# Test 6: Do repeats cluster in specific lines/folios?
print("\n" + "=" * 70)
print("TEST 6: REPEAT CONCENTRATION")
print("=" * 70)

repeats_per_line = Counter()
for t in within_line_repeats:
    repeats_per_line[(t['folio'], t['line'])] += 1

lines_with_1_repeat = sum(1 for c in repeats_per_line.values() if c == 1)
lines_with_2_repeat = sum(1 for c in repeats_per_line.values() if c == 2)
lines_with_3plus = sum(1 for c in repeats_per_line.values() if c >= 3)

print(f"\nLines by repeat count:")
print(f"  1 repeat: {lines_with_1_repeat}")
print(f"  2 repeats: {lines_with_2_repeat}")
print(f"  3+ repeats: {lines_with_3plus}")

if lines_with_3plus > 0:
    print(f"\nLines with 3+ repeats (high concentration):")
    for (folio, line), count in repeats_per_line.most_common(10):
        tokens = a_tokens_by_line[(folio, line)]
        words = [t['word'] for t in tokens]
        print(f"  {folio}.{line}: {count} repeats in {len(tokens)} tokens")
        print(f"    {' '.join(words)}")

# Test 7: Specific repeated tokens - what are they?
print("\n" + "=" * 70)
print("TEST 7: REPEATED TOKEN IDENTITY ANALYSIS")
print("=" * 70)

# Categorize the top repeated tokens
top_repeats = repeat_counts.most_common(30)

# Check characteristics
print(f"\nTop 30 repeated tokens analysis:")
print(f"  {'Token':<15} {'Count':>5} {'MIDDLE':<10} {'PP/RI':>5} {'Len':>3}")
print(f"  {'-'*15} {'-'*5} {'-'*10} {'-'*5} {'-'*3}")

for word, count in top_repeats:
    m = morph.extract(word)
    pp_ri = "PP" if m.middle in b_middles else "RI"
    print(f"  {word:<15} {count:>5} {m.middle or 'None':<10} {pp_ri:>5} {len(word):>3}")

# Summary
print("\n" + "=" * 70)
print("SUMMARY: WHAT PURPOSE DO REPEATS SERVE?")
print("=" * 70)

pp_rate = pp_repeat / (pp_repeat + ri_repeat) * 100 if (pp_repeat + ri_repeat) > 0 else 0
pos_bias = np.mean(repeat_positions)
freq_ratio = np.mean(repeat_middle_freqs)/np.mean(nonrep_middle_freqs)

print(f"""
KEY FINDINGS:
- PP rate in repeats: {pp_rate:.1f}% (vs {nonrep_pp_rate*100:.1f}% in non-repeats)
- Position bias: {pos_bias:.3f} (0.5 = neutral, >0.5 = late-biased)
- MIDDLE frequency: Repeats use {freq_ratio:.1f}x more common MIDDLEs
- Exact vs MIDDLE-only: {exact_repeats}:{middle_only_repeats} ratio

INTERPRETATION:
""")

if pp_rate > nonrep_pp_rate * 100 + 5:
    print("- Repeats are PP-ENRICHED -> they ARE pipeline-relevant")
elif pp_rate < nonrep_pp_rate * 100 - 5:
    print("- Repeats are RI-ENRICHED -> they may be record-internal markers")
else:
    print("- Repeats have similar PP/RI ratio -> no pipeline bias")

if freq_ratio > 1.5:
    print("- Repeats use COMMON MIDDLEs -> likely structural/grammatical function")
elif freq_ratio < 0.7:
    print("- Repeats use RARE MIDDLEs -> possibly emphasis/correction")
else:
    print("- Repeats use typical MIDDLEs -> no frequency bias")

if pos_bias > 0.55:
    print("- Repeats are LATE-biased -> possibly confirmation/closure")
elif pos_bias < 0.45:
    print("- Repeats are EARLY-biased -> possibly initialization/framing")
else:
    print("- Repeats are position-neutral")

# Save results
results = {
    'total_repeats': len(within_line_repeats),
    'pp_rate_repeats': float(pp_rate),
    'pp_rate_nonrepeats': float(nonrep_pp_rate * 100),
    'position_bias': float(pos_bias),
    'middle_freq_ratio': float(freq_ratio),
    'exact_vs_middle_ratio': float(exact_repeats/max(1,middle_only_repeats)),
    'top_repeated_tokens': [(w, c) for w, c in repeat_counts.most_common(20)],
}

out_path = PROJECT_ROOT / 'phases' / 'A_RECORD_B_ROUTING_TOPOLOGY' / 'results' / 't9_repeat_function.json'
with open(out_path, 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to {out_path.name}")
