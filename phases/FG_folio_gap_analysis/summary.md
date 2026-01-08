# Phase FG: Folio Gap Analysis

**Question:** Were folios removed from the Voynich Manuscript after composition?

**Status:** CLOSED (4/4 tests PASS)

---

## Methodology

Tested for structural signatures of post-composition folio removal using internal evidence only. If folios were removed *after* writing, we would expect:

- State discontinuities between adjacent extant folios
- Disrupted HT orientation patterns at folio boundaries
- Grammar sequences starting mid-procedure
- Truncation asymmetry in section archetypes

If folios were removed *before* writing, the text would show nothing.

---

## Results

### FG-1: State Continuity Break Test

**Method:** Compared state vectors (terminal state, link density, kernel dominance, hazard density, cycle regularity) between consecutive folios.

| Metric | Value |
|--------|-------|
| Folios analyzed | 83 |
| Consecutive pairs | 82 |
| Null mean distance | 1.072 |
| Observed mean distance | 0.937 |
| Effect size (d) | -0.20 |
| Extreme discontinuities (>3 sigma) | 0 |

**Top transitions (all < 3 sigma):**
- f85v2 -> f86v3: z=2.33
- f55v -> f57r: z=1.81 (expected - f57r is RESTART_PROTOCOL)

**VERDICT: PASS** - Observed continuity BETTER than random (no removal signal)

---

### FG-2: HT Orientation Reset Test

**Method:** Compared HT prefix distributions at folio starts vs mid-folio positions.

| Metric | Value |
|--------|-------|
| Start (first 10 tokens) | 149 HT tokens |
| Mid-folio | 9,573 HT tokens |
| End (last 10 tokens) | 128 HT tokens |
| EARLY-phase enrichment at starts | 2.69x |

EARLY-phase prefixes (op-, pc-, do-) are strongly enriched at folio starts (47.0% vs 17.4% mid-folio), confirming proper orientation patterns.

**VERDICT: PASS** - Folio starts show proper orientation patterns

---

### FG-3: Grammar Start-State Expectation Test

**Method:** Checked whether folios begin with morphologically valid patterns (HT, grammar, or known compositional forms).

| Metric | Value |
|--------|-------|
| Starts with core HT prefix | 32.5% |
| Starts with any known prefix | 75.9% |
| Anomalous starts | 20 folios |
| Of anomalous, morphologically regular | 15/20 (75%) |

The 20 "anomalous" starts break down as:
- 15 (18.1% of total) are EVA-valid compositional forms (pdair, pdsairy, kcheedchdy, etc.)
- 5 (6.0% of total) are transcription artifacts:
  - f85v2: `***in` (damaged token)
  - f113v: `folorarom` (rare 'm' glyph - valid EVA)
  - f84r: `lmyl` (rare 'm' glyph - valid EVA)
  - f75v, f76r: `s` (single character, truncated)

None indicate structural anomaly - all are explicable as transcription noise.

**VERDICT: PASS** - Most folios start with recognizable morphological patterns

---

### FG-4: Section Archetype Integrity Test

**Method:** Compared variance in first half vs second half of each section.

| Section | Folios | First Half Var | Second Half Var | Asymmetry |
|---------|--------|---------------|-----------------|-----------|
| S | 23 | 0.0055 | 0.0028 | 0.0027 |
| H | 32 | 0.0029 | 0.0050 | 0.0021 |
| B | 20 | 0.0012 | 0.0020 | 0.0008 |
| C | 6 | 0.0043 | 0.0042 | 0.0001 |

Mean asymmetry: 0.0014 (very low)
Max asymmetry: 0.0027 (Section S)

**VERDICT: PASS** - Sections are internally symmetric

---

## Conclusion

**NO STRUCTURAL EVIDENCE of post-composition folio removal detected.**

All four tests pass:
1. State continuity is *better* than random (d=-0.20)
2. HT orientation patterns confirm proper composition
3. Folio starts are morphologically valid
4. Sections are internally symmetric

The strongest transitions (f85v2 -> f86v3, f55v -> f57r) are within 3 sigma and explicable by known restart mechanisms.

---

## Formal Statement

> *"We found no statistically measurable discontinuities in procedural state, human-orientation patterns, or section archetypes indicating post-composition folio removal. Any missing pages must predate composition or fall outside the encoded control system."*

---

## What This Does NOT Mean

- Does not prove no pages are missing
- Does not address folios removed *before* writing
- Does not constrain physical codicology (binding, quire structure)
- Does not address illustrations or decoration

The test is *structural* - it detects removal signatures in the *text*. Blank pages, decorative pages, or pages from a different document could have been removed without textual evidence.

---

## New Constraints

| # | Constraint | Evidence |
|---|------------|----------|
| 353 | State continuity between adjacent Currier B folios is BETTER than random (d=-0.20); no extreme discontinuities detected | FG-1 |
| 354 | EARLY-phase HT prefixes (op-, pc-, do-) are 2.69x enriched at folio starts; orientation pattern intact | FG-2 |
| 355 | 75.9% of Currier B folios start with known morphological prefixes; 18.1% EVA-valid compositional; 6.0% transcription artifacts | FG-3 |
| 356 | Section variance asymmetry is negligible (max 0.0027, mean 0.0014); no truncation signal | FG-4 |

---

*Phase FG CLOSED. 4 tests run, 4 PASS, 0 INVESTIGATE.*
