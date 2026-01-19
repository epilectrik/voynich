# BRUNSCHWIG_REVERSE_ACTIVATION Phase

## Purpose

Reverse-map ALL 197 Brunschwig recipes through AZC/Currier A to extract finer-grained statistics and complete the originally intended mapping task.

## Background

Previous phases (BRUNSCHWIG_FULL_MAPPING, SENSORY_LOAD_ENCODING) established:
- 86.8% grammar compliance for Brunschwig procedures
- 4 semantic anchors found
- Inverse SLI-HT correlation (r=-0.453, p<0.0001)
- Constraint pressure substitutes for vigilance signaling

However, we never actually reverse-mapped specific recipes through AZC zones to test sensory encoding at recipe level.

## Critical Constraint: C384

**NO ENTRY-LEVEL A-B COUPLING** - Cannot map Recipe X to Entry Y directly.

Valid path:
```
Recipe -> REGIME -> Zone Compatibility -> MIDDLE Vocabulary -> Statistical A Profile
```

## Scripts

| Script | Purpose |
|--------|---------|
| `reverse_activate_all.py` | Process all 197 recipes through the pipeline |
| `sensory_granularity_test.py` | Test sensory encoding at recipe level |

## Outputs

- `results/brunschwig_reverse_activation.json` - Full results for all 197 recipes
- `REVERSE_ACTIVATION_REPORT.md` - Findings and analysis

## Data Sources

| File | Purpose |
|------|---------|
| `data/brunschwig_materials_master.json` | 197 recipes with procedures |
| `results/middle_zone_legality.json` | MIDDLE zone counts |
| `results/middle_zone_survival.json` | Zone survival clusters |
| `results/middle_incompatibility.json` | 95% illegal MIDDLE pairs |
| `results/unified_folio_profiles.json` | 83 B folio metrics |
| `results/azc_escape_by_position.json` | Position escape rates |

## Methodology

### Zone Affinity Computation

For each recipe, compute affinity to zones (C/P/R/S) based on:
- Intervention rate (high -> P-affinity)
- SLI (high -> R-affinity for sequential processing)
- Product type (PRECISION -> S-affinity, OIL_RESIN -> R-affinity)
- REGIME assignment

### Vocabulary Fingerprint

Filter legal MIDDLEs by zone compatibility, then compute:
- n_legal: count of legal MIDDLEs
- hub_ratio: proportion of hub MIDDLEs (high connectivity)
- tail_pressure: proportion of rare MIDDLEs (C477 link)

### Folio Distribution Prediction

Score each B folio by:
- REGIME match
- SLI similarity
- Zone alignment
- Return top-10 predicted folios (aggregate, respects C384)

## Tests

1. **SLI -> Tail Pressure -> HT Pathway** - Does recipe SLI predict vocabulary tail pressure, which predicts HT?
2. **Modality Signatures** - Do SOUND/SIGHT/SMELL recipes differ on zone profiles?
3. **SLI Cluster Analysis** - Do SLI clusters differ on zone affinity?
4. **Zone vs REGIME Prediction** - Is zone affinity more discriminative than REGIME alone?

## Constraints Respected

- C384: Aggregate folio prediction, no entry-level mapping
- C469: Categorical zone assignment
- C475: MIDDLE incompatibility in vocabulary filtering
- C443: Escape rates guide zone affinity

---

*Phase created: 2026-01-19*
