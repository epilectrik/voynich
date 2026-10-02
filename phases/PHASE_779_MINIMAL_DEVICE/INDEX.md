# PHASE_779 — The minimal device: which of B's registered regularities is a sampler of the measured rules not outside?

**Status: DESIGN v2 (design audit incorporated); fidelity gate PASSED with the Metropolis sampler; plant grids
running; not yet locked.**
- **Question:** take the simplest sampler of B's measured specification (page × line-type composition, line-position
  vocabulary, two-unit junction routing). On eight registered regularities it is not given, is B inside or outside
  its ensemble? A layer map: what follows from the rules, what is an extra layer.
- **Device:** `scripts/mind779.py`. Stocks per page × line type, drawn without replacement; zone tables with
  back-off for rare words; within-line routing weights divided by the first-unit marginal; a within-cell
  Metropolis sampler (the sequential sampler failed the fidelity gate through depletion). Ladder R0L → R1L → R2aL →
  R2L (primary) → R3L; page-only, memo, with-replacement and header-extension variants.
- **Predictions (counted):** glyph-unit line homogeneity (C1214 relative), within-folio paragraph PREFIX JSD
  (C1811/C1812), pair zeros in C2081's form, e-run lag-1 agreement, qo/ch-sh alternation (C549), hapax dispersion,
  e-run medial position gradient (C1671), the C2056 lane. Each powered by a plant with a declared grid (MDE80).
- **Panel:** D3–D5 tested; D2 (and D6 on the memo variant) are fidelity statistics.
- Pre-registration: `PRE_REGISTRATION.md`.

## Result on Currier B
Pending the lock and the run.
