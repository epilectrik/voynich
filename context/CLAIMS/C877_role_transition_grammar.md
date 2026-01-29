# C877 - Role Transition Grammar

**Tier:** 2 | **Scope:** B | **Phase:** B_CONTROL_FLOW_SEMANTICS

## Statement

Role transitions follow a formal grammar with high-probability paths: EN->EN (38.5%), CC->EN (37.7%), AX->EN (32.6%), FQ->EN (29.5%). Escape route FL->FQ (16.0%) with recovery FQ->EN (29.5%).

## Evidence

Transition matrix (>15%):
- EN->EN: 38.5% (processing continues)
- CC->EN: 37.7% (control triggers processing)
- UN->UN: 33.8%
- AX->EN: 32.6% (monitoring triggers processing)
- FQ->EN: 29.5% (escape recovers)
- FL->FQ: 16.0% (state triggers escape)

Rare transitions (<5%):
- *->CC: 2.8-3.5% (control rarely receives)
- *->FL: 3.7-4.8% (state rarely receives directly)

## Interpretation

Processing (EN) is the hub - most transitions either continue processing or return to it. Escape (FQ) provides recovery pathway back to processing.

## Provenance

- `phases/B_CONTROL_FLOW_SEMANTICS/scripts/05_state_transition_grammar.py`
- `phases/B_CONTROL_FLOW_SEMANTICS/results/state_transition_grammar.json`
