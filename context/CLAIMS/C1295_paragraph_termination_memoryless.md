# C1295: Paragraph Termination is Memoryless

**Tier:** 2
**Scope:** B
**Phase:** PARAGRAPH_TERMINATION_TRIGGER (Phase 457)
**Date:** 2026-02-24

## Statement

Paragraph termination has no detectable line-level trigger. All 7 trigger hypotheses FAIL (Bonferroni p<0.00625): thermal level (T1, length-controlled Fisher p=0.236), B-track thermal signature (T2, Fisher p=0.178), thermal step (T3, perm p=0.822), thermal budget (T4, within-folio rho=-0.007 p=0.930), mode gate (T5, chi2=1.19 p=0.276), category shift (T6, perm p=0.400), folio prediction extension (T7, F-test p=0.365 LOO decreases). N=257 paragraphs with 3+ body lines, 537 total.

## Architecture

- **Extends C963 body homogeneity to thermal/category grain.** C963 showed role fractions are position-independent after length control. C1295 confirms this extends to e_frac (thermal), ke_ratio, suffix mode, and 8-category composition. No structural feature predicts whether a body line is the last one.
- **T1 length confound confirmed.** Raw e_frac difference (last 0.380 vs interior 0.358) vanishes after stratifying by n_toks quartile. The signal is entirely driven by last lines being shorter (7.5 vs 9.8 tokens), confirming C963's length-is-the-only-systematic-progression finding.
- **No thermal budget (T4, definitive).** Within-folio Spearman of mean e_frac vs body length: rho=-0.007, p=0.930 (45 folios). Paragraphs with higher cooling content do not terminate sooner. The 85% folio-specific body length variance (C1239) is not reducible to thermal dynamics.
- **-am is a marker, not a trigger.** C1237 established -am as 5.19x enriched at paragraph-final positions. C1295 shows nothing in the body predicts when -am will fire. The termination decision is set at folio/paragraph design level (C1239), not by within-paragraph state evolution.
- **Overall verdict: TERMINATION_MEMORYLESS** (1/8 PASS, 7/8 FAIL).

## Provenance

- Extends C963 (body homogeneity) from role fractions to thermal/category grain
- Extends C1237 (-am termination) with negative trigger search
- Extends C1239 (body length parameterization) by ruling out within-paragraph determinants
- Extends C1241 (header-body independence) with body-internal independence
- Extends C1260 (B-track thermal propagation) with negative termination signal
- Resolves Phase 450 T5 (penultimate lines distinguishable at 2.45x) as length-driven, not trigger-driven
