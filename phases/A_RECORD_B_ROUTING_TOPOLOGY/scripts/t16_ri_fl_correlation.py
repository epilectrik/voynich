"""
T16: RI-FL State Correlation Test

C777 established that FL MIDDLEs in B encode material state progression:
- 'i'-forms at process start (pos ~0.30)
- 'y'-forms at process end (pos ~0.94)

Question: Do INITIAL RI (A paragraph start) correlate with early FL states,
and FINAL RI (A paragraph end) correlate with late FL states?

If yes: RI tokens may encode the FL state of materials they reference.
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
print("T16: RI-FL STATE CORRELATION TEST")
print("=" * 70)

# FL state classification from C777
FL_EARLY = {'i', 'ii', 'in'}  # pos 0.30-0.42
FL_MEDIAL = {'r', 'ar', 'al', 'l', 'ol'}  # pos 0.51-0.64
FL_LATE = {'o', 'ly', 'am', 'm', 'dy', 'ry', 'y'}  # pos 0.75-0.94

# Character markers from C777
EARLY_CHARS = {'i'}  # 'i' = initial marker
LATE_CHARS = {'y', 'o', 'm'}  # terminal markers

# Build B vocabulary for PP/RI classification
b_middles = set()
for token in tx.currier_b():
    w = token.word.strip()
    if not w or '*' in w:
        continue
    m = morph.extract(w)
    if m.middle:
        b_middles.add(m.middle)

GALLOWS = {'k', 't', 'p', 'f'}

def starts_with_gallows(word):
    if not word:
        return False
    w = word.strip()
    return bool(w) and w[0] in GALLOWS

# Collect A tokens by line
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

# Build paragraphs
paragraphs = []
a_folios = defaultdict(list)
for (folio, line), tokens in sorted(a_tokens_by_line.items()):
    a_folios[folio].append((line, tokens))

for folio in sorted(a_folios.keys()):
    lines = a_folios[folio]
    current_para = {'folio': folio, 'tokens': []}

    for line, tokens in lines:
        if tokens and starts_with_gallows(tokens[0]['word']):
            if current_para['tokens']:
                paragraphs.append(current_para)
            current_para = {'folio': folio, 'tokens': []}
        current_para['tokens'].extend(tokens)

    if current_para['tokens']:
        paragraphs.append(current_para)

# Classify RI by position
initial_ri = []  # position < 0.2
final_ri = []    # position > 0.8

for p in paragraphs:
    tokens = p['tokens']
    n = len(tokens)
    if n < 3:
        continue

    for i, t in enumerate(tokens):
        if not t['is_ri']:
            continue

        rel_pos = i / (n - 1)

        if rel_pos < 0.2:
            initial_ri.append(t)
        elif rel_pos > 0.8:
            final_ri.append(t)

print(f"\nINITIAL RI tokens: {len(initial_ri)}")
print(f"FINAL RI tokens: {len(final_ri)}")

# Test 1: First letter (FL) of RI tokens
print("\n" + "=" * 70)
print("TEST 1: FIRST LETTER OF RI TOKENS")
print("=" * 70)

def get_first_letter(word):
    """Get the first letter after any gallows/prefix."""
    if not word:
        return None
    # The first character of the MIDDLE would be more accurate
    m = morph.extract(word)
    if m.middle:
        return m.middle[0] if m.middle else None
    return word[0] if word else None

initial_fl = Counter(get_first_letter(t['word']) for t in initial_ri)
final_fl = Counter(get_first_letter(t['word']) for t in final_ri)

print(f"\nFirst letter distribution (from word):")
print(f"  {'Letter':<8} {'INITIAL':>10} {'FINAL':>10} {'Ratio':>10}")
print(f"  {'-'*8} {'-'*10} {'-'*10} {'-'*10}")

all_letters = set(initial_fl.keys()) | set(final_fl.keys())
for letter in sorted(all_letters, key=lambda x: (x is None, x)):
    init_n = initial_fl.get(letter, 0)
    final_n = final_fl.get(letter, 0)
    if init_n + final_n < 3:
        continue
    ratio = init_n / final_n if final_n > 0 else float('inf')
    letter_str = letter if letter else '(none)'
    print(f"  {letter_str:<8} {init_n:>10} {final_n:>10} {ratio:>10.2f}")

# Test 2: MIDDLE first character
print("\n" + "=" * 70)
print("TEST 2: MIDDLE FIRST CHARACTER")
print("=" * 70)

initial_mid_fl = Counter(t['middle'][0] if t['middle'] else None for t in initial_ri)
final_mid_fl = Counter(t['middle'][0] if t['middle'] else None for t in final_ri)

print(f"\nMIDDLE first character distribution:")
print(f"  {'Char':<8} {'INITIAL':>10} {'FINAL':>10} {'Ratio':>10}")
print(f"  {'-'*8} {'-'*10} {'-'*10} {'-'*10}")

all_chars = set(initial_mid_fl.keys()) | set(final_mid_fl.keys())
for char in sorted(all_chars, key=lambda x: (x is None, x)):
    init_n = initial_mid_fl.get(char, 0)
    final_n = final_mid_fl.get(char, 0)
    if init_n + final_n < 3:
        continue
    ratio = init_n / final_n if final_n > 0 else float('inf')
    char_str = char if char else '(none)'
    print(f"  {char_str:<8} {init_n:>10} {final_n:>10} {ratio:>10.2f}")

# Test 3: Check for 'i' vs 'y' pattern (C777 markers)
print("\n" + "=" * 70)
print("TEST 3: EARLY vs LATE CHARACTER MARKERS")
print("=" * 70)

def classify_by_c777(middle):
    """Classify MIDDLE by C777 FL character markers."""
    if not middle:
        return 'UNKNOWN'
    first_char = middle[0]
    last_char = middle[-1]

    # Check first character
    if first_char == 'i':
        return 'EARLY'
    elif first_char in {'y', 'm'}:
        return 'LATE'

    # Check last character
    if last_char == 'y':
        return 'LATE'
    elif last_char == 'i':
        return 'EARLY'

    return 'NEUTRAL'

initial_stage = Counter(classify_by_c777(t['middle']) for t in initial_ri)
final_stage = Counter(classify_by_c777(t['middle']) for t in final_ri)

print(f"\nC777 stage classification:")
print(f"  {'Stage':<10} {'INITIAL RI':>12} {'FINAL RI':>12}")
print(f"  {'-'*10} {'-'*12} {'-'*12}")
for stage in ['EARLY', 'NEUTRAL', 'LATE', 'UNKNOWN']:
    init_n = initial_stage.get(stage, 0)
    final_n = final_stage.get(stage, 0)
    init_pct = init_n / len(initial_ri) * 100 if initial_ri else 0
    final_pct = final_n / len(final_ri) * 100 if final_ri else 0
    print(f"  {stage:<10} {init_n:>5} ({init_pct:>5.1f}%) {final_n:>5} ({final_pct:>5.1f}%)")

# Test 4: Check if RI MIDDLEs overlap with FL MIDDLEs
print("\n" + "=" * 70)
print("TEST 4: RI MIDDLE OVERLAP WITH FL MIDDLES")
print("=" * 70)

all_fl_middles = FL_EARLY | FL_MEDIAL | FL_LATE
initial_middles = set(t['middle'] for t in initial_ri if t['middle'])
final_middles = set(t['middle'] for t in final_ri if t['middle'])

initial_fl_overlap = initial_middles & all_fl_middles
final_fl_overlap = final_middles & all_fl_middles

print(f"\nFL MIDDLE overlap:")
print(f"  INITIAL RI MIDDLEs that ARE FL MIDDLEs: {initial_fl_overlap}")
print(f"  FINAL RI MIDDLEs that ARE FL MIDDLEs: {final_fl_overlap}")

# If RI MIDDLEs don't overlap with FL MIDDLEs (as expected since RI is A-exclusive),
# check if they STRUCTURALLY PARALLEL FL MIDDLEs

# Test 5: SUFFIX distribution (C777 notes -y as terminal marker)
print("\n" + "=" * 70)
print("TEST 5: SUFFIX DISTRIBUTION (-y as terminal marker)")
print("=" * 70)

initial_suffix = Counter(t['suffix'] for t in initial_ri)
final_suffix = Counter(t['suffix'] for t in final_ri)

initial_y_suffix = sum(c for s, c in initial_suffix.items() if s and 'y' in s)
final_y_suffix = sum(c for s, c in final_suffix.items() if s and 'y' in s)

initial_y_rate = initial_y_suffix / len(initial_ri) if initial_ri else 0
final_y_rate = final_y_suffix / len(final_ri) if final_ri else 0

print(f"\nSUFFIX with 'y' (terminal marker):")
print(f"  INITIAL RI: {initial_y_suffix} ({initial_y_rate:.1%})")
print(f"  FINAL RI: {final_y_suffix} ({final_y_rate:.1%})")
print(f"  Ratio: {final_y_rate/initial_y_rate:.2f}x" if initial_y_rate > 0 else "  (INITIAL has no y-suffixes)")

# Check specific suffixes
print(f"\nTop suffixes by position:")
print(f"  INITIAL: {initial_suffix.most_common(5)}")
print(f"  FINAL: {final_suffix.most_common(5)}")

# Summary
print("\n" + "=" * 70)
print("SUMMARY: RI-FL STATE CORRELATION")
print("=" * 70)

# Calculate correlation metrics
early_in_initial = initial_stage.get('EARLY', 0) / len(initial_ri) if initial_ri else 0
late_in_final = final_stage.get('LATE', 0) / len(final_ri) if final_ri else 0

print(f"""
C777 FL State Index (B):
- 'i'-forms mark process START (pos ~0.30)
- 'y'-forms mark process END (pos ~0.94)

RI Position Correlation:
- INITIAL RI with 'i/EARLY' markers: {early_in_initial:.1%}
- FINAL RI with 'y/LATE' markers: {late_in_final:.1%}

Y-SUFFIX (terminal marker) distribution:
- INITIAL RI: {initial_y_rate:.1%}
- FINAL RI: {final_y_rate:.1%}
""")

if final_y_rate > initial_y_rate * 1.5:
    print("FINDING: FINAL RI has MORE y-suffix (terminal marker)")
    print("         -> Consistent with FINAL RI marking 'output state'")

if late_in_final > early_in_initial:
    print("FINDING: FINAL RI more likely to contain LATE markers")
    print("         -> Structural parallel to FL state progression")

if early_in_initial > 0.2 or late_in_final > 0.2:
    print("\nCONCLUSION: There IS a structural correlation between")
    print("RI position and C777 state markers. INITIAL RI may encode")
    print("'input state' and FINAL RI 'output state' in FL terms.")
else:
    print("\nCONCLUSION: Weak or no correlation found between")
    print("RI position and C777 state markers. The connection")
    print("may be more abstract than direct FL encoding.")

# Save results
results = {
    'initial_ri_count': len(initial_ri),
    'final_ri_count': len(final_ri),
    'initial_stage_distribution': {k: v for k, v in initial_stage.items()},
    'final_stage_distribution': {k: v for k, v in final_stage.items()},
    'initial_y_suffix_rate': float(initial_y_rate),
    'final_y_suffix_rate': float(final_y_rate),
    'initial_fl_overlap': list(initial_fl_overlap),
    'final_fl_overlap': list(final_fl_overlap),
}

out_path = PROJECT_ROOT / 'phases' / 'A_RECORD_B_ROUTING_TOPOLOGY' / 'results' / 't16_ri_fl_correlation.json'
with open(out_path, 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to {out_path.name}")
