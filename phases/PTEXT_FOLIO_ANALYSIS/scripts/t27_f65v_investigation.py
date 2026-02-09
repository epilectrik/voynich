#!/usr/bin/env python3
"""
Test 27: f65v Deep Investigation

f65v is anomalous among AZC folios:
- 100% P-text (paragraph text)
- 0 diagram tokens (no C, R, S positions)
- Why is this folio different?

Investigate:
1. What does f65v actually contain?
2. How does it compare to neighboring folios?
3. Is it really an AZC folio or misclassified?
4. What's its vocabulary profile?
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

from pathlib import Path
from collections import Counter, defaultdict
from scripts.voynich import Transcript, Morphology

tx = Transcript()
morph = Morphology()

print("=" * 70)
print("TEST 27: f65v DEEP INVESTIGATION")
print("=" * 70)
print()

# 1. Get all f65v tokens
print("1. f65v TOKEN CENSUS")
print("-" * 50)

filepath = Path('C:/git/voynich/data/transcriptions/interlinear_full_words.txt')

f65v_tokens = []
f65v_placements = Counter()
f65v_lines = defaultdict(list)

# Also get neighboring folios for comparison
neighbors = ['f65r', 'f65v', 'f66r', 'f66v']
neighbor_data = defaultdict(lambda: {'tokens': [], 'placements': Counter()})

with open(filepath, 'r', encoding='utf-8') as f:
    header = f.readline()
    for line in f:
        parts = line.strip().split('\t')
        if len(parts) > 12:
            transcriber = parts[12].strip('"').strip()
            if transcriber != 'H':
                continue

            folio = parts[2].strip('"').strip()
            token = parts[0].strip('"').strip().lower()
            placement = parts[10].strip('"').strip()
            line_num = parts[11].strip('"').strip()
            section = parts[3].strip('"').strip()
            language = parts[5].strip('"').strip()
            currier = parts[6].strip('"').strip()

            if not token.strip() or '*' in token:
                continue

            if folio == 'f65v':
                f65v_tokens.append({
                    'token': token,
                    'placement': placement,
                    'line': line_num,
                    'section': section,
                    'language': language,
                    'currier': currier
                })
                f65v_placements[placement] += 1
                f65v_lines[line_num].append(token)

            if folio in neighbors:
                neighbor_data[folio]['tokens'].append(token)
                neighbor_data[folio]['placements'][placement] += 1

print(f"Total f65v tokens: {len(f65v_tokens)}")
print()

if f65v_tokens:
    print("Placement distribution:")
    for placement, count in f65v_placements.most_common():
        pct = count / len(f65v_tokens) * 100
        print(f"  {placement}: {count} ({pct:.1f}%)")

    print()
    print("Metadata from first token:")
    first = f65v_tokens[0]
    print(f"  Section: {first['section']}")
    print(f"  Language: {first['language']}")
    print(f"  Currier: {first['currier']}")

print()

# 2. Compare to neighbors
print("2. COMPARISON TO NEIGHBORING FOLIOS")
print("-" * 50)

for folio in neighbors:
    data = neighbor_data[folio]
    n_tokens = len(data['tokens'])
    placements = data['placements']

    # Calculate P vs diagram ratio
    p_count = sum(c for p, c in placements.items() if p.startswith('P'))
    diagram_count = sum(c for p, c in placements.items() if p.startswith(('C', 'R', 'S')))
    other_count = n_tokens - p_count - diagram_count

    print(f"{folio}: {n_tokens} tokens")
    print(f"  P-text: {p_count} ({p_count/n_tokens*100:.1f}%)" if n_tokens > 0 else "  P-text: 0")
    print(f"  Diagram (C/R/S): {diagram_count} ({diagram_count/n_tokens*100:.1f}%)" if n_tokens > 0 else "  Diagram: 0")
    print(f"  Other: {other_count}")
    print()

# 3. f65v vocabulary analysis
print("3. f65v VOCABULARY PROFILE")
print("-" * 50)

f65v_middles = Counter()
f65v_prefixes = Counter()

for t in f65v_tokens:
    m = morph.extract(t['token'])
    if m:
        if m.middle:
            f65v_middles[m.middle] += 1
        if m.prefix:
            f65v_prefixes[m.prefix] += 1

print("Top MIDDLEs:")
for mid, count in f65v_middles.most_common(15):
    print(f"  {mid}: {count}")

print()
print("Top PREFIXes:")
for pre, count in f65v_prefixes.most_common(10):
    print(f"  {pre}: {count}")

print()

# 4. Check if f65v vocabulary appears in Currier A vs B
print("4. f65v VOCABULARY: CURRIER A vs B AFFINITY")
print("-" * 50)

f65v_middle_set = set(f65v_middles.keys())

# Get A and B middle sets
a_middles = set()
b_middles = set()

for token in tx.currier_a():
    m = morph.extract(token.word)
    if m and m.middle:
        a_middles.add(m.middle)

for token in tx.currier_b():
    m = morph.extract(token.word)
    if m and m.middle:
        b_middles.add(m.middle)

shared_with_a = f65v_middle_set & a_middles
shared_with_b = f65v_middle_set & b_middles
unique_to_f65v = f65v_middle_set - a_middles - b_middles

print(f"f65v unique MIDDLEs: {len(f65v_middle_set)}")
print(f"Shared with Currier A: {len(shared_with_a)} ({len(shared_with_a)/len(f65v_middle_set)*100:.1f}%)")
print(f"Shared with Currier B: {len(shared_with_b)} ({len(shared_with_b)/len(f65v_middle_set)*100:.1f}%)")
print(f"Unique to f65v: {len(unique_to_f65v)} ({len(unique_to_f65v)/len(f65v_middle_set)*100:.1f}%)")

if unique_to_f65v:
    print(f"  Unique examples: {', '.join(list(unique_to_f65v)[:10])}")

print()

# 5. Line-by-line content
print("5. f65v LINE-BY-LINE CONTENT")
print("-" * 50)

for line_num in sorted(f65v_lines.keys(), key=lambda x: int(x) if x.isdigit() else 0):
    tokens = f65v_lines[line_num]
    print(f"Line {line_num}: {' '.join(tokens[:10])}{'...' if len(tokens) > 10 else ''}")

print()

# 6. Physical context
print("6. PHYSICAL CONTEXT")
print("-" * 50)

print("""
f65v is part of the AZC (Astronomical/Zodiac/Cosmological) section.

According to standard Voynich organization:
- f65r-f67r: Part of quire 10 (cosmological diagrams)
- f65v specifically: Should contain diagram with text

But f65v has:
- 100% paragraph text (P placement)
- 0% diagram positions (no C, R, S)

This could mean:
1. f65v is MISLABELED as AZC (actually Currier A text page)
2. f65v is a TEXT-ONLY page within the diagram section
3. The diagram exists but has NO labeled text
4. Transcription artifact (diagram text not captured)
""")

# 7. Check what the actual folio looks like in terms of structure
print("7. STRUCTURAL ANALYSIS")
print("-" * 50)

# Count paragraphs
paragraphs = set()
for t in f65v_tokens:
    # Paragraph is typically encoded in placement
    if t['placement'].startswith('P'):
        # Extract paragraph number if present
        paragraphs.add(t['placement'])

print(f"Distinct P-placements: {len(paragraphs)}")
print(f"Placements: {sorted(paragraphs)}")

# Check line count
print(f"Distinct lines: {len(f65v_lines)}")
print(f"Total tokens: {len(f65v_tokens)}")
print(f"Avg tokens/line: {len(f65v_tokens)/len(f65v_lines):.1f}" if f65v_lines else "N/A")

print()

# 8. Synthesis
print("=" * 70)
print("SYNTHESIS: WHAT IS f65v?")
print("=" * 70)

print(f"""
FINDINGS:

1. f65v has {len(f65v_tokens)} tokens, ALL in P (paragraph) placement
2. Neighbors have mixed P + diagram content
3. Vocabulary profile: {len(shared_with_a)/len(f65v_middle_set)*100:.1f}% shared with A, {len(shared_with_b)/len(f65v_middle_set)*100:.1f}% shared with B
4. {len(f65v_lines)} lines of text

INTERPRETATION OPTIONS:

A. f65v is a CURRIER A TEXT PAGE misplaced in AZC section
   - Would need to check visual manuscript
   - Section/language metadata may be wrong

B. f65v is ANNOTATION for adjacent diagrams
   - Text without its own diagram
   - Describes f65r or f66r diagrams

C. f65v DIAGRAM has no labeled text
   - The physical diagram exists
   - But text is in paragraph form, not diagram positions
   - Different layout than other AZC pages

D. TRANSCRIPTION gap
   - Diagram text wasn't captured
   - Only paragraph text was transcribed
""")

# Check Currier assignment
currier_assignments = Counter(t['currier'] for t in f65v_tokens)
print(f"\nCurrier assignments in f65v: {dict(currier_assignments)}")

if 'A' in currier_assignments:
    print("\nf65v is marked as CURRIER A in the transcript!")
    print("This confirms it's linguistically A, not B or AZC diagram text.")
