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

### PT-017: t-atom gloss revision — "apparatus-mediated operation" not "transfer"
- **Method:** Investigated C2 falsification from Phase 641 (t-atom ↔ transfer_count, ρ=-0.47, p=0.07, wrong direction). Split "transfer_count" feature into three narrower features: physical transfer (pour/decant/vert/funde), distillation only (stilla/distilla), and apparatus operation (vas/seal/cucurbita/alembic/lute). Re-correlated t-atom rate against each.
- **Finding:** Physical transfer = 0 occurrences across all 16 matched Testamentum chapters (recipes don't describe pouring). t-atom ↔ distillation-only: ρ=-0.49, p=0.05 (inverse). **t-atom ↔ apparatus-operation: ρ=+0.39, p=0.13 (RIGHT direction, underpowered).** The original C2 falsification was contaminated by lumping distillation with transfer.
- **Proposed revision:** t = "apparatus-mediated operation / through-apparatus step" (vessel-internal stationary work). Distinct from ot-prefix (C1958: transfer-rate/drip-rate monitoring). t-atom encodes work happening WITHIN the apparatus; ot-prefix encodes tracking moving content via drip observation.
- **Evidence by folio (t_rate, apparatus_count):**
  - f82v vessel spec: apparatus=8, t_rate=0.097 (HIGHEST t_rate)
  - f82r sealed maceration: apparatus=5, distill=0, t_rate=0.084
  - f83r apparatus-heavy: apparatus=19, t_rate=0.091
  - f75r aqua vitae reflux: apparatus=1, distill=4, t_rate=0.041 (LOW)
  - f112r cohobation: apparatus=0, distill=5, t_rate=0.048 (LOW)
- **Compound readings under revised gloss:**
  - qotedy = heat-source + apparatus-op + cycle-close = apparatus-mediated heating cycle
  - qotal = heat-source + apparatus-op + state = bring apparatus to state
  - qotain = heat-source + apparatus-op + contained-form = apparatus-internal contained heating
- **Why the original SOLID-tier "transfer" gloss held for a while:** In distillation recipes where both apparatus AND transfer are present, the gloss produced coherent compositional readings. The failure only surfaced when tested against recipes where distillation≠physical-transfer and apparatus-only work (maceration, vessel spec) exists.
- **Constraint implication:** If validated via SISMEL, t-atom SOLID-tier gloss should revise from "transfer" to "apparatus-mediated operation" (or similar narrower term). ot-prefix (C1958) remains as-is — it genuinely tracks drip rate, which is different from t-atom.
- **Status:** Preliminary. Needs SISMEL validation at paragraph↔step level. Currently near-significant (p=0.13 for right-direction apparatus correlation) — promotion blocked by N=16 sample size.
- **Session:** 2026-04-16

### PT-017b: f82v/Ch28M deep alignment qualitatively confirms PT-017
- **Method:** Deep token-by-token alignment of f82v (298 tokens, 6 paragraphs) against Ch28M "De vasis proprijs habendis" (vessel specification chapter). Chapter enumerates ~11 vessel-function-names (distillatory, dissolvatory, putrefactory, calcinatory, mortificatory, congelatory, crematory, informatory, roastatory, odentatory, terminatory). Tests the revised t-atom gloss directly on the folio where it should show most clearly.
- **Finding:** f82v has 18 qot-compounds (6.0% of tokens) across 9 unique types — qotal, qotedy, qoty, qotar, qotol, qoteedy, qotey, qoteytyqoky, qotshedy. Count matches closely with Ch28M's ~11 enumerated vessel-function-names. P1 (first paragraph) holds 9/18 qot-compounds, consistent with Ch28M's "one form, many names" enumeration section.
- **Cross-folio qot-density (operational specificity validates PT-017):**
  - f82r sealed maceration: 6.2% (continuous apparatus-internal work)
  - f82v vessel specification: 6.0% (enumeration of vessel modes)
  - f83r Ch9P integrated recipe: 4.1%
  - f112v distillation: 3.1%
  - f76r element separation: 2.2%
  - f75r aqua vitae 9x reflux: 1.9% (vapor-in-motion, ot-prefix territory not t-atom)
- **Falsification test:** Under old gloss "t = transfer," vessel-specification recipe should have LOW t (no material movement). Instead f82v has the 2nd-highest qot- rate. "Transfer" fails this test. "Apparatus-mediated operation" passes cleanly.
- **Under revised gloss:** Each qot- variant becomes a distinct apparatus-operation mode (qotal = apparatus-op to state / calcinatory-like; qotedy = apparatus-op cycle-close / distillatory-like; etc.).
- **Status:** Cross-class qualitative validation of PT-017 on a fourth operation class (vessel specification). Third major gloss revision this session: qokaiin (PT-014) → revised gloss sustained-contained-form; t-atom (PT-017) → apparatus-mediated operation. Both survived direct contrastive testing on specific folios. Formal statistical promotion still blocked by N=16.
- **Session:** 2026-04-16

### PT-018: f55r → Brunschwig 1512 Ch XXXVI (opium, three-method preparation)
- **Method:** Cold read of f55r (124 tokens, 2 paragraphs, completely untouched before this session). Prior external identification of the plant illustration as opium poppy (user's memory). Compared structural signature against all 16 matched folios, found radically different profile (opaque terminals 48% vs matched 69-77%, 88% e-depth=0, o/a HEAD atoms dominant, `or` highest-frequency token at 7×, low qo 8.9% / low qot- 1 / low ot 3.2%). Located Brunschwig 1512 Ch XXXVI as dedicated opium chapter with structure: description → three varieties → three preparation methods. Did direct token-by-token alignment of f55r P2 against the three methods.
- **Three-method structural match via strong terminators:** P2 contains three strong terminator markers (`olkardam`, `kam`, `otaldiin`) bounding 3 natural blocks + a tail. Each block has a distinct operational profile matching one Brunschwig method:
  - **Block 1 (7 tokens, ends `olkardam`)** = method OVERVIEW ("opium is made thus...")
  - **Block 2 (20 tokens, ends `kam`)** = Method 1 (cut skin, passive milk flow, gentle dry): core sequence `dal qoko lkeedy dar kaiin dy kam` = carefully place + arrange heat + gentle equipment-fire + add material + contained-heat + cycle-close + heat-final
  - **Block 3 (22 tokens, ends `otaldiin`)** = Method 2 (pierce, collect drip, dry): has `qokal` (fire-to-state, stronger than kam) + terminal drip pair `otal otaldiin` matching "what comes out is dried"
  - **Tail (17 tokens, ends `ain`)** = Method 3 (pound in own milk, sun-dry): contains `qokaiin` (PT-014 revised gloss: sustained-contained-heat = "soak in own juice") + multiple flow operations `otol otar` + softest possible terminus `ain` matching passive solar drying
- **Method-distinguishing markers align:** Method 1 is mildest (weakest heat, passive flow) → f55r block 2 has gentlest `-eedy` cycle and single-heat-final `kam`. Method 2 distinguished by piercing + collecting exudate → f55r block 3 has stronger `qokal` fire + the specific `otal otaldiin` drip pair. Method 3 distinguished by soaking in own juice + sun-drying → f55r tail has `qokaiin` sustained-contained + multiple flows + passive `ain` ending.
- **Pharmaceutical-regime hypothesis:** f55r's signature class (low opaque, low qo, high `or`, careful-dosing `dal`, low-heat, `otal` flow markers) is **distinct from the alchemical-distillation regime** of matched Testamentum folios. Suggests the Voynich herbal section contains at least two encoding regimes — one mapping to Testamentum (alchemy), another to Brunschwig 1512 ingredient-reference (pharmaceuticals).
- **Testable prediction:** Other unmatched herbal folios should show signature-class membership: plants with known potent-pharmaceutical uses (henbane, mandrake, hellebore, belladonna, hemlock, saffron, colchicum, etc.) should produce the same low-heat / careful-dosing / flow-marker profile as f55r. Run signature clustering across ~20 unmatched herbal folios to test.
- **Known limitations:**
  - Several f55r tokens (char, chek, xar, odar, xaloeees, cpheody, ckhy, dl, oiiin, chelal, shar) don't have clean one-word maps to Brunschwig phases — the alignment isn't 1:1 at every position, consistent with Voynich notation being denser than source text (one instruction → many operator actions)
  - Method 1/2 intensity distinction (`kam` vs `qokal`) is real in Voynich but Brunschwig doesn't explicitly say Method 2 uses more heat — interpretive
  - `qokaiin` mapping to Method 3 relies on PT-014 revised gloss holding
  - Haven't ruled out: any 3-method preparation in our corpus would produce 3 distinguishable token profiles. Need a second 3-method preparation as additional test
- **Status:** Strongest unmatched-folio → specific-chapter candidate match we have. Not promotable until SISMEL-era alignment depth available. Pre-registered for retest when SISMEL arrives.
- **Session:** 2026-04-17

### PT-019: Pharmaceutical-regime cluster in Voynich B herbal section (Phase 642)
- **Method:** Unsupervised k-means clustering on 52-dimensional structural feature vectors across all 82 B folios. No reference to f55r's values (addressing expert-advisor concern that PT-018 was curve-fit to a single data point).
- **Finding:** k=4 optimal (silhouette=0.328). A 26-folio cluster emerges that contains f55r AND has 0/16 overlap with matched Testamentum folios. PC1 separates the cluster from matched folios by 8-10 standard deviations.
- **Cluster composition (26 folios):** f33r/v, f34r/v, f39r/v, f40r/v, f43r, f50r/v, f55r/v, f85r1/2, f86v4-6, f94r/v, f95r1/2/v1/v2, f105v, f114r. Heavily concentrated in the herbal section (f1-f66) and pharmaceutical section (f94-f105).
- **PC1 structural distinction:**
  - Alchemical side (matched Testamentum): qo-prefix, e-depth=1, k/e-HEAD atoms, -y suffix (heat-cycle operations)
  - Pharmaceutical side (f55r cluster): e-depth=0 (~88%), a/o-HEAD, BARE prefix, high vocab diversity (low-heat observational/conditional)
- **Shuffle test on PT-018 (addressing crazy-expert concern):** Across 648k words of Brunschwig 1500+1512, only 2 out of 2160 300-word windows contain ≥3 distinctive extraction-method patterns (milk flows out, pierce skin, pound in own, dry in sun, cut outer skin, etc.). Both windows are the opium Ch XXXVI passage. The target of PT-018's 3-block alignment is uniquely specific — not a generic structural coincidence.
- **Systematic folio-to-ingredient matching (Phase 642 s3) failed to discriminate:** Tested 26 cluster folios against 7 Brunschwig 1512 ingredient chapters via cosine similarity of 7 operational features. f55r ranks Opium #2/7 (Scordeon beats it at +0.57 vs +0.12). Negative control failed: matched Testamentum folios score mean top-1 similarity +0.46 vs cluster +0.53 — not a clean separation.
- **Implication:** Pharmaceutical regime is structurally real but heterogeneous. PT-018's signal comes from block-level structural alignment (3 blocks, terminator-bounded, method-distinguishing markers) not from aggregate feature density. A systematic matching pipeline needs block-level feature extraction, not folio-level cosine similarity.
- **Failure modes identified:**
  - 7 ingredient chapters too small and internally similar as target corpus
  - Aggregate features (extraction_count, sealing_count, etc.) capture too-generic operations; can't discriminate opium-preparation from metallurgical-separation
  - No plant-ID ground truth available for most cluster folios; validation path blocked
- **Next steps:** Block-level matching pipeline (hard — requires paragraph-segment-level feature extraction), multi-source target corpus (Rupescissa + Tichtel + others), or symptom-index target (crazy-expert's alternative).
- **Status:** Pharmaceutical regime established structurally; specific-chapter matching unresolved. Real finding is "there ARE at least two encoding regimes in Voynich B" — not "this specific folio matches this specific chapter."
- **Session:** 2026-04-18

### PT-020: Voynich B has three-part vocabulary (shared core + two regime extensions)
- **Method:** Computed token-type inventories for the 26-folio pharmaceutical cluster (PT-019) vs the 16-folio matched Testamentum cluster. Measured type overlap, high-frequency exclusive vocabulary, and PPMI regime-association within shared tokens. Applied robustness filter (types appearing on ≥2 folios).
- **Finding (PT-012 FALSIFIED in strong form, refined form emerges):**
  - Full Jaccard = 0.201, Robust Jaccard = 0.431 — well below the ~0.7 threshold PT-012 (one-closed-dictionary) would predict
  - **563 types are shared** between regimes (common core)
  - **Alchemical extension: 26 robust high-freq (≥5) EXCLUSIVE types** — sheckhy (19 occurrences, 18 folios), rain (13, 16 folios), lkain (12, 15 folios), shecthy (12, 11 folios), `qo` bare prefix (12, 9 folios), etc. — widely distributed in alchem, NEVER in pharm.
  - **Pharmaceutical extension: 6 robust high-freq (≥5) EXCLUSIVE types** — qotchdy (10, 19 folios), shor (9, 18 folios), qokshey (5, 7 folios), etc.
  - Asymmetry: alchemical regime has ~4× the high-freq exclusive vocabulary of pharmaceutical regime
- **Strong regime-lean on shared tokens (PPMI):**
  - Pharm-biased: aiin (+2.95x rate), daiin (+2.06x), or (+3.15x), ar (+2.69x), chdy (+3.53x) — containment-form suffixes + route/respond tokens dominant
  - Alchem-biased: qokeedy (121:8, PMI -2.72), qokain (121:9, PMI -2.56), qokeey (104:9, PMI -2.36), shedy (0.24x), qokedy (0.26x), qokal (0.27x) — qo-prefix heat-cycle operations dominant
- **Revised PT-012 formulation:** "Voynich B has a shared core vocabulary (~563 types) + two regime-specific extensions (~1080 and ~1150 types respectively), with strong frequency modulation even on shared tokens. The regimes are functionally distinct at the vocabulary level, not just at the deployment level."
- **SISMEL-testable prediction:** When SISMEL-matched pharmaceutical recipes arrive, Voynich folios matched to them should activate (a) the shared core vocabulary and (b) the pharmaceutical extension, but NOT the alchemical extension (qokeedy, qokain, qokeey, sheckhy, etc.) at their characteristic alchemical frequencies.
- **Constraint implications:**
  - Relates to C531-C535 (folio-unique MIDDLEs 98.8%) — but this is at REGIME level, different structural layer
  - Extends C1049 (shared vocabulary = section-universal substrate) by adding regime extensions on top
  - Refines C1134 (section-specific vocabulary frequency-modulated) — modulation is so extreme for some tokens (qokeedy 121:8 alchem:pharm) it's functionally exclusive
  - Does NOT conflict with C121 (479 instruction classes) — instruction classes can span regimes while specific tokens instantiate them differently
- **Status:** Binary-outcome test run. Strong form of PT-012 FALSIFIED. Revised three-part-vocabulary formulation is a candidate Tier 2 claim pending SISMEL replication. Directly produces two orthogonal SISMEL predictions (one about vocabulary activation, one about extension-exclusive tokens).
- **Session:** 2026-04-18

### PT-021: Recto/verso continuation is leaf-level not folio-level; OTHER category contains continuation pages
- **Method:** Computed structural continuation signals (e-depth similarity, opaque-rate similarity, prefix distribution cosine, shared words between last-line-of-r and first-line-of-v) for 39 recto/verso pairs spanning all 82 B folios. Composite score aggregates these four signals. Compared within-regime (BOTH_PHARM, BOTH_ALCHEM) to cross-regime (CROSS_*) pairs.
- **Key findings:**
  - Pharm-pharm pairs (11): mean composite 0.592
  - Alchem-alchem pairs (3): mean composite 0.596
  - Cross-regime pairs (12): mean composite 0.639 (HIGHER than within-regime)
- **Interpretation:** Within-regime leaf-as-logical-unit is CONSISTENT (pharm and alchem show nearly identical 0.59 composite). But cross-regime pairs scoring HIGHER reveals something important: many "CROSS_REGIME" pairs actually involve one matched folio + its verso classified as "OTHER" because the verso has shifted structural profile (e.g., recto = distillation, verso = cooling/preservation/observation phase). The OTHER category (40 folios) likely contains many continuation pages of matched recipes.
- **Specific high-continuation cross-regime pairs (likely unidentified continuations):**
  - f75r (Ch19M aqua vitae) + f75v(OTHER) composite = 0.911
  - f114r (PHARM) + f114v(OTHER) composite = 0.861
  - f77r(OTHER) + f77v (Ch27M furnace) composite = 0.761
  - f107r (Ch44M) + f107v(OTHER) composite = 0.737
  - f103r (Ch16M) + f103v(OTHER) composite = 0.741
- **Implications for Phase 642 cluster / coverage estimates:**
  - "16 matched Testamentum folios" may underestimate by ~10-30% leaf-level coverage (when versos continue recipes)
  - "26 pharmaceutical cluster folios" similarly may undercount leaf-level pharmaceutical pages
  - Current folio-level cluster may be capturing RECIPE-START pages and not continuation pages
- **Testable refinement:** Re-run s2 unsupervised clustering on LEAF-LEVEL features (recto + verso concatenated or averaged) rather than folio-level features. Predict cleaner cluster separation AND higher pharmaceutical-regime coverage.
- **SISMEL implication:** When SISMEL data arrives, test whether the recipes for matched folios (like f75r → Ch19M) extend naturally onto the verso pages. If yes, we formalize leaf-level matching; if no, the verso pages are different content that just shares structural statistics.
- **Does NOT conflict with:** C1399-C1400 (paragraph ordering null) — this is about cross-page continuation, different structural layer. C1936 (recto/verso sequential pairing in matched set) — consistent with, strengthens.
- **Status:** Novel codicological finding emerging from simple structural continuation test. Suggests revision of analysis unit from folio to leaf. Binary-outcome test complete; re-clustering on leaf-level features is the natural next step but deferred until SISMEL.
- **Session:** 2026-04-18

### PT-022: Voynich notation is ATELIC (state-aspect) not BOUNDED (step-count)
- **Method:** Deep leaf-unit read of f75r + f75v testing PT-021's prediction that f75v continues f75r's Ch19M aqua vitae recipe. Ch19M specifies "distill + return pure substance through NINE TIMES" — a clean 9-iteration count. If notation encodes iterations, we'd expect 9 bounded structural units across the leaf.
- **Results:**
  - **Continuity confirmed:** shared tokens at boundary (`dain`, `qokedy`), material addition at start of verso (`pchedar`), feature profile continuous. PT-021's "operational continuity across leaf" validated.
  - **Iteration count NOT encoded:** Only 2 strong-close events (`am`, `ram`) across the entire 751-token leaf (f75r 412 + f75v 339). If 9 cycles were segmented, we'd expect ~9 terminator-bounded blocks. Cycling density is distributed (f75r peaks 21-22, f75v peaks 11-15), not enumerated.
- **Interpretation:** The recipe says "9 times" but the folio captures the OPERATIONAL ENVELOPE (sustained cycling activity), not a LITERAL COUNT. The operator reads the recipe to know 9; the folio captures what the operation LOOKS like (qokeedy balneum + dar material + -dy closures, repeated as needed), not how many times to repeat it.
- **Linguistic-aspect parallel:** The notation appears ATELIC (unbounded state-aspect, like English "was distilling" with continuous inner structure) rather than TELIC/BOUNDED (count-aspect, like "distilled three times"). This suggests the iterate atom `i` and iterate-suffix encode ITERATIVE ASPECT rather than COUNT-OF-ITERATIONS.
- **Consistent with C171 (semantic ceiling):** Notation captures operational state, not recipe-level metadata. Count-of-repeats is recipe metadata (in Latin text), not operational state (in folio notation).
- **Consistent with C1056 (sensory judgment not encoded):** "Knowing when to stop" after 9 cycles is operator-side knowledge; notation doesn't mark cycle boundaries.
- **Partial falsification of specific PT-018 interpretation:** The 3-block structure we found in f55r P2 may not be "3 preparation methods" in the literal-enumeration sense either — it may be 3 ASPECTUAL phases (setup/main/completion) with internal state differences. The method-distinguishing markers could correspond to aspectual transitions, not step-counts.
- **New testable prediction for SISMEL:** Catalan recipes that specify N repetitions should produce folios with SUSTAINED feature profiles in that operation channel, but NOT N bounded structural units. Folios matching "repeat 3 times" and "repeat 9 times" should be distinguishable by DENSITY of the iterated operation but not by COUNT of bounded blocks.
- **Implication for matching pipeline:** Feature-based matching (as in Phase 642 s3) will naturally capture aspectual profile (good); block-level matching expecting N-to-N correspondence between recipe steps and folio blocks will systematically fail for iterated operations (worth documenting as a constraint on future matching designs).
- **Status:** Testable corollary of PT-021. Refines interpretation of Voynich notation's grammatical aspect. Has implications for C1399-C1400 (paragraph ordering null is CONSISTENT with aspectual rather than sequential reading), C1394 HEAD+MOD*+TERM model (may need aspectual annotation), and future matching pipeline design.
- **Session:** 2026-04-18
- **REVISED 2026-04-18 via PT-022b:** The strong form of PT-022 ("count NEVER encoded") is wrong. User observation led to targeted check: f75r has a run of 4 consecutive identical `qokedy` tokens at P1 L13, plus a 5-token qok-heat sequence at P3 L7, plus surrounding dense qok-family tokens. Wide-set max run on f75r = 11, which is the longest in the entire B corpus (next highest = 6 on f103r). The user correctly identified this as explicit enumeration matching Ch19M's "nine times." See PT-022b.

### PT-022b: Voynich count-enumeration IS encoded via sequential token repetition (PT-022 revision)
- **Method:** Ran cycle-heat run detection across all 82 B folios, counting contiguous runs of qokedy/qokeedy (narrow) and wider qok-family (qokedy, qokeedy, qokeeedy, qokchdy, qokechdy, qokeey, qoky, qokey) with max_gap=2 tolerance. Triggered by user observation that f75r had ~10 qokedy/qokeedy tokens clustered near end.
- **Key findings:**
  - **f75r wide-set max run = 11** — the longest in the entire B corpus by a large margin
  - **f75r narrow-set: 6-token run + 4-token run (sum = 10)** — matches Ch19M's "nine times" iteration count
  - **f75r P1 L13: `qokedy qokedy qokedy qokedy`** — 4 IDENTICAL consecutive tokens (specifically diagnostic — one doesn't write "heat heat heat heat" in aspectual notation; this IS enumeration)
  - **f75r P3 L7: `qokeedy qokeedy qokedy qokedy qokeedy`** — 5 consecutive qok-heat tokens with variation
  - Next-highest wide-run = 6 (f103r); next after that = 5 (f82r, f107v, f108r, f108v, f83r, f84r). f75r's 11 stands alone.
- **Interpretation:** Voynich notation is primarily atelic/aspectual (PT-022's main claim stands for most recipes) BUT enumeration can be encoded via sequential token-repetition when the recipe has an explicit emphatic count. f75r's 9-cycle aqua vitae (Ch19M) uses this mechanism.
- **The distinguishing feature:** Identical-token repetition (qokedy×4) is especially diagnostic because it's not operationally meaningful unless the operator is counting. You don't write "heat heat heat heat" to mean "heat in aspectual mode"; you write it to mean "heat 4 times."
- **Consistency with existing constraints:**
  - Extends C1394 (HEAD+MOD*+TERM) — within-token MOD* iteration is different from cross-token repetition; both are forms of iteration at different structural layers
  - Does NOT conflict with C1399-C1400 (paragraph ordering null) — both are corpus-aggregate findings; folio-specific enumeration is within-paragraph, different layer
  - Refines PT-022: atelic is default; enumerative is triggered by explicit-count recipes
- **Testable SISMEL prediction (strengthened):** Catalan recipes with explicit N-counts (e.g., "three times," "five times," "nine times") should match folios where the primary operation token appears in a run of approximately N length in wide-set. Specifically:
  - Recipe "do 9 times" → folio should have qok-family run ≥ 8-10
  - Recipe "do 3 times" → folio should have run ≥ 2-4
  - Non-iterative recipe → no long run expected
- **Implications for matching pipeline:** Token-run detection should be added as a feature for folios matching iterative recipes. Density-matching (my earlier proposal) is necessary but not sufficient — run-length matching is an additional signal specifically for count-emphasis recipes.
- **Implication for PT-018 (f55r opium):** f55r's 3-block structure may still be aspectual-phases (extraction/drip/sun-dry) rather than literal 3 methods. The enumeration mechanism (token repetition) is DIFFERENT from the aspectual structure and doesn't appear on f55r — consistent with opium recipe not emphasizing count.
- **Status:** Revises PT-022. Count-enumeration IS encoded when recipe demands it. f75r is the clearest exemplar. SISMEL will directly test this via recipes with varied explicit counts.
- **Session:** 2026-04-18 (revision triggered by user catching anomaly that initial analysis missed)

### PT-022c: Recount with proper gap tolerance — f75r has 10 (not 4) qokedy/qokeedy, matching Ch19M's 9
- **Method:** User correction: my strict-adjacency counting missed the wider dense-region pattern. Re-ran scan counting all qokedy+qokeedy instances per 35-token window across all 82 B folios.
- **Corrected data:**
  - **f75r: 10 qokedy+qokeedy within 35 tokens (positions 330-364, L36-L41)** — matches Ch19M's explicit "through nine times"
  - f78r: 9 hits (unmatched recipe; density suggests iterative)
  - f108r: 8 hits; f108v/f26r/f77r/f78v/f79v: 7 hits (mostly unmatched)
  - f82r, f83r, f84r, f77v, f41r: 6 hits
  - f76v, f82v, f84v: 5 hits
  - Many matched folios: 4-6 hits
- **Uniquely diagnostic on f75r:** The 4 IDENTICAL consecutive `qokedy` tokens at P1 L13 (positions 115-118). No other folio in the corpus has this specific repetition pattern. One doesn't write the same word 4 times in succession for any reason OTHER than counting — this is the strongest evidence of literal enumeration in the corpus.
- **Refined interpretation:**
  - Dense qokedy+qokeedy regions encode sustained cycling activity (aspectual), which has DURATIONAL OR ENUMERATIVE interpretations depending on recipe
  - When recipe has explicit count (Ch19M's "nine times"), the dense-region count approximates it — f75r's 10 ≈ Ch19M's 9
  - The 4-identical-token run at L13 is unambiguous enumeration (not aspectual activity)
  - Other high-density folios (f78r=9, f108r=8) may correspond to unidentified iterative recipes — testable when SISMEL data arrives and we find their recipe matches
- **Predictions refined:**
  - f78r should match a recipe with ~8-9 explicit iterations (if count-hypothesis holds)
  - f108r should match ~7-8 iterations
  - Recipes specifying "3 times" should produce folios with dense-region count ~3
  - Identical-token repetition (like L13's qokedy×4) is the marker of emphatic count-encoding; without it, dense regions may be just sustained activity
- **Methodological note:** My initial strict-adjacency (max_gap=0-2) analysis missed the 10-count because it operates over wider dispersion. User's specific observation corrected this. Pattern: hand-targeted observation caught what statistical-regularity scanning missed. Consistent with the general session pattern of domain-guided observations outperforming blind scans.
- **Status:** Correction to PT-022b. The specific claim "10 qokedy+qokeedy in dense region on f75r matching Ch19M's 9x" is correct. The broader enumeration mechanism is supported by both the density match AND the unique L13 identical-repetition pattern.
- **Session:** 2026-04-18

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
