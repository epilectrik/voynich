# CLASS_COSURVIVAL_TEST: Findings (STRICT INTERPRETATION)

## Executive Summary

Under the **strict interpretation** (C502), class-level filtering is **meaningful, not trivial**.

| Model | Unique Patterns | Always-Survive Classes | Infrastructure Survival |
|-------|-----------------|------------------------|-------------------------|
| Union (WRONG) | 5 | 49 (100%) | 98-100% |
| **Strict (CORRECT)** | **1,203** | **6 (12%)** | **13-27%** |

The union model made class-level filtering appear trivially coarse. The strict model reveals significant class-level discrimination.

---

## Finding 1: Meaningful Class-Level Filtering

| Metric | Union (WRONG) | Strict (CORRECT) |
|--------|---------------|------------------|
| Unique class patterns | 5 | **1,203** |
| All-49-classes records | 98.4% | **0%** |
| Mean classes surviving | 49 | **32.3** |
| Range | 47-49 | **6-48** |

### Interpretation

Under strict interpretation:
- **No A record** gives full access to all 49 classes
- Average A record leaves only **32 classes** available (34% filtered)
- Minimum is **6 classes** (extreme restriction)
- Maximum is **48 classes** (never all 49)

---

## Finding 2: Unfilterable Core (6 Classes)

Only 6 classes survive in **ALL** A contexts:

| Class | Survival | Type | MIDDLEs |
|-------|----------|------|---------|
| 7 | 100% | ATOMIC | None (tokens: ar, al) |
| 11 | 100% | ATOMIC | None (token: ol) |
| 9 | 100% | CORE_CONTROL | 'a', 'o' (universal) |
| 21 | 100% | AUXILIARY | 'y', 'o', 'lo', 't', 'r', 'ra' |
| 22 | 100% | AUXILIARY | 'l', 'y', 'g', 'm', 'r' |
| 41 | 100% | AUXILIARY | 'l', 'e', 's', 'r' |

### Why These 6?

- **Classes 7, 11**: Atomic tokens (MIDDLE=None) - always pass any filter
- **Classes 9, 21, 22, 41**: MIDDLEs are universal connectors ('a', 'o', 'y', 'l', 'r', 'e') present in nearly all A records

These form the **minimum viable instruction set** - always available regardless of A context.

---

## Finding 3: Infrastructure Classes Are NOT Protected

| Infrastructure Class | Survival Rate | Status |
|---------------------|---------------|--------|
| 36 | **20.9%** | Heavily filtered |
| 42 | **25.9%** | Heavily filtered |
| 44 | **13.1%** | Most filtered |
| 46 | **27.3%** | Heavily filtered |

### Interpretation

The union model suggested infrastructure classes were ~100% available (protected).

The strict model shows they are **heavily filtered** (13-27% survival). This means:
- Infrastructure operations require specific vocabulary contexts
- Not all programs have full infrastructure access
- A-record specification determines infrastructure availability

---

## Finding 4: Class Survival Rate Spectrum

### Tier 1: Always Survive (100%)
Classes 7, 9, 11, 21, 22, 41

### Tier 2: High Survival (80-95%)
| Class | Survival | Role |
|-------|----------|------|
| 27 | 93.0% | AUXILIARY |
| 28 | 92.3% | AUXILIARY |
| 6 | 91.5% | AUXILIARY |
| 29 | 90.4% | AUXILIARY |
| 20 | 87.0% | AUXILIARY |
| 31 | 87.6% | ENERGY_OPERATOR |
| 39 | 86.3% | ENERGY_OPERATOR |
| 38 | 85.0% | FLOW_OPERATOR |
| 34 | 84.9% | ENERGY_OPERATOR |
| 14 | 84.5% | FREQUENT_OPERATOR |
| 5 | 83.5% | AUXILIARY |
| 19 | 83.1% | AUXILIARY |
| 47 | 83.1% | ENERGY_OPERATOR |
| 24 | 80.4% | AUXILIARY |
| 37 | 80.2% | ENERGY_OPERATOR |

### Tier 3: Medium Survival (50-80%)
| Class | Survival | Role |
|-------|----------|------|
| 25 | 78.7% | AUXILIARY |
| 43 | 74.6% | ENERGY_OPERATOR |
| 8 | 72.7% | ENERGY_OPERATOR |
| 16 | 72.6% | AUXILIARY |
| 23 | 70.4% | FREQUENT_OPERATOR |
| 2 | 67.0% | AUXILIARY |
| 35 | 67.4% | ENERGY_OPERATOR |
| 30 | 60.8% | FLOW_OPERATOR |
| 3 | 60.0% | AUXILIARY |
| 48 | 57.2% | ENERGY_OPERATOR |
| 26 | 54.1% | AUXILIARY |
| 13 | 52.6% | FREQUENT_OPERATOR |
| 40 | 50.8% | FLOW_OPERATOR |

### Tier 4: Low Survival (30-50%)
| Class | Survival | Role |
|-------|----------|------|
| 17 | 48.9% | AUXILIARY |
| 49 | 48.9% | ENERGY_OPERATOR |
| 4 | 45.2% | AUXILIARY |
| 45 | 40.5% | ENERGY_OPERATOR |
| 10 | 39.1% | CORE_CONTROL |
| 1 | 38.3% | AUXILIARY |
| 15 | 36.5% | AUXILIARY |
| 32 | 34.4% | ENERGY_OPERATOR |
| 33 | 34.1% | ENERGY_OPERATOR |

### Tier 5: Rare (<30%)
| Class | Survival | Role |
|-------|----------|------|
| 46 | 27.3% | INFRASTRUCTURE |
| 18 | 27.6% | AUXILIARY |
| 42 | 25.9% | INFRASTRUCTURE |
| 36 | 20.9% | INFRASTRUCTURE |
| 44 | 13.1% | INFRASTRUCTURE |
| 12 | 12.9% | CORE_CONTROL |

---

## Finding 5: Co-Survival Structure

### Equivalence Classes

Only **1 group** with 100% co-survival: the 6 always-survive classes (7, 9, 11, 21, 22, 41).

All other 43 classes are **singletons** - each has unique survival patterns relative to others.

### Interpretation

Under the strict model:
- No classes are perfectly correlated except the unfilterable core
- Each class has independent survival characteristics
- Class availability is truly discriminating

---

## Constraint Implications

| Constraint | Status | Explanation |
|------------|--------|-------------|
| **C481** | **VALIDATED** | 1,203 unique class patterns confirms discrimination |
| **C502** | **VALIDATED** | Strict interpretation produces meaningful filtering |
| **C411** | **EXTENDS** | ~34% class-level filtering (not just MIDDLE-level) |

---

## Corrected Understanding

### The Union Model Was Wrong

The union model (AZC expands vocabulary) produced trivial class-level results:
- 5 patterns, 98.4% all-49-classes
- Suggested class-level filtering was meaningless

### The Strict Model Is Correct

The strict model (only A-record MIDDLEs are legal) produces:
- 1,203 patterns, 0% all-49-classes
- 6 classes always survive (unfilterable core)
- Infrastructure classes are heavily filtered (13-27%)
- Mean 32.3 classes per A record (34% filtered)

---

## Key Insight

> **Class-level filtering is meaningful under strict interpretation.** Each A record creates a unique instruction subset, filtering out 34% of classes on average. Only 6 classes (the unfilterable core) are always available. Infrastructure classes require specific vocabulary contexts.

---

## Files Generated

| File | Description |
|------|-------------|
| `a_record_survivors.json` | Per-A-record class survivors (strict model) |
| `cosurvival_analysis.json` | Pairwise co-survival, Jaccard similarity |
| `class_token_map.json` | Token-to-class mapping |
