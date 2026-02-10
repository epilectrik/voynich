# C949: FL Non-Executive Verdict

**Tier:** 2 | **Scope:** B | **Phase:** FL_RESOLUTION_TEST

## Statement

FL is a per-line, kernel-free, non-executive state trace that records an ordered condition of the process for documentary purposes. It is structurally real but largely ignored by execution grammar, with limited uptake in precision contexts only.

## Evidence

Six-test battery at token/MIDDLE/suffix resolution (pre-registered interpretation matrix):

1. **Token-variant selection (PRIMARY):** NMI(FL_stage, neighbor_MIDDLE) = 0.0552, 97.1th percentile of shuffles (p=0.029). Fails pre-registered 99.9th threshold. Effect driven by EN neighbors only.

2. **FL-LINK complementarity:** No spatial separation (KS p=0.853, MWU p=0.289). FL and LINK independently distributed.

3. **Suffix morphology:** Flat across FL stages (NMI p=0.657, chi2 p=0.751, Spearman rho=0.008).

4. **Negative control:** FL stage does NOT predict role (chi2 p=0.441, V=0.069). Confirmed.

5. **ch-prefix exception:** ch-FL shows significant suffix effect (NMI p=0.004, 7x global). Precision annotation submode.

6. **Section T:** Has MORE FL (28.4%) than S/B (21.2%). Gradient anomaly not from suppression.

## Architectural Necessity

FL had to be informationally weak by design:
- If FL significantly influenced execution, it would encode material semantics (violating C120 PURE_OPERATIONAL)
- Cross-line carryover forbidden (FL resets per line)
- Cannot compete with kernel-mediated control

The 97th-percentile NMI is consistent with a signal that exists, is real, is occasionally glanced at, but holds no safety or control authority.

## Provenance

- `phases/FL_RESOLUTION_TEST/scripts/01_variant_selection.py` through `06_section_t_diagnostic.py`
- Pre-registered test plan with hard stop conditions
- External expert consultation
- Related: C777, C770-C776, C807, C810, C876
