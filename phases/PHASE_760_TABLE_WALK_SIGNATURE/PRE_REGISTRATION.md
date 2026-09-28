# PHASE_760 — Table-walk signature: do adjacent tokens keep one coordinate and rotate it? (pre-registration)

**Locked:** 2026-09-27, before any analysis code for this phase was written or run. Design audited by the lean-expert
(verdict LOCK WITH CHANGES; every requested change is incorporated below).
**Origin:** discussion 2026-09-27 (human question: "what if a token is a 3-dimensional array index, a lookup value for
something else?"). Hypothesis-driven exploration of one cheap signature of a lookup model. A pass is a Tier-2
measurement of adjacency structure between slots; "tokens are indices into a table" is an interpretation that needs an
external test (e.g., the same statistics on the Naibbe, Timm and M1 ensembles) or human sign-off.
**Prior work checked (none tests this signature):** C1964 (prefix runs, one slot, descriptive), C549 (qo/ch-sh
interleaving), C1562 (HEAD self-transition), C1002 (suffix sequential grammar, edy→edy self-repetition), C2077
(adjacent identical / edit-distance-1 rates as fit targets, no null), C1212/C1563 (cross-slot boundary coupling), C1003
(within-token synergy), SSD_PHY_1a / C973 (MIDDLE-space dimensionality).
**Hypothesis (table walk):** tokens produced by moving between neighbouring cells of a multi-dimensional table keep
one coordinate from token to token more often than the line's composition implies, and the kept coordinate changes
along the walk.
**Change control:** after lock nothing below may change without a new phase number.

## Data
Currier B, H track, `P` placement, labels excluded; uncertain tokens are blockers (no pair across them), as in
PHASE_756. Adjacent pair = two consecutive certain tokens in a line. **Gated set:** lines with ≥ 5 certain tokens (the
effective number of pairs whose partners can move under N1 is reported).

## Coordinates
- **Primary frame:** `Morphology().extract(token)` → (PREFIX, MIDDLE, SUFFIX), current parser (post-C1957);
  articulator ignored. A slot is **comparable** in a pair when both values are non-empty; it is **kept** when
  comparable and equal. Pairs with identical (P, M, S) tuples are "no move" and are excluded from kept-slot counts
  (in the real text and in every null replicate alike). The number of tokens with an empty MIDDLE is reported.
- **Glyph frame (concordance requirement for a positive verdict):** (first glyph unit, interior glyph-unit string, last
  glyph unit) with the PHASE_754 tokenizer, same rules.

## Statistics
- **K_s (primary, per slot s ∈ {PREFIX, MIDDLE, SUFFIX}):** number of adjacent non-identical pairs in which slot s is
  kept. Compared as counts with the null count distributions.
- **Known-effect checks (a slot counts as new only if its check passes):**
  - PREFIX: C549/C1964 predict alternation (fewer kept prefixes than the null). A walk needs an excess; an excess in the
    PREFIX slot is therefore new by construction; a deficit is reported as C549 reproduced.
  - MIDDLE: must exceed what HEAD sharing (C1562) predicts. Check statistic: among pairs whose MIDDLEs have the same
    HEAD atom (`Morphology().atomize`), the count with the whole MIDDLE kept; compared with the null's count among its
    own same-HEAD pairs (conditional excess).
  - SUFFIX: C1002 reports edy→edy self-repetition (current parser: kept suffix "dy"). Check statistic: K_SUFFIX with
    pairs whose kept suffix is "dy" removed.
- **Bins (secondary):** counts of pairs keeping 0, 1, 2 or 3 slots, within strata k = 2 and k = 3 comparable slots;
  sensitivity with "empty" treated as a value.
- **Rotation (primary for the walk):** eligible triples (t1, t2, t3) in which both pairs keep exactly one slot
  (gated lines). 3 × 3 table of kept slot at pair 1 vs pair 2; statistic = diagonal count (same slot kept twice). Null:
  pair-2 labels permuted among eligible triples, 10,000 permutations (seed 760), which keeps both marginals. A walk
  predicts a diagonal deficit. N of eligible triples and MDE80 are reported (overlapping triples share t2; stated).

## Nulls (for K_s and the checks)
- **N1:** zone-preserving within-line shuffle (INITIAL and FINAL tokens fixed, MEDIAL permuted, blockers fixed), 1,000
  replicates, seed 760.
- **N_EDGE (co-primary):** PHASE_756's N5 kernel with glyph-unit edges — within-line medial swaps with a soft
  constraint preserving each section's (last glyph unit → first glyph unit) boundary-pair counts, zones and line
  composition; β = 4; 4 chains (2 from the real text, 2 from an N1 state with β annealed over 1,000 sweeps); burn-in
  2,000 sweeps; 250 samples per chain every 10 sweeps (1,000 samples). Required: fraction of movable MEDIAL positions
  changed ≥ 0.50 and per-section edge TV ≤ 0.02; if not met at β = 4, β = 2 is used; split R-hat for each K_s reported.
- **N0** (full within-line shuffle) and **NP** (within-paragraph permutation keeping line lengths and zones), 1,000
  replicates each, reported only.
p-values: one-sided in the pre-stated direction, p = (1 + #{null ≥ observed}) / (1 + R); both tails reported.

## Decision rules (locked)
A slot is **new-positive** if: K_s excess with p < 0.0033 (0.01 / 3 slots) under **both** N1 and N_EDGE in the primary
frame; its known-effect check passes (p < 0.05 under N1, same direction); and the glyph frame shows an excess in the
corresponding slot with p < 0.05 under N1.
- **TABLE-WALK SIGNATURE** — ≥ 1 new-positive slot AND rotation diagonal deficit p < 0.01.
- **SLOT PERSISTENCE (no walk)** — ≥ 1 new-positive slot, rotation p ≥ 0.05.
- **NO SIGNATURE** — no new-positive slot. The walk model is bounded; per-slot MDE80 (2.485 × null SD, in pairs and as a
  rate) recorded as negative knowledge.
- **INCONCLUSIVE** — any other combination.
Known effects (C549 prefix alternation, C1002 suffix self-repetition, C1562 HEAD persistence) are reported as reproduced
or not, under both nulls. Sections are reported descriptively only.

## What this phase does not do
It does not test whether tokens are lookup keys (C171: that needs an external table), synergy against external targets,
or any generator.
