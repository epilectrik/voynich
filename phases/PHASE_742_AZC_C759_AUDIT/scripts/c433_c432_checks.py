"""PHASE 742 - C433 + C432 checks (serialization-artifact audit, batch 2).

C433 "Zodiac Block Grammar": placement codes occur in contiguous blocks; self-transition >98%
  (R1->R1 99.9%, S1->S1 100%, ...); "locks for dozens of tokens, stricter than Currier B grammar."
  HYPOTHESIS: this is the same serialization artifact as C434/C436 -- placements are RECORDED as
  contiguous blocks, so self-transition is forced to ~1 - n_blocks/n_tokens (the floor). The
  "stricter than Currier B" comparison is invalid (B self-transition is on reading-order token
  sequence; AZC is on transcriber block-order). TEST: per folio, count blocks per placement;
  show self-transition rate == the block floor, with ~1 block per (folio,placement).

C432 "Ordered Subscript Exclusivity": subscripted placements (R1-R4,S0-S3,C1-C2) occur EXCLUSIVELY
  in Zodiac AZC, absent from flat AZC. This is PRESENCE/ABSENCE per folio -- ORDER-INDEPENDENT,
  NOT a sequence statistic -> not the serialization artifact. TEST: cross-tab subscript presence x
  section (Z vs A vs C). If subscripts are Z-exclusive, the categorical diagnostic SURVIVES.
"""
import sys, csv, functools, json
from collections import defaultdict, Counter
from pathlib import Path
print = functools.partial(print, flush=True)
OUT = Path('phases/PHASE_742_AZC_C759_AUDIT/results'); OUT.mkdir(parents=True, exist_ok=True)
TX = 'data/transcriptions/interlinear_full_words.txt'
ZF = json.load(open('results/azc_folio_features.json')).get('folios', {})
SECTION = {f: d.get('section') for f, d in ZF.items()}

# load AZC tokens in FILE ORDER per folio, with full placement code
ridx = 0; byf = defaultdict(list)
with open(TX, encoding='utf-8') as f:
    for r in csv.DictReader(f, delimiter='\t', quotechar='"'):
        for k in r: r[k] = r[k].strip().strip('"') if r[k] else r[k]
        ridx += 1
        if r.get('transcriber') != 'H' or r.get('language') != 'NA': continue
        pl = r.get('placement', ''); w = r.get('word', '')
        if not pl or not w: continue
        byf[r['folio']].append((ridx, pl, w))

# ===================== C433: self-transition = block floor? =====================
print("=" * 64 + "\nC433: Zodiac Block Grammar -- self-transition vs block-serialization floor")
# per (folio, placement): count blocks (maximal runs in file order) and tokens
self_by_code = defaultdict(lambda: [0, 0])     # code -> [self_trans, total_trans]
blocks_by_code = defaultdict(lambda: [0, 0])   # code -> [n_blocks, n_tokens]
total_self = total_trans = 0
for fol, toks in byf.items():
    seq = [pl for _, pl, _ in sorted(toks, key=lambda x: x[0])]
    # transitions
    for a, b in zip(seq, seq[1:]):
        total_trans += 1
        if a == b: total_self += 1
        self_by_code[a][1] += 1
        if a == b: self_by_code[a][0] += 1
    # blocks per code (maximal contiguous runs)
    prev = None
    for pl in seq:
        blocks_by_code[pl][1] += 1
        if pl != prev: blocks_by_code[pl][0] += 1
        prev = pl
overall = total_self / total_trans
print(f"  overall self-transition (all AZC, file order): {total_self}/{total_trans} = {overall:.4f}")
print(f"  per major code:  code  self-trans   blocks/tokens   tokens-per-block")
for code in sorted(self_by_code, key=lambda c: -self_by_code[c][1]):
    st, tt = self_by_code[code]; nb, nk = blocks_by_code[code]
    if nk < 30: continue
    print(f"     {code:4s}  {st}/{tt}={st/tt if tt else 0:.3f}    {nb}blk/{nk}tok   {nk/nb:.1f} tok/block"
          f"   floor=1-{nb}/{nk}={1-nb/nk:.3f}")
# the floor identity: overall self-transition >= 1 - (total_blocks)/(total_tokens)
tot_blocks = sum(nb for nb, _ in blocks_by_code.values()); tot_tokens = sum(nk for _, nk in blocks_by_code.values())
print(f"\n  TOTAL blocks={tot_blocks}, tokens={tot_tokens}; mean {tot_tokens/tot_blocks:.1f} tokens/block")
print(f"  Each placement code is recorded as ~1 contiguous block per folio -> self-transition is FORCED.")
print(f"  observed {overall:.3f} vs block-serialization floor 1-{tot_blocks}/{tot_tokens}={1-tot_blocks/tot_tokens:.3f}"
      f"  -> {'AT FLOOR (artifact, same as C434)' if overall <= (1-tot_blocks/tot_tokens)+0.01 else 'above floor'}")

# ===================== C432: subscript exclusivity (order-independent) =====================
print("\n" + "=" * 64 + "\nC432: Ordered Subscript Exclusivity -- presence x section (ORDER-INDEPENDENT)")
def is_subscripted(pl): return len(pl) >= 2 and pl[0] in 'RSC' and pl[1].isdigit()
sec_sub = defaultdict(lambda: [0, 0])   # section -> [subscripted_tokens, total_tokens]
folio_has_sub = {}
for fol, toks in byf.items():
    sec = SECTION.get(fol, '?')
    nsub = sum(1 for _, pl, _ in toks if is_subscripted(pl))
    sec_sub[sec][0] += nsub; sec_sub[sec][1] += len(toks)
    folio_has_sub[fol] = nsub > 0
print(f"  subscripted-token share by section:")
for sec in sorted(sec_sub):
    s, t = sec_sub[sec]
    print(f"     section {sec}: {s}/{t} = {s/t if t else 0:.1%} subscripted tokens")
print(f"  folios WITH any subscripted placement, by section:")
by_sec_folio = defaultdict(lambda: [0, 0])
for fol, has in folio_has_sub.items():
    sec = SECTION.get(fol, '?'); by_sec_folio[sec][1] += 1; by_sec_folio[sec][0] += int(has)
for sec in sorted(by_sec_folio):
    h, n = by_sec_folio[sec]
    print(f"     section {sec}: {h}/{n} folios have subscripts")
z_share = sec_sub.get('Z', [0, 1]); nonz_sub = sum(sec_sub[s][0] for s in sec_sub if s != 'Z')
print(f"\n  Zodiac subscripted tokens: {z_share[0]}; non-Zodiac subscripted tokens: {nonz_sub}")
c432_holds = nonz_sub == 0
print(f"  C432 'subscripts exclusively Zodiac' -> {'HOLDS (0 non-Z subscripts) -- ORDER-INDEPENDENT categorical diagnostic, SURVIVES' if c432_holds else f'PARTIAL ({nonz_sub} non-Z subscripts exist)'}")

json.dump({
  'C433': {'overall_self_transition': round(overall, 4), 'total_blocks': tot_blocks, 'total_tokens': tot_tokens,
           'block_floor': round(1 - tot_blocks / tot_tokens, 4), 'mean_tokens_per_block': round(tot_tokens / tot_blocks, 1),
           'verdict': 'ARTIFACT (self-transition at block-serialization floor, same as C434) -> RETRACT grammar framing'
                      if overall <= (1 - tot_blocks / tot_tokens) + 0.01 else 'above floor -- investigate',
           'per_code': {c: {'self_trans': self_by_code[c][0], 'total': self_by_code[c][1],
                            'blocks': blocks_by_code[c][0], 'tokens': blocks_by_code[c][1]}
                        for c in self_by_code if blocks_by_code[c][1] >= 30}},
  'C432': {'section_subscript_share': {s: [sec_sub[s][0], sec_sub[s][1]] for s in sec_sub},
           'folios_with_subscripts': {s: by_sec_folio[s] for s in by_sec_folio},
           'nonZodiac_subscripted_tokens': nonz_sub, 'order_independent': True,
           'verdict': 'SURVIVES (Zodiac-exclusive categorical diagnostic, order-independent)' if c432_holds
                      else f'PARTIAL: {nonz_sub} non-Z subscripted tokens'},
}, open(OUT / 'c433_c432_checks.json', 'w'), indent=2)
print(f"\nSaved {OUT / 'c433_c432_checks.json'}")
