# CURRIER A STRUCTURE: Comprehensive Synthesis

## Executive Summary

Currier A is a **material registry** organized at multiple structural levels:
1. **Record level** - RI tokens mark input/output materials
2. **Paragraph level** - Two types: material-focused (WITH-RI) vs process-focused (WITHOUT-RI)
3. **Folio level** - Paragraphs serve positional functions (opening, middle, closing)
4. **Section level** - H (Herbal) vs P (Pharmaceutical) use different organizational strategies

---

## Part 1: The RI Input/Output Model (Prior Constraints)

### C832: Initial/Final RI Vocabulary Separation

Within records, RI tokens show **complete vocabulary separation** by position:

| Position | Function | Signature Prefixes | Example |
|----------|----------|-------------------|---------|
| INITIAL (< 0.2) | Input material | po-, do- | What source material |
| FINAL (> 0.8) | Output material | ch-, ct- | What result produced |

- Jaccard similarity = **0.010** (essentially disjoint vocabularies)
- Only **4 tokens** appear in both positions

### C837: The ct-ho Linker Signature

The 4 tokens that bridge initial/final positions:

| Token | PREFIX | MIDDLE | Interpretation |
|-------|--------|--------|----------------|
| cthody | ct | ho | Transferable output |
| ctho | ct | ho | Transferable output |
| ctheody | ct | heo | Transferable output |
| qokoiiin | qo | koi | Different mechanism |

**Key insight:** ct-ho marks "transferable outputs" - materials that can serve as inputs to other processes.

---

## Part 2: Paragraph-Level Structure (New Findings)

### Two Opening Types

| Type | Count | % | First Line Content |
|------|-------|---|-------------------|
| WITH-RI | 215 | 62.9% | RI + PP (material identification) |
| WITHOUT-RI | 127 | 37.1% | Pure PP (92.7% have no RI) |

### WITHOUT-RI Characteristics

| Property | Value | Interpretation |
|----------|-------|----------------|
| First line pure PP | 92.7% | Skip material identification |
| RI vocabulary Jaccard | 0.028 | Almost completely distinct from WITH-RI |
| Linker density (ct/RI) | 1.35x higher | More linking vocabulary |
| LINK prefixes (ol/or) | 2.7x enriched | More monitoring vocabulary |
| LAST position | 1.62x enriched | Closure function |
| FIRST position | 22% appear here | Independent units |

### Backward Reference Mechanism

WITHOUT-RI paragraphs reference **preceding** paragraphs:

| Measure | WITH-RI | WITHOUT-RI |
|---------|---------|------------|
| Backward overlap (Jaccard) | 0.189 | 0.202 |
| Forward overlap (Jaccard) | 0.207 | 0.164 |
| **Asymmetry (back/forward)** | 0.91x | **1.23x** |

WITHOUT-RI after WITH-RI shows highest overlap (0.228) - they reference the just-identified material.

### Cross-Folio Continuity

FIRST-position WITHOUT-RI paragraphs are **NOT** continuations from previous folios:
- Cross-folio overlap: 0.209 (similar to WITH-RI's 0.223)
- They are independent units, not cross-folio references

---

## Part 3: Position Sub-Types

### WITHOUT-RI by Position

| Position | Count | Distinctive Features |
|----------|-------|---------------------|
| FIRST | 28 | Higher qo (15.9%), 2.14x more linkers, setup/energy focus |
| MIDDLE | 44 | Highest sh (18.5%), peak phase control |
| LAST | 42 | Higher ct (6.9%), higher ol (3.1%), closure/linking focus |

RI vocabulary Jaccard between FIRST and LAST: **0.013** (completely distinct sub-types)

### Functional Interpretation

| Position | Function | Evidence |
|----------|----------|----------|
| FIRST WITHOUT-RI | Folio preamble/setup | High energy (qo), independent |
| MIDDLE WITHOUT-RI | Process annotations | Backward reference, phase control |
| LAST WITHOUT-RI | Closure/cross-reference | High linker, high LINK prefixes |

---

## Part 4: Section-Level Differences

### Distribution

| Section | Folios | % WITHOUT-RI | Character |
|---------|--------|--------------|-----------|
| H (Herbal) | 95 | **48.7%** | Process-heavy |
| P (Pharmaceutical) | 16 | 20.8% | Material-heavy |
| T | 3 | 26.7% | Material-heavy |

### PP Profile Differences in WITHOUT-RI

| Prefix | Section H | Section P | H/P Ratio | Interpretation |
|--------|-----------|-----------|-----------|----------------|
| ct (LINKER) | 6.6% | 1.7% | **3.87x** | H = cross-referencing |
| qo (ESCAPE) | 13.2% | 21.1% | 0.63x | P = safety protocols |
| ok (AUXILIARY) | 5.4% | 15.5% | 0.35x | P = auxiliary ops |
| ol (MONITOR) | 1.7% | 5.5% | 0.31x | P = monitoring |

**Key finding:** WITHOUT-RI paragraphs serve **different functions** in different sections:
- **Section H:** Cross-reference/indexing between plant materials
- **Section P:** Safety and recovery protocols for drug preparation

---

## Part 5: The ct-ho Vocabulary System

### Two-Level Operation

The ct-ho pattern operates at both RI and PP levels:

| Level | Tokens | Context | Function |
|-------|--------|---------|----------|
| RI (C837) | ctho, cthody, ctheody | Initial/final positions | Mark transferable materials |
| PP (new) | cthy, cthol, cthor | WITHOUT-RI paragraphs | Process instructions for transfers |

### Reserved MIDDLEs

In Section H, certain MIDDLEs are almost **exclusively** ct-prefixed:

| MIDDLE | ct-prefixed | Total | % Reserved |
|--------|-------------|-------|------------|
| h | 182 | 185 | 98.4% |
| hy | 96 | 97 | 99.0% |
| ho | 36 | 36 | 100% |

This creates a **reserved vocabulary** for linking/transfer operations.

---

## Part 6: The Integrated Model

### Record Structure (Within Paragraph)

```
[INITIAL RI: input material] + [PP: process steps] + [FINAL RI: output material]
     (po-, do- prefix)              (ch, sh, qo...)        (ch-, ct- prefix)
```

### Paragraph Structure (Within Folio)

```
FOLIO START
  |
  +-- [WITH-RI paragraph] -- Material record: identifies input, describes process, identifies output
  |
  +-- [WITHOUT-RI paragraph] -- Process annotation: describes processes for preceding material
  |         ^
  |         | backward reference (Jaccard 0.228)
  |
  +-- [WITH-RI paragraph] -- Next material record
  |
  +-- [WITHOUT-RI paragraph] -- Closure/cross-reference: links to other folios/materials
  |
FOLIO END
```

### Section Organization

**Section H (Herbal):**
- More WITHOUT-RI (48.7%) - needs more cross-referencing
- WITHOUT-RI = indexing/linking between plant materials
- Heavy ct-ho vocabulary for "transferable outputs"

**Section P (Pharmaceutical):**
- Fewer WITHOUT-RI (20.8%) - material identification is primary
- WITHOUT-RI = safety protocols (escape routes, monitoring)
- Heavy qo, ok, ol vocabulary for hazard management

---

## Part 7: Potential Contradictions and Tensions

### 1. RI Vocabulary Overlap

| Comparison | Jaccard | Tension |
|------------|---------|---------|
| INITIAL vs FINAL RI (C832) | 0.010 | Very low |
| WITH-RI vs WITHOUT-RI paragraphs | 0.028 | Very low |
| FIRST vs LAST WITHOUT-RI | 0.013 | Very low |

**No contradiction** - all comparisons show vocabulary separation. The system maintains distinct vocabularies at every level.

### 2. ct-prefix Function

| Finding | Source | Claim |
|---------|--------|-------|
| C837 | Prior | ct-ho marks transferable outputs (RI level) |
| Test 24 | New | ct-prefix is 78% PP in Section H |

**Resolution:** ct-ho operates at TWO levels:
- RI level: marks the materials themselves
- PP level: describes processes that create/use these materials

### 3. WITHOUT-RI as "Continuations"

| Test | Finding |
|------|---------|
| Test 08 (continuation) | REJECTED - WITHOUT-RI are independent |
| Test 19 (backward reference) | CONFIRMED - higher overlap with PRECEDING |

**Resolution:** NOT a contradiction. WITHOUT-RI paragraphs are:
- **Independent structural units** (not syntactic continuations)
- **Semantically reference** preceding material (process applies to just-identified material)

### 4. Cross-Folio vs Within-Folio

| Context | WITHOUT-RI overlap |
|---------|-------------------|
| Within-folio (with PREV) | 0.202 |
| Cross-folio (with PREV folio) | 0.209 |

**No contradiction** - similar overlap suggests folio boundaries don't strongly affect continuity. The "backward reference" is primarily a within-folio phenomenon for non-FIRST paragraphs.

---

## Part 8: What Remains Unknown

1. **Specific material mappings** - We know the STRUCTURE but not which RI tokens map to which Brunschwig materials

2. **The qokoiiin exception** - One linker doesn't follow ct-ho pattern; different mechanism?

3. **Section T** - Only 3 folios, insufficient data

4. **AZC interaction** - How do A entries activate through AZC? (Covered by other constraints)

5. **B convergence specifics** - All paragraph types converge to all 82 B folios (Jaccard 1.0); the PP vocabulary is shared, but HOW does routing work?

---

## Part 9: Proposed New Constraints

From this investigation, the following constraints are ready for formalization:

### C881: A Record Paragraph Structure (Tier 2)

Currier A paragraphs divide into two opening types with distinct functions:
- WITH-RI (62.9%): Material-focused records starting with RI identification
- WITHOUT-RI (37.1%): Process-focused annotations starting with pure PP (92.7%)

### C882: WITHOUT-RI Backward Reference (Tier 2)

WITHOUT-RI paragraphs show backward reference to preceding paragraphs:
- Backward/forward asymmetry: 1.23x
- Highest overlap when following WITH-RI (0.228)
- Mechanism: Sequential convention (process applies to preceding material)

### C883: Section-Specific WITHOUT-RI Function (Tier 2)

WITHOUT-RI paragraphs serve different functions by section:
- Section H: Cross-reference/indexing (ct-prefix 3.87x enriched)
- Section P: Safety protocols (qo, ok, ol enriched)

### C884: ct-ho Reserved Vocabulary (Tier 2)

MIDDLEs h, hy, ho are almost exclusively ct-prefixed (98-100%):
- Creates reserved vocabulary for linking/transfer operations
- Extends C837 (ct-ho linker signature) to PP level

---

## Conclusion

Currier A is a **hierarchically organized material registry**:

1. **Records** identify input materials, describe processes, and identify output materials
2. **Paragraphs** alternate between material identification (WITH-RI) and process annotation (WITHOUT-RI)
3. **Folios** have positional structure (opening setup, middle content, closing cross-references)
4. **Sections** specialize: H for plant material indexing, P for pharmaceutical safety

The ct-ho vocabulary system provides **cross-reference capability** at both RI and PP levels, allowing materials to be marked as "transferable outputs" that link across the registry.

This structure is consistent with a **practical reference work** (per Brunschwig model) where users need to:
- Look up specific materials (WITH-RI records)
- Understand processing steps (WITHOUT-RI annotations)
- Navigate between related materials (ct-ho cross-references)
- Follow safety protocols (Section P's WITHOUT-RI)
