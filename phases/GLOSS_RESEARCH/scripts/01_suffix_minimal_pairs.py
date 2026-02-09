"""Test 01: Suffix Minimal Pairs

Question: Do suffixes (-y, -dy, -hy, -ey, -ly) encode different operations
when attached to the same stem (prefix+middle)?

Method:
  1. Extract all B tokens, decompose into prefix+middle+suffix
  2. Group by stem (prefix+middle), find stems with 2+ different suffixes
  3. For each minimal pair, compare:
     - Line position (early/mid/late)
     - Regime distribution
     - Preceding/following token patterns
     - Section distribution
  4. If suffix choice correlates with context, they encode different operations
     If randomly distributed, suffixes are grammatical variants
"""
import json, sys
from pathlib import Path
from collections import Counter, defaultdict
sys.path.insert(0, str(Path(r'C:\git\voynich')))
from scripts.voynich import Transcript, Morphology

tx = Transcript()
morph = Morphology()

# Collect all B tokens with morphological decomposition and line context
tokens = list(tx.currier_b())
print(f"Total B tokens: {len(tokens)}")

# Build line-level index: folio -> line -> [tokens]
lines = defaultdict(lambda: defaultdict(list))
for t in tokens:
    lines[t.folio][t.line].append(t)

# Decompose each token
stem_suffix_map = defaultdict(lambda: defaultdict(list))  # stem -> suffix -> [token_contexts]

for t in tokens:
    m = morph.extract(t.word)
    if not m.middle:
        continue

    stem = (m.prefix or '') + m.middle
    suffix = m.suffix or ''

    # Get line position (fraction of line)
    line_tokens = lines[t.folio][t.line]
    pos_in_line = next((i for i, lt in enumerate(line_tokens) if lt is t), 0)
    line_len = len(line_tokens)
    pos_frac = pos_in_line / max(line_len - 1, 1)

    stem_suffix_map[stem][suffix].append({
        'word': t.word,
        'folio': t.folio,
        'line': t.line,
        'pos_frac': pos_frac,
        'section': t.section,
    })

# Find stems with multiple suffixes (minimal pairs)
TARGET_SUFFIXES = {'y', 'dy', 'hy', 'ey', 'ly', 'ain', 'aiin', 'al', 'ar', 'am', 'or', 'ol', 's', ''}
minimal_pairs = {}
for stem, suffix_dict in stem_suffix_map.items():
    # Only consider target suffixes
    relevant = {s: contexts for s, contexts in suffix_dict.items() if s in TARGET_SUFFIXES}
    if len(relevant) >= 2:
        total = sum(len(c) for c in relevant.values())
        if total >= 5:  # minimum evidence threshold
            minimal_pairs[stem] = relevant

print(f"\nStems with 2+ suffix variants (min 5 total tokens): {len(minimal_pairs)}")

# Analyze the top minimal pairs
print(f"\n{'='*80}")
print(f"TOP MINIMAL PAIRS BY TOTAL FREQUENCY")
print(f"{'='*80}")

sorted_pairs = sorted(minimal_pairs.items(),
                       key=lambda x: sum(len(c) for c in x[1].values()),
                       reverse=True)

for stem, suffix_dict in sorted_pairs[:30]:
    total = sum(len(c) for c in suffix_dict.values())
    print(f"\nSTEM: '{stem}' ({total} tokens)")

    for suffix, contexts in sorted(suffix_dict.items(), key=lambda x: -len(x)):
        count = len(contexts)
        mean_pos = sum(c['pos_frac'] for c in contexts) / count

        # Position distribution: early (<0.25), mid (0.25-0.75), late (>0.75)
        early = sum(1 for c in contexts if c['pos_frac'] < 0.25)
        mid = sum(1 for c in contexts if 0.25 <= c['pos_frac'] <= 0.75)
        late = sum(1 for c in contexts if c['pos_frac'] > 0.75)

        # Section distribution
        sections = Counter(c['section'] for c in contexts)
        sec_str = ', '.join(f"{s}:{n}" for s, n in sections.most_common(3))

        # Folio spread
        folios = len(set(c['folio'] for c in contexts))

        sfx_label = suffix if suffix else '(none)'
        print(f"  -{sfx_label:<6} {count:>4}x  pos={mean_pos:.2f}  E/M/L={early}/{mid}/{late}  fol={folios:>2}  {sec_str}")

# Statistical test: for each stem, is suffix choice correlated with position?
print(f"\n{'='*80}")
print(f"POSITION BIAS TEST")
print(f"{'='*80}")
print(f"For each stem: does suffix choice predict line position?")
print(f"Comparing mean position of each suffix variant.\n")

sig_pairs = []
for stem, suffix_dict in sorted_pairs[:30]:
    positions_by_suffix = {}
    for suffix, contexts in suffix_dict.items():
        if len(contexts) >= 3:  # need enough data
            positions_by_suffix[suffix] = [c['pos_frac'] for c in contexts]

    if len(positions_by_suffix) >= 2:
        # Compare the two most common suffixes
        items = sorted(positions_by_suffix.items(), key=lambda x: -len(x[1]))
        s1, p1 = items[0]
        s2, p2 = items[1]
        mean1 = sum(p1) / len(p1)
        mean2 = sum(p2) / len(p2)
        diff = abs(mean1 - mean2)

        s1_label = s1 if s1 else '(none)'
        s2_label = s2 if s2 else '(none)'

        marker = "***" if diff > 0.15 else "**" if diff > 0.10 else "*" if diff > 0.05 else ""
        print(f"  {stem:<12} -{s1_label:<6}(n={len(p1):>3}, pos={mean1:.2f}) vs -{s2_label:<6}(n={len(p2):>3}, pos={mean2:.2f})  diff={diff:.2f} {marker}")

        if diff > 0.10:
            sig_pairs.append((stem, s1, mean1, len(p1), s2, mean2, len(p2), diff))

print(f"\n{'='*80}")
print(f"SUFFIX GLOBAL POSITION PROFILES")
print(f"{'='*80}")
print(f"Mean line position for each suffix across ALL tokens:\n")

suffix_positions = defaultdict(list)
for t in tokens:
    m = morph.extract(t.word)
    if not m.middle or not m.suffix:
        continue
    if m.suffix not in TARGET_SUFFIXES:
        continue

    line_tokens = lines[t.folio][t.line]
    pos_in_line = next((i for i, lt in enumerate(line_tokens) if lt is t), 0)
    line_len = len(line_tokens)
    pos_frac = pos_in_line / max(line_len - 1, 1)
    suffix_positions[m.suffix].append(pos_frac)

for suffix in sorted(suffix_positions.keys(), key=lambda s: -len(suffix_positions[s])):
    positions = suffix_positions[suffix]
    count = len(positions)
    mean = sum(positions) / count
    early = sum(1 for p in positions if p < 0.25) / count * 100
    late = sum(1 for p in positions if p > 0.75) / count * 100
    print(f"  -{suffix:<6} n={count:>5}  mean_pos={mean:.3f}  early={early:.1f}%  late={late:.1f}%")

# Save results
results = {
    'total_stems_with_pairs': len(minimal_pairs),
    'significant_position_diffs': [
        {'stem': s, 'suffix1': s1, 'pos1': round(m1,3), 'n1': n1,
         'suffix2': s2, 'pos2': round(m2,3), 'n2': n2, 'diff': round(d,3)}
        for s, s1, m1, n1, s2, m2, n2, d in sig_pairs
    ],
    'global_suffix_profiles': {
        s: {'count': len(p), 'mean_pos': round(sum(p)/len(p), 3)}
        for s, p in suffix_positions.items()
    }
}

with open('phases/GLOSS_RESEARCH/results/01_suffix_minimal_pairs.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nResults saved to phases/GLOSS_RESEARCH/results/01_suffix_minimal_pairs.json")
