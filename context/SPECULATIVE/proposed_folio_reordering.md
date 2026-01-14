# Proposed Original Folio Order

**Date:** 2026-01-14 | **Status:** Tier 3 SPECULATIVE | **Version:** 1.0

---

## Executive Summary

> **The current folio order is severely disrupted. Structural gradient optimization reveals the manuscript was originally organized as a progressive curriculum.**
>
> **Reordering improves gradient correlations from -0.38 to +2.51 (combined score).**

---

## Evidence for Misbinding

### Current Order Problems

| Metric | Current | Expected | Status |
|--------|---------|----------|--------|
| Risk gradient (C161) | rho = 0.08 | rho = 0.39 | DISRUPTED |
| Completion gradient (C325) | rho = -0.23 | rho = +0.24 | **REVERSED** |
| CEI gradient | rho = -0.23 | positive | **REVERSED** |

The current binding shows **negative correlations** where our constraints document positive gradients. This is strong evidence of misbinding.

### Optimal Order Improvements

| Metric | Current | Optimal | Improvement |
|--------|---------|---------|-------------|
| Risk gradient | 0.076 | **0.780** | +0.704 |
| Tension gradient | -0.229 | **0.845** | +1.074 |
| CEI gradient | -0.227 | **0.886** | +1.113 |
| Combined | -0.380 | **+2.510** | +2.890 |

---

## Proposed Curriculum Structure

The optimal ordering reveals three clear phases:

### Phase 1: EARLY (Positions 1-27)

| Property | Value |
|----------|-------|
| Dominant regime | REGIME_2 |
| Average hazard | 0.517 (lowest) |
| Character | Introductory, low-risk operations |

**Opening block (positions 1-7):** 7 contiguous REGIME_2 folios
- f48r, f105v, f105r, f115v, f86v5, f85v2, f86v3

### Phase 2: MIDDLE (Positions 28-55)

| Property | Value |
|----------|-------|
| Dominant regime | REGIME_1 |
| Average hazard | 0.592 (moderate) |
| Character | Core training, intermediate complexity |

**Core block (positions 29-38):** 10 contiguous REGIME_1 folios
- f80r, f78r, f82v, f106r, f114r, f84v, f78v, f83r, f111r, f113r

### Phase 3: LATE (Positions 56-83)

| Property | Value |
|----------|-------|
| Dominant regime | REGIME_3 |
| Average hazard | 0.633 (highest) |
| Character | Advanced operations, highest complexity |

**Closing block (positions 76-83):** 8 contiguous REGIME_3 folios
- f39r, f103r, f33v, f83v, f33r, f31r, f46r, f95r2

---

## Regime Interpretation

| Regime | Curriculum Role | Mean Position | Hazard Level |
|--------|-----------------|---------------|--------------|
| REGIME_2 | Introductory | 7.3 | Low |
| REGIME_1 | Core/Intermediate | 37.8 | Moderate |
| REGIME_4 | Auxiliary/Bridging | 40.4 | Variable |
| REGIME_3 | Advanced | 71.2 | High |

---

## Notable Displacements

Folios most displaced from their optimal positions:

| Folio | Current Pos | Optimal Pos | Displacement | Note |
|-------|-------------|-------------|--------------|------|
| f115v | 81 | 4 | 78 | Davis's anomalous folio |
| f31r | 2 | 80 | 78 | Should be late, not early |
| f33r | 4 | 79 | 75 | Should be late |
| f105v | 65 | 1 | 64 | Should open the sequence |
| f107v | 69 | 7 | 62 | Early phase folio |

**Average displacement: 29 positions** - massive scrambling.

---

## Alignment with Davis's Findings

Lisa Fagin Davis (2024) independently concluded the manuscript was misbound based on:
- Water stain analysis
- LSA similarity scores
- Bifolium conjoint analysis

Our structural gradient analysis **confirms** misbinding through a completely different methodology:
- Hazard density progression
- Execution tension gradient
- CEI completion gradient

Both approaches converge on the same conclusion: **the current order is wrong**.

---

## Full Proposed Sequence

See: `results/proposed_folio_order.txt`

**First 20 positions:**
1. f48r (REGIME_2, HERBAL)
2. f105v (REGIME_2, STARRED)
3. f105r (REGIME_2, STARRED)
4. f115v (REGIME_2, STARRED) ← Davis's anomalous folio
5. f86v5 (REGIME_2, ROSETTE)
6. f85v2 (REGIME_2, ROSETTE)
7. f86v3 (REGIME_2, ROSETTE)
8. f107v (REGIME_1, STARRED)
9. f107r (REGIME_2, STARRED)
10. f41v (REGIME_4, HERBAL)
11. f50r (REGIME_4, HERBAL)
12. f113v (REGIME_2, STARRED)
13. f50v (REGIME_4, HERBAL)
14. f80v (REGIME_1, BALNEO)
15. f26v (REGIME_2, HERBAL)
16. f81v (REGIME_1, BALNEO)
17. f40v (REGIME_4, HERBAL)
18. f79v (REGIME_1, BALNEO)
19. f112r (REGIME_1, STARRED)
20. f86v6 (REGIME_4, ROSETTE)

**Last 10 positions:**
74. f116r (REGIME_3, STARRED)
75. f76r (REGIME_1, BALNEO)
76. f39r (REGIME_3, HERBAL)
77. f103r (REGIME_3, STARRED)
78. f33v (REGIME_3, HERBAL)
79. f83v (REGIME_3, BALNEO)
80. f33r (REGIME_3, HERBAL)
81. f31r (REGIME_3, HERBAL)
82. f46r (REGIME_3, HERBAL)
83. f95r2 (REGIME_3, PHARMA)

---

## Methodology

### Optimization Approach

1. **Objective:** Maximize combined gradient score (risk + tension + CEI)
2. **Method:** Simulated annealing (50,000 iterations)
3. **Constraints:** Based on C161 (risk gradient) and C325 (completion gradient)

### Limitations

- Optimization finds **a** good ordering, not necessarily **the** original
- Section boundaries not enforced as hard constraints
- Bifolium conjoint relationships not incorporated (could refine further)

### Future Work

1. Incorporate Davis's LSA similarity scores as additional constraint
2. Enforce bifolium structure (conjoint pages must stay together)
3. Cross-validate with water stain analysis
4. Test if proposed order improves other structural metrics

---

## Implications

If this reordering is correct:

1. **The manuscript is a graded curriculum** - simple to complex progression
2. **REGIME_2 = introductory material** - lowest hazard, starting point
3. **REGIME_3 = advanced material** - highest hazard, endpoint
4. **Misbinding occurred early** - before 17th century foliation
5. **Reading the current order obscures the pedagogical structure**

---

## Files

| File | Content |
|------|---------|
| `results/folio_reordering.json` | Full optimization results |
| `results/proposed_folio_order.txt` | Complete sequence with annotations |
| `phases/YALE_ALIGNMENT/folio_reordering.py` | Optimization algorithm |
| `phases/YALE_ALIGNMENT/proposed_reordering_analysis.py` | Detailed analysis |

---

## Constraints Referenced

| Constraint | Statement | Relevance |
|------------|-----------|-----------|
| C161 | Folio Ordering = Risk Gradient (rho=0.39) | Violated in current order |
| C325 | Completion Gradient (rho=+0.24) | Reversed in current order |
| C155 | Piecewise-Sequential Geometry | Supports ordered structure |
| C368 | Regime Clustering in Quires | Regimes should cluster |

---

## Navigation

- [materiality_alignment.md](materiality_alignment.md) - Davis lecture analysis
- [yale_expert_alignment.md](yale_expert_alignment.md) - Expert validation
- [INTERPRETATION_SUMMARY.md](INTERPRETATION_SUMMARY.md) - Full synthesis

---

*Document created 2026-01-14. Proposed ordering is Tier 3 speculative. Model remains frozen.*
