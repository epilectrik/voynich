# HT_RECONCILIATION Phase

## Objective

Reconcile older Human Track (HT) constraints (C166-C170, C341-C348, C404-C406, C450-C453, C507) with newer UN_COMPOSITIONAL_MECHANICS findings (C610-C621). Test whether HT tokens participate in C475 incompatibility, lane architecture, and A-B routing.

## Key Finding

**HT = UN.** Both labels describe the same population: 4,421 types, 7,042 occurrences (30.5% of B text), defined by exclusion from the 479-type classified grammar. HT tokens are C475-compliant, lane-segregated but lane-indifferent, and do not materially alter routing architecture when removed. C404-C405 (non-operational) confirmed.

## Results Summary

| Test | Verdict | Key Metric |
|------|---------|------------|
| T1: HT/UN Identity | **PASS** | Zero-delta match (4,421 types, 7,042 occ) |
| T2: C475 Graph Participation | **MINIMAL** | 4.6% of HT MIDDLE types in graph (38.5% of occ) |
| T3: C475 Violation Rate | **COMPLIANT** | 0.69% (baseline 0.63%) |
| T4: Lane Distribution | **SEGREGATED** | Chi2=278.71, p=4e-60; OTHER +9.5pp, QO -7.7pp |
| T5: Lane Transitions | **NEUTRAL** | Same-lane rate 37.7% = expected 37.9%, lift=0.994x |
| T6: Coverage Impact | **METRIC-SENSITIVE** | Coverage 31%->43% on removal; routing preserved r=0.85 |
| T7: Folio Distribution | **COMPENSATORY** | Density varies 15.5-47.2%; anti-correlated with coverage r=-0.376 |

## Constraints Established

| # | Name | Verdict |
|---|------|---------|
| C740 | HT/UN Population Identity | HT = UN, zero delta |
| C741 | HT C475 Minimal Graph Participation | 4.6% type coverage, 38.5% occurrence coverage |
| C742 | HT C475 Line-Level Compliance | 0.69% violation rate, comparable to classified baseline |
| C743 | HT Lane Segregation | Radically different lane distribution (p=4e-60) |
| C744 | HT Lane Indifference | No same-lane preference (z=-1.66, ns) |
| C745 | HT Coverage Metric Sensitivity | Coverage inflates on removal; routing preserved (r=0.85) |
| C746 | HT Folio Compensatory Distribution | Non-uniform density; anti-correlated with coverage |

## Constraint Reconciliation

| Old Constraint | Status | Reconciliation |
|----------------|--------|----------------|
| C166 (HT identification) | **CONFIRMED** | = UN definition from C610 (C740) |
| C167-C170 (HT structure) | **ACTIVE** | Lane data (C743) extends structural understanding |
| C341-C348 (HT stratification) | **ACTIVE** | PREFIX disjointness confirmed by lane segregation (C743) |
| C404-C405 (non-operational) | **CONFIRMED** | T3, T5, T6 all consistent with non-operational status |
| C406 (Zipf/hapax) | **CONFIRMED** | 95.4% of HT MIDDLEs not in C475 graph (too rare) |
| C450-C453 (global threading) | **ACTIVE** | T7 compensatory distribution consistent with threading |
| C507 (PP-HT substitution) | **ACTIVE** | T7 compensation consistent with substitution |
| C610-C621 (UN mechanics) | **CONFIRMED** | T1 proves same population, T2-T5 extend characterization |

## Scripts

| Script | Tests | Runtime |
|--------|-------|---------|
| `ht_un_identity.py` | T1 | <10s |
| `ht_c475_compliance.py` | T2, T3 | ~2min (1000 permutations) |
| `ht_lane_participation.py` | T4, T5 | ~2min (1000 permutations) |
| `ht_coverage_impact.py` | T6, T7 | ~3min (coverage matrix) |

## Gating Logic

T1 is a gate: if HT != UN, subsequent tests are invalid. T1 passed with zero delta.
Scripts 2-4 are independent of each other.

## Data Dependencies

| File | Purpose |
|------|---------|
| `scripts/voynich.py` | Transcript, Morphology |
| `phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json` | Classified token set |
| `phases/UN_COMPOSITIONAL_MECHANICS/results/un_census.json` | UN inventory |
| `results/middle_incompatibility.json` | C475 illegal pairs (top 100) |
