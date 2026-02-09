#!/usr/bin/env python3
"""
Test: Are -am/-y tokens STATE MARKERS rather than apparatus references?

Predictions if STATE MARKERS:
1. Specific operation->state mappings (each variant follows specific operations)
2. No co-occurrence (can't be two states at once)
3. Kernel type correlation (state confirmation in phase-managed contexts)
4. Variant differentiation (oly vs oldy vs daly vs ldy have distinct predecessors)
"""

import sys
from pathlib import Path
from collections import defaultdict, Counter
import json
import numpy as np
from scipy import stats as scipy_stats

sys.path.insert(0, str(Path(__file__).parent))
from voynich import Transcript

class_map_path = Path(__file__).parent.parent / 'phases' / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
with open(class_map_path) as f:
    class_data = json.load(f)
token_to_role = class_data.get('token_to_role', {})

tx = Transcript()
GALLOWS = {'k', 't', 'p', 'f'}

AM_CLASS = {'am', 'dam', 'otam'}
Y_CLASS = {'oly', 'oldy', 'daly', 'ldy'}
ALL_TOKENS = AM_CLASS | Y_CLASS | {'ary'}

# Build line data
folio_lines = defaultdict(lambda: defaultdict(list))
folio_section = {}

for token in tx.currier_b():
    if '*' in token.word:
        continue
    folio_lines[token.folio][token.line].append(token.word)
    if token.folio not in folio_section:
        folio_section[token.folio] = token.section

print("="*70)
print("STATE MARKER HYPOTHESIS TEST")
print("="*70)

# TEST 1: CO-OCCURRENCE
print(f"\n{'='*70}")
print("TEST 1: CO-OCCURRENCE (can't be two states at once)")
print("="*70)

lines_with_multiple = 0
lines_with_am_and_y = 0
lines_with_any = 0

cooccurrence_pairs = Counter()

for folio in folio_lines:
    for line in folio_lines[folio]:
        words = folio_lines[folio][line]

        markers_in_line = [w for w in words if w in ALL_TOKENS]

        if len(markers_in_line) >= 1:
            lines_with_any += 1

        if len(markers_in_line) >= 2:
            lines_with_multiple += 1
            # Check if both AM and Y present
            has_am = any(w in AM_CLASS for w in markers_in_line)
            has_y = any(w in Y_CLASS for w in markers_in_line)
            if has_am and has_y:
                lines_with_am_and_y += 1

            # Record pairs
            for i, m1 in enumerate(markers_in_line):
                for m2 in markers_in_line[i+1:]:
                    cooccurrence_pairs[(m1, m2)] += 1

print(f"\nLines with any -am/-y token: {lines_with_any}")
print(f"Lines with 2+ tokens: {lines_with_multiple} ({100*lines_with_multiple/lines_with_any:.1f}%)")
print(f"Lines with BOTH -am AND -y: {lines_with_am_and_y}")

if lines_with_multiple > 0:
    print(f"\nCo-occurring pairs:")
    for (m1, m2), count in cooccurrence_pairs.most_common(10):
        print(f"  {m1} + {m2}: {count}")

if lines_with_am_and_y == 0:
    print("\n-> SUPPORTS STATE HYPOTHESIS: -am and -y never co-occur")
elif lines_with_am_and_y < 5:
    print(f"\n-> WEAK SUPPORT: Only {lines_with_am_and_y} lines with both (rare)")
else:
    print(f"\n-> CONTRADICTS: {lines_with_am_and_y} lines have both -am and -y")

# TEST 2: VARIANT-SPECIFIC PREDECESSORS
print(f"\n{'='*70}")
print("TEST 2: VARIANT-SPECIFIC PREDECESSORS")
print("="*70)

variant_predecessors = {token: Counter() for token in Y_CLASS}

for folio in folio_lines:
    for line in folio_lines[folio]:
        words = folio_lines[folio][line]
        for i, word in enumerate(words):
            if word in Y_CLASS and i > 0:
                pred = words[i-1]
                variant_predecessors[word][pred] += 1

print(f"\nTop 5 predecessors for each -y variant:")
for variant in sorted(Y_CLASS):
    preds = variant_predecessors[variant]
    if sum(preds.values()) < 5:
        continue
    print(f"\n  {variant} (n={sum(preds.values())}):")
    for pred, count in preds.most_common(5):
        role = token_to_role.get(pred, '?')
        print(f"    {pred:<15} {count:<4} {role}")

# Calculate overlap between variants
print(f"\nPredecessor overlap between -y variants:")
variants = [v for v in Y_CLASS if sum(variant_predecessors[v].values()) >= 10]

if len(variants) >= 2:
    for i, v1 in enumerate(variants):
        for v2 in variants[i+1:]:
            preds1 = set(variant_predecessors[v1].keys())
            preds2 = set(variant_predecessors[v2].keys())
            overlap = len(preds1 & preds2)
            union = len(preds1 | preds2)
            jaccard = overlap / union if union > 0 else 0
            print(f"  {v1} vs {v2}: Jaccard = {jaccard:.2f} ({overlap}/{union} shared)")

# TEST 3: KERNEL TYPE CORRELATION
print(f"\n{'='*70}")
print("TEST 3: KERNEL TYPE CORRELATION")
print("="*70)

def get_paragraph_kernel_type(words):
    """Classify paragraph by dominant kernel."""
    if len(words) < 10:
        return None

    k = sum(w.count('k') for w in words)
    h = sum(w.count('h') for w in words)
    e = sum(w.count('e') for w in words)
    total = k + h + e

    if total < 10:
        return None

    k_pct = k / total
    h_pct = h / total

    if k_pct > 0.35:
        return 'HIGH_K'
    elif h_pct > 0.35:
        return 'HIGH_H'
    else:
        return 'BALANCED'

def get_paragraphs(folio):
    """Extract paragraphs from folio."""
    lines = folio_lines[folio]
    paragraphs = []
    current_para = []

    for line_num in sorted(lines.keys()):
        words = lines[line_num]
        if not words:
            continue
        first_word = words[0]
        if first_word and first_word[0] in GALLOWS:
            if current_para:
                paragraphs.append(current_para)
            current_para = [(line_num, words)]
        else:
            current_para.append((line_num, words))

    if current_para:
        paragraphs.append(current_para)

    return paragraphs

# Count -y tokens by paragraph kernel type
y_by_kernel = Counter()
am_by_kernel = Counter()
para_by_kernel = Counter()

for folio in folio_lines:
    paras = get_paragraphs(folio)
    for para in paras:
        all_words = [w for _, words in para for w in words]
        kernel_type = get_paragraph_kernel_type(all_words)

        if kernel_type:
            para_by_kernel[kernel_type] += 1

            y_count = sum(1 for w in all_words if w in Y_CLASS)
            am_count = sum(1 for w in all_words if w in AM_CLASS)

            if y_count > 0:
                y_by_kernel[kernel_type] += 1
            if am_count > 0:
                am_by_kernel[kernel_type] += 1

print(f"\n{'Kernel Type':<12} {'Paragraphs':<12} {'With -y':<10} {'Rate %':<10} {'With -am':<10} {'Rate %':<10}")
print("-"*70)

for kt in ['HIGH_H', 'HIGH_K', 'BALANCED']:
    total = para_by_kernel.get(kt, 0)
    y_count = y_by_kernel.get(kt, 0)
    am_count = am_by_kernel.get(kt, 0)

    y_rate = 100 * y_count / total if total > 0 else 0
    am_rate = 100 * am_count / total if total > 0 else 0

    print(f"{kt:<12} {total:<12} {y_count:<10} {y_rate:<10.1f} {am_count:<10} {am_rate:<10.1f}")

# Chi-square for -y distribution across kernel types
print(f"\nChi-square: -y rate varies by kernel type?")
observed_y = [y_by_kernel.get(kt, 0) for kt in ['HIGH_H', 'HIGH_K', 'BALANCED']]
expected_rate = sum(observed_y) / sum(para_by_kernel.values())
expected_y = [para_by_kernel.get(kt, 0) * expected_rate for kt in ['HIGH_H', 'HIGH_K', 'BALANCED']]

if all(e >= 5 for e in expected_y):
    chi2, p_val = scipy_stats.chisquare(observed_y, expected_y)
    print(f"Chi-square = {chi2:.2f}, p = {p_val:.4f}")
    if p_val < 0.05:
        print("-> SUPPORTS STATE HYPOTHESIS: -y rate varies by kernel type")
    else:
        print("-> No significant variation")

# TEST 4: SPECIFIC OPERATION->STATE MAPPINGS
print(f"\n{'='*70}")
print("TEST 4: OPERATION -> STATE MAPPING SPECIFICITY")
print("="*70)

# For each ENERGY_OPERATOR predecessor, which -y variant does it prefer?
energy_to_y = defaultdict(Counter)

for folio in folio_lines:
    for line in folio_lines[folio]:
        words = folio_lines[folio][line]
        for i, word in enumerate(words):
            if word in Y_CLASS and i > 0:
                pred = words[i-1]
                if token_to_role.get(pred) == 'ENERGY_OPERATOR':
                    energy_to_y[pred][word] += 1

print(f"\nENERGY_OPERATOR -> -y variant preferences:")
print(f"{'Energy Op':<15} {'n':<6} {'Preferred -y':<12} {'%':<8} {'Entropy':<10}")
print("-"*55)

for energy_op, y_counts in sorted(energy_to_y.items(), key=lambda x: -sum(x[1].values())):
    total = sum(y_counts.values())
    if total < 3:
        continue

    top_y, top_count = y_counts.most_common(1)[0]
    pct = 100 * top_count / total

    # Calculate entropy (low = specific, high = random)
    probs = [c/total for c in y_counts.values()]
    entropy = -sum(p * np.log2(p) for p in probs if p > 0)
    max_entropy = np.log2(len(Y_CLASS))  # Maximum if uniform

    print(f"{energy_op:<15} {total:<6} {top_y:<12} {pct:<8.0f} {entropy:.2f}/{max_entropy:.2f}")

# TEST 5: SEQUENCE PATTERNS
print(f"\n{'='*70}")
print("TEST 5: STATE SEQUENCE PATTERNS")
print("="*70)

# Do state markers appear in regular patterns within paragraphs?
para_marker_positions = []

for folio in folio_lines:
    paras = get_paragraphs(folio)
    for para in paras:
        all_words = [w for _, words in para for w in words]
        n = len(all_words)
        if n < 5:
            continue

        positions = []
        for i, w in enumerate(all_words):
            if w in ALL_TOKENS:
                positions.append(i / (n-1) if n > 1 else 0.5)

        if len(positions) >= 2:
            para_marker_positions.append({
                'n_markers': len(positions),
                'positions': positions,
                'spacing': [positions[i+1] - positions[i] for i in range(len(positions)-1)]
            })

if para_marker_positions:
    all_spacings = [s for p in para_marker_positions for s in p['spacing']]
    print(f"\nParagraphs with 2+ markers: {len(para_marker_positions)}")
    print(f"Mean spacing between markers: {np.mean(all_spacings):.3f} (normalized)")
    print(f"Std spacing: {np.std(all_spacings):.3f}")

    # Is spacing regular?
    cv = np.std(all_spacings) / np.mean(all_spacings) if np.mean(all_spacings) > 0 else 0
    print(f"Coefficient of variation: {cv:.2f}")

    if cv < 0.5:
        print("-> SUPPORTS STATE HYPOTHESIS: Regular spacing suggests structured state checkpoints")
    else:
        print("-> Irregular spacing (CV > 0.5)")

# SUMMARY
print(f"\n{'='*70}")
print("SUMMARY: STATE MARKER HYPOTHESIS")
print("="*70)

print("""
STATE MARKER PREDICTIONS:

1. NO CO-OCCURRENCE: If states are mutually exclusive,
   -am and -y shouldn't appear on same line.

2. VARIANT SPECIFICITY: Different -y tokens (oly, oldy, daly, ldy)
   should follow different operations if they encode different states.

3. KERNEL CORRELATION: State confirmation should matter more
   in phase-managed (HIGH_H) contexts.

4. OPERATION->STATE MAPPING: Specific ENERGY operations should
   prefer specific -y variants (low entropy).

5. REGULAR SPACING: State checkpoints should appear at
   regular intervals in processing sequences.
""")

# Save results
output = {
    'lines_with_multiple': lines_with_multiple,
    'lines_with_am_and_y': lines_with_am_and_y,
    'y_by_kernel': dict(y_by_kernel),
    'am_by_kernel': dict(am_by_kernel),
}

output_path = Path(__file__).parent.parent / 'results' / 'state_marker_test.json'
with open(output_path, 'w') as f:
    json.dump(output, f, indent=2)

print(f"\nResults saved to {output_path}")
