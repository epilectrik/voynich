# C1573: Paragraph emphasis distributions recover within-section folio specificity

**Tier:** 2
**Phase:** 561 (HIERARCHICAL_TRACE_ATTRIBUTION)
**Scope:** B, paragraph, distribution, folio, within-section, specificity, emphasis, EMD, C1398, C1570, domain, section

## Claim

Paragraph-level domain emphasis DISTRIBUTIONS (6D HEAD-domain vectors per paragraph) recover within-section folio specificity that folio-average features failed to capture (C1570). The continuous paragraph emphasis cloud per folio is geometrically distinctive within sections, confirmed by Earth Mover's Distance at z=6.21 (S), 5.06 (H), 2.34 (B) against paragraph-shuffle null.

Line-level distributional fingerprints (15D profiles) also carry folio-specific information via within-folio variance compression (B1 variance ratio PASS in all 3 sections).

## Evidence

**T2: Paragraph distributions (283 qualifying paragraphs, 500 permutations):**
- C1 Continuous EMD (primary): ALL 3 sections PASS (S z=6.21, H z=5.06, B z=2.34)
- C2 Zone Inventory: ALL 6 tests PASS (direct + unsupervised, all p < 0.05)
- C3 Paragraph Ecology: 18/18 tests PASS
- C4 Continuous Variance: 0/3 FAIL (folios do NOT differ in internal paragraph dispersion)
- Overall: PASS (3/4 sub-tests)

**T3: Line distributions (2,328 qualifying lines, 300 permutations):**
- B1 Variance Ratio: PASS (3/3 sections; S: 7/15, H: 13/15, B: 4/15 features with ratio < 0.90)
- B2 Energy Distance: FAIL (S: 28.5% significant, H: 7.7%, B: 2.1%; aggregate 12.1% < 15%)
- Overall: PASS (1/2 sub-tests)

**C1398 gradient interpretation confirmed:** ARI between direct C1398 zone assignment and unsupervised k-means = 0.2867 (below 0.3). The paragraph operational space is a continuous gradient with weak clustering (silhouette 0.113), not discrete types. The distributional tests succeed because they respect this continuous geometry (EMD on the full 6D cloud) rather than forcing discrete zone assignments.

**Section-specific patterns:** Section S shows strongest paragraph-level folio differentiation (z=6.21). Section H shows strongest line-level differentiation (13/15 B1 features). Section B is weakest but still passes T2 primary test (z=2.34).

## Provenance

- T2 script: `phases/HIERARCHICAL_TRACE_ATTRIBUTION/scripts/t2_paragraph_distributions.py`
- T3 script: `phases/HIERARCHICAL_TRACE_ATTRIBUTION/scripts/t3_line_distributions.py`
- Results: `phases/HIERARCHICAL_TRACE_ATTRIBUTION/results/t2_paragraph_distributions.json`, `t3_line_distributions.json`
- Corrects/extends: C1570 (folio-average FAIL is resolution-dependent, not absolute)
- Builds on: C1398 (paragraph operational gradient), C1399 (paragraph zone inertia)
