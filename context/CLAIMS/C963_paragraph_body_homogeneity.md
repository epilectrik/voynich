# C963: Paragraph Body Homogeneity

**Tier:** 2 | **Scope:** B | **Phase:** LINE_CONTROL_BLOCK_GRAMMAR

## Statement

Body lines within paragraphs (lines 2+) are compositionally homogeneous. The only progression is line shortening (rho = -0.23). After controlling for line length, no role-composition features show significant progression.

## Evidence

- 174 paragraphs with 5+ lines, 1,324 body lines analyzed
- Line length vs position: rho = -0.229, shuffle p = 0.001 (significant, Bonferroni-corrected)
- EN fraction: raw rho = -0.023 (p = 0.350); length-controlled rho ~ 0 (collapsed)
- FL fraction: raw rho = -0.050 (p = 0.068); length-controlled ~ 0
- CC fraction: raw rho = -0.049 (p = 0.076); length-controlled ~ 0
- qo_prefix fraction: raw rho = -0.051 (p = 0.046); length-controlled rho = -0.076 (p = 0.004, fails Bonferroni)
- Only 1/7 features survived Bonferroni correction (needed 3+ for PASS)

## Interpretation

Paragraphs shrink toward their ends (C677) but do not change compositional character. Each body line is a structurally equivalent control block — the practitioner writes shorter instructions as the paragraph progresses, but uses the same operational vocabulary throughout. This reinforces C845 (paragraph self-containment).

## Provenance

- `phases/LINE_CONTROL_BLOCK_GRAMMAR/scripts/08_paragraph_line_progression.py`
- Related: C677, C840, C845
