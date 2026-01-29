# C733: PP Token Variant Line Structure

**Status:** VALIDATED | **Tier:** 2 | **Phase:** PP_LINE_LEVEL_STRUCTURE | **Scope:** A

## Finding

Whole PP token co-occurrence within Currier A lines is non-random **beyond MIDDLE assignment**. The specific token variant (PREFIX+SUFFIX combination) chosen to represent a MIDDLE on a given line is correlated with the variants of other tokens on that line.

### T9a: Whole-Token Free Shuffle

| Metric | Value |
|--------|-------|
| Unique PP word forms | 2,372 |
| Unique PP MIDDLEs | 389 |
| Token/MIDDLE ratio | 6.10x |
| Observed unique word pairs | 20,757 |
| Null (free shuffle) unique | 21,646 +/- 75 |
| p (fewer unique) | < 0.001 |
| Observed word pair variance | 0.897 |
| Null variance | 0.710 +/- 0.031 |
| p (higher variance) | < 0.001 |

### T9b: Variant Shuffle (MIDDLE Assignment Preserved)

| Metric | Value |
|--------|-------|
| Observed unique word pairs | 20,757 |
| Variant-null unique | 21,094 +/- 60 |
| p (fewer unique) | < 0.001 |
| Observed word pair variance | 0.897 |
| Variant-null variance | 0.791 +/- 0.028 |
| p (higher variance) | < 0.001 |

The variant shuffle holds MIDDLE-to-line assignment fixed and only randomizes which token form fills each MIDDLE slot within the folio. T9b's significance means the specific variant choice is structured, not just the MIDDLE identity.

## Decomposition

The free shuffle (T9a) produces a larger gap (889 fewer unique pairs) than the variant shuffle (T9b, 337 fewer). This decomposes the total word-level structure into:
- **~62%** explained by MIDDLE assignment (incompatibility)
- **~38%** explained by token variant selection (PREFIX+SUFFIX coordination)

Note: at the MIDDLE level, variance was BELOW null (C728, p=1.0). At the whole-token level, variance is ABOVE null (p<0.001). This reversal means specific token variants are concentrated — some word-pair combinations are enriched while others are depleted — even though their underlying MIDDLEs show no concentration.

## Implication

MIDDLE-level analysis (C728) concluded that within-line PP selection is random beyond incompatibility. This is true for MIDDLEs but NOT true for whole tokens. The PREFIX and SUFFIX dimensions carry structured selection that the MIDDLE decomposition masks.

This is consistent with C697 (PREFIX clustering within lines) and C730 (PREFIX-MIDDLE coupling): lines select not just compatible MIDDLEs but specific morphological variants. The combination of PREFIX coherence and MIDDLE incompatibility produces whole-token co-occurrence patterns that neither dimension explains alone.

**Revised summary:** A lines draw MIDDLEs randomly from the compatibility-valid pool, but select specific morphological variants of those MIDDLEs in a coordinated fashion.

## Provenance

- Script: `phases/PP_LINE_LEVEL_STRUCTURE/scripts/pp_whole_token_test.py` (T9a, T9b)
- Extends: C728 (MIDDLE co-occurrence), C697 (PREFIX clustering), C730 (PREFIX-MIDDLE coupling)
- Refines: C732 (uniformity holds for SUFFIX and diversity, but not whole-token variant)
