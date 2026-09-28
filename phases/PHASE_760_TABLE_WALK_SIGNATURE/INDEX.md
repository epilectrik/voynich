# PHASE_760 — Table-walk signature

**Status:** COMPLETE. Locked verdict **NO SIGNATURE** → registered as C2079 (Tier 2, negative knowledge).
**Pre-registration:** `PRE_REGISTRATION.md` (locked, commit 785f797; lean-expert audit applied).
**Script:** `scripts/table_walk.py` (2.6 min; per-type coordinates precomputed, each null replicate O(n) vectorized).
**Results:** `results/table_walk.json`, `results/run_log.txt`.

## Question
Prompted by the question "what if a token is a 3-D array index, a lookup value for something else?". If a writer produced
tokens by moving between neighbouring cells of a multi-dimensional table, adjacent tokens would keep one coordinate
more often than line composition implies, and the kept coordinate would change along the walk.

## Data
Currier B, H, P placement, lines with ≥ 5 certain tokens: 19,024 adjacent pairs, 18,833 non-identical by
(PREFIX, MIDDLE, SUFFIX) tuple. No token has an empty MIDDLE under the current parser.

## Results (kept-slot counts, observed minus null mean; p one-sided in each direction)
| Slot | Observed | N1 zone-preserving shuffle | N_EDGE (N5, glyph edges, β = 4) | Known-effect check | Glyph frame (N1) |
|---|---|---|---|---|---|
| PREFIX | 1,696 | **−126** (p_low 0.001) | **−65** (p_low 0.010) | deficit = C549 alternation reproduced | first unit −71 (p_low 0.044) |
| MIDDLE | 803 | **−77** (p_low 0.001) | −4 (p 0.42 / 0.60) | same-HEAD conditional: no excess (p_up 0.99) | interior −18 (n.s.) |
| SUFFIX | 2,168 | **+178** (p_up 0.001) | **+135** (p_up 0.001) | without dy→dy: +46 (p 0.019), N_EDGE +51 (p 0.003) | last unit −31 (p_up 0.77) |
N_EDGE diagnostics: 74% of movable positions changed, max section edge TV 0.0003; split R-hat for the slot counts
1.13–1.18 (reported, not gating). Full within-line shuffle (N0) and paragraph permutation (NP) are in the JSON; NP gives
the same directions as N1.

**Rotation:** 817 triples in which both pairs keep exactly one slot. Table (rows = slot kept at pair 1, columns = pair 2;
PREFIX, MIDDLE, SUFFIX): [[144, 25, 71], [27, 20, 35], [147, 18, 330]]. Same slot kept twice: 494 vs 364 expected from the
marginals (p_excess = 0.0001; p_deficit = 1.0). MDE80 for the diagonal ≈ 31 triples.

## Verdict (locked rules): NO SIGNATURE
No slot is new-positive: PREFIX and MIDDLE are kept less often than composition implies, and the SUFFIX excess — real
under both nulls and partly beyond the known dy→dy repetition — does not appear at the glyph level (the last glyph unit
is not kept more often), failing the pre-registered concordance requirement. The rotation test shows the opposite of a
walk: when a coordinate is kept, the same one tends to be kept again (suffix runs, e.g. …dy …dy …dy).

## Reading
- Adjacent tokens alternate their prefixes (qo/ch/sh interleaving, C549), do not repeat their MIDDLEs (the apparent
  avoidance is explained by boundary glyph coupling: it disappears under the edge-preserving null), and run their
  suffixes. Nothing looks like stepping through neighbouring cells of a table.
- This bounds one version of the lookup idea (sequential reading off a table). It does not bear on whether tokens are
  lookup keys at all: without the table, that cannot be tested internally (C171).
- The SUFFIX run effect beyond dy→dy is a parser-level (morphological) persistence, not a glyph-level one; worth noting
  alongside C1002.
