# C1736: Within-Folio THERMAL-Safety Paragraph Gradient

**Tier:** 2
**Phase:** BRUNSCHWIG_1512_BLIND_PREDICTION (Phase 598)
**Scope:** B, paragraph, THERMAL, safety, e->y, ke-depth

## Finding

Within individual folios, paragraphs with higher THERMAL category fraction show:

1. **Higher e->y safe pathway rate** (Spearman rho=0.155, p=0.0015, n=418 paragraphs across 46 folios)
2. **Deeper ke engagement** (Spearman rho=0.303, p<0.0001, n=418 paragraphs across 46 folios)
3. **No systematic ordinal gradient** (mean rho=-0.006, t-test p=0.919) — confirming C1399/C1400 paragraph ordering null

## Method

Within-folio deviation analysis: for each folio, compute paragraph means for THERMAL fraction, e->y fraction, and mean e-depth. Subtract folio means to get deviations. Correlate deviations across all paragraphs. This controls for folio-level effects by construction — every comparison is within a single folio.

## Significance

This result is immune to section confounds (within-folio comparisons cannot be confounded by section). It confirms that the 1512 Brunschwig alignment operates at paragraph resolution: thermal operations deploy more safety infrastructure (e->y) and engage the kernel more deeply (ke-depth), exactly as predicted by the 1512's finding that thermal procedures require more safety precautions and more elaborate kernel processing.

The H3 result (rho=0.303, p<0.0001) is the single strongest finding from Phase 598.

## What This Does NOT Show

The paragraph ordering null (H1) confirms C1399/C1400: there is no systematic first-to-last gradient. Paragraphs are parallel subroutines, not sequential steps. The THERMAL->safety association is about paragraph emphasis, not temporal ordering within a folio.

## Key Metrics

- H2 (THERMAL->e->y): rho=0.155, p=0.0015, n=418 paragraphs, 46 folios
- H3 (THERMAL->ke-depth): rho=0.303, p<0.0001, n=418 paragraphs, 46 folios
- H1 (null gradient): mean rho=-0.006, t-test p=0.919, n=46 folios

## Provenance

- Source: `phases/BRUNSCHWIG_1512_BLIND_PREDICTION/results/followup_results.json`
- Depends on: C1399 (paragraph ordering null), C1400 (state-independent ordering), C1457 (e->y safety), C1225 (ke-depth), C1250 (THERMAL category)
