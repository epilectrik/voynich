"""
Full atom-level decode of f75r vs PL Ch19 (Aqua vitae composite).

Recipe (Ch19):
  1. Take aqua vitae, separate moisture through distillation
  2. Substance is gold-like (vegetable brazilwood)
  3. Add 1/3 pure honey with wax
  4. Ferment in balneum mariae (water bath)
  5. Repeat distillation+fermentation 9x, returning pure substance each 2nd distillation

Atom glosses (C1195, C1394):
  HEAD: k=heat, e=cool, a=into, o=arrange, t=transfer
  MOD:  p=pause, f=flag, i=iterate, c=loop, d=seal, s=stage
  TERM: y=end, n=bind, m=final, h=watch, l=state, r=respond
  FREE: k,t (dual role)

PREFIX domains (C929, C1218-C1219, C1538):
  qo=thermal, ch=test(active), sh=monitor(passive), ok=vessel,
  ot=ops-verify, da=setup, sa=scaffold, ol=continue, or=flow,
  po=pre-work, so=scaffold-arrange, ke=heat-burst, ko=heat-work,
  pch=stage-test, tch=transfer-test, dch=mark-test, lch=hold-test,
  ka=heat-yield, ta=transfer-yield, lk=hold-heat, lsh=hold-monitor,
  ct=control, ar=release
"""

import sys, os, io
from collections import Counter, defaultdict

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))))
from scripts.voynich import Transcript, Morphology

tx = Transcript()
morph = Morphology()

# ═══ ATOM GLOSSES ═══
ATOM = {
    'k': 'heat', 'e': 'cool', 'a': 'into', 'o': 'arrange', 't': 'transfer',
    'p': 'pause', 'f': 'flag', 'i': 'iterate', 'c': 'loop', 'd': 'seal',
    's': 'stage', 'y': 'end', 'n': 'bind', 'm': 'final', 'h': 'watch',
    'l': 'state', 'r': 'respond', 'g': 'complete', 'x': 'diagram',
    'q': 'thermal-activate',
}

HEADS = set('aeokt')
TERMS = set('ynmhlr')
MODS  = set('pficds')

PREFIX_GLOSS = {
    'qo': 'THERMAL',    'ch': 'TEST',       'sh': 'MONITOR',
    'ok': 'VESSEL',     'ot': 'OPS-CHK',    'da': 'SETUP',
    'sa': 'SCAFFOLD',   'ol': 'CONTINUE',   'or': 'FLOW',
    'po': 'PRE-WORK',   'so': 'SCAFF-ARR',  'ke': 'HEAT-BURST',
    'ko': 'HEAT-WORK',  'ka': 'HEAT-YIELD', 'ta': 'XFER-YIELD',
    'pch': 'STAGE-TEST','tch': 'XFER-TEST', 'dch': 'MARK-TEST',
    'lch': 'HOLD-TEST', 'lk': 'HOLD-HEAT',  'lsh': 'HOLD-MON',
    'ct': 'CONTROL',    'te': 'XFER-COOL',  'de': 'MARK-COOL',
    'se': 'SCAFF-COOL', 'pe': 'START-COOL',
}

def atomize_middle(mid):
    """Decompose MIDDLE into HEAD + MOD* + TERM with glosses."""
    if not mid:
        return '(?)'

    chars = list(mid)
    parts = []

    # Classify each character positionally
    for idx, c in enumerate(chars):
        g = ATOM.get(c, c)

        # Role annotation
        if idx == 0 and c in HEADS:
            role = 'H'
        elif idx == len(chars) - 1 and c in TERMS:
            role = 'T'
        elif idx == 0 and c not in HEADS:
            role = 'pH'  # pseudo-head (headless)
        elif c in MODS:
            role = 'M'
        elif c in HEADS and idx > 0:
            # HEAD atom in non-initial = modifier function
            role = 'M'
        elif c in TERMS and idx < len(chars) - 1:
            role = 'M'
        else:
            role = '?'

        parts.append((c, g, role))

    return parts

def gloss_token(word, m):
    """Produce a compact operational gloss from morphological decomposition."""
    art = m.articulator
    pre = m.prefix
    mid = m.middle
    suf = m.suffix

    # PREFIX domain
    pre_g = PREFIX_GLOSS.get(pre, pre.upper() if pre else 'BARE')

    # MIDDLE atoms
    if mid:
        atoms = atomize_middle(mid)
        mid_parts = []
        for c, g, role in atoms:
            mid_parts.append(g)
        mid_g = '.'.join(mid_parts)
    else:
        mid_g = '(?)'

    # SUFFIX atoms
    if suf:
        suf_parts = []
        for c in suf:
            suf_parts.append(ATOM.get(c, c))
        suf_g = '-' + '.'.join(suf_parts)
    else:
        suf_g = ''

    # HT marker
    ht = '[HT]' if art else ''

    return f"{ht}{pre_g}: {mid_g}{suf_g}"

# ═══ GET f75r TOKENS ═══
tokens = [t for t in tx.all()
          if t.folio == 'f75r' and t.word.strip() and not t.is_label]

lines = sorted(set(t.line for t in tokens), key=lambda x: int(x) if x.isdigit() else 0)
print(f"f75r: {len(tokens)} tokens, {len(lines)} lines")

# ═══ PARAGRAPH DETECTION ═══
# First token of each line — gallows initial = paragraph boundary
para_boundaries = []
for li in lines:
    lt = [t for t in tokens if t.line == li]
    if lt:
        first = lt[0].word
        if first and first[0] in 'tkpf' and len(first) > 1:
            para_boundaries.append(li)

# Build paragraph ranges
paragraphs = []
for i, start in enumerate(para_boundaries):
    if i + 1 < len(para_boundaries):
        end_idx = lines.index(para_boundaries[i + 1])
        p_lines = lines[lines.index(start):end_idx]
    else:
        p_lines = lines[lines.index(start):]
    p_tokens = [t for t in tokens if t.line in p_lines]
    paragraphs.append({
        'idx': i + 1,
        'lines': p_lines,
        'tokens': p_tokens,
        'first_word': p_tokens[0].word if p_tokens else '?',
    })

print(f"Paragraphs: {len(paragraphs)}")
for p in paragraphs:
    print(f"  P{p['idx']}: L{p['lines'][0]}-L{p['lines'][-1]} "
          f"({len(p['tokens'])}T, opens with '{p['first_word']}')")

# ═══ FULL LINE-BY-LINE DECODE ═══
print("\n" + "=" * 100)
print("FULL ATOM-LEVEL DECODE: f75r")
print("=" * 100)

# Track statistics
prefix_counts = Counter()
head_counts = Counter()
mod_counts = Counter()
term_counts = Counter()
suffix_atom_counts = Counter()

current_para = 0

for li in lines:
    # Check paragraph boundary
    while current_para < len(paragraphs) - 1 and li >= paragraphs[current_para + 1]['lines'][0]:
        current_para += 1

    # Paragraph header
    if li in para_boundaries:
        pidx = [p['idx'] for p in paragraphs if p['lines'][0] == li][0]
        n_tok = len([t for t in tokens if t.line in paragraphs[pidx-1]['lines']])
        print(f"\n{'─' * 100}")
        print(f"  ┌─ PARAGRAPH {pidx} (L{paragraphs[pidx-1]['lines'][0]}-"
              f"L{paragraphs[pidx-1]['lines'][-1]}, {n_tok}T)")
        print(f"{'─' * 100}")

    lt = [t for t in tokens if t.line == li]
    words = ' '.join(t.word for t in lt)
    print(f"\n  L{li:>2s}│ {words}")
    print(f"     │ {'─' * 90}")

    for t in lt:
        m = morph.extract(t.word)
        gloss = gloss_token(t.word, m)

        # Detailed atom breakdown
        mid = m.middle or ''
        atoms = atomize_middle(mid) if mid else []

        # Collect stats
        if m.prefix:
            prefix_counts[m.prefix] += 1
        for c, g, role in atoms:
            if role == 'H':
                head_counts[c] += 1
            elif role == 'pH':
                head_counts[f'~{c}'] += 1
            elif role == 'T':
                term_counts[c] += 1
            elif role == 'M':
                mod_counts[c] += 1
        if m.suffix:
            for c in m.suffix:
                suffix_atom_counts[c] += 1

        # Build atom string for display
        atom_str = ''
        if atoms:
            atom_str = '  [' + ' '.join(f'{c}={g}' for c, g, role in atoms) + ']'

        art_str = f"({m.articulator}+)" if m.articulator else ""
        pre_str = m.prefix or "(bare)"
        suf_str = f" -{m.suffix}" if m.suffix else ""

        print(f"     │  {t.word:16s}  {art_str}{pre_str:6s}+{mid:8s}{suf_str:6s}  → {gloss}")

# ═══ PARAGRAPH-LEVEL PROFILES ═══
print("\n" + "=" * 100)
print("PARAGRAPH OPERATIONAL PROFILES")
print("=" * 100)

for p in paragraphs:
    pidx = p['idx']
    ptokens = p['tokens']
    n = len(ptokens)

    # PREFIX distribution
    p_pre = Counter()
    p_head = Counter()
    p_mid_atoms = Counter()

    for t in ptokens:
        m = morph.extract(t.word)
        if m.prefix:
            p_pre[m.prefix] += 1
        mid = m.middle or ''
        if mid:
            atoms = atomize_middle(mid)
            for c, g, role in atoms:
                if role == 'H':
                    p_head[c] += 1
                elif role == 'pH':
                    p_head[f'~{c}'] += 1
                p_mid_atoms[c] += 1

    # Thermal vs monitoring ratio
    thermal_pre = p_pre.get('qo', 0) + p_pre.get('ko', 0) + p_pre.get('ke', 0)
    monitor_pre = p_pre.get('ch', 0) + p_pre.get('sh', 0)
    k_head = p_head.get('k', 0)
    e_head = p_head.get('e', 0)

    print(f"\n  P{pidx} (L{p['lines'][0]}-L{p['lines'][-1]}, {n}T)")
    print(f"    PREFIX: {', '.join(f'{k}:{v}' for k, v in p_pre.most_common(6))}")
    print(f"    HEAD:   {', '.join(f'{k}:{v}' for k, v in p_head.most_common(5))}")
    print(f"    Thermal PFX: {thermal_pre}/{n} ({100*thermal_pre/n:.0f}%)  "
          f"Monitor PFX: {monitor_pre}/{n} ({100*monitor_pre/n:.0f}%)")
    print(f"    k-HEAD: {k_head}/{n} ({100*k_head/n:.0f}%)  "
          f"e-HEAD: {e_head}/{n} ({100*e_head/n:.0f}%)")

    # Notable tokens
    dar_count = sum(1 for t in ptokens if t.word == 'dar')
    chekar_count = sum(1 for t in ptokens if t.word == 'chekar')
    qokedy_count = sum(1 for t in ptokens if t.word == 'qokedy')
    qokeedy_count = sum(1 for t in ptokens if t.word == 'qokeedy')
    ol_count = sum(1 for t in ptokens if t.word == 'ol')
    dain_count = sum(1 for t in ptokens if t.word == 'dain')

    markers = []
    if dar_count: markers.append(f'dar×{dar_count}')
    if chekar_count: markers.append(f'chekar×{chekar_count}')
    if qokedy_count: markers.append(f'qokedy×{qokedy_count}')
    if qokeedy_count: markers.append(f'qokeedy×{qokeedy_count}')
    if ol_count: markers.append(f'ol×{ol_count}')
    if dain_count: markers.append(f'dain×{dain_count}')
    if markers:
        print(f"    MARKERS: {', '.join(markers)}")

# ═══ RECIPE ALIGNMENT ═══
print("\n" + "=" * 100)
print("RECIPE ALIGNMENT: Ch19 (Aqua Vitae Composite)")
print("=" * 100)

print("""
Ch19 Recipe Steps:
  1. Take aqua vitae, separate moisture through distillation
  2. Substance is gold-like (vegetable brazilwood)
  3. Add 1/3 pure honey with wax
  4. Ferment in balneum mariae (water bath)
  5. Repeat distillation + fermentation 9x
     (return pure substance each 2nd distillation)

Key predictions from recipe:
  - Heavy THERMAL (qo, k-HEAD) for distillation steps
  - dar tokens where material is added (honey + wax)
  - double-dar on L35-36 = two materials (honey AND wax)
  - qokedy x4 run = unique iteration marker (9x loop)
  - chekar on balneum folios (quality check on water bath)
  - monitoring (ch/sh) for fermentation observation
  - e-depth variation: kee (gentle balneum) vs ke (sharper distillation)
""")

# ═══ SPECIFIC PATTERN ANALYSIS ═══
print("=" * 100)
print("PATTERN ANALYSIS: Surprises & Confirmations")
print("=" * 100)

# 1. dar distribution
print("\n  ── dar (material addition) distribution ──")
for li in lines:
    lt = [t for t in tokens if t.line == li]
    words = [t.word for t in lt]
    if 'dar' in words:
        count = words.count('dar')
        pidx = next(p['idx'] for p in paragraphs if li in p['lines'])
        context = ' '.join(words)
        marker = " *** DOUBLE DAR ***" if count >= 2 else ""
        print(f"    L{li:>2s} (P{pidx}): dar×{count}  {context}{marker}")

# 2. e-depth thermal profile
print("\n  ── e-depth thermal profile (heat intensity) ──")
print("    k=full heat(e0), ke=steady(e1), kee=gentle(e2), keee=very gentle(e3)")
for li in lines:
    lt = [t for t in tokens if t.line == li]
    for t in lt:
        m = morph.extract(t.word)
        mid = m.middle or ''
        if mid.startswith('k') and 'e' in mid:
            # Count e-depth
            e_count = 0
            for c in mid[1:]:
                if c == 'e':
                    e_count += 1
                else:
                    break
            if e_count > 0:
                pidx = next(p['idx'] for p in paragraphs if li in p['lines'])
                depth_label = {1: 'steady(e1)', 2: 'gentle(e2)', 3: 'very-gentle(e3)'}.get(e_count, f'e{e_count}')
                print(f"    L{li:>2s} (P{pidx}): {t.word:16s} mid={mid:8s} e-depth={depth_label}")

# 3. qokedy/qokeedy runs
print("\n  ── Heat cycle tokens (qokedy/qokeedy) ──")
for li in lines:
    lt = [t for t in tokens if t.line == li]
    words = [t.word for t in lt]
    qok = [w for w in words if w.startswith('qok')]
    if qok:
        pidx = next(p['idx'] for p in paragraphs if li in p['lines'])
        print(f"    L{li:>2s} (P{pidx}): {', '.join(qok)}  full line: {' '.join(words)}")

# 4. chekar tokens (balneum marker)
print("\n  ── chekar (balneum quality check) ──")
for li in lines:
    lt = [t for t in tokens if t.line == li]
    for t in lt:
        if 'chekar' in t.word or (t.word.startswith('ch') and 'ek' in t.word):
            pidx = next(p['idx'] for p in paragraphs if li in p['lines'])
            m = morph.extract(t.word)
            atoms = atomize_middle(m.middle) if m.middle else []
            atom_str = ' '.join(f'{c}={g}' for c, g, role in atoms)
            words = [x.word for x in tokens if x.line == li]
            print(f"    L{li:>2s} (P{pidx}): {t.word:16s} [{atom_str}]  context: {' '.join(words)}")

# 5. Iteration markers
print("\n  ── Iteration/cycling markers (dain, ol) ──")
for li in lines:
    lt = [t for t in tokens if t.line == li]
    words = [t.word for t in lt]
    dain_n = words.count('dain')
    ol_n = words.count('ol')
    if dain_n or ol_n:
        pidx = next(p['idx'] for p in paragraphs if li in p['lines'])
        markers = []
        if dain_n: markers.append(f'dain×{dain_n}')
        if ol_n: markers.append(f'ol×{ol_n}')
        print(f"    L{li:>2s} (P{pidx}): {', '.join(markers)}  {' '.join(words)}")

# 6. Monitoring gradient (ch vs sh across lines)
print("\n  ── Monitoring gradient: ch (active test) vs sh (passive monitor) ──")
for li in lines:
    lt = [t for t in tokens if t.line == li]
    ch_n = sum(1 for t in lt if morph.extract(t.word).prefix and morph.extract(t.word).prefix.endswith('ch'))
    sh_n = sum(1 for t in lt if morph.extract(t.word).prefix == 'sh')
    n = len(lt)
    if ch_n + sh_n > 0:
        pidx = next(p['idx'] for p in paragraphs if li in p['lines'])
        bar_ch = '█' * ch_n
        bar_sh = '░' * sh_n
        print(f"    L{li:>2s} (P{pidx}): ch={ch_n} sh={sh_n} /{n}  {bar_ch}{bar_sh}")

# ═══ CORPUS-LEVEL STATS ═══
print("\n" + "=" * 100)
print("AGGREGATE STATISTICS")
print("=" * 100)

print(f"\n  PREFIX distribution (top 10):")
for pre, ct in prefix_counts.most_common(10):
    pct = 100 * ct / len(tokens)
    print(f"    {pre:8s}: {ct:3d} ({pct:5.1f}%)  [{PREFIX_GLOSS.get(pre, pre)}]")

print(f"\n  HEAD atom distribution:")
for h, ct in head_counts.most_common():
    pct = 100 * ct / len(tokens)
    label = ATOM.get(h.lstrip('~'), h)
    pseudo = ' (headless)' if h.startswith('~') else ''
    print(f"    {h:4s}: {ct:3d} ({pct:5.1f}%)  {label}{pseudo}")

print(f"\n  TERM atom distribution:")
for t_atom, ct in term_counts.most_common():
    pct = 100 * ct / len(tokens)
    print(f"    {t_atom:4s}: {ct:3d} ({pct:5.1f}%)  {ATOM.get(t_atom, t_atom)}")

print(f"\n  MOD atom distribution:")
for mod, ct in mod_counts.most_common():
    pct = 100 * ct / len(tokens)
    print(f"    {mod:4s}: {ct:3d} ({pct:5.1f}%)  {ATOM.get(mod, mod)}")

# ═══ COVERAGE CHECK ═══
print("\n" + "=" * 100)
print("COVERAGE")
print("=" * 100)

unknown_atoms = set()
for t in tokens:
    m = morph.extract(t.word)
    mid = m.middle or ''
    for c in mid:
        if c not in ATOM:
            unknown_atoms.add(c)
    suf = m.suffix or ''
    for c in suf:
        if c not in ATOM:
            unknown_atoms.add(c)

if unknown_atoms:
    print(f"  *** UNKNOWN ATOMS: {unknown_atoms} ***")
else:
    print(f"  100% atom coverage — all characters in all MIDDLEs and SUFFIXes have glosses")

print(f"\n  Total tokens decoded: {len(tokens)}")
print(f"  Lines: {len(lines)}")
print(f"  Paragraphs: {len(paragraphs)}")

print("\n" + "=" * 100)
print("DONE")
print("=" * 100)
