# SMALL_ROLE_ANATOMY Phase

**Phase:** SMALL_ROLE_ANATOMY
**Date:** 2026-01-26
**Constraints:** C581-C592 (12 new)
**Status:** COMPLETE

---

## Goal

Exhaustively characterize the three small operational roles in Currier B — **CC** (Core Control), **FL** (Flow), **FQ** (Frequent) — completing the five-role taxonomy. Resolve census discrepancies, establish MIDDLE inventories, test internal class structure, analyze hazard participation, introduce the suffix dimension, and produce a unified five-role comparison.

---

## Key Findings

### 1. Census Resolution

All three census discrepancies resolved:

| Role | Definitive Classes | Tokens | % of B | Note |
|------|--------------------|--------|--------|------|
| CC | {10, 11, 12, 17} | ~1,023 | 4.4% | C560 places Class 17 in CC; Class 12 ghost (0 tokens per C540) |
| FL | {7, 30, 38, 40} | 1,078 | 4.7% | BCSC undercounted at 2; ICC gives 4 |
| FQ | {9, 13, 14, 23} | 2,890 | 12.5% | C559 used wrong set {9,20,21,23}; Classes 20,21 are AX per C563 |

**Important:** Scripts used ICC's CC={10,11,12} (735 tokens). C560 (validated Tier 2) establishes Class 17 as CC, giving CC={10,11,12,17} with ~1,023 tokens. C581 reflects the corrected census.

### 2. Pipeline Purity

All roles are 100% PP (pipeline-participating) at the MIDDLE level. CC has 3 MIDDLEs, FL has 17, FQ has 19 — all classified as PP. Zero RI or B-exclusive MIDDLEs in any role. Combined with EN (100% PP per C575) and AX (98.2% PP per C567), pipeline vocabulary dominates all of Currier B.

### 3. Cross-Role MIDDLE Sharing (Jaccard Matrix)

|    | CC    | EN    | FL    | FQ    | AX    |
|----|-------|-------|-------|-------|-------|
| CC | 1.000 | 0.031 | 0.053 | 0.048 | 0.052 |
| EN | 0.031 | 1.000 | 0.125 | 0.297 | 0.402 |
| FL | 0.053 | 0.125 | 1.000 | 0.333 | 0.230 |
| FQ | 0.048 | 0.297 | 0.333 | 1.000 | 0.328 |
| AX | 0.052 | 0.402 | 0.230 | 0.328 | 1.000 |

- CC is maximally isolated (Jaccard < 0.06 with all roles)
- EN-AX highest sharing (0.402), confirming C567
- FL-FQ moderate sharing (0.333)
- EN has 29 exclusive MIDDLEs, AX has 17, FL has 3, CC and FQ have 0

### 4. Suffix Role Selectivity (New Dimension)

Chi-square = 5063.2, p < 1e-300. Three suffix strata:

| Stratum | Roles | Suffix Types | Bare % |
|---------|-------|-------------|--------|
| SUFFIX_RICH | EN | 17 | 39.0% |
| SUFFIX_MODERATE | AX | 19 | 62.3% |
| SUFFIX_DEPLETED | FL, FQ | 1-2 | 93-94% |
| SUFFIX_FREE | CC | 0 | 100.0% |

EN-AX share suffix vocabulary (Jaccard = 0.800). CC/FL/FQ are suffix-isolated.

### 5. Internal Structure Verdicts

| Role | Verdict | KW Significant | Mean JS |
|------|---------|---------------|---------|
| CC | GENUINE_STRUCTURE (2 active + 1 ghost) | 75% | 0.032 |
| FL | GENUINE_STRUCTURE (hazard/safe split) | 100% | 0.039 |
| FQ | GENUINE_STRUCTURE (4-way) | 100% | 0.014 |
| EN | DISTRIBUTIONAL_CONVERGENCE | — | — |
| AX | COLLAPSED (positional gradient) | — | — |

All three small roles have genuine internal structure — a striking contrast with the large roles.

### 6. FL Hazard-Safe Split

FL divides into two genuine subgroups:

| Subgroup | Classes | Position (mean) | Final Rate | Hazard Role |
|----------|---------|-----------------|------------|-------------|
| Hazard | {7, 30} | 0.55 (medial) | 12.3% | Source-biased (4.5x) |
| Safe | {38, 40} | 0.81 (final) | 55.7% | Non-hazardous |

Mann-Whitney: position p = 9.4e-20, final rate p = 7.3e-33. FL initiates forbidden transitions far more than it receives them.

### 7. FQ 4-Way Differentiation

| Class | Tokens | Character | Position | Special |
|-------|--------|-----------|----------|---------|
| 9 | 630 | aiin/o/or | Medial | Self-chaining, prefix-free |
| 13 | 1,191 | ok/ot-prefixed | Medial | Largest FQ class, 16% suffixed |
| 14 | 707 | ok/ot-prefixed | Medial | Distinct from 13 (p=1.6e-10) |
| 23 | 362 | d/l/r/s/y/am/dy | Final-biased | Morphologically minimal |

### 8. CC Positional Dichotomy

Class 10 (daiin): initial-biased, mean position 0.413, 27.1% line-initial
Class 11 (ol): medial, mean position 0.511, 5.0% line-initial
Mann-Whitney p = 2.8e-5. Complementary control primitives.

---

## Five-Role Complete Taxonomy

| Role | Classes | Tokens | % of B | PP% | Suffix | Hazard | Structure |
|------|---------|--------|--------|-----|--------|--------|-----------|
| EN | 18 | 7,211 | 31.2% | 100% | Rich (17 types) | Target | CONVERGENCE |
| AX | 19 | ~3,852 | 16.6% | 98.2% | Moderate (19 types) | None | COLLAPSED |
| FQ | 4 | 2,890 | 12.5% | 100% | Depleted (1 type) | Mixed | GENUINE |
| FL | 4 | 1,078 | 4.7% | 100% | Depleted (2 types) | Source | GENUINE |
| CC | 4 | ~1,023 | 4.4% | 100% | Free (0 types) | None | GENUINE |

AX = 19 classes: Class 17 reassigned to CC per C560; Class 14 confirmed FQ per ICC + behavioral evidence (C583).

---

## C559 Correction

C559 (FREQUENT Role Structure) used incorrect membership {9, 20, 21, 23}. Classes 20 and 21 are AX per C563 (AX_FINAL subgroup). Correct FQ membership is {9, 13, 14, 23} per ICC. C559 is marked **SUPERSEDED** by C583 and C587. Downstream constraints C550, C551, C552, C556 are flagged for re-verification (C592).

---

## Scripts

| Script | Purpose | Output |
|--------|---------|--------|
| sr_census_and_inventory.py | Census reconciliation, MIDDLE inventory, Jaccard matrix | sr_census.json |
| sr_feature_matrix.py | Per-class distributional profiles (5 dimensions) | sr_features.json |
| sr_suffix_analysis.py | Suffix patterns across all 5 roles | sr_suffix_analysis.json |
| sr_hazard_anatomy.py | Hazard participation for FL and FQ | sr_hazard_anatomy.json |
| sr_internal_structure.py | Within-role differentiation tests | sr_internal_structure.json |
| sr_synthesis.py | Unified synthesis and constraint enumeration | sr_synthesis.json |

Execution order: Scripts 1-3 (parallel) → Scripts 4-5 (parallel) → Script 6.

---

## Constraints Produced

| # | Name | Key Finding |
|---|------|------------|
| C581 | CC Definitive Census | CC={10,11,12,17}, 1023 tokens, Class 12 ghost |
| C582 | FL Definitive Census | FL={7,30,38,40}, 1078 tokens, BCSC 2→4 |
| C583 | FQ Definitive Census | FQ={9,13,14,23}, 2890 tokens, supersedes C559 |
| C584 | Near-Universal Pipeline Purity | CC/EN/FL/FQ 100% PP; AX 98.2% |
| C585 | Cross-Role MIDDLE Sharing | EN-AX Jaccard 0.402; CC isolated |
| C586 | FL Hazard-Safe Split | {7,30} hazard vs {38,40} safe; p=9.4e-20 |
| C587 | FQ Internal Differentiation | 4-way genuine structure, 100% KW |
| C588 | Suffix Role Selectivity | Chi2=5063.2; three suffix strata |
| C589 | Small Role Genuine Structure | CC/FL/FQ all GENUINE vs AX COLLAPSED, EN CONVERGENCE |
| C590 | CC Positional Dichotomy | daiin initial vs ol medial, p=2.8e-5 |
| C591 | Five-Role Complete Taxonomy | 49 classes → 5 roles, complete partition |
| C592 | C559 Membership Correction | C559 SUPERSEDED; downstream flags |

All constraints validated by expert-advisor at Tier 2. Expert corrections applied: C584 title changed to "Near-Universal" (acknowledging AX 98.2% per C567), C589 language tightened, C559 marked SUPERSEDED (not just annotated).

---

## BCSC Update Recommendations

1. EN class_count: 11 → 18 (C573)
2. FL class_count: 2 → 4 (C582)
3. FQ membership: {9,13,14,23} not {9,20,21,23} (C583)
4. CC: add Class 12 ghost note, Class 17 per C560 (C581)
5. Add suffix dimension to role profiles (C588)
6. Add hazard direction: FL initiates, EN receives (C586)
7. Internal structure: small roles GENUINE, large roles COLLAPSED/CONVERGENCE (C589)
