# Era-Compatibility Assessment

*Generated: 2026-01-01*
*Status: PASS - No anachronistic patterns detected*

---

## Purpose

This document assesses whether the discovered prefix archetypes are compatible with late medieval/early Renaissance plant anatomy concepts (15th century frame).

---

## Medieval Anatomical Framework

A 15th-century practitioner would have used **operational anatomy categories** (usage-based, not modern taxonomy):

| Category | Latin | Description | Medieval Examples |
|----------|-------|-------------|-------------------|
| RADIX | Radix | Roots, rhizomes, bulbs | Ginger root, mandrake root |
| HERBA | Herba/Herba tota | Above-ground aerial parts | St. John's Wort herb |
| FOLIUM | Folium | Leaves specifically | Bay leaves, senna leaves |
| FLOS | Flos | Flowers | Rose petals, chamomile flowers |
| FRUCTUS | Fructus/Semen | Fruits and seeds | Pepper, fennel seeds |
| CORTEX | Cortex/Lignum | Bark and wood | Cinnamon bark, juniper wood |
| SUCCUS | Succus/Gummi/Resina | Saps, gums, resins | Myrrh, frankincense |

These 7 categories represent the major distinctions relevant to a distillation practitioner.

---

## Archetype-to-Category Mapping Analysis

### Discovered Archetypes: 5

| Archetype | Size | Hub | Slot | Initial% | Possible Medieval Analog |
|-----------|------|-----|------|----------|-------------------------|
| 0 | 9,303 | tol | 4.6 | 9.6% | General/mixed category |
| 1 | 8,227 | sho | 4.5 | 0.0% | Internal parts (herba?) |
| 2 | 1,236 | sho | 3.6 | 22.0% | Entry markers (structural) |
| 3 | 5,742 | tol | 4.6 | 0.0% | Qualified materials |
| 4 | 16,603 | tol | 4.5 | 0.0% | Default/whole plant |

### Assessment

**Compatible count range:** 5 archetypes vs 7 medieval categories

This is **plausible** because:
- Not all 7 categories may be relevant to the specific processes encoded
- Some categories may be combined (e.g., FRUCTUS+SEMEN)
- One archetype (2) is structural (position markers), not material

**Effective material archetypes:** 4 (excluding archetype 2)
**Medieval material categories:** 6-7

The ratio (4:7) is reasonable if the manuscript focuses on a subset of materials.

---

## Feature Compatibility Check

### HUB ASSOCIATION

The archetypes cluster by hub (tol vs sho):
- **tol-associated:** Archetypes 0, 3, 4 (31,648 tokens)
- **sho-associated:** Archetypes 1, 2 (9,463 tokens)

**Era-appropriate interpretation:**
- Hub could encode material **source category** (plant family, growing region, pharmacological class)
- Hub could encode **processing affinity** (which materials process similarly)
- Hub could encode **recipe section** (which part of the procedure)

**Anachronistic interpretation (REJECTED):**
- Hubs do NOT correspond to modern botanical taxonomy (no genus/species evidence)
- Hubs do NOT correspond to cellular/tissue type (not available in 15th century)

### SLOT POSITION

Slot positions range from 3.6 to 4.6:
- **Lower slot (archetype 2, slot 3.6):** Entry-initial position markers
- **Higher slots (archetypes 0, 1, 3, 4, slots 4.5-4.6):** Content positions

**Era-appropriate interpretation:**
- Slot could encode **processing order** (which materials processed first)
- Slot could encode **importance/quantity** (primary vs secondary ingredients)

**Anachronistic interpretation (REJECTED):**
- Slots do NOT encode molecular properties (not available)
- Slots do NOT encode extraction efficiency (modern concept)

### ENTRY-INITIAL RATE

Only archetype 2 has high entry-initial rate (22%):
- **Structural interpretation:** These are **recipe section markers**, not material selectors
- Members include: ts, cp, cf, po, fc, op, of (previously identified as POSITION markers in Phase 7B)

**Era-appropriate:** Recipe/entry markers are standard in medieval procedural texts.

---

## Anachronism Check

The following modern botanical concepts were checked for absence:

| Concept | Status | Notes |
|---------|--------|-------|
| Vascular tissue | NOT PRESENT | No features distinguish monocots/dicots |
| Cellular structure | NOT PRESENT | No features relate to cell types |
| Photosynthetic capacity | NOT PRESENT | No features relate to chlorophyll |
| Secondary metabolites | INDETERMINATE | Hub association could encode this, but not proven |
| Taxonomic rank | NOT PRESENT | No genus/species-level encoding |
| Geographic origin | INDETERMINATE | Hub could encode this, but not proven |

**Result:** No anachronistic patterns detected. The archetype features (hub, slot, position) could all be reconstructed from 15th-century observational practice.

---

## Comparison to Known Medieval Practices

### Brunschwig's Categories (c. 1500)

Hieronymus Brunschwig's *Liber de arte distillandi* uses material categories that align with our framework:

| Brunschwig Category | Our Framework |
|--------------------|---------------|
| Waters (aquae) | Process output, not input |
| Herbs (herbae) | HERBA |
| Roots (radices) | RADIX |
| Flowers (flores) | FLOS |
| Seeds (semina) | FRUCTUS/SEMEN |
| Barks (cortices) | CORTEX |
| Gums (gummae) | SUCCUS |

The 5-archetype structure could encode a subset of these categories.

### Processing Order in Medieval Recipes

Medieval distillation recipes typically order materials by:
1. Hardness (harder materials crushed first)
2. Volatility (more volatile processed later)
3. Quantity (bulk materials first)

The slot position variation (3.6 to 4.6) is consistent with a processing-order encoding.

---

## Limitations

### Cannot Prove Encoding

Era-compatibility does NOT prove that prefixes encode material selection. The archetypes could instead encode:
- Grammatical function (position marking)
- Hub category association (non-material meaning)
- Scribe preference (stylistic variation)
- Random clustering (false positives)

### Missing Visual Data

Without visual annotations linking specific plant illustrations to specific prefixes, we cannot test whether archetypes correspond to visible plant-part differences.

---

## Verdict

**ERA-COMPATIBILITY: PASS**

The discovered prefix archetypes are:
1. Compatible with 15th-century plant anatomy concepts
2. Free of anachronistic patterns (no modern botany required)
3. Structurally consistent with known medieval procedural categorization

However, compatibility does NOT prove encoding. The question of whether prefixes actually encode plant-part constraints remains **INCONCLUSIVE** pending visual annotation data.

---

## Conclusion

> The prefix archetype structure is **architecturally compatible** with late medieval plant anatomy concepts. A 15th-century practitioner could have used a 5-category material classification system without anachronistic knowledge.
>
> This does NOT prove the prefixes encode material selection. It only establishes that such an encoding would be **era-appropriate if it exists**.

---

*This document reports TEST 4 findings. See anatomical_constraint_tests.md for the complete test battery.*
