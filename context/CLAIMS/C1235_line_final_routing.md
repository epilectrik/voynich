# C1235 - Line-Final Routing Architecture

**Tier:** 2 | **Scope:** B | **Phase:** CONTROL_LOOP_ARCHITECTURE (Phase 441)

## Statement

Line-final tokens constitute routing decisions, not processing steps. Active kernel atoms (k, e) are depleted 0.52-0.63x at line-final. Decision atom m is enriched 29.77x. Routing prefixes dominate: ar 9.57x, al 6.21x, or 5.38x, da 2.43x. Energy prefixes depleted: sh 0.37x, qo 0.57x. Classification: 34.9% batch-close (terminal suffix or m-atom), 14.6% loop-check (checkpoint suffix or iteration atom), 50.5% neutral (bare routing).

## Evidence

### Kernel atom enrichment at line-final

| Atom | Line-final enrichment | Role |
|------|----------------------|------|
| m | 29.77x | Decision (strongest signal) |
| a | 1.70x | Routing |
| l | 1.54x | Routing |
| r | 1.47x | Routing |
| k | 0.63x | Processing (depleted) |
| e | 0.52x | Processing (depleted) |

### Prefix enrichment at line-final

| Prefix | Enrichment | Category |
|--------|------------|----------|
| ar | 9.57x | Routing |
| al | 6.21x | Routing |
| or | 5.38x | Routing |
| da | 2.43x | Routing |
| sh | 0.37x | Energy (depleted) |
| qo | 0.57x | Energy (depleted) |

### Line-final classification (1992 lines)

| Category | % | Definition |
|----------|---|------------|
| Batch-close | 34.9% | Terminal suffix or m-atom |
| Loop-check | 14.6% | Checkpoint suffix or iteration atom |
| Neutral | 50.5% | Bare routing |

### Top line-final words

| Category | Words |
|----------|-------|
| Batch-close | am (44), dam (28), otam (25), qokam (19) |
| Loop-check | daiin (24), aiin (14), dain (9), otain (9) |

### Key observations

1. **1992 lines** analyzed from 591 paragraphs, 82 folios
2. **Processing depleted**: k and e atoms are actively avoided at line-final
3. **Decision enriched**: m-atom enrichment (29.77x) is the strongest positional signal in the entire system
4. **Batch-close at line-final is within-paragraph** — see C1237 for paragraph termination

## Related constraints

- C1002: am 88% line-final
- C964: Boundary-constrained free-interior
- C1237: Paragraph termination by -am (distinct from within-paragraph batch-close)

## Provenance

- `phases/CONTROL_LOOP_ARCHITECTURE/scripts/decision_point_analysis.py`
- `phases/CONTROL_LOOP_ARCHITECTURE/results/decision_point_analysis.json`
