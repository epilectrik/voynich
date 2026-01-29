"""
T17: RI Repeater Position Analysis

95% of RI are singletons. What about the 5% that repeat?
- Do they appear only in INITIAL position?
- Do they appear only in FINAL position?
- Do they appear in BOTH (linking records together)?
"""

import sys
import json
from pathlib import Path
from collections import defaultdict, Counter
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))
from scripts.voynich import Transcript, Morphology

tx = Transcript()
morph = Morphology()

print("=" * 70)
print("T17: RI REPEATER POSITION ANALYSIS")
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
        'prefix': m.prefix,
        'suffix': m.suffix,
        'is_ri': is_ri,
    })

# Build paragraphs
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

# Track RI occurrences with position info
ri_occurrences = defaultdict(list)  # word -> list of {para_idx, position_class}

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

        ri_occurrences[t['word']].append({
            'para_idx': p['para_idx'],
            'folio': p['folio'],
            'rel_pos': rel_pos,
            'pos_class': pos_class,
        })

# Classify RI tokens by repetition
singletons = {w: occs for w, occs in ri_occurrences.items() if len(occs) == 1}
repeaters = {w: occs for w, occs in ri_occurrences.items() if len(occs) > 1}

print(f"\nRI tokens: {len(ri_occurrences)}")
print(f"  Singletons (1 occurrence): {len(singletons)} ({len(singletons)/len(ri_occurrences)*100:.1f}%)")
print(f"  Repeaters (2+ occurrences): {len(repeaters)} ({len(repeaters)/len(ri_occurrences)*100:.1f}%)")

# Analyze repeaters
print("\n" + "=" * 70)
print("REPEATER POSITION PATTERNS")
print("=" * 70)

# For each repeater, what positions does it appear in?
position_patterns = Counter()
linking_candidates = []  # appear in both INITIAL and FINAL

for word, occs in repeaters.items():
    positions = set(o['pos_class'] for o in occs)
    pattern = '+'.join(sorted(positions))
    position_patterns[pattern] += 1

    if 'INITIAL' in positions and 'FINAL' in positions:
        linking_candidates.append((word, occs))

print(f"\nRepeater position patterns:")
print(f"  {'Pattern':<30} {'Count':>8}")
print(f"  {'-'*30} {'-'*8}")
for pattern, count in position_patterns.most_common():
    print(f"  {pattern:<30} {count:>8}")

# Analyze linking candidates
print("\n" + "=" * 70)
print("LINKING CANDIDATES (appear in BOTH INITIAL and FINAL)")
print("=" * 70)

if linking_candidates:
    print(f"\n{len(linking_candidates)} RI tokens appear in BOTH INITIAL and FINAL positions:\n")

    for word, occs in sorted(linking_candidates, key=lambda x: -len(x[1])):
        initial_folios = [o['folio'] for o in occs if o['pos_class'] == 'INITIAL']
        final_folios = [o['folio'] for o in occs if o['pos_class'] == 'FINAL']

        print(f"  {word}:")
        print(f"    INITIAL in: {initial_folios}")
        print(f"    FINAL in: {final_folios}")

        # Check if FINAL of one para matches INITIAL of another (linking!)
        initial_paras = set(o['para_idx'] for o in occs if o['pos_class'] == 'INITIAL')
        final_paras = set(o['para_idx'] for o in occs if o['pos_class'] == 'FINAL')

        if initial_paras != final_paras:
            print(f"    -> POTENTIAL LINK: Different paragraphs!")
        print()
else:
    print("\nNo RI tokens appear in both INITIAL and FINAL positions.")

# What about INITIAL-only vs FINAL-only repeaters?
print("\n" + "=" * 70)
print("REPEATER POSITION BIAS")
print("=" * 70)

initial_only = sum(1 for p in position_patterns if p == 'INITIAL')
final_only = sum(1 for p in position_patterns if p == 'FINAL')
middle_only = sum(1 for p in position_patterns if p == 'MIDDLE')
mixed = sum(1 for p, c in position_patterns.items() if '+' in p)

print(f"\nRepeater position exclusivity:")
print(f"  INITIAL only: {initial_only}")
print(f"  FINAL only: {final_only}")
print(f"  MIDDLE only: {middle_only}")
print(f"  Mixed (multiple positions): {mixed}")

# Detailed look at top repeaters
print("\n" + "=" * 70)
print("TOP REPEATERS BY FREQUENCY")
print("=" * 70)

top_repeaters = sorted(repeaters.items(), key=lambda x: -len(x[1]))[:15]

print(f"\n{'Word':<18} {'Count':>6} {'Positions':<20} {'Folios'}")
print(f"{'-'*18} {'-'*6} {'-'*20} {'-'*30}")

for word, occs in top_repeaters:
    positions = Counter(o['pos_class'] for o in occs)
    pos_str = ', '.join(f"{p}:{c}" for p, c in positions.most_common())
    folios = sorted(set(o['folio'] for o in occs))
    folio_str = ', '.join(folios[:5]) + ('...' if len(folios) > 5 else '')
    print(f"{word:<18} {len(occs):>6} {pos_str:<20} {folio_str}")

# Summary
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

total_linking = len(linking_candidates)
total_repeaters = len(repeaters)

print(f"""
REPEATER STATISTICS:
- Total RI types: {len(ri_occurrences)}
- Singletons: {len(singletons)} ({len(singletons)/len(ri_occurrences)*100:.1f}%)
- Repeaters: {len(repeaters)} ({len(repeaters)/len(ri_occurrences)*100:.1f}%)

LINKING ANALYSIS:
- Repeaters in BOTH INITIAL and FINAL: {total_linking}
- This is {total_linking/total_repeaters*100:.1f}% of repeaters
""")

if total_linking > 0:
    print("FINDING: Some RI tokens DO link records!")
    print("         They appear as FINAL in one paragraph")
    print("         and INITIAL in another - chain linking.")
else:
    print("FINDING: No RI tokens link INITIAL to FINAL")
    print("         Repeaters stay in their position class")

# Save results
results = {
    'total_ri_types': len(ri_occurrences),
    'singleton_count': len(singletons),
    'repeater_count': len(repeaters),
    'position_patterns': dict(position_patterns),
    'linking_candidates': len(linking_candidates),
    'linking_words': [w for w, _ in linking_candidates],
}

out_path = PROJECT_ROOT / 'phases' / 'A_RECORD_B_ROUTING_TOPOLOGY' / 'results' / 't17_ri_repeater_position.json'
with open(out_path, 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to {out_path.name}")
