"""
26_pp_excluding_line1.py

Hypothesis: PP on line 1 of A paragraphs is structural, not vocabulary.
If we exclude line-1 PP, does the remaining PP better match B?

Test:
1. Separate A paragraph PP into line-1 vs lines-2+
2. Compare B coverage with and without line-1 PP
3. Check if line-1 PP has different properties
"""

import sys
import json
from pathlib import Path
from collections import defaultdict, Counter

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'scripts'))
from voynich import Transcript, Morphology, load_middle_classes

print("="*70)
print("PP ANALYSIS: LINE 1 vs LINES 2+")
print("="*70)

tx = Transcript()
morph = Morphology()
ri_middles, pp_middles = load_middle_classes()

# =============================================================
# STEP 1: Build B PP vocabulary
# =============================================================
print("\nSTEP 1: Building B PP vocabulary...")

b_pp_middles = set()
for t in tx.currier_b():
    if not t.word or '*' in t.word:
        continue
    try:
        m = morph.extract(t.word)
        if m.middle and m.middle in pp_middles:
            b_pp_middles.add(m.middle)
    except:
        pass

print(f"B PP MIDDLEs: {len(b_pp_middles)}")

# =============================================================
# STEP 2: Build A paragraphs with line structure
# =============================================================
print("\n" + "="*70)
print("STEP 2: Building A paragraphs with line structure...")

GALLOWS = {'k', 't', 'p', 'f'}

def starts_with_gallows(word):
    return word and word[0] in GALLOWS

# Collect A tokens by folio and line
a_by_folio_line = defaultdict(list)
for t in tx.currier_a():
    if t.word and '*' not in t.word:
        a_by_folio_line[(t.folio, t.line)].append(t)

# Build paragraphs tracking which line each token is on
paragraphs = []  # List of {tokens: [...], lines: {line_num: [tokens]}}

current_para = {'tokens': [], 'lines': defaultdict(list), 'folio': None, 'start_line': None}
current_folio = None
line_in_para = 0

for (folio, line) in sorted(a_by_folio_line.keys()):
    tokens = a_by_folio_line[(folio, line)]

    # New paragraph on gallows-initial or new folio
    if tokens and (starts_with_gallows(tokens[0].word) or folio != current_folio):
        if current_para['tokens']:
            paragraphs.append(current_para)
        current_para = {'tokens': [], 'lines': defaultdict(list), 'folio': folio, 'start_line': line}
        current_folio = folio
        line_in_para = 1
    else:
        line_in_para += 1

    for t in tokens:
        current_para['tokens'].append(t)
        current_para['lines'][line_in_para].append(t)

if current_para['tokens']:
    paragraphs.append(current_para)

print(f"Built {len(paragraphs)} paragraphs")

# =============================================================
# STEP 3: Extract PP by line position
# =============================================================
print("\n" + "="*70)
print("STEP 3: Extracting PP by line position...")

para_analysis = []

for i, para in enumerate(paragraphs):
    line1_pp = set()
    lines2plus_pp = set()
    all_pp = set()

    for line_num, tokens in para['lines'].items():
        for t in tokens:
            try:
                m = morph.extract(t.word)
                if m.middle and m.middle in pp_middles:
                    all_pp.add(m.middle)
                    if line_num == 1:
                        line1_pp.add(m.middle)
                    else:
                        lines2plus_pp.add(m.middle)
            except:
                pass

    para_analysis.append({
        'para_idx': i,
        'folio': para['folio'],
        'n_lines': len(para['lines']),
        'line1_pp': line1_pp,
        'lines2plus_pp': lines2plus_pp,
        'all_pp': all_pp,
    })

# Summary
total_line1_pp = set()
total_lines2plus_pp = set()
for p in para_analysis:
    total_line1_pp.update(p['line1_pp'])
    total_lines2plus_pp.update(p['lines2plus_pp'])

print(f"\nPP MIDDLE distribution:")
print(f"  Line 1 only: {len(total_line1_pp - total_lines2plus_pp)}")
print(f"  Lines 2+ only: {len(total_lines2plus_pp - total_line1_pp)}")
print(f"  Both: {len(total_line1_pp & total_lines2plus_pp)}")

# =============================================================
# STEP 4: Compare B coverage
# =============================================================
print("\n" + "="*70)
print("STEP 4: B coverage comparison")
print("="*70)

def b_coverage(pp_set):
    if not b_pp_middles:
        return 0
    return len(pp_set & b_pp_middles) / len(b_pp_middles)

# Per-paragraph comparison
all_pp_coverages = []
line1_coverages = []
lines2plus_coverages = []

for p in para_analysis:
    all_pp_coverages.append(b_coverage(p['all_pp']))
    line1_coverages.append(b_coverage(p['line1_pp']))
    lines2plus_coverages.append(b_coverage(p['lines2plus_pp']))

print(f"\nMean B coverage by PP source:")
print(f"  All PP: {sum(all_pp_coverages)/len(all_pp_coverages):.1%}")
print(f"  Line 1 PP only: {sum(line1_coverages)/len(line1_coverages):.1%}")
print(f"  Lines 2+ PP only: {sum(lines2plus_coverages)/len(lines2plus_coverages):.1%}")

print(f"\nMax B coverage:")
print(f"  All PP: {max(all_pp_coverages):.1%}")
print(f"  Line 1 PP only: {max(line1_coverages):.1%}")
print(f"  Lines 2+ PP only: {max(lines2plus_coverages):.1%}")

# =============================================================
# STEP 5: Is line-1 PP different from lines-2+ PP?
# =============================================================
print("\n" + "="*70)
print("STEP 5: Is line-1 PP morphologically different?")
print("="*70)

# Kernel content
def kernel_profile(middles):
    if not middles:
        return {'k': 0, 'h': 0, 'e': 0}
    k = sum(1 for m in middles if 'k' in m) / len(middles)
    h = sum(1 for m in middles if 'h' in m) / len(middles)
    e = sum(1 for m in middles if 'e' in m) / len(middles)
    return {'k': k, 'h': h, 'e': e}

line1_kernel = kernel_profile(total_line1_pp)
lines2plus_kernel = kernel_profile(total_lines2plus_pp)

print(f"\nKernel content:")
print(f"           Line 1    Lines 2+")
print(f"  k rate:  {line1_kernel['k']:.3f}     {lines2plus_kernel['k']:.3f}")
print(f"  h rate:  {line1_kernel['h']:.3f}     {lines2plus_kernel['h']:.3f}")
print(f"  e rate:  {line1_kernel['e']:.3f}     {lines2plus_kernel['e']:.3f}")

# B overlap
line1_in_b = len(total_line1_pp & b_pp_middles)
lines2plus_in_b = len(total_lines2plus_pp & b_pp_middles)

print(f"\nOverlap with B:")
print(f"  Line 1 PP in B: {line1_in_b}/{len(total_line1_pp)} ({100*line1_in_b/len(total_line1_pp):.1f}%)")
print(f"  Lines 2+ PP in B: {lines2plus_in_b}/{len(total_lines2plus_pp)} ({100*lines2plus_in_b/len(total_lines2plus_pp):.1f}%)")

# =============================================================
# STEP 6: What's the line-1-only PP?
# =============================================================
print("\n" + "="*70)
print("STEP 6: Line-1-only PP MIDDLEs")
print("="*70)

line1_only = total_line1_pp - total_lines2plus_pp
print(f"\nPP that appears ONLY on line 1 (never on lines 2+): {len(line1_only)}")

# Are these in B?
line1_only_in_b = line1_only & b_pp_middles
print(f"  Of these, in B: {len(line1_only_in_b)} ({100*len(line1_only_in_b)/len(line1_only) if line1_only else 0:.1f}%)")

if line1_only:
    print(f"\n  Examples: {sorted(line1_only)[:20]}")

# =============================================================
# STEP 7: Re-test paragraph coverage excluding line 1
# =============================================================
print("\n" + "="*70)
print("STEP 7: Paragraph B coverage EXCLUDING line 1")
print("="*70)

# Best paragraphs by lines-2+ PP coverage
para_by_lines2plus = sorted(para_analysis, key=lambda p: -b_coverage(p['lines2plus_pp']))

print(f"\nTop paragraphs by lines-2+ PP coverage:")
for p in para_by_lines2plus[:10]:
    all_cov = b_coverage(p['all_pp'])
    l2_cov = b_coverage(p['lines2plus_pp'])
    print(f"  Para {p['para_idx']} ({p['folio']}): lines2+ = {l2_cov:.1%}, all = {all_cov:.1%}, diff = {all_cov - l2_cov:+.1%}")

# =============================================================
# SUMMARY
# =============================================================
print("\n" + "="*70)
print("SUMMARY")
print("="*70)

print(f"""
QUESTION: Does excluding line-1 PP change the picture?

LINE-1 vs LINES-2+ PP:
  Line-1 PP MIDDLEs: {len(total_line1_pp)}
  Lines-2+ PP MIDDLEs: {len(total_lines2plus_pp)}
  Line-1 only (never elsewhere): {len(line1_only)}

B COVERAGE:
  Mean coverage (all PP): {sum(all_pp_coverages)/len(all_pp_coverages):.1%}
  Mean coverage (lines 2+ only): {sum(lines2plus_coverages)/len(lines2plus_coverages):.1%}
  Difference: {sum(all_pp_coverages)/len(all_pp_coverages) - sum(lines2plus_coverages)/len(lines2plus_coverages):+.1%}

B OVERLAP:
  Line-1 PP in B: {100*line1_in_b/len(total_line1_pp):.1f}%
  Lines-2+ PP in B: {100*lines2plus_in_b/len(total_lines2plus_pp):.1f}%
""")

if abs(line1_in_b/len(total_line1_pp) - lines2plus_in_b/len(total_lines2plus_pp)) > 0.1:
    print("FINDING: Line-1 PP has DIFFERENT B overlap than lines-2+ PP.")
    if line1_in_b/len(total_line1_pp) < lines2plus_in_b/len(total_lines2plus_pp):
        print("Line-1 PP is LESS connected to B - may be structural.")
    else:
        print("Line-1 PP is MORE connected to B - may be vocabulary anchor.")
else:
    print("FINDING: Line-1 PP and lines-2+ PP have similar B overlap.")
    print("No evidence that line-1 PP is structurally different.")
