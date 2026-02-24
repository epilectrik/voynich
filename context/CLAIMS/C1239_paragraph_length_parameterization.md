# C1239 - Paragraph Body Length Parameterization

**Tier:** 2 | **Scope:** B | **Phase:** PARAGRAPH_TERMINATION_MECHANICS (Phase 442)

## Statement

Paragraph body length is section-parameterized (F=17.35, eta2=0.107) and REGIME-parameterized (F=12.55, eta2=0.061). Within sections, termination is roughly memoryless (HERBAL var/mean=0.92, T=1.06). BIO averages 6.15 body lines, HERBAL 2.80. ~85% of length variance is folio/paragraph specific. The overall non-geometric distribution (chi2=64.30) is a mixture artifact, not evidence of cross-line memory.

## Evidence

### Overall distribution (n=584 paragraphs)

| Metric | Value |
|--------|-------|
| Mean body length | 4.0 lines |
| Std dev | 3.61 |
| Geometric chi2 | 64.30 (df=10) |
| Geometric p | 0.2498 |

### Section effects (ANOVA)

| Section | Mean body lines |
|---------|----------------|
| B (BIO) | 6.15 |
| C | 4.88 |
| S (STARS) | 3.62 |
| T | 3.05 |
| H (HERBAL) | 2.80 |

- F = 17.35, eta2 = 0.107 (section explains 10.7% of variance)

### REGIME effects (ANOVA)

| REGIME | Mean body lines |
|--------|----------------|
| REGIME_1 | 5.03 |
| REGIME_4 | 3.32 |
| REGIME_3 | 3.26 |
| REGIME_2 | 3.07 |

- F = 12.55, eta2 = 0.061 (REGIME explains 6.1% of variance)

### Within-section memorylessness

| Section | var/mean ratio | Geometric T-stat |
|---------|---------------|-----------------|
| HERBAL | 0.92 | 1.06 (near-geometric) |
| T | ~1.0 | ~1.0 |
| BIO | 5.00 | overdispersed (folio variation) |
| STARS | 2.22 | overdispersed (folio variation) |

### Key finding

The overall non-geometric distribution is a mixture artifact: different sections have different termination rates, and mixing geometric distributions produces a non-geometric aggregate. Within sections (especially HERBAL), termination is roughly memoryless — each line independently decides to stop with a section-specific probability.

## Interpretation

Paragraph length is set by the process type (section) and operational context (REGIME), not by internal state accumulation. Each extraction pass (line) independently terminates with a probability parameterized by the section. BIO processes run longest because thermal-intensive extraction requires more passes. HERBAL processes are shortest. This confirms C1237's steady-state model.

## Related constraints

- C854: A=4.8L, B=4.37L mean paragraph length
- C860: Section parameterizes paragraph COUNT per folio
- C1237: -am paragraph termination, steady-state execution
- C1233: Cross-line independence

## Provenance

- `phases/PARAGRAPH_TERMINATION_MECHANICS/scripts/termination_analysis.py`
- `phases/PARAGRAPH_TERMINATION_MECHANICS/results/termination_analysis.json`
