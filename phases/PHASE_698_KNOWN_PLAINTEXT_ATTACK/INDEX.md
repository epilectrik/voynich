# PHASE 698: Known-Plaintext Attack on f75r↔III.19 — Strong Form Falsified, Operational-Class Match Reinforced

**Status:** COMPLETE
**Date:** 2026-05-17
**Constraints registered:** C2034, C2035, C2036 (Tier 1)
**Sharpening:** C1971 phrasing methodology note
**Posture:** Long arc with two interpretive overshoots reversed by expert pushback

---

## Origin and trigger

Started as a known-plaintext cipher attack on f75r ↔ SISMEL III.19.0 (aqua vitae reflux distillation). The 8D thermal-profile matcher (C1366/C1888) had assigned this pair; the cold-read framework (C1971) verified operational-class signature. The hypothesis: strong-form Path A — Voynich tokens have specific Latin-text correspondences that could be reverse-engineered from the matched recipe content.

---

## Test arc

### Phase 1: Strong-form Path A tests (all returned null or contrary)

**1.1 Operational-phase alignment + Spearman test.** Per-line 4D thermal profile (k/h/e/qok), z-scored, matched each Voynich line to best Latin phase by Euclidean distance. Spearman between Latin narrative order and Voynich line position: **ρ = −0.80**. Only 5 of 9 Latin phases got line assignments; phase_7_rectification dominated 31 of 46 lines due to e-ratio methodology artifact. No linear-transcription signal.

**1.2 qok-peak block-structure shuffle null.** f75r has 6 qok-density peaks ≥40% (L9, L11, L13, L31, L37, L38). Within-folio shuffle null on contiguous-cluster structure: observed max-run = 3, null mean = 2.90, **p = 0.63**. Block structure is consistent with random arrangement of the same densities.

**1.3 Mantel-style correlation across 14 catalogued folios.** For each folio, extracted token sets and matched-chapter Catalan content-word sets. Built pairwise distance matrices and tested correlation across 6 variants:

| Variant | ρ | One-tailed p (positive) |
|---------|---|-------------------------|
| All folios, Jaccard | −0.21 | 0.89 |
| All folios, Overlap | +0.07 | 0.26 |
| Part III only, Jaccard | −0.15 | 0.81 |
| Part III only, Overlap | +0.09 | 0.22 |
| All folios, MIDDLE Jaccard | −0.09 | 0.68 |
| **Part III only, MIDDLE Overlap** | **+0.12** | **0.14** |

Best variant ρ = +0.12, p = 0.14 — not significant.

**1.4 Positional anchor check.** Catalan "per quatre vegades" appears at 89% through III.19.0 text. f75r P4 center (containing the 4-qokedy run) is at 32% through the folio. **57-point gap.** "ix vegades" at 98% vs P9 center at 85% (13-point gap).

### Phase 2: Expert pushback + interpretive correction

Initial conclusion: "strong-form Path A is dead, the testamentum matching is weak sauce." Both expert-advisor and crazy-expert pushed back hard:

- **My four falsifications targeted a stronger claim than C1971 actually makes.** C1971 claims operational-class signature matching with discriminating structural features — NOT token-level textual cipher.
- **The cold-read methodology has real rigor** I had underweighted: pre-registered structural predictions, negative-control protocol (wrong recipe III.21 → 0/7 vs correct III.19 → 8/8), tiered confidence calibration.
- **The 8/8 framing IS partly inflated** by tautological predictions (high e-depth, qo dominance, observation MIDDLEs present — true of any Currier B distillation folio).
- **The discriminating power needed direct calibration** the project hadn't done.

### Phase 3: Three calibration tests requested by experts

**3.1 Catalan cardinality baseline rate (Test A).** Scanned 189 SISMEL Catalan sub-recipes for cardinality phrases (×N vegades). Result: only 2 of 189 contain ANY cardinality phrase. **III.19.0 is the ONLY Catalan recipe with both ×4 AND ×9 in the entire corpus** (1/189 = 0.5%). Combined with f75r being the corpus-singular 4-qokedy folio (C1889, 1/82), the conjunction probability under independent random pairing is approximately 1/16,500. Look-elsewhere effect at the Catalan level is essentially zero.

**3.2 Near-miss negative controls (Test B).** Applied the 8 pre-registered predictions to 7 near-miss candidate recipes (other iterative-distillation operations), decomposed into SPECIFIC (5) vs TAUTOLOGICAL (3):

| Recipe | Total /8 | SPECIFIC /5 | Tautological /3 |
|--------|---------|------------|----------------|
| **III.19.0 (CORRECT)** | **7/8** | **5/5** | 2/3 |
| III.11.0 cohobation | 4/8 | 2/5 | 2/3 |
| III.15.0 ferment conversion | 4/8 | 1/5 | 3/3 |
| III.16.0 ferment multiplication | 4/8 | 2/5 | 2/3 |
| III.18.0 potable gold | 4/8 | 2/5 | 2/3 |
| III.22.0 fire governance | 4/8 | 1/5 | 3/3 |
| III.44.0 quicksilver coagulation | 4/8 | 2/5 | 2/3 |
| III.21.0 (EXTREME control) | 3/8 | 1/5 | 2/3 |
| III.12.0 sublimation | 2/8 | 0/5 | 2/3 |

**SPECIFIC-prediction subset is the discriminator.** Correct match: 5/5. Near-miss range: 0-2/5. Extreme control: 1/5. Tautological predictions pass ~2-3/3 across all recipes regardless (floors). Automated predictor lost 1 point on III.19.0 vs human cold-read (8/8) due to regex coverage of monitoring vocabulary.

**3.3 MIDDLE-as-morpheme NL test (Test C).** Crazy-expert proposed MIDDLEs might be arbitrary lexical units (Chinese-character-style ~80-150 closed lexicon), not compositional operational primitives. Test: compute MIDDLE distribution statistics vs natural-language morpheme distributions.

| Property | V-MIDDLEs | V-tokens | Catalan (subsample n=21,610) |
|----------|-----------|----------|------------------------------|
| Unique types | **1,302** | 4,640 | 4,393 |
| TTR | 0.060 | 0.215 | 0.203 |
| Hapax rate | 63.0% | 66.9% | 64.2% |
| Top-10 share | **49.1%** | 14.7% | 25.3% |
| Zipf slope | **−1.51** | −0.79 | −0.91 |

**Closed-lexicon hypothesis refuted by inventory size:** 1,302 unique MIDDLE types is 10× larger than the 80-150 hypothesized closed lexicon. Distribution is more concentrated than NL (top-10 49% vs Catalan 25%) and steeper Zipf (−1.51 vs −0.91). MIDDLE distribution looks operational with productive tail, not closed lexicon.

**Subtle finding:** MIDDLE hapax rate (63%) matches Catalan hapax rate (64%). There IS productive-tail behavior similar to natural language's long tail of rare words. This leaves open a more refined hypothesis (lexical-content tail vs operational productive tail) — flagged for follow-on phase.

---

## What survives, what dies

### Surviving (locked or strengthened)

- **C1971 cold-read framework** — operational-class signature matching with discriminating structural features. Reinforced by near-miss negative-control test showing 5/5 SPECIFIC vs 0-2/5 near-miss separation. Sharpened phrasing.
- **C1889 (corpus-singular 4-qokedy run)** — joint with new Catalan baseline gives joint conjunction probability ~1/16,500.
- **8D thermal profile matcher (C1366/C1888)** — operational-class identification at folio level. Not challenged.
- **Atom system (C1394/C1195)** — locked operational glosses. Not challenged.

### Dying (registered as findings, not retracted from C1971)

- **Strong-form Path A** (token-level textual cipher). Falsified at 4 levels (linear order, block structure, folio-aggregate Jaccard, anchor position). Not registered as falsification because C1971 doesn't claim what was tested.
- **Block-structure interpretation of f75r** (operation-block decomposition). Was my framework-echo; not registered.
- **MIDDLE-as-closed-lexicon NL hypothesis** (Chinese-character-style 80-150 inventory). Registered as Tier 1 falsification (C2036).
- **"Cold reads are weak sauce" framing.** Reversed in synthesis after reading the actual cold reads and negative-control protocol.

### Recalibrated (not falsified, sharpened)

- **C1971 "8/8 verified" framing** — sharpened to "5/5 SPECIFIC predictions + 2/3 tautological floors." The underlying discriminating power survives near-miss controls.

---

## Constraints registered

### C2034 — Catalan cardinality baseline (Tier 2)

III.19.0 ×4+×9 conjunction is unique in 189 SISMEL Catalan sub-recipes. Only 2/189 contain ANY cardinality phrase in Catalan (III.12 ×3, III.19 ×4+×9). Joint with C1889 (f75r corpus-singular 4-qokedy run, 1/82) gives conjunction probability under independent random pairing ≈ 1/16,500. Bounds look-elsewhere effect at Catalan corpus level to essentially zero.

### C2035 — Mantel null on folio-aggregate token similarity (Tier 2, bounding constraint)

Across 14 catalogued folios in C1971, pairwise Voynich token-set Jaccard distance is uncorrelated with pairwise matched-Latin-chapter content-word Jaccard distance. Best of 6 variants: ρ = +0.12, p = 0.14 (one-tailed positive). Operational-class signature matching does NOT propagate to folio-aggregate lexical overlap. Scope-restriction on C1971: the 8D matcher's operational-class identification is real but does not entail token-level content correspondence.

### C2036 — Closed-lexicon NL hypothesis falsified (Tier 1)

MIDDLE-as-arbitrary-lexical-unit hypothesis (Chinese-character-style closed lexicon ~80-150 morphemes) refuted by Currier B MIDDLE inventory size: 1,302 unique types in 21,610 tokens (10× larger than hypothesized range). Top-10 token share 49.1% (vs Catalan 25.3% size-matched control); Zipf slope −1.51 (vs Catalan −0.91). Distribution is operational with productive tail, not closed lexical inventory. Parallels C1976 (polyalphabetic cipher rejected) and C1376 (Currier B not NL).

### C1971 — Phrasing sharpening (not a new constraint)

Add methodology note: discriminating power resides in pre-registered SPECIFIC predictions (5 of 8 in f75r protocol); TAUTOLOGICAL predictions (3 of 8 — heat intensity, procedural complexity, monitoring presence) are floors that any iterative-distillation Currier B folio passes. Near-miss negative controls (other distillation recipes) score 0-2/5 SPECIFIC vs correct match 5/5. The 8/8 cold-read framing is correct but inflated; the underlying separation is at the SPECIFIC-prediction layer.

---

## Methodology lessons

1. **Two interpretive overshoots in one session.** First overshoot: "strong-form Path A is real, run a known-plaintext attack" — failed at 4 tests. Second overshoot: "the cold reads are weak sauce" — reversed after reading the actual protocol. The discipline that catches both: actually read what the existing framework claims before testing or before dismissing.

2. **`feedback_specific_vs_tautological_predictions.md`** added to methodology memory. The 8/8 cold-read framing is correct but should be decomposed into SPECIFIC (genuine discriminators) and TAUTOLOGICAL (floors). All pre-registration protocols going forward should distinguish these.

3. **Expert pushback as iterative correction.** Both experts identified gaps in my reasoning that the data confirmed. Specifically: (a) baseline rate not computed, (b) negative control rigged by extremity, (c) closed-lexicon NL hypothesis untested. All three were resolvable with concrete tests. The session arc — overshoot → expert pushback → retest → register only what survives — is exactly the discipline `feedback_mechanism_cycle_procedural_ceiling.md` describes working at the procedural ceiling.

4. **Mantel null is the most under-appreciated finding.** Negative results that bound interpretation are higher-EV than positive structural measurements at this project stage. C2035 should be referenced any time someone asks "does the matching catalog mean texts are decoded?" — answer: no, the matching is at the operational-class level, not the lexical level.

---

## Deferred (next phases)

### PHASE_699 candidate: Hapax MIDDLE concentration test

Crazy-expert proposed: per-folio hapax MIDDLE concentration vs frequency-matched non-hapax. If hapaxes are 3×+ more folio-concentrated than frequency-matched controls, lexical-content-tail interpretation wins over operational-productive-tail interpretation. C914's 3.7× label enrichment is the precedent. This test would discriminate between "operational productive tail" and "lexical content tail (specific materials/parameters/names as one-off MIDDLE forms)" — a substantive alternative to the framework's current characterization.

### PHASE_700 candidate: Computus tables alternative-class adversarial test

Crazy-expert proposed: test Voynich MIDDLE distribution against computus tables (paschal/calendrical computation). C2032 established Voynich has structured sequential autocorrelation absent in NL; computus tables have known structured number-sequence autocorrelation (epact cycles, 19-year/28-year periods). If MIDDLE distribution matches a computus corpus signature, that's a structural alternative-class hit; if not, it's a clean falsification of one more alternative class. External adversarial corpus is the kind of test that breaks through the procedural ceiling.

---

## Scripts

| Script | Purpose |
|--------|---------|
| `_reconnaissance.py` | Initial scale-ratio analysis (412 Voynich tokens vs 707 Latin / 965 Catalan words in III.19) |
| `_operational_phase_alignment.py` | Per-line 4D thermal profile for f75r + Latin phase profiles |
| `_profile_matching.py` | Voynich line ↔ Latin phase profile matching (Spearman −0.80) |
| `_qok_peak_blocks.py` | qok-density peak detection + operational block context |
| `_block_structure_controls.py` | Within-folio shuffle null on qok-peak block structure (p=0.63) |
| `_mantel_voynich_latin.py` | Mantel-style folio-aggregate Jaccard correlation (6 variants) |
| `_paragraph_subrecipe_counts.py` | Voynich paragraph count vs SISMEL sub-recipe count comparison |
| `_f75r_subrecipe_anchor_check.py` | Locate ×4 and ×9 in III.19 sub-recipes |
| `_f75r_positional_anchors.py` | Position of cardinality phrases in III.19.0 text vs Voynich paragraph positions |
| `_cardinality_baseline.py` | Test (a): Cardinality baseline rate across 189 SISMEL sub-recipes |
| `_middle_as_morpheme_nl_test.py` | Test (c): MIDDLE distribution vs NL morpheme statistics |
| `_near_miss_negative_controls.py` | Test (b): Apply 8 predictions to near-miss recipes, SPECIFIC vs TAUTOLOGICAL |

---

## Origin

User-prompted exploration of Path A (known-plaintext attack) starting with operational profile alignment between f75r and SISMEL Part III canonical text. User explicitly noted: "the 4x and 9x qok tokens were discovered AFTER 8d matching associated f75r with that recipe" — the 8D thermal profile is what made the match; cardinality anchors were corroborative not foundational.

User-driven correction at "do you still feel like these folios are hiding some natural language?" forced a fresh read of the cold-read protocol and revealed the interpretive overshoot. User-driven correction at "consult with the experts" enabled the calibration phase.

Both expert agents (expert-advisor and crazy-expert) flagged convergent gaps that the three calibration tests resolved.
