# C828: PP Repetition Exclusivity

**Status:** VALIDATED | **Tier:** 2 | **Phase:** A_RECORD_B_ROUTING_TOPOLOGY | **Scope:** A

## Finding

Within-line token repetition in Currier A is **100% PP, 0% RI** (p=2.64e-07). RI tokens never repeat within a line. This reflects the functional bifurcation between PP (operational parameters) and RI (identity anchors).

## Key Numbers

| Metric | Value |
|--------|-------|
| Total within-line repeats | 357 |
| PP repeats | 357 (100.0%) |
| RI repeats | 0 (0.0%) |
| Chi-squared | 26.5 |
| p-value | 2.64e-07 |
| Non-repeat PP rate | 92.8% |

## Interpretation

The contrast is architecturally necessary:

**PP tokens (may repeat):**
- Carry operational parameters (C504, C506)
- PP count determines class survival breadth (r=0.715)
- Repetition encodes intensity/cycle count
- More repetitions = stronger parametric signal

**RI tokens (never repeat):**
- Function as identity anchors (C526)
- Encode binary presence: substance is specified or not
- Repetition adds no information ("lavender lavender" = "lavender")
- One occurrence sufficient for identity

This confirms the two-track vocabulary model (C498): PP and RI serve fundamentally different functions, and repetition behavior reflects this bifurcation.

## Relationship to C502

Under the C502 vocabulary-allowance model, repetition does not change which MIDDLEs are legal - the same set is allowed whether a token appears once or four times. Therefore, repetition must encode **downstream execution parameters**, not filtering criteria.

## Provenance

- Script: `phases/A_RECORD_B_ROUTING_TOPOLOGY/scripts/t9_repeat_function.py`
- Confirms: C498 (two-track vocabulary), C526 (RI lexical layer)
- Related: C506 (PP count gradient), C504 (PP capacity function)
