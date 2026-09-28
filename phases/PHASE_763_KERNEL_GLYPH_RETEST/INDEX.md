# PHASE_763 — Glyph-level re-test of "kernel-centric"

**Status:** COMPLETE. Locked verdict: **MIXED**, registered as C2082, which supersedes C089.
**Pre-registration:** `PRE_REGISTRATION.md`, locked at commit af4a55b after two lean-expert design audits (v1 → v3).
**Script:** `scripts/kernel_retest.py`, 61 min.
**Results:** `results/kernel_retest.json`, `results/run_log.txt`.
**Post-hoc exploration** (not pre-registered, not verdict-bearing): `scripts/explore_arm_s_decomposition.py` →
`results/explore_arm_s_decomposition.json`.

## Question
Is the glyph-level kernel {k, e, bench (ch/sh)} more central than frequency- and position-matched control glyphs?
- **Within tokens (Arm W).**
- **In what a token carries about the next one, beyond its first glyph (Arm S).**

This is the fair test the Tier-0 restatement called for (v7.24). The old evidence, X_adversarial_audit Attack 1,
ranked EVA letters and could not fail.

## Results (locked rules)

**Arm S — cross-token routing beyond the prefix channel: PASS (Holm).**

The statistic is I(g ∈ t; class(t+1) | first glyph unit of t), Miller–Madow corrected, compared with the PHASE_756 N5
null (glyph edges, β = 2). The N5 gates passed after one pre-registered extension: R-hat 1.002, minimum ESS 1,509,
fraction changed 0.83, TV within tolerance.

| Variant | Kernel mean z | Control-triad median | E | p (89 triads) |
|---|---|---|---|---|
| **Primary (S1)** | 6.50 | 2.12 | **4.39** | **0.011** (minimum attainable) |
| R1: target = first glyph of t+1 | 8.37 | 1.63 | 6.74 | 0.011 |
| R2: + length bin, target = role | 2.24 | 1.40 | 0.85 | 0.056 |
| R3: ZL transcription | 6.61 | 1.88 | 4.74 | 0.011 |
| S2 (h-bearing glyphs merged) | 6.38 | 2.50 | 3.88 | 0.013 |
| Unconditional MI (descriptive) | 12.69 | 4.08 | 8.60 | 0.011 |

- **Folio-bootstrap E:** 95% interval 2.4–7.5.
- **Generator floors:** neither generator reproduces the effect. Naibbe GV1/P-REC E ranges −0.5 to 1.0; Timm–Schinner
  −0.8 to 1.2 (20 members each; the members' N5 gates are reported, not enforced).
- **Power certification:** failed. π\* = 0.5, detection 54% < 80%. This only matters for a FAIL, and Arm S passed.

**Per glyph (descriptive): the pass is not a kernel property.**

| Glyph | e | bench | k | d (non-kernel) | t | y | a | o |
|---|---|---|---|---|---|---|---|---|
| z (primary) | **10.1** | **7.6** | 1.8 | **8.9** | 3.8 | 3.6 | 2.2 | −0.7 |

- k sits at the median of its controls (a, d, o, t, ckh).
- The non-kernel glyph d is as strong as the bench.
- The trio passes because e and bench are strong and the bench's controls (p, t, o, s, cth) are weak.

**Post-hoc decomposition (exploration): the signal is the word ending.** Each row adds more of token t to the
conditioning set; the target is class(t+1).

| Conditioning on token t | e | bench | d | k |
|---|---|---|---|---|
| first glyph (the Arm S statistic) | 9.7 | 7.8 | 8.9 | 1.9 |
| + last glyph | 5.0 | 2.4 | 3.5 | 1.6 |
| + last two glyphs | 1.9 | 1.5 | −0.4 | 0.8 |
| class of t | 4.2 | 4.9 | 4.0 | 0.8 |

Once the last two glyph units of a token are known (its -dy / -ey / -edy type ending), the "kernel" glyphs add
almost nothing. So what Arm S measured is this: **a token's ending predicts the next token's class beyond the
last-glyph → first-glyph coupling**. That coupling is C1212/C1563, and N5 holds it fixed. The finding extends it to
the two-glyph ending and to the class of the next token; compare C1002 (the suffix sequential grammar, e.g. edy → edy)
and C2061.

**Arm W — within-token centrality: INCONCLUSIVE.**

The statistic is centred random-walk closeness, compared with the edge-anchored run-block permutation null
(R = 1,000). The RWB identity check held to a relative error of 5e-15.

| | Kernel mean z | Control-triad median | E | p (79 triads) |
|---|---|---|---|---|
| H (S1) | 18.3 | 10.9 | 7.4 | 0.088 |
| S2 | 20.6 | 15.0 | 5.6 | 0.41 |
| ZL | 19.0 | 11.0 | 7.9 | 0.14 |
| Type-weighted (descriptive) | 4.1 | 2.9 | 1.1 | 0.44 |

- **Uncertified.** At π = 1.0 the plants reach a mean E of 4.4, but detection is 0/100: the plant (moving a kernel run
  to the first interior slot) also displaces the control glyphs, so some control triads score as high as the kernel.
  Arm W therefore cannot return FAIL.
- **Glyph order raises almost every glyph's closeness.** a 31.7, e 25.3, o 24.3, k 20.6 (the controls a and o score as
  high as the kernel). This is closer to a property of any ordered script than of a kernel.
- **Floors:**
  - Latin: the best letter triads have E 28–35, so the result is not distinctive.
  - Naibbe and Timm: E ranges 13.2–18.5 and 8.1–22.3. B's kernel effect (7.4) lies below both.
  - Currier A: E 3.5, just below B's downsample range (3.7–7.6).
- **Folio-bootstrap interval for E:** −30 to 58. The within-token statistic is unstable across folios.

**Overall: MIXED.** Only the cross-token arm passes, and its per-glyph structure shows it is word-ending routing, not a
kernel.

## Registry actions (locked table: MIXED)
- **C2082 (Tier 2, new):** the Arm S measurement, worded as ending-to-next-class routing and stating the per-glyph
  facts. It supersedes C089.
- **C089:** STATUS:SUPERSEDED by C2082. "Kernel-centric" is not restored.
- **C103–C105:** role glosses, annotated; they stay at Tier 3.
- **Tier 0 and the Tier-3 working interpretation:** wording unchanged; the PHASE_763 result is noted.

## Deviations
- **H_S2 node set:** f (236 instances) falls outside the 99% coverage node set, so it is merged into X and cannot be
  ranked. It is therefore absent from the S2 pool. The S2 control sets are unchanged.
- **First full run:** it crashed on a numba cache-loading error, caused by how the script imported the N5 module. The
  fix gave the script its own numba cache directory and registered the imported module under its name. Nothing
  statistical changed, and the stages that had finished reproduced exactly.
- **Arm W plant (D3):** the plant design did not certify. Arm W therefore could not return FAIL, as the locked rules
  provide.

## Side observation (not part of this phase)
PHASE_760 ran its N_EDGE null at β = 4. PHASE_756's diagnostics show that setting does not mix (fraction-changed ESS
≈ 5). PHASE_760's verdict also rested on the N1 null, which agreed, but the N_EDGE arm should be re-run at β = 2.
