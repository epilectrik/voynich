# C827: Paragraph as Operational Aggregation Unit

**Status:** VALIDATED | **Tier:** 2 | **Phase:** A_RECORD_B_ROUTING_TOPOLOGY | **Scope:** A-B

## Finding

Gallows-initial "paragraphs" in Currier A folios may be the **operational aggregation unit** for A->B filtering. Paragraphs provide 2.8x better token survival than single lines while maintaining manageable constraint complexity.

## Paragraph Definition

A "paragraph" is defined as a contiguous sequence of A lines starting with a gallows-initial line (first token begins with k, t, p, or f) and continuing until the next gallows-initial line.

**Gallows characters:** {k, t, p, f}

## Token Survival by Aggregation Level

| Unit | Count | Mean PP | Token Survival | vs Line |
|------|-------|---------|----------------|---------|
| Single Line | 1,559 | 5.8 | 11.2% | 1.0x |
| **Paragraph** | 306 | 20.2 | **31.8%** | **2.8x** |
| Full A-Folio | 114 | 38.9 | 50.0% | 4.5x |

## Why Paragraphs May Be Optimal

1. **Substantial improvement over lines:** 2.8x better token survival
2. **Reasonable vocabulary size:** ~20 PP MIDDLEs (vs ~39 for full folio)
3. **Visual structure:** Gallows-initial markers are visually prominent
4. **Operational coherence:** Enough PP to enable meaningful B program execution

## Interpretation

Single A lines (C233 LINE_ATOMIC) are structurally atomic but **operationally insufficient** (C693). Full folios provide maximum coverage but may exceed what any single operation needs.

Paragraphs represent a **middle ground**:
- Enough PP vocabulary for operational coherence
- Bounded enough to maintain specificity
- Visually marked with gallows characters for easy identification

This suggests the manuscript's visual organization (gallows-initial paragraph breaks) may correspond to operational boundaries.

## Relationship to Other Constraints

- **C233 (LINE_ATOMIC):** Lines are structural units; paragraphs are operational units
- **C693 (USABILITY_GRADIENT):** Single lines insufficient; aggregation required
- **C826 (TOKEN_FILTERING_MODEL):** Aggregation helps via union of PP allowances

## Provenance

- Script: `phases/A_RECORD_B_ROUTING_TOPOLOGY/scripts/t6_aggregation_levels.py`
- Script: `phases/A_RECORD_B_ROUTING_TOPOLOGY/scripts/t7_model_reconciliation.py`
- Depends: C502 (token filtering), C693 (usability), C233 (line atomic)
