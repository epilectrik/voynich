#!/usr/bin/env python3
"""
Non-Closer RI Investigation

Expert-recommended tests for RI tokens that are NOT line-final closers.
The "positional grammar" interpretation only applies to closers (84 MIDDLEs).
The other 265 RI MIDDLEs (openers, middle-position) remain open questions.

Tests:
- Test A: MIDDLE Incompatibility Participation
- Test B: AZC Participation
- Test C: Opener-Closer Pairing
- Test D: Middle-Position Distribution
"""

import json
from collections import defaultdict, Counter
from pathlib import Path

# Load pre-classified token data
with open('phases/A_INTERNAL_STRATIFICATION/results/token_data.json', 'r') as f:
    tokens = json.load(f)

with open('phases/A_INTERNAL_STRATIFICATION/results/middle_classes.json', 'r') as f:
    middle_classes = json.load(f)

# Get exclusive (RI) MIDDLEs
ri_middles = set(middle_classes['a_exclusive_middles'])

# Group tokens by line
lines = defaultdict(list)
for t in tokens:
    line_key = f"{t['folio']}.{t['line']}"
    lines[line_key].append(t)

print("=" * 70)
print("NON-CLOSER RI INVESTIGATION")
print("=" * 70)
print()

# First, classify RI tokens by position
ri_openers = set()      # RI MIDDLEs that appear at position 0
ri_closers = set()      # RI MIDDLEs that appear at last position
ri_middle_pos = set()   # RI MIDDLEs that appear in middle positions

ri_opener_tokens = []   # Token instances at position 0
ri_closer_tokens = []   # Token instances at last position
ri_middle_tokens = []   # Token instances at middle positions

for line_key, line_tokens in lines.items():
    if len(line_tokens) == 0:
        continue

    for i, t in enumerate(line_tokens):
        if t['middle_class'] != 'exclusive':
            continue

        middle = t['middle']

        if i == 0:
            ri_openers.add(middle)
            ri_opener_tokens.append(t)
        elif i == len(line_tokens) - 1:
            ri_closers.add(middle)
            ri_closer_tokens.append(t)
        else:
            ri_middle_pos.add(middle)
            ri_middle_tokens.append(t)

# Non-closer RI = openers + middle-position
noncloser_ri_middles = (ri_openers | ri_middle_pos) - ri_closers
pure_openers = ri_openers - ri_closers - ri_middle_pos  # Only ever at position 0
pure_middle = ri_middle_pos - ri_openers - ri_closers   # Only ever in middle

print("RI POSITIONAL CLASSIFICATION")
print("-" * 40)
print(f"Total RI MIDDLEs: {len(ri_middles)}")
print(f"RI at opener position (pos 0): {len(ri_openers)}")
print(f"RI at closer position (last): {len(ri_closers)}")
print(f"RI at middle positions: {len(ri_middle_pos)}")
print()
print(f"Non-closer RI (openers + middle): {len(noncloser_ri_middles)}")
print(f"Pure openers (only at pos 0): {len(pure_openers)}")
print(f"Pure middle (only middle positions): {len(pure_middle)}")
print()

# Token counts
print("TOKEN INSTANCE COUNTS")
print("-" * 40)
print(f"RI tokens at opener position: {len(ri_opener_tokens)}")
print(f"RI tokens at closer position: {len(ri_closer_tokens)}")
print(f"RI tokens at middle position: {len(ri_middle_tokens)}")
print()

# ============================================================
# TEST A: MIDDLE Incompatibility Participation
# ============================================================
print("=" * 70)
print("TEST A: MIDDLE INCOMPATIBILITY PARTICIPATION")
print("=" * 70)
print()
print("Question: Do non-closer RI MIDDLEs participate in the 95.7% incompatibility rate?")
print()

# Load incompatibility data
with open('results/middle_incompatibility.json', 'r') as f:
    incompatibility_data = json.load(f)

# The incompatibility analysis was on AZC folios only
# We need to check if non-closer RI MIDDLEs appear in AZC
# and if they show the same incompatibility patterns

# Get illegal pairs from the data
illegal_pairs = set()
for pair_data in incompatibility_data.get('illegal_pairs', []):
    pair = tuple(pair_data[0])
    illegal_pairs.add(pair)

# Get all MIDDLEs from incompatibility analysis
incomp_middles = set(incompatibility_data['graph_analysis']['components'][0])  # Main component

# Check overlap with non-closer RI
noncloser_in_incomp = noncloser_ri_middles & incomp_middles
closer_in_incomp = ri_closers & incomp_middles

print(f"Non-closer RI MIDDLEs in incompatibility graph: {len(noncloser_in_incomp)}")
print(f"Closer RI MIDDLEs in incompatibility graph: {len(closer_in_incomp)}")

# For non-closer RI, count illegal pairs
def count_illegal_pairs_for_middle(middle, illegal_pairs):
    """Count how many illegal pairs a MIDDLE participates in."""
    count = 0
    for (m1, m2) in illegal_pairs:
        if middle == m1 or middle == m2:
            count += 1
    return count

# Sample analysis for non-closers vs closers
noncloser_pair_counts = []
closer_pair_counts = []

for m in list(noncloser_in_incomp)[:50]:  # Sample
    noncloser_pair_counts.append(count_illegal_pairs_for_middle(m, illegal_pairs))

for m in list(closer_in_incomp)[:50]:  # Sample
    closer_pair_counts.append(count_illegal_pairs_for_middle(m, illegal_pairs))

if noncloser_pair_counts:
    print(f"Non-closer RI mean illegal pairs: {sum(noncloser_pair_counts)/len(noncloser_pair_counts):.1f}")
if closer_pair_counts:
    print(f"Closer RI mean illegal pairs: {sum(closer_pair_counts)/len(closer_pair_counts):.1f}")
print()

# ============================================================
# TEST B: AZC Participation
# ============================================================
print("=" * 70)
print("TEST B: AZC PARTICIPATION")
print("=" * 70)
print()
print("Question: Do non-closer RI MIDDLEs appear in AZC positions?")
print()

# Load AZC terminal analysis
with open('phases/A_INTERNAL_STRATIFICATION/results/azc_terminal_analysis.json', 'r') as f:
    azc_data = json.load(f)

azc_ri_middles = set(azc_data['azc_terminal_middles'])

# Check non-closer RI in AZC
noncloser_in_azc = noncloser_ri_middles & azc_ri_middles
closer_in_azc = ri_closers & azc_ri_middles

print(f"Non-closer RI MIDDLEs in AZC: {len(noncloser_in_azc)}")
print(f"Closer RI MIDDLEs in AZC: {len(closer_in_azc)}")
print()

if noncloser_in_azc:
    print("Non-closer RI MIDDLEs that appear in AZC:")
    for m in sorted(noncloser_in_azc):
        print(f"  {m}")
    print()

    # What placements do they use?
    noncloser_placements = Counter()
    closer_placements = Counter()
    for tok in azc_data['tokens']:
        if tok['middle'] in noncloser_in_azc:
            noncloser_placements[tok['placement']] += 1
        elif tok['middle'] in closer_in_azc:
            closer_placements[tok['placement']] += 1

    print("Non-closer RI placement distribution in AZC:")
    for pl, count in noncloser_placements.most_common():
        print(f"  {pl}: {count}")
    print()
    print("Closer RI placement distribution in AZC:")
    for pl, count in closer_placements.most_common():
        print(f"  {pl}: {count}")
    print()

# ============================================================
# TEST C: Opener-Closer Pairing
# ============================================================
print("=" * 70)
print("TEST C: OPENER-CLOSER PAIRING")
print("=" * 70)
print()
print("Question: When a line has BOTH opener and closer RI, are they correlated?")
print()

# Find lines with both opener and closer RI
lines_with_both = []
for line_key, line_tokens in lines.items():
    if len(line_tokens) < 2:
        continue

    first_ri = line_tokens[0]['middle_class'] == 'exclusive'
    last_ri = line_tokens[-1]['middle_class'] == 'exclusive'

    if first_ri and last_ri:
        lines_with_both.append({
            'line': line_key,
            'opener': line_tokens[0]['middle'],
            'closer': line_tokens[-1]['middle'],
            'length': len(line_tokens),
            'opener_token': line_tokens[0]['token'],
            'closer_token': line_tokens[-1]['token']
        })

print(f"Lines with BOTH opener RI and closer RI: {len(lines_with_both)}")
print()

if lines_with_both:
    # Check for pairing patterns
    pair_counter = Counter()
    for l in lines_with_both:
        pair_counter[(l['opener'], l['closer'])] += 1

    print(f"Distinct opener-closer pairs: {len(pair_counter)}")
    print()
    print("Top opener-closer pairs:")
    for (opener, closer), count in pair_counter.most_common(10):
        print(f"  {opener} ... {closer}: {count}")
    print()

    # Check if same MIDDLE appears as both opener and closer
    same_middles = sum(1 for l in lines_with_both if l['opener'] == l['closer'])
    print(f"Lines where opener MIDDLE == closer MIDDLE: {same_middles}")
    print()

    # Examples
    print("Examples of opener-closer RI lines:")
    for l in lines_with_both[:5]:
        print(f"  {l['line']}: [{l['opener_token']}] ... [{l['closer_token']}]")
    print()

# ============================================================
# TEST D: Middle-Position Distribution
# ============================================================
print("=" * 70)
print("TEST D: MIDDLE-POSITION BEHAVIOR")
print("=" * 70)
print()
print("Question: Are middle-position RI tokens like DA articulation or content?")
print()

# Analyze middle-position RI
middle_ri_middles = Counter()
middle_ri_prefixes = Counter()
middle_ri_suffixes = Counter()

for t in ri_middle_tokens:
    middle_ri_middles[t['middle']] += 1
    middle_ri_prefixes[t['prefix']] += 1
    middle_ri_suffixes[t['suffix']] += 1

print(f"Middle-position RI token instances: {len(ri_middle_tokens)}")
print(f"Distinct MIDDLEs in middle position: {len(middle_ri_middles)}")
print()

print("Top MIDDLEs in middle position:")
for middle, count in middle_ri_middles.most_common(10):
    print(f"  {middle}: {count}")
print()

print("PREFIX distribution (middle-position RI):")
for prefix, count in middle_ri_prefixes.most_common(10):
    print(f"  {prefix}: {count}")
print()

# Compare to DA articulation pattern
# DA articulation uses specific prefixes heavily
# Check if middle-position RI has similar PREFIX concentration

total_middle_ri = len(ri_middle_tokens)
top_prefix_share = middle_ri_prefixes.most_common(1)[0][1] / total_middle_ri if total_middle_ri > 0 else 0
top3_prefix_share = sum(c for _, c in middle_ri_prefixes.most_common(3)) / total_middle_ri if total_middle_ri > 0 else 0

print(f"Top 1 PREFIX share: {100*top_prefix_share:.1f}%")
print(f"Top 3 PREFIX share: {100*top3_prefix_share:.1f}%")
print()

# Check position distribution within lines
position_dist = Counter()
for t in ri_middle_tokens:
    line_key = f"{t['folio']}.{t['line']}"
    line_tokens = lines[line_key]
    pos = next(i for i, tok in enumerate(line_tokens) if tok['token'] == t['token'])
    line_len = len(line_tokens)

    # Normalize position
    if line_len > 2:
        # Position 1 = right after opener, position -2 = right before closer
        if pos == 1:
            position_dist['pos_1'] += 1
        elif pos == line_len - 2:
            position_dist['pos_-2'] += 1
        else:
            position_dist['inner'] += 1

print("Position within middle zone:")
for pos, count in position_dist.most_common():
    print(f"  {pos}: {count}")
print()

# Check folio spread for middle-position RI
folio_counts = Counter(t['folio'] for t in ri_middle_tokens)
print(f"Folios with middle-position RI: {len(folio_counts)}")
print(f"Top folios:")
for folio, count in folio_counts.most_common(5):
    print(f"  {folio}: {count}")
print()

# ============================================================
# SYNTHESIS
# ============================================================
print("=" * 70)
print("SYNTHESIS: NON-CLOSER RI CHARACTERIZATION")
print("=" * 70)
print()

# Classification of non-closer RI
print("CLASSIFICATION OF NON-CLOSER RI:")
print("-" * 40)
print()

# 1. Opener RI
print("1. OPENER RI (position 0):")
print(f"   Distinct MIDDLEs: {len(ri_openers)}")
print(f"   Token instances: {len(ri_opener_tokens)}")
opener_folio_count = len(set(t['folio'] for t in ri_opener_tokens))
print(f"   Folio spread: {opener_folio_count}")
print()

# 2. Middle-position RI
print("2. MIDDLE-POSITION RI:")
print(f"   Distinct MIDDLEs: {len(ri_middle_pos)}")
print(f"   Token instances: {len(ri_middle_tokens)}")
middle_folio_count = len(set(t['folio'] for t in ri_middle_tokens))
print(f"   Folio spread: {middle_folio_count}")
print()

# 3. Closer RI (for comparison)
print("3. CLOSER RI (for comparison):")
print(f"   Distinct MIDDLEs: {len(ri_closers)}")
print(f"   Token instances: {len(ri_closer_tokens)}")
closer_folio_count = len(set(t['folio'] for t in ri_closer_tokens))
print(f"   Folio spread: {closer_folio_count}")
print()

# Interpretation hints
print("INTERPRETATION HINTS:")
print("-" * 40)

# Check if non-closer RI is folio-localized
if opener_folio_count < 10 and len(ri_opener_tokens) > 20:
    print("- Opener RI is folio-localized (batch-specific?)")
elif opener_folio_count > 30:
    print("- Opener RI is widespread (general function?)")

if len(noncloser_in_azc) > 0:
    print(f"- {len(noncloser_in_azc)} non-closer RI MIDDLEs appear in AZC -> context-sensitive")
else:
    print("- Non-closer RI doesn't appear in AZC -> A-internal only")

if len(lines_with_both) > 0:
    print(f"- {len(lines_with_both)} lines have opener-closer RI brackets")

print()

# Save results
results = {
    'ri_positional_classification': {
        'total_ri_middles': len(ri_middles),
        'opener_middles': len(ri_openers),
        'closer_middles': len(ri_closers),
        'middle_position_middles': len(ri_middle_pos),
        'noncloser_middles': len(noncloser_ri_middles),
        'pure_openers': len(pure_openers),
        'pure_middle': len(pure_middle)
    },
    'token_counts': {
        'opener_tokens': len(ri_opener_tokens),
        'closer_tokens': len(ri_closer_tokens),
        'middle_tokens': len(ri_middle_tokens)
    },
    'test_a_incompatibility': {
        'noncloser_in_graph': len(noncloser_in_incomp),
        'closer_in_graph': len(closer_in_incomp),
        'noncloser_mean_illegal_pairs': sum(noncloser_pair_counts)/len(noncloser_pair_counts) if noncloser_pair_counts else 0,
        'closer_mean_illegal_pairs': sum(closer_pair_counts)/len(closer_pair_counts) if closer_pair_counts else 0
    },
    'test_b_azc': {
        'noncloser_in_azc': len(noncloser_in_azc),
        'closer_in_azc': len(closer_in_azc),
        'noncloser_azc_middles': sorted(noncloser_in_azc),
        'closer_azc_middles': sorted(closer_in_azc)
    },
    'test_c_pairing': {
        'lines_with_both': len(lines_with_both),
        'distinct_pairs': len(pair_counter) if lines_with_both else 0,
        'same_middle_count': same_middles if lines_with_both else 0,
        'top_pairs': [(list(p), c) for p, c in pair_counter.most_common(10)] if lines_with_both else []
    },
    'test_d_middle_position': {
        'token_count': len(ri_middle_tokens),
        'distinct_middles': len(middle_ri_middles),
        'top_middles': list(middle_ri_middles.most_common(10)),
        'top_prefixes': list(middle_ri_prefixes.most_common(5)),
        'top_prefix_share': top_prefix_share,
        'top3_prefix_share': top3_prefix_share,
        'position_distribution': dict(position_dist),
        'folio_count': len(folio_counts)
    },
    'lists': {
        'ri_openers': sorted(ri_openers),
        'ri_closers': sorted(ri_closers),
        'ri_middle_pos': sorted(ri_middle_pos),
        'noncloser_ri': sorted(noncloser_ri_middles),
        'pure_openers': sorted(pure_openers),
        'pure_middle': sorted(pure_middle)
    }
}

output_path = Path('phases/A_RECORD_STRUCTURE_ANALYSIS/results/noncloser_ri_investigation.json')
output_path.parent.mkdir(parents=True, exist_ok=True)
with open(output_path, 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to: {output_path}")
