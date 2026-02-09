#!/usr/bin/env python3
"""
Test 20: Do Rosettes Labels Reference Specific B Folios?

Hypothesis: Rosettes are a high-level map referencing other B folios.
Test: Do Rosettes label tokens cluster with specific B folios?

If true:
- Each Rosettes circle should share vocabulary with specific B folios
- Not random distribution across all B folios
"""

import sys
sys.path.insert(0, 'C:/git/voynich')

from pathlib import Path
from collections import defaultdict, Counter
import numpy as np

filepath = Path('C:/git/voynich/data/transcriptions/interlinear_full_words.txt')

ROSETTES = {'f85r1', 'f85r2', 'f86v3', 'f86v4', 'f86v5', 'f86v6'}

# Collect Rosettes labels by sub-folio
rosettes_by_subfolio = defaultdict(set)

# Collect B folio vocabulary
b_folio_tokens = defaultdict(set)
b_folio_sections = {}

with open(filepath, 'r', encoding='utf-8') as f:
    header = f.readline()
    for line in f:
        parts = line.strip().split('\t')
        if len(parts) > 12:
            transcriber = parts[12].strip('"').strip()
            if transcriber != 'H':
                continue

            currier = parts[6].strip('"').strip()
            folio = parts[2].strip('"').strip()
            section = parts[3].strip('"').strip()
            token = parts[0].strip('"').strip().lower()
            placement = parts[10].strip('"').strip()

            if not token.strip() or '*' in token:
                continue

            if folio in ROSETTES:
                # Only label placements
                if placement in ['C', 'C1', 'C2', 'Q', 'T']:
                    rosettes_by_subfolio[folio].add(token)
            elif currier == 'B' and folio not in ROSETTES:
                b_folio_tokens[folio].add(token)
                b_folio_sections[folio] = section

print("=" * 70)
print("TEST 20: DO ROSETTES LABELS REFERENCE SPECIFIC B FOLIOS?")
print("=" * 70)
print()

# 1. Overview
print("1. DATA OVERVIEW")
print("-" * 50)

for subfolio in sorted(rosettes_by_subfolio.keys()):
    print(f"{subfolio}: {len(rosettes_by_subfolio[subfolio])} unique label tokens")

print(f"\nTotal B folios (non-Rosettes): {len(b_folio_tokens)}")
print()

# 2. For each Rosettes sub-folio, find B folios with highest vocabulary overlap
print("2. ROSETTES -> B FOLIO VOCABULARY OVERLAP")
print("-" * 50)

for subfolio in sorted(rosettes_by_subfolio.keys()):
    ros_tokens = rosettes_by_subfolio[subfolio]

    overlaps = []
    for b_folio, b_tokens in b_folio_tokens.items():
        shared = ros_tokens & b_tokens
        if shared:
            jaccard = len(shared) / len(ros_tokens | b_tokens)
            overlap_pct = len(shared) / len(ros_tokens) * 100
            overlaps.append((b_folio, len(shared), overlap_pct, jaccard, b_folio_sections.get(b_folio, '?')))

    overlaps.sort(key=lambda x: -x[1])

    print(f"\n{subfolio} ({len(ros_tokens)} label tokens):")
    print(f"  Top B folios by shared tokens:")

    for b_folio, shared, pct, jaccard, section in overlaps[:10]:
        print(f"    {b_folio} ({section}): {shared} shared ({pct:.1f}% of Rosettes labels)")

print()

# 3. Are there B folios that appear in multiple Rosettes sub-folios?
print("3. B FOLIOS REFERENCED BY MULTIPLE ROSETTES SUB-FOLIOS")
print("-" * 50)

b_folio_appearances = defaultdict(list)

for subfolio in rosettes_by_subfolio:
    ros_tokens = rosettes_by_subfolio[subfolio]

    for b_folio, b_tokens in b_folio_tokens.items():
        shared = ros_tokens & b_tokens
        if len(shared) >= 5:  # At least 5 shared tokens
            b_folio_appearances[b_folio].append((subfolio, len(shared)))

# Sort by number of Rosettes sub-folios that reference them
multi_ref = [(b, apps) for b, apps in b_folio_appearances.items() if len(apps) >= 3]
multi_ref.sort(key=lambda x: -len(x[1]))

print(f"B folios referenced by 3+ Rosettes sub-folios (>=5 shared tokens each):")
print()

for b_folio, appearances in multi_ref[:15]:
    section = b_folio_sections.get(b_folio, '?')
    refs = ', '.join(f"{sub}({n})" for sub, n in appearances)
    print(f"  {b_folio} ({section}): {refs}")

print()

# 4. Section distribution of referenced B folios
print("4. SECTION DISTRIBUTION OF TOP-REFERENCED B FOLIOS")
print("-" * 50)

# For each Rosettes sub-folio, what sections do its top matches come from?
for subfolio in sorted(rosettes_by_subfolio.keys()):
    ros_tokens = rosettes_by_subfolio[subfolio]

    section_counts = Counter()
    for b_folio, b_tokens in b_folio_tokens.items():
        shared = ros_tokens & b_tokens
        if len(shared) >= 3:
            section = b_folio_sections.get(b_folio, '?')
            section_counts[section] += len(shared)

    print(f"\n{subfolio} -> B section distribution:")
    for section, count in section_counts.most_common():
        print(f"  {section}: {count} shared tokens")

print()

# 5. Specificity test: Are references concentrated or diffuse?
print("5. REFERENCE SPECIFICITY TEST")
print("-" * 50)
print("If Rosettes reference specific folios, vocabulary should be concentrated.")
print("If generic B vocabulary, it should be diffuse across all B folios.")
print()

for subfolio in sorted(rosettes_by_subfolio.keys()):
    ros_tokens = rosettes_by_subfolio[subfolio]

    # Count how many B folios each Rosettes token appears in
    token_spread = []
    for token in ros_tokens:
        n_folios = sum(1 for b_tokens in b_folio_tokens.values() if token in b_tokens)
        token_spread.append(n_folios)

    mean_spread = np.mean(token_spread) if token_spread else 0
    median_spread = np.median(token_spread) if token_spread else 0

    # Concentrated tokens (appear in <5 B folios)
    concentrated = sum(1 for s in token_spread if 0 < s < 5)
    diffuse = sum(1 for s in token_spread if s >= 10)

    print(f"{subfolio}:")
    print(f"  Mean B-folio spread per token: {mean_spread:.1f}")
    print(f"  Median B-folio spread: {median_spread:.1f}")
    print(f"  Concentrated tokens (<5 folios): {concentrated} ({concentrated/len(ros_tokens)*100:.1f}%)")
    print(f"  Diffuse tokens (>=10 folios): {diffuse} ({diffuse/len(ros_tokens)*100:.1f}%)")

print()

# 6. Summary
print("=" * 70)
print("CONCLUSION")
print("=" * 70)

# Calculate overall diffusion
all_ros_tokens = set()
for tokens in rosettes_by_subfolio.values():
    all_ros_tokens.update(tokens)

all_spreads = []
for token in all_ros_tokens:
    n_folios = sum(1 for b_tokens in b_folio_tokens.values() if token in b_tokens)
    all_spreads.append(n_folios)

mean_overall = np.mean(all_spreads)
concentrated_overall = sum(1 for s in all_spreads if 0 < s < 5) / len(all_spreads) * 100
diffuse_overall = sum(1 for s in all_spreads if s >= 10) / len(all_spreads) * 100

print(f"""
ROSETTES REFERENCE PATTERN:

Overall token spread: mean {mean_overall:.1f} B folios per token
- Concentrated (<5 folios): {concentrated_overall:.1f}%
- Diffuse (>=10 folios): {diffuse_overall:.1f}%
""")

if diffuse_overall > 50:
    print("VERDICT: DIFFUSE - Rosettes use generic B vocabulary")
    print("The labels are common execution terms, not specific folio references.")
    print("Rosettes are a PROCEDURAL DOCUMENT using standard B vocabulary,")
    print("not an INDEX pointing to specific procedures elsewhere.")
elif concentrated_overall > 30:
    print("VERDICT: MIXED - Some concentrated, some diffuse vocabulary")
    print("Rosettes may reference specific folios for some content")
    print("while using generic B vocabulary for others.")
else:
    print("VERDICT: CONCENTRATED - Rosettes reference specific B folios")
    print("The labels point to particular procedures in the manuscript.")
