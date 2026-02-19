# C1120: Lifecycle Domain Progression Falsified

**Tier:** 2 (STRUCTURAL INFERENCE)
**Scope:** B
**Phase:** LIFECYCLE_DOMAIN_TEST (Phase 400)
**Extends:** C932 (body vocabulary gradient), C963 (body homogeneity)
**Relates to:** C961 (WORK zone unordered), C964 (free-interior grammar), C1022 (paragraph-neutral macro-dynamics), C1116 (Bio/Stars character)

---

## Statement

Within-paragraph Bio-score shows no lifecycle progression. Mean Spearman rho = -0.068 (Wilcoxon p=0.052, not significant). The slight negative trend is fully explained by C932's spec-to-exec gradient (residualized rho = -0.067, p=0.065, not significant; specification vocabulary is incidentally Bio-enriched). 174 paragraphs tested across 5-test battery, 0/5 support lifecycle hypothesis. Domain character is determined at folio level (ICC=0.393), not by within-paragraph position.

---

## Evidence

### Bio-Score Definition

Per-token Bio-score from 3 components (averaged):
- PREFIX: qo → +1 (Bio-enriched), ok → -1 (Stars-enriched), else → 0
- Kernel: k → +1 (Bio), e → -1 (Stars), both/neither → 0
- Macro-state: CC → +1 (Bio), FQ → -1 (Stars), AXM → +0.5 (Bio-enriched)

Score range [-1, +1]. 12,391 tokens scored. Mean = 0.042, balanced distribution.

### 5-Test Battery

| Test | Type | Verdict |
|------|------|---------|
| T1: Within-paragraph trend | PRIMARY | LIFECYCLE_FALSIFIED_PRIMARY (rho=-0.068, p=0.052) |
| T2: C932-controlled trend | CONTROL | LIFECYCLE_FALSIFIED_CONTROLLED (residual rho=-0.067, p=0.065) |
| T3: Domain mixing stability | DIAGNOSTIC | STABLE_DOMAIN_WITHIN_PARAGRAPH (perm p=0.19) |
| T4: Folio domain purity | SUPPORTING | FOLIO_DETERMINES_DOMAIN (ICC=0.393) |
| T5: REGIME_1 section effect | NULL MODEL | SECTION_PARAMETERIZED, LIFECYCLE_FALSIFIED_CROSS_SECTION |

### T5 Detail: Bio-Section Negative Rho

Bio-section paragraphs within REGIME_1 show significant negative rho (z=-2.63, p=0.006). This is the OPPOSITE of lifecycle prediction and is explained by C932: specification vocabulary (early body lines) is incidentally Bio-enriched (qo-PREFIX, k-kernel), while universal execution vocabulary (late body lines) is domain-neutral.

### Lifecycle Hypothesis — FALSIFIED

The hypothesis that individual B programs span multiple lifecycle domains (grow → harvest → prepare → distill) is rejected. Programs maintain stable domain character inherited from their folio/section context. The only within-paragraph gradient is C932's vocabulary rarity progression, which incidentally correlates with domain character markers.

---

## Provenance

- Phase: 400 (LIFECYCLE_DOMAIN_TEST)
- Script: `phases/LIFECYCLE_DOMAIN_TEST/scripts/lifecycle_domain_test.py`
- Results: `phases/LIFECYCLE_DOMAIN_TEST/results/lifecycle_domain_results.json`
- Expert validation: 0 Tier 0-2 conflicts
- Related: C932, C963, C961, C964, C1022, C1054, C1116
