# C673: CC Trigger Sequential Independence

**Status:** VALIDATED | **Tier:** 0 | **Phase:** B_LINE_SEQUENTIAL_STRUCTURE | **Scope:** B

## Finding

CC trigger type (daiin/ol/ol_d) shows **no sequential memory** across lines. Self-transition fraction = 0.390 vs permuted baseline = 0.395. Permutation p=1.0. The CC trigger for each line is selected independently of the previous line's CC trigger.

## Scope note (2026-06)

**CROSS-VOICE; predates Mode A/B (C1258).** A within-Mode-B retest (crude y-terminal≥50% proxy) found CC-trigger self-transition 0.711 vs within-folio-Mode-B shuffle 0.723 (z=−1.9, p=0.98) — consistent with no within-voice CC coupling, but **inconclusive** given proxy noise (a crude-proxy null attenuates toward the null; cf. C1341 ~20% contextual mode modulation). Does not overturn or extend C673; a positive within-voice claim would require faithful C1231 centroid mode assignment. See `context/SYSTEM/NEGATIVE_AUDIT.md` Disposition 5.

## Method

Extract first CC token per line, classify to subgroup (CC_DAIIN=class 10, CC_OL=class 11, CC_OL_D=class 17). Build transition matrix across adjacent lines within folios. Permutation test: shuffle CC sequence within folio 1000 times. Chi-square on transition matrix.

## Key Numbers

| Metric | Value |
|--------|-------|
| Lines with CC trigger | 789/2401 (32.9%) |
| CC distribution | DAIIN=249, OL=320, OL_D=220 |
| Self-transition fraction | 0.390 |
| Permuted baseline | 0.395 |
| Permutation p | 1.000 |
| Chi-square | 9.95, dof=4, p=0.041 |

## Transition Matrix

| From \ To | DAIIN | OL | OL_D |
|-----------|-------|-----|------|
| DAIIN | 36.9% | 36.0% | 27.1% |
| OL | 30.6% | 44.9% | 24.5% |
| OL_D | 25.1% | 42.4% | 32.5% |

## Interpretation

The CC trigger is re-selected each line without reference to the previous line's choice. The marginal chi-square (p=0.041) reflects the unequal base rates (OL=320 is most frequent), not sequential memory. Combined with C606 (CC trigger predicts within-line EN subfamily with V=0.246), this means CC routing is intra-line only: each line's CC trigger independently determines that line's execution parameters.

## Provenance

- Script: `phases/B_LINE_SEQUENTIAL_STRUCTURE/scripts/line_sequential_coupling.py` (Test 4)
- Extends: C606 (CC trigger → EN subfamily within-line), C608 (no lane coherence p=0.963)
