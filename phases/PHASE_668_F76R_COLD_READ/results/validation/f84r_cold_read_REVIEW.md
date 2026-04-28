# f84r Cold Read — Error Check Review

**Reviewer:** Expert-advisor agent (automated)
**Date:** 2026-04-27
**Files reviewed:**
- `f84r_cold_read.md` (the cold read)
- `f84r_decode_summary.json` (quantitative data)
- `f84r_cold_read.txt` (raw token data)
- `_cold_read_reference.md` (reference)

---

## ERRORS

### ERROR 1: P1 chekar count stated as 2 but narrated inconsistently

The summary table (line 132) states P1 has `chekar: 2`, which matches `decode_summary.json` (`"chekar_count": 2`). However, the P1 narrative never identifies these 2 chekar tokens on specific lines. In P3 the text says "Three quality checks (chekar tokens) verify progress during the long run" (matching `chekar_count: 3` in JSON). In P1, the L9 narrative mentions `cheky` ("quick thermal check") and `chey` ("quick active verification") but these are NOT chekar — `chekar` is specifically the token `chekar` (ch + e.k.a.r). Looking at the raw data, L2 has `shekar` (sh-prefix, not ch-prefix, so NOT `chekar`), and L9 has `cheky` not `chekar`. The actual `chekar` tokens in P1 are not clearly located in the narrative. This is not technically wrong in the summary table (the script counted them), but the narrative fails to call them out explicitly the way it does for P3. Minor error — the 2 chekar tokens in P1 should be identified by line.

**Checking the raw data for P1 chekar:** Scanning all P1 lines in the raw decode... no token literally spelled `chekar` appears in P1 lines 1-12. The `decode_summary.json` reports `chekar_count: 2` for P1, but this may be a counting error in the decode script (perhaps counting `shekar` as chekar, or using a substring match). L2 has `shekar` (sh-prefix) and L12 has no chekar. This needs verification — the JSON count may be wrong, or the script may count `shekar` under `chekar_count`.

**Verdict:** POSSIBLE ERROR in decode_summary.json. If the script counts `shekar` as `chekar`, that's a bug. The cold read never explicitly places chekar tokens in P1 lines, which may be an honest reflection of their absence. Needs script audit.

### ERROR 2: L2 narrative says "schckhy" encodes ckh, but the token's prefix is `sch`

The cold read says on L2: "Then a dense cluster of heat-level checks: `chckhdy` and `schckhy` — both encoding **ckh** (is the fire right?)." The raw data shows `schckhy` has prefix `sch`, meaning the body starts at `ckhy`. The ckh substring IS present in the body (`c.k.h.y`), so calling it a ckh observation MIDDLE is correct. However, the cold read implies both tokens have the same structural status. `chckhdy` has ch-prefix (active test), while `schckhy` has sch-prefix (a rare extended prefix). The ckh identification is valid per the observation MIDDLE convention (searching for ckh in the atom string), but the narrative should note the prefix difference. **Minor — not factually wrong but imprecise.**

### ERROR 3: L3 narrative claims "Two `dar` tokens appear — the first consecutive material additions on the folio"

Looking at the raw data for L3:
```
dar ... shedy ... qokedy ... qokeedy ... qokedy ... chedy ... okain ... chey ... qokedy ... dar ...
```

The two `dar` tokens are NOT consecutive — they are separated by 8 tokens. The cold read says "Two `dar` tokens appear" which is correct, but "the first consecutive material additions" is misleading since they are not adjacent. The word "consecutive" here appears to mean "occurring on the same line" rather than "adjacent tokens." **This is an overstatement.** The phrase should be "the first line with two material additions" or similar.

### ERROR 4: P2 e-depth stated as 0.48 in the cold read vs 0.476 in JSON

The cold read says e-depth = 0.48 (summary table and cross-paragraph patterns). The JSON says `"mean_e_depth": 0.476`. This is legitimate rounding (0.476 → 0.48), but the P3 e-depth is stated as 0.50 while JSON says 0.495. All values round consistently to 2 decimal places. **Not an error — consistent rounding convention.**

### ERROR 5: L1 narrative mentions tokens not on L1

The cold read says L1 has "a heat-source prefix (`kal`), then moves through state verification (`chedy`), gentle heat establishment (`qokeey`), and vessel management (`okeedy`, `olshed`)." Checking the raw data for L1:
```
lmyl  kal  chedy  qokeey  otedy  dytedy  okeedy  olshed  opshed  ykcsedy  qotedy  opoly
```

All mentioned tokens ARE on L1. The narrative then says "Two transfer-rate checks (`otedy`, `qotedy`)" — both present on L1. **APPROVED — all tokens check out.**

### ERROR 6: L8 token sequence quoted in the cold read

The cold read quotes:
```
L8:  ... qokeedy  dy  qokedy  daiin  shckhedy  qokaiin  checthy  dar  checthy  am
```

Checking raw data for L8:
```
otedy  pshol  pchcfhdy  qokeedy  dy  qokedy  daiin  shckhedy  qokaiin  checthy  dar  checthy  am
```

The cold read uses "..." to indicate it's showing a partial sequence starting from `qokeedy`. The tokens in the quoted sequence all match the raw data exactly and in correct order. **APPROVED.**

### ERROR 7: P3 L15 narrative claims `oraiiin` has "triple-i iteration depth"

The raw data shows:
```
L15: ... oraiiin ... oqofchedy ... oroly ...
```

The token `oraiiin` has atoms `a.i.i.i.n` — three i atoms. The cold read correctly identifies this as "triple-i." **APPROVED.**

### ERROR 8: Cipher resolution — does the cold read use Part II correctly?

The cold read's cipher note states: "II.12 uses the Part II (Liber Practicus) letter cipher. A = God (Déu), G = philosophical mercury (mercuri), E = menstrual (menstruall)." This matches the reference file's Part II cipher: A=God, B=mercury, E=menstrual, G=philosophical mercury, H=gold. The five-asterisk word resolved to "or" (gold) via Tavola 2 is consistent with the SISMEL convention.

The translation correctly resolves: A=God, G=vegetal mercury, *****=gold, E=menstrual. **APPROVED — correct Part II cipher throughout.**

### ERROR 9: Total dar count

The cold read's cross-paragraph patterns section states "folio's total 25 dar" (P1=9, P2=1, P3=15, total=25). JSON confirms: 9+1+15=25. **APPROVED.**

### ERROR 10: P2 L13 "5 ot-prefix tokens" claim

The cold read says "5 times on this 13-token line." Checking L13 raw data:
```
pchedy  qotchedy  otaiiin  chcthy  shedy  otedy  qoty  qotedy  ol  okedy  otedy  rom  otaly
```

Counting ot-prefix tokens: `otaiiin`, `otedy`, `otedy`, `otaly` = 4 ot-prefix tokens. But wait — `qotchedy`, `qoty`, `qotedy` have qo-prefix, not ot-prefix. The JSON confirms P2 prefix counts: `"ot": 5`. Let me recount: `otaiiin`(1), `otedy`(2), `otedy`(3), `otaly`(4)... that's only 4 on L13. However P2 has 2 lines. Let me check L14: `qotol  shcthhy  oty  dar  shcthy  schdy  qokeedy  olkey`. `oty` = ot-prefix (5th). So P2 has 5 ot total but only 4 on L13. The cold read claims "5 times on this 13-token line" for L13 specifically.

**ERROR CONFIRMED:** The cold read overstates ot-prefix count on L13. The raw data shows 4 ot-prefix tokens on L13, with the 5th (`oty`) on L14. The claim "more transfer-rate tokens than any other line on the folio" should be verified against P1/P3 lines. The total P2 count of 5 ot is correct, but attributing all 5 to L13 is wrong.

### ERROR 11: L13 token count

The cold read says L13 is "a 13-token line." Counting raw data L13: `pchedy qotchedy otaiiin chcthy shedy otedy qoty qotedy ol okedy otedy rom otaly` = 13 tokens. **APPROVED.**

---

## OVERSTATEMENTS

### OVERSTATEMENT 1: "The most on any line in this paragraph" (L6 ckh checks)

The cold read says L6 has "Three heat-level checks on one line — the most on any line in this paragraph." Checking: L6 has `shckhy`, `chckhy`, `chckhy` = 3 ckh observations. L12 has `chckhy` = 1. Other lines have 0 or 1 each. **The claim appears correct for P1.** Not an overstatement.

### OVERSTATEMENT 2: "The nigredo is not a vague thematic correspondence — it is a locatable diagnostic event"

This is strong language but is supported by the evidence: two ecth observations flanking a dar on a specific line (L8), with no other ecth observations in P1 or P3. The structural signal (paired ecth around a material addition) is genuinely distinctive. This is Tier 3 interpretive claim, appropriately confident for the evidence level. **Acceptable — strong but supported.**

### OVERSTATEMENT 3: "The folio allocates its space in proportion to the duration of each phase"

P3 = 50% of folio for 45-day putrefaction; P1 = 44% for 2-4 day digestion; P2 = 6% for a brief transition. But P1 is 44% of tokens for a 2-4 day phase while P3 is 50% for a 45-day phase. If the allocation were truly proportional to duration, P3 should dominate far more (45:4:instant ≈ 92%:8%:0%). The folio allocates more to the longer phase, but NOT proportionally. **OVERSTATEMENT.** Should say "allocates more space to the longer phase" rather than "in proportion to."

### OVERSTATEMENT 4: e-depth definition

The cold read defines e-depth as "the ratio of cooling atoms (`e`) to total atoms." This is imprecise. Per C1225 and the morphology system, e-depth counts the number of consecutive `e` atoms after the HEAD k-atom, measuring thermal intensity (higher e-depth = gentler heat). The cold read's definition would make e-depth a simple frequency ratio, which is NOT how the parser computes it. The JSON's `mean_e_depth` values (0.582, 0.476, 0.495) are plausible for either definition, but the cold read's conceptual framing is incorrect.

**However:** The `mean_e_depth` field in the decode summary may actually be computed as a ratio of e-atoms to total atoms (folio-level aggregation), not as the C1225 per-token ke-depth measure. If so, the cold read's definition matches what the script computes, even though it diverges from the formal C1225 definition. This is a **definitional confusion** between two different e-depth concepts. The cold read should clarify which measure it uses.

### OVERSTATEMENT 5: "15 material additions (60% of the folio's total 25 dar) are distributed across the long paragraph"

This is factually correct but the interpretive claim — that putrefaction requires periodic material replenishment — is weakly grounded. The recipe says NOTHING about adding materials during putrefaction ("put everything to putrefy for a month and a half"). 15 dar in P3 is a structural observation; attributing it to "periodic replenishment" is speculative. The cold read acknowledges this somewhat ("materials may need periodic replenishment") but could be more cautious.

---

## OMISSIONS

### OMISSION 1: fch token on L15

The raw data shows `fchedy` on L15 of P3. Per C1939, `fch` encodes mercury/mercury-water handling (the dark pipeline MIDDLE). The cold read's P3 narrative for L15 does not mention this token at all. Given that the recipe is about dissolving gold WITH mercury, the appearance of `fch` (mercury-marker) at the start of the putrefaction paragraph is potentially significant and should be noted.

### OMISSION 2: `otaiiin` triple-i on L13

The cold read correctly notes this token ("the deepest iteration depth on the folio") but does not connect it to the recipe context. Triple-i is extremely rare across the corpus. Its appearance in P2 (the transition between digestion and putrefaction) may signal preparation for the 45-day putrefaction cycle — the deepest iteration the recipe requires. The cold read mentions the token but misses the opportunity to connect it to the recipe's temporal structure.

### OMISSION 3: P1 has 0 chekar in the narrative but 2 in the JSON

As noted in ERROR 1, the narrative never identifies the 2 chekar tokens supposedly in P1. If these are real, they should be located. If the JSON count is wrong (counting shekar as chekar), that should be noted.

### OMISSION 4: `cs` token absence

Per C1940, `cs` (adjust.sequence) encodes gold. Given this is a gold dissolution recipe, one might expect `cs` tokens. Their presence or absence should be noted. Scanning the raw data... no explicit `cs` standalone token appears, though `olcsedy` appears on L28. The cold read should note whether gold-marker MIDDLEs appear.

### OMISSION 5: Token dictionary missing some actually-used tokens

The token dictionary lists ~50 tokens but several tokens that appear in the narrative are not in the dictionary: `salchedy`, `qolkeey`, `qolchey`, `qotchedy`, `olchcthy`, `shckhedy`, `otaiiin`, `qokolchedy`, `opalkaiin`, `oqofchedy`. Some of these are discussed in the narrative but not formally defined. The long/rare compound tokens are compositionally readable, but the most important ones (especially `otaiiin` and `fchedy`) should be in the dictionary.

---

## APPROVED SECTIONS

### APPROVED: Recipe text and cipher resolution
The Catalan text, cipher notes, and English translation are correct. Part II cipher is applied correctly throughout. The five-asterisk resolution to "gold" via Tavola 2 is properly documented.

### APPROVED: Token Dictionary (core entries)
The ~50 most frequent tokens are correctly decomposed with atoms matching the reference. Workshop readings are consistent with the B Operational Dictionary and PT-013 glosses. Source attributions (PT-013, B Dict, Compositional) are properly tiered.

### APPROVED: Folio summary table
Token counts (361 total, P1=158, P2=21, P3=182), line counts (34 total, P1=1-12, P2=13-14, P3=15-34), and dar counts (9, 1, 15) all match the JSON. Observation MIDDLE counts match (P1: 6 ckh, 2 ecth, 1 cth; P2: 2 cth, 1 cthh; P3: 5 ckh, 2 cth).

### APPROVED: L8 nigredo diagnostic
The paired ecth observations flanking a dar on L8 is the strongest structural signal in the cold read. Both `checthy` tokens are verified in the raw data. The sequence is correctly quoted. The interpretive leap to nigredo diagnostic is appropriately flagged as structural observation, not translation.

### APPROVED: Cross-paragraph observation MIDDLE distribution
The table correctly tallies: P1 (6 ckh, 1 cth, 2 ecth = 9), P2 (2 cth + 1 cthh = 3), P3 (5 ckh, 2 cth = 7). All match JSON and raw data.

### APPROVED: P2 transfer-watch extended (`shcthhy` with doubled h)
The raw data confirms `shcthhy` on L14 with atoms `c.t.h.h.y`. The doubled h observation is correctly identified and the interpretive reading (prolonged scrutiny) is consistent with the atom system.

### APPROVED: Paragraph-level structure mapping
The three-paragraph structure maps cleanly to the recipe's three stages. The gallows-initial lines (13, 15) correctly delimit paragraph boundaries. The overall narrative flow is well-organized and follows the recipe progression without forcing.

### APPROVED: Constraint references
The cold read references C1394 (atom decomposition), C1225 (e-depth), and general Voynich structural principles correctly. No constraint violations detected.

---

## OVERALL ASSESSMENT

**Quality: GOOD with minor corrections needed.**

The cold read is well-structured, follows the reference template closely, and produces a coherent paragraph-by-paragraph reading. The recipe-folio correspondence is genuine and well-argued. The L8 nigredo diagnostic (paired ecth around dar) is the standout finding.

**Required corrections:**
1. **ERROR 10 (ot count on L13):** Fix "5 ot-prefix tokens on L13" to "4 on L13, 5 across P2" — this is a factual error.
2. **ERROR 1/OMISSION 3 (P1 chekar):** Investigate whether the JSON's chekar_count=2 for P1 is correct; if counting `shekar` as chekar, note the bug; if genuine, locate them.
3. **ERROR 3 (consecutive dar):** Reword "the first consecutive material additions" to "the first line with two material additions."
4. **OVERSTATEMENT 3 (proportional allocation):** Reword "in proportion to" to "reflecting" or "corresponding to."
5. **OVERSTATEMENT 4 (e-depth definition):** Clarify which e-depth measure is being used.

**Recommended additions:**
1. Note `fchedy` (fch = mercury marker) on L15 — relevant to a gold-dissolution-with-mercury recipe.
2. Add `otaiiin` and `fchedy` to the token dictionary.
3. Note the absence or presence of `cs` (gold marker) MIDDLEs.

**No structural or interpretive errors that would compromise the COHERENT verdict.** The core reading is sound.
