"""
Full atom-level decode of f75r using atomize() — v2.

Uses the new Morphology.atomize() method which bypasses the MIDDLE/SUFFIX
boundary and reads post-prefix characters as a flat atom sequence with
HEAD+MOD*+TERM positional roles. This corrects the -edy suffix theft bug
that was hiding e-depth (balneum mariae gentle heat signatures).

Recipe (PL Ch19 — Aqua vitae composite):
  1. Take aqua vitae (already distilled)
  2. Add 1/3 pure honey with wax (TWO materials)
  3. Ferment in balneum mariae (water bath, gentle heat)
  4. Distill again
  5. Return pure substance each 2nd distillation
  6. Repeat up to 9 times → yields quintessence
"""

import sys, os, io
from collections import Counter, defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))))
from scripts.voynich import Transcript, Morphology, ATOM_GLOSSES, HEAD_ATOMS

tx = Transcript()
morph = Morphology()

PREFIX_LABEL = {
    'qo': 'THERMAL', 'ch': 'TEST', 'sh': 'MONITOR', 'ok': 'VESSEL',
    'ot': 'OPS-CHK', 'da': 'SETUP', 'sa': 'SCAFFOLD', 'ol': 'CONTINUE',
    'or': 'FLOW', 'po': 'PRE-WORK', 'so': 'SCAFF-ARR', 'ke': 'HEAT-BURST',
    'ko': 'HEAT-WORK', 'ka': 'HEAT-YIELD', 'ta': 'XFER-YIELD',
    'pch': 'STAGE-TEST', 'tch': 'XFER-TEST', 'dch': 'MARK-TEST',
    'lch': 'HOLD-TEST', 'lk': 'HOLD-HEAT', 'lsh': 'HOLD-MON',
    'ct': 'CONTROL', 'te': 'XFER-COOL', 'do': 'MARK-WORK',
}

# ═══ LOAD f75r ═══
tokens = [t for t in tx.all()
          if t.folio == 'f75r' and t.word.strip() and not t.is_label]
lines = sorted(set(t.line for t in tokens), key=lambda x: int(x))

# ═══ PARAGRAPH DETECTION ═══
para_bounds = []
for li in lines:
    lt = [t for t in tokens if t.line == li]
    if lt and lt[0].word[0] in 'tkpf' and len(lt[0].word) > 1:
        para_bounds.append(li)

paragraphs = []
for i, start in enumerate(para_bounds):
    if i + 1 < len(para_bounds):
        end_idx = lines.index(para_bounds[i + 1])
        p_lines = lines[lines.index(start):end_idx]
    else:
        p_lines = lines[lines.index(start):]
    p_tokens = [t for t in tokens if t.line in p_lines]
    paragraphs.append({'idx': i+1, 'lines': p_lines, 'tokens': p_tokens})

print(f"f75r: {len(tokens)} tokens, {len(lines)} lines, {len(paragraphs)} paragraphs")

# ═══ FULL LINE-BY-LINE DECODE ═══
print("\n" + "=" * 110)
print("FULL ATOM-LEVEL DECODE: f75r (atomize v2)")
print("=" * 110)

# Stats accumulators
all_heads = Counter()
all_mods = Counter()
all_terms = Counter()
all_prefixes = Counter()
all_e_depths = Counter()

current_para = 0

for li in lines:
    # Paragraph header
    if li in para_bounds:
        pidx = next(p['idx'] for p in paragraphs if p['lines'][0] == li)
        p = paragraphs[pidx - 1]
        n = len(p['tokens'])
        print(f"\n{'=' * 110}")
        print(f"  PARAGRAPH {pidx}  (L{p['lines'][0]}-L{p['lines'][-1]}, {n}T)")
        print(f"{'=' * 110}")

    lt = [t for t in tokens if t.line == li]
    raw_line = ' '.join(t.word for t in lt)
    print(f"\n  L{li:>2s} | {raw_line}")
    print(f"     | {'~' * 95}")

    for t in lt:
        a = morph.atomize(t.word)

        # Collect stats
        if a.prefix:
            all_prefixes[a.prefix] += 1
        for c, role, g in a.atoms:
            if role == 'HEAD': all_heads[c] += 1
            elif role == 'PSEUDO_HEAD': all_heads[f'~{c}'] += 1
            elif role == 'SOLE':
                if c in HEAD_ATOMS: all_heads[c] += 1
                else: all_heads[f'~{c}'] += 1
            elif role == 'MOD': all_mods[c] += 1
            elif role == 'TERM': all_terms[c] += 1
        all_e_depths[a.e_depth] += 1

        # Format
        pre_label = PREFIX_LABEL.get(a.prefix, a.prefix.upper() if a.prefix else 'BARE')
        art_str = f"[{a.articulator}]" if a.articulator else ""
        hl_str = " (headless)" if a.is_headless else ""

        # Atom string with roles
        atom_parts = []
        for c, role, g in a.atoms:
            if role == 'HEAD':
                atom_parts.append(f"*{g}*")  # emphasize HEAD
            elif role == 'TERM':
                atom_parts.append(f">{g}")    # mark TERM
            elif role == 'PSEUDO_HEAD':
                atom_parts.append(f"~{g}~")
            elif role == 'SOLE':
                atom_parts.append(f"[{g}]")
            else:
                atom_parts.append(g)
        atom_str = '.'.join(atom_parts)

        # e-depth annotation
        e_note = ""
        if a.e_depth >= 2:
            e_note = f"  [e{a.e_depth}: GENTLE]"
        elif a.e_depth == 1:
            e_note = f"  [e1: steady]"

        print(f"     |  {t.word:16s}  {art_str}{pre_label:12s} {atom_str}{hl_str}{e_note}")


# ═══ PARAGRAPH PROFILES ═══
print("\n\n" + "=" * 110)
print("PARAGRAPH PROFILES (with corrected e-depth)")
print("=" * 110)

for p in paragraphs:
    pidx = p['idx']
    ptokens = p['tokens']
    n = len(ptokens)

    p_pre = Counter()
    p_head = Counter()
    p_edepth = Counter()
    markers = []

    for t in ptokens:
        a = morph.atomize(t.word)
        if a.prefix: p_pre[a.prefix] += 1
        for c, role, g in a.atoms:
            if role in ('HEAD', 'SOLE'):
                p_head[c] += 1
            elif role == 'PSEUDO_HEAD':
                p_head[f'~{c}'] += 1
        p_edepth[a.e_depth] += 1

    words = [t.word for t in ptokens]
    thermal_pfx = sum(p_pre.get(p, 0) for p in ['qo', 'ko', 'ke', 'lk'])
    monitor_pfx = sum(p_pre.get(p, 0) for p in ['ch', 'sh', 'pch', 'tch', 'dch', 'lch', 'lsh'])
    k_head = p_head.get('k', 0)
    e_head = p_head.get('e', 0)

    # e-depth distribution
    e0 = p_edepth.get(0, 0)
    e1 = p_edepth.get(1, 0)
    e2 = p_edepth.get(2, 0)

    # Notable markers
    dar_n = words.count('dar')
    dal_n = words.count('dal')
    chekar_n = sum(1 for w in words if w == 'chekar')
    qokedy_n = words.count('qokedy')
    qokeedy_n = words.count('qokeedy')
    dain_n = words.count('dain')
    ol_n = words.count('ol')
    mk = []
    if dar_n: mk.append(f'dar x{dar_n}')
    if dal_n: mk.append(f'dal x{dal_n}')
    if chekar_n: mk.append(f'CHEKAR x{chekar_n}')
    if qokedy_n: mk.append(f'qokedy x{qokedy_n}')
    if qokeedy_n: mk.append(f'qokeedy x{qokeedy_n}')
    if dain_n: mk.append(f'dain x{dain_n}')
    if ol_n: mk.append(f'ol x{ol_n}')

    print(f"\n  P{pidx} (L{p['lines'][0]}-L{p['lines'][-1]}, {n}T)")
    print(f"    THERMAL pfx: {thermal_pfx}/{n} ({100*thermal_pfx/n:.0f}%)  "
          f"MONITOR pfx: {monitor_pfx}/{n} ({100*monitor_pfx/n:.0f}%)")
    print(f"    k-HEAD: {k_head}/{n} ({100*k_head/n:.0f}%)  "
          f"e-HEAD: {e_head}/{n} ({100*e_head/n:.0f}%)")
    print(f"    e-depth: e0={e0} e1={e1} e2={e2}  "
          f"[gentle ratio: {100*e2/(e1+e2) if e1+e2 > 0 else 0:.0f}%]")
    if mk:
        print(f"    MARKERS: {', '.join(mk)}")


# ═══ RECIPE ALIGNMENT ═══
print("\n\n" + "=" * 110)
print("RECIPE ALIGNMENT: f75r vs Ch19 (with corrected e-depth)")
print("=" * 110)

recipe_map = {
    1: ("ASSESS & RECEIVE",
        "Take the aqua vitae. Check what you have before starting.",
        "Monitor-heavy, e-HEAD dominant. Checking starting material."),
    2: ("FIRST HEAT + ADD",
        "Begin heating. Add first material.",
        "Single line, thermal spike. dar x1."),
    3: ("DISTILLATION CYCLE",
        "First full distillation with active test-heat interleave.",
        "Balanced thermal/monitoring. Classic control loop."),
    4: ("ENUMERATED REPETITION",
        "Repeat the heat cycle. The 4x qokedy run.",
        "UNIQUE in all Currier B. Thermal dominant."),
    5: ("FERMENTATION / OBSERVATION",
        "Set in balneum mariae. Watch and wait.",
        "Most monitoring-dominant. Passive observation."),
    6: ("CYCLE RESTART",
        "Return pure substance. Restart the cycle.",
        "Iteration markers: dain x2, ol x2. Material return."),
    7: ("QUALITY GATE",
        "Examine the product. No heat.",
        "ZERO k-HEAD. Pure observation checkpoint."),
    8: ("RE-DISTILLATION",
        "Active distillation with heavy iteration.",
        "Balanced thermal/monitoring. dain x3."),
    9: ("MAIN 9x LOOP",
        "The heart: add honey+wax, heat gently, check quality, repeat.",
        "MASSIVE (120T). dar x7, double-dar, chekar, kee/ke alternation."),
}

for pidx in range(1, len(paragraphs) + 1):
    p = paragraphs[pidx - 1]
    ptokens = p['tokens']
    n = len(ptokens)
    label, recipe, evidence = recipe_map.get(pidx, ("?", "?", "?"))

    # Compute e-depth gentle ratio for this paragraph
    e1_ct = sum(1 for t in ptokens if morph.atomize(t.word).e_depth == 1)
    e2_ct = sum(1 for t in ptokens if morph.atomize(t.word).e_depth >= 2)
    gentle_ratio = 100 * e2_ct / (e1_ct + e2_ct) if (e1_ct + e2_ct) > 0 else 0

    print(f"\n  P{pidx} ({n}T, L{p['lines'][0]}-L{p['lines'][-1]})")
    print(f"  Recipe: {recipe}")
    print(f"  Label:  {label}")
    print(f"  e-depth gentle ratio: {gentle_ratio:.0f}% ({e2_ct} gentle / {e1_ct+e2_ct} thermal)")


# ═══ e-DEPTH TRAJECTORY ═══
print("\n\n" + "=" * 110)
print("e-DEPTH TRAJECTORY ACROSS FOLIO")
print("Does gentle heat (e2+) correlate with balneum mariae phases?")
print("=" * 110)

for li in lines:
    lt = [t for t in tokens if t.line == li]
    e1_n = sum(1 for t in lt if morph.atomize(t.word).e_depth == 1)
    e2_n = sum(1 for t in lt if morph.atomize(t.word).e_depth >= 2)
    if e1_n + e2_n == 0:
        continue
    pidx = next(p['idx'] for p in paragraphs if li in p['lines'])
    bar_e1 = '|' * e1_n
    bar_e2 = '#' * e2_n
    phase = recipe_map.get(pidx, ("?",))[0]
    print(f"  L{li:>2s} P{pidx} [{phase:22s}]  e1={e1_n} {bar_e1}  e2={e2_n} {bar_e2}")


# ═══ L37-38 THERMAL BLOCK (corrected) ═══
print("\n\n" + "=" * 110)
print("L37-38: PURE THERMAL BLOCK (corrected e-depth)")
print("=" * 110)

for li in ['37', '38']:
    lt = [t for t in tokens if t.line == li]
    print(f"\n  L{li}: {' '.join(t.word for t in lt)}")
    for t in lt:
        a = morph.atomize(t.word)
        pre_label = PREFIX_LABEL.get(a.prefix, a.prefix or 'BARE')
        atoms_raw = ''.join(c for c, _, _ in a.atoms)
        e_label = {0: '', 1: 'STEADY', 2: 'GENTLE', 3: 'VERY GENTLE'}.get(a.e_depth, '')
        print(f"    {t.word:16s}  {pre_label:12s}  {a.gloss:35s}  {e_label}")


# ═══ DOUBLE-DAR LINES (corrected) ═══
print("\n\n" + "=" * 110)
print("L35-36: DOUBLE-DAR LINES (honey + wax)")
print("=" * 110)

for li in ['35', '36']:
    lt = [t for t in tokens if t.line == li]
    print(f"\n  L{li}: {' '.join(t.word for t in lt)}")
    for t in lt:
        a = morph.atomize(t.word)
        pre_label = PREFIX_LABEL.get(a.prefix, a.prefix or 'BARE')
        e_label = f"  [e{a.e_depth}]" if a.e_depth > 0 else ""
        print(f"    {t.word:16s}  {pre_label:12s}  {a.gloss}{e_label}")


# ═══ AGGREGATE STATS ═══
print("\n\n" + "=" * 110)
print("AGGREGATE STATISTICS")
print("=" * 110)

print(f"\n  e-depth distribution:")
for ed, ct in sorted(all_e_depths.items()):
    pct = 100 * ct / len(tokens)
    print(f"    e{ed}: {ct:4d} ({pct:5.1f}%)")

print(f"\n  PREFIX (top 10):")
for pre, ct in all_prefixes.most_common(10):
    pct = 100 * ct / len(tokens)
    label = PREFIX_LABEL.get(pre, pre)
    print(f"    {pre:8s} ({label:12s}): {ct:3d} ({pct:5.1f}%)")

print(f"\n  HEAD atoms:")
for h, ct in all_heads.most_common():
    pct = 100 * ct / len(tokens)
    g = ATOM_GLOSSES.get(h.lstrip('~'), h)
    hl = ' (headless)' if h.startswith('~') else ''
    print(f"    {h:4s} ({g:10s}): {ct:3d} ({pct:5.1f}%){hl}")

print(f"\n  Coverage: 100% — {len(tokens)} tokens decoded")
print("=" * 110)
