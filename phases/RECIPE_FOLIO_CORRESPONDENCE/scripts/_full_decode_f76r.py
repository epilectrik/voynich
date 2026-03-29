"""
Full atom-level decode of f76r using atomize().

Recipe: PL Ch18 — Element separation with silver-plate purity test.
  1. Start with crude mixture dissolved into four elemental fractions
  2. Purify liquid fractions through 7+ iterative redistillations
  3. Test purity each cycle: silver-plate test (drop on heated silver,
     if blackens = impure, keep distilling; if evaporates clean = done)
  4. Wash earth fraction with purified water -> philosophical Mercury
  5. Distill air fraction -> tincture oil

Key predictions (from prior crib decode, f76r.md):
  - ch-DOMINANT (17.0%) — this folio is about TESTING, not heating
  - Monitoring gradient (rho=0.710, strongest in corpus)
  - ch->sh transition within P3 (active testing -> passive monitoring)
  - e-depth inversion: kee (gentle) early -> ke (sharp) late
  - P4 correction spike: ok/ot elevated
  - All paragraph headers sh-family
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

PREFIX_LABEL = {
    'qo': 'THERMAL', 'ch': 'TEST', 'sh': 'MONITOR', 'ok': 'VESSEL',
    'ot': 'OPS-CHK', 'da': 'SETUP', 'sa': 'SCAFFOLD', 'ol': 'CONTINUE',
    'or': 'FLOW', 'po': 'PRE-WORK', 'so': 'SCAFF-ARR', 'ke': 'HEAT-BURST',
    'ko': 'HEAT-WORK', 'ka': 'HEAT-YIELD', 'ta': 'XFER-YIELD',
    'pch': 'STAGE-TEST', 'tch': 'XFER-TEST', 'dch': 'MARK-TEST',
    'lch': 'HOLD-TEST', 'lk': 'HOLD-HEAT', 'lsh': 'HOLD-MON',
}

def safe_int(x):
    try: return int(x)
    except: return 0

tokens = [t for t in tx.all() if t.folio == 'f76r' and t.word.strip() and not t.is_label]
lines = sorted(set(t.line for t in tokens), key=safe_int)

print(f"f76r: {len(tokens)} tokens, {len(lines)} lines")

# Paragraph detection
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
for p in paragraphs:
    first = p['tokens'][0].word if p['tokens'] else '?'
    print(f"  P{p['idx']}: L{p['lines'][0]}-L{p['lines'][-1]} ({len(p['tokens'])}T, opens: {first})")

# Recipe phase mapping
recipe = {
    1: 'SETUP: Initial observation + begin heating crude mixture',
    2: 'SEPARATION: Strong heating to separate four elemental fractions',
    3: 'CORE LOOP: Iterative redistillation with silver-plate purity testing',
    4: 'WASHING: Correct/wash earth fraction with purified water',
    5: 'FINAL: Distill air fraction to produce tincture oil',
}

# ═══ PARAGRAPH PROFILES ═══
print("\n" + "=" * 110)
print("PARAGRAPH PROFILES (atomize v2)")
print("=" * 110)

for p in paragraphs:
    pidx = p['idx']
    ptokens = p['tokens']
    n = len(ptokens)

    pre = Counter()
    heads = Counter()
    e_depths = Counter()
    words = [t.word for t in ptokens]

    for t in ptokens:
        a = morph.atomize(t.word)
        if a.prefix: pre[a.prefix] += 1
        for c, role, g in a.atoms:
            if role in ('HEAD', 'SOLE'): heads[c] += 1
        e_depths[a.e_depth] += 1

    qo_pct = 100 * sum(pre.get(p2, 0) for p2 in ['qo', 'ko', 'ke', 'lk']) / n
    ch_pct = 100 * sum(pre.get(p2, 0) for p2 in ['ch', 'pch', 'tch', 'dch', 'lch']) / n
    sh_pct = 100 * sum(pre.get(p2, 0) for p2 in ['sh', 'lsh']) / n
    ok_pct = 100 * pre.get('ok', 0) / n
    ot_pct = 100 * pre.get('ot', 0) / n

    e1 = e_depths.get(1, 0)
    e2 = e_depths.get(2, 0)
    gentle = 100 * e2 / (e1 + e2) if (e1 + e2) > 0 else 0

    dar_n = words.count('dar')
    dal_n = words.count('dal')
    chekar_n = sum(1 for w in words if w == 'chekar')
    dp_count = sum(1 for t in ptokens if morph.extract(t.word).middle in dp_set)

    # Paragraph opener
    opener = ptokens[0].word if ptokens else '?'
    opener_a = morph.atomize(opener)
    opener_pre = opener_a.prefix or 'BARE'

    phase = recipe.get(pidx, '?')

    print(f"\n  P{pidx} (L{p['lines'][0]}-L{p['lines'][-1]}, {n}T) — opens: {opener} ({opener_pre})")
    print(f"    Recipe: {phase}")
    print(f"    THERMAL: {qo_pct:.0f}%  TEST: {ch_pct:.0f}%  MONITOR: {sh_pct:.0f}%  VESSEL: {ok_pct:.0f}%  OPS: {ot_pct:.0f}%")
    print(f"    k-HEAD: {100*heads.get('k',0)/n:.0f}%  e-HEAD: {100*heads.get('e',0)/n:.0f}%")
    print(f"    e-depth: e1={e1} e2={e2} gentle={gentle:.0f}%")
    print(f"    dar={dar_n} dal={dal_n} chekar={chekar_n} dark={dp_count}")
    print(f"    PREFIX top: {', '.join(f'{k}:{v}' for k,v in pre.most_common(6))}")

# ═══ e-DEPTH TRAJECTORY ═══
print("\n\n" + "=" * 110)
print("e-DEPTH TRAJECTORY (corrected via atomize)")
print("Prediction: kee (gentle) early -> ke (sharp) late = e-depth INVERSION")
print("=" * 110)

for li in lines:
    lt = [t for t in tokens if t.line == li]
    e1_n = sum(1 for t in lt if morph.atomize(t.word).e_depth == 1)
    e2_n = sum(1 for t in lt if morph.atomize(t.word).e_depth >= 2)
    if e1_n + e2_n == 0:
        continue
    pidx = next((p['idx'] for p in paragraphs if li in p['lines']), '?')
    bar_e1 = '|' * e1_n
    bar_e2 = '#' * e2_n
    print(f"  L{li:>2s} P{pidx}  e1={e1_n} {bar_e1}  e2={e2_n} {bar_e2}")

# ═══ ch vs sh GRADIENT ═══
print("\n\n" + "=" * 110)
print("ch vs sh MONITORING GRADIENT")
print("Prediction: ch (active test) early -> sh (passive monitor) late within P3")
print("=" * 110)

for li in lines:
    lt = [t for t in tokens if t.line == li]
    ch_n = sum(1 for t in lt if (morph.atomize(t.word).prefix or '').endswith('ch'))
    sh_n = sum(1 for t in lt if morph.atomize(t.word).prefix in ('sh', 'lsh'))
    if ch_n + sh_n == 0:
        continue
    pidx = next((p['idx'] for p in paragraphs if li in p['lines']), '?')
    bar_ch = 'T' * ch_n  # T for Test
    bar_sh = 'M' * sh_n  # M for Monitor
    print(f"  L{li:>2s} P{pidx}  ch={ch_n} {bar_ch}  sh={sh_n} {bar_sh}")

# ═══ ok/ot CORRECTION SPIKE ═══
print("\n\n" + "=" * 110)
print("ok/ot DISTRIBUTION (vessel/ops verification)")
print("Prediction: P4 should have elevated ok/ot (washing/correction step)")
print("=" * 110)

for p in paragraphs:
    n = len(p['tokens'])
    ok_n = sum(1 for t in p['tokens'] if morph.atomize(t.word).prefix == 'ok')
    ot_n = sum(1 for t in p['tokens'] if morph.atomize(t.word).prefix == 'ot')
    total = ok_n + ot_n
    pct = 100 * total / n
    bar = '#' * int(pct * 2)
    print(f"  P{p['idx']}: ok={ok_n} ot={ot_n} total={total}/{n} ({pct:.1f}%) {bar}")

# ═══ dar/dal ═══
print("\n\n" + "=" * 110)
print("dar/dal DISTRIBUTION")
print("=" * 110)

for t in tokens:
    if t.word in ('dar', 'dal'):
        pidx = next((p['idx'] for p in paragraphs if t.line in p['lines']), '?')
        lt = [x for x in tokens if x.line == t.line]
        words = [x.word for x in lt]
        print(f"  P{pidx} L{t.line:>2s} {t.word}: {' '.join(words)}")

total_dar = sum(1 for t in tokens if t.word == 'dar')
total_dal = sum(1 for t in tokens if t.word == 'dal')
print(f"\n  Total: dar={total_dar} dal={total_dal} ratio={'%.1f' % (total_dar/total_dal) if total_dal > 0 else 'INF'}:1")

# ═══ DARK PIPELINE ═══
print("\n\n" + "=" * 110)
print("DARK PIPELINE TOKENS")
print("=" * 110)

for t in tokens:
    m = morph.extract(t.word)
    if m.middle and m.middle in dp_set:
        a = morph.atomize(t.word)
        pidx = next((p['idx'] for p in paragraphs if t.line in p['lines']), '?')
        lt = [x for x in tokens if x.line == t.line]
        idx = next(i for i, x in enumerate(lt) if x.word == t.word)
        prev_w = lt[idx-1].word if idx > 0 else '(START)'
        next_w = lt[idx+1].word if idx < len(lt)-1 else '(END)'
        print(f"  P{pidx} L{t.line:>2s}: {t.word:16s} mid={m.middle:8s} {a.gloss}")
        print(f"        after:{prev_w}  before:{next_w}")

# ═══ COMPARISON WITH f75r ═══
print("\n\n" + "=" * 110)
print("f76r vs f75r: PREFIX INVERSION CHECK")
print("=" * 110)

f75r = [t for t in tx.all() if t.folio == 'f75r' and t.word.strip() and not t.is_label]
f76r = tokens

for label, toks in [('f75r (Ch19: aqua vitae)', f75r), ('f76r (Ch18: element sep)', f76r)]:
    n = len(toks)
    pre = Counter()
    for t in toks:
        a = morph.atomize(t.word)
        if a.prefix: pre[a.prefix] += 1
    print(f"\n  {label} ({n}T):")
    print(f"    qo={100*pre.get('qo',0)/n:.1f}%  ch={100*pre.get('ch',0)/n:.1f}%  sh={100*pre.get('sh',0)/n:.1f}%")
    print(f"    ok={100*pre.get('ok',0)/n:.1f}%  ot={100*pre.get('ot',0)/n:.1f}%  da={100*pre.get('da',0)/n:.1f}%")

print("\n" + "=" * 110)
print("DONE")
print("=" * 110)
