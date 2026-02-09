# C904: -ry Suffix S-Zone Enrichment

## Statement

In AZC diagrams, tokens with -ry suffix show 3.18x enrichment in S-zones (48.7% vs 15.3% baseline).

## Evidence

| Metric | Value |
|--------|-------|
| -ry tokens in S-zones | 19/39 (48.7%) |
| Baseline S-zone rate | 505/3299 (15.3%) |
| Enrichment ratio | **3.18x** |

### Position Distribution

| Position | -ry count | Percentage |
|----------|-----------|------------|
| S-zones (S, S0, S1, S2, S3) | 19 | 48.7% |
| R-zones | 9 | 23.1% |
| C (center) | 4 | 10.3% |
| Other | 7 | 17.9% |

### Token Classification

- PP: 28 (71.8%)
- INFRA: 9 (23.1%)
- UNKNOWN: 2 (5.1%)

## Cross-Validation

This finding connects two independent analyses:

1. **C839 (Input-Output Morphological Asymmetry):** Identified -ry as the strongest OUTPUT marker with 0.20x ratio (5x OUTPUT bias) based on input/output positional analysis in Currier B.

2. **C435/C443 (S-Zone Semantics):** S-zones have zero escape permission (locked, must accept outcome). They represent commitment/boundary positions.

The spatial concentration of OUTPUT markers at commitment positions is structurally coherent: -ry marks output-appropriate vocabulary, and S-zones are where outputs are finalized.

## Interpretation

S-zones in AZC diagrams function as **output capture positions** where processing results are recorded. The -ry suffix marks tokens that belong at these commitment points.

## Scope

- **System:** AZC
- **Tier:** 2 (statistical finding with structural coherence)

## Provenance

- AZC folio notes audit (2026-02-02)
- Cross-referenced with C839 output marker analysis

## Related Constraints

- C839: -ry as OUTPUT marker
- C435: S/R positional division
- C443: Positional escape gradient (S = 0%)
