# FL_RESOLUTION_TEST Phase

**Status:** CLOSED
**Verdict:** FL is a deliberately low-impact, ordered annotation layer (NON-EXECUTIVE)
**Tests:** 6 | **Constraints:** C949-C955
**Scope:** Currier B

## Governing Premise

All tests operate at TOKEN / MIDDLE / SUFFIX resolution, strictly conditioned on role and prefix. Role-level and class-level tests are invalid by construction (FL role-independence already established).

## Results Summary

| Test | Hypothesis | Result | Verdict |
|------|-----------|--------|---------|
| T1 (PRIMARY) | FL stage biases token variants within role | 97.1th pctile, p=0.029 | **WEAK PASS** |
| T2 (SECONDARY) | FL-LINK complementary zones | KS p=0.853, MWU p=0.289 | **FAIL** |
| T3 (TERTIARY) | Suffix shifts with FL stage | NMI p=0.657, flat | **FAIL** |
| T4 (SANITY) | FL stage != role (negative control) | Chi2 p=0.441, V=0.069 | **CONFIRMED** |
| T5 (ch-PROBE) | ch-FL stronger effects | Suffix p=0.004 (7x global) | **PARTIAL** |
| T6 (SECTION T) | Section T FL-suppressed | T has 28.4% FL (> S/B 21.2%) | **REJECTED** |

## Interpretation Matrix (Pre-Registered)

| Outcome | Criteria | Status |
|---------|----------|--------|
| FL is assessment output for variant selection | H1 PASS (>99.9th) | **No** - weak pass only |
| FL is canonical ASSESS phase | H1 + H2 PASS | **No** - H2 failed |
| FL indexes degree of completion | H3 PASS | **No** - failed globally |
| Precision sensing mode (ch) | ch-only effects | **Yes** - suffix p=0.004 |
| FL not active in execution grammar | All FAIL | **Nearly** - H1 borderline |

## Final Characterization

> **FL is a per-line, kernel-free, non-executive state trace that records an ordered condition of the process, primarily for documentary purposes, not for internal grammar control.**

FL is structurally real (gradient survives shuffle at p < 0.0001) but largely ignored by execution grammar. The 97th-percentile token-variant signal is consistent with occasional opportunistic reuse, not systematic grammatical uptake. FL had to be informationally weak by design: if it significantly influenced execution, it would encode material semantics (forbidden by C120), create cross-line carryover (forbidden), or compete with kernel-mediated control (forbidden).

The sole exception is ch-prefixed FL, which shows a significant suffix effect (p=0.004, 7x the global effect size), consistent with a precision-annotation submode where state declarations are more tightly coupled to execution parameters.

## Stop Conditions

- FL is NOT part of the control loop (H2 FAIL)
- FL does NOT predict role choice (T4 CONFIRMED)
- FL does NOT affect suffix morphology globally (H3 FAIL)
- No further execution-level tests on general FL are warranted
- ch-FL precision submode is the only open thread

## Scripts

| Script | Test |
|--------|------|
| 01_variant_selection.py | T1: NMI(FL_stage, neighbor_middle) per role/prefix |
| 02_link_complementarity.py | T2: FL-LINK distance + depletion analysis |
| 03_suffix_profile.py | T3: Suffix distribution by FL stage |
| 04_negative_control.py | T4: Chi2(FL stage x role) reconfirmation |
| 05_ch_prefix_probe.py | T5: ch-FL specific retests of T1-T3 |
| 06_section_t_diagnostic.py | T6: Section T FL profile + retests |

## Provenance

- Designed by external expert consultation
- Pre-registered interpretation matrix with hard stop conditions
- All shuffle controls: 1000 iterations, within-prefix-group permutation
- Scope: 11 strong-forward folios (S/B sections) + Section T
