# C935: Compound Header Tokens Are Dual-Purpose (Specification + Identification)

**Tier:** 2
**Scope:** B
**Phase:** PARAGRAPH_EXECUTION_SEQUENCE

## Constraint

Line-1 compound MIDDLEs decompose into core atoms that appear as simple MIDDLEs in paragraph body lines. Hit rate: 71.6% vs 59.2% random baseline (1.21x lift, +12.4pp). This means "HT/unclassified" tokens are not a separate non-operational layer but compound operational specifications that ALSO serve as identification markers due to their rarity.

## Evidence

**Compound atom -> body prediction:**

| Metric | Value |
|--------|-------|
| Paragraphs tested | 83 (with line-1 compounds) |
| Average line-1 compound atoms | 6.7 |
| Average body simple MIDDLEs | 43.5 |
| **Prediction hit rate** | **71.6%** |
| Random baseline | 59.2% |
| Lift | 1.21x |

71.6% of atoms extracted from line-1 compound MIDDLEs appear as simple (core) MIDDLEs somewhere in the paragraph body. This is significantly above the 59.2% rate expected if line-1 compounds were unrelated to body content.

**HT vs grammar compound rates:**

| Population | Compound Rate | Avg MIDDLE Length |
|------------|---------------|-------------------|
| Grammar (479 types) | 31.5% | 2.04 chars |
| HT/UN (~4400 types) | 45.8% | 2.64 chars |
| Ratio | 1.46x | — |

100% of compounds in BOTH populations decompose fully into core atoms.

**Folio cross-prediction:**

Line-1 similarity does NOT predict body similarity across folios (r=0.051). This is expected: compound tokens identify *this specific program*, not a category. Two different specifications can invoke similar generic control loops.

## Interpretation

Compound tokens on line 1 serve a dual purpose:

```
"opcheodai" decomposes to: op + ch + e + od + ai
                             |    |   |   |    |
                             |    |   |   |    +-- precision [ai]
                             |    |   |   +------- discharge [od]
                             |    |   +----------- cool [e]
                             |    +--------------- adjust [ch]
                             +-------------------- [op prefix]

OPERATIONAL:  Specifies "adjust, cool, discharge with precision"
IDENTIFYING:  This exact combination is rare/unique -> identifies which program
```

Like a technical part number (SS-316L-SCH40-2IN) that encodes both composition and identity.

## Why C404 Still Holds (Statistically)

Removing compound tokens doesn't change program outcomes because:
- Body lines already encode the same operations in simple form
- The header is a compressed specification; the body unpacks it
- Redundancy, not emptiness, explains terminal independence (p=0.92)

## Revision Impact

| Constraint | Change |
|------------|--------|
| C404 | "Non-operational" -> "Operationally redundant" |
| C766 | "Don't execute; they identify" -> "Dual-purpose: specify AND identify" |
| HT Tier 3 (attention/practice) | WEAKENED — compound specification is simpler explanation |

## Relationship to Existing Constraints

| Constraint | Relationship |
|------------|--------------|
| C404 | REVISES interpretation (evidence unchanged) |
| C766 | EXTENDS — adds body-prediction evidence to compound structure |
| C840 | DEEPENS — header isn't just "HT identification," it's compound specification |
| C842 | REFINES — step function is spec->exec transition, not operational->non-operational |
| C932 | VALIDATES — body vocabulary gradient is the "unpacking" of header compounds |
| C747 | REFRAMES — line-1 HT enrichment = compound specification concentration |

## Provenance

- Script: `scratchpad/ht_decomposition_test.py`
- Script: `scratchpad/line1_body_prediction.py`
- Phase: PARAGRAPH_EXECUTION_SEQUENCE

## Status

CONFIRMED - Prediction hit rate significantly above random (71.6% vs 59.2%).
