"""
T8: Repetition as Boundary Marker

Hypothesis: If A operational units provide vocabulary allowances, repetition
within a unit is redundant. Token repetition may signal unit boundaries.

Tests:
1. Within-line repetition rate (should be low if lines are units)
2. Within-paragraph repetition rate (should be low if paragraphs are units)
3. Cross-boundary repetition (does first token of new unit repeat from previous?)
4. Gallows-initial correlation (do gallows lines start "fresh" vocabulary?)
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
print("T8: REPETITION AS BOUNDARY MARKER")
print("=" * 70)

GALLOWS = {'k', 't', 'p', 'f'}

def starts_with_gallows(word):
    if not word:
        return False
    w = word.strip()
    return bool(w) and w[0] in GALLOWS

# Collect A tokens by folio and line
print("\nStep 1: Collecting A tokens...")

a_tokens_by_line = defaultdict(list)  # (folio, line) -> [tokens]
a_tokens_by_folio = defaultdict(list)  # folio -> [tokens in order]

for token in tx.currier_a():
    w = token.word.strip()
    if not w or '*' in w:
        continue

    m = morph.extract(w)
    a_tokens_by_line[(token.folio, token.line)].append({
        'word': w,
        'middle': m.middle,
        'folio': token.folio,
        'line': token.line,
    })
    a_tokens_by_folio[token.folio].append({
        'word': w,
        'middle': m.middle,
        'line': token.line,
    })

print(f"  Lines: {len(a_tokens_by_line)}")
print(f"  Folios: {len(a_tokens_by_folio)}")

# Test 1: Within-line repetition
print("\n" + "=" * 70)
print("TEST 1: WITHIN-LINE TOKEN REPETITION")
print("=" * 70)

lines_with_repetition = 0
total_lines = 0
within_line_repeats = 0
total_tokens = 0

for (folio, line), tokens in a_tokens_by_line.items():
    if len(tokens) < 2:
        continue

    total_lines += 1
    total_tokens += len(tokens)

    words = [t['word'] for t in tokens]
    word_counts = Counter(words)

    repeats_in_line = sum(c - 1 for c in word_counts.values() if c > 1)
    within_line_repeats += repeats_in_line

    if any(c > 1 for c in word_counts.values()):
        lines_with_repetition += 1

print(f"  Lines with 2+ tokens: {total_lines}")
print(f"  Lines with any repetition: {lines_with_repetition} ({lines_with_repetition/total_lines*100:.1f}%)")
print(f"  Total repeated tokens: {within_line_repeats} ({within_line_repeats/total_tokens*100:.2f}%)")

# Test 2: Within-paragraph repetition
print("\n" + "=" * 70)
print("TEST 2: WITHIN-PARAGRAPH TOKEN REPETITION")
print("=" * 70)

# Build paragraphs
paragraphs = []  # list of (folio, para_num, [tokens])

for folio in sorted(a_tokens_by_folio.keys()):
    tokens = a_tokens_by_folio[folio]

    current_para = []
    para_num = 0
    prev_line = None

    for t in tokens:
        # Check if this is first token of a new line
        if t['line'] != prev_line:
            # Check if this line starts with gallows
            line_tokens = a_tokens_by_line[(folio, t['line'])]
            if line_tokens and starts_with_gallows(line_tokens[0]['word']):
                # New paragraph
                if current_para:
                    paragraphs.append((folio, para_num, current_para))
                current_para = []
                para_num += 1

        current_para.append(t)
        prev_line = t['line']

    if current_para:
        paragraphs.append((folio, para_num, current_para))

print(f"  Total paragraphs: {len(paragraphs)}")

paras_with_repetition = 0
within_para_repeats = 0
total_para_tokens = 0

for folio, para_num, tokens in paragraphs:
    if len(tokens) < 2:
        continue

    total_para_tokens += len(tokens)

    words = [t['word'] for t in tokens]
    word_counts = Counter(words)

    repeats = sum(c - 1 for c in word_counts.values() if c > 1)
    within_para_repeats += repeats

    if any(c > 1 for c in word_counts.values()):
        paras_with_repetition += 1

print(f"  Paragraphs with repetition: {paras_with_repetition} ({paras_with_repetition/len(paragraphs)*100:.1f}%)")
print(f"  Repeated tokens in paragraphs: {within_para_repeats} ({within_para_repeats/total_para_tokens*100:.2f}%)")

# Test 3: Cross-line repetition (does new line repeat tokens from previous?)
print("\n" + "=" * 70)
print("TEST 3: CROSS-LINE REPETITION")
print("=" * 70)

cross_line_repeats = 0
cross_line_pairs = 0

for folio in sorted(a_tokens_by_folio.keys()):
    lines = sorted(set(t['line'] for t in a_tokens_by_folio[folio]))

    for i in range(1, len(lines)):
        prev_line = lines[i-1]
        curr_line = lines[i]

        prev_tokens = set(t['word'] for t in a_tokens_by_line[(folio, prev_line)])
        curr_tokens = [t['word'] for t in a_tokens_by_line[(folio, curr_line)]]

        if not prev_tokens or not curr_tokens:
            continue

        cross_line_pairs += 1

        # How many tokens in current line appeared in previous line?
        repeats = sum(1 for w in curr_tokens if w in prev_tokens)
        cross_line_repeats += repeats

print(f"  Adjacent line pairs: {cross_line_pairs}")
print(f"  Tokens repeated from previous line: {cross_line_repeats}")
print(f"  Mean repeats per transition: {cross_line_repeats/cross_line_pairs:.2f}")

# Test 4: Gallows-initial lines - do they "reset" vocabulary?
print("\n" + "=" * 70)
print("TEST 4: GALLOWS-INITIAL VOCABULARY RESET")
print("=" * 70)

gallows_repeat_rate = []
non_gallows_repeat_rate = []

for folio in sorted(a_tokens_by_folio.keys()):
    lines = sorted(set(t['line'] for t in a_tokens_by_folio[folio]))

    for i in range(1, len(lines)):
        prev_line = lines[i-1]
        curr_line = lines[i]

        prev_tokens = set(t['word'] for t in a_tokens_by_line[(folio, prev_line)])
        curr_tokens = a_tokens_by_line[(folio, curr_line)]

        if not prev_tokens or not curr_tokens:
            continue

        # Is this line gallows-initial?
        is_gallows = starts_with_gallows(curr_tokens[0]['word'])

        # What fraction of current line tokens appeared in previous line?
        curr_words = [t['word'] for t in curr_tokens]
        repeat_rate = sum(1 for w in curr_words if w in prev_tokens) / len(curr_words)

        if is_gallows:
            gallows_repeat_rate.append(repeat_rate)
        else:
            non_gallows_repeat_rate.append(repeat_rate)

mean_gallows = np.mean(gallows_repeat_rate) if gallows_repeat_rate else 0
mean_non_gallows = np.mean(non_gallows_repeat_rate) if non_gallows_repeat_rate else 0

print(f"  Gallows-initial lines: {len(gallows_repeat_rate)}")
print(f"  Non-gallows lines: {len(non_gallows_repeat_rate)}")
print(f"  ")
print(f"  Mean repeat rate from previous line:")
print(f"    Gallows-initial: {mean_gallows:.1%}")
print(f"    Non-gallows: {mean_non_gallows:.1%}")
print(f"    Ratio: {mean_non_gallows/mean_gallows:.2f}x" if mean_gallows > 0 else "    (division by zero)")

# Statistical test
from scipy.stats import mannwhitneyu
if len(gallows_repeat_rate) > 10 and len(non_gallows_repeat_rate) > 10:
    stat, p_val = mannwhitneyu(gallows_repeat_rate, non_gallows_repeat_rate)
    print(f"  Mann-Whitney U: p={p_val:.2e}")

    if mean_gallows < mean_non_gallows and p_val < 0.05:
        print(f"  --> Gallows lines have LOWER repeat rate (vocabulary reset)")
    elif p_val >= 0.05:
        print(f"  --> No significant difference")

# Test 5: First repeated token as boundary marker
print("\n" + "=" * 70)
print("TEST 5: TOKEN REPETITION AS BOUNDARY SIGNAL")
print("=" * 70)

# Within each folio, track running vocabulary
# When a token repeats, note the position

repeat_positions = []  # position within folio where repeat occurs
gallows_positions = []  # position within folio of gallows-initial lines

for folio in sorted(a_tokens_by_folio.keys()):
    tokens = a_tokens_by_folio[folio]

    seen_words = set()
    seen_middles = set()

    for i, t in enumerate(tokens):
        # Track gallows positions
        if i == 0 or tokens[i-1]['line'] != t['line']:
            # First token of line
            if starts_with_gallows(t['word']):
                gallows_positions.append(i / len(tokens))  # Normalized position

        # Track repetition
        if t['word'] in seen_words:
            repeat_positions.append(i / len(tokens))  # Normalized position

        seen_words.add(t['word'])

print(f"  Total repeats (folio-level): {len(repeat_positions)}")
print(f"  Total gallows-initial tokens: {len(gallows_positions)}")

if repeat_positions and gallows_positions:
    print(f"  ")
    print(f"  Mean position of repeats: {np.mean(repeat_positions):.3f}")
    print(f"  Mean position of gallows: {np.mean(gallows_positions):.3f}")

# Test 6: Do repeats cluster near gallows lines?
print("\n" + "=" * 70)
print("TEST 6: REPEAT-GALLOWS PROXIMITY")
print("=" * 70)

# For each folio, measure distance from each repeat to nearest gallows line
repeat_to_gallows_dist = []

for folio in sorted(a_tokens_by_folio.keys()):
    tokens = a_tokens_by_folio[folio]
    if len(tokens) < 5:
        continue

    # Find gallows positions (token indices)
    gallows_indices = []
    for i, t in enumerate(tokens):
        if i == 0 or tokens[i-1]['line'] != t['line']:
            if starts_with_gallows(t['word']):
                gallows_indices.append(i)

    if not gallows_indices:
        continue

    # Find repeat positions
    seen = set()
    for i, t in enumerate(tokens):
        if t['word'] in seen:
            # Find distance to nearest gallows
            min_dist = min(abs(i - g) for g in gallows_indices)
            repeat_to_gallows_dist.append(min_dist)
        seen.add(t['word'])

if repeat_to_gallows_dist:
    print(f"  Mean distance from repeat to nearest gallows: {np.mean(repeat_to_gallows_dist):.1f} tokens")
    print(f"  Median distance: {np.median(repeat_to_gallows_dist):.1f} tokens")

# Summary
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

print(f"""
Within-line repetition: {lines_with_repetition/total_lines*100:.1f}% of lines have repeats
Within-paragraph repetition: {paras_with_repetition/len(paragraphs)*100:.1f}% of paragraphs have repeats

Gallows-initial lines have {'LOWER' if mean_gallows < mean_non_gallows else 'HIGHER'} repeat rate
from previous line ({mean_gallows:.1%} vs {mean_non_gallows:.1%})

INTERPRETATION:
""")

if lines_with_repetition/total_lines < 0.10:
    print("- Lines are largely non-repetitive (supports LINE as unit)")
else:
    print("- Lines have notable repetition (LINE may not be unit)")

if mean_gallows < mean_non_gallows * 0.8:
    print("- Gallows lines 'reset' vocabulary (supports PARAGRAPH as unit)")
else:
    print("- No clear vocabulary reset at gallows (weak paragraph boundary)")

# Save results
results = {
    'within_line_repetition_pct': float(lines_with_repetition/total_lines*100),
    'within_para_repetition_pct': float(paras_with_repetition/len(paragraphs)*100),
    'gallows_repeat_rate': float(mean_gallows),
    'non_gallows_repeat_rate': float(mean_non_gallows),
    'repeat_rate_ratio': float(mean_non_gallows/mean_gallows) if mean_gallows > 0 else None,
}

out_path = PROJECT_ROOT / 'phases' / 'A_RECORD_B_ROUTING_TOPOLOGY' / 'results' / 't8_repetition_boundary.json'
with open(out_path, 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to {out_path.name}")
