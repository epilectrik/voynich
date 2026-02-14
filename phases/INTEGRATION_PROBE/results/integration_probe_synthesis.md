# Integration Probe Synthesis: Connecting A → AZC → B

**Date:** 2026-01-11
**Phase:** INTEGRATION_PROBE
**Status:** Analysis Complete

---

## Research Question

How do the three text systems (Currier A, AZC, Currier B) connect functionally?

**Specific questions:**
1. What does each A entry represent?
2. What determines which AZC folios are relevant?
3. How does A composition connect to AZC compatibility?

---

## Probe Results Summary

### Probe 1: PREFIX -> AZC Folio Affinity

**Finding:** PARTIAL affinity - some PREFIX families show strong concentration

| PREFIX | AZC Family | Deviation from Expected |
|--------|------------|------------------------|
| **qo-** | 91% A/C | **-32.7pp A/C-enriched** |
| **ol-** | 81% A/C | **-22.7pp A/C-enriched** |
| **ot-** | 54% Zodiac | **+11.9pp Zodiac-enriched** |
| ch-, sh-, ok- | ~35-50% Zodiac | Near expected |

**Interpretation:** PREFIX encodes AZC *family* affinity for specialized families (qo, ol, ot), but not for "universal" families (ch, ok).

### Probe 2: MIDDLE -> AZC Exclusivity

**Finding:** STRONG exclusivity - MIDDLEs are highly folio-specific

| Metric | Exclusive MIDDLEs | Shared MIDDLEs | Difference |
|--------|-------------------|----------------|------------|
| Count | 545 (77%) | 164 (23%) | |
| Mean entropy | **0.023** | 0.39 | **0.367** |
| Median entropy | **0.0** | 0.346 | |
| Mean coverage | **3.3%** | 18.7% | **15.4pp** |

**Interpretation:** Exclusive MIDDLEs (median entropy = 0.0) typically appear in **exactly 1 AZC folio**. MIDDLE is the primary folio-specific component.

### Probe 3: AZC Folio Unique Contributions

**Finding:** Folios are MIDDLE-diverse but family-coherent

| Metric | Value |
|--------|-------|
| Folio-exclusive tokens | **77.8%** |
| PREFIX-coherent folios | 14.7% (only 5 of 34) |
| Family-level PREFIX differentiation | Present |

**Interpretation:** Individual folios have diverse PREFIX compositions, but MIDDLE makes vocabulary folio-specific. AZC families (Zodiac vs A/C) show PREFIX-level differentiation.

---

## The Connecting Model

### Morphological Components Encode Different Levels

| Component | Encodes | Evidence |
|-----------|---------|----------|
| **PREFIX** | AZC family affinity | qo/ol -> A/C (91%/81%), ot -> Zodiac (54%) |
| **MIDDLE** | AZC folio specificity | 77% exclusive, median entropy = 0.0 |
| **SUFFIX** | Universal legality | Not folio-specific (from C277) |

### The A → AZC → B Pipeline (Refined)

```
Currier A Entry
     |
     v
PREFIX component -----> Determines AZC FAMILY (Zodiac or A/C)
     |
     v
MIDDLE component -----> Determines specific AZC FOLIO constraints
     |
     v
AZC Constraint Profile -----> Filters vocabulary available in B
     |
     v
Currier B Program -----> Uses filtered vocabulary for execution
```

---

## Proposed New Constraints

Based on probe results, propose the following Tier 2 constraints:

### C471 - PREFIX Determines AZC Family Affinity

**Statement:** PREFIX families encode AZC family affinity: qo- and ol- strongly favor A/C family (91%/81% concentration); ot- favors Zodiac family (54%); ch-, sh-, ok- are broadly distributed.

**Evidence:** Integration Probe 1

### C472 - MIDDLE Encodes AZC Folio Specificity

**Statement:** PREFIX-exclusive MIDDLEs (77% of all MIDDLEs) appear in a median of 1 AZC folio (entropy = 0.0). The MIDDLE component, not PREFIX, is the primary determinant of AZC folio-level constraint compatibility.

**Evidence:** Integration Probe 2 (mean entropy 0.023 for exclusive vs 0.39 for shared)

### C473 - A Entry = Constraint Bundle

**Statement:** A Currier A entry's morphological composition (PREFIX + MIDDLE + SUFFIX) determines its AZC compatibility profile. The entry does not encode addressable content but rather specifies which operational contexts (AZC constraint sets) are valid.

**Evidence:** Integration Probes 1-3 combined; 77.8% of AZC vocabulary is folio-exclusive; exclusive MIDDLEs map to single folios

---

## Answers to Research Questions

### 1. What does each A entry represent?

**Answer:** A constraint bundle. Each A entry, through its morphological composition (PREFIX + MIDDLE), specifies:
- Which AZC folio FAMILY is relevant (via PREFIX)
- Which specific AZC folios' constraints apply (via MIDDLE)
- The relationship is vocabulary-mediated, not addressable

### 2. What determines which AZC folios are relevant?

**Answer:** Vocabulary composition. The tokens used in a B program determine which AZC folios' constraints are activated:
- Tokens with specialized PREFIX (qo-, ol-) activate A/C family constraints
- Tokens with exclusive MIDDLEs activate specific folio constraints
- 70% of AZC folios remain active per window (ambient field from F-AZC-015)

### 3. How does A composition connect to AZC compatibility?

**Answer:** Through morphological encoding:
- PREFIX determines family-level (Zodiac vs A/C) affinity
- MIDDLE determines folio-level specificity
- Together, they create a "compatibility signature" for each vocabulary item

---

## Implications

1. **Currier A is a constraint catalog** - each entry specifies which operational contexts (AZC constraint sets) apply

2. **AZC is not a selection mechanism** - it's a legality filter. The 30% of inactive AZC folios per window are excluded by vocabulary choice, not by dynamic decision

3. **The pipeline is vocabulary-driven** - constraints propagate through vocabulary composition, not through entry-level addressing

4. **Morphology is functional** - the compositional structure (PREFIX + MIDDLE + SUFFIX) is not decorative; it encodes operational context compatibility

---

## Next Steps

1. Validate C471-C473 with expert review
2. If accepted, update constraint registry
3. Consider whether this resolves remaining open questions or opens new ones
4. Archive probe scripts

---

*Integration Probe Complete*
