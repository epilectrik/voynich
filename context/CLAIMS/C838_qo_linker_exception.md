# C838: qo-Prefix Linker Exception

**Tier:** 2
**Scope:** A
**Phase:** A_RECORD_B_ROUTING_TOPOLOGY

## Constraint

The qo-prefix RI linker (qokoiiin) does not follow the ct-ho pattern that characterizes the other 3 linkers, suggesting multiple linker mechanisms or distinct functional roles for qo-mediated vs ct-mediated positional bridging.

## Evidence

From t20_linker_morphology.py:

**Linker Comparison:**

| Token | PREFIX | MIDDLE | SUFFIX | Pattern |
|-------|--------|--------|--------|---------|
| cthody | ct | ho | dy | ct-ho |
| ctho | ct | ho | (none) | ct-ho |
| ctheody | ct | heo | dy | ct-ho |
| **qokoiiin** | **qo** | **koi** | **iin** | **DIFFERENT** |

**PREFIX Semantics (from C467):**

| PREFIX | Role | B-enrichment |
|--------|------|--------------|
| ct | Anchor | 0.14x (A-enriched) |
| qo | Kernel-adjacent | 1.51x (B-enriched) |

The qo-prefix carries completely different control-flow semantics than ct-:
- ct = registry-internal, Section H dominated
- qo = execution-facing, kernel-adjacent

## Interpretation

If both ct-ho and qo-koi tokens function as positional linkers, they may serve different pipeline roles:

| Type | PREFIX | Pattern | Hypothesized Role |
|------|--------|---------|-------------------|
| ct-linkers | ct | ct-ho/heo | Registry-internal bridging |
| qo-linker | qo | qo-koi | Execution-facing bridging |

This may relate to the AND/OR ambiguity in C835:
- ct-linkers: Aggregation (AND) - combining registry specifications
- qo-linker: Alternative (OR) - routing to execution paths

## Provenance

- t20_linker_morphology.json: linker_morphology
- Related: C467 (PREFIX control-flow), C837 (ct-ho signature), C835 (linker mechanism)

## Status

CONFIRMED - The exception is structural. Interpretation of functional difference is Tier 3.
