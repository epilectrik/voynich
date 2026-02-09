"""Apparatus discrimination test via reverse Brunschwig triangulation.

Question: Can we identify which APPARATUS TYPE a Voynich folio uses
based on operational token signatures?

Brunschwig describes 5 fire-based distillation methods with distinct
operational requirements:

  1. BALNEUM MARIE (water bath, degree 1 -> REGIME_2)
     - Sealed glass vessel in water bath
     - Extended gentle heating (sustained)
     - Extended cooling (overnight mandatory)
     - High monitoring (continuous finger test)
     - Low hazard

  2. PER ALEMBICUM (standard alembic, degree 2 -> REGIME_1)
     - Standard glass apparatus
     - Moderate heating
     - Standard cooling
     - Regular monitoring (drip timing)
     - Medium hazard

  3. PER ARENAM / PER CINEREM (sand/ash bath, degree 2-3 -> R1/R3)
     - Indirect heat buffer (sand or ashes)
     - Moderate-intense heating
     - Standard cooling
     - Visual monitoring
     - Medium-high hazard

  4. PER IGNEM (direct fire, degree 3 -> REGIME_3)
     - Direct flame on vessel (earthenware)
     - Intense, rapid heating
     - Rapid cooling needed (thermal shock risk)
     - Visual monitoring, watch for overheating
     - HIGH hazard (fire, cracking, scorching)

  5. PRECISION / ANIMAL (degree 4 -> REGIME_4)
     - Balneum marie only (proteins denature)
     - Very gentle, tight tolerance
     - Precision cooling
     - Highest monitoring frequency
     - Precision hazard (narrow window)

Discriminating signals per folio:
  - ok/olk frequency (sealed apparatus indicator)
  - ck frequency (direct fire indicator)
  - ke frequency (sustained/gentle indicator)
  - ek/ep frequency (precision indicator)
  - ee/eey/eeo frequency (extended cooling -> water bath)
  - e/eo frequency (rapid cooling -> direct fire)
  - hy/cth frequency (hazard intensity)
  - LINK density (monitoring frequency)
  - h-kernel ratio (hazard exposure)

Method: Compute these signatures per folio, then test whether
REGIME assignments correlate with expected apparatus profiles.
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

# Build folio -> regime lookup
folio_regime = {}
for regime, folios in regime_mapping.items():
    for f in folios:
        folio_regime[f] = regime

# ============================================================
# STEP 1: Compute apparatus signatures per folio
# ============================================================

# Define apparatus-discriminating middle groups
SEAL_MIDDLES = {'ok', 'olk', 'okch', 'oksh'}    # Sealed vessel indicator
DIRECT_HEAT = {'ck', 'kc', 'ka'}                 # Direct/intense fire
SUSTAINED_HEAT = {'ke', 'keo', 'ko'}             # Gentle/sustained
PRECISION_HEAT = {'ek', 'ep', 'keo', 'ko'}       # Precision operations
EXTENDED_COOL = {'ee', 'eey', 'eeo', 'eeol', 'eee', 'eeeo', 'eod'}  # Extended cooling
RAPID_COOL = {'e', 'eo', 'ed'}                   # Rapid/standard cooling
HAZARD_INTENSE = {'hy', 'eckh', 'cth'}           # Intense hazard markers
LINK_MIDDLES = {'ol', 'eol', 'eeol'}             # Monitoring/continuation
CHECK_MIDDLES = {'ch', 'che', 'ckh', 'osh', 'sh'}  # Verification operations
OIL_MARKERS = {'okch', 'kc'}                     # Oil procedure markers (F-BRU-020)

# Folio-level apparatus profile
folio_profiles = {}

for folio in sorted(set(t.folio for t in tx.currier_b())):
    regime = folio_regime.get(folio, 'UNKNOWN')
    tokens = [t for t in tx.currier_b() if t.folio == folio and t.word.strip() and '*' not in t.word]
    if len(tokens) < 20:
        continue

    middles = []
    for t in tokens:
        m = morph.extract(t.word)
        if m.middle:
            middles.append(m.middle)

    n = len(middles)
    if n == 0:
        continue

    mid_counter = Counter(middles)

    # Compute rates (per 100 tokens for readability)
    def rate(group):
        return sum(mid_counter.get(m, 0) for m in group) / n * 100

    profile = {
        'folio': folio,
        'regime': regime,
        'n_tokens': len(tokens),
        'n_middles': n,
        'seal_rate': rate(SEAL_MIDDLES),
        'direct_heat_rate': rate(DIRECT_HEAT),
        'sustained_heat_rate': rate(SUSTAINED_HEAT),
        'precision_heat_rate': rate(PRECISION_HEAT),
        'extended_cool_rate': rate(EXTENDED_COOL),
        'rapid_cool_rate': rate(RAPID_COOL),
        'hazard_rate': rate(HAZARD_INTENSE),
        'link_rate': rate(LINK_MIDDLES),
        'check_rate': rate(CHECK_MIDDLES),
        'oil_marker_rate': rate(OIL_MARKERS),
    }
    folio_profiles[folio] = profile

# ============================================================
# STEP 2: Expected apparatus profiles from Brunschwig
# ============================================================

print("=" * 90)
print("APPARATUS DISCRIMINATION TEST")
print("=" * 90)
print("""
Brunschwig apparatus -> Expected token signatures:

  BALNEUM MARIE (R2):  HIGH seal, HIGH sustained_heat, HIGH extended_cool, HIGH link, LOW hazard
  PER ALEMBICUM (R1):  MOD seal, MOD heat (generic), MOD cool, MOD link, MOD hazard
  PER IGNEM (R3):      LOW seal, HIGH direct_heat, HIGH rapid_cool, LOW link, HIGH hazard
  PRECISION (R4):      MOD seal, HIGH precision_heat, HIGH precision_cool, HIGH link, MOD hazard
""")

# ============================================================
# STEP 3: Compute REGIME-level averages
# ============================================================

regime_avgs = {}
for regime in ['REGIME_1', 'REGIME_2', 'REGIME_3', 'REGIME_4']:
    folios = [p for p in folio_profiles.values() if p['regime'] == regime]
    if not folios:
        continue
    n = len(folios)
    avg = {}
    for key in ['seal_rate', 'direct_heat_rate', 'sustained_heat_rate',
                 'precision_heat_rate', 'extended_cool_rate', 'rapid_cool_rate',
                 'hazard_rate', 'link_rate', 'check_rate', 'oil_marker_rate']:
        avg[key] = sum(f[key] for f in folios) / n
    avg['n_folios'] = n
    regime_avgs[regime] = avg

print(f"{'Signal':<22} {'R1':>8} {'R2':>8} {'R3':>8} {'R4':>8}  {'Brunschwig Prediction'}")
print(f"{'-'*22} {'-'*8} {'-'*8} {'-'*8} {'-'*8}  {'-'*30}")

predictions = {
    'seal_rate':           ('MOD', 'HIGH', 'LOW', 'MOD',  'Sealed vessel = balneum marie'),
    'direct_heat_rate':    ('LOW', 'LOW',  'HIGH','LOW',  'Direct fire = per ignem'),
    'sustained_heat_rate': ('MOD', 'HIGH', 'LOW', 'LOW',  'Gentle sustained = balneum marie'),
    'precision_heat_rate': ('LOW', 'LOW',  'LOW', 'HIGH', 'Tight tolerance = precision/animal'),
    'extended_cool_rate':  ('MOD', 'HIGH', 'LOW', 'MOD',  'Overnight cool = balneum marie'),
    'rapid_cool_rate':     ('MOD', 'LOW',  'HIGH','MOD',  'Quick cool = direct fire risk'),
    'hazard_rate':         ('MOD', 'LOW',  'HIGH','MOD',  'Intense hazard = direct fire'),
    'link_rate':           ('MOD', 'HIGH', 'LOW', 'HIGH', 'High monitoring = gentle methods'),
    'check_rate':          ('MOD', 'HIGH', 'LOW', 'HIGH', 'High checking = gentle methods'),
    'oil_marker_rate':     ('LOW', 'LOW',  'HIGH','LOW',  'Oil markers = per ignem (F-BRU-020)'),
}

results = []
for key, (pr1, pr2, pr3, pr4, desc) in predictions.items():
    r1 = regime_avgs.get('REGIME_1', {}).get(key, 0)
    r2 = regime_avgs.get('REGIME_2', {}).get(key, 0)
    r3 = regime_avgs.get('REGIME_3', {}).get(key, 0)
    r4 = regime_avgs.get('REGIME_4', {}).get(key, 0)

    name = key.replace('_rate', '').replace('_', ' ')
    print(f"  {name:<22} {r1:>7.2f} {r2:>7.2f} {r3:>7.2f} {r4:>7.2f}  {desc}")

    # Test prediction
    vals = {'R1': r1, 'R2': r2, 'R3': r3, 'R4': r4}
    preds = {'R1': pr1, 'R2': pr2, 'R3': pr3, 'R4': pr4}

    # Score: does HIGH match highest? LOW match lowest?
    sorted_vals = sorted(vals.items(), key=lambda x: x[1])
    highest = sorted_vals[-1][0]
    lowest = sorted_vals[0][0]

    high_preds = [r for r, p in preds.items() if p == 'HIGH']
    low_preds = [r for r, p in preds.items() if p == 'LOW']

    hit_high = highest in high_preds if high_preds else None
    hit_low = lowest in low_preds if low_preds else None

    result = 'PASS' if hit_high and (hit_low is None or hit_low) else 'PARTIAL' if hit_high or hit_low else 'FAIL'
    results.append((key, result, highest, high_preds, lowest, low_preds))

print(f"\n{'='*90}")
print(f"PREDICTION RESULTS")
print(f"{'='*90}\n")

pass_count = sum(1 for _, r, *_ in results if r == 'PASS')
partial_count = sum(1 for _, r, *_ in results if r == 'PARTIAL')
fail_count = sum(1 for _, r, *_ in results if r == 'FAIL')

for key, result, highest, high_preds, lowest, low_preds, in results:
    name = key.replace('_rate', '').replace('_', ' ')
    h_str = f"highest={highest}, predicted={'|'.join(high_preds)}"
    l_str = f"lowest={lowest}, predicted={'|'.join(low_preds)}" if low_preds else ""
    print(f"  [{result:>7}] {name:<22} {h_str}  {l_str}")

print(f"\n  PASS: {pass_count}  PARTIAL: {partial_count}  FAIL: {fail_count}")
total = pass_count + partial_count + fail_count
print(f"  Score: {pass_count}/{total} full pass, {pass_count + partial_count}/{total} at least partial")

# ============================================================
# STEP 4: Apparatus assignment per REGIME
# ============================================================

print(f"\n{'='*90}")
print(f"APPARATUS ASSIGNMENT BY REGIME")
print(f"{'='*90}\n")

apparatus_hypotheses = {
    'REGIME_1': {
        'apparatus': 'Per Alembicum (standard distillation)',
        'brunschwig': 'Ash/sand bath, degree 2, moderate indirect heat',
        'expected': 'Moderate all signals, no extreme peaks',
    },
    'REGIME_2': {
        'apparatus': 'Balneum Marie (water bath)',
        'brunschwig': 'Sealed glass in water, degree 1, gentlest fire method',
        'expected': 'HIGH seal, sustained heat, extended cooling, monitoring',
    },
    'REGIME_3': {
        'apparatus': 'Per Ignem (direct fire)',
        'brunschwig': 'Earthenware over flame, degree 3, intense direct heat',
        'expected': 'HIGH direct heat, rapid cool, hazard; LOW seal, monitoring',
    },
    'REGIME_4': {
        'apparatus': 'Precision / Animal handling',
        'brunschwig': 'Balneum marie only, degree 4, tight tolerance',
        'expected': 'HIGH precision heat, monitoring; LOW direct heat',
    },
}

for regime in ['REGIME_1', 'REGIME_2', 'REGIME_3', 'REGIME_4']:
    hyp = apparatus_hypotheses[regime]
    avg = regime_avgs.get(regime, {})
    n = avg.get('n_folios', 0)
    print(f"  {regime} ({n} folios):")
    print(f"    Hypothesis: {hyp['apparatus']}")
    print(f"    Brunschwig: {hyp['brunschwig']}")
    print(f"    Expected:   {hyp['expected']}")
    print(f"    Observed:")
    for key in ['seal_rate', 'sustained_heat_rate', 'direct_heat_rate',
                 'precision_heat_rate', 'extended_cool_rate', 'rapid_cool_rate',
                 'hazard_rate', 'link_rate', 'check_rate']:
        v = avg.get(key, 0)
        name = key.replace('_rate', '').replace('_', ' ')
        print(f"      {name:<22} {v:.2f}%")
    print()

# ============================================================
# STEP 5: Per-folio outlier detection
# ============================================================

print(f"{'='*90}")
print(f"PER-FOLIO APPARATUS SIGNATURES (sorted by seal_rate)")
print(f"{'='*90}\n")
print(f"{'Folio':<10} {'Regime':<10} {'N':>5} {'Seal':>6} {'SustH':>6} {'DirH':>6} {'PrecH':>6} {'ExtC':>6} {'RapC':>6} {'Haz':>6} {'Link':>6} {'Chk':>6}")
print(f"{'-'*10} {'-'*10} {'-'*5} {'-'*6} {'-'*6} {'-'*6} {'-'*6} {'-'*6} {'-'*6} {'-'*6} {'-'*6} {'-'*6}")

for folio in sorted(folio_profiles, key=lambda f: -folio_profiles[f]['seal_rate']):
    p = folio_profiles[folio]
    print(f"  {p['folio']:<10} {p['regime']:<10} {p['n_middles']:>5} "
          f"{p['seal_rate']:>5.1f} {p['sustained_heat_rate']:>5.1f} "
          f"{p['direct_heat_rate']:>5.1f} {p['precision_heat_rate']:>5.1f} "
          f"{p['extended_cool_rate']:>5.1f} {p['rapid_cool_rate']:>5.1f} "
          f"{p['hazard_rate']:>5.1f} {p['link_rate']:>5.1f} {p['check_rate']:>5.1f}")

# ============================================================
# STEP 6: Discriminating middles (which middles best separate regimes?)
# ============================================================

print(f"\n{'='*90}")
print(f"APPARATUS-DISCRIMINATING MIDDLES")
print(f"{'='*90}")
print(f"Middles with highest variance across regimes (best discriminators):\n")

# Compute per-regime enrichment for each middle with enough data
all_middles_by_regime = defaultdict(lambda: Counter())
regime_totals = Counter()

for token in tx.currier_b():
    if not token.word.strip() or '*' in token.word:
        continue
    regime = folio_regime.get(token.folio)
    if not regime:
        continue
    regime_totals[regime] += 1
    m = morph.extract(token.word)
    if m.middle:
        all_middles_by_regime[m.middle][regime] += 1

# Find most discriminating middles (highest max/min ratio)
discriminators = []
for mid, rcounts in all_middles_by_regime.items():
    total = sum(rcounts.values())
    if total < 30:
        continue
    rates = {}
    for r in ['REGIME_1', 'REGIME_2', 'REGIME_3', 'REGIME_4']:
        n = regime_totals[r]
        rates[r] = (rcounts.get(r, 0) / n * 100) if n > 0 else 0

    max_rate = max(rates.values())
    min_rate = min(rates.values())
    if min_rate > 0:
        ratio = max_rate / min_rate
    else:
        ratio = max_rate / 0.01 if max_rate > 0 else 1.0

    peak = max(rates, key=rates.get)
    gloss = md['middles'].get(mid, {}).get('gloss') or '?'
    discriminators.append((mid, gloss, total, ratio, peak, rates))

discriminators.sort(key=lambda x: -x[3])

print(f"{'Middle':<14} {'Gloss':<25} {'Total':>5} {'Ratio':>6} {'Peak':<6} {'R1%':>6} {'R2%':>6} {'R3%':>6} {'R4%':>6}")
print(f"{'-'*14} {'-'*25} {'-'*5} {'-'*6} {'-'*6} {'-'*6} {'-'*6} {'-'*6} {'-'*6}")
for mid, gloss, total, ratio, peak, rates in discriminators[:30]:
    peak_short = peak.replace('REGIME_', 'R')
    gloss_short = (gloss or '?')[:24]
    print(f"  {mid:<14} {gloss_short:<25} {total:>5} {ratio:>5.1f}x {peak_short:<6} "
          f"{rates['REGIME_1']:>5.2f} {rates['REGIME_2']:>5.2f} "
          f"{rates['REGIME_3']:>5.2f} {rates['REGIME_4']:>5.2f}")

# ============================================================
# STEP 7: Save results
# ============================================================

output = {
    'regime_averages': regime_avgs,
    'apparatus_hypotheses': apparatus_hypotheses,
    'prediction_results': [
        {'signal': k, 'result': r, 'highest': h, 'predicted_high': hp, 'lowest': l, 'predicted_low': lp}
        for k, r, h, hp, l, lp in results
    ],
    'score': {'pass': pass_count, 'partial': partial_count, 'fail': fail_count},
    'folio_profiles': folio_profiles,
    'top_discriminators': [
        {'middle': m, 'gloss': g, 'total': t, 'ratio': round(r, 1),
         'peak': p, 'rates': {k: round(v, 3) for k, v in rt.items()}}
        for m, g, t, r, p, rt in discriminators[:30]
    ],
}

out_path = Path('phases/GLOSS_RESEARCH/results/16_apparatus_discrimination.json')
out_path.parent.mkdir(parents=True, exist_ok=True)
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)
print(f"\nResults saved to {out_path}")
