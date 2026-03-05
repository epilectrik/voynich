# C1406: Section is REGIME Composition at Paragraph Level

**Tier:** 2 (ESTABLISHED)
**Scope:** B, section, REGIME, paragraph, PREFIX
**Phase:** SECTION_PARAGRAPH_AXM_DRIVERS (Phase 514)
**Extends:** C1404 (section REGIME-dominated), C1405 (paragraph AXM PREFIX-driven)
**Relates to:** C179 (4 stable REGIMEs), C1029 (section-parameterized grammar weights), C1116 (within-REGIME section parameterization)

---

## Statement

At the paragraph level, section membership provides **no independent information** about AXM rate beyond what PREFIX composition already captures. The mechanism is: section determines REGIME composition (V=0.573), REGIME determines which PREFIX profiles are available, and PREFIX profiles directly determine paragraph AXM rate (CV R2=0.736). This three-step chain means section's influence is fully mediated.

### Evidence Chain

1. **Section -> REGIME** (C1404): Section B is 100% REGIME_1. Sections C and T have 0% REGIME_1. V=0.573.

2. **REGIME -> PREFIX availability**: Different REGIMEs have different PREFIX profiles (C545, C551). REGIME_1 is qo-enriched; REGIME_2/4 are more distributed.

3. **PREFIX -> AXM** (C1405): qo_frac and chsh_frac together predict ~70% of paragraph AXM variance.

4. **Section -> AXM (direct)**: Section alone has CV R2 = -0.027 (worse than guessing the grand mean). Section + PREFIX = 0.736 = PREFIX alone.

### Section + REGIME Redundancy

| Model | CV R2 |
|-------|-------|
| Section only | -0.027 |
| REGIME only | -0.092 |
| Section + REGIME | -0.077 |

Neither section nor REGIME has positive predictive power at paragraph level. Both have negative CV R2. Their combination is also negative. This is because within any section or REGIME, paragraph PREFIX profiles vary freely (C1403: folio ICC=0.286, 71% paragraph-level variation).

### What Sections ARE (Revised)

Sections are **REGIME allocation policies**, not grammar variants or material-class divisions:
- Section B = "always REGIME_1" (sustained gentle processing)
- Section H = "mix of REGIMEs 2/3/4" (diverse apparatus)
- Section S = "REGIMEs 1 and 3" (split between gentle and interventional)
- Section T = "REGIMEs 3 and 4" (interventional and precision)

The section label tells you the REGIME mix. The REGIME mix constrains PREFIX availability. PREFIX determines AXM rate. But at the paragraph level, the specific PREFIX profile chosen within those constraints is what matters -- and that choice is paragraph-specific, not section-determined.

---

## Falsification Criteria

1. If within-section, within-REGIME paragraph subgroups show distinct AXM profiles not explained by PREFIX, section carries independent signal
2. If a different paragraph feature (not PREFIX-derived) shows section-specificity in its AXM relationship, section modulates through non-PREFIX channels
3. If the mediation chain (section -> REGIME -> PREFIX -> AXM) is broken at any link by an intervening variable, the chain model is incomplete

---

## Method

- Nested cross-validated regression models comparing section, REGIME, PREFIX, and combinations
- 283 paragraphs across 5 sections and 4 REGIMEs
- Marginal contribution calculated as delta CV R2 between full model and full-minus-section model
- Section-conditioned correlation analysis (C3 interaction test) confirms sign consistency for 6/7 features

**Script:** `phases/SECTION_PARAGRAPH_AXM_DRIVERS/scripts/section_paragraph_drivers.py`
**Results:** `phases/SECTION_PARAGRAPH_AXM_DRIVERS/results/section_paragraph_drivers.json` (tests A5, B6)
