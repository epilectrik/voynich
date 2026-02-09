"""
111_ritual_pattern_test.py

RITUAL PATTERN TEST

Test whether Voynich shows liturgical/ritual structural patterns.

Components:
1. Call-and-response: Alternating patterns between token classes
2. Formulaic openings: Line-initial token clustering
3. Boundary refrains: Repeated sequences at paragraph/folio boundaries
4. Positive control: Test same metrics on known liturgical text (Latin mass)

If Voynich shows null on all tests AND positive control shows signal,
ritual hypothesis is falsified.
"""

import sys
import math
from pathlib import Path
from collections import defaultdict, Counter

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'scripts'))
from voynich import Transcript, Morphology, load_middle_classes

print("="*70)
print("RITUAL PATTERN TEST")
print("="*70)

tx = Transcript()
morph = Morphology()

# Load instruction class mapping
import json
class_map_path = Path(__file__).parent.parent.parent / 'CLASS_COSURVIVAL_TEST' / 'results' / 'class_token_map.json'
with open(class_map_path) as f:
    class_data = json.load(f)

word_to_class = class_data.get('token_to_class', {})

def get_class(word):
    """Get instruction class for a word."""
    if word in word_to_class:
        return f"C{word_to_class[word]}"
    try:
        m = morph.extract(word)
        if m.middle and m.middle in word_to_class:
            return f"C{word_to_class[m.middle]}"
    except:
        pass
    return None

# =============================================================
# BUILD VOYNICH DATA
# =============================================================
print("\nBuilding Voynich class sequences...")

# Group by folio and line
b_by_folio_line = defaultdict(list)
for t in tx.currier_b():
    if t.word and '*' not in t.word:
        cls = get_class(t.word)
        if cls:
            b_by_folio_line[(t.folio, t.line)].append(cls)

# Build class sequence for B
b_class_sequence = []
b_line_initials = []
b_folio_boundaries = []

prev_folio = None
for (folio, line) in sorted(b_by_folio_line.keys()):
    classes = b_by_folio_line[(folio, line)]
    if classes:
        b_line_initials.append(classes[0])
        if folio != prev_folio:
            b_folio_boundaries.append(len(b_class_sequence))
            prev_folio = folio
        b_class_sequence.extend(classes)

print(f"Total classified tokens: {len(b_class_sequence)}")
print(f"Lines: {len(b_line_initials)}")
print(f"Folios: {len(b_folio_boundaries)}")

# =============================================================
# TEST 1: CALL-AND-RESPONSE (ALTERNATING PATTERNS)
# =============================================================
print("\n" + "="*70)
print("TEST 1: CALL-AND-RESPONSE (Alternating Patterns)")
print("="*70)

def measure_alternation(sequence):
    """
    Measure tendency for class X to be followed by class Y and vice versa.
    High alternation = call-and-response pattern.
    """
    if len(sequence) < 3:
        return 0, 0

    # Count X->Y->X patterns (immediate return to same class)
    immediate_returns = 0
    # Count X->Y->Z where Z != X (no return)
    no_returns = 0

    for i in range(len(sequence) - 2):
        if sequence[i] == sequence[i+2]:
            immediate_returns += 1
        else:
            no_returns += 1

    total = immediate_returns + no_returns
    if total == 0:
        return 0, 0

    return immediate_returns / total, total

def measure_period_2_autocorr(sequence):
    """
    Measure autocorrelation at lag 2.
    Liturgy with call-response should show high lag-2 correlation.
    """
    if len(sequence) < 3:
        return 0

    matches = sum(1 for i in range(len(sequence)-2) if sequence[i] == sequence[i+2])
    return matches / (len(sequence) - 2)

voynich_alternation, voynich_total = measure_alternation(b_class_sequence)
voynich_lag2 = measure_period_2_autocorr(b_class_sequence)

print(f"\nVoynich B:")
print(f"  Immediate return rate (X->Y->X): {voynich_alternation:.1%}")
print(f"  Lag-2 autocorrelation: {voynich_lag2:.1%}")

# Baseline: shuffled sequence
import random
shuffled = b_class_sequence.copy()
random.shuffle(shuffled)
shuffled_alternation, _ = measure_alternation(shuffled)
shuffled_lag2 = measure_period_2_autocorr(shuffled)

print(f"\nShuffled baseline:")
print(f"  Immediate return rate: {shuffled_alternation:.1%}")
print(f"  Lag-2 autocorrelation: {shuffled_lag2:.1%}")

# Expected for call-response
print(f"\nExpected for call-response: ~30-50% immediate return rate")

# =============================================================
# TEST 2: FORMULAIC OPENINGS
# =============================================================
print("\n" + "="*70)
print("TEST 2: FORMULAIC OPENINGS (Line-Initial Clustering)")
print("="*70)

initial_counts = Counter(b_line_initials)
n_unique_initials = len(initial_counts)
total_lines = len(b_line_initials)

# Concentration: what fraction of lines use top-5 initials?
top5_initials = initial_counts.most_common(5)
top5_fraction = sum(c for _, c in top5_initials) / total_lines

# Entropy of initial distribution
def entropy(counter):
    total = sum(counter.values())
    h = 0
    for count in counter.values():
        if count > 0:
            p = count / total
            h -= p * math.log2(p)
    return h

initial_entropy = entropy(initial_counts)
max_entropy = math.log2(49)  # 49 classes

print(f"\nVoynich line-initial distribution:")
print(f"  Unique initials: {n_unique_initials} of 49 classes")
print(f"  Entropy: {initial_entropy:.2f} bits (max: {max_entropy:.2f})")
print(f"  Top-5 concentration: {top5_fraction:.1%}")

print(f"\nTop 5 line-initial classes:")
for cls, count in top5_initials:
    print(f"  {cls}: {count} ({count/total_lines:.1%})")

# Compare to overall class distribution
overall_counts = Counter(b_class_sequence)
overall_entropy = entropy(overall_counts)
print(f"\nOverall class entropy: {overall_entropy:.2f} bits")
print(f"Initial vs overall entropy ratio: {initial_entropy/overall_entropy:.2f}")

# Liturgy would show LOWER entropy at line starts (formulaic invocations)
print(f"\nExpected for liturgy: Initial entropy << overall entropy")

# =============================================================
# TEST 3: BOUNDARY REFRAINS
# =============================================================
print("\n" + "="*70)
print("TEST 3: BOUNDARY REFRAINS (Repeated Sequences)")
print("="*70)

def find_ngram_repeats(sequence, n=3, boundary_width=10):
    """
    Find n-gram repetitions, especially at boundaries.
    """
    ngrams = []
    for i in range(len(sequence) - n + 1):
        ngrams.append(tuple(sequence[i:i+n]))

    ngram_counts = Counter(ngrams)
    repeated = {ng: c for ng, c in ngram_counts.items() if c > 1}

    return len(repeated), len(ngrams), ngram_counts

repeated_3grams, total_3grams, ngram_counts = find_ngram_repeats(b_class_sequence, n=3)
repeated_4grams, total_4grams, _ = find_ngram_repeats(b_class_sequence, n=4)

print(f"\nVoynich n-gram repetition:")
print(f"  Repeated 3-grams: {repeated_3grams} ({repeated_3grams/total_3grams:.1%} of {total_3grams})")
print(f"  Repeated 4-grams: {repeated_4grams} ({repeated_4grams/total_4grams:.1%})")

# Most common n-grams
print(f"\nMost common 3-grams:")
for ng, count in ngram_counts.most_common(5):
    print(f"  {ng}: {count}")

# Check near folio boundaries
boundary_ngrams = Counter()
for boundary_idx in b_folio_boundaries[1:]:  # Skip first
    if boundary_idx >= 5 and boundary_idx < len(b_class_sequence) - 5:
        # 5 tokens before and after boundary
        pre = tuple(b_class_sequence[boundary_idx-3:boundary_idx])
        post = tuple(b_class_sequence[boundary_idx:boundary_idx+3])
        boundary_ngrams[pre] += 1
        boundary_ngrams[post] += 1

print(f"\nFolio boundary 3-grams (repeated):")
repeated_boundary = {ng: c for ng, c in boundary_ngrams.items() if c > 1}
print(f"  Repeated boundary sequences: {len(repeated_boundary)}")
for ng, count in sorted(repeated_boundary.items(), key=lambda x: -x[1])[:5]:
    print(f"  {ng}: {count}")

# =============================================================
# POSITIVE CONTROL: SYNTHETIC LITURGICAL TEXT
# =============================================================
print("\n" + "="*70)
print("POSITIVE CONTROL: SYNTHETIC LITURGICAL PATTERN")
print("="*70)

def generate_liturgical_sequence(n_tokens=5000, n_classes=49):
    """
    Generate synthetic liturgical-style text:
    - Strong call-response (A->B->A patterns)
    - Formulaic openings (few classes dominate line starts)
    - Boundary refrains (repeated sequences at boundaries)
    """
    sequence = []
    line_initials = []
    boundaries = []

    # Formulaic openings - 5 classes dominate
    opening_classes = [f"C{i}" for i in range(1, 6)]

    # Current position
    pos = 0
    line_len = 0
    folio_len = 0

    while pos < n_tokens:
        # Start new line?
        if line_len == 0:
            # Formulaic opening (80% from top 5)
            if random.random() < 0.8:
                cls = random.choice(opening_classes)
            else:
                cls = f"C{random.randint(1, n_classes)}"
            line_initials.append(cls)
            sequence.append(cls)
            line_len = 1
            pos += 1

            # Folio boundary refrain
            if folio_len > 50 and random.random() < 0.1:
                # Insert refrain
                refrain = [f"C{random.randint(1, 10)}" for _ in range(3)]
                sequence.extend(refrain)
                pos += 3
                boundaries.append(pos)
                folio_len = 0

        else:
            # Call-response pattern (50% chance of X->Y->X)
            if len(sequence) >= 2 and random.random() < 0.5:
                sequence.append(sequence[-2])  # Return to 2 steps ago
            else:
                sequence.append(f"C{random.randint(1, n_classes)}")
            pos += 1
            line_len += 1

            # End line
            if line_len > random.randint(5, 12):
                line_len = 0
                folio_len += 1

    return sequence, line_initials, boundaries

liturgy_seq, liturgy_initials, liturgy_boundaries = generate_liturgical_sequence(len(b_class_sequence))

liturgy_alternation, _ = measure_alternation(liturgy_seq)
liturgy_lag2 = measure_period_2_autocorr(liturgy_seq)
liturgy_initial_entropy = entropy(Counter(liturgy_initials))
liturgy_repeated_3, liturgy_total_3, _ = find_ngram_repeats(liturgy_seq, n=3)

print(f"\nSynthetic liturgical text:")
print(f"  Immediate return rate: {liturgy_alternation:.1%}")
print(f"  Lag-2 autocorrelation: {liturgy_lag2:.1%}")
print(f"  Initial entropy: {liturgy_initial_entropy:.2f} bits")
print(f"  Repeated 3-grams: {liturgy_repeated_3} ({liturgy_repeated_3/liturgy_total_3:.1%})")

# =============================================================
# SUMMARY
# =============================================================
print("\n" + "="*70)
print("SUMMARY: RITUAL PATTERN COMPARISON")
print("="*70)

print(f"""
                        Voynich     Liturgical   Shuffled
                                    (synthetic)  baseline
Alternation (X->Y->X):  {voynich_alternation:.1%}       {liturgy_alternation:.1%}        {shuffled_alternation:.1%}
Lag-2 autocorr:         {voynich_lag2:.1%}       {liturgy_lag2:.1%}        {shuffled_lag2:.1%}
Initial entropy:        {initial_entropy:.2f}        {liturgy_initial_entropy:.2f}         N/A
Repeated 3-grams:       {repeated_3grams/total_3grams:.1%}        {liturgy_repeated_3/liturgy_total_3:.1%}         ~0%

INTERPRETATION:
""")

# Diagnose
ritual_score = 0
if voynich_alternation > shuffled_alternation * 1.5:
    print("- Alternation ELEVATED vs baseline: +1 ritual point")
    ritual_score += 1
else:
    print("- Alternation similar to baseline: 0 ritual points")

if initial_entropy < overall_entropy * 0.8:
    print("- Initial entropy REDUCED (formulaic): +1 ritual point")
    ritual_score += 1
else:
    print("- Initial entropy similar to overall: 0 ritual points")

if repeated_3grams / total_3grams > 0.01:
    print("- High 3-gram repetition (refrains): +1 ritual point")
    ritual_score += 1
else:
    print("- Low 3-gram repetition: 0 ritual points")

print(f"\nRITUAL SCORE: {ritual_score}/3")
if ritual_score >= 2:
    print("-> Ritual hypothesis SUPPORTED")
elif ritual_score == 1:
    print("-> Weak ritual signal, inconclusive")
else:
    print("-> Ritual hypothesis NOT SUPPORTED")
