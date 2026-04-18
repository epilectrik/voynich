# Phase 642: Brunschwig-Voynich Systematic Matching

**Phase:** 642
**Status:** DESCOPED to foundational-feasibility test (s0 + unsupervised s2 only)
**Type:** Matching pipeline (parallel to Testamentum matching workflow)
**Draft:** 2026-04-17 (v2 post-expert review)
**Window:** 3 days before SISMEL Catalan arrival

## EXECUTIVE UPDATE (post-expert review)

Both expert-advisor and crazy-expert flagged the same critical weakness: the "pharmaceutical regime" hypothesis was derived from ONE folio (f55r). Building a full matching pipeline on a single data point risks curve-fitting to a single folio masquerading as a discovered principle.

**Descoped to foundational feasibility test:**
- s0a + s0b: segment Brunschwig corpora (prerequisite, not controversial)
- s2: **UNSUPERVISED clustering** of all 82 B folios WITHOUT using f55r as reference
- Decision gate: if a genuine cluster separates from the matched-Testamentum folio set AND f55r is part of it (not a cluster-of-one), proceed with full matching pipeline. If not, phase is premature.

Full pipeline (s3-s7) deferred pending foundational test. Plan below retained for reference once foundational test passes.

## Context

We have extensive Testamentum-Voynich matches (15-16 matched folio↔chapter pairs from Phases 627+, e.g., `phases/RECIPE_FOLIO_CORRESPONDENCE/results/recipe_matching.json`). We also have extensive Brunschwig STRUCTURAL analysis (decomposition, apparatus mapping, complementarity, variance architecture) — but NO systematic per-folio matching pipeline against Brunschwig entries the way we did for Testamentum.

PT-018 (this session, 2026-04-17) demonstrated that f55r — a completely untouched unmatched herbal folio — matches Brunschwig 1512 Ch XXXVI (opium) with method-distinguishing token alignment. This was a hand-targeted hit based on a plant illustration ID; no pipeline produced it.

If f55r → Ch XXXVI is real, there's no principled reason other unmatched herbal folios shouldn't match other Brunschwig entries. We've never looked systematically.

## Hypothesis

The Voynich herbal section (f1-f66) contains **at least two encoding regimes:**

1. **Alchemical-operation regime** — matches Testamentum structure (our 15-16 existing matches mostly Mercuriorum/Practica)
2. **Pharmaceutical-preparation regime** — matches Brunschwig structure (ingredient-reference + preparation-methods)

Distinguishing signature for regime 2 (established from f55r):
- Opaque terminals ≤ 55% (vs matched Testamentum folios' 69-77%)
- e-depth=0 dominance ≥ 80%
- qo-prefix ≤ 12%
- qot-compounds ≤ 2%
- HEAD atoms dominated by o, a (arrange, yield) rather than k, e (heat, cool)
- `or` prominent as top-frequency token (route/respond)
- Careful-dosing markers (`dal`) present

## Goal

Produce a ranked-candidate list of Brunschwig entries for each unmatched Voynich B folio, validated via blind predictions where possible. Primary deliverable: `brunschwig_matching.json` analogous to Testamentum's `recipe_matching.json`.

## Brunschwig Corpus Structure

### Brunschwig 1500 "Liber de arte distillandi" (small book, distillation manual)

| Part | Lines (approx) | Content | Entry count | Relevance |
|------|---------------|---------|-------------|-----------|
| Part 1 | 1-2800 | Distillation methods, apparatus, 4 degrees | ~30 method descriptions | For furnace/distillation folios |
| Part 2 | 3566-21000 | Alphabetical herbal encyclopedia | ~200 per-herb entries | **PRIMARY TARGET for unmatched herbal folios** |
| Part 3 | 21000+ | Disease/symptom index | indexed, not match-candidates | Reference only |

### Brunschwig 1512 "Gross Distilierbuch" (large book, compounding)

| Section | Content | Entry type | Relevance |
|---------|---------|-----------|-----------|
| Book 1 | Aqua vitae composita, balsams, theriac | Compound recipes | For multi-ingredient folios |
| Ingredient reference chapters | E.g., Ch XXXVI opium, XXXIX agaric, etc. | Per-ingredient descriptive + preparation | **PRIMARY TARGET for single-plant herbal folios** |
| Recipe catalog | Complex compounds | Multi-step recipes | For complex-preparation folios |

## Voynich-Side Targets

**Unmatched folios to test:**
- Herbal section (f1-f66): 66 folios. Currently 0 matched to Testamentum directly, 16 in matched set are all biological/stars/pharmaceutical section
- **Actually the 15-16 matched folios are mostly f75r-f116r** — the herbal section (f1-f66) is essentially entirely unmatched
- Biology/stars section unmatched folios that might be pharmaceutical

Priority ranking:
1. Herbal folios with IDENTIFIABLE plants (where external plant ID exists) — highest signal
2. Herbal folios with pharmaceutical-regime signature (opaque terminals <55%, low qo, high `or`)
3. Other unmatched herbal folios

## Directory Structure

```
phases/B_BRUNSCHWIG_MATCHING/
  PLAN.md                            (this file)
  INDEX.md                           (on completion)
  scripts/
    s0a_brunschwig_1500_segmenter.py   (Part 2 per-herb entries)
    s0b_brunschwig_1512_segmenter.py   (ingredient reference chapters)
    s1_shared_brunschwig.py            (loaders, features)
    s2_pharmaceutical_regime_cluster.py (signature-class across all B folios)
    s3_per_folio_matching.py           (rank Brunschwig entries per folio)
    s4_plant_id_validation.py          (use existing plant ID where available)
    s5_deep_alignment_top_candidates.py (f55r-style alignment on top hits)
    s6_blind_prediction.py             (held-out validation)
    s7_summary.py                      (aggregate scorecard)
  results/
    brunschwig_1500_entries.json
    brunschwig_1512_chapters.json
    pharmaceutical_regime_scores.json
    per_folio_matching.json
    plant_id_validated.json
    deep_alignment_results.json
    blind_predictions.json
    brunschwig_matching_scorecard.json
```

## Script Details

### s0a — Brunschwig 1500 Part 2 entry segmenter

Segment the herbal encyclopedia into per-entry chunks. Each 1500 Part 2 entry follows:

```
[Plant name] water / [Plant name] wasser.
  The plant called by [the Greeks] [Greek name], by [the Latins] [Latin name],
  and in German [German name]. [Physical description]. The best part and
  time for its distillation is [part] at [time].
  A [Use 1, with dosage and indication]
  B [Use 2]
  C [Use 3]
  ... [up to Z]
```

Extract per entry:
- Primary name(s) in each language
- Physical description text
- Best-part-and-time specification (part: leaves/root/seed/flower/whole; time: spring/summer/etc.)
- Uses A-Z with: dosage, indication, application method (drunk/washed/rubbed/soaked-cloth)

Output: `brunschwig_1500_entries.json` — one entry per herb with all fields.

### s0b — Brunschwig 1512 ingredient chapter segmenter

Ingredient reference chapters have variable structure but typically:

```
Chapter N — [Ingredient]
  [Etymology / definition]
  [Sources / geographic provenance]
  [Varieties / grades]
  [Preparation methods — one or more]
  [Uses as ingredient in other compounds]
```

Extract per chapter:
- Ingredient name + Latin/Greek/Arabic synonyms
- Preparation methods (if any) — this is the match target for f55r-like folios
- Quality/grade criteria

Output: `brunschwig_1512_chapters.json`.

### s1 — Shared Brunschwig utilities

- `load_brunschwig_1500_entries()` → list of entries
- `load_brunschwig_1512_chapters()` → list of chapters
- `brunschwig_feature_profile(entry)` → feature vector appropriate for Brunschwig structure
- `folio_feature_profile(folio)` → reuse from Phase 641 `s1_shared_validation.py` (already exists)

**Brunschwig-specific feature extraction** (different from Testamentum's):

| Feature | Extracted from Brunschwig | Expected Voynich correlate |
|---------|---------------------------|-----------------------------|
| plant_part_seed | "seed", "kern", "samen" | — plant-description on folio |
| plant_part_root | "root", "wurtzel" | — |
| plant_part_flower | "flower", "blossom", "blume" | — |
| plant_part_leaf | "leaf", "leaves", "blatt" | — |
| preparation_water | "water", "wasser", distilled preparation | qokeedy-like (gentle distillation) |
| preparation_oil | "oil", "öl" | — |
| preparation_tincture | "tincture", "extract" | — |
| indication_topical | "rubbed", "washed", "cloth-soaked", "laid" | — |
| indication_internal | "drunk", "consumed", dose in lots | — |
| careful_dose_marker | specific dosage (e.g., "two lot", "one quintin") | dal-rate (careful placement) |
| observation_required | "when you see", "until", signs-to-watch | or-rate (route/respond) |

### s2 — Pharmaceutical-regime signature cluster

Compute f55r-like signature for **all 82 B folios**. Cluster by distance from f55r profile.

Output: ranked list of folios by pharmaceutical-regime membership score.

**Signature dimensions:**
- opaque_terminal_rate (low = pharmaceutical)
- e_depth_zero_rate (high = pharmaceutical)
- qo_prefix_rate (low = pharmaceutical)
- qot_compound_rate (low = pharmaceutical)
- or_token_rate (high = pharmaceutical)
- dal_rate (presence = pharmaceutical)
- ao_HEAD_rate (high = pharmaceutical)

Normalize each dimension, compute distance from f55r's values. Rank.

Expected: the 15-16 matched Testamentum folios should land FAR from f55r (they're alchemical regime). Unmatched herbal folios should spread; pharmaceutical-regime candidates cluster with f55r.

### s3 — Per-folio Brunschwig matching

For each folio in pharmaceutical-regime cluster (from s2):
1. Compute folio feature vector
2. Compute similarity to each Brunschwig entry
3. Rank candidates
4. Also check: does this folio match Brunschwig BETTER than any Testamentum chapter?

Output: per-folio top-5 Brunschwig candidates with similarity scores.

### s4 — Plant-ID validation

For folios with external plant identifications (from Voynich scholarship, user's annotations, or project memory), verify that the top Brunschwig candidate corresponds to the identified plant.

Example: if f55r plant-ID = opium poppy and s3's top-1 Brunschwig candidate for f55r = Ch XXXVI (opium), we have a validated match.

If plant-ID ≠ top candidate → either the pipeline is wrong OR the plant-ID is wrong OR both. Investigate.

### s5 — Deep alignment on top candidates

For the top-3 candidate matches from s3 (highest-confidence, with plant-ID validation if available):
- Do f55r-style token-by-token deep alignment
- Check for method-distinguishing markers (like f55r's 3 terminators matched Ch XXXVI's 3 methods)
- Produce alignment tables

### s6 — Blind prediction

Hold out 3-5 folios from s3's pipeline. Predict their top Brunschwig match FROM SIGNATURE ONLY (no plant-ID input). Then check against available plant-ID. Validates whether the signature-based pipeline works without external plant knowledge.

### s7 — Summary scorecard

Aggregate:
- Pharmaceutical-regime cluster size
- Number of candidate matches produced
- Number validated via plant-ID
- Number surviving deep alignment
- Blind prediction accuracy

## Statistical Apparatus

Since we're producing ranked candidates (not binary hypothesis tests), use:
- Rank-correlation of feature vectors (folio ↔ entry)
- Top-N retrieval rate (is the correct match in top-5? top-10?)
- Comparison against Testamentum matching strength — for each pharmaceutical-regime folio, is Brunschwig top-1 a better match than Testamentum top-1?

## Pre-Registered Predictions

1. **Cluster hypothesis:** Unmatched herbal folios with f55r-like signature (opaque terminals <55%, low qo, high `or`) should match Brunschwig entries better than Testamentum chapters.
2. **Matched-folio control:** The 15-16 existing Testamentum matches should NOT match Brunschwig entries better than they match Testamentum (control: matching pipeline shouldn't produce false Brunschwig matches for clearly-alchemical folios).
3. **Plant-ID consistency:** If external plant ID available, top-1 Brunschwig candidate should match the plant (tested on f55r already: opium → Ch XXXVI — check retrospectively in pipeline).
4. **Method-marker alignment:** Top candidates with preparation-method structure (like Ch XXXVI) should show the 3-method distinguishing-marker pattern we found in f55r.

## Falsification Criteria

| Result | Condition | Implication |
|--------|-----------|-------------|
| SUCCESS | ≥5 folios in pharmaceutical-cluster match Brunschwig better than Testamentum + plant-ID validates top candidates | Promotable findings, new match class established |
| PARTIAL | Some folios produce consistent matches but pipeline noisy | Refine features, document what works |
| NULL | Pharmaceutical-cluster folios don't match any specific Brunschwig entry better than random | f55r → Ch XXXVI was coincidence; revise pharmaceutical-regime hypothesis |
| FALSIFIED | Testamentum-matched folios ALSO match Brunschwig strongly | Matching pipeline is capturing generic Latin herbal style, not specific recipe structure |

## Execution Order

1. s0a + s0b (parallel): segment both Brunschwig books into entries
2. s1: library
3. s2: pharmaceutical-regime clustering across all B folios
4. s3: per-folio matching on pharmaceutical-regime cluster
5. s4: plant-ID validation (where available)
6. s5: deep alignment on top-3 candidates
7. s6: blind prediction on 3-5 held-out folios
8. s7: summary scorecard

## Scope — Realistic 3-Day Window

**Critical path (must complete):**
- s0a, s0b, s1, s2, s3 — produce ranked candidates per folio
- Spot-check top candidates manually for 2-3 folios

**Nice-to-have (if time):**
- s4 — systematic plant-ID validation
- s5 — deep alignment
- s6 — blind prediction

**Defer if needed:**
- Comprehensive s7 summary (can do during SISMEL work in parallel)

## Key Files

| File | Purpose |
|------|---------|
| `sources/brunchwig-zip/brunschwig_1500_english.txt` | 1500 small book full text |
| `sources/brunchwig-zip/brunschwig_1512_english.txt` | 1512 large book full text |
| `sources/brunschwig_1500/BRUNSCHWIG_1500_REFERENCE.md` | Structural guide to 1500 |
| `phases/BRUNSCHWIG_FULL_MAPPING/` | Prior extraction work (~200 materials) — reuse |
| `phases/BRUNSCHWIG_STRUCTURAL_RECIPE_DECOMPOSITION/` | Prior structural analysis — reuse |
| `scripts/voynich.py` | Transcript + Morphology |
| `phases/B_GLOSS_RECIPE_CORRELATION/scripts/s1_shared_validation.py` | Folio profile functions (reuse) |
| `phases/RECIPE_FOLIO_CORRESPONDENCE/results/recipe_matching.json` | Testamentum matches for comparison |

## Bookkeeping (local-only, no push — per user instruction)

Per user instruction (in effect since this session): commit but do NOT push to origin or github. Standard 7-step bookkeeping stopping before push.

## Why This Matters

1. **Complementary to SISMEL:** Testamentum work (including SISMEL's richer text) targets alchemical-regime folios. Brunschwig work targets pharmaceutical-regime folios. Together could match 50%+ of the Voynich vs. currently ~19% matched.
2. **Tests the closed-vocabulary hypothesis (PT-012):** If f55r's 92 unique words mostly reuse the 479 known token types in different operational contexts (pharmaceutical rather than alchemical), that's evidence the closed vocabulary spans multiple regimes.
3. **Publishable finding:** Two-regime herbal encoding matching two different medieval source traditions is genuinely novel.
4. **Gap-closing:** Addresses the "control corpus" gap identified by crazy-expert in Phase 641 review — Brunschwig won't work as a control (structural differences), but it CAN work as a PARALLEL target.
5. **Low-cost to run:** All data already exist. No new transcription needed.
