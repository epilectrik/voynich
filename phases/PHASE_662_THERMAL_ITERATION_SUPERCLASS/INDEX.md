# Phase 662: Thermal-Iteration Superclass Folio-Binary Partition

**Phase:** 662
**Status:** COMPLETE — VERDICT INCONCLUSIVE (weak directional, underpowered)
**Started:** 2026-04-26
**Pre-reg commit:** d3fb478
**Prior:** Phase 661 (DISTILLATION verb folio-binary, INCONCLUSIVE/reversed)

## Result

Aggregated DISTILLATION + PUTREFACTION + IMBIBITION + REFINEMENT into thermal-iteration superclass per locked rule. Tested ke/ek ratio.

| Group | n | ke/ek mean |
|---|:---:|---:|
| Superclass-positive | 12 | 14.73 |
| Superclass-negative | 2 | 8.64 |

| Metric | Value |
|---|---|
| Cohen's d | +0.458 (just below 0.5 SUPPORTED bar) |
| p(predicted direction) | 0.3411 |
| Verdict | INCONCLUSIVE |

## What this teaches (combined with Phase 661)

| Granularity | Direction | Cohen's d | Verdict |
|---|---|---|---|
| Verb-category narrow (DISTILLATION only) | REVERSED | -0.62 | INCONCLUSIVE-reversed (Phase 661) |
| Operational-mode broader | PREDICTED | +0.46 | INCONCLUSIVE (Phase 662, underpowered) |

The signal IS in the predicted direction at operational-mode granularity. The means flipped (8.6 vs 14.7 in Phase 662 vs 17.8 vs 11.7 in Phase 661) when aggregation matched the VMS encoding level.

But thermal-iteration verbs are TOO COMMON in matched chapters (12/14 = 86%). Only III.15 (ferment conversion) and III.27 (furnace specification) lack them. N=2 negatives is structurally underpowered.

## Granularity-mismatch finding (combined Phase 661+662)

**Folio-binary partition with N=14 matched-pair table is structurally exhausted as a methodology.** The signal exists at operational-mode granularity (Phase 662 direction confirms), but folio-aggregate sampling can't extract it cleanly with available N when the partition is too unbalanced.

This is consistent with C1735 (Brunschwig fire-degree intensity tracks VMS structure), C1872 (k_ratio inverse-thermal proxy), and C1226 (ke/ek = process-context conditioning) — all of which already operationalize thermal mode at sub-folio resolution. The folio-aggregate level is the wrong scale.

## What remains untested (NOT committed)

The methodologically-honest next step is paragraph-level partition: use C1959 layout-rho to map verb-ordinal → folio-paragraph signature. That gives N × P data points instead of 14, and can survive the unbalanced partition. This is crazy-expert's original recommendation, deferred to Phase 663+ candidate (not committed tonight per expert-advisor: "you'd compound granularity questions").

## Constraint candidate (NOT registered)

**Tier 3 candidate:**
> Folio-aggregate ke/ek ratio shows weak directional alignment with thermal-iteration verb presence in matched Catalan chapters (Cohen's d=0.46, p=0.34). The signal direction confirms when aggregation matches VMS operational-mode granularity (12/14 superclass-positive vs 2/14 negative) but does not reach SUPPORTED threshold due to underpowered negative group.

This is descriptive only. Not registered. The replicable next-step is paragraph-level testing.

## What did NOT change

- No constraints registered or downgraded.
- Verb corpus (Phase 660) still useful at paragraph resolution.
- f82r/III.22, f76r/II.18, etc. matched-pair table unchanged.
- C1969 (window-density specificity for f75r ×9) unaffected.

## Summary

Phase 662 closes the folio-binary verb-partition methodology. Direction confirms at operational-mode granularity but sample size insufficient for statistical significance. Paragraph-level testing is the natural next phase but explicitly deferred per expert guidance.
