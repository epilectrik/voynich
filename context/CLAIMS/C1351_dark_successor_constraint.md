# C1351: Dark MIDDLEs Constrain Local Grammar Continuation

**Tier:** 2
**Scope:** B
**Phase:** DARK_PIPELINE_STRUCTURE (472)

## Constraint

Dark MIDDLEs have significantly narrower successor entropy than bridge MIDDLEs (median 2.59 vs 4.18 bits, Mann-Whitney Z=-7.45, p<0.001). Each dark token channels the grammar into a restricted set of next-step instruction classes, rather than being followed by diverse operations. The 34.6% no-class successor rate (vs 27.4% for bridge) means about one-third of dark successors are also non-grammar tokens (other dark/HT tokens), further constraining the effective grammar continuation.

## Evidence

From dark_pipeline_structure.py test T2 (57 dark MIDDLEs, 76 bridge MIDDLEs with ≥5 classified successors):

| Population | Median entropy | Mean entropy | N qualified |
|------------|---------------|-------------|-------------|
| Dark MIDDLEs | **2.585** | 2.662 | 57 |
| Bridge MIDDLEs | **4.181** | 3.868 | 76 |

| Metric | Value |
|--------|-------|
| Mann-Whitney Z | -7.445 |
| Mann-Whitney p | <0.001 |
| Dark no-class successor rate | 34.6% |
| Bridge no-class successor rate | 27.4% |

**Lowest-entropy dark MIDDLEs** (most constrained successors):

| MIDDLE | Entropy | Observations | Classes |
|--------|---------|-------------|---------|
| olke | 1.37 | 5 | 3 |
| ec | 1.46 | 6 | 3 |
| eee | 1.70 | 13 | 5 |
| ofch | 1.75 | 8 | 4 |

**Highest-entropy dark MIDDLEs** (most diverse successors):

| MIDDLE | Entropy | Observations | Classes |
|--------|---------|-------------|---------|
| lk | 3.88 | 38 | 18 |
| eed | 3.85 | 58 | 20 |
| eok | 3.85 | 23 | 16 |

Even the highest-entropy dark MIDDLEs (3.85-3.88 bits) fall below the bridge median (4.18 bits).

## Interpretation

This is the opposite of the material-referent prediction. Material referents (substances acted upon by diverse procedures) would show WIDE successor entropy — the same substance gets heated, filtered, dissolved, combined, etc. Instead, dark MIDDLEs show NARROW entropy: each dark token channels the grammar into a specific continuation pattern.

This is consistent with dark MIDDLEs as **context-setting parameters** — each one constrains the local execution environment, limiting which grammar operations follow. Rather than naming what is being processed (material), they specify how the next step should be configured (context). This aligns with C918 (A parameterizes B) and C1349 (dark pipeline preserves A's category structure): the parameterization is not "use ingredient X" but "configure for context Y."

The gradient from low-entropy (olke: 3 classes) to high-entropy (eed: 20 classes) dark MIDDLEs suggests the population spans a range from highly specific context-setters to more general ones, consistent with a parameterization vocabulary rather than a naming vocabulary.

## Provenance

- dark_pipeline_structure.json: test T2
- Extends: C942 (context-dependent successor profiles — dark MIDDLEs show this more strongly than bridge)
- Extends: C1137 (dark = 100% HT/UN — they are outside grammar but constrain grammar continuation)
- Extends: C1349 (dark preserves A's category structure — the parameterization content survives into B)
- Contra: material referent interpretation (narrow entropy falsifies the prediction of diverse operations on same substance)

## Status

CONFIRMED — dark MIDDLEs have significantly narrower successor entropy than bridge (Z=-7.45, p<0.001), constraining local grammar continuation rather than receiving diverse operations.
