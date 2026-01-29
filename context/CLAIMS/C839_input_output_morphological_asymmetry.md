# C839: RI Input-Output Morphological Asymmetry

**Tier:** 2
**Scope:** A
**Phase:** A_RECORD_B_ROUTING_TOPOLOGY

## Constraint

RI tokens show asymmetric morphological diversity by positional function: INITIAL-only (input) tokens have many distinct morphological markers, while FINAL-only (output) tokens show fewer distinctive markers.

## Evidence

From t19_input_output_morphology.py:

**INPUT-biased markers (12+ identified):**

| Type | Markers | Strength |
|------|---------|----------|
| PREFIX | po-, ko-, to-, sh-, do-, pch-, tch- | 3-inf x |
| SUFFIX | -ain, -r, -ey, -eey, -ar, -al, -hy, -or | 2-7x |
| MID_START | f-, p-, l-, e-, d- | 2-inf x |

**OUTPUT-biased markers (5 identified):**

| Type | Markers | Strength |
|------|---------|----------|
| PREFIX | so-, yk- | 0.33-0.50x |
| SUFFIX | -ry, -g, -eol | 0.20-0.50x |
| MID_END | -a, -e | 0.50-0.57x |

**Asymmetry ratio:** ~12 input markers vs ~5 output markers (2.4x asymmetry)

## Key Markers

**Strongest INPUT markers:**
- Gallows prefixes: ko- (9x), to- (inf), po- (inf)
- Suffixes: -r (7x), -ey (4.5x), -ain (inf)

**Strongest OUTPUT marker:**
- Suffix: -ry (0.20x = 5x OUTPUT bias)

## Interpretation

The asymmetry suggests:

1. **Many inputs → fewer outputs** (convergent processing)
2. **Raw materials are diverse, products are standardized**
3. **INPUT vocabulary is exploratory, OUTPUT vocabulary is terminal**

This connects to C512.a (Positional Asymmetry): START-class dominated by RI elaborations (16.1% PP), END-class dominated by PP atoms (71.4%). The INPUT/OUTPUT morphological asymmetry may be the RI-level manifestation of this same START-heavy pattern.

## Provenance

- t19_input_output_morphology.json: input_markers, output_markers
- Related: C512.a (positional asymmetry), C832 (INITIAL/FINAL separation)

## Status

CONFIRMED - Asymmetry is structural. Interpretation is Tier 3.
