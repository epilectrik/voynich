# C875 - Escape Trigger Grammar

**Tier:** 3 | **Scope:** B | **Phase:** B_CONTROL_FLOW_SEMANTICS

## Statement

FQ escape is triggered primarily by hazard FL stages: 80.4% of FL-triggered escapes come from HAZARD stages (INITIAL/EARLY/MEDIAL), with MEDIAL dominating at 70.4%.

## Evidence

- Pre-FQ FL stage distribution:
  - MEDIAL: 70.4% (HAZARD)
  - TERMINAL: 12.9% (SAFE)
  - LATE: 6.7% (SAFE)
  - EARLY: 6.2% (HAZARD)
  - INITIAL: 3.9% (HAZARD)
- Hazard stages total: 80.4%
- Safe stages total: 19.6%
- Escape chains: mean 1.19 tokens (84.3% single-token)

## Interpretation

Escape is triggered when material is in unstable (hazard) state, particularly MEDIAL stage. Most escapes resolve quickly (single token).

## Provenance

- `phases/B_CONTROL_FLOW_SEMANTICS/scripts/03_escape_trigger_analysis.py`
- `phases/B_CONTROL_FLOW_SEMANTICS/results/escape_trigger_analysis.json`
- Related: C775 (hazard FL drives escape)
