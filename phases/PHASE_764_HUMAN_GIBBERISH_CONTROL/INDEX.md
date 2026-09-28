# PHASE_764 — Human-improvised gibberish vs Currier B boundary coupling

**Status:** COMPLETE. Locked verdict: **MIXED / UNRESOLVED**. Per the locked table this is a phase record only, with
no registry row. STATUS_BRIEF §4 now reads "human gibberish: tested at folio scale, unresolved".
**Pre-registration:** `PRE_REGISTRATION.md`, locked at commit 839f565 after a lean-expert audit (edits E1–E10). The
B-only pre-lock checks are in `results/prelock_b_checks.json`.
**Scripts:** `scripts/gibberish_control.py` (8.8 min), `scripts/g764.py` (shared machinery), `scripts/prelock_b_checks.py`.
**Results:** `results/gibberish_control.json`, `results/run_log.txt`.
**Data:** Gaskell & Bowern 2022 (38 volunteer gibberish samples, 71 meaningful texts). The data sit in
`external/gaskell-bowern`: modified MIT licence, git-ignored, not redistributed; cite the paper.

## Question
Does gibberish improvised by people reach Currier B's boundary coupling, I(last unit of word t; first unit of word
t+1), at matched folio scale (≈ 200–400 within-line pairs)? Gaskell & Bowern did not measure this.

## Certification (all passed)
- **Power:** 0.895 at 224 pairs; 80% at about 197 pairs, so 23 of the 38 samples are used.
- **Positive control:** B single-folio pseudo-samples against B chunks from other folios: AUC 0.515
  [0.387, 0.642], REPRODUCED, CI half-width 0.127 (≤ 0.15).
- **Negative control:** gibberish with its words shuffled within lines: AUC 0.990 [0.981, 0.998], NOT REPRODUCED.

## Result (S1, the only verdict-bearing statistic)
| Comparison | AUC | 95% CI | Label |
|---|---|---|---|
| **B vs gibberish (AUC_BG)** | **0.825** | **0.714–0.919** | **UNRESOLVED** (the lower bound misses 0.80) |
| Meaningful vs gibberish (AUC_MG) | 0.585 | 0.453–0.703 | — |
| B vs meaningful (AUC_BM) | 0.775 | 0.751–0.797 | — |

**Variants** (none flips the label, and none can upgrade UNRESOLVED):

| Variant | AUC | Label |
|---|---|---|
| V1, EVA characters | 0.862 | UNRESOLVED |
| V2, top-6 binning | 0.976 | NOT REPRODUCED |
| V3, segment-matched null | 0.814 | UNRESOLVED |
| V4, edge-fixed shuffle | 0.913 | NOT REPRODUCED |
| V5, normalised by H(F1) | 0.883 | NOT REPRODUCED |

**Sensitivities:** ZL counting all spaces 0.891; H track 0.878; single-folio reference 0.835. All UNRESOLVED.

**Reading:**
- In every version B's coupling exceeds most gibberish samples: point estimates run from 0.81 to 0.98. That is
  consistent, but with 23 writers the uncertainty band does not clear the pre-registered bar.
- Some individual writers reach B's level: J_G = 0.57 of gibberish samples fall inside B's 5–95% band at their size,
  against J_M = 0.63 for meaningful chunks.
- **Meaningful text sits about as far below B as gibberish does** (AUC_BM 0.775 vs AUC_BG 0.825), and it is
  indistinguishable from gibberish on this statistic (AUC_MG 0.585).
- So B's strong boundary coupling is a property that separates B from human-written text in general. It is not a
  meaning-versus-gibberish discriminator.

## Descriptive (not verdict-bearing)
| Quantity | Gibberish | B | Meaningful |
|---|---|---|---|
| S3: first unit × line position (B vs G AUC) | — | **0.986** (B far stronger) | not computed (artificial wraps) |
| S4: adjacent identical repetition, log O/E | −0.35 | **+0.03** | −1.35 |
| Near-repeat rate (adjacent words at edit distance ≤ 1) | 0.015 | **0.049** | 0.010 |
| H(first unit), bits | 4.06 | **3.10** | 3.94 |
| S2 (ending routing), pair-weighted mean | 0.006 | set-mean median −0.052 | — |

- **S2** is uninterpretable at this size. The power check had already shown this: at small N the conditional MI is
  dominated by estimator bias, which differs with alphabet size.
- **B is more rule-bound at the word and line level than either human group.** Its position-in-line dependence is
  much stronger, as are adjacent repetition and near-repetition, and its word-initial choice is narrower.
- The S3 contrast is a **lead, not a result**. It was descriptive, the samples' line-break provenance is not
  documented, and gibberish lines are shorter. A confirmatory test would need data not used here.

## What this does and does not show
- **It does not rule out gibberish.** Modern improvisers reach B's coupling in some samples, and the pre-registered
  bar was not met.
- **It does not support meaning.** B differs from meaningful text on these statistics about as much as it differs
  from gibberish.
- **It does show** that on every low-level measure taken here, B is more constrained than casual human writing of
  either kind. That fits a practised, rule-governed system: a notation, a cipher, or trained habitual writing. The
  question is which, and folio-scale statistics from short modern samples cannot say.

## Deviations
None beyond those declared in the pre-registration (D1 resolution threshold; D2 ZL as primary B).
- **Positive control:** the reference excludes chunks that *start* on the pseudo-sample's folio. A chunk may still run
  into that folio when it crosses a folio boundary.
- **Cross-folio chunks:** 79% of B reference chunks cross a folio boundary within their section, because a chunk
  starts at a random line and needs about 200–400 pairs. The single-folio-only reference gives the same picture (AUC
  0.835).
