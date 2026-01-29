#!/usr/bin/env python3
"""
LINK DENSITY RECONCILIATION

Resolves the discrepancy between token-level LINK density (6.6%) and the
"38% weighted by folio" figure in the Tier 0 frozen conclusion.

Sections:
1. Token-Level LINK Census (total count, by section, verify C334)
2. Folio-Level LINK Density Distribution (per-folio, test 38% interpretations)
3. Line-Level LINK Density (per-line, test "38% of lines" interpretation)
4. LINK-ICC Cross-Classification (LINK tokens mapped to ICC roles)
"""

import os
import sys
import json
from collections import Counter, defaultdict

os.chdir('C:/git/voynich')
sys.path.insert(0, '.')

from scripts.voynich import Transcript, Morphology

# ==============================================================================
# LOAD DATA
# ==============================================================================

print("=" * 70)
print("LINK DENSITY RECONCILIATION")
print("Resolving the 6.6% vs 38% discrepancy")
print("=" * 70)

tx = Transcript()
morph = Morphology()

# Load all B tokens
b_tokens = []
for token in tx.currier_b():
    b_tokens.append(token)

print(f"\nTotal Currier B tokens: {len(b_tokens)}")

# Load ICC class map
with open('phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json', 'r') as f:
    class_map = json.load(f)

token_to_class = class_map['token_to_class']
class_to_role = class_map['class_to_role']

# Role name abbreviation map
ROLE_ABBREV = {
    'CORE_CONTROL': 'CC',
    'ENERGY_OPERATOR': 'EN',
    'FLOW_OPERATOR': 'FL',
    'FREQUENT_OPERATOR': 'FQ',
    'AUXILIARY': 'AX',
}

def is_link(word):
    """Canonical LINK definition: contains 'ol' substring."""
    return 'ol' in word if word else False

# ==============================================================================
# SECTION 1: TOKEN-LEVEL LINK CENSUS
# ==============================================================================

print("\n" + "=" * 70)
print("SECTION 1: TOKEN-LEVEL LINK CENSUS")
print("=" * 70)

# Count LINK tokens
link_tokens = [t for t in b_tokens if is_link(t.word)]
non_link_tokens = [t for t in b_tokens if not is_link(t.word)]

link_pct = len(link_tokens) / len(b_tokens) * 100
print(f"\nLINK tokens: {len(link_tokens)} / {len(b_tokens)} = {link_pct:.1f}%")
print(f"Non-LINK tokens: {len(non_link_tokens)}")

# By section
section_counts = defaultdict(lambda: {'total': 0, 'link': 0})
for t in b_tokens:
    sec = t.section if t.section else 'UNKNOWN'
    section_counts[sec]['total'] += 1
    if is_link(t.word):
        section_counts[sec]['link'] += 1

print(f"\nLINK by Section (verify against C334):")
print(f"{'Section':<12} {'Total':>8} {'LINK':>8} {'Density':>10} {'C334':>10}")
print("-" * 50)

# C334 reference values
c334_ref = {'B': 19.6, 'H': 9.1, 'C': 10.1, 'S': 9.8}

for sec in sorted(section_counts.keys()):
    ct = section_counts[sec]
    density = ct['link'] / ct['total'] * 100 if ct['total'] > 0 else 0
    ref = c334_ref.get(sec, '---')
    print(f"{sec:<12} {ct['total']:>8} {ct['link']:>8} {density:>9.1f}% {str(ref):>10}")

# Unique LINK types
link_types = Counter(t.word for t in link_tokens)
print(f"\nUnique LINK types: {len(link_types)}")
print(f"Top 10 most frequent LINK tokens:")
for word, count in link_types.most_common(10):
    print(f"  {word:<20} {count:>5}x")

# ==============================================================================
# SECTION 2: FOLIO-LEVEL LINK DENSITY DISTRIBUTION
# ==============================================================================

print("\n" + "=" * 70)
print("SECTION 2: FOLIO-LEVEL LINK DENSITY DISTRIBUTION")
print("=" * 70)

# Group by folio
folio_data = defaultdict(lambda: {'total': 0, 'link': 0})
for t in b_tokens:
    folio_data[t.folio]['total'] += 1
    if is_link(t.word):
        folio_data[t.folio]['link'] += 1

folio_densities = []
folio_details = []
for folio in sorted(folio_data.keys()):
    fd = folio_data[folio]
    density = fd['link'] / fd['total'] if fd['total'] > 0 else 0
    folio_densities.append(density)
    folio_details.append({
        'folio': folio,
        'total': fd['total'],
        'link': fd['link'],
        'density': density,
    })

import numpy as np
densities_arr = np.array(folio_densities)

print(f"\nNumber of B folios: {len(folio_densities)}")
print(f"\nFolio-level LINK density statistics:")
print(f"  Mean:   {densities_arr.mean():.4f} ({densities_arr.mean()*100:.1f}%)")
print(f"  Median: {np.median(densities_arr):.4f} ({np.median(densities_arr)*100:.1f}%)")
print(f"  Std:    {densities_arr.std():.4f}")
print(f"  Min:    {densities_arr.min():.4f} ({densities_arr.min()*100:.1f}%)")
print(f"  Max:    {densities_arr.max():.4f} ({densities_arr.max()*100:.1f}%)")

# Test: does mean(folio densities) = 38%?
print(f"\n--- TEST: Does mean(folio_density) = 38%? ---")
print(f"  Mean of folio densities: {densities_arr.mean()*100:.1f}%")
print(f"  {'YES' if abs(densities_arr.mean()*100 - 38) < 2 else 'NO'}: ", end="")
if abs(densities_arr.mean()*100 - 38) < 2:
    print("Mean of per-folio densities matches 38%")
else:
    print(f"Mean is {densities_arr.mean()*100:.1f}%, not 38%")

# Weighted mean (by token count)
total_link = sum(fd['link'] for fd in folio_data.values())
total_all = sum(fd['total'] for fd in folio_data.values())
weighted_pct = total_link / total_all * 100
print(f"\n  Token-weighted density: {weighted_pct:.1f}%")
print(f"  {'YES' if abs(weighted_pct - 38) < 2 else 'NO'}: ", end="")
if abs(weighted_pct - 38) < 2:
    print("Token-weighted matches 38%")
else:
    print(f"Token-weighted is {weighted_pct:.1f}%, not 38%")

# Test: proportion of folios with density > various thresholds
for threshold in [0.05, 0.10, 0.20, 0.30, 0.38, 0.50]:
    prop = np.mean(densities_arr > threshold)
    print(f"  Folios with density > {threshold*100:.0f}%: {prop*100:.1f}% ({np.sum(densities_arr > threshold)} folios)")

# Test: proportion of folios with ANY LINK token
has_link = np.mean(densities_arr > 0)
print(f"\n  Folios with at least 1 LINK: {has_link*100:.1f}% ({np.sum(densities_arr > 0)} of {len(folio_densities)})")

# Distribution histogram (text-based)
print(f"\nFolio density distribution:")
bins = [0, 0.02, 0.05, 0.08, 0.10, 0.15, 0.20, 0.30, 0.50, 1.0]
for i in range(len(bins) - 1):
    count = np.sum((densities_arr >= bins[i]) & (densities_arr < bins[i+1]))
    bar = '#' * count
    print(f"  {bins[i]*100:5.0f}%-{bins[i+1]*100:4.0f}%: {count:3d} {bar}")

# ==============================================================================
# SECTION 3: LINE-LEVEL LINK DENSITY
# ==============================================================================

print("\n" + "=" * 70)
print("SECTION 3: LINE-LEVEL LINK DENSITY")
print("=" * 70)

# Group by (folio, line)
line_data = defaultdict(lambda: {'total': 0, 'link': 0})
for t in b_tokens:
    key = (t.folio, t.line)
    line_data[key]['total'] += 1
    if is_link(t.word):
        line_data[key]['link'] += 1

line_densities = []
lines_with_link = 0
total_lines = 0

for key in sorted(line_data.keys()):
    ld = line_data[key]
    if ld['total'] > 0:
        density = ld['link'] / ld['total']
        line_densities.append(density)
        total_lines += 1
        if ld['link'] > 0:
            lines_with_link += 1

line_densities_arr = np.array(line_densities)
lines_with_link_pct = lines_with_link / total_lines * 100

print(f"\nTotal B lines: {total_lines}")
print(f"Lines with >=1 LINK: {lines_with_link} ({lines_with_link_pct:.1f}%)")

print(f"\n--- TEST: Does '38% of lines contain LINK' match? ---")
print(f"  Lines with >=1 LINK: {lines_with_link_pct:.1f}%")
print(f"  {'YES' if abs(lines_with_link_pct - 38) < 2 else 'NO'}: ", end="")
if abs(lines_with_link_pct - 38) < 2:
    print("Line coverage matches 38%!")
else:
    print(f"Line coverage is {lines_with_link_pct:.1f}%, not 38%")

# Line-level density statistics
print(f"\nLine-level LINK density statistics (all lines):")
print(f"  Mean:   {line_densities_arr.mean():.4f} ({line_densities_arr.mean()*100:.1f}%)")
print(f"  Median: {np.median(line_densities_arr):.4f}")

# Among lines that have LINK
link_line_densities = line_densities_arr[line_densities_arr > 0]
if len(link_line_densities) > 0:
    print(f"\nAmong lines with >=1 LINK (n={len(link_line_densities)}):")
    print(f"  Mean density: {link_line_densities.mean():.4f} ({link_line_densities.mean()*100:.1f}%)")
    print(f"  Median density: {np.median(link_line_densities):.4f}")
    print(f"  Max density: {link_line_densities.max():.4f}")

# LINK count per line distribution
link_per_line = [line_data[key]['link'] for key in sorted(line_data.keys()) if line_data[key]['total'] > 0]
link_count_dist = Counter(link_per_line)
print(f"\nLINK tokens per line distribution:")
for count in sorted(link_count_dist.keys()):
    n = link_count_dist[count]
    pct = n / total_lines * 100
    bar = '#' * min(n // 5, 40)
    print(f"  {count} LINK: {n:>5} lines ({pct:.1f}%) {bar}")

# ==============================================================================
# SECTION 4: LINK-ICC CROSS-CLASSIFICATION
# ==============================================================================

print("\n" + "=" * 70)
print("SECTION 4: LINK-ICC CROSS-CLASSIFICATION")
print("=" * 70)

# For each LINK token, look up ICC class
link_classified = 0
link_unclassified = 0
link_role_counts = Counter()
link_class_counts = Counter()

for t in link_tokens:
    word = t.word
    if word in token_to_class:
        cls = str(token_to_class[word])
        role = class_to_role.get(cls, 'UNKNOWN')
        abbrev = ROLE_ABBREV.get(role, role)
        link_role_counts[abbrev] += 1
        link_class_counts[cls] += 1
        link_classified += 1
    else:
        link_role_counts['UN'] += 1
        link_unclassified += 1

total_link = len(link_tokens)
print(f"\nLINK tokens: {total_link}")
print(f"  Classified (in ICC): {link_classified} ({link_classified/total_link*100:.1f}%)")
print(f"  Unclassified (UN):   {link_unclassified} ({link_unclassified/total_link*100:.1f}%)")

print(f"\nLINK distribution across ICC roles:")
print(f"{'Role':<6} {'Count':>8} {'% of LINK':>10} {'% of role':>12}")
print("-" * 40)

# Also compute total per role for context
role_totals = Counter()
for t in b_tokens:
    if t.word in token_to_class:
        cls = str(token_to_class[t.word])
        role = class_to_role.get(cls, 'UNKNOWN')
        abbrev = ROLE_ABBREV.get(role, role)
        role_totals[abbrev] += 1
    else:
        role_totals['UN'] += 1

for role in ['CC', 'EN', 'FL', 'FQ', 'AX', 'UN']:
    count = link_role_counts.get(role, 0)
    pct_link = count / total_link * 100 if total_link > 0 else 0
    pct_role = count / role_totals[role] * 100 if role_totals.get(role, 0) > 0 else 0
    print(f"{role:<6} {count:>8} {pct_link:>9.1f}% {pct_role:>11.1f}%")

# LINK by ICC class (top classes)
print(f"\nTop ICC classes among LINK tokens:")
for cls, count in link_class_counts.most_common(15):
    role = class_to_role.get(cls, '?')
    abbrev = ROLE_ABBREV.get(role, role)
    pct = count / total_link * 100
    print(f"  Class {cls:>3} ({abbrev:<3}): {count:>5} ({pct:.1f}%)")

# Morphological analysis: where does 'ol' appear?
print(f"\nMorphological position of 'ol' in LINK tokens:")
ol_positions = Counter()  # prefix, middle, suffix, compound
for t in link_tokens:
    word = t.word
    m = morph.extract(word)
    positions = []
    if m.prefix and 'ol' in m.prefix:
        positions.append('PREFIX')
    if m.middle and 'ol' in m.middle:
        positions.append('MIDDLE')
    if m.suffix and 'ol' in m.suffix:
        positions.append('SUFFIX')
    if not positions:
        positions.append('SPAN')  # 'ol' spans morphological boundaries
    for pos in positions:
        ol_positions[pos] += 1

for pos in ['PREFIX', 'MIDDLE', 'SUFFIX', 'SPAN']:
    count = ol_positions.get(pos, 0)
    pct = count / total_link * 100
    print(f"  {pos:<8}: {count:>6} ({pct:.1f}%)")

# Is class 11 the standalone 'ol' class?
class_11_tokens = [word for word, cls in token_to_class.items() if cls == 11]
class_11_link = sum(1 for w in class_11_tokens if 'ol' in w)
print(f"\nClass 11 analysis:")
print(f"  Total class 11 tokens: {len(class_11_tokens)}")
print(f"  Class 11 tokens with 'ol': {class_11_link} ({class_11_link/len(class_11_tokens)*100:.1f}% if class 11 has members)")
# Sample class 11 tokens
print(f"  Sample class 11 tokens: {class_11_tokens[:10]}")

# Check if 'ol' standalone is a token
ol_standalone = sum(1 for t in b_tokens if t.word == 'ol')
print(f"  Standalone 'ol' token count: {ol_standalone}")

# ==============================================================================
# SECTION 5: RECONCILIATION SUMMARY
# ==============================================================================

print("\n" + "=" * 70)
print("SECTION 5: RECONCILIATION SUMMARY")
print("=" * 70)

print(f"\n--- LINK Density by Measurement Level ---")
print(f"  Token-level:       {link_pct:.1f}% ({len(link_tokens)}/{len(b_tokens)})")
print(f"  Folio mean:        {densities_arr.mean()*100:.1f}%")
print(f"  Folio median:      {np.median(densities_arr)*100:.1f}%")
print(f"  Line coverage:     {lines_with_link_pct:.1f}% (lines with >=1 LINK)")
print(f"  Line mean density: {line_densities_arr.mean()*100:.1f}%")

print(f"\n--- VERDICT on 38% ---")
candidates = {
    'Token-level': link_pct,
    'Folio mean': densities_arr.mean() * 100,
    'Folio median': np.median(densities_arr) * 100,
    'Line coverage': lines_with_link_pct,
    'Line mean density': line_densities_arr.mean() * 100,
}

best_match = None
best_dist = float('inf')
for name, val in candidates.items():
    dist = abs(val - 38)
    print(f"  {name:<20}: {val:.1f}% (distance from 38%: {dist:.1f}pp)")
    if dist < best_dist:
        best_dist = dist
        best_match = name

print(f"\n  Closest match: {best_match} ({candidates[best_match]:.1f}%)")
if best_dist < 5:
    print(f"  INTERPRETATION: '38%' likely means '{best_match}'")
else:
    print(f"  WARNING: No measurement level reproduces 38% (closest: {best_dist:.1f}pp away)")

# Check alternative LINK definitions
print(f"\n--- Alternative LINK Definitions ---")

# Maybe 38% uses a broader definition?
# Test: tokens where 'ol' is in any position (prefix 'ol')
prefix_ol = sum(1 for t in b_tokens if t.word.startswith('ol'))
print(f"  Tokens starting with 'ol': {prefix_ol} ({prefix_ol/len(b_tokens)*100:.1f}%)")

# Test: tokens with 'o' followed by 'l' anywhere
import re
ol_regex = sum(1 for t in b_tokens if re.search(r'o.*l', t.word or ''))
print(f"  Tokens matching o.*l regex: {ol_regex} ({ol_regex/len(b_tokens)*100:.1f}%)")

# Test: does including A/AZC change things?
all_tokens_list = list(tx.all())
all_link = sum(1 for t in all_tokens_list if is_link(t.word))
print(f"  LINK across all systems: {all_link}/{len(all_tokens_list)} ({all_link/len(all_tokens_list)*100:.1f}%)")

# Check what "weighted by folio" might mean for C334 section densities
print(f"\n--- C334 Section Density Reconciliation ---")
print(f"  The '38%' reference includes 'weighted by folio' qualifier")
print(f"  C334 shows section B = 19.6%, which is the highest section density")
print(f"  None of the section densities reach 38%")

# ==============================================================================
# SAVE RESULTS
# ==============================================================================

results = {
    'token_level': {
        'total_b': len(b_tokens),
        'link_count': len(link_tokens),
        'link_pct': round(link_pct, 2),
        'unique_link_types': len(link_types),
    },
    'section_densities': {
        sec: {
            'total': section_counts[sec]['total'],
            'link': section_counts[sec]['link'],
            'density_pct': round(section_counts[sec]['link'] / section_counts[sec]['total'] * 100, 2) if section_counts[sec]['total'] > 0 else 0,
        }
        for sec in sorted(section_counts.keys())
    },
    'folio_level': {
        'n_folios': len(folio_densities),
        'mean_density': round(float(densities_arr.mean()), 4),
        'median_density': round(float(np.median(densities_arr)), 4),
        'std_density': round(float(densities_arr.std()), 4),
        'min_density': round(float(densities_arr.min()), 4),
        'max_density': round(float(densities_arr.max()), 4),
        'folios_with_link': int(np.sum(densities_arr > 0)),
        'pct_folios_with_link': round(float(np.mean(densities_arr > 0) * 100), 1),
    },
    'line_level': {
        'total_lines': total_lines,
        'lines_with_link': lines_with_link,
        'pct_lines_with_link': round(lines_with_link_pct, 1),
        'mean_line_density': round(float(line_densities_arr.mean()), 4),
    },
    'icc_cross_classification': {
        'classified': link_classified,
        'unclassified': link_unclassified,
        'by_role': dict(link_role_counts),
        'by_class_top10': dict(link_class_counts.most_common(10)),
    },
    'ol_morphological_position': dict(ol_positions),
    'reconciliation': {
        'best_match': best_match,
        'best_match_value': round(candidates[best_match], 1),
        'distance_from_38': round(best_dist, 1),
        'all_candidates': {k: round(v, 1) for k, v in candidates.items()},
    },
}

output_path = 'phases/LINK_DENSITY_RECONCILIATION/results/link_density_audit.json'
with open(output_path, 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to {output_path}")
print(f"\n{'=' * 70}")
print("LINK DENSITY RECONCILIATION COMPLETE")
print(f"{'=' * 70}")
