# A_SECTION_T_CHARACTERIZATION Phase Summary

**Date:** 2026-01-21
**Status:** COMPLETE
**Result:** APPARENT ANOMALY RESOLVED VIA MEASUREMENT DISAMBIGUATION

---

## Original Question

Why does Section T vocabulary have 0% presence in Currier B procedures (C299)?

---

## Investigation Path

### Phase 1: Initial Characterization

Tested whether Section T's B-absence was explained by registry-internal vocabulary (C498).

| Test | Expected if C498 explains | Actual | Verdict |
|------|---------------------------|--------|---------|
| RI Fraction | >57.6% (enriched) | 32.3% | DEPLETED |
| AZC Participation | <28.1% (reduced) | 52.8% | ENRICHED |
| Control Operators | Present | 0 found | ABSENT |
| CT-prefix | Enriched | 2.3% | DEPLETED |
| Folio Spread | ~1.3 (localized) | 12.73 | PP-LIKE |

**Finding:** Section T vocabulary is NOT registry-internal. It's MORE pipeline-participating than baseline.

### Phase 2: AZC Zone Distribution

Tested whether Section T vocabulary concentrates in S-zone (boundary) positions.

| Zone | Section T | Baseline | Ratio |
|------|-----------|----------|-------|
| S (boundary) | 15.1% | 17.9% | 0.81x DEPLETED |
| Interior (C+P+R) | 73.6% | 70.2% | 1.05x |

**Finding:** Section T vocabulary is DEPLETED in boundary zones, slightly ENRICHED in interior zones.

### Phase 3: Vocabulary Overlap Test (Key Discovery)

Tested actual vocabulary overlap between Section T and Currier B.

| Metric | Result |
|--------|--------|
| Section T MIDDLEs also in B | **86 / 127 (67.7%)** |
| Baseline (all A MIDDLEs in B) | 42.4% |
| B folios with ANY T MIDDLE | **82 / 82 (100%)** |

**Finding:** Section T vocabulary appears in ALL B folios with HIGHER overlap than typical A vocabulary.

---

## Resolution

### Two Different Questions Were Conflated

| Question | Answer |
|----------|--------|
| Does B use any vocabulary that appears in Section T? | **YES - 100% of B folios** |
| Does B use vocabulary that is *distinctive* of Section T? | **NO - 0%** |

**Both results are true simultaneously and are not in tension.**

### What C299 Actually Measures

C299 measures **section-characteristic vocabulary** (discriminators enriched or exclusive to a section), not raw vocabulary overlap.

- Section H: strong distinctive signal → dominates B (91.6%)
- Section P: weak distinctive signal → rare in B (8.4%)
- Section T: **zero distinctive signal** → nothing to map (0%)

### What Section T Actually Is

Section T (f1r, f58r, f58v) contains **no section-characteristic discrimination vocabulary**. It consists entirely of shared, infrastructure-level tokens used across all systems and sections.

The vocabulary includes: `_EMPTY_`, `a`, `al`, `ck`, `d`, `ai`, `ar`, etc. - all maximally generic infrastructure MIDDLEs.

---

## Architectural Interpretation

Section T functions as:
- A **generic baseline** (not specialized registry content)
- A **template/scaffold** (demonstrates morphology without domain specifics)
- A **non-discriminative registry surface** (orientation, not content)

This parallels C497 (f49v Instructional Apparatus):

| Folio(s) | Role |
|----------|------|
| f49v | Explicit instructional apparatus (demonstrates morphology) |
| f1r, f58r, f58v (Section T) | Implicit infrastructural baseline (generic content) |

---

## Constraint Compliance

| Constraint | Status |
|------------|--------|
| C299 | VALIDATED - measures section-characteristic vocabulary correctly |
| C295 | COMPATIBLE - "uniform sparse" = pure infrastructure |
| C383/C407/C466 | COMPATIBLE - infrastructure tokens are universal |
| C497 | COMPATIBLE - Section T is analogous to f49v template function |

---

## Outcome

### ✅ No new constraint needed

There is no new architectural necessity discovered.

### ✅ Clarification note added to C299

> **C299.a (Clarification):** C299 measures the presence of section-characteristic vocabulary (discriminators enriched or exclusive to a Currier A section), not raw vocabulary overlap. Section T shows 0% presence in Currier B because it contains no section-distinctive vocabulary, despite its constituent tokens appearing ubiquitously across B as infrastructure.

### ✅ Model remains stable

- C299 was correct
- The A→AZC→B architecture is unchanged
- No Tier reopening required

---

## Why This Resolution Matters

The earlier "execution-sterile but AZC-interior" puzzle implied a hidden blocking rule. This clarification shows:

- ❌ There is no hidden block
- ❌ No missing B-side filter
- ❌ No strange AZC loophole
- ✅ Just absence of distinctive content

**Section T isn't excluded - it's empty of distinctive content.**

---

## Files Produced

```
phases/A_SECTION_T_CHARACTERIZATION/
├── scripts/
│   ├── section_t_analysis.py
│   ├── azc_zone_analysis.py
│   └── permutation_and_overlap_test.py
├── results/
│   ├── section_t_analysis.json
│   ├── azc_zone_analysis.json
│   └── permutation_and_overlap.json
└── PHASE_SUMMARY.md
```

---

## Navigation

← [../HT_MORPHOLOGICAL_CURRICULUM/PHASE_SUMMARY.md](../HT_MORPHOLOGICAL_CURRICULUM/PHASE_SUMMARY.md) | ↑ [../../context/CLAUDE_INDEX.md](../../context/CLAUDE_INDEX.md)
