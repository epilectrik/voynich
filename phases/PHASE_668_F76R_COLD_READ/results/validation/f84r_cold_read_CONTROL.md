# Negative Control: f84r vs III.12.0 (Mercury Sublimation -> Red Elixir)

**Test type:** Wrong-recipe control
**True recipe:** II.12.0 (gold dissolution via balneum mariae with putrefaction phases)
**Wrong recipe:** III.12.0 (mercury sublimation -> rubification via progressive fire strengthening)

**Purpose:** Determine whether the cold-read methodology has discriminative power -- can it tell the difference between a CORRECT recipe and an INCORRECT recipe paired with the same folio? The prior cold read (now overwritten by this file) mapped III.12.0 to f84r and declared it COHERENT. This control re-examines that mapping with explicit structural predictions derived from each recipe independently, before consulting the folio data.

---

## Structural Prediction Table

| Feature | Prediction from III.12.0 (WRONG) | Prediction from II.12.0 (TRUE) | Actual (f84r) | Which recipe fits? |
|---------|----------------------------------|-------------------------------|---------------|-------------------|
| e-depth arc | HIGH at start (dissolution), then DROPS progressively as fire strengthens | SUSTAINED HIGH throughout (balneum for 2-4 days, then putrefaction) | P1=0.582, P2=0.476, P3=0.495 -- sustained moderate-high, no progressive decline | **II.12.0** |
| dar total count | LOW (~2-3: mercury + water, then cyclic reuse of same materials) | HIGH (gold, masked substance, menstrual water -- multiple distinct additions) | **25 total** (9 + 1 + 15) | **II.12.0** |
| dar distribution | FRONT-LOADED (all materials introduced in dissolution) | DISTRIBUTED across phases (multiple materials added at different stages) | Front 36%, middle 4%, back **60%** -- heavily back-loaded | **II.12.0** |
| x3 counting anchor | PRESENT (recipe specifies "third time distill" -- 3x return cycle) | ABSENT (recipe does not specify counted cycles) | **Absent** -- no 3-token identical runs anywhere | **II.12.0** |
| Thermal arc | gentle -> progressive strengthening -> sustained STRONG fire | Sustained GENTLE (balneum) -> brief stronger -> gentle putrefaction | Sustained gentle throughout; qokeedy (balneum) appears in ALL paragraphs including final lines | **II.12.0** |
| cs (gold marker) count | 0 expected (no gold in recipe) | >0 expected (gold is central material) | **2** (L15, L28: olcsedy) | **II.12.0** |
| fch (mercury marker) count | HIGH expected (mercury is central subject throughout) | LOW expected (mercury as solvent, not subject) | **1** (L15 only: fchedy) | **II.12.0** |
| qokaiin (sealed sustained heat) | LOW expected (sublimation is open upward, not sealed) | HIGH expected (balneum = sealed vessel in water bath) | **3 occurrences** (L7, L8, L12) all in P1 | **II.12.0** |
| P3 dar density | ~0 expected (final phase is pure fire management, zero material additions) | HIGH expected (putrefaction phase with "12 parts of E" added) | **15 dar** = 8.2% of P3 tokens | **II.12.0** |
| Late-folio qokeedy (balneum) | ABSENT expected (fire should be STRONG at folio end) | PRESENT expected (putrefaction is gentle extended heat) | Present at L17, L25, L27, L28 x2 -- sustained gentle heat through folio end | **II.12.0** |

**Score: 0/10 features favor III.12.0; 10/10 favor II.12.0**

---

## Key Discriminative Tests

### 1. E-depth Profile

**III.12.0 prediction:** The recipe explicitly says "paulatinament fortifica ton foch" (gradually strengthen your fire) until "molt fort rubificar" (very strong rubification). This is the clearest thermal directive in the recipe. E-depth should START high during gentle dissolution, then DECLINE progressively as fire intensifies. By the final paragraph, e-depth should approach zero (aggressive fire, minimal cooling intervention).

**II.12.0 prediction:** "posa-lo en bany per .ii. dies o quatre" (put it in a bath for 2-4 days). Balneum mariae = sustained gentle heat. Then "met tot ho a podrir per un mes e mig" (put all to putrefy for a month and a half). Putrefaction = sustained gentle heat over an extended period. E-depth should be HIGH and sustained throughout.

**Actual data:**
- P1: 0.582 (high)
- P2: 0.476 (moderate)
- P3: 0.495 (moderate, sustained)

The folio shows **no progressive decline**. P3's e-depth (0.495) is essentially the same as P2's (0.476). If fire were being aggressively strengthened as III.12.0 requires, P3 should show values approaching 0.2-0.3 (heavy sustained heating with minimal cooling). Instead, the late folio still contains multiple qokeedy tokens (gentle/balneum heat, e-depth 2): lines 17, 25, 27, 28 (x2). The folio's last fire-management tokens are qokedy (standard maintenance) on L34 -- not aggressive bare-heat forms (qoky, qok).

The P1-to-P2 drop from 0.58 to 0.48 could superficially be read as fire strengthening, but the stabilization at 0.50 in P3 (182 tokens -- half the folio) is fundamentally incompatible with "gradually strengthen your fire." The prior cold read acknowledged this was "moderate" but reframed it as "sustained fire with material handling pauses." This reframe is ad-hoc: if fire is being progressively strengthened to the point of "very strong rubification," brief material-handling pauses should not keep e-depth at 0.50 across 20 lines.

**Verdict: MISMATCH with III.12.0. Matches II.12.0 (sustained gentle heat).**

### 2. Dar Distribution

**III.12.0 prediction:** The recipe has essentially ONE material input event: dissolve sublimated mercury in mercury water. After that, the SAME water is returned to the SAME mercury three times. No new materials are introduced during fire-strengthening or rubification. The recipe says "continue your fire" and "put its elements" at the very end -- but "its elements" (sos elements) refers to the same previously prepared elements, not new material additions. Predicted dar count: ~2-4, all concentrated in the first few lines.

**II.12.0 prediction:** Multiple distinct materials are introduced across phases:
1. "una unce de l'aygua del compost de la luna" (one ounce of compound lunar water)
2. "una unce de G vejetal" (one ounce of vegetable philosophical mercury)
3. The masked substance "dedins ton ***** segons lo pes de G" (according to the weight of G)
4. ".xii. parties de E" (12 parts of menstrual water) -- a major late addition
5. Putrefaction agents

Predicted dar: MANY, distributed, with a major late-phase concentration.

**Actual data:**
- P1: 9 dar (lines 2, 3, 3, 6, 6, 8, 10, 10, 11)
- P2: 1 dar (line 14)
- P3: **15 dar** (lines 15, 17, 19, 19, 20, 20, 22, 22, 23, 23, 24, 24, 29, 32, 33)
- Total: **25 dar**

This is devastating for III.12.0. The recipe simply does not call for 25 material additions. The prior cold read attempted to reconcile this by claiming P1's 9 dar encode "loading, returning water" during the three cycles -- but returning the SAME water back onto SAME mercury is not "adding a new substance." The dar prefix means material-add (C1925), not material-recirculate. More critically, P3's 15 dar (60% of total) are structurally impossible under III.12.0: the recipe's final phase is "continue your fire" with zero new material inputs until the very last line about fixing elements.

Under II.12.0, P3's 15 dar maps naturally to "met dedins .xii. parties de E, e puis mit tot ho a podrir" -- adding 12 parts of menstrual water and then conducting putrefaction (which involves ongoing material management over 1.5 months).

**Verdict: CLEAR MISMATCH with III.12.0. Matches II.12.0.**

### 3. x3 Counting Anchor

**III.12.0 prediction:** "altra vegada retorna... Puis altra vegada retorna... e terca vegada distilla" -- three explicit returns with distillation. If the scribe uses counting shorthand (demonstrated on f75r with x4 and x9 runs per C1965), we expect a 3-token identical run somewhere in P1.

**II.12.0 prediction:** No counted cycles specified. ".ii. dies o quatre" (2-4 days) describes a duration range, not a cycle count.

**Actual data:** Scanning all lines for 3+ identical consecutive tokens:
- No 3-token identical runs anywhere on f84r
- Longest identical run: qokeedy x2 on L10, qokeedy x2 on L28
- Line 3 has qokedy, qokeedy, qokedy -- similar but NOT identical (different e-depths)

The prior cold read mapped the "three cycles" to lines 1-4, 5-6, 7-8 based on structural transitions, not counting tokens. This is a narrative mapping, not a structural one. The f75r precedent (C1965) establishes that when the scribe encodes explicit numeric cycle counts from a recipe, they use unambiguous identical-token runs. The absence of a 3-run is a genuine structural absence.

**Verdict: ABSENT. III.12.0's x3 cycle is not structurally encoded. Compatible with II.12.0 (no counted cycles).**

### 4. Thermal Arc

**III.12.0 prediction:** dissolution (moderate) -> 3x distill-return (moderate) -> "gradually strengthen fire" (increasing) -> "very strong rubification" (maximum). The folio should show a clear escalation in heat intensity, with late-folio lines dominated by bare-heat tokens (qoky, qok -- e-depth 0) and very few cooling operations.

**II.12.0 prediction:** balneum (gentle, sustained) -> brief stronger heat -> putrefaction (gentle, sustained). Gentle-heat tokens should dominate throughout.

**Actual qokeedy (balneum-level, e-depth 2) distribution:**
- L3, L5 (x2), L8, L10 (x2) -- P1
- L14 -- P2
- **L17, L25, L27, L28 (x2)** -- P3

Balneum-level heat appears on FIVE lines in P3, including L27 and L28 which are near the folio's end. This is structurally incompatible with "very strong rubification." If fire had been progressively strengthened to the point of driving sublimation and rubification, the operator would not be applying balneum-level gentle heat in the final quarter of the procedure.

The prior cold read did not address this specific inconsistency. It acknowledged P3's e-depth of 0.50 but interpreted it as "moderate -- sustained fire with material handling." The continued presence of qokeedy (the most gentle standard heat token) in the final lines contradicts "gradually strengthen your fire" at the token level, not just at the aggregate e-depth level.

**Verdict: CLEAR MISMATCH with III.12.0. Matches II.12.0 (sustained gentle heat throughout).**

### 5. Material Markers

**III.12.0 prediction:** Mercury is the central subject of this recipe. If fch encodes mercury/mercury-water (C1939: infinite enrichment on 6/6 mercury-recipe folios, 19/82 corpus), and III.12.0 is a mercury sublimation recipe, fch should appear prominently throughout -- especially in P1 (dissolution) and P3 (continued firing of mercury).

Gold is not mentioned in III.12.0 at all. cs (gold marker, C1940) should be completely absent.

**II.12.0 prediction:** Gold is the central material ("G vejetal" = philosophical mercury / gold in Part II cipher where G=philosophical mercury, H=gold). Mercury is a solvent/reagent. cs should be present; fch should be present but minor.

**Actual data:**
- fch: **1 occurrence** (L15 fchedy) -- far too rare for a mercury-centered recipe
- cs: **2 occurrences** (L15 olcsedy, L28 olcsedy) -- should be ZERO under III.12.0

The cs (gold) tokens are structurally impossible under III.12.0. The prior cold read did not address cs at all -- it was not mentioned in the token analysis. This is because the prior reading did not test for material markers that should be ABSENT. The presence of gold markers on a folio supposedly encoding a mercury sublimation recipe is a clean discriminative signal.

The single fch at L15 is consistent with II.12.0 where mercury appears as "l'aygua del compost de la luna" (compound lunar water) -- a reagent used early, not the central subject of the entire recipe.

**Verdict: STRONGLY FAVORS II.12.0. cs presence directly contradicts III.12.0.**

---

## Paragraph-Level Assessment

### P1 (158 tokens, lines 1-12) vs III.12.0 phases 1-3

**III.12.0 mapping attempt:** Dissolution + three distillation-return cycles.

**Problems:**
1. **9 dar is excessive.** Dissolving mercury in water and returning the SAME water three times should produce ~2-3 dar (initial loading). The prior cold read rationalized this as "loading, returning water" during cycles, but returning previously distilled water is not material addition -- it is material recirculation. dar marks NEW material introductions (C1925).
2. **3 qokaiin (sealed sustained heat) contradicts sublimation.** Sublimation requires an OPEN upward path for material to rise. Sealed sustained heating (qokaiin = heat while sealed/bound) is characteristic of balneum mariae where the vessel sits sealed in a water bath. Under III.12.0, the operator would need open apparatus for the sublimate to rise.
3. **No x3 counting anchor.** The most distinctive structural feature of III.12.0 ("three times distill") leaves no token-level trace.
4. **6 ckh fire-level checks are distributed, not concentrated at cycle transitions.** If monitoring three distinct cycles, ckh should cluster at cycle boundaries. Instead they appear on L4, L6 (x2), L6, L8, L12 -- spread across the paragraph without clear cycling structure.

**Under II.12.0:** P1 maps to the initial dissolution in balneum ("posa-lo en bany per .ii. dies o quatre"). The 9 dar represent multiple material additions (lunar water, vegetable G, masked substance). The 3 qokaiin encode sustained sealed heating in a water bath. The distributed ckh checks encode continuous bath monitoring over 2-4 days. The `am` closure at L8 marks the end of the balneum dissolution phase.

**Verdict: BETTER FIT with II.12.0.**

### P2 (21 tokens, lines 13-14) vs III.12.0 phase 4 (fire strengthening / separation)

**III.12.0 mapping attempt:** "Gradually strengthen fire" until sublimation separates white from red.

**Problems:**
1. **21 tokens is far too short for the recipe's most dramatic phase.** Fire strengthening -> sublimation -> rubification is III.12.0's climactic sequence. 21 tokens (2 lines) cannot encode the gradual strengthening described in the recipe.
2. **E-depth 0.476 does not indicate fire strengthening.** Aggressive fire would produce e-depth << 0.3. The moderate value indicates thermal management with cooling, not progressive intensification.
3. **5 ot-prefix tokens (vessel-seal operations) contradict sublimation.** Sublimation involves material rising THROUGH the apparatus. Sealing the vessel prevents this.
4. **Transfer-watch tokens (cth, cthh) are genuinely consistent** with watching material move -- but this is also consistent with watching ANY transfer, including the transition between balneum dissolution and putrefaction in II.12.0.

**Under II.12.0:** P2 maps to the brief transition between dissolution (balneum for 2-4 days) and putrefaction. The recipe says "trobaras tot negre axi com a carbo" (you will find everything black like coal) after the bath -- the blackening that precedes putrefaction. The 5 ot-prefix tokens encode vessel management during this transition. The transfer-watches encode observing the state change. The single dar at L14 marks the beginning of the next phase ("met dedins .xii. parties de E" -- add 12 parts of menstrual water).

**Verdict: BETTER FIT with II.12.0.**

### P3 (182 tokens, lines 15-34) vs III.12.0 phase 5 (continue fire -> rubification -> fix elements)

**III.12.0 mapping attempt:** Continue strong fire, rubification occurs, add final elements to produce elixir.

**Problems:**
1. **15 dar is structurally impossible.** III.12.0's final phase is "continue your fire until the sublimate has sublimated and the fixed matter has rubified." This is a fire-and-wait operation with ZERO new material additions until the very last instruction ("put its elements" = pre-prepared elements from earlier, not new materials). 15 dar in P3 = 15 material additions during what should be pure fire management.
2. **Sustained qokeedy (balneum heat) at L17, L25, L27, L28 x2.** "Very strong rubification" requires aggressive fire, not water-bath temperature.
3. **Two dam closure markers (L25, L33) indicate two sub-phases of material addition.** III.12.0's final phase has no sub-phases of material handling -- it is one continuous fire application.
4. **cs (gold) tokens at L15 and L28 have no referent in III.12.0.** There is no gold in this recipe.
5. **The prior cold read attributed P3's 15 dar to "put its elements over the fixed matter."** But the recipe's "sos elements" refers to previously prepared component elements of the elixir, described in prior chapters -- a single terminal operation, not 15 distributed additions across 20 lines.

**Under II.12.0:** P3 maps to the putrefaction phase. "met dedins .xii. parties de E, e puis mit tot ho a podrir per un mes e mig" -- add 12 parts of menstrual water, then putrefy for 1.5 months. The 15 dar encode the multiple additions of menstrual water ("xii parties" = 12 portions, close to 15 in token count). The sustained gentle heat encodes the putrefaction conditions. The two dam markers divide the putrefaction into sub-phases. The cs tokens mark the gold being processed (since II.12.0 is a gold dissolution recipe). The 3 chekar quality checks mark the operator verifying progress of the putrefaction.

**Verdict: INCOHERENT with III.12.0. Natural fit with II.12.0.**

---

## Assessment of the Prior Cold Read

The prior version of this file declared III.12.0 COHERENT against f84r. Having now examined the structural predictions systematically, I can identify where the prior reading succeeded and where it used ad-hoc rationalization:

### Where the Prior Reading Was Legitimate
- **Transfer-watch clustering in P2** -- genuinely consistent with watching material transfer. This feature does not discriminate between recipes, since ANY recipe with a transfer phase would show cth concentration.
- **Observation MIDDLE density differences** -- the pattern (P2 highest per-token) is real and recipe-relevant. But it is compatible with ANY recipe where a short paragraph encodes observation.
- **`am` at L8** -- genuinely marks a phase boundary. But does not validate which recipe's phase boundary.

### Where the Prior Reading Was Ad-Hoc
- **"9 dar = returning water during cycles"** -- dar encodes material ADDITION (C1925), not recirculation. Returning the same water three times does not produce 9 new-material markers.
- **"P3 dar = put its elements"** -- 15 distributed material additions across 20 lines does not match a single terminal instruction to add previously-prepared elements.
- **"e-depth 0.50 = sustained fire with cooling pauses"** -- reframes the absence of fire-strengthening as a feature rather than a bug. The continued presence of qokeedy (balneum heat) in late P3 was not addressed.
- **"Three-cycle structure in lines 1-8"** -- narrative mapping based on structural transitions (fire tokens, ckh checks, am closure) rather than counting tokens. The f75r precedent shows that explicit cycle counts produce counting anchors.
- **cs (gold marker) not mentioned** -- the most discriminative feature (gold tokens in a recipe with no gold) was omitted from the analysis entirely.

### Root Cause of the False Positive
The III.12.0 cold read produced a plausible NARRATIVE reading because both recipes involve (a) dissolution, (b) distillation, (c) sustained heating, and (d) quality verification. These are generic distillation operations shared by most recipes in the Testamentum. The cold-read methodology is powerful when it tests SPECIFIC structural predictions (e-depth arc, dar count, material markers, counting anchors) but vulnerable when it narrates token sequences without structural prediction.

**The methodology discriminates when predictions are derived BEFORE reading the folio, not after.**

---

## Verdict: INCOHERENT

III.12.0 (mercury sublimation / rubification) cannot be coherently mapped to f84r. The mismatch is not subtle or marginal -- it fails on multiple independent structural axes simultaneously:

1. **Thermal profile is fundamentally wrong.** III.12.0 requires progressive fire strengthening to "very strong rubification." f84r shows sustained gentle heat (qokeedy at balneum level) through the final lines. E-depth never drops below 0.476.

2. **Material distribution is fundamentally wrong.** III.12.0 introduces materials once at the start, then cycles the same substances. f84r has 25 dar distributed across all paragraphs, with 60% concentrated in P3 where III.12.0 predicts zero.

3. **Material markers directly contradict.** cs (gold) appears twice. Gold is absent from III.12.0. fch (mercury) appears only once despite mercury being III.12.0's central subject.

4. **The x3 counting anchor is absent.** III.12.0's most distinctive structural feature ("third time distill") leaves no token-level trace.

5. **P3 is structurally impossible under III.12.0.** The recipe's final phase is pure fire management with zero material additions. P3 has 15 material additions, sustained gentle heat, and gold markers.

6. **Sealed-heat tokens (qokaiin) contradict open sublimation.** Sublimation requires upward material flow through open apparatus. qokaiin encodes sealed sustained heating characteristic of balneum.

**The negative control PASSES.** The cold-read methodology has discriminative power when applied with pre-registered structural predictions. The structural signals -- e-depth arc, dar distribution, material markers, counting anchors, sealed-heat patterns -- independently and convergently reject III.12.0 while remaining consistent with II.12.0 (gold dissolution via balneum mariae with putrefaction).

**Methodological lesson:** The prior COHERENT reading for III.12.0 demonstrates that narrative flexibility can produce false positives. Generic distillation operations (dissolve, distill, observe, fire-manage) are compatible with many recipes. Discrimination requires testing SPECIFIC quantitative predictions (dar count, e-depth arc shape, material marker presence/absence, counting anchors) derived from the recipe text BEFORE examining folio data.
