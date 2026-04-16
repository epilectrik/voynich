# Phase 641: B Gloss Recipe Correlation (Latin features)

**Phase:** 641
**Status:** PLANNING
**Type:** Statistical validation with pre-registered contrastive predictions
**Draft:** 2026-04-16 (v2, post-expert review)

## Context

We have 15+ matched Voynich B folio ↔ Pseudo-Lull Testamentum recipe pairs. Each folio decodes at the atom level (C1394 HEAD+MOD*+TERM, 100% coverage). Each matched recipe has a known original Latin text (1566/1567 Cologne editions, transcribed by Opus 4.6 agents from source images — not OCR). This is a parallel corpus.

Atom/prefix/suffix glosses (PT-013, PT-014, PT-015) were validated qualitatively on 3 folios (f83r, f82r, f112v). Phase 641 tests them **statistically** across all 15 matched pairs with pre-registered predictions, permutation p-values, BH-FDR correction, leave-one-out stability, bootstrap CIs, and a control-corpus requirement.

## Unit of Analysis

**Paragraph-level sequential.** Within a matched folio, paragraphs correspond to recipe steps in order. C1399/C1400 (corpus-wide "no universal ordering") is explained by recipe diversity: each recipe has its own step sequence, so averaging across 83 folios washes out the within-folio sequentiality. Supported by f75r, f82r, f112v sequential alignments this project.

This matters for two reasons:
1. Ordinal alignment (DTW / Kendall-τ on step order) is meaningful — primary diagnostic
2. Per-paragraph aggregation is valid — finer-grained than per-folio

## Why Latin (not English)

- Latin is source; English is LLM-translated from it (same project, same agents). English adds translator interpretation without adding independent signal.
- Transcription method is AI vision (Opus 4.6) not OCR — error model is systematic interpretation bias, not random character confusion. File header documents normalization rules (long-s normalized, tildes expanded, u/v preserved, æ/œ preserved).
- Medieval alchemical Latin vocabulary more stable than English translations. `balneum`, `cineres`, `fornax`, `sublima-`, `digere-`, `distilla-`, `coagula-`, `cohoba-` are unambiguous; English scatters these across multiple synonyms.
- Latin body: 12,956 lines vs. English 6,737 — nearly 2×.

## Goal

Convert PT-013/14/15 to promotable constraint-level claims with:
1. Pre-registered contrastive predictions (written before looking)
2. Permutation p-values with BH-FDR correction
3. Leave-one-out stability
4. Bootstrap ρ CIs
5. Testamentum must beat a control corpus
6. Held-out validation on unseen folios

---

## Pre-Registration (written before any statistics are run)

### Hypotheses to test (20 items)

**Block A — PREFIX glosses (6 items):**

| # | PREFIX | Predicted Latin correlate | Direction |
|---|--------|---------------------------|-----------|
| A1 | qo | sum of heat_mode_counts | + |
| A2 | ch | sum of (monitoring + heat_transition) | + |
| A3 | sh | monitoring_count (passive: `vide`, `appare`, `observa`) | + |
| A4 | ok | vessel_count (`vas`, `cucurbita`, `alembic`) | + |
| A5 | ot | transfer_count (`pour`, `decant`, drip markers) — per C1958 | + |
| A6 | da | material_addition_count (`accipe`, `pone`, `adde`) | + |

**Block B — Suffix function (4 items):**

| # | Suffix | Predicted function | Correlate | Direction |
|---|--------|--------------------|-----------|-----------|
| B1 | -aiin/-ain | containment form | sealing_count (`claude`, `lute`, `cera`) + vessel_count | + |
| B2 | -dy | cycle closure | iteration_count (`repete`, `iterum`) | + |
| B3 | -y | endpoint (test on ey, hy, dy separately — not bare y) | compound-specific | varies |
| B4 | -am | phase finalization, paragraph-final rate | transition_count (`postea`, `deinde`) | + |

**Block C — SOLID atoms (6 items):**

| # | Atom | Current gloss | Correlate | Direction |
|---|------|---------------|-----------|-----------|
| C1 | d | do/execute | material_addition + transfer | + |
| C2 | t | transfer | transfer_count | + |
| C3 | l | state (static) | heat_transition_count | **-** (inverse) |
| C4 | o | arrange | vessel_count | + |
| C5 | c | adjust | heat_transition_count | + |
| C6 | p | pause | termination_count + `quiesce`/`cessa` | + |

**Block D — LOCKED atoms under scrutiny (2 items, no demotion):**

| # | Atom | Drift check | Prediction |
|---|------|-------------|------------|
| D1 | a (yield vs. into) | termination_count | negative if "yield" (process complete) |
| D2 | n (bind/contain vs. halt) | iteration_count | negative if "halt" |

**Block E — PLAUSIBLE atoms (3 items, expect INCONCLUSIVE due to low power):**

| # | Atom | Predicted correlate | Direction |
|---|------|---------------------|-----------|
| E1 | r (respond) | monitoring + heat_transition | + |
| E2 | f (flag) | termination_count | + |
| E3 | s (sequence) | iteration + transition | + |

**Block F — Contrastive pre-registration for qokaiin (from PT-014 revision):**

qokaiin has two candidate glosses competing:
- H1 (falsified in PT-014): "strengthen/intensify heat"
- H2 (current): "heat-source: sustained contained form"

Contrastive predictions on 15 matched folios:
- H1 predicts: qokaiin rate correlates with `heat_transition_count` (+)
- H2 predicts: qokaiin rate correlates with `sealing_count + vessel_count` (+) AND inversely with `heat_transition_count` (−)

Same test on 5 held-out (non-matched) folios with decoded recipes from external sources: if H2 survives on held-out, it becomes promotable.

**Block G — m-terminal (1 item):**

| # | Feature | Correlate | Direction |
|---|---------|-----------|-----------|
| G1 | m-terminal rate (C1434-1439, TRANSITION category) | transition_count + paragraph-final position | + |

**Block H — Ordinal alignment (primary structural test):**

For each matched pair, extract:
- Recipe step sequence (from Latin regex — ordered list of feature-marked lines/sentences)
- Folio paragraph sequence (ordered list of paragraph-level feature profiles)

Compute Kendall-τ between the two sequences. Null: shuffled paragraph order.

**Prediction:** Across 15 matched pairs, mean Kendall-τ > 0 with p < 0.05 (one-sided). Individual pairs: ≥ 10/15 positive at τ > 0.2.

This is the **primary diagnostic** — directly tests "this folio executes this recipe."

---

## Statistical Apparatus

1. **Spearman rank correlation** — robust to outliers, appropriate for N=15
2. **Exact permutation p-values** (10,000 shuffles) — no parametric assumptions
3. **Section-stratified permutation** — folios share section composition; can't treat as exchangeable. Stratify by Currier section within null distribution construction.
4. **Bootstrap ρ CIs** — 1,000 resamples, 95% CI. Surfaces folio-driven artifacts (if CI crosses 0, finding rides on 1-2 folios).
5. **Leave-one-out stability** — for each supported finding, drop each pair in turn, re-run. Finding must survive all 15 LOO iterations.
6. **BH-FDR q=0.10** across the 20 blocks (A+B+C+D+E+G = 22 tests; block F separate; block H standalone)

## Falsification Criteria (revised)

| Result | Condition | Action |
|--------|-----------|--------|
| SUPPORTED | Predicted direction + passes BH-FDR q=0.10 + bootstrap CI excludes 0 + LOO-stable | Promotable to C#### constraint |
| INCONCLUSIVE | Predicted direction but fails FDR/LOO/CI | No change |
| FALSIFIED | Direction reversed + p < 0.05 raw | Demote PLAUSIBLE/SOLID; flag LOCKED |

## Promotion Requirements (revised)

To promote a PT entry to a C#### constraint:
- SUPPORTED in Latin
- SUPPORTED in English parity run (or explainable English-INCONCLUSIVE via translator choice)
- Passes control-corpus requirement (Brunschwig Latin and non-recipe control text do NOT show the same correlation at the same strength, proving the finding is Testamentum-specific, not a generic regex coincidence)
- For qokaiin-family: survives contrastive prediction on held-out folios

---

## Directory Structure

```
phases/B_GLOSS_RECIPE_CORRELATION/
  PLAN.md                            (this file)
  INDEX.md                           (on completion)
  scripts/
    s0_latin_feature_extractor.py   (builds pl_channel_features_latin.json)
    s0b_brunschwig_features.py      (control corpus Latin features)
    s0c_nonrecipe_control.py        (non-recipe Latin text baseline)
    s1_shared_validation.py         (shared loaders, stat fns, LOO, bootstrap)
    s2_preregistered_tests.py       (Blocks A-G, single script runs all, 22 tests)
    s3_ordinal_alignment.py         (Block H, DTW + Kendall-τ on step order)
    s4_qokaiin_contrastive.py       (Block F, contrastive test + held-out validation)
    s5_control_comparison.py        (Testamentum vs. Brunschwig vs. non-recipe)
    s6_english_parity.py            (re-run s2 against English features, compare)
    s7_validation_summary.py        (aggregate scorecard, verdicts, LOO table)
  results/
    pl_channel_features_latin.json
    brunschwig_features_latin.json
    nonrecipe_features.json
    preregistered_tests.json
    ordinal_alignment.json
    qokaiin_contrastive.json
    control_comparison.json
    english_parity.json
    validation_scorecard.json
```

## Script Details

### s0 — Latin Feature Extractor

Regex over `testamentum_complete_latin.txt`, segmented by `CAPVT` markers cross-referenced with `pseudo_lull_structural_profile.json` chapter indices.

**Feature families** (Latin stems with `\w*` suffix handling inflection):

| Channel | Latin patterns |
|---------|---------------|
| heat_mode | `ign\w+`, `calor\w+`, `balneum`, `cineres`, `fornax\w*`, `arena`, `stercor\w+` |
| heat_transition | `augeat\w* ign\w*`, `minuat\w* ign\w*`, `fortiter`, `leniter`, `intende\w+`, `remitte\w+` |
| monitoring | `vide\w+`, `appare\w+`, `signum`, `signa`, `manifest\w+`, `observa\w+`, `nota\w+` |
| material_addition | `sume\w*`, `accipe\w*`, `recipe`, `pone\w+`, `adde\w+`, `mitte\w+`, `infunde\w*` |
| sealing | `claude\w*`, `obtura\w*`, `sigilla\w*`, `lute\s+et`, `pasta`, `cera\w*` |
| transition | `postea`, `deinde`, `tunc`, `mox`, `statim`, `postmodum` |
| intensity | `fortiter`, `leniter`, `paulatim`, `gradatim`, `vehementer`, `modice` |
| termination | `donec`, `quousque`, `ad complementum`, `consumat\w+`, `exsiccet\w*` |
| iteration | `repete\w*`, `iterum`, `itera\w+`, `reiter\w+`, `toties` |
| vessel | `vas\w*`, `cucurbita\w*`, `alembic\w*`, `ampulla\w*`, `retorta\w*` |
| transfer | `transfer\w+`, `vert\w+`, `decant\w+`, `effunde\w+` |

Per-chapter counts normalized by chapter line length. Pre-registered regex list locked before s2 runs.

### s0b / s0c — Control Corpora

- **s0b:** Same feature extraction on Brunschwig 1512 Latin (different distillation tradition, plausibly a false match)
- **s0c:** Same feature extraction on a non-recipe Latin text — use Testamentum's Theorica (speculative/theoretical, not operational) as a within-source control. Any "recipe feature" that shows up strongly in Theorica is detecting Latin style, not recipe content.

### s1 — Shared Validation

- `load_matched_pairs()` → 15 pairs with tier
- `folio_paragraph_profile(folio)` → per-paragraph atom/prefix/suffix counts
- `folio_atom_profile(folio)` → per-folio aggregate counts
- `recipe_feature_profile(chapter_idx, source='latin')` → per-chapter features
- `recipe_step_sequence(chapter_idx)` → ordered list of feature-marked steps
- `folio_paragraph_sequence(folio)` → ordered list of paragraph feature profiles
- `spearman_with_perm(x, y, n_perm=10000, stratify_by=None)` → ρ + exact p
- `bootstrap_rho(x, y, n_boot=1000)` → 95% CI
- `leave_one_out(x, y, pair_labels)` → verdict table
- `bh_fdr(pvals, q)` → significance threshold under FDR control

### s2 — Pre-Registered Tests (Blocks A-G)

Runs all 22 hypothesis tests in one script, produces single JSON output. All regex patterns and predictions locked before execution.

### s3 — Ordinal Alignment (Block H)

For each matched pair:
1. Extract recipe step sequence (ordered feature-marked Latin lines within chapter range)
2. Extract paragraph sequence (ordered paragraph-level feature profiles within folio)
3. Compute Kendall-τ on rank-aligned sequences (using feature-profile distance for matching)
4. Null: shuffle paragraph order, re-compute τ, 10,000 permutations
5. Test: mean τ across 15 pairs > 0 at p < 0.05 (one-sided); ≥ 10/15 pairs individually at τ > 0.2

This tests the structural claim ("folio executes recipe") directly.

### s4 — qokaiin Contrastive (Block F)

1. Run both candidate-correlation tests on 15 matched folios
2. Identify 5 held-out folios (high-confidence matches from elsewhere, e.g., verso pairs from C1953-1955 recto/verso scans that we haven't touched for gloss work)
3. Run same tests on held-out set
4. Report: which gloss survives on held-out data

### s5 — Control Comparison

Compare feature-correlation strengths between:
- Testamentum-matched pairs (the 15)
- Testamentum-paired with SHUFFLED chapter assignments (permuted pairings)
- Brunschwig features subbed in for Testamentum features on same folios
- Theorica (non-recipe) features subbed in

Testamentum must produce stronger, more coherent correlations than all three controls.

### s6 — English Parity

Re-run s2 against existing English `pl_channel_features.json`. Report concordance. Any Latin-SUPPORTED item that's English-FALSIFIED gets investigated (not auto-rejected).

### s7 — Validation Summary

Scorecard with per-item verdict, p (FDR-corrected), bootstrap CI, LOO stability, English parity status, control-comparison margin, promotion eligibility.

---

## Expected Outcomes

From expert-advisor's prior assessment:
- **Strong support expected:** k-HEAD, e-MOD/depth, qo-PREFIX, ok-PREFIX, da-PREFIX, ot-PREFIX, m-terminal
- **Expected INCONCLUSIVE (low power):** r, f, s, g, x
- **Falsification risk:** bare y-terminal (gloss too broad — tested compound-specific instead)

## Risks

- **15 pairs is small.** Even with FDR + LOO + bootstrap, many items may land INCONCLUSIVE. That's acceptable.
- **Selection bias on the 15 pairs** — they were chosen by 8D feature matcher which includes thermal. Permuted-pairing null (s5) checks this.
- **Latin transcription bias** — systematic agent choices could inflate certain stems. Non-recipe Theorica control detects this.
- **Ordinal alignment depends on paragraph segmentation being correct.** We've verified segmentation on f82r/f83r/f112v sequential work.

## Execution Order

1. `s0_latin_feature_extractor.py` + `s0b_brunschwig_features.py` + `s0c_nonrecipe_control.py` (parallel)
2. `s1_shared_validation.py` (library, no standalone run)
3. `s2_preregistered_tests.py`, `s3_ordinal_alignment.py`, `s4_qokaiin_contrastive.py` (parallel)
4. `s5_control_comparison.py`, `s6_english_parity.py` (parallel after s2 runs)
5. `s7_validation_summary.py` (last)

## Bookkeeping (local-only, no push)

Per user instruction: commit but do NOT push to `origin` or `github` until further notice. Standard 7-step bookkeeping, stopping before push.
