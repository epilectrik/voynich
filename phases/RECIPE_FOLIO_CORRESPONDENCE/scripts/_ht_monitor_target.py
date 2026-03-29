"""
Are HT tokens telling us WHAT to monitor?

HT = articulator + prefix + middle + suffix
On f75r, nearly all HT tokens are sh-based (monitor).

Hypothesis: the articulator encodes the MONITORING TARGET:
  d+sh = monitor the seal/closure
  y+sh = monitor for completion/endpoint
  s+sh = monitor the stage/sequence
  l+sh = monitor the level/degree
  r+sh = monitor the received material/input
  p+sh = monitor during pause
  k+sh = monitor the heat

Test:
  1. Are HT tokens predominantly sh-prefixed across ALL of Currier B?
  2. Do different articulators appear in different operational contexts?
  3. Do articulators correlate with what PRECEDES the HT token?
  4. On f75r, do HT monitor targets match recipe expectations?
"""

import sys, os, io
from collections import Counter, defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))))
from scripts.voynich import Transcript, Morphology

tx = Transcript()
morph = Morphology()

ATOM = {
    'k': 'heat', 'e': 'cool', 'a': 'into', 'o': 'arrange', 't': 'transfer',
    'p': 'pause', 'f': 'flag', 'i': 'iterate', 'c': 'loop', 'd': 'close',
    's': 'stage', 'y': 'end', 'n': 'hold', 'm': 'final', 'h': 'watch',
    'l': 'level', 'r': 'receive', 'g': 'complete', 'x': 'diagram',
    'q': 'thermal-activate',
}

all_b = [t for t in tx.currier_b() if t.word.strip() and not t.is_label]

# ═══ 1. ALL HT TOKENS IN CURRIER B ═══
print("=" * 100)
print("1. HT TOKEN PREFIX DISTRIBUTION (ALL CURRIER B)")
print("=" * 100)

ht_all = []
for t in all_b:
    m = morph.extract(t.word)
    if m.articulator:
        ht_all.append((t, m))

print(f"\nTotal HT tokens in Currier B: {len(ht_all)} ({100*len(ht_all)/len(all_b):.1f}%)")

# What prefix do HT tokens have?
ht_prefix = Counter()
for t, m in ht_all:
    ht_prefix[m.prefix or 'NONE'] += 1

print(f"\nHT token prefixes:")
for pre, ct in ht_prefix.most_common():
    pct = 100 * ct / len(ht_all)
    print(f"  {pre:8s}: {ct:5d} ({pct:5.1f}%)")

# What % are sh-based (sh, lsh)?
sh_based = sum(ct for pre, ct in ht_prefix.items() if 'sh' in pre)
ch_based = sum(ct for pre, ct in ht_prefix.items() if 'ch' in pre and 'sh' not in pre)
print(f"\n  sh-based (monitor): {sh_based} ({100*sh_based/len(ht_all):.1f}%)")
print(f"  ch-based (test):    {ch_based} ({100*ch_based/len(ht_all):.1f}%)")
print(f"  Other:              {len(ht_all)-sh_based-ch_based} ({100*(len(ht_all)-sh_based-ch_based)/len(ht_all):.1f}%)")

# ═══ 2. ARTICULATOR DISTRIBUTION ═══
print("\n" + "=" * 100)
print("2. ARTICULATOR DISTRIBUTION")
print("=" * 100)

art_counts = Counter()
art_prefix = defaultdict(Counter)
for t, m in ht_all:
    art_counts[m.articulator] += 1
    art_prefix[m.articulator][m.prefix or 'NONE'] += 1

for art, ct in art_counts.most_common():
    pct = 100 * ct / len(ht_all)
    top_pre = art_prefix[art].most_common(3)
    pre_str = ', '.join(f"{p}:{c}" for p, c in top_pre)
    art_name = ATOM.get(art, art)
    print(f"  {art} ({art_name:10s}): {ct:5d} ({pct:5.1f}%)  prefixes: {pre_str}")

# ═══ 3. WHAT PRECEDES EACH ARTICULATOR? ═══
print("\n" + "=" * 100)
print("3. WHAT OPERATION PRECEDES EACH HT ARTICULATOR?")
print("   If articulators encode monitor targets, they should follow")
print("   the operation they're monitoring")
print("=" * 100)

# For each HT token, find the preceding token's prefix
art_prev_prefix = defaultdict(Counter)
art_prev_head = defaultdict(Counter)

for t, m in ht_all:
    # Find preceding token on same line
    line_toks = [x for x in all_b if x.folio == t.folio and x.line == t.line]
    line_toks.sort(key=lambda x: all_b.index(x))

    idx = None
    for i, lt in enumerate(line_toks):
        if lt.word == t.word and lt.line == t.line and lt.folio == t.folio:
            idx = i
            break

    if idx is not None and idx > 0:
        prev = line_toks[idx - 1]
        pm = morph.extract(prev.word)
        prev_pre = pm.prefix or 'BARE'
        art_prev_prefix[m.articulator][prev_pre] += 1
        # HEAD of preceding token
        prev_mid = pm.middle or ''
        if prev_mid and prev_mid[0] in 'aeokt':
            art_prev_head[m.articulator][prev_mid[0]] += 1
    elif idx == 0:
        art_prev_prefix[m.articulator]['(LINE-INITIAL)'] += 1

for art in sorted(art_counts.keys(), key=lambda a: -art_counts[a]):
    if art_counts[art] < 10:
        continue
    art_name = ATOM.get(art, art)
    print(f"\n  {art} ({art_name}) — preceded by:")

    # Top preceding prefixes
    total_prev = sum(art_prev_prefix[art].values())
    print(f"    Prefix of preceding token:")
    for pre, ct in art_prev_prefix[art].most_common(8):
        pct = 100 * ct / total_prev if total_prev else 0
        print(f"      {pre:15s}: {ct:4d} ({pct:5.1f}%)")

    # Preceding HEAD
    if art_prev_head[art]:
        total_h = sum(art_prev_head[art].values())
        print(f"    HEAD of preceding token:")
        for h, ct in art_prev_head[art].most_common():
            pct = 100 * ct / total_h if total_h else 0
            print(f"      {h} ({ATOM[h]:10s}): {ct:4d} ({pct:5.1f}%)")

# ═══ 4. POSITION: LINE-INITIAL vs INTERIOR vs LINE-FINAL ═══
print("\n" + "=" * 100)
print("4. POSITIONAL DISTRIBUTION BY ARTICULATOR")
print("=" * 100)

art_pos = defaultdict(Counter)
for t, m in ht_all:
    line_toks = [x for x in all_b if x.folio == t.folio and x.line == t.line]
    line_toks.sort(key=lambda x: all_b.index(x))
    idx = None
    for i, lt in enumerate(line_toks):
        if lt.word == t.word and lt.line == t.line and lt.folio == t.folio:
            idx = i
            break
    if idx == 0:
        art_pos[m.articulator]['INITIAL'] += 1
    elif idx == len(line_toks) - 1:
        art_pos[m.articulator]['FINAL'] += 1
    else:
        art_pos[m.articulator]['INTERIOR'] += 1

print(f"\n  {'Art':4s} {'Name':10s} {'INITIAL':>8s} {'INTERIOR':>9s} {'FINAL':>8s} {'Init%':>7s}")
print(f"  {'-'*50}")
for art in sorted(art_counts.keys(), key=lambda a: -art_counts[a]):
    total = sum(art_pos[art].values())
    if total < 5: continue
    ini = art_pos[art].get('INITIAL', 0)
    mid = art_pos[art].get('INTERIOR', 0)
    fin = art_pos[art].get('FINAL', 0)
    ini_pct = 100 * ini / total
    print(f"  {art:4s} {ATOM.get(art,art):10s} {ini:8d} {mid:9d} {fin:8d} {ini_pct:6.1f}%")

# ═══ 5. f75r HT TOKENS IN RECIPE CONTEXT ═══
print("\n" + "=" * 100)
print("5. f75r HT TOKENS: WHAT ARE THEY TELLING THE OPERATOR TO MONITOR?")
print("=" * 100)

f75r = [t for t in all_b if t.folio == 'f75r']
lines_75 = sorted(set(t.line for t in f75r), key=lambda x: int(x))

for t in f75r:
    m = morph.extract(t.word)
    if not m.articulator:
        continue

    art = m.articulator
    art_name = ATOM.get(art, art)
    pre = m.prefix or 'BARE'
    mid = m.middle or '?'
    suf = m.suffix or ''

    # Context
    line_toks = [x for x in f75r if x.line == t.line]
    words = [x.word for x in line_toks]
    idx = next(i for i, x in enumerate(line_toks) if x.word == t.word)
    prev_w = words[idx-1] if idx > 0 else '(start)'
    next_w = words[idx+1] if idx < len(words)-1 else '(end)'

    prev_m = morph.extract(prev_w) if idx > 0 else None
    prev_pre = prev_m.prefix if prev_m else ''

    # Recipe phase
    lnum = int(t.line)
    if lnum <= 5: phase = "ASSESS"
    elif lnum <= 6: phase = "FIRST HEAT"
    elif lnum <= 12: phase = "DISTILLATION"
    elif lnum <= 16: phase = "REPETITION"
    elif lnum <= 22: phase = "FERMENTATION"
    elif lnum <= 26: phase = "CYCLE RESTART"
    elif lnum <= 27: phase = "QUALITY GATE"
    elif lnum <= 31: phase = "RE-DISTILL"
    else: phase = "MAIN LOOP"

    # Proposed reading
    reading = f"Monitor the {art_name}"
    if pre == 'sh':
        reading = f"Monitor the {art_name} (passive)"
    elif pre == 'da':
        reading = f"Setup: watch the {art_name}"
    elif pre == 'ta':
        reading = f"Transfer: watch the {art_name}"
    elif pre == 'ol':
        reading = f"Continue monitoring the {art_name}"

    match_note = ""
    if phase == "ASSESS" and art in ('s', 'l'):
        match_note = " <-- checking stage/level of starting material"
    elif phase == "DISTILLATION" and art == 'd':
        match_note = " <-- checking seals during distillation"
    elif phase == "DISTILLATION" and art == 's':
        match_note = " <-- checking stage of distillation"
    elif phase == "FERMENTATION" and art == 'y':
        match_note = " <-- watching for completion of fermentation"
    elif phase == "QUALITY GATE" and art == 'p':
        match_note = " <-- quality check during pause"
    elif phase == "MAIN LOOP" and art == 'y':
        match_note = " <-- watching for cycle completion"
    elif phase == "MAIN LOOP" and art == 'd':
        match_note = " <-- checking seal integrity in loop"
    elif phase == "MAIN LOOP" and art == 'r':
        match_note = " <-- monitoring received material"
    elif phase == "MAIN LOOP" and art == 's':
        match_note = " <-- monitoring sequence/stage progress"

    print(f"\n  L{t.line:>2s} [{phase:13s}] {t.word}")
    print(f"    {art}({art_name}) + {pre}+{mid}+{suf}")
    print(f"    After: {prev_w} ({prev_pre})")
    print(f"    Reading: {reading}{match_note}")

# ═══ 6. DO NON-f75r HT TOKENS ALSO FOLLOW THIS PATTERN? ═══
print("\n" + "=" * 100)
print("6. CROSS-CORPUS: ART + PRECEDING OPERATION CORRELATION")
print("   If articulators encode monitor targets, d-articulated HT should")
print("   follow sealing/closing operations, y-art should follow endpoints, etc.")
print("=" * 100)

# Specifically test: does d-art follow d-MIDDLE tokens more than chance?
# does y-art follow y-terminal tokens more than chance?
for test_art in ['d', 'y', 's', 'l', 'r']:
    art_name = ATOM.get(test_art, test_art)

    # Preceding token's MIDDLE content
    match_count = 0
    total_count = 0

    for t, m in ht_all:
        if m.articulator != test_art:
            continue

        line_toks = [x for x in all_b if x.folio == t.folio and x.line == t.line]
        line_toks.sort(key=lambda x: all_b.index(x))
        idx = None
        for i, lt in enumerate(line_toks):
            if lt.word == t.word and lt.line == t.line and lt.folio == t.folio:
                idx = i
                break

        if idx is not None and idx > 0:
            prev = line_toks[idx - 1]
            pm = morph.extract(prev.word)
            prev_mid = pm.middle or ''
            prev_suf = pm.suffix or ''

            total_count += 1

            # Does preceding token contain the same atom?
            if test_art in prev_mid or test_art in prev_suf:
                match_count += 1

    if total_count > 0:
        match_pct = 100 * match_count / total_count
        # Baseline: how often does this atom appear in any token's middle+suffix?
        all_content = Counter()
        for t2 in all_b:
            m2 = morph.extract(t2.word)
            content = (m2.middle or '') + (m2.suffix or '')
            for c in set(content):
                all_content[c] += 1
        baseline = 100 * all_content.get(test_art, 0) / len(all_b)
        enrichment = match_pct / baseline if baseline > 0 else 0

        print(f"\n  {test_art}-art ({art_name}): {match_count}/{total_count} preceded by token containing '{test_art}' ({match_pct:.1f}%)")
        print(f"    Baseline ('{test_art}' in any token): {baseline:.1f}%")
        print(f"    Enrichment: {enrichment:.2f}x")

print("\n" + "=" * 100)
print("DONE")
print("=" * 100)
