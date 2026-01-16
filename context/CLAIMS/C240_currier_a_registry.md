# C240: A = NON_SEQUENTIAL_CATEGORICAL_REGISTRY

**Tier:** 2 | **Status:** CLOSED | **Phase:** CAS

---

## Claim

Currier A functions as a non-sequential categorical registry - analogous to a parts catalog rather than assembly instructions.

## Defining Properties

| Property | Evidence | Constraint |
|----------|----------|------------|
| LINE_ATOMIC | Median 3 tokens/line, MI=0 across lines | C233 |
| POSITION_FREE | Zero JS divergence between positions | C234 |
| CATEGORICAL TAGGING | 8+ mutually exclusive marker prefixes | C235 |
| FLAT (not hierarchical) | Zero vocabulary overlap between markers | C236 |
| DATABASE_LIKE | TTR=0.137, 70.7% bigram reuse | C237 |

## The 8 Marker Families

| Prefix | Function | Section Preference |
|--------|----------|-------------------|
| ch | Primary classifier | Balanced |
| sh | Sister to ch | Section-conditioned |
| ok | Primary classifier | Balanced |
| ot | Sister to ok | Section-conditioned |
| da | Infrastructure | Universal |
| qo | Bridging | Moderate |
| ol | Bridging | B-enriched |
| ct | Section H specialist | 85.9% in H |

## Analogy

| System | Analogy | Function |
|--------|---------|----------|
| Currier A | Parts catalog | Index of available components |
| Currier B | Assembly instructions | How to use components |
| AZC | Diagram labels | Position markers |

## Related Constraints

- C229 - A is DISJOINT from B grammar
- C233-239 - Defining property details
- C267 - Compositional morphology (897 combinations)

---

## Navigation

← [INDEX.md](INDEX.md) | ↑ [../CLAUDE_INDEX.md](../CLAUDE_INDEX.md)
