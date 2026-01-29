# C637: B MIDDLE Sister Preference

**Tier:** 2 | **Status:** CLOSED | **Scope:** CURRIER_B | **Source:** SISTER_PAIR_CHOICE_DYNAMICS

## Statement

In Currier B, MIDDLE identity predicts sister pair choice (ch vs sh) with moderate strength: MIDDLE composition explains **22.9% of folio-level ch_preference variance** (rho=0.479, p=0.000005, n=82). B has 77 MIDDLEs meeting threshold (>=5 ch+sh tokens), with a global ch_preference of 0.596. 8 MIDDLEs are >90% ch-preferring, 0 are >90% sh-preferring, and 28 are balanced (40-60%). B is **less MIDDLE-differentiated** than A (mean deviation 0.140 vs C410.a's 0.254). Cross-system A-B MIDDLE preferences are **correlated** (rho=0.440, p=0.003, 44 shared MIDDLEs), confirming MIDDLE preferences are partially intrinsic.

## Evidence

### Per-MIDDLE ch/sh Ratio

- 77 B MIDDLEs with >=5 ch+sh tokens (5,821 total tokens: 3,180 ch + 2,155 sh + 486 other)
- Global B ch_preference: 0.596
- Distribution: 8 >90% ch, 0 >90% sh, 28 balanced (40-60%), 41 moderate
- Mean absolute deviation from global: 0.140 (unweighted), 0.083 (token-weighted)
- Top ch-preferring: a (1.0), cfh (1.0), okch (1.0), kcfh (1.0), okcfh (1.0)
- Top sh-preferring: none above 90%, lowest is eee (0.250)

### Folio-Level MIDDLE Composition Score

Predicted folio ch_preference = weighted mean of per-MIDDLE ch_ratios (weighted by token count):
- Spearman rho: 0.479 (p=0.000005)
- R-squared: 0.229 (22.9% of variance explained)
- Prediction works because high-ch MIDDLEs cluster in certain folios

### Cross-System A vs B Comparison

- 44 MIDDLEs meet >=5 threshold in both A and B
- Spearman rho: 0.440 (p=0.003)
- C410.a top MIDDLEs in B: okch 0.800 (A: 0.963), l 0.882 (A: 0.963), et 0.729 (A: 1.0), s 0.688 (A: 0.929)
- yk below B threshold (only 4 tokens in B)
- A-preferring MIDDLEs generally maintain direction in B but with reduced magnitude

### ok/ot Sister Pair

- 35 MIDDLEs with >=5 ok+ot tokens (2,068 total)
- Global ok_preference: 0.506 (near 50/50, unlike ch/sh's 0.596)
- Less differentiated than ch/sh (mean deviation 0.107 vs 0.140)

## Interpretation

MIDDLE identity carries an intrinsic preference for ch vs sh that is **partially cross-system** (rho=0.440 A-B correlation) but **weaker in B** than A (deviation 0.140 vs 0.254). This 22.9% of folio-level variance is the first identified structural determinant of sister pair choice. The remaining 77.1% is explained by other predictors (section, REGIME, lane balance) and folio-level "free choice" (see C639). The ok/ot pair is less differentiated (near 50/50 globally), suggesting ch/sh carries more structural information than ok/ot.

## Extends

- **C410.a**: A MIDDLE preferences (25.4% deviation) -- B shows same direction but weaker (14.0%)
- **C408**: Sister pairs are equivalence classes -- MIDDLE identity partially breaks equivalence
- **C412**: ch_preference anticorrelates with escape (rho=-0.326) -- MIDDLE composition is one mechanism

## Related

C408, C410, C412, C604, C605, C638, C639

## Provenance

- **Phase:** SISTER_PAIR_CHOICE_DYNAMICS
- **Date:** 2026-01-26
- **Script:** middle_sister_preference.py
