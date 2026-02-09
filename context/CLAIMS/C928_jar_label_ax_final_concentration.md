# C928: Jar Label AX_FINAL Concentration

## Status
- **Tier**: 2 (Structural)
- **Scope**: A, B, Labels
- **Status**: CLOSED
- **Source**: Phase LABEL_INVESTIGATION

## Statement

Jar label PP bases appear in Currier B at 2.1x enrichment in AX_FINAL positions (35.1% vs 16.7% baseline). Chi-square = 30.15, p = 4.0e-08. This concentration suggests jar labels identify materials that B deploys at maximum scaffold depth (boundary/completion positions per C565).

## Evidence

### Sample
- Jar labels: 16 (from PHARMA_LABEL_DECODING)
- Unique jar PP bases: 13
- B tokens containing jar PP bases: analyzed for role distribution

### Role Distribution

| Role | Jar PP Bases | Global B Baseline | Enrichment |
|------|--------------|-------------------|------------|
| **AX_FINAL** | **35.1%** | 16.7% | **2.10x** |
| AX_MED | 3.8% | 12.7% | 0.30x |
| EN | 38.6% | 42.8% | 0.90x |
| OTHER | 22.5% | 27.8% | 0.81x |

### Statistical Test

| Metric | Value |
|--------|-------|
| Chi-square | 30.15 |
| p-value | 4.0e-08 |
| Highly significant | YES |

### Comparison to Content Labels

| Label Type | AX_FINAL Rate | Enrichment vs Baseline |
|------------|---------------|------------------------|
| **Jar** | 35.1% | **2.10x** |
| Content (root/leaf) | 19.1% | 1.14x |
| B Baseline | 16.7% | 1.00x |

Jar labels show dramatically higher AX_FINAL concentration than content labels.

## Interpretation

### Per C565 (AX_FINAL Position)
AX_FINAL represents maximum scaffold depth - the boundary/completion position in the auxiliary structure. Per C571, PREFIX selects role while MIDDLE carries material identity.

### Jar vs Content Function
- **Jar labels**: Container/configuration identifiers. Their PP bases appear in B as terminal material specifications (AX_FINAL = "the thing being processed").
- **Content labels**: Material identifiers (roots, leaves). Show moderate AX enrichment (1.14x) but not concentrated in AX_FINAL.

### Pipeline Implication
```
JAR LABEL (e.g., "okaradag")
    |
    v
PP BASE (e.g., "ara")
    |
    v
B TOKEN in AX_FINAL position (bare scaffold, material specification)
    = "what to process"
```

The jar-to-AX_FINAL pipeline suggests jar labels identify materials that B procedures operate ON, deployed at the maximum scaffold position where material identity is specified without operational modification.

## Contrast with Overall Label Enrichment

The aggregate label PP base AX enrichment (1.03x, p=0.046, V=0.009) is NOT significant by project standards. The signal comes specifically from:
1. **Jar labels** (not content labels)
2. **AX_FINAL** specifically (not AX_MED or total AX)

This specificity strengthens the finding - it's not a diffuse effect but a targeted concentration.

## Related Constraints

| Constraint | Relationship |
|------------|--------------|
| C565 | AX_FINAL positional semantics (boundary/completion) |
| C570 | AX PREFIX derivability (bare = AX_FINAL) |
| C571 | PREFIX selects role, MIDDLE carries material |
| C523 | Pharma jar label vocabulary bifurcation |
| C524 | Jar morphological compression |
| C914 | RI label enrichment |

## Falsification Criteria

Disproven if:
1. Larger jar label sample shows AX_FINAL rate <25%
2. Section-specific control eliminates the effect
3. AX_FINAL concentration explained by confound (folio, position, etc.)

## Provenance

```
phases/LABEL_INVESTIGATION/scripts/label_b_role_stats.py
phases/LABEL_INVESTIGATION/results/label_b_role_stats.json
phases/LABEL_INVESTIGATION/results/label_b_pipeline.json
```
