# Phase 637: Dark Pipeline Material Identification

**Status:** COMPLETE
**Verdict:** MATERIAL_IDENTIFICATION_SUPPORTED
**Constraints:** C1939-C1942

---

## Research Question

Can specific dark pipeline MIDDLEs be identified as encoding specific materials, apparatus, or processes by cross-referencing their folio distribution against known recipe content from 19 matched folio-recipe pairs?

## Background

Phase 631 (C1901-C1907) established that dark pipeline MIDDLEs are PREFIX-locked identification vocabulary with section-modulated atom compositions. Phase 634 (C1925-C1929) established cross-folio vocabulary patterns (dar=material introduction, chekar=quality check). This phase extends identification from token-level (dar, chekar) to the dark pipeline layer — the 300 unmatched MIDDLEs that encode substance/apparatus identity.

## Novel Contribution

1. Manual reading of 466 dark tokens across 19 folios against Latin/English recipe text
2. Two material identifiers validated corpus-wide: fch=mercury (∞ enrichment), cs=gold (17.5x)
3. Three functional classes of dark MIDDLEs: equipment, process, material
4. Currier A cross-reference: f58r/f58v identified as master catalog folios
5. Comprehensive dark pipeline dictionary: 152 MIDDLEs with candidate readings

---

## Scripts

| Script | Location | What |
|--------|----------|------|
| `_dark_pipeline_inventory.py` | RECIPE_FOLIO_CORRESPONDENCE/scripts/ | Per-folio dark token inventory with line context |
| `_dark_cross_folio.py` | RECIPE_FOLIO_CORRESPONDENCE/scripts/ | Cross-folio dark MIDDLE co-occurrence analysis |
| `_test_dark_candidates.py` | RECIPE_FOLIO_CORRESPONDENCE/scripts/ | Corpus-wide validation of 7 candidates |
| `_dark_currier_a_crossref.py` | RECIPE_FOLIO_CORRESPONDENCE/scripts/ | A-system RI derivative cross-reference |

---

## Constraints

### C1939: fch encodes mercury/mercury-water (Tier 3)

The dark MIDDLE fch (flag.adjust.watch) appears on all 6 folios matched to mercury-involving recipes and on zero folios matched to non-mercury recipes among the 19-folio matched set. Corpus-wide: 19/82 Currier B folios contain fch. Currier A cross-reference: 5 exact matches + 16 RI derivatives (ofch x8 dominant) across 19 A folios, 79% in same sections as B folios with fch. The atom composition "flag for cautious monitored handling" describes mercury's operational profile — volatile, toxic, requiring constant vigilance.

The 13 unmatched B folios containing fch are predictions: they should involve mercury processing. Two (f103v, f85r1) are already confirmed reverse-blind matches involving mercury.

- Scope: B, A, dark pipeline, fch, mercury, C1901, C1903
- Metrics: matched_enrichment=∞ (6 vs 0). corpus_folios=19/82. A_tokens=21. A_folios=19. section_overlap=79%. predictions=13.
- Tier 3 because: depends on Tier 3 recipe-folio assignments for the mercury/non-mercury classification.

### C1940: cs encodes gold (Tier 3)

The dark MIDDLE cs (adjust.sequence) shows 17.5x enrichment on folios matched to gold-involving recipes vs non-gold recipes. Corpus-wide: 9/82 Currier B folios contain cs. f84r (gold dissolution) has 3 occurrences at L1 (introduction), L28 (mid-putrefaction), L30 (near completion) — mapping the arc of gold treatment. f84v (verso of same leaf) has 2 occurrences. Currier A: 1 exact + 2 RI derivatives (cshe, csee), sparse.

The atom composition "adjust.sequence" = sequential staged treatment, describing gold's multi-step processing character.

- Scope: B, dark pipeline, cs, gold, C1901
- Metrics: enrichment=17.5x. corpus_folios=9/82. f84r=3x. f84v=2x(same_leaf). A_tokens=3.
- Tier 3 because: depends on Tier 3 recipe-folio assignments.

### C1941: Dark pipeline MIDDLEs divide into three functional classes (Tier 3)

Manual reading of 466 dark tokens across 19 recipe-matched folios reveals three functional classes:

**Equipment identifiers** (lch, lk, eed): Appear on 10+ matched folios regardless of recipe. Encode shared apparatus (distillation assembly, fire/furnace, vessel cooling). lch=16/19 folios, lk=15/19. Atom compositions describe equipment handling profiles.

**Process identifiers** (cth, eke, ksh, tsh, ro, ep, lsh, eet): Appear on 3-9 folios wherever a specific technique is used. Encode operational techniques (state-transition monitoring, precision testing, sequential thermal observation, cohobation, fermentation, phase-boundary establishment). cth confirmed on 5+ folios at state-transition points.

**Material identifiers** (fch, cs, eckh, rai + folio-exclusives): Encode specific materials by handling profile. Concentrated on folios using that material. fch=mercury (19/82), cs=gold (9/82), eckh=volatile liquid (18/82), rai=metallic product (11/82). 16+ folio-exclusive MIDDLEs encode recipe-specific materials (loch=lunaria, rol=tincture ferment, fsh=lute compound, alod=aludel).

All three classes use the same 18-atom compositional system. The atoms describe WHAT the identified thing requires operationally, not what it IS chemically.

- Scope: B, dark pipeline, C1901, C1906, C171
- Metrics: tokens_analyzed=466. unique_middles=152. equipment=3. process=11. material=8+16_exclusive. folios=19.
- Tier 3 because: class assignments depend on recipe-derived interpretations.

### C1942: f58r/f58v are A-system master catalog folios (Tier 3)

Currier A folios f58r (366 tokens, Section T) and f58v (365 tokens, Section T) contain A-system records (exact matches + RI derivatives) for 6 of 9 tested dark pipeline material/equipment identifiers: fch (mercury), lch (apparatus), lk (fire), cth (state-transition), eet (cooling transfer), tsh (cohobation). No other A folio shows this degree of dark MIDDLE catalog concentration. f58r alone has: fch x3 + lch x5 + lk x5 + cth x2 + eet x1 + tsh x1 = 17 dark-related A tokens.

This is consistent with the A system's role as a vocabulary catalog (C1499): f58r/f58v catalog the identification vocabulary that B folios deploy during execution.

- Scope: A, T, dark pipeline, C1499, C1903
- Metrics: f58r_dark_related=17. dark_middles_represented=6/9. f58r_A_tokens=366. f58v_A_tokens=365. section=T.
- Tier 3 because: "master catalog" interpretation depends on dark MIDDLE identifications which are Tier 3.

---

## Documentation

The comprehensive Dark Pipeline Dictionary is at `context/DARK_PIPELINE_DICTIONARY.md`. It contains:
- Tier 1-4 readings for all 152 dark MIDDLEs found on matched folios
- Corpus-wide validation results for 7 candidates (6 supported, 1 failed)
- Folio-exclusive material candidates
- Predictions for unmatched folios based on fch and cs distribution
- Currier A cross-reference summary

---

## Summary

Phase 637 demonstrates that the dark pipeline's identification vocabulary can be partially decoded through recipe-folio correspondence. Two material identifiers (fch=mercury, cs=gold) show strong enrichment patterns validated corpus-wide. The dark pipeline divides into equipment, process, and material identifiers — all using the same atom compositional system to describe operational handling profiles. The A-system master catalog on f58r/f58v independently confirms the material vocabulary through cross-system RI derivative presence. All findings are capped at Tier 3 due to dependence on Tier 3 recipe-folio assignments.
