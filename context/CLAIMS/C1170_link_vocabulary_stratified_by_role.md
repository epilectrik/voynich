# C1170: LINK Vocabulary Stratified by Role

**Tier:** 2
**Scope:** B, LINK, vocabulary, role
**Phase:** LINK_FUNCTIONAL_ARCHITECTURE (Phase 418)
**Depends on:** C609, C808

## Statement

LINK vocabulary (801 types, 3,047 tokens, 69% hapax) is strongly stratified by ICC role and ol_position. Chi-square test of role × ol_position contingency table: chi2=1493.4, p≈0, Cramér's V=0.404. CC contains exactly 1 type (standalone `ol`, 421 tokens, all MIDDLE). EN has 12 types (MIDDLE/SPAN/SUFFIX only, no PREFIX). AX has 49 types dominated by PREFIX (59.4%, e.g., `olkeedy`, `olchedy`, `olaiin`). FQ has 3 types (all MIDDLE, e.g., `otol`). FL has 1 type (10 tokens, MIDDLE only). UN contains 735 types with the highest diversity (TTR=0.629, entropy=9.16 bits).

## Evidence

### Population
| Metric | Value |
|--------|-------|
| Total LINK tokens | 3,047 |
| Total LINK types | 801 |
| Hapax legomena | 553 (69.0%) |
| Top type | `ol` (421 tokens, CC, MIDDLE) |

### Role × ol_position Cross-Tabulation
| Role | MIDDLE | PREFIX | SPAN | SUFFIX | Total |
|------|--------|--------|------|--------|-------|
| AX | 102 | 475 | 157 | 65 | 799 |
| CC | 421 | 0 | 0 | 0 | 421 |
| EN | 326 | 0 | 146 | 106 | 578 |
| FL | 10 | 0 | 0 | 0 | 10 |
| FQ | 71 | 0 | 0 | 0 | 71 |
| UN | 308 | 400 | 287 | 173 | 1,168 |

### Chi-Square Independence Test
| Metric | Value |
|--------|-------|
| Chi-square | 1493.4 |
| p-value | ≈0 |
| dof | 15 |
| Cramér's V | 0.404 |

### Per-Role Diversity
| Role | Types | Tokens | Entropy (bits) | TTR |
|------|-------|--------|----------------|-----|
| AX | 49 | 799 | 5.08 | 0.061 |
| CC | 1 | 421 | 0.00 | 0.002 |
| EN | 12 | 578 | 2.94 | 0.021 |
| FL | 1 | 10 | 0.00 | 0.100 |
| FQ | 3 | 71 | 1.54 | 0.042 |
| UN | 735 | 1,168 | 9.16 | 0.629 |

## Interpretation

The `ol` substring participates in fundamentally different morphological configurations across roles. In CC, it IS the token. In AX, it serves as a prefix (the token's ol-prefix leads into typical AX morphology). In EN, it appears within the MIDDLE or crosses MIDDLE-SUFFIX boundaries. This stratification means `ol` is not a unified functional marker — it is a morphological component that gets recruited differently by the grammar depending on role context.

## Provenance

- Phase 418 Test 1: LINK_VOCABULARY_STRATIFICATION
- Script: `phases/LINK_FUNCTIONAL_ARCHITECTURE/scripts/link_functional_architecture.py`
- Results: `phases/LINK_FUNCTIONAL_ARCHITECTURE/results/link_functional_architecture.json` → test1_vocabulary_stratification
