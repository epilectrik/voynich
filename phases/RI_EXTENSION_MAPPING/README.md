# RI_EXTENSION_MAPPING Phase

**Date:** 2026-02-04
**Status:** COMPLETE
**Tier:** 2 (Structural)
**Verdict:** RI = PP + derivational extension (confirmed)

---

## Key Discovery

**RI vocabulary is built by extending PP vocabulary with single-character suffixes/prefixes.**

This is not independent vocabulary - it's derivational morphology for creating instance-specific identifiers.

---

## Results Summary

### Priority 1: Extension Character Distribution

| Finding | Value |
|---------|-------|
| Containment rate | 90.9% |
| Single-char extensions | 71.6% |
| Mean extension length | 1.43 chars |
| Position split | 53% suffix, 47% prefix |

**Top extensions:** 'o' (16.8%), 'd' (12.3%), 'h' (11.5%), 's' (7.1%), 'e' (7.1%)

**Position preferences:**
- 'd' is 89% suffix (almost always added at end)
- 'h' is 79% prefix (almost always added at front)
- 'q' is 100% prefix (never suffix)
- 'a' is 80% suffix

### Priority 2: Non-Containment Cases (9.1%)

The 112 non-containment tokens are:
- **'ho' (42 tokens)** - ct-prefixed linker vocabulary, special case
- **Asterisk tokens (uncertain readings)** - transcription artifacts
- Only **24 "truly novel"** cases, almost all with asterisks

**Conclusion:** True non-containment is <3% when excluding linker vocabulary and uncertain readings.

### Priority 3: First-Line RI Structure

Pure-RI first lines (24/345 = 7%):
- **83% in Section P** (pharmaceutical)
- **0% ct-prefixed** (NOT linkers)
- **23/24 are single-line paragraphs**
- Mean position: para 7.7 (later in folio)
- All tokens are unique singletons
- Prefixes: da (25%), ot (20%), sa (15%)

**Interpretation:** These are specialized single-line reference entries in Section P, distinct from the linker system.

---

## Structural Model

```
PP MIDDLE (general concept, shared with B)
    │
    ├── + suffix extension → RI MIDDLE (specific instance)
    │   Examples: od → odo, oda, ods
    │
    └── + prefix extension → RI MIDDLE (specific instance)
        Examples: od → hod, cod, dod
```

**Extension characters encode instance differentiation:**
- Same PP root + different extension = different instance
- Extensions vary by folio context
- Labels need more RI because they identify SPECIFIC illustrated items

---

## Section Differences

| Section | RI Rate | Pure-RI First Lines | Notes |
|---------|---------|---------------------|-------|
| H (Herbal) | 6.8% | 2.0% | Standard distribution |
| P (Pharma) | 7.4% | **15.4%** | Concentrated pure-RI entries |
| T | 8.7% | 0% | Higher RI, no pure-RI first lines |

Section P has specialized single-line RI entries that Section H lacks.

---

## Files

```
phases/RI_EXTENSION_MAPPING/
├── README.md
├── scripts/
│   ├── 01_extension_distribution.py
│   ├── 02_non_containment_cases.py
│   └── 03_firstline_ri_structure.py
└── results/
    ├── extension_distribution.json
    ├── non_containment_cases.json
    └── firstline_ri_structure.json
```

---

## Documented Constraints

### C913: RI Derivational Morphology
> 90.9% of RI MIDDLEs contain a PP MIDDLE as substring. RI = PP + extension, where extensions are typically single characters (o, d, h, s, e, a, y, l, t, c). Extensions are 71.6% single-character, with 53% suffix position and 47% prefix position. Position preferences exist: 'd' is 89% suffix, 'h' is 79% prefix, 'q' is 100% prefix.

**Tier:** 2 | **Scope:** A | **Status:** CLOSED

### C914: RI Label Enrichment
> RI vocabulary is 3.7x enriched in illustration labels (27.3% vs 7.4% in text). Labels identify specific illustrated items, requiring instance-specific vocabulary built via the PP+extension derivational system.

**Tier:** 2 | **Scope:** A | **Status:** CLOSED

### C915: Section P Pure-RI Entries
> 83% of pure-RI first-line paragraphs occur in Section P. These are single-line entries (23/24), appear later in folios (mean para 7.7), use da/ot/sa prefixes (not ct-), and are distinct from the linker system. They may represent specialized reference entries in pharmaceutical content.

**Tier:** 2 | **Scope:** A | **Status:** CLOSED

### C916: RI Instance Identification System (Synthesis)
> RI functions as an instance identification system built via PP+extension derivation. PP encodes general categories (shared with B); RI identifies specific instances. This explains A's purpose as an index bridging general procedures (B) to specific applications. Labels are 3.7x RI-enriched for illustration identification.

**Tier:** 2 | **Scope:** A | **Status:** CLOSED

---

## Relationship to Existing Constraints

| Constraint | Relationship |
|------------|--------------|
| C240 | A = Registry - C916 explains the indexing mechanism |
| C498 | RI definition - now explained compositionally by C913 |
| C511 | Derivational productivity - C913 IS the mechanism |
| C526 | RI lexical layer - extensions provide instance anchoring |
| C718-C719 | RI-PP independence - compositionally related but functionally separate |
| C833 | RI first-line concentration - C915 identifies specialized subset |
| C835 | Linkers - 'ho' MIDDLE is linker vocabulary, explains non-containment |

---

## Implications

1. **RI is not independent vocabulary** - it's derived from PP
2. **Extensions encode instance-specificity** - same concept, different instance
3. **Labels need more RI** because they point to specific illustrated items
4. **Section P has specialized structure** - pure-RI entry markers
5. **True vocabulary divergence is <3%** when accounting for linkers and uncertain readings
