# C1231 - Universal Suffix Mode Centroids

**Tier:** 2 | **Scope:** B | **Phase:** EXTRACTION_CYCLING_VALIDATION (Phase 439)

## Statement

The two suffix modes identified within individual paragraphs (C1229) converge on universal centroids across all 55 qualifying paragraphs: Mode A = [terminal=0.430, connector=0.019, iterate=0.086, bare=0.466], Mode B = [terminal=0.155, connector=0.031, iterate=0.072, bare=0.741]. Global silhouette using paragraph-derived labels is 0.293 (>0.2 threshold); re-clustering all body lines globally yields silhouette 0.428. Between-mode variance exceeds within-mode variance by F=4.56. The modes are a universal grammar property, not paragraph-specific noise.

## Evidence

### Mode universality statistics

| Metric | Value |
|--------|-------|
| Paragraphs with mode assignments | 55 |
| Total body lines analyzed | 635 |
| Within-mode variance (mean) | 0.008 |
| Between-mode variance | 0.038 |
| F-statistic | 4.560 |
| Global silhouette (paragraph labels) | 0.293 |
| Global silhouette (refit k=2) | 0.428 |

### Global centroids

| Suffix category | Mode A | Mode B | Difference |
|-----------------|--------|--------|------------|
| Terminal | 0.430 | 0.155 | +0.275 |
| Connector | 0.019 | 0.031 | -0.012 |
| Iterate | 0.086 | 0.072 | +0.014 |
| Bare | 0.466 | 0.741 | -0.275 |

### Key observations

1. **Terminal vs bare is the primary discriminator**: The two modes differ by 27.5 percentage points on terminal and bare fractions, with connector and iterate nearly identical
2. **Refit silhouette exceeds paragraph-based**: Global k=2 clustering (0.428) outperforms paragraph-derived labels (0.293), meaning line-level structure is even cleaner than paragraph-level mode assignment captures
3. **F > 2 confirms universality**: Modes are more different from each other than individual paragraphs' modes vary from the global centroids

## Interpretation

The two operational modes are universal features of the B grammar, not local variation within the ~57% design freedom envelope (C980). Every paragraph with sufficient body lines exhibits the same binary alternation between a specification-heavy phase (Mode A) and a continuation-heavy phase (Mode B). This supports the interpretation that paragraphs encode iterative processes with a universal control structure.

## Related constraints

- C1229: Alternating suffix modes within paragraphs (discovery of two modes)
- C1230: Mode MIDDLE differentiation (functional grounding of modes)
- C963: Body homogeneity at role-fraction level (modes operate at finer grain)
- C980: Free variation envelope (modes are NOT within-envelope noise)

## Provenance

- `phases/EXTRACTION_CYCLING_VALIDATION/scripts/extraction_cycling_test.py` (T6)
- `phases/EXTRACTION_CYCLING_VALIDATION/results/extraction_cycling_results.json`
