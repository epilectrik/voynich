# Positive Control: f82r ↔ III.19.3 (Fourth Water, Lunaria Maceration)

**Test type:** True-recipe positive control
**Recipe:** III.19.3 "Confeccio de la 4a aygua" (fourth water constitution, lunaria maceration)
**Negative control result:** [pending -- II.16.0 control still running]

## Recipe Summary

III.19.3 is a VERY SHORT recipe (369 chars Catalan) with only two main operations:

1. **Material preparation:** Add 3 parts lunaria moisture onto flesh substance
2. **Seal:** Close cucurbit with glass cover + common wax
3. **Macerate:** Place on ashes, 3 natural days, sawdust fire (gentle sustained heat)
4. **Distill:** Place alembic on top, distill all water through the balneum
5. **Store:** Keep the distillate aside

Two thermal phases: gentle ash-fire maceration (3 days), then balneum distillation.
Only one material addition (lunaria onto flesh).
Two sealing materials (glass + wax).

---

## Structural Prediction Table

| # | Prediction | Expected | Actual | Verdict |
|---|-----------|----------|--------|---------|
| 1 | SCALE TENSION: 9 paragraphs too many for 2-step recipe | High tension | **HIGH TENSION but partially resolvable** (see Scale Assessment) | PARTIALLY MET |
| 2 | High e-depth (gentle heat throughout) | e-depth >> 0.5 across most paragraphs | Mean e-depth: P1=0.76, P3=0.88, P4=0.86, P6=1.00, P7=1.00, P8=1.02 -- YES, very high | **PASS** |
| 3 | Low dar count (only 1 material addition) | dar <= 2 total folio | Total dar = 14 across folio -- **NO, very high** | **FAIL** |
| 4 | x3 counting anchor possible | Window of 3 identical tokens somewhere | No 3-token identical run observed | **FAIL** |
| 5 | Short sealing paragraph with dar (glass + wax) | Distinct short sealing paragraph | P5 (15 tokens) has ok=3, ot=1, dal=1, otain=1 -- vessel-oriented but not a crisp sealing signature | **PARTIAL** |
| 6 | Two thermal phases: maceration then distillation | Clear e-depth shift or prefix shift between early and late paragraphs | P1-P4 qo-dominated (maceration heat), P8 shows t-HEAD surge (9 t-HEAD tokens = transfer/distillation) | **PASS** |
| 7 | Sparse observation MIDDLEs | Few or zero ckh/cth tokens | Only 3 obs MIDDLEs total (2x ckh in P1, 1x ecth in P1), none in later paragraphs | **PASS** |
| 8 | Zero dar during sealed maceration | No dar in middle paragraphs | P3 has 0 dar, P7 has 0 dar -- but P6 has 4 dar, P4 has 2 | **PARTIAL** |

**Score: 3 PASS, 2 PARTIAL, 1 PARTIALLY MET, 2 FAIL out of 8 predictions.**

---

## Key Quantitative Evidence

### Folio-Level Summary

| Para | Lines | Tokens | dar | e-depth | Obs MIDDLEs | k-HEAD | t-HEAD | qo% |
|------|-------|--------|-----|---------|-------------|--------|--------|-----|
| P1 | 1-9 | 72 | 3 | 0.76 | ckh x2, ecth x1 | 23 | 5 | 38.9% |
| P2 | 10-11 | 17 | 1 | 0.47 | -- | 1 | 2 | 29.4% |
| P3 | 12-13 | 17 | 0 | 0.88 | -- | 5 | 1 | 35.3% |
| P4 | 14-16 | 28 | 2 | 0.86 | -- | 8 | 1 | 32.1% |
| P5 | 17-18 | 15 | 1 | 0.67 | -- | 2 | 0 | 13.3% |
| P6 | 19-24 | 57 | 4 | 1.00 | -- | 11 | 0 | 28.1% |
| P7 | 25 | 9 | 0 | 1.00 | -- | 2 | 0 | 22.2% |
| P8 | 26-30 | 44 | 1 | 1.02 | -- | 9 | **9** | 40.9% |
| P9 | 31-32 | 16 | 1 | 0.69 | -- | 0 | 0 | 0.0% |
| **TOTAL** | 1-32 | **275** | **14** | **0.86** | **3** | **61** | **18** | **31.3%** |

### e-depth Thermal Arc

The thermal profile shows two zones:
- P1-P5: moderate-to-high e-depth (0.47-0.88), representing standard gentle heat operations
- P6-P8: maximum e-depth (1.00-1.02), representing deep gentle heat -- consistent with balneum distillation

This two-phase arc aligns with the recipe's maceration-then-balneum structure.

### dar Distribution

| Para | dar count | Tokens with dar-like action |
|------|-----------|----------------------------|
| P1 | 3 | daiin x3 + dairchey |
| P2 | 1 | dar x1 |
| P3 | 0 | -- |
| P4 | 2 | daiin x1 + dam x1 |
| P5 | 1 | dal x1 |
| P6 | 4 | daiin x3 + dal x1 |
| P7 | 0 | -- |
| P8 | 1 | daldy x1 |
| P9 | 1 | daiin x1 |

**Problem:** The recipe describes only ONE material addition (3 parts lunaria onto flesh). The folio has 14 dar-family tokens distributed across 7 of 9 paragraphs. This is structurally excessive for a single-addition recipe. Some daiin tokens are infrastructure (iteration triggers per C557), not material additions, but the density is still high.

### t-HEAD Concentration in P8

P8 (lines 26-30) has 9 t-HEAD tokens out of 44 total (20.5%), compared to the folio average of 6.5% for P1-P7. The t-HEAD tokens in P8 are:

- qoteedy x2 (transfer, gentle cooling)
- qotedy x2 (transfer, cool, done)
- qotain x1 (transfer, yield, iterate)
- qoteeol x1 (transfer, cool, cool, arrange, state)
- qoty x3 (transfer, done)

This surge is consistent with the distillation phase ("distilla tota l'aygua per lo bany"), where material is being transferred through the alembic. The qoty triplet (3 consecutive transfer-close tokens) on line 28 could encode the "distill ALL the water" completeness emphasis.

### hh Token in P8

P8 line 28 contains `okchhy` -- the only hh (extended watching) token on the folio. In the recipe context, this aligns with monitoring the distillation process, which requires careful observation of the distillate quality.

---

## Paragraph-Level Assessment

### P1 (72 tokens, lines 1-9): Sustained Maceration with Periodic Checks

**Recipe says:** "Place all on ashes for 3 natural days with composed sawdust fire."

**What the tokens say:** This is by far the largest paragraph (26.2% of folio), dominated by qo-prefix (38.9%) with heavy k-HEAD (23 tokens). The thermal pattern is consistent gentle heat: qokeedy (balneum-level), qokeey (gentle heat state), qokedy (standard heat), alternating with sh-prefix passive observation and ch-prefix active monitoring. Three daiin tokens mark iteration boundaries (cycling). One chekar-type observation (shckhy on L1 and chckhy on L3) monitors heat level.

**Match assessment:** A 3-day maceration under ash-fire WOULD require sustained attention to maintain gentle heat and periodic monitoring. A 72-token paragraph is plausible for encoding 3 days of fire management. The high qo density and moderate e-depth (0.76) match ash-fire rather than balneum. **COHERENT** for the maceration phase, though the paragraph seems oversized relative to the recipe's brevity.

### P2 (17 tokens, lines 10-11): Transition -- Cool, Transfer, Reseal

**Recipe says:** (Transition between maceration and distillation -- "Puis mit-li dessus e distilla")

**What the tokens say:** Mixed prefix profile. Ends with kam (ka + m = final marker per C912). Contains a dar on L11 (the recipe's "then put alembic on top" = adding apparatus). Contains ol-prefix x2 (vessel-load), ok-prefix x2 (vessel management), and qo x5 heat operations. The mean e-depth drops to 0.47 -- the lowest on the folio -- suggesting a transitional cooling/apparatus change phase.

**Match assessment:** The e-depth dip is consistent with opening the sealed cucurbit (breaking the ash-fire seal), placing the alembic, and resetting for distillation. The kam paragraph-closer marks the end of the maceration stage. The single dar could encode adding the alembic. **COHERENT** as a transition paragraph.

### P3 (17 tokens, lines 12-13): Resume Heating Under New Configuration

**Recipe says:** "distilla tota l'aygua per lo bany" (distill all water through the bath)

**What the tokens say:** qo-prefix dominant (6/17 = 35.3%), k-HEAD returns strongly (5 tokens), e-depth rises to 0.88. Three ol-prefix tokens (vessel management). Zero dar -- no material being added. Contains qokaiin (sustained sealed heating) at the end.

**Match assessment:** After the transition in P2, P3 resumes heating under the new balneum configuration. The elevated e-depth (0.88 vs P1's 0.76) is consistent with balneum being a gentler and more controlled heat method than ash-fire. Zero dar is correct -- the sealed system is now distilling, not receiving material. **COHERENT.**

### P4 (28 tokens, lines 14-16): Active Distillation with Monitoring

**Recipe says:** (Continued distillation)

**What the tokens say:** High qo (9/28 = 32.1%) with elevated k-HEAD (8 tokens). Contains 2 daiin tokens (iteration markers) and a dam (process step finalizer on L15). Multiple dy (cycle-close) tokens. The e-depth remains high (0.86). Line 16 has qokeeey (e-depth 3 -- very gentle heat) followed by standard qokedy.

**Match assessment:** Continued distillation with active fire management. The dam on L15 could mark the end of the initial distillation take. The qokeeey on L16 suggests maximum gentleness during a critical distillation moment. The 2 dar-family tokens are slightly excessive for a sealed distillation, but daiin functions as an iteration trigger (C557), not a material addition. **PARTIALLY COHERENT** -- the dar excess is minor.

### P5 (15 tokens, lines 17-18): Vessel Management Interlude

**Recipe says:** "tapa la carabasa ab son cubertor de vidre ab cera communa" (seal the cucurbit with glass cover and common wax) -- NOTE: this sealing step comes BEFORE the maceration in the recipe, but the folio's paragraph order need not match the recipe's textual order exactly.

**What the tokens say:** ok-prefix dominates (3/15 = 20.0%, highest on folio). Contains otain (vessel-seal: yield iterate), dal (careful placement), and ory (vessel response). The e-depth drops to 0.67. The ok-prefix concentration and vessel-oriented vocabulary suggest apparatus manipulation.

**Match assessment:** This could encode either the original sealing step (glass + wax) or a mid-process vessel adjustment during distillation. The dal (careful placement) could correspond to placing the glass cover. The ok-prefix cluster is distinctive for vessel management. **PARTIALLY COHERENT** -- the placement in the paragraph sequence is uncertain.

### P6 (57 tokens, lines 19-24): Extended Balneum Distillation

**Recipe says:** "distilla tota l'aygua per lo bany" (distill ALL the water through the bath)

**What the tokens say:** This is the second-largest paragraph (20.7% of folio). Maximum e-depth of 1.00 -- the deepest gentle-heat encoding on the folio. Heavy qo (16/57 = 28.1%) with sh-prefix observation (8 tokens) and ch-prefix active checking (6 tokens). Contains keeedy (e-depth 3) and qokeeey (e-depth 3) -- the deepest thermal tokens on the folio, consistent with balneum mariae. Four daiin tokens (iteration markers for cycling). Ends with sheey/ry (observe then close).

**Match assessment:** This is the most balneum-characteristic paragraph on the folio. The sustained maximum e-depth, the dense sh/ch alternation for monitoring, and the keeedy/qokeeey tokens are a strong balneum signature. The instruction to "distill ALL the water" would require prolonged gentle heat with constant monitoring -- exactly what this paragraph encodes. The 4 daiin tokens mark cycling iterations (repeated distillation passes). **STRONGLY COHERENT.**

### P7 (9 tokens, line 25): Quality Gate / Observation Pause

**Recipe says:** "e aquella guarda a part" (and keep it aside)

**What the tokens say:** Very short paragraph. Maximum e-depth (1.00). Contains oteey (vessel-seal check), okey (vessel check), cheal (check yield state), ches + aiin (check sequence + iterate). Zero dar.

**Match assessment:** This tiny paragraph is a quality-check gate between the main distillation (P6) and the final operations (P8). In the recipe context, this is the moment where the operator verifies the distillate quality before storing it. The e-depth remains at maximum (balneum still active or just completed). The oteey + okey combination checks the vessel state. **COHERENT** as a quality gate.

### P8 (44 tokens, lines 26-30): Transfer and Collection Phase

**Recipe says:** "distilla tota l'aygua" continued, plus collection/storage

**What the tokens say:** This paragraph shows the dramatic t-HEAD surge (9 tokens = 20.5%, vs 3.7% across P1-P7). The t-HEAD tokens encode transfer operations: qoteedy, qotedy, qotain, qoteeol, qoty x3. Maximum e-depth (1.02). Contains the folio's only hh token (okchhy = extended watching at vessel). Heavy lch-prefix (5 tokens = equipment checking). One daldy (careful collection). Ends with a ram on L29 (stage done -- note result per PT-013).

**Match assessment:** The t-HEAD explosion is the clearest structural signal on the folio. Distillation IS transfer -- material moves from the cucurbit through the alembic into the receiver. The qoty triplet on L28 (transfer.end x3) could encode complete collection of all distillate. The ram on L29 closes the stage. The hh token marks the extended careful watching that real distillation requires (watching the distillate character as it finishes). **STRONGLY COHERENT.**

### P9 (16 tokens, lines 31-32): Shutdown and Storage

**Recipe says:** "guarda a part" (keep aside)

**What the tokens say:** Zero qo-prefix (0.0% -- only paragraph without heat management). Heavy ch-prefix (5/16 = 31.3%) -- active checking. Contains daiin (final iteration marker). Multiple cheol/cheor (check arrangement/response). The e-depth drops to 0.69 -- cooling down.

**Match assessment:** The complete absence of qo-prefix is striking and unique on this folio. This is the only paragraph where the fire is no longer being managed. The operator is performing final checks (ch-dominant) on the cooled product before storage. The e-depth decline from P8's 1.02 to 0.69 encodes the cooling-down gradient. **COHERENT** as a shutdown/storage paragraph.

---

## Scale Assessment

### The core tension: 275 tokens and 9 paragraphs for a 369-character recipe

This is the primary challenge for the positive control. The recipe describes 2 main operations (macerate, distill) in about 5 sentences. Can 9 paragraphs be justified?

**Yes, partially.** The key insight is that the recipe specifies WHAT to do but omits the detailed HOW of fire management, monitoring, and apparatus manipulation that a practitioner needs. A 3-day maceration under ash-fire requires:

- Constant fire management (adding sawdust, adjusting airflow) -- P1's 72 tokens
- Periodic opening and closing of the furnace -- contributes to P2
- Transition to a different heating configuration (balneum) -- P2
- Resuming heat under new configuration -- P3
- Extended distillation with monitoring -- P4, P6
- Vessel management during distillation -- P5
- Quality verification -- P7
- Collection of distillate (the physical transfer operation) -- P8
- Shutdown and storage -- P9

This is 9 distinct operational phases, which maps reasonably well to 9 paragraphs. The recipe compresses a multi-day process into 5 sentences; the folio encodes the operator's moment-by-moment control requirements.

**However:** The 14 dar tokens remain problematic. A single-material-addition recipe should not need 14 material-handling tokens. Some of these are daiin (infrastructure/iteration triggers), but the total dar-family density (5.1%) is higher than expected for this recipe type.

### Plausible paragraph-recipe mapping:

| Para | Recipe Phase | Evidence |
|------|-------------|---------|
| P1 | 3-day ash-fire maceration | 72 tokens, qo-dominant, moderate e-depth, sustained cycling |
| P2 | Open cucurbit, add alembic | E-depth dip to 0.47, kam closer, dar=1 for alembic placement |
| P3 | Resume heating (balneum) | E-depth rises to 0.88, zero dar, sustained sealed heating |
| P4 | Active distillation | High qo, dam process-step marker, very gentle tokens |
| P5 | Vessel management | ok-dominant, dal (careful placement), sealing/checking |
| P6 | Extended balneum distillation | Maximum e-depth, keeedy/qokeeey, 57 tokens for "distill ALL" |
| P7 | Quality gate | 9-token observation pause, zero dar |
| P8 | Transfer/collection | **t-HEAD surge**, ram stage-close, hh extended watching |
| P9 | Shutdown/storage | Zero qo (fire off), ch-dominant final checks, e-depth declining |

---

## Cross-Paragraph Patterns

### E-depth Thermal Arc

| Para | e-depth | Phase |
|------|---------|-------|
| P1 | 0.76 | Ash-fire maceration (moderate gentle) |
| P2 | 0.47 | **Transition dip** (opening vessel, changing setup) |
| P3 | 0.88 | Balneum onset (deeper gentle than ash) |
| P4 | 0.86 | Balneum sustained |
| P5 | 0.67 | Vessel manipulation interlude |
| P6 | 1.00 | **Peak balneum** (distill ALL the water) |
| P7 | 1.00 | Quality gate (still at balneum) |
| P8 | 1.02 | **Maximum** (deep gentle during collection) |
| P9 | 0.69 | **Cooling down** (fire off, product stored) |

The thermal arc tells a coherent story: moderate ash-fire heat -> dip for apparatus change -> deeper balneum heat peaking during collection -> decline at shutdown. This is consistent with the recipe's two-heat-source structure (ashes then balneum).

### dar Distribution Pattern

- P1 has 3 dar (setup, adding materials -- matches recipe's material preparation)
- P2 has 1 dar (adding alembic for distillation)
- P3 has 0 (sealed distillation, no additions)
- P4 has 2 (iteration markers; one dam = process step close)
- P5 has 1 dal (careful placement during vessel management)
- P6 has 4 (iteration markers for cycling in extended distillation)
- P7 has 0 (observation only)
- P8 has 1 daldy (careful collection of distillate)
- P9 has 1 (final handling)

**Interpretation:** Most dar-family tokens in the middle paragraphs are daiin (infrastructure/iteration) rather than dar (vigorous material addition). The actual material-addition dar tokens concentrate in P1-P2, consistent with the recipe. But the aggregate count (14) is still high for the recipe's simplicity.

---

## Key Discriminative Signals

### Signals that SUPPORT III.19.3 alignment:

1. **Two-phase thermal arc:** e-depth cleanly divides into ash-fire (P1, 0.76) and balneum (P6-P8, 1.00-1.02) with a transition dip at P2 (0.47). This precisely matches the recipe's two heat sources.

2. **t-HEAD distillation surge in P8:** The 9 t-HEAD tokens (20.5%) are the folio's clearest structural signal. Distillation IS transfer. The qoty triplet (transfer.end x3) and ram (stage done) mark collection completion.

3. **Zero-qo shutdown in P9:** The only paragraph without fire management. The recipe ends with "guarda a part" (keep aside) -- no more heating needed.

4. **P7 quality gate:** A 9-token observation paragraph between distillation and collection, consistent with checking distillate quality before storing.

5. **P1 scale:** 72 tokens for a 3-day operation makes sense -- sustained fire management requires many instruction cycles.

### Signals that CHALLENGE III.19.3 alignment:

1. **dar excess:** 14 dar-family tokens for a single-material-addition recipe is high. Even accounting for daiin as infrastructure, the material-handling density exceeds what the recipe specifies.

2. **No x3 counting anchor:** The recipe explicitly uses "3 parts" and "3 days" but no 3-token identical run appears on the folio.

3. **P6 has 4 dar tokens:** During what should be sealed distillation, 4 material-handling tokens (3 daiin + 1 dal) suggest more active material intervention than the recipe describes.

4. **Scale remains in tension:** 275 tokens for a 369-character recipe requires accepting that >80% of the encoded content is implied operational knowledge not present in the recipe text.

---

## Verdict: PARTIALLY COHERENT

**The thermal architecture is strongly coherent.** The two-phase e-depth arc (ash-fire -> transition dip -> balneum peak -> cooling shutdown) maps cleanly to III.19.3's two heat sources. The t-HEAD distillation surge in P8 is a clear structural signal. The zero-qo shutdown in P9 is the correct endpoint.

**The material-handling profile is mildly incoherent.** The 14 dar-family tokens are excessive for a single-addition recipe. This is the primary weakness. Most are daiin (iteration infrastructure), but the density remains higher than the recipe predicts.

**The scale tension is partially resolved.** A 3-day maceration + full distillation is genuinely a multi-day process requiring sustained operator attention. The 9 paragraphs can be mapped to 9 distinct operational phases with reasonable plausibility. But this mapping requires accepting that the folio encodes a large amount of operational detail that the recipe never mentions.

**Overall:** The thermal and structural signals are strong enough to support the match, but the material-handling excess prevents full coherence. This is consistent with C1929's prior assessment (match NOT confident by 8D criteria, ratio=0.791, but atom-level evidence is present). The positive control produces a stronger signal than a random recipe would (the thermal arc and t-HEAD surge are specific to this recipe type), but it is not overwhelmingly compelling as a standalone identification.

**Discrimination power depends on the negative control:** If II.16.0 (wrong recipe) produces a comparably coherent reading, the positive control fails to discriminate. If II.16.0 is incoherent, the thermal and transfer signals here become discriminative evidence.

---

## Discrimination Summary

*To be completed when negative control (f82r ↔ II.16.0) finishes.*

| Dimension | Positive (III.19.3) | Negative (II.16.0) | Discriminates? |
|-----------|--------------------|--------------------|----------------|
| E-depth two-phase arc | Two clear phases matching ash-fire -> balneum | [pending] | [pending] |
| t-HEAD distillation surge | P8 = 20.5% t-HEAD, strong transfer signal | [pending] | [pending] |
| dar distribution | 14 total, excess for recipe | [pending] | [pending] |
| Zero-qo shutdown | P9 correct fire-off | [pending] | [pending] |
| Scale coherence | 9-para mappable with operational expansion | [pending] | [pending] |
| Overall verdict | PARTIALLY COHERENT | [pending] | [pending] |
