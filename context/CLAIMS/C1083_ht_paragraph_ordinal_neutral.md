### C1083 — HT Density Is Paragraph-Ordinal Neutral

- **Tier:** 2 (ESTABLISHED)
- **Scope:** B (HT density × paragraph ordinal within folio)
- **Phase:** HT_INTERACTION_ARCHITECTURE (2026-02-15)

**Finding:** HT density shows no correlation with paragraph ordinal: Spearman rho=0.018, p=0.69, n=502 paragraphs (≥5 tokens). First-paragraph vs last-paragraph comparison: MW p=0.086, Cohen's d=0.27 (first mean=0.319 vs last mean=0.291 — marginal but not significant). Stratified analysis: 2-paragraph folios rho=-0.12 p=0.50; 3-paragraph rho=-0.08 p=0.68; 4+-paragraph rho=-0.02 p=0.69. All null.

**Interpretation:** Negative control confirmed. HT density is independent of paragraph position within folios, consistent with PSC PARALLEL_PROGRAMS guarantee (C855: paragraphs are independent mini-programs). HT allocation does not systematically increase or decrease across paragraphs, supporting the view that each paragraph operates independently. The marginal first > last difference (d=0.27) does not reach significance and is consistent with sampling noise given the effect sizes in other HT analyses.

**Confirms:** C855 (paragraphs are parallel programs), C861 (LINK/hazard paragraph-ordinal neutral), C1022 (macro-dynamics paragraph-neutral)
**Extends PSC guarantee:** HT allocation now joins LINK density and hazard topology as paragraph-ordinal neutral

**Quantitative:**
- Paragraphs analyzed (≥5 tokens): 502
- Mean HT density: 0.327
- Ordinal correlation: rho=0.018, p=0.69
- First vs last: MW p=0.086, Cohen's d=0.27 (NS)
- All stratified analyses NS
