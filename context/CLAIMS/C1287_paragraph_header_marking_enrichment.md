# C1287: Paragraph Headers are MARKING-Enriched

**Tier:** 2
**Scope:** B
**Phase:** CATEGORY_MECHANISM_DECOMPOSITION (Phase 455)
**Date:** 2026-02-24

## Statement

Paragraph headers (first token, par_initial=True) have distinct category profiles from paragraph bodies. MARKING 2.44x enriched in headers (18.3% vs 7.5%), STAGING 1.45x enriched (18.5% vs 12.7%), THERMAL 0.46x suppressed (11.0% vs 24.0%). Chi2=128.0, V=0.075, p<0.001. N=498 header tokens, 22,503 body tokens.

## Architecture

- **Layered paragraph specification.** Headers specify marking/adjustment operations; bodies execute thermal/flow operations. This contrasts with C1283 (line entries are THERMAL-enriched): the paragraph-level and line-level entry mechanisms differ.
- **Three-level hierarchy:**
  - Paragraph header: MARKING/STAGING specification (what to annotate/set up)
  - Line entry: THERMAL specification (what thermal parameters to apply)
  - Line body: FLOW/TRANSITION execution (operational execution)
- **MARKING role clarified.** MARKING vocabulary (mark, flag, note, adjust, hazard, link) concentrates at paragraph boundaries, functioning as setup annotation before operational execution.
- **Extends C893.** C893 established HT enrichment at paragraph headers. C1287 shows this co-occurs with MARKING enrichment, suggesting HT tokens at headers serve marking/annotation functions.

## Provenance

- Extends C893 (paragraph header HT enrichment) with category mechanism
- Contrasts C1283 (line entry THERMAL enrichment) -- different levels, different categories
- Extends C1253 (paragraph position modulates category)
