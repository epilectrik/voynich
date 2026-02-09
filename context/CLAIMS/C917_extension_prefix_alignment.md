# C917: Extension-Prefix Operational Alignment

## Status
- **Tier**: 2 (STRUCTURAL)
- **Status**: CLOSED
- **Source**: Phase A_PP_EXTENSION_SEMANTICS

## Statement

RI extensions in Currier A align with B's PREFIX-MIDDLE operational patterns: 'h'-extension tokens have 82% 'ct' prefix (vs 0% for other extensions), mirroring B's ct+h linker signature (75% of 'ct' prefixes have 'h' MIDDLE).

## Evidence

### Bidirectional ct-h Alignment

**In Currier B:**
- 'ct' prefix + 'h' MIDDLE: 45/60 = 75.0%
- This is the documented linker signature (C837)

**In Currier A RI:**
- 'h'-extension with 'ct' prefix: 46/56 = 82.1%
- ALL other extensions with 'ct' prefix: 0/300+ = 0.0%
- Chi-square: 404.9, p-value: 4.70e-90

### Secondary qo-k/t Pattern

**In Currier B:**
- 'qo' prefix + 'k' MIDDLE: 1706/4069 = 41.9%
- 'qo' prefix + 't' MIDDLE: 501/4069 = 12.3%

**In Currier A RI:**
- 'k'-extension with 'qo' prefix: 29.4%
- 't'-extension with 'qo' prefix: 46.4%

### Extension-Context Mapping

| Extension | Dominant PREFIX | B Pattern | Operational Context |
|-----------|-----------------|-----------|---------------------|
| h | ct (82%) | ct+h linker | monitoring/intervention |
| t | qo (46%) | qo+t terminal | output/terminal |
| k | qo (29%) | qo+k energy | energy/input |
| d | NO_PREFIX (47%) | bare tokens | transitions |
| o | mixed | general | default variant |

## Interpretation

Extensions encode OPERATIONAL CONTEXT alignment:

1. **h-extension** = material variant for LINKER context
   - In B, linker operations use ct+h pattern
   - In A, h-extended materials get ct prefix
   - The extension specifies "use this material in monitoring context"

2. **k/t-extension** = material variant for ENERGY/TERMINAL context
   - In B, energy operations use qo+k pattern
   - In A, k/t-extended materials prefer qo prefix
   - The extension specifies "use this material in energy/output context"

3. **d-extension** = material variant for TRANSITION context
   - Often bare (no prefix)
   - Direct reference without operational wrapper

## Implication

Currier A is an **OPERATIONAL CONFIGURATION LAYER**:
- B provides generic procedures with material slots (PP MIDDLEs)
- A provides context-specific variants of those materials (RI = PP + extension)
- Extensions encode which operational context the variant serves
- PREFIX + MIDDLE + extension = doubly-specified operational reference

This is NOT indexing or arbitrary identification. This is **operational parameterization**.

## Secondary Findings (Tier 3)

### Secondary PREFIX Enrichments

These patterns are statistical enrichments, not dominant correlations like h-extension's 82% ct-prefix rate:

| Extension | Enriched Prefix | Rate | Baseline | Enrichment |
|-----------|-----------------|------|----------|------------|
| o | ct | 18% | 4% | 5.1x |
| l | da | 16% | 5% | 3.1x |
| s | sh | 21% | 7% | 3.1x |
| e | sh | 20% | 7% | 2.9x |

Note: o-extension shows ct-enrichment (5.1x), suggesting some linker-context association, though much weaker than h-extension. The l/s/e extensions show prefix-family associations (da, sh).

### Section Distribution

- h-extension: 1.9x enriched in Section P (43% vs 22% baseline)
- t-extension: concentrated in Section H (93%)

### SUFFIX Correlations

Extensions show systematic suffix associations:

| Extension | Dominant Suffix | Rate |
|-----------|-----------------|------|
| l | -dy | 53% |
| s | -hy | 53% |
| a | -ly | 48% |
| h | -ey | 43% |
| t | -y | 40% |
| o | -dy | 39% |

See C919 for d-extension suffix exclusion (categorically excludes -y family).

## Related Constraints
- C837: ct-ho linker signature
- C913: RI derivational morphology (RI = PP + extension)
- C240: A = NON_SEQUENTIAL_CATEGORICAL_REGISTRY
- C229: Currier A is DISJOINT from B
- C919: d-extension suffix exclusion

## Falsification Criteria

Disproven if:
1. h-extension tokens found with distributed prefix patterns (not ct-dominated)
2. ct prefix appears equally across all extension types
3. Extension-prefix correlation explained by folio/section confounding
