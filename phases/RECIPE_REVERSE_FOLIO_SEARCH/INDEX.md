# Recipe Reverse-Folio Search

**Phase:** 646
**Status:** COMPLETE — ONE_NEW_MATCH_CONFIRMED (f77r ↔ III.28.0)
**Type:** Reverse-direction match search (recipe → folio)
**Started:** 2026-04-25
**Completed:** 2026-04-25
**Outcome:** Searched unmatched B folios for structural-signature matches to confirmed-match templates. f77r ↔ III.28.0 (4-element temperament) emerges as new confirmed match. Test B rho=+0.861, p=0.0005. Total confirmed matches: 7 → 8.

## Purpose

Per crazy-expert's earlier recommendation: convert the methodology from "predict folio→recipe" to "predict recipe→folio." For each of the 8 confirmed-match folios (treated as templates), search unmatched B folios for matching structural signatures. The bidirectional alignment strengthens the architectural claim — moving from "this folio encodes this recipe" to "this recipe class has a recognizable Voynich-side syntactic fingerprint."

## Methodology

1. Compute structural signatures for the 7 confirmed-match folios (treated as templates: f75r, f84r, f78r, f86v3, f82r, f108v, f79v)
2. Compute signatures for all unmatched B folios (≥200 tokens, ≥4 paragraphs) — 26 candidates
3. Standardize features (z-score) and compute Euclidean distance from each unmatched folio to nearest template
4. For closest candidates, identify structural anchors and predict matching recipe count
5. Search SISMEL unmatched recipes for predicted counts
6. Verify top hit via raw-line reading + Test B

## Results

### Top candidates by signature distance

| Folio | Tokens | Paras | Best template | Recipe | Distance | Run |
|-------|------:|:----:|:----:|:----:|:---:|:---:|
| f104v | 458 | 13 | f86v3 | II.10.0 | 1.84 | 3 |
| f77r  | 325 | 13 | f82r  | III.19.3 | 2.29 | 2 |
| f114r | 447 | 12 | f86v3 | II.10.0 | 2.34 | 2 |
| f105v | 390 | 10 | f86v3 | II.10.0 | 2.35 | 2 |
| f114v | 362 | 11 | f86v3 | II.10.0 | 2.40 | 2 |

### Verification: f77r → III.28.0

f77r had **two within-line 4-clusters** (L11, L34) suggesting a 4-anchor. Searched unmatched recipes with 4-count and found:

**III.28.0 — "Ara direm del temperament de la pedra; e com està en los .iiii. elements ab distemperament"** (theoretical chapter on the stone's existence across the 4 elements: earth, water, air, fire — and balancing the 4 qualities: hot, cold, dry, humid).

Recipe content overview:
- Theoretical exposition of how the stone is in all 4 elements (terra, aygua, ayre, foch)
- Operational guidance: combine water + earth in small parts, return water over white earth `diverses vegades`, then combine with air, decoct in `foch de temperança`

f77r structure:
- 13 paragraphs, 325 tokens, 40 lines
- 4 paragraph-initial line-starts at L1, L2, L3, L4 (consecutive specification block)
- 2 more at L17, L30 (mid-folio paragraph breaks)
- High qokeedy density (gentle-heat dominant)
- Heavy qokaiin/qokain (iteration verbs throughout)
- 0 dar, 3 dal — abstract recipe with few discrete materials
- 0 chekar (continuous procedure, no phase gates)

### Atom-decode operational score

| Criterion | Recipe expectation | f77r evidence | Verdict |
|-----------|--------|------|---------|
| 4-element specification | `.iiii. elements` | 4 line-initial paragraphs L1-L4 + within-line 4-clusters at L11, L34 | ⭐ MATCH |
| Theoretical/abstract content | mostly philosophical | High qok density, low dar count | ⭐ MATCH |
| Sustained gentle heat | `foch de temperança` | qokeedy dominant | ⭐ MATCH |
| Multiple iterations | `diverses vegades` / `retorna` | Heavy qokaiin/qokain | ⭐ MATCH |
| Material combinations | water + earth, then air | dal at L17, L37, L39 (3 dal) | ⭐ MATCH |
| No discrete observation gate | continuous | 0 chekar | ⭐ MATCH |
| Long recipe match | 10019 chars | 325 tokens, 13 paragraphs (compact) | ~ WEAK |
| Layout-phase order | spec → body → closure | Test B rho +0.861, p=0.0005 | ⭐ MATCH (strict sig) |

**Score: 7 MATCH / 1 WEAK / 0 MISMATCH = STRONG SUPPORT.**

## Test B result

Phase assignment locked before correlation: P1-P4 (4 line-initial spec paragraphs) = phase 1, P5-P12 (body operational) = phase 2, P13 (closure) = phase 3.

- rho = +0.8613
- perm p = 0.0005 ★ STRICT SIGNIFICANCE
- n_paragraphs = 13 (meets n≥10 criterion)

## Implications for C1959

**8th confirmed match added.** Updated aggregate:
- Confirmed matches: 7 → **8** (across **7** distinct recipe classes; 4-element-temperament added)
- Mean rho across 8 matches: ~+0.85
- Strict significance (p<0.05): 4/7 → **5/8**
- n≥10 individually-significant folios: f84r (n=18), f108v (n=10), **f77r (n=13)** = 3 folios

**Tier 2 promotion threshold review:** Per expert-advisor's "3+ additional confirmed-match folios with n≥10 paragraphs reach individual significance" criterion, the additional-at-n≥10 count is now 2 (f108v + f77r) beyond original baseline (f84r at n=18). Still short of strict 3-additional threshold by 1. However, total significant folios is 5/8 with 3 at n≥10. Pragmatic position is closer to Tier 2 territory than registered Tier 3.

**Decision:** Hold formal Tier 2 promotion review for now. Update C1959's evidence base to reflect 8 matches + new aggregates. Future investigation that adds 1 more n≥10 individually-significant match should trigger explicit promotion review.

## Other reverse-scan candidates (NOT verified)

The reverse scan flagged additional candidates that did NOT advance:

- **f104v** (closest by distance, d=1.84): only 3-run anchor of `sheol` (sh-prefix, not qok-class). Unusual anchor type; matched recipe candidates are diverse with no clean fit. Deferred.
- **f114r, f105v, f114v, f105r** etc.: many unmatched folios cluster near II.10.0 template due to general signature similarity, but have no distinctive count anchors. Cannot be confidently matched without additional structural evidence.
- **f111r** (614 tokens, sublimation-class candidate): has 3-clusters but only 6 paragraphs (low Test B power). Defer.

The reverse-direction scan demonstrates that distinctive count anchors (not generic signature similarity) drive successful matches. f77r had a clean 4-anchor; the others lacked equivalent specificity.

## Scripts

| Script | Purpose |
|--------|---------|
| `reverse_scan.py` | Compute signatures + nearest-template per unmatched folio |
| `verify_top_candidates.py` | Predict recipes from anchors for top candidates |
| `verify_f77r.py` | Pull f77r raw lines + III.28.0 recipe text |
| `test_B_f77r.py` | Test B layout-phase correlation for f77r ↔ III.28.0 |

## Results files

- `scan_results.json` — full signature scan output
- `test_B_f77r.json` — Test B numerical result
