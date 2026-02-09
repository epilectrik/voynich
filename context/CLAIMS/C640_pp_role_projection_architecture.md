# C640: PP Role Projection Architecture

**Tier:** 2 | **Status:** CLOSED | **Scope:** CROSS_SYSTEM | **Source:** A_TO_B_ROLE_PROJECTION

## Statement

> **Aggregation Note (2026-01-30):** This constraint analyzes PP MIDDLE projection to B roles.
> PP MIDDLE inventories derive from line-level analysis. Per C885, the operational unit for
> A-B vocabulary correspondence is the A FOLIO (114 units, 81% coverage).

Projecting A's 404 PP (Pipeline-Participating) MIDDLEs onto B's 49-class, 5-role instruction system yields **89 matches (22.0%)** because B's classified vocabulary contains only 90 distinct MIDDLEs across 480 token types. AZC-Mediated (235) and B-Native (169) PP populations show **significantly different role profiles**: B-Native matched PP MIDDLEs are 100% ENERGY_OPERATOR-dominant (8/8), while AZC-Mediated distribute across AUXILIARY (53.1%), ENERGY_OPERATOR (40.7%), FLOW_OPERATOR (4.9%), and FREQUENT_OPERATOR (1.2%). PP role distribution **differs from B token shares** (chi2=42.37, p<0.0001): AUXILIARY is over-represented and CORE_CONTROL/FREQUENT_OPERATOR are under-represented among PP MIDDLEs.

## Evidence

### Match Rate

| Metric | Value |
|--------|-------|
| PP MIDDLEs | 404 |
| Matched to B classes | 89 (22.0%) |
| Unmatched | 315 (78.0%) |
| B unique MIDDLEs (via parser) | 90 |

The low match rate reflects B's compositional vocabulary: 480 token types use only 90 distinct MIDDLEs. Most PP MIDDLEs from A form B tokens not captured in the 49-class cosurvival system.

### Population Role Comparison (Matched PP Only)

| Role | AZC-Med (n=81) | B-Native (n=8) | MW p |
|------|----------------|----------------|------|
| AX | 53.1% | 0.0% | 0.0013 * |
| CC | 0.0% | 0.0% | 1.0 |
| EN | 40.7% | 100.0% | 0.0006 * |
| FL | 4.9% | 0.0% | NS |
| FQ | 1.2% | 0.0% | NS |

Two roles differ significantly (AX and EN). B-Native PP MIDDLEs are exclusively EN-dominant, while AZC-Med PP MIDDLEs span multiple roles.

### Role Clustering (Chi-Squared GOF)

| Role | Observed | Expected (from B shares) |
|------|----------|--------------------------|
| AX | 43 | 21.4 |
| CC | 0 | 5.7 |
| EN | 41 | 40.0 |
| FL | 4 | 6.0 |
| FQ | 1 | 16.0 |

Chi2=42.37, df=4, p<0.0001. PP MIDDLEs do NOT uniformly sample B roles.

### Frequency Confound

AZC-Mediated PP MIDDLEs have dramatically higher B-side frequency (median=9, mean=88.9) vs B-Native (median=2, mean=4.4), MW p<0.0001. This confounds population comparisons — differences in role, suffix, and REGIME profiles may partly reflect frequency rather than pathway identity.

### Role Specificity

- Mean role entropy: 0.566 (MODERATE)
- Single-role PP: 47 (52.8%), multi-role: 42 (47.2%)
- B-Native: 100% single-role; AZC-Med: 48.1% single-role (Fisher p=0.0061)

## Interpretation

The PP-to-B role projection establishes that A's shared vocabulary is **non-uniformly distributed** across B's role architecture: AUXILIARY and ENERGY_OPERATOR dominate, while CORE_CONTROL and FREQUENT_OPERATOR are virtually absent. This is consistent with PP MIDDLEs encoding A-record elements that participate primarily in EN and AX B-programs, rather than in CC kernel operations or FQ frequent-operator patterns.

The B-Native population (169 MIDDLEs, 8 matched) appears to be exclusively EN-associated, suggesting these MIDDLEs enter B without AZC mediation precisely because they serve a narrow EN execution role. AZC-Mediated MIDDLEs show broader role participation, consistent with AZC's function as a multi-pathway routing mechanism (C498).

The 22% match rate is a fundamental limitation: 78% of PP MIDDLEs have no B-class assignment, meaning downstream analyses operate on a sparse projection. All population comparisons are further confounded by dramatic frequency differences.

## Extends

- **C498**: AZC-Med/B-Native bifurcation confirmed (235/169 exact match)
- **C498.a**: B-Native population identified as exclusively EN-dominant
- **C121**: 49 instruction classes confirmed; 90 unique MIDDLEs across 480 types
- **C506**: PP composition doesn't affect class survival — now shown at role level

## Related

C121, C384, C498, C506, C560, C581

## Provenance

- **Phase:** A_TO_B_ROLE_PROJECTION
- **Date:** 2026-01-26
- **Script:** pp_role_foundation.py
