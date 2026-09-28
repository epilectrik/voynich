# PHASE_756 — C957 joint null (N5) and cross-track check (pre-registration)

**Locked:** 2026-09-27, before any analysis code for this phase was written or run. Design audited by the
lean-expert before locking (verdict LOCK WITH CHANGES; all requested changes are incorporated below).
**Origin:** PHASE_753 lean-expert review (required next test); STRATEGIC_REVIEW_2026-09-27 §3 #2 (gate for the
rival-generator panel, #5).
**Claim under test:** C957 as rescoped 2026-09-27 (Tier 2, screen level): the number of zero cells among common
Currier B token bigrams exceeds a zone-preserving within-line null and an edge-glyph generator *separately*.
Rejecting two single-mechanism nulls separately is expected even with no residual (each is anti-conservative about
the mechanism it omits). This phase asks whether an excess of zero cells survives a null that preserves **line
composition, zones and boundary glyph coupling jointly**.
**Change control:** the thresholds, the β grid, the tolerances, burn-in, sample counts and seeds below cannot be
changed after pass 1 has run without a new phase number.

## Data
- **Primary scope:** Currier B, H track, placement starting with `P` (paragraph text), labels excluded
  (`Transcript().currier_b(exclude_uncertain=False)`, then filtered). Lines keyed by (folio, line). Section from the
  token's `section` field (S, B, H, C, T).
- **Uncertain tokens** (`is_uncertain`) stay in their line as fixed blockers: they never move, and no edge or bigram
  is formed with them (lines are effectively split at them for counting).
- **Common tokens:** frequency ≥ 10 in the primary data. **Bigrams:** within-line adjacent pairs of certain tokens,
  both common. **Zones:** INITIAL = first position of the line, FINAL = last position, MEDIAL = everything between.
- **Reported, not verdict-bearing:** the C957-identical data (all Currier B placements, uncertain tokens dropped and
  neighbours joined; PHASE_753 pipeline), run through the same N5 procedure.

## The null N5 (MCMC over within-line medial permutations)
**State:** for every line, a permutation of its movable MEDIAL tokens (MEDIAL positions not holding an uncertain
token). INITIAL and FINAL tokens and blockers never move, so line composition and zone membership are exact in every
state (asserted).

**Edge classes.** For every within-line adjacent pair of certain tokens (u, v) — all tokens, not only common ones,
including INITIAL→first-medial and last-medial→FINAL — the edge type is (last unit of u, first unit of v).
- **Unit EVA:** single EVA characters.
- **Unit GLYPH:** glyph units from PHASE_754's tokenizer `c[tkpf]h|[cs]h|i+[nrlm]|.` (benches ch/sh, benched gallows
  cth/ckh/cph/cfh, minim groups i+[n r l m], otherwise single characters). A glyph unit determines its EVA character,
  so the GLYPH edge matrix determines the EVA matrix: the GLYPH null is the more constrained, more conservative one.
For section s, C_s(state) is the count matrix of edge types over lines of section s; C_s^real is the real one.

**Target:** π(state) ∝ exp(−β · L1(state)), with L1(state) = Σ_s Σ_cells |C_s(state) − C_s^real| (in counts). The real
text has L1 = 0; as β → ∞, π approaches the uniform distribution over within-line medial permutations reproducing
every section's edge-count matrix exactly.

**Move:** choose a line with probability proportional to its number of movable MEDIAL pairs, choose two distinct
movable MEDIAL positions uniformly, propose swapping their tokens. The proposal is symmetric; accept with probability
min(1, exp(−β ΔL1)), ΔL1 computed from the affected edges. A sweep = one proposal per movable MEDIAL token.

## Diagnostics (definitions)
- **Edge TV** for a section group g: 0.5 · Σ |p_g(state) − p_g^real| over the normalized (last unit → first unit)
  matrix of within-line adjacent pairs in g. Groups: every section with ≥ 1,000 within-line edges is its own group;
  sections with fewer are pooled with the smallest section that has ≥ 1,000. Reported as the mean over samples and as
  the 95th percentile.
- **Coupling reference K_g:** TV between the real matrix p_g^real and the product of its own marginals. **Tolerance
  tol_g = min(0.02, 0.10 · K_g)** (the slack may be at most 10% of the coupling it is meant to preserve).
- **Fraction changed:** over movable MEDIAL positions in lines with ≥ 2 movable MEDIAL tokens that are not all the
  same type; a position is changed if its token type differs from the real text. Also reported over all positions,
  plus the share of the candidate cells' expected count contributed by frozen lines (lines with no admissible move).
- **Mixing:** rank-normalized split R-hat (Vehtari et al. 2021) across the 4 chains of a pass, and bulk ESS pooled over
  them, each for Z(E≥3), L1 and fraction changed.

## Choice of β (fixed rule; the zero-cell statistic is never computed during calibration)
Grid β ∈ {0.5, 1, 2, 4, 8}, run separately for each unit. For each β: 2 pilot chains, 1,000 sweeps each, one from the
real state and one from a random zone-preserving medial shuffle (N1 state) with β annealed linearly from 0 to β over
the first 500 sweeps. Diagnostics use every 10th sweep of the last 500. β is **admissible** if (i) fraction changed
≥ 0.50 in the real-start chain, (ii) mean TV ≤ tol_g for every group in both chains, and (iii) the annealed chain's
mean L1 is within 10% of the real-start chain's (or both are ≤ 1% of the edge count). **β\* = the largest admissible β**
(most constrained end of the feasible range). The pilot output is committed with the results.

## Main runs (per unit, at β\*)
8 chains: pass 1 = chains 1–4 (seeds 75601–75604 EVA; 75611–75614 GLYPH), pass 2 = chains 5–8 (seeds 75605–75608
EVA; 75615–75618 GLYPH). In each pass, 2 chains start from the real state and 2 from an N1 state with β annealed
linearly from 0 to β\* over sweeps 0–1,000 and held at β\* for sweeps 1,000–2,000. Burn-in 2,000 sweeps for every
chain; no sample is counted before sweep 2,000. Then 1,000 samples per chain at a thinning interval of 5 sweeps
(4,000 samples per pass).
**Required in pass 2:** R-hat < 1.05 and bulk ESS ≥ 1,000 for Z(E≥3), L1 and fraction changed; mean TV ≤ tol_g for
every group; fraction changed ≥ 0.50; zones exact. If any fails, burn-in and sample counts are doubled once. If it
still fails, the next smaller admissible β is used (same procedure). The null is NOT ACHIEVED for a unit when no
admissible β passes.

## Statistic
- **Pass 1:** E(a, b) = mean count of the ordered common pair (a, b) over all pass-1 samples. **Candidate set**
  C(E_min) = {(a, b) : E(a, b) ≥ E_min}, defined without reference to the real counts and fixed before pass 2.
  **Primary E_min = 3**; E_min = 5 reported only. Stability: the Jaccard overlap of the candidate sets computed from
  chains {1, 2} and {3, 4} must be ≥ 0.95; otherwise pass-1 samples are doubled (up to 4×), and a final value below
  0.95 is reported.
- **Cross-track cleaning (primary).** A cell is TRACK-FRAGILE if its real H count is 0 and the ordered pair (a, b) is
  attested at least once in track F or track C (within-line adjacent pair of certain tokens, Currier B, `P`
  placement, anywhere in that track). TRACK-FRAGILE cells are removed from the candidate set for both the real text
  and every null sample. The cleaned statistic is primary; the raw one is reported.
- Z_real = number of (cleaned) candidates with real count 0. Z_r = the same count in pass-2 sample r.
  **p = (1 + #{r : Z_r ≥ Z_real}) / (1 + R)**, R = number of pass-2 samples. ESS is reported next to p.
- **L1 extrapolation:** OLS of Z_r on L1_r over the pass-2 samples, Z_r′ = Z_r − b · L1_r (projected to L1 = 0);
  p′ is p computed with Z_r′.
- **Leave-one-cell-out:** remove the real-zero candidate with the smallest pass-2 P0 (fraction of samples with count 0;
  ties broken by larger E) from both real and null; p⁻¹ is the recomputed p.

## Decision rules (locked)
p_EVA and p_GLYPH are the cleaned primary p-values of the two units; the same subscripts apply to p′ and p⁻¹.

| Verdict | Condition | Registry action |
|---|---|---|
| **NULL-NOT-ACHIEVED** | The EVA null is not achieved at any admissible β | Annotate C957 "N5 not achievable at spec"; no fallback to a weaker null in this phase; the rival panel uses edge-glyph MI and zone statistics instead of D1 |
| **RESIDUAL** | p_EVA < 0.01 AND p_GLYPH < 0.01 AND p′ < 0.01 for both AND p⁻¹ < 0.01 for both | Tier-2 residual row, no pair list, measurement wording only (no "prohibition"): "common-token zero cells exceed a joint null preserving line composition, zones and per-section boundary coupling (N5, EVA and glyph-unit edges), cross-track cleaned". D1 for the panel = zeros minus each corpus's own N5 expectation, positive control M1 |
| **REDUCES** | p_GLYPH ≥ 0.10 (whatever p_EVA is), or p_EVA ≥ 0.10 with the GLYPH null not achieved | C957 superseded by a reduction row citing C956 and C1212/C1563: "the common-token zero-cell excess is explained by line composition, positional zones and boundary glyph coupling" (stating which unit was needed). D1 dropped from the panel |
| **FRAGILE** | p_EVA < 0.01 and p_GLYPH < 0.01 but p′ or p⁻¹ ≥ 0.01 for either unit; or p_GLYPH < 0.01 with p_EVA ≥ 0.01 | As INCONCLUSIVE, with the fragility named |
| **INCONCLUSIVE** | Anything else | C957 stays at screen level, annotated with the N5 result; no new row |

The raw (uncleaned) statistic, E_min = 5 and the C957-identical data are reported and do not enter the verdict.

## Per-pair output (descriptive only; no pair-level claims under any verdict)
For each real-zero candidate: E, P0, PHASE_753's N1/N2 P0 where available, counts in each other track (F, C, V, T, G,
U), concatenations a+b as single tokens in any track.

## What this phase does not do
It tests no operational meaning ("hazard", "prohibition"). It decides only whether a screen-level zero excess
survives a joint null, as the gate for the rival-generator panel's D1.
