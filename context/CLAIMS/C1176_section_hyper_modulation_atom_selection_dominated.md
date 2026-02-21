# C1176: Section Hyper-Modulation Is Atom-Selection-Dominated

**Tier:** 2
**Scope:** B, dark pipeline, section, atoms
**Phase:** DARK_PIPELINE_COMBINATORICS (Phase 419)
**Depends on:** C1141, C1143, C1148

## Statement

The dark pipeline's 3.9× section hyper-modulation (C1148, JS=0.483 vs 0.124 baseline) is driven by atom-level section specificity, not by combination-emergent effects. A multiplicative independence model — P(compound in section S) proportional to product of P(atom_i in S) — achieves R²=0.781 on observed vs predicted compound section profiles across 20 qualifying compounds (2+ atoms, >=5 tokens, all atoms profiled from 31 atoms with >=10 tokens). Pseudo-R² (1 - JS_pred/JS_uniform) = 0.677. Mean JS(observed, predicted) = 0.099, vs mean JS(observed, uniform) = 0.305. The atoms themselves carry section specificity, and compounds inherit it multiplicatively.

## Evidence

### Multiplicative Model Performance
| Metric | Value |
|--------|-------|
| Qualifying compounds | 20 |
| Atoms profiled (>=10 tokens) | 31 |
| Pearson R² | 0.781 |
| Pseudo-R² | 0.677 |
| Mean JS(obs, predicted) | 0.099 |
| Mean JS(obs, uniform) | 0.305 |

### Interpretation

C1143 established that dark-exclusive and shared atoms have equivalent section profiles (MW p=0.107). This seemed to suggest atoms are section-neutral. However, C1143 tested section *concentration* (Herfindahl) between two atom classes, not whether individual atoms predict compound profiles. The present test shows that while CLASSES of atoms don't differ in concentration, INDIVIDUAL atoms carry distinct section profiles that combine multiplicatively to produce compound-level section specificity.

This resolves the apparent tension between C1143 (atoms seem section-neutral) and C1148 (compounds are 3.9× section-differentiated): atom Herfindahl distributions overlap between dark-exclusive and shared classes, but individual atom section profiles still differ enough to produce compound-level concentration when multiplied together.

## Provenance

- Phase 419 Test 2: SECTION_HYPER_MODULATION
- Script: `phases/DARK_PIPELINE_COMBINATORICS/scripts/dark_pipeline_combinatorics.py`
- Results: `phases/DARK_PIPELINE_COMBINATORICS/results/dark_pipeline_combinatorics.json` -> test2_section_hyper_modulation
