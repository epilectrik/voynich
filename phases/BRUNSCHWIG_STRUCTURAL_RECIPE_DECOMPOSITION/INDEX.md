# Phase 617: Brunschwig Structural Recipe Decomposition

**Status:** COMPLETE
**Verdict:** NO_STRUCTURAL_PREDICTION (0/3 pre-registered H-tests)
**Constraints:** C1806-C1807
**Date:** 2026-03-20

---

## Research Question

Phases 598 and 600 mapped Brunschwig recipe categories (fire degree, method class, closure demand) to folio-level apparatus statistics. Both failed (WEAK and 0/4). Phase 616 (C1799-C1805) revealed the encoding hierarchy: PREFIX composition (r=0.476) → vocabulary (absorbed) + paragraph deployment (r=0.163 independent). Phase 617 asks whether Brunschwig recipe **internal structure** (complexity, monitoring density, method diversity) predicts Voynich **paragraph-level** features within Stars section, where REGIME alignment is validated (C1735).

## Design

### Brunschwig Side
- 387 classified recipes (first_book + third_book)
- Fire classes: gentle (degree 1, n=205), elevated (degree 2+, n=40), unclassed (n=142)
- Metrics: complexity_score, monitoring_density (conditional co-occurrence within 15-word window of temporal markers), n_methods

### Voynich Side
- Stars section: R1 (n=10) vs R3 (n=12)
- Per-folio features: mean paragraph body length, OPERATION-Iteration zone fraction, h_ratio, e-to-y rate, headless rate, token count

## Results

| Test | Description | Metric | Result | Verdict |
|------|-------------|--------|--------|---------|
| H1 | Body length R3 > R1 | U=34, p=0.960 | R1 mean=98.3, R3 mean=69.0 (reversed) | FAIL |
| H2 | Op-Iter fraction R3 > R1 | U=76, p=0.160 | R3 mean=0.50, R1 mean=0.35 (correct dir) | FAIL |
| H3a | Monitoring gentle > elevated | U=3331, p=0.983 | Elevated=0.00298 > Gentle=0.00184 (reversed) | FAIL |
| H3b | h_ratio R1 > R3 | U=0, p=1.000 | R3=0.219 >> R1=0.101 (reversed, perfect separation) | FAIL |
| PC1 | e-to-y R1 > R3 (C1735 replication) | U=112, p=0.0003, r=-0.867 | R1=0.182 > R3=0.104 | PASS |
| N1 | Token count two-sided null | U=92, p=0.041 | R1=501 > R3=441 | FAIL |
| N2 | Headless rate two-sided null | U=23, p=0.016 | R3=0.076 > R1=0.053 | FAIL |

**Directional consistency:** 1/3 H-tests with correct pre-registered direction.

## Scripts

| Script | Runtime | Output |
|--------|---------|--------|
| `scripts/structural_recipe_decomposition.py` | ~2.3s | `results/structural_recipe_decomposition_results.json` |

## Key Findings

### 1. Pre-registration Direction Error in H3 (C1806)

The pre-registered direction for H3a/H3b was derived from a misreading of C1750 (sublimation h_ratio=0.235 vs distillation h_ratio=0.113). The derivation assumed "gentle procedures = more monitoring." But sublimation is the MORE demanding procedure — C1750 actually shows that complex/demanding procedures have higher h_ratio. The corrected chain:

- Elevated Brunschwig recipes have more monitoring keywords (H3a empirical result: 0.00298 vs 0.00184)
- R3 (mapped to elevated via C1735) has dramatically higher h_ratio (U=0, all 12 R3 values > all 10 R1 values)
- Both directions consistent with C1750/C1752: demanding procedures → more monitoring

The h_ratio U=0 result is the strongest Brunschwig-Voynich signal outside C1735 (ey_rate). However, since the direction was pre-registered incorrectly, the phase verdict remains NO_STRUCTURAL_PREDICTION per project pre-registration discipline. The corrected finding is registered as C1806 for use in future pre-registered tests.

### 2. Brunschwig Monitoring Density: Elevated > Gentle (C1807)

Empirical fact about Brunschwig recipes: elevated-fire recipes (degree 2+) have higher monitoring keyword density than gentle-fire recipes (degree 1). Both conditional (0.00298 vs 0.00184) and raw (0.00444 vs 0.00328) measures agree. Complex procedures require more checkpoint instructions (watch color, test with finger, etc.). This corrects the assumption that gentle = more monitoring-intensive.

### 3. H1 Invalid per C1241

Expert review identified that H1 (paragraph body length as complexity proxy) is structurally invalid: C1241 establishes header-body length independence. Paragraph length is not driven by operational complexity. This test should not have been included.

### 4. H2 Directionally Correct but Underpowered

R3 has higher OPERATION-Iteration zone fraction (0.50 vs 0.35) as predicted, but p=0.16 with n=10 vs n=12. Suggestive but not significant.

### 5. Negative Controls Fail

Both negative controls differ significantly between R1 and R3 (token count p=0.04, headless rate p=0.02). REGIME differences permeate more features than the null hypothesis assumed — expected given C1404 (sections are REGIME allocation policies) and C1574 (headless ecology is folio-parameterized).

## Verdict Rationale

NO_STRUCTURAL_PREDICTION: 0/3 pre-registered H-tests pass, 1/3 correct direction, positive control passes (machinery works). The phase verdict is scored strictly as pre-registered, consistent with Phases 598 (WEAK) and 600 (0/4).

The h_ratio finding (U=0, perfect separation) and Brunschwig monitoring density ordering are registered as new constraints (C1806-C1807) with explicit provenance noting the pre-registration direction error. These findings are real and informative but require future pre-registered confirmation before use as prediction anchors.

## Brunschwig-Voynich Bridge Status

After three failed bridge phases (598 WEAK, 600 0/4, 617 0/3), the surviving Brunschwig-Voynich alignment remains:
- **C1735**: Thermal intensity → ey_rate within Stars (p=0.0007, replicated Phase 617 PC1 p=0.0003)
- **C1736**: Within-folio thermal gradient (rho=0.303)
- **C1740**: Safety substitution within Stars (ii_rate R1<R3, p=0.026)
- **C1750/C1752**: Monitoring-thermal axis (sublimation > distillation h_ratio)
- **C1806** (NEW, post-hoc): h_ratio REGIME gradient within Stars (U=0)
- **C1807** (NEW): Brunschwig elevated > gentle monitoring density

The bridge ceiling is axis-level alignment, not recipe-level specificity. C1569 (within-section folio specificity absent in domain tuning) and C1799 (vocabulary absorbed by PREFIX) explain why: folio identity is encoded through domain MIX (PREFIX/HEAD), not within-domain parameters that map to Brunschwig recipe differences.

## Dependencies

- Phase 580 (apparatus manifold)
- Phase 598 (C1735, thermal intensity → ey_rate)
- Phase 600 (C1739-C1740, closure-response alignment)
- Phase 616 (C1799-C1805, encoding hierarchy)
- C1750/C1752 (monitoring-thermal axis)
- C1241 (header-body length independence)
- C1398 (paragraph zone assignments)
