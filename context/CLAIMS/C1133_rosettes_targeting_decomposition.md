# C1133: Rosettes Targeting Decomposition

**Tier:** 2
**Status:** Active
**Scope:** Rosettes foldout / Currier B sections
**Phase:** 405 (SECTION_PROGRAM_ARCHITECTURE)
**Qualifies:** C1125 (Section T targeting — adds critical context)

## Finding

The C1125 finding that "all 9 rosettes correlate most strongly with Section T" is a **vocabulary-size artifact** of section-level Jaccard comparison, not a genuine section-targeting effect. Per-folio analysis reveals a different picture.

### Critical Context for C1125

1. **Section T has only 1 B folio after Rosettes exclusion:** f66r (329 tokens, 112 MIDDLEs). The other T folio (f85r1) IS a Rosettes foldout folio, excluded from the comparison.

2. **Per-folio, f66r ranks #11 of 76**, not #1. The top 10 Rosettes-overlapping folios are 9 Section S (Stars/Recipes) + 1 Section H (Herbal):

| Rank | Folio | Section | Jaccard |
|------|-------|---------|---------|
| 1 | f105r | S | 0.181 |
| 2 | f116r | S | 0.175 |
| 3 | f112v | S | 0.171 |
| 11 | f66r | T | 0.161 |

3. **Section T "wins" at the section level because it has the smallest vocabulary** (112 MIDDLEs vs S: 851, H: 406, B: 396). Jaccard = intersection/union. All sections share ~17-24 MIDDLEs with Rosettes (similar intersections), but T's smaller union inflates the ratio.

4. **f66r's overlap IS genuine** (100th percentile of size-controlled bootstrap from all sections), but not unique — multiple S folios overlap more.

### Bridge Density Triangle: FALSIFIED

Bridge MIDDLE density **negatively** correlates with Rosettes overlap (Spearman rho = -0.60):

| Section | Per-Folio Bridge Mean | Section Bridge | Rosettes Overlap |
|---------|-----------------------|----------------|------------------|
| H | 69.9% (highest) | 19.7% | 0.077 (2nd) |
| B | 60.9% | 18.7% | 0.071 (3rd) |
| S | 48.2% | 9.9% (lowest) | 0.040 (4th*) |
| T | 47.3% (lowest) | 47.3% (section = folio) | 0.183 (1st*) |

*Section-level Jaccard from C1125. Per-folio ranking shows S folios overlap most.

The bridge density triangle (Rosettes bridge-enriched + target T + T bridge-enriched → closed explanation) does not hold. f66r ranks #66/76 in bridge density. The mechanism is vocabulary diversity, not bridge concentration.

### f66r Overlap Composition

40 MIDDLEs shared between f66r and Rosettes:
- 30 bridge MIDDLEs (75%)
- 10 non-bridge MIDDLEs (25%)

The overlap is predominantly bridge-mediated (75%), but f66r is not a bridge hub. It has moderate bridge density (47.3%) with genuine vocabulary affinity beyond bridge vocabulary.

### Section Architecture (Confirmatory)

Sections are differentiated (mean JS divergence = 0.091, confirming C552/C1029), with T intermediate on all metrics:
- Role profiles: T has highest FLOW_OPERATOR (11.4%) and CORE_CONTROL (6.9%)
- Kernel balance: T is unremarkable (k=18.5%, h=7.9%, e=35.9%)
- Grammar coverage: T lowest (61.4% vs B 77.7%)
- T is not architecturally distinctive — the Rosettes connection is vocabulary-based, not architecture-based

### Naming Correction

C1125 says "Section T (pharmaceutical)" but TRANSCRIPT_ARCHITECTURE identifies T = "Text" (text-only pages). Section P = Pharmaceutical (jars/containers). The parenthetical in C1125 is incorrect.

## Implication

The Rosettes foldout does not specifically "target" Section T. It overlaps most with diverse, vocabulary-rich folios — primarily Section S (Stars/Recipes). The C1125 section-level comparison is confounded by vocabulary size differences. The Rosettes vocabulary is general-purpose metalayer vocabulary that overlaps with whatever B folios have the most diverse MIDDLE inventories.

## Provenance

- Source: Phase 405, Tests T1-T8 (8-test battery)
- Qualifies: C1125 (adds context, corrects framing)
- Related: C1124 (Rosettes bridge enrichment), C1128 (generic indexing), C552 (section role profiles)
