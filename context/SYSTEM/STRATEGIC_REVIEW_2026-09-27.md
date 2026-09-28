# Strategic Review — 2026-09-27 (post model upgrade)

**Status:** CURRENT forward plan. Supersedes the v7.17 (2026-06-03) "forward discovery exhausted / external
channels foreclosed / consolidate" framing, which the user ruled out (memory:
`feedback_never_declare_exhausted_until_understood`). Structure is mapped; referents are unrecovered; the
semantic character of Tier 0 is now under adversarial test.

**Inputs (this session):** expert-advisor (full interpretive layer, 2 rounds), lean-expert (constraints +
statistics only, 2 rounds), crazy-expert (unguarded generation), an external literature scout, and two
read-only repo audits (open threads / drift; load-bearing constraints / audit coverage). Differential rule
applied: where expert-advisor and lean-expert diverged, the divergence is recorded with its resolution.

---

## 1. Verdict

1. **The foundation is less audited than the registry claims.** Of the 43 most-cited live constraints,
   34 were never re-examined under a modern null; the unaudited mass sits in the atom/category layer at the
   top of the citation graph. The v7.17 "audits essentially done" call was premature.
2. **Several atom-layer constraints are EVA-orthography restatements** (new failure pattern:
   *transliteration-unit artifact*). EVA writes single glyphs as letter strings (ch, sh, ckh, cth, cph,
   cfh; in, iin, ain, aiin, ir, air), so letter statistics inside those strings are identities of the
   transliteration: C1440 (h "transparent": h never stands alone), C1209 (n terminal: final form), C1207
   ({c,h} r=+0.75 is the bench ligature; {a,i,n,r} is the minim-group family), C1484, C521's "e→h = 0.00".
3. **Tier 0 has never faced an external generator of *meaningful* Voynich-like text.** PCA-v1 was an internal
   contract-composition audit. The only external generator ever run is Timm & Schinner (C2077). The Naibbe
   verbose homophonic cipher (Greshko, *Cryptologia* 2025, public code) received only a desk review
   (`phases/NAI_naibbe_investigation/`, 2025-12-31); the generator was never run. No sub-lexical
   (verbose/homophonic/syllabic) cipher class has been tested: C1976 tested polyalphabetic substitution at
   the atom level, C2035 folio-level lexical correspondence, C2036 a closed lexicon.
4. **Content and encoding are separate questions.** The Testamentum-tradition *content* reading and the
   "operational notation, not encoded prose" *encoding* claim are supported by different evidence. The
   rival-generator test threatens only the encoding half; a verbose cipher of a distillation text would
   still be a distillation text, and one that is potentially decipherable.
5. **The registry and agent inputs have drifted.** Expert agents are fed demoted/superseded constraints as
   live Tier 2, "ANALYSIS CLOSED" banners, a hard-coded stance citing demoted C973/C982/C458, contracts
   citing C783/C1118/C470/C475/C476/C481/C433–435, and a stale crazy-expert stance (content stops at C1642).
   `CORE/frozen_conclusion.md` still asserts "100% coverage", "17 transitions in 5 hazard classes",
   "0 violations" (C2063 counts 13) and a tainted "0.19% reference rate".

## 2. Source correction found during the review: III.19 says "four times, OTHERWISE nine times"

The SISMEL Catalan III.19 (Pereira–Spaggiari 1999, p. 411, f. 63va), checked against the page scan
(`sources/sismel_testamentum/scans/sismel_testamentum_286_R.jpg`), reads:

> *"e aquesta distillació e fermentació reitera en renovellant la bresca a cascuna segona distillació per
> quatre vegades **aliter** ix vegades."*

= "repeat this distillation and fermentation, renewing the comb at each second distillation, **four times,
otherwise nine times**." The editor prints the manuscript's own *aliter* doublets in bold (compare line 9:
"picada **aliter** *broicé e triblé*"), and the introduction's list of *aliter* readings has
"per quatre vegades aliter .ix. vegades III.19, 7".

The phrase quoted across the project, *"per quatre vegades aliter broicé e triblé; e aprés ix vegades"*
("…and afterwards nine times"), is an **OCR splice**: "broicé e triblé; e aprés" belongs to the capon
passage three lines lower. There is no "and afterwards nine times" in III.19. Consequences:
- ×4 and ×9 are **alternative counts for one repeated step**, not two sequential phases. This also explains
  why each Latin stream kept only one count: the tradition carried a variant, and the Catalan scribe kept both.
- Readings built on two phases are void: PHASE_650's "×4 first, then ×9"; PHASE_751's "×9 high-fire
  rectification" framing of f75r; expert-advisor's round-1 "×4 phase / ×9 phase" enactment kill (withdrawn in
  round 2); PT-CA-1's "two different axes" (PT-CA-1 caught the *aliter* line but treated the spliced OCR text as
  a second, genuine occurrence).
- **Unaffected:** C2034's statistical fact (III.19 is the only Catalan sub-recipe mentioning both 4 and 9) and
  C1889's corpus fact (f75r is the only B folio with a ≥4 identical-token run).
- **Encoding note:** "four" is written as the word *quatre* (Latin 1566: *quater rectificatam*), nine as the
  numeral *ix*. A letter-level cipher of "quatre" yields six different letters, not four identical tokens.
  So if f75r encodes III.19, its ×4 run is iconic repetition, not an enciphered numeral. This bears on the
  encoding fork but is conditional on the correspondence being real.
- **Anchor pricing (both experts):** the registered "≈1/16,500" multiplies in the ×9 window, which C1969
  itself says is not a count (f86v3 and f108r reach the window with no count in their recipes) and which was
  the third operationalization tried (Phase 657 NULL, 658 INCONCLUSIVE). Honest pricing: the ×4 leg
  (selection-safe p≈0.10) × the Catalan "quatre vegades" base rate (1/189), before search multiplicity.
  Anchor class retained; headline number and two-phase narrative corrected.

## 3. Consensus priorities (execution order)

| # | Work | First concrete step | Kill / gate |
|---|---|---|---|
| 1 | **Registry-integrity pass** | Reconciliation script diffing INDEX status, generated table, contracts, agent inputs, frozen_conclusion; fix at source; register P726/P727; strip closure banners; refresh crazy stance; regenerate | n/a (bookkeeping) |
| 2 | **C957 three-null screen** (the surviving hazard layer) | Re-run the screen with candidates defined on within-line expectation (E≥5; sensitivity E≥3) and 1,000 zone-preserving within-line shuffles; then an edge-glyph-matched generator; then cross-track/uncertain-space checks on survivors | C957 stays a mechanism statistic only if the zero-cell count exceeds all three nulls |
| 3 | **Units/orthography gate** | Glyph-unit re-tokenizer (ch, sh, cth, ckh, cph, cfh, iin/in-groups, ee handling as declared variants); re-run C521, C1207, C1209, C1440, C1484 and the e-run family on glyph units and against a within-token character n-gram null; UN merge-split test | A claim that vanishes under re-tokenization or is reproduced by the within-token n-gram is spelling, not grammar |
| 4 | **Reconcile C2032** | Commit `PHASE_691/NL_SYLLABLE_TEST_RESULTS.md` + script; re-run C2031's frozen definitions on all of B, all of Section B and the matched subset; report lag1, lag2, lag2−lag1 with N-matched CIs (drop r21 as primary) | If Section B does not show lag2−lag1>0 with CI excluding 0, rescope C2031/C2032/C2053 to "matched subset, unreplicated" |
| 5 | **Rival-generator panel** (Naibbe first, Rugg grille second; Timm and M2 fixed members) | Implement Naibbe from published code on ≥3 plaintexts (Latin recipe: Testamentum/Codicillus; Latin pharmacy: Mesue; Italian prose); cheap statistics first: edge-glyph MI, identical-run distribution, zero-bigram screen count, repeat sparsity (C1790), order-information budget vs positive controls | **No kill evaluated until #2–#4 report.** Exclusion rule (lean): B outside the generator ensemble's central (1−0.01/k) interval on ≥2 certified discriminators under every declared plaintext×layout variant, and M2 contains B |
| 6 | **Testamentum text side** | ×4∧×9 regex in the native languages across Rupescissa, pseudo-Lull Latin, Codicillus, Brunschwig, Mesue, Antidotarium (genre baseline); numeral→signature rules frozen before any forward scan; prospective anchors on unexamined recipes | Specific-text claim rises only if the conjunction stays rare at genre level and a forward anchor is hit above the base rate |
| 7 | **Codicology (PHASE_752 v2) for Malta (video due 2026-11-09)** | Pipeline negative control first: run the unchanged pipeline on the Aberdeen Bestiary (known collation, continuous text), prediction locked; then second transcription track (ZL3b); then the side-of-flat-sheet contrast pooled across quires | Register a bifolium constraint only if re-pairing p<0.01 in ≥2 of 3 strata, both tracks, after length residualization |

### Progress (updated 2026-09-27, same session; branch `strategic-review-2026-09`)
| # | Status | Outcome |
|---|---|---|
| 1 Registry integrity | **DONE** | Generator fixes (demotions visible at Tier 3, dead rows never re-imported, silent tier default fixed); v6.90 dispositions applied; P726/P727 registered; banners withdrawn; frozen_conclusion facts corrected; contracts stamped; `scripts/registry_integrity_check.py`; CHANGELOG v7.22 |
| 2 C957 screen | **DONE (PHASE_753, PHASE_756): REDUCES** | Joint null (line composition + zones + per-section edge counts; MCMC β = 2, diagnostics passed): 2 zeros vs 1.98 expected (p = 0.60). C957 superseded by the reduction row C2081; the raw residual (5 vs 2.0, p = 0.054) is carried by pairs the F transcription attests. No hazard/prohibition layer survives beyond known effects |
| 3 Units/orthography gate | **RUN (PHASE_754, PHASE_758)** | PHASE_754: C1440, C1209, C1484, C1207, C521 PARTLY ORTHOGRAPHIC (glyph facts retained). PHASE_758: e-run length read consistently across tracks (κ 0.95–0.96; F under-reads 4.7% of 2+ runs); C1225 a SEGMENTATION ARTIFACT of the pre-C1957 parser (glyph fact kept: longer e-runs → more y, script-wide); C2031 and C1967 TRACK-ROBUST. Remaining: C1394 slot model |
| 4 C2032 reconciliation | **RUN (PHASE_755)** | Locked verdict LENGTH-CONFOUNDED: Section B alternates (D +0.028, CI excludes 0) but the B-vs-S divergence is not shown within equal-length strata. C2031/C2032/C2053 rescoped. Records the unregistered 2026-05-16 length-stratified FAIL |
| 5 Rival panel (Naibbe) | **DONE (PHASE_757): EXCLUDED** | Locked verdict EXCLUDED on all 64 variants (both code versions × 4 plaintexts × 2 layouts × 2 spacing × 2 noise; 1,000 members each): D2 edge coupling, D3 repetition, D6 line zones outside in 64/64; D5 order information (B lower than every variant) 51/64; holds with D2 removed. Registered C2080 (negative knowledge); scope notes on C119/C120/C171/C173. Next in this line: Rugg grille; a modified-Naibbe or coarser-unit cipher would be a new test |
| 6 Testamentum text side | **Audit DONE (PHASE_762)**; genre baseline and prospective anchors pending | The 8D chapter matching carries no correspondence signal (no source beats its own shuffled features); recto/verso adjacency and section mapping do not reproduce; the C1887 permutation test is uninformative. C2052 triage applied (20 rows → Tier 3). Remaining: an f75r coincidence budget, then a prospective test |
| 7 PHASE_752 v2 / Malta | **Step 1 DONE (PHASE_759)**; steps 2–3 pending | Aberdeen negative control SPECIFIC: no sheet effect in a continuous-text codex (p 0.34 / 0.44), strong facing continuity (p 0.0001), planted effect detected, not underpowered. Voynich (H, residualized): herbal pure-A p 0.0007, Q13 0.013, Q20 0.017 — only 1 of 3 strata < 0.01, so the gate is not met on H. Contrast for Malta: Aberdeen shows continuity and no sheet effect; Voynich shows a sheet effect and no continuity |

Also queued (lower priority or externally dependent): label grounding with blind image coding (re-transcribe
labels from IIIF first; C2004/C2005 gaps); scribal corrections as the writers' own error model; blind
practitioner raters with decoy profiles (External Corroboration Protocol, redesigned); f57v key-table test;
A-herbal alphabetical-order test; material-set enrichment scan with a frozen label ledger; reversal
statistic for the "closed-loop" wording of Tier 0.

## 4. Divergences and resolutions (differential check)

| Item | expert-advisor | lean-expert | Resolution |
|---|---|---|---|
| f75r ×9 window as a cipher kill ("K4", name collides with C2077's K4) | Round 1: decisive enactment kill. Round 2: **dropped** (contradicted C1969) | Circular, N=1, forking paths (×3); not a kill | Dropped. Replaced by generic run-structure statistics (identical-run distribution; per-folio max qok-window density; joint count) and EA's line-break-continuity statistic (K4*). The divergence showed interpretation, not statistics, had carried the round-1 verdict. |
| C957 as a kill | Round 1: "sharpest kill"; round 2: agrees P≈5e-17 is post-selection; gated | Original screen-level shuffle (9 vs 0.6±0.8) is the right statistic, probably the wrong null class | Gated by the three-null screen (#2). Never quote 5e-17 again; the valid statistic is the screen-level zero-cell count. |
| Davis scribe as a stratifier | Weakened by Timm (2026) "five hands collapse onto A/B + labels"; verify hands from letterform alone | Scribe as mandatory stratum | Treat "scribe" as a quire/section grouping until hands are verified by letterform-only paleography. |
| Newton chymistry notebooks | Positive control for notation | Not a positive control (assumes the hypothesis); use as a same-hand operational vs non-operational comparator | Lean's framing adopted. |

## 5. Retire (as evidence or at current tier; rows are annotated, not deleted)

- Closure banners and certification language: "ANALYSIS CLOSED", "Structural work is DONE", "Core model CLOSED
  (PCA-v1 passed)", "Characterization program COMPLETE", "definitively irrecoverable", "May Never Be Answerable".
- 8D matcher top-1 / ratio-confidence evaluation (C2026) and match breadth as content evidence (C2052).
- C1971 cold-read coherence as evidence (self-scored, no blind decoys; a floor); C1956 (post-hoc dimension selection).
- Class-level hazard vocabulary: "the 17", the 5 hazard classes, ENERGY_OVERSHOOT (C783 demoted, C2060). The hazard
  layer is C957's token-level zeros, pending #2.
- REGIME as 4 crisp classes and REGIME = Brunschwig fire degree (C1712, C2070; the gloss absorbed a sign flip in C1872).
- Category-as-unit analysis in new work (C2069); MARKING-dependent results until recomputed.
- The Puff–Voynich "83:83 isomorphism" / "19/20 full procedural alignment" (INTERPRETATION_SUMMARY §X).
- C322 "SEASON-GATED WORKFLOW" at Tier 2 (lineage of the retracted C1681–C1688; C2068: the zodiac is winterless).
- Tier-4 etymology tables (Kochen/Erkalten/Coquo) in agent contexts.
- C157 "uniquely compatible (100%)" framing; C090 (4-cycles are a floor for a diameter-1 graph); C196/C197
  (invented archetype); C212/C164 at Tier 2 (no base-rate null); C2024 at Tier 2 (look-elsewhere).
- The virtual-apparatus family (C1581–C1680) as manuscript knowledge (crazy-expert R1: plant responses are keyed
  to imposed categories; knowledge about our simulator). Move to a model-diagnostics appendix pending review.
- r21 (lag2/lag1) as a primary statistic; chi² for cross-layer coupling; configuration-model nulls on co-occurrence graphs.

## 6. Rework

- **frozen_conclusion.md supporting facts:** coverage = 69.5% of B tokens (100% of the grammar's own 480 types;
  HT/UN defined by exclusion, C740/C566); hazard layer = token-level zeros (C957, pending #2), class-level
  demoted (C783), classes imposed (C2060), real corpus has 13 class-level violations (C2063); "convergence"
  reframed as occupancy/thematic dominance (C1401–C1403); "not a language / not a cipher" scoped to the
  classes actually tested (verbose/homophonic untested). The Tier 0 sentence itself is unchanged pending #5.
- **C119/C120/C173/C171:** scope to hypothesis classes actually tested ("exclusions tested token≈word encodings;
  sub-lexical encodings untested").
- **C124:** state the denominator. **C074/C079/C084/C323:** reword "convergence" to occupancy per C1402/C1403.
- **Atom grammar (C1394–C1560):** separate glyph orthography from distributional structure after gate #3; strip
  operational glosses from orthographic items (ATOM_GLOSSES in `scripts/voynich.py` are role hypotheses, not facts).
- **Section/REGIME family** (C2028, C2031, C1994/C1995, C1999, C1404, C2024): within-scribe (or within-quire)
  N-matched contrasts; lag2−lag1 instead of r21.
- **Order family** (C361, C369, C370, C1839, C1977, C1936, C161): decompose by physical relation (same leaf,
  conjoint, facing, consecutive leaf) under the re-pairing null; do not assume binding order is authorial.
- **Matcher family (C1882–C1956, C1971–C1975):** finish the per-constraint triage C2052 queued (reserved
  "PHASE_719", never run); P726 (English-translation featurization) and P727 (6/27 counts not reproduced).
- **Measurement/gloss split:** C1195, C1196, C1934, C1388–C1392, C1925, C1926, C1958, mapping clauses of C929/C931.
- **Contracts:** regenerate from live constraint status (BCSC HAZARD_TOPOLOGY_FIXED cites C783/C1118; CASC cites
  C475/C476/C481; AZC-ACT cites C433–C435; AZC-B-ACT's headline cites C470).
- **C2077:** re-score K2 and K4 under noise parity and e-run invariance.
- **RIGOR_AND_FAILURE_TAXONOMY v1.1:** add transliteration-unit artifact, wrong unit of comparison (Voynich tokens
  vs Latin words, not letters), physical-layout shadow, binding-order confound, strawman rival, fit-on-real-data-only
  (own-partition refit), noise-parity asymmetry, scope overreach, OCR-splice (source-reading error).

## 7. Method upgrades adopted as working rules

1. Test ledger: every confirmatory test logged (script hash, family, null, kill, α, outcome incl. failures);
   external timestamping for major pre-registrations.
2. Sheet-blocked cross-fitting for anything fitted (partitions, classifiers, matchers, gloss tables). There is no
   untouched holdout after ~750 phases; new *channels* (second transcription, images, external corpora, generator
   panels, prospective anchors) are the only genuinely out-of-sample evidence.
3. Own-pipeline refit nulls (refit fitted partitions on each null corpus); screen-level nulls for any "we found k
   zeros/enrichments" claim; noise parity when comparing real B with synthetic text.
4. Bounded nulls: every null reports its minimum detectable effect; no "absent/epiphenomenal/exhausted" beyond it.
5. Split measurement rows from gloss rows (Tier 2 measurement + Tier 3 gloss).
6. Scribe/quire as a mandatory stratum; transcription-uncertainty bootstrap; no ratio statistics near noise floors.
7. MDE planning: folio-level Spearman at n=82 detects ρ≈0.31 (α=.05) / 0.39 (α=.005); half-sample 0.43/0.53.
   Folio-level effects near ρ≈0.3 cannot be confirmed out of sample at this N — carry them as estimates.
8. Echo audit: self-published "procedural operator" readings (e.g., Honeycutt on Zenodo, "31 operator classes,
   77 forbidden pairs") are an echo risk, never corroboration, unless methodological independence is shown.

## 8. External resources (scout, verified 2026-09)

- **Naibbe:** Greshko, *Cryptologia* (online 2025-11-26), DOI 10.1080/01611194.2025.2566408 (CC BY 4.0); code
  github.com/greshko/naibbe-cipher (modified MIT, cite the paper); Zenodo 17219445. Tuned on Currier B; known
  failures: line-as-unit effects, rare-type tail (41% vs 70% single-occurrence types), edge-glyph coupling
  (0.006 vs 0.197 bits reported).
- **Rozanova & Temerev**, arXiv 2608.17096 (MIT code, github.com/lrozanova/voynich-units): EVA glyphs are not
  letters; tokens are not words; uncertain spaces are mostly word-internal (AUC 0.905 from page coordinates);
  harness includes Naibbe and Timm ports.
- **Parisel**, arXiv 2604.19762 (RF1b-e): right-to-left structure within words, left-to-right across boundaries;
  public grille code (github.com/labyrinthinesecurity/currier-signatures).
- **Timm (2026)**, "One Hand, Five Labels" (Zenodo 19009571): contests Davis's five-hand attribution.
- **Transliterations** (voynich.nu/transcr.html): ZL3b (2025-05-13), RF1b-e, GC2a (v101), CD2a (Currier), FG2a,
  IT2a; IVTFF page headers encode quire, page, bifolio position and Davis hand.
- **Beinecke IIIF** manifest 2002046 (213 canvases; f1r 2,972×3,766 px ≈420 ppi). 2014 multispectral (10 pages,
  mostly marginalia; released 2024). McCrone 2009 report (public PDF).
- **Controls:** Aberdeen Bestiary (published collation + transcription); BnF lat. 6741 (Alcherio recipes kept as
  loose bifolios; Merrifield 1849 OCR); BnF Fr. 640 (Making & Knowing XML; gatherings must be reconstructed);
  Newton chymistry notebooks; Gaskell & Bowern human-gibberish corpus (github.com/danielgaskell/voynich).
- **Voynich 2026** (Malta, online, 2026-12-09; proceedings CEUR-WS): programme not yet published; chair
  C. Layfield co-authored the singulion paper that PHASE_752 replicates and critiques.

## 9. Sequencing against the one external date

Malta video deadline 2026-11-09: (1) PHASE_752 v2 with the Aberdeen negative control and the second track;
(2) a public, timestamped Naibbe pre-registration; (3) the best-of-N critique of the singulion reorderings.
