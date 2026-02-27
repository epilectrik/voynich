# C1348: A Sections Differentiate at Category Level Despite MIDDLE-Level Uniformity

**Tier:** 2
**Scope:** cross-system
**Phase:** A_B_CATEGORY_FLOW (471)

## Constraint

A sections (H, P, T) share the same bridge MIDDLEs (C1136: cosine 0.9997 at MIDDLE level), yet produce significantly different category profiles through differential frequency weighting (chi2=380, V=0.144, perm p=0.001). Section P is THERMAL-heavy (25.1%), section T is FLOW-heavy (22.9%), and section H is STAGING-heavy (26.0%). The section-level category signal propagates cross-system: A-section T's bridge category profile correlates strongly with B-section T (rho=0.85, p=0.016), while A-section H correlates more weakly (rho=0.62, p=0.086).

## Evidence

From a_b_category_flow.py test T3 (bridge MIDDLEs across 3 A sections):

**A-section bridge category profiles:**

| Category | Section H | Section P | Section T |
|----------|----------|----------|----------|
| THERMAL | 10.1% | **25.1%** | 16.5% |
| FLOW | 17.8% | 13.4% | **22.9%** |
| STAGING | **26.0%** | 24.0% | 18.3% |
| TRANSITION | 19.4% | 19.3% | **22.3%** |
| OPERATION | 10.3% | 8.1% | 8.3% |
| MONITORING | 6.4% | 2.4% | 3.4% |
| CONTAINMENT | 5.5% | 5.0% | 5.2% |
| MARKING | 4.7% | 2.6% | 3.1% |

| Metric | Value |
|--------|-------|
| Chi-squared | 380.43 |
| Cramer's V | 0.144 |
| Permutation p | 0.001 |
| JSD(H, P) | 0.025 |
| JSD(H, T) | 0.013 |
| JSD(P, T) | 0.014 |

**Cross-system correlation (shared sections):**

| A section → B section | Spearman rho | p |
|------------------------|-------------|---|
| H → H | 0.619 | 0.086 |
| T → T | **0.851** | **0.016** |

## Interpretation

C1136 establishes that A sections share the same MIDDLEs (section-blind at MIDDLE level). This constraint shows the sections are NOT category-blind: by using shared MIDDLEs at different frequencies, each section creates a distinct category signature. Section P emphasizes THERMAL vocabulary (consistent with P's pharmaceutical character), section T emphasizes FLOW (consistent with T's procedural character), and section H emphasizes STAGING (consistent with H's organizational character).

The strong T→T cross-system correlation (rho=0.85) means A-section T's category emphasis survives the A→B pipeline and shapes B's category landscape in the same section. This is category-level parameterization: A doesn't send different MIDDLEs to different B sections, it sends the same MIDDLEs at different rates, and that rate difference carries category-level information.

## Provenance

- a_b_category_flow.json: test T3
- Extends: C1136 (section-blind MIDDLEs — now shown to be category-differentiated despite MIDDLE uniformity)
- Extends: C918 (A parameterizes B — section-level category flow is a parameterization channel)
- Extends: C1261 (A category coherence — section profiles are distinct expressions of A's category organization)

## Status

CONFIRMED — A sections differentiate at category level (V=0.144, perm p=0.001) despite sharing the same MIDDLEs (C1136). Category signal propagates cross-system for section T (rho=0.85, p=0.016).
