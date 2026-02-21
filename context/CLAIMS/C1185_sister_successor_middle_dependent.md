# C1185: Sister-Specific Successor Routing Is MIDDLE-Dependent (Not Universal)

**Tier:** 2
**Scope:** B, sister pairs, transition structure
**Phase:** SISTER_PAIR_MECHANISM (Phase 420)
**Depends on:** C506.b, C1026, C957

## Statement

ch and sh drive marginally different successor class distributions when matched for position and section (global p=0.034, observed mean JSD=0.651 vs null 95th=0.650). However, the effect is concentrated in 5/102 individually significant strata (4.9%). This is MIDDLE-dependent: a few specific MIDDLEs show genuine sister-specific successor routing, but most MIDDLEs treat ch and sh as truly interchangeable in their transition behavior. The 49-class grammar (C121) is NOT challenged — this is token-level routing variation inside fixed class boundaries, consistent with C506.b (intra-class behavioral heterogeneity) and C1003 (pairwise composite, no three-way synergy).

## Evidence

| Metric | Value |
|--------|-------|
| Testable strata (MIDDLE+pos_bin+section) | 102 |
| Observed mean JSD | 0.651 |
| Null mean JSD (500 permutations) | 0.629 |
| Null 95th percentile | 0.650 |
| Global p-value | 0.034 |
| Per-stratum significant (p<0.05) | 5/102 (4.9%) |

## Interpretation

The global significance (p=0.034) sits just above the null 95th percentile, indicating a real but weak effect. The concentration in 5 strata means that for most MIDDLE types, ch and sh genuinely ARE interchangeable in their successor behavior — validating C121's class equivalence at the transition level for ~95% of cases. The 5% where sister identity matters likely involve specific operational contexts where the active-test vs passive-monitor distinction (C929) produces different subsequent operations.

## Provenance

- Phase 420 Test 6: SUCCESSOR_DECOMPOSITION
- Script: `phases/SISTER_PAIR_MECHANISM/scripts/sister_pair_mechanism.py`
- Results: `phases/SISTER_PAIR_MECHANISM/results/sister_pair_mechanism.json` -> test6_successor_decomposition
