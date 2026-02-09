"""Prefix REGIME discrimination test.

We REGIME-tested MIDDLEs (Tests 11-13) and apparatus signatures (Test 16).
Now we test PREFIXES — which appear on nearly every token and determine
the "verb" in auto-composed readings.

Current prefix glosses (from F-BRU-012 and expert validation):
  ch = check          sh = observe        qo = energy
  ol = continue       da = setup          ok = lock
  ot = (scaffold)     ct = control        ar = close
  pch = chop          tch = pound         kch = precision heat
  fch = prepare       lk = L-modified     ke = sustain
  te = gather         se = scaffold       de = divide
  pe = start

Question: Do prefixes distribute differently across REGIMEs?
If so, we can refine glosses to be apparatus-specific.

Signals:
  1. REGIME enrichment (which apparatus does this prefix correlate with?)
  2. Positional data (where in the line does this prefix appear?)
  3. What MIDDLEs follow each prefix? (prefix-middle co-selection)
  4. Bigram context (what prefix follows this prefix in sequence?)
"""
import json, sys
from pathlib import Path
from collections import Counter, defaultdict
sys.path.insert(0, str(Path(r'C:\git\voynich')))
from scripts.voynich import Transcript, Morphology

tx = Transcript()
morph = Morphology()
md = json.load(open('data/middle_dictionary.json', encoding='utf-8'))
regime_mapping = json.load(open('results/regime_folio_mapping.json', encoding='utf-8'))

folio_regime = {}
for regime, folios in regime_mapping.items():
    for f in folios:
        folio_regime[f] = regime

# ============================================================
# STEP 1: Prefix frequency and REGIME distribution
# ============================================================

prefix_regime = defaultdict(lambda: Counter())
prefix_total = Counter()
regime_totals = Counter()
prefix_middles = defaultdict(lambda: Counter())  # prefix -> {middle -> count}

# Positional data
line_tokens = defaultdict(list)
for token in tx.currier_b():
    if not token.word.strip() or '*' in token.word:
        continue
    line_tokens[(token.folio, token.line)].append(token)

token_positions = {}
for key, tokens in line_tokens.items():
    n = len(tokens)
    for i, tok in enumerate(tokens):
        pos = i / max(1, n - 1) if n > 1 else 0.5
        token_positions[(tok.folio, tok.line, i)] = pos

prefix_positions = defaultdict(list)
idx_tracker = defaultdict(int)

for token in tx.currier_b():
    if not token.word.strip() or '*' in token.word:
        continue
    regime = folio_regime.get(token.folio)
    if not regime:
        continue
    regime_totals[regime] += 1

    m = morph.extract(token.word)
    pfx = m.prefix
    if not pfx:
        pfx = '(none)'

    prefix_regime[pfx][regime] += 1
    prefix_total[pfx] += 1

    if m.middle:
        prefix_middles[pfx][m.middle] += 1

    key = (token.folio, token.line)
    idx = idx_tracker[key]
    idx_tracker[key] += 1
    pos = token_positions.get((token.folio, token.line, idx))
    if pos is not None:
        prefix_positions[pfx].append(pos)

# ============================================================
# STEP 2: Print REGIME distribution for all prefixes
# ============================================================

print("=" * 95)
print("PREFIX REGIME DISTRIBUTION")
print("=" * 95)
print(f"\n{'Prefix':<10} {'Gloss':<22} {'Total':>6} {'R1%':>7} {'R2%':>7} {'R3%':>7} {'R4%':>7}  {'Peak':>4} {'Enrich':>6} {'MeanPos':>7}")
print(f"{'-'*10} {'-'*22} {'-'*6} {'-'*7} {'-'*7} {'-'*7} {'-'*7}  {'-'*4} {'-'*6} {'-'*7}")

# Known prefix glosses
PREFIX_GLOSSES = {
    'ch': 'check', 'sh': 'observe', 'qo': 'energy',
    'ol': 'continue', 'da': 'setup', 'ok': 'lock',
    'ot': '(scaffold)', 'ct': 'control', 'ar': 'close',
    'pch': 'chop', 'tch': 'pound', 'kch': 'precision heat',
    'fch': 'prepare', 'lk': 'L-modified', 'ke': 'sustain',
    'te': 'gather', 'se': 'scaffold', 'de': 'divide',
    'pe': 'start', 'to': 'scaffold-path', 'po': 'pre-process',
    'lch': 'L-check', 'lsh': 'L-observe',
    '(none)': '(bare token)',
}

results = []
for pfx in sorted(prefix_total, key=lambda p: -prefix_total[p]):
    total = prefix_total[pfx]
    if total < 20:
        continue
    gloss = PREFIX_GLOSSES.get(pfx, '?')
    rates = {}
    for r in ['REGIME_1', 'REGIME_2', 'REGIME_3', 'REGIME_4']:
        n = regime_totals[r]
        rates[r] = (prefix_regime[pfx].get(r, 0) / n * 100) if n > 0 else 0

    peak = max(rates, key=rates.get)
    mean_rate = sum(rates.values()) / 4
    enrich = rates[peak] / mean_rate if mean_rate > 0 else 0
    peak_short = peak.replace('REGIME_', 'R')

    positions = prefix_positions.get(pfx, [])
    mean_pos = sum(positions) / len(positions) if positions else 0.5

    results.append((pfx, gloss, total, rates, peak_short, enrich, mean_pos))

    print(f"  {pfx:<10} {gloss:<22} {total:>6} "
          f"{rates['REGIME_1']:>6.2f} {rates['REGIME_2']:>6.2f} "
          f"{rates['REGIME_3']:>6.2f} {rates['REGIME_4']:>6.2f}  "
          f"{peak_short:>4} {enrich:>5.1f}x {mean_pos:>6.3f}")

# ============================================================
# STEP 3: Highly discriminating prefixes
# ============================================================

print(f"\n{'='*95}")
print(f"HIGHLY DISCRIMINATING PREFIXES (enrichment > 1.5x)")
print(f"{'='*95}\n")

discriminating = [(pfx, g, t, r, p, e, mp) for pfx, g, t, r, p, e, mp in results if e > 1.5]
discriminating.sort(key=lambda x: -x[5])

for pfx, gloss, total, rates, peak, enrich, mean_pos in discriminating:
    print(f"  {pfx:<10} '{gloss}'")
    print(f"    Total: {total}, Peak: {peak} ({enrich:.1f}x enrichment)")
    print(f"    R1={rates['REGIME_1']:.2f}  R2={rates['REGIME_2']:.2f}  "
          f"R3={rates['REGIME_3']:.2f}  R4={rates['REGIME_4']:.2f}")
    print(f"    Mean position: {mean_pos:.3f}")

    # Top middles for this prefix
    top_mids = prefix_middles[pfx].most_common(8)
    mid_str = ', '.join(f"{m}({c})" for m, c in top_mids)
    print(f"    Top middles: {mid_str}")
    print()

# ============================================================
# STEP 4: Prefix pairs — do prefixes sequence differently by REGIME?
# ============================================================

print(f"{'='*95}")
print(f"PREFIX BIGRAM ANALYSIS")
print(f"{'='*95}")
print(f"What prefix FOLLOWS each prefix in token sequence?\n")

prefix_bigrams = defaultdict(lambda: Counter())
prev_pfx = None
for token in tx.currier_b():
    if not token.word.strip() or '*' in token.word:
        prev_pfx = None
        continue
    m = morph.extract(token.word)
    pfx = m.prefix or '(none)'
    if prev_pfx and prev_pfx in PREFIX_GLOSSES and prefix_total[prev_pfx] >= 50:
        prefix_bigrams[prev_pfx][pfx] += 1
    prev_pfx = pfx

print(f"{'Prefix':<10} {'Top 6 following prefixes'}")
print(f"{'-'*10} {'-'*70}")
for pfx in sorted(prefix_bigrams, key=lambda p: -prefix_total.get(p, 0)):
    total = sum(prefix_bigrams[pfx].values())
    if total < 30:
        continue
    top = prefix_bigrams[pfx].most_common(6)
    gloss = PREFIX_GLOSSES.get(pfx, '?')
    following = ', '.join(f"{p}({c})" for p, c in top)
    print(f"  {pfx:<10} {following[:75]}")

# ============================================================
# STEP 5: Prefix-MIDDLE co-selection by REGIME
# ============================================================

print(f"\n{'='*95}")
print(f"PREFIX-MIDDLE CO-SELECTION: Does the same prefix select different middles per REGIME?")
print(f"{'='*95}\n")

# For the most common prefixes, show top middles per regime
for pfx in ['ch', 'sh', 'qo', 'da', 'ok', 'ot', 'ol', 'pch', 'tch', 'de']:
    if prefix_total.get(pfx, 0) < 50:
        continue
    gloss = PREFIX_GLOSSES.get(pfx, '?')
    print(f"  PREFIX '{pfx}' ({gloss}):")

    regime_mid_counts = defaultdict(lambda: Counter())
    for token in tx.currier_b():
        if not token.word.strip() or '*' in token.word:
            continue
        regime = folio_regime.get(token.folio)
        if not regime:
            continue
        m = morph.extract(token.word)
        if m.prefix == pfx and m.middle:
            mid_gloss = md['middles'].get(m.middle, {}).get('gloss') or m.middle
            regime_mid_counts[regime][mid_gloss] += 1

    for r in ['REGIME_1', 'REGIME_2', 'REGIME_3', 'REGIME_4']:
        top3 = regime_mid_counts[r].most_common(5)
        r_short = r.replace('REGIME_', 'R')
        top_str = ', '.join(f"{g}({c})" for g, c in top3)
        print(f"    {r_short}: {top_str[:70]}")
    print()

# ============================================================
# STEP 6: Save results
# ============================================================

output = {
    'prefix_regime_distribution': [
        {'prefix': pfx, 'gloss': g, 'total': t,
         'rates': {k: round(v, 3) for k, v in r.items()},
         'peak': p, 'enrichment': round(e, 2), 'mean_position': round(mp, 3)}
        for pfx, g, t, r, p, e, mp in results
    ],
    'discriminating_prefixes': [
        {'prefix': pfx, 'gloss': g, 'total': t, 'peak': p, 'enrichment': round(e, 2)}
        for pfx, g, t, r, p, e, mp in discriminating
    ],
}

out_path = Path('phases/GLOSS_RESEARCH/results/18_prefix_regime_discrimination.json')
out_path.parent.mkdir(parents=True, exist_ok=True)
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)
print(f"\nResults saved to {out_path}")
