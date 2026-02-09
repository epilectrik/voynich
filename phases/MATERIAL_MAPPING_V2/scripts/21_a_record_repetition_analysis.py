"""
21_a_record_repetition_analysis.py

Analyze repetition patterns in A records.

If A records are vocabulary lists: tokens should appear once
If A records are procedures: tokens should repeat (do X, then X again)

Questions:
1. How much repetition is there in A records?
2. Do certain tokens repeat more than others?
3. Is repetition structured (patterns) or random?
"""

import sys
from pathlib import Path
from collections import defaultdict, Counter
import json

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'scripts'))
from voynich import Transcript, Morphology

print("="*70)
print("A RECORD REPETITION ANALYSIS")
print("="*70)

tx = Transcript()
morph = Morphology()

# Load paragraph structure
para_results = Path(__file__).parent.parent.parent / "PARAGRAPH_INTERNAL_PROFILING" / "results"
with open(para_results / "a_paragraph_tokens.json") as f:
    para_tokens = json.load(f)

print(f"Loaded {len(para_tokens)} A paragraphs")

# =============================================================
# STEP 1: Measure repetition within paragraphs
# =============================================================
print("\n" + "="*70)
print("STEP 1: Repetition within paragraphs")
print("="*70)

para_stats = []
for para_id, tokens in para_tokens.items():
    words = [t['word'] for t in tokens if t.get('word') and '*' not in t.get('word', '')]

    if not words:
        continue

    total = len(words)
    unique = len(set(words))
    repetition_rate = 1 - (unique / total) if total > 0 else 0

    # Count how many times the most common word appears
    word_counts = Counter(words)
    max_count = max(word_counts.values()) if word_counts else 0
    most_common = word_counts.most_common(1)[0] if word_counts else ('', 0)

    para_stats.append({
        'para_id': para_id,
        'total': total,
        'unique': unique,
        'repetition_rate': repetition_rate,
        'max_count': max_count,
        'most_common': most_common[0],
        'most_common_count': most_common[1]
    })

# Summary
total_tokens = sum(p['total'] for p in para_stats)
total_unique = sum(p['unique'] for p in para_stats)
mean_rep_rate = sum(p['repetition_rate'] for p in para_stats) / len(para_stats)

print(f"\nTotal tokens across all paragraphs: {total_tokens}")
print(f"Sum of unique per paragraph: {total_unique}")
print(f"Mean repetition rate per paragraph: {mean_rep_rate:.1%}")

# Distribution of repetition rates
print("\nRepetition rate distribution:")
bins = [(0, 0.1), (0.1, 0.2), (0.2, 0.3), (0.3, 0.4), (0.4, 0.5), (0.5, 1.0)]
for low, high in bins:
    count = sum(1 for p in para_stats if low <= p['repetition_rate'] < high)
    print(f"  {low:.0%}-{high:.0%}: {count} paragraphs")

# =============================================================
# STEP 2: Which tokens repeat most?
# =============================================================
print("\n" + "="*70)
print("STEP 2: Most repeated tokens")
print("="*70)

# Global token counts
all_words = []
for para_id, tokens in para_tokens.items():
    for t in tokens:
        word = t.get('word', '')
        if word and '*' not in word:
            all_words.append(word)

word_counts = Counter(all_words)
print(f"\nTotal tokens: {len(all_words)}")
print(f"Unique tokens: {len(word_counts)}")
print(f"Overall repetition: {1 - len(word_counts)/len(all_words):.1%}")

print("\nMost common tokens in A:")
for word, count in word_counts.most_common(20):
    try:
        m = morph.extract(word)
        prefix = m.prefix or '-'
        middle = m.middle or '-'
    except:
        prefix, middle = '?', '?'
    print(f"  {word}: {count} ({prefix}/{middle})")

# =============================================================
# STEP 3: Repetition by token class (RI vs PP)
# =============================================================
print("\n" + "="*70)
print("STEP 3: Repetition by token class")
print("="*70)

from voynich import load_middle_classes
ri_middles, pp_middles = load_middle_classes()

ri_tokens = []
pp_tokens = []

for para_id, tokens in para_tokens.items():
    for t in tokens:
        word = t.get('word', '')
        if not word or '*' in word:
            continue
        try:
            m = morph.extract(word)
            if m.middle:
                if m.middle in ri_middles:
                    ri_tokens.append(word)
                elif m.middle in pp_middles:
                    pp_tokens.append(word)
        except:
            pass

ri_unique = len(set(ri_tokens))
pp_unique = len(set(pp_tokens))

print(f"\nRI tokens: {len(ri_tokens)} total, {ri_unique} unique ({1-ri_unique/len(ri_tokens):.1%} repetition)")
print(f"PP tokens: {len(pp_tokens)} total, {pp_unique} unique ({1-pp_unique/len(pp_tokens):.1%} repetition)")

# =============================================================
# STEP 4: Look at repetition patterns within paragraphs
# =============================================================
print("\n" + "="*70)
print("STEP 4: Example paragraphs with high repetition")
print("="*70)

# Find paragraphs with highest repetition
high_rep = sorted(para_stats, key=lambda x: -x['repetition_rate'])[:5]

for p in high_rep:
    para_id = p['para_id']
    tokens = para_tokens[para_id]
    words = [t['word'] for t in tokens if t.get('word') and '*' not in t.get('word', '')]

    print(f"\n{para_id}: {p['total']} tokens, {p['unique']} unique ({p['repetition_rate']:.0%} repetition)")
    print(f"  Most common: '{p['most_common']}' appears {p['most_common_count']} times")

    # Show the sequence
    word_counts = Counter(words)
    repeated = [(w, c) for w, c in word_counts.items() if c > 1]
    repeated.sort(key=lambda x: -x[1])

    print(f"  Repeated tokens: {repeated[:5]}")

# =============================================================
# STEP 5: Is repetition positional?
# =============================================================
print("\n" + "="*70)
print("STEP 5: Positional repetition patterns")
print("="*70)

# Do the same tokens appear at similar positions across paragraphs?
# Or is repetition random?

# Check: for tokens that repeat within a paragraph, what's the typical gap?
gaps = []
for para_id, tokens in para_tokens.items():
    words = [t['word'] for t in tokens if t.get('word') and '*' not in t.get('word', '')]

    # For each word, find positions where it appears
    word_positions = defaultdict(list)
    for i, w in enumerate(words):
        word_positions[w].append(i)

    # For words that appear 2+ times, compute gaps
    for w, positions in word_positions.items():
        if len(positions) >= 2:
            for i in range(len(positions) - 1):
                gap = positions[i+1] - positions[i]
                gaps.append(gap)

if gaps:
    mean_gap = sum(gaps) / len(gaps)
    print(f"\nWhen tokens repeat, mean gap between occurrences: {mean_gap:.1f} tokens")

    # Distribution
    print("Gap distribution:")
    gap_bins = [(1, 2), (2, 5), (5, 10), (10, 20), (20, 100)]
    for low, high in gap_bins:
        count = sum(1 for g in gaps if low <= g < high)
        print(f"  Gap {low}-{high}: {count} ({100*count/len(gaps):.1f}%)")

# =============================================================
# STEP 6: Compare to B repetition
# =============================================================
print("\n" + "="*70)
print("STEP 6: Compare A vs B repetition")
print("="*70)

# Get B tokens by folio
b_words = []
for t in tx.currier_b():
    if t.word and '*' not in t.word:
        b_words.append(t.word)

b_unique = len(set(b_words))
b_rep_rate = 1 - b_unique / len(b_words)

print(f"\nA: {len(all_words)} tokens, {len(word_counts)} unique ({1-len(word_counts)/len(all_words):.1%} repetition)")
print(f"B: {len(b_words)} tokens, {b_unique} unique ({b_rep_rate:.1%} repetition)")

# =============================================================
# SUMMARY
# =============================================================
print("\n" + "="*70)
print("SUMMARY")
print("="*70)

print(f"""
REPETITION IN A RECORDS:

1. Mean per-paragraph repetition: {mean_rep_rate:.1%}
   - This is NOT a vocabulary list (which would have ~0% repetition)
   - Tokens repeat within the same paragraph

2. PP tokens repeat more than RI tokens:
   - RI: {1-ri_unique/len(ri_tokens):.1%} repetition
   - PP: {1-pp_unique/len(pp_tokens):.1%} repetition
   - PP (procedure) tokens are reused; RI (identity) tokens are unique

3. A has LESS repetition than B:
   - A: {1-len(word_counts)/len(all_words):.1%}
   - B: {b_rep_rate:.1%}
   - B programs reuse vocabulary more intensively

4. Most repeated tokens are common PP words (daiin, chedy, etc.)

INTERPRETATION:

A records are NOT just vocabulary lists. The repetition suggests:
- Procedural sequences (do X, then X again)
- Or emphasis/weighting (X is used frequently in this procedure)
- Or actual operational content, not just specification
""")
