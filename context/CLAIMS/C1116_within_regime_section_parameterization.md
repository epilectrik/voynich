# C1116: Within-REGIME Section Parameterization

**Tier:** 2 (STRUCTURAL INFERENCE)
**Scope:** B
**Phase:** SECTION_INCOMPATIBILITY_TEST (Phase 398)
**Extends:** C1029 (section-parameterized grammar weights), C552 (section role profiles)
**Relates to:** C979 (REGIME weights not topology), C1085 (Bio k-enrichment), C1106 (Stars e-stability)

---

## Statement

Within REGIME_1 (32 folios), Bio and Stars show consistent quantitative distributional divergence across all 6 tested dimensions (class distribution V=0.239, PREFIX profile V=0.153, kernel balance PERMANOVA F=4.16 p=0.019, macro-state V=0.090, vocabulary JSD=0.078, affordance bins V=0.038) but zero qualitative incompatibility (0 robust operator substitution pairs, 0 primary tests reaching INCOMPATIBLE on large-section comparisons). Section parameterization persists within REGIME, confirming C1029 at within-REGIME granularity. Herbal excluded from robust claims (N=2 folios in REGIME_1). Multi-domain interpretation remains Tier 3 — section divergence is consistent with technique variation within a single process family.

---

## Evidence

### REGIME_1 Section Composition
- Bio: 20 folios, 6850 tokens (5324 classified)
- Stars: 10 folios, 5008 tokens (3571 classified)
- Herbal: 2 folios, 203 tokens (unreliable — excluded from robust analysis)
- Cosmo: 0 folios in REGIME_1 (in R2/R3/R4 only)

### 6-Dimension Test Results (within REGIME_1)

| Test | Metric | Value | Threshold | Verdict |
|------|--------|-------|-----------|---------|
| A: Operator Substitution | Robust substitution pairs | 0 | ≥3 for INCOMP | WEAKLY (B-S V=0.239) |
| B: Vocabulary Discontinuity | B-S JSD sigma | 1.99 | >2.0 for INCOMP | WEAKLY |
| C: Kernel Balance | PERMANOVA p | 0.019 | <0.01 for INCOMP | WEAKLY |
| D: Macro-State Distribution | Cramer's V | 0.090 | >0.10 for INCOMP | WEAKLY |
| E: PREFIX Profile | Cramer's V | 0.153 | >0.10 for INCOMP | INCOMP (supporting) |
| F: Affordance Bins | Cramer's V | 0.038 | >0.10 for INCOMP | WEAKLY (supporting) |

### Key Distributional Differences (B vs S within REGIME_1)

| Dimension | Bio | Stars | Interpretation |
|-----------|-----|-------|----------------|
| AXM fraction | 74.4% | 67.2% | Bio more energy-intensive (C1084) |
| FQ fraction | 13.1% | 20.6% | Stars more monitoring-intensive (C1107) |
| CC fraction | 5.9% | 3.3% | Bio more control-change-dense |
| qo PREFIX | 23.7% | 17.8% | Bio uses more energy selectors (C911) |
| ok PREFIX | 5.0% | 8.9% | Stars uses more infrastructure setup |
| k kernel | 34.3% | 27.5% | Bio k-enriched (C1085) |
| e kernel | 56.8% | 65.9% | Stars e-enriched (C1106) |

### Overall Verdict: SECTION_DIFFERENTIATED

Combined primary score: 4/8 (4 WEAKLY, 0 INCOMPATIBLE)
Combined support score: 3/4 (1 INCOMPATIBLE, 1 WEAKLY)

The consistency of weak effects across all dimensions confirms that section parameterization (C1029) operates at within-REGIME granularity. The absence of any qualitative incompatibility (no operator substitution, no topology change) means these differences are technique variation within a shared grammar, not evidence of fundamentally different process domains.

---

## Interpretation

Bio and Stars programs within the same REGIME share identical grammar topology but tune their weight distributions differently — Bio emphasizes energy-channel operations (qo, k, high AXM) while Stars emphasizes monitoring/stability operations (ok/ot, e, high FQ, high LINK per C1107). In the Brunschwig framework (Tier 3), this maps to balneum mariae (water-bath: sustained even heating) versus direct-fire techniques (close monitoring required). Both are thermal process control techniques using the same grammar, not fundamentally different process domains.

The multi-domain interpretation (Tier 3: sections represent different operational domains beyond thermal processing) is not supported by this test. Section divergence within REGIME is quantitative weight modulation, exactly as C979 and C1029 predict.

---

## Provenance

- Phase: 398 (SECTION_INCOMPATIBILITY_TEST)
- Script: `phases/SECTION_INCOMPATIBILITY_TEST/scripts/section_incompatibility_test.py`
- Results: `phases/SECTION_INCOMPATIBILITY_TEST/results/section_incompatibility_results.json`
- Expert validation: Expert-advisor confirmed 0 Tier 0-2 conflicts, recommended SECTION_DIFFERENTIATED over INCOMPATIBLE
- Related: C979, C1029, C552, C1085, C1106, C1107, C1047, C1084
