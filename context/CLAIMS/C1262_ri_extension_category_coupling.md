# C1262: RI Extension Character Category Coupling

**Tier:** 2
**Scope:** A
**Phase:** A_CATEGORY_SCATTERSHOT (Phase 452)
**Date:** 2026-02-24

## Statement

The extension character in RI MIDDLEs (the character appended to a PP base per C913) is associated with the operational category of the PP base. Chi-squared=165.2 on 16x8 contingency table (482 RI decompositions), permutation p=0.001, Cramer's V=0.221. Extensions are operationally coupled, not arbitrary identity markers.

## Architecture

- **Extensions are category-sensitive.** The choice of which character extends a PP base is non-random with respect to that base's operational category.
- **Notable associations:** h-extensions concentrate on MARKING bases (50%), k-extensions on OPERATION bases (42%), o-extensions on MONITORING bases (26%), e-extensions on THERMAL bases (24%).
- **Upgrades C913.** C913 established that 90.9% of RI MIDDLEs contain a PP substring. C1262 adds that the extension character is operationally meaningful, not just an identity tag.

## Key Findings

| Metric | Value |
|--------|-------|
| RI MIDDLEs decomposed | 486 / 576 unique RI |
| Filtered (3+ per ext char) | 482 |
| Extension characters | 16 |
| Categories | 8 |
| Chi-squared | 165.2 |
| Cramer's V | 0.221 |
| Permutation p | 0.001 |

### Top Extension-Category Associations

| Extension | Dominant Category | Fraction | Count |
|-----------|-------------------|----------|-------|
| h | MARKING | 0.50 | 16 |
| k | OPERATION | 0.42 | 19 |
| a | MARKING | 0.34 | 50 |
| l | OPERATION | 0.33 | 21 |
| o | MONITORING | 0.26 | 81 |
| e | THERMAL | 0.24 | 51 |

## Provenance

- Builds on C913 (RI derivational morphology), C917, C918
- Extends C1250 (8 operational categories) into RI extension analysis
- PP base identification via C913 methodology (longest PP substring from start)
