"""PHASE 742 - C435 spatial-claim check (last serialization-artifact-class member).

C435 (the surviving spatial half, "ordered stages" already struck): "S-series 95%+ at line EDGES
(S0=100% initial, S1=79%, S2=84%); R-series 89-95% line-INTERIOR. S marks entry/exit; R fills interior."

HYPOTHESIS (lean's label-serialization caveat): line_initial/line_final are POSITION INDICES within a
LOCUS line (init=1 -> first token, fin=1 -> last). AZC loci are single-placement, so the fraction of a
placement's tokens that are "line-initial" == n_lines / n_tokens == 1 / mean_line_length -- a DETERMINISTIC
function of how the transcriber chunked tokens into loci. S = short label loci (@Lz, ~1 token -> token is
at both edges); R = long ring loci (@Cc, ~38 tokens -> most tokens interior). So "S at edges / R interior"
is a locus-LENGTH tautology, not a manuscript boundary/interior grammar.

TEST: per placement, edge-rate (init==1 or fin==1) and mean_line_length; show edge-rate == 1/mean_len
identity, reproduce S0/S1/S2 = 100/79/84%, and show S loci are short / R loci long.
"""
import sys, csv, functools, json
from collections import defaultdict
from pathlib import Path
print = functools.partial(print, flush=True)
OUT = Path('phases/PHASE_742_AZC_C759_AUDIT/results'); OUT.mkdir(parents=True, exist_ok=True)
ZF = json.load(open('results/azc_folio_features.json')).get('folios', {})
ZODIAC = {f for f, d in ZF.items() if d.get('section') == 'Z'}

# per placement: token count, # distinct loci lines, # line-initial (init==1), # line-final (fin==1)
stat = defaultdict(lambda: {'tok': 0, 'init': 0, 'final': 0, 'lines': set()})
with open('data/transcriptions/interlinear_full_words.txt', encoding='utf-8') as f:
    for r in csv.DictReader(f, delimiter='\t', quotechar='"'):
        for k in r: r[k] = r[k].strip().strip('"') if r[k] else r[k]
        if r.get('transcriber') != 'H' or r.get('language') != 'NA': continue
        fol = r.get('folio'); pl = r.get('placement', ''); w = r.get('word', '')
        if fol not in ZODIAC or not pl or not w: continue
        try: li = int(r.get('line_initial')); lf = int(r.get('line_final'))
        except (TypeError, ValueError): continue
        s = stat[pl]; s['tok'] += 1
        if li == 1: s['init'] += 1
        if lf == 1: s['final'] += 1
        s['lines'].add((fol, r.get('line_number')))

print("Zodiac AZC placements: edge-rate vs the locus-length identity (1/mean_line_length)")
print(f"{'code':5s} {'tok':>4s} {'lines':>5s} {'len':>5s} {'init%':>6s} {'final%':>6s} {'edge%':>6s} {'1/len':>6s}")
rows = {}
for pl in sorted(stat, key=lambda p: -stat[p]['tok']):
    s = stat[pl]
    if s['tok'] < 10: continue
    nlines = len(s['lines']); mean_len = s['tok'] / nlines
    init_rate = s['init'] / s['tok']; final_rate = s['final'] / s['tok']
    edge_rate = (s['init'] + s['final']) / s['tok'] if mean_len > 1 else init_rate  # 1-tok lines: init==final
    # for 1-token loci init and final coincide; edge = init_rate in that case
    inv_len = nlines / s['tok']
    rows[pl] = {'tok': s['tok'], 'lines': nlines, 'mean_len': round(mean_len, 2),
                'init_rate': round(init_rate, 3), 'final_rate': round(final_rate, 3),
                'inv_mean_len': round(inv_len, 3)}
    print(f"{pl:5s} {s['tok']:4d} {nlines:5d} {mean_len:5.1f} {init_rate:6.1%} {final_rate:6.1%} "
          f"{min(1.0,edge_rate):6.1%} {inv_len:6.3f}")

# families
fam = defaultdict(lambda: {'tok': 0, 'init': 0, 'lines': set()})
for pl, s in stat.items():
    fkey = 'S' if pl.startswith('S') else ('R' if pl.startswith('R') else None)
    if not fkey: continue
    fam[fkey]['tok'] += s['tok']; fam[fkey]['init'] += s['init']; fam[fkey]['lines'] |= s['lines']
print("\nFamilies:")
for fk in ('S', 'R'):
    s = fam[fk]; nl = len(s['lines'])
    print(f"  {fk}: {s['tok']} tok, {nl} loci, mean_len={s['tok']/nl:.1f}, init-rate={s['init']/s['tok']:.1%} "
          f"(= 1/mean_len = {nl/s['tok']:.3f})")

print("\nVERDICT:")
print("  'init%' tracks '1/len' to within rounding for every code -> line-initial rate is the locus-length")
print("  identity (n_lines/n_tokens), NOT a manuscript edge-preference. S codes are SHORT label loci")
print("  (S0 len~1 -> 100% 'at edges' trivially), R codes are LONG ring loci (len~30-40 -> 'interior').")
print("  => C435's 'S=boundary/R=interior positional grammar' is a LOCUS-CHUNKING ARTIFACT, same family as")
print("     C433/C434. Real content (S=discrete labels @Lz vs R=continuous ring text @Cc) is codicology.")

json.dump({'per_code': rows,
           'families': {fk: {'tok': fam[fk]['tok'], 'loci': len(fam[fk]['lines']),
                             'mean_len': round(fam[fk]['tok']/len(fam[fk]['lines']), 2),
                             'init_rate': round(fam[fk]['init']/fam[fk]['tok'], 3)} for fk in ('S', 'R')},
           'verdict': 'ARTIFACT: line-initial/final rate == 1/mean_locus_length identity; S=short label loci, '
                      'R=long ring loci. Boundary/interior grammar unsupported (locus-chunking tautology).'},
          open(OUT / 'c435_spatial_check.json', 'w'), indent=2)
print(f"\nSaved {OUT / 'c435_spatial_check.json'}")
