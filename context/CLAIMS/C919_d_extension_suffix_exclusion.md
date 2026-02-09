# C919: d-Extension Suffix Exclusion

## Status
- **Tier**: 2 (STRUCTURAL)
- **Scope**: A
- **Status**: CLOSED
- **Source**: Phase A_PP_EXTENSION_SEMANTICS

## Statement

The d-extension categorically excludes -y family suffixes (0% rate) while all other extensions show 46-83% -y suffix rates. The d-extension takes -iin/-al suffixes instead, indicating it belongs to a different grammatical class (END-class).

## Evidence

### Suffix Family Distribution by Extension

| Extension | -y family suffix | -iin family suffix |
|-----------|------------------|-------------------|
| s | 83% | 8% |
| t | 82% | 0% |
| l | 60% | 0% |
| o | 52% | 2% |
| a | 47% | 0% |
| h | 46% | 0% |
| **d** | **0%** | **14%** |

### d-Extension Suffix Pattern

- d+aiin: 7 occurrences
- d+al: 6 occurrences
- d+ar: 3 occurrences
- d+NO_SUFFIX: 26 occurrences (53%)

The d-extension NEVER combines with -y, -dy, -hy, -ly, -ey, or any -y family suffix.

### Contrast with Other Extensions

| Extension | Top Suffix | Rate |
|-----------|------------|------|
| l | -dy | 53% |
| s | -hy | 53% |
| a | -ly | 48% |
| h | -ey | 43% |
| t | -y | 40% |
| o | -dy | 39% |
| **d** | **-aiin** | **14%** |

## Interpretation

### END-Class Mechanism

The d-extension appears to function as an END-class element (per C510 compositional grammar). Since -y suffixes are also closers/END-class, combining d-extension with -y would create a grammatical violation (double closer).

This explains:
1. Why d-extension takes -iin/-al instead (compatible suffixes)
2. Why d-extension often has NO_SUFFIX (53%) - it's already a closer
3. Why all other extensions freely combine with -y family

### Operational Context

Combined with C917 (d-extension has 47% NO_PREFIX):
- d-extension = "bare" transition variant
- Takes -iin (state markers) not -y (continuation markers)
- Functions as transition/closure context

## Related Constraints

| Constraint | Relationship |
|------------|--------------|
| C917 | Extension-prefix alignment (d has 47% NO_PREFIX) |
| C918 | A as operational configuration layer |
| C510-C512 | Positional sub-component grammar (END-class) |
| C277 | -y suffix as continuation/closer marker |

## Falsification Criteria

Disproven if:
1. d-extension tokens found with -y family suffixes at >5% rate
2. The 0% rate explained by sampling artifact or folio confounding
3. Other extensions found with similar -y exclusion pattern
