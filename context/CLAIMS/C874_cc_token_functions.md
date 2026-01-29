# C874 - CC Token Functions

**Tier:** 3 | **Scope:** B | **Phase:** B_CONTROL_FLOW_SEMANTICS

## Statement

Core Control tokens have distinct positional functions: 'daiin' (mean position 0.370, 27.1% line-initial) serves as initialization marker, 'ol' (mean position 0.461, distributed) serves as continuation marker.

## Evidence

- daiin: 314 occurrences, position 0.370, 27.1% line-initial
- ol: 421 occurrences, position 0.461, 5.0% line-initial
- Both kernel-free (0% kernel rate)
- Direct transitions rare (daiin->ol: 6, ol->daiin: 5)

## Interpretation

- daiin = "begin/start/initialize" (sets up processing context)
- ol = "proceed/continue/next" (signals ongoing processing)
- Pure control words without kernel operations

## Provenance

- `phases/B_CONTROL_FLOW_SEMANTICS/scripts/02_cc_token_semantics.py`
- `phases/B_CONTROL_FLOW_SEMANTICS/results/cc_token_semantics.json`
- Related: C788 (CC singleton identity)
