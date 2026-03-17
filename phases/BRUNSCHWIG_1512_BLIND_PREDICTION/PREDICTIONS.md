# Phase 598b: Pre-Registered Predictions

**Locked:** 2026-03-15
**SHA-256:** `ddeee7f7252ff378b7a1ca0b964f6d38b433f7ec0f90ab17526a383b36ef058d`
**Basis:** 431 confirmed recipes from Brunschwig 1512 *de compositis* (never used in any prior fit)
**Method:** Approach A — class-level distributional predictions, no individual recipe-to-folio mapping

---

## Source Distribution (from 1512 only)

| Fire Degree | Count | % of specified |
|-------------|-------|---------------|
| Gentle (degree 1) | 227 | 83.2% |
| Elevated (degree 2-4) | 46 | 16.8% |
| Ratio | 4.9:1 gentle-to-elevated | |

| Property | Gentle (d1) | Elevated (d2-4) |
|----------|-------------|-----------------|
| Mean methods/recipe | 1.78 | 2.50 |
| Mean distill references | 3.08 | 6.23 |
| Dominant product | water (31%) | quintessence (33%) |
| Balneum Mariae rate | high | lower |

---

## Positive Predictions (5)

### P1: REGIME Distribution Matches Fire Degree Ratio

**Logic:** The 1512 book is 83% gentle processes. If the Voynich grammar encodes similar processes, its REGIME system should reflect gentle-process dominance.

**Prediction:** REGIME_1 + REGIME_2 folios constitute >65% of B folios.

**Threshold:** FAIL if gentle-REGIME fraction < 0.60.

---

### P2: k/(k+ke) Ratio Discriminates REGIME Classes

**Logic:** Gentle processes (balneum Mariae, degree 1) use sustained low heat — basic kernel engagement. Elevated processes (degree 2-3) use stronger heat — extended kernel engagement (C1225). The 1512 shows clear separation: gentle = simple methods, elevated = complex multi-method procedures.

**Prediction:** Mean k/(k+ke) ratio is HIGHER for REGIME_1 folios than for REGIME_3+4 folios.

**Threshold:** Mann-Whitney p < 0.05, directional (REGIME_1 > REGIME_3+4). FAIL if p >= 0.05 or direction reversed.

---

### P3: e→y Safe Pathway Rate Discriminates REGIME Classes

**Logic:** Gentle processes are forgiving — low risk, simple completion paths. The 1512 degree-1 recipes are overwhelmingly simple waters with straightforward distillation. Elevated processes involve multi-step refinement with higher failure risk. The e→y pathway (C1457-C1462) provides stability anchoring.

**Prediction:** Mean e→y fraction is HIGHER for REGIME_1 folios than for REGIME_3+4 folios.

**Threshold:** Mann-Whitney p < 0.05, directional. FAIL if p >= 0.05 or direction reversed.

---

### P4: Terminal r→a Routing Rate Discriminates REGIME Classes

**Logic:** Elevated processes in the 1512 book require more active intervention — monitoring apparatus under stress, managing multiple distillation steps. Terminal r→a routing (C1563) feeds the a-HEAD hazard domain. Intense processes should route more through hazard-adjacent territory.

**Prediction:** Mean r→a routing fraction is HIGHER for REGIME_3+4 folios than for REGIME_1 folios.

**Threshold:** Mann-Whitney p < 0.05, directional. FAIL if p >= 0.05 or direction reversed.

---

### P5: Procedural Complexity Correlates with ke-Depth

**Logic:** The 1512 book shows a clear complexity gradient: degree 1 recipes average 3.08 distillation references, degree 3 recipes average 6.86 (2.2x). More complex procedures need more elaborated kernel operations. If the Voynich encodes this, folios with higher procedural complexity (more tokens per line, more instruction class diversity) should show deeper ke engagement.

**Prediction:** Folio-level mean ke-depth positively correlates with folio-level instruction class entropy.

**Threshold:** Spearman rho > 0.15, p < 0.05. FAIL if rho <= 0.15 or p >= 0.05.

---

## Negative Controls (2)

### N1: Headless Compound Rate Independence

**Logic:** Headless compounds are system-level grammatical infrastructure (C1523-C1527), not process-specific. Fire degree should not affect whether the grammar uses headless forms.

**Prediction:** Headless compound fraction does NOT differ significantly between REGIME_1 and REGIME_3+4 folios.

**Threshold:** Mann-Whitney p > 0.10 (non-significant). FAIL if p < 0.05 (unexpected discrimination).

---

### N2: Atom Inventory Overlap Preservation

**Logic:** The 1512 book uses the same basic vocabulary (distill, digest, seal, etc.) regardless of fire degree — the intensity changes but the operation types don't. The Voynich should show the same: all REGIMEs share a common atom inventory.

**Prediction:** Pairwise Jaccard similarity of atom inventories between REGIME_1 folios and REGIME_3+4 folios exceeds 0.80.

**Threshold:** FAIL if Jaccard < 0.75 (would indicate separate grammars, not shared grammar with intensity modulation).

---

## Decision Logic

```
Score = count of P1-P5 that PASS

Score 5/5: STRONG_ALIGNMENT (1512 independently predicts Voynich structure)
Score 4/5: ALIGNMENT (one prediction fails, remainder consistent)
Score 3/5: WEAK_ALIGNMENT (marginal — some predictions hold)
Score 2/5 or less: NO_ALIGNMENT (1512 does not predict Voynich structure)

Negative controls:
- Both N1 and N2 PASS: Controls confirm shared grammar, not separate systems
- Either FAILS: Caveated result (unexpected discrimination undermines shared-grammar premise)
```

## Falsifiability Statement

If the Voynich grammar does NOT encode processes similar to those in Brunschwig's 1512 manual, we expect:
- P1 to fail (REGIME distribution has no reason to match fire degree ratios)
- P2-P4 to fail (REGIME classes would not discriminate on distillation-relevant features)
- P5 to fail (complexity and ke-depth would be unrelated)
- N1 to pass trivially (headless rate is grammar-internal regardless)
- N2 to pass trivially (shared grammar is already established)

A result of 2/5 or less positive predictions, with both negative controls passing, would constitute evidence AGAINST the Brunschwig alignment hypothesis.
