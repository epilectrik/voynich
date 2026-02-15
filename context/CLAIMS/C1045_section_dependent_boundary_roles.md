# C1045: Section-Dependent Boundary Role Composition

**Tier:** 2 (STRUCTURAL INFERENCE)
**Scope:** B
**Phase:** SECTION_PARAMETERIZED_LINE_GRAMMAR (Phase 365)
**Extends:** C959 (opener is role marker), C960 (boundary vocabulary is open)
**Relates to:** C1029 (section-parameterized grammar), C552 (section-specific role profiles), C964 (boundary-constrained free interior)

---

## Statement

Line opener and closer role distributions are section-dependent:

| Position | Chi-squared | p-value | Cramer's V |
|----------|------------|---------|------------|
| Opener | 74.67 | <0.0001 | 0.103 |
| Closer | 56.15 | <0.0001 | 0.090 |

Sections draw from different role mixtures at line boundaries while preserving the universal boundary-constrained free-interior architecture (C964). The effect is moderate (V=0.09-0.10) — sections modulate boundary composition, not the boundary mechanism itself.

---

## Evidence

- 4 sections x 5 roles contingency tables for openers and closers
- All sections contribute >= 20 lines
- Both openers and closers pass p < 0.001 AND V >= 0.05
- Opener effect slightly stronger than closer effect (V=0.103 vs 0.090)

---

## Interpretation

C959 established that the opener token signals the role mix for the line. C1045 refines this: the opener's role is drawn from a section-specific distribution. Different sections preferentially start lines with different roles, reflecting the section's processing emphasis. Similarly for closers — the exit role varies by section context. This is the boundary-specific manifestation of C1029's general section parameterization.

---

## Method

- Per-section role counts at position 0 (opener) and position N-1 (closer)
- Chi-squared contingency test + Cramer's V
- Zero-count columns removed before test
- Threshold: p < 0.001 AND V >= 0.05

**Script:** `phases/SECTION_PARAMETERIZED_LINE_GRAMMAR/scripts/section_line_grammar.py`
**Results:** `phases/SECTION_PARAMETERIZED_LINE_GRAMMAR/results/section_line_grammar.json`
