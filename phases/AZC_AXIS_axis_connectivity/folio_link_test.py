#!/usr/bin/env python3
"""
AZC Folio Link Test

Tests whether AZC folios link preferentially to specific A/B folios
(supporting calendar/coordination hypothesis) or uniformly to all
(falsifying specific coordination).
"""

import os
from collections import defaultdict, Counter
import math

os.chdir('C:/git/voynich')

print("=" * 70)
print("AZC FOLIO LINK TEST")
print("=" * 70)

# Load data
with open('data/transcriptions/interlinear_full_words.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()

header = lines[0].strip().split('\t')
header = [h.strip('"') for h in header]

# Extract tokens by language and folio
azc_tokens = []
a_tokens = []
b_tokens = []

for line in lines[1:]:
    parts = line.strip().split('\t')
    if len(parts) >= len(header):
        row = {header[i]: parts[i].strip('"') for i in range(len(header))}
        # Filter to PRIMARY transcriber (H) only
        if row.get('transcriber', '').strip() != 'H':
            continue
        lang = row.get('language', '')
        if lang == 'NA' or lang == '':
            azc_tokens.append(row)
        elif lang == 'A':
            a_tokens.append(row)
        elif lang == 'B':
            b_tokens.append(row)

# Build folio vocabulary sets
azc_folio_vocab = defaultdict(set)
a_folio_vocab = defaultdict(set)
b_folio_vocab = defaultdict(set)

azc_folio_section = {}

for t in azc_tokens:
    folio = t.get('folio', '')
    azc_folio_vocab[folio].add(t['word'])
    azc_folio_section[folio] = t.get('section', '')

for t in a_tokens:
    folio = t.get('folio', '')
    a_folio_vocab[folio].add(t['word'])

for t in b_tokens:
    folio = t.get('folio', '')
    b_folio_vocab[folio].add(t['word'])

print(f"\nFolio counts:")
print(f"  AZC: {len(azc_folio_vocab)} folios")
print(f"  A:   {len(a_folio_vocab)} folios")
print(f"  B:   {len(b_folio_vocab)} folios")

# === TEST 1: AZC-to-A Folio Links ===
print("\n" + "=" * 70)
print("TEST 1: AZC -> A FOLIO PREFERENTIAL LINKS")
print("=" * 70)

# For each AZC folio, find Jaccard similarity to each A folio
azc_a_links = {}

for azc_folio, azc_vocab in azc_folio_vocab.items():
    best_matches = []
    for a_folio, a_vocab in a_folio_vocab.items():
        intersection = len(azc_vocab.intersection(a_vocab))
        union = len(azc_vocab.union(a_vocab))
        jaccard = intersection / union if union > 0 else 0
        if intersection >= 5:  # Minimum overlap threshold
            best_matches.append((a_folio, jaccard, intersection))

    best_matches.sort(key=lambda x: -x[1])
    azc_a_links[azc_folio] = best_matches[:5]  # Top 5

print("\nTop AZC -> A folio links (Jaccard similarity, min 5 shared tokens):")
print(f"{'AZC Folio':<12} {'Section':<4} {'Top A Match':<12} {'Jaccard':<10} {'Shared':<8}")
print("-" * 55)

for azc_folio in sorted(azc_a_links.keys()):
    matches = azc_a_links[azc_folio]
    section = azc_folio_section.get(azc_folio, '?')
    if matches:
        top = matches[0]
        print(f"{azc_folio:<12} {section:<4} {top[0]:<12} {top[1]:<10.3f} {top[2]:<8}")

# === TEST 2: AZC-to-B Folio Links ===
print("\n" + "=" * 70)
print("TEST 2: AZC -> B FOLIO PREFERENTIAL LINKS")
print("=" * 70)

azc_b_links = {}

for azc_folio, azc_vocab in azc_folio_vocab.items():
    best_matches = []
    for b_folio, b_vocab in b_folio_vocab.items():
        intersection = len(azc_vocab.intersection(b_vocab))
        union = len(azc_vocab.union(b_vocab))
        jaccard = intersection / union if union > 0 else 0
        if intersection >= 5:
            best_matches.append((b_folio, jaccard, intersection))

    best_matches.sort(key=lambda x: -x[1])
    azc_b_links[azc_folio] = best_matches[:5]

print("\nTop AZC -> B folio links:")
print(f"{'AZC Folio':<12} {'Section':<4} {'Top B Match':<12} {'Jaccard':<10} {'Shared':<8}")
print("-" * 55)

for azc_folio in sorted(azc_b_links.keys()):
    matches = azc_b_links[azc_folio]
    section = azc_folio_section.get(azc_folio, '?')
    if matches:
        top = matches[0]
        print(f"{azc_folio:<12} {section:<4} {top[0]:<12} {top[1]:<10.3f} {top[2]:<8}")

# === TEST 3: Link Concentration vs Uniformity ===
print("\n" + "=" * 70)
print("TEST 3: LINK CONCENTRATION (PREFERENTIAL vs UNIFORM)")
print("=" * 70)

# For each AZC folio, calculate how concentrated its links are
# High concentration = links to few folios (preferential)
# Low concentration = links to many folios (uniform)

def gini_coefficient(values):
    """Calculate Gini coefficient (0 = uniform, 1 = concentrated)"""
    if not values or sum(values) == 0:
        return 0
    sorted_values = sorted(values)
    n = len(sorted_values)
    cumulative = 0
    for i, v in enumerate(sorted_values):
        cumulative += (2 * (i + 1) - n - 1) * v
    return cumulative / (n * sum(sorted_values))

azc_a_concentration = {}
azc_b_concentration = {}

for azc_folio, azc_vocab in azc_folio_vocab.items():
    # A links
    a_overlaps = []
    for a_folio, a_vocab in a_folio_vocab.items():
        overlap = len(azc_vocab.intersection(a_vocab))
        if overlap > 0:
            a_overlaps.append(overlap)
    if a_overlaps:
        azc_a_concentration[azc_folio] = gini_coefficient(a_overlaps)

    # B links
    b_overlaps = []
    for b_folio, b_vocab in b_folio_vocab.items():
        overlap = len(azc_vocab.intersection(b_vocab))
        if overlap > 0:
            b_overlaps.append(overlap)
    if b_overlaps:
        azc_b_concentration[azc_folio] = gini_coefficient(b_overlaps)

mean_a_gini = sum(azc_a_concentration.values()) / len(azc_a_concentration) if azc_a_concentration else 0
mean_b_gini = sum(azc_b_concentration.values()) / len(azc_b_concentration) if azc_b_concentration else 0

print(f"\nLink concentration (Gini coefficient):")
print(f"  0.0 = perfectly uniform (links equally to all folios)")
print(f"  1.0 = perfectly concentrated (links to one folio)")
print(f"\n  Mean AZC->A concentration: {mean_a_gini:.3f}")
print(f"  Mean AZC->B concentration: {mean_b_gini:.3f}")

if mean_a_gini > 0.3 or mean_b_gini > 0.3:
    print("\n  Result: PREFERENTIAL LINKING detected")
else:
    print("\n  Result: Links are relatively UNIFORM")

# === TEST 4: Section-Specific Link Patterns ===
print("\n" + "=" * 70)
print("TEST 4: SECTION-SPECIFIC LINK PATTERNS")
print("=" * 70)

# Group AZC folios by section
section_a_targets = defaultdict(Counter)
section_b_targets = defaultdict(Counter)

for azc_folio, azc_vocab in azc_folio_vocab.items():
    section = azc_folio_section.get(azc_folio, '?')

    # Find top A links
    for a_folio, a_vocab in a_folio_vocab.items():
        overlap = len(azc_vocab.intersection(a_vocab))
        if overlap >= 10:
            section_a_targets[section][a_folio] += overlap

    # Find top B links
    for b_folio, b_vocab in b_folio_vocab.items():
        overlap = len(azc_vocab.intersection(b_vocab))
        if overlap >= 10:
            section_b_targets[section][b_folio] += overlap

print("\nTop A folio targets by AZC section:")
for section in ['Z', 'A', 'C']:
    if section in section_a_targets:
        top = section_a_targets[section].most_common(5)
        top_str = ", ".join(f"{f}({c})" for f, c in top)
        print(f"  {section}: {top_str}")

print("\nTop B folio targets by AZC section:")
for section in ['Z', 'A', 'C']:
    if section in section_b_targets:
        top = section_b_targets[section].most_common(5)
        top_str = ", ".join(f"{f}({c})" for f, c in top)
        print(f"  {section}: {top_str}")

# === TEST 5: Do Different AZC Sections Link to Different A Sections? ===
print("\n" + "=" * 70)
print("TEST 5: AZC SECTION -> A SECTION MAPPING")
print("=" * 70)

# Get A folio sections
a_folio_section = {}
for t in a_tokens:
    folio = t.get('folio', '')
    a_folio_section[folio] = t.get('section', '')

# For each AZC section, count links to each A section
azc_to_a_section = defaultdict(Counter)

for azc_folio, azc_vocab in azc_folio_vocab.items():
    azc_sec = azc_folio_section.get(azc_folio, '?')

    for a_folio, a_vocab in a_folio_vocab.items():
        overlap = len(azc_vocab.intersection(a_vocab))
        if overlap >= 5:
            a_sec = a_folio_section.get(a_folio, '?')
            azc_to_a_section[azc_sec][a_sec] += overlap

print("\nAZC Section -> A Section link strength:")
print(f"{'AZC':<6} {'H':<10} {'P':<10} {'T':<10} {'Dominant':<10}")
print("-" * 50)

for azc_sec in ['Z', 'A', 'C']:
    if azc_sec in azc_to_a_section:
        counts = azc_to_a_section[azc_sec]
        total = sum(counts.values())
        h_pct = counts.get('H', 0) / total * 100 if total else 0
        p_pct = counts.get('P', 0) / total * 100 if total else 0
        t_pct = counts.get('T', 0) / total * 100 if total else 0
        dominant = max(counts, key=counts.get) if counts else '?'
        print(f"{azc_sec:<6} {h_pct:<10.1f} {p_pct:<10.1f} {t_pct:<10.1f} {dominant:<10}")

# === VERDICT ===
print("\n" + "=" * 70)
print("VERDICT")
print("=" * 70)

print(f"""
FINDINGS:

1. Link Concentration:
   - AZC->A Gini: {mean_a_gini:.3f}
   - AZC->B Gini: {mean_b_gini:.3f}
   {"- PREFERENTIAL linking detected" if mean_a_gini > 0.3 or mean_b_gini > 0.3 else "- Links are relatively UNIFORM"}

2. Section-Specific Patterns:
   - Different AZC sections (Z, A, C) link to {"DIFFERENT" if len(set(azc_to_a_section.get('Z', {}).keys()) ^ set(azc_to_a_section.get('C', {}).keys())) > 0 else "SAME"} A section profiles

3. Interpretation:
""")

if mean_a_gini > 0.4 and mean_b_gini > 0.4:
    print("   STRONG PREFERENTIAL LINKS: AZC folios coordinate with SPECIFIC")
    print("   A/B folios, not uniformly. Supports calendar/coordination hypothesis.")
elif mean_a_gini > 0.3 or mean_b_gini > 0.3:
    print("   MODERATE PREFERENTIAL LINKS: Some specificity detected.")
    print("   Partial support for coordination hypothesis.")
else:
    print("   UNIFORM LINKS: AZC links broadly to A/B vocabulary.")
    print("   Does NOT support specific folio-to-folio coordination.")
    print("   May indicate general vocabulary bridge rather than scheduling.")

print("\n" + "=" * 70)
print("FOLIO LINK TEST COMPLETE")
print("=" * 70)
