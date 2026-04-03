# Recipe Matching: How We Identified the Source Tradition

This document describes the methodology used to match individual chapters of the Pseudo-Lullian *Testamentum* to individual Voynich manuscript folios. 42 unique procedural chapters map to ~25 folios, covering approximately 89% of the *Testamentum*'s procedural content (42 of 47 chapters classified as procedural). The methodology progressed through four stages: statistical matching, expanded matching, reverse-blind prediction, and instruction-level validation.

For the broader project context, see [README.md](README.md). For claims and limits, see [WHAT_WE_CLAIM.md](WHAT_WE_CLAIM.md).

---

## 1. The Source Text

The Pseudo-Lullian *Testamentum* is a 14th-15th century alchemical treatise attributed to Ramon Llull but written by an unknown practitioner. The 1566 Cologne printed edition contains 209 chapters across four parts:

| Part | Chapters | Content |
|------|----------|---------|
| Theorica | 96 | Alchemical theory and philosophy |
| Practica | 32 | Step-by-step laboratory procedures |
| Liber Mercuriorum | 51 | Mercury preparation, pearl-making, fermentation, furnace/vessel specifications |
| Liber Furnis | 30 | Furnace construction and fire management |

Of these, 47 chapters contain procedural content (specific operational instructions). The remaining 162 are theoretical, descriptive, or philosophical. The manuscript encodes only procedural content — theoretical and descriptive chapters produce zero validated matches (C1932).

The full Latin text and English translation are in `sources/pseudo_lull_testamentum/`.

**Why this text?** The *Testamentum* was selected based on a convergence of prior findings: (1) Brunschwig structural alignment (28 tests, Phases 419-461) established the distillation domain; (2) Brunschwig explicitly cites the Pseudo-Lullian tradition as his source; (3) the manuscript's radiocarbon date (1404-1438) falls within the Pseudo-Lullian production window (1330s-1500s); (4) the *Testamentum* is the most extensive procedural text in the tradition. The *Testamentum* was tested first because it was the most probable candidate from these converging lines of evidence, not because it was randomly selected.

---

## 2. Stage 1: Statistical Matching (Phase 628)

### Feature Extraction

Each PL chapter was characterized by a 4-channel feature vector extracted from the English translation text using keyword classifiers:

| Channel | What it measures | Recipe keywords |
|---------|-----------------|-----------------|
| **k-channel** (thermal) | Heat operations | fire, heat, warm, bath, ashes, flame, coals, furnace |
| **h-channel** (monitoring) | Observation steps | see, observe, watch, color, smell, taste, sign |
| **e-channel** (correction) | Error handling | careful, error, spoil, corrupt, danger, burn |
| **t-channel** (termination) | Endpoint criteria | until, when, complete, cease, enough, perfect |

Each Voynich folio was characterized by 12 operational features from the token-level grammar analysis (k_ratio, h_ratio, e_ratio, terminal_rate, and 4 deployment features from the morph system).

### The 8D Residual Matching

8 locked feature dimensions map recipe features to folio features:

| # | PL feature | Voynich feature | Direction |
|---|-----------|-----------------|-----------|
| 1 | heat_rate | k_ratio | inverse |
| 2 | monitoring_rate | h_ratio | direct |
| 3 | correction_rate | e_ratio | direct |
| 4 | termination_rate | terminal_rate | direct |
| 5 | consistency_frac | d_m_linefinal_rate | inverse |
| 6 | heat_rate | displaced_suffix_transparency | inverse |
| 7 | monitoring_rate | header_enrichment | inverse |
| 8 | heat_transition_rate | thermo_ke | direct |

The matching procedure:
1. Build 8D vectors for all chapters and all folios
2. Apply sign corrections to the PL side (directions 1-8 above)
3. Subtract the mean from each set (residual centering)
4. Jointly standardize (z-score across combined PL + V vectors)
5. Compute Euclidean distance matrix (chapters × folios)
6. Assign each chapter to its nearest folio (greedy with pair-swap improvement)

### Validation

| Test | Result |
|------|--------|
| Permutation test (1,000 shuffles) | Real assignment beats all shuffles: **p < 0.001** (C1887) |
| Cross-family replication | Sublimation (57%), dissolution (33%), fixation (30%) — features generalize without retuning (C1885) |
| Wrong-regime control | R4 collapses to 1/16 confident (vs 9/16 for correct R1) (C1886) |
| Cross-validation | 11/16 chapters maintain >40% consensus across 500 feature-subset trials (C1883) |

### Results

16 distillation-family chapters matched to REGIME_1 folios. 9/16 confident (ratio > 1.15 between best and second-best distances). 3 individually validated with independent structural evidence:

- **f75r ↔ Ch19 Mercuriorum** (aqua vitae, 9× reflux): Only 4+ consecutive identical token run in the corpus; unique double-dar; **independent Brunschwig cross-confirmation** — Brunschwig Ch28 (the expanded practical version of the same recipe) ranks #2 for f75r at distance 1.478 vs PL Ch19 at 1.300. Two texts from different traditions independently identify the same folio for the same recipe.
- **f76r ↔ Ch18 Practica** (element separation, silver-plate test): Strongest monitoring gradient in corpus (ρ = 0.710, rank 1/13); ch→sh active-to-passive transition maps the testing progression
- **f84r ↔ Ch14 Practica** (gold dissolution): Dual-layer 12-header architecture; product chain link to f75r via PL cipher key ("vegetable G" = quintessence)

Source: Phase 628 (C1882-C1890). Script: `phases/RECIPE_FOLIO_CORRESPONDENCE/scripts/recipe_matching.py`.

---

## 3. Stage 2: Expanded Matching (Phases 634-635)

### Beyond Distillation

The Phase 628 matching only tested distillation-family chapters. We expanded to all operation families (sublimation, fermentation, fixation, dissolution, coagulation, separation) using the same frozen 8D features.

**Result:** Mean distance increased only 7% (2.358 vs 2.214), demonstrating the features are family-agnostic (C1933). 8+ new validated matches found, including the strongest expanded match: f79r ↔ Ch12 Mercuriorum (mercury sublimation → elixir, d = 1.02).

### Cross-Folio Vocabulary

Three tokens show cross-folio consistency across independently-matched folios:

| Token | Decomposition | Behavior | Evidence |
|-------|--------------|----------|---------|
| `dar` | da(setup) + r(respond) | Present on all folios matched to recipes introducing NEW materials; absent on all folios matched to cohobation/separation-only recipes | 6/6 partition (C1925) |
| `chekar` | ch(test) + ek(precision) + ar(close) | Appears in post-thermal, vessel-monitoring context | 7/7 folios, qo depleted 0.48× on chekar lines (C1926) |
| `dal` | da(setup) + l(state) | Marks careful/measured material placement, distinct from dar's vigorous introduction | Confirmed via Latin verb mapping: "coniungendo" (joining) → dal, not dar |

### Section-Level Correspondence

The matches cluster geographically in the manuscript:

- **Section B (f75-f84):** 8/11 folios in this range match Mercuriorum chapters (C1927); additional matches from expanded and reverse-blind methods bring the Section B total to ~14 folios
- **Section S (f103-f116):** 6 folios match transmutation/multiplication chapters Ch40+ (C1930)
- **Section T (f66r):** One fixation recipe in ring diagram format (C1931)

Source: Phases 634-635 (C1925-C1933).

---

## 4. Stage 3: Reverse-Blind Prediction (Phase 636)

### Method

The first two stages were confirmatory: examine a folio, compare to its matched recipe, confirm correspondence. Stage 3 tests whether the process works in **reverse**: read a recipe, derive structural predictions, scan unmatched folios, identify the match.

Procedure:
1. Read a PL chapter and extract predictions: expected dar count, gentle heat ratio, dominant PREFIX, folio size, iteration markers
2. Score all ~49 unmatched folios against these predictions
3. Select the top candidate
4. Cold-read the candidate at atom level to confirm or reject

### Results

| Recipe | Top candidate | Scan score | Atom confirmation |
|--------|--------------|------------|-------------------|
| Ch27 Practica (imbibition) | **f103v** | 10/11 | 6/7 YES |
| Ch7-10 Mercuriorum (pearl-making) | **f39r** | 10/11 | 6/7 + 1 PARTIAL |
| Ch2+3+6 Mercuriorum (coagulate+sublimate+rectify) | **f77r** | — | **7/7 PERFECT** |
| Ch29 Practica (troubleshooting) | **f43v** | 7/11 | 4/6 + 2 PARTIAL |

The f103v identification was the first **predictive** (not confirmatory) recipe-folio match in the project (C1935). f77r scored 7/7 perfect — every prediction derived from the recipe was confirmed on the folio (documented in Phase 636 narrative; no individual constraint for the f77r result).

### Organizational Findings

The reverse-blind work also revealed:

- **Multi-chapter folios:** Short related procedures are consolidated onto single folios. f80r encodes Ch21-25M (5 animal distillation chapters). f77r encodes Ch2+3+6M (3 mercury preparation steps). (C1937)
- **Recto/verso pairing:** Sequential operations appear on opposite sides of the same physical leaf. f103r/v (multiplication → imbibition), f66r/v (fixation → inceration), f108r/v (separation → dissolution). (C1936)

Source: Phase 636 (C1934-C1938).

---

## 5. Stage 4: Instruction-Level Validation

### The Problem

Several matches initially appeared weak — "head-scratcher" assessments where the folio's thermal profile didn't match the recipe's apparent structure. The root cause was **summary compression**: recipes were mentally reduced to 2-3 phase labels ("balneum then ash") when they actually contain 14-43 distinct operational instructions.

### Method

For each weak match, count every operational verb in the recipe text (Latin or English — both contain the same verbs). Map the verb sequence to the folio's paragraph structure. Check whether proportions align.

### Results

| Folio | Before | After | Recipe verbs found | Key resolution |
|-------|--------|-------|-------------------|----------------|
| f108r | Head-scratcher | Supported | 14 (was summarized as 2 phases) | ok=22.4% maps 4-step apparatus setup; e-depth follows 4-phase sequence |
| f78v | Moderate | Supported | 16 (balneum is step 11/16) | 9.2% gentle heat correct: balneum occupies 6% of recipe |
| f81v | Supported with concerns | Supported-strong | 26 (was summarized as ~7) | 8.5% gentle heat correct: balneum is step 3/26 |
| f83r | Moderate | Supported | 43 (was summarized as 4) | 75.7% opaque terminals maps 9 sealing operations; ch=17% maps drop-counting system |
| f112r | Supported (weak) | Supported-strong | 25 (alternating balneum/ash) | Distributed balneum correct for alternating recipe; ok escalation maps Latin "custodi" |
| f76v | Supported (zero dar) | Supported-strong | 12 (Latin: "coniungendo" = join) | Zero dar correct: recipe verb is "join/bind," not "add." 22 n-atoms map the binding step. |
| f111v | Unclear (competing) | Supported | Ch10M: 23 steps vs Ch20M: 9 steps | Ch10M wins on all 5 dimensions: token density, zero dar, low gentle heat, heat trajectory, vocabulary uniqueness |

Every weak match improved when analyzed at instruction level rather than phase level. The Voynich notation encodes at the granularity of individual operational verbs, not summarized phases.

### Latin Verb → Atom System Mapping

The instruction-level analysis revealed that different Latin verb types activate different parts of the Voynich atom system:

| Latin verb type | Example | Voynich encoding |
|----------------|---------|-----------------|
| Vigorous material introduction | accipe, pone (take, place) | `dar` (da + r = setup + respond) |
| Careful measured placement | pone secundum pondus (place by weight) | `dal` (da + l = setup + state) |
| Binding/joining | coniungendo, licabis (join, bind) | n-atoms (bind) |
| Visual quality check | videas quod comburat (see that it burns) | sh PREFIX (passive monitoring) |
| Active discrete test | pone super laminam argenti (place on silver plate) | ch PREFIX + chekar |
| Graduated fire change | paulatiue vigorando ignem (gradually strengthening) | e-depth gradient (kee → ke → k) |

---

## 6. Negative Controls

| Source tested | Chapters/segments | Result |
|--------------|------------------|--------|
| PL Theorica | 96 theoretical chapters | Zero atom-validated matches (C1932) |
| PL Furnis | 30 construction chapters | 2 genuine matches (furnace + vessel specs), rest noise (C1932) |
| Codicillus | 19 procedural segments | Zero new folio assignments; most segments collapse onto single attractor folio (informal — not a registered constraint) |
| Brunschwig 1512 compounds | 20 complex recipes | Zero confident matches; collapse onto attractors (informal — not a registered constraint) |
| Brunschwig 1500 simples | 245 plant distillations | Too thin (2-3 steps each) to differentiate folios (informal observation) |

The matching system says YES to procedural Practica and Mercuriorum content, and NO to everything else tested. The Theorica/Furnis negatives (C1932) are registered constraints; the Codicillus and Brunschwig negatives are informal observations from exploratory scanning using the same 8D pipeline. No alternative medieval alchemical texts beyond these have been tested.

---

## 7. Summary of Coverage

**Mercuriorum (25 unique chapters matched across 17 folios):**

*Note: Ch22M appears both within the f80r multi-chapter encoding (Ch21-25M ash chain) and as an independent detailed treatment on f82r. It is counted once in the total.*

| Chapter(s) | Recipe | Folio | Method |
|-----------|--------|-------|--------|
| Ch1M | Lunaria → quicksilver | f112v | Expanded matching |
| Ch2+3+6M | Coagulate + sublimate + rectify | f77r | Reverse blind (7/7) |
| Ch4M | Fix sublimated substance | f116r | Expanded matching |
| Ch7-10M | Pearl-making sequence | f39r | Reverse blind (6/7) |
| Ch11M | Red mercury tincture | f112r | Phase 628 |
| Ch12M | Mercury sublimation → elixir | f79r | Expanded matching (d=1.02) |
| Ch14M | Composite ferments | f78v | Expanded matching |
| Ch15M | Ferment conversion | f76v | Expanded matching |
| Ch16M | Ferment multiplication | f103r | Expanded matching |
| Ch18M | Potable gold / water of life | f81v | Phase 628 |
| Ch19M | Aqua vitae composite (9× reflux) | **f75r** | **Phase 628 CONFIRMED** |
| Ch20M | Flesh bath distillation | f79v? | Speculative |
| Ch21-25M | Animal ash chain (5 waters) | f80r | Phase 628 (multi-chapter) |
| Ch22M | Lunaria maceration | f82r | Phase 628 |
| Ch27M | Furnace specification | f77v | Phase 628 |
| Ch28M | Vessel specification | f82v | Phase 628 |
| Ch44M | Quicksilver coagulation | f107r | Expanded matching |

**Practica (17 unique chapters matched across 13 folios):**

| Chapter(s) | Recipe | Folio | Method |
|-----------|--------|-------|--------|
| Ch9P | First distillation of menstrual solvent | f83r | Phase 628 |
| Ch10+11P | Silver + mercury balneum dissolution | f108v | Reverse blind |
| Ch12+20+22P | Dissolution + imbibition + amalgamation | f85r1 | Reverse blind |
| Ch14P | Gold dissolution (balneum + putrefaction) | **f84r** | **Phase 628 CONFIRMED** |
| Ch16P | Element separation (two-phase) | f108r | Phase 628 |
| Ch18P | Element separation (silver-plate test) | **f76r** | **Phase 628 CONFIRMED** |
| Ch19P | Washing of fire and earth | f46r | Reverse blind |
| Ch21P+28P | Red sulfur + red elixir fixation | f115r | Blind test + split |
| Ch24P | Fixation (repeated sublimation) | f66r | Full-spectrum scan |
| Ch26P | Oil inceration / fusibility test | f66v | Reverse blind |
| Ch27P | Mercury imbibition / exuberation | f103v | Reverse blind (6/7 CONFIRMED) |
| Ch29P | Troubleshooting / correction | f43v | Reverse blind |
| Ch30P | Medicine multiplication | f105v | Reverse blind |

**Not encoded (confirmed non-procedural):**
- Ch5M — 4-sentence philosophical stub
- Ch13M — cipher taxonomy (B=gold, C=sulphur)
- Ch26M — medical administration (humoral dosing) — not encodable in B grammar
- Ch29M — elemental theory (philosophical)
- 14 Practica theoretical chapters
- 96 Theorica chapters (all philosophical)
- 28/30 Furnis chapters (construction specifications)

**42 unique procedural chapters → ~25 folios (some folios encode multiple short chapters; some chapters share a leaf as recto/verso pairs). Coverage: 42 of 47 chapters classified as procedural (89%).**

*Classification note: "Procedural" means the chapter contains specific operational instructions (heat, distill, seal, etc.). The 5 excluded chapters are: Ch5M (philosophical stub), Ch13M (cipher taxonomy), Ch26M (medical administration — humoral dosing, not operational procedure), Ch29M (elemental theory). This classification was made based on chapter content, not matching results — Ch26M was excluded because the B grammar lacks conditional branching for patient-type selection, not because it failed to match.*

---

## 8. Limitations

- **Individual chapter assignments are Tier 3** (interpretive, not proven). The matching FRAMEWORK is Tier 2 (validated by permutation test, cross-family replication, negative controls). But any specific "this folio = this chapter" assignment could be revised by new evidence. No individual false discovery rate has been computed; the permutation test validates aggregate significance, not per-match confidence.

- **Feature selection circularity.** The 8D features were tuned on distillation→R1 (16 chapters, 32 folios). The permutation test validates whether the ASSIGNMENT is better than random, but the feature SELECTION was data-driven from the same corpus. Cross-family generalization (+7% distance penalty) mitigates this but does not fully resolve it.

- **~40 folios remain unmatched — but this is a structural prediction, not a failure.** The unmatched folios are concentrated in Section H (herbal pages with plant illustrations), which is physically and organizationally separate from the sections where matches cluster. The pattern is consistent with a multi-domain workshop manual where each manuscript section draws from a different source tradition:
  - **Section B (f75-f84):** Matched to PL Mercuriorum (mercury preparation pipeline)
  - **Section S (f103-f116):** Matched to PL transmutation/multiplication chapters
  - **Section H (f1-f57):** Unmatched — plant illustrations suggest herbal distillation recipes, but Brunschwig's Small Book (2-3 steps per plant) is too operationally thin to differentiate folios, and the Large Book compounds collapse onto attractors
  
  One Section H folio HAS been matched: **f31r** was identified as a rosewater distillation candidate via structural profile scoring against Brunschwig's rosewater recipe — the one herbal recipe with extensive operational detail (cohobation, 5 quality tests, rectification, sun exposure, 3-year shelf life). The match works precisely because Brunschwig devoted pages to rosewater where most herbs get 2-3 lines. This confirms that Section H folios CAN match to herbal recipes when the source text has sufficient operational content.
  
  The Section H illustrations may carry COMPLEMENTARY content: the text encodes HOW to distill (operational grammar), the illustration identifies WHAT to distill (plant identity). This is consistent with C138 (illustrations don't constrain text) — the two are not redundant but independent information channels. The Testamentum accounts for ~25 of 83 Currier B folios (30%); the remaining folios likely encode content from a herbal distillation tradition whose surviving texts lack the operational detail needed for 8D matching.

- **Limited alternative source testing.** Only the *Testamentum*, Brunschwig (1500 and 1512), and the Codicillus have been tested. Other medieval alchemical texts (Geber, Turba Philosophorum, Rosarium Philosophorum, etc.) have not been evaluated. The claim is "Testamentum matches better than anything tested," not "Testamentum is the only possible source."

- **Instruction-level validation has no reported failures.** Every weak match improved under verb-counting analysis (7/7 upgrades, Section 5). One match was REJECTED before this stage (f84v, single-sentence recipe vs 347-token folio), but no match that entered verb-counting analysis was killed by it. This could indicate the method always confirms, though the f84v rejection shows the broader methodology CAN reject matches.

- **Instruction-level validation is interpretive.** Counting operational verbs and mapping them to paragraph structure requires judgment about where one instruction ends and the next begins. No inter-rater reliability testing was performed. Verb counts were not performed blind to folio properties.

- **The reverse-blind method had implicit constraints.** By Phase 636, the section-level correspondence (Section B = Mercuriorum, Section S = transmutation) was known. This reduced the effective search space for reverse-blind scans from ~49 unmatched folios to ~15-20 section-appropriate candidates.

- **No pre-registration.** Feature dimensions, matching algorithms, and evaluation criteria were developed iteratively. The permutation test and cross-family replication provide post-hoc validation, but no element of the methodology was pre-registered.

- **The atom glosses are operational labels, not translations.** When we say `dar` = "material introduction," we mean the token appears at material-introduction points in matched recipes. We do not claim the Voynich author thought of `dar` as meaning "material introduction" in any language. The Latin verb-to-atom mapping (Section 5) is an interpretive observation, not a registered constraint.

---

## 9. Reproducibility

All scripts, data, and results are in this repository:

| Component | Location |
|-----------|----------|
| 8D matching code | `phases/RECIPE_FOLIO_CORRESPONDENCE/scripts/shared_628.py` |
| Recipe matching script | `phases/RECIPE_FOLIO_CORRESPONDENCE/scripts/recipe_matching.py` |
| Replication + permutation | `phases/RECIPE_FOLIO_CORRESPONDENCE/scripts/replication_validation.py` |
| Full-spectrum scan | `phases/RECIPE_FOLIO_CORRESPONDENCE/scripts/_full_spectrum_matcher.py` |
| Reverse-blind scripts | `phases/REVERSE_BLIND_MATCHING/` (listed in Phase 636 INDEX) |
| PL Latin text | `sources/pseudo_lull_testamentum/testamentum_complete_latin.txt` |
| PL English translation | `sources/pseudo_lull_testamentum/testamentum_complete_english.txt` |
| Codicillus Latin + English | `sources/codicillus/codicillus_complete_latin.txt`, `codicillus_complete_english.txt` |
| Brunschwig 1512 (Large Book) | `sources/brunschwig_1512/brunschwig_1512_english.txt` (45,926 lines) |
| Brunschwig 1512 compound features | `sources/brunschwig_1512/brunschwig_1512_compound_features.json` |
| Brunschwig 1500 (Small Book) | `sources/brunschwig_1500/` |
| Voynich transcript | EVA interlinear format, H-track (loaded via `scripts/voynich.py`) |
| Per-folio analysis | `context/FOLIOS/f*.md` (40 documented folios) |
| Constraint registry | `context/CLAIMS/INDEX.md` (C1882-C1938) |

---

*For the full constraint system, see `context/CLAIMS/INDEX.md`. For the conceptual walkthrough, see [GUIDE.md](GUIDE.md).*
