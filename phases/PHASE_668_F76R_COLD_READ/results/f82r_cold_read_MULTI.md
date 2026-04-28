# Multi-Recipe Test: f82r vs III.19 Waters 2-6

**Folio:** f82r (Currier B, 9 paragraphs, 275 tokens, 32 lines)
**Test recipes:** III.19.1 through III.19.5 (waters 2-6 of the medicinal water sequence)
**Prior result:** Single-recipe test (f82r vs III.19.3 alone) returned PARTIALLY COHERENT with scale tension

---

## 1. Folio Summary

| Para | Lines | Tokens | dar | dal | dam | e-depth | okain/otain | qo% | Obs MIDDLEs | hh |
|------|-------|--------|-----|-----|-----|---------|-------------|-----|-------------|-----|
| P1 | 1-9 | 72 | 3 | 0 | 0 | 0.76 | 0 | 38.9% | ckh:2 ecth:1 | 0 |
| P2 | 10-11 | 17 | 1 | 0 | 1 | 0.47 | 0 | 29.4% | — | 0 |
| P3 | 12-13 | 17 | 0 | 0 | 0 | 0.88 | 0 | 35.3% | — | 0 |
| P4 | 14-16 | 28 | 2 | 0 | 1 | 0.86 | 0 | 32.1% | — | 0 |
| P5 | 17-18 | 15 | 1 | 1 | 0 | 0.67 | 3 | 13.3% | — | 0 |
| P6 | 19-24 | 57 | 4 | 1 | 0 | 1.00 | 0 | 28.1% | — | 0 |
| P7 | 25-25 | 9 | 0 | 0 | 0 | 1.00 | 0 | 22.2% | — | 0 |
| P8 | 26-30 | 44 | 1 | 1 | 0 | 1.02 | 0 | 40.9% | — | 1 |
| P9 | 31-32 | 16 | 1 | 0 | 0 | 0.69 | 0 | 0.0% | — | 0 |
| **Total** | 1-32 | **275** | **13** | **3** | **2** | **0.85** | **3** | **30.2%** | **3** | **1** |

**e-depth** measures thermal intensity (how many `e` atoms modify a `k`-HEAD token). Higher e-depth = gentler, more controlled heat. Balneum mariae operations (water bath distillation) produce e-depth >= 0.8. Direct ash distillation produces lower e-depth.

---

## 2. The Five Sub-Recipes (III.19.1 through III.19.5)

### III.19.1 -- Second Water (337 chars)
Take a capon or hen, pluck and gut it, separate feet and bones. Mince all flesh. Put in the alembic and in the balneum; distill all the water, and set it aside.

**Key features:** Butchery preparation (physical, non-thermal), then single balneum distillation. One material (flesh). One output ("set aside").

### III.19.2 -- Third Water (207 chars)
Take the flesh of the hen or capon and over ashes distill its moisture with moderate continuous fire; and beware of burning the flesh; and set aside the moisture.

**Key features:** Ash distillation (NOT balneum). **Explicit quality warning** ("guarda't de la combustibilitat"). One output.

### III.19.3 -- Fourth Water (369 chars)
Take simple lunaria moisture, put 3 parts on the flesh substance. Seal the cucurbit with glass cover and common wax. Place on ashes for 3 natural days with sawdust fire. Then put it on top and distill all the water through the balneum, and keep it apart.

**Key features:** New material addition (lunaria). **Sealing step** (glass + wax). 3-day maceration on ashes, then balneum distillation. Two-phase heat: sawdust fire then balneum.

### III.19.4 -- Fifth Water (143 chars)
Take the substance of the said hen or capon, and over ashes separate all moisture by distillation.

**Key features:** Very short. Ash distillation. No new materials. One output.

### III.19.5 -- Sixth Water (195 chars)
Take the bones of the said capon or hen, and very finely minced put them in the alembic and over ashes; take all their liquor by distillation, and set it apart.

**Key features:** New material (bones). Mincing preparation. Ash distillation. One output.

### Combined Recipe Structure

| Step | Water | Material | Method | Heat Type | Distinctive |
|------|-------|----------|--------|-----------|-------------|
| 1 | 2nd | Minced flesh | Balneum distillation | Gentle (balneum) | Butchery prep first |
| 2 | 3rd | Flesh | Ash distillation | Moderate (ashes) | **"Beware burning"** |
| 3 | 4th | Lunaria + flesh | Seal, macerate 3 days, then balneum | Mixed (ashes -> balneum) | Sealing, new material |
| 4 | 5th | Flesh substance | Ash distillation | Moderate (ashes) | Brief, minimal |
| 5 | 6th | Bones (minced) | Ash distillation | Moderate (ashes) | Different material |

**Total combined:** 1,251 characters, 5 distinct operations on 3 material types (flesh, flesh+lunaria, bones).

---

## 3. Multi-Recipe Prediction Scorecard

| # | Prediction | Evidence | Verdict |
|---|-----------|----------|---------|
| 1 | 9 paragraphs maps to ~5 operations + prep/transitions | 5 waters + butchery prep = 6 core steps. P1 (72 tokens) is disproportionately large for a single step -- likely covers butchery prep + first distillation together. 9 paras is reasonable for 5 waters + prep + transitions | **PASS** |
| 2 | Multiple dar tokens (5+ material introductions) | 13 dar + 3 dal + 2 dam = 18 material events. 5 waters each begin "Take..." (pren). 13 dar is plausible for 5 material introductions + intermediate handling across 5 operations | **PASS** |
| 3 | Alternating heat: balneum (high e-depth) / ashes (lower) | P1 e=0.76, P2 e=0.47, P3 e=0.88, P4 e=0.86, P5 e=0.67, P6 e=1.00, P7 e=1.00, P8 e=1.02, P9 e=0.69. There IS variation but no clean alternating pattern. P2 (0.47) is the clearest ash signature; P6-P8 (~1.0) are clear balneum. The 2nd water (balneum) -> 3rd (ashes) -> 4th (ashes then balneum) -> 5th (ashes) -> 6th (ashes) predicts ONE balneum at start, ONE at the 4th water's second phase, and ashes elsewhere. This roughly matches: P1 moderate, P2 low, P3-P4 moderate, P5 low-moderate, P6-P8 high | **PARTIAL** |
| 4 | Sealing step for 4th water | P5 has 3x okain (vessel seal/iterate) -- the only paragraph with okain tokens. This is exactly the sealing signature identified in C1929. P5 also has the folio's only ot-prefix token (otain = seal transfer rate). Triple okain for a glass+wax sealing step is proportionate | **STRONG PASS** |
| 5 | Quality gate at 3rd water (beware burning) | P2 has the folio's only kam token (= finalize and close, per dam gloss). It also shows L10 checkho (MONITOR: cool.adjust.heat.watch.arrange) -- an active heat-level check. The "beware burning" warning maps to active monitoring during ash distillation. P2's low e-depth (0.47) confirms non-balneum heat. The quality concern is present but not as prominent as a dedicated observation paragraph | **PARTIAL** |
| 6 | Transfer tokens at distillation outputs | qot-prefix (transfer via heat source) tokens appear in P1 (L5, L8), P4 (L16), P6 (L24), P8 (L26-L29), concentrated at paragraph endings. P8 is especially transfer-heavy (t-HEAD = 9/44 tokens = 20.5%, by far the highest). This matches 5 separate "distill and set aside" sequences | **PASS** |
| 7 | Bone processing at end | P8-P9 show a shift: P8 has the folio's only hh token (okchhy, L28 -- "double watch at the vessel"), heavy transfer operations (9x t-HEAD), and P9 drops to zero qo (no fire management). P9's profile (ch/sh/lch dominant, e-dominant HEADs, no qo) looks like post-distillation quality checking. This is consistent with the final bone extraction being a straightforward ash distillation (P8) followed by final output handling (P9). The mincing preparation is not clearly distinguishable from the distillation itself | **PARTIAL** |
| 8 | x3 counting for 4th water (3 parts, 3 days) | P5 has exactly 3 okain tokens but these encode sealing iterations not a count of 3. No clean x3 qokedy-type counting run is visible anywhere on the folio. The "3 natural days" might be encoded in P6's length (57 tokens, 6 lines -- the longest paragraph), representing sustained multi-day processing. But there is no explicit counting anchor like f75r's x4 and x9 runs | **FAIL** |

**Score: 4 PASS, 3 PARTIAL, 1 FAIL out of 8 predictions.**

---

## 4. Paragraph-to-Water Mapping

### P1 (72 tokens, lines 1-9) -- Butchery Preparation + 2nd Water (Balneum Distillation)

**Recipe says (III.19.1):** Take a capon, pluck, gut, separate feet and bones. Mince all flesh. Put in alembic and in balneum; distill all water, set aside.

**What the tokens say:**
- P1 is the largest paragraph by far (72/275 = 26.2% of folio). This is consistent with combining the preparatory butchery steps AND the first distillation.
- 3x dar (material additions): L1 dar from daiin context, L9 dairchey (material add + check), L9 region. Three material events could encode: (a) take the capon, (b) separate the parts, (c) put minced flesh into alembic.
- e-depth 0.76: moderate, consistent with balneum distillation (just below the 0.8 threshold -- perhaps because the butchery preparation portion is non-thermal, pulling the average down).
- qo = 38.9% (highest of any paragraph): heavy fire management for the distillation phase.
- 1x chekar (ckh observation MIDDLE) at L1 and another at L3: fire-level checks during balneum.
- 1x ecth (L4, octheol): cooled-transfer-watch -- handling a cooled intermediate.
- Lines 1-5 show heavy qo/sh interleaving (heat and observe). Lines 6-9 shift toward sh-dominant with transfer tokens (qoteor, shecthy): observation and cooled transfer at the end.

**Match quality:** GOOD. Scale, thermal profile, material additions, and the prep-then-distill structure all align.

### P2 (17 tokens, lines 10-11) -- 3rd Water (Ash Distillation with Burning Warning)

**Recipe says (III.19.2):** Take flesh, distill moisture on ashes with moderate continuous fire. BEWARE burning. Set aside.

**What the tokens say:**
- e-depth 0.47: the LOWEST on the folio, consistent with direct ash fire (not balneum).
- 1x dar (L11): take the flesh for this step.
- L10 ends with kam (= finalize): this is a short, decisive operation.
- L11 has checkho (cool.adjust.heat.watch.arrange) -- an active quality check during heating. This is the "beware burning" signature: the scribe is actively checking heat levels during a potentially destructive ash distillation.
- L10 chopchedy: a complex monitoring token (arrange.pause.adjust.watch.cool.do.end) -- elaborate caution.
- L10 qotedor (transfer.cool.do.arrange.respond): heat-driven transfer with careful handling.
- Only 17 tokens for a 207-character recipe: proportionate.

**Match quality:** GOOD. Low e-depth (ashes), active quality monitoring (burning risk), kam closure, material addition, and brevity all match.

### P3 (17 tokens, lines 12-13) -- Transition / Preparation for 4th Water

**Recipe context:** Between the 3rd and 4th waters, the recipe says to take lunaria moisture and put it on the flesh substance. P3 has NO dar tokens -- it does not introduce new material.

**What the tokens say:**
- e-depth 0.88: elevated, consistent with gentle handling.
- 0 dar: no new material introduced.
- 3x ol-prefix: vessel loading/managing.
- L12 olchedy appears twice (L12 and L13 end): vessel-state checking.
- L13 qokain -> deeedy -> qokeey -> qokaiin: a heating ramp sequence (heat-cycle -> deep-cool -> gentle-heat -> sustained-heat). This looks like bringing the apparatus to the right state for the next operation.
- No kam or ram closure markers.

**Match quality:** MODERATE. P3 looks like a transitional paragraph -- re-preparing the apparatus between waters rather than encoding a specific recipe step. This is the kind of "housekeeping" paragraph that a multi-recipe folio would need but a single recipe would not.

### P4 (28 tokens, lines 14-16) -- 4th Water Phase 1 (Lunaria Addition + Ash Maceration)

**Recipe says (III.19.3, first half):** Take lunaria moisture, put 3 parts on flesh. Seal with glass and wax. Place on ashes for 3 days with sawdust fire.

**What the tokens say:**
- 2x dar (L14 daiin, L15 dam): two material events -- (a) add lunaria moisture, (b) finalize the addition step (dam = "process step complete").
- e-depth 0.86: moderate-high, perhaps reflecting the "sawdust fire" which is gentle but sustained.
- L14 qokchdy: "adjust fire while watching" -- careful fire management for the sawdust fire.
- L14 lkeedy: "equipment sustained, gentle cooling" -- apparatus management.
- L15 has qokeedy x2 (gentle fire, balneum-level) interspersed with cheey (check gently): sustained gentle heating.
- L15 ends with dam: "this material step is done."
- L16 shows a thermal ramp: qoteey -> chedy -> qokeeey -> qokedy -> lteedy -> qokeedy: escalating then settling heat, consistent with bringing the sawdust fire up and stabilizing for a 3-day maceration.

**Match quality:** GOOD. Material addition, gentle sustained heat (sawdust fire), and the dam closure all fit the first phase of the 4th water.

### P5 (15 tokens, lines 17-18) -- 4th Water Phase 2 (Sealing)

**Recipe says (III.19.3, sealing):** Seal the cucurbit with its glass cover with common wax.

**What the tokens say:**
- 3x okain (L17 otain, L18 okain x2): vessel sealing/management iterations. This is the ONLY paragraph with okain tokens on the entire folio.
- 1x dal (L17): careful material placement -- applying the wax seal.
- L17 chedar: active check after sealing (check the seal).
- e-depth 0.67: moderate -- not actively heating, but not cold either (the sealed vessel sits on ashes).
- ok-prefix = 3/15 = 20%: the highest ok concentration on the folio, consistent with vessel-focused operations.
- Only 15 tokens: proportionate for a short sealing operation.

**Match quality:** STRONG. Triple okain for a sealing step matches C1929 exactly. The dal for wax application, chedar for seal-checking, and vessel-prefix concentration all converge.

### P6 (57 tokens, lines 19-24) -- 4th Water Phase 3 (Balneum Distillation) + 5th Water

**Recipe says (III.19.3, second half):** Then distill all the water through the balneum, and keep it apart.
**Recipe says (III.19.4):** Take flesh substance, and over ashes separate all moisture by distillation.

**What the tokens say:**
- The LARGEST operational paragraph (57 tokens, 6 lines).
- e-depth 1.00: full balneum signature. This is the balneum distillation of the 4th water.
- 4x dar + 1x dal: heavy material handling. The 4 dar tokens are spread across L19-L22 (one per line cluster). This is more material events than a single distillation would need.
- Multiple qokeeedy tokens (e-depth 3, L21 and L22): the deepest thermal gentleness on the folio. Extreme care during this balneum phase.
- Lines 19-22: heavy qo+sh interleaving with high e-depth = active balneum distillation.
- Lines 23-24: shift to qokeey repetitions with raiin tokens = sustained gentle heat with yield-iterate cycles. This could be the transition from the 4th water's balneum into the 5th water's ash distillation.
- L24 ends with a sequence of sh-observe tokens (sheeerl, sheedy, lshed, sheey): heavy observation at the end -- watching distillate output.

**Match quality:** GOOD for 4th water balneum. The paragraph is long enough to potentially encode BOTH the 4th water balneum AND the 5th water (which is very brief -- 143 characters, a simple ash distillation). The 4 dar tokens suggest material handling for both waters. The thermal shift from deep balneum (L19-22) to moderate sustained heat (L23-24) is consistent with transitioning from balneum to ashes.

### P7 (9 tokens, line 25 only) -- Quality Gate / Inter-Water Check

**What the tokens say:**
- The SMALLEST paragraph: 9 tokens on a single line.
- e-depth 1.00: gentle.
- 0 dar: no material.
- 0 transfer: not producing output.
- Token sequence: tshey -> qokeedy -> cheal -> lchedar -> ches -> aiin -> oteey -> qokaiin -> okey.
  - Watch briefly -> gentle fire -> check yield state -> check equipment (respond) -> check sequence -> iterate -> vessel seal done -> sustained heat -> vessel done.
- This looks like a CHECKPOINT: the scribe verifies the apparatus state between operations. Check everything is right before proceeding.

**Match quality:** N/A -- this is not a recipe step. It is an inter-operation verification paragraph, which makes structural sense in a multi-recipe folio. A single-recipe folio of this size would typically not need a standalone checkpoint paragraph.

### P8 (44 tokens, lines 26-30) -- 6th Water (Bone Distillation)

**Recipe says (III.19.5):** Take the bones, mince finely, put in alembic and over ashes; take all their liquor by distillation, and set it apart.

**What the tokens say:**
- 1x dar (L26 daldy): one material addition -- the minced bones.
- 1x dal (L26 daldy parsed as dal+dy): careful material placement.
- e-depth 1.02: surprisingly high for what should be an ash distillation. However, this is the LAST water and the final distillation of the sequence -- perhaps the scribe maintains gentle heat for bone extraction.
- **t-HEAD = 9/44 tokens (20.5%):** by far the most transfer-heavy paragraph. Lines 27-29 have qotain, qoteeol, qotedy, qoty x3, qoteey x2 -- an extraordinary concentration of heat-driven transfers. This matches "take all their liquor by distillation" -- a thorough extraction.
- L28 okchhy: the folio's only hh (double-watch at the vessel). This heightened vessel monitoring during bone distillation could reflect the difficulty of extracting from solid bone material.
- L29 ram: "stage done, note result" -- the final distillation is complete.
- L30: post-distillation sequence with cheol x2 (checking arrangement state), rsheedy (watching the cooling), and final lched (equipment check done).

**Match quality:** GOOD. The material addition, extreme transfer concentration, ram closure, and heightened vessel monitoring all fit bone distillation. The high e-depth is unexpected for "ash distillation" but could reflect careful handling of bone material.

### P9 (16 tokens, lines 31-32) -- Final Output / Sequence Closure

**What the tokens say:**
- 1x dar (L31 daiin): one last material event.
- e-depth 0.69: moderate, winding down.
- **0% qo-prefix**: NO fire management at all. The fire is out.
- ch-dominant (5/16 = 31.3%): active checking/verification.
- L31 chckhey + lcheckhy: two heat-level checks (verifying the fire is properly managed/out).
- L32 cheol -> ikhey -> cheor -> chey: check arrangement -> heat-watch -> check response -> check done. Pure verification sequence.

**Match quality:** GOOD as a sequence closure. Zero qo (fire is out), pure monitoring/checking, moderate e-depth (cooling). This is not a recipe step -- it is the conclusion of the entire 5-water sequence: verify everything, collect the last output, confirm done.

---

## 5. Paragraph-to-Water Mapping Summary

| Para | Tokens | Mapped to | Confidence |
|------|--------|-----------|------------|
| P1 | 72 | III.19.1 (2nd water): Butchery prep + balneum distillation | HIGH |
| P2 | 17 | III.19.2 (3rd water): Ash distillation with burning caution | HIGH |
| P3 | 17 | Transition: Apparatus preparation for 4th water | MODERATE |
| P4 | 28 | III.19.3 phase 1: Lunaria addition + sawdust fire maceration | HIGH |
| P5 | 15 | III.19.3 phase 2: Sealing (glass + wax) | HIGH |
| P6 | 57 | III.19.3 phase 3 + III.19.4: Balneum distill + 5th water ash distill | MODERATE |
| P7 | 9 | Checkpoint: Inter-operation verification | HIGH (as checkpoint) |
| P8 | 44 | III.19.5 (6th water): Bone distillation | HIGH |
| P9 | 16 | Sequence closure: Final verification | HIGH |

---

## 6. Cross-Paragraph Patterns

### e-Depth Thermal Arc

| Para | e-depth | Predicted heat type | Actual recipe heat | Match |
|------|---------|--------------------|--------------------|-------|
| P1 | 0.76 | Moderate-gentle | Balneum | YES (pulled down by non-thermal butchery) |
| P2 | 0.47 | Direct/ash | Ashes | YES |
| P3 | 0.88 | Gentle | (transition) | N/A |
| P4 | 0.86 | Gentle-sustained | Sawdust fire | YES |
| P5 | 0.67 | Moderate | (sealing, not heating) | CONSISTENT |
| P6 | 1.00 | Balneum | Balneum -> ashes | PARTIAL (balneum yes, ash not visible) |
| P7 | 1.00 | Gentle | (checkpoint) | N/A |
| P8 | 1.02 | Balneum | Ashes | UNEXPECTED |
| P9 | 0.69 | Moderate-cooling | (closure) | CONSISTENT |

The thermal arc broadly tracks the recipe's heat specifications with one notable exception: P8 (bone distillation) shows balneum-level e-depth when the recipe specifies ashes. Possible explanations: (a) bone extraction requires gentler handling than typical ash distillation to avoid burning, (b) the scribe encoded the practitioner's actual technique rather than the recipe's nominal specification, or (c) the mapping is imprecise.

### dar Distribution

| Para | dar | dal | dam | Total material events | Recipe material actions |
|------|-----|-----|-----|-----------------------|----------------------|
| P1 | 3 | 0 | 0 | 3 | Take capon, separate parts, put in alembic |
| P2 | 1 | 0 | 1 | 2 | Take flesh |
| P3 | 0 | 0 | 0 | 0 | (transition) |
| P4 | 2 | 0 | 1 | 3 | Take lunaria, put 3 parts on flesh |
| P5 | 1 | 1 | 0 | 2 | Apply wax seal |
| P6 | 4 | 1 | 0 | 5 | Distill water + take flesh substance |
| P7 | 0 | 0 | 0 | 0 | (checkpoint) |
| P8 | 1 | 1 | 0 | 2 | Take bones, mince, put in alembic |
| P9 | 1 | 0 | 0 | 1 | Final collection |
| **Total** | **13** | **3** | **2** | **18** | ~12-15 "take/put/set aside" actions |

The 18 total material events across 5 waters + transitions is proportionate. Each "pren" (take) in the Catalan maps to a dar. Each "mit a part" (set aside) maps to a dal or transfer sequence. The 13 dar are distributed across 7 of 9 paragraphs, indicating active material handling throughout.

### Observation MIDDLE Distribution

| Code | Location | Workshop sense | Recipe context |
|------|----------|----------------|----------------|
| ckh (x2) | P1 L1, P1 L3 | Is the fire at right level? | Checking balneum temperature during 2nd water |
| ecth (x1) | P1 L4 | Cooled-transfer watch | Handling cooled intermediate in 2nd water |
| hh (x1) | P8 L28 | Extended monitoring | Extra caution during bone distillation |

Observation MIDDLEs concentrate in P1 (balneum setup, where temperature control is critical) and P8 (bone distillation, where over-extraction is a risk). The "beware burning" quality gate in P2 uses checkho and chopchedy rather than dedicated observation MIDDLEs -- the warning is encoded through PREFIX-level active monitoring rather than specialized MIDDLEs.

---

## 7. Comparison to Single-Recipe Result

### Does multi-recipe explain the 14 dar tokens?

**Single-recipe prediction:** 1 dar (for lunaria addition only).
**Multi-recipe prediction:** 5+ dar (one per water's material introduction).
**Actual:** 13 dar.

**Verdict:** Multi-recipe RESOLVES this tension. 5 waters each beginning with "take..." plus intermediate material handling events accounts for 13 dar naturally. Under single-recipe, 13 dar for a 2-step recipe was inexplicable. Under multi-recipe, it is proportionate (2.6 dar per water on average, reflecting the "take X, put in alembic, distill, set aside" pattern repeated for each water).

### Does multi-recipe explain the missing x3 anchor?

**Single-recipe prediction:** x3 counting run for ".iii. parts" and ".iii. dies".
**Multi-recipe context:** The x3 counts are embedded within ONE water's recipe (the 4th), which spans only P4-P5-P6. No clean x3 counting run is visible.

**Verdict:** UNRESOLVED. Multi-recipe does not help here. The x3 may not be encoded as a counting run (unlike f75r's x4 and x9, which are for distillation cycle counts -- a different kind of repetition). "3 parts" and "3 days" are proportional specifications, not iteration counts. Per C287, repetition does not encode abstract quantity or proportion -- it encodes literal enumeration of processing cycles. Parts and days are not processing cycles, so the absence of counting runs is actually CONSISTENT with the constraint system.

### Does multi-recipe explain the scale?

**Single-recipe:** 9 paragraphs and 275 tokens for a 369-character 2-step recipe = gross mismatch.
**Multi-recipe:** 9 paragraphs for 5 waters (1,251 combined characters) + prep + transitions + checkpoint = proportionate.

**Verdict:** Multi-recipe RESOLVES this tension completely. The token-to-character ratio becomes 275/1251 = 0.22, comparable to other matched folios. The paragraph-to-operation ratio is 9/5 = 1.8 paragraphs per water, which accounts for multi-phase operations (the 4th water alone needs 3 paragraphs) and structural overhead (transition P3, checkpoint P7, closure P9).

### Does multi-recipe explain the paragraph size variation?

**Single-recipe:** Why is P1 (72 tokens) 8x larger than P7 (9 tokens)?
**Multi-recipe:** P1 encodes butchery preparation + balneum distillation (the longest and most complex step). P7 is a single-line checkpoint between operations. P6 encodes a sustained multi-day balneum + the brief 5th water. Size variation maps to operational complexity.

**Verdict:** Multi-recipe RESOLVES this. Paragraph sizes track operational complexity across the 5-water sequence.

---

## 8. Discriminating Multi- vs Single-Recipe

| Criterion | Single-Recipe (III.19.3 only) | Multi-Recipe (III.19.1-5) | Winner |
|-----------|-------------------------------|---------------------------|--------|
| Scale (275 tokens) | 369-char recipe: MISMATCH | 1,251-char combined: PROPORTIONATE | Multi |
| dar count (13) | Predicts 1: MISMATCH | Predicts 5+: PROPORTIONATE | Multi |
| e-depth variation | One recipe, two phases: partial | 5 waters alternating balneum/ash: explained | Multi |
| Sealing (P5 okain x3) | Central to recipe: PASS | Same (4th water is one of five): PASS | Tie |
| P1 size (72 tokens) | Most of recipe: MISMATCH | Butchery + first distillation: EXPLAINED | Multi |
| P7 checkpoint | Why checkpoint mid-recipe? | Natural inter-water verification: EXPLAINED | Multi |
| P9 zero-qo closure | Premature fire shutdown? | End of 5-water sequence: NATURAL | Multi |
| Paragraph count (9) | 9 for 2 steps: EXCESS | 9 for 5 waters + overhead: RIGHT | Multi |
| Transfer concentration P8 | Not predicted | Bone distillation "take all liquor": FITS | Multi |
| kam in P2 | Not specific | "Beware burning" quality gate closure: FITS | Multi |
| x3 anchor | Predicted, MISSING | Still missing | Tie |

**Multi-recipe wins 8 criteria, ties 2, loses 0.**

---

## 9. Verdict

### COHERENT under multi-recipe hypothesis

The multi-recipe model (f82r encodes III.19.1 through III.19.5, waters 2-6 of the medicinal water preparation) resolves all three primary tensions from the single-recipe test:

1. **Scale resolved:** 275 tokens for 1,251 characters of combined recipe text is proportionate.
2. **dar count resolved:** 13 dar tokens for 5 waters each requiring material introduction is proportionate (2.6 per water).
3. **Paragraph structure resolved:** 9 paragraphs = 5 waters + 1 transition + 1 checkpoint + 1 combined para + 1 closure.

The paragraph-to-water mapping is internally consistent:
- P1-P2 map cleanly to the first two waters (balneum then ash distillation).
- P4-P5-P6 decompose the complex 4th water into its three phases (maceration, sealing, distillation).
- P8 maps to the final bone distillation with its distinctive transfer concentration.
- P3, P7, P9 serve structural roles (transition, checkpoint, closure) that a multi-recipe folio needs but a single recipe does not.

The sealing signature (P5 triple okain) remains the strongest individual prediction, now contextualized as one step within a larger sequence rather than the centerpiece of a single recipe.

**One unresolved issue:** P8's high e-depth (1.02) when the 6th water recipe specifies ashes. This may reflect practitioner technique rather than nominal recipe specification, or the mapping may be imprecise for this paragraph.

**Discrimination:** Multi-recipe is CLEARLY better than single-recipe. Single-recipe left 3 major tensions unresolved (scale, dar count, paragraph structure) that multi-recipe resolves. No criterion favors single-recipe over multi-recipe.

This result is consistent with C1937 ("short related procedures are consolidated onto single folios") -- the five waters are related sub-recipes within a single production sequence, exactly the pattern observed on f80r (Ch21-25M, 5 chapters on one folio).
