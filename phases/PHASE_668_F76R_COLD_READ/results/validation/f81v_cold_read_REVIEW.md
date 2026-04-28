# Error Check: f81v Cold Read

**Reviewer:** Expert-Advisor Agent
**Date:** 2026-04-27
**Files reviewed:** f81v_cold_read.md, f81v_decode_summary.json, f81v_cold_read.txt

---

## ERRORS

### E1. chekar count discrepancy (P1)

The JSON reports `chekar_count: 4` for P1, but the cold read text states "3 heat-level checks across 9 lines" in the match assessment, and the Observation MIDDLE distribution table lists only `ckh: 3` for P1. The JSON's `chekar_count` (which tracks `chekar`-style quality checks, tokens like `chekal`) is a different metric from `obs_middle_counts` (which tracks `ckh`/`cth`/`ecth` atom patterns inside MIDDLEs). These are two distinct counts, but the cold read narrative conflates them. The 3 explicit `chckhy` tokens on L4, L5, L7 are correctly identified as heat-level checks (`ckh` observation MIDDLEs). But the 4th `chekar` on L9 (`checkhy` = `e.c.k.h.y`) also contains `ckh` — the raw decode shows it tagged as a heat-level-check? Actually no: looking at the decode, L9's `checkhy` is NOT flagged with `<< heat-level-check`, while L4/L5/L7 `chckhy` tokens ARE. The JSON's `obs_middle_counts: {"ckh": 3}` confirms 3 ckh instances, consistent with the cold read's observation table. The `chekar_count: 4` is a separate metric. **No factual error in the cold read text itself, but the discrepancy between chekar_count (4) and ckh observation MIDDLEs (3) is not explained.** Minor issue — the cold read correctly uses the ckh count, not chekar.

**Verdict: NOT AN ERROR in the narrative. The cold read correctly reports 3 ckh. The JSON's chekar_count=4 includes `chekal`-type tokens (quality checks) which are a broader category. No correction needed.**

### E2. P2 chekar count: cold read says "two heat-level checks (L17, L18)" but JSON shows chekar_count: 3

The cold read text identifies two heat-level checks in P2: one on L17 (`shckhy`) and one on L18 (`chckhy`). The observation MIDDLE table lists `ckh: 2` for P2 — consistent. But the JSON shows `chekar_count: 3` for P2. The extra count is likely `chekal` on L20 or `cheky`-type tokens. Again, the narrative uses the ckh observation MIDDLE count (2) correctly. **No error.**

### E3. L1 token `otoin` glossed as "seal the vessel" — prefix classification

The decode shows `otoin` with prefix `ot` (transfer rate / drip-rate monitoring per the reference), but the cold read glosses it as "seal the vessel." The `ot` prefix domain is "Transfer rate: monitoring output — drip rate, melt flow" per the reference and C1958. The atoms are `o.i.n` = "arrange, iterate, bind." The cold read text writes "vessel operations: `otoin` ('seal the vessel')" — this is an overstatement. The token is ot-prefixed (transfer-rate domain), not ok-prefixed (vessel domain). An ot-prefix token encoding `arrange.iterate.bind` would be closer to "set up iterative transfer monitoring" than "seal the vessel." The word "seal" is more naturally associated with ok-prefix sealed-vessel operations (e.g., `okain`).

**Verdict: MINOR ERROR. `otoin` is ot-prefixed (transfer rate), not ok-prefixed (vessel). The gloss "seal the vessel" is unjustified for an ot-prefix token. Should read something like "set up transfer cycle" or "initiate drip monitoring cycle."**

### E4. L15 — `qofchedy` identification as fch (mercury marker)

The expert positive control notes "fch at L15 (mercury rectification transition)" and the cold read mentions L15 contains `qofchedy`. Looking at the decode: `qofchedy [HEAT-OP] f.c.h.e.d.y = flag.adjust.watch.cool.do.end`. The cold read does NOT mention the fch significance at all. The atoms `f.c.h` match the `fch` observation MIDDLE identified in C1939 as encoding mercury/mercury-water (enrichment on all 6/6 mercury-recipe folios). This is a significant omission — see OMISSIONS section.

### E5. "cs gold marker absent" — claimed by expert but not addressed in cold read

The expert positive control notes "cs gold marker absent despite gold being central subject (expert: gold is dissolved intermediate)." The cold read does not discuss cs absence. See OMISSIONS.

### E6. L10 `dairam` gloss as "material from P1's inhumation is being loaded into the cucurbit"

The cold read text states this about `dairam`: "the single material token `dairam` ('material cycle: respond, yield, finalize') closes the line — material from P1's inhumation is being loaded into the cucurbit." The interpretation that this specific token encodes loading the dissolved gold into the cucurbit is reasonable given the recipe context but is presented with slightly too much confidence for a compositional reading. The token dictionary correctly labels the source as "Compositional." The narrative text, however, presents the mapping as near-certain rather than plausible.

**Verdict: MINOR OVERSTATEMENT. The claim that `dairam` specifically encodes "loading into the cucurbit" is interpretive and should be hedged.**

---

## OVERSTATEMENTS

### O1. "The largest single-transition e-depth jump of any 2-paragraph folio in the cold-read set"

The Cross-Paragraph Patterns section claims the 0.33 to 0.55 e-depth jump is "the largest single-transition e-depth jump of any 2-paragraph folio in the cold-read set." This is an unverified superlative. Without checking all other 2-paragraph folios in the cold-read set, this claim cannot be confirmed. If it IS true, it should cite the comparison data; if not verified, it should be qualified with "one of the largest" or removed.

**Verdict: OVERSTATEMENT unless verified. Recommend softening to "a substantial e-depth contrast" or providing comparative data.**

### O2. "Extreme material density" / "highest material density on any cold-read folio"

P1 discussion states "15 material additions in 91 tokens. This is by far the highest material density on any cold-read folio." And the verdict says "21 dar, 8.1% of tokens." Both claims need verification against other cold-read folios. The absolute statements ("by far the highest") are risky without a comparison table.

**Verdict: OVERSTATEMENT unless verified. Recommend either verifying against all cold-read folios or softening the language.**

### O3. Line-by-line narrative occasionally over-interprets token sequences

Several line readings present highly specific interpretations as confident when the workshop readings are compositional (lowest confidence tier). Examples:
- L3: `dalal` as "measuring and placing material with extra care" — the token dictionary lists this as "Compositional" with reading "Careful double placement — measure and place." The narrative amplifies this.
- L7: `sheckhal` as "passively observe the heat state while checking yield" — a 6-atom token decoded compositionally, presented as a confident workshop reading.
- L27: `oiiin` as encoding "the final multi-component combination" — the triple-iteration token is compositional, and the specific claim about multi-component combination is recipe-driven interpretation, not token-driven.

**Verdict: MINOR OVERSTATEMENTS throughout the line-by-line narrative. Compositional readings should be identified as lower-confidence when the narrative presents specific operational claims.**

---

## OMISSIONS

### OM1. fch mercury marker on L15 not discussed

The expert positive control specifically flags "fch at L15 (mercury rectification transition)" as a key finding. The decode shows `qofchedy` on L15 with atoms `f.c.h.e.d.y`. The `fch` pattern is identified in C1939 as a mercury/mercury-water marker (enrichment on 6/6 mercury-recipe folios, 19/82 corpus). This folio matches a recipe involving mercury processing ("Rectifica son mercuri de la fleuma"), and the fch token appears at exactly the transition point where the recipe shifts to mercury handling.

The cold read mentions `qofchedy` in passing within the L15 narrative but does not identify it as an fch mercury marker. This is a significant omission given that it was one of the expert's confirmed findings.

**Recommendation: Add explicit discussion of fch on L15 as mercury marker per C1939, noting its position at the lunaria-to-rectification transition.**

### OM2. cs (gold) absence not discussed

The expert notes "cs gold marker absent despite gold being central subject" and provides the explanation: "gold is dissolved intermediate." C1940 identifies `cs` (adjust.sequence) as a gold marker (17.5x enrichment, concentrated on f84r/f84v). The absence of `cs` on a recipe about potable gold is structurally informative — it suggests gold is not being processed as gold (a raw material requiring multi-step adjustment) but as a dissolved intermediate already incorporated into the liquid medium. The cold read should discuss this absence.

**Recommendation: Add a paragraph in Cross-Paragraph Patterns or the Verdict discussing cs absence as consistent with gold being a dissolved intermediate rather than a raw material being processed.**

### OM3. Cipher note is accurate but could be more explicit

The cipher note correctly identifies that III.18 uses Part III cipher and that no explicit letter codes appear in this sub-recipe. This is accurate. However, it would strengthen the cold read to note that the substances described (dissolved gold, lunaria, vegetal water, mercury) correspond to specific cipher letters (D = simple dissolved gold, B = simple water) even though the letters are not used explicitly.

**Recommendation: Minor — expand the cipher note or leave as is. Not a critical omission.**

### OM4. No mention of ok/ot ratio

The expert highlighted key prefix-domain analysis. The cold read does include prefix distribution tables, but does not compute or discuss the ok/ot ratio, which per C1958 is informative about recipe emphasis. P1 has ok=10, ot=2 (ratio 5.0); P2 has ok=12, ot=2 (ratio 6.0). Both are ok-dominant, suggesting vessel temperature management dominates over drip-rate monitoring. This is consistent with a recipe about sealed inhumation followed by distillation within vessels, rather than drip-counting. Not a critical omission but a missed opportunity for structural confirmation.

**Recommendation: Minor — could add ok/ot discussion but not required.**

---

## APPROVED

### A1. e-depth contrast correctly identified and well-explained

The 0.33 (P1) vs 0.55 (P2) e-depth contrast is the strongest structural signal, and the cold read correctly interprets it: sealed inhumation = sustained heat with minimal cooling intervention; distillation/rectification = active cooling. The explanation of what e-depth measures is accurate and well-phrased.

### A2. dar distribution correctly analyzed

71% front-loading of material additions in P1 is correctly identified, correctly counted (15+6=21 total, 15/21=71.4%), and the interpretation that this inverts the typical pattern is well-explained by the recipe's material-heavy opening phase.

### A3. Observation MIDDLE analysis accurate

All 5 observation MIDDLEs being heat-level checks (`ckh`) is correctly identified. The absence of `cth` and `ecth` is correctly noted as informative. The interpretation — temperature control is the dominant concern because the recipe demands gentle decoction throughout — is sound.

### A4. Two-paragraph structure well-justified

The cold read correctly identifies the 2-paragraph structure as unusual and provides a convincing explanation: the recipe has one natural division point (sealed inhumation to open distillation). The paragraph break at this boundary is correctly identified.

### A5. Prefix distribution shift table

The prefix distribution shift table (P1 vs P2) is accurate against the JSON data:
- da: 15 -> 6 (correct)
- qo: 7 -> 35 (correct)
- ch: 8 -> 23 (correct)
- sh: 8 -> 20 (correct)
- ok: 10 -> 12 (correct)

The interpretation of the 5x qo jump as reflecting the shift from sealed heating to active fire management is well-grounded.

### A6. Recipe translation and Catalan text

The Catalan text and English translation are accurate. The cipher note correctly identifies III.18 as Part III (Liber Mercuriorum) and correctly states the Part III cipher key.

### A7. Token dictionary is well-constructed

The token dictionary covers the major tokens on the folio, correctly attributes sources (PT-013, B Dict, Compositional), and the compositional readings are consistent with the atom system (C1394).

---

## OVERALL

**Rating: GOOD with minor corrections needed.**

The cold read is structurally sound and produces a coherent mapping between folio structure and recipe content. The e-depth contrast, dar distribution, observation MIDDLE pattern, prefix distribution shift, and paragraph structure are all correctly analyzed and well-explained. The line-by-line narrative is detailed and mostly accurate.

**Required corrections:**
1. **E3**: Fix `otoin` gloss — it is ot-prefixed (transfer rate), not a vessel-sealing operation.
2. **OM1**: Add explicit discussion of `fch` mercury marker on L15 per C1939.
3. **OM2**: Add discussion of `cs` (gold marker) absence and its structural significance.

**Recommended improvements:**
4. **O1/O2**: Verify or soften superlative claims about e-depth jump and material density.
5. **O3**: Flag compositional readings more carefully in line narratives.
6. **OM4**: Optional — add ok/ot ratio discussion.

**No constraint violations detected.** The cold read respects C171 (semantic ceiling), C120 (pure operational), C1394 (atom system), C1939 (fch marker), and C1940 (cs marker). The interpretive claims are appropriately scoped to structural-operational language rather than substance identification.
