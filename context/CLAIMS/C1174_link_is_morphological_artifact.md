# C1174: LINK Is Morphological Artifact, Not Functional Layer

**Tier:** 2
**Scope:** B, LINK, synthesis
**Phase:** LINK_FUNCTIONAL_ARCHITECTURE (Phase 418)
**Depends on:** C609, C805, C808, C1170, C1171, C1172, C1173

## Statement

The LINK population (`ol` substring, 13.2% of B, 3,047 tokens) is a morphological artifact, not a functional layer. A 5-test battery demonstrates: (1) vocabulary is strongly stratified by role (V=0.404, C1170); (2) behavior is role-dominant with no cross-role substrate effect (0/4 consistent, C1171); (3) BIO's 2× excess is targeted at SPAN-position tokens, not uniformly enriched (EN_SPAN 4.65×, C1172); (4) macro-automaton dynamics show passive participation (1.09× boundary enrichment, CC-dominated occupancy); (5) boundary enrichment does not correlate with divergence measures (entry rho=-0.059, exit rho=-0.151, both NS, C1173). The `ol` substring is a morphological component recruited differently by each grammatical role — CC uses it as standalone operator, AX uses it as prefix, EN uses it in MIDDLE/SPAN positions. There is no unified LINK functional substrate.

## Evidence

### 5-Test Battery Summary
| Test | Verdict | Key Metric |
|------|---------|------------|
| T1: Vocabulary Stratification | STRATIFIED | V=0.404, chi2=1493 |
| T2: Cross-Role Consistency | ROLE_DOMINANT | 0/4 consistent, JSD≈baseline |
| T3: Section Decomposition | BIO_TARGETED | EN_SPAN 4.65×, MIDDLE depleted |
| T4: Macro-Automaton Dynamics | PASSIVE | 1.09× boundary, CC=22.4% |
| T5: Boundary Architecture | ENRICHED_PASSIVE | rho=-0.059/-0.151, both NS |

### Synthesis Logic
| T1 | T2 | T4 | → Overall |
|----|----|-----|----------|
| STRATIFIED | ROLE_DOMINANT | PASSIVE | **LINK_MORPHOLOGICAL_ARTIFACT** |

### What `ol` Actually Does in Each Role
| Role | How `ol` participates | ol_position | Tokens |
|------|-----------------------|-------------|--------|
| CC | IS the entire token (standalone `ol`) | MIDDLE | 421 |
| AX | Prefix component (leads into AX morphology) | PREFIX (59%) | 799 |
| EN | Within or crossing MIDDLE boundaries | MIDDLE/SPAN/SUFFIX | 578 |
| FQ | Part of specific FQ tokens (e.g., `otol`) | MIDDLE | 71 |
| FL | Rare presence in MIDDLE | MIDDLE | 10 |
| UN | High diversity, all positions | ALL | 1,168 |

## Interpretation

The prior characterization of LINK as "monitoring/waiting phases" (C366, C609) reflected the aggregate behavior of a morphologically diverse population whose behavioral uniformity was an artifact of averaging across roles. When decomposed by role and ol_position, no unified LINK function emerges. The `ol` substring is a productive morphological element that the grammar uses differently in different contexts:

- As CC operator `ol`: a specific instruction (C874: "continue" function)
- As AX prefix: modifying auxiliary tokens (ol+keedy, ol+chedy, ol+aiin)
- As EN component: appearing within energy operator morphology

BIO's LINK excess is specifically driven by morphological complexity (SPAN tokens) rather than functional LINK deployment. The boundary enrichment (C805) reflects the positional preferences of the specific roles that contain `ol`, not a LINK-specific boundary function.

## Provenance

- Phase 418: LINK_FUNCTIONAL_ARCHITECTURE (5-test battery)
- Script: `phases/LINK_FUNCTIONAL_ARCHITECTURE/scripts/link_functional_architecture.py`
- Results: `phases/LINK_FUNCTIONAL_ARCHITECTURE/results/link_functional_architecture.json` → synthesis
