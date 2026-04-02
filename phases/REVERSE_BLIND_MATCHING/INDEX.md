# Phase 636: Reverse-Blind Matching and Atom Refinement

**Status:** COMPLETE
**Verdict:** PREDICTIVE_MATCHING_CONFIRMED
**Constraints:** C1934-C1938

---

## Research Question

Can recipe-derived predictions identify matching folios from a pool of unmatched candidates? And can the 7-axis discrimination battery resolve competing atom glosses beyond what recipe comparison achieves?

## Background

Phases 628-635 established recipe-folio matching via post-hoc analysis: examine a folio, compare to its matched recipe, confirm correspondence. This phase tests whether the process works in REVERSE: read a recipe, derive structural predictions, scan unmatched folios, identify the match. Additionally, the 7-axis discrimination battery addresses the limitation identified during atom gloss validation — recipe comparison validates HEAD atoms but cannot discriminate MOD/TERM atom glosses.

## Novel Contribution

1. Reverse-blind matching: recipe → predictions → scan → match (predictive, not confirmatory)
2. d=do/execute replaces d=mark via 7-axis discrimination battery (4-point margin)
3. Recto/verso pairs encode sequential operations on the same physical leaf
4. Multi-chapter folios: short related procedures combined (f80r = Ch21-25M)
5. Blind structural characterizations of unmatched folios (predictions banked for future testing)
6. 37 documented folios (up from 30 at Phase 635)

---

## Scripts

| Script | Location | What |
|--------|----------|------|
| `s1_discrimination_battery.py` | ATOM_GLOSS_RECIPE_VALIDATION/scripts/ | 7-axis atom gloss battery |
| `_blind_read_f115r.py` | RECIPE_FOLIO_CORRESPONDENCE/scripts/ | Fully blind atom read |
| `_blind_read_f112v.py` | RECIPE_FOLIO_CORRESPONDENCE/scripts/ | Partial blind atom read |
| `_blind_read_f83r.py` | RECIPE_FOLIO_CORRESPONDENCE/scripts/ | Partial blind atom read |
| `_blind_read_f106r.py` | RECIPE_FOLIO_CORRESPONDENCE/scripts/ | Blind characterization (unmatched) |
| `_blind_read_f103v.py` | RECIPE_FOLIO_CORRESPONDENCE/scripts/ | Reverse blind confirmation |
| `_blind_read_f43v.py` | RECIPE_FOLIO_CORRESPONDENCE/scripts/ | Reverse blind confirmation |
| `_reverse_blind_ch27p.py` | RECIPE_FOLIO_CORRESPONDENCE/scripts/ | Reverse blind scan (imbibition) |
| `_reverse_blind_ch29p.py` | RECIPE_FOLIO_CORRESPONDENCE/scripts/ | Reverse blind scan (troubleshooting) |
| `_reverse_blind_ch30p.py` | RECIPE_FOLIO_CORRESPONDENCE/scripts/ | Reverse blind scan (multiplication) |
| `_reverse_blind_ch19p.py` | RECIPE_FOLIO_CORRESPONDENCE/scripts/ | Reverse blind scan (washing) |
| `_reverse_blind_batch.py` | RECIPE_FOLIO_CORRESPONDENCE/scripts/ | Batch scan (Ch10P, Ch12P, Ch26P, Ch21P) |
| `_reverse_blind_balneum_pair.py` | RECIPE_FOLIO_CORRESPONDENCE/scripts/ | Small balneum folio search |
| `_test_prep_prefixes.py` | RECIPE_FOLIO_CORRESPONDENCE/scripts/ | Prep verb falsification |
| `_check_f_fermentation.py` | RECIPE_FOLIO_CORRESPONDENCE/scripts/ | German verb test (f-atom) |
| `_check_sr_german.py` | RECIPE_FOLIO_CORRESPONDENCE/scripts/ | German verb test (s, r atoms) |
| `_check_m_mixing.py` | RECIPE_FOLIO_CORRESPONDENCE/scripts/ | German verb test (m-atom) |

---

## Constraints

### C1934: d=do/execute replaces d=mark (Tier 2, revises C1195)

7-axis discrimination battery scores d="do/execute" at 12/14, 4 points above d="mark" at 8/14. Axes: (1) OPERATION category shift +55.6% matches "do/execute" not "mark"; (2) near-inner modifier scope appropriate for execution; (3) y-terminal selects d because executed actions have natural endpoints; (4) d+"complete" tautological with y="end" (eliminates "complete"); (5) d is 2.11x B-enriched (execution register matches action verb); (6) ed="cool+do"=discharge, od="arrange+do"=collect, dy="do+end"=done — all compound readings improve; (7) d avoids f, consistent with non-redundant functional roles. Other 4 atoms confirmed: o=arrange (13/14), c=adjust (12/14), p=pause (13/14), s=sequence (12/14).

- Scope: B, atom, d, C1195, C1394
- Metrics: d_score=12/14. margin=4. B_enrichment=2.11x. o=13. c=12. p=13. s=12.

### C1935: Reverse-blind matching produces predictive folio identifications (Tier 2)

Recipe-derived structural predictions (dar count, gentle heat ratio, dominant PREFIX, folio size) identify matching folios from pools of 49 unmatched candidates. Tested on 5 Practica chapters: f103v/Ch27P scored 10/11 in scan, confirmed 6/7 at atom level; f43v/Ch29P scored 7/11, confirmed 4/6; f105v/Ch30P scored 9/11 (not cold-read); f46r/Ch19P scored 9/11 (not cold-read); f108v/Ch10P scored 7/8 (not cold-read). The confirmed f103v match is the first PREDICTIVE (not confirmatory) recipe-folio identification in the project.

- Scope: B, PL, matching, C1882, C1933
- Metrics: ch27p_scan=10/11. ch27p_confirmed=6/7. ch29p_scan=7/11. ch29p_confirmed=4/6. candidates_scanned=49.

### C1936: Recto/verso pairs encode sequential operations on the same leaf (Tier 2)

Multiple independently-matched recto/verso pairs encode sequential or related procedures: f66r/v (Ch24P fixation → Ch26P inceration), f103r/v (Ch16M ferment multiplication → Ch27P Mercury imbibition), f108r/v (Ch16P element separation → Ch10P silver dissolution). The sequential pairing preserves procedural logic across the page turn, indicating deliberate organizational design rather than arbitrary binding.

- Scope: B, manuscript organization, C1927, C1930
- Metrics: paired_leaves=3. sequential_confirmed=3of3.

### C1937: Multi-chapter folios combine related short procedures (Tier 2, extends C1927)

Short related procedures from the same source section are combined onto single folios. f80r encodes Ch21-25M (5 animal ash distillation chapters, each 1-2 sentences). Ch10P and Ch11P (simple balneum dissolutions, 3-4 sentences each) appear to be encoded within f108v rather than on separate folios. The manuscript's organizing unit is operational scope, not source chapter count. This explains the Phase 628 null result: paragraph count does not correlate with recipe step count because multiple recipes may share a folio.

- Scope: B, manuscript organization, C1927
- Metrics: f80r_chapters=5(Ch21-25M). ch10p_ch11p_combined_in_f108v.

### C1938: Blind atom reading correctly predicts recipe type on untouched folios (Tier 2)

Fully blind atom-level reading of f115r (never profiled, never decoded) correctly predicted: fixation recipe type (confirmed by Ch28P "repeat sublimation until fixed"), non-balneum thermal regime (confirmed: "three fires"), multiple material additions (confirmed: 3:3:3:1.5 formula + red oil), testing-dominant (confirmed: "until you see it melt like wax"). Score: 6/8 YES + 2 PARTIAL. Additional blind tests: f112v (7/8+1P, partial blind), f83r (3/8+3P+2I, recipe too short). Prediction accuracy tracks with recipe detail level.

- Scope: B, atom, blind test, C1394, C1897
- Metrics: f115r_score=6of8. f112v_score=7of8. f83r_score=3of8(recipe_too_short). fully_blind=f115r.

---

## Additional Findings (not constraints)

### German verb mapping: 7 atoms confirmed, 4 tested and rejected

7 atom characters map to German alchemical verb initials: k=Kochen, e=Erkalten, h=Hüten, i=Iterieren, t=Tragen, o=Ordnen, p=Pausieren. These were already correctly glossed from internal structural analysis — the German mapping confirms but does not extend them. 4 atoms tested against recipe-specific operation concentration: f=Fermentieren (1.00x, dead flat), s=Sublimieren (1.61x, weak), r=Rektifizieren (0.97x, dead flat), d=Destillieren (0.82x, inverted). The MOD/TERM atoms are grammar atoms that don't track operation types.

### Compound prefixes (pch, tch, dch, fch, lch) are NOT preparation verbs

Recipe-folio comparison across 10 matched folios: pch does NOT concentrate on grinding folios (f83r pch=4 vs f103r pch=7). lch dominates uniformly regardless of recipe type. Compound prefixes are paragraph-opening structural markers (6.5x par-initial enrichment), not preparation operation referents. Definitively closes the F-BRU-012 prep verb hypothesis (GLOSSING.md Test 22 SUPERSEDED notation updated).

### Atom gloss validation: 18 folios, zero contradictions for LOCKED atoms

All 8 LOCKED atoms (k, e, h, y, i, n, a, t) produce correct readings against every recipe checked. Compositional rules identified: (1) e/k gradient — opposite thermal poles create modulation, not addition; (2) a = directional threshold — terminal determines direction (a+r = outward/yield, a+n = inward/bind). Recipe comparison validates HEAD atoms and PREFIXes but cannot discriminate MOD/TERM atoms (d, o, c, p, s) — the 7-axis battery was developed to address this gap.

### Folio characterizations banked for future testing

f106r: blind structural characterization (two-phase thermal, dar=2, P14 sh=11 monitoring endpoint, predicted distillation/dissolution). Predictions recorded in folio notes, testable against future matching.

---

## Summary

Phase 636 extends the recipe-folio matching methodology from confirmatory to predictive. The reverse-blind approach (recipe → predictions → scan → match) successfully identified f103v as Ch27P imbibition with 6/7 atom-level confirmation — the first predictive match in the project. The 7-axis discrimination battery resolved the d-atom gloss (do/execute replaces mark) where recipe comparison could not. The recto/verso pairing and multi-chapter folio findings reveal deliberate organizational logic in the manuscript's binding. 37 folios documented, with 7 new reverse-blind candidates awaiting cold-read confirmation.
