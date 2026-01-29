# C794: Line-1 Composite Header Structure

**Tier:** 2
**Scope:** B, A<>B
**Phase:** B_LINE_POSITION_HT (extension)

## Constraint

Line-1 HT vocabulary has a two-part composite structure:

1. **PP Component (68.3%)**: Uses vocabulary from A's PP pool, carries A-folio context information
2. **B-Exclusive Component (31.7%)**: Uses vocabulary not in any A folio, serves as folio identification

## Evidence

### Partition

| Component | Occurrences | Share |
|-----------|-------------|-------|
| PP (in A) | 315 | 68.3% |
| B-exclusive | 146 | 31.7% |

### PP Component Function: A-Context Declaration

| Test | Result |
|------|--------|
| PP line-1 HT in best-match A folio | 39.6% |
| PP line-1 HT in random A folio | 20.7% |
| Lift | 1.92x |
| Wilcoxon p | < 0.0001 |

**Prediction test**: Using only PP line-1 HT MIDDLEs to predict best-match A folio:
- Correct: 13.9%
- Random baseline: 0.88%
- **Lift: 15.8x**

### B-Exclusive Component Function: Folio Identification

| Metric | Value |
|--------|-------|
| Folio-unique rate | 94.1% |
| Multi-folio MIDDLEs | 5.9% |

Most common B-exclusive line-1 HT MIDDLEs are short primitives shared across folios (ted, opsh, shed). The folio-unique 94.1% are compound forms.

### Independence

PP fraction in line-1 does NOT correlate with body PP vocabulary size (rho=0.002, p=0.99). The two components serve independent functions.

## Interpretation

**Line-1 is a composite header with dual function:**

1. **Context Declaration** (PP portion): "This program operates under the context specified by A-folio X"
   - Uses vocabulary shared with A
   - The specific PP MIDDLEs present identify which A folio context applies
   - 15.8x better than random at predicting best-match A

2. **Folio Identification** (B-exclusive portion): "This is B-folio Y"
   - Uses vocabulary unique to B
   - 94.1% folio-unique (appears in only one folio's line-1)
   - Serves as identification tag, not operational content

This explains why line-1 has 50.2% HT (C747) - it's serving a header function that requires:
- Non-operational vocabulary (HT) to avoid being executed
- PP vocabulary to declare A-context
- B-exclusive vocabulary to identify the folio

## Dependencies

- C747 (Line-1 HT enrichment)
- C749 (Line-1 HT morphological distinction)
- C792 (B-exclusive = HT identity)
- C734 (A-B coverage architecture)

## Provenance

```
phases/B_LINE_POSITION_HT/scripts/line1_mechanism.py
phases/B_LINE_POSITION_HT/scripts/line1_a_context.py
```
