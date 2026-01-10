# C452: HT Unified Prefix Vocabulary

**Tier:** 2 | **Status:** CLOSED | **Scope:** HT / GLOBAL | **Refines:** C347

---

## Statement

HT prefix vocabulary is **unified across all three systems** (A, B, AZC) with near-complete overlap (Jaccard >= 0.947). However, HT density is **discontinuous at system boundaries** (p=0.049).

HT is a **SINGLE notation layer** that varies in **DENSITY**, not **VOCABULARY**, across systems.

**Interpretation:** HT was a unified notation system applied throughout the manuscript, with context-dependent frequency modulation. The same 19 prefixes appear everywhere; only their density changes.

---

## Evidence

### Vocabulary Overlap

| Comparison | Jaccard Similarity | Overlap | Interpretation |
|------------|-------------------|---------|----------------|
| A <-> B | **1.000** | 19/19 | Complete overlap |
| A <-> AZC | 0.947 | 18/19 | Near-complete |
| B <-> AZC | 0.947 | 18/19 | Near-complete |

The single missing prefix in AZC is likely a sample size artifact (AZC has only 30 folios vs 114 for A and 83 for B).

### System Boundary Discontinuity

| Measure | Value |
|---------|-------|
| Mean boundary change | 0.061 |
| Mean within-system change | 0.052 |
| Mann-Whitney U | 3491 |
| P-value | 0.049 |
| Effect size (r) | -0.187 |
| Verdict | DISCONTINUOUS |

HT density changes **more** at system boundaries than within systems, though the effect is modest.

### Prefix Usage by System

| System | Top 3 Prefixes (rate) | Total HT Tokens |
|--------|----------------------|-----------------|
| Currier A | yk (0.116), do (0.113), yt (0.102) | 6,078 |
| Currier B | sa (0.109), al (0.105), yk (0.090) | 10,509 |
| AZC | yk (0.182), al (0.181), yt (0.135) | 1,494 |

**Same vocabulary, different distribution.** Prefix usage patterns vary by system, but the prefix set is shared.

---

## What This Constraint Claims

- All 19 HT prefixes appear in all three systems
- Vocabulary overlap is near-complete (Jaccard >= 0.947)
- Density shifts occur at system boundaries
- HT is ONE notation system, not three parallel ones

---

## What This Constraint Does NOT Claim

- HT prefixes have system-specific meanings
- The boundary discontinuity is causal (may be epiphenomenal)
- Prefix distribution differences are semantically significant
- Complete type-level overlap (only prefix-level tested)

---

## Relationship to Other Constraints

| Constraint | Relationship |
|------------|--------------|
| **C347** | C452 refines: HT is morphologically distinct AND unified cross-system |
| **C451** | C452 complements: density varies, vocabulary doesn't |
| **C168** | C452 confirms at prefix level: single unified layer |

---

## System Boundaries Identified

30 system transitions across the manuscript:

| Transition | Count |
|------------|-------|
| A -> B | 12 |
| B -> A | 11 |
| B -> AZC | 3 |
| AZC -> B | 2 |
| A -> AZC | 1 |
| AZC -> A | 1 |

---

## Phase Documentation

Research conducted: 2026-01-10 (HT-THREAD analysis)

Scripts:
- `phases/exploration/ht_folio_features.py` - Per-folio feature extraction
- `phases/exploration/ht_cross_system_analysis.py` - Cross-system threading

Results:
- `results/ht_folio_features.json`
- `results/ht_cross_system_analysis.json`
- `results/ht_threading_synthesis.md`

---

## Navigation

<- [INDEX.md](INDEX.md) | ^ [../CLAUDE_INDEX.md](../CLAUDE_INDEX.md)
