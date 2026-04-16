# Pending Tests and Informal Findings

Informal observations and exploratory results awaiting formal testing. These are NOT constraints — they are hypotheses generated from casual analysis that need rigorous validation before entering the constraint system.

**When to promote:** A finding moves from here to a proper phase when (1) we have the data to test it rigorously (e.g., SISMEL Catalan text arrives), or (2) we design a proper statistical test with controls.

**When to delete:** If a finding is formalized as a constraint or falsified by a proper test, remove it from this file.

---

## Awaiting SISMEL Catalan Text

### PT-001: Paragraph-level atom profiles track recipe stages
- **Observation:** On f79r (Ch12M) and f83r (Ch9P), per-paragraph e_depth, prefix distribution, and atom class ratios correspond to known recipe steps.
- **Key examples:** f79r P3 (harshest heat, e_depth=0.34) = "substance of fire" step. f79r P7 (zero thermal, sh-dominant) = "watch for reddishness." f83r P3 (ot=8 peak) = drip-counting phase.
- **Test:** Repeat across all matched folios using Catalan recipe text for step-level alignment.
- **Session:** 2026-04-11

### PT-002: dar count tracks material introduction events
- **Observation:** f79r has dar=3 at 3 material-handling moments. f75r P9 has dar=7, Brunschwig's composita lists 7 herbs in second batch.
- **Concern:** The 7/7 could be coincidence. Testamentum Ch19 uses honey+wax (2 ingredients), not 7 herbs. May indicate workshop variant rather than Testamentum match.
- **Test:** Check dar counts against Catalan recipe ingredient lists across all matched folios.
- **Session:** 2026-04-11

### PT-002b: Systematic dar/dal count vs recipe material events (21 folios)
- **Observation:** dar count tracks distinct material introduction events across all 21 matched folios. dar=0 folios (f108r, f112r, f112v, f76v, f77r) ALL encode recipes that process existing material without new additions (separation, cohobation, conversion, rectification). dar>=5 folios (f84r=13, f75r=10, f76r=7, f77v=5, f116r=5) ALL encode multi-ingredient recipes. f79r dar=3 maps to exactly 3 material moments in Ch12M.
- **dal pattern:** f77v has dal=10 (highest) — furnace specification = careful placement/arrangement of materials, not vigorous introduction. dal = passive transfer, dar = active introduction.
- **Status:** Strongly supports C1925 across full matched set. Approaching constraint-ready but Catalan text would allow per-step verification.
- **Session:** 2026-04-12

### PT-003: `dalkeeey` encodes maximum gentleness at physically dangerous step
- **Observation:** Hapax legomenon (unique to f79r), e_depth=3 (maximum), appears at P4 L21 where recipe says "return water over Mercury" — the most thermally dangerous step.
- **Test:** Check whether other e_depth=3 tokens appear at recipe-predicted danger points on other folios.
- **Session:** 2026-04-11

### PT-004: Testamentum as complementary text vs source tradition
- **Observation:** The folio is operationally denser than the recipe (~50 tokens per recipe sentence). The recipe provides material identity and sequence; the folio provides control logic. They're complementary.
- **Question:** Is the Testamentum itself the working reference, or did the workshop have a modified version? The 7 dar vs 2 Testamentum ingredients suggests possible workshop variant.
- **Test:** Compare Catalan recipe detail level against folio density. If Catalan has enough detail for step-level alignment, it's the complement. If it's still terse, the complement is a lost workshop document.
- **Session:** 2026-04-11

---

## Hazard Topology

### PT-005: FL_HAZ clusters at material handling phases, not high-heat phases
- **Observation:** Across f79r, f83r, f75r — FL_HAZ tokens concentrate at material introduction and active intervention steps, not at steady-state heating. f79r P4 (return water, 3.9% hazard) vs P2 (strongest fire, 2.9%). f75r P9 (7 dar additions, 8.3% hazard) vs P3 (first distillation, 0%).
- **Interpretation:** Disfavored transitions encode "wrong action at wrong time during material handling," not "dangerous temperature."
- **Test:** Formalize across all matched folios. Check whether FL_HAZ rate correlates with dar density rather than qo density.
- **Session:** 2026-04-11

---

## Suffix Mode A/B

### PT-006: Mode A/B correlates with specification vs active intervention
- **Observation:** Across f79r, f83r, f75r — Mode A (100%) dominates setup, monitoring, quality tests, and routine distillation passes. Mode B appears at active intervention steps (material handling, fire adjustment). Highest interleave rate maps to most complex/dangerous operations.
- **Key example:** f79r P4 (return water, A%=62%, interleave=43%) vs P7 (watch color, A%=100%, interleave=0%).
- **Test:** Formalize with Catalan recipe verb classification: specification verbs (posa, guarda) should map to Mode A lines, action verbs (fortifica, destil-lar) to Mode B lines.
- **Session:** 2026-04-11

---

## HT / Line 1 Content

### PT-007: Line 1 compound tokens encode recipe-identifying information
- **Observation:** fch (mercury marker) appears in line 1 compound tokens on mercury recipe folios (f78v, f76v). cs appears on gold/silver folios (f82r, f83r, f84r). Complex compound tokens on f76r encode test apparatus.
- **Test:** Check whether line 1 fch/cs presence predicts recipe type across all matched folios.
- **Session:** 2026-04-11

### PT-008: fch = mercurial solvent marker (not specific to mineral mercury)
- **Observation:** fch appears on 25% of Section H (herbal) folios, not just pharma. e_depth differs by section: B=0.86 (gentlest, mineral Hg), H=0.57 (harsher, alcohol extraction), S=0.63 (transmutation). Section H fch tokens have more ch-prefix (active checking).
- **Interpretation:** fch marks "volatile mercurial solvent requiring flagged caution" — mineral mercury (Section B/S), vegetable mercury/alcohol (Section H), or animal mercury/ammonia. Section H split: 25% alcohol extraction, 75% water/steam distillation.
- **Test:** Check whether Section H fch folios have different thermal profiles from non-fch herbal folios (consistent with alcohol vs water extraction).
- **Session:** 2026-04-12

---

## Brunschwig Comparison

### PT-009: f75r thermal arc vs Brunschwig composita procedure
- **Observation:** f75r's 9 paragraphs show declining e_depth (0.63 to 0.42) across distillation passes, then quality test (P7, e_depth=0.18 with zero heat), then rebound for final phase. Brunschwig's composita uses constant gentle balneum throughout.
- **Concern:** Found "strong matches" to both simplex (declining fire) and composita (constant gentle fire) recipes — post-hoc rationalization risk.
- **What's solid:** P7 zero-heat quality test, chekar at P9, 4x qokedy cohobation run, ~9-10x heat cluster matching 9x reflux.
- **Test:** Retest with Catalan Ch19 text for definitive recipe alignment.
- **Session:** 2026-04-11

---

## Structural Predictions Confirmed (for reference)

14 pre-recipe structural predictions confirmed, 0 refuted (session 2026-04-11 audit):
- Section B = balneum heating (Phase 385)
- Section S = different operational type (Phase 385)
- REGIME-degree mapping (Phase ~419)
- f75r = iterative recipe (Phase 22-23)
- Bathing figures = vessels in water baths (Phase ~355)
- f77r/f82r = most forgiving folios (Phase 23)
- REGIME_4 = precision not forbidden (Phase ~419)
- Galenic org-level yes, recipe-level no (Phase 377)
- Verb-level notation granularity (Phase ~100-200)
- fch=mercury, cs=gold hard-filter (Phase 637)
- Three-class dark pipeline taxonomy (Phase 637)
- Brunschwig recovery architecture (Phase ~355)
- Three-level operational hierarchy (Phase 462)
- Section-MIDDLE alignment k vs e (C909)

3 untested (non-Testamentum content): f57r restart protocol, Section H herbal, f31r rosewater.

---

## Herbal Section Source Text

### PT-010: Alchemical herbals as Section H source tradition
- **Observation:** Voynich herbal page layout (one plant per page, short text paragraphs) matches "alchemical herbals" — Northern Italian 15th century manuscripts that combine Tractatus de herbis plant illustrations with alchemical/distillation recipes. These are the ONLY known medieval manuscripts with the same page layout as the Voynich herbal section.
- **Key source tradition:** Circa Instans (Platearius, 12th c. Salerno) → Tractatus de herbis (14th c., added illustrations) → Alchemical herbals (15th c., added operational recipes). The Voynich sits at the endpoint of this tradition.
- **The gap:** The original Circa Instans has therapeutic uses but no distillation. The later alchemical herbals add operational content but aren't transcribed/translated — they exist as physical manuscripts in European libraries.
- **Potential resources:** Monica Green's English translation of Circa Instans (Academia.edu PDF). Compendium Salernitanum (Morgan Library MS M.873, 488 plant drawings, N. Italy 1350-1375). Tractatus de herbis Egerton 747 (British Library, SISMEL critical edition 2009).
- **Test:** When pharma matches are confirmed, pivot to herbal section. Compare Section H folio thermal profiles against Circa Instans preparation methods (which part used, preparation type) to see if token profiles distinguish root extraction from flower distillation from seed pressing.
- **Session:** 2026-04-12

### PT-011: Section H fch split = alcohol vs water distillation
- **Observation:** 25% of Section H folios have fch on line 1, 75% don't. fch = mercurial solvent marker. In herbal context, vegetable mercury = alcohol (aqua vitae). Prediction: fch herbal folios encode alcohol extraction (macerate in aqua vitae), non-fch encode water/steam distillation.
- **Supporting evidence:** Section H fch tokens have lower e_depth (0.57) than Section B (0.86) — harsher handling consistent with alcohol vs mineral mercury. Section H fch tokens have more ch-prefix (active checking) — consistent with monitoring alcohol extraction.
- **Test:** Compare thermal profiles of fch vs non-fch herbal folios. If fch folios show different apparatus signatures, monitoring patterns, or temperature profiles, the split is real.
- **Session:** 2026-04-12

---

## Catalan-Grounded Glosses (2026-04-16)

### PT-013: Recipe-grounded token definitions from Catalan Ch9P alignment
- **Method:** Aligned 20 Catalan operational steps from Ch9P (Buosi-Moncunill thesis) against f83r P3 tokens. Each Catalan instruction pinpoints what specific tokens mean at that recipe step.
- **10 upgraded definitions:**

| Token | Old (structural) | New (Catalan-grounded) | Cross-folio |
|-------|------------------|----------------------|-------------|
| qokaiin | deep sustained cyclic heating | heat-source: sustained contained form (apply heat while sealed/bound) | 15/15 consistent (see PT-014) |
| qokal | heat to completion | fire reached target — heat stage done | 10/10 |
| otal | transfer rate: yield to state | note the output rate (drips or melt-flow) | 8/10 (broadened from "drip count") |
| dal | careful passive placement | carefully collect distillate / careful placement | 9/10 |
| qokchedy | heat with careful monitoring | adjust fire while watching | 3/3 |
| ram | respond arrange final | stage done — note result | 4/4 |
| lchedy | check equipment state | check apparatus (seals, receiver, furnace) | 8/10 |
| qokedy | apply standard heat | maintain current fire level | 10/10 |
| qokeedy | gentle balneum heat | gentle fire — balneum/sawdust level | 10/10 (28x on f108v pure balneum) |
| shedy | passive monitoring | watch the distillate (clarity, fumes, color) | 10/10 |

- **Cross-folio validation:** 8/10 definitions work without modification on all matched folios. 2 needed broadening (qokaiin: "strengthen" too specific for maceration folios; otal: "drip count" too specific for fusibility folios).
- **Key finding:** The Catalan instruction "obra-li lo pertuis quant l'oiras soflar" (open hole when you hear hissing) has NO corresponding token — confirming C1056 (sensory judgment not encoded).
- **Status:** Preliminary. Full alignment across all Catalan-available chapters (Ch1-12P, Ch1-14M) needed. SISMEL book will provide additional recipe text for expanded alignment.
- **Session:** 2026-04-16

### PT-014: f82r / Ch22M validation — 10/11 glosses hold on different operation class
- **Method:** Aligned f82r (275 tokens, 4 paragraphs) against Ch22M (Lunaria maceration, 3-day sealed) — a different operation class than the f83r P3 distillation that produced PT-013. Maceration stresses glosses on a predominantly passive, gentle-heat, sealed-vessel procedure.
- **Paragraph architecture match:**
  - P1 (72 tok): prepare lunaria / set up vessel
  - P2 (72 tok): combine + seal — contains `dar` at L2 (material addition), `dam` at L6 (finalize), `dal` at L8 (careful place)
  - P3 (5 tok only): alembic transition — sole instance of reduplicated `okain okain char` (take-vessel, check, take-vessel)
  - P4 (126 tok): 3-day maceration + distillation — gentlest e-depth profile (67% e-depth ≥ 1), `ram` at L11 near completion
- **Sealing signature:** 75.3% opaque terminals (matches f83r 75.7%) — grammatical encoding of sealed state, not explicit "seal" token.
- **Balneum signature:** qokeedy=14 occurrences (highest token freq on folio) on a recipe explicitly specifying "ashes for three natural days" — strongest qokeedy concentration expected for any matched folio. Confirms PT-013 gloss.
- **Glosses that hold on maceration:** qokeedy, qokedy, shedy, chedy, lchedy, qokal, dar, dal, dam, ram, okain (11 tested, 11 consistent with gloss).
- **Gloss breaking:** `qokaiin` as "strengthen/intensify heat" appears 10× on f82r — a recipe that NEVER calls for fire strengthening. Independently reproduces the PT-013 note that qokaiin's Catalan-grounded gloss is over-specific. Likely true reading is structural: "heat to [containment form]" — specifies a containment-form closure rather than an intensity change.
- **Sub-hypothesis tested and FALSIFIED:** "okain-doubling = vessel-transition marker." Corpus-wide, okain-okain adjacent = 1 event, gap-1 = 1, gap-2 = 4 (6 events total across 135 okain tokens). Observed/expected under random placement = 0.14x — under-dispersed, not clustered. Control `daiin` shows same under-dispersion (0.08x), confirming this is a general Voynich immediate-repetition aversion, not an okain-specific vessel signal. Event paragraph lengths mean 70 / median 63 — not enriched in short paragraphs. f82r P3 is one of 6 events, not a reliable pattern.

- **qokaiin gloss revised (2026-04-16):** Full context scan across all 15 matched folios (70 occurrences) produced direct falsification of PT-013 Catalan-grounded "strengthen fire":
  - **Rate by recipe type is inverse of H1:** DISTILL 0.70% (lowest) vs. SEAL_MACER 1.74% vs. FURNACE 2.42% (highest). If qokaiin meant strengthening fire, distillation (which explicitly calls for fire-strengthening) should top the list — it's last.
  - **Preceder profile is monitoring, not heating:** sh=23, ch=16, qo=9 (top prefix preceders). Top specific preceders: shedy (9), chey (7), chedy (4). qokaiin follows check/monitor events, not heat events.
  - **Follower profile same:** ch=20, sh=12, BARE (daiin/aiin)=10.
  - **Position:** uniform within paragraph (31/31/37 early/mid/late) — not a transition marker.
  - **Structural reading that fits:** qokaiin = qo (heat-source) + k (heat) + -aiin (yield+iter+iter+bind suffix, shared with daiin/okaiin/shaiin). The -aiin family encodes the "sustained contained form." qokaiin = "heat-source: sustained contained form" = apply heat while the vessel is in its sealed/bound state. This fits sealed maceration folios and furnace spec, and is compatible with distillation moments where the apparatus is fully sealed before driving more heat (the f83r Catalan "fortifica" moment operator-verb matches because strengthening fire on a closed retort IS heat-while-sealed, viewed from the operator side).
  - Consistent with C171 (semantic ceiling: notation encodes operations, not operator-perspective verbs).
  - **PT-013 qokaiin row updated** from "strengthen/intensify heat" to "heat-source: sustained contained form (apply heat while sealed/bound)" with 15/15 cross-folio consistency.
- **Status:** Cross-operation-class validation of PT-013. 10/10 Catalan-grounded glosses now validated or upgraded. Reduplication sub-hypothesis falsified.
- **Session:** 2026-04-16

### PT-015: f112v / Ch1M third-class validation — revised qokaiin gloss holds
- **Method:** Deep alignment of f112v (415 tokens, 13 paragraphs) against Ch1M (lunaria → quicksilver, pipeline origin). Third operation class after f83r distillation (PT-013) and f82r sealed maceration (PT-014). Tests the revised qokaiin gloss from PT-014 specifically.
- **Signatures:**
  - Opaque terminals 69.6% (sealed but intermittent — distillation vents via alembic, matches recipe)
  - BARE prefix 20.5% (UNUSUALLY HIGH; typical folios <10%) — see new observation below
  - ch=20.0% (high active-check), sh=5.3% (low passive watch), qo=16.6% (moderate heat)
  - 13 paragraphs matches ~15-operation recipe structure
- **qokaiin revised gloss confirmed:** All 4 qokaiin occurrences (P3L3, P5L2, P10L4, P11L2) fall in sealed-apparatus phases (gentle distillation, forced distillation). None at "strengthen fire" moments in isolation. Revised gloss "heat-source: sustained contained form" holds on a third operation class.
- **Other glosses:** qokeedy x12 (dominant, matches "gentle bath"), am x5 (multi-phase completions fit Ch1M's multi-phase structure), chedy x8 (high — matches many "signs" to check), shedy x3 (low — fits active distillation), lchedy x1 (lowest of any matched folio — operator trusts routine equipment), otal x2 (both early — matches fractionation drip-monitoring), dal absent (no careful-placement moments in recipe).
- **Sub-hypothesis tested and FALSIFIED:** "BARE-prefix dominance marks pipeline-origin recipes." Corpus BARE-rate distribution (82 folios): mean 17.6%, median 16.6%, stdev 5.5%. f112v at 20.5% is z = +0.53 (not exceptional). Spearman rho chapter# vs BARE = -0.315, p = 0.23 (not significant). f107r Ch44M (very late) has BARE = 20.1% (rank 25); f83r Ch9P (early) has BARE = 9.1% (rank 79). The "pipeline origin" signal is absent. Observed pattern is a SECTION effect: matched folios in pharmaceutical section (f100s) cluster high-BARE (f112r=21.1%, f112v=20.5%, f107r=20.1%, f116r=19.6%); matched folios in stars/biological section (f75-f84) cluster low-BARE (f82r=9.5%, f82v=9.4%, f83r=9.1%). Original baseline was wrong — I had compared f112v against f82r and f83r, which are themselves low-BARE outliers.
- **Status:** Third-class validation of PT-013/PT-014. All 10 Catalan-grounded glosses now validated on distillation (f83r), sealed maceration (f82r), AND pipeline-origin distillation (f112v). BARE sub-hypothesis falsified.
- **Session:** 2026-04-16

### PT-016: Phase 641 formal validation null — structural observation
- **Method:** Phase 641 ran 24 pre-registered hypothesis tests (atom/prefix/suffix glosses vs Latin Testamentum regex features) across 15-16 matched folio-recipe pairs with permutation p-values, BH-FDR correction, leave-one-out stability, bootstrap CIs. Plus ordinal alignment via Kendall-τ on category sequences.
- **Result:** 0/24 pass FDR at q=0.10. 0/24 bootstrap CIs exclude zero. Mean ordinal alignment ρ = +0.26 (vs null +0.04), p = 0.22. No constraints promotable.
- **Interpretation:** Null is STRUCTURALLY predicted by the matches themselves. Voynich folios encode operational EXECUTION; Latin Testamentum encodes recipe DESCRIPTION. A "place on ashes for 3 days" recipe (1 line, 2 heat mentions) maps to 275 tokens with 31% qo-prefix — the folio describes continuous heat maintenance over 3 days, not the naming of the operation. Consistent with C171 semantic ceiling. Rate correlation at folio granularity is the wrong instrument.
- **Near-significant right-direction signals** (LOO-stable, underpowered at N=16): E2 f-flag ↔ termination (ρ=+0.39), C6 p-pause ↔ termination (ρ=+0.37), A2 ch ↔ monitoring+transition (ρ=+0.35), D2 n ↔ iteration inverse (ρ=-0.34, supports "halt" gloss).
- **Potential falsification worth investigating:** C2 t-atom ↔ transfer, ρ=-0.47, p=0.07, wrong direction. If real, suggests 't' doesn't encode transfer directly.
- **Perfect alignment on one pair:** f82v Ch28M vessel specification ρ=+1.0 (3 shared categories matched perfectly). f83r Ch9P ρ=-0.60 suggests Voynich sometimes executes in reverse of description order (prep fire before adding material).
- **Control-corpus critique addressed:** Brunschwig 1500 (small distillation book) and 1512 (compounding book) both separate operational from recipe content. No medieval text we have integrates them the way Testamentum does. Testamentum's structural integration is selectively fitting — candidate alternatives fail at the structural filter before content matters.
- **Status:** Phase 641 COMPLETE with null-but-informative result. Proper paragraph↔step alignment requires richer per-step text (awaits SISMEL Catalan arrival). The matches remain defensible on converging-evidence grounds (see PT-015 and Phase INDEX).
- **Session:** 2026-04-16

---

## Encoding Architecture Insight (2026-04-14)

### PT-012: Vocabulary is a closed dictionary, not a free generative grammar
- **Discovery:** Blind encoding tests (encoding modern gold refining procedure in Voynich notation) produced 77-89% valid tokens using atom construction rules. But only 36-43 unique tokens vs f84r's 195. Invalid tokens violated co-occurrence constraints we couldn't articulate.
- **Key insight:** Only 479 of 48,640 possible MIDDLE types exist (0.9% occupancy, C1028). The scribe wasn't generating tokens from atom rules — they were selecting from a fixed vocabulary of ~479 instruction types, then wrapping with PREFIX/SUFFIX.
- **Analogy:** Atom rules are phonotactics (which letter combinations are legal). The vocabulary is the lexicon (which legal combinations are actual words). Knowing English phonotactics doesn't generate the English dictionary.
- **Implication for decoding:** We don't need to decode infinite atom combinations. We need to decode 479 specific words. Each recipe match adds entries to the dictionary (dar=material introduction, chekar=quality check, qokeedy=gentle balneum heat, etc.). The SISMEL book is a dictionary-building opportunity, not a cipher-cracking one.
- **Supporting evidence:** 
  - C1028: 0.9% product space occupancy, pairwise co-occurrence gating at 100% recall
  - C121: 479 token types collapse to 49 instruction classes
  - C1415: 83 forbidden PREFIX x HEAD pairs (selectional constraints on vocabulary)
  - C1553: ch/sh categorically excluded from MIDDLE-initial position (5821:0)
  - C1491: Headless MIDDLEs require da/sa/ta PREFIX (94-96% exclusive)
  - Blind encoding test: 14 invalid tokens all violate specific co-occurrence rules
- **Status:** Conceptual reframe, not a testable hypothesis. But changes how we approach the SISMEL comparison — focus on dictionary-building (which of the 479 words appear at which recipe steps) rather than atom-level decode.
- **Session:** 2026-04-14

---

## Debunked

### Period 17 (Derek Earnhart / Ed Honeycutt)
- **Claim:** 17-cycle rhythm in gallows spacing, detected via DFT.
- **Test:** Rank #236/879 on Currier B, #427/459 on Currier A, #4442/4614 on full corpus. Shuffle test p=0.306 (B), p=0.939 (A), p=0.965 (full).
- **Verdict:** Pure noise. No signal at any level.
- **Session:** 2026-04-11
