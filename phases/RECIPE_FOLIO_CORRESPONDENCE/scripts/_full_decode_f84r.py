"""
Full atom-level decode of f84r using atomize().

Recipe: PL Ch14 Practica — Gold dissolution in balneum mariae.
  1. Take 1oz water of composite silver (distilled through alembic)
  2. Cast in 1 dram of vegetable G (cipher substance)
  3. Add fine gold (according to weight of G)
  4. Place in balneum mariae 3-4 days
  5. Find it black as charcoal (nigredo — color monitoring)
  6. Add twelve parts of E (cipher substance)
  7. Putrefy for one complete month

Key predictions:
  - chekar present (balneum = water bath quality check) — CONFIRMED in f84r.md
  - dar-heavy (13 dar = highest in corpus) — material additions
  - sh > ch (passive monitoring for extended balneum + putrefaction)
  - Gentle heat early (balneum) -> passive containment late (putrefaction)
  - 12 headers possibly = "twelve parts of E"
  - Dark pipeline should show balneum-class identifiers (eet?)
"""

import sys, io, json
from collections import Counter, defaultdict
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from scripts.voynich import Transcript, Morphology, ATOM_GLOSSES

tx = Transcript()
morph = Morphology()

with open(ROOT / 'data' / 'dark_pipeline_middles.json', encoding='utf-8') as f:
    dp_set = set(json.load(f)['middles'])

tokens = [t for t in tx.all() if t.folio == 'f84r' and t.word.strip() and not t.is_label]

def safe_int(x):
    try: return int(x)
    except: return 0

lines = sorted(set(t.line for t in tokens), key=safe_int)
print(f"f84r: {len(tokens)} tokens, {len(lines)} lines")

# ═══ PARAGRAPH PROFILES ═══
para_bounds = []
for li in lines:
    lt = [t for t in tokens if t.line == li]
    if lt and lt[0].word and lt[0].word[0] in 'tkpf' and len(lt[0].word) > 1:
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

print(f"Paragraphs: {len(paragraphs)}")

# ═══ e-DEPTH + THERMAL TRAJECTORY ═══
print("\n" + "=" * 100)
print("e-DEPTH TRAJECTORY")
print("Prediction: gentle (kee/balneum) early -> passive late (putrefaction)")
print("=" * 100)

for li in lines:
    lt = [t for t in tokens if t.line == li]
    e1 = sum(1 for t in lt if morph.atomize(t.word).e_depth == 1)
    e2 = sum(1 for t in lt if morph.atomize(t.word).e_depth >= 2)
    qo_n = sum(1 for t in lt if morph.atomize(t.word).prefix in ('qo', 'ko', 'ke', 'lk'))
    sh_n = sum(1 for t in lt if morph.atomize(t.word).prefix in ('sh', 'lsh'))
    ch_n = sum(1 for t in lt if (morph.atomize(t.word).prefix or '').endswith('ch'))
    dar_n = sum(1 for t in lt if t.word == 'dar')
    n = len(lt)
    if e1 + e2 == 0 and qo_n == 0 and sh_n + ch_n == 0:
        continue
    bar_e2 = '#' * e2
    bar_e1 = '|' * e1
    bar_qo = 'Q' * qo_n
    bar_mon = 'M' * (sh_n + ch_n)
    dar_flag = ' **DAR**' * dar_n
    print(f"  L{li:>2s} ({n:2d}T)  e2={e2}{bar_e2} e1={e1}{bar_e1}  qo={qo_n}{bar_qo}  mon={sh_n+ch_n}{bar_mon}{dar_flag}")

# ═══ dar DISTRIBUTION ═══
print("\n" + "=" * 100)
print("dar/dal DISTRIBUTION (13 dar = highest in corpus)")
print("=" * 100)

for t in tokens:
    if t.word in ('dar', 'dal'):
        lt = [x for x in tokens if x.line == t.line]
        words = [x.word for x in lt]
        print(f"  L{t.line:>2s} {t.word}: {' '.join(words)}")

# ═══ chekar ═══
print("\n" + "=" * 100)
print("chekar (balneum quality check)")
print("=" * 100)

for t in tokens:
    if t.word == 'chekar':
        lt = [x for x in tokens if x.line == t.line]
        words = [x.word for x in lt]
        print(f"  L{t.line:>2s}: {' '.join(words)}")

# ═══ DARK PIPELINE ═══
print("\n" + "=" * 100)
print("DARK PIPELINE TOKENS")
print("=" * 100)

dark_mids = set()
for t in tokens:
    m = morph.extract(t.word)
    if m.middle and m.middle in dp_set:
        a = morph.atomize(t.word)
        atoms = '.'.join(ATOM_GLOSSES.get(c, '?') for c in m.middle)
        n_fol = len(set(x.folio for x in tx.currier_b() if morph.extract(x.word).middle == m.middle))
        dark_mids.add(m.middle)
        print(f"  L{t.line:>2s}: {t.word:16s} mid={m.middle:8s} ({atoms:>25s})  {n_fol}f")

print(f"\n  Unique dark MIDDLEs: {len(dark_mids)}")

# Compare to f75r and f76r
all_b = [t for t in tx.currier_b() if t.word.strip() and not t.is_label]
f75r_dark = set(morph.extract(t.word).middle for t in all_b if t.folio == 'f75r' and morph.extract(t.word).middle in dp_set)
f76r_dark = set(morph.extract(t.word).middle for t in all_b if t.folio == 'f76r' and morph.extract(t.word).middle in dp_set)

shared_75 = dark_mids & f75r_dark
shared_76 = dark_mids & f76r_dark
only_84 = dark_mids - f75r_dark - f76r_dark

print(f"\n  Shared with f75r (aqua vitae): {sorted(shared_75)}")
print(f"  Shared with f76r (element sep): {sorted(shared_76)}")
print(f"  Unique to f84r: {sorted(only_84)}")

# Check for eet (honeycomb candidate) and rai (Mercury candidate)
print(f"\n  eet (honeycomb): {'PRESENT' if 'eet' in dark_mids else 'ABSENT'}")
print(f"  rai (Mercury):   {'PRESENT' if 'rai' in dark_mids else 'ABSENT'}")

# ═══ 12 HEADERS ═══
print("\n" + "=" * 100)
print("THE 12 HEADERS (micro-paragraphs)")
print("Ch14 says 'add twelve parts of E' — 12 headers = 12 portions?")
print("=" * 100)

# Headers are 1-2 token paragraph-initial+final tokens on L1-L12
for li in lines[:14]:
    lt = [t for t in tokens if t.line == li]
    # Check for par_initial tokens
    for t in lt:
        if t.par_initial and t.par_final:
            a = morph.atomize(t.word)
            m = morph.extract(t.word)
            is_dark = m.middle in dp_set if m.middle else False
            dark_flag = ' [DARK]' if is_dark else ''
            print(f"  L{t.line:>2s}: {t.word:16s} {a.gloss:40s}{dark_flag}")

# ═══ COMPARISON TABLE ═══
print("\n" + "=" * 100)
print("f84r vs f75r vs f76r")
print("=" * 100)

for label, folio in [('f84r (Ch14 gold)', 'f84r'), ('f75r (Ch19 aqua vitae)', 'f75r'), ('f76r (Ch18 elem sep)', 'f76r')]:
    ftoks = [t for t in all_b if t.folio == folio]
    n = len(ftoks)
    pre = Counter()
    e_depths = Counter()
    for t in ftoks:
        a = morph.atomize(t.word)
        if a.prefix: pre[a.prefix] += 1
        e_depths[a.e_depth] += 1

    words = [t.word for t in ftoks]
    dar = words.count('dar')
    dal = words.count('dal')
    chekar = sum(1 for w in words if w == 'chekar')
    e1 = e_depths.get(1, 0)
    e2 = e_depths.get(2, 0)
    gentle = 100 * e2 / (e1+e2) if e1+e2 > 0 else 0

    qo = 100 * sum(pre.get(p, 0) for p in ['qo', 'ko', 'ke', 'lk']) / n
    ch = 100 * sum(pre.get(p, 0) for p in ['ch', 'pch', 'tch', 'dch', 'lch']) / n
    sh = 100 * sum(pre.get(p, 0) for p in ['sh', 'lsh']) / n

    dark_n = sum(1 for t in ftoks if morph.extract(t.word).middle in dp_set)

    print(f"  {label}: {n}T  qo={qo:.0f}% ch={ch:.0f}% sh={sh:.0f}%  gentle={gentle:.0f}%  dar={dar} dal={dal} chekar={chekar} dark={dark_n}")

print("\n" + "=" * 100)
print("DONE")
print("=" * 100)
