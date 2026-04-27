# Phase 662 — Pre-Registration

**Locked:** 2026-04-26
**Type:** Confirmatory hypothesis test
**Prior:** Phase 661 (DISTILLATION folio-binary, INCONCLUSIVE/reversed); pre-survey suggested verb-category granularity is too narrow.

---

## Why this exists

Phase 661 confirmed that Catalan verb-category DISTILLATION does not carve VMS folio-aggregate signatures — the partition direction reverses (means 11.67 distill+ vs 17.81 distill-) because thermally-intensive non-distillation recipes (lunaria maceration, element separation, mercury cohobation) share VMS thermal-marker signatures with distillation recipes.

This phase tests the **thermal-iteration superclass** hypothesis: Catalan verb categories that share an operational-mode signature (sustained thermal monitoring) can be aggregated into a higher abstraction level that DOES carve VMS signatures cleanly.

Both expert agents (in consultation tonight) converged on this as the right pivot.

---

## Hypothesis

**H:** Folios matched to recipes carrying ≥1 verb from the **thermal-iteration superclass** show higher ke/ek ratio than folios matched to recipes carrying NONE of those verbs.

**H₀:** Superclass-positive and superclass-negative folios do not differ in ke/ek ratio.

---

## Locked decisions

### 1. Thermal-iteration superclass (locked aggregation rule)

The superclass is the union of these Phase 660 verb categories:
- **DISTILLATION** (distil·la, destil·lar, distillació, distillaràs)
- **PUTREFACTION** (putrefer, putrifició, macerar, digerir, digestió)
- **IMBIBITION** (enbeure, lava, banya, untar)
- **REFINEMENT** (rectifica, mundificar, purificar, depura)

Rationale: each represents a sustained thermal-monitoring operation per existing constraints (C1226 ke/ek = process-context conditioning; C1735 Brunschwig fire-degree; C1872 k_ratio inverse-thermal proxy).

**Aggregation rule:** A matched chapter is **superclass-positive** if its Catalan text contains ≥1 verb instance from any of these 4 categories per Phase 660 VERB_CORPUS.json.

This rule is locked BEFORE running. Adding/removing categories after the test would be HARKing.

### 2. Partition (locked, computed deterministically from rule)

Will be computed at script run time from VERB_CORPUS.json. No post-hoc folio reassignment.

Pre-test partition prediction:
- Superclass-positive should include all DISTILLATION-positive folios PLUS f82r (III.22 lunaria maceration → PUTREFACTION + IMBIBITION verbs likely present), f76r (II.18 element separation → may have REFINEMENT), and any others.
- Superclass-negative would be only matched chapters with NO thermal-iteration verbs at all (vessel/furnace specs, ferment conversion).

The actual partition is determined by the verb corpus, not by my prediction.

### 3. Test signature (locked, single-candidate)

**Primary endpoint:** ke/ek ratio per folio (same as Phase 661). One candidate, no exploration. Per expert-advisor: avoid qokee composite (qo-PREFIX C1300/C1538 confound). Per crazy-expert recommendation, ke/ek is the cleanest theoretically-motivated single feature.

### 4. Falsification criterion (locked, per crazy-expert)

If superclass-positive vs superclass-negative effect size on ke/ek is < 0.5 SD (Cohen's d), the VMS doesn't encode thermal mode at this granularity either, and the verb-corpus partition methodology is exhausted at folio resolution.

### 5. Statistical test (locked)

- One-sided Mann-Whitney U via 10,000-permutation null. Predicted direction: positive > negative.
- Cohen's d on raw means.

### 6. Verdicts

| Verdict | Criterion |
|---|---|
| SUPPORTED | predicted direction + p ≤ 0.05 + Cohen's d ≥ 0.5 |
| DIRECTIONAL | predicted direction + p ≤ 0.20 + Cohen's d ≥ 0.3 |
| INCONCLUSIVE | predicted direction but p > 0.20 OR d < 0.3 |
| REVERSED-NULL | OPPOSITE direction p ≤ 0.10 |
| FALSIFIED | OPPOSITE direction p ≤ 0.05 |

### 7. What this phase does NOT do

- No paragraph-level analysis (deferred).
- No multi-feature scoring.
- No re-categorization of folios after testing.
- No constraint registration without ALSO ensuring Cohen's d ≥ 0.5 (effect-size bar, not just p-value).

---

## Honest expectation

If thermal-iteration superclass IS the right granularity, the means should re-align in the predicted direction with effect size d ≥ 0.5. f82r (ke/ek=45) and f112r (ke/ek=42) — both extreme outliers in Phase 661 — should be reclassified into superclass-positive in this test, eliminating the within-group outliers that reversed Phase 661's direction.

If still null/reversed at this abstraction level, the conclusion is: VMS folio-aggregate signatures don't carve at any external-corpus verb-category granularity. The verb corpus would still be useful at paragraph resolution (Phase 663+) but not at folio aggregation.

This is the test the pivot was designed for.
