# Error Check: f79r Cold Read

**Reviewed against:** f79r_decode_summary.json, f79r_cold_read.txt, _cold_read_reference.md, embedded expert context (1966 constraints)

---

## ERRORS

### E1. P1 chekar_count listed as 0 in summary table, but JSON says 1

The summary table on line 137 shows `chekar_count` as `--` (zero) for P1. But the JSON (paragraph 1) shows `"chekar_count": 1`. The cold read narrative for P1 (line 172) correctly describes a quality check on L3 (`chckhey`), so the narrative is fine -- the summary table is wrong.

**Fix:** Change P1 row in the summary table to show `1` under the `chekar_count` column (or a designated column), and update P1's "Obs MIDDLEs" if applicable.

### E2. P3 chekar_count listed as 0 in summary table, but JSON says 1

Same issue. JSON shows `"chekar_count": 1` for P3. The summary table row for P3 shows `--` for chekar. The narrative doesn't explicitly call this out.

**Fix:** Add chekar_count=1 to P3 summary row. Identify which token triggers this count.

### E3. P8 chekar_count = 2 is correctly stated, but narrative attributes them incorrectly

The narrative (line 329) says "Two quality checks (chekar_count = 2) -- the highest on the folio." This is correct per JSON. However, the narrative then says "The chekes token on L35" is one of the checks. Looking at the raw decode, L35 has `chekes` (atoms: e.k.e.s) -- this appears to be the quality check detection. The narrative is acceptable here but the parenthetical column name `chekar_count` in the narrative doesn't match the summary table header, which uses "chekar" implicitly. Minor formatting issue, not a factual error.

### E4. "fch mercury markers exclusively in sublimation paragraph (P5)" -- expert says this, cold read says something different

The expert positive control states "fch mercury markers exclusively in sublimation paragraph (P5)." The cold read (P5 section, line 261-262) identifies two tokens on L22: `efchedy` and `qofchey`, and describes them as containing the `f` atom. However, the cold read interprets the `f` atom through the Part III cipher ("F = compound red sulphur") rather than through C1939 which establishes fch as a mercury/mercury-water marker (fch = flag.adjust.watch, 6/6 mercury-recipe folios).

The cold read says: "In the Part III cipher, F = compound red sulphur. These tokens are rare (only 2 on this folio, both on L22), and their appearance during the rubification phase, when red sulphur is being formed, is notable."

**This is an error of interpretation.** The cipher letter "F" in the recipe text is a substitution cipher for a textual word -- it has nothing to do with the atom `f` in Voynich morphology. The `f` atom in Voynich tokens is glossed as "flag" (C1392, C1195 PLAUSIBLE tier). The token `fch` (flag.adjust.watch) is established as a mercury marker (C1939) with infinity enrichment on 6/6 mercury-recipe folios. These tokens should be read as mercury/mercury-water markers appearing during the sublimation step (which involves mercury), not as references to the Part III cipher letter F.

**Fix:** Rewrite the P5 L22 analysis. Replace the cipher-letter interpretation with the C1939 mercury-marker interpretation. The `efchedy` and `qofchey` tokens contain the `fch` atom combination, which is the established mercury-water marker. Their appearance on L22 during the rubification/sublimation phase -- when mercury is being actively processed -- is consistent with C1939.

### E5. "ldaiin" on L12 described as "the single material addition" for P3

The cold read (line 217) says P3 has one material addition, citing `ldaiin` on L12. The JSON confirms `dar_count: 1` for P3. However, looking at the raw decode, `ldaiin` has prefix `da` (MATERIAL-ADD) with the `l` as an articulator or prefix extension. The token is correctly counted as a material addition. But the cold read then interprets this as "maps to the water return" -- the recipe says to return water onto mercury. This is plausible but the `l` prefix component (`lda` or `l` + `da`) suggests an equipment-mediated material addition rather than a simple pour. Minor interpretive stretch, not an error.

---

## OVERSTATEMENTS

### O1. "The f-atom tokens on L22 correlate with the formation of red sulphur" (P5, line 269)

See E4 above. This is the most significant overstatement in the document. The correlation is being drawn between a Voynich morphological atom and a recipe cipher letter -- two completely unrelated systems. The `f` atom in Voynich tokens has its own structural gloss ("flag", C1392) and established distributional pattern (C1939, mercury marker). Linking it to the Part III cipher letter F is a category error that conflates the manuscript's internal encoding system with the recipe's substitution cipher.

### O2. P4: "The progression from qokain (single iteration) to qokaiin (double iteration) on L17-L18 encodes the gradual intensification" (line 243)

This is an overstatement of what the iteration depth difference encodes. C1204 (i-extension inverted gradient) and C1730 (ii-deployment follows a REGIME refinement-intensity gradient) establish that double-ii relates to hazard/safety contexts, not simply "more intense heating." The progression from single-i to double-ii is structurally meaningful but attributing it to "gradual fire intensification" stretches beyond what the constraint system supports. The difference between `qokain` and `qokaiin` is more about sustained/bound cycling depth than heat intensity per se.

### O3. P5: "Three material additions correspond to handling the products of the separation" (line 258)

The cold read attributes all three `dar` in P5 to product handling. But the expert key point notes: "dar concentrates in P5 (sublimation), not P1-P3 (dissolution) -- physically informative mismatch." The expert flagged this as a mismatch because the recipe text describes sublimation/rubification at this point, not new material additions. Three `dar` tokens in the rubification paragraph is anomalous relative to the recipe, not perfectly explained. The cold read smooths this over rather than acknowledging the tension.

**Fix:** Acknowledge that 3 dar in P5 is the folio's highest concentration and represents a mild tension with the recipe, which describes observation of rubification/sublimation rather than material additions. The expert interpreted this as "physically informative mismatch" -- the operator may be handling products of separation (collecting sublimate), but this is an inference, not a direct recipe match.

### O4. P7: "Two material additions map to collecting the separated products (white sublimate, red fixed matter)" (line 317)

The two `daiin` tokens on L32-L33 are interpreted as product collection. But `daiin` is glossed as "start a new cycle -- extended binding" (B Dict D0), not "collect product." The cold read is interpreting the material-addition semantics in a way that fits the recipe, but the token's established gloss is about cycling/binding, not collection. This is an interpretive stretch. The `dal` token (on P5 L22) is the one glossed as "carefully collect" -- `daiin` is different.

### O5. "The two quality checks (highest on the folio)" in P8

The JSON shows P8 has chekar_count=2. But the summary table for P1 should show chekar_count=1 (per E1) and P3 should show chekar_count=1 (per E2). So while P8 does have the highest count at 2, the claim "No other paragraph has more than one" (line 329) is wrong -- P1 and P3 each have 1. This is a minor factual overstatement since P8 is indeed the highest, but the phrasing "no other paragraph has more than one" is literally correct (1 is not more than 1), so this passes. Still, the summary table errors (E1, E2) could mislead readers.

### O6. x3 counting claim not addressed

The expert key points flag "x3 counting is ambiguous -- distributed iteration markers rather than clean counting shorthand." The cold read does describe three distillation returns (P2, P3, P4) mapping to the recipe's three iterations, but doesn't explicitly claim a clean x3 counting idiom, which is appropriate. However, the read also doesn't flag this as ambiguous per the expert's caution. The recipe's "three times" is mapped to three paragraphs, not to a token-level counting idiom (unlike f75r's x4/x9 qokedy runs). This distinction should be noted.

---

## OMISSIONS

### M1. No mention of C1939 (fch mercury marker)

The cold read completely misses the established fch mercury-marker constraint (C1939: fch encodes mercury/mercury-water, infinity enrichment on 6/6 mercury-recipe folios). This is one of the strongest structural markers available for recipe identification and directly relevant to a mercury sublimation recipe. The two fch-containing tokens on L22 should be highlighted as mercury markers, not as cipher-letter references.

### M2. No acknowledgment of the dar-in-P5 mismatch

The expert flagged this as the most interpretively interesting tension: dar concentrates in P5 (sublimation), not P1-P3 (dissolution). The cold read explains it away rather than acknowledging the mismatch and what it might mean physically (operator handling products during sublimation rather than adding reagents during dissolution).

### M3. No mention of the x3 counting ambiguity

The expert specifically flags x3 as ambiguous. The recipe has three distillation returns; the folio has three distillation-focused paragraphs (P2-P4). But unlike f75r where x4 and x9 appeared as literal token repetitions, here the "three" is encoded structurally (three paragraphs) not lexically (three identical tokens). The cold read should note this difference.

### M4. P5 fch tokens not connected to C1925 (dar material tracking)

The relationship between dar and fch as complementary material markers is not discussed. C1925 establishes dar as encoding new material introduction. C1939 establishes fch as mercury-specific. Their co-occurrence in P5 (3 dar + 2 fch-containing tokens) is notable and unremarked.

---

## APPROVED

### A1. e-depth thermal arc is correctly computed and matches JSON

All 10 paragraph e-depth values match the JSON exactly: 0.76, 0.56, 0.51, 0.34, 0.62, 0.60, 0.91, 0.70, 1.50, 0.45. The V-shape interpretation (descending through distillation, bottoming at fire-strengthening, spiking at cooling/collection, renewing for final operation) is structurally sound and matches the recipe's physical demands.

### A2. dar distribution is correctly computed and matches JSON

All 10 paragraph dar counts match: 0, 1, 1, 2, 3, 0, 2, 1, 0, 2. Total = 12 dar tokens on the folio.

### A3. Observation MIDDLE distribution matches JSON

The observation MIDDLE counts match the JSON: P2 has 1 cth, P3 has 2 cth, P4 has 2 ckh, P5 has 1 cth, P10 has 1 ckh. All other paragraphs show 0. The type-shift observation (cth during distillation, ckh during fire-strengthening) is genuine and structurally interesting.

### A4. hh-extended token correctly identified only in P10

JSON confirms hh_count=1 only in P10, and the raw decode shows `shecphhdy` on L39 (atoms: e.c.p.h.h.d.y). The cold read correctly identifies this as the folio's only hh-extended token and places appropriate interpretive weight on it.

### A5. Token dictionary is well-constructed

The dictionary covers the major tokens on the folio with correct atom decompositions. Source attributions distinguish PT-013 validated tokens from B Dictionary and compositional readings. The prefix domain table and atom reference table match the reference document.

### A6. qo-density claim for P3 is correct

P3 has 19/51 = 37.3% qo-prefixed tokens. The JSON confirms qo=19 for P3. No other paragraph approaches this density (P4 has 16/77 = 20.8%).

### A7. Paragraph sizes and line ranges match JSON throughout

All 10 paragraphs have correct token counts, line ranges, and gallows-initial line identification matching the JSON and raw decode.

### A8. The overall structural narrative (dissolution -> distillation x3 -> fire strengthening -> rubification -> observation -> cooling -> verification -> final operation) maps plausibly to the recipe

The paragraph-level procedural arc is well-constructed and follows the recipe's natural flow without forced reordering. The fact that 10 paragraphs map to ~8-9 distinct recipe phases with reasonable token allocation is a genuine structural observation.

---

## OVERALL

**Grade: B+ (Good with notable errors)**

The cold read is structurally sound in its quantitative claims (e-depth, dar counts, observation MIDDLEs, token counts all verified against JSON). The paragraph-by-paragraph narrative is generally plausible and follows the recipe's procedural arc convincingly.

**Critical fix needed:** The fch/cipher-letter conflation (E4/O1/M1) is the most serious issue -- it confuses two entirely unrelated systems (Voynich morphological atoms vs. Catalan cipher substitutions) and misses the opportunity to use C1939's mercury-marker finding, which would actually strengthen the match. This should be rewritten.

**Secondary fixes:** The summary table chekar errors (E1, E2), the dar-in-P5 smoothing (O3/M2), and the daiin-as-collection overinterpretation (O4) should be corrected. The x3 ambiguity (M3) should be noted.

**Strengths:** The e-depth thermal arc analysis is the strongest element -- it tracks the recipe's physical demands precisely and relies on quantitative data rather than individual token glosses. The observation MIDDLE type-shift (cth during distillation vs ckh during fire-strengthening) is a genuine structural finding. The overall verdict of COHERENT is justified despite the errors noted above.
