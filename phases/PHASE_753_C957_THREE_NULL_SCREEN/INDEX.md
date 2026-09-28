# PHASE_753 — C957 three-null screen

**Status:** COMPLETE (locked verdict reported; post-hoc analysis reported; C957 disposition pending the lean-expert rigor review requested 2026-09-27).
**Pre-registration:** `PRE_REGISTRATION.md`, committed 4f6373c before any code.
**Script:** `scripts/c957_three_null_screen.py` (v3; ~1.6 min). **Results:** `results/c957_three_null_screen.json`
(v1 output with a per-pair tracking bug kept as `results/c957_three_null_screen_v1_TRACKING_BUG.json`).

## Question
Is C957's "9 forbidden token bigrams" layer a token-level sequential phenomenon, or does it reduce to positional
zone exclusivity (C956) or boundary glyph coupling (C1212/C1563)? Gate for the rival-generator panel
(STRATEGIC_REVIEW_2026-09-27 §3 #2).

## Data (identical to C957)
2,420 lines, 23,096 tokens, 334 common tokens (freq ≥ 10), 10,061 within-line adjacent common-token pairs.
Replication: the analytic E≥5 set has 58 pairs and 9 real zeros; the full within-line shuffle gives 0.66 zeros
(C957 reported 0.64 ± 0.75). Pipeline reproduces C957.

## Locked result
Statistic: number of candidate pairs (each null's own mean count ≥ E_min) with real count 0, against the same
count in each replicate.

| Null | Candidates E≥5 / E≥3 | E≥5: real zeros, null mean, p | E≥3: real zeros, null mean, p |
|---|---|---|---|
| N0 full within-line shuffle (C957's original) | 67 / 172 | 2, 0.08, 0.003 | 20, 2.21, 0.001 |
| **N1 zone-preserving within-line shuffle (primary)** | 81 / 219 | 3, 0.06, 0.001 | 24, 2.63, 0.001 |
| **N2 edge-glyph generator** | 82 / 218 | 2, 0.12, 0.004 | 9, 3.66, 0.012 |

**Locked verdict: CERTIFIED** (p_N1 < 0.01 and p_N2 < 0.01 at E≥5; both < 0.05 at E≥3). Read strictly: the
zero-cell count is not explained by positional zones alone, nor by boundary glyph coupling alone.

## Post-hoc analysis (does not change the locked verdict)
**Bug found and fixed (v2).** v1 tracked per-pair zero frequencies only for pairs that were candidates under the
same null; untracked pairs defaulted to "never zero", which falsely flagged 9 pairs as robust under both N1 and N2.
v2 tracks one union set (38 pairs) under every null. Screen-level statistics were unaffected.

**Per pair (v2):** no pair is robust (P0 < 0.01) under both N1 and N2. C957's nine named pairs all have
P0 under N2 between 0.038 and 0.594 — for example chedy→aiin (expected 0.77 under N2) and chey→shedy (P0 0.124).
The zeros that surprise N1 are explained by N2 and vice versa: N1 keeps line composition but destroys edge
coupling; N2 keeps edge coupling but destroys composition.

**Joint nulls.**
- N3 (permute medial tokens only among same first/last-glyph signature within a line) is **degenerate**: it
  changes 12.7% of positions (N1: 67.9%) and reproduces edges exactly, so it "explains" every zero by construction.
  Not used.
- N4 (keep each line's initial and final tokens and its medial multiset; re-order medial tokens with each pick
  weighted by the real last-glyph → first-glyph transition rate) changes 67.2% of positions and halves the edge
  mismatch (edge-distribution TV 0.082 vs 0.183 for N1, 0.022 for N2). Screen under N4: E≥5 1 real zero vs 0.06
  (p = 0.058); E≥3 18 vs 2.47 (p = 0.002). The N4 excess sits on aiin→aiin, daiin→aiin and ol→qokain — all
  boundary pairs (n→a, l→q) that the full-edge null N2 explains (P0 0.23–0.33) — plus chey→chedy (P0 0.004 under
  N4, 0.038 under N2).

| Null | Positions changed per replicate | Edge-distribution TV vs real |
|---|---|---|
| N0 | 0.887 | 0.202 |
| N1 | 0.679 | 0.183 |
| N2 | 0.890 | 0.022 |
| N3 | 0.127 | 0.000 |
| N4 | 0.672 | 0.082 |

## Reading
1. The locked verdict stands: the zero count exceeds each single mechanism.
2. C957's named list is **not** a list of token-specific prohibitions: individually, its pairs are mostly
   boundary-glyph coupling (-y → a-, n → a, l → q) plus line composition.
3. Whether a residual zero excess survives a fully joint null (composition + zones + exact edge-transition
   counts, with real freedom) is **unresolved**: N4 reproduces edges only halfway, and its excess is carried by
   edge-type pairs.
4. For the rival panel, the zero-cell screen can serve only as a comparison statistic computed identically on
   real text and generator output, never as evidence of specific prohibitions. Do not quote P≈5e-17.

## Proposed disposition (pending lean-expert review)
Annotate C957: strike "surviving directional prohibition layer of the hazard topology"; keep the screen-level
measurement at Tier 2 with the scope above; mark the named pair list and the "token-specific" chey pairs as
largely boundary-coupling. Update frozen_conclusion.md / contracts wording accordingly.
