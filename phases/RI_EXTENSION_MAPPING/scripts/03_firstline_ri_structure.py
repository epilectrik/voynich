"""
03_firstline_ri_structure.py - Analyze pure-RI first lines

20% of paragraph first-lines are pure RI (no PP).
These are concentrated in Section P.
What vocabulary appears there? What's their function?
"""

import sys
sys.path.insert(0, 'C:/git/voynich')
from scripts.voynich import Transcript, Morphology
from collections import defaultdict, Counter
import json

tx = Transcript()
morph = Morphology()

# Build B vocabulary
print("Building vocabulary...")
b_middles = set()
for t in tx.currier_b():
    m = morph.extract(t.word)
    if m and m.middle:
        b_middles.add(m.middle)

print(f"  PP vocabulary: {len(b_middles)} MIDDLEs")

# Build paragraph structure
print("Building paragraph structure...")
para_lines = defaultdict(lambda: defaultdict(list))
current_para = 0
prev_folio = None

for t in tx.currier_a():
    if t.folio != prev_folio:
        current_para = 1
        prev_folio = t.folio

    para_lines[(t.folio, current_para)][t.line].append(t)

    if t.par_final:
        current_para += 1

# Classify first lines
print("Classifying first lines...")
first_line_data = []

for (folio, para), lines in para_lines.items():
    if not lines:
        continue

    first_line_num = min(lines.keys())
    first_line_tokens = lines[first_line_num]

    ri_tokens = []
    pp_tokens = []

    for t in first_line_tokens:
        m = morph.extract(t.word)
        if m and m.middle:
            if m.middle in b_middles:
                pp_tokens.append(t)
            else:
                ri_tokens.append(t)

    if ri_tokens and not pp_tokens:
        line_type = 'PURE_RI'
    elif pp_tokens and not ri_tokens:
        line_type = 'PURE_PP'
    elif ri_tokens and pp_tokens:
        line_type = 'MIXED'
    else:
        line_type = 'EMPTY'

    first_line_data.append({
        'folio': folio,
        'para': para,
        'section': first_line_tokens[0].section if first_line_tokens else None,
        'line_type': line_type,
        'ri_tokens': ri_tokens,
        'pp_tokens': pp_tokens,
        'num_lines': len(lines)
    })

# ============================================================
# ANALYSIS 1: First Line Type Distribution
# ============================================================
print("\n" + "="*70)
print("ANALYSIS 1: FIRST LINE TYPE DISTRIBUTION")
print("="*70)

type_counts = Counter(d['line_type'] for d in first_line_data)
total = len(first_line_data)

print(f"\nFirst line types:")
for ltype, count in type_counts.most_common():
    print(f"  {ltype}: {count} ({100*count/total:.1f}%)")

# ============================================================
# ANALYSIS 2: Pure-RI First Lines by Section
# ============================================================
print("\n" + "="*70)
print("ANALYSIS 2: PURE-RI BY SECTION")
print("="*70)

pure_ri = [d for d in first_line_data if d['line_type'] == 'PURE_RI']

section_counts = Counter(d['section'] for d in pure_ri)
section_totals = Counter(d['section'] for d in first_line_data)

print(f"\nPure-RI first lines by section:")
for section in ['H', 'P', 'T']:
    ri_count = section_counts.get(section, 0)
    total_count = section_totals.get(section, 0)
    if total_count > 0:
        print(f"  Section {section}: {ri_count}/{total_count} ({100*ri_count/total_count:.1f}%)")

# ============================================================
# ANALYSIS 3: Pure-RI Vocabulary
# ============================================================
print("\n" + "="*70)
print("ANALYSIS 3: PURE-RI VOCABULARY")
print("="*70)

ri_words = Counter()
ri_middles = Counter()
ri_prefixes = Counter()

for d in pure_ri:
    for t in d['ri_tokens']:
        ri_words[t.word] += 1
        m = morph.extract(t.word)
        if m:
            if m.middle:
                ri_middles[m.middle] += 1
            if m.prefix:
                ri_prefixes[m.prefix] += 1

print(f"\nTotal pure-RI first-line tokens: {sum(ri_words.values())}")
print(f"Unique words: {len(ri_words)}")
print(f"Unique MIDDLEs: {len(ri_middles)}")

print(f"\nMost common words:")
for word, count in ri_words.most_common(15):
    print(f"  {word}: {count}")

print(f"\nMost common MIDDLEs:")
for middle, count in ri_middles.most_common(15):
    print(f"  {middle}: {count}")

print(f"\nPREFIX distribution:")
for prefix, count in ri_prefixes.most_common(10):
    pct = 100 * count / sum(ri_prefixes.values())
    print(f"  {prefix}: {count} ({pct:.1f}%)")

# ============================================================
# ANALYSIS 4: Are These Linkers?
# ============================================================
print("\n" + "="*70)
print("ANALYSIS 4: LINKER CHECK")
print("="*70)

KNOWN_LINKERS = ['cthody', 'ctho', 'ctheody', 'qokoiiin']

linker_count = 0
for d in pure_ri:
    for t in d['ri_tokens']:
        if t.word in KNOWN_LINKERS:
            linker_count += 1

print(f"\nKnown linker tokens in pure-RI first lines: {linker_count}")

# Check if they're ct-prefixed (linker-like)
ct_count = ri_prefixes.get('ct', 0)
total_prefixed = sum(ri_prefixes.values())
print(f"ct-prefixed tokens: {ct_count}/{total_prefixed} ({100*ct_count/total_prefixed:.1f}%)")

# ============================================================
# ANALYSIS 5: Paragraph Context
# ============================================================
print("\n" + "="*70)
print("ANALYSIS 5: PARAGRAPH CONTEXT")
print("="*70)

# What comes after pure-RI first lines?
ri_para_lengths = [d['num_lines'] for d in pure_ri]
pp_para_lengths = [d['num_lines'] for d in first_line_data if d['line_type'] == 'PURE_PP']

print(f"\nParagraph length after pure-RI first line:")
print(f"  Mean: {sum(ri_para_lengths)/len(ri_para_lengths):.2f} lines")
print(f"  Distribution: {Counter(ri_para_lengths).most_common()}")

print(f"\nParagraph length after pure-PP first line:")
print(f"  Mean: {sum(pp_para_lengths)/len(pp_para_lengths):.2f} lines")

# Position in folio
ri_para_nums = [d['para'] for d in pure_ri]
pp_para_nums = [d['para'] for d in first_line_data if d['line_type'] == 'PURE_PP']

print(f"\nParagraph position (pure-RI):")
print(f"  Mean: {sum(ri_para_nums)/len(ri_para_nums):.2f}")
print(f"  First paragraph: {sum(1 for p in ri_para_nums if p == 1)}/{len(ri_para_nums)}")

print(f"\nParagraph position (pure-PP):")
print(f"  Mean: {sum(pp_para_nums)/len(pp_para_nums):.2f}")
print(f"  First paragraph: {sum(1 for p in pp_para_nums if p == 1)}/{len(pp_para_nums)}")

# ============================================================
# ANALYSIS 6: Example Pure-RI First Lines
# ============================================================
print("\n" + "="*70)
print("ANALYSIS 6: EXAMPLES")
print("="*70)

print(f"\nPure-RI first line examples:")
for d in pure_ri[:20]:
    tokens = [t.word for t in d['ri_tokens']]
    print(f"  {d['folio']} para {d['para']} (section {d['section']}): {' '.join(tokens)}")

# ============================================================
# ANALYSIS 7: Extension Patterns in First-Line RI
# ============================================================
print("\n" + "="*70)
print("ANALYSIS 7: EXTENSION PATTERNS")
print("="*70)

pp_sorted = sorted(b_middles, key=len, reverse=True)

def get_extension(ri_middle):
    for pp in pp_sorted:
        if len(pp) >= 2:
            if ri_middle.startswith(pp) and len(ri_middle) > len(pp):
                return ri_middle[len(pp):]
            elif ri_middle.endswith(pp) and len(ri_middle) > len(pp):
                return ri_middle[:-len(pp)]
    return None

extensions = Counter()
no_extension = 0

for d in pure_ri:
    for t in d['ri_tokens']:
        m = morph.extract(t.word)
        if m and m.middle:
            ext = get_extension(m.middle)
            if ext:
                extensions[ext] += 1
            else:
                no_extension += 1

print(f"\nExtensions in pure-RI first lines:")
print(f"  With extension: {sum(extensions.values())}")
print(f"  No extension (including 'ho'): {no_extension}")

print(f"\nTop extensions:")
for ext, count in extensions.most_common(10):
    print(f"  '{ext}': {count}")

# ============================================================
# SUMMARY
# ============================================================
print("\n" + "="*70)
print("SUMMARY")
print("="*70)

print(f"""
Pure-RI first lines: {len(pure_ri)}/{len(first_line_data)} ({100*len(pure_ri)/len(first_line_data):.1f}%)

Section distribution:
  H: {section_counts.get('H', 0)} ({100*section_counts.get('H', 0)/len(pure_ri):.0f}%)
  P: {section_counts.get('P', 0)} ({100*section_counts.get('P', 0)/len(pure_ri):.0f}%)
  T: {section_counts.get('T', 0)} ({100*section_counts.get('T', 0)/len(pure_ri):.0f}%)

Key characteristics:
- ct-prefixed: {100*ct_count/total_prefixed:.0f}%
- Single-line paragraphs: {sum(1 for l in ri_para_lengths if l == 1)}/{len(ri_para_lengths)}
- Later in folio (mean para {sum(ri_para_nums)/len(ri_para_nums):.1f})

Top vocabulary: {', '.join(w for w, c in ri_words.most_common(5))}
""")

# Save results
output = {
    'pure_ri_count': len(pure_ri),
    'total_first_lines': len(first_line_data),
    'section_distribution': dict(section_counts),
    'top_words': dict(ri_words.most_common(20)),
    'top_middles': dict(ri_middles.most_common(20)),
    'prefix_distribution': dict(ri_prefixes),
    'mean_para_length': sum(ri_para_lengths)/len(ri_para_lengths),
    'mean_para_position': sum(ri_para_nums)/len(ri_para_nums)
}

with open('C:/git/voynich/phases/RI_EXTENSION_MAPPING/results/firstline_ri_structure.json', 'w') as f:
    json.dump(output, f, indent=2)

print("Results saved to firstline_ri_structure.json")
