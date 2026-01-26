# C550: Role Transition Grammar

**Tier:** 2 | **Status:** CLOSED | **Scope:** B

---

## Statement

> Instruction class roles exhibit non-random transition probabilities. Self-transitions are enriched for all semantic roles (FREQUENT 2.38x, FLOW 2.11x, ENERGY 1.35x), while FLOW and FREQUENT show bidirectional affinity (1.54-1.73x). ENERGY operators avoid transitioning to other roles (0.71-0.80x depletion to FLOW, FREQUENT, UNCLASSIFIED).

---

## Evidence

**Test:** `phases/CLASS_SEMANTIC_VALIDATION/scripts/role_transition_matrix.py`

### Self-Transition Enrichment

| Role | Observed Self-Rate | Expected | Enrichment | Chi2 | p-value |
|------|-------------------|----------|------------|------|---------|
| FREQUENT | 13.4% | 5.6% | **2.38x** | 115.3 | <0.0001 |
| FLOW | 9.9% | 4.7% | **2.11x** | 51.6 | <0.0001 |
| ENERGY | 33.6% | 24.8% | **1.35x** | 167.8 | <0.0001 |
| CORE_CONTROL | 5.5% | 4.4% | 1.24x | - | - |

### Cross-Role Affinities

| Transition | Observed | Expected | Enrichment | Chi2 | p-value |
|------------|----------|----------|------------|------|---------|
| FLOW -> FREQUENT | 87 | 50.2 | **1.73x** | 26.9 | <0.0001 |
| FREQUENT -> FLOW | 77 | 50.1 | **1.54x** | 14.4 | 0.0001 |

### ENERGY Avoidance Pattern

| Transition | Observed | Expected | Depletion | Chi2 | p-value |
|------------|----------|----------|-----------|------|---------|
| ENERGY -> FREQUENT | 218 | 306.0 | **0.71x** | 25.3 | <0.0001 |
| ENERGY -> FLOW | 190 | 253.6 | **0.75x** | 15.9 | 0.0001 |
| ENERGY -> UNCLASSIFIED | 1320 | 1656.5 | **0.80x** | 68.4 | <0.0001 |

### REGIME_1 ENERGY Chaining

| REGIME | EN->EN Rate | vs Baseline |
|--------|-------------|-------------|
| REGIME_1 | 40.4% | 1.20x |
| REGIME_2 | 27.8% | 0.83x |
| REGIME_3 | 29.2% | 0.87x |
| REGIME_4 | 28.5% | 0.85x |

---

## Interpretation

### Phrasal Role Structure

Roles exhibit **phrasal behavior** - they cluster into multi-token sequences rather than mixing randomly. The hierarchy (FREQ > FLOW > ENERGY) suggests:

- **FREQUENT operators** (Class 9, 20, 21, 23): Form extended sequences, possibly representing repeated operations
- **FLOW operators** (Class 7, 30, 38, 40): Chain together for extended flow control
- **ENERGY operators** (Class 8, 31-34, 36): Self-chain when thermally active

### FLOW-FREQUENT Symbiosis

The bidirectional enrichment suggests FLOW and FREQUENT roles are **complementary but distinct**. They appear together in sequences but maintain role identity.

### ENERGY Transition Preference Asymmetry

ENERGY operators show transition preference asymmetry, avoiding transitions to other semantic roles (0.71-0.80x depletion, not prohibition). When ENERGY is active, it:
- Preferentially chains to itself (qo-chains, ch-chains)
- Shows reduced interleaving with non-ENERGY roles within chains
- Suggests thermal operations tend to cluster, though mixing is permitted

### REGIME_1 Signature

REGIME_1 shows elevated EN->EN chaining (1.20x). Combined with C547 (qo-chain enrichment), this confirms REGIME_1 as a high-thermal-activity regime.

---

## Cross-References

| Constraint | Relationship |
|------------|--------------|
| C366 | Consistent - LINK transition patterns align with role affinities |
| C386 | Consistent - transition suppression beyond forbidden 17 |
| C547 | Extended - qo-chain REGIME_1 enrichment at transition level |
| C549 | Refined - interleaving occurs between families, not within families |
| C544 | Quantified - ENERGY interleaving is inter-family, not intra-role |
| C543 | Supported - roles have positional grammar, now shown at transition level |

---

## Provenance

- **Phase:** CLASS_SEMANTIC_VALIDATION
- **Date:** 2026-01-25
- **Script:** role_transition_matrix.py

---

## Navigation

<- [C549_interleaving_significance.md](C549_interleaving_significance.md) | [INDEX.md](INDEX.md) ->
