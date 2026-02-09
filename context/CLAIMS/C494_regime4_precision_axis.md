# C494: REGIME_4 Precision Axis

**Tier:** 3 | **Status:** CLOSED | **Scope:** REGIME_INTERPRETATION

---

## Statement

> REGIME_4 encodes precision-constrained execution (tight control, narrow tolerance) rather than intensity level. Standard procedures fail REGIME_4 constraints; precision variants pass.

---

## Evidence

**Test:** `phases/BRUNSCHWIG_TEMPLATE_FIT/precision_variant_test.py`

### REGIME_4 Characteristics

| Property | Value | Meaning |
|----------|-------|---------|
| Escape rate (qo) | 0.107 (lowest) | Lowest thermal intensity |
| HIGH_IMPACT | Forbidden | Precision excludes aggressive intervention |
| max_k_steps | 3 | Controlled energy operations |
| min_LINK_ratio | 25% | High monitoring overhead |

> **Terminology Note (2026-01-30):** "Escape rate" here refers to qo_density (qo-prefixed tokens,
> Classes 32/33/36), which measures thermal/energy operation intensity. This is distinct from
> FQ density (FREQUENT_OPERATOR classes 9/13/14/23), which measures grammatical escape/flow
> control operators. REGIME_4 has LOWEST qo_density (gentle heat) but HIGHEST FQ_density
> (tight tolerances requiring high error correction). These orthogonal measures support the
> precision interpretation: gentle processing with rigorous error handling.

### Test Results

| Procedure Type | REGIME_4 Fit | LINK Ratio |
|----------------|--------------|------------|
| Standard First Degree | NO | 22% |
| **Precision First Degree** | **YES** | **43%** |
| Standard Second Degree | NO | 19% |
| Precision Second Degree | NO | 38% |
| **Precision Intense** | **YES** | **44%** |

**Summary:**
- Standard procedures: 0/2 fit REGIME_4
- Precision procedures: 2/3 fit REGIME_4

---

## Interpretation Correction

### Old (RETIRED)
"REGIME_4 = forbidden/intense procedures"

This never sat right because REGIME_4 appears in 25/83 folios - too frequent to be "forbidden."

### New (CONFIRMED)
**REGIME_4 = precision-constrained execution regime**

The fourth axis is control tightness, not intensity:
- A gentle procedure requiring exact timing fits REGIME_4
- A violent procedure without precision does NOT fit REGIME_4

---

## Four-Axis Model (Corrected)

| REGIME | Selection Criterion | Brunschwig Analog |
|--------|---------------------|-------------------|
| REGIME_2 | Low intensity, introductory | First degree (flowers) |
| REGIME_1 | Moderate, forgiving | Second degree (herbs) |
| REGIME_3 | High intensity, aggressive | Third/Fourth degree |
| **REGIME_4** | **Precision, tight control** | **Any degree requiring exact timing** |

---

## Real-World Examples (REGIME_4)

- Volatile aromatic distillation (gentle but exact timing)
- Close-boiling fraction separation (narrow temperature window)
- Heat-sensitive material processing (must not overshoot)

---

## Empirical Confirmation: Section H Data (C494.a)

**Finding:** Section H provides empirical evidence for the "gentle but precise" case.

| Section | REGIME_4 % | ch/sh ratio | High-fire % | Profile |
|---------|------------|-------------|-------------|---------|
| H | **43.8%** | **1.86** | **3.9%** | Gentle + Precise |
| S | 43.0% | 2.00 | 7.1% | Aggressive + Precise |
| B | 10.0% | 0.96 | 7.5% | Balanced |

**Section H shows:**
- Highest REGIME_4 concentration among Currier B sections (43.8%)
- Highest ch/sh ratio (1.86) = precision mode dominates
- LOWEST high-fire suffix rate (3.9%) = gentle processing

**Cross-analysis within ch-prefix tokens:**

| Section | Within-ch high/low ratio | Interpretation |
|---------|--------------------------|----------------|
| S | 0.43 | Precision + high fire |
| B | 0.34 | Balanced |
| H | **0.20** | **Precision + low fire** |

Even when using precision mode (ch), Section H stays at low fire-degree.

**Interpretation:** Section H documents "volatile aromatic distillation" - procedures requiring:
- Gentle heat (low fire-degree)
- Precise temperature control (ch-dominance)
- High monitoring (REGIME_4 concentration)

This confirms C494's claim that precision and intensity are orthogonal. Section H is the empirical instantiation of "gentle but exact timing."

**Source:** REGIME_SEMANTIC_INTERPRETATION phase (2026-01-25)

---

## Provenance

- **Phase:** BRUNSCHWIG_TEMPLATE_FIT
- **Date:** 2026-01-14
- **Files:** `phases/BRUNSCHWIG_TEMPLATE_FIT/precision_variant_test.py`

---

## Cross-References

| Constraint | Relationship |
|------------|--------------|
| C490 | AGGRESSIVE exclusion (orthogonal to precision) |
| C458 | Design freedom (hazard clamped, recovery free) |
| C493 | Grammar embedding (precision fits) |

---

## Navigation

<- [C493_brunschwig_grammar_embedding.md](C493_brunschwig_grammar_embedding.md) | [INDEX.md](INDEX.md) ->
