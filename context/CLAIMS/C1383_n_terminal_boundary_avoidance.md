# C1383: n-Terminal MIDDLE Boundary Avoidance

**Tier:** 2
**Scope:** B
**Phase:** GLOSS_PREDICTION_TESTS (Phase 495)
**Date:** 2026-03-02

## Statement

n-terminal MIDDLEs systematically avoid positional and mode boundaries in Currier B. They are depleted at suffix mode transitions (0.81x, chi2=23.9, p<0.0001) and depleted at line-final positions (0.694x, chi2=22.4, p=0.000005). The line-final depletion holds in 4/5 sections (B=0.73x, H=0.97x, S=0.56x, T=0.47x; only C=1.13x weakly inverts). n-terminal MIDDLEs concentrate in steady-state, mid-line, mid-mode regions — they are interior atoms that avoid all tested boundary types.

## Evidence

### E1: Mode boundary avoidance (from P6 test)

| Position | n-terminal rate | Other rate | Ratio |
|----------|----------------|------------|-------|
| Mode transition lines | 8.35% | 10.30% | 0.81x |
| Non-transition lines | 10.30% | baseline | — |

- Chi-squared: 23.914, p < 0.0001

### E2: Line-final avoidance (from P9 test)

| Position | n-terminal rate | Other rate | Ratio |
|----------|----------------|------------|-------|
| Line-final | 7.45% | 10.73% | 0.694x |
| All other | baseline | baseline | — |

- Chi-squared: 22.433, p = 0.000005
- Section breakdown: B=0.73x, C=1.13x, H=0.97x, S=0.56x, T=0.47x

### E3: Mean line position

- n-terminal mean normalized position: 0.479
- Other mean normalized position: 0.502
- Mann-Whitney p = 0.001

## Relationship to Existing Constraints

- **C1208** (Tier 2): Classifies n as NEGATIVE anti-clustering (z=-4.3 to -6.1). C1383 extends this from token-to-token carryover to line-level positional behavior — n avoids clustering at boundaries just as it avoids clustering with itself.
- **C1209** (Tier 2): n is 99.4% terminal within MIDDLEs. C1383 shows this within-MIDDLE terminality does NOT translate to line-level terminality — n is positionally final *inside* MIDDLEs but positionally interior *across* lines.
- **C1210** (Tier 2): n-terminal is forbidden with non-iteration INITIAL atoms (a→n 0/796, e→n 1/813). C1383 extends the boundary-avoidance pattern to line-level structure.
- **C1382** (Tier 2): k and a are mode-polarized. n is mode-avoiding — it concentrates where mode is stable, not where mode changes. n is the anti-boundary atom.

## Interpretation

n marks steady-state continuation. It avoids mode transitions (where the program switches operational phase), line-final positions (where routing decisions occur per C1235), and consecutive self-repetition (C1208). This is consistent with n encoding "sustain/iterate" — an instruction that by definition belongs in the middle of an ongoing process, not at its boundaries. Any future prediction involving n at boundaries should be expected to fail.
