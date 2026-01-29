"""
T19: Input vs Output Morphology Analysis

We have two cleanly separated RI populations:
- INITIAL RI (position < 0.2) = INPUT context
- FINAL RI (position > 0.8) = OUTPUT context
- Jaccard = 0.010 (almost disjoint)

This is a labeled training set for input/output morphology.
Extract the morphological signature that distinguishes them.
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
print("T19: INPUT vs OUTPUT MORPHOLOGY ANALYSIS")
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
        'articulator': m.articulator,
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
initial_ri = []  # INPUT
final_ri = []    # OUTPUT

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

print(f"\nINPUT (INITIAL RI): {len(initial_ri)} tokens")
print(f"OUTPUT (FINAL RI): {len(final_ri)} tokens")

# ============================================================
# ANALYSIS 1: PREFIX DISTRIBUTION
# ============================================================
print("\n" + "=" * 70)
print("ANALYSIS 1: PREFIX DISTRIBUTION (INPUT vs OUTPUT)")
print("=" * 70)

input_prefix = Counter(t['prefix'] for t in initial_ri)
output_prefix = Counter(t['prefix'] for t in final_ri)

all_prefixes = set(input_prefix.keys()) | set(output_prefix.keys())

print(f"\n{'PREFIX':<10} {'INPUT':>8} {'IN%':>8} {'OUTPUT':>8} {'OUT%':>8} {'RATIO':>8} {'BIAS':>10}")
print(f"{'-'*10} {'-'*8} {'-'*8} {'-'*8} {'-'*8} {'-'*8} {'-'*10}")

prefix_biases = {}
for prefix in sorted(all_prefixes, key=lambda x: (x is None, x or '')):
    in_n = input_prefix.get(prefix, 0)
    out_n = output_prefix.get(prefix, 0)
    if in_n + out_n < 3:
        continue

    in_pct = in_n / len(initial_ri) * 100
    out_pct = out_n / len(final_ri) * 100

    # Ratio relative to expected (if evenly distributed)
    in_expected = len(initial_ri) / (len(initial_ri) + len(final_ri))
    actual_in_frac = in_n / (in_n + out_n) if (in_n + out_n) > 0 else 0.5

    if out_n > 0:
        ratio = in_n / out_n
    else:
        ratio = float('inf')

    if ratio > 1.5:
        bias = "INPUT"
    elif ratio < 0.67:
        bias = "OUTPUT"
    else:
        bias = "neutral"

    prefix_str = prefix if prefix else "(none)"
    prefix_biases[prefix] = bias
    print(f"{prefix_str:<10} {in_n:>8} {in_pct:>7.1f}% {out_n:>8} {out_pct:>7.1f}% {ratio:>8.2f} {bias:>10}")

# ============================================================
# ANALYSIS 2: SUFFIX DISTRIBUTION
# ============================================================
print("\n" + "=" * 70)
print("ANALYSIS 2: SUFFIX DISTRIBUTION (INPUT vs OUTPUT)")
print("=" * 70)

input_suffix = Counter(t['suffix'] for t in initial_ri)
output_suffix = Counter(t['suffix'] for t in final_ri)

all_suffixes = set(input_suffix.keys()) | set(output_suffix.keys())

print(f"\n{'SUFFIX':<10} {'INPUT':>8} {'IN%':>8} {'OUTPUT':>8} {'OUT%':>8} {'RATIO':>8} {'BIAS':>10}")
print(f"{'-'*10} {'-'*8} {'-'*8} {'-'*8} {'-'*8} {'-'*8} {'-'*10}")

suffix_biases = {}
for suffix in sorted(all_suffixes, key=lambda x: (x is None, x or '')):
    in_n = input_suffix.get(suffix, 0)
    out_n = output_suffix.get(suffix, 0)
    if in_n + out_n < 3:
        continue

    in_pct = in_n / len(initial_ri) * 100
    out_pct = out_n / len(final_ri) * 100

    if out_n > 0:
        ratio = in_n / out_n
    else:
        ratio = float('inf')

    if ratio > 1.5:
        bias = "INPUT"
    elif ratio < 0.67:
        bias = "OUTPUT"
    else:
        bias = "neutral"

    suffix_str = suffix if suffix else "(none)"
    suffix_biases[suffix] = bias
    print(f"{suffix_str:<10} {in_n:>8} {in_pct:>7.1f}% {out_n:>8} {out_pct:>7.1f}% {ratio:>8.2f} {bias:>10}")

# ============================================================
# ANALYSIS 3: MIDDLE FIRST CHARACTER
# ============================================================
print("\n" + "=" * 70)
print("ANALYSIS 3: MIDDLE FIRST CHARACTER (INPUT vs OUTPUT)")
print("=" * 70)

input_mid_first = Counter(t['middle'][0] if t['middle'] else None for t in initial_ri)
output_mid_first = Counter(t['middle'][0] if t['middle'] else None for t in final_ri)

all_chars = set(input_mid_first.keys()) | set(output_mid_first.keys())

print(f"\n{'CHAR':<10} {'INPUT':>8} {'IN%':>8} {'OUTPUT':>8} {'OUT%':>8} {'RATIO':>8} {'BIAS':>10}")
print(f"{'-'*10} {'-'*8} {'-'*8} {'-'*8} {'-'*8} {'-'*8} {'-'*10}")

mid_first_biases = {}
for char in sorted(all_chars, key=lambda x: (x is None, x or '')):
    in_n = input_mid_first.get(char, 0)
    out_n = output_mid_first.get(char, 0)
    if in_n + out_n < 3:
        continue

    in_pct = in_n / len(initial_ri) * 100
    out_pct = out_n / len(final_ri) * 100

    if out_n > 0:
        ratio = in_n / out_n
    else:
        ratio = float('inf')

    if ratio > 1.5:
        bias = "INPUT"
    elif ratio < 0.67:
        bias = "OUTPUT"
    else:
        bias = "neutral"

    char_str = char if char else "(none)"
    mid_first_biases[char] = bias
    print(f"{char_str:<10} {in_n:>8} {in_pct:>7.1f}% {out_n:>8} {out_pct:>7.1f}% {ratio:>8.2f} {bias:>10}")

# ============================================================
# ANALYSIS 4: MIDDLE LAST CHARACTER
# ============================================================
print("\n" + "=" * 70)
print("ANALYSIS 4: MIDDLE LAST CHARACTER (INPUT vs OUTPUT)")
print("=" * 70)

input_mid_last = Counter(t['middle'][-1] if t['middle'] else None for t in initial_ri)
output_mid_last = Counter(t['middle'][-1] if t['middle'] else None for t in final_ri)

all_chars = set(input_mid_last.keys()) | set(output_mid_last.keys())

print(f"\n{'CHAR':<10} {'INPUT':>8} {'IN%':>8} {'OUTPUT':>8} {'OUT%':>8} {'RATIO':>8} {'BIAS':>10}")
print(f"{'-'*10} {'-'*8} {'-'*8} {'-'*8} {'-'*8} {'-'*8} {'-'*10}")

for char in sorted(all_chars, key=lambda x: (x is None, x or '')):
    in_n = input_mid_last.get(char, 0)
    out_n = output_mid_last.get(char, 0)
    if in_n + out_n < 3:
        continue

    in_pct = in_n / len(initial_ri) * 100
    out_pct = out_n / len(final_ri) * 100

    if out_n > 0:
        ratio = in_n / out_n
    else:
        ratio = float('inf')

    if ratio > 1.5:
        bias = "INPUT"
    elif ratio < 0.67:
        bias = "OUTPUT"
    else:
        bias = "neutral"

    char_str = char if char else "(none)"
    print(f"{char_str:<10} {in_n:>8} {in_pct:>7.1f}% {out_n:>8} {out_pct:>7.1f}% {ratio:>8.2f} {bias:>10}")

# ============================================================
# ANALYSIS 5: WORD LENGTH
# ============================================================
print("\n" + "=" * 70)
print("ANALYSIS 5: WORD LENGTH (INPUT vs OUTPUT)")
print("=" * 70)

input_lengths = [len(t['word']) for t in initial_ri]
output_lengths = [len(t['word']) for t in final_ri]

print(f"\nINPUT mean length: {np.mean(input_lengths):.2f} (std={np.std(input_lengths):.2f})")
print(f"OUTPUT mean length: {np.mean(output_lengths):.2f} (std={np.std(output_lengths):.2f})")

from scipy.stats import mannwhitneyu
stat, p = mannwhitneyu(input_lengths, output_lengths)
print(f"Mann-Whitney U: p={p:.4f}")

if np.mean(input_lengths) > np.mean(output_lengths):
    print("-> INPUT words are LONGER")
else:
    print("-> OUTPUT words are LONGER")

# ============================================================
# ANALYSIS 6: ARTICULATOR PRESENCE
# ============================================================
print("\n" + "=" * 70)
print("ANALYSIS 6: ARTICULATOR PRESENCE (INPUT vs OUTPUT)")
print("=" * 70)

input_artic = sum(1 for t in initial_ri if t['articulator'])
output_artic = sum(1 for t in final_ri if t['articulator'])

input_artic_pct = input_artic / len(initial_ri) * 100
output_artic_pct = output_artic / len(final_ri) * 100

print(f"\nINPUT with articulator: {input_artic} ({input_artic_pct:.1f}%)")
print(f"OUTPUT with articulator: {output_artic} ({output_artic_pct:.1f}%)")

if input_artic_pct > output_artic_pct * 1.5:
    print("-> Articulator is INPUT-biased")
elif output_artic_pct > input_artic_pct * 1.5:
    print("-> Articulator is OUTPUT-biased")
else:
    print("-> Articulator is neutral")

# ============================================================
# ANALYSIS 7: GALLOWS IN MIDDLE
# ============================================================
print("\n" + "=" * 70)
print("ANALYSIS 7: GALLOWS IN MIDDLE (INPUT vs OUTPUT)")
print("=" * 70)

def has_gallows(middle):
    if not middle:
        return False
    return any(c in GALLOWS for c in middle)

input_gallows = sum(1 for t in initial_ri if has_gallows(t['middle']))
output_gallows = sum(1 for t in final_ri if has_gallows(t['middle']))

input_gal_pct = input_gallows / len(initial_ri) * 100
output_gal_pct = output_gallows / len(final_ri) * 100

print(f"\nINPUT with gallows in MIDDLE: {input_gallows} ({input_gal_pct:.1f}%)")
print(f"OUTPUT with gallows in MIDDLE: {output_gallows} ({output_gal_pct:.1f}%)")

# ============================================================
# SUMMARY: MORPHOLOGICAL SIGNATURE
# ============================================================
print("\n" + "=" * 70)
print("SUMMARY: INPUT vs OUTPUT MORPHOLOGICAL SIGNATURE")
print("=" * 70)

input_markers = []
output_markers = []

for prefix, bias in prefix_biases.items():
    if bias == "INPUT":
        input_markers.append(f"PREFIX={prefix or 'none'}")
    elif bias == "OUTPUT":
        output_markers.append(f"PREFIX={prefix or 'none'}")

for suffix, bias in suffix_biases.items():
    if bias == "INPUT":
        input_markers.append(f"SUFFIX={suffix or 'none'}")
    elif bias == "OUTPUT":
        output_markers.append(f"SUFFIX={suffix or 'none'}")

for char, bias in mid_first_biases.items():
    if bias == "INPUT":
        input_markers.append(f"MID_START={char}")
    elif bias == "OUTPUT":
        output_markers.append(f"MID_START={char}")

print(f"""
INPUT MATERIAL MARKERS:
{chr(10).join('  - ' + m for m in input_markers) if input_markers else '  (none identified)'}

OUTPUT MATERIAL MARKERS:
{chr(10).join('  - ' + m for m in output_markers) if output_markers else '  (none identified)'}

LENGTH:
  INPUT: {np.mean(input_lengths):.1f} chars
  OUTPUT: {np.mean(output_lengths):.1f} chars
  {'INPUT longer' if np.mean(input_lengths) > np.mean(output_lengths) else 'OUTPUT longer'}

ARTICULATOR:
  INPUT: {input_artic_pct:.1f}%
  OUTPUT: {output_artic_pct:.1f}%
""")

# Save results
results = {
    'input_count': len(initial_ri),
    'output_count': len(final_ri),
    'input_prefixes': dict(input_prefix),
    'output_prefixes': dict(output_prefix),
    'input_suffixes': dict(input_suffix),
    'output_suffixes': dict(output_suffix),
    'input_mean_length': float(np.mean(input_lengths)),
    'output_mean_length': float(np.mean(output_lengths)),
    'input_markers': input_markers,
    'output_markers': output_markers,
}

out_path = PROJECT_ROOT / 'phases' / 'A_RECORD_B_ROUTING_TOPOLOGY' / 'results' / 't19_input_output_morphology.json'
with open(out_path, 'w') as f:
    json.dump(results, f, indent=2, default=str)

print(f"Results saved to {out_path.name}")
