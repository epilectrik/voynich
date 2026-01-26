#!/usr/bin/env python3
"""
Test: Do the OLD and NEW suffix frameworks align or conflict?

OLD: Suffix correlates with A/B enrichment (decision archetype)
NEW: Suffix correlates with material class (fire degree)

If they ALIGN: A/B enrichment should track with animal/herb pattern
If they CONFLICT: We need to choose or reconcile
"""

import json
import csv
from collections import Counter, defaultdict
from pathlib import Path

PROJECT_ROOT = Path('.')

with open(PROJECT_ROOT / 'phases' / 'A_INTERNAL_STRATIFICATION' / 'results' / 'middle_classes.json', 'r') as f:
    data = json.load(f)
pp_middles = set(data['a_shared_middles'])

KNOWN_PREFIXES = ['qo', 'ol', 'or', 'al', 'ar', 'ok', 'ot', 'ch', 'sh', 'ct', 'd', 's', 'y', 'o', 'a', 'k', 't', 'p', 'f', 'c']
KNOWN_SUFFIXES = ['eedy', 'edy', 'aiy', 'dy', 'ey', 'y', 'am', 'an', 'ar', 'al', 'or', 'ol', 'od', 'os']

animal_pp = {'te', 'ho', 'ke'}

def extract_parts(token):
    if not token:
        return None, None, None
    prefix = None
    suffix = None
    for p in sorted(KNOWN_PREFIXES, key=len, reverse=True):
        if token.startswith(p):
            prefix = p
            token = token[len(p):]
            break
    for s in sorted(KNOWN_SUFFIXES, key=len, reverse=True):
        if token.endswith(s) and len(token) > len(s):
            suffix = s
            token = token[:-len(s)]
            break
    return prefix, token if token else None, suffix

# Collect suffix counts by Currier type (A vs B)
suffix_by_currier = {'A': Counter(), 'B': Counter()}

with open(PROJECT_ROOT / 'data' / 'transcriptions' / 'interlinear_full_words.txt', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f, delimiter='\t')
    for row in reader:
        if row.get('transcriber', '').strip() != 'H':
            continue
        lang = row.get('language', '').strip()
        if lang not in ['A', 'B']:
            continue
        word = row.get('word', '').strip()
        if not word or '*' in word:
            continue

        prefix, middle, suffix = extract_parts(word)
        if suffix:
            suffix_by_currier[lang][suffix] += 1

# Calculate A/B enrichment
print("="*70)
print("TEST 1: A/B ENRICHMENT (OLD FRAMEWORK BASIS)")
print("="*70)

a_total = sum(suffix_by_currier['A'].values())
b_total = sum(suffix_by_currier['B'].values())

print(f"\nCurrier A tokens with suffix: {a_total}")
print(f"Currier B tokens with suffix: {b_total}")

print(f"\n{'Suffix':<8} {'A count':>10} {'B count':>10} {'A %':>8} {'B %':>8} {'B/A ratio':>10}")
print("-"*60)

ab_ratios = {}
for suffix in ['y', 'dy', 'edy', 'ey', 'ol', 'or', 'ar', 'al', 'am']:
    a_count = suffix_by_currier['A'][suffix]
    b_count = suffix_by_currier['B'][suffix]
    a_pct = 100 * a_count / a_total if a_total else 0
    b_pct = 100 * b_count / b_total if b_total else 0

    # B/A enrichment ratio (normalized)
    a_rate = a_count / a_total if a_total else 0
    b_rate = b_count / b_total if b_total else 0
    ratio = b_rate / a_rate if a_rate > 0 else float('inf')
    ab_ratios[suffix] = ratio

    print(f"  -{suffix:<6} {a_count:>10} {b_count:>10} {a_pct:>7.1f}% {b_pct:>7.1f}% {ratio:>10.2f}x")

# Now compare with our animal/herb finding
print("\n" + "="*70)
print("TEST 2: COMPARE A/B ENRICHMENT WITH ANIMAL/HERB PATTERN")
print("="*70)

# From our previous analysis:
# Animal PP prefers: -ey (47%), -ol (31%)
# Herb PP prefers: -y (31%), -dy (10%)

print("""
Our NEW finding (animal vs herb PP):
  ANIMAL-preferred: -ey (47% vs 13%), -ol (31% vs 17%)
  HERB-preferred:   -y (0% vs 31%), -dy (0% vs 10%)

OLD framework prediction (from ccm_suffix_mapping.md):
  B-enriched (high ratio): -edy (191x), -dy (4.6x), -ar (3.2x)
  A-enriched (low ratio):  -or, -chy, -chor
  Balanced:                -ol (~1x), -aiin (~1x)
""")

print("ACTUAL A/B ratios from current data:")
for suffix in ['y', 'dy', 'edy', 'ey', 'ol', 'or', 'ar']:
    ratio = ab_ratios.get(suffix, 0)
    print(f"  -{suffix}: {ratio:.2f}x B/A")

print("\n" + "="*70)
print("TEST 3: DOES FIRE-DEGREE PREDICT A/B ENRICHMENT?")
print("="*70)

print("""
Hypothesis: If suffix encodes fire degree, and B execution involves
more high-fire processes, then:
  - HIGH-fire suffixes (-ey, -ol) should be B-enriched
  - LOW-fire suffixes (-y, -dy) should be A-enriched (or balanced)

Let's check:
""")

high_fire = ['ey', 'ol']
low_fire = ['y', 'dy']

high_fire_a = sum(suffix_by_currier['A'][s] for s in high_fire)
high_fire_b = sum(suffix_by_currier['B'][s] for s in high_fire)
low_fire_a = sum(suffix_by_currier['A'][s] for s in low_fire)
low_fire_b = sum(suffix_by_currier['B'][s] for s in low_fire)

print(f"HIGH-fire (-ey, -ol): A={high_fire_a}, B={high_fire_b}")
high_a_rate = high_fire_a / a_total
high_b_rate = high_fire_b / b_total
print(f"  A rate: {100*high_a_rate:.1f}%, B rate: {100*high_b_rate:.1f}%")
print(f"  B/A ratio: {high_b_rate/high_a_rate:.2f}x")

print(f"\nLOW-fire (-y, -dy): A={low_fire_a}, B={low_fire_b}")
low_a_rate = low_fire_a / a_total
low_b_rate = low_fire_b / b_total
print(f"  A rate: {100*low_a_rate:.1f}%, B rate: {100*low_b_rate:.1f}%")
print(f"  B/A ratio: {low_b_rate/low_a_rate:.2f}x")

print("\n" + "="*70)
print("VERDICT")
print("="*70)

if high_b_rate/high_a_rate > 1.2 and low_b_rate/low_a_rate < 0.8:
    print("""
ALIGNED: Fire-degree interpretation EXPLAINS A/B enrichment!
  - High-fire suffixes are B-enriched (execution involves intense processing)
  - Low-fire suffixes are A-enriched (registry describes gentler materials)

The frameworks are COMPATIBLE - fire degree is the underlying dimension
that manifests as both:
  - Animal/herb material class difference
  - A/B Currier section difference
""")
elif high_b_rate/high_a_rate < 0.8 and low_b_rate/low_a_rate > 1.2:
    print("""
CONFLICT: Fire-degree interpretation CONTRADICTS A/B enrichment!
  - High-fire suffixes are A-enriched (opposite of prediction)
  - Low-fire suffixes are B-enriched (opposite of prediction)

Need to reconsider one of the frameworks.
""")
else:
    print("""
PARTIAL/UNCLEAR: Results don't strongly support either alignment or conflict.
  - May need more nuanced interpretation
  - Or the two frameworks capture different aspects
""")
