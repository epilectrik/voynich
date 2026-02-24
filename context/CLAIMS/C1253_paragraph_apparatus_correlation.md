# C1253: Paragraph-Level Apparatus Correlation

**Tier:** 2 (ESTABLISHED)
**Scope:** B
**Phase:** PARAGRAPH_OPERATIONAL_CLASSIFICATION (Phase 447)
**Extends:** C1250 (gloss category structural coherence, T6: token-level rho=0.758), C1248 (apparatus-marker co-occurrence)
**Relates to:** C1247 (aii REGIME_3 specificity), C1249 (section-conditioned apparatus diversity)

---

## Statement

The THERMAL category fraction at paragraph level correlates with folio apparatus profile score at rho=0.409 (p=0.000, n=466 paragraphs, 1000 within-section permutations). This is weaker than the token-level correlation (rho=0.758, C1250 T6) but still highly significant against the shuffled null (mean shuffled rho=0.257).

The attenuation from 0.758 to 0.409 is expected: paragraph-level aggregation mixes thermal and non-thermal tokens within each paragraph, diluting the per-token signal. The persistence of significance confirms that apparatus type influences operational content at the paragraph level, not just at individual token positions.

---

## Interpretation

Paragraphs in folios with higher apparatus distillation scores contain more THERMAL-category operations. This confirms the apparatus-gloss link (C1250 T6) scales from individual tokens to the paragraph operational unit (C827). The weaker effect at paragraph level is consistent with paragraphs being multi-operation units that mix categories, while individual tokens carry cleaner category assignments.

---

## Method

- 466 paragraphs with >=5 classified body tokens
- Per-paragraph THERMAL fraction from 8-category body gloss profile
- Folio apparatus score from `data/apparatus_profiles.json` (DISTILLATION marker fraction)
- Spearman rank correlation
- Null model: permute paragraph-folio assignments within section (1000 permutations)
- Token-level comparison value from C1250 T6 (rho=0.758)

**Script:** `phases/PARAGRAPH_OPERATIONAL_CLASSIFICATION/scripts/paragraph_operational_classification.py`
**Results:** `phases/PARAGRAPH_OPERATIONAL_CLASSIFICATION/results/paragraph_operational_classification.json`
