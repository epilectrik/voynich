# C1272: AZC Mediates Bridge-Dark Category Sorting

**Tier:** 2
**Scope:** AZC, A->B
**Phase:** AZC_CATEGORY_SCATTERSHOT (Phase 453)
**Date:** 2026-02-24

## Statement

Bridge and dark pipeline MIDDLEs occupy different AZC positional zones. Chi-squared=33.45, V=0.117, p<0.001. Bridge MIDDLEs (77 in AZC, 2,139 tokens) are R-dominated (47.5%); dark pipeline MIDDLEs (144 in AZC, 312 tokens) are more S-shifted (26.9%). After controlling for bridge/dark status: category still predicts zone within bridge (chi2=50.9, V=0.089, p=0.0003) but NOT within dark (chi2=26.2, V=0.167, p=0.198). AZC's positional structure sorts bridge vocabulary by category but not dark vocabulary.

## Architecture

- **AZC is the sorting mechanism.** C1264 established that bridge and dark MIDDLEs have divergent category profiles. C1272 shows WHERE this sorting happens: AZC positional zones partition bridge vocabulary by category, which then propagates to B via the grammar channel.
- **Bridge = category-sorted, dark = category-undifferentiated in AZC.** Bridge MIDDLEs show category-zone coupling (p=0.0003), meaning their positional placement in AZC is category-aware. Dark MIDDLEs do not (p=0.198), consistent with dark pipeline operating through the identification channel (C1140) where category-zone coupling is unnecessary.
- **Connects C1264 to C468.** The bridge/dark category divergence (C1264, V=0.441) is mediated by AZC zone assignment, which then produces the 28x escape rate difference (C468) via vocabulary availability in B.

## Key Findings

| Metric | Value |
|--------|-------|
| Bridge in AZC | 77/85 (90.6%) |
| Dark in AZC | 144/300 (48.0%) |
| Bridge zone distribution | R=47.5%, C=23.1%, P=14.9%, S=14.5% |
| Dark zone distribution | R=44.2%, C=16.3%, P=12.5%, S=26.9% |
| Chi-squared (overall) | 33.45 |
| Cramer's V | 0.117 |
| Partial (bridge, category->zone) | p=0.0003 |
| Partial (dark, category->zone) | p=0.198 (null) |

## Provenance

- Extends C1264 (bridge/dark category divergence) with sorting mechanism
- Extends C468 (28x escape rate) with category-zone mediation
- Extends C1140 (four-way partition) -- bridge vs dark channel behavior in AZC
