# C893: Paragraph Kernel Signature Predicts Operation Type

**Tier:** 2
**Scope:** B
**Phase:** BRUNSCHWIG_CLOSED_LOOP_DIMENSIONS

## Constraint

HIGH_K paragraphs (k>35% of kernel characters) show 2x FQ enrichment (19.7% vs 9.7%, p<0.0001) consistent with recovery/escape function. HIGH_H paragraphs show elevated EN (22.0% vs 19.3%, p=0.036) consistent with active processing. Kernel signature at paragraph level discriminates operation category.

## Evidence

Analysis of 527 B paragraphs classified by kernel signature:

| Para Type | Count | FQ Rate | EN Rate | k/token | h/token |
|-----------|-------|---------|---------|---------|---------|
| HIGH_K | 58 | **19.7%** | 19.3% | **0.45** | 0.30 |
| HIGH_H | 203 | 9.7% | **22.0%** | 0.26 | **0.58** |
| BALANCED | 235 | 12.6% | 23.9% | 0.34 | 0.41 |

**Statistical tests (HIGH_K vs HIGH_H):**

| Operation | HIGH_K | HIGH_H | p-value | Significance |
|-----------|--------|--------|---------|--------------|
| FQ (escape) | 19.7% | 9.7% | <0.0001 | *** |
| EN (energy) | 19.3% | 22.0% | 0.036 | * |
| CC (control) | 4.8% | 3.0% | 0.006 | ** |

## Interpretation

Paragraph kernel signature encodes operation type at the paragraph level:

- **HIGH_K paragraphs**: Concentrate escape/recovery operations (FQ). The k-rich vocabulary reflects ENERGY_MODULATOR interventions for crisis handling.

- **HIGH_H paragraphs**: Concentrate energy/fire operations (EN). The h-rich vocabulary reflects PHASE_MANAGER operations for active processing with monitoring.

This is NOT a compositional artifact of C780 (Role Kernel Taxonomy). C780 describes token-level properties; this constraint describes paragraph-level spatial organization - which paragraphs concentrate which operations.

## Brunschwig Alignment (Tier 3)

The operation mapping aligns with BRSC hypotheses:

| Para Type | Brunschwig Operation Category |
|-----------|------------------------------|
| HIGH_K | RECOVERY PROCEDURES - "If it overheats, remove from fire and let cool" |
| HIGH_H | ACTIVE DISTILLATION - "Distill with fire of second degree, watching drip rate" |
| BALANCED | GENERAL PROCEDURES - Standard distillation steps |

This extends BRSC's FQ→recovery mapping to paragraph-level granularity: recovery procedures concentrate in HIGH_K paragraphs rather than being uniformly distributed.

## Relationship to Existing Constraints

| Constraint | Relationship |
|------------|--------------|
| C780 | EXTENDS - C780 is token-level; this is paragraph-level aggregation |
| C781 | VALIDATES - FQ's k+e/0%h profile explains HIGH_K→FQ concentration |
| C778 | VALIDATES - EN's h-dominance explains HIGH_H→EN concentration |
| C103-105 | ALIGNS - k=ENERGY_MODULATOR, h=PHASE_MANAGER functions |

## Provenance

- Script: `scripts/brunschwig_operation_mapping.py`
- Data: `results/brunschwig_operation_mapping.json`
- Phase: BRUNSCHWIG_CLOSED_LOOP_DIMENSIONS
- Expert validation: Approved 2026-01-30

## Status

CONFIRMED - Statistically significant (p<0.0001 for main effect)
