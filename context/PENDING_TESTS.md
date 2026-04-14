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
