# C898 - A PP Internal Structure

**Tier:** 2 (Structural) | **Scope:** A | **Phase:** A_PP_INTERNAL_STRUCTURE

## Statement

Currier A PP (procedural payload) vocabulary has significant internal organization that refines C234's aggregate "position-free" finding:

1. **Positional preferences** within A lines (KS p<0.0001)
2. **Scale-free co-occurrence network** with hub structure (CV=1.69)
3. **Bimodal position distribution** with EARLY and LATE peaks

---

## C898.a: PP Positional Grammar

PP tokens exhibit consistent positional preferences within A lines, despite C234's aggregate position-freedom:

### LATE-Biased (position 0.6-0.85)

| Type | Elements | Mean Position |
|------|----------|---------------|
| MIDDLEs | m, am, d, dy, hy, l, al, s, in | 0.62-0.85 |
| PREFIXes | da, ka, sa, al | 0.60-0.66 |

### EARLY-Biased (position 0.3-0.4)

| Type | Elements | Mean Position |
|------|----------|---------------|
| MIDDLEs | or | 0.35 |
| PREFIXes | pch, dch, sch | 0.31-0.38 |

### Position Distribution

| Zone | % of PP | Interpretation |
|------|---------|----------------|
| 0.0-0.1 (INITIAL) | 13.9% | Opening concentration |
| 0.4-0.6 (MIDDLE) | 17.8% | Valley (depleted) |
| 0.9-1.0 (FINAL) | 18.9% | Closing concentration |

**Overall KS test vs uniform:** p < 0.0001

This bimodal pattern aligns with C830's finding that repetition is FINAL-biased (mean position 0.675), since C828 confirms 100% of within-line repeats are PP.

**Provenance:** `phases/A_PP_INTERNAL_STRUCTURE/results/pp_positional_preferences.json`

---

## C898.b: PP Hub Network Structure

PP co-occurrence forms a scale-free network with clear hub-and-bridge topology:

### Network Statistics

| Metric | Value |
|--------|-------|
| Nodes (MIDDLEs) | 351 (degree ≥5) |
| Edges | 4,233 |
| Mean degree | 21.6 |
| **CV (degree)** | **1.69** (hub-dominated) |

### Top Hubs

| MIDDLE | Degree | Strength | Role |
|--------|--------|----------|------|
| **iin** | 277 | 1,592 | Mega-hub |
| ol | 208 | 1,036 | Secondary hub |
| s | 197 | 783 | Secondary hub |
| or | 188 | 844 | Hub + bridge |
| y | 181 | 875 | Secondary hub |

### Bridge Nodes (High Betweenness/Degree)

| MIDDLE | Bridge Ratio | Function |
|--------|--------------|----------|
| l | 1.17 | Connects vocabulary regions |
| iin | 1.00 | Universal connector |
| or | 0.75 | EARLY-position bridge |
| al | 0.67 | LATE-position bridge |

The hub structure is consistent with C475's finding that 95.7% of MIDDLE pairs are incompatible - hubs are the "legal connectors" that bridge otherwise isolated vocabulary.

**Provenance:** `phases/A_PP_INTERNAL_STRUCTURE/results/pp_network_topology.json`

---

## C898.c: Relationship to C234

C234 establishes that A tokens show "no positional grammar within lines" with "zero JS divergence between positions" at the aggregate level.

C898 **refines** this by showing PP specifically has positional structure:
- The aggregate may be uniform, but the PP subpopulation is bimodally distributed
- This is analogous to C498.d refining C498 for RI length-frequency correlation

The refinement relationship is:
- C234: Aggregate A tokens → position-free
- C898: PP subpopulation → positionally structured (EARLY/LATE biased)

---

## Methodological Notes

### Sample Imbalance (Test 4)

The WITH-RI vs WITHOUT-RI comparison had 20:1 sample imbalance (1,477 vs 73 lines). The low Jaccard (0.232) is an observed pattern, not a statistically robust structural law.

### Gradient Analysis (Null Result)

PCA showed the primary axis of PP variation is MIDDLE_DIVERSITY vs CLOSURE (PC1: 29.5%), not section membership. PC2 (24.7%) does separate sections (p<0.0001) via GALLOWS-CH loading.

---

## Provenance

- `phases/A_PP_INTERNAL_STRUCTURE/results/pp_positional_preferences.json`
- `phases/A_PP_INTERNAL_STRUCTURE/results/pp_network_topology.json`
- `phases/A_PP_INTERNAL_STRUCTURE/results/pp_gradient_analysis.json`

## Related Constraints

| Constraint | Relationship |
|------------|--------------|
| C234 | **REFINED** - PP has positional structure within aggregate freedom |
| C830 | **SUPPORTS** - FINAL-bias explained by PP LATE-biased MIDDLEs |
| C828 | **SUPPORTS** - 100% PP repeats explains position concentration |
| C475 | **CONSISTENT** - Hub structure expected from incompatibility layer |
| C512 | **CONSISTENT** - Hub PP are section-invariant substrate |
| C517 | **CONSISTENT** - Hubs contain compression hinge characters |

## Status

CONFIRMED - Structural measurements with strong statistical support.
