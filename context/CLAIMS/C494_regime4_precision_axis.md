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
| Escape rate | 0.107 (lowest) | Least forgiving of deviation |
| HIGH_IMPACT | Forbidden | Precision excludes aggressive intervention |
| max_k_steps | 3 | Controlled energy operations |
| min_LINK_ratio | 25% | High monitoring overhead |

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
