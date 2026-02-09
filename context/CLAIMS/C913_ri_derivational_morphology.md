# C913: RI Derivational Morphology

**Tier:** 2 (Structural)
**Scope:** A
**Status:** CLOSED
**Phase:** RI_EXTENSION_MAPPING

---

## Statement

90.9% of RI MIDDLEs contain a PP MIDDLE as substring, following a [PP + extension] derivational pattern. Extensions are typically single characters (71.6%), with 53% suffix position and 47% prefix position. Position preferences exist: 'd' is 89% suffix, 'h' is 79% prefix, 'q' is 100% prefix.

---

## Evidence

**Phase:** RI_EXTENSION_MAPPING (2026-02-04)

**Primary findings:**

| Metric | Value |
|--------|-------|
| Containment rate | 90.9% |
| Single-char extensions | 71.6% |
| Multi-char extensions | 28.4% |
| Mean extension length | 1.43 chars |
| Suffix position | 53% |
| Prefix position | 47% |

**Top extensions by frequency:**
- 'o': 16.8%
- 'd': 12.3%
- 'h': 11.5%
- 's': 7.1%
- 'e': 7.1%
- 'a': 5.8%
- 'y': 4.2%
- 'l': 3.9%
- 't': 3.5%
- 'c': 2.9%

**Position preferences (extensions with n>=5):**
- 'd': 89% suffix (almost always added at end)
- 'h': 79% prefix (almost always added at front)
- 'q': 100% prefix (never suffix)
- 'a': 80% suffix

**Model:**
```
PP MIDDLE (general concept, shared with B)
    |
    +-- + suffix extension --> RI MIDDLE (specific instance)
    |   Examples: od -> odo, oda, ods
    |
    +-- + prefix extension --> RI MIDDLE (specific instance)
        Examples: od -> hod, cod, dod
```

**Source:** `phases/RI_EXTENSION_MAPPING/results/extension_distribution.json`

---

## Implications

1. **RI is not independent vocabulary** - it's derived from PP through productive morphology
2. **Extensions encode instance-specificity** - same PP root + different extension = different instance
3. **True vocabulary divergence is <3%** when accounting for linkers ('ho') and uncertain readings
4. **Systematic morphological process** - not random variation

---

## Related Constraints

| Constraint | Relationship |
|------------|--------------|
| C498 | RI definition - now explained compositionally |
| C511 | Derivational productivity - this IS the mechanism |
| C526 | RI lexical layer - extensions provide instance anchoring |
| C718-C719 | RI-PP independence - compositionally related but functionally separate |
| C914 | Label enrichment - extensions needed for illustration identification |
| C915 | Section P entries - pure RI vocabulary context |
