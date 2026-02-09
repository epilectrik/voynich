# C915: Section P Pure-RI Entries

**Tier:** 2 (Structural)
**Scope:** A
**Status:** CLOSED
**Phase:** RI_EXTENSION_MAPPING

---

## Statement

83% of pure-RI first-line paragraphs occur in Section P. These are single-line entries (23/24), appear later in folios (mean paragraph position 7.7), use da/ot/sa prefixes (NOT ct-prefixed linkers), and represent specialized reference entries distinct from the linker system.

---

## Evidence

**Phase:** RI_EXTENSION_MAPPING (2026-02-04)

**Primary findings:**

| Metric | Value |
|--------|-------|
| Pure-RI first lines | 24/345 (7.0%) |
| Section P concentration | 20/24 (83.3%) |
| Section H | 3/24 (12.5%) |
| Section T | 1/24 (4.2%) |
| Single-line paragraphs | 23/24 (95.8%) |
| Mean paragraph position | 7.7 |
| ct-prefixed tokens | 0% |

**Section breakdown:**
- Section H: 2.0% pure-RI first lines
- Section P: **15.4%** pure-RI first lines
- Section T: 0% pure-RI first lines

**Prefix distribution:**
- da: 25%
- ot: 20%
- sa: 15%
- (NOT ct - ruling out linker function)

**Distinguishing characteristics:**
- NOT linkers (0% ct-prefix, known linkers absent)
- Single-line (not paragraph headers)
- Later in folios (not folio-initial)
- All RI tokens are unique singletons

**Source:** `phases/RI_EXTENSION_MAPPING/results/firstline_ri_structure.json`

---

## Implications

1. **Section P has specialized structure** - pharmaceutical content requires reference entries
2. **Pure-RI entries are NOT linkers** - distinct from the ct-prefixed linker system (C835)
3. **Single-line format suggests indexing** - not narrative text, not procedural instructions
4. **Position suggests supplementary role** - later in folio = addendum/reference material

---

## Functional Model

Section P pharmaceutical folios include:
```
Paragraph 1-6: Standard PP+RI mixed text (procedures)
Paragraph 7+: Pure-RI single-line entries (reference index?)
```

These may represent:
- Cross-references to specific preparations elsewhere
- Index entries for illustrated containers/tools
- Instance-specific annotations

---

## Related Constraints

| Constraint | Relationship |
|------------|--------------|
| C913 | Derivational morphology - these entries use RI vocabulary |
| C914 | Label enrichment - similar instance-identification function |
| C835 | Linker mechanism - ct-prefixed linkers are distinct system |
| C833 | RI first-line concentration - specialized subset |
| C902 | Late Currier A register - section-specific patterns |
