"""Multi-atom MIDDLE segmentation.

The current decomposer assumes: MIDDLE = extensions + ONE_ATOM + extensions
Long MIDDLEs (ext >= 4) probably contain MULTIPLE atoms:
  opdaildo = op + dai + l + do  (? atoms + extensions)
  opdaildo = op + d + ai + l + do  (atoms: op, ai; ext: d, l, do?)

This script uses dynamic programming to find the optimal segmentation
that maximizes coverage by known atoms, treating remaining characters
as single-char extensions.
"""
import json
import sys
from collections import Counter, defaultdict

sys.path.insert(0, '.')
from scripts.voynich import Transcript, Morphology, MiddleAnalyzer, BFolioDecoder

# --- Setup ---
tx = Transcript()
morph = Morphology()
decoder = BFolioDecoder()
mid_analyzer = MiddleAnalyzer()
mid_analyzer.build_inventory('B')
core_middles = mid_analyzer._core_middles

with open('data/middle_dictionary.json', encoding='utf-8') as f:
    mid_dict = json.load(f)['middles']

# All known atoms (core MIDDLEs that have glosses)
atoms = {}
for name in sorted(core_middles):
    entry = mid_dict.get(name, {})
    gloss = entry.get('gloss')
    if gloss:
        atoms[name] = gloss

# Single-char extension glosses
ext_glosses = {}
for name, entry in mid_dict.items():
    if len(name) == 1 and entry.get('gloss'):
        ext_glosses[name] = entry['gloss']

print(f"Known atoms with glosses: {len(atoms)}")
print(f"Known extension chars: {len(ext_glosses)}")


def segment_dp(middle):
    """Find optimal segmentation of a MIDDLE into atoms + extension chars.

    Uses dynamic programming. Cost model:
    - Matching an atom costs 0 (ideal)
    - Using a known extension char costs 1
    - Unknown char costs 10 (heavily penalize)

    Returns list of (segment, type, gloss) tuples.
    """
    n = len(middle)
    # dp[i] = (min_cost, backtrack_info) for middle[:i]
    INF = float('inf')
    dp = [(INF, None)] * (n + 1)
    dp[0] = (0, None)

    for i in range(n):
        if dp[i][0] == INF:
            continue

        # Option 1: match a known atom starting at position i
        for atom_name in atoms:
            alen = len(atom_name)
            if i + alen <= n and middle[i:i+alen] == atom_name:
                new_cost = dp[i][0] + 0  # atoms are free
                if new_cost < dp[i + alen][0]:
                    dp[i + alen] = (new_cost, ('atom', i, atom_name))

        # Option 2: single char as extension
        ch = middle[i]
        if ch in ext_glosses:
            ext_cost = 1
        else:
            ext_cost = 10  # unknown char = heavy penalty
        new_cost = dp[i][0] + ext_cost
        if new_cost < dp[i + 1][0]:
            dp[i + 1] = (new_cost, ('ext', i, ch))

    # Backtrack
    if dp[n][0] == INF:
        return None  # can't segment

    segments = []
    pos = n
    while pos > 0:
        _, info = dp[pos]
        if info is None:
            break
        seg_type, start, value = info
        if seg_type == 'atom':
            segments.append((value, 'ATOM', atoms[value]))
            pos = start
        else:
            gloss = ext_glosses.get(value, f'?{value}')
            segments.append((value, 'EXT', gloss))
            pos = start

    segments.reverse()
    return segments


def format_segmentation(segments):
    """Format a segmentation for display."""
    parts = []
    for seg, stype, gloss in segments:
        if stype == 'ATOM':
            parts.append(f"[{seg}]={gloss}")
        else:
            parts.append(f"({seg})={gloss}")
    return ' + '.join(parts)


def compose_multi_gloss(segments):
    """Compose a readable gloss from multi-atom segmentation."""
    atom_parts = []
    ext_parts = []
    for seg, stype, gloss in segments:
        if stype == 'ATOM':
            atom_parts.append(gloss)
        else:
            ext_parts.append(gloss)

    result = ', '.join(atom_parts)
    if ext_parts:
        result += f" (+{', '.join(ext_parts)})"
    return result


# --- Test on all folio-unique MIDDLEs ---
folio_middles = defaultdict(set)
for t in tx.currier_b():
    m = morph.extract(t.word)
    if m and m.middle:
        folio_middles[m.middle].add(t.folio)

unique_middles = {mid: list(folios)[0]
                  for mid, folios in folio_middles.items()
                  if len(folios) == 1}


# --- Compare single-atom vs multi-atom on long MIDDLEs ---
def single_atom_decompose(middle, max_ext=3):
    """Current single-atom decomposition."""
    if middle in core_middles:
        return ('CORE', middle, '', '')
    best = None
    for atom in sorted(core_middles, key=len, reverse=True):
        idx = middle.find(atom)
        if idx >= 0:
            pre = middle[:idx]
            post = middle[idx + len(atom):]
            ext_len = len(pre) + len(post)
            if ext_len <= max_ext and (best is None or ext_len < best[4]):
                best = (atom, pre, post, ext_len, ext_len)
    if best:
        return ('COMPOUND', best[0], best[1], best[2])
    return ('NOVEL', None, '', '')


print(f"\n{'='*80}")
print("MULTI-ATOM vs SINGLE-ATOM: PROBLEM CASES (ext > 3)")
print(f"{'='*80}")

problem_middles = []
for mid in sorted(unique_middles.keys(), key=len, reverse=True):
    result = single_atom_decompose(mid, max_ext=3)
    if result[0] == 'NOVEL' or (result[0] == 'COMPOUND' and
            len(result[2]) + len(result[3]) > 3):
        # Can't decompose with ext<=3
        problem_middles.append(mid)

print(f"\nMIDDLEs that fail single-atom decomposition (ext>3): {len(problem_middles)}")

for mid in problem_middles[:40]:
    # Single-atom (relaxed to ext<=6)
    sa = single_atom_decompose(mid, max_ext=6)
    if sa[0] == 'COMPOUND':
        sa_str = f"{sa[2]}[{sa[1]}]{sa[3]} = ?"
        # compose gloss
        atom_gloss = mid_dict.get(sa[1], {}).get('gloss', '?')
        ext_str = sa[2] + sa[3]
        ext_parts = [ext_glosses.get(ch, f'?{ch}') for ch in ext_str]
        sa_gloss = f"{atom_gloss} (+{', '.join(ext_parts)})"
    else:
        sa_str = "NOVEL"
        sa_gloss = "???"

    # Multi-atom
    ma = segment_dp(mid)
    if ma:
        ma_str = format_segmentation(ma)
        ma_gloss = compose_multi_gloss(ma)
        n_atoms = sum(1 for _, t, _ in ma if t == 'ATOM')
        n_ext = sum(1 for _, t, _ in ma if t == 'EXT')
    else:
        ma_str = "FAILED"
        ma_gloss = "???"
        n_atoms = 0
        n_ext = 0

    print(f"\n  '{mid}' (len={len(mid)}, folio={unique_middles[mid]})")
    print(f"    Single: {sa_gloss}")
    print(f"    Multi:  {ma_gloss}  [{n_atoms} atoms, {n_ext} ext]")
    print(f"            {ma_str}")


# --- Coverage improvement ---
print(f"\n\n{'='*80}")
print("COVERAGE COMPARISON")
print(f"{'='*80}")

single_glossable = 0
multi_glossable = 0
multi_better = 0
examples_improved = []

for mid in unique_middles:
    sa = single_atom_decompose(mid, max_ext=3)
    sa_ok = sa[0] in ('CORE', 'COMPOUND')

    ma = segment_dp(mid)
    ma_ok = ma is not None and any(t == 'ATOM' for _, t, _ in ma)

    if sa_ok:
        single_glossable += 1
    if ma_ok:
        multi_glossable += 1
    if ma_ok and not sa_ok:
        multi_better += 1
        if len(examples_improved) < 15:
            examples_improved.append((mid, ma))

total = len(unique_middles)
print(f"  Single-atom (ext<=3): {single_glossable}/{total} ({100*single_glossable/total:.1f}%)")
print(f"  Multi-atom:           {multi_glossable}/{total} ({100*multi_glossable/total:.1f}%)")
print(f"  Newly glossable:      {multi_better}")

if examples_improved:
    print(f"\n  Examples of newly glossable MIDDLEs:")
    for mid, segs in examples_improved:
        gloss = compose_multi_gloss(segs)
        detail = format_segmentation(segs)
        print(f"    '{mid}' -> {gloss}")
        print(f"      {detail}")


# --- Quality check: do multi-atom segmentations make procedural sense? ---
print(f"\n\n{'='*80}")
print("MULTI-ATOM QUALITY CHECK: Do segmentations read procedurally?")
print(f"{'='*80}")

# Check: how many atoms per MIDDLE?
atom_counts = Counter()
for mid in unique_middles:
    ma = segment_dp(mid)
    if ma:
        n_atoms = sum(1 for _, t, _ in ma if t == 'ATOM')
        atom_counts[n_atoms] += 1

print(f"\nAtoms per MIDDLE (multi-atom segmentation):")
for n, count in sorted(atom_counts.items()):
    bar = '#' * min(count, 60)
    print(f"  {n} atoms: {count:4d} {bar}")

# Show examples of 2-atom and 3-atom segmentations
print(f"\n2-ATOM examples (core operation + secondary operation):")
shown = 0
for mid in sorted(unique_middles.keys(), key=len):
    ma = segment_dp(mid)
    if ma:
        n_atoms = sum(1 for _, t, _ in ma if t == 'ATOM')
        if n_atoms == 2 and shown < 15:
            gloss = compose_multi_gloss(ma)
            detail = format_segmentation(ma)
            print(f"  '{mid}' -> {gloss}")
            print(f"    {detail}")
            shown += 1

print(f"\n3-ATOM examples (multi-step compound):")
shown = 0
for mid in sorted(unique_middles.keys(), key=len):
    ma = segment_dp(mid)
    if ma:
        n_atoms = sum(1 for _, t, _ in ma if t == 'ATOM')
        if n_atoms == 3 and shown < 10:
            gloss = compose_multi_gloss(ma)
            detail = format_segmentation(ma)
            print(f"  '{mid}' -> {gloss}")
            print(f"    {detail}")
            shown += 1

# --- Sanity: check if multi-atom also improves NON-unique MIDDLEs ---
print(f"\n\n{'='*80}")
print("DOES MULTI-ATOM IMPROVE COMMON MIDDLEs TOO?")
print(f"{'='*80}")

# Get all MIDDLEs with 5+ occurrences that fail single-atom ext<=3
all_middles = Counter()
for t in tx.currier_b():
    m = morph.extract(t.word)
    if m and m.middle:
        all_middles[m.middle] += 1

common_problems = []
for mid, count in all_middles.most_common():
    if count >= 5:
        sa = single_atom_decompose(mid, max_ext=3)
        if sa[0] not in ('CORE', 'COMPOUND'):
            ma = segment_dp(mid)
            if ma and any(t == 'ATOM' for _, t, _ in ma):
                common_problems.append((mid, count, ma))

print(f"\nCommon MIDDLEs (5+ tokens) that multi-atom newly glosses: {len(common_problems)}")
for mid, count, segs in common_problems[:20]:
    gloss = compose_multi_gloss(segs)
    detail = format_segmentation(segs)
    print(f"  '{mid}' (x{count}): {gloss}")
    print(f"    {detail}")
