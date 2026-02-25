# C1264: Bridge vs Dark Pipeline Category Divergence

**Tier:** 2
**Scope:** A->B
**Phase:** A_CATEGORY_SCATTERSHOT (Phase 452)
**Date:** 2026-02-24

## Statement

Bridge MIDDLEs (85, C1139) and dark pipeline MIDDLEs (300, C1140) have significantly different operational category profiles. Chi-squared=73.0, permutation p=0.001, Cramer's V=0.441. Bridges are TRANSITION-enriched (20% vs 2%); dark pipeline is MARKING-dominated (36% vs 11%). The divergence survives length control (short-bin p=0.0002, medium-bin p=0.001).

## Architecture

- **Pipeline channel is category-structured.** The route a MIDDLE takes from A into B (bridge vs dark pipeline) is predicted by its operational category.
- **Bridges carry state-change vocabulary.** TRANSITION (20%), FLOW (18%), STAGING (13%) dominate bridges -- the vocabulary of phase changes, material movement, and process sequencing.
- **Dark pipeline carries annotation vocabulary.** MARKING (36%), FLOW (20%), THERMAL (19%) dominate dark pipeline -- the vocabulary of bookkeeping, annotation, and thermal state.
- **Not a length confound.** Short MIDDLEs (1-2 chars) show the divergence (p=0.0002), as do medium MIDDLEs (3-4 chars, p=0.001).

## Key Findings

| Metric | Value |
|--------|-------|
| Bridge MIDDLEs with category | 84/85 |
| Dark MIDDLEs with category | 292/300 |
| Chi-squared | 73.0 |
| Cramer's V | 0.441 |
| Permutation p | 0.001 |

### Category Distribution

| Category | Bridge | Dark Pipeline |
|----------|--------|---------------|
| CONTAINMENT | 8% | 1% |
| FLOW | 18% | 20% |
| MARKING | 11% | 36% |
| MONITORING | 7% | 2% |
| OPERATION | 11% | 11% |
| STAGING | 13% | 10% |
| THERMAL | 12% | 19% |
| TRANSITION | 20% | 2% |

### Length Control

| Bin | n_bridge | n_dark | chi2 | p |
|-----|----------|--------|------|---|
| Short (1-2) | 53 | 58 | 28.3 | 0.0002 |
| Medium (3-4) | 31 | 197 | 23.9 | 0.001 |
| Long (5+) | 0 | 37 | (skip) | - |

## Provenance

- Builds on C1139 (three-channel A-B pipeline), C1141 (dark pipeline bridge atom substrate), C1254
- Extends C1250 (8 operational categories) into pipeline channel analysis
