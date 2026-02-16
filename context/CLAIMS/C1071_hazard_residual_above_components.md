### C1071 — Forbidden Transitions Operate Above Component-Level Rules

- **Tier:** 2 (ESTABLISHED)
- **Scope:** B (hazard architecture)
- **Phase:** MULTI_LAYER_COMPATIBILITY_ARCHITECTURE (2026-02-15)

**Finding:** Only 4/17 C109 forbidden transitions (24%) are blocked by any of three component-level constraint layers: C475 blocks 4/17 (MIDDLE incompatibility), C911 blocks 0/17 (PREFIX x MIDDLE), C1063 blocks 0/17 (PREFIX x SUFFIX). All 13 residual forbidden transitions involve MIDDLEs that are COMPATIBLE in C475 — the forbidden-ness is purely directional and token-specific, not component-decomposable.

**Interpretation:** Quantitatively confirms C627's finding that forbidden transitions are a token-specific directional lookup table. The three morphological constraint layers (MIDDLE compatibility, PREFIX x MIDDLE, PREFIX x SUFFIX) form a component-level safety architecture that is necessary but vastly insufficient for explaining execution-level hazards. The 13/13 residual pairs being C475-compatible proves that forbidden transitions cannot be reduced to component incompatibility — they require the specific directional sequence.

**Extends:** C627 (forbidden pairs = token-specific lookup table), C109 (17 forbidden transitions), C996 (all involve HUB_UNIVERSAL MIDDLEs)

**Quantitative:**
- Total coverage: 4/17 (24%)
- C475 coverage: 4/17
- C911 coverage: 0/17
- C1063 coverage: 0/17
- Residual compatible in C475: 13/13 (100%)
- Residual types: spoke→bridge (9), bridge→spoke (4)
