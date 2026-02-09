# C766: UN = Derived Identification Vocabulary

## Constraint

UN (unclassified) tokens represent derived vocabulary built by combinatorial compounding of base MIDDLEs, not operational grammar elements.

## Quantitative Evidence

| Metric | Classified | UN | Difference |
|--------|------------|-----|------------|
| Compound rate | 35.2% | 81.1% | +45.9pp |
| Folio-unique rate | 2.3% | 64.5% | +62.3pp |
| Mean MIDDLE length | 2.26 | 4.09 | +1.82 chars |
| Unique MIDDLEs | 88 | 1,339 | - |

## Critical Finding

- **Classified-only MIDDLEs: 0** - All 88 classified MIDDLEs also appear in UN tokens
- **UN-only MIDDLEs: 1,251** - These appear ONLY in UN tokens, never in classified grammar
- **UN-only compound rate: 84.3%** - These derived forms are overwhelmingly compound

## Structural Model

```
BASE GRAMMAR (88 MIDDLEs, 479 token types, 49 classes)
    |
    | combinatorial compounding
    v
DERIVED VOCABULARY (1,251 UN-only MIDDLEs, 4,421 token types)
    |
    | folio-specific selection
    v
IDENTIFICATION TOKENS (line-1 HT, jar labels, illustration labels)
```

## Implications

1. **UN is not noise** - It's systematically derived from operational vocabulary
2. **The 49-class grammar captures primitives** - Base MIDDLEs that seed derivation
3. **Derivation serves dual purpose** - 64.5% folio-unique rate confirms identification; 71.6% atom-body overlap confirms operational content (C935)
4. **C404-C405 reframed** - Derived forms are operationally redundant, not operationally empty (C935)

> **Revision (2026-02-06):** Original implication #4 said "Derived forms don't execute; they identify."
> C935 shows compound atoms on line 1 predict body simple MIDDLEs (71.6% vs 59.2% random).
> Compound tokens are BOTH identifying (rare combinations) AND operational (same atoms as body).
> The "don't execute" framing was incorrect. Correct framing: operationally redundant with body.

## Reconciliation

| Constraint | Relationship |
|------------|--------------|
| C166, C610 | HT/UN population = derived vocabulary population |
| C404-C405 | Operationally redundant because body encodes same atoms in simple form |
| C511 | Derivational productivity (12.67x) = this compounding mechanism |
| C618 | 95.7% PP-atom-containing = compound structure |
| C747-C750 | Line-1 HT enrichment = compound specification layer placement |
| C935 | Compound header atoms predict body content (1.21x lift) |

## Tier

**Tier 2** - Empirically validated structural relationship

## Source

- Phase: COMPOUND_MIDDLE_ARCHITECTURE
- Test: T4 (t4_classified_compound.py)
- Data: class_token_map.json (479 classified types), B corpus (23,096 tokens)
