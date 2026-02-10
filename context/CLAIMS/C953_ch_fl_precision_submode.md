# C953: ch-FL Precision Annotation Submode

**Tier:** 2 | **Scope:** B | **Phase:** FL_RESOLUTION_TEST

## Statement

ch-prefixed FL tokens show a significant suffix effect (NMI p = 0.004) that general FL does not. ch-FL stage predicts the suffix morphology of neighboring tokens at 7x the global effect size, consistent with a precision-annotation submode.

## Evidence

- ch-FL suffix NMI: 0.189 (p = 0.004)
- All-FL suffix NMI: 0.027 (p = 0.657)
- Ratio: 7.0x
- ch-FL variant NMI: 0.156 (2.8x global, but p = 0.38 due to n = 113)
- ch-FL tokens: 64, ch-FL pairs: 113
- ch-FL stage distribution: MEDI(6), LATE(24), FINL(12), TERM(22)

## Context

- ch has known precision semantics (C412: anticorrelated with qo-escape, C929: sensory modality)
- ch-FL showed borderline dampening (4/4 folios) and alternation (p = 0.069) in precursor investigation
- Section T independently shows a suffix effect (p = 0.038), suggesting monitoring-heavy contexts share this property

## Interpretation

When FL is delivered through the precision channel (ch prefix), it interacts with execution morphology. This is the sole surviving execution-level FL signal. It may represent a mode where state annotations are written with tighter tolerances and are conditionally consulted by the grammar.

## Provenance

- `phases/FL_RESOLUTION_TEST/scripts/05_ch_prefix_probe.py`
- Related: C412, C929, C949, C952
