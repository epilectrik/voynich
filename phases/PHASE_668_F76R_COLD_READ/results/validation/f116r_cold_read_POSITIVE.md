# Positive Control: f116r ↔ III.4.0 Fixation of Sublimated Mercury

**Match tier:** NOT MATCHED (8D matching never assigned this pair)
**Verdict:** PARTIALLY COHERENT — structural patterns align on 4/7 predictions, but critical mercury marker (fch) is completely absent, and the recipe's two-part structure does not map cleanly onto the folio's 8-paragraph layout.

---

## The Recipe (III.4.0 — SISMEL Catalan)

> Quant hauràs sublimat e presa la pura substancia del mercuri, adonchs fixaràs la una part de aquell. E quant aquella part serrà fixada, fixarà aprés l'altra. Donchs, reitera la sublimació de la partida no fixa sobra la cosa fixa, en tro que aquella semblantment sia fixa. La qual cosa temptaràs assaiant si bona fusió prestarà sobre lo foch. E si ho fa, fet és; e si non fa, ajusta-li de l'argent viu exuberat en reiterant sa sublimació en tro que sia fusible. E la manera de la exuberació de tot argent viu te havem dat... Mas si la vols més composta, dissol altre mercuri en l'aygua primera que és exuberada de la ànima del dit mercuri; e puys separa l'aygua per distilació, e así reitera en distillant e redistillant sobre ses feces en tro haya beguda l'aygua e tirada a ella tota la humiditat de les feces mercurials. Ffill, aquesta és la humiditat encerativa que sobre totes les altres està contra la batalla del foch.

*Cipher note: III.4.0 is in Part III (Liber Mercuriorum). Letter codes: B=simple water, C=simple red sulphur, D=simple dissolved gold. "Argent viu" (quicksilver/mercury) appears in plaintext here, not in cipher.*

**Translation:** When you have sublimated and taken the pure mercury substance, fix one part of it. When that part is fixed, fix the other. Reiterate sublimation of the unfixed part over the fixed, until both are fixed. Test by trying if good fusion occurs on fire. If yes, done. If not, add exuberated quicksilver and reiterate sublimation until fusible. For a more complex version: dissolve other mercury in the first water (exuberated from said mercury's soul), separate water by distillation, reiterate distilling and redistilling over dregs until all moisture is absorbed. This is the incerative moisture that withstands fire.

**Recipe structure:**
1. Fix part A of sublimated mercury
2. Fix part B using part A
3. Reiterate sublimation of unfixed over fixed
4. FUSIBILITY TEST: try on fire — if it melts, done
5. If fails: add exuberated quicksilver, reiterate
6. Alternative: dissolve more mercury in first water
7. Distill/redistill over dregs until all moisture absorbed
8. Result: incerative moisture (fire-resistant)

---

## The Folio

**f116r:** 537 tokens, 50 lines, 8 paragraphs (gallows-delimited)

| Para | Lines | Tokens | dar | chekar | e-depth | Obs MIDDLEs | Mapped recipe phase |
|------|-------|--------|-----|--------|---------|-------------|---------------------|
| P1 | 1–3 | 33 | 1 | 0 | 0.42 | — | Fix part A? |
| P2 | 4–6 | 33 | 1 | 0 | 0.55 | 1 ckh | Fix part B? |
| P3 | 7–14 | 80 | 4 | 0 | 0.64 | — | Reiterated sublimation |
| P4 | 15–17 | 32 | 5 | 0 | 0.62 | 1 cth | Material additions (quicksilver) |
| P5 | 18 | 12 | 0 | 0 | 0.50 | — | Transition / test? |
| P6 | 19–30 | 140 | 4 | 2 | 0.50 | 4 cth, 4 ckh | Main complex operation + testing |
| P7 | 31–36 | 65 | 1 | 1 | 0.57 | 2 ckh, 1 hh | Distillation / redistillation |
| P8 | 37–49 | 142 | 3 | 1 | 0.48 | 4 ckh, 1 cphh, 1 cth, 1 hh | Final redistillation over dregs |

**e-depth** measures the ratio of cooling atoms (`e`) to total atoms. Higher values = more cooling intervention (active distillation). Lower values = more sustained uninterrupted heat (fixation, sublimation). The values on f116r cluster in the 0.42–0.64 range, indicating moderate thermal intensity throughout — consistent with fixation (sustained heating without heavy cooling), rather than the sharp thermal arcs typical of reflux distillation.

---

## Prediction Table

| # | Prediction | Expected | Observed | Verdict |
|---|-----------|----------|----------|---------|
| 1 | Low e-depth (fixation = sustained strong heat) | e-depth < 0.40 across most paragraphs | Mean e-depths 0.42–0.64; P1 lowest at 0.42, P3/P4 highest at 0.62–0.64 | **PARTIAL** — P1 is on the low end but paragraphs overall are moderate, not low. The recipe also includes distillation steps (latter half), which raise e-depth. Not a clean pass. |
| 2 | Iterative structure | High -ain/-aiin density, repeated cycling tokens | qokain appears 23x across the folio; aiin appears 7x; extensive iteration vocabulary throughout all paragraphs | **PASS** — Clear iterative structure. "Reitera la sublimació" maps to sustained qokain cycling. |
| 3 | FUSIBILITY TEST: chekar or observation MIDDLE | At least 1 chekar token at a structural boundary | 4 chekar/checkhy tokens: P6 (2), P7 (1), P8 (1). Also chckhy/shckhy (heat-level checks) appear 12+ times across folio | **PASS** — Concentrated in P6 onward, exactly where the recipe's test-and-iterate loop begins. |
| 4 | fch mercury markers | fch tokens present (mercury is the subject) | **0 fch tokens on entire folio** | **FAIL** — Complete absence. C1939 established fch as mercury marker with high enrichment on mercury-recipe folios. This is a strong negative signal. |
| 5 | dar tokens for adding quicksilver | dar > 3, concentrated at material addition points | 19 dar tokens total (1+1+4+5+0+4+1+3). Highest concentration in P4 (5) and P3/P6 (4 each) | **PASS** — Exceptionally high dar count. P4's 5 dar tokens in 32 tokens = 15.6%, consistent with the recipe's "add exuberated quicksilver" conditional additions. |
| 6 | Two-part structure (simple then complex) | Clear structural break around paragraph 4–5, with second half more complex | P5 is a single-line 12-token paragraph that could mark a structural break. P6 (140 tokens) is the largest paragraph. P1–P4 average 44 tokens; P6–P8 average 116 tokens. | **PASS** — Clear size asymmetry: first half = small paragraphs (setup/simple fixation), second half = large paragraphs (complex alternative). P5 as structural hinge. |
| 7 | Cohobation pattern (distill/redistill over dregs) | Late paragraphs show cycling qo heat interspersed with ot vessel tokens, repeated dar | P8 (L37–49): 24 qo-prefix tokens, 3 ot-prefix, 3 da-prefix, heavy sh observation. Line 42: qokain-sheckhy-qokain-shekain-shkain-shedy = pure heat+observe cycling. | **PARTIAL** — P8 shows sustained heat-observe cycling but lacks the specific vessel-dreg interaction pattern (ot tokens are sparse). The redistillation is plausible but not diagnostic. |

**Score: 4 PASS, 2 PARTIAL, 1 FAIL out of 7 predictions.**

---

## Paragraph-by-Paragraph Assessment

### P1 (Lines 1–3, 33 tokens) — Initial Fixation Setup?

**Recipe says:** "When you have sublimated and taken the pure mercury substance, fix one part of it."

**What the tokens say:**

P1 opens with `kchdpy` (precision-heat) then `shey` (watch briefly) and `qokain` (sustained cyclic heating). The line then moves to vessel operations: `otalshedy` (seal vessel, watch state), `shear` (observe the yield), `ain` (iterate), `or` (note result). Line 2 shows cooling attention: double `okeey` (vessel: gentle cooling done), then iterative binding `okain` (seal vessel for cycle). Line 3 has the paragraph's single `dain` (bind material into cycle), followed by apparatus tokens `lshey`, `cthy` (transfer-watch observation MIDDLE), `lshedy` (equipment check).

The low e-depth (0.42) is consistent with fixation — sustained heating without heavy cooling intervention. The vocabulary is primarily observation and vessel management during a heating cycle.

**Match assessment:** Plausible as initial fixation. Low thermal complexity, single material binding, sustained heating with observation.

### P2 (Lines 4–6, 33 tokens) — Second Fixation?

**Recipe says:** "When that part is fixed, fix the other."

**What the tokens say:**

P2 opens with `padar` (an unusual token — possibly paragraph-initial infrastructure). The paragraph is dominated by ot-prefix tokens (8 total): `oteedy` (2x), `otedy`, `otey`, `otor`, `oty` — intensive transfer-rate monitoring. Line 4 has `chckhy` (check heat level — observation MIDDLE ckh), the paragraph's single observation point. Line 5 introduces `dain` (bind material) followed by `qokchdy` (adjust fire while watching), showing active heat management with monitoring.

The e-depth rises to 0.55, and the heavy ot-prefix presence suggests transfer monitoring — watching what comes over or through. This is less like fixation and more like a step where material is being transferred or tested.

**Match assessment:** Partially consistent. The ot-dominant character suggests monitoring material behavior (melting? sublimation transfer?), which could map to testing whether Part A is fixed before proceeding to Part B.

### P3 (Lines 7–14, 80 tokens) — Reiterated Sublimation

**Recipe says:** "Reiterate the sublimation of the unfixed part over the fixed, until both are fixed."

**What the tokens say:**

This is the folio's largest structurally active paragraph. Line 7 opens with `pchol` (paragraph setup) then immediately goes to heat: `qo` bare, `qokain` (sustained cyclic heating), `qoteey` (gentle heat transfer). Lines 8–9 are heavily qo-dominated: `qokeey` (gentle heat × 2), `qokeedy` (balneum-level heat × 2), `qokain` (sustained cycling × 3). This is intensive, sustained, iterative thermal processing.

The 4 dar tokens (L8 dar, L10 dar, L12 dain × 2) punctuate the thermal cycling — material is being re-introduced at intervals. Line 10 has `checkhy` (quality check with observation — "is the product fusible yet?") followed by `dar` + `shedy` + `qokeedy` — check quality, add material, observe, heat gently. This pattern repeats.

E-depth of 0.64 is the folio's highest, indicating active cooling/stabilization between heating cycles — exactly what sublimation-then-cooling-then-resublimation looks like.

**Match assessment:** Strong. Iterative heat cycling with periodic material reintroduction and quality checking maps well to "reiterate sublimation until fixed." The highest e-depth paragraph reflects the thermal cycling of sublimation (heat up, sublime, cool, collect, repeat).

### P4 (Lines 15–17, 32 tokens) — Conditional Material Addition

**Recipe says:** "If not [fusible], add exuberated quicksilver and reiterate sublimation until fusible."

**What the tokens say:**

P4 has the folio's highest dar concentration: 5 dar/dain/daiin tokens in 32 tokens (15.6%). Line 15 opens with vessel operations (`pchoetal`, `otedal`, `otal`) then `daiin` (start a new material cycle) → `okeedy` (gentle vessel cooling) → `qoky` (cease heating) → `dar` (add substance). Line 16: another `dar` followed by monitoring (`chedy`, `sheedy`), then `shcthy` (transfer-watch observation: cth MIDDLE) — watching what's being added or transformed. Line 17: `dain` → `chey` → `qokeey` → `okeey` — add material, check, heat gently, cool vessel.

The e-depth of 0.62 (high) plus heavy material addition = adding quicksilver and immediately subjecting it to thermal cycling. The `shcthy` (cth observation) midway through is watching the transformation during addition.

**Match assessment:** Strong. The dar concentration is the folio's highest, precisely where the recipe says to add more quicksilver. The thermal cycling after each addition maps to "reiterate sublimation until fusible."

### P5 (Line 18, 12 tokens) — Structural Transition

**Recipe says:** (Between simple fixation and complex alternative)

**What the tokens say:**

A single short line: `pcharalor` (paragraph opener) → `qokey` (heat done) → `rain` → `otedy` (check drip rate) → `opain` → vessel operations → `oteeedy` (extended gentle transfer monitoring) → `ches` → `ary` (close).

Only 12 tokens, no dar, no observation MIDDLEs. The `oteeedy` with triple-e is extremely rare (deep gentle monitoring of transfer). This reads as a brief checkpoint — assessing the state before the next major phase.

**Match assessment:** Plausible as structural hinge. The recipe shifts from "simple fixation" to "but if you want it more complex..." This brief paragraph could mark that transition.

### P6 (Lines 19–30, 140 tokens) — Complex Operation with Testing

**Recipe says:** "Dissolve other mercury in the first water... separate the water by distillation..."

**What the tokens say:**

The folio's largest paragraph. Heavy prefix diversity: ch=28, qo=20, sh=16, ot=10, ok=9 — all major operational channels active simultaneously. This is the most complex paragraph on the folio.

The two chekar tokens appear here (P6's first observation MIDDLEs of this type on the folio). Line 10 has `checkhy` (full quality check: cool, adjust, heat, watch) — the fusibility test? Line 21 has `shckhy` (passively observe the heat level). Lines 22, 24, 28, 30 all have `chcthy` (transfer-watch) — 4 instances of this observation MIDDLE.

Four ckh observations (heat-level checks) and four cth observations (transfer-watches) in a single paragraph is exceptional concentration. The recipe requires dissolving mercury, separating by distillation, and repeated testing — all of which demand both heat management and transfer monitoring.

The 4 dar tokens are distributed across lines 19, 22, 23, 27 — material additions spaced through the operation.

**Match assessment:** Strong. The paragraph's complexity (most prefix-diverse, most observation-dense on the folio) maps to the recipe's most demanding phase: dissolving mercury in prepared water, distilling, and testing. The chekar tokens appearing here for the first time correspond to the fusibility test.

### P7 (Lines 31–36, 65 tokens) — Active Distillation

**Recipe says:** "...reiterate distilling and redistilling over its dregs..."

**What the tokens say:**

P7 is qo+sh dominated (13 qo, 12 sh) with very high k-HEAD count (11) — pure thermal processing with passive observation. Lines 34–35 show intensive cycling: `qokain` → `ar` → `raiin` → `shek` → `okain` → `qolchey` → `okain` → `shckhy` (heat, observe, vessel, heat, observe, check — tight heat-monitor loop).

Line 35: `qokeey` → `qokain` → `qokeey` — gentle heat, sustained heating, gentle heat. Three consecutive qo tokens = pure fire management. Line 36 closes with `qoklain` — heat to hold state, iterating.

One chekar token (L31 `opchekan`), 2 ckh observations, and 1 hh-extended monitoring (L36 `qcthhy`). The hh marks a point of sustained double-watch — extended monitoring of a critical moment.

**Match assessment:** Consistent with redistillation. Heavy thermal cycling, tight heat-observe loops, and the hh-extended monitoring suggesting a critical point in the distillation process.

### P8 (Lines 37–49, 142 tokens) — Final Extended Operation

**Recipe says:** "...until it has drunk the water and drawn to itself all the moisture from the mercurial dregs. Son, this is the incerative moisture that withstands fire."

**What the tokens say:**

The folio's second-largest paragraph, and its most thermally active: 24 qo-prefix, 26 sh-prefix, 22 ch-prefix, 10 ok-prefix. K-HEAD count is the folio's highest (26). This is sustained intensive heating with heavy monitoring from all channels.

Line 42 is striking: `qo` → `qokain` → `sheckhy` → `qokain` → `shekain` → `shkain` → `shedy` → `shey` → `qokan` → `cham`. Six consecutive heat/observe tokens — "heat, check, heat, check, check, check, heat, finalize." This reads as the final push: sustained heating with obsessive monitoring as the dregs absorb the last moisture.

Four ckh observations (heat-level checks) plus 1 cphh (extended pause-watch) and 1 cth (transfer-watch). One chekar (L38 `chkar` — quality check). One hh-extended (L45 `shcphhy` — sustained deep pause-watch).

3 dar tokens across lines 38, 47 (×2) — late material additions. The `daiin` on L38 opens the paragraph's thermal cycling. The final tokens close methodically: L48 `qol` → `or` → `cheey` → `qor` → `aram` (hold heat, note result, check, respond, done). L49: `chcthy` → `chckhy` → `qol` → `ain` → `ary` — final transfer-watch, final heat-check, hold heat, iterate one more time, close.

**Match assessment:** Strong. The heaviest thermal paragraph with maximal monitoring maps well to the recipe's final extended redistillation — "reiterate distilling and redistilling over dregs until all moisture is absorbed." The obsessive heat-observe cycling in L42 reads exactly as a practitioner pushing the final stages of a fixation process.

---

## Cross-Paragraph Patterns

### E-depth Thermal Arc

| Para | e-depth | Thermal character |
|------|---------|-------------------|
| P1 | 0.42 | Low — sustained heat (fixation) |
| P2 | 0.55 | Moderate — transfer monitoring |
| P3 | 0.64 | Highest — active thermal cycling (sublimation) |
| P4 | 0.62 | High — material addition + cycling |
| P5 | 0.50 | Moderate — transition/checkpoint |
| P6 | 0.50 | Moderate — complex multi-channel operation |
| P7 | 0.57 | Moderate-high — redistillation |
| P8 | 0.48 | Moderate — sustained final heating |

The arc shows P3–P4 as the thermal peak (sublimation cycling), with a dip at P5 (transition), then steady moderate values for the complex second half. This is consistent with a recipe that begins with active sublimation-fixation cycles then shifts to dissolution-distillation operations.

### Dar Distribution

| Para | dar count | dar rate | Mapped action |
|------|-----------|----------|---------------|
| P1 | 1 | 3.0% | Initial material handling |
| P2 | 1 | 3.0% | Second portion handling |
| P3 | 4 | 5.0% | Reintroduction during sublimation cycles |
| P4 | **5** | **15.6%** | Conditional quicksilver addition |
| P5 | 0 | 0.0% | No addition (transition) |
| P6 | 4 | 2.9% | Dissolution material additions |
| P7 | 1 | 1.5% | Minor addition |
| P8 | 3 | 2.1% | Final material introductions |

The P4 spike at 15.6% is diagnostic — it maps precisely to the recipe's conditional instruction "add exuberated quicksilver" (ajusta-li de l'argent viu exuberat).

### Observation MIDDLE Distribution

| Para | ckh (heat-check) | cth (transfer-watch) | chekar (quality) | hh (extended) |
|------|-------------------|----------------------|-------------------|---------------|
| P1 | — | — | — | — |
| P2 | 1 | — | — | — |
| P3 | — | — | — | — |
| P4 | — | 1 | — | — |
| P5 | — | — | — | — |
| P6 | 4 | 4 | 2 | — |
| P7 | 2 | — | 1 | 1 |
| P8 | 4 | 1 | 1 | 1 |

Observation MIDDLEs concentrate heavily in P6–P8 (the complex second half), with P6 alone carrying 8 of the 18 total observations. The chekar (quality-test) tokens appear only in P6–P8, mapping to the recipe's fusibility test and its reiteration.

---

## Critical Failure: Missing Mercury Markers

The single strongest negative signal is the complete absence of fch tokens. C1939 established that fch (flag.adjust.watch — "flagged cautious monitoring") appears on 6/6 folios matched to mercury-intensive recipes and encodes volatile/toxic material handling. III.4.0 is explicitly about mercury fixation — "substancia del mercuri," "argent viu exuberat" — yet f116r has zero fch tokens in 537 tokens across 50 lines.

This is not marginal: the enrichment on confirmed mercury folios is described as "infinite" (C1939). If f116r were encoding a mercury procedure, fch should be present. Its absence either means:

1. f116r does not encode this recipe (most parsimonious)
2. fch encodes a different aspect of mercury handling than fixation-specific operations
3. The fch marker is less universal than C1939 suggests

For a positive control, option 1 is the working assumption: this folio is probably not encoding III.4.0 specifically.

---

## Verdict: PARTIALLY COHERENT

**What works (4/7):**
- Iterative structure is strong — qokain (23x), extensive cycling vocabulary throughout
- Chekar quality-test tokens appear exactly where the fusibility test should be (P6 onward)
- Dar distribution peaks at P4 (15.6%), matching the conditional quicksilver addition
- Two-part structure with clear size asymmetry (small P1–P4, large P6–P8, P5 as hinge)

**What partially works (2/7):**
- E-depth is moderate rather than unambiguously low (fixation prediction was for < 0.40)
- Cohobation pattern in P8 is plausible but not diagnostic

**What fails (1/7):**
- Zero fch mercury markers — a strong negative signal for a mercury-fixation recipe

**Overall assessment:** The structural alignment is better than chance — 4 clean passes and 2 partials in 7 predictions is a respectable hit rate. The iterative structure, quality-testing distribution, material-addition spike, and two-part layout all converge. However, the absence of mercury markers prevents upgrading beyond PARTIALLY COHERENT. A generic fixation or sublimation recipe (not mercury-specific) could produce the same folio profile.

This positive control demonstrates that the prediction methodology has genuine discriminative power (it correctly identifies structural features when they're present) while also showing its limits (absence of expected domain markers is a hard constraint that general structural alignment cannot overcome). The fch absence is particularly informative: it shows that token-level diagnostics (C1939) can override paragraph-level structural patterns, maintaining the system's falsifiability.

**Comparison to confirmed matches:** The confirmed f75r ↔ III.19.0 match scored 8/8 structural predictions with additional corpus-singular counting anchors. f116r ↔ III.4.0 scores 4/7 with no singular anchors and a critical marker absence — clearly a lower tier of evidence, consistent with a match that is structurally plausible but not confirmed.
