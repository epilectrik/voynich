# C924: HT-RI Shared Derivational Morphology

## Status
- **Tier**: 2 (STRUCTURAL)
- **Scope**: GLOBAL
- **Status**: CLOSED
- **Source**: Phase EXTENSION_DISTRIBUTION_PATTERNS

## Statement

HT (Human Track) MIDDLEs show 97.9% containment in PP vocabulary, with 15/16 extension characters overlapping with RI extensions. RI and HT share the same derivational system (PP + extension), with differentiation at the PREFIX level, not the MIDDLE level.

## Evidence

### HT MIDDLE Containment

| Metric | Value |
|--------|-------|
| HT tokens analyzed | 8,424 |
| Unique HT MIDDLEs | 592 |
| HT MIDDLEs in PP directly | 405 (68.4%) |
| HT MIDDLEs NOT in PP | 187 |
| HT-only containing PP | 183/187 = **97.9%** |
| HT-only containing Core PP | 181/187 = **96.8%** |

### Containment by System

| System | HT Tokens | HT-only MIDDLEs | Containment |
|--------|-----------|-----------------|-------------|
| Currier A | 2,051 | 94 | 96.8% |
| Currier B | 5,198 | 2 | 100% |
| AZC | 1,175 | 100 | 99.0% |

### Extension Vocabulary Overlap

| Vocabulary | Characters |
|------------|------------|
| RI extensions | a, c, d, e, f, h, i, k, l, m, n, o, p, q, r, s, t, y |
| HT extensions | a, c, d, e, f, g, h, k, l, m, o, p, r, s, t, y |
| **Overlap** | **15/16 = 94%** |
| HT-only | g |

### Top HT Extensions

| Extension | Count |
|-----------|-------|
| a | 14 |
| d | 7 |
| r | 7 |
| l | 6 |
| c | 5 |
| h | 5 |

## Interpretation

### Unified Derivational Model

```
MIDDLE = PP + extension  (same in both RI and HT)

RI token = [A/B PREFIX] + [PP + ext] + [SUFFIX]
HT token = [HT PREFIX]  + [PP + ext] + [SUFFIX]
```

### Architectural Implications

| Layer | Determines |
|-------|------------|
| PREFIX | Function (operational vs identification vs annotation) |
| PP MIDDLE | Material/content vocabulary (shared substrate) |
| Extension | Discrimination refinement (unified across RI and HT) |
| SUFFIX | Context/phase marker |

### Why HT Containment (97.9%) > RI Containment (90.9%)

HT appears to be a "purer" derivative layer. RI has more A-internal specialization (9.1% non-PP content), while HT is more strictly derived from the shared PP substrate.

## Comparison to C913

| System | Containment Rate | Extension Chars |
|--------|------------------|-----------------|
| RI (C913) | 90.9% | 18 |
| HT | 97.9% | 16 |
| Overlap | - | 15/16 = 94% |

## Related Constraints

| Constraint | Relationship |
|------------|--------------|
| C913 | RI Derivational Morphology - parallel finding |
| C347 | HT Disjoint PREFIX Vocabulary - confirmed |
| C452 | HT Unified PREFIX across systems - compatible |
| C461 | HT correlates with rare MIDDLEs - explained by derivation |
| C610 | UN/HT novel MIDDLEs contain PP atoms - confirmed |
| C766 | UN = Derived Identification Vocabulary - compatible |

## Falsification Criteria

Disproven if:
1. Larger HT sample shows containment rate < 80%
2. HT extension vocabulary diverges significantly from RI
3. Alternative MIDDLE derivation model explains HT better
