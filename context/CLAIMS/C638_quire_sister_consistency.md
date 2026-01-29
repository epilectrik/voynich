# C638: Quire Sister Consistency

**Tier:** 2 | **Status:** CLOSED | **Scope:** CURRIER_B | **Source:** SISTER_PAIR_CHOICE_DYNAMICS

## Statement

Quire membership predicts folio-level ch_preference (KW H=32.002, p=0.0001, eta_sq=0.329), with ICC(1,1)=0.362 (FAIR clustering). However, quire is **heavily confounded with section** (Cramer's V=0.875, chi2=251.1). Within section H (the only section spanning multiple testable quires), quire does NOT predict ch_preference (KW p=0.665). Quire has **no independent effect** after controlling for section. Section is the dominant organizational predictor (KW H=27.427, p<0.0001, eta_sq=0.321), substantially stronger than REGIME (KW H=9.882, p=0.020, eta_sq=0.088).

## Evidence

### Quire-Section Structure

9 quires contain B folios with sufficient ch+sh tokens (n=82 total):

| Quire | N | Mean ch_pref | Std | Maps to Section |
|-------|---|-------------|-----|-----------------|
| D | 4 | 0.645 | 0.146 | H |
| E | 8 | 0.708 | 0.099 | H |
| F | 8 | 0.624 | 0.136 | H |
| G | 4 | 0.741 | 0.164 | H |
| H | 3 | 0.533 | 0.075 | H/T (split) |
| M | 20 | 0.486 | 0.059 | B |
| N | 6 | 0.535 | 0.060 | C/T (split) |
| Q | 6 | 0.640 | 0.222 | H |
| T | 23 | 0.683 | 0.120 | S |

Most quires map to exactly one section. Quire M = Section B, Quire T = Section S, Quires D/E/F/G/Q = Section H.

### Kruskal-Wallis Comparison

| Predictor | H | p | eta_sq | Sig |
|-----------|---|---|--------|-----|
| Quire (k=9) | 32.002 | 0.0001 | 0.329 | * |
| Section (k=4) | 27.427 | <0.0001 | 0.321 | * |
| REGIME (k=4) | 9.882 | 0.020 | 0.088 | * |

### ICC(1,1)

- ICC(1,1) = 0.362 (FAIR: 0.2-0.5 range)
- MSB (between-quire) = 0.0797
- MSW (within-quire) = 0.0138
- k0 (adjusted group size) = 8.47

### Quire-Section Confound

- Chi-squared for quire-section independence: chi2=251.1, p<0.0001, dof=32
- Cramer's V = 0.875 (near-perfect association)
- Section H spans quires D, E, F, G, H, Q (32 folios): within-section KW for quire p=0.665 (NOT significant)
- All other sections map to single quires (no stratified test possible)

### Verdict

QUIRE_CONFOUNDED_WITH_SECTION. Quire's apparent predictive power is entirely section-mediated. No independent quire effect survives stratification.

## Interpretation

The FAIR ICC (0.362) reflects section membership, not genuine quire-level clustering. Within section H -- the only section with multiple quires and sufficient data for testing -- quires do not differ in ch_preference (p=0.665). This means the manuscript's physical organization (quires) does not impose an additional constraint on sister pair choice beyond what section already determines. The section-level effect (eta_sq=0.321) is substantially stronger than REGIME (eta_sq=0.088), confirming section as the dominant categorical predictor. C604's REGIME KW replicates exactly (H=9.882).

## Extends

- **C604**: REGIME predicts ch_preference (H=9.882, p=0.020) -- CONFIRMED, but section is 3.6x stronger by eta_sq
- **C450**: Quire effect on HT density (eta_sq=0.150) -- quire effect on ch_preference (eta_sq=0.329) is larger, but confounded

## Related

C412, C450, C604, C637, C639

## Provenance

- **Phase:** SISTER_PAIR_CHOICE_DYNAMICS
- **Date:** 2026-01-26
- **Script:** quire_sister_consistency.py
