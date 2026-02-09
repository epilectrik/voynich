# C911: PREFIX-MIDDLE Compatibility Constraints

**Tier:** 2 | **Scope:** B | **Status:** CLOSED

---

## Statement

PREFIX and MIDDLE are **not independent**. Each PREFIX class selects for specific MIDDLE families, with 102 forbidden combinations where expected count ≥5 but observed = 0. This establishes **morphological compatibility constraints** that operate at the token level, more restrictive than paragraph-level co-occurrence.

---

## Evidence

### PREFIX Class → MIDDLE Family Selection

| PREFIX Class | Selects For | Enrichment | Forbidden From |
|--------------|-------------|------------|----------------|
| **qo-** | k-family (k, ke, t, kch) | 4.6-5.5x | e-family, infra |
| **ch-/sh-** | e-family (edy, ey, eey) | 2.0-3.1x | k-family, infra |
| **da-/sa-** | infrastructure (iin, in, r, l) | 5.9-12.8x | Everything else |
| **ot-/ol-** | h-family (ch, sh) | 3.3-6.8x | k-family |
| **ok-** | e-family + infra (e, aiin, ar) | 2.6-3.3x | k-family |

### Forbidden Combinations (sample)

| PREFIX | MIDDLE | Expected | Observed |
|--------|--------|----------|----------|
| qo | ey | 135.5 | 0 |
| da | edy | 82.7 | 0 |
| ok | k | 133.0 | 0 |
| ot | k | 130.5 | 0 |
| da | e | 39.6 | 0 |
| (none) | edy | 295.0 | 0 |

Total forbidden combinations: 102

### PREFIX Selectivity

All major prefixes show HIGHLY SELECTIVE behavior (chi-square p < 0.001):

| PREFIX | Chi-square | n |
|--------|------------|---|
| qo | 11,003 | 4,069 |
| da | 6,935 | 1,083 |
| (none) | 4,929 | 3,864 |
| ch | 3,033 | 3,492 |
| sh | 2,400 | 2,329 |

---

## Interpretation

### Functional Mapping

| PREFIX | Handling Mode | Compatible Operations |
|--------|--------------|----------------------|
| qo- | Energy handling | Heating, thermal operations |
| ch-/sh- | Stability handling | Settling, equilibration |
| da-/sa- | Infrastructure | Connectors, markers |
| ot-/ol- | Monitoring | Phase checking |

### Specific Findings

1. **da- is pure infrastructure**: Only combines with iin, in, r, l. This explains why `dam` (da + m) is a specific infrastructure token enriched 7.24x in precision folios.

2. **qo- is pure energy**: Only combines with k-family. Cannot take e-family suffixes.

3. **ch-/sh- are stability**: Take e-family MIDDLEs (edy, ey), NOT k-family.

4. **Paragraph-level freedom, token-level constraint**: MIDDLEs co-occur freely within paragraphs (phi > 0.15 for 585 pairs), but individual tokens are constrained.

---

## Provenance

- **Phase:** MIDDLE_SEMANTIC_DEEPENING (2026-02-04)
- **Method:** PREFIX × MIDDLE enrichment matrix, chi-square selectivity tests
- **Sample:** 23,096 tokens, 27 common prefixes, 53 common MIDDLEs

---

## Related Constraints

- C908-C910 (MIDDLE Semantic Mapping)
- C267 (Compositional Morphology)
- C510-C513 (Sub-Component Grammar)
- F-BRU-012 (PREFIX × MIDDLE modification system)
