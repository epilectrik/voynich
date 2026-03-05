# C1401: C325 Completion Gradient is Section Confound

**Tier:** 2 (ESTABLISHED)
**Scope:** B, convergence, section, position
**Phase:** STATE_C_CONVERGENCE_REVISIT (Phase 513)
**Qualifies:** C325 (completion gradient)
**Extends:** C1400 (paragraph state-independent ordering), C324 (section-dependent terminals)
**Relates to:** C074 (dominant convergence), C084 (MONOSTATE), C976 (6-state automaton)

---

## Statement

The folio-position vs STATE-C rate gradient (C325: rho=+0.24, p=0.03) is a **section confound**, not a real positional effect. Within every section, the gradient collapses to zero. The correlation exists because section B (74.5% AXM) occupies later manuscript positions (section-position rho=+0.391, p=0.0003).

### Within-Section Gradients

| Section | N folios | rho | p | Mean AXM |
|---------|----------|------|---|----------|
| B | 20 | -0.012 | 0.960 | 74.5% |
| H | 32 | +0.084 | 0.648 | 58.9% |
| S | 23 | -0.008 | 0.971 | 66.8% |
| C | 5 | +0.600 | 0.285 | 58.2% |

No section shows a significant within-section gradient. The raw corpus-wide signal (rho=+0.226, p=0.041) is entirely driven by section B's later position in the manuscript combined with its higher AXM rate.

C325 is **QUALIFIED**: the finding (rho=+0.24) is factually correct as a raw statistic but misleading as a claim about positional convergence. The gradient describes section composition, not program dynamics.

---

## Falsification Criteria

1. If a section with 20+ folios shows within-section rho > 0.3 with p < 0.01, positional convergence is real within that section
2. If the section-position correlation weakens below rho=0.2 in a different transcriber track, the confound may be track-specific

---

## Method

- 82 B folios classified by section (B/C/H/S/T)
- AXM rate per folio from C976 6-state automaton (state 4 = AXM)
- Raw: Spearman correlation of folio ordinal position vs AXM terminal rate
- Within-section: same correlation computed separately per section
- Section-position: Spearman of section (numerically encoded) vs folio position

**Script:** `phases/STATE_C_CONVERGENCE_REVISIT/scripts/state_c_revisit.py`
**Results:** `phases/STATE_C_CONVERGENCE_REVISIT/results/state_c_revisit.json` (T1)
