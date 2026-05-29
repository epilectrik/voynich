# PHASE_738: qo→CHSH Window-Control Discriminating Test

**Status:** COMPLETE — **VERDICT: C549 = real token-order structure (Test C, above composition); above-char-Markov status INDETERMINATE — the char-Markov null is the WRONG INSTRUMENT for this token-adjacency claim. Sentinel control (Tests A/D) one-sided/biased toward SURVIVE, proven uninformative by Test E.**
**Resolves:** the PHASE_737/C2064 cascade flag — is C549 (qo→ch/sh) / C2056 (correction lanes) survival a window-blindness artifact (like daiin) or genuine above-Markov structure?

> **NOTE:** the in-script "combined verdict" (ABOVE-MARKOV CONFIRMED) from Tests A–D is SUPERSEDED by Test E. The sentinel non-collapse was an artifact of suffix-sentinel corruption, not real supra-token structure. Read the Final Verdict section below.

## Question

PHASE_737 found daiin→CHSH survival is window-blindness-eligible (the char-5-gram cannot condition on a long source token's prefix identity at the boundary). `qol` (qo-prefixed short token) demoted, raising the worry that C549/C2056 — whose qo-prefixed sources are mostly LONG — survive only by the same artifact. C549/C2056 were just elevated as Layer-1 "local control bigrams" in the consolidation banner.

## Three complementary tests (qo-prefixed source → next-token-starts-ch/sh)

**Test C — within-line token shuffle (correct instrument; is the adjacency real above composition?):**

| source | real | shuffle | z | p | verdict |
|---|---|---|---|---|---|
| short-qo (≤4) | 0.396 | 0.265 | 6.23 | 0.000 | REAL token-order |
| long-qo (≥5) | 0.281 | 0.243 | 5.91 | 0.000 | REAL token-order |
| all-qo | 0.292 | 0.245 | 7.87 | 0.000 | REAL token-order |

**Test B — standard char-5-gram null, length-split (windowing diagnostic):**

| source | real_exc | synth_exc | z | p | verdict |
|---|---|---|---|---|---|
| short-qo | +0.1383 | +0.0984 | 1.78 | 0.020 | survive (weak; **fails** Bonferroni α=0.0167) |
| long-qo | +0.0358 | +0.0158 | 3.26 | 0.000 | survive (clear) |

**Test A — sentinel-injection (prefix-family in boundary window; mechanism test), long-qo:**

| | real_exc | synth_exc | z | p | verdict |
|---|---|---|---|---|---|
| long-qo + qo-family sentinel | +0.0373 | +0.0202 | 2.39 | 0.000 | **survive — NO collapse** |

## Reading

- **The adjacency is real above composition** (Test C, all three, p=0.000) — qo→ch/sh is genuine token-order structure, not composition shadow. This is the clean, decisive result and the grounding for the verdict.

## Test D — stem/token-resolution sentinel (each of 522 distinct qo-tokens gets a unique suffix char)

real_exc +0.038, synth_exc +0.021, z=2.54, p=0.000 → SURVIVE. Predicted COLLAPSE (if residual were stem-local); it did not. **But this SURVIVE is an artifact — see Test E.**

## Test E — sentinel-fidelity audit (the non-circular proof, mandatory per expert sign-off)

The Test A/D SURVIVE has two indistinguishable readings from the residual alone: (a) the suffix-sentinel is ungeneratable so the synth mis-tags qo-tokens → Test D biased toward SURVIVE → uninformative, vs (b) a real sentinel-invariant supra-token signal. Both predict A≈D≈standard-B. Crazy-expert's discriminating test: MEASURE the synth's sentinel-emission fidelity directly, stratified by length.

| stratum | n | correct-unique-sentinel | sentinel-is-qo-char |
|---|---|---|---|
| short-qo (len ≤4) | 20,422 | **0.996** | 0.998 |
| long-qo (len ≥5) | 176,381 | **0.281** | 0.336 |

Fidelity gap short−long = **+0.714**, sharply length-dependent. For long qo-tokens — which carry the *entire* surviving residual — the generator emits the correct sentinel only 28% of the time (and emits *no* qo-family sentinel 66% of the time). **The suffix-sentinel could not inject qo-identity for long tokens; Test A/D were biased toward SURVIVE; their non-collapse is uninformative.** Reading (a) confirmed by direct measurement, not circular inference.

## FINAL VERDICT

- **C549 (qo→ch/sh): real token-order structure ABOVE COMPOSITION** — clean, decisive, length-invariant (Test C, z 5.9–7.9, p=0.000). This is the valid grounding.
- **Above-char-Markov status: INDETERMINATE.** The standard-5-gram survival (Test B) is window-blindness-eligible (PHASE_737: the char-5-gram cannot observe a long source token's prefix at the boundary). The sentinel control built to fix this is itself broken: a suffix-appended sentinel must be predicted from prefix-blind suffix context, so it is unusable at generation for long tokens (Test E: 28% fidelity). The char-Markov instrument is **exhausted** for this token-adjacency claim under all three regimes — low-order (window-blind), suffix-sentinel (ungeneratable), high-order (overfits). The +0.017 sentinel-surviving residual is at the project's noise floor (<5pp) AND from a biased instrument — carries no weight.
- **C549 is the WRONG kind of claim for the char-5-gram null.** It is a token-adjacency / prefix-routing claim; the correct null is the within-line token shuffle (Test C), which it passes decisively. "Survives/fails the 5-gram null" is neither necessary nor sufficient for it.
- **daiin (PHASE_737) stays separate and ambiguous** — different role (CC vs ENERGY), different instrument; qo's result does not transfer.
- **PHASE_737 short-witness reconciliation:** individual short tokens (qol) being char-reproducible was the wrong generalization for the token-adjacency claim — the char-5-gram verdict tracks token length (windowing), not validity. Test C (length-invariant) is the instrument that doesn't have this pathology.

## Disposition

- **C549: PROVISIONAL → CONFIRMED on Test-C grounds** (real token-order structure above composition). Drop the "above-char-Markov" framing as wrong-instrument/indeterminate. Add the instrument caveat.
- **C2056: REVISED from 5-lane to 4-lane family** (Test C on all five lanes, source=qok, within-line token shuffle, Bonferroni α=0.010, N_shuf=500):
  - **CONFIRMED above composition (4/5):** qok→ok (z=4.27, p=0.002), qok→ot (z=2.35, p=0.008, marginal), qok→ch (z=8.12, p=0.000, strong), qok→oke/ok-e (z=4.25, p=0.002).
  - **DEMOTED (1/5):** qok→sh (passive monitor) — z=1.97, p=0.018, fails Bonferroni; above-shuffle excess +1.0pp, under C2056's own <5pp falsification clause; consistent with it being the weakest lane in the original (+17pp residual / real +4.7% above shuffle). The active-monitor (ch) lane is strong; the passive-monitor (sh) lane drops out.
  - Sanity check: broad qo→ch/sh z=7.93 reproduces PHASE_738 Test C all-qo z=7.87. The architectural unit (post-heat correction window, multiple above-composition lanes) STANDS; the specific 5-lane composition is corrected to 4. C929 (ch=active / sh=passive) note: the passive lane is the one that fails the composition control.
- **Methodology — new failure pattern (9th/10th):** "null cannot observe the claimed antecedent" — a char-Markov null is the wrong instrument for token-adjacency claims whose conditioning variable (source prefix) is not in any usable char-window; sentinel-injection fixes fail because suffix sentinels are ungeneratable. Diagnostic: a verdict that flips with token length is windowing, not structure; confirm with a within-line token-shuffle (composition) null and a direct sentinel-fidelity audit.
