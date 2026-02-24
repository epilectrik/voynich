# C1236 - Suffix Scope Markers

**Tier:** 2 | **Scope:** B | **Phase:** CONTROL_LOOP_ARCHITECTURE (Phase 441)

## Statement

Terminal suffixes (-edy, -dy, -eey) are Mode A specification markers (2.5-3.0x enriched in Mode A). Checkpoint suffixes (-aiin, -ain) are mode-independent loop controllers (1.25x slight Mode A enrichment, NOT Mode B markers). Mode A lines average 36.1% terminal suffixes; Mode B lines average 62.0% bare tokens. Mode A = specification lines (set parameters), Mode B = execution lines (continue processing).

## Evidence

### Token counts

| Mode | Tokens |
|------|--------|
| Mode A | 9224 |
| Mode B | 12931 |

### Terminal suffix enrichment in Mode A

| Suffix | Mode A enrichment |
|--------|-------------------|
| -edy | 2.99x |
| -om | 2.94x |
| -dy | 2.54x |
| -eey | 2.50x |
| -hy | 2.31x |
| -ey | 2.27x |
| -am | 1.92x |

### Checkpoint suffix enrichment

| Suffix | Mode A enrichment | Interpretation |
|--------|-------------------|----------------|
| -aiin, -ain | 1.25x | Mode-independent (NOT Mode B markers) |

### BARE token enrichment

| Mode | BARE % | Enrichment in Mode B |
|------|--------|---------------------|
| Mode A | 38.2% | — |
| Mode B | 62.0% | 0.62x (A depleted relative to B) |

### Co-occurrence

- aiin + edy co-occurrence: 330 lines — canonical "specify and iterate" instruction

### Key observations

1. **Terminal suffixes are Mode A markers**: 2.5-3.0x enrichment establishes them as specification signals
2. **Checkpoint suffixes are mode-independent**: Only 1.25x Mode A enrichment — they control looping regardless of mode
3. **Mode A = specification, Mode B = execution**: Suffix presence/absence is the primary mode discriminator
4. **BARE dominance in Mode B**: 62.0% bare tokens indicate execution without output specification

## Related constraints

- C1229: Alternating suffix modes
- C1231: Universal suffix mode centroids
- C1230: Mode MIDDLE differentiation

## Provenance

- `phases/CONTROL_LOOP_ARCHITECTURE/scripts/suffix_scope_analysis.py`
- `phases/CONTROL_LOOP_ARCHITECTURE/results/suffix_scope_analysis.json`
