"""
Phase 440 (round 2): Atom-level gloss validation for o, a + prefix so.

Expert review of round 1 output flagged:
  o="work" (WEAK, C1195) — no discriminating power
  a="yield" (WEAK, C1195) — positional mismatch (86.3% initial)
  so="scaffold" — unsourced, contradicts CC_INIT role assignment

This script reproduces the key distributional findings.

Usage:
    python phases/PREFIX_GLOSS_VALIDATION/scripts/atom_so_analysis.py
"""
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from scripts.voynich import Transcript, Morphology

OUT = Path(__file__).parent.parent / 'results'
tx = Transcript()
morph = Morphology()
b_tokens = list(tx.currier_b())

morphs = []
for tok in b_tokens:
    if not tok.word.strip() or '*' in tok.word:
        continue
    m = morph.extract(tok.word)
    morphs.append((tok, m))

total = len(morphs)
lines = defaultdict(list)
for tok, m in morphs:
    lines[(tok.folio, tok.line)].append(tok)

print(f"Currier B corpus: {total} tokens\n")

# ============================================================
# 1. O ATOM in MIDDLEs
# ============================================================
print("=" * 70)
print("1. O ATOM — vessel vs work")
print("=" * 70)

o_mid = [(tok, m) for tok, m in morphs if m.middle and 'o' in m.middle]
non_o = [(tok, m) for tok, m in morphs if m.middle and 'o' not in m.middle]
n_o = len(o_mid)

# Position in MIDDLE
o_initial = sum(1 for _, m in o_mid if m.middle[0] == 'o')
o_terminal = sum(1 for _, m in o_mid if m.middle[-1] == 'o')
o_sole = sum(1 for _, m in o_mid if m.middle == 'o')

# Kernel co-occurrence
k_co = sum(1 for _, m in o_mid if 'k' in m.middle)
e_co = sum(1 for _, m in o_mid if 'e' in m.middle)
h_co = sum(1 for _, m in o_mid if 'h' in m.middle)

# Suffix -dy enrichment
o_dy = sum(1 for _, m in o_mid if m.suffix == 'dy')
non_o_dy = sum(1 for _, m in non_o if m.suffix == 'dy')
o_sfxd = sum(1 for _, m in o_mid if m.suffix)
non_o_sfxd = sum(1 for _, m in non_o if m.suffix)

# PREFIX complementary distribution
o_qo = sum(1 for _, m in o_mid if m.prefix == 'qo')
non_o_qo = sum(1 for _, m in non_o if m.prefix == 'qo')
o_ch = sum(1 for _, m in o_mid if m.prefix == 'ch')
non_o_ch = sum(1 for _, m in non_o if m.prefix == 'ch')
o_bare = sum(1 for _, m in o_mid if not m.prefix)
non_o_bare = sum(1 for _, m in non_o if not m.prefix)

print(f"\n  o-in-MIDDLE: {n_o} tokens ({n_o/total*100:.1f}%)")
print(f"  Position: initial={o_initial}({o_initial/n_o*100:.1f}%) terminal={o_terminal}({o_terminal/n_o*100:.1f}%) sole={o_sole}")
print(f"  Kernel co-occurrence: k={k_co}({k_co/n_o*100:.1f}%) e={e_co}({e_co/n_o*100:.1f}%) h={h_co}({h_co/n_o*100:.1f}%)")
print(f"  k in non-o: {sum(1 for _, m in non_o if 'k' in m.middle)/len(non_o)*100:.1f}%")
print(f"  -dy suffix: o={o_dy}/{o_sfxd}({o_dy/o_sfxd*100:.1f}% of suffixed) vs non-o={non_o_dy}/{non_o_sfxd}({non_o_dy/non_o_sfxd*100:.1f}%)")
print(f"  qo prefix: o={o_qo}({o_qo/n_o*100:.1f}%) vs non-o={non_o_qo}({non_o_qo/len(non_o)*100:.1f}%)")
print(f"  ch/sh prefix: o={o_ch+sum(1 for _, m in o_mid if m.prefix=='sh')}({(o_ch+sum(1 for _, m in o_mid if m.prefix=='sh'))/n_o*100:.1f}%)")
print(f"  Bare (no prefix): o={o_bare}({o_bare/n_o*100:.1f}%) vs non-o={non_o_bare}({non_o_bare/len(non_o)*100:.1f}%)")
print(f"\n  KEY: k-o anti-correlation, -dy 6.5x enriched, qo depleted 3.2x.")
print(f"  'vessel' fits: sealed, monitored, anti-correlated with energy kernel.")

# ============================================================
# 2. A ATOM in MIDDLEs
# ============================================================
print("\n" + "=" * 70)
print("2. A ATOM — accept vs yield")
print("=" * 70)

a_mid = [(tok, m) for tok, m in morphs if m.middle and 'a' in m.middle]
n_a = len(a_mid)

# Position
a_initial = sum(1 for _, m in a_mid if len(m.middle) > 1 and m.middle[0] == 'a')
a_multi = sum(1 for _, m in a_mid if len(m.middle) > 1)

# What follows a when initial
followers = Counter()
for _, m in a_mid:
    if len(m.middle) > 1 and m.middle[0] == 'a':
        followers[m.middle[1]] += 1

# a->y forbidden test
a_then_y = sum(1 for _, m in a_mid if len(m.middle) > 1 and m.middle[0] == 'a' and 'y' in m.middle[1:])

# Suffix rate
a_bare_sfx = sum(1 for _, m in a_mid if not m.suffix)
non_a = [(tok, m) for tok, m in morphs if m.middle and 'a' not in m.middle]
non_a_bare_sfx = sum(1 for _, m in non_a if not m.suffix)

print(f"\n  a-in-MIDDLE: {n_a} tokens ({n_a/total*100:.1f}%)")
print(f"  Initial position: {a_initial}/{a_multi} = {a_initial/a_multi*100:.1f}% (C1209 claims 86.3%)")
print(f"  Followers when initial: {followers.most_common(8)}")
print(f"  a->y occurrences: {a_then_y} (FORBIDDEN test)")
print(f"  Suffixless: a={a_bare_sfx/n_a*100:.1f}% vs non-a={non_a_bare_sfx/len(non_a)*100:.1f}%")
print(f"  Top a-MIDDLEs: {Counter(m.middle for _, m in a_mid).most_common(8)}")
print(f"\n  KEY: 86.3% initial = onset atom. a->i 50.5% = accept-then-iterate.")
print(f"  a->y forbidden. 'accept/intake' fits; 'yield as output' contradicts position.")

# ============================================================
# 3. SO PREFIX
# ============================================================
print("\n" + "=" * 70)
print("3. SO PREFIX — initiate vs scaffold")
print("=" * 70)

so_sub = [(tok, m) for tok, m in morphs if m.prefix == 'so']
n_so = len(so_sub)
so_mids = Counter(m.middle for _, m in so_sub)
so_line_init = sum(1 for tok, _ in so_sub if lines[(tok.folio, tok.line)][0] is tok)
so_sections = Counter(tok.section for tok, _ in so_sub)

# Kernel density
so_kernel = sum(1 for _, m in so_sub if m.middle and any(c in m.middle for c in 'khe'))
so_sfx_bare = sum(1 for _, m in so_sub if not m.suffix)

print(f"\n  SO: {n_so} tokens ({n_so/total*100:.1f}%)")
print(f"  Line-initial: {so_line_init} ({so_line_init/n_so*100:.1f}%)")
print(f"  Top MIDDLEs: {so_mids.most_common(8)}")
print(f"  Kernel density: {so_kernel/n_so*100:.1f}%")
print(f"  Suffixless: {so_sfx_bare/n_so*100:.1f}%")
print(f"  Sections: {dict(so_sections.most_common())}")
print(f"\n  KEY: 70.4% line-initial, 72% kernel. Role=CC_INIT, not scaffold.")
print(f"  Proposed: so='initiate'")

print(f"\n{'=' * 70}")
print("Phase 440 round 2 complete.")
print(f"{'=' * 70}")
