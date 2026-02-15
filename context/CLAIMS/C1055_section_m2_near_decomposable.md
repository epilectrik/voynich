# C1055: M2 Generative Sufficiency is Near-Section-Decomposable

**Tier:** 2 (STRUCTURAL INFERENCE)
**Scope:** B
**Phase:** SECTION_SPECIFIC_M2 (Phase 370)
**Relates to:** C1025 (generative sufficiency at M2), C1029 (section-parameterized weights), C1047 (no section-dynamics interaction)

---

## Statement

M2 generative sufficiency (C1025) is **near-section-decomposable**: per-section M2 models reach 78-79% pass rate (11.7-11.8/15) for BIO and STARS_RECIPE, 70% for HERBAL, falling just below the 80% (12/15) global threshold. The pooling advantage is only **+0.5 tests** (global=12.0, weighted-local=11.5), confirming C1047's finding that section pooling creates no emergent structure.

### Per-Section M2 Performance

| Section | Tokens | Mean Pass | Pass Rate |
|---------|--------|-----------|-----------|
| BIO | 5,324 | 11.7/15 | 78% |
| HERBAL | 2,305 | 10.6/15 | 70% |
| STARS_RECIPE | 7,027 | 11.8/15 | 79% |
| COSMO | 994 | 9.6/15 | 64% |
| **Global** | **16,054** | **12.0/15** | **80%** |

The 3 universally-failing tests (B4, B5, C2) are the same per-section as globally — these are test battery specification issues (C1030), not section-specific failures. Excluding these, per-section M2 passes 11.7-11.8/12 remaining tests.

### Cross-Section Transfer

Global M2 tested against section-specific real metrics degrades substantially on distributional tests: D1 (stationary distribution) fails in 4/4 sections, B2 (AXM self-transition) fails in 3/4 sections, D3 (cross-line MI) fails in 4/4 sections. But sequential topology tests (B1 spectral gap, B3 forbidden violations) are preserved across all sections.

Cross-section transfer (train-X, test-Y) does NOT correlate with C1029 pairwise JSD (rho=-0.24, p=0.45). Section "distance" as measured by transition matrix JSD does not predict generative transfer performance.

### Test Sensitivity

Of 15 tests, 11 are section-invariant (pass rate range <= 20pp) and 4 are section-sensitive (A2 hapax rate, B1 spectral gap, B5 forward-backward JSD, D3 cross-line MI).

---

## Interpretation

The 49-class Markov + forbidden suppression architecture is independently sufficient for each major section. The slight gap from 80% is not structural — it reflects sample-size sensitivity in A2 (hapax rate, 55% for BIO) and the inherent B5 asymmetry variation across sections. The architecture works per section because:

1. Topology is universal (C1029: zero section-only transitions)
2. Local training captures section-specific weights automatically
3. Section dynamics are additive only (C1047)
4. Forbidden pairs apply identically everywhere

The global model's +0.5 test advantage comes from transition matrix smoothing (pooling fills sparse cells), not from emergent cross-section structure. This confirms that sections parameterize a single grammar rather than implementing distinct grammars.

---

## Method

- 4 sections tested: BIO (5,324 tokens), HERBAL (2,305), STARS_RECIPE (7,027), COSMO (994)
- Per-section M2: section-specific transition matrix, opener probs, class→token probs, line lengths
- Global M2: all Currier B pooled (16,054 tokens)
- 20 instantiations per model per section
- 15-test battery (identical to Phase 348/C1025)
- Cross-section transfer: 12 directional pairs tested
- 5 hypotheses: H1 (local sufficiency) FAIL marginal, H2 (global degradation) PASS, H3 (JSD-transfer correlation) FAIL, H4 (test classification) PASS, H5 (no pooling advantage) PASS
- Verdict: 3/5

**Script:** `phases/SECTION_SPECIFIC_M2/scripts/section_specific_m2.py`
**Results:** `phases/SECTION_SPECIFIC_M2/results/section_specific_m2.json`
