"""PHASE 743 - frequency-matched control for the labels-more-novel finding (BOTH experts' decisive gate).

Confound: "novel MIDDLE" (not in A/B inventory) is monotone in frequency; label (S) tokens use rarer
MIDDLEs than ring-text (R) (C525/C760/C914). So the 15.2% vs 8.1% novelty gap may be "labels use rarer
vocab" (already established) re-measured, NOT an S/R-axis effect.

CONTROL: match on MIDDLE frequency within AZC. (1) stratify by freq bin, report within-bin S vs R novelty
gap; (2) downsample R to S's freq-bin distribution, recompute aggregate gap, 200 iters, 95% CI.
KILL: if frequency-matched gap CI crosses 0 -> frequency/label-vocab artifact (C525/C760/C914 re-measured)
-> document null, do NOT register. Plus per-folio consistency (guard against few-folio-driven pooled p).
"""
import sys, functools, json
from collections import defaultdict, Counter
from pathlib import Path
import numpy as np
print = functools.partial(print, flush=True)
sys.path.insert(0, '.')
from scripts.voynich import Transcript, Morphology

OUT = Path('phases/PHASE_743_AZC_RING_SEQUENCE/results'); OUT.mkdir(parents=True, exist_ok=True)
tx = Transcript(); morph = Morphology()
ZF = json.load(open('results/azc_folio_features.json')).get('folios', {})
ZODIAC = {f for f, d in ZF.items() if d.get('section') == 'Z'}

A_mid = set(); B_mid = set()
for t in tx.currier_a():
    w = (t.word or '').strip()
    if w and '*' not in w and (m := morph.extract(w).middle): A_mid.add(m)
for t in tx.currier_b():
    w = (t.word or '').strip()
    if w and '*' not in w and (m := morph.extract(w).middle): B_mid.add(m)
novel = lambda m: m is not None and m not in A_mid and m not in B_mid

# AZC-internal MIDDLE frequency (all AZC, for stable freq estimate)
azc_freq = Counter()
for t in tx.azc(h_only=True):
    w = (t.word or '').strip()
    if w and '*' not in w and (m := morph.extract(w).middle): azc_freq[m] += 1

# zodiac S/R tokens
toks = {'S': [], 'R': []}   # each: (folio, middle, novel, freq)
for t in tx.azc(h_only=True):
    if t.folio not in ZODIAC: continue
    w = (t.word or '').strip()
    if not w or '*' in w or not t.placement: continue
    g = 'S' if t.placement[0] == 'S' else ('R' if t.placement[0] == 'R' else None)
    if not g: continue
    m = morph.extract(w).middle
    toks[g].append((t.folio, m, novel(m), azc_freq.get(m, 0)))

def nrate(lst): return np.mean([x[2] for x in lst]) if lst else float('nan')
print(f"raw novelty: S={nrate(toks['S']):.3f} (n={len(toks['S'])})  R={nrate(toks['R']):.3f} (n={len(toks['R'])})  "
      f"gap={nrate(toks['S'])-nrate(toks['R']):+.3f}")

# (1) stratify by AZC-freq bin
def fbin(f): return '1' if f <= 1 else ('2-3' if f <= 3 else ('4-9' if f <= 9 else '10+'))
print("\nwithin-frequency-bin novelty (the confound control):")
print(f"  {'bin':5s} {'S n':>5s} {'S nov':>6s} {'R n':>5s} {'R nov':>6s} {'gap':>6s}")
strat = {}
for b in ['1', '2-3', '4-9', '10+']:
    S = [x for x in toks['S'] if fbin(x[3]) == b]; R = [x for x in toks['R'] if fbin(x[3]) == b]
    if S and R:
        strat[b] = (len(S), nrate(S), len(R), nrate(R), nrate(S) - nrate(R))
        print(f"  {b:5s} {len(S):5d} {nrate(S):6.3f} {len(R):5d} {nrate(R):6.3f} {nrate(S)-nrate(R):+6.3f}")
    else:
        print(f"  {b:5s} {len(S):5d} {'--':>6s} {len(R):5d} {'--':>6s}  (one arm empty)")

# (2) downsample R to S's freq-bin distribution, 200 iters
Sbins = Counter(fbin(x[3]) for x in toks['S'])
Rby = defaultdict(list)
for x in toks['R']: Rby[fbin(x[3])].append(x)
rng = np.random.default_rng(0); gaps = []
sNov = nrate(toks['S'])
for _ in range(200):
    samp = []
    ok = True
    for b, k in Sbins.items():
        pool = Rby.get(b, [])
        if len(pool) < 1: ok = False; break
        idx = rng.choice(len(pool), size=k, replace=len(pool) < k)
        samp.extend(pool[i] for i in idx)
    if not ok: continue
    gaps.append(sNov - nrate(samp))
gaps = np.array(gaps)
lo, hi = np.percentile(gaps, [2.5, 97.5])
print(f"\nFREQUENCY-MATCHED gap (R downsampled to S freq-dist, {len(gaps)} iters):")
print(f"  median gap = {np.median(gaps):+.3f}   95% CI [{lo:+.3f}, {hi:+.3f}]")
crosses0 = lo <= 0 <= hi
print(f"  -> {'CI CROSSES 0: frequency artifact (C525/C760/C914 re-measured) -> DOCUMENT NULL, do NOT register' if crosses0 else 'gap SURVIVES frequency matching -> genuine S/R-axis effect'}")

# (3) per-folio consistency
pf = []
for fol in ZODIAC:
    S = [x for x in toks['S'] if x[0] == fol]; R = [x for x in toks['R'] if x[0] == fol]
    if S and R: pf.append(nrate(S) - nrate(R))
n_pos = sum(1 for g in pf if g > 0)
print(f"\nper-folio: S novelty > R in {n_pos}/{len(pf)} folios (gaps {[round(g,2) for g in sorted(pf)]})")

res = {'raw_gap': round(nrate(toks['S']) - nrate(toks['R']), 3),
       'stratified': {b: {'S_n': v[0], 'S_nov': round(v[1], 3), 'R_n': v[2], 'R_nov': round(v[3], 3),
                          'gap': round(v[4], 3)} for b, v in strat.items()},
       'freq_matched_gap_median': round(float(np.median(gaps)), 3),
       'freq_matched_CI': [round(float(lo), 3), round(float(hi), 3)],
       'CI_crosses_0': bool(crosses0),
       'per_folio_S_gt_R': f"{n_pos}/{len(pf)}",
       'verdict': 'FREQUENCY_ARTIFACT_document_null' if crosses0 else 'SURVIVES_freq_match'}
(OUT / 'freq_matched_control.json').write_text(json.dumps(res, indent=2))
print(f"\nSaved {OUT / 'freq_matched_control.json'}")
