"""
f57v X/Y Placement Compound Analysis

Questions:
1. What are X/Y placements on f57v?
2. Are these compound MIDDLEs (contain PP atoms)?
3. How do they compare to line-1 HT identification tokens?
4. Do they relate to the R2 coordinate system?
"""

import sys
from pathlib import Path
from collections import Counter, defaultdict

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.voynich import Transcript, Morphology

tx = Transcript()
morph = Morphology()

print("="*70)
print("f57v X/Y PLACEMENT COMPOUND ANALYSIS")
print("="*70)

# ============================================================
# GET PP MIDDLES (shared A-B vocabulary)
# ============================================================

a_middles = set()
for token in tx.currier_a():
    w = token.word.strip()
    if w and '*' not in w:
        m = morph.extract(w)
        if m.middle:
            a_middles.add(m.middle)

b_middles = set()
for token in tx.currier_b():
    w = token.word.strip()
    if w and '*' not in w:
        m = morph.extract(w)
        if m.middle:
            b_middles.add(m.middle)

pp_middles = a_middles & b_middles
print(f"\nPP MIDDLEs (shared A-B): {len(pp_middles)}")

# ============================================================
# COLLECT ALL f57v TOKENS BY PLACEMENT
# ============================================================

f57v_by_placement = defaultdict(list)

for token in tx.all():
    if token.folio == 'f57v':
        w = token.word.strip()
        if w and '*' not in w:
            m = morph.extract(w)
            f57v_by_placement[token.placement].append({
                'word': w,
                'middle': m.middle,
                'prefix': m.prefix,
                'suffix': m.suffix,
                'line': token.line
            })

print(f"\nPlacements on f57v: {sorted(f57v_by_placement.keys())}")

# ============================================================
# ANALYZE X AND Y PLACEMENTS
# ============================================================
print("\n" + "="*70)
print("X PLACEMENT TOKENS")
print("="*70)

x_tokens = f57v_by_placement.get('X', [])
print(f"\nTotal X tokens: {len(x_tokens)}")

for t in x_tokens:
    word = t['word']
    mid = t['middle']

    # Find PP atoms contained in this MIDDLE
    pp_atoms = [pp for pp in pp_middles if pp in mid and pp != mid] if mid else []

    print(f"\n  '{word}'")
    print(f"    PREFIX: {t['prefix']}, MIDDLE: '{mid}', SUFFIX: {t['suffix']}")
    print(f"    PP atoms contained: {pp_atoms[:10]}")
    print(f"    Compound: {'YES' if pp_atoms else 'NO'}")

print("\n" + "="*70)
print("Y PLACEMENT TOKENS")
print("="*70)

y_tokens = f57v_by_placement.get('Y', [])
print(f"\nTotal Y tokens: {len(y_tokens)}")

for t in y_tokens:
    word = t['word']
    mid = t['middle']

    # Find PP atoms contained in this MIDDLE
    pp_atoms = [pp for pp in pp_middles if pp in mid and pp != mid] if mid else []

    print(f"\n  '{word}'")
    print(f"    PREFIX: {t['prefix']}, MIDDLE: '{mid}', SUFFIX: {t['suffix']}")
    print(f"    PP atoms contained: {pp_atoms[:10]}")
    print(f"    Compound: {'YES' if pp_atoms else 'NO'}")

# ============================================================
# COMPARE TO RING TOKENS
# ============================================================
print("\n" + "="*70)
print("COMPARISON: X/Y vs RING PLACEMENTS")
print("="*70)

def analyze_placement(tokens, name):
    if not tokens:
        return None

    middles = [t['middle'] for t in tokens if t['middle']]
    if not middles:
        return None

    # Compound rate
    compound_count = 0
    pp_atom_counts = []
    for mid in middles:
        pp_atoms = [pp for pp in pp_middles if pp in mid and pp != mid]
        if pp_atoms:
            compound_count += 1
            pp_atom_counts.append(len(pp_atoms))

    compound_rate = 100 * compound_count / len(middles)
    mean_pp = sum(pp_atom_counts) / len(pp_atom_counts) if pp_atom_counts else 0
    mean_mid_len = sum(len(m) for m in middles) / len(middles)

    return {
        'name': name,
        'n_tokens': len(tokens),
        'n_middles': len(middles),
        'compound_rate': compound_rate,
        'mean_pp_atoms': mean_pp,
        'mean_middle_len': mean_mid_len
    }

placements_to_compare = ['R1', 'R2', 'R3', 'R4', 'X', 'Y']
results = []

for p in placements_to_compare:
    tokens = f57v_by_placement.get(p, [])
    r = analyze_placement(tokens, p)
    if r:
        results.append(r)

print(f"\n{'Placement':<10} {'Tokens':<8} {'Compound%':<12} {'Mean PP atoms':<15} {'Mean MID len':<12}")
print("-" * 60)
for r in results:
    print(f"{r['name']:<10} {r['n_tokens']:<8} {r['compound_rate']:<12.1f} {r['mean_pp_atoms']:<15.2f} {r['mean_middle_len']:<12.2f}")

# ============================================================
# CHECK IF X/Y MIDDLES APPEAR ELSEWHERE
# ============================================================
print("\n" + "="*70)
print("X/Y MIDDLE UNIQUENESS")
print("="*70)

# Get all MIDDLEs from the entire manuscript
all_middles_by_folio = defaultdict(set)
for token in tx.all():
    w = token.word.strip()
    if w and '*' not in w:
        m = morph.extract(w)
        if m.middle:
            all_middles_by_folio[token.folio].add(m.middle)

# Check X/Y MIDDLEs
xy_middles = set()
for t in x_tokens + y_tokens:
    if t['middle']:
        xy_middles.add(t['middle'])

print(f"\nUnique MIDDLEs in X/Y positions: {len(xy_middles)}")
print(f"MIDDLEs: {sorted(xy_middles, key=len, reverse=True)}")

# Where else do these appear?
for mid in sorted(xy_middles, key=len, reverse=True):
    folios_with_mid = [f for f, mids in all_middles_by_folio.items() if mid in mids]
    print(f"\n  '{mid}' appears in {len(folios_with_mid)} folios:")
    if len(folios_with_mid) <= 5:
        print(f"    {folios_with_mid}")
    else:
        print(f"    {folios_with_mid[:5]}... and {len(folios_with_mid)-5} more")

# ============================================================
# CHECK RELATIONSHIP TO FL PRIMITIVES
# ============================================================
print("\n" + "="*70)
print("RELATIONSHIP TO FL PRIMITIVES")
print("="*70)

# FL characters per C771
fl_chars = set('adilmnory')

# Check if X/Y MIDDLEs use FL-only chars or include kernel/helpers
for mid in sorted(xy_middles, key=len, reverse=True):
    mid_chars = set(mid)
    uses_fl_only = mid_chars <= fl_chars
    kernel_chars = mid_chars & set('khe')
    helper_chars = mid_chars & set('cst')

    print(f"\n  '{mid}'")
    print(f"    FL-only: {uses_fl_only}")
    print(f"    Kernel chars (k,h,e): {kernel_chars if kernel_chars else 'none'}")
    print(f"    Helper chars (c,s,t): {helper_chars if helper_chars else 'none'}")

# ============================================================
# VERDICT
# ============================================================
print("\n" + "="*70)
print("VERDICT")
print("="*70)

xy_results = [r for r in results if r['name'] in ['X', 'Y']]
ring_results = [r for r in results if r['name'] in ['R1', 'R3']]

if xy_results and ring_results:
    xy_compound = sum(r['compound_rate'] for r in xy_results) / len(xy_results)
    ring_compound = sum(r['compound_rate'] for r in ring_results) / len(ring_results)

    xy_mid_len = sum(r['mean_middle_len'] for r in xy_results) / len(xy_results)
    ring_mid_len = sum(r['mean_middle_len'] for r in ring_results) / len(ring_results)

    print(f"""
X/Y vs Ring Comparison:
  - X/Y compound rate: {xy_compound:.1f}%
  - Ring (R1/R3) compound rate: {ring_compound:.1f}%

  - X/Y mean MIDDLE length: {xy_mid_len:.2f}
  - Ring mean MIDDLE length: {ring_mid_len:.2f}

{'X/Y positions contain LONGER, MORE COMPOUND MIDDLEs than ring text'
 if xy_compound > ring_compound and xy_mid_len > ring_mid_len
 else 'Pattern unclear - needs more analysis'}
""")
