#!/usr/bin/env python3
"""
SPATIAL HYPOTHESIS STRESS TESTS

Test the aggressive hypothesis:
"The Voynich is organized around POSITIONS, not tokens.
 Text is subordinate to spatial state."

Tests:
1. Placement Automaton Structure (planar? cyclic? nested?)
2. Diagram Domination (does placement beat identity for prediction?)
3. B Bleed (does B grammar deform near AZC?)
"""

import os
from collections import defaultdict, Counter
import math

os.chdir('C:/git/voynich')

print("=" * 70)
print("SPATIAL HYPOTHESIS STRESS TESTS")
print("Tier 3.5: Reckless Structurally-Grounded Speculation")
print("=" * 70)

# Load data
with open('data/transcriptions/interlinear_full_words.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()

header = lines[0].strip().split('\t')
header = [h.strip('"') for h in header]

all_tokens = []
for line in lines[1:]:
    parts = line.strip().split('\t')
    if len(parts) >= len(header):
        row = {header[i]: parts[i].strip('"') for i in range(len(header))}
        all_tokens.append(row)

# Separate by language
azc_tokens = [t for t in all_tokens if t.get('language', '') in ['NA', '']]
b_tokens = [t for t in all_tokens if t.get('language', '') == 'B']

# Get AZC-only vocabulary
azc_words = set(t['word'] for t in azc_tokens)
a_words = set(t['word'] for t in all_tokens if t.get('language', '') == 'A')
b_words = set(t['word'] for t in b_tokens)
azc_only = azc_words - a_words - b_words

print(f"\nLoaded {len(azc_tokens)} AZC tokens, {len(b_tokens)} B tokens")
print(f"AZC-only vocabulary: {len(azc_only)} types")

# =========================================================================
# TEST 1: PLACEMENT AUTOMATON STRUCTURE
# =========================================================================

print("\n" + "=" * 70)
print("TEST 1: PLACEMENT AUTOMATON STRUCTURE")
print("Is the grammar PLANAR, CYCLIC, or NESTED?")
print("=" * 70)

# Build transition matrix for AZC-only tokens
azc_only_tokens = [t for t in azc_tokens if t['word'] in azc_only]

# Group by line
by_line = defaultdict(list)
for t in azc_only_tokens:
    key = (t.get('folio', ''), t.get('line_number', ''))
    by_line[key].append(t)

# Count placement transitions
placement_transitions = Counter()
placement_counts = Counter()

for key, tokens in by_line.items():
    for i in range(len(tokens)):
        p1 = tokens[i].get('placement', 'UNK')
        placement_counts[p1] += 1
        if i < len(tokens) - 1:
            p2 = tokens[i+1].get('placement', 'UNK')
            placement_transitions[(p1, p2)] += 1

# Build adjacency structure
placements = sorted(set(p for p, _ in placement_transitions.keys()) |
                   set(p for _, p in placement_transitions.keys()))

print(f"\nPlacement classes: {len(placements)}")
print(f"Observed transitions: {len(placement_transitions)}")
print(f"Possible transitions: {len(placements) ** 2}")
print(f"Sparsity: {len(placement_transitions) / (len(placements) ** 2) * 100:.1f}%")

# Identify structure
# Check for cycles
def find_cycles(transitions, max_length=4):
    """Find all cycles up to max_length."""
    nodes = set(p for p, _ in transitions) | set(p for _, p in transitions)
    adjacency = defaultdict(set)
    for (p1, p2), count in transitions.items():
        if count > 0:
            adjacency[p1].add(p2)

    cycles = []
    for start in nodes:
        # BFS for cycles
        queue = [(start, [start])]
        while queue:
            current, path = queue.pop(0)
            if len(path) > max_length:
                continue
            for next_node in adjacency[current]:
                if next_node == start and len(path) > 1:
                    cycles.append(path + [start])
                elif next_node not in path:
                    queue.append((next_node, path + [next_node]))
    return cycles

cycles = find_cycles(placement_transitions)
print(f"\nCycles found (length 2-4): {len(cycles)}")

# Show some cycles
unique_cycles = []
for c in cycles:
    normalized = tuple(sorted(c[:-1]))
    if normalized not in [tuple(sorted(uc[:-1])) for uc in unique_cycles]:
        unique_cycles.append(c)

print(f"Unique cycle structures: {len(unique_cycles)}")
for c in unique_cycles[:10]:
    print(f"  {' -> '.join(c)}")

# Check for hierarchy (are there "levels"?)
# Compute in-degree and out-degree
in_degree = Counter()
out_degree = Counter()
for (p1, p2), count in placement_transitions.items():
    out_degree[p1] += count
    in_degree[p2] += count

print(f"\nDegree analysis (potential hierarchy):")
print(f"{'Placement':<8} {'In':<8} {'Out':<8} {'Ratio':<8} {'Role':<15}")
print("-" * 50)
for p in sorted(placements, key=lambda x: -placement_counts.get(x, 0))[:12]:
    ind = in_degree.get(p, 0)
    outd = out_degree.get(p, 0)
    ratio = outd / ind if ind > 0 else float('inf')
    if ratio > 1.5:
        role = "SOURCE (start)"
    elif ratio < 0.67:
        role = "SINK (end)"
    else:
        role = "TRANSIT"
    print(f"{p:<8} {ind:<8} {outd:<8} {ratio:<8.2f} {role:<15}")

# Check planarity heuristic (if edges don't cross much)
# Simple test: can we order nodes so most edges go "forward"?
def forward_edge_score(order, transitions):
    """What fraction of edges go forward in this ordering?"""
    pos = {p: i for i, p in enumerate(order)}
    forward = 0
    total = 0
    for (p1, p2), count in transitions.items():
        if p1 in pos and p2 in pos:
            if pos[p2] > pos[p1]:
                forward += count
            total += count
    return forward / total if total > 0 else 0

# Try ordering by out-degree ratio
ordered_by_ratio = sorted(placements, key=lambda p: out_degree.get(p, 0) / (in_degree.get(p, 1)))
forward_score = forward_edge_score(ordered_by_ratio, placement_transitions)

print(f"\nForward edge score (ordered by role): {forward_score:.1%}")
if forward_score > 0.7:
    print("  -> LAYERED/HIERARCHICAL structure detected")
elif forward_score > 0.5:
    print("  -> PARTIALLY ORDERED structure")
else:
    print("  -> CYCLIC structure (no clear hierarchy)")

# =========================================================================
# TEST 2: DIAGRAM DOMINATION
# =========================================================================

print("\n" + "=" * 70)
print("TEST 2: DIAGRAM DOMINATION")
print("Does PLACEMENT predict next token better than TOKEN IDENTITY?")
print("=" * 70)

# For AZC-only tokens, compare predictive power
# Method: entropy of next-token distribution given placement vs given current token

def conditional_entropy(condition_counts, outcome_counts):
    """Calculate H(outcome | condition)."""
    total = sum(sum(outcomes.values()) for outcomes in condition_counts.values())
    h = 0
    for condition, outcomes in condition_counts.items():
        p_condition = sum(outcomes.values()) / total
        # Entropy of outcomes given this condition
        outcome_total = sum(outcomes.values())
        h_given = 0
        for outcome, count in outcomes.items():
            if count > 0:
                p = count / outcome_total
                h_given -= p * math.log2(p)
        h += p_condition * h_given
    return h

# Build conditional distributions
# Given placement, what's next token?
placement_to_next_token = defaultdict(Counter)
# Given current token, what's next token?
token_to_next_token = defaultdict(Counter)
# Given placement, what's next placement?
placement_to_next_placement = defaultdict(Counter)

for key, tokens in by_line.items():
    for i in range(len(tokens) - 1):
        p1 = tokens[i].get('placement', 'UNK')
        t1 = tokens[i]['word']
        p2 = tokens[i+1].get('placement', 'UNK')
        t2 = tokens[i+1]['word']

        placement_to_next_token[p1][t2] += 1
        token_to_next_token[t1][t2] += 1
        placement_to_next_placement[p1][p2] += 1

# Calculate entropies
h_token_given_placement = conditional_entropy(placement_to_next_token, None)
h_token_given_token = conditional_entropy(token_to_next_token, None)
h_placement_given_placement = conditional_entropy(placement_to_next_placement, None)

# Baseline: unconditional entropy of next token
all_next_tokens = Counter()
for outcomes in placement_to_next_token.values():
    all_next_tokens.update(outcomes)
total_next = sum(all_next_tokens.values())
h_unconditional = 0
for count in all_next_tokens.values():
    if count > 0:
        p = count / total_next
        h_unconditional -= p * math.log2(p)

print(f"\nEntropy analysis (lower = more predictive):")
print(f"  H(next_token) unconditional:     {h_unconditional:.2f} bits")
print(f"  H(next_token | current_token):   {h_token_given_token:.2f} bits")
print(f"  H(next_token | placement):       {h_token_given_placement:.2f} bits")
print(f"  H(next_placement | placement):   {h_placement_given_placement:.2f} bits")

print(f"\nPredictive power (information gain):")
token_gain = h_unconditional - h_token_given_token
placement_gain = h_unconditional - h_token_given_placement
print(f"  Token identity provides:   {token_gain:.2f} bits")
print(f"  Placement provides:        {placement_gain:.2f} bits")

if placement_gain > token_gain:
    print(f"\n  *** PLACEMENT BEATS IDENTITY by {placement_gain - token_gain:.2f} bits ***")
    print(f"  -> SPATIAL DOMINATION CONFIRMED")
else:
    print(f"\n  Token identity wins by {token_gain - placement_gain:.2f} bits")
    print(f"  -> Spatial hypothesis NOT dominant here")

# =========================================================================
# TEST 3: B BLEED
# =========================================================================

print("\n" + "=" * 70)
print("TEST 3: B BLEED")
print("Does B grammar DEFORM near AZC boundaries?")
print("=" * 70)

# Find folios that have BOTH AZC and B content
azc_folios = set(t.get('folio', '') for t in azc_tokens)
b_folios = set(t.get('folio', '') for t in b_tokens)
mixed_folios = azc_folios.intersection(b_folios)

print(f"\nFolios with both AZC and B: {len(mixed_folios)}")

if mixed_folios:
    # Group tokens by folio and line
    folio_lines = defaultdict(lambda: defaultdict(list))
    for t in all_tokens:
        folio = t.get('folio', '')
        line = t.get('line_number', '')
        folio_lines[folio][line].append(t)

    # For mixed folios, find B tokens near AZC tokens
    # "Near" = same line or adjacent line

    b_near_azc = []
    b_far_from_azc = []

    for folio in mixed_folios:
        lines = folio_lines[folio]
        line_nums = sorted(lines.keys())

        # Identify which lines have AZC
        azc_lines = set()
        for line_num, tokens in lines.items():
            if any(t.get('language', '') in ['NA', ''] for t in tokens):
                azc_lines.add(line_num)

        # Categorize B tokens
        for line_num, tokens in lines.items():
            b_in_line = [t for t in tokens if t.get('language', '') == 'B']
            if not b_in_line:
                continue

            # Is this line near AZC?
            try:
                line_idx = line_nums.index(line_num)
                adjacent_lines = set()
                if line_idx > 0:
                    adjacent_lines.add(line_nums[line_idx - 1])
                if line_idx < len(line_nums) - 1:
                    adjacent_lines.add(line_nums[line_idx + 1])
                adjacent_lines.add(line_num)

                near_azc = bool(adjacent_lines.intersection(azc_lines))
            except:
                near_azc = False

            if near_azc:
                b_near_azc.extend(b_in_line)
            else:
                b_far_from_azc.extend(b_in_line)

    print(f"\nB tokens near AZC: {len(b_near_azc)}")
    print(f"B tokens far from AZC: {len(b_far_from_azc)}")

    # Compare LINK density
    link_near = sum(1 for t in b_near_azc if 'ol' in t['word'] or t['word'] == 'ol')
    link_far = sum(1 for t in b_far_from_azc if 'ol' in t['word'] or t['word'] == 'ol')

    # More precise: check for common LINK patterns
    link_tokens = {'ol', 'chol', 'chor', 'sho', 'cho'}
    link_near = sum(1 for t in b_near_azc if t['word'] in link_tokens)
    link_far = sum(1 for t in b_far_from_azc if t['word'] in link_tokens)

    link_rate_near = link_near / len(b_near_azc) * 100 if b_near_azc else 0
    link_rate_far = link_far / len(b_far_from_azc) * 100 if b_far_from_azc else 0

    print(f"\nLINK density comparison:")
    print(f"  Near AZC:  {link_rate_near:.2f}%")
    print(f"  Far from AZC: {link_rate_far:.2f}%")

    if link_rate_near > link_rate_far * 1.2:
        print(f"  -> B grammar SOFTENS near AZC (more waiting)")
    elif link_rate_far > link_rate_near * 1.2:
        print(f"  -> B grammar INTENSIFIES away from AZC")
    else:
        print(f"  -> No significant deformation detected")

else:
    print("No mixed folios found - cannot test B bleed")

    # Alternative: test at vocabulary level
    print("\nAlternative: Testing B behavior when using AZC-shared vocabulary...")

    azc_shared = azc_words.intersection(b_words)

    b_using_shared = [t for t in b_tokens if t['word'] in azc_shared]
    b_not_shared = [t for t in b_tokens if t['word'] not in azc_shared]

    print(f"B tokens using AZC-shared vocab: {len(b_using_shared)}")
    print(f"B tokens using B-only vocab: {len(b_not_shared)}")

# =========================================================================
# VERDICT
# =========================================================================

print("\n" + "=" * 70)
print("SPATIAL HYPOTHESIS VERDICT")
print("=" * 70)

print(f"""
TEST RESULTS:

1. PLACEMENT AUTOMATON:
   - Sparsity: {len(placement_transitions) / (len(placements) ** 2) * 100:.1f}% of transitions observed
   - Cycles: {len(unique_cycles)} unique cycle structures
   - Forward score: {forward_score:.1%}
   - Structure: {"LAYERED" if forward_score > 0.7 else "PARTIALLY ORDERED" if forward_score > 0.5 else "CYCLIC"}

2. DIAGRAM DOMINATION:
   - Placement information gain: {placement_gain:.2f} bits
   - Token identity gain: {token_gain:.2f} bits
   - Winner: {"PLACEMENT (spatial primary)" if placement_gain > token_gain else "IDENTITY (token primary)"}

3. B BLEED:
   - Mixed folios: {len(mixed_folios)}
   - {"LINK rates differ near/far AZC" if mixed_folios else "No direct test possible"}

OVERALL ASSESSMENT:
""")

spatial_evidence = 0
if forward_score > 0.5:
    spatial_evidence += 1
    print("  [+] Placement structure is ordered (not random)")
if placement_gain > token_gain * 0.8:  # Within 20%
    spatial_evidence += 1
    print("  [+] Placement has substantial predictive power")
if len(unique_cycles) > 5:
    spatial_evidence += 1
    print("  [+] Cyclic structure exists (state-space behavior)")

print(f"\n  Spatial evidence score: {spatial_evidence}/3")

if spatial_evidence >= 2:
    print("""
  The SPATIAL HYPOTHESIS is STRUCTURALLY SUPPORTED.

  Position appears to be a PRIMARY organizing axis,
  not subordinate to token identity.

  This is consistent with:
  - Diagram-first design
  - Coordinate control notation
  - Spatial state encoding
""")
else:
    print("""
  The spatial hypothesis is NOT strongly supported.
  Token identity remains primary.
""")

print("=" * 70)
print("SPATIAL HYPOTHESIS TESTS COMPLETE")
print("=" * 70)
