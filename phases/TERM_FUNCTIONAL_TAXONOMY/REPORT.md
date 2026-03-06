# Phase 535: TERMINAL Functional Taxonomy

**Date:** 2026-03-06
**Status:** COMPLETE
**Constraints produced:** C1483-C1487

---

## Research Question

The 6 TERMINAL atoms {y, l, r, h, m, n} set the exit condition of every compound MIDDLE. Individual facts were known -- opacity gradient (C1440-C1441), r=99% FLOW, h=transparent (V=0.988), m=87% TRANSITION -- but there was no unified behavioral profile across all dimensions. This phase characterizes all 6 terminals comprehensively, paralleling what Phase 533 did for HEAD atoms.

## Method

12-dimensional characterization of each terminal + bare across:
- T1: Category profile (8-category distribution)
- T2: Opacity (suffix attachment rate)
- T3: HEAD compatibility (HEAD x TERM frequency/enrichment)
- T4: Modifier compatibility (which modifiers each terminal attracts/avoids)
- T5: Hazard profile (forbidden violation rate as source and target)
- T6: Line position (quintile distribution, initial/final rates)
- T7: PREFIX selectivity (which PREFIXes select each terminal)
- T8: Population census (token/type counts)
- T9: Bare vs terminated comparison
- T10: Pairwise behavioral distance (category JSD)
- T11: Category determination power (entropy, Cramer's V)
- T12: Full HEAD x TERM frame category matrix

N = 23,096 tokens, 20,676 adjacency pairs.

## Key Findings

### 1. TERMINAL Category Specificity Gradient (C1483)

Overall TERMINAL x CATEGORY Cramer's V = **0.463** -- terminals are the second strongest category determinant after HEAD.

| Terminal | Dominant Category | Dominant % | Norm Entropy | Sig Categories |
|----------|------------------|------------|--------------|----------------|
| r        | FLOW             | 98.9%      | 0.036        | 1              |
| m        | TRANSITION       | 87.9%      | 0.211        | 2              |
| l        | STAGING          | 64.5%      | 0.456        | 3              |
| y        | OPERATION        | 40.6%      | 0.631        | 4              |
| n        | TRANSITION       | 39.3%      | 0.652        | 4              |
| h        | MARKING          | 30.0%      | 0.844        | 6              |
| bare     | THERMAL          | 43.2%      | 0.818        | 6              |

The gradient spans from r (near-categorical, 1 significant category) to h (diffuse, 6 significant categories). r is essentially a FLOW operator regardless of HEAD -- it carries 98.9% FLOW across all 5 HEADs + headless. m is a TRANSITION operator (87.9%). At the other extreme, h participates meaningfully in 6 categories and functions as a multi-purpose monitor rather than a category-specific atom.

### 2. TERMINAL Modifier Exclusivity (C1484)

Each terminal selects from a narrow modifier subset, creating near-exclusive modifier channels:

| Terminal | Primary Modifier | Enrichment | All Others |
|----------|-----------------|------------|------------|
| n        | i only           | i=8.606x   | All 0.0x   |
| y        | d only           | d=2.868x   | All <0.03x |
| h        | {c,p,f,s}        | c=9.1x, p=7.7x, f=6.4x, s=5.0x | i=0.1x, d=0.1x |
| l        | (depleted)       | All <0.2x  | mod_rate=1.8% |
| r        | (depleted)       | All <0.3x  | mod_rate=3.0% |
| m        | (depleted)       | All <0.2x  | mod_rate=3.8% |

This is a near-perfect partition: n takes i, y takes d, h takes {c,p,f,s}, and l/r/m resist modification. This means the modifier slot is fully TERMINAL-gated -- knowing the terminal tells you which modifiers are legal. This extends C1479 (HEAD modifier selectivity) to the TERMINAL dimension, showing the dual constraint: HEAD and TERMINAL jointly determine the modifier palette.

The n-i exclusivity is total: n has 3,553 i-modifier instances and ZERO instances of any other modifier. Every n-terminal MIDDLE is of the form [HEAD?] + i* + n.

### 3. TERMINAL HEAD Affinity Partition (C1485)

Terminals create a clear partition of the HEAD space:

| Terminal | Primary HEAD | Enrichment | Excluded HEADs |
|----------|-------------|------------|-----------------|
| y        | e (72.7%)   | 2.40x      | a (0.002x), k (0.01x), o (0.007x), t (0.03x) |
| n        | a (59.3%)   | 4.44x      | e (0.002x), k (0x), t (0x) |
| m        | a (60.2%)   | 4.52x      | e (0.01x), k (0.03x), t (0x) |
| l        | o (30.3%)   | 2.57x      | k (0.04x), t (0.05x) |
| r        | a (35.0%)   | 2.63x      | e (0.03x), k (0.03x), t (0.04x) |
| h        | None (45.6%)| 1.68x      | a (0.12x) |
| bare     | k (28.5%)   | 2.12x      | a (0.30x) |

The HEAD x TERM contingency reveals near-categorical exclusions:
- k and t HEADs categorically avoid n and m terminals (0-1 tokens each)
- e-HEAD is locked to y-terminal (3,475 tokens = 72.7% of all y tokens)
- a-HEAD dominates n and m terminals (59-60%)

This HEAD-TERMINAL affinity creates a de facto compositional grammar where HEAD and TERMINAL jointly specify the instruction frame.

### 4. m-Terminal Line-Final Closure (C1486 -- confirms C1434-C1439)

m-terminal: mean position 0.903, 73.7% line-final (vs ~10% for other terminals). 87.9% TRANSITION. Only 10 unique MIDDLEs. 4.2% suffix rate (OPAQUE). This is a quantitative confirmation of the line-closure valve mechanism from C1434-C1439, now in context of all 6 terminals showing m as a unique positional outlier.

No other terminal has mean position above 0.52. m is a structural singularity.

### 5. Hazard Asymmetry (reinforces C1447)

As hazard SOURCE: y carries 90.9% of all violations (10/11), r carries 9.1% (1/11). h, l, m, n, bare have ZERO source violations.

As hazard TARGET: n absorbs 90.9% of all target violations (10/11). All others have 0 or 1.

This creates a directional hazard circuit: violations flow FROM y-terminal tokens TO n-terminal tokens. The y->n hazard axis is the primary violation vector.

### 6. Pairwise Distance Structure

Most distant pair: m vs r (JSD=0.977) -- essentially opposite categories (TRANSITION vs FLOW).
Most similar pair: bare vs h (JSD=0.220) -- both are diffuse, multi-category.

The distance matrix reveals three clusters:
1. **Categorical terminals:** r and m are distant from everything (mean JSD >0.7)
2. **Moderate terminals:** l, y, n form an intermediate cluster (mutual JSD 0.34-0.60)
3. **Diffuse terminals:** bare and h are most similar to each other and furthest from r/m

### 7. Six-Terminal Functional Taxonomy (C1487)

The 6 terminals decompose into three functional tiers along category specificity:

**LOCKED (1-2 categories):**
- r = FLOW (98.9%) -- the flow routing terminal
- m = TRANSITION (87.9%) -- the closure valve terminal

**CHANNELED (3-4 categories):**
- l = STAGING (64.5%) -- the staging/state terminal
- y = OPERATION (40.6%) + CONTAINMENT (14.0%) + TRANSITION (9.9%) -- the work completion terminal
- n = TRANSITION (39.3%) + STAGING (27.7%) + MARKING (12.3%) -- the iteration binding terminal

**DIFFUSE (5-6 categories):**
- h = MARKING (30.0%) + MONITORING (16.3%) + THERMAL (23.9%) -- the transparent monitoring terminal
- bare = THERMAL (43.2%) + FLOW (14.8%) + MARKING (11.2%) -- the default operational terminal

This taxonomy cross-cuts the opacity gradient (C1440):
- OPAQUE terminals (m, n, y: <5% suffix) span LOCKED and CHANNELED tiers
- SEMI-TRANSPARENT terminals (l, r: 17-20%) span LOCKED and CHANNELED tiers
- TRANSPARENT terminals (h: 98.7%, bare: 89.0%) are exclusively DIFFUSE

The key insight: opacity is INDEPENDENT of category specificity. r is SEMI-TRANSPARENT but LOCKED to FLOW. h is TRANSPARENT but DIFFUSE. Opacity controls whether the instruction needs a suffix parameter; category specificity controls what operational domain the instruction operates in. These are orthogonal design axes.

## Cross-References

| Constraint | Finding | Relationship |
|------------|---------|--------------|
| C1440-C1441 | Terminal opacity gradient | CONFIRMED: m/n/y <5%, l/r 17-20%, h >98% |
| C1447 | r-terminal hazard vector | CONFIRMED: 90.9% of source violations |
| C1434-C1439 | m-terminal closure valve | CONFIRMED: 73.7% line-final, 87.9% TRANSITION |
| C1475-C1479 | HEAD domain differentiation | PARALLELED: TERMINAL provides complementary taxonomy |
| C1472-C1474 | Modifier co-occurrence avoidance | EXPLAINED: terminals gate modifier selection |
| C1448 | HEAD x TERM frame hazard map | EXTENDED: y=source, n=target hazard axis |
| C1383 | n-terminal boundary avoidance | CONSISTENT: n is interior-biased (mean pos 0.479) |

## Verdict

The 6 TERMINAL atoms form a complete functional taxonomy that is the symmetric counterpart to the 5 HEAD atoms (C1475-C1479). Where HEAD determines the operational DOMAIN (THERMAL, FLOW, etc.), TERMINAL determines the EXIT CONDITION (flow routing, closure, staging, completion, iteration, monitoring). Together, HEAD and TERMINAL create a frame that specifies both what an instruction does and how it terminates.

The TERMINAL taxonomy has two independent design axes:
1. **Category specificity** (how narrowly the terminal constrains operational domain)
2. **Opacity** (whether the instruction takes a suffix parameter)

These axes are orthogonal, producing six distinct functional profiles from six atoms.
