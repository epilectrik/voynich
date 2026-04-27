# Phase 663: Paragraph-Level Thermal-Iteration Superclass Partition

**Phase:** 663
**Status:** COMPLETE — VERDICT REVERSED-NULL (signal direction flipped at paragraph resolution)
**Started:** 2026-04-26
**Pre-reg commit:** 766b78a

## Result

| | n paragraphs | mean ke/ek |
|---|:---:|---:|
| Superclass-positive | 95 | 5.63 |
| Superclass-negative | 9 | 8.41 |
| Cohen's d | | -0.572 (REVERSED) |
| p(predicted) | | 0.9387 |
| p(reversed) | | 0.0654 |

**Verdict:** REVERSED-NULL. Direction flipped from Phase 662 (folio-aggregate, predicted +0.46) to Phase 663 (paragraph distribution, reversed -0.57).

## Sensitivity finding (NOT the pre-registered hypothesis)

The pre-registered sensitivity check within superclass-positive folios produced a striking incidental pattern:

| Subgroup | n paragraphs | mean ke/ek |
|---|:---:|---:|
| **CONFIRMED matches** (f75r, f76r, f84r) | 12 | **9.74** |
| Supported matches | 83 | 5.03 |
| Superclass-negative | 9 | 8.41 |

CONFIRMED-match paragraphs have ~2x higher ke/ek than supported-match paragraphs. The supported tier appears to dilute the signal. This is descriptive only — not registered as a constraint.

## Combined Phase 661+662+663 lesson

| Phase | Resolution | Direction | Cohen's d | Verdict |
|---|---|---|---|---|
| 661 | Folio-aggregate (DISTILLATION narrow) | REVERSED | -0.62 | INCONCLUSIVE |
| 662 | Folio-aggregate (superclass broad) | PREDICTED | +0.46 | INCONCLUSIVE (underpowered) |
| 663 | Paragraph distribution (superclass broad) | REVERSED | -0.57 | REVERSED-NULL |

The signal direction was unstable across granularity levels. Folio-aggregate at superclass granularity was directional-correct but underpowered. Paragraph-distribution at the same partition flipped direction.

The match-quality sensitivity finding suggests the matched-pair table is heterogeneous: CONFIRMED matches share a structural signature that supported matches dilute. Tests that pool both tiers as "positive" produce unstable signal.

## Methodologically-honest conclusion

**The verb-corpus folio-binary partition methodology is exhausted, even at paragraph resolution.** Three pre-registered tests (661, 662, 663) all returned INCONCLUSIVE or REVERSED-NULL on this approach.

What survives: the sensitivity finding that CONFIRMED-tier matches differ structurally from supported-tier matches. This points to a different next move — match-quality-stratified analysis, or verb-position-matching tests within CONFIRMED matches only.

## What did NOT change

- No constraints registered or downgraded
- No matched-pair table revisions
- C1969 unaffected
- Verb corpus (Phase 660) infrastructure remains valid; just doesn't produce signal at this partition shape

## Untested next moves (NOT committed)

- Verb-position-matching: paragraph at thermal-iter verb position vs paragraph not at thermal-iter position, WITHIN folios. N=12 CONFIRMED paragraphs may be enough if effect is strong.
- Match-quality stratification: re-run partition tests using CONFIRMED matches only.
- Different signature entirely: ke/ek may not be the right feature for paragraph-resolution tests.

These are notes, not commitments. The honest read is that the verb-corpus is built but the partition tests aren't producing constraints with the available matched-pair sample.
