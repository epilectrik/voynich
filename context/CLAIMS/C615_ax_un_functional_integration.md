# C615: AX-UN Functional Integration

**Tier:** 2 | **Status:** CLOSED | **Scope:** CURRIER_B | **Source:** AX_BEHAVIORAL_UNPACKING

## Statement

2,246 AX-predicted UN tokens (PREFIX majority=AX) route identically to classified AX in all three subgroups (all p>0.1). 89.3% of classified AX MIDDLEs are shared, but AX-UN introduces 339 novel MIDDLEs (312 truly novel, never seen in any classified role). If absorbed, AX grows from 16.7% to 26.4% of B with preserved subgroup proportions and minimal routing shift (max delta 3.2%).

## Evidence

### Routing Comparison (Section 2)

| Subgroup | Chi-squared | p-value | Cramer's V | Verdict |
|----------|-------------|---------|-------------|---------|
| AX_INIT | 3.56 | 0.614 | 0.046 | SIMILAR |
| AX_MED | 8.76 | 0.119 | 0.056 | SIMILAR |
| AX_FINAL | 8.11 | 0.150 | 0.098 | SIMILAR |

No significant routing difference between classified AX and AX-predicted UN tokens in any subgroup.

### Subgroup Classification (Section 1)

| Method | AX_INIT | AX_MED | AX_FINAL |
|--------|---------|--------|----------|
| PREFIX-based | 26.9% | 48.8% | 24.3% |
| Position-based | 43.7% | 21.8% | 34.6% |
| Classified (ref) | 31.0% | 53.4% | 15.6% |

PREFIX-based classification reproduces the MED-dominant pattern of classified AX. Position-based classification disagrees (35% agreement), confirming that positional thirds are a poor proxy for structural subgroups.

### MIDDLE Overlap (Section 3)

| Metric | Value |
|--------|-------|
| Classified AX unique MIDDLEs | 56 |
| AX-UN unique MIDDLEs | 389 |
| Shared | 50 (89.3% of classified, 12.9% of AX-UN) |
| Jaccard similarity | 0.127 |
| Shared token coverage | 64.8% |
| Truly novel (no classified occurrence) | 312 |
| Novel appearing in EN | 24 |
| Novel appearing in FL | 3 |

AX-UN tokens use mostly known AX MIDDLEs (64.8% by volume) but introduce substantial novel vocabulary. Most novel MIDDLEs have no classified occurrence in any role — they are the morphological extended tail.

### Combined Profile (Section 4)

| Category | Classified | AX-UN | Combined |
|----------|-----------|-------|----------|
| AX_INIT | 1,195 (31.0%) | 604 (26.9%) | 1,799 (29.5%) |
| AX_MED | 2,056 (53.4%) | 1,096 (48.8%) | 3,152 (51.7%) |
| AX_FINAL | 601 (15.6%) | 546 (24.3%) | 1,147 (18.8%) |
| **Total** | **3,852 (16.7%)** | **2,246** | **6,098 (26.4%)** |

Absorption increases AX_FINAL proportion (15.6% to 18.8%) and decreases AX_MED (53.4% to 51.7%), but MED remains dominant.

## Extends

- **C613**: Confirms continuous AX-UN boundary. Adds subgroup-level analysis and MIDDLE overlap characterization.

## Related

C570, C611, C612, C613, C614

## Method

PREFIX majority role prediction for AX-UN identification. Chi-squared for routing comparison. Jaccard similarity for MIDDLE overlap. PREFIX-based subgroup classification (not positional).
