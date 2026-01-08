# Phase SITD: Shot in the Dark Exploratory Tests

**Date:** 2026-01-08
**Status:** CLOSED
**Constraints:** 411 (1 Tier 2), plus 1 Tier 4 interpretive finding

## Objective

Take epistemically legitimate "shots in the dark" that ask **qualitatively different questions** from prior work. Pre-define success criteria; accept null as valid closure.

## Tests Conducted

### PRIMARY: Grammar Reduction Test (Tier 2)

**Question:** Is 49 instruction classes the true minimum, or can some be merged without loss of predictive power?

**Methodology:**
1. Built transition matrix for all 49 classes from Currier B
2. Computed pairwise class similarity (Jaccard on transitions, behavioral signatures, role matching)
3. Attempted agglomerative clustering with constraint: <=1% entropy increase per merge
4. Found minimum class count that satisfies constraints

**Results:**

| Metric | Value |
|--------|-------|
| Original classes | 49 |
| Reducible to | 29 |
| Reduction | **40.8%** |
| Entropy cost | <1% per merge |

**Key merges:**
- ENERGY_OPERATOR: 11 classes collapse to 2 mega-classes
- AUXILIARY: 8 classes collapse to 1 mega-class
- FREQUENT_OPERATOR: 4 classes collapse to 1 class
- CORE_CONTROL (daiin, ol): **Cannot merge** - refuse to collapse (1.11% entropy cost)

**Conclusion (Constraint 411):** The grammar is deliberately over-specified. The 49-class system maintains ~20 more classes than structurally necessary. This indicates intentional vocabulary diversification for human-facing mnemonic, ergonomic, or readability considerations rather than minimal encoding.

**Tier Assessment:** Tier 2 (structural design property, not interpretation)

---

### SECONDARY: Forgiving vs Brittle Program Axis (Tier 4)

**Question:** Is there a skill-level dimension orthogonal to aggressive/conservative?

**Methodology:**
For each of 82 B programs, computed:
1. Hazard density (hazard tokens / total tokens)
2. Escape density (qo-prefix tokens / total tokens)
3. Mean distance to nearest escape
4. Maximum safe run (longest stretch without hazard tokens)

Combined into "forgiveness score" (higher = more recovery options).

**Results:**

| Metric | Value |
|--------|-------|
| Score range | 5.82 (5.0 std devs) |
| Hazard-Escape correlation | -0.184 (relatively independent) |
| Effect size vs aggressive/conservative | 0.509 (moderate) |

**Quartile profiles:**
| Quartile | Hazard% | Escape% | Safe Run |
|----------|---------|---------|----------|
| Q1 (Brittle) | 11.1% | 7.5% | 27.6 |
| Q4 (Forgiving) | 7.8% | 23.8% | 45.0 |

**Extreme programs:**
- Most brittle: f33v, f48v, f39v (concentrated hazards, few escapes)
- Most forgiving: f77r, f82r, f83v (many escape routes, spread-out hazards)

**Conclusion:** Programs vary along a forgiving↔brittle continuum that is NOT fully explained by aggressive/conservative. This could suggest **competency-graded reference** — some programs designed with more recovery options for less experienced operators.

**Tier Assessment:** Tier 4 (interpretive speculation about operator intent)

---

## Epistemological Notes

Both tests followed proper tier discipline:
- Pre-defined success criteria
- Accepted null as valid closure
- Did not let speculation infect constraints

The grammar reduction finding is **structural and falsifiable** — it reveals a design property (intentional over-specification) without semantic claims. The forgiveness finding is **behavioral meta-structure** that depends on operator intent, pushing it to Tier 4.

## Scripts

- `grammar_reduction_test.py` — Primary test: class mergeability analysis
- `program_forgiveness_test.py` — Secondary test: forgiving/brittle axis

## Expert Validation

Expert guidance confirmed:
- Grammar reduction is legitimate Tier 2 (structural, repeatable, strengthens model)
- Forgiveness axis is valuable Tier 4 context (important but not enforceable)
- Core tokens (daiin, ol) refusing to merge **supports** prior findings about their special status
