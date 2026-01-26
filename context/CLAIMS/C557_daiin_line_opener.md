# C557: daiin Line-Initial ENERGY Trigger

**Tier:** 2 | **Status:** CLOSED | **Scope:** B

---

## Statement

> The token "daiin" (Class 10, CORE_CONTROL) functions as a line-initial ENERGY trigger. With 27.7% line-initial rate (2.2x CC role average of 12.5%), daiin is the most common line opener. Following daiin, 47.1% of tokens are ENERGY class (vs ~25% baseline). Class 10 is a singleton containing only daiin, making it a unique control signal.

---

## Evidence

**Test:** `phases/CLASS_SEMANTIC_VALIDATION/scripts/daiin_opener_function.py`

### Line-Initial Statistics

| Metric | Value |
|--------|-------|
| daiin total occurrences | 314 |
| Line-initial daiin | 87 (27.7%) |
| CC role average initial | 12.5% |
| Ratio | **2.2x enriched** |

### Top Line-Initial Tokens

| Token | Count | % of Initials | Class | Role |
|-------|-------|---------------|-------|------|
| daiin | 87 | 3.4% | 10 | CC |
| saiin | 48 | 1.9% | 29 | AX |
| dain | 35 | 1.4% | 26 | AX |
| sain | 34 | 1.3% | 27 | AX |
| qokeedy | 32 | 1.3% | 33 | EN |

### Follower Role Distribution

| Role | Count | % |
|------|-------|---|
| ENERGY | 40 | 47.1% |
| UNCLASSIFIED | 22 | 25.9% |
| AUXILIARY | 14 | 16.5% |
| FREQUENT | 4 | 4.7% |
| FLOW | 3 | 3.5% |
| CORE_CONTROL | 2 | 2.4% |

### Section-Specific Behavior

| Section | daiin Initial Rate | daiin Rate/1000 |
|---------|-------------------|-----------------|
| RECIPE | 36.3% | 12.05 |
| REGIME_4 | 28.9% | 15.51 |
| BIO | 20.5% | 12.12 |
| HERBAL | 17.7% | 23.07 |

### REGIME_3 Anomaly

| REGIME | Initial Rate | Occurrence Rate |
|--------|--------------|-----------------|
| REGIME_3 | 11.9% | 24.22/1000 (highest) |
| Others | 28-34% | 10-15/1000 |

REGIME_3 uses daiin frequently (highest rate) but rarely line-initially (lowest rate). daiin in REGIME_3 functions differently than elsewhere.

---

## Interpretation

### daiin as Control Signal

daiin morphology: [PREFIX: da] + [MIDDLE: iin]

1. **Singleton class:** Class 10 = {daiin} - unique control vocabulary
2. **Line-initial function:** 27.7% initial rate signals line-opener role
3. **ENERGY trigger:** 47.1% ENERGY followers (1.9x baseline enrichment)
4. **Section-dependent:** RECIPE uses daiin-initial pattern most heavily

### Functional Model

daiin appears to function as a "start thermal processing" marker:
- Line-initial position signals control block boundary
- ENERGY-dominant followers indicate thermal operations follow
- Singleton class suggests unique grammatical function

### REGIME_3 Exception

REGIME_3's inverted pattern (high occurrence, low initial rate) suggests:
- daiin retains semantic function but loses positional role
- Or: REGIME_3 procedures differ structurally from others

---

## Cross-References

| Constraint | Relationship |
|------------|--------------|
| C085 | Consistent - daiin contains 'd' primitive |
| C358 | Confirmed - daiin identified as initial boundary marker |
| C407 | Aligned - DA-family is infrastructural; daiin serves infrastructure function |
| C550 | Extended - daiin exemplifies CC->EN transition pattern |
| C556 | Contextualized - daiin is CC exception to medial concentration |
| C552 | Refined - RECIPE section's +CC profile partly from daiin positioning |

---

## Provenance

- **Phase:** CLASS_SEMANTIC_VALIDATION
- **Date:** 2026-01-25
- **Script:** daiin_opener_function.py

---

## Navigation

<- [C556_energy_medial_concentration.md](C556_energy_medial_concentration.md) | [INDEX.md](INDEX.md) ->
