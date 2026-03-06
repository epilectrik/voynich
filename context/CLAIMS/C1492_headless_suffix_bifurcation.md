# C1492: Headless Suffix Bifurcation

**Tier:** 2
**Scope:** B, MIDDLE, headless, suffix, bifurcation, binary, parametric
**Phase:** HEADLESS_COMPOUND_SUBGRAMMAR (Phase 536)
**Date:** 2026-03-06

## Statement

Headless compounds bifurcate into two suffix populations. BARE (binary ops): d-initial 14.9% suffix rate, i-initial 9.3% -- these operate as binary presence/absence signals without parametric specification. SUFFIXED (parametric ops): c-initial 96.2%, p-initial 96.8%, f-initial 93.2% -- these require suffix specification for full instruction encoding. The split maps to functional domains: d(CONTAINMENT) and i(STAGING) are self-contained binary operations; c(OPERATION), p(MARKING), f(MARKING) are parametric operations that need suffix to specify scope/mode. Aggregate headless suffix rate is 47.5% (vs headed 35.7%). Modifier ordering grammar (C1472) compliance matches headed compounds: headless 61.9% vs headed 70.1% for multi-modifier pairs.

## Evidence

- **BARE group:** d suffix=14.9%, i suffix=9.3%, s suffix=62.5% (intermediate)
- **SUFFIXED group:** c suffix=96.2%, p suffix=96.8%, f suffix=93.2%, l suffix=77.3%
- **Aggregate:** headless 47.5% vs headed 35.7% suffix rate
- **Binary interpretation:** d/i tokens with no suffix are complete instructions (seal/iterate)
- **Parametric interpretation:** c/p/f tokens need suffix to specify how the operation executes
- **C1472 ordering compliance:** headless 61.9% vs headed 70.1% (same grammar, not distinguishable)

## Cross-references

- C1440: Three-tier terminal opacity gradient (suffix gating mechanism)
- C1472: Modifier co-occurrence avoidance dominates ordering
- C1489: Headless pseudo-HEAD category differentiation (functional domain split)
- C1393: Compound MIDDLE composition grammar
- C1488: Headless compound population structure
