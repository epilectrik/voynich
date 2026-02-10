# RISK_PROFILE_MIGRATION Phase

**Status:** CLOSED
**Verdict:** WEAK — No hazard sub-group migration; kernel shift is safe-space only
**Tests:** 7 (01-07)
**Scope:** Currier B (23,243 tokens, 2,420 lines, 83 folios)

## Governing Premise

C965 (kernel composition shift: h rises, e drops through paragraph body) survived the PARAGRAPH_STATE_COLLAPSE phase. External expert proposed this might reflect deeper risk-profile evolution: the *type* of risk being managed shifts even while total risk exposure stays constant.

Central question:
> Does the hazard sub-group mix shift in tandem with the kernel composition shift, indicating risk type migration within a fixed control envelope?

## Results Summary

| Test | Topic | Verdict | Key Finding |
|------|-------|---------|-------------|
| T01 | Hazard Rate Flatness | **PASS** | Hazard fraction ~22.8%, flat (partial rho=+0.007, p=0.81). C458 confirmed. |
| T02 | Hazard Sub-Group Migration | **FAIL** | FL_HAZ, EN_CHSH, FQ_CONN, FQ_CLOSER — all flat |
| T03 | Risk Type Migration | **FAIL** | PHASE_ORDERING, COMPOSITION_JUMP, CONTAINMENT, RATE_MISMATCH — all flat |
| T04 | Kernel Hazard vs Safe | **PARTIAL** | C965 shift present in SAFE pool only (h rho=+0.09, p=0.002), absent from hazard pool |
| T05 | Hazard-Escape Dynamics | **FAIL** | FL_HAZ and FL_SAFE rates both flat |
| T06 | Risk-Kernel Cross-Correlation | **PASS** | Per-line rho=0.48 (p~10^-60), shuffle p=0.001 — but partly mechanical (EN_CHSH = ch/sh prefix = h-kernel) |
| T07 | Integrated Verdict | **WEAK** | Score 2.5/6.0 |

## Key Findings

### 1. C458 Design Clamp Extends to Paragraph Level (T01)

Total hazard-involved fraction is ~22.8% per line, completely flat across quintiles. The design clamp that keeps hazard exposure constant across folios (C458, CV=0.04-0.11) also operates within paragraphs. Risk is truly stationary.

### 2. Hazard Sub-Group Mix Does NOT Shift (T02, T03)

The relative proportions of FL_HAZ (initiator), EN_CHSH (absorber), and FQ_CONN/FQ_CLOSER (relay/closer) do not change through body lines. All four sub-group fractions and all four failure class exposures are flat after length control. There is no risk type migration.

### 3. C965 Kernel Shift Is Safe-Space Only (T04)

The h-kernel rise and e-kernel decline operate exclusively in non-hazard tokens:
- **Safe pool**: h_fraction partial rho = +0.090 (p=0.002, Bonferroni significant)
- **Hazard pool**: h_fraction partial rho = +0.048 (p=0.23, not significant)

This means C965 is a compositional drift within the *operational* instruction space, not a change in *hazard mediation strategy*.

### 4. EN_CHSH <-> h-Kernel Cross-Correlation Is Partly Mechanical (T06)

The per-line cross-correlation between EN_CHSH share and h-kernel fraction is rho=0.48 (p~10^-60), significant vs shuffle null (p=0.001). However, this is partly a mechanical effect: EN_CHSH tokens are *defined* by ch/sh prefixes, which *are* the h-kernel marker. Lines with more EN_CHSH hazard tokens mechanically have higher h-kernel fractions. The shuffle test (pooling hazard labels across lines) confirms this is a real per-line association, but it reflects the structural identity between sub-group definition and kernel classification, not independent co-evolution of risk and mediation.

## Interpretation

The expert's hypothesis — that the *risk type* evolves while capability stays constant — is **not supported**. The hazard system is flat in every dimension tested: total rate, sub-group mix, failure class exposure, escape sub-type, and hazard-kernel coupling.

C965 (kernel composition shift) is real but operates in the **non-hazard instruction space**. Late body lines use more h-kernel (ch/sh prefix) tokens among safe operations (AX, CC, safe EN, safe FQ), while hazard-involved tokens maintain their composition throughout.

The refined interpretation of C965:
> Late body lines don't change what risks they manage — they change which **safe operational vocabulary** they prefer. The h-kernel rise in safe tokens may reflect a grammar-wide preference for ch/sh-prefix monitoring operations in later control blocks, independent of hazard management.

## Stop Conditions

- Phase verdict: WEAK (2.0/6.0)
- No hazard sub-group migration detected
- No failure class redistribution
- Kernel shift localized to safe tokens — not a risk mediation signal
- The "tandem" hypothesis (C965 + hazard migration) is falsified
- No further hazard-positional investigation warranted

## Scripts

| Script | Test | Output |
|--------|------|--------|
| 01_total_hazard_rate_flatness.py | T01 | 01_*.json |
| 02_hazard_subgroup_migration.py | T02 | 02_*.json |
| 03_risk_type_migration.py | T03 | 03_*.json |
| 04_kernel_mediation_hazard_vs_safe.py | T04 | 04_*.json |
| 05_hazard_escape_positional_dynamics.py | T05 | 05_*.json |
| 06_risk_kernel_cross_correlation.py | T06 | 06_*.json |
| 07_integrated_verdict.py | T07 | 07_*.json |

## Provenance

- Designed in response to external expert proposal after PARAGRAPH_STATE_COLLAPSE phase
- Pre-registered pass/fail criteria per test
- Hazard sub-groups from C601, C541, C586
- Failure class mapping from C109, C541
- Kernel classification from PARAGRAPH_STATE_COLLAPSE T07
- All length controls: partial Spearman rho via OLS residualization
- All shuffle controls: 1000 iterations, seed=42, within-paragraph line permutation
- Bonferroni correction within each script
