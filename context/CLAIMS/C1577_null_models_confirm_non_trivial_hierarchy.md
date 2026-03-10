# C1577: Four permutation null models confirm non-trivial hierarchical structure

**Tier:** 2
**Phase:** 562 (SECTION_TEMPLATE_TRACE_EXECUTOR)
**Scope:** B, null, permutation, hierarchy, token, domain, terminal, routing, C1563

## Claim

Four permutation null models confirm the hierarchical trace executor captures non-trivial structure that cannot be reproduced by shuffled data:

- **N1 (token-shuffle within folio):** z=14.07 — destroying local structure collapses trace quality
- **N3 (line-shuffle within section):** z=9.27 — destroying folio line packet identity degrades E4
- **N4 (within-domain form shuffle):** z=8.77 — compositional token structure (terminals, modifiers) carries information beyond domain inventory
- **N5 (terminal shuffle within-line):** z=14.18 — C1563 routing grammar is real and structurally productive

N4 is the critical separation: preserving domain sequence while destroying within-domain token composition sharply degrades non-domain axes (hazard + routing + closure), proving the hierarchy captures real compositional structure, not merely domain allocation.

## Evidence

- N1: 100 permutations, real=-3.2832, null_mean=-3.3259, null_std=0.003
- N3: 50 permutations, real=-3.2832, null_mean=-3.2897, null_std=0.0007
- N4: 100 permutations, real_nd=-1.7170, null_mean=-1.7562, null_std=0.0045
- N5: 50 permutations, real_domain=-1.5663, null_mean=-1.5808, null_std=0.001

## Provenance

- T5: `phases/SECTION_TEMPLATE_TRACE_EXECUTOR/scripts/t5_trace_validation.py`
- Builds on: C1563 (terminal routing grammar)
