"""
Chekar Prediction Test

Cross-folio crib analysis (Session handoff) found chekar appears on 7 folios:
  CONFIRMED balneum: f75r, f84r, f108r
  UNTESTED prediction: f33r, f34r, f94r, f95r1

Prediction: the 4 untested folios should show balneum-compatible
operational profiles — gentle sustained heat, monitoring-dominant,
material additions (dar), iteration markers.

Tests:
  1. Operational profile: qo%, ch/sh%, k-HEAD%, e-HEAD%, e-depth
  2. Comparison to confirmed balneum folios vs corpus baseline
  3. dar/dal presence and distribution
  4. Dark pipeline overlap with confirmed balneum folios
  5. Do they look more like balneum folios or random folios?
"""

import sys, os, io, json
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

all_b = [t for t in tx.currier_b() if t.word.strip() and not t.is_label]

confirmed_balneum = ['f75r', 'f84r', 'f108r']
predicted_balneum = ['f33r', 'f34r', 'f94r', 'f95r1']
all_folios = sorted(set(t.folio for t in all_b))

def folio_profile(folio):
    toks = [t for t in all_b if t.folio == folio]
    if not toks:
        return None
    n = len(toks)

    pre = Counter()
    heads = Counter()
    e_depths = Counter()
    words = [t.word for t in toks]

    for t in toks:
        a = morph.atomize(t.word)
        if a.prefix: pre[a.prefix] += 1
        for c, role, g in a.atoms:
            if role in ('HEAD', 'SOLE'):
                heads[c] += 1
        e_depths[a.e_depth] += 1

    m = morph.extract(toks[0].word)
    section = toks[0].section

    qo_pct = 100 * pre.get('qo', 0) / n
    ch_pct = 100 * pre.get('ch', 0) / n
    sh_pct = 100 * pre.get('sh', 0) / n
    ok_pct = 100 * pre.get('ok', 0) / n
    ot_pct = 100 * pre.get('ot', 0) / n
    da_pct = 100 * pre.get('da', 0) / n
    monitor_pct = 100 * sum(pre.get(p, 0) for p in ['ch', 'sh', 'pch', 'tch', 'dch', 'lch', 'lsh']) / n

    k_pct = 100 * heads.get('k', 0) / n
    e_pct = 100 * heads.get('e', 0) / n

    e0 = e_depths.get(0, 0)
    e1 = e_depths.get(1, 0)
    e2 = e_depths.get(2, 0)
    gentle_ratio = 100 * e2 / (e1 + e2) if (e1 + e2) > 0 else 0

    dar_n = words.count('dar')
    dal_n = words.count('dal')
    chekar_n = sum(1 for w in words if w == 'chekar')
    dain_n = words.count('dain')

    # Dark pipeline
    dark_mids = set()
    dark_count = 0
    for t in toks:
        em = morph.extract(t.word)
        if em.middle and em.middle in dp_set:
            dark_mids.add(em.middle)
            dark_count += 1

    return {
        'folio': folio, 'n': n, 'section': section,
        'qo': qo_pct, 'ch': ch_pct, 'sh': sh_pct, 'monitor': monitor_pct,
        'ok': ok_pct, 'ot': ot_pct, 'da': da_pct,
        'k_head': k_pct, 'e_head': e_pct,
        'e0': e0, 'e1': e1, 'e2': e2, 'gentle_ratio': gentle_ratio,
        'dar': dar_n, 'dal': dal_n, 'chekar': chekar_n, 'dain': dain_n,
        'dark_mids': dark_mids, 'dark_count': dark_count,
        'dark_pct': 100 * dark_count / n,
    }


# ═══ COMPUTE ALL PROFILES ═══
profiles = {}
for f in all_folios:
    p = folio_profile(f)
    if p:
        profiles[f] = p

# ═══ CONFIRMED BALNEUM BASELINE ═══
print("=" * 110)
print("CONFIRMED BALNEUM FOLIO PROFILES")
print("=" * 110)

header = (f"{'Folio':>8s} {'N':>5s} {'Sec':>4s} {'qo%':>5s} {'ch%':>5s} {'sh%':>5s} {'mon%':>5s} "
          f"{'k%':>4s} {'e%':>4s} {'e2%':>4s} {'dar':>4s} {'dal':>4s} {'chkr':>5s} {'dain':>5s} {'dp%':>4s}")
print(f"\n  {header}")
print(f"  {'-'*95}")

for f in confirmed_balneum:
    p = profiles[f]
    print(f"  {p['folio']:>8s} {p['n']:5d} {p['section']:>4s} {p['qo']:5.1f} {p['ch']:5.1f} {p['sh']:5.1f} {p['monitor']:5.1f} "
          f"{p['k_head']:4.1f} {p['e_head']:4.1f} {p['gentle_ratio']:4.0f} {p['dar']:4d} {p['dal']:4d} {p['chekar']:5d} {p['dain']:5d} {p['dark_pct']:4.1f}")

# Compute balneum averages
bal_avg = {}
for key in ['qo', 'ch', 'sh', 'monitor', 'k_head', 'e_head', 'gentle_ratio', 'dark_pct']:
    bal_avg[key] = sum(profiles[f][key] for f in confirmed_balneum) / len(confirmed_balneum)
bal_avg['dar_mean'] = sum(profiles[f]['dar'] for f in confirmed_balneum) / len(confirmed_balneum)

print(f"\n  Balneum average: qo={bal_avg['qo']:.1f} ch={bal_avg['ch']:.1f} sh={bal_avg['sh']:.1f} "
      f"mon={bal_avg['monitor']:.1f} k={bal_avg['k_head']:.1f} e={bal_avg['e_head']:.1f} "
      f"gentle={bal_avg['gentle_ratio']:.0f}% dar_mean={bal_avg['dar_mean']:.1f}")

# ═══ PREDICTED BALNEUM ═══
print("\n\n" + "=" * 110)
print("PREDICTED BALNEUM FOLIOS (chekar present, untested)")
print("=" * 110)

print(f"\n  {header}")
print(f"  {'-'*95}")

for f in predicted_balneum:
    if f not in profiles:
        print(f"  {f:>8s} -- NOT IN CURRIER B")
        continue
    p = profiles[f]
    print(f"  {p['folio']:>8s} {p['n']:5d} {p['section']:>4s} {p['qo']:5.1f} {p['ch']:5.1f} {p['sh']:5.1f} {p['monitor']:5.1f} "
          f"{p['k_head']:4.1f} {p['e_head']:4.1f} {p['gentle_ratio']:4.0f} {p['dar']:4d} {p['dal']:4d} {p['chekar']:5d} {p['dain']:5d} {p['dark_pct']:4.1f}")

# ═══ CORPUS BASELINE ═══
print("\n\n" + "=" * 110)
print("CORPUS BASELINE (all Currier B folios)")
print("=" * 110)

non_chekar = [f for f in all_folios if f not in confirmed_balneum + predicted_balneum and f in profiles]
corpus_avg = {}
for key in ['qo', 'ch', 'sh', 'monitor', 'k_head', 'e_head', 'gentle_ratio', 'dark_pct']:
    corpus_avg[key] = sum(profiles[f][key] for f in non_chekar) / len(non_chekar)
corpus_avg['dar_mean'] = sum(profiles[f]['dar'] for f in non_chekar) / len(non_chekar)

print(f"\n  Corpus average (excl chekar folios): qo={corpus_avg['qo']:.1f} ch={corpus_avg['ch']:.1f} "
      f"sh={corpus_avg['sh']:.1f} mon={corpus_avg['monitor']:.1f} k={corpus_avg['k_head']:.1f} "
      f"e={corpus_avg['e_head']:.1f} gentle={corpus_avg['gentle_ratio']:.0f}% dar_mean={corpus_avg['dar_mean']:.1f}")

# ═══ DISTANCE TEST ═══
print("\n\n" + "=" * 110)
print("DISTANCE TEST: Are predicted folios closer to balneum or corpus?")
print("=" * 110)

features = ['qo', 'ch', 'sh', 'monitor', 'k_head', 'e_head', 'gentle_ratio']

def euclidean_dist(p, ref):
    return sum((p[k] - ref[k])**2 for k in features) ** 0.5

print(f"\n  {'Folio':>8s} {'Dist to balneum':>16s} {'Dist to corpus':>15s} {'Closer to':>12s}")
print(f"  {'-'*55}")

for f in predicted_balneum:
    if f not in profiles:
        continue
    p = profiles[f]
    d_bal = euclidean_dist(p, bal_avg)
    d_corp = euclidean_dist(p, corpus_avg)
    closer = 'BALNEUM' if d_bal < d_corp else 'CORPUS'
    print(f"  {f:>8s} {d_bal:16.1f} {d_corp:15.1f} {closer:>12s}")

# Also show confirmed for reference
for f in confirmed_balneum:
    p = profiles[f]
    d_bal = euclidean_dist(p, bal_avg)
    d_corp = euclidean_dist(p, corpus_avg)
    print(f"  {f:>8s} {d_bal:16.1f} {d_corp:15.1f} {'(confirmed)':>12s}")

# ═══ DETAILED COMPARISON ═══
print("\n\n" + "=" * 110)
print("FEATURE-BY-FEATURE: Predicted vs Balneum vs Corpus")
print("=" * 110)

for key, label in [('qo', 'qo (THERMAL) %'), ('monitor', 'Monitor (ch+sh+...) %'),
                    ('k_head', 'k-HEAD %'), ('e_head', 'e-HEAD %'),
                    ('gentle_ratio', 'Gentle heat ratio %')]:
    print(f"\n  {label}:")
    print(f"    Balneum avg: {bal_avg[key]:6.1f}")
    print(f"    Corpus avg:  {corpus_avg[key]:6.1f}")
    for f in predicted_balneum:
        if f in profiles:
            val = profiles[f][key]
            direction = 'toward balneum' if abs(val - bal_avg[key]) < abs(val - corpus_avg[key]) else 'toward corpus'
            print(f"    {f:>8s}:     {val:6.1f}  ({direction})")

# ═══ DAR/DAL ANALYSIS ═══
print("\n\n" + "=" * 110)
print("DAR/DAL ON PREDICTED FOLIOS")
print("=" * 110)

for f in predicted_balneum:
    if f not in profiles:
        continue
    p = profiles[f]
    toks = [t for t in all_b if t.folio == f]
    print(f"\n  {f}: dar={p['dar']}, dal={p['dal']}, chekar={p['chekar']}, dain={p['dain']}")

    # Show dar lines
    for t in toks:
        if t.word in ('dar', 'dal', 'chekar'):
            line_toks = [x for x in toks if x.line == t.line]
            words = [x.word for x in line_toks]
            print(f"    L{t.line:>2s}: {' '.join(words)}")

# ═══ DARK PIPELINE OVERLAP ═══
print("\n\n" + "=" * 110)
print("DARK PIPELINE: Do predicted folios share dark MIDDLEs with confirmed balneum?")
print("=" * 110)

for f in predicted_balneum:
    if f not in profiles:
        continue
    p = profiles[f]
    shared_75 = p['dark_mids'] & profiles['f75r']['dark_mids']
    shared_84 = p['dark_mids'] & profiles['f84r']['dark_mids']
    shared_108 = p['dark_mids'] & profiles['f108r']['dark_mids']

    print(f"\n  {f}: {len(p['dark_mids'])} dark MIDDLEs")
    print(f"    Shared with f75r: {len(shared_75)}  {sorted(shared_75)[:5]}")
    print(f"    Shared with f84r: {len(shared_84)}  {sorted(shared_84)[:5]}")
    print(f"    Shared with f108r: {len(shared_108)}  {sorted(shared_108)[:5]}")

# ═══ REGIME CHECK ═══
print("\n\n" + "=" * 110)
print("REGIME AND SECTION")
print("=" * 110)

for f in confirmed_balneum + predicted_balneum:
    if f not in profiles:
        continue
    p = profiles[f]
    # Get REGIME from first token
    toks = [t for t in all_b if t.folio == f]
    print(f"  {f}: section={p['section']}, tokens={p['n']}")

# ═══ VERDICT ═══
print("\n\n" + "=" * 110)
print("VERDICT: Do predicted balneum folios look like balneum?")
print("=" * 110)

pass_count = 0
for f in predicted_balneum:
    if f not in profiles:
        continue
    p = profiles[f]
    d_bal = euclidean_dist(p, bal_avg)
    d_corp = euclidean_dist(p, corpus_avg)
    closer_to_balneum = d_bal < d_corp
    has_dar = p['dar'] > 0
    has_chekar = p['chekar'] > 0

    status = 'PASS' if closer_to_balneum and has_chekar else 'PARTIAL' if has_chekar else 'FAIL'
    if status == 'PASS':
        pass_count += 1

    print(f"\n  {f}: {status}")
    print(f"    Closer to balneum: {'YES' if closer_to_balneum else 'NO'}")
    print(f"    Has chekar: {'YES' if has_chekar else 'NO'}")
    print(f"    Has dar: {'YES' if has_dar else 'NO'}")
    print(f"    Key features: qo={p['qo']:.1f}% mon={p['monitor']:.1f}% gentle={p['gentle_ratio']:.0f}%")

print(f"\n  OVERALL: {pass_count}/4 predicted folios pass as balneum-compatible")

print("\n" + "=" * 110)
print("DONE")
print("=" * 110)
