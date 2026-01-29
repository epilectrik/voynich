"""
T6: Aggregation Level Analysis

Test what level of A-record aggregation produces usable B programs.

Levels:
1. Single line (record) - we know this is too narrow
2. "Paragraph" - gallows-initial chunks (lines starting with gallows until next gallows-initial)
3. Full A-folio - union of all lines in a folio

For each level, compute:
- Mean PP vocabulary size
- Mean B-folio viability
- Operational coherence (can produce complete programs)
"""

import sys
import json
from pathlib import Path
from collections import defaultdict
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))
from scripts.voynich import Transcript, Morphology

tx = Transcript()
morph = Morphology()

print("=" * 70)
print("T6: AGGREGATION LEVEL ANALYSIS")
print("=" * 70)

# Gallows characters (the "fancy" characters that start paragraphs)
GALLOWS = {'k', 't', 'p', 'f'}

def starts_with_gallows(word):
    """Check if word starts with a gallows letter"""
    if not word:
        return False
    # Check first character after stripping
    w = word.strip()
    if not w:
        return False
    return w[0] in GALLOWS

# Step 1: Build B-folio PP vocabularies
print("\nStep 1: Building B-folio PP vocabularies...")

b_folio_middles = defaultdict(set)
all_b_middles = set()

for token in tx.currier_b():
    w = token.word.strip()
    if not w or '*' in w:
        continue
    m = morph.extract(w)
    if m.middle:
        b_folio_middles[token.folio].add(m.middle)
        all_b_middles.add(m.middle)

# Step 2: Build A structures at different levels
print("Step 2: Building A-record structures...")

# Level 1: Single lines
a_lines = defaultdict(set)  # (folio, line) -> PP MIDDLEs

# Level 2: Paragraphs (gallows-initial chunks)
a_paragraphs = defaultdict(set)  # (folio, para_num) -> PP MIDDLEs
current_para = defaultdict(int)  # folio -> current paragraph number

# Level 3: Full folios
a_folios = defaultdict(set)  # folio -> PP MIDDLEs

# Also track which lines start with gallows
gallows_initial_lines = set()

# Process A tokens
prev_folio = None
for token in tx.currier_a():
    w = token.word.strip()
    if not w or '*' in w:
        continue

    folio = token.folio
    line = token.line

    # Reset paragraph counter on new folio
    if folio != prev_folio:
        current_para[folio] = 0
        prev_folio = folio

    # Check if this is a line-initial gallows token
    line_key = (folio, line)
    if line_key not in a_lines:  # First token of this line
        if starts_with_gallows(w):
            gallows_initial_lines.add(line_key)
            current_para[folio] += 1  # Start new paragraph

    m = morph.extract(w)
    if not m.middle:
        continue

    # Add to all levels
    a_lines[line_key].add(m.middle)
    a_paragraphs[(folio, current_para[folio])].add(m.middle)
    a_folios[folio].add(m.middle)

# Compute PP vocabulary (shared with B)
all_a_middles = set()
for middles in a_folios.values():
    all_a_middles.update(middles)
pp_vocabulary = all_a_middles & all_b_middles

print(f"  PP vocabulary: {len(pp_vocabulary)}")
print(f"  A lines: {len(a_lines)}")
print(f"  A paragraphs: {len(a_paragraphs)}")
print(f"  A folios: {len(a_folios)}")
print(f"  Gallows-initial lines: {len(gallows_initial_lines)} ({len(gallows_initial_lines)/len(a_lines)*100:.1f}%)")

# Filter to PP only
for key in a_lines:
    a_lines[key] = a_lines[key] & pp_vocabulary
for key in a_paragraphs:
    a_paragraphs[key] = a_paragraphs[key] & pp_vocabulary
for key in a_folios:
    a_folios[key] = a_folios[key] & pp_vocabulary

b_folio_pp = {f: middles & pp_vocabulary for f, middles in b_folio_middles.items()}
b_folios = list(b_folio_pp.keys())

# Step 3: Compute viability at each level
print("\nStep 3: Computing viability at each level...")

def compute_viability(a_pp_set):
    """How many B-folios can this A-unit produce?"""
    if not a_pp_set:
        return len(b_folios)  # No constraints = all viable
    viable = 0
    for b_folio in b_folios:
        if a_pp_set.issubset(b_folio_pp[b_folio]):
            viable += 1
    return viable

# Level 1: Lines
line_pp_counts = [len(v) for v in a_lines.values()]
line_viabilities = [compute_viability(v) for v in a_lines.values()]

# Level 2: Paragraphs
para_pp_counts = [len(v) for v in a_paragraphs.values()]
para_viabilities = [compute_viability(v) for v in a_paragraphs.values()]

# Level 3: Folios
folio_pp_counts = [len(v) for v in a_folios.values()]
folio_viabilities = [compute_viability(v) for v in a_folios.values()]

# Step 4: Report results
print("\n" + "=" * 70)
print("RESULTS BY AGGREGATION LEVEL:")
print("=" * 70)

results = {}

for name, pp_counts, viabilities, n in [
    ("Single Line", line_pp_counts, line_viabilities, len(a_lines)),
    ("Paragraph (gallows-chunk)", para_pp_counts, para_viabilities, len(a_paragraphs)),
    ("Full A-Folio", folio_pp_counts, folio_viabilities, len(a_folios)),
]:
    mean_pp = np.mean(pp_counts)
    mean_viab = np.mean(viabilities)
    zero_viab = sum(1 for v in viabilities if v == 0)
    narrow = sum(1 for v in viabilities if 0 < v < 10)
    broad = sum(1 for v in viabilities if v >= 40)

    print(f"\n{name} (n={n}):")
    print(f"  Mean PP MIDDLEs: {mean_pp:.1f}")
    print(f"  Mean viability: {mean_viab:.1f} / {len(b_folios)} B-folios ({mean_viab/len(b_folios)*100:.1f}%)")
    print(f"  Zero viability: {zero_viab} ({zero_viab/n*100:.1f}%)")
    print(f"  Narrow (<10): {narrow} ({narrow/n*100:.1f}%)")
    print(f"  Broad (>=40): {broad} ({broad/n*100:.1f}%)")

    results[name] = {
        'n': n,
        'mean_pp': float(mean_pp),
        'mean_viability': float(mean_viab),
        'mean_viability_pct': float(mean_viab / len(b_folios) * 100),
        'zero_viability_pct': float(zero_viab / n * 100),
        'narrow_pct': float(narrow / n * 100),
        'broad_pct': float(broad / n * 100),
    }

# Step 5: Interpretation
print("\n" + "=" * 70)
print("INTERPRETATION:")
print("=" * 70)

line_viab = results["Single Line"]["mean_viability"]
para_viab = results["Paragraph (gallows-chunk)"]["mean_viability"]
folio_viab = results["Full A-Folio"]["mean_viability"]

print(f"\nViability progression:")
print(f"  Line -> Paragraph: {para_viab/line_viab:.2f}x narrower")
print(f"  Paragraph -> Folio: {folio_viab/para_viab:.2f}x narrower")
print(f"  Line -> Folio: {folio_viab/line_viab:.2f}x narrower")

if results["Paragraph (gallows-chunk)"]["zero_viability_pct"] < results["Single Line"]["zero_viability_pct"]:
    print("\n  Paragraphs have FEWER zero-viability cases than lines.")
    print("  (Aggregation helps, but paragraphs may still be too narrow)")

if results["Full A-Folio"]["zero_viability_pct"] < 5:
    print("\n  Full A-folios have very few zero-viability cases.")
    print("  A-folio may be the operational unit.")

# Save
out_path = PROJECT_ROOT / 'phases' / 'A_RECORD_B_ROUTING_TOPOLOGY' / 'results' / 't6_aggregation_levels.json'
with open(out_path, 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to {out_path.name}")
