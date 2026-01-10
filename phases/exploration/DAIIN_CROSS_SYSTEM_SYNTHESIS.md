# daiin Cross-System Analysis - Synthesis

**Date:** 2026-01-09
**Status:** COMPLETE
**Constraint outcome:** NONE (descriptive finding, confirms C383)

---

## Research Question

> Is daiin a **universal articulator** that adapts its structural role by system context?

**Known patterns before analysis:**
- In A: DA = internal articulation punctuation (C422)
- In B: daiin = line-initial boundary marker (3-11x enriched)
- In AZC: Unknown

---

## Findings

### 1. Position Distribution

| System | DA Rate | Initial | Internal | Final |
|--------|---------|---------|----------|-------|
| A | 9.72% | 0.64x | 0.90x | **1.72x** |
| B | 4.74% | **1.63x** | 0.82x | **1.60x** |
| AZC | 6.32% | 0.64x | 1.01x | 0.96x |

**Pattern:**
- A: DA enriched at **FINAL** positions (entry boundaries)
- B: DA enriched at **INITIAL+FINAL** positions (line boundaries)
- AZC: DA shows **NO positional enrichment** (neutral)

### 2. AZC Placement Correlation

DA in AZC is **PLACEMENT-coded**, not POSITION-coded:

| Placement | Enrichment | Interpretation |
|-----------|------------|----------------|
| B (central) | **4.32x** | DA marks central positions |
| R (radial) | **1.99x** | DA marks radial positions |
| S-series | 0.07-0.46x | DA **avoids** edge positions |

### 3. Form Distribution

| Form | A | B | AZC |
|------|---|---|-----|
| daiin* | **49.3%** | 32.4% | 19.9% |
| dal* | 11.8% | 22.0% | **28.3%** |
| dar* | 11.9% | 23.2% | 23.6% |

- A is **daiin-dominant**
- B is diverse
- AZC is **most diverse**, daiin is minority

---

## Conclusion

### Refined Universal Articulator Hypothesis

DA adapts its structural role by system context:

| System | DA Role | Mechanism |
|--------|---------|-----------|
| A | Entry articulator | Sequential boundary (final-enriched) |
| B | Line articulator | Sequential boundary (initial/final-enriched) |
| AZC | Diagram articulator | **Spatial position** (central-enriched) |

> **daiin is a universal articulator, but in AZC it expresses SPATIAL structure rather than SEQUENTIAL structure.**

This is a **refinement**, not an exception. DA remains an articulator in all three systems, but its articulation target differs:
- A/B: Sequential boundaries (entry/line)
- AZC: Spatial positions (diagram center)

---

## Constraint Status

| Status | Rationale |
|--------|-----------|
| **NO NEW CONSTRAINT** | Finding is descriptive |
| **C383 CONFIRMED** | Type system is unified |
| **C422 CONFIRMED** | DA articulation in A |

The finding documents how DA's universal articulation function adapts to system context. This is an **interpretation**, not a structural rule.

---

## Files Created

| File | Purpose |
|------|---------|
| `phases/exploration/daiin_cross_system.py` | Analysis script |
| `phases/exploration/DAIIN_CROSS_SYSTEM_SYNTHESIS.md` | This document |
| `context/ARCHITECTURE/cross_system_synthesis.md` | Integration document |

---

## Summary Table

```
System    DA Role              Enrichment Pattern       Form Dominant
------    -------              ------------------       -------------
A         Entry articulator    Final (1.72x)           daiin (49%)
B         Line articulator     Initial+Final (1.6x)    diverse
AZC       Diagram articulator  Central placement       dal/dar (52%)
```

**Research thread: CLOSED**
