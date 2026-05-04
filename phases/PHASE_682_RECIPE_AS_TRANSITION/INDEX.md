# Phase 682: Recipe-As-Transition Hypothesis

**Status:** COMPLETE — pre-registered hypothesis FALSIFIED
**Started:** 2026-05-04
**Goal:** Test whether each matched-recipe folio encodes a single state transition between rosette nodes (recipe-as-edge in the rosette-as-PFD interpretation).

## Pre-Registered Hypothesis (locked in PRE_REGISTRATION.md)

**H1:** Each matched-recipe folio encodes a single state transition. Its start-paragraph fingerprint maps to one rosette node; end-paragraph fingerprint to a different node. Across 11 matched recipes, implied (start→end) edges should align with rosette paths.

## Tests and Results

### TEST 1: Recipes are transitions (start_node ≠ end_node)

| | Required | Actual |
|---|---|---|
| Recipes with start_node ≠ end_node | ≥10/11 | **3/9 testable** |

Most recipes (6 of 9) have IDENTICAL start_node and end_node. **8 of 9 start_nodes are EAST.** Recipes are not transitions in fingerprint space — they're stable operational programs that share a common preparation signature.

### TEST 2: Path alignment

| | Required | Actual | Random null |
|---|---|---|---|
| Recipes with start→end on a rosette path | ≥8/11 | **1/9** | 4.4 expected |

Permutation null: p=0.9959 (recipes are LESS path-aligned than random).

### TEST 3: Coherent walk (operational ordering)

Pre-registered ordering by raw→finished progression. Walk: WEST → EAST → EAST → EAST → EAST → EAST → EAST → EAST → EAST. **Technical pass (7/8 coherent steps) but trivially** — 8/9 starts collapse to EAST. The "walk" doesn't move.

## Verdict

Per pre-registration decision tree: **"Recipes-as-transitions NOT supported; no registration."**

## Substantive Finding

8 of 9 matched recipes' START paragraphs map to **EAST**. EAST has the highest ok-prefix rate (31.4%) of any rosette — most apparatus-tracking. Recipes' early paragraphs are most apparatus-heavy, hence consistently land on EAST.

Recipes are NOT single edges in an operations graph. They're operational programs with shared preparation/apparatus signatures. The "rosettes-as-PFD-with-recipes-as-paths" interpretation FAILS.

## Constraint Registered

### C1990 (Tier 1 falsification): Recipes-as-transitions in rosette graph REJECTED

Pre-registered Phase 682 test of "recipes are single state transitions in the rosette graph (recipe-as-edge)" REJECTED. With 11 matched-recipe folios:
- Test 1 (start ≠ end, ≥10/11): FAIL (3/9 testable)
- Test 2 (path-aligned, ≥8/11): FAIL (1/9, p=0.9959 — worse than random)
- Test 3 (coherent walk): trivial pass (8/9 starts collapse to EAST)

Recipes are NOT single edges in an operations graph. 8/9 starts map to EAST (highest ok-prefix rosette, 31.4%). Recipes share a common preparation/apparatus signature; they are operational programs, not single state transitions. The "rosettes-as-PFD with recipes-as-paths" interpretation falsified at the structural level.

**Tier:** 1 (Currier B + Rosettes, falsification of pre-registered hypothesis)

## Scripts

- `s1_recipe_transitions.py` — pre-registered Mann-Whitney + permutation tests

## Relationship to Existing Constraints

- **C1989** (path/node structural differentiation): Survives — path/node distinction is real, but recipes don't map to it as transitions
- **C1124-C1130** (rosettes metalayer): Workshop-diagram interpretation refined — rosettes ARE a metalayer, but recipes are not the canonical paths through it
- **C1128** (generic indexing): Strengthened — recipes don't specifically index any rosette path; their starts collapse to a single node (EAST)
