# C1392: f-Atom Marking Flag Profile

**Tier:** 2
**Scope:** B
**Phase:** F_ATOM_SEMANTIC_DEEP_DIVE (Phase 502)
**Depends on:** C1195 (atom gloss confidence tiers), C1190 (MIDDLE additive composition), C1209 (slot syntax)

## Constraint

Atom f (gloss: "flag") is the #2 MARKING atom in the system (12.009x enrichment, behind only p at 12.033x). f is the purest identification atom: 100% of f-initial vocabulary falls in the HT/UN layer and NONE enters the 49-class execution grammar. This structural role is unique among all atoms and distinguishes f from fellow MARKING atoms p (88.7% AXM) and d (execution grammar participant). All f-compounds are uniformly MARKING (90.9%) with no category diversification — the strongest compound uniformity of any tested atom. The fch compound (23 tokens, glossed "note") is the dominant structure, with f->c junction at 10.28x enrichment. H1 "flag" is the decisive best hypothesis (F-F10: 4/4 discriminants, F-F12: 5/5 convergence). f remains PLAUSIBLE due to data sparsity (215 tokens) but the gloss is strongly supported.

## Key Evidence

| Property | Value | Significance |
|----------|-------|-------------|
| MARKING enrichment | 12.009x (rank #2) | Behind only p (12.033x) |
| 49-class grammar | 0% (100% HT/UN) | Never enters execution grammar |
| Compound uniformity | 90.9% MARKING | Strongest of any tested atom |
| f->c junction | 10.28x enrichment | fch is compound unit |
| CHSH+f MARKING | 82.8% (11.75x) | Comparable to CHSH+p 87.4% |
| H1 discriminants | 4/4 | NEUTRAL 100%, R4 1.58x, line-1 27.9% |
| Compositional convergence | 5/5 FULL match | All compounds MARKING |
| Line-1 enrichment | 7.00x (27.9%) | Folio opener gallows role |
| Battery score | 6/12 (6P, 4F, 1I, 1NA) | Data ceiling, not structural |

## Structural Role

f is a **pure identification/annotation atom** operating exclusively in the HT/UN layer:
- It marks/flags items without participating in the execution grammar
- This is distinct from p (MARKING within AXM execution) and d (MARKING within execution grammar)
- f's gallows role (folio opener, position 0.30, C865) is consistent with identification/flagging at document boundaries
- The fch compound ("note") combines flagging (f) with adjustment (c) and watching (h) — annotating for later attention

## Falsification

Would be falsified if f-initial tokens were shown to participate in the 49-class execution grammar, or if f-compounds were found to carry non-MARKING category signals.

## Provenance

- `phases/F_ATOM_SEMANTIC_DEEP_DIVE/scripts/p_f01_category_profile.py` through `p_f12_compositional_convergence.py` — 12 prediction test scripts
- `phases/F_ATOM_SEMANTIC_DEEP_DIVE/results/f_atom_prediction_results.json` — structured results
