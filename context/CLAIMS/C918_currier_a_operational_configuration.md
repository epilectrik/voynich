# C918: Currier A as Operational Configuration Layer

## Status
- **Tier**: 2 (STRUCTURAL)
- **Status**: CLOSED
- **Source**: Phase A_PP_EXTENSION_SEMANTICS

## Statement

Currier A functions as an **operational configuration layer** for Currier B procedures: A entries specify context-specific material variants (via RI extensions) that parameterize B's generic procedural vocabulary.

## Evidence

### RI Derivational Structure
- 90.9% of RI MIDDLEs derive from PP bases (C913)
- RI = PP + extension (single-character modifier)
- Extensions are kernel primitives (79.9%)

### Extension Operational Alignment
- Extensions correlate with specific PREFIX patterns (C917)
- h-extension → ct prefix (82%) = linker context
- k/t-extension → qo prefix (40-50%) = energy/terminal context
- d-extension → NO_PREFIX (47%) = transition context

### PP as Procedural Vocabulary
- PP MIDDLEs appear in both A and B
- In B, PP operate as generic material references in procedures
- In A, PP get extended to create context-specific variants

### Extension Distribution
- Kernel primitives NEVER get extended (0% for k,e,h,d,l,o)
- Only COMPOUND MIDDLEs get extended (30-50%)
- Operators remain fixed; materials get variants

## Model

```
CURRIER B (Procedure Library)
  - Generic procedures operating on PP MIDDLEs
  - Material slots: "apply X to material M"
  - Context-agnostic

CURRIER A (Configuration Layer)
  - Context-specific material variants (RI = PP + extension)
  - Extension encodes operational context:
    - h = monitoring/linker context
    - k = energy context
    - t = terminal context
    - d = transition context
    - o = default variant
  - PREFIX + extension = doubly-specified context

INTERACTION
  - B procedures reference generic materials (PP)
  - A provides which VARIANT to use for each context
  - Extension type matches B's operational categories
```

## Analogy

- **B** = procedure library (function definitions)
- **A** = parameter file (context-specific arguments)
- **PP** = formal parameter (material slot)
- **RI** = actual argument (specific variant)
- **Extension** = context selector

## Why This Matters

Explains the A-B relationship:
1. B is SELF-SUFFICIENT for execution (documented fact)
2. A appears DISJOINT (no direct reference)
3. Yet A uses B vocabulary systematically

RESOLUTION: A doesn't reference B instances. A CONFIGURES B procedures by specifying which material variants to use in which operational contexts.

## Related Constraints
- C229: Currier A is DISJOINT from B
- C240: A = NON_SEQUENTIAL_CATEGORICAL_REGISTRY
- C913: RI derivational morphology
- C917: Extension-prefix operational alignment
- C837: ct-ho linker signature

## Falsification Criteria

Disproven if:
1. Extensions shown to be arbitrary (no PREFIX correlation)
2. PP-RI relationship is not derivational
3. A entries found to directly reference B instances
4. Extension semantics explained by non-operational factors
