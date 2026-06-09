# C2077: Self-Citation / Copy-Modify Generation Excluded as a Complete Account of Currier B

**Tier:** 2 | **Scope:** B | **Phase:** SELF_CITATION_HEAD_TO_HEAD | **Date:** 2026-06-08
**Class:** adversarial-external negative knowledge (rival from outside the prior; kill conditions
pre-registered before generator construction; human-signed-off wording)

## Statement

Self-citation/copy-modify generation (Timm–Schinner class; uniform glyph kernel, 8 parameters
including Yule–Simon long-range copying), fitted to Currier B's surface statistics (vocabulary
growth, edit-distance-1 network, adjacency rates, Zipf, token length), is **excluded as a complete
account of Currier B**:

1. **Fit stage:** even at its optimum (~500 evaluations, loss 10.8→2.62), the uniform-kernel
   generator over-generates the type inventory 1.8× (8,777 vs 4,889) with under-steep Zipf
   (−0.56 vs −1.05) while matching the edit-distance-1 network density almost exactly
   (15.99 vs 15.31) — **B's novelty production is morphology-channeled** (new words land inside
   the existing lattice); uniform mutation is not.
2. **K2 (production process):** the generator's adjacent-line copy-explainability gap
   (−0.108 [−0.115, −0.102]) is absent from B (−0.019, near the no-copy controls M2/scramble
   ≈ 0.00) — the copy mechanism cannot avoid its production signature; B does not have it.
3. **K4 (local autocorrelation):** the generator forces within-line e-depth autocorrelation
   (lag1 0.20 [0.12, 0.29]; lag2 0.19 [0.10, 0.28]) that B lacks (+0.035 / +0.056) — and the
   M2 49-class Markov baseline reproduces B's value almost exactly (0.032), so **the failure is
   specific to the copying mechanism**, not to generative models per se.
4. **K1′ (directional token zeroes, supporting):** the generator never expresses the 9 forbidden
   ordered token bigrams at evaluable expectation (its joint E = 0.9 vs B's 35.5 — its lexicon
   drifts off B's high-frequency core, same root cause as 1) and produces zero directional-zero
   census pairs in 200/200 runs vs B's 1 (thin secondary).

## Evidence (B vs 200-corpus fitted-generator ensemble; controls N=60)

| stat | B | generator [2.5%, 97.5%] | M2 Markov | scramble |
|---|---|---|---|---|
| K2 copy-explainability gap | −0.019 | −0.108 [−0.115, −0.102] | −0.001 | −0.000 |
| K4 e-depth lag1 | +0.035 | 0.202 [0.117, 0.292] | 0.032 | 0.030 |
| K4 e-depth lag2 | +0.056 | 0.193 [0.104, 0.283] | 0.009 | 0.028 |
| K1′ fwd O/E (9 bigrams) | 0.000 (E=35.5) | 0.51 [0.00, 2.40] (E=0.9 — inexpressible) | 0.46 | 0.96 |
| K1′ census | 1 | 0.00 [0, 0] | 1.75 | 0.02 |

## Caveats (recorded at registration)

- The K4 sign-prediction in the lock was mis-calibrated (C2032's −0.66 is a different
  instrument; B's lag1 on this operationalization is +0.035). The pre-registered ensemble
  criterion (P3) carried the kill, not the sign.
- K1′ is supporting, not independent (expressibility failure + 1-count census); K3 correlated
  with K1′, counted as supportive only.
- B's faint adjacent-line trace (−0.019 vs controls ~0) is attributable to paragraph-level
  state homogeneity (C1967/C1834), not copy-execution; the H-HYBRID question (designed content
  written with some copy influence) remains open at that whisper level — what is excluded is
  copy-modify as the *generative source* of B's structure.
- Excludes the self-citation CLASS as fitted (uniform kernel, ≤10 params, single fit per P2);
  the empirical-kernel secondary was not run — by the locked P1 interpretation its passes would
  mean "morphological structure required," already demonstrated at fit stage. Other generation
  mechanisms (e.g., table/grille) are not directly tested here.

## Side findings (same phase, Phase 0)

- **C783 DEMOTED 2→3:** the 17 "forbidden class transitions" show NO aggregate suppression at
  the class level (powered pairs forbidden-direction O/E = 1.13 strict-adjacency; one pair 2×
  enriched) — registry compression of token-level facts. The real prohibition layer is
  token-level (C957), where directionality is confirmed: 9 forward bigrams at 0 obs vs ~37.5
  joint expectation (P≈5e-17), reverses at-null.
- **C458 DEMOTED 2→3:** the clamp/free CV asymmetry (0.72 raw gap) collapses to 0.089 under
  frequency matching — each set sits at its own frequency-matched null (hazard 82nd pctile,
  recovery 36th). Frequency shadow (C475 class), compounded by densities-vs-counts measurement
  mixing. The regime-separation half of C458 is untested by this audit and stands.

## Provenance

- `phases/SELF_CITATION_HEAD_TO_HEAD/PRE_REGISTRATION.md` (locked design + Phase 0/1 results)
- Scripts: `p0_preflight_audits.py`, `p0b_strict_adjacency_verification.py`,
  `p1_generator_fit.py`, `p1b_refine.py`, `p2_battery.py`
- Results: `results/p0_preflight_audits.json`, `p0b_strict_adjacency.json`,
  `p1_generator_fit.json`, `p2_battery.json`

## References

C957 (token-level forbidden bigrams — the surviving prohibition layer), C783/C109 (class-level
framing demoted/annotated), C458 (demoted leg), C501/C511 (the copy-compatible facts the rival
DOES explain), C2055 (char-Markov surface — the rival's home field), C1967/C1834 (paragraph
homogeneity explains B's faint adjacency trace), C2052/C2076 (the adversarial-external test
pattern this extends).
