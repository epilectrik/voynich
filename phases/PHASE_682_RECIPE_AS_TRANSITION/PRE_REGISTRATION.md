# Phase 682 Pre-Registration

**Locked: 2026-05-04, before any start/end fingerprint computation.**

## Hypothesis

**H1:** Each matched-recipe folio encodes a single state transition. Its start-paragraph fingerprint maps to one rosette node (input state), and its end-paragraph fingerprint maps to a different rosette node (output state).

**H2:** Across 11 matched recipes, the implied (start→end) edge graph forms a coherent operational topology aligned with the 8 rosette paths.

## Background

Phase 681 tested whether dar-MIDDLE composition encodes state WITHIN one recipe. Result: REJECTED (dar has no MIDDLE variability, ARI=-0.089, Mantel rho=0.000). The hypothesis was wrongly framed: state-variation lives BETWEEN recipes (each recipe = one transition), not WITHIN.

Phase 680 showed:
- Rosettes have AZC-like fingerprints categorically distinct from B body text
- Rosette nodes have high ok-prefix (apparatus tracking)
- Rosette paths have high da-prefix (material introduction)
- Each rosette has a "closest matched recipe" by fingerprint similarity

Phase 682 reframes: if recipes are transitions, their START fingerprint and END fingerprint should map to DIFFERENT rosette nodes, with the (start→end) edge corresponding to a rosette path.

## Operational Definitions

**Start paragraphs:** first 3 paragraphs of each matched folio (or first 1/3 of paragraphs if folio has <9 paragraphs).

**End paragraphs:** last 3 paragraphs (or last 1/3 if folio has <9 paragraphs).

**Fingerprint:** PREFIX rates + HEAD atom rates + TERM atom rates + e-depth + bare rate (same as Phase 680).

**Closest rosette node:** minimum-distance node by fingerprint Manhattan-style across feature dimensions (same metric as Phase 680).

**Rosette graph:** the 9 rosettes connected by 8 paths in octagonal cycle (NW—N—NE—E—SE—S—SW—W—NW). CENTER is connected to none (or to all, depending on interpretation; we treat it as adjacent to ALL 8 outer rosettes for "any-path" tests).

## Tests

### TEST 1: Recipes are transitions, not steady states

**Prediction:** For ≥7/11 matched recipes, start_node ≠ end_node.

**Null:** Recipes are not transitions; start ≈ end → start_node = end_node randomly.

**Pass criterion:** ≥7/11 recipes have start_node ≠ end_node.

**Reasoning:** With 9 nodes and random start/end assignment, P(start = end) = 1/9 ≈ 11% per recipe. Expected matches under null: ~9.8/11. Observed should significantly exceed null.

Wait — that's wrong. If random with 9 nodes, P(start ≠ end) = 8/9 ≈ 89%. Expected ~9.8/11 different. So ≥7/11 different is NOT impressive (it's below null expectation). Adjust:

**Pass criterion (revised):** ≥10/11 recipes have start_node ≠ end_node (above 89% null expectation by binomial).

Actually the cleaner test: **does the start→end pair correspond to ADJACENT rosettes** (i.e., a real rosette path) more often than random?

P(start, end adjacent | random) = 8 paths × 2 directions / (9 × 8) = 16/72 ≈ 22%.
Expected adjacent under null: ~2.4/11.

**Pass criterion (final):** ≥6/11 recipes have start_node and end_node connected by a rosette path. Binomial P(X≥6 | n=11, p=0.22) ≈ 0.018 — significant at p<0.05.

### TEST 2: Operational graph topology

For all 11 recipes' (start_node, end_node) pairs:
- Build a graph G_recipes with these as edges
- Compare to G_rosettes (8 octagonal-cycle paths + center connections)

**Predictions:**
- Most recipe edges should align with actual rosette paths (Test 1 above generalizes)
- The recipe edges should not be arbitrary — should show topological coherence (no isolated nodes, connected component covering most rosettes)

**Pass criterion:** at least 6 of the 8 rosette paths have at least one matched recipe edge aligning with them (recipe start AND end map to the two endpoints of that path).

### TEST 3: Stage progression (clean increments)

**Prediction:** If recipes are ordered by their operational stage (raw → finished), their start→end transitions should walk a coherent path through the rosette diagram.

**Operational ordering** (pre-registered before computing fingerprints):
1. f112v (lunaria → quicksilver) — earliest, raw plant input
2. f76v (ferment conversion) — early, ferment formation
3. f75r (aqua vitae) — early-mid, distillation
4. f82r (multi-recipe waters) — mid, parallel waters
5. f76r (element separation) — mid, decomposition
6. f103r (ferment multiplication) — mid-late, multi-chamber
7. f79r (mercury sublimation) — mid-late, mercury work
8. f112r (red mercury tincture) — late, coloration
9. f84r (gold dissolution) — late, gold work
10. f81v (potable gold) — late, finished medicinal
11. f116r (fixation) — final, stabilization

**Pass criterion:** sequential start_nodes in this ordering form a coherent walk on the rosette graph (each step is to an adjacent or shared node ≥7 of 10 transitions). Permutation null: shuffle the 11 recipe ordering, recompute walk coherence.

## Confound Controls

- **Paragraph-1 confound:** start fingerprint includes P1; check separately whether excluding P1 changes start-node assignment significantly
- **Single-paragraph recipes:** if a recipe has fewer than 6 paragraphs, "start" and "end" fingerprints overlap. Note these and treat as ambiguous
- **f82r multi-recipe folio:** Phase 668 noted f82r encodes 5 sub-recipes. Treat its result as ambiguous if it doesn't fit the single-transition model
- **CENTER rosette:** if many recipes' start or end maps to CENTER, that suggests CENTER is a frequent state (input or output), which would be substantively interesting but methodologically complicates the path-alignment test

## Decision Tree

| Outcome | Verdict |
|---------|---------|
| Test 1 PASS (≥6/11 adjacent) AND Test 2 PASS (≥6/8 paths covered) | Strong: recipes-as-transitions supported, Tier 3 candidate |
| Test 1 PASS, Test 2 FAIL | Recipes are transitions but don't align with rosette paths — different topology |
| Test 1 FAIL | Recipes are NOT transitions in this fingerprint sense; identification-vocabulary explanation prevails |
| Both PASS + Test 3 walk coherent | Tier 3 strong candidate; cross-corpus replication needed for Tier 2 |

## Predicted Outcomes (For Calibration)

If the rosettes-as-PFD interpretation is correct:
- Test 1: ~7-9/11 recipes show start_node ≠ end_node connected by rosette path
- Test 2: ~5-7 of 8 paths have at least one recipe edge

If the rosettes-as-PFD interpretation is wrong (rosettes are something else):
- Test 1: ≤4/11 (random rate)
- Test 2: ≤3/8 paths covered

Crazy-expert's bet (if asked, probably): partial signal, leaning null, ~3-5/11. The 11×9 mapping space is too large to constrain meaningfully with 11 recipes.

## What Will NOT Happen

- No post-hoc adjustment of recipe ordering
- No adjusting the start/end paragraph window after seeing results
- No claim of specific node-to-state interpretation (CENTER ≠ "quintessence" etc.)
- No tier promotion above Tier 3
