# MIDDLE_SEMANTIC_DEEPENING Phase

**Date:** 2026-02-04
**Status:** COMPLETE
**Verdict:** PRODUCTIVE - Major morphological constraints discovered
**Predecessor:** MIDDLE_SEMANTIC_MAPPING (C908-C910)
**Goal:** Deep characterization of MIDDLE functional semantics

---

## Research Questions

### 1. Precision Vocabulary Deep Dive (m MIDDLE)
The `m` MIDDLE is 7.24x enriched in REGIME_4 (precision) folios - the strongest signal found.
- What contexts does `m` appear in?
- What PREFIX/SUFFIX combinations?
- What folios? What sections?
- Hypothesis: `m` encodes measurement or fine adjustment

### 2. MIDDLE Co-occurrence Networks
Which MIDDLEs appear together vs never co-occur?
- Paragraph-level co-occurrence matrix
- Identify mutually exclusive pairs (incompatible operations)
- Identify strongly correlated pairs (operation sequences)
- Could reveal apparatus constraints

### 3. PREFIX × MIDDLE Interaction
PREFIX encodes handling mode, MIDDLE encodes operation type.
- Are certain PREFIX+MIDDLE combinations forbidden?
- Do prefixes select for specific MIDDLE families?
- Extends F-BRU-012 (PREFIX × MIDDLE modification system)

### 4. h-Cluster Function (ch/sh/pch/d)
These MIDDLEs correlate with HIGH_H (phase monitoring).
- Also overlap with C907 -hy infrastructure
- What distinguishes ch from sh from pch?
- Line position patterns?
- Hypothesis: Phase-checking operations at different granularities

### 5. SUFFIX Semantic Patterns
We've characterized MIDDLE thoroughly. What about SUFFIX?
- -y vs -dy vs -edy distinction
- -in vs -iin patterns
- Do suffixes encode intensity/completion?

### 6. Folio-Unique MIDDLEs
MIDDLEs appearing in only one folio = identification vocabulary
- How many folio-unique MIDDLEs exist?
- What do they mark? Material-specific operations?

---

## Prior Work (MIDDLE_SEMANTIC_MAPPING)

| Finding | Constraint | Key Metric |
|---------|------------|------------|
| Kernel correlation | C908 | 55% significant |
| Section vocabulary | C909 | 96% section-specific |
| REGIME clustering | C910 | 67% REGIME-specific, m=7.24x |

---

## Planned Analyses

| Script | Purpose | Priority |
|--------|---------|----------|
| `01_m_middle_deep_dive.py` | Precision vocabulary characterization | HIGH |
| `02_middle_cooccurrence.py` | Paragraph-level co-occurrence network | HIGH |
| `03_prefix_middle_interaction.py` | PREFIX × MIDDLE combination analysis | MEDIUM |
| `04_h_cluster_function.py` | ch/sh/pch/d functional analysis | MEDIUM |
| `05_suffix_patterns.py` | SUFFIX semantic mapping | MEDIUM |
| `06_folio_unique_middles.py` | Identification vocabulary analysis | LOW |

---

## Success Criteria

**PRODUCTIVE if:**
- `m` MIDDLE function characterized
- Co-occurrence network reveals operational constraints
- PREFIX × MIDDLE interaction patterns documented
- New Tier 2-3 constraints

**NULL if:**
- `m` appears randomly distributed
- No co-occurrence structure
- PREFIX × MIDDLE combinations unrestricted

