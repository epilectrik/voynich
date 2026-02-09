# C885: A-B Vocabulary Correspondence

**Tier:** 2
**Scope:** A-B
**Phase:** A_B_CORRESPONDENCE_SYSTEMATIC

## Constraint

A folios provide 81.2% vocabulary coverage for B paragraphs (1.71x vs random). Single A paragraphs provide 58.3% coverage (2.04x vs random). Aggregating 2-3 A paragraphs achieves 76-80% coverage. The A-B relationship is meaningful but requires folio-level or multi-paragraph aggregation; single A paragraphs are insufficient for B program execution.

## Evidence

Definitive test across all unit combinations:

| A Unit | B Unit | Best-Match Coverage | Random | Lift |
|--------|--------|---------------------|--------|------|
| Paragraph | Paragraph (>=10 PP) | 58.3% | 28.5% | **2.04x** |
| Paragraph | Folio | 36.9% | 20.1% | 1.83x |
| Folio | Folio | 59.8% | 37.5% | 1.60x |
| **Folio** | **Paragraph** | **81.2%** | 47.4% | 1.71x |

**Multi-paragraph aggregation:**

| A Paragraphs | B Paragraph Coverage |
|--------------|---------------------|
| 2 | 76.5% |
| 3 | 80.4% |
| 5 | 84.7% |

**Sample sizes:**
- 306 A paragraphs
- 114 A folios
- 481 large B paragraphs (>=10 PP MIDDLEs)
- 82 B folios

## What Works vs What Doesn't

### Works (Real Signal)

| Approach | Result | Meaning |
|----------|--------|---------|
| A folio -> B paragraph | 81.2% coverage, 1.71x lift | A folios provide B vocabulary |
| A para -> B para (best-match) | 58.3%, 2.04x lift | Structure exists at para level |
| Multi-para aggregation | 80%+ with 3 paragraphs | Aggregation works |

### Doesn't Work (Artifacts or Null)

| Approach | Result | Meaning |
|----------|--------|---------|
| Lane balance matching | 0.99x lift | Artifact of best-match algorithm |
| Kernel matching | 1.17x lift | Marginal, not useful |
| Hazard exposure | 99.7% match | Too universal to discriminate |
| Linker bundles | 0.99x lift | No better than random aggregation |

## Interpretation

A folios are "material contexts" that define available vocabulary. B paragraphs are "mini-programs" that execute with that vocabulary. The operator selects an A context (folio) appropriate for their material. B programs execute using the vocabulary available in that context.

```
A FOLIO (multiple paragraphs)
|-- Paragraph 1: ~20 PP MIDDLEs
|-- Paragraph 2: ~20 PP MIDDLEs
|-- ...
+-- Combined: 60-100 PP MIDDLEs
         |
         v
    81% coverage of B paragraph vocabulary
         |
         v
B PARAGRAPH (mini-program)
|-- 15-30 PP MIDDLEs
+-- Executes with available vocabulary
```

## Implications

1. **A and B are related** - 2x lift over random is meaningful
2. **Aggregation is required** - Single A paragraph insufficient (~58%)
3. **A folio is natural unit** - 81% coverage matches B paragraph needs
4. **No 1:1 mapping** - Multiple A contexts can work with same B program
5. **Operator judgment needed** - System doesn't auto-select; operator chooses

## Relationship to Existing Constraints

| Constraint | Relationship |
|------------|--------------|
| C384 | CONFIRMS - No entry-level A-B coupling, but folio-level works |
| C693 | EXTENDS - Material activation operates at folio level |
| C846 | EXTENDS - Pool-based model, but folio is the operational pool unit |
| C840 | CONFIRMS - B paragraphs are mini-programs with ~81% vocabulary from A folio |
| C827 | CONFIRMS - Paragraph as operational unit for aggregation |

## Provenance

- Script: `phases/A_B_CORRESPONDENCE_SYSTEMATIC/scripts/99_definitive_test.py`
- Data: `phases/A_B_CORRESPONDENCE_SYSTEMATIC/results/definitive_test.json`
- Depends: C384, C693, C846, C840, C827

## Status

CONFIRMED - Definitive test establishes folio-level as operational unit for A-B correspondence.
