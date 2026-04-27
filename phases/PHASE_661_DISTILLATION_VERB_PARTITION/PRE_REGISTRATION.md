# Phase 661 — Pre-Registration

**Locked:** 2026-04-26
**Type:** Confirmatory hypothesis test (cross-folio partition)
**Honest expectation:** Pre-survey suggests REVERSED direction. This pre-registration is locked anyway to produce a documented bound on Catalan-verb-category-to-VMS-folio-signature granularity.

---

## Context

Phase 660 produced a SISMEL Catalan operator-verb corpus with 18 categories. DISTILLATION is the most procedurally-specific category (83 procedural vs 14 Theorica = 5.9x). Among 14 matched folio↔chapter pairs, 9 are DISTILLATION-positive (Catalan recipe contains ≥1 DISTILLATION verb) and 5 are negative.

A pre-survey of candidate VMS-side signatures showed the predicted direction is REVERSED. Specifically: the ke/ek ratio is HIGHER on DISTILLATION-negative folios than positive ones (driven by f82r/lunaria-maceration and f76r/element-separation, both non-distillation but thermally intensive recipes).

**The expected null is itself the test.** Per expert-advisor: "documented null on Catalan-verb-category → VMS-folio-signature at folio-binary granularity strengthens C171/C1121 (semantic ceiling, domain irrecoverability) and bounds the granularity at which external corpus categories carve VMS. That's a constraint, not a failure."

---

## Hypothesis

**H:** DISTILLATION-positive matched folios show higher ke/ek ratio than DISTILLATION-negative matched folios.

**H₀ (null):** No directional difference between groups in ke/ek ratio at the folio-aggregate level.

**Falsifiable:** if observed effect is opposite predicted direction at p ≤ 0.10, claim is rejected (null with reversal). If effect is in predicted direction at p ≤ 0.10, claim is supported.

---

## Locked decisions

### 1. Partition (locked)

| Group | Folios | Source |
|---|---|---|
| DISTILLATION-positive (9) | f75r, f112r, f84r, f79r, f103r, f81v, f112v, f116r, f107r | matched chapters with ≥1 DISTILLATION verb in Phase 660 corpus |
| DISTILLATION-negative (5) | f82v, f76r, f82r, f76v, f77v | matched chapters with 0 DISTILLATION verbs |

Verb-category presence determined by Phase 660 `VERB_CORPUS.json` records with `category=='DISTILLATION'` aggregated to chapter level (any subrecipe in chapter).

### 2. Test signature (locked, single-candidate)

**Primary endpoint:** ke/ek ratio = (count of folio tokens containing 'ke' substring) / (max(1, count of folio tokens containing 'ek' substring))

Compute per folio. Aggregate per group as mean.

**Secondary endpoint (reported, not load-bearing):** -edy ending percentage = 100 × (count tokens ending in 'edy') / total tokens.

### 3. Statistical test (locked)

Mann-Whitney U test (one-sided, predicted direction: positive group higher). 10,000-permutation null. Report p-value.

### 4. Verdict (locked)

| Verdict | Criterion |
|---|---|
| SUPPORTED | predicted direction + p ≤ 0.05 |
| DIRECTIONAL | predicted direction + p ≤ 0.20 |
| INCONCLUSIVE | no clear direction OR predicted direction with p > 0.20 |
| REVERSED-NULL | OPPOSITE direction with p ≤ 0.10 |
| FALSIFIED | OPPOSITE direction with p ≤ 0.05 |

### 5. What this phase does NOT do

- No multi-candidate signature exploration.
- No paragraph-level analysis (deferred to Phase 662+).
- No re-categorization of folios after testing.
- No constraint registration on positive direction without ALSO running Phase 662 to confirm via thermal-iteration superclass.

---

## Honest expectation

REVERSED-NULL or FALSIFIED, based on pre-survey data:
- Distill+ ke/ek mean: 11.67
- Distill- ke/ek mean: 17.81

The result is informative either way. Reversed → confirms that Catalan verb-category granularity doesn't match VMS folio-aggregate encoding (constraint candidate). Null → same conclusion. Supported → would be surprising and trigger re-examination of pre-survey.
