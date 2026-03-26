"""
Exploratory: Crib-based decoding of f75r using Ch19 (aqua vitae) recipe.

Recipe (Ch19 summary):
  1. Take aqua vitae, separate moisture through distillation
  2. Substance is gold-like (vegetable brazilwood)
  3. Add 1/3 pure honey with wax
  4. Ferment in balneum mariae (water bath)
  5. Repeat distillation+fermentation 9x, returning pure substance each 2nd distillation

Approach:
  - Map recipe operational concepts to paragraph-level kernel profiles
  - Identify f75r-unique vocabulary (tokens appearing nowhere else)
  - Check whether unique tokens cluster at recipe-specific paragraphs
  - Analyze the iteration markers (dain/ol cycling) in the 9x loop body
  - Look for material-input tokens (dar = setup input) distribution
"""

import sys, json, os
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
from scripts.voynich import Transcript, Morphology

tx = Transcript()
morph = Morphology()

# ─── 1. Get f75r tokens (H-track, text only) ───
f75r_tokens = [t for t in tx.all()
               if t.folio == 'f75r'
               and t.word.strip()
               and not t.is_label]

print(f"f75r text tokens: {len(f75r_tokens)}")

# ─── 2. Build paragraph structure ───
# Paragraph boundaries from gallows-initial lines
gallows_lines = []
for t in f75r_tokens:
    if t.line not in [l for l, _ in gallows_lines]:
        m = morph.extract(t.word)
        first_char = t.word[0] if t.word else ''
        # Check if line starts with gallows (first token has gallows-class prefix)
        if first_char in ('t', 'k', 'p', 'f') and t.word not in ('the',):
            # Verify it's actually paragraph-initial by checking position
            line_tokens = [x for x in f75r_tokens if x.line == t.line]
            if line_tokens and line_tokens[0].word == t.word:
                gallows_lines.append((t.line, first_char))

# Build paragraphs
all_lines = sorted(set(t.line for t in f75r_tokens), key=lambda x: int(x) if x.isdigit() else 0)
para_starts = [l for l, _ in gallows_lines]

paragraphs = []
for i, start_line in enumerate(para_starts):
    if i + 1 < len(para_starts):
        end_line = para_starts[i + 1]
        lines = [l for l in all_lines if int(l) >= int(start_line) and int(l) < int(end_line)]
    else:
        lines = [l for l in all_lines if int(l) >= int(start_line)]

    tokens = [t for t in f75r_tokens if t.line in lines]
    gallows_char = [g for l, g in gallows_lines if l == start_line][0]
    paragraphs.append({
        'lines': lines,
        'tokens': tokens,
        'gallows': gallows_char,
        'n_tokens': len(tokens)
    })

print(f"\nParagraphs: {len(paragraphs)}")
for i, p in enumerate(paragraphs):
    print(f"  P{i+1}: L{p['lines'][0]}-L{p['lines'][-1]} ({p['n_tokens']}T, {p['gallows']}-gallows)")

# ─── 3. Per-paragraph kernel and PREFIX profiles ───
print("\n" + "="*80)
print("PARAGRAPH OPERATIONAL PROFILES")
print("="*80)

PREFIX_GLOSSES = {
    'qo': 'HEAT-SRC',
    'ch': 'TEST',
    'sh': 'MONITOR',
    'da': 'SETUP',
    'sa': 'SCAFFOLD',
    'ok': 'VESSEL-TEMP',
    'ot': 'OPS-VERIFY',
    'ol': 'CONTINUE',
    'so': 'SCAFFOLD-O',
    'po': 'PRE-WORK',
    'ke': 'HEAT-BURST',
    'pch': 'STAGE-TEST',
    'tch': 'XFER-TEST',
    'dch': 'MARK-TEST',
    'lch': 'HOLD-TEST',
    'lk': 'HOLD-HEAT',
    'lsh': 'HOLD-MONITOR',
    'ar': 'PURE-SAFE',
    'ko': 'HEAT-WORK',
}

for i, p in enumerate(paragraphs):
    print(f"\n--- P{i+1} (L{p['lines'][0]}-L{p['lines'][-1]}, {p['gallows']}-gallows, {p['n_tokens']}T) ---")

    # Kernel counts
    k_count = h_count = e_count = other_count = 0
    prefix_counts = Counter()
    middle_counts = Counter()
    suffix_counts = Counter()

    for t in p['tokens']:
        m = morph.extract(t.word)
        mid = m.middle or ''

        # Kernel classification
        if mid.startswith('k'):
            k_count += 1
        elif mid.startswith('h'):
            h_count += 1
        elif mid.startswith('e'):
            e_count += 1
        else:
            other_count += 1

        if m.prefix:
            prefix_counts[m.prefix] += 1
        if m.middle:
            middle_counts[m.middle] += 1
        if m.suffix:
            suffix_counts[m.suffix] += 1

    total = k_count + h_count + e_count + other_count
    print(f"  Kernel: k={k_count}({100*k_count/total:.0f}%) h={h_count}({100*h_count/total:.0f}%) e={e_count}({100*e_count/total:.0f}%) other={other_count}")

    # Top prefixes
    top_pre = prefix_counts.most_common(5)
    pre_str = ', '.join(f"{pre}:{ct}" for pre, ct in top_pre)
    print(f"  Top PREFIX: {pre_str}")

    # Top middles
    top_mid = middle_counts.most_common(5)
    mid_str = ', '.join(f"{mid}:{ct}" for mid, ct in top_mid)
    print(f"  Top MIDDLE: {mid_str}")

# ─── 4. f75r-unique vocabulary ───
print("\n" + "="*80)
print("f75r-UNIQUE VOCABULARY")
print("="*80)

# Get ALL Currier B tokens (H-track, text only)
all_b_tokens = [t for t in tx.currier_b()
                if t.word.strip()]

# Build per-folio word sets
folio_words = defaultdict(set)
for t in all_b_tokens:
    folio_words[t.folio].add(t.word)

f75r_words = folio_words['f75r']
other_words = set()
for folio, words in folio_words.items():
    if folio != 'f75r':
        other_words.update(words)

unique_to_f75r = f75r_words - other_words
shared_words = f75r_words & other_words

print(f"\nf75r vocabulary: {len(f75r_words)} unique words")
print(f"  Shared with other B folios: {len(shared_words)}")
print(f"  UNIQUE to f75r: {len(unique_to_f75r)}")

# Show unique words with their morphology and paragraph location
if unique_to_f75r:
    print(f"\n  Unique words:")
    for w in sorted(unique_to_f75r):
        m = morph.extract(w)
        # Find which paragraph(s) this word appears in
        paras = set()
        for pi, p in enumerate(paragraphs):
            if any(t.word == w for t in p['tokens']):
                paras.add(f"P{pi+1}")

        lines = set()
        for t in f75r_tokens:
            if t.word == w:
                lines.add(t.line)

        art = m.articulator or '-'
        pre = m.prefix or '-'
        mid = m.middle or '-'
        suf = m.suffix or '-'
        print(f"    {w:20s}  ART={art:3s} PRE={pre:5s} MID={mid:8s} SUF={suf:5s}  lines={','.join(sorted(lines, key=lambda x: int(x) if x.isdigit() else 0))}  paras={','.join(sorted(paras))}")

# ─── 5. Iteration marker analysis (dain/ol cycling) ───
print("\n" + "="*80)
print("ITERATION MARKERS: dain + ol sequences")
print("="*80)

for li in all_lines:
    line_tokens = [t for t in f75r_tokens if t.line == li]
    words = [t.word for t in line_tokens]

    # Check for iteration markers
    has_dain = 'dain' in words
    has_ol = 'ol' in words
    dain_count = words.count('dain')
    ol_count = words.count('ol')

    if has_dain or has_ol:
        # Which paragraph?
        para_num = None
        for pi, p in enumerate(paragraphs):
            if li in p['lines']:
                para_num = pi + 1
                break

        markers = []
        if has_dain:
            markers.append(f"dain×{dain_count}")
        if has_ol:
            markers.append(f"ol×{ol_count}")

        print(f"  L{li:>2s} (P{para_num}): {' '.join(words)}")
        print(f"         markers: {', '.join(markers)}")

# ─── 6. Material input markers (dar = setup+input) ───
print("\n" + "="*80)
print("MATERIAL INPUT MARKERS: dar (setup input)")
print("="*80)

for li in all_lines:
    line_tokens = [t for t in f75r_tokens if t.line == li]
    words = [t.word for t in line_tokens]

    dar_count = words.count('dar')
    if dar_count > 0:
        para_num = None
        for pi, p in enumerate(paragraphs):
            if li in p['lines']:
                para_num = pi + 1
                break

        print(f"  L{li:>2s} (P{para_num}): dar×{dar_count}  context: {' '.join(words)}")

# ─── 7. qokeedy (balneum mariae = sustained gentle heat) distribution ───
print("\n" + "="*80)
print("BALNEUM MARIAE MARKERS: qokeedy (sustained modulated heat)")
print("="*80)

for li in all_lines:
    line_tokens = [t for t in f75r_tokens if t.line == li]
    words = [t.word for t in line_tokens]

    keedy_tokens = [w for w in words if 'keedy' in w or 'keed' in w]
    if keedy_tokens:
        para_num = None
        for pi, p in enumerate(paragraphs):
            if li in p['lines']:
                para_num = pi + 1
                break

        print(f"  L{li:>2s} (P{para_num}): {', '.join(keedy_tokens)}  context: {' '.join(words)}")

# ─── 8. ot-PREFIX distribution (operational verification) ───
print("\n" + "="*80)
print("OT-PREFIX (operational verification) DISTRIBUTION")
print("="*80)

ot_by_para = Counter()
for pi, p in enumerate(paragraphs):
    for t in p['tokens']:
        m = morph.extract(t.word)
        if m.prefix == 'ot' or (t.word.startswith('ot') and len(t.word) > 2):
            ot_by_para[pi+1] += 1

for pi in range(1, len(paragraphs)+1):
    total = paragraphs[pi-1]['n_tokens']
    ot = ot_by_para.get(pi, 0)
    pct = 100 * ot / total if total > 0 else 0
    bar = '#' * int(pct * 2)
    print(f"  P{pi}: {ot:2d}/{total:3d} ({pct:5.1f}%) {bar}")

# ─── 9. Recipe alignment scoring ───
print("\n" + "="*80)
print("RECIPE STEP -> PARAGRAPH ALIGNMENT")
print("="*80)

recipe_steps = [
    ("Take aqua vitae, separate moisture", "DISTILL_SETUP",
     "Expect: high k, moderate h, apparatus initialization"),
    ("Add 1/3 pure honey with wax", "MATERIAL_ADD",
     "Expect: dar (setup input) tokens, material references"),
    ("Ferment in balneum mariae", "FERMENT",
     "Expect: high h (monitoring), qokeedy (sustained heat), slow process"),
    ("Return pure substance (quality check)", "QUALITY_CHECK",
     "Expect: very high h, low k, observation-only"),
    ("9x distillation+fermentation loop", "ITERATION_LOOP",
     "Expect: dain/ol cycling, repeated token patterns, temperature profiles"),
]

for step_name, code, expect in recipe_steps:
    print(f"\n  [{code}] {step_name}")
    print(f"    {expect}")

    # Score each paragraph
    scores = []
    for pi, p in enumerate(paragraphs):
        score = 0
        reasons = []

        words = [t.word for t in p['tokens']]
        n = p['n_tokens']

        # Kernel profile
        k_count = sum(1 for t in p['tokens'] if (morph.extract(t.word).middle or '').startswith('k'))
        h_count = sum(1 for t in p['tokens'] if (morph.extract(t.word).middle or '').startswith('h'))
        e_count = sum(1 for t in p['tokens'] if (morph.extract(t.word).middle or '').startswith('e'))
        k_pct = 100 * k_count / n if n else 0
        h_pct = 100 * h_count / n if n else 0

        if code == 'DISTILL_SETUP':
            if p['gallows'] == 'k':
                score += 3
                reasons.append("K-gallows (heat init)")
            if k_pct > 40:
                score += 2
                reasons.append(f"high k ({k_pct:.0f}%)")
            if pi == 0:
                score += 2
                reasons.append("first paragraph")

        elif code == 'MATERIAL_ADD':
            dar_count = words.count('dar')
            if dar_count > 0:
                score += 2 * dar_count
                reasons.append(f"dar×{dar_count} (setup input)")
            sal_count = sum(1 for w in words if w.startswith('sal') or w.startswith('sol'))
            if sal_count > 0:
                score += 1
                reasons.append(f"sal/sol×{sal_count}")

        elif code == 'FERMENT':
            if h_pct > 10:
                score += 3
                reasons.append(f"high monitoring ({h_pct:.0f}%)")
            keedy_count = sum(1 for w in words if 'keedy' in w)
            if keedy_count > 0:
                score += 2
                reasons.append(f"keedy×{keedy_count} (sustained heat)")

        elif code == 'QUALITY_CHECK':
            if h_pct > 30:
                score += 4
                reasons.append(f"very high monitoring ({h_pct:.0f}%)")
            if k_pct < 10:
                score += 3
                reasons.append(f"near-zero heat ({k_pct:.0f}%)")
            ot_count = sum(1 for t in p['tokens'] if morph.extract(t.word).prefix == 'ot')
            if ot_count > 0:
                score += 2
                reasons.append(f"ot×{ot_count} (operational verification)")

        elif code == 'ITERATION_LOOP':
            dain_count = sum(1 for w in words if w == 'dain')
            ol_count = sum(1 for w in words if w == 'ol')
            if dain_count + ol_count > 3:
                score += 3
                reasons.append(f"dain/ol cycling ({dain_count}+{ol_count})")
            if n > 80:
                score += 2
                reasons.append(f"large paragraph ({n}T)")
            # Temperature profile
            keedy_count = sum(1 for w in words if 'keedy' in w or 'kedy' in w)
            if keedy_count > 5:
                score += 2
                reasons.append(f"heat tokens×{keedy_count}")

        if score > 0:
            scores.append((score, pi+1, reasons))

    scores.sort(reverse=True)
    for score, pnum, reasons in scores[:3]:
        print(f"    -> P{pnum} (score={score}): {'; '.join(reasons)}")

# ─── 10. Token-level: what does each line of the 4x qokedy paragraph say? ───
print("\n" + "="*80)
print("DETAILED DECODE: P4 (Lines 13-16) — The Repetition Paragraph")
print("="*80)

p4 = paragraphs[3]  # 0-indexed
for li in p4['lines']:
    line_tokens = [t for t in f75r_tokens if t.line == li]
    print(f"\n  Line {li}:")

    for t in line_tokens:
        m = morph.extract(t.word)
        pre = m.prefix or '(bare)'
        mid = m.middle or '?'
        suf = m.suffix or '(none)'

        # Build operational gloss
        pre_gloss = PREFIX_GLOSSES.get(pre, pre)

        # Middle gloss from atoms
        mid_gloss_parts = []
        for c in mid:
            atom_map = {
                'k': 'heat', 'e': 'cool', 'h': 'watch', 't': 'transfer',
                'a': 'yield', 'o': 'work', 'i': 'iterate', 'd': 'mark',
                'c': 'adjust', 'p': 'pause', 'f': 'flag', 's': 'sequence',
                'r': 'input', 'l': 'frame', 'n': 'bind', 'm': 'close',
                'y': 'done'
            }
            mid_gloss_parts.append(atom_map.get(c, c))
        mid_gloss = '-'.join(mid_gloss_parts)

        suf_gloss_map = {
            'edy': 'thorough', 'ain': 'settle', 'ar': 'close', 'y': 'done',
            'dy': 'close', 'am': 'finalize', 'ey': 'set', 'hy': 'verify',
            'ly': 'settled', 'al': 'complete', 'or': 'portion',
            'eedy': 'extended-thorough', 'aiin': 'sustained-cycle',
        }
        suf_gloss = suf_gloss_map.get(suf, suf)

        print(f"    {t.word:18s}  [{pre_gloss:12s}] {mid_gloss:20s} -> {suf_gloss}")

# ─── 11. Token-level: P7 (the pure observation paragraph) ───
print("\n" + "="*80)
print("DETAILED DECODE: P7 (Line 27) — The Quality Check")
print("="*80)

p7 = paragraphs[6]
for li in p7['lines']:
    line_tokens = [t for t in f75r_tokens if t.line == li]
    print(f"\n  Line {li}:")

    for t in line_tokens:
        m = morph.extract(t.word)
        pre = m.prefix or '(bare)'
        mid = m.middle or '?'
        suf = m.suffix or '(none)'

        pre_gloss = PREFIX_GLOSSES.get(pre, pre)

        mid_gloss_parts = []
        for c in mid:
            atom_map = {
                'k': 'heat', 'e': 'cool', 'h': 'watch', 't': 'transfer',
                'a': 'yield', 'o': 'work', 'i': 'iterate', 'd': 'mark',
                'c': 'adjust', 'p': 'pause', 'f': 'flag', 's': 'sequence',
                'r': 'input', 'l': 'frame', 'n': 'bind', 'm': 'close',
                'y': 'done'
            }
            mid_gloss_parts.append(atom_map.get(c, c))
        mid_gloss = '-'.join(mid_gloss_parts)

        suf_gloss_map = {
            'edy': 'thorough', 'ain': 'settle', 'ar': 'close', 'y': 'done',
            'dy': 'close', 'am': 'finalize', 'ey': 'set', 'hy': 'verify',
            'ly': 'settled', 'al': 'complete', 'or': 'portion',
            'eedy': 'extended-thorough', 'ol': 'hold',
        }
        suf_gloss = suf_gloss_map.get(suf, suf)

        print(f"    {t.word:18s}  [{pre_gloss:12s}] {mid_gloss:20s} -> {suf_gloss}")

# ─── 12. Token-level: P9 Lines 37-38 (the temperature profile) ───
print("\n" + "="*80)
print("DETAILED DECODE: P9 Lines 37-38 — The Balneum Mariae Temperature Profile")
print("="*80)

for li in ['37', '38']:
    line_tokens = [t for t in f75r_tokens if t.line == li]
    print(f"\n  Line {li}:")

    for t in line_tokens:
        m = morph.extract(t.word)
        pre = m.prefix or '(bare)'
        mid = m.middle or '?'
        suf = m.suffix or '(none)'

        pre_gloss = PREFIX_GLOSSES.get(pre, pre)

        # e-depth annotation
        e_depth_str = ''
        if mid == 'k':
            e_depth_str = ' <- FULL HEAT (e-depth=0)'
        elif mid == 'ke':
            e_depth_str = ' <- MODULATED (e-depth=1)'
        elif mid == 'kee':
            e_depth_str = ' <- GENTLE (e-depth=2)'

        mid_gloss_parts = []
        for c in mid:
            atom_map = {
                'k': 'heat', 'e': 'cool', 'h': 'watch', 't': 'transfer',
                'a': 'yield', 'o': 'work', 'i': 'iterate', 'd': 'mark',
                'c': 'adjust', 'p': 'pause', 'f': 'flag', 's': 'sequence',
                'r': 'input', 'l': 'frame', 'n': 'bind', 'm': 'close',
                'y': 'done'
            }
            mid_gloss_parts.append(atom_map.get(c, c))
        mid_gloss = '-'.join(mid_gloss_parts)

        suf_gloss_map = {
            'edy': 'thorough', 'ain': 'settle', 'ar': 'close', 'y': 'done',
            'dy': 'close', 'am': 'finalize', 'ey': 'set', 'hy': 'verify',
            'ly': 'settled', 'al': 'complete', 'or': 'portion',
        }
        suf_gloss = suf_gloss_map.get(suf, suf)

        print(f"    {t.word:18s}  [{pre_gloss:12s}] {mid_gloss:20s} -> {suf_gloss}{e_depth_str}")

# ─── 13. Cross-folio: How unique is f75r's operational vocabulary? ───
print("\n" + "="*80)
print("CROSS-FOLIO VOCABULARY COMPARISON")
print("="*80)

# Count qokeedy across all B folios
qokeedy_by_folio = Counter()
qokedy_by_folio = Counter()
for t in all_b_tokens:
    if t.word == 'qokeedy':
        qokeedy_by_folio[t.folio] += 1
    if t.word == 'qokedy':
        qokedy_by_folio[t.folio] += 1

print(f"\nqokeedy (sustained modulated heat) — top folios:")
for folio, count in qokeedy_by_folio.most_common(10):
    marker = " <- f75r" if folio == 'f75r' else ""
    print(f"  {folio}: {count}{marker}")

print(f"\nqokedy (full heat batch) — top folios:")
for folio, count in qokedy_by_folio.most_common(10):
    marker = " <- f75r" if folio == 'f75r' else ""
    print(f"  {folio}: {count}{marker}")

# ─── 14. f75r operational sequence summary ───
print("\n" + "="*80)
print("f75r OPERATIONAL SEQUENCE (paragraph-by-paragraph)")
print("="*80)

recipe_map = {
    1: "SETUP — Take aqua vitae, initialize apparatus",
    2: "COMMAND — Single distillation instruction (separate moisture)",
    3: "DISTILL — Primary distillation sequence",
    4: "REPEAT — Sustained heating loop (4× qokedy enumeration)",
    5: "FERMENT — Balneum mariae fermentation (highest monitoring)",
    6: "PROCESS — Post-fermentation heating (honey+wax processed?)",
    7: "CHECK — Quality observation (ZERO heat, pure monitoring)",
    8: "TRANSFER — Re-distillation (T-gallows = drive off volatile)",
    9: "LOOP — Main 9× iteration cycle (temperature profiles, cycling)",
}

for pi in range(1, len(paragraphs)+1):
    p = paragraphs[pi-1]
    recipe_step = recipe_map.get(pi, "?")

    # Compact kernel
    n = p['n_tokens']
    k_ct = sum(1 for t in p['tokens'] if (morph.extract(t.word).middle or '').startswith('k'))
    h_ct = sum(1 for t in p['tokens'] if (morph.extract(t.word).middle or '').startswith('h'))
    e_ct = sum(1 for t in p['tokens'] if (morph.extract(t.word).middle or '').startswith('e'))

    print(f"\n  P{pi} ({p['gallows']}-gallows, {n}T, L{p['lines'][0]}-L{p['lines'][-1]})")
    print(f"    Kernel: k={100*k_ct/n:.0f}% h={100*h_ct/n:.0f}% e={100*e_ct/n:.0f}%")
    print(f"    -> {recipe_step}")

print("\n" + "="*80)
print("DONE")
print("="*80)
