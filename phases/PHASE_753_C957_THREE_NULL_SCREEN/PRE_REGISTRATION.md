# PHASE_753 — C957 three-null screen (pre-registration)

**Locked:** 2026-09-27, before any analysis code for this phase was written or run.
**Origin:** STRATEGIC_REVIEW_2026-09-27 §3 #2 (lean-expert top priority; expert-advisor round 2 §2 agrees).
**Claim under test:** C957 (Tier 2): 9 forward token bigrams among the 334 common Currier B tokens have
0 observations despite corpus-wide expected counts ≥ 5 — "the surviving directional prohibition layer of the
hazard topology" (C783 class level demoted; C109 taxonomy struck). The headline P≈5e-17 is a post-selection
product and is not used here.

## Why a new null is needed
C957's original null (`LINE_CONTROL_BLOCK_GRAMMAR/scripts/02_mandatory_forbidden_bigrams.py`) was already a
within-line permutation with a screen-level zero count (real 9 vs 0.64 ± 0.75). Two gaps remain:
1. **Position.** A full within-line shuffle moves tokens into line positions they never occupy. C956: 192 of the
   same 334 tokens are excluded from at least one zone (INITIAL / MEDIAL / FINAL). Zeros between tokens that
   never meet positionally would be C956 restated, not a bigram prohibition.
2. **Boundary phonotactics.** Cross-token edge coupling (last glyph of token N → first glyph of token N+1) is
   already registered (C1212, C1563). If a generator that knows only the previous token's final glyph reproduces
   the zeros, the "prohibition" is boundary phonotactics.
Also, candidates must be defined on each null's own expected counts, not the corpus-wide analytic expectation.

## Data (identical to C957)
`Transcript().currier_b()` (H track, labels and uncertain tokens excluded by default), `*` stripped, lines keyed
by (folio, line). Common tokens: frequency ≥ 10 (expected 334). Bigrams: within-line adjacent pairs where both
tokens are common. Zones per line: INITIAL = position 1, FINAL = last position, MEDIAL = everything between.

## Statistic
For a null model M: E_M(a,b) = mean count of ordered pair (a,b) across M's replicates.
Candidates C_M(E_min) = {(a,b) common×common : E_M(a,b) ≥ E_min}. Primary E_min = 5; sensitivity E_min = 3.
Z_real(M) = number of candidates with real count 0. Null distribution: in each replicate r of M, Z_r = number of
candidates with count 0 in r. One-sided p_M = (1 + #{r : Z_r ≥ Z_real}) / (1 + R).

## Null models
- **N0 — replication (full within-line permutation, C957's original).** R = 1000, seed 7530. Reported both with
  C957's analytic candidate set and with N0's own expected counts. Pipeline check: the analytic version must
  reproduce Z_real = 9 and a null mean ≈ 0.6.
- **N1 — PRIMARY: zone-preserving within-line shuffle.** In each line, the INITIAL and FINAL tokens stay in place
  and the MEDIAL tokens are permuted among themselves. R = 1000, seed 7531.
- **N2 — edge-glyph generator.** Each line keeps its INITIAL token. Each later position i draws, with replacement,
  from the pooled real occurrences of tokens that (a) sit in the same zone as position i (MEDIAL or FINAL) and
  (b) immediately follow, in real data within a line, a token ending in the same final EVA character as the token
  generated at position i−1. If that pool is empty, fall back to the zone-only pool (fallback rate reported).
  Line lengths are the real ones. R = 500, seed 7532.

## Decision rules (locked)
Primary reading at E_min = 5; "holds at E_min = 3" means the same side of the threshold at p < 0.05.
- **CERTIFIED** — p_N1 < 0.01 AND p_N2 < 0.01, holding at E_min = 3. C957's screen-level zero count becomes a usable
  mechanism statistic (panel discriminator D1) for the rival-generator panel.
- **POSITIONAL** — p_N1 ≥ 0.05. The zeros are explained by zone exclusivity (C956 restated); C957 is rescoped as a
  positional consequence and its "directional prohibition" framing is struck.
- **PHONOTACTIC** — p_N1 < 0.01 but p_N2 ≥ 0.05. The zeros reduce to boundary glyph coupling (C1212/C1563); C957 is
  rescoped accordingly.
- **INCONCLUSIVE** — any other combination (a p in [0.01, 0.05)).

## Per-pair analysis (descriptive, no additional verdicts)
For each real-zero candidate: P0_M = fraction of M's replicates in which the pair has count 0. "Robust zero" =
P0 < 0.01 under both N1 and N2. Report C957's original 9, including its two "token-specific" pairs
(chey→chedy, chey→shedy). Report the reverse-pair counts (observed vs E_M) as a descriptive directionality table;
per lean-expert, reverse-at-or-above-expectation cannot by itself separate chance zeros from prohibitions.

## Segmentation check (robust zeros only)
For each robust-zero pair (a,b), count single tokens spelled a+b (concatenation) in the H track and in every other
transcriber track. A robust zero whose concatenated form occurs is flagged SEGMENTATION-SUSPECT (the pair may be
written joined), not counted as evidence for or against a prohibition.

## What this phase does not do
It does not test any operational meaning of the zeros ("hazard"). It decides only whether C957 is a positional,
phonotactic, or genuinely token-level sequential phenomenon, as a gate for the rival-generator panel.
