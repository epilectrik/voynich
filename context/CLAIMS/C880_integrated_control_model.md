# C880 - Integrated Control Model

**Tier:** 3 | **Scope:** B | **Phase:** B_CONTROL_FLOW_SEMANTICS

## Statement

Currier B encodes a batch processing control system with forward-biased state progression, kernel-based transitions (e-setup, h-align, k-activate), and exception handling via FQ escape routes.

## Model

```
LINK (check) -> EN (k/h/e ops) -> FL (stage) -> FQ (if hazard)
                    ^                              |
                    +------------------------------+
                         (recovery to processing)

Control injection: CC (daiin=init, ol=continue) -> EN
Kernel pattern: e-setup -> h-align -> k-activate
```

## Component Semantics

| Role | Function | Key Feature |
|------|----------|-------------|
| EN | State transition | 91.9% kernel, 38.5% self-loop |
| FL | Material state index | 5 stages, kernel-free |
| FQ | Escape handler | 80.4% hazard triggered |
| CC | Control markers | daiin=init, ol=continue |
| AX | Support/monitoring | Includes LINK checkpoints |

## Confidence

- HIGH: Role distribution, transition grammar, FL stages
- MEDIUM: Kernel semantics, escape triggers, LINK function
- LOW: Process domain labels, specific interpretations

## Provenance

- `phases/B_CONTROL_FLOW_SEMANTICS/scripts/08_integrated_model.py`
- `phases/B_CONTROL_FLOW_SEMANTICS/results/integrated_semantic_model.json`
- Builds on: C467, C552, C770-C815, C788-C791, C804-C809, C855-C862
