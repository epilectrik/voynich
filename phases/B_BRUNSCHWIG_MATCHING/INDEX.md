# Phase 642: Brunschwig-Voynich Systematic Matching

**Phase:** 642
**Status:** COMPLETE (neutral/negative result — informative)
**Type:** Matching pipeline
**Started:** 2026-04-17
**Completed:** 2026-04-18

## Purpose

Test whether the Voynich herbal section (f1-f66, essentially 0% matched to Testamentum) contains folios matchable to Brunschwig's ingredient-reference and recipe corpora, based on the f55r→Brunschwig 1512 Ch XXXVI (opium) match established in PT-018.

## Scripts Executed

| Script | Purpose | Status |
|--------|---------|--------|
| `s2_unsupervised_cluster.py` | Cluster all 82 B folios on 52 structural features (no f55r reference) | COMPLETE |
| `s0c_ingredient_chapters.py` | Segment Brunschwig 1512 "Von X" ingredient-reference chapters | COMPLETE |
| `s3_folio_ingredient_matching.py` | Match 26 cluster folios against 7 ingredient chapters | COMPLETE |

## Key Findings

### 1. Pharmaceutical-regime cluster is REAL (s2)
- k=4 clustering with silhouette=0.328
- 26-folio cluster containing f55r, **0/16 overlap with matched Testamentum folios**
- PC1 separates regimes by 8-10 standard-deviation units
- Cluster 1 members: f33r/v, f34r/v, f39r/v, f40r/v, f43r, f50r/v, f55r/v, f85r1/2, f86v4-6, f94r/v, f95r1/2/v1/v2, f105v, f114r
- PC1 loadings distinguish: **Testamentum side**: qo-prefix, e-depth=1, k/e-HEAD (alchemical heat-cycles); **Cluster side**: e-depth=0, a/o-HEAD, BARE prefix, high vocab diversity (low-heat observational)

### 2. PT-018 target passage is UNIQUELY SPECIFIC (shuffle test)
- Across 648k words of Brunschwig 1500 + 1512, only TWO 300-word windows contain ≥3 distinctive extraction-method patterns
- Both windows are the opium Ch XXXVI passage
- No other Brunschwig passage comes close — the target of PT-018's 3-block alignment is genuinely unique in the corpus

### 3. Systematic aggregate-feature matching is INSUFFICIENT (s3 — the negative finding)
- Ranked 7 ingredient chapters (Piper, Cinnamomum, Rosa, Scordeon, Opium, Agaricus, Crocus) against 26 cluster folios via cosine similarity of 7 operational features
- **f55r: Opium rank #2/7** — passes "top-3" test but Scordeon (+0.57) beats Opium (+0.12)
- **Negative control fails**: matched Testamentum folios mean top-1 sim = +0.46 vs cluster mean +0.53 (only marginal separation)
- **f80r alchemical folio gets Opium as top-1 (+0.82)** — higher than any pharmaceutical-cluster folio
- **f76r alchemical folio gets Agaricus as top-1 (+0.87)** — highest similarity in entire test, for a confirmed alchemical folio

## Interpretation

**PT-018 structural alignment holds; aggregate feature matching does not.**

The 3-block-with-distinguishing-markers alignment (f55r P2 → Ch XXXVI three opium preparation methods) was the real signal. Aggregate cosine similarity on per-folio feature rates doesn't reproduce that. This tells us:

1. **Block-level structural alignment** (identifying operational blocks within a paragraph, matching each block's distinguishing markers to candidate chapters' method-specific markers) is the tool that captures PT-018's signal. Aggregate features don't.

2. **The pharmaceutical cluster is real but heterogeneous** — the 26 folios share a "not-alchemical" signature but don't individually map to specific Brunschwig ingredients via simple feature matching.

3. **Target corpus may be wrong or insufficient.** 7 ingredient chapters is a small target set and they share operational features (all describe preparations). Other candidate corpora not tested: Brunschwig Book 5 disease-symptom index (per crazy-expert suggestion), multi-source fusion (Rupescissa quintessences, Tichtel clinical notes).

## Constraint Status

**No constraint promotions.** Phase 642 was an exploration, not a hypothesis validation.

## Pre-Registered Predictions — Outcome

| Prediction | Outcome |
|---|---|
| Cluster hypothesis: unmatched herbal folios with pharmaceutical-regime signature exist | **PASSED** (s2 confirmed 26-folio cluster) |
| Matched-folio control: Testamentum-matched folios shouldn't match Brunschwig strongly | **FAILED** (matched folios match at similar strength to cluster) |
| Plant-ID consistency (retrospective on f55r→opium) | **PARTIAL** (opium #2/7 for f55r; Scordeon beats it) |
| Method-marker alignment with structural-block approach | **DEFERRED** (not tested in this phase — would require block-level feature extraction) |

## Deferred Work

1. **Block-level matching pipeline** — requires paragraph-by-paragraph segmentation and block-level feature extraction (terminator types, method-distinguishing markers). This is what PT-018 did manually; a systematic version would need significant engineering.

2. **Multi-source fusion** — Voynich herbal folios might draw from multiple source traditions. Pipeline would need to compute best match across Testamentum + Brunschwig 1500 + Brunschwig 1512 + others, and allow multi-source assignments.

3. **Disease/symptom index as target corpus** — crazy-expert's suggestion. If the Voynich is workshop-indexed by symptom-to-preparation rather than by plant, the target corpus should be Brunschwig 1500 Part 3 (disease index) not Part 2 (herbal encyclopedia).

4. **Plant-ID ground-truth collection** — establish tier-1 botanical IDs for cluster folios to enable proper validation of any future matching pipeline.

## Key Files

| File | Purpose |
|------|---------|
| `results/unsupervised_cluster.json` | 26-folio pharmaceutical cluster identified |
| `results/brunschwig_1512_ingredient_chapters.json` | 7 ingredient chapters extracted |
| `results/folio_ingredient_matching.json` | Per-folio ranked candidates + aggregate stats |

## What Makes This Result Informative Despite Being Neutral

1. **The "pharmaceutical regime" is a real structural class** in the Voynich B corpus — not a figment of f55r-centric curve-fitting. 26 folios cluster together on structural features, separated from alchemical-matched folios by 8-10 standard deviations on PC1.

2. **PT-018 target specificity is confirmed** — the Brunschwig opium chapter is uniquely the densest extraction-method passage in 648k words. This defuses the "any 3-method text would match" concern.

3. **Feature-matching approach clearly insufficient** — we now know aggregate folio-level features don't discriminate ingredients. Future work should focus on block-level structural matching.

4. **The pipeline didn't collapse into noise** — f55r does rank Opium top-3 via systematic pipeline, 4 cluster folios rank Opium top-1. There's signal, just not enough to promote to constraints via this method.

This is a genuine neutral result that advances understanding: we know what direction to go (block-level matching), we know the cluster is real, we know the exemplar is specific, and we know the naive feature-matching approach doesn't work.
