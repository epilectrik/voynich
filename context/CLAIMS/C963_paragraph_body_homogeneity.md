# C963: Paragraph Body Homogeneity

**Tier:** 2 | **Scope:** B | **Phase:** LINE_CONTROL_BLOCK_GRAMMAR, PARAGRAPH_STATE_COLLAPSE

## Statement

Body lines within paragraphs (lines 2+) are compositionally homogeneous. The only progression is line shortening (rho = -0.23). After controlling for line length, no role-composition features show significant progression. This extends to ALL diversity metrics: Shannon entropy (vocabulary, role, suffix, kernel), distinct counts (roles, classes, MIDDLEs, suffixes), and rate-normalized versions are all flat after line-length control.

## Evidence (Original — LINE_CONTROL_BLOCK_GRAMMAR)

- 174 paragraphs with 5+ lines, 1,324 body lines analyzed
- Line length vs position: rho = -0.229, shuffle p = 0.001 (significant, Bonferroni-corrected)
- EN fraction: raw rho = -0.023 (p = 0.350); length-controlled rho ~ 0 (collapsed)
- FL fraction: raw rho = -0.050 (p = 0.068); length-controlled ~ 0
- CC fraction: raw rho = -0.049 (p = 0.076); length-controlled ~ 0
- qo_prefix fraction: raw rho = -0.051 (p = 0.046); length-controlled rho = -0.076 (p = 0.004, fails Bonferroni)
- Only 1/7 features survived Bonferroni correction (needed 3+ for PASS)

## Evidence (Extended — PARAGRAPH_STATE_COLLAPSE)

7 independent tests, all FAIL for diversity collapse:

| Test | Raw rho | Partial rho (length-controlled) | Shuffle p (partial) |
|------|---------|--------------------------------|---------------------|
| Vocabulary entropy | -0.181 | -0.020 | 0.449 |
| Role entropy | -0.156 | +0.009 | 0.611 |
| Suffix entropy | -0.047 | -0.011 | 0.685 |
| n_unique_roles | -0.183 | +0.024 | 0.783 |
| n_unique_classes | -0.275 | -0.010 | 0.348 |
| n_unique_MIDDLEs | -0.281 | +0.027 | 0.833 |
| n_unique_suffixes | -0.181 | -0.026 | 0.210 |

Critical confound: line length correlates with MIDDLE entropy at rho = +0.75. All raw diversity declines are mechanical artifacts of C677 line shortening.

Rate-normalized versions (metric/n_tokens) also show no significant trends.

AX subgroup fractions (INIT/MEDIAL/FINAL) are flat. HT rate is flat (confirming C842 within body).

## Interpretation

Paragraphs shrink toward their ends (C677) but do not change compositional character. Each body line is a structurally equivalent control block — the practitioner writes shorter instructions as the paragraph progresses, but uses the same operational vocabulary throughout. This reinforces C845 (paragraph self-containment).

The "quiet and rigid" appearance of late paragraphs is an optical illusion of line shortening: fewer tokens per line means fewer distinct types per line, but the *rate* (types/token) is unchanged. The effective instruction set does NOT shrink.

## Provenance

- `phases/LINE_CONTROL_BLOCK_GRAMMAR/scripts/08_paragraph_line_progression.py`
- `phases/PARAGRAPH_STATE_COLLAPSE/scripts/01_vocabulary_entropy_collapse.py`
- `phases/PARAGRAPH_STATE_COLLAPSE/scripts/02_role_entropy_collapse.py`
- `phases/PARAGRAPH_STATE_COLLAPSE/scripts/03_suffix_entropy_collapse.py`
- `phases/PARAGRAPH_STATE_COLLAPSE/scripts/04_effective_instruction_set.py`
- `phases/PARAGRAPH_STATE_COLLAPSE/scripts/05_ax_terminal_scaffold.py`
- `phases/PARAGRAPH_STATE_COLLAPSE/scripts/06_ht_ax_substitution.py`
- `phases/PARAGRAPH_STATE_COLLAPSE/scripts/07_kernel_diversity_collapse.py`
- Related: C677, C840, C842, C845, C932, C965
