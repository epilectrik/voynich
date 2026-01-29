# C863: Paragraph-Ordinal EN Subfamily Gradient

**Status:** Validated
**Tier:** 3
**Phase:** FOLIO_PARAGRAPH_ARCHITECTURE
**Scope:** B

## Statement

Early paragraphs (ordinal 1-2) show qo-prefixed EN enrichment; late paragraphs (ordinal 6+) show ch/sh-prefixed EN enrichment. This supports a sequential-phase interpretation where energy input precedes stabilization.

## Evidence

```
EN tokens enriched in EARLY paragraphs:
  qo              class=41  1.70x
  qokeeo          class=49  1.54x
  qokair          class=49  1.53x
  qokeed          class=49  1.50x

EN tokens enriched in LATE paragraphs:
  sheal           class=39  2.05x
  choty           class=35  1.79x
  shcthy          class=47  1.65x
  cheky           class=34  1.50x

Ordinal concentration:
  84 tokens show >40% concentration in specific ordinals
  23.7% of token occurrences follow concentrated patterns
  Almost all concentrate in ordinal 6+ (late paragraphs)
```

## Alignment with Established Constraints

| Constraint | Relationship |
|------------|--------------|
| C397 | qo-prefix = escape route (25-47%) - early phases need escape/venting |
| C412 | ch-preference anticorrelated with qo-escape - opposing modes |
| C544 | qo/ch-sh interleave at line level - paragraph level is coarser manifestation |
| C574 | QO/CHSH grammatically equivalent but lexically partitioned |
| C645 | CHSH post-hazard dominance (75.2%) - late = stabilization |

## Interpretation

### Sequential Phase Model

```
FOLIO = Single procedure for Material X

Early paragraphs (qo-dominant):
  - Setup/venting phase
  - Energy input operations
  - Establishing circulation
  - FL scoped to this phase

Late paragraphs (ch/sh-dominant):
  - Precision/finishing phase
  - Stabilization operations
  - Controlled collection
  - FL scoped to this phase
```

### Reconciliation with Linguistic Independence

Paragraphs are **sequentially coupled** but **linguistically independent**:
- The "hand-off" is physical material state, not vocabulary
- Each phase independently assesses state and selects interventions (C171)
- FL scoping (86% termination) works because each phase has own material flow
- Low vocabulary overlap (11.8%) reflects different operations, not different materials

### Distillation Mapping

| Phase | PREFIX | Lane Function | Distillation Analog |
|-------|--------|---------------|---------------------|
| Early | qo- | ENERGY_MODULATOR | Heat, establish circulation, vent volatiles |
| Late | ch/sh- | STABILITY_ANCHOR | Precise temperature, collection, cooling |

## Provenance

- Script: `09_paragraph_character_probe.py`
- Data: `paragraph_character_probe.json`
- Expert validation: Confirmed no conflicts, strongly supports model

## Related

- C544 (EN interleaving)
- C574 (QO/CHSH partition)
- C645 (CHSH post-hazard dominance)
- C855-C862 (folio-paragraph architecture)
