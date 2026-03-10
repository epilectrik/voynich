# C1574: Headless ecology is folio-specific not paragraph-specific

**Tier:** 2
**Phase:** 561 (HIERARCHICAL_TRACE_ATTRIBUTION)
**Scope:** B, headless, ecology, folio, paragraph, section, hierarchy, C1398

## Claim

Headless token ecology is primarily folio-specific rather than paragraph-specific. 13/14 headless features have VS_folio|section > VS_section, but paragraphs within a folio share similar headless profiles (T4-C: only 2/55 qualifying folios show significant paragraph-within-folio headless dispersion). The folio sets the headless budget; paragraphs draw from it homogeneously.

This implies headless is a **folio-level infrastructural regime**, not a paragraph-subroutine dial. Paragraph emphasis can vary strongly in thermal/containment/monitoring style, but the kind of infrastructure/meta-operation substrate available is more folio-global.

## Evidence

**T4 hierarchical headless attribution (402 qualifying paragraphs, 14 features):**

- T4-A PASS: 5/14 features have VS_section > 0.05 (hl_rate=0.192, sfx_bifurc=0.136, pseudo_l_frac=0.112, pseudo_d_frac=0.081, pseudo_cpf_frac=0.064). Headless ecology is section-parameterized.
- T4-B PASS: 13/14 features have VS_folio|section > VS_section. Folio-level variance dominates section-level for nearly all features.
- T4-C FAIL: Only 2/55 (3.6%) qualifying folios exceed null+2sigma for paragraph-within-folio headless dispersion (threshold: 30%). Paragraphs within a folio do NOT specialize their headless deployment.
- T4-D PASS: Section S shows within-section headless discrimination z=4.51.

**Strongest folio-level headless features:**
- hl_headed_adj_rate: VS_folio=0.284
- pseudo_d_frac: VS_folio=0.262
- pseudo_l_frac: VS_folio=0.258
- hl_rate: VS_folio=0.257

**Architectural implication:** Paragraph emphasis varies by operational emphasis (C1398 zones), but headless ecology is a program-level (folio-level) setting. The executor must parameterize headless at folio level, not paragraph level.

## Provenance

- T4 script: `phases/HIERARCHICAL_TRACE_ATTRIBUTION/scripts/t4_headless_ecology.py`
- T4 results: `phases/HIERARCHICAL_TRACE_ATTRIBUTION/results/t4_headless_ecology.json`
- Builds on: C1398 (paragraph operational gradient)

## Note: displaced k/t = 0 (PROVISIONAL, pending reconciliation)

T4 found displaced_kt_rate identically zero across all 402 qualifying paragraphs, while displaced_nonkt_rate (e/a/o displaced heads) averages ~20%. This potentially conflicts with C1494-C1497, which describe k/t as enriched in displaced position with transparent-terminal behavior. A reconciliation audit against the original C1494-C1497 parser and token census is needed before this sub-claim can be elevated to Tier 2. The zero result may reflect a stricter operationalization or a parsing mismatch.
