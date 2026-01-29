"""
T18: RI Link Network Analysis

4 RI tokens link records by appearing as FINAL in one paragraph
and INITIAL in another. Analyze the network structure:

1. What folios are connected?
2. Is there a geographic pattern (nearby folios, same quire)?
3. Is there directionality (early folio -> late folio)?
4. What does the link graph look like?
"""

import sys
import json
from pathlib import Path
from collections import defaultdict, Counter
import numpy as np
import re

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))
from scripts.voynich import Transcript, Morphology

tx = Transcript()
morph = Morphology()

print("=" * 70)
print("T18: RI LINK NETWORK ANALYSIS")
print("=" * 70)

# Build B vocabulary for PP/RI classification
b_middles = set()
for token in tx.currier_b():
    w = token.word.strip()
    if not w or '*' in w:
        continue
    m = morph.extract(w)
    if m.middle:
        b_middles.add(m.middle)

GALLOWS = {'k', 't', 'p', 'f'}

def starts_with_gallows(word):
    if not word:
        return False
    w = word.strip()
    return bool(w) and w[0] in GALLOWS

def folio_sort_key(folio):
    """Extract numeric part for sorting."""
    match = re.match(r'f(\d+)', folio)
    if match:
        return int(match.group(1))
    return 999

# Collect A tokens by line
a_tokens_by_line = defaultdict(list)
for token in tx.currier_a():
    w = token.word.strip()
    if not w or '*' in w:
        continue
    m = morph.extract(w)
    is_ri = m.middle not in b_middles if m.middle else False
    a_tokens_by_line[(token.folio, token.line)].append({
        'word': w,
        'middle': m.middle,
        'is_ri': is_ri,
    })

# Build paragraphs with folio info
paragraphs = []
a_folios = defaultdict(list)
for (folio, line), tokens in sorted(a_tokens_by_line.items()):
    a_folios[folio].append((line, tokens))

for folio in sorted(a_folios.keys()):
    lines = a_folios[folio]
    current_para = {'folio': folio, 'tokens': [], 'para_idx': len(paragraphs)}

    for line, tokens in lines:
        if tokens and starts_with_gallows(tokens[0]['word']):
            if current_para['tokens']:
                paragraphs.append(current_para)
            current_para = {'folio': folio, 'tokens': [], 'para_idx': len(paragraphs)}
        current_para['tokens'].extend(tokens)

    if current_para['tokens']:
        paragraphs.append(current_para)

# Track RI with detailed position info
ri_locations = defaultdict(list)  # word -> list of {folio, para_idx, pos_class}

for p in paragraphs:
    tokens = p['tokens']
    n = len(tokens)
    if n < 3:
        continue

    for i, t in enumerate(tokens):
        if not t['is_ri']:
            continue

        rel_pos = i / (n - 1)

        if rel_pos < 0.2:
            pos_class = 'INITIAL'
        elif rel_pos > 0.8:
            pos_class = 'FINAL'
        else:
            pos_class = 'MIDDLE'

        ri_locations[t['word']].append({
            'folio': p['folio'],
            'para_idx': p['para_idx'],
            'pos_class': pos_class,
            'rel_pos': rel_pos,
        })

# Find linkers (appear in both INITIAL and FINAL)
linkers = {}
for word, locs in ri_locations.items():
    positions = set(loc['pos_class'] for loc in locs)
    if 'INITIAL' in positions and 'FINAL' in positions:
        linkers[word] = locs

print(f"\nFound {len(linkers)} linking RI tokens")

# Analyze each linker
print("\n" + "=" * 70)
print("LINK NETWORK STRUCTURE")
print("=" * 70)

all_links = []  # (source_folio, target_folio, word)
folio_roles = defaultdict(lambda: {'source': [], 'target': []})

for word, locs in linkers.items():
    initial_locs = [l for l in locs if l['pos_class'] == 'INITIAL']
    final_locs = [l for l in locs if l['pos_class'] == 'FINAL']

    print(f"\n{word}:")
    print(f"  Appears as INITIAL (input) in: {[l['folio'] for l in initial_locs]}")
    print(f"  Appears as FINAL (output) in: {[l['folio'] for l in final_locs]}")

    # Create directed links: FINAL -> INITIAL (output feeds input)
    for final_loc in final_locs:
        for initial_loc in initial_locs:
            source = final_loc['folio']
            target = initial_loc['folio']
            all_links.append((source, target, word))
            folio_roles[source]['source'].append(word)
            folio_roles[target]['target'].append(word)

    # Check folio order
    initial_nums = [folio_sort_key(l['folio']) for l in initial_locs]
    final_nums = [folio_sort_key(l['folio']) for l in final_locs]

    if initial_nums and final_nums:
        mean_initial = np.mean(initial_nums)
        mean_final = np.mean(final_nums)
        if mean_final < mean_initial:
            print(f"  Direction: FINAL folios (avg {mean_final:.0f}) -> INITIAL folios (avg {mean_initial:.0f})")
            print(f"  -> Earlier folios output to later folios (FORWARD)")
        else:
            print(f"  Direction: FINAL folios (avg {mean_final:.0f}) <- INITIAL folios (avg {mean_initial:.0f})")
            print(f"  -> Later folios output to earlier folios (BACKWARD)")

# Analyze link structure
print("\n" + "=" * 70)
print("LINK GRAPH ANALYSIS")
print("=" * 70)

print(f"\nTotal directed links: {len(all_links)}")

# Unique folio pairs
unique_pairs = set((s, t) for s, t, w in all_links)
print(f"Unique folio pairs: {len(unique_pairs)}")

# Source and target folios
source_folios = set(s for s, t, w in all_links)
target_folios = set(t for s, t, w in all_links)
all_linked_folios = source_folios | target_folios

print(f"\nFolios that OUTPUT (FINAL position): {sorted(source_folios, key=folio_sort_key)}")
print(f"Folios that INPUT (INITIAL position): {sorted(target_folios, key=folio_sort_key)}")
print(f"Total folios in network: {len(all_linked_folios)}")

# Check for bidirectional links
bidirectional = []
for s, t, w in all_links:
    if any(s2 == t and t2 == s for s2, t2, w2 in all_links):
        bidirectional.append((s, t, w))

if bidirectional:
    print(f"\nBidirectional links (A->B and B->A): {bidirectional}")
else:
    print(f"\nNo bidirectional links found (all links are one-way)")

# Folio distance analysis
print("\n" + "=" * 70)
print("FOLIO DISTANCE ANALYSIS")
print("=" * 70)

distances = []
for source, target, word in all_links:
    source_num = folio_sort_key(source)
    target_num = folio_sort_key(target)
    distance = target_num - source_num
    distances.append(distance)
    print(f"  {source} -> {target} ({word}): distance = {distance:+d}")

print(f"\nDistance statistics:")
print(f"  Mean: {np.mean(distances):+.1f}")
print(f"  Median: {np.median(distances):+.1f}")
print(f"  Range: {min(distances):+d} to {max(distances):+d}")

forward = sum(1 for d in distances if d > 0)
backward = sum(1 for d in distances if d < 0)
same = sum(1 for d in distances if d == 0)

print(f"\nDirection distribution:")
print(f"  Forward (to later folio): {forward} ({forward/len(distances)*100:.1f}%)")
print(f"  Backward (to earlier folio): {backward} ({backward/len(distances)*100:.1f}%)")
print(f"  Same folio: {same} ({same/len(distances)*100:.1f}%)")

# Hub analysis
print("\n" + "=" * 70)
print("HUB ANALYSIS")
print("=" * 70)

out_degree = Counter(s for s, t, w in all_links)
in_degree = Counter(t for s, t, w in all_links)

print(f"\nTop SOURCE folios (most outgoing links):")
for folio, count in out_degree.most_common(5):
    words = folio_roles[folio]['source']
    print(f"  {folio}: {count} outgoing via {set(words)}")

print(f"\nTop TARGET folios (most incoming links):")
for folio, count in in_degree.most_common(5):
    words = folio_roles[folio]['target']
    print(f"  {folio}: {count} incoming via {set(words)}")

# Summary
print("\n" + "=" * 70)
print("SUMMARY: RI LINK NETWORK")
print("=" * 70)

print(f"""
NETWORK STRUCTURE:
- {len(linkers)} linking tokens create {len(all_links)} directed links
- {len(all_linked_folios)} folios participate in the network
- {len(source_folios)} source folios, {len(target_folios)} target folios

DIRECTIONALITY:
- {forward}/{len(distances)} links go FORWARD (to later folios)
- {backward}/{len(distances)} links go BACKWARD (to earlier folios)
- Mean distance: {np.mean(distances):+.1f} folios

INTERPRETATION:
""")

if forward > backward:
    print("Links predominantly flow FORWARD through the manuscript.")
    print("Earlier folios' outputs become later folios' inputs.")
    print("-> Suggests a PROGRESSIVE workflow or dependencies.")
elif backward > forward:
    print("Links predominantly flow BACKWARD through the manuscript.")
    print("Later folios' outputs become earlier folios' inputs.")
    print("-> Suggests BACK-REFERENCES or iterative refinement.")
else:
    print("Links flow equally in both directions.")
    print("-> Suggests a NON-LINEAR or networked relationship.")

# Check if linkers share morphology
print("\n" + "=" * 70)
print("LINKER MORPHOLOGY")
print("=" * 70)

for word in linkers.keys():
    m = morph.extract(word)
    print(f"  {word}: prefix={m.prefix}, middle={m.middle}, suffix={m.suffix}")

# Save results
results = {
    'linker_count': len(linkers),
    'linker_words': list(linkers.keys()),
    'total_links': len(all_links),
    'unique_pairs': len(unique_pairs),
    'source_folios': sorted(source_folios, key=folio_sort_key),
    'target_folios': sorted(target_folios, key=folio_sort_key),
    'mean_distance': float(np.mean(distances)),
    'forward_links': forward,
    'backward_links': backward,
    'links': [(s, t, w) for s, t, w in all_links],
}

out_path = PROJECT_ROOT / 'phases' / 'A_RECORD_B_ROUTING_TOPOLOGY' / 'results' / 't18_ri_link_network.json'
with open(out_path, 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to {out_path.name}")
