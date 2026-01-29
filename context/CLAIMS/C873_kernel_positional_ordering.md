# C873 - Kernel Positional Ordering

**Tier:** 3 | **Scope:** B | **Phase:** B_CONTROL_FLOW_SEMANTICS

## Statement

Kernel characters show positional ordering: e (0.404) < h (0.410) < k (0.443). This represents a safety interlock pattern: verify stability before applying energy.

## Evidence

- 'e' mean position: 0.404 (earliest)
- 'h' mean position: 0.410 (middle)
- 'k' mean position: 0.443 (latest)
- Most common combination: "he" (31.4% of kernel tokens)

## Interpretation

The ordering encodes a safe process control sequence:

1. **e first** - "Is the current state stable?" - verify before proceeding
2. **h middle** - "Is alignment correct?" - phase/prepare
3. **k last** - "Apply energy" - only after checks pass

This is analogous to: "Don't apply heat until you've observed your preparation is stable."

The "he" combination (31.4%) represents the verification pair - stability check + alignment - that precedes action. The grammar prevents "heating blind."

Supporting evidence:
- C814 (kernel-escape inverse, rho=-0.528): proper kernel sequence = less escape needed
- C875 (escape triggers): hazard FL without proper verification triggers escape
- High kernel rate in stable processing (EN 91.9% kernel)

## Provenance

- `phases/B_CONTROL_FLOW_SEMANTICS/scripts/01_kernel_semantics.py`
- `phases/B_CONTROL_FLOW_SEMANTICS/results/kernel_semantics.json`
