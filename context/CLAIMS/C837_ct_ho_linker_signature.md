# C837: ct-ho Linker Morphological Signature

**Tier:** 2 (pattern), 3 (interpretation)
**Scope:** A
**Phase:** A_RECORD_B_ROUTING_TOPOLOGY

## Constraint

RI tokens that appear in both INITIAL and FINAL positions (linkers) have a distinct morphological signature: 75% ct-prefix and 75% h-initial MIDDLE, creating a 12-15x enrichment for the ct-ho combination compared to pure input/output categories.

## Evidence

From t20_linker_morphology.py:

**The 4 Linkers:**

| Token | PREFIX | MIDDLE | SUFFIX |
|-------|--------|--------|--------|
| cthody | ct | ho | dy |
| ctho | ct | ho | (none) |
| ctheody | ct | heo | dy |
| qokoiiin | qo | koi | iin |

**Feature Distribution:**

| Feature | PURE INPUT | LINKER | PURE OUTPUT | Enrichment |
|---------|------------|--------|-------------|------------|
| ct- prefix | 5.0% | **75%** | 6.0% | **12-15x** |
| MIDDLE starts 'h' | 5.0% | **75%** | 6.0% | **12-15x** |
| -dy suffix | 12.1% | **50%** | 9.5% | ~4x |

Key observation: Linkers are NOT a gradient between input and output. They have a UNIQUE signature that distinguishes them from both categories.

## Interpretation (Tier 3)

The **ct-ho combination** appears to mark "transferable outputs" - materials that can serve as inputs to other processes:

- **ct-** prefix: A-enriched (C282), 85.9% Section H (C273), "anchor" role (C467)
- **-ho-/-heo-** MIDDLE: Present in 100% of ct-linkers (3/4)
- **ct-ho together**: Morphological marker for "this output is reusable"

This extends C528 (RI PREFIX bifurcation) by showing that within the PREFIX-REQUIRED RI population, the ct-ho subset has special positional bridging function.

## The qokoiiin Exception

One linker (qokoiiin = qo-koi-iin) does NOT follow the ct-ho pattern:
- qo- prefix: Kernel-adjacent, different control-flow semantics (C467)
- May represent a different linkage mechanism
- See C838 for analysis

## ct-ho is Necessary But Not Sufficient (2026-01-30)

From linker_destination_followup.py:

| ct-ho token category | Count |
|---------------------|-------|
| Total unique ct-ho tokens in Currier A | 42 |
| ct-ho tokens that ARE linkers | 3 (cthody, ctho, ctheody) |
| ct-ho tokens that are NOT linkers | 39 |

**Linker rate within ct-ho population: 7.1%**

The ct-ho morphological pattern is **necessary** (3/4 linkers have it) but **not sufficient** (only 7.1% of ct-ho tokens function as linkers). Additional structural properties beyond morphology determine linker function.

## Extension to PP Level

CURRIER_A_STRUCTURE_V2 phase confirmed that ct-ho operates at BOTH RI and PP levels:

| Level | Tokens | Function |
|-------|--------|----------|
| RI (this constraint) | ctho, cthody, ctheody | Mark transferable materials |
| PP (C889) | cthy, cthol, cthor | Process instructions for transfers |

In Section H, MIDDLEs h/hy/ho are 98-100% ct-prefixed, creating a reserved vocabulary for linking/transfer operations at the PP level.

## Provenance

- t20_linker_morphology.json: ct_prefix_rates, linker_morphology
- Related: C282 (ct A-enrichment), C467 (PREFIX control-flow), C528 (RI PREFIX bifurcation), C835 (linker mechanism), C889 (ct-ho PP extension)

## Status

CONFIRMED (pattern) / SPECULATIVE (interpretation)
