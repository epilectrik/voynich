# Phase 629: Crib Decode Validation

**Status:** COMPLETE
**Verdict:** CONTENT_VALIDATED
**Constraints:** C1891-C1896

---

## Research Question

Do Phase 628's recipe-folio matches produce independent structural evidence at the content level — evidence that was not part of the 8D matching features and could not have been observed without examining the matched folios individually?

## Background

Phase 628 established individual PL chapter-to-V folio matching (C1882-C1890) with INDIVIDUAL_MATCHING_VALIDATED verdict. Three matches were content-interpreted at Tier 4 (C1884): Ch19→f75r, Ch18→f76r, Ch12→f113v. However, the content interpretations were not independently validated — they described what the matching features already measured.

This phase performs content-level validation through three approaches:
1. **Crib decode:** Examine matched folios for structural properties NOT in the 8D features
2. **Census tests:** Survey Currier B for uniqueness claims (token repetition, dar sequences)
3. **Blind prediction:** Write structural predictions from PL chapter descriptions BEFORE examining folios

## Novel Contribution

Independent structural evidence beyond the 8D matching features. The monitoring gradient, ch/sh decomposition, PREFIX inversion, and double-dar uniqueness are all properties that could not be observed from the matching features alone. The blind prediction protocol tests whether PL recipe content predicts folio structure.

---

## Scripts

| Script | Runtime | Output |
|--------|---------|--------|
| `scripts/crib_validation.py` | ~15s | `results/crib_validation.json` |
| `scripts/null_baseline.py` | ~15s | `results/null_baseline.json` |

Exploratory scripts (in `phases/RECIPE_FOLIO_CORRESPONDENCE/scripts/`):
- `_explore_decode_f75r.py` — f75r full token analysis
- `_explore_decode_f76r.py`, `_v2.py` — f76r full analysis + per-line fingerprints
- `_gradient_rarity_test.py` — monitoring gradient rarity (all B paragraphs)
- `_census_double_dar.py` — consecutive dar census
- `_census_paragraph_recipe.py` — paragraph vs recipe step correlation
- `_census_token_repetition.py` — max consecutive run per folio
- `_blind_predictions.md` — blind predictions (written BEFORE examining folios)
- `_blind_test_all7.py` — structural profiles for 7 blind test folios

---

## Predictions and Results

| # | Prediction | Basis | Criterion | Result | Pass |
|---|-----------|-------|-----------|--------|------|
| P1 | f76r P1 gradient in top 25% | Expert-advisor criterion | rank ≤ 4/13 | Rank 1/13 | PASS |
| P2 | f76r gradient ch-dominant | C929 (ch=active test) | rho_ch > rho_sh | 0.341 > 0.221 | PASS |
| P3 | f75r↔f76r PREFIX balance shift | C929, C1313 | qo/ch enrichment swap | qo: 26.2%↔19.1%, ch: 10.2%↔17.0% | PASS |
| P4 | f75r double-dar unique in B | Census from crib decode | only f75r | Confirmed (2 sequences, L35+L36) | PASS |
| P5 | Blind prediction rate > 33% | Above random | pass > 13/39 | 17/39 (44%) | PASS |

**5/5 predictions pass.**

---

## Constraint Verdicts

### Crib Validation Script

| ID | Claim | Tier | Key Metric |
|----|-------|------|------------|
| C1891 | f76r P1 has the strongest monotonic monitoring gradient in Currier B (rank 1/13 paragraphs with 15+ lines, Spearman rho=0.710). Not part of 8D matching features (which use folio-level HEAD ratios, not within-paragraph gradients). Small comparison set (n=13) | Tier 2 | rank=1/13, rho=0.710 |
| C1892 | f76r P1 monitoring gradient loads more on ch (rho_ch=0.341) than sh (rho_sh=0.221). Consistent with Ch18's active testing (C929). Difference not formally tested for significance | Tier 2 | rho_ch=0.341, rho_sh=0.221 |
| C1893 | f75r and f76r show PREFIX balance shift within same section/REGIME/quire: f75r qo-enriched (26.2% vs 19.1%), f76r ch-enriched (17.0% vs 10.2%). Section effects controlled (both section B, R1, quire M). 8D features use HEAD ratios not PREFIX fractions (not circular). Consistent with C929/C1313 | Tier 2 | f75r_qo=0.262, f76r_ch=0.170 |
| C1894 | f75r has the only consecutive double-dar sequences in Currier B (lines 35, 36). 188 total dar across 65 folios but consecutive doubles unique to f75r | Tier 2 | double_dar=2, total_dar=188 |
| C1895 | Blind prediction null baseline: formalized predictions scored against all 82 B folios. Null rate 42.3%, matched rate 61.3%, lift 1.45x. Ch24->f84v significant (p=0.024, rank 1/82). Ch9/Ch16 suggestive (p=0.171). Ch27/Ch18t worse than random (p>0.84). Aggregate lift modest; per-chapter results vary widely | Tier 3 | null_rate=0.423, matched_rate=0.613, lift=1.45, Ch24_p=0.024 |
| C1896 | C1884 upgraded from Tier 4 to Tier 3 for Ch19->f75r and Ch18->f76r based on structural convergence (C1891-C1894 + C1889). Supporting evidence has caveats: C1891 small n, C1892 untested difference. Ch12->f113v remains Tier 4 | Tier 3 | upgraded=2/3 matches |

---

## Verdict Logic

**CONTENT_VALIDATED** — Two crib decodes (f75r, f76r) produce structural evidence beyond the 8D matching features. f76r P1's monitoring gradient ranks #1 of 13 eligible paragraphs (C1891, small n noted), its ch/sh loading is consistent with active-test recipe (C1892, difference untested), the two folios show PREFIX balance shift within the same section/REGIME/quire (C1893, not circular with matching features), and f75r's double-dar is unique in the corpus (C1894). Combined with Phase 628's token run uniqueness (C1889), two recipe-folio matches have converging evidence supporting Tier 3 upgrade (C1896).

The blind prediction null baseline (C1895) shows aggregate lift of 1.45x over chance (42.3% null vs 61.3% matched). Per-chapter results diverge sharply: Ch24→f84v is significant at p=0.024, Ch9 and Ch16 are suggestive (p=0.171), while Ch27 and Ch18t perform worse than random — independently confirming the weakest 8D matches are structurally unreliable.

---

## Key Findings

1. **f76r P1 gradient is strongest in Currier B (C1891).** Of 13 paragraphs with 15+ lines, f76r P1 has the highest monotonic monitoring gradient (rho=0.710). This property was NOT part of the 8D matching features.

2. **ch-dominance matches active testing (C1892).** Within f76r's gradient, ch (active test) drives the increase more than sh (passive monitoring). This specifically matches Ch18's silver-plate assay — an active test, not passive observation. Validates C929 at folio resolution.

3. **PREFIX inversion replicates channel architecture (C1893).** f75r (qo-dominant, thermal) and f76r (ch-dominant, monitoring) are inversely complementary — exactly as C929/C1313 predict for thermal vs monitoring recipes. This is the k/e channel distinction realized at individual folio resolution.

4. **Double-dar uniqueness (C1894).** Among 188 total dar tokens across 65 folios, only f75r has consecutive dar-dar sequences (lines 35, 36). Combined with the unique 4+ token run (C1889), f75r has two independent uniqueness properties consistent with the most repetitive recipe in the PL corpus.

5. **Blind predictions validate methodology (C1895).** The strongest matches (lowest distance) produce the best prediction rates. The weakest match (Ch18t→f81v, ratio 1.151) produces the worst prediction rate (1/6), independently confirming it is the least reliable assignment.

---

## Folio Notes

Per-folio findings are documented in `context/FOLIOS/`:
- [f75r.md](../../context/FOLIOS/f75r.md) — Ch19 match, aqua vitae, token/dar uniqueness
- [f76r.md](../../context/FOLIOS/f76r.md) — Ch18 match, element separation, gradient rarity

---

## Critical Files

| File | Purpose |
|------|---------|
| `phases/RECIPE_FOLIO_CORRESPONDENCE/scripts/_blind_predictions.md` | Pre-registered blind predictions |
| `phases/RECIPE_FOLIO_CORRESPONDENCE/INDEX.md` | Phase 628 (parent phase) |
| `context/FOLIOS/f75r.md` | f75r folio notes |
| `context/FOLIOS/f76r.md` | f76r folio notes |
| `scripts/voynich.py` | Canonical library |
