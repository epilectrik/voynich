# f112r Cold Read Review

**Reviewer:** Expert-advisor agent
**Date:** 2026-04-27
**Cold read verdict:** PARTIALLY COHERENT
**Expert positive-control verdict:** PARTIALLY COHERENT (same tier, different reasons)

---

## ERRORS

### E1. P2 dar count and "3x cohobation" claim — OVERSTATED, not wrong
The cold read says: "Three material additions (dair, dair, dam) across the paragraph. The recipe says '3 times' for the bath distillation cycle. Three dar tokens in P2 directly encode the three-fold cohobation."

Checking the JSON: P2 has `dar_count: 3` and the raw decode shows `dair` (L8), `dair` (L10), and `dam` (L10). The count is correct. However, `dam` is glossed as "material handling finalized" (not a material *addition*) — it is a closure marker, not a cohobation return. The cold read conflates two different operations (material return vs. material-handling finalization) to get the count to match "3 times." This is an overstatement: at most 2 material returns + 1 finalization marker, not 3 cohobation returns.

**Severity:** Moderate. The 3-dar count is factually correct but the interpretive claim that all three encode cohobation returns is strained. `dam` closing a material phase is not the same as returning distillate to earth.

### E2. P14 e-depth of 0.92 vs. recipe ending with calcination — UNADDRESSED
The expert's primary criticism was that P14 (e-depth=0.92) contradicts the recipe's final instruction: "wash it with distillation and calcination until it is as red as burning fire." The recipe's endpoint is calcination-to-red, which should produce LOW e-depth (sustained dry heat, minimal cooling). The cold read instead maps P14 to "final distillation to deep red" and treats the high e-depth as coherent.

The cold read's P12-P13-P14 mapping is:
- P12 (0.95) = distillation washing
- P13 (0.54) = calcination
- P14 (0.92) = "final distillation to deep red"

But the recipe says "wash it with distillation AND calcination UNTIL red." The natural reading is that distillation and calcination alternate or combine as a washing method, with calcination being the terminal operation that produces the red color. A folio that ends with e-depth=0.92 ends with intensive distillation, not calcination. The cold read invents a "final distillation" phase that is not in the recipe text.

**Severity:** High. This is the expert's central objection and the cold read fails to flag or address it. The recipe ends with "calcination until red as burning fire" — the folio ends with its second-highest distillation intensity. This is a genuine discordance.

### E3. P6 — "Zero fire management tokens with qo prefix" claim is incorrect
The cold read states: "Zero material additions, zero fire management tokens with `qo` prefix." Checking the JSON for P6: `prefix_counts` shows `qo` is NOT present. This claim is correct against the JSON. However, the cold read then says the key sequence includes `kedy` and glosses it as "steady-state thermal: done." The token `kedy` has prefix `ke` (not `qo`), so the "zero qo" claim is technically correct. No error here on closer inspection.

**Severity:** None — claim is accurate.

### E4. Observation MIDDLE in P5 — chekar vs obs_middle discrepancy
The cold read says P5 has "One quality check... chekar is counted once in the summary (via `cheeteey` or similar — the JSON shows chekar_count: 1)." Checking the JSON: P5 has `chekar_count: 1` but `obs_middle_counts: {}` (empty). The cold read's paragraph summary table shows P5 with 0 obs MIDDLEs, but the text discussion claims a chekar. These are different metrics: chekar is a quality-check signature, obs MIDDLEs are ckh/cth/ckhh. The cold read conflates them in the Cross-Paragraph Patterns section where the observation MIDDLE distribution table shows P5 with 0 obs MIDDLEs (correct), but the P5 narrative mentions the chekar. This is not technically an error — it is two different metrics — but the narrative implies the chekar IS an observation MIDDLE, which is misleading.

**Severity:** Low. The paragraph narrative overloads the "quality check" concept. The folio summary table correctly shows 0 obs MIDDLEs for P5, and the cross-paragraph table correctly shows 0. The narrative should have distinguished chekar from obs MIDDLEs more clearly.

### E5. P4 prefix count claim — "15 different prefixes for 37 tokens"
The cold read says: "The prefix mix is highly diverse (15 different prefixes for 37 tokens) -- the most varied paragraph on the folio." Checking the JSON for P4: `prefix_counts` has 15 keys including `none`. This is correct as stated, though counting `none` (bare prefix) as a "prefix" is slightly misleading. More importantly, P5 has 15 prefixes for 53 tokens per the JSON — so P4 is tied, not uniquely "the most varied." Minor factual slip.

**Severity:** Low. P4 ties with P5 in prefix count; claiming it is "the most varied" is inaccurate.

---

## OVERSTATEMENTS

### O1. "Three material additions match 'per .iii. vegades'" (P2)
See E1 above. The claim is presented with high confidence ("Three dar tokens in P2 directly encode the three-fold cohobation") but two of the three tokens are `dair` (iterative material addition) and the third is `dam` (material handling finalized). The match is suggestive but weaker than presented.

### O2. "The folio returns to intensive distillation for the final push to red" (P14)
The recipe's "until it is as red as burning fire" follows "wash it with distillation and calcination." The cold read assumes the red endpoint is achieved by distillation. The recipe more naturally reads that calcination achieves the red, with distillation as a washing/purification step. Mapping P14's extreme distillation signature to "achieve deep red" overstates the coherence.

### O3. P1 transfer monitoring claim — "the heaviest transfer monitoring of any paragraph"
The cold read says P1 has "15 of 48 tokens" with ot prefix, calling it the heaviest transfer monitoring. Checking the JSON: P1 has `ot: 15`. P3 has `ot: 7` out of 34 tokens (20.6%), P1 has 15/48 (31.3%). So P1 does have the highest absolute count and rate. This claim is accurate.

### O4. "The most significant heat token in this paragraph" (P12, qokeeiin)
The cold read calls `qokeeiin` "the most significant heat token" in P12 and says it encodes "exactly what 'wash with distillation' demands." This interpretive framing is reasonable but overstated — the token is one of three qo-prefix tokens and its specific significance over the others is asserted, not demonstrated.

### O5. Verdict framing
The cold read's verdict is PARTIALLY COHERENT, which is appropriate. However, the "What works well" section lists 5 strong points while the "What is weaker" section lists only 4, and the weakest point (no counting anchor) is relatively mild. The overall framing slightly favors coherence given the P14 e-depth problem (E2 above), which is buried in the weakness list as point 4 (balneum tokens in ash distillation) rather than the much more serious P14-calcination discordance.

---

## OMISSIONS

### M1. P14 e-depth vs. calcination — the expert's central objection
The expert specifically flagged: "P14 e-depth=0.92 CONTRADICTS calcination (recipe ends with 'wash by calcination until red') — calcination should produce near-zero e-depth." The cold read does not raise this as a discordance. It should have been the first item in "What is weaker" or ideally addressed in the P14 paragraph read itself. This is the single most significant omission.

### M2. No x3 counting anchor for ".iii. vegades"
The expert noted the absence of a corpus-singular counting anchor for the recipe's explicit "3 times" instruction. The cold read's weakness section mentions "No counting anchor" (point 2) and correctly notes that 3 dar in P2 is distributional not structural. However, it could have been more explicit: on f75r, the x4 and x9 counts produced corpus-singular identical-token runs (C1965). Here, 3 dar tokens of DIFFERENT types (dair, dair, dam) do not constitute a counting anchor in the same sense. The omission is partial — the cold read notes the weakness but undersells how significant it is relative to the confirmed-tier standard.

### M3. dar is front-loaded (P2-P5), not distributed across cohobation cycles
The expert noted dar concentration in P2-P5 while the recipe's cohobation logic should distribute material returns across the full extraction cycle. The cold read's dar distribution table correctly shows all dar in P2/P4/P5, and the text correctly notes "After P5, zero material additions." But it frames this positively ("the second half of the folio is pure process management") rather than noting the potential discordance: if cohobation means repeatedly returning distillate to residue, one might expect dar tokens throughout the extraction phases (P3, P8, P10), not only in the first half.

### M4. The "do not rubify" warning has no clear structural marker
The cold read maps P6 to the rubification warning based on e-depth drop and testing dominance. This is reasonable but the cold read does not note that there is no explicit warning marker or negative-instruction encoding in the token grammar. The grammar does not encode "do NOT do X" — it encodes operations. P6's check-heavy profile is consistent with ANY inspection pause, not specifically a warning. This limitation should have been noted.

---

## APPROVED

### A1. Folio summary table — accurate
All paragraph line ranges, token counts, dar counts, e-depth values, and observation MIDDLE counts match the JSON exactly.

### A2. e-depth thermal arc — correctly described
The double-peak structure and the P12-P13 swing are real and accurately reported. The cold read correctly identifies P12 (0.95) as the distillation peak and P13 (0.54) as the calcination valley.

### A3. Observation MIDDLE distribution — accurate
Four observation MIDDLEs (P3 cth, P6 cth, P8 ckh, P10 ckhh) match the JSON exactly. The placement narrative is reasonable.

### A4. ok-prefix shift across the folio — real pattern
The claim that the second half is ok-dominated is supported: P12 (ok=7/19), P13 (ok=8/28), P14 (ok=8/39). First-half paragraphs show more ot dominance (P1 ot=15, P3 ot=7). This is a genuine structural observation.

### A5. P6 as warning/inspection — well-argued
The e-depth drop, ch-dominance, zero qo, and cth observation MIDDLE together make a plausible case for an inspection pause. The interpretation is appropriately scoped.

### A6. P7 as micro-gate — well-argued
The 3-token paragraph with m-terminal closing is a reasonable gate interpretation. Appropriately brief.

### A7. Token dictionary — comprehensive and accurate
The token table matches the reference format, includes atoms, compositional readings, and workshop readings with source attributions. No errors detected in the dictionary entries.

### A8. Cipher note — correct
The cold read correctly identifies III.11 as Part III (Liber Mercuriorum) and notes the Part III cipher key. No cipher letters appear explicitly in this sub-recipe, which is correctly noted.

### A9. Recipe translation — accurate
The English translation faithfully renders the Catalan original. The operational phase breakdown (7 phases) is reasonable.

### A10. Paragraph fragmentation analysis — insightful
The observation that 14 paragraphs for 394 tokens (28 tokens/para average) is notably fragmented, and that this matches the multi-phase nature of cohobation, is a useful structural observation.

---

## OVERALL

**The cold read is competent but has one serious omission and one moderate error:**

1. **SERIOUS (M1/E2):** P14's e-depth of 0.92 is presented as coherent with "final distillation to deep red," but the recipe ends with calcination ("wash with distillation and calcination until red as burning fire"). Calcination should produce low e-depth, not near-peak distillation intensity. The cold read should have flagged this as a significant discordance rather than inventing a "final distillation" phase not present in the recipe text. This was the expert's central objection.

2. **MODERATE (E1/O1):** The "3 dar = 3x cohobation" claim conflates material returns (dair) with material finalization (dam). Two returns + one closure is not the same as three cohobation cycles.

3. **MINOR (M3):** dar front-loading in P2-P5 with zero in the second half could indicate the recipe's cohobation logic is not well-matched to the folio's material handling pattern.

The PARTIALLY COHERENT verdict is appropriate but for reasons the cold read partially misidentifies. The macro-level patterns (e-depth arc, dar distribution, prefix shift) are genuinely present and correctly described. The weakness is at the recipe-endpoint level: the folio's thermal signature at its conclusion does not match what the recipe demands.

**Recommended action:** Revise P14 paragraph read to acknowledge the calcination-endpoint discordance. Move this to the top of the "What is weaker" section. Downgrade P14 match assessment from "Coherent" to "Discordant" or at minimum "Weakly coherent — see note on calcination endpoint." Soften the P2 "3 dar = 3x cohobation" claim to note that dam is a finalization marker, not a material return.
