# C872: HT Discrimination Vocabulary Interpretation

**Tier:** 3 (Speculative)
**Scope:** Currier-B
**Phase:** HT_TOKEN_INVESTIGATION

## Statement

HT tokens function as **folio-specific discrimination vocabulary**—they distinguish one folio's procedure from another at Line 1 without encoding what the material IS. The operator supplies material identity; HT supplies discriminative markers that identify WHICH procedure is active.

## Evidence Summary

| Finding | Source |
|---------|--------|
| 30.5% of B is HT | C740 |
| Line-1 has 47% HT (vs 27%) | C747, C851 |
| 86% of L1 HT is folio-unique | C870 |
| HT mixes with PP (89% mixed lines) | C871 |
| HT avoids CC/FQ zones | C871 |
| HT enriched with FL | C871 |
| Line-1 HT not just gallows opener | HT_TOKEN_INVESTIGATION |

## Model

```
Line 1 = HEADER
  [Gallows: Type] [HT: ID] [HT: Variant] [AX_INIT: Setup]
       |              |           |            |
    Procedure     "Which?"    "Which?"     Scaffold
      marker       folio      variant     initialize

Later Lines = BODY
  [EN: Energy] [CC: Control] [FQ: Ops] [FL: Flow]
       |            |            |          |
    Modulate      Bound       Execute     Direct
```

**HT is the "human" layer**: Names, identifiers, folio-specific markers
**PP is the "program" layer**: Shared instruction grammar

## Semantic Ceiling Compliance

This interpretation respects C120 (PURE_OPERATIONAL):
- HT tokens **discriminate** procedures (operational function)
- They do NOT **denote** materials (semantic content)
- The discrimination is structural, not semantic

## Tier Justification

Tier 3 because:
1. Structural findings (C870, C871) are Tier 2
2. "Discrimination vocabulary" interpretation requires functional inference
3. Alternative interpretations possible (e.g., scribal variation, copying errors)
4. Cannot verify discriminative function without external reference

## Related Constraints

| Constraint | Relationship |
|------------|--------------|
| C120 | RESPECTS semantic ceiling |
| C740 | DEPENDS ON HT = UN identity |
| C747-C749 | BUILDS ON line-1 enrichment |
| C766 | ALIGNS WITH UN derived vocabulary |
| C792 | ALIGNS WITH B-exclusive = HT |
| C794-C795 | ALIGNS WITH A-context prediction |

## Provenance

- Phase: HT_TOKEN_INVESTIGATION
- Script: 04_ht_synthesis.py
- Validated by: expert-advisor
