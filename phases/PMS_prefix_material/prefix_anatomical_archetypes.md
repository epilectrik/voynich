# Prefix Anatomical Archetypes

*Generated: 2026-01-01*
*Status: TEST 1 PASS - Stable archetypes discovered*

---

## Summary

| Metric | Value |
|--------|-------|
| Best cluster count (k) | 5 |
| Silhouette score | 0.463 |
| Threshold (k <= 8, sil > 0.2) | PASS |
| Era-appropriate (4-7 categories) | YES |

---

## Discovered Archetypes

Five stable prefix archetypes were discovered through unsupervised clustering on hub strength, slot position, and entry-initial/final rates.

### Archetype 0: TOL-ASSOCIATED GENERAL PREFIXES
- **Members (10):** yk, ar, sh, qe, ch, or, ol, al, ote, oke
- **Token count:** 9,303
- **Dominant hub:** tol
- **Mean slot:** 4.63
- **Entry-initial rate:** 9.6%
- **Interpretation:** General-purpose prefixes associated with tol hub category. Moderate entry-initial rate suggests they mark content throughout the entry.

### Archetype 1: SHO-ASSOCIATED INTERNAL PREFIXES
- **Members (4):** cha, dai, sho, cho
- **Token count:** 8,227
- **Dominant hub:** sho
- **Mean slot:** 4.47
- **Entry-initial rate:** 0.0%
- **Interpretation:** Never appear at entry start. Strongly associated with sho hub. May mark internal processing stages.

### Archetype 2: ENTRY-INITIAL POSITION MARKERS
- **Members (7):** ts, cp, cf, po, fc, op, of
- **Token count:** 1,236
- **Dominant hub:** sho
- **Mean slot:** 3.63
- **Entry-initial rate:** 22.0%
- **Interpretation:** Strong entry-initial bias. These are **structural position markers** (previously identified in Phase 7B as POSITION type). They mark the beginning of entries/sections.

### Archetype 3: TOL-ASSOCIATED EXTENDED PREFIXES
- **Members (6):** sha, ota, oko, oke, ara, ote
- **Token count:** 5,742
- **Dominant hub:** tol
- **Mean slot:** 4.62
- **Entry-initial rate:** 0.0%
- **Interpretation:** Never entry-initial, associated with tol. These are longer/compound prefixes that may encode more specific constraints.

### Archetype 4: HIGH-FREQUENCY TOL PREFIXES
- **Members (3):** she, qok, che
- **Token count:** 16,603
- **Dominant hub:** tol
- **Mean slot:** 4.48
- **Entry-initial rate:** 0.0%
- **Interpretation:** The most frequent prefixes (16,603 tokens). Never entry-initial. These may be default/unmarked cases for tol-category content.

---

## Archetype Structure

```
STRUCTURAL DIMENSION:
  Archetype 2 (entry-initial position markers)
       ↓
  Archetype 0 (general, moderate initial)
       ↓
  Archetypes 1, 3, 4 (internal-only)

HUB DIMENSION:
  TOL-associated: Archetypes 0, 3, 4
  SHO-associated: Archetypes 1, 2
```

---

## Era-Compatibility Assessment

The 5 archetypes could map to medieval plant anatomy concepts:

| Archetype | Possible Medieval Analog |
|-----------|-------------------------|
| 0 | General material category (unspecified) |
| 1 | Internal parts (herba, folium) |
| 2 | Section markers (recipe/entry type indicators) |
| 3 | Specific material qualifiers |
| 4 | Default processing (whole plant or common material) |

**Note:** This mapping is speculative. The archetype structure is **compatible** with era-appropriate concepts but does not prove specific material-selection encoding.

---

## Stability Analysis

| k | Silhouette | Notes |
|---|------------|-------|
| 3 | 0.404 | Underfitting |
| 4 | 0.436 | Good |
| 5 | **0.463** | Best |
| 6 | 0.426 | Slight decline |
| 7 | 0.351 | Overfitting starts |
| 8 | 0.357 | Overfitting |

The 5-cluster solution is robust (highest silhouette) and falls within the era-appropriate range of 4-7 plant-part categories.

---

## Conclusion

**TEST 1 VERDICT: PASS**

A small, stable set of 5 prefix archetypes was discovered. The archetypes are:
- Clearly separable (silhouette = 0.463)
- Era-appropriate in number (5 is within 4-7 range)
- Distinguishable by structural features (hub association, slot position, entry-initial rate)

However, this does NOT prove material-selection encoding. The archetypes are structurally real but their semantic content (if any) remains unknown.

---

*This document reports TEST 1 findings only. See anatomical_constraint_tests.md for the critical TEST 3 results.*
