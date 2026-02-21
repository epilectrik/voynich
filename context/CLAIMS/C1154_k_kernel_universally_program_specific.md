# C1154: k-Kernel and e-Kernel Variance Are Universally Program-Specific

**Tier:** 2
**Scope:** B, kernel, section differentiation
**Phase:** SECTION_CONDITIONED_GENERATIVE_FIDELITY (Phase 411)
**Depends on:** C1150, C1152

## Statement

The k-kernel (execution) and e-kernel variance across folios is ~2x larger than section-M2 can reproduce, uniformly across all sections (k: 1.82-2.32x, e: 1.76-2.21x). The h-kernel (monitoring) is section-determined in 3 of 4 sections (BIO 1.29x, HERBAL 1.04x, COSMO 0.74x) but program-specific in STARS_RECIPE (2.18x). Execution strategy is always a program-level decision; monitoring requirements can be either section-level or program-level depending on domain.

## Evidence

| Section | k ratio | h ratio | e ratio | h captured? |
|---------|---------|---------|---------|-------------|
| BIO | 2.32x | 1.29x | 2.21x | YES |
| COSMO | 2.11x | 0.74x | 2.10x | YES |
| HERBAL_B | 1.82x | 1.04x | 1.88x | YES |
| STARS_RECIPE | 1.99x | 2.18x | 1.76x | NO |

**k-kernel:** Uniformly uncaptured (mean 2.06x). The amount of active execution each folio performs is never determined by section membership alone. This is consistent with C1150's finding that dark-dominant folios shift k_frac independently of section.

**h-kernel:** Section-determined in BIO, HERBAL, COSMO (ratio 0.74-1.29x) — these sections have characteristic monitoring requirements. Program-specific in STARS_RECIPE (2.18x) — this mixed section contains procedures with widely varying monitoring needs.

**e-kernel:** Uniformly uncaptured (mean 1.99x), tracking k-kernel closely. The k/e pairing suggests these operate as a coupled execution pair, distinct from h-kernel monitoring.

## Structural Implication

The k/e vs h asymmetry suggests two kernel subsystems:
- **Execution pair (k, e):** Always program-specific. How much active operation a procedure requires.
- **Monitoring operator (h):** Domain-determined in specialized sections, program-determined in general sections.

This is consistent with C1150's kernel shift finding: dark-dominant folios (material-heavy) reduce k-kernel execution, and this shift is program-level, not section-level.
