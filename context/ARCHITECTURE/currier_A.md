# Currier A: Non-Sequential Categorical Registry

**Status:** CLOSED | **Tier:** 2 | **Scope:** 30.5% of tokens, 114 folios

---

## Overview

Currier A is **DISJOINT** from B in grammar but **UNIFIED** in type system. It functions as a non-sequential categorical registry—like a parts catalog compared to B's assembly instructions.

| Metric | Value |
|--------|-------|
| Token coverage | 30.5% (~37,000 tokens) |
| Folios | 114 |
| TTR | 0.137 (low = high repetition) |
| Tokens/line (median) | 22 |
| LINK density | 3.0% |
| Bigram reuse | 70.7% |

---

## Key Properties (Tier 2)

| Property | Evidence | Constraint |
|----------|----------|------------|
| LINE_ATOMIC | Median 3 tokens/line, MI=0 across lines | C233 |
| POSITION_FREE | Zero JS divergence between positions | C234 |
| CATEGORICAL TAGGING | 8+ mutually exclusive marker prefixes | C235 |
| FLAT (not hierarchical) | Zero vocabulary overlap between markers | C236 |
| DATABASE_LIKE | TTR=0.137, 70.7% bigram reuse | C237 |
| DESIGNED SEPARATION | 25/112,733 cross-transitions (0.0%) | C239 |
| SHARED TYPE SYSTEM | Same kernel dichotomy as B | C383 |

---

## 8 Marker Prefix Families

| Prefix | Function | Section Preference |
|--------|----------|-------------------|
| **ch** | Primary classifier | Balanced |
| **sh** | Sister to ch (equivalence class) | Section-conditioned |
| **ok** | Primary classifier | Balanced |
| **ot** | Sister to ok (equivalence class) | Section-conditioned |
| **da** | Infrastructure (record articulation) | Universal |
| **qo** | Bridging family | Moderate |
| **ol** | Bridging family | B-enriched |
| **ct** | Section H specialist (85.9%) | H-concentrated |

### Sister Pair Architecture (C407-410)

- **ch/sh**: Equivalence class (J=0.23), mutually exclusive, section-conditioned
- **ok/ot**: Equivalence class (J=0.24), mutually exclusive, section-conditioned
- Sister pairs AVOID direct sequence (0.6x suppression)
- Sister pairs SHARE predecessor contexts (336 shared)
- Choice is section-conditioned (quire level, not folio level)

---

## Compositional Morphology (Tier 2)

Marker tokens are **compositional, not atomic**:

```
marker_token = [ARTICULATOR] + PREFIX + [MIDDLE] + SUFFIX
```

| Component | Count | Role | Required? |
|-----------|-------|------|-----------|
| ARTICULATOR | ~9 forms | Optional refinement (yk-, yt-, kch-) | No |
| PREFIX | 8 | Primary classifier family | Yes |
| MIDDLE | 42 common | Modifier subcode | No |
| SUFFIX | 7 universal | Terminal variant code | Yes |

### Key Findings

- **897 observed combinations** of PREFIX × MIDDLE × SUFFIX (C268)
- **7 universal suffixes** across 6+ prefixes (C269)
- **28 middles are PREFIX-EXCLUSIVE** (C276)
- **Suffix is universal**, Middle is type-specific (C277-278)

This explains:
- Low TTR (0.137) — component reuse
- High bigram reuse (70.7%) — predictable combinations
- Learnability — small codebook, compositional rules

---

## Multiplicity Encoding (Tier 2)

64.1% of entries exhibit **repeating block structure**: `[BLOCK] × N`

| Metric | Value | Constraint |
|--------|-------|------------|
| Entries with repetition | 64.1% (1013/1580) | C250 |
| Average repetition | 2.79x | C252 |
| Distribution | 2x: 416, 3x: 424, 4x: 148, 5x: 20, 6x: 5 | C252 |
| Block uniqueness | 100% (no cross-entry reuse) | C253 |
| Section isolation | 100% (no cross-section reuse) | C255 |

### This is LITERAL ENUMERATION

- **NOT:** `ITEM = 5` (abstract quantity with arithmetic)
- **BUT:** `ITEM, ITEM, ITEM, ITEM, ITEM` (discrete instances)
- No cross-entry arithmetic
- No reference frame for comparison
- 3x dominance (55%) reflects human counting bias (C258)

---

## Optional Articulator Layer (Tier 2)

~20% of Currier A tokens have **extended articulator forms** (yk-, yt-, kch-, ks-, ko-, yd-, ysh-, ych-).

| Test | Result |
|------|--------|
| Section exclusivity | PASS — MORE concentrated than core prefixes |
| Mutual exclusivity | FAIL — Co-occur with core prefixes (24.6%) |
| Identity necessity | FAIL — 100% removable without identity loss |
| Identity contribution | ZERO unique distinctions (C292) |

**Conclusion:** Articulators are an **optional refinement layer**—systematic but not discriminative.

---

## Structural Primitives

Two tokens serve as structural infrastructure across both A and B:

| Token | B Role | A Role | Enrichment |
|-------|--------|--------|------------|
| **daiin** | CORE_CONTROL (execution boundary) | Record articulation | A-enriched 1.55x |
| **ol** | CORE_CONTROL (pairs with daiin) | Marginal presence | B-enriched 0.21x |

- `daiin` = "portable articulator" (adapts to ANY context)
- `ol` = "execution anchor" (functional only in sequential grammar)

---

## Folio Organization (Tier 2)

| Property | Finding | Constraint |
|----------|---------|------------|
| Thematic coherence | NONE (within=between, p=0.997) | C345 |
| Sequential coherence | YES (adjacent 1.31x more similar) | C346 |

Folios are **physical containers**, not organizational units. Local clustering exists without folio-level structure.

---

## Section Distribution

| Section | % of A | Characteristics |
|---------|--------|-----------------|
| H | ~45% | Dense, mixed-marker, highest articulator use |
| P | ~25% | Balanced, moderate articulator |
| T | ~15% | Uniform, sparse, highest mean repetition |
| Other | ~15% | Various |

Sections have **distinct configurations** (C295):
- H = dense mixed entries
- P = balanced exclusive/mixed
- T = uniform sparse with high repetition

---

## A vs B: Key Differences

| Aspect | Currier A | Currier B |
|--------|-----------|-----------|
| Structure | Non-sequential | Sequential |
| Function | Registry/catalog | Executable programs |
| Grammar | No sequential grammar | 49-class grammar |
| LINK density | 3.0% | 6.6% (38% overall) |
| TTR | 0.137 | 0.096 |
| Folio sharing | 114 folios | 83 folios |
| **Overlap** | **0 shared folios** | **0 shared folios** |

---

## Key Constraints

| # | Constraint |
|---|------------|
| 229 | A is DISJOINT |
| 233 | A = LINE_ATOMIC |
| 234 | A = POSITION_FREE |
| 240 | A = NON_SEQUENTIAL_CATEGORICAL_REGISTRY |
| 250 | 64.1% show repeating blocks |
| 267 | Tokens are COMPOSITIONAL |
| 383 | GLOBAL TYPE SYSTEM across A/B/AZC |

---

## Behavioral Classification (Tier 3)

The 8 PREFIX families map to **operational domains** based on B-grammar evidence:

| Domain | Prefixes | % of Classified | Structural Basis |
|--------|----------|-----------------|------------------|
| ENERGY_OPERATOR | ch, sh, qo | 59.4% | Dominates energy/escape roles in B |
| CORE_CONTROL | da, ol | 19.1% | Structural anchors |
| FREQUENT_OPERATOR | ok, ot | 15.1% | FREQUENT role in canonical grammar |
| REGISTRY_REFERENCE | ct | 6.4% | 0% B terminals; 7x A-enriched |

**Key finding:** Discrimination gradient—ENERGY domain has 8.7x more unique MIDDLEs than REGISTRY domain (564 vs 65).

See [CURRIER_A_BRIEFING.md](CURRIER_A_BRIEFING.md) for consolidated summary.
See [../SPECULATIVE/a_behavioral_classification.md](../SPECULATIVE/a_behavioral_classification.md) for detailed Tier-3 analysis.

---

## Navigation

← [currier_B.md](currier_B.md) | [currier_AZC.md](currier_AZC.md) →
