"""
Phase 440 (round 4): Atom-level distributional analysis for t in MIDDLE.

Current gloss: t="transfer" (SOLID, C1195)
Goal: Find distillation-specific meaning from distributional evidence.

Conclusion: t="drive" — German treiben/abtreiben (to drive off volatile fraction).
Supported by: 87% qo-prefixed sole-t, k-exclusion 0.6%, 95% suffixed,
t→h 56:1 asymmetry, c→t→e/h sequence. k/t QO-EDY hierarchy (brunschwig_comparison.md).
MIDPROCESS gap (C1222) confirms Voynich decomposes DISTILL into k+t sub-steps.

Usage:
    python phases/PREFIX_GLOSS_VALIDATION/scripts/atom_t_analysis.py
"""
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from scripts.voynich import Transcript, Morphology

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
# 1. T IN MIDDLE - basic stats
# ============================================================
print("=" * 70)
print("1. T ATOM — position and frequency")
print("=" * 70)

t_mid = [(tok, m) for tok, m in morphs if m.middle and 't' in m.middle]
non_t = [(tok, m) for tok, m in morphs if m.middle and 't' not in m.middle]
n_t = len(t_mid)

t_sole = sum(1 for _, m in t_mid if m.middle == 't')
t_multi = [(tok, m) for tok, m in t_mid if len(m.middle) > 1]
t_initial = sum(1 for _, m in t_multi if m.middle[0] == 't')
t_terminal = sum(1 for _, m in t_multi if m.middle[-1] == 't')

print(f"\n  t-in-MIDDLE: {n_t} tokens ({n_t/total*100:.1f}%)")
print(f"  Sole MIDDLE: {t_sole} ({t_sole/n_t*100:.1f}%)")
print(f"  Initial (multi-char): {t_initial}/{len(t_multi)} = {t_initial/len(t_multi)*100:.1f}%")
print(f"  Terminal (multi-char): {t_terminal}/{len(t_multi)} = {t_terminal/len(t_multi)*100:.1f}%")

# ============================================================
# 2. Combinatorial neighbors
# ============================================================
print("\n" + "=" * 70)
print("2. T ATOM — combinatorial neighbors")
print("=" * 70)

pre_t = Counter()
post_t = Counter()
for _, m in t_mid:
    mid = m.middle
    for i, ch in enumerate(mid):
        if ch == 't':
            if i > 0:
                pre_t[mid[i-1]] += 1
            if i < len(mid) - 1:
                post_t[mid[i+1]] += 1

print(f"\n  Characters before t: {pre_t.most_common(10)}")
print(f"  Characters after t:  {post_t.most_common(10)}")

t_middles = Counter(m.middle for _, m in t_mid)
print(f"\n  Top t-MIDDLEs: {t_middles.most_common(15)}")

# ============================================================
# 3. PREFIX selection
# ============================================================
print("\n" + "=" * 70)
print("3. T ATOM — PREFIX co-occurrence")
print("=" * 70)

t_prefixes = Counter(m.prefix for _, m in t_mid if m.prefix)
non_t_prefixes = Counter(m.prefix for _, m in non_t if m.prefix)
t_bare = sum(1 for _, m in t_mid if not m.prefix)
non_t_bare = sum(1 for _, m in non_t if not m.prefix)

print(f"\n  t-MIDDLE prefix distribution:")
for pfx, cnt in t_prefixes.most_common(12):
    non_t_cnt = non_t_prefixes.get(pfx, 0)
    t_rate = cnt / n_t * 100
    non_t_rate = non_t_cnt / len(non_t) * 100
    ratio = t_rate / non_t_rate if non_t_rate > 0 else float('inf')
    print(f"    {pfx}: {cnt} ({t_rate:.1f}%) vs non-t {non_t_cnt} ({non_t_rate:.1f}%) ratio={ratio:.2f}x")
print(f"  Bare (no prefix): t={t_bare}({t_bare/n_t*100:.1f}%) vs non-t={non_t_bare}({non_t_bare/len(non_t)*100:.1f}%)")

# ============================================================
# 4. SUFFIX selection
# ============================================================
print("\n" + "=" * 70)
print("4. T ATOM — SUFFIX co-occurrence")
print("=" * 70)

t_suffixes = Counter(m.suffix if m.suffix else '(bare)' for _, m in t_mid)
non_t_suffixes = Counter(m.suffix if m.suffix else '(bare)' for _, m in non_t)

print(f"\n  t-MIDDLE suffix distribution:")
for sfx, cnt in t_suffixes.most_common(10):
    non_t_cnt = non_t_suffixes.get(sfx, 0)
    t_rate = cnt / n_t * 100
    non_t_rate = non_t_cnt / len(non_t) * 100
    ratio = t_rate / non_t_rate if non_t_rate > 0 else float('inf')
    print(f"    {sfx}: {cnt} ({t_rate:.1f}%) vs non-t {non_t_cnt} ({non_t_rate:.1f}%) ratio={ratio:.2f}x")

# ============================================================
# 5. Kernel co-occurrence
# ============================================================
print("\n" + "=" * 70)
print("5. T ATOM — kernel interaction")
print("=" * 70)

t_k = sum(1 for _, m in t_mid if 'k' in m.middle)
t_e = sum(1 for _, m in t_mid if 'e' in m.middle)
t_h = sum(1 for _, m in t_mid if 'h' in m.middle)
t_no_kernel = sum(1 for _, m in t_mid if not any(c in m.middle for c in 'keh'))

print(f"\n  Kernel co-occurrence with t:")
print(f"    k: {t_k/n_t*100:.1f}% (baseline {sum(1 for _, m in non_t if 'k' in m.middle)/len(non_t)*100:.1f}%)")
print(f"    e: {t_e/n_t*100:.1f}% (baseline {sum(1 for _, m in non_t if 'e' in m.middle)/len(non_t)*100:.1f}%)")
print(f"    h: {t_h/n_t*100:.1f}% (baseline {sum(1 for _, m in non_t if 'h' in m.middle)/len(non_t)*100:.1f}%)")
print(f"    NO kernel: {t_no_kernel/n_t*100:.1f}%")

# ============================================================
# 6. Line position
# ============================================================
print("\n" + "=" * 70)
print("6. T ATOM — line position")
print("=" * 70)

t_line_init = sum(1 for tok, _ in t_mid if lines[(tok.folio, tok.line)][0] is tok)
t_line_final = sum(1 for tok, _ in t_mid if lines[(tok.folio, tok.line)][-1] is tok)

t_positions = []
for tok, m in t_mid:
    line_toks = lines[(tok.folio, tok.line)]
    if len(line_toks) < 2:
        continue
    idx = next((i for i, t2 in enumerate(line_toks) if t2 is tok), 0)
    t_positions.append(idx / (len(line_toks) - 1))

print(f"\n  Line-initial: {t_line_init/n_t*100:.1f}%")
print(f"  Line-final: {t_line_final/n_t*100:.1f}%")
print(f"  Mean position: {sum(t_positions)/len(t_positions):.3f}")

# ============================================================
# 7. Section distribution
# ============================================================
print("\n" + "=" * 70)
print("7. T ATOM — section distribution")
print("=" * 70)

t_sections = Counter(tok.section for tok, _ in t_mid)
non_t_sections = Counter(tok.section for tok, _ in non_t)

print(f"\n  Sections:")
for sec in sorted(set(list(t_sections.keys()) + list(non_t_sections.keys()))):
    t_cnt = t_sections.get(sec, 0)
    nt_cnt = non_t_sections.get(sec, 0)
    t_rate = t_cnt / n_t * 100
    nt_rate = nt_cnt / len(non_t) * 100
    print(f"    {sec}: t={t_cnt}({t_rate:.1f}%) vs non-t={nt_cnt}({nt_rate:.1f}%)")

# ============================================================
# 8. Forbidden / rare sequences
# ============================================================
print("\n" + "=" * 70)
print("8. T ATOM — forbidden/rare sequences")
print("=" * 70)

tt_count = sum(1 for _, m in morphs if m.middle and 'tt' in m.middle)
# t-X and X-t bigrams
t_post = Counter()
t_pre = Counter()
for _, m in morphs:
    mid = m.middle or ''
    for i in range(len(mid)-1):
        if mid[i] == 't':
            t_post[mid[i+1]] += 1
        if mid[i+1] == 't':
            t_pre[mid[i]] += 1

print(f"\n  t->t (doubled): {tt_count}")
print(f"  t->X bigrams: {t_post.most_common(10)}")
print(f"  X->t bigrams: {t_pre.most_common(10)}")

# Directional asymmetries
for partner in ['k', 'e', 'h', 'o', 'a', 'r', 'l', 'c', 'd']:
    tp = sum(1 for _, m in morphs if m.middle and f't{partner}' in m.middle)
    pt = sum(1 for _, m in morphs if m.middle and f'{partner}t' in m.middle)
    if tp > 0 or pt > 0:
        print(f"  t->{partner}: {tp} vs {partner}->t: {pt}")

# ============================================================
# 9. Sole t MIDDLE — who selects it?
# ============================================================
print("\n" + "=" * 70)
print("9. Sole t MIDDLE — context")
print("=" * 70)

sole_t = [(tok, m) for tok, m in morphs if m.middle == 't']
sole_t_pfx = Counter(m.prefix for _, m in sole_t if m.prefix)
sole_t_sfx = Counter(m.suffix if m.suffix else '(bare)' for _, m in sole_t)
sole_t_words = Counter(tok.word for tok, _ in sole_t)

print(f"\n  Sole t tokens: {len(sole_t)}")
print(f"  Prefixes: {sole_t_pfx.most_common(10)}")
print(f"  Suffixes: {sole_t_sfx.most_common(10)}")
print(f"  Top words: {sole_t_words.most_common(10)}")

# ============================================================
# 10. Compare t with structurally similar atoms
# ============================================================
print("\n" + "=" * 70)
print("10. T vs similar atoms (d, c, s)")
print("=" * 70)

for atom in ['d', 'c', 's', 't']:
    atom_mid = [(tok, m) for tok, m in morphs if m.middle and atom in m.middle]
    n_atom = len(atom_mid)
    if n_atom == 0:
        continue
    atom_sole = sum(1 for _, m in atom_mid if m.middle == atom)
    atom_multi = [m for _, m in atom_mid if len(m.middle) > 1]
    atom_initial = sum(1 for m in atom_multi if m.middle[0] == atom)
    atom_terminal = sum(1 for m in atom_multi if m.middle[-1] == atom)
    atom_k = sum(1 for _, m in atom_mid if 'k' in m.middle and atom != 'k')
    atom_e = sum(1 for _, m in atom_mid if 'e' in m.middle and atom != 'e')
    atom_bare = sum(1 for _, m in atom_mid if not m.suffix)

    print(f"\n  {atom}: {n_atom} tokens")
    print(f"    sole={atom_sole}({atom_sole/n_atom*100:.1f}%)")
    print(f"    init={atom_initial}/{len(atom_multi)}({atom_initial/max(len(atom_multi),1)*100:.1f}%)")
    print(f"    term={atom_terminal}/{len(atom_multi)}({atom_terminal/max(len(atom_multi),1)*100:.1f}%)")
    print(f"    k-co={atom_k/n_atom*100:.1f}% e-co={atom_e/n_atom*100:.1f}%")
    print(f"    suffixless={atom_bare/n_atom*100:.1f}%")

# ============================================================
# 11. What role do t-MIDDLE tokens play in the grammar?
# ============================================================
print("\n" + "=" * 70)
print("11. T ATOM — grammar class distribution")
print("=" * 70)

# Check if tokens have analysis data
from scripts.voynich import BFolioDecoder
decoder = BFolioDecoder()

# Sample: decode a few folios and check t-MIDDLE token roles
t_roles = Counter()
t_prefix_roles = Counter()
t_zones = Counter()
sample_folios = ['f76r', 'f75r', 'f78r', 'f103r', 'f111r', 'f86v6', 'f99v', 'f100r', 'f101r', 'f102r']

for folio_id in sample_folios:
    try:
        analysis = decoder.decode_folio(folio_id)
        for line in analysis.lines:
            for tok in line.tokens:
                m = morph.extract(tok.word)
                if m.middle and 't' in m.middle:
                    if hasattr(tok, 'prefix_role') and tok.prefix_role:
                        t_prefix_roles[tok.prefix_role] += 1
                    if hasattr(tok, 'zone') and tok.zone:
                        t_zones[tok.zone] += 1
    except:
        pass

if t_prefix_roles:
    print(f"\n  PREFIX roles for t-MIDDLE tokens: {t_prefix_roles.most_common()}")
if t_zones:
    print(f"  Zones for t-MIDDLE tokens: {t_zones.most_common()}")

# ============================================================
# 12. t in SUFFIX position vs MIDDLE position
# ============================================================
print("\n" + "=" * 70)
print("12. T in SUFFIX vs MIDDLE")
print("=" * 70)

t_in_suffix = sum(1 for _, m in morphs if m.suffix and 't' in m.suffix)
t_in_middle_only = sum(1 for _, m in morphs if m.middle and 't' in m.middle and (not m.suffix or 't' not in m.suffix))

print(f"\n  t in MIDDLE (not suffix): {t_in_middle_only}")
print(f"  t in SUFFIX: {t_in_suffix}")

# What suffixes contain t?
t_suffixes_list = Counter()
for _, m in morphs:
    if m.suffix and 't' in m.suffix:
        t_suffixes_list[m.suffix] += 1
print(f"  t-containing suffixes: {t_suffixes_list.most_common()}")

# ============================================================
# 13. Paragraph position — does t appear more in certain zones?
# ============================================================
print("\n" + "=" * 70)
print("13. T ATOM — paragraph position (early/mid/late lines)")
print("=" * 70)

# Reconstruct paragraphs from par_initial boundaries
# Walk tokens in order, incrementing paragraph ID at each par_initial=True
para_id = 0
para_lines = defaultdict(list)
for tok, m in morphs:
    if tok.par_initial:
        para_id += 1
    para_lines[(tok.folio, para_id)].append((tok, m))

t_in_first_quarter = 0
t_in_last_quarter = 0
t_total_para = 0
non_t_first = 0
non_t_last = 0
non_t_total = 0

for (folio, para), tokens in para_lines.items():
    # Get unique line numbers, sorted
    line_nums = sorted(set(tok.line for tok, _ in tokens))
    if len(line_nums) < 4:
        continue
    first_q = set(line_nums[:len(line_nums)//4])
    last_q = set(line_nums[-len(line_nums)//4:])

    for tok, m in tokens:
        if m.middle and 't' in m.middle:
            t_total_para += 1
            if tok.line in first_q:
                t_in_first_quarter += 1
            if tok.line in last_q:
                t_in_last_quarter += 1
        elif m.middle:
            non_t_total += 1
            if tok.line in first_q:
                non_t_first += 1
            if tok.line in last_q:
                non_t_last += 1

if t_total_para > 0:
    print(f"\n  First quarter of paragraph: t={t_in_first_quarter/t_total_para*100:.1f}% vs non-t={non_t_first/non_t_total*100:.1f}%")
    print(f"  Last quarter of paragraph:  t={t_in_last_quarter/t_total_para*100:.1f}% vs non-t={non_t_last/non_t_total*100:.1f}%")

print(f"\n{'=' * 70}")
print("SUMMARY: t = 'drive'")
print(f"{'=' * 70}")
print("""
  Evidence:
    1. 87% of sole-t tokens are qo-prefixed (energy channel owns it)
    2. k-exclusion extreme: 0.6% (t is NOT heating — complementary to k)
    3. 95% suffix-requiring (needs endpoints, unlike self-completing r)
    4. t->h 56:1 asymmetry (drives into watching/monitoring)
    5. c->t->e/h sequence (adjust -> drive -> cool/watch)
    6. tt FORBIDDEN (0 occurrences)
    7. Never appears in suffixes (purely operational, not flow-control)

  'transfer' fails: too vague, doesn't discriminate from any other atom.
  'drive' fits: German treiben/abtreiben = "drive off" volatile fraction.

  Distillation cycle in atoms:
    k -> t -> e -> h -> l
    heat -> drive -> cool -> watch -> collect
    (kochen -> treiben -> ? -> ? -> lege)

  k and t are complementary energy operations:
    k = raw heat input (KERNEL operator, kochen = cook/boil)
    t = controlled extraction (NOT kernel, treiben = drive off)

  Supported by existing research:
    - k/t hierarchy in QO-EDY (brunschwig_comparison.md)
    - MIDPROCESS gap (C1222): modern distillation 34.5% process control,
      Brunschwig 0% — Voynich decomposes DISTILL into k+t sub-steps
    - Brunschwig uses DISTILL 227 times undifferentiated;
      Voynich separates fire management (k) from vapor management (t)
""")
print("Phase 440 round 4 complete.")
