# C870: Line-1 HT Folio Specificity

**Tier:** 2
**Scope:** Currier-B
**Phase:** HT_TOKEN_INVESTIGATION

## Statement

Line-1 HT tokens are highly folio-specific: 85.9% of unique Line-1 HT vocabulary appears in only ONE folio. 1,229 tokens (67% of Line-1 HT vocabulary) are BOTH folio-unique AND Line-1 exclusive.

## Evidence

| Metric | Value |
|--------|-------|
| Line-1 HT vocabulary | 1,834 unique types |
| Folio-singletons | 1,576 (85.9%) |
| 2-folio spread | 181 (9.9%) |
| 5+ folio spread | 13 (0.7%) |
| Folio-unique AND Line-1 only | 1,229 |

### Folio Spread Distribution

| Folios | Token count | % |
|--------|-------------|---|
| 1 | 1,576 | 85.9% |
| 2 | 181 | 9.9% |
| 3 | 46 | 2.5% |
| 4 | 18 | 1.0% |
| 5+ | 13 | 0.7% |

## Interpretation

Line-1 HT tokens form a **folio-specific discrimination vocabulary**. They identify which procedure is active without encoding what the material IS (semantic ceiling per C120). Each folio has a largely unique set of Line-1 HT tokens that distinguish it from other folios.

This is consistent with:
- C766: UN = derived identification vocabulary
- C792: B-exclusive = HT identity
- C747: Line-1 HT enrichment

## Implications

1. Line-1 is a "header" that discriminates this folio's procedure from others
2. HT tokens serve as folio identifiers, not operational instructions
3. The grammar (PP) is shared; the identification (HT) is folio-specific

## Provenance

- Phase: HT_TOKEN_INVESTIGATION
- Script: 02_line1_ht_identity.py
- Data: line1_ht_identity.json
