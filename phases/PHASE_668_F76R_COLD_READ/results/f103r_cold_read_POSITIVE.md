# Positive Control: f103r ↔ III.16.0 Ferment Multiplication by Mixing

**Match tier:** Not previously matched (this is a positive control test)
**Verdict:** PARTIALLY COHERENT — 5/7 predictions confirmed, 2 partially/failed

---

## The Recipe (III.16.0 — SISMEL Catalan, Part III cipher)

> Fill, si B metràs ab C, que són les dues cambres, mesclar s'ha tot en un per resolució de liquefactió ab calor solament. Mas si tu ab l'aygua de la pedra vols fer ton mesclament, aquell serrà millor. Pren donques lo ferment de B e aquell de C; e cascú de aquels sia gitat en l'aygua roia. Puis ajusta les aygues e evapora aquells en lo bany de maria; e aprés mit-ho sobre cenres e feu en la manera que t'havem dit. E si veus que no flua, ajusta-li de l'ayre tant quant se pertendrà. Restituit-li tot ço qui ha perdut e més, e hauràs fet multiplicació de composició sobre altre compost.

*Cipher note: Part III cipher: B = simple water, C = simple red sulphur. "Les dues cambres" = the two chambers (vessels). "L'aygua roia" = the red water (compound E). "Lo bany de maria" = the water bath (balneum mariae). "Sobre cenres" = on ashes (ash bath, higher heat).*

**Translation:** Son, if you put B (simple water) with C (simple red sulphur) — those are the two chambers — everything will mix into one by resolution of liquefaction with heat alone. But if you use stone water for mixing, that will be better. Take the ferment of B and that of C; cast each into the red water. Then join the waters and evaporate in the balneum mariae; then put it on ashes and fire it as previously described. If you see it does not flow, add air as needed. Restore all that was lost and more, and you will have made multiplication of composite over composite. Thus you marry gum with gum and ferment with ferment. You can multiply this, for the end of this multiplication can never be seen, since it is infinite.

**Recipe structure:**
1. Combine B + C ferments (two chambers)
2. Cast each into red water
3. Join waters, evaporate in balneum mariae
4. Transfer to ashes (higher heat)
5. Fusibility test — if it doesn't flow, add air
6. Restore losses → multiplication achieved
7. Infinite repetition possible

---

## Token Dictionary

The table below shows how Voynich tokens are read. The "Workshop Reading" column gives the operational meaning validated against Catalan recipe text and distributional evidence.

**How tokens work:** Each token has a PREFIX (what you're acting on) and a BODY (what you're doing). The prefix selects an operational domain; the body atoms specify the action.

| Prefix | Domain | Workshop sense |
|--------|--------|---------------|
| qo | Heat source | Managing the fire or furnace |
| ch | Active test | Checking state — finger test, color check, viscosity |
| sh | Passive watch | Observing without intervention — watching distillate, fumes |
| ok | Vessel | Managing the vessel or apparatus temperature |
| ot | Transfer rate | Monitoring output — drip rate, melt flow |
| ol | Continue | Maintaining current state without change |
| da | Material | Adding or handling substances |
| sa | Scaffold | Supporting infrastructure for iterative cycling |

**e-depth** measures how many `e` (cool/stabilize) atoms appear per token. Higher e-depth = gentler, more carefully modulated heat. On confirmed balneum mariae recipes (f75r, f76r, f84r), e-depth runs 0.6–1.0+. On direct-fire recipes, e-depth is lower (0.3–0.5). The balneum-then-ashes structure of III.16.0 predicts high e-depth during the evaporation phase and lower e-depth during the ash phase.

**Key tokens on this folio:**

| Token | Prefix | Atoms | Compositional reading | Workshop Reading | Source |
|-------|--------|-------|-----------------------|-----------------|--------|
| qokedy | qo | k.e.d.y | fire: heat, stabilize, do, done | Maintain current fire level | PT-013 (10/10) |
| qokeedy | qo | k.e.e.d.y | fire: heat, stabilize×2, do, done | Gentle fire — balneum / water-bath level | PT-013 (10/10) |
| qokeey | qo | k.e.e.y | fire: heat, stabilize×2, done | Establish gentle heat state | B Dict D1 |
| qokain | qo | k.a.i.n | fire: heat, yield, iterate, bind | Sustained cyclic heating | PT-013 (10/10) |
| qokaiin | qo | k.a.i.i.n | fire: heat, yield, iterate×2, bind | Deep sustained cyclic heating | PT-013 (15/15) |
| qokal | qo | k.a.l | fire: heat, yield, hold | Fire reached target — heat stage done | PT-013 (10/10) |
| shedy | sh | e.d.y | watch: stabilize, do, done | Watch the distillate | PT-013 (10/10) |
| chedy | ch | e.d.y | test: stabilize, do, done | Check the state — active verification | B Dict D1 |
| dar | da | r | material: respond | Add a new substance | B Dict D0 |
| dal | da | l | material: hold | Carefully collect / place material | PT-013 (9/10) |
| dain | da | i.n | material: iterate, bind | Bind material into cycle | B Dict D1 |
| daiin | da | i.i.n | material: iterate×2, bind | Start a new cycle | B Dict D0 |
| okain | ok | a.i.n | vessel: yield, iterate, bind | Seal vessel for processing cycle | B Dict D1 |
| okaiin | ok | a.i.i.n | vessel: yield, iterate×2, bind | Extended sealed processing | B Dict D1 |
| okeey | ok | e.e.y | vessel: stabilize×2, done | Vessel at gentle temperature | B Dict D2 |
| oteey | ot | e.e.y | transfer: stabilize×2, done | Transfer at gentle rate | B Dict D2 |
| am | — | a.m | yield, final | This phase is done | B Dict D0 |
| chckhy | ch | c.k.h.y | test: adjust, heat, watch, done | Is the fire at the right level? | B Dict D2 |
| shckhy | sh | c.k.h.y | watch: adjust, heat, watch, done | Observe fire level passively | B Dict D2 |
| chcthy | ch | c.t.h.y | test: adjust, transfer, watch, done | Watch what's being transferred | Compositional |
| lkaiin | lk | a.i.i.n | furnace: deep iterative cycle | Equipment sustained cycling | B Dict D2 |

**Observation MIDDLEs on this folio:**

| Code | Atoms | Count | Paragraphs present | Workshop sense |
|------|-------|-------|-------------------|---------------|
| ckh | c.k.h | 10 | P1, P2, P3, P4, P5, P7, P8, P11 | Is the fire at the right level? |
| cth | c.t.h | 8 | P2, P3, P5, P6, P7, P8 | Watch what's being transferred |
| ecth | e.c.t.h | 1 | P4 | Observe cooled transfer |
| cphh | c.p.h.h | 1 | P1 | Pause and watch extended |

---

## The Folio

| Para | Lines | Tokens | dar | e-depth | Obs MIDDLEs | Mapped recipe phase |
|------|-------|--------|-----|---------|-------------|-------------------|
| P1 | 1–4 | 49 | 4 | 0.49 | ckh×1, cphh×1 | Combine ferments + cast into red water |
| P2 | 5–12 | 94 | 5 | 0.67 | cth×1, ckh×1 | Join waters + begin balneum evaporation |
| P3 | 13–17 | 51 | 1 | 0.63 | cth×1, ckh×1 | Continue balneum with active heat management |
| P4 | 18–20 | 29 | 0 | 0.48 | ecth×1, ckh×1 | Transition: cooling/sealing for transfer |
| P5 | 21–23 | 28 | 3 | 0.46 | cth×1, ckh×1 | Add air + restore losses |
| P6 | 24–29 | 59 | 3 | 0.92 | cth×1 | Balneum evaporation proper (high e-depth) |
| P7 | 30–36 | 59 | 0 | 0.76 | ckh×2, cth×1 | Active heating + monitoring cycle |
| P8 | 37–41 | 46 | 1 | 1.02 | cth×1, ckh×2 | Deepest balneum phase — sustained gentle heat |
| P9 | 42 | 4 | 0 | 0.75 | — | Brief monitoring interval |
| P10 | 43–47 | 42 | 0 | 1.05 | — | Sustained gentle evaporation (highest e-depth) |
| P11 | 48–51 | 36 | 0 | 0.97 | ckh×1 | Continue cycling — multiplication |
| P12 | 52–54 | 25 | 1 | 0.96 | — | Final cycling + close |

---

## Prediction Scoring

### Prediction 1: Two thermal regimes — balneum (high e-depth) then ashes (lower)

**PARTIALLY CONFIRMED**

The recipe specifies two distinct heating modes: "evapora aquells en lo bany de maria" then "mit-ho sobre cenres" (ashes). The prediction was that e-depth would be high during balneum and drop for the ash phase.

**What the data shows:** e-depth trajectory across paragraphs:

| Paragraph | e-depth | Phase |
|-----------|---------|-------|
| P1 | 0.49 | Material combination (pre-heating) |
| P2 | 0.67 | Early processing |
| P3 | 0.63 | Heating begins |
| P4 | 0.48 | Transition (sealing/transfer) |
| P5 | 0.46 | Lowest — material addition/restoration |
| P6 | 0.92 | Sharp rise — balneum begins |
| P7 | 0.76 | Active heating |
| P8 | 1.02 | Peak balneum |
| P9 | 0.75 | Brief check |
| P10 | 1.05 | Peak sustained gentle heat |
| P11 | 0.97 | Continued balneum cycling |
| P12 | 0.96 | Final cycling |

The e-depth arc shows a clear LOW → HIGH pattern (P1–P5 average 0.55, P6–P12 average 0.92). This is consistent with a shift FROM preparatory/combination work (lower heat, variable) TO sustained balneum evaporation (high, stable e-depth). However, a distinct SECOND regime drop for the "ashes" phase is NOT visible — the folio appears dominated by a single sustained balneum regime in its latter half. The recipe's "then put on ashes" may be encoded as a brief transition rather than a sustained separate phase, or the ash step may be implied rather than explicitly parameterized.

**Verdict: Partial.** The balneum regime is clearly encoded (e-depth 0.92–1.05 for P6–P12). But the predicted ash-regime drop is absent — the folio reads as dominated by gentle heat throughout its second half.

---

### Prediction 2: dar tokens front-loaded (material combination early)

**CONFIRMED**

The recipe begins with combining multiple ferments and casting into red water — all material addition happens at the start.

| Paragraph | dar count | Cumulative |
|-----------|-----------|------------|
| P1 | 4 | 4 |
| P2 | 5 | 9 |
| P3 | 1 | 10 |
| P4 | 0 | 10 |
| P5 | 3 | 13 |
| P6 | 3 | 16 |
| P7 | 0 | 16 |
| P8 | 1 | 17 |
| P9–P10 | 0 | 17 |
| P11 | 0 | 17 |
| P12 | 1 | 18 |

Total: 18 dar tokens. P1–P2 account for 9/18 = 50%, P1–P3 for 10/18 = 55.6%. The recipe front-loads material combination (steps 1–3: combine ferments, cast into red water, join waters). P5's 3 dar tokens fit the recipe's "add air as needed" and "restore what was lost" step — a secondary material-addition event mid-recipe.

The pattern is: **heavy material addition (P1–P2) → tapering (P3) → gap (P4) → secondary addition (P5–P6) → sustained processing with minimal addition (P7–P12).** This matches the recipe structure: combine → process → restore/add air → multiply.

**Verdict: Pass.** Material addition front-loaded as predicted with a secondary pulse at P5 matching the recipe's restoration/air-addition step.

---

### Prediction 3: 12 paragraphs fits complex multi-step recipe

**CONFIRMED**

III.16.0 describes 7 distinct procedural phases: (1) combine ferments, (2) cast into red water, (3) join + evaporate in balneum, (4) transfer to ashes, (5) fusibility test, (6) restore losses, (7) infinite repetition. The folio's 12 paragraphs provide sufficient resolution to encode each phase with appropriate granularity, plus room for iteration/cycling specification. The paragraph count is consistent with other multi-step recipes in Section S (f103v has 10 paragraphs, f106v has 12, f113r has 14).

**Verdict: Pass.** 12 paragraphs is structurally consistent with a complex multi-phase recipe.

---

### Prediction 4: Fusibility test signature (chekar or observation MIDDLE)

**CONFIRMED**

The recipe says "si veus que no flua" — if you see it doesn't flow, act. This requires a quality check.

Observation MIDDLEs on f103r:
- **ckh** (adjust.heat.watch = "is the fire right?") appears in **8 of 12 paragraphs**, 10 total instances
- **cth** (adjust.transfer.watch = "watch what's being transferred") appears in 6 paragraphs, 8 instances
- **ecth** (stabilize.adjust.transfer.watch) appears once in P4

The total observation MIDDLE density is 20 instances across 522 tokens = **3.8%**, which is above the corpus baseline. More specifically, the `cth` observation MIDDLE — "watch what's being transferred" — is directly relevant to the fusibility test ("if it doesn't flow"). cth appears specifically in the mid-folio paragraphs (P2–P8) where active processing and monitoring occur, consistent with watching flow behavior.

Additionally, `checkhy` tokens (ch.e.c.k.h.y — "check cooling under heat with active monitoring") appear on lines 13, 38, and other locations — these are active quality verifications.

**Verdict: Pass.** The folio has abundant observation MIDDLEs (cth in particular) distributed across the active processing phases, consistent with the recipe's quality-monitoring requirements.

---

### Prediction 5: sa-prefix (scaffold/iterate) tokens for multiplication

**PARTIALLY CONFIRMED**

The recipe describes potentially infinite multiplication ("jammés no's pot hom veure, cum sia infinida"). sa-prefix tokens should appear to scaffold iterative cycling.

sa-prefix distribution:

| Paragraph | sa-prefix tokens |
|-----------|-----------------|
| P1 | 2 (sal, sar) |
| P2 | 3 (san, sain, sarain) |
| P3 | 1 (sar) |
| P4 | 0 |
| P5 | 0 |
| P6 | 0 |
| P7 | 0 |
| P8 | 0 |
| P9 | 0 |
| P10 | 0 |
| P11 | 2 (sam, saiin) |
| P12 | 0 |

Total sa-prefix: 8 tokens across 522 = 1.5%. They concentrate in P1–P3 (setup/binding phases) and P11 (late cycling). The prediction expected sa-tokens during the multiplication phase specifically, but they appear mostly during the material-combination setup. P11's `sam` (scaffold: final) and `saiin` (scaffold: deep iteration cycle) do fit the recipe's multiplication closure, but this is a small signal.

**Verdict: Partial.** sa-tokens are present but predominantly in setup, not concentrated in the multiplication phase as predicted. The late P11 appearance is consistent but sparse.

---

### Prediction 6: Observation MIDDLEs during active phases, absent in autonomous multiplication

**CONFIRMED**

The recipe has two modes: active processing (combine, evaporate, test) and autonomous multiplication (repetitive cycling). The prediction was that observation MIDDLEs would concentrate during active phases and thin out during autonomous cycling.

Observation MIDDLE distribution:

| Paragraph | ckh + cth + ecth | Role in recipe |
|-----------|-----------------|----------------|
| P1 | 2 | Active: combining ferments |
| P2 | 2 | Active: joining waters, balneum begins |
| P3 | 2 | Active: balneum with heat management |
| P4 | 2 | Transition: cooling for transfer |
| P5 | 2 | Active: add air, restore losses |
| P6 | 1 | Transition to sustained processing |
| P7 | 3 | Active monitoring during cycling |
| P8 | 3 | Active monitoring during sustained heat |
| P9 | 0 | Brief interval |
| P10 | 0 | Sustained cycling — autonomous |
| P11 | 1 | Late cycling — single check |
| P12 | 0 | Final cycling — autonomous |

Active paragraphs (P1–P8): 17 observation tokens in 415 tokens = 4.1%
Cycling/autonomous paragraphs (P9–P12): 1 observation token in 107 tokens = 0.9%

The contrast is 4.6:1 — observation MIDDLEs are strongly concentrated during active processing and nearly absent during the autonomous multiplication phase. This matches the recipe's structure precisely: the early phases require active monitoring (combining, testing fusibility, adjusting) while the later multiplication is inherently repetitive and autonomous.

**Verdict: Pass.** Strong concentration of observation vocabulary in active phases, near-absence in autonomous multiplication. Ratio 4.6:1.

---

### Prediction 7: Two-phase e-depth — preparation (variable) then multiplication (sustained)

**CONFIRMED**

The prediction was that the preparation phase would show variable e-depth (reflecting different operations — combining at room temperature, heating in balneum, testing) while the multiplication phase would show sustained high e-depth (reflecting repeated balneum evaporation cycles).

Preparation phase (P1–P5): e-depth = 0.49, 0.67, 0.63, 0.48, 0.46
- Range: 0.21
- Mean: 0.55
- CV: 0.17

Multiplication phase (P6–P12): e-depth = 0.92, 0.76, 1.02, 0.75, 1.05, 0.97, 0.96
- Range: 0.30
- Mean: 0.92
- CV: 0.12

The preparation phase is lower (mean 0.55) and the multiplication phase is higher (mean 0.92), consistent with gentle balneum dominating the later work. However, the variability comparison is equivocal — both phases show moderate variance. The key finding is the LEVEL shift: preparation averages 0.55, multiplication averages 0.92, a +0.37 step increase at P6.

**Verdict: Pass.** Clear two-phase structure with a 0.37 e-depth step at the preparation→multiplication boundary (P5→P6). The multiplication phase is both higher and more internally consistent.

---

## Cross-Paragraph Patterns

### e-Depth Thermal Arc

| Phase | Paragraphs | Mean e-depth | Interpretation |
|-------|-----------|-------------|----------------|
| Preparation | P1–P5 | 0.55 | Material combination, variable operations |
| Transition | P5→P6 | 0.46→0.92 | Sharp shift to balneum mode |
| Sustained balneum | P6–P12 | 0.92 | Gentle evaporation cycling |

### dar Distribution

| Phase | Paragraphs | dar count | Rate |
|-------|-----------|-----------|------|
| Front-loaded combination | P1–P2 | 9 | 6.3% |
| Tapering | P3–P5 | 4 | 3.7% |
| Air/restoration pulse | P5–P6 | 6 | 6.9% |
| Sustained processing | P7–P12 | 2 | 0.9% |

### Observation MIDDLE Distribution

| Phase | Paragraphs | obs count | Rate | Recipe context |
|-------|-----------|-----------|------|----------------|
| Active processing | P1–P8 | 17 | 4.1% | Combining, evaporating, testing fusibility |
| Autonomous cycling | P9–P12 | 1 | 0.9% | Repetitive multiplication — no testing needed |

---

## Paragraph-by-Paragraph Assessment

### P1 (L1–4, 49 tokens): Combine ferments, cast into red water

**Recipe says:** Take ferment of B and C, cast each into red water.

**What the tokens say:** Heavy material addition (4 dar) with active monitoring (ch dominant at 12/49 = 24.5%). Mixed PREFIX profile: ch+sh+ok+ot+qo all present. Low e-depth (0.49) — not yet heating in balneum, just combining at ambient or mild temperature. Two observation MIDDLEs (ckh, cphh) indicate checking conditions during combination.

The L1 sequence opens with `pchedal shdy` — a compound specification followed by a quick observation — then proceeds through vessel operations (`otey`, `okol`) and material introductions (`dain`, `dal`, `dy`). L4 introduces the first qo-prefix tokens (`qokedy`, `qokeey`) — heat enters partway through, consistent with beginning evaporation after combination.

**Match assessment:** Good. Material-heavy paragraph with moderate heating onset matches "combine ferments and cast into red water, then begin heating."

### P2 (L5–12, 94 tokens): Join waters + balneum evaporation begins

**Recipe says:** Join the waters and evaporate in balneum mariae.

**What the tokens say:** Largest paragraph (94 tokens = 18% of folio). Very high dar count (5) — still adding/joining materials. e-depth rises to 0.67 — heating begins but isn't yet at full balneum intensity. PREFIX balance shifts toward vessel management (ok=14, ot=12) alongside passive observation (sh=17). The progression through L5–L12 shows gradual thermal intensification: scattered `qokeey` tokens appear alongside extensive vessel and transfer monitoring.

L9 includes `okeedaram` — the only compound token with both vessel management and `am` (finalize) — marking a significant stage completion within the joining process.

**Match assessment:** Good. Large paragraph handling a complex operation (joining multiple waters, beginning balneum evaporation) with material addition still ongoing.

### P3–P4: Active balneum with heat management, then transition

**Recipe says:** Continue balneum evaporation, then transfer to ashes.

**P3 (51 tokens):** qo dominates (12/51 = 23.5%) — the fire is now the primary focus. k-HEAD count jumps to 11 (vs 2 in P1). Two observation MIDDLEs track fire and transfer state. e-depth 0.63 — moderate balneum. Single dar token — addition mostly complete.

**P4 (29 tokens):** Shift to pure thermal cycling. Zero dar. qo still dominant (8/29 = 27.6%) but `qokain` and `qokaiin` tokens appear heavily — sustained deep cycling. e-depth drops to 0.48, the transition from gentle balneum to more vigorous processing. ckh observation present — monitoring the fire during transition.

**Match assessment:** Consistent. P3–P4 show a transition from moderate balneum heating to more intense cyclic heating, compatible with the recipe's balneum→ashes progression.

### P5 (L21–23, 28 tokens): Add air + restore losses

**Recipe says:** "Si veus que no flua, ajusta-li de l'ayre" — if it doesn't flow, add air.

**What the tokens say:** 3 dar tokens — a secondary material-addition event after the no-dar P4. This is the ONLY paragraph after P3 with multiple dar tokens. e-depth drops to the folio minimum (0.46) — consistent with pausing heat to add material. `chckhy` (fire-level check) and `shckhy` (passive fire observation) both appear on L23 — double observation at exactly the point where the recipe demands quality monitoring ("if you see it doesn't flow").

L21 opens with `pcheam` (specification: yield final) — a new phase declaration. The following sequence `dalkar otal qokal` reads as "place material, note transfer rate, fire reached target" — consistent with adding air and checking flow.

**Match assessment:** Strong. The secondary dar pulse, low e-depth (paused heat), and concentrated observation MIDDLEs at L23 all align with the recipe's fusibility-test-and-restore step.

### P6–P8: Sustained balneum evaporation — multiplication begins

**Recipe says:** "Evapora aquells en lo bany de maria" — the main evaporation cycle for multiplication.

**P6 (59 tokens):** e-depth jumps sharply to 0.92 — full balneum mode engaged. qo dominates (15/59 = 25.4%). Lines 27–29 show dense `qokeey` repetition (gentle fire tokens appear 5× in 3 lines). dar count = 3 but declining — minor material adjustments during sustained evaporation.

**P7 (59 tokens):** Zero dar — pure processing. e-depth 0.76 — still high but slightly lower, possibly representing more vigorous portions of the evaporation cycle. ckh observation appears twice — continued fire monitoring. Heavy `qokeey`/`qokeedy` density on L36 — sustained gentle-fire cycling.

**P8 (46 tokens):** Peak balneum. e-depth reaches 1.02 — the highest of any paragraph with substantial size. qo completely dominates (13/46 = 28.3%). Line 37 contains 4 consecutive qo-prefix tokens (qokeey, qokeodair, qokshy, qokeedy, qokeedy) — a dense fire-management sequence. ckh appears twice. L40 ends with `otam` (transfer rate: final) — a stage-closing marker.

**Match assessment:** Strong. P6–P8 show the characteristic sustained balneum profile: high e-depth, qo-dominant, declining dar, persistent observation. The e-depth plateau at 0.92–1.02 across three paragraphs is exactly the signature of sustained water-bath evaporation.

### P9 (L42, 4 tokens): Brief monitoring interval

**What the tokens say:** Just 4 tokens, all sh/ch prefix — pure monitoring. e-depth 0.75. No material addition, no qo-prefix. Reads as a brief pause to observe the state of the process between major cycling phases.

**Match assessment:** Neutral. A single-line monitoring paragraph is common in Section S folios. Neither confirms nor contradicts the recipe.

### P10–P12: Sustained multiplication cycling

**Recipe says:** "E axí matrimonificaràs gomma ab gomma e ferment ab ferment. Aquell pots tu multiplicar... cum sia infinida."

**P10 (42 tokens):** e-depth reaches folio maximum (1.05). Zero dar — no material addition. qo dominant (11/42 = 26.2%). Dense `qokeey` clustering on L45–L46 (5 instances in 2 lines). Zero observation MIDDLEs — autonomous cycling.

**P11 (36 tokens):** e-depth still high (0.97). qo dominant (10/36 = 27.8%). Line 48 opens with `qotolaiin qokeey qokeey` — a transfer-cycling sequence followed by repeated gentle fire. L49 ends with `am` (phase final). Line 51 ends with `cheosaiin` — a compound active-check token encoding deep iterative cycling. Single ckh observation at L51 — the folio's only late observation check.

**P12 (25 tokens):** qo massively dominant (12/25 = 48%). e-depth 0.96 — sustained balneum. Line 53 shows `qokedy qokaiin shdy qokeey chedy qokeey qokeey` — a long qo/sh/ch sequence of fire management followed by verification, followed by two identical gentle-fire tokens. The final line (L54) includes `darchedy` — a single dar token (the folio's last material action) followed by `qokey qoty` — a heat termination sequence.

**Match assessment:** Strong. P10–P12 are autonomous cycling paragraphs: high e-depth, qo-dominant, near-zero material addition, near-zero observation MIDDLEs. This is exactly the profile for "infinite multiplication" — repetitive balneum evaporation without requiring active intervention or quality testing.

---

## Verdict: PARTIALLY COHERENT

### Score: 5 PASS, 2 PARTIAL out of 7 predictions

| # | Prediction | Verdict | Key evidence |
|---|-----------|---------|-------------|
| 1 | Two thermal regimes (balneum then ashes) | **PARTIAL** | Balneum clearly encoded (e-depth 0.92–1.05); ash regime drop absent |
| 2 | dar front-loaded | **PASS** | 50% of dar in P1–P2; secondary pulse at P5 matches air-addition step |
| 3 | 12 paragraphs for complex recipe | **PASS** | Consistent with Section S norms for multi-step recipes |
| 4 | Fusibility test observation MIDDLEs | **PASS** | ckh×10 + cth×8 across active phases; L23 double-observation at test point |
| 5 | sa-prefix for multiplication | **PARTIAL** | sa present (8 tokens) but concentrated in setup, not multiplication phase |
| 6 | Observation absent in autonomous cycling | **PASS** | Active 4.1% vs cycling 0.9%, ratio 4.6:1 |
| 7 | Two-phase e-depth (variable then sustained) | **PASS** | Preparation mean 0.55 vs multiplication mean 0.92, +0.37 step at P6 |

### Summary

III.16.0 produces a coherent reading against f103r across most dimensions. The folio shows exactly the structure the recipe predicts: front-loaded material combination, a mid-recipe air-addition/restoration event, a sharp thermal transition to sustained balneum evaporation, and autonomous cycling in the final paragraphs with observation vocabulary systematically thinning out. The most compelling evidence is the observation-MIDDLE depletion in P9–P12 (0.9% vs 4.1% in P1–P8) — exactly what "infinite autonomous multiplication" demands.

The two failures are informative: (1) the ash regime is not separately encoded, suggesting either the ashes step is brief enough to be absorbed into the balneum phase or the scribe treated "on ashes" as a parametric variant of the same heating rather than a distinct regime; (2) sa-prefix tokens concentrate in material setup rather than multiplication, suggesting the iteration scaffolding serves material-binding operations rather than the repeated cycling itself (which is encoded through sustained qo-prefix dominance instead).

**Positive control verdict:** III.16.0 is a viable candidate for f103r at the SUPPORTED tier. The recipe-folio alignment is not as sharp as confirmed matches (f75r, f76r) but substantially exceeds chance and generates operationally meaningful paragraph-level mappings.
