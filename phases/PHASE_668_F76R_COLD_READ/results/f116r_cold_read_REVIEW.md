# Error Check: f116r Cold Read

**Reviewer:** Expert-advisor agent
**Date:** 2026-04-27
**Match:** f116r ↔ III.4.0 (fixation of sublimated mercury)
**Cold read verdict:** COHERENT
**Expert positive control verdict:** PARTIALLY COHERENT (4/7)

---

## ERRORS

### E1. Verdict should be PARTIALLY COHERENT, not COHERENT

The cold read assigns verdict **COHERENT** (line 4 header and line 438 verdict section). The expert positive control downgraded this to **PARTIALLY COHERENT** with the critical observation that zero fch (mercury) markers appear on this folio. Per C1939, fch is enriched on all 6/6 confirmed mercury-recipe folios. A recipe that is explicitly "about mercury" -- fixation of sublimated mercury, exuberated quicksilver, dissolving mercury in water -- should show fch markers if the mercury-vocabulary diagnostic has any validity. The cold read never mentions fch at all, which means it either missed the diagnostic or chose to suppress it. This is a material error: the verdict must be downgraded.

**Fix:** Change verdict to PARTIALLY COHERENT at both locations. Add a Limitations or Caveats subsection to the verdict acknowledging the fch absence.

### E2. P1 qo-prefix count is wrong in the narrative

The P1 summary table (line 127) correctly shows the prefix counts from the JSON, but the narrative for P1 (lines 148-159) says "qokain (sustained cyclic heating)" as though qo is prominent. The JSON shows P1 has only **1 qo-prefix token** out of 33. The narrative gives the impression of a heat-dominant paragraph when in fact the dominant HEAD atoms are `e` (10) and `a` (10), with only `k` (1). The "supervised thermal operation" framing overstates the thermal character of P1.

**Fix:** The narrative should note that P1 is dominated by observation and vessel handling (sh=5, ok=4, ch=3), not heat-source operations. The single qo token is peripheral, not characteristic.

### E3. P3 "14 qo-prefix tokens" stated; JSON confirms 14 -- CORRECT, but sh-prefix count stated as "6 sh" while JSON shows 6 -- correct

No error here. Verified against JSON.

### E4. P4 token count discrepancy: cold read says 32, JSON says 32

No error. Consistent.

### E5. P6 qo-prefix count: cold read says dense qo; JSON shows qo=20 of 140

The cold read (line 266) says P6 has 20 qo tokens -- but the JSON shows qo=20 out of 140 tokens = 14.3%. The narrative describes P6 as dominated by observation and heat operations, which is reasonable (ch=28 is actually the highest prefix in P6, not qo). The cold read doesn't note that ch-prefix dominates P6, which would be more accurate.

**Fix:** Minor. Acknowledge ch=28 is the dominant prefix in P6, not qo=20. This doesn't change the operational reading much (ch=active testing fits the fusibility endpoint search), but the emphasis is slightly misplaced.

### E6. "Two quality checks (chekar-class tokens) appear in P6" -- verified: JSON shows chekar_count=2 for P6

Correct. No error.

---

## OVERSTATEMENTS

### O1. CRITICAL: No mention of missing fch mercury markers

The recipe is explicitly about mercury: "fixation of sublimated mercury," "add exuberated quicksilver," "dissolve another mercury." C1939 establishes fch as a mercury/mercury-water marker with infinite enrichment on 6/6 confirmed mercury-recipe folios and presence on 19/82 corpus folios. The cold read makes no mention of fch's absence. This is the single most important diagnostic failure for this match, and the cold read suppresses it entirely.

The generic cold read that preceded the expert review gave a COHERENT verdict. The expert correctly identified this as a critical failure. The cold read as written would mislead a reader into thinking this is a clean match.

**Severity:** HIGH. This is the primary reason the expert downgraded to PARTIALLY COHERENT.

### O2. P1 "supervised thermal operation" framing

As noted in E2, P1 has 1 qo token and 1 k-HEAD atom. Calling this "supervised thermal operation" based on a single heat token is an overstatement. The paragraph is observation-heavy (sh=5) and vessel-oriented (ok=4). A more honest framing would be "supervised setup with minimal heat."

### O3. P4 "fusibility test" interpretation presented as definitive

The cold read states that P4 encodes the fusibility test with high confidence. The transfer-watch (cth=1) is used as evidence of watching melt behavior. But 1 transfer-watch in 32 tokens is not a strong signature -- P6 has 4 cth tokens in 140 tokens (same rate, ~2.9% vs ~3.1%). The heavy dar count (5) is genuinely distinctive and well-noted, but the fusibility-test reading rests substantially on narrative coherence rather than distinctive token signatures.

**Severity:** MODERATE. The dar=5 peak is real and distinctive. The fusibility interpretation is plausible but not uniquely determined by the tokens.

### O4. "P5 as branch decision" is a just-so story

P5 (12 tokens, single line) is described as encoding a "decision boundary." But short single-line paragraphs are common in Currier B (C1852: 87.8% of HEADER_ONLY paragraphs are non-gallows-initial). A 12-token paragraph with zero dar and heavy ot-prefix could equally be a brief monitoring interlude. The "branch decision" reading is coherent with the recipe but not independently distinguishable from ordinary short paragraphs.

**Severity:** LOW. This is reasonable interpretation, just presented with more certainty than warranted.

### O5. e-depth interpretive frame slightly circular

The cold read interprets low e-depth as "sustained heat" (sublimation) and high e-depth as "heat-cool oscillation" (active distillation). These interpretations are consistent with F-B-007 and C1225/C1226, but the cold read presents them as though the e-depth values uniquely diagnose the operation type. In reality, e-depth ranges 0.42-0.64 across the folio -- a narrow range where all values are in the "moderate" band. The narrative makes it sound like 0.42 is dramatically different from 0.64 when both are within normal variation.

**Severity:** LOW. The directional interpretation is correct (lower = more sustained heat, higher = more cooling intervention). The overstatement is in treating small differences as operationally significant.

---

## OMISSIONS

### OM1. CRITICAL: No discussion of fch absence

Restated from O1 for emphasis. C1939 (fch = mercury marker, enriched on all 6/6 confirmed mercury-recipe folios). The folio summary JSON shows f-HEAD = 1 token total (in P7). Zero fch MIDDLEs. For a recipe that is fundamentally about mercury processing, this is a glaring absence that must be discussed. The expert positive control correctly identified this.

### OM2. No discussion of chekar distribution relative to other matched folios

The cold read notes chekar=2 in P6, chekar=1 in P7, chekar=1 in P8 (4 total). It would be informative to compare this to other matched folios -- is 4 chekar high or low for a 537-token folio? Without corpus context, the reader cannot assess whether this is genuinely distinctive. C1926 establishes chekar as appearing on 7/83 B folios; f116r having chekar is relevant but the count deserves corpus context.

### OM3. No mention of Section S characteristics

f116r is in Section S (Stars/Recipe section). The cold read never mentions this. C1106 (Stars e-stability kernel enrichment), C1107 (Stars LINK monitoring concentration), and C1930 (higher Mercuriorum chapters map to Section S) are all relevant context. Noting that f116r's section membership is consistent with the match (Mercuriorum → Section S per C1930) would strengthen the structural case.

### OM4. No mention of folio-unique vocabulary

C531 establishes that 98.8% of B folios have unique MIDDLEs. The cold read mentions some folio-specific compound tokens (e.g., `alolfchy` in P7 line 31) but never systematically addresses what vocabulary is unique to this folio and whether those unique MIDDLEs have mercury-relevant character.

### OM5. Cipher note says "No letter codes appear in this particular sub-recipe" -- correct but could note why

III.4.0 is unusual among Part III recipes in having no cipher letters. The cold read correctly states this but doesn't note its significance: the recipe uses plain Catalan throughout, making the translation straightforward with no cipher ambiguity. This is a minor omission.

---

## APPROVED

### A1. Paragraph-recipe phase mapping is structurally sound

The 8-paragraph to 8-phase mapping is credible. The recipe's procedural structure (sublimate -> fix -> reiterate sublimation -> test fusibility -> conditional addition -> exuberation reiteration -> optional composite dissolution -> feces cohobation) has a genuine 8-step organization that maps naturally to 8 gallows-delimited paragraphs.

### A2. dar distribution analysis is the strongest element

The dar distribution table (line 392-403) is well-constructed and genuinely informative. dar=5 in P4 (the conditional addition paragraph) and dar=0 in P5 (the decision point) are distinctive and support the recipe mapping. dar=3 in P8 (cohobation, which recycles rather than adds) vs dar=4 in P3/P6 (which add material) is a real and well-noted contrast.

### A3. Observation MIDDLE distribution is well-analyzed

The concentration of obs MIDDLEs in P6 (8) and P8 (5) with sparse distribution elsewhere is correctly identified as encoding the endpoint-search character of those paragraphs. The JSON confirms ckh=4 + cth=4 in P6 and ckh=4 + cth=1 + cphh=1 in P8.

### A4. P8 terminal cth+ckh pair on L49

The final line containing both a transfer-watch and a heat-level check is verified in the raw decode (line 771-772: `chcthy` followed by `chckhy`). This is a genuine structural feature that matches the recipe's endpoint test (fusibility over fire). Well-identified.

### A5. Token dictionary is comprehensive and accurate

The token table (lines 64-112) is well-constructed with appropriate source citations. Workshop readings are consistent with PT-013 and B Dictionary entries. Atom decompositions are correct.

### A6. P7 observation dominance is correctly identified

P7's sh=12 in 65 tokens (18.5%) is genuinely the highest sh-density per token on the folio. The JSON confirms this. The shift from heat-dominant (P3: qo=14, sh=6) to observation-heavy (P7: qo=13, sh=12) is a real structural change.

### A7. Cross-paragraph pattern tables are accurate

The e-depth, dar, and observation MIDDLE distribution tables match the JSON data. No arithmetic errors detected.

---

## OVERALL

**Rating:** NEEDS REVISION

The cold read is well-written and structurally competent. The paragraph-recipe mapping, dar distribution analysis, and observation MIDDLE tracking are genuine strengths. The token-level readings are consistent with the established dictionary.

However, the cold read has one critical flaw: **it omits the fch mercury-marker absence entirely and assigns COHERENT when the expert positive control correctly identified this as a PARTIALLY COHERENT match.** A recipe about mercury fixation that shows zero fch markers fails a key diagnostic (C1939). This is not a fatal failure -- the iterative sublimation structure, fusibility test, conditional branching, and feces cohobation all have plausible token-level signatures -- but it is a significant gap that must be acknowledged.

**Required changes:**
1. Downgrade verdict to PARTIALLY COHERENT
2. Add a "Limitations" or "Critical gaps" subsection discussing fch absence
3. Tone down P1 "supervised thermal operation" framing (E2)
4. Note Section S membership as consistent with C1930
5. Acknowledge that the match is PARTIALLY COHERENT specifically because the token-level structure matches the recipe's procedural architecture but the material-identity vocabulary (fch = mercury) is absent

**What's good as-is:**
- dar distribution analysis
- Observation MIDDLE distribution analysis
- P8 terminal cth+ckh pair identification
- Token dictionary construction
- Cross-paragraph pattern tables
- P7 observation-dominance analysis
