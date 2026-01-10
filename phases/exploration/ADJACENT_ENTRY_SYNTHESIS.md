# Adjacent Entry Analysis: What Drives the 1.31x Similarity?

**Date:** 2026-01-09
**Status:** COMPLETE
**Related Constraint:** C346

---

## Summary

Decomposed the 1.31x adjacent entry similarity (C346) to reveal the organizational logic of Currier A.

**Key Finding:** The catalog is organized by CONTENT/TOPIC, not by marker category. Adjacent entries share vocabulary because they describe related content, not because they're grouped by prefix family.

---

## Decomposition Results

| Component | Adjacent | Non-adjacent | Ratio | p-value |
|-----------|----------|--------------|-------|---------|
| **token_jaccard** | 0.0252 | 0.0192 | **1.31x** | <0.000001 |
| **middle_jaccard** | 0.0572 | 0.0467 | **1.23x** | <0.000001 |
| **suffix_jaccard** | 0.2338 | 0.1987 | **1.18x** | <0.000001 |
| **prefix_jaccard** | 0.3624 | 0.3142 | **1.15x** | <0.000001 |
| marker_continuity | 0.8265 | 0.7656 | 1.08x | <0.000001 |
| dominant_marker_match | 0.2966 | 0.2624 | 1.13x | 0.002 |

**Primary driver:** Full vocabulary sharing (1.31x), followed by middle components (1.23x).

**Weakest driver:** Marker continuity (1.08x) - entries don't cluster strongly by prefix.

---

## Section Boundary Effect

| Comparison | Mean Jaccard | Ratio |
|------------|--------------|-------|
| Same section | 0.0160 | - |
| Cross section | 0.0066 | **2.42x** |

**Interpretation:** Section (H/P/T) is the dominant organizational axis. Vocabulary similarity drops sharply at section boundaries.

---

## Marker Transitions

Same-marker transitions: 31.8% (adjacent) vs 29.9% (non-adjacent) = only 1.06x

**Top adjacent transitions:**
```
ch -> ch: 318 (dominant same-marker)
qo -> ch: 78  (bridging to primary)
da -> ch: 72  (infrastructure to primary)
sh -> ch: 71  (sister pair transition)
ch -> sh: 70  (sister pair transition)
```

**Sister pair ch-sh:**
- Same ch: 318
- Same sh: 24
- ch <-> sh: 141 (frequent alternation)

---

## Marker Distribution by Section

| Section | ch | da | sh | qo | ct | ok |
|---------|-----|-----|-----|-----|-----|-----|
| H (Herbal) | 32.2% | 15.4% | 14.6% | 14.2% | 7.6% | 2.7% |
| P (Pharmaceutical) | 27.7% | 15.6% | 10.8% | 17.1% | 1.7% | 13.3% |
| T (Text-only) | 23.4% | 15.1% | 18.9% | 12.9% | 2.5% | 11.4% |

**Observations:**
- ch dominates all sections but declines from H (32%) to T (23%)
- ct is Section H specialist (7.6% vs <3% elsewhere) - confirms C240
- ok rises in P and T (13%, 11%) vs H (2.7%)
- qo peaks in P (17.1%)

---

## Interpretation

### Organizational Hierarchy

1. **SECTION** (H/P/T) - Primary axis (2.42x boundary effect)
2. **CONTENT/TOPIC** - Secondary axis (1.31x vocabulary clustering)
3. **SUB-TYPE** - Tertiary (1.23x middle component sharing)
4. **PROPERTIES** - Quaternary (1.18x suffix sharing)
5. **MARKER FAMILY** - Weakest (1.15x prefix sharing)

### What This Means

The catalog is **NOT** organized like a parts list:
```
[ch entries] → [sh entries] → [ok entries] → ...
```

It's organized more like a **topical encyclopedia**:
```
[Topic A entries, mixed markers] → [Topic B entries, mixed markers] → ...
```

Adjacent entries share vocabulary because they describe related CONTENT (plants, preparations, etc.), not because they share the same marker prefix.

### Marker Function

Markers classify WITHIN topics, not across them:
- A topical cluster might contain ch-, sh-, da-, qo- entries
- The marker indicates the TYPE of information (classification, quantity, property)
- Not the TOPIC of information (which is indicated by vocabulary)

---

## Constraint Implications

### Confirms C345-C346
- C345: No folio-level thematic coherence - CONFIRMED (folios are containers)
- C346: Adjacent entries share 1.31x vocabulary - CONFIRMED and DECOMPOSED

### Extends C240 Understanding
- The 8 marker families are classification tags, not organizational groups
- Catalog sorted by topic/content, markers applied within topics

### New Constraint Candidate

> **C4XX: Currier A Organization is CONTENT-FIRST, not MARKER-FIRST**
>
> Adjacent entries share vocabulary (1.31x) because they describe related content.
> Marker prefixes classify entries within topical clusters, not across them.
> Section is the primary organizational axis (2.42x boundary effect).

---

## Scripts

| File | Purpose |
|------|---------|
| `adjacent_entry_analysis.py` | Decomposition of C346 similarity |
| `adjacent_section_boundary.py` | Section boundary effect test |

---

## Navigation

← [FIRST_TOKEN_SYNTHESIS.md](FIRST_TOKEN_SYNTHESIS.md) | ↑ [../../context/CLAUDE_INDEX.md](../../context/CLAUDE_INDEX.md)
