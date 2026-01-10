# C451: HT System Stratification

**Tier:** 2 | **Status:** CLOSED | **Scope:** HT / GLOBAL | **Extends:** C341

---

## Statement

HT density is **system-conditioned**: Currier A (0.170) > AZC (0.162) > Currier B (0.149), with A vs B significantly different (Mann-Whitney p=0.0043 after Bonferroni correction).

This formalizes the previously qualitative observation in C341 that HT varies by program type, now establishing it as a **cross-system architectural property**.

**Interpretation:** HT density reflects functional differences between systems. Currier A's higher HT density is consistent with A containing more "waiting-heavy" registry operations.

---

## Evidence

### System-Level Comparison

| System | Mean HT Density | Std | N Folios |
|--------|-----------------|-----|----------|
| Currier A | 0.170 | 0.049 | 114 |
| AZC | 0.162 | 0.064 | 30 |
| Currier B | 0.149 | 0.055 | 83 |

### Statistical Tests

| Test | Statistic | P-value |
|------|-----------|---------|
| Kruskal-Wallis (3-way) | H = 7.79 | 0.020 |
| Mann-Whitney A vs B | U = varies | **0.0043** (significant) |
| Mann-Whitney A vs AZC | U = varies | 0.489 (not significant) |
| Mann-Whitney B vs AZC | U = varies | 0.372 (not significant) |

Bonferroni-corrected threshold: alpha = 0.0167 (0.05 / 3)

**Only A vs B is significant after correction.**

### Consistency with C341

C341 established HT-program stratification within Currier B:

| Waiting Profile | HT Density |
|-----------------|------------|
| EXTREME | 15.9% |
| HIGH | 10.4% |
| MODERATE | 8.5% |
| LOW | 5.7% |

C451 extends this to show the **same pattern holds across systems**: A (more registry/waiting operations) has higher HT than B (more execution operations).

---

## What This Constraint Claims

- HT density differs significantly between A and B
- A > AZC > B ordering is consistent with functional interpretation
- This is a **system-level property**, not folio-level noise
- C341's within-B finding generalizes cross-system

---

## What This Constraint Does NOT Claim

- A and B have different HT vocabularies (they don't - see C452)
- AZC is significantly different from A or B (it isn't)
- Causal direction (A causes HT vs HT reflects A function)
- Specific semantic content of HT tokens

---

## Relationship to Other Constraints

| Constraint | Relationship |
|------------|--------------|
| **C341** | C451 extends: within-B stratification now shown cross-system |
| **C450** | C451 is additive: system and quire effects are both present |
| **C452** | C451 complements: density varies, vocabulary doesn't |

---

## Phase Documentation

Research conducted: 2026-01-10 (HT-THREAD analysis)

Scripts:
- `phases/exploration/ht_folio_features.py` - Per-folio feature extraction
- `phases/exploration/ht_distribution_analysis.py` - System comparison

Results:
- `results/ht_folio_features.json`
- `results/ht_distribution_analysis.json`
- `results/ht_threading_synthesis.md`

---

## Navigation

<- [INDEX.md](INDEX.md) | ^ [../CLAUDE_INDEX.md](../CLAUDE_INDEX.md)
