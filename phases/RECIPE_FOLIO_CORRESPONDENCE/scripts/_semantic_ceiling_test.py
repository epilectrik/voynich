"""
With a hard external reference (PL Ch19 = f75r), can we find ANY tokens
that carry semantic content beyond control operations?

Candidates:
  1. HT tokens (articulated) - C935 says "compound specifications" but
     what if some annotate materials or substances?
  2. Hapax legomena - tokens unique to f75r. If they're material names
     they'd appear only where that material is used.
  3. dar vs dal - both "setup" but different MIDDLEs. Does r vs l
     encode material TYPE?
  4. Tokens shared ONLY between balneum folios (f75r, f84r, f108r)
     but absent from non-balneum folios - could encode balneum-specific
     content.
  5. The unparseable tokens (qey, oqekain, qckhsy) - positioned where
     material names would appear IF the ms encoded materials.
  6. Suffix variation on same stem - does suffix encode a property
     of the MATERIAL rather than the operation?
"""

import sys, os, io
from collections import Counter, defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))))
from scripts.voynich import Transcript, Morphology

tx = Transcript()
morph = Morphology()

all_b = [t for t in tx.currier_b() if t.word.strip() and not t.is_label]
f75r = [t for t in all_b if t.folio == 'f75r']
lines_75 = sorted(set(t.line for t in f75r), key=lambda x: int(x))

# Build per-folio word sets
folio_words = defaultdict(set)
folio_word_counts = defaultdict(Counter)
for t in all_b:
    folio_words[t.folio].add(t.word)
    folio_word_counts[t.folio][t.word] += 1

ATOM = {
    'k': 'heat', 'e': 'cool', 'a': 'into', 'o': 'arrange', 't': 'transfer',
    'p': 'pause', 'f': 'flag', 'i': 'iterate', 'c': 'loop', 'd': 'close',
    's': 'stage', 'y': 'end', 'n': 'hold', 'm': 'final', 'h': 'watch',
    'l': 'level', 'r': 'receive', 'g': 'complete', 'x': 'diagram',
    'q': 'thermal-activate',
}

balneum_folios = {'f75r', 'f84r', 'f108r'}  # confirmed balneum procedures
chekar_folios = {'f75r', 'f84r', 'f108r', 'f33r', 'f34r', 'f94r', 'f95r1'}

# ═══ 1. HT TOKENS ON f75r ═══
print("=" * 100)
print("1. HT TOKENS ON f75r")
print("   C935: compound specifications. But what do they ANNOTATE?")
print("=" * 100)

ht_tokens = []
for t in f75r:
    m = morph.extract(t.word)
    if m.articulator:
        ht_tokens.append(t)

print(f"\n  {len(ht_tokens)} HT tokens on f75r ({100*len(ht_tokens)/len(f75r):.1f}%)")

# Group by articulator
by_art = defaultdict(list)
for t in ht_tokens:
    m = morph.extract(t.word)
    by_art[m.articulator].append(t)

for art, toks in sorted(by_art.items()):
    print(f"\n  Articulator '{art}' ({len(toks)} tokens):")
    for t in toks:
        m = morph.extract(t.word)
        # What does this HT token annotate? Show surrounding context
        line_toks = [x for x in f75r if x.line == t.line]
        idx = next(i for i, x in enumerate(line_toks) if x.word == t.word and x.line == t.line)

        # Preceding and following tokens
        prev_w = line_toks[idx-1].word if idx > 0 else '(start)'
        next_w = line_toks[idx+1].word if idx < len(line_toks)-1 else '(end)'

        pre = m.prefix or 'BARE'
        mid = m.middle or '?'
        suf = m.suffix or ''
        mid_atoms = '.'.join(ATOM.get(c,c) for c in mid)

        # Is this HT token unique to f75r?
        other_folios = [f for f in folio_words if f != 'f75r' and t.word in folio_words[f]]
        unique = "** UNIQUE TO f75r **" if not other_folios else f"also on {len(other_folios)} folios"

        print(f"    L{t.line:>2s}: {t.word:16s} [{art}+{pre}+{mid}+{suf}] = {mid_atoms}")
        print(f"          context: ...{prev_w} >>> {t.word} >>> {next_w}...  {unique}")

# ═══ 2. HAPAX LEGOMENA ═══
print("\n" + "=" * 100)
print("2. HAPAX LEGOMENA (tokens unique to f75r)")
print("   If ANY tokens encode materials, they'd be hapax — specific to one recipe")
print("=" * 100)

f75r_unique = folio_words['f75r'] - set().union(*(folio_words[f] for f in folio_words if f != 'f75r'))
print(f"\n  {len(f75r_unique)} tokens unique to f75r")

# For each hapax, show its context and morphology
for w in sorted(f75r_unique):
    m = morph.extract(w)
    pre = m.prefix or 'BARE'
    mid = m.middle or '?'
    suf = m.suffix or ''
    art = m.articulator

    # Where does it appear?
    for t in f75r:
        if t.word == w:
            line_toks = [x for x in f75r if x.line == t.line]
            words = [x.word for x in line_toks]
            idx = words.index(w)
            prev_w = words[idx-1] if idx > 0 else '(start)'
            next_w = words[idx+1] if idx < len(words)-1 else '(end)'

            mid_atoms = '.'.join(ATOM.get(c,c) for c in mid)
            parseable = all(c in ATOM for c in mid)
            parse_flag = "" if parseable else " *** UNPARSEABLE ***"

            ht_flag = "[HT] " if art else ""
            print(f"  {ht_flag}{w:18s}  {pre}+{mid}+{suf}  ({mid_atoms}){parse_flag}")
            print(f"    L{t.line:>2s}: ...{prev_w} >>> {w} >>> {next_w}...")

# ═══ 3. dar vs dal ═══
print("\n" + "=" * 100)
print("3. dar vs dal: TWO KINDS OF MATERIAL ADDITION?")
print("   dar = da+r (setup:receive), dal = da+l (setup:level)")
print("   Ch19 has honey (liquid) AND wax (solid). Does r vs l encode phase?")
print("=" * 100)

# Find all dar and dal on f75r with context
for keyword in ['dar', 'dal']:
    print(f"\n  {keyword} on f75r:")
    for t in f75r:
        if t.word == keyword:
            line_toks = [x for x in f75r if x.line == t.line]
            words = [x.word for x in line_toks]
            idx = words.index(keyword)
            # Surrounding 2 tokens
            start = max(0, idx-2)
            end = min(len(words), idx+3)
            context = words[start:end]
            context_str = ' '.join(f'>>>{w}<<<' if w == keyword else w for w in context)
            print(f"    L{t.line:>2s}: {context_str}")

# Cross-corpus: dar and dal co-occurrence
dar_folios = set(t.folio for t in all_b if t.word == 'dar')
dal_folios = set(t.folio for t in all_b if t.word == 'dal')
both = dar_folios & dal_folios
print(f"\n  dar appears on {len(dar_folios)} folios")
print(f"  dal appears on {len(dal_folios)} folios")
print(f"  BOTH on same folio: {len(both)} folios")
if both:
    print(f"    {sorted(both)}")

# On folios with both, what's the ratio?
for f in sorted(both):
    d_r = folio_word_counts[f]['dar']
    d_l = folio_word_counts[f]['dal']
    print(f"    {f}: dar={d_r}, dal={d_l}, ratio={d_r/d_l:.1f}")

# ═══ 4. TOKENS SHARED ONLY BETWEEN BALNEUM FOLIOS ═══
print("\n" + "=" * 100)
print("4. BALNEUM-EXCLUSIVE VOCABULARY")
print("   Tokens shared by 2+ balneum folios but absent from non-balneum")
print("=" * 100)

balneum_shared = folio_words['f75r'] & folio_words['f84r'] & folio_words['f108r']
non_balneum_words = set()
for f in folio_words:
    if f not in balneum_folios:
        non_balneum_words.update(folio_words[f])

balneum_exclusive = balneum_shared - non_balneum_words
print(f"\n  Tokens on ALL 3 balneum folios: {len(balneum_shared)}")
print(f"  Of those, ABSENT from all non-balneum folios: {len(balneum_exclusive)}")
if balneum_exclusive:
    for w in sorted(balneum_exclusive):
        m = morph.extract(w)
        print(f"    {w:18s}  {m.prefix or 'BARE'}+{m.middle or '?'}+{m.suffix or ''}")

# Relax: shared by any 2 balneum folios, absent from non-balneum
for pair in [('f75r','f84r'), ('f75r','f108r'), ('f84r','f108r')]:
    shared = folio_words[pair[0]] & folio_words[pair[1]]
    exclusive = shared - non_balneum_words
    if exclusive:
        print(f"\n  Shared by {pair[0]} + {pair[1]} only:")
        for w in sorted(exclusive):
            m = morph.extract(w)
            mid_atoms = '.'.join(ATOM.get(c,c) for c in (m.middle or '?'))
            print(f"    {w:18s}  {m.prefix or 'BARE'}+{m.middle or '?'}+{m.suffix or ''}  ({mid_atoms})")

# ═══ 5. SUFFIX VARIATION ON SAME PREFIX+MIDDLE STEM ═══
print("\n" + "=" * 100)
print("5. SUFFIX ROTATION ON f75r")
print("   Same prefix+middle with different suffixes = same operation, different WHAT?")
print("   If suffix encodes material properties, rotation = different materials")
print("=" * 100)

# Build stem -> suffix map
stem_suffs = defaultdict(lambda: defaultdict(list))
for t in f75r:
    m = morph.extract(t.word)
    pre = m.prefix or ''
    mid = m.middle or ''
    suf = m.suffix or ''
    if pre and mid:
        stem = f"{pre}+{mid}"
        stem_suffs[stem][suf].append(t.line)

# Show stems with 3+ different suffixes
print(f"\n  Stems with 3+ suffix variants:")
for stem, sufmap in sorted(stem_suffs.items()):
    if len(sufmap) >= 3:
        total = sum(len(lines) for lines in sufmap.values())
        print(f"\n  {stem} ({total} tokens, {len(sufmap)} suffixes):")
        for suf, slines in sorted(sufmap.items(), key=lambda x: -len(x[1])):
            suf_atoms = '.'.join(ATOM.get(c,c) for c in suf) if suf else '(bare)'
            print(f"    -{suf or '(bare)':8s} x{len(slines):2d}  ({suf_atoms})  lines: {','.join(sorted(set(slines), key=lambda x: int(x)))}")

# ═══ 6. UNPARSEABLE TOKENS: MATERIAL NAMES? ═══
print("\n" + "=" * 100)
print("6. TOKENS THAT RESIST PARSING")
print("   qey, oqekain, qckhsy, ithey - positioned where materials would be")
print("=" * 100)

suspect_words = ['qey', 'oqekain', 'qckhsy', 'ithey', 'lch', 'ckhey']
for w in suspect_words:
    found = [t for t in f75r if t.word == w]
    if found:
        t = found[0]
        m = morph.extract(w)
        line_toks = [x for x in f75r if x.line == t.line]
        words = [x.word for x in line_toks]

        # Ch19 recipe context for this line position
        lnum = int(t.line)
        if lnum <= 5: phase = "P1: ASSESS (take aqua vitae)"
        elif lnum <= 6: phase = "P2: FIRST HEAT"
        elif lnum <= 12: phase = "P3: DISTILLATION CYCLE"
        elif lnum <= 16: phase = "P4: ENUMERATED REPETITION"
        elif lnum <= 22: phase = "P5: FERMENTATION"
        elif lnum <= 26: phase = "P6: CYCLE RESTART"
        elif lnum <= 27: phase = "P7: QUALITY GATE"
        elif lnum <= 31: phase = "P8: RE-DISTILLATION"
        else: phase = "P9: MAIN LOOP"

        print(f"\n  {w}")
        print(f"    Morphology: pre={m.prefix or 'NONE'} mid={m.middle or 'NONE'} suf={m.suffix or 'NONE'}")
        print(f"    L{t.line}: {' '.join(words)}")
        print(f"    Recipe phase: {phase}")

        # Is it on other folios?
        other = [t2.folio for t2 in all_b if t2.word == w and t2.folio != 'f75r']
        if other:
            print(f"    Also on: {Counter(other).most_common()}")
        else:
            print(f"    ** UNIQUE TO f75r **")
    else:
        print(f"\n  {w}: not found on f75r")

print("\n" + "=" * 100)
print("DONE")
print("=" * 100)
