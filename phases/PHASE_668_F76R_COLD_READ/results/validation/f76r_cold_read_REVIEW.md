# Cold Read Review: f76r

**Reviewer:** Expert-advisor agent
**Date:** 2026-04-27
**Files reviewed:** f76r_cold_read.md, f76r_decode_summary.json, f76r_cold_read.txt

---

## ERRORS

### 1. P4 observation MIDDLE miscount / misclassification (MINOR)

The JSON records P4's observation MIDDLE as `ecthe: 1` (not `ecth: 1`). The raw decode shows the token as `checthey` with atoms `e.c.t.h.e.y`, tagged `<< cooled-transfer-watch-end`. The cold read calls this "ecth variant" and counts it as 1 ecth. This is defensible — the extra trailing `e` is part of the suffix-side close — but the observation MIDDLE distribution table (Cross-Paragraph Patterns section) shows `ecth` for P4 without noting the `ecthe` vs `ecth` distinction. The JSON explicitly records `ecthe`, not `ecth`. The table should either note the variant form or use a footnote. Not a factual error in interpretation, but a data-table inconsistency.

### 2. `d` atom gloss inconsistency between Token Dictionary and Atom Table (MINOR)

The atom table says `d` = "mark / do" (SOLID). In the token dictionary body text, the `d` atom is glossed as "mark" in `qokedy` ("heat, stabilize, **mark**, done") but as "do" in the same token's workshop reading: "Maintain current fire level" — where the "mark" reading is absorbed into the operational gloss. This is not wrong, but the dual gloss "mark / do" is deployed inconsistently: some compositional readings use "mark" (`dar` = "material: respond"), others use "do" (`chedy` = "test: stabilize, **do**, done"). The Token Dictionary intro text says "mark (d)" at first mention, but the constraint system (C1934) formally upgraded `d` from "mark" to "do/execute." The cold read should pick one primary gloss for consistency. **Recommendation:** Use "do" as primary per C1934, note "mark" as legacy.

### 3. L1 token `chcfhdy` classified as "flag-heat-check" (cfh) — not in the Observation MIDDLEs table (MINOR)

The cold read's Observation MIDDLEs table lists `ckh`, `cth`, and `ecth` as the three observation MIDDLE codes. But P1's summary and the folio summary table both report `cfh: 1`. The `cfh` code is never defined in the Observation MIDDLEs table — it just appears in the P1 summary row. The cold read text mentions it once: "1 flag-heat check (cfh)" but never explains what `cfh` means. **Fix:** Either add `cfh` to the Observation MIDDLEs table with a compositional reading (`c.f.h` = adjust, flag, watch = "flagged heat check"), or note it as an anomalous/rare code in a footnote.

---

## OVERSTATEMENTS

### 1. "Six `chey` tokens across L19 alone" — actually 5 (MINOR)

The cold read says: "six `chey` ('quick active verification') tokens across L19 alone." The raw decode for L19 shows: `chey`, `chey`, `ky`, `chey`, `chey`, `chey` — that is 5 `chey` tokens plus 1 `ky`. The `ky` is not `chey`. **Correction:** Five `chey` tokens, not six.

### 2. "Two `qokaiin` — sustained deep cycling continues" on L21 — actually 1 (MINOR)

The cold read says about L21: "Two `qokaiin` — sustained deep cycling continues." The raw decode for L21 shows only 1 `qokaiin` token (position 7 of 13). The second `qokaiin` is on L20 (position 8 of 13). The cold read may be referring to L20-L21 together, but the sentence says "L21" specifically. **Correction:** L21 has 1 `qokaiin`; there is 1 additional `qokaiin` on L20.

### 3. "The monitoring density is exceptional... No other paragraph approaches this density" — true in absolute, overstated in rate

P1 has 17 observation MIDDLEs in 357 tokens (4.8%). P3 has 4 in 65 tokens (6.2%). P2 has 3 in 58 tokens (5.2%). So P1 has the highest absolute count but NOT the highest rate per token. The cold read's claim "No other paragraph approaches this density" is true in absolute terms but misleading in rate terms. **Recommendation:** Qualify with "in absolute count" or note P3's higher rate but lower diversity of observation types.

### 4. "Three quality checks (`chekear` / `chekain` type)" in P1 — count and type warrant clarification

The JSON shows `chekar_count: 3` for P1. The raw decode shows:
- L6: `chekain` (e.k.a.i.n)
- L8: `chekain` (e.k.a.i.n)
- L12: `chekear` (e.k.e.a.r)

The cold read correctly states "three quality checks" but the text claims on L12 "This is the first explicit quality assessment." If there are 3 quality checks and 2 occur before L12 (`chekain` on L6 and L8), then L12's `chekear` is the THIRD, not the first. The `chekain` tokens are quality-check-into-iteration (cyclic re-entry), while `chekear` is quality-check-with-response (assessment). The cold read conflates these when it calls L12 "the first explicit quality assessment" — `chekain` on L6/L8 is also quality assessment, just with a different terminal action. **Recommendation:** Rephrase L12 as "the first response-type quality assessment" or "the first quality assessment that produces a verdict rather than feeding back into iteration."

### 5. Silver-plate test positioning — not explicitly identified

The recipe describes testing "after the 6th distillation" — putting a drop on a silver plate. The cold read never explicitly identifies WHICH line or token sequence corresponds to the silver-plate test. It discusses quality checks at L12 and monitoring intensification at L25-L27, suggesting L25-L27 maps to "the approach to the 6th-distillation quality test." But it never commits to a specific line or token for the silver-plate test itself. This is actually APPROPRIATE caution (the token system does not encode "put a drop on silver"), but the prompt asks whether the cold read correctly maps the sevenfold structure. **Assessment:** The cold read handles this well — it identifies quality-check tokens (`chekear`, `chekain`) as assessment points and notes the intensifying monitoring toward the end of P1, but does not overstate by claiming a specific silver-plate-test token. This is honest.

---

## OMISSIONS

### 1. No `chekar` tokens in P2/P3/P4 — not discussed

The JSON shows `chekar_count: 0` for P2, P3, and P4. All 3 quality checks are in P1. The cold read notes the quality checks in P1 but never explicitly observes their ABSENCE from P2-P4. The recipe says "similarly you will do" for the parallel elements — the compressed paragraphs presumably include the quality test implicitly. Worth a sentence noting the structural asymmetry.

### 2. P1 paragraph count dominance not framed against corpus norms

The cold read says "P1 contains 65% of the folio's tokens... This is by far the largest paragraph on f76r." The expert positive mentioned that f76r "has only 4 paragraphs (not 12) with P1 being a massive 357-token paragraph." The cold read does note the asymmetry in the "Structural signature" section, but does not quantify how unusual a 357-token paragraph is relative to corpus norms. C858 (paragraph count reflects complexity, rho=0.836) and C1239 (paragraph body length parameterization) provide relevant baselines but are not cited. **Recommendation:** One sentence noting whether 357 tokens is extreme by Currier B standards would strengthen the structural observation.

### 3. Cipher note says "No cipher letters appear explicitly in this sub-recipe" — correct but could note plaintext references

The cipher note correctly states that no A-H cipher letters appear in II.16.0. However, the recipe DOES mention "menstrual" (= cipher E in other contexts) and "argent" (= cipher F) in plaintext. The cipher note already acknowledges this: "The recipe refers to 'menstruall' (E) and 'argent' / 'argent fi' (F) in plaintext." This is complete and correct. **No action needed** — just confirming it was checked.

### 4. f76r → II.16.0, not II.18 as listed in the match header

The prompt says the match is "f76r ← II.16.0 (element separation, sevenfold distillation, silver-plate test)." The cold read header says "II.16.0." This is consistent. Earlier project memory references "Ch18" for f76r using the old 1566 numbering. The cold read correctly uses the SISMEL numbering (II.16.0). **No action needed.**

---

## APPROVED

### 1. Recipe text and translation — CORRECT
The Catalan text matches the SISMEL source. The English translation is accurate and captures the procedural logic. The "septena distillacio" (sevenfold distillation) is correctly identified as the core procedure.

### 2. Token Dictionary — WELL CONSTRUCTED
The dictionary covers the major tokens appearing on f76r, provides both compositional and workshop readings, and correctly classifies confidence tiers (LOCKED/SOLID/PLAUSIBLE). The prefix domain table is consistent with C1962 and C929.

### 3. Paragraph structure mapping — CORRECT
4 paragraphs confirmed by gallows-initial lines at L1, L30, L35, L41 (matching the raw data). Token counts match the JSON: P1=357, P2=58, P3=65, P4=66. Total 546 tokens across 47 lines.

### 4. dar counts — CORRECT
P1=19, P2=4, P3=1, P4=3. Matches JSON exactly. The front-loading interpretation (70% in P1) is arithmetically correct (19/27 = 70.4%).

### 5. e-depth values — CORRECT
P1=0.60, P2=0.50, P3=0.46, P4=0.58. All match JSON (0.599, 0.500, 0.462, 0.576 respectively, rounded correctly).

### 6. Observation MIDDLE counts — MOSTLY CORRECT
P1: ckh=10, cth=4, ecth=2, cfh=1 (total 17). P2: ckh=2, ecth=1 (total 3). P3: ckh=4 (total 4). P4: ecthe=1 (counted as ecth variant, total 1). All match JSON. Grand total 25, with P1 at 17/25 = 68%. Correct.

### 7. P3 prefix shift interpretation — STRONG
The observation that P3 shifts from fire-centric (`qo` dominant in P1) to vessel-centric (`ok` dominant in P3) is well-grounded in the data. P1: qo=75 vs ok=22. P3: ok=11 vs qo=6. The physical interpretation (volatile air rectification requires sealed apparatus management) is consistent with the recipe's distinction between water (liquid) and air (volatile) processing.

### 8. Cross-paragraph e-depth arc — WELL INTERPRETED
The thermal trajectory P1(0.60) > P2(0.50) > P3(0.46) < P4(0.58) is correctly identified and physically interpreted. The P3 minimum for volatile processing and P4 rise for product collection are plausible.

### 9. Compression ratio observation — CORRECT
P2 at 58 tokens vs P1 at 357 = 6.16:1, correctly reported as "6.2:1." The mapping to the recipe's "semblant faras" instruction is appropriate.

### 10. Folio ends on gentle heat — CORRECT
L47: `qokaiin`, `ol`, `shedy`, `qokeey`, `or`, `shdy`. The last heat token is `qokeey` (gentle fire), and the final tokens are observation/arrangement. The cold read's "gentle heat and observation" characterization is accurate.

---

## OVERALL

**Grade: GOOD with minor corrections needed.**

The cold read is structurally sound and produces a coherent paragraph-by-paragraph mapping to II.16.0. The four-paragraph structure (full protocol / compressed repeat / air variant / product collection) aligns well with the recipe's rhetorical structure. Quantitative claims (token counts, dar counts, e-depth values, observation MIDDLE counts) are verified against the JSON with only trivial rounding.

**Required fixes (3):**
1. L19 `chey` count: 5, not 6
2. L21 `qokaiin` count: 1, not 2 (the second is on L20)
3. L12 should not be called "the first explicit quality assessment" when `chekain` tokens appear on L6 and L8

**Recommended improvements (4):**
1. Add `cfh` to the Observation MIDDLEs table or footnote it
2. Standardize `d` atom gloss to "do" per C1934, noting "mark" as legacy
3. Note the absence of `chekar` tokens from P2-P4 as a structural observation
4. Note P4's observation MIDDLE is technically `ecthe` not `ecth` (or add a footnote)

**No structural or interpretive errors found.** The mapping of paragraphs to recipe phases is defensible, the thermal arc interpretation is physically grounded, and the silver-plate test is handled with appropriate caution (not over-identified with any specific token). The cipher note is correct: II.16.0 uses Part II cipher keys but no cipher letters appear in this sub-recipe.
