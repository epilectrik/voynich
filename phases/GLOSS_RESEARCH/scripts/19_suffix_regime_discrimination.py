"""Suffix REGIME discrimination test.

Middles (Tests 11-13): 23 refinements, up to 8.5x enrichment
Prefixes (Test 18): modest enrichment (max 2.0x), domain selectors
Suffixes: Strong positional profiles (Test 01) but never REGIME-tested.

Current suffix glosses:
  -y   = done / terminal           (pos 0.583)
  -dy  = close / seal              (pos 0.528)
  -hy  = verify / maintain         (pos 0.504)
  -ey  = set / established         (pos 0.435, EARLY)
  -ly  = settled / cooled          (pos 0.695, LATE)
  -am  = finalize                  (pos 0.930, LINE-FINAL)
  -aiin/-ain = check               (pos 0.465/0.477)
  -al  = complete / transfer       (pos 0.494)
  -ar  = close                     (pos 0.480)
  -or  = portion                   (pos 0.473)
  -s   = next / boundary           (pos 0.458)
  -edy = (thorough)                (compound)

Question: Do suffixes distribute differently across REGIMEs?
If so, we can refine glosses to be apparatus-specific.

Brunschwig predictions:
  R2 (balneum marie): More -ey (set/established before long process),
     more -am (line-final sealing), more -ly (settled/cooled overnight)?
  R3 (per ignem): More -s (rapid sequence), more -dy (quick close),
     less -ly (no long settling)?
  R4 (precision): More -hy (verify/maintain tight tolerance)?
"""
import json, sys
from pathlib import Path
from collections import Counter, defaultdict
sys.path.insert(0, str(Path(r'C:\git\voynich')))
from scripts.voynich import Transcript, Morphology

tx = Transcript()
morph = Morphology()
regime_mapping = json.load(open('results/regime_folio_mapping.json', encoding='utf-8'))

folio_regime = {}
for regime, folios in regime_mapping.items():
    for f in folios:
        folio_regime[f] = regime

# ============================================================
# STEP 1: Suffix frequency and REGIME distribution
# ============================================================

suffix_regime = defaultdict(lambda: Counter())
suffix_total = Counter()
regime_totals = Counter()

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

suffix_positions = defaultdict(list)
idx_tracker = defaultdict(int)

for token in tx.currier_b():
    if not token.word.strip() or '*' in token.word:
        continue
    regime = folio_regime.get(token.folio)
    if not regime:
        continue
    regime_totals[regime] += 1

    m = morph.extract(token.word)
    sfx = m.suffix or '(none)'

    suffix_regime[sfx][regime] += 1
    suffix_total[sfx] += 1

    key = (token.folio, token.line)
    idx = idx_tracker[key]
    idx_tracker[key] += 1
    pos = token_positions.get((token.folio, token.line, idx))
    if pos is not None:
        suffix_positions[sfx].append(pos)

# Known suffix glosses
SUFFIX_GLOSSES = {
    'y': 'done', 'dy': 'close', 'hy': 'verify/maintain',
    'ey': 'set', 'ly': 'settled', 'am': 'finalize',
    'aiin': 'check', 'ain': 'check', 'al': 'complete',
    'ar': 'close', 'or': 'portion', 's': 'next/boundary',
    'edy': 'thorough', 'ody': 'collect-close', 'r': 'input',
    'iin': 'iterate', 'in': 'link', 'ol': 'continue',
    'd': 'mark', 'l': 'frame', '(none)': '(bare)',
}

# ============================================================
# STEP 2: Print REGIME distribution
# ============================================================

print("=" * 100)
print("SUFFIX REGIME DISTRIBUTION")
print("=" * 100)
print(f"\n{'Suffix':<10} {'Gloss':<18} {'Total':>6} {'R1%':>7} {'R2%':>7} {'R3%':>7} {'R4%':>7}  "
      f"{'Peak':>4} {'Enrich':>6} {'MeanPos':>7}")
print(f"{'-'*10} {'-'*18} {'-'*6} {'-'*7} {'-'*7} {'-'*7} {'-'*7}  "
      f"{'-'*4} {'-'*6} {'-'*7}")

results = []
for sfx in sorted(suffix_total, key=lambda s: -suffix_total[s]):
    total = suffix_total[sfx]
    if total < 20:
        continue
    gloss = SUFFIX_GLOSSES.get(sfx, '?')
    rates = {}
    for r_name in ['REGIME_1', 'REGIME_2', 'REGIME_3', 'REGIME_4']:
        n = regime_totals[r_name]
        rates[r_name] = (suffix_regime[sfx].get(r_name, 0) / n * 100) if n > 0 else 0

    peak = max(rates, key=rates.get)
    mean_rate = sum(rates.values()) / 4
    enrich = rates[peak] / mean_rate if mean_rate > 0 else 0
    peak_short = peak.replace('REGIME_', 'R')

    positions = suffix_positions.get(sfx, [])
    mean_pos = sum(positions) / len(positions) if positions else 0.5

    results.append((sfx, gloss, total, rates, peak_short, enrich, mean_pos))
    print(f"  {sfx:<10} {gloss:<18} {total:>6} "
          f"{rates['REGIME_1']:>6.2f} {rates['REGIME_2']:>6.2f} "
          f"{rates['REGIME_3']:>6.2f} {rates['REGIME_4']:>6.2f}  "
          f"{peak_short:>4} {enrich:>5.1f}x {mean_pos:>6.3f}")

# ============================================================
# STEP 3: Highly discriminating suffixes
# ============================================================

print(f"\n{'='*100}")
print(f"HIGHLY DISCRIMINATING SUFFIXES (enrichment > 1.3x)")
print(f"{'='*100}\n")

discriminating = [(s, g, t, r, p, e, mp) for s, g, t, r, p, e, mp in results if e > 1.3]
discriminating.sort(key=lambda x: -x[5])

for sfx, gloss, total, rates, peak, enrich, mean_pos in discriminating:
    print(f"  -{sfx:<10} '{gloss}'")
    print(f"    Total: {total}, Peak: {peak} ({enrich:.1f}x enrichment)")
    print(f"    R1={rates['REGIME_1']:.2f}  R2={rates['REGIME_2']:.2f}  "
          f"R3={rates['REGIME_3']:.2f}  R4={rates['REGIME_4']:.2f}")
    print(f"    Mean position: {mean_pos:.3f}")
    print()

# ============================================================
# STEP 4: Brunschwig predictions test
# ============================================================

print(f"{'='*100}")
print(f"BRUNSCHWIG SUFFIX PREDICTIONS")
print(f"{'='*100}")
print("""
Brunschwig apparatus -> Expected suffix signatures:

  BALNEUM MARIE (R2): MORE -ey (establish before long process), -ly (overnight cooling),
                       -am (line-final sealing)
  PER IGNEM (R3):     MORE -s (rapid transitions), -dy (quick close), LESS -ly
  PRECISION (R4):     MORE -hy (maintain tight tolerance), -aiin (frequent checks)
  STANDARD (R1):      Baseline, moderate everything
""")

predictions = {
    'ey':   ('MOD', 'HIGH', 'LOW', 'MOD',  'Set/establish = before long gentle process'),
    'ly':   ('MOD', 'HIGH', 'LOW', 'LOW',  'Settled = overnight cooling (balneum marie)'),
    'am':   ('MOD', 'HIGH', 'LOW', 'MOD',  'Finalize = sealing end of gentle procedure'),
    's':    ('MOD', 'LOW',  'HIGH','MOD',  'Next/boundary = rapid transitions in direct fire'),
    'dy':   ('MOD', 'LOW',  'HIGH','MOD',  'Close = quick close in intense process'),
    'hy':   ('LOW', 'MOD',  'MOD', 'HIGH', 'Verify/maintain = tight tolerance checking'),
    'aiin': ('MOD', 'MOD',  'LOW', 'HIGH', 'Check = frequent checking in precision'),
    'ar':   ('MOD', 'HIGH', 'LOW', 'MOD',  'Close = apparatus closure'),
    'or':   ('MOD', 'LOW',  'HIGH','MOD',  'Portion = collecting portions in direct fire'),
}

print(f"{'Suffix':<10} {'Prediction':<55} {'Result':<8}")
print(f"{'-'*10} {'-'*55} {'-'*8}")

pass_count = 0
partial_count = 0
fail_count = 0

for sfx, (pr1, pr2, pr3, pr4, desc) in predictions.items():
    # Find this suffix in results
    match = [r for r in results if r[0] == sfx]
    if not match:
        continue
    _, _, total, rates, peak_short, enrich, _ = match[0]

    vals = {'R1': rates['REGIME_1'], 'R2': rates['REGIME_2'],
            'R3': rates['REGIME_3'], 'R4': rates['REGIME_4']}
    preds = {'R1': pr1, 'R2': pr2, 'R3': pr3, 'R4': pr4}

    sorted_vals = sorted(vals.items(), key=lambda x: x[1])
    highest = sorted_vals[-1][0]
    lowest = sorted_vals[0][0]

    high_preds = [r for r, p in preds.items() if p == 'HIGH']
    low_preds = [r for r, p in preds.items() if p == 'LOW']

    hit_high = highest in high_preds if high_preds else None
    hit_low = lowest in low_preds if low_preds else None

    result = 'PASS' if hit_high and (hit_low is None or hit_low) else 'PARTIAL' if hit_high or hit_low else 'FAIL'
    if result == 'PASS':
        pass_count += 1
    elif result == 'PARTIAL':
        partial_count += 1
    else:
        fail_count += 1

    print(f"  -{sfx:<10} {desc:<55} [{result}]")
    print(f"             highest={highest}(pred={'|'.join(high_preds)}), "
          f"lowest={lowest}(pred={'|'.join(low_preds)})")

print(f"\n  PASS: {pass_count}  PARTIAL: {partial_count}  FAIL: {fail_count}")
print(f"  Score: {pass_count}/{pass_count+partial_count+fail_count} full pass, "
      f"{pass_count+partial_count}/{pass_count+partial_count+fail_count} at least partial")

# ============================================================
# STEP 5: Cross-reference with positional data (Test 01)
# ============================================================

print(f"\n{'='*100}")
print(f"SUFFIX POSITION x REGIME INTERACTION")
print(f"{'='*100}")
print(f"Do suffixes appear at different positions in different regimes?\n")

# Compute mean position per suffix per regime
suffix_regime_pos = defaultdict(lambda: defaultdict(list))
idx_tracker2 = defaultdict(int)
for token in tx.currier_b():
    if not token.word.strip() or '*' in token.word:
        continue
    regime = folio_regime.get(token.folio)
    if not regime:
        continue
    m = morph.extract(token.word)
    sfx = m.suffix or '(none)'
    if suffix_total[sfx] < 50:
        continue
    key = (token.folio, token.line)
    idx = idx_tracker2[key]
    idx_tracker2[key] += 1
    pos = token_positions.get((token.folio, token.line, idx))
    if pos is not None:
        suffix_regime_pos[sfx][regime].append(pos)

print(f"{'Suffix':<10} {'Gloss':<18} {'R1 pos':>7} {'R2 pos':>7} {'R3 pos':>7} {'R4 pos':>7}  {'Shift?'}")
print(f"{'-'*10} {'-'*18} {'-'*7} {'-'*7} {'-'*7} {'-'*7}  {'-'*20}")

for sfx in sorted(suffix_regime_pos, key=lambda s: -suffix_total[s]):
    gloss = SUFFIX_GLOSSES.get(sfx, '?')
    pos_by_regime = {}
    for r_name in ['REGIME_1', 'REGIME_2', 'REGIME_3', 'REGIME_4']:
        positions = suffix_regime_pos[sfx][r_name]
        pos_by_regime[r_name] = sum(positions) / len(positions) if positions else 0.5

    # Check for position shift
    vals = list(pos_by_regime.values())
    shift = max(vals) - min(vals)
    shift_str = f'SHIFT {shift:.3f}' if shift > 0.05 else 'stable'

    print(f"  {sfx:<10} {gloss:<18} "
          f"{pos_by_regime['REGIME_1']:>6.3f} {pos_by_regime['REGIME_2']:>6.3f} "
          f"{pos_by_regime['REGIME_3']:>6.3f} {pos_by_regime['REGIME_4']:>6.3f}  "
          f"{shift_str}")

# ============================================================
# STEP 6: Save results
# ============================================================

output = {
    'suffix_regime_distribution': [
        {'suffix': s, 'gloss': g, 'total': t,
         'rates': {k: round(v, 3) for k, v in r.items()},
         'peak': p, 'enrichment': round(e, 2), 'mean_position': round(mp, 3)}
        for s, g, t, r, p, e, mp in results
    ],
    'prediction_score': {'pass': pass_count, 'partial': partial_count, 'fail': fail_count},
}

out_path = Path('phases/GLOSS_RESEARCH/results/19_suffix_regime_discrimination.json')
out_path.parent.mkdir(parents=True, exist_ok=True)
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)
print(f"\nResults saved to {out_path}")
