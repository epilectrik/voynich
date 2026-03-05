# C1407: PREFIX-AXM Relationship Universal Across Sections

**Tier:** 2 (ESTABLISHED)
**Scope:** B, PREFIX, AXM, section, universality
**Phase:** SECTION_PARAGRAPH_AXM_DRIVERS (Phase 514)
**Extends:** C1405 (paragraph AXM PREFIX-driven), C1023 (PREFIX routing sole load-bearing)
**Relates to:** C821 (line syntax REGIME invariance), C1012 (PREFIX positive channeling), C979 (REGIME modulates weights not topology)

---

## Statement

The PREFIX-to-AXM relationship has **consistent sign and direction across all sections**. Of 7 tested features (qo_frac, chsh_frac, bare_frac, k_frac, e_frac, thermal_frac, transition_frac), 6 show consistent correlation signs across all sections. Only `transition_frac` shows sign inconsistency (positive in B/C, near-zero in H/S). This extends the universality findings of C821 (line syntax invariant across REGIMEs) and C979 (REGIME modulates weights not topology) to the paragraph-section interaction.

### Section-Specific Correlations (C3 Interaction Test)

| Feature | B | S | H | C | Consistent? |
|---------|---|---|---|---|-------------|
| qo_frac | + | + | + | + | YES |
| chsh_frac | + | + | + | + | YES |
| bare_frac | - | - | - | - | YES |
| k_frac | + | + | + | + | YES |
| e_frac | + | + | + | + | YES |
| thermal_frac | + | + | + | + | YES |
| transition_frac | + | ~0 | ~0 | + | NO |

(Section T omitted due to insufficient paragraphs n=2)

### Implications

1. **Universal grammar**: The way PREFIX composition maps to macro-state dynamics does not change between sections. A paragraph with high qo_frac will be AXM-dominant regardless of whether it is in section B, H, S, or C.

2. **Section modulates magnitude, not direction**: While the absolute AXM rates differ by section (C1404), the relative effect of PREFIX shifts is the same. This parallels C979's finding at the folio level.

3. **No section-specific exceptions**: The single inconsistency (transition_frac) involves a feature with weak overall signal, not a reversal of a strong predictor.

4. **Design principle**: Section, REGIME, and paragraph PREFIX represent different levels of the same hierarchy. Section sets the envelope (REGIME mix), REGIME constrains the PREFIX palette, but within those constraints the PREFIX-to-dynamics mapping is universal.

---

## Falsification Criteria

1. If a major PREFIX channel (qo, ch/sh, BARE) shows a significant sign reversal in any section with adequate sample size, universality fails
2. If section-specific regression coefficients differ by more than 2x for a major predictor, magnitude invariance fails
3. If an interaction term (section x PREFIX) significantly improves CV R2 beyond the additive model, the additive universality assumption is too strong

---

## Method

- Section-stratified Spearman correlations between 7 morphological features and paragraph AXM rate
- 283 paragraphs: B=69, S=119, H=73, C=20, T=2
- Sign consistency evaluated qualitatively (all positive or all negative across sections with n>10)
- Section T excluded from interaction analysis due to n=2

**Script:** `phases/SECTION_PARAGRAPH_AXM_DRIVERS/scripts/section_paragraph_drivers.py`
**Results:** `phases/SECTION_PARAGRAPH_AXM_DRIVERS/results/section_paragraph_drivers.json` (test C3)
