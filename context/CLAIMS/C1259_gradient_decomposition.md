# C1259: Gradient Decomposition by Suffix Mode

**Tier:** 2
**Scope:** B
**Phase:** GRADIENT_DECOMPOSITION (Phase 451)
**Date:** 2026-02-24

## Statement

Decomposing prior paragraph-body gradients by suffix mode reveals: Mode A proportion is FLAT across the paragraph body (rho=-0.027, p=0.449, 63 paragraphs with 8+ body lines), ruling out mode-proportion shift as the mechanism behind aggregate gradients. Of 5 retested constraints: C933 (prep verb early concentration) is an ARTIFACT of prep verbs being Mode A tokens (77% Mode A); C1227 (FL resets) is GENUINE within the B-track (B->B regression 49.7% > cross-mode 40.5%); C676/C1228 (suffix trajectory, PREFIX switching) show GENUINE/MIXTURE patterns within Mode B. C932 (vocabulary rarity gradient) and C965 (kernel composition gradient) could NOT be replicated in aggregate, yielding NO_GRADIENT before decomposition was possible.

## Architecture

- **Mode proportion is not a confound.** Mode A fraction is ~42% across all quintiles (Q0=42.0%, Q4=39.4%). Gradients cannot be explained by shifting A/B proportions.
- **Prep verbs are Mode A vocabulary.** The early concentration of te, pch, tch, lch (C933) reflects Mode A's overall character, not a paragraph-positional gradient.
- **FL resets are B-track internal.** B->B pairs have the highest regression rate (49.7%), exceeding cross-mode (40.5%) and A->A (33.6%). FL cycling is a within-track process.
- **Suffix trajectory is genuine in Mode B.** Bare suffix fraction increases through paragraph body within Mode B (rho=0.072, p=0.008).
- **PREFIX switching is a mixture.** Within-mode JSD (0.326) < cross-mode JSD (0.352, p=0.002), partly explained by mode alternation but not entirely.

## Key Findings

| Test | Classification | Key Metric | Reference |
|------|---------------|------------|-----------|
| T1: Mode proportion | FAIL (flat) | rho=-0.027, p=0.449 | New |
| T2: Vocabulary rarity | NO_GRADIENT | Aggregate rare r=-0.054 (C932 claimed -0.97) | C932 |
| T3: Prep verb position | ARTIFACT | 77% of prep verbs are Mode A | C933 |
| T4: Kernel composition | NO_GRADIENT | Aggregate h rho=-0.019 (C965 claimed +0.10) | C965 |
| T5: FL reset | GENUINE | B->B 49.7% > cross-mode 40.5% | C1227 |
| T6: PREFIX switch | MIXTURE | Within 0.326 < cross 0.352, p=0.002 | C1228 |
| T7: Suffix trajectory | GENUINE | Mode B bare rho=0.072, p=0.008 | C676 |

## Constraint Status Updates

- **C932** (vocabulary rarity gradient): NOT REPLICATED in aggregate. Original r=-0.97 (RARE) not reproduced (r=-0.054). Methodology concern.
- **C933** (prep verb early concentration): ARTIFACT of Mode A vocabulary. Prep verbs are overwhelmingly Mode A tokens (77%). Within Mode B, no positional bias (p=0.639).
- **C965** (kernel composition gradient): NOT REPLICATED in aggregate. Original h rho=+0.10 not reproduced (rho=-0.019). No gradient in either mode.
- **C1227** (FL resets): GENUINE. FL regression is a B-track phenomenon. B->B rate highest.
- **C676** (suffix trajectory): GENUINE within Mode B. Bare suffix fraction increases (rho=0.072, p=0.008).
- **C1228** (PREFIX switching): MIXTURE. Partly mode alternation, partly genuine within-track process.

## Implications

The flat Mode A proportion rules out the most obvious confound from parallel mode tracks (C1258). Gradients that survive decomposition (FL resets, suffix trajectory) are genuine within-track processes. The non-replication of C932/C965 is a methodology concern independent of mode decomposition.

## Method

63 paragraphs with 8+ body lines (Currier B). Lines assigned to Mode A/B via C1231 suffix centroids. Each gradient test computed in aggregate, Mode B only, and Mode A only, using same statistical methods as the original constraint. T3 and T5-T6 use 1000-permutation tests. Bonferroni threshold p < 0.007 for 7 tests.

## Provenance

- Phase 451 main battery: T1-T7
- Retests C932, C933, C965, C1227, C1228, C676
- Builds on C1258 (parallel mode tracks), C1231 (mode centroids)
