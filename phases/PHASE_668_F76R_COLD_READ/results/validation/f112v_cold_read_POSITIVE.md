# Positive Control: f112v ↔ III.1.0 (Lunaria → Quicksilver Pipeline)

**Test type:** True-recipe positive control
**Recipe:** III.1.0 (Liber Mercuriorum Ch.1: lunaria → quicksilver creation, long multi-step)
**Negative control result:** [pending — III.19.3 control still running]

## Structural Prediction Table

| # | Prediction | Expected | Actual | Verdict |
|---|-----------|----------|--------|---------|
| 1 | 15 paragraphs appropriate for recipe complexity | 13+ steps → needs many paragraphs | 15 paragraphs, 415 tokens. Recipe has ~13 distinct operational steps plus introductory and concluding phases. Count is a reasonable match. | **PASS** |
| 2 | Multiple thermal regimes (balneum → ash fire → cooling → gentle fire) | e-depth should vary substantially across paragraphs, NOT monotonic | e-depth ranges from 0.30 to 1.41 across paragraphs. Rises P1-P6 (0.81→1.41), drops at P9 (0.60), rises again P10 (1.11), drops P13-P15 (0.30→0.42). Non-monotonic with multiple peaks and troughs. | **PASS** |
| 3 | e-depth arc: high (balneum) → lower (ash fire) → zero (cooling) → moderate (gentle) | Identifiable phases of thermal variation | P6 has the highest e-depth (1.41) — the most intense balneum distillation. P9 has the lowest non-terminal e-depth (0.60) — consistent with a mode switch away from gentle heat. P13 (0.30) and P15 (0.42) are the lowest — consistent with the final gentle-fire/desiccation phase which uses slow fire, not balneum. The arc is not a clean four-phase map but shows plausible thermal regime variation. | **PARTIAL** |
| 4 | Significant dar count (multiple material additions/returns) | Several dar tokens distributed across paragraphs | 10 dar total across 8 paragraphs (P1, P2, P3, P4, P8, P13, P14, P15). This is a HIGH dar count for a 415-token folio. P3 and P14 each have 2 dar. Recipe specifies at least 5 distinct material handling events (take lunaria, put water on dregs, return liquor to dregs, repeat). 10 dar distributed across most of the folio is consistent with a recipe where material is repeatedly moved, returned, and reintroduced. | **PASS** |
| 5 | Quality gate: observation MIDDLEs at "animated water begins to burn" | Observation MIDDLEs (cfh, ckh, cth, ecth) at a monitoring point | 4 observation MIDDLEs: cfh at P3 (flag+adjust+watch — "is the fire correct?"), ckh at P14 (adjust+heat+watch — "heat-level check"), cth at P15 (adjust+transfer+watch — "watch what's being transferred"). Recipe says "en tro que veies distillar per l'aygua animada que comença a cremar" (until you see the animated water begin to burn). cfh at P3 is plausible as the quality gate for this step (P1-P2 = separation, P3 = fire monitoring for the quality checkpoint). Also 4 chekar tokens at P2, P5, P12, P15 — additional active verification moments. | **PASS** |
| 6 | Cooling phase with near-zero heat tokens | At least one paragraph with suppressed qo prefix | P9 has 0 qo tokens (5 tokens total: ta, aiin, okeear, oteody, arar). This is the only paragraph with zero qo. Recipe says "lexa refradar la materia ab tot lo vexell" — let the material cool with the vessel. A 5-token paragraph with no heat tokens is a concise encoding of "let it cool." P13 also has low qo (3/23 = 13%, below folio average). | **PASS** |
| 7 | Iterative structure (return + repeat) | Repetitive patterns: saiin/daiin cycling, iteration markers | The folio is saturated with iteration markers: saiin appears at P1/P3/P4/P5/P6/P10/P13 (7 paragraphs), daiin at P1/P3/P4/P5/P14/P15 (6 paragraphs). Multiple aiiin tokens (triple-i: deep iteration) at P1/P2/P4/P5/P15. Recipe says "reitera ta distillació" — iterate your distillation. The pervasive iteration vocabulary across most paragraphs is consistent with a recipe built around repeated distillation cycles with material return. | **PASS** |
| 8 | Two apparatus configurations (balneum then ash fire) | Shift in prefix profile mid-folio suggesting equipment change | P1-P7: ok prefix consistently present (vessel management during balneum). P6 (peak balneum, e-depth 1.41) has ch=7, qo=4 — heavy monitoring of gentle heat. P10 onward: ch prefix dominates even more heavily (P10: ch=10, P14: ch=9) — consistent with closer monitoring needed during the more dangerous ash-fire phase. The prefix profile shift from balanced ok/qo/ch in P1-P4 to ch-dominant in P10-P14 is directionally consistent with a move from passive balneum to active ash-fire monitoring. Not conclusive but directionally correct. | **PARTIAL** |

**Summary: 6 PASS, 2 PARTIAL, 0 FAIL**

## Key Quantitative Evidence

### Folio-Level Summary

| Para | Lines | Tokens | dar | e-depth | chekar | Obs MIDDLEs | fch | Mapped Recipe Phase |
|------|-------|--------|-----|---------|--------|-------------|-----|---------------------|
| P1 | 1-6 | 52 | 1 | 0.81 | 0 | — | 1 | Take lunaria, begin separation |
| P2 | 7-10 | 28 | 1 | 0.64 | 1 | — | 0 | Separate phlegmatic water (balneum) |
| P3 | 11-14 | 35 | 2 | 0.74 | 0 | cfh | 0 | Continue until animated water burns (quality gate) |
| P4 | 15-19 | 45 | 1 | 0.91 | 0 | — | 0 | Distill animated water aside; divide in two |
| P5 | 20-24 | 42 | 0 | 0.93 | 1 | — | 0 | Put animated water on dregs |
| P6 | 25-26 | 17 | 0 | 1.41 | 0 | — | 0 | Sawdust fire distillation in balneum mariae |
| P7 | 27-29 | 28 | 0 | 1.14 | 0 | — | 0 | Continue balneum distillation |
| P8 | 30 | 10 | 1 | 0.90 | 0 | — | 0 | Switch to dry ash fire; distill oil |
| P9 | 31 | 5 | 0 | 0.60 | 0 | — | 0 | Let material cool with vessel |
| P10 | 32-34 | 28 | 0 | 1.11 | 0 | — | 0 | Return first liquor to dregs |
| P11 | 35 | 6 | 0 | 0.67 | 0 | — | 0 | Begin repeated distillation cycle |
| P12 | 36 | 10 | 0 | 0.90 | 1 | — | 0 | Continue iteration until dregs dry |
| P13 | 37-38 | 23 | 1 | 0.30 | 0 | — | 0 | Unctuous moisture raised; gentle fire |
| P14 | 39-41 | 24 | 2 | 0.58 | 0 | ckh | 0 | Continue gentle fire; elements embrace |
| P15 | 42-47 | 62 | 1 | 0.42 | 1 | cth | 0 | Termination: elements bind, desiccate |

**e-depth** measures thermal intensity: higher values indicate more gentle/stabilized heat (balneum mariae signature), lower values indicate either stronger direct fire or reduced thermal involvement. The recipe specifies at least three thermal regimes: balneum mariae, ash fire with sawdust continuity, and gentle (lent) fire for final desiccation. The e-depth profile should therefore show variation, not a flat or monotonically declining pattern.

### e-depth Thermal Arc

| Phase | Paragraphs | Mean e-depth | Recipe Phase |
|-------|-----------|-------------|--------------|
| Opening separation | P1-P3 | 0.73 | Element separation in balneum — moderate gentle heat |
| Animated water distillation | P4-P5 | 0.92 | Distilling aside the animated water — elevated gentle heat |
| Peak balneum | P6-P7 | 1.28 | "en bany marie" — maximum balneum signature |
| Mode switch + cooling | P8-P9 | 0.75 | Ash fire then "lexa refradar" — heat change then cooling |
| Return/iteration | P10-P12 | 0.89 | Return liquor, iterate — moderate sustained heat |
| Final gentle fire | P13-P15 | 0.43 | "lauger foch" — slow gentle fire for desiccation (LOW e-depth) |

The thermal arc shows a clear two-hump pattern: initial rise to balneum peak at P6-P7, brief dip for the ash-fire/cooling transition at P8-P9, recovery for the return-iteration phase at P10-P12, then final decline for the desiccation phase at P13-P15.

**Critical note on final phase:** The recipe's final "lauger foch" (slow gentle fire) produces the LOWEST e-depth on the folio (0.30-0.42). This is initially counterintuitive — why would "gentle fire" have low e-depth? The answer is that this phase is a slow drying fire, not a balneum. Balneum mariae (water bath) produces high e-depth because the thermal control is mediated through water, encoding the dampening/stabilization semantics of the e-atom. Direct dry fire, even when gentle, lacks that mediation layer. The e-depth pattern correctly discriminates between "gentle balneum" (high e-depth) and "gentle dry fire" (low e-depth).

### dar Distribution

| Paragraph | dar count | Recipe context |
|-----------|-----------|----------------|
| P1 | 1 | Take lunaria liquor |
| P2 | 1 | Handling phlegmatic water |
| P3 | 2 | Working with elements during quality-gate phase |
| P4 | 1 | Distill animated water aside |
| P8 | 1 | Material handling at ash-fire transition |
| P13 | 1 | Handling unctuous moisture |
| P14 | 2 | Return liquor + iterate (2 material handling events) |
| P15 | 1 | Final material handling |

10 dar across 8 of 15 paragraphs. The recipe is a material-intensive procedure: take lunaria, separate water, divide in two, put water on dregs, return liquor, iterate. The dar distribution is broadly consistent — material handling events are spread across the procedure, with the heaviest concentration in the opening (element separation) and the return/iteration phase.

### fch (mercury marker, C1939) Distribution

P1 contains 1 fch token (fcheol, L1). The recipe is explicitly about creating quicksilver ("los nostres argents vius" — our quicksilvers). The presence of fch in the opening paragraph, where the recipe specifies taking "liquor mercuriall o lunaria," is consistent with the C1939 finding that fch indexes mercury-related operations.

However, only 1 fch on the entire folio is LOW for a mercury-focused recipe. f106v (Ch40M silver transmutation, C1943) has fch x2, f113r (Ch47M elemental separation, C1944) has fch x4. This could indicate that III.1.0 is not primarily about mercury processing per se but about creating the precursor liquors FROM lunaria — the mercury is the input material (marked once at introduction), not the ongoing focus of the procedural operations.

### Observation MIDDLEs

| Para | MIDDLE | Atoms | Workshop reading | Recipe context |
|------|--------|-------|-----------------|----------------|
| P3 | cfh | c.f.h | adjust, flag, watch | Is the fire at the right level? At the "animated water burns" quality gate |
| P14 | ckh | c.k.h | adjust, heat, watch | Is the heat level correct? During the gentle-fire phase |
| P15 | cth | c.t.h | adjust, transfer, watch | Watch what's being transferred. Final distillation monitoring |

3 observation MIDDLEs concentrated in the quality-gate (P3), gentle-fire (P14), and termination (P15) phases. The recipe is monitoring-intensive at exactly these points: the animated-water burn test, the fire-level maintenance during the desiccation phase, and the final "elements embrace and bind" endpoint.

## Paragraph-Level Assessment

### P1 (Lines 1-6, 52 tokens): Take lunaria, begin separation

**Recipe says:** "Tu pendràs de la liquor mercuriall o lunaria quant en volràs, e de aquella per distillació departiràs les elements."

**What the tokens say:** The paragraph opens with keeoal (steady-state thermal to arrangement state), chool (monitor arrangement), followed by heavy ok (vessel management, 9 tokens) and qo (heat, 8 tokens) prefix deployment. The single fch token (fcheol) on L1 marks the mercury-related material at introduction. dar x1 (daiin, L5) marks material introduction. The ok/qo interleaving through 6 lines encodes a sustained distillation setup: vessel management coordinated with heat application. Mean e-depth 0.81 indicates moderate balneum — consistent with the recipe's "en bany ta distillació."

**Match assessment:** COHERENT. Material introduction (fch + dar), vessel setup (heavy ok), balneum distillation (moderate e-depth), all present over a substantial 52-token paragraph encoding the initial separation.

### P2 (Lines 7-10, 28 tokens): Separate phlegmatic water

**Recipe says:** "Primerament separaràs l'aygua fleumatica en la qual està mortificat lo esperit."

**What the tokens say:** pch header (paragraph specification). Heavy ok prefix (6 tokens) and ot (4 tokens) — vessel + transfer rate monitoring. chekar x1 at L8 (chekaiiin: active check with iteration). dar x1 (dain, L10) — material handling. Mean e-depth 0.64 (lower than P1) — the phlegmatic water is the first, easiest fraction to separate, requiring less intensive thermal control.

**Match assessment:** COHERENT. Vessel-focused monitoring (ok/ot dominant) with a quality check and material handling, at reduced thermal intensity for the straightforward phlegmatic separation.

### P3 (Lines 11-14, 35 tokens): Continue until animated water burns (quality gate)

**Recipe says:** "E continua en bany ta distillació en tro que veies distillar per l'aygua animada que comença a cremar."

**What the tokens say:** tch header. qo increases (6 tokens) — more heat management as distillation intensifies. cfh observation MIDDLE at L11 (chcfhy: flag+adjust+watch) — the recipe's quality gate, watching for the animated water to begin burning. dar x2 (daiin L12, daiin L13) — material handling as fractions are separated. The 2-dar paragraph is consistent with "aquella distilla a part" (distill that aside) and dividing into two parts. Mean e-depth 0.74, moderate balneum.

**Match assessment:** COHERENT. The cfh observation MIDDLE at the precise point where the recipe requires visual monitoring ("until you see") is the strongest single piece of evidence. Increasing heat engagement (qo) and material separation (2 dar) align with the recipe's intensifying distillation and fraction collection.

### P4 (Lines 15-19, 45 tokens): Distill animated water aside; intensive phase

**Recipe says:** "E aquella distilla a part... E aquella partiràs en dues parts."

**What the tokens say:** pch header. This is the most qo-heavy paragraph on the folio (14/45 = 31%). Also the most ch-heavy (9 tokens). Mean e-depth 0.91 — elevated balneum intensity. Multiple qokeedy tokens (gentle balneum heat) interspersed with qokeeey (L18: deep gentle heat) and qokeeody (gentle heat with arrangement). The qo saturation encodes sustained, intensive distillation. dar x1 at L17. Two am tokens (L15, L18) — phase closures within the paragraph, consistent with the recipe's two-part division.

**Match assessment:** COHERENT. The highest-heat-engagement paragraph encodes the most thermally intensive phase of the recipe: extended distillation to collect the animated water, with two internal phase completions matching the two-part division.

### P5 (Lines 20-24, 42 tokens): Put animated water on dregs

**Recipe says:** "Tu mettràs la dita part de l'aygua animada sobre les feces, que serràn en semblança de pega fusa."

**What the tokens say:** pch header. ch prefix dominates (12 tokens) — heavy active monitoring. This is logical: putting liquid on hot pitch-like residue requires careful observation. qo still significant (9 tokens). Mean e-depth 0.93 — sustained balneum. chekar x1 at P5 — active quality verification during this sensitive operation. Notably, dar = 0 despite this being a material-addition step. However, the recipe describes returning previously separated material, not introducing new substance — the dar-free encoding may reflect that this is a re-combination, not a new material introduction.

**Match assessment:** PARTIALLY COHERENT. The monitoring intensity (ch dominant) and thermal profile match the sensitive operation of putting liquid on hot residue. The absence of dar is surprising but defensible — this is material return, not new material introduction.

### P6 (Lines 25-26, 17 tokens): Sawdust fire distillation in balneum mariae

**Recipe says:** "E soit fet ceste distillacion en bany marie."

**What the tokens say:** Short paragraph (17 tokens, 2 lines). ch dominant (7 tokens), qo present (4 tokens). lk x1 (lkeeedy: furnace equipment at deep gentle heat). **Mean e-depth 1.41 — the HIGHEST on the folio.** This is the peak balneum mariae signature. The recipe explicitly specifies "en bany marie" at this point.

**Match assessment:** STRONGLY COHERENT. The highest e-depth on the entire folio occurs at the paragraph where the recipe explicitly specifies balneum mariae distillation. This is the single strongest piece of structural evidence in the entire assessment.

### P7 (Lines 27-29, 28 tokens): Continue balneum / transition toward ash fire

**Recipe says:** "Aprés mit-ho en foch sech cinerench ab aquell continuitat de serradura."

**What the tokens say:** pch header. qo dominant (8 tokens). Mean e-depth 1.14 — still elevated but declining from P6's peak. Multiple ke-prefix tokens (2: keedy, keeeody) plus yk tokens (2: ykeey). The e-depth is transitioning downward from the balneum peak, consistent with preparation for the mode switch to ash fire.

**Match assessment:** COHERENT. The declining-but-still-elevated e-depth encodes the transition from pure balneum toward ash fire, with continued thermal engagement (heavy qo).

### P8 (Line 30, 10 tokens): Switch to dry ash fire; distill oil

**Recipe says:** "Distilla lo oli, e a la fi de la distillació lexa refradar la materia ab tot lo vexell."

**What the tokens say:** Short paragraph (10 tokens, 1 line). po header — unusual opener. sh dominant (2 tokens: sheedy, sheedar — watching the distillate). ok x2 (vessel management). dar x1 (dalkedy: material handling with heat). qo x1 (qopchedy: heat with pause+adjustment — adjusting the fire mode). Mean e-depth 0.90 — dropped from P7's 1.14.

**Match assessment:** PARTIALLY COHERENT. The reduced e-depth is consistent with switching from balneum to ash fire (less thermal mediation). The dar token and passive observation (sh) match oil distillation. But the paragraph is very short (10 tokens) for what the recipe describes as a significant operational phase.

### P9 (Line 31, 5 tokens): Let material cool with vessel

**Recipe says:** "Lexa refradar la materia ab tot lo vexell."

**What the tokens say:** Minimal paragraph: 5 tokens on a single line. ta header (transfer), aiin (yield into cycle), okeear (vessel: cool and respond), oteody (transfer rate: cool arrangement done), arar (respond and complete). **Zero qo tokens** — no heat source management. Mean e-depth 0.60 — the lowest in the mid-folio range.

**Match assessment:** STRONGLY COHERENT. A 5-token paragraph with zero heat-source engagement perfectly encodes "let it cool." The brevity itself is meaningful — cooling is a passive operation requiring minimal instruction. The vessel (ok) and transfer (ot) prefixes encode "the vessel is cooling and the material is settling."

### P10 (Lines 32-34, 28 tokens): Return first liquor to dregs

**Recipe says:** "Puys retorna la primera liquor sobre les feces e reitera ta distillació."

**What the tokens say:** tch header. ch dominant (10 tokens) — heavy monitoring during the return operation. qo returns (5 tokens) — heat source re-engaged after the cooling pause. Multiple qopchedy tokens (heat with pause+adjustment). checkhy x2 (check heat level). Mean e-depth 1.11 — elevated again, consistent with resuming balneum-type distillation.

**Match assessment:** COHERENT. Heat re-engagement (qo returns after P9's zero), elevated e-depth recovery, and heavy monitoring (ch dominant) all match the recipe's resumption of distillation after cooling. The checkhy tokens (heat-level checks) match the need to establish the correct fire level when restarting.

### P11 (Line 35, 6 tokens): Begin repeated distillation cycle

**Recipe says:** (continuing iteration: "reitera ta distillació axí com ja és dit")

**What the tokens say:** Minimal paragraph: 6 tokens. pch header, shedy (watch), qokaiin (sustained heat with deep iteration), okar (vessel response), chedy (check state), checkhy (check heat level). Mean e-depth 0.67.

**Match assessment:** COHERENT. A brief operational handoff paragraph: re-establish the distillation cycle parameters. The qokaiin (sustained deep cyclic heating) with checkhy (heat-level verification) encodes the restart of an iterative distillation pass.

### P12 (Line 36, 10 tokens): Continue iteration until dregs dry

**Recipe says:** "En tro que les feces esteguen totes seques e arses."

**What the tokens say:** tch header. lk x2 (furnace equipment: lky, lkedy). qo x2 (qokeedy: gentle heat, qotedy: heat-driven transfer). chekar x1 (cheky: active heat check). Mean e-depth 0.90. raram at line end (paragraph closure with final marker).

**Match assessment:** COHERENT. Equipment-focused (2 lk tokens) with sustained gentle heat (qokeedy) and a quality check. The recipe says to continue until dregs are dry — this encodes ongoing equipment-managed distillation with monitoring.

### P13 (Lines 37-38, 23 tokens): Unctuous moisture raised; transition to gentle fire

**Recipe says:** "E que l'humit unctuós sia tot sublevat... E per aquella se fa negror, blanchor e rojor."

**What the tokens say:** te header (preparation/transfer). dar x1 (dain L38). Mean e-depth **0.30 — the LOWEST on the folio**. qo reduced (3 tokens). a-HEAD dominant (7 tokens) — yield operations. The dramatic e-depth drop signals a fundamental thermal regime change: away from balneum-type processing toward the recipe's "lauger foch" (gentle fire) for the final desiccation phase.

**Match assessment:** COHERENT. The lowest e-depth on the folio at the precise point where the recipe transitions from distillation cycling to gentle-fire desiccation. The yield-heavy HEAD profile (a-HEAD = 7) matches the recipe's focus on the product that has been "raised" (sublevat).

### P14 (Lines 39-41, 24 tokens): Continue gentle fire; elements embrace

**Recipe says:** "E aquest foch se deu continuar en tro que les elements se sien abrachats et ensamble liés."

**What the tokens say:** te header (continuation of preparation). ch dominant (9 tokens) — heavy monitoring of a delicate endpoint. dar x2 (daiin L40 x2) — the recipe's final material interactions. ckh observation MIDDLE at L41 (checkhey: check heat level) — monitoring fire intensity during the critical binding phase. Mean e-depth 0.58, still low (gentle dry fire, not balneum).

**Match assessment:** COHERENT. The ckh observation MIDDLE (heat-level check) at the phase where the recipe says to continue fire until elements "embrace and bind" is a strong match. Heavy monitoring (ch = 9) encodes the careful attention needed at this critical endpoint. The 2 dar tokens match the recipe's handling of elements that are being combined.

### P15 (Lines 42-47, 62 tokens): Termination — elements bind, desiccate

**Recipe says:** "E la lur terminació és que a poch a poch se sien cremats en tro que en aquell lent foch se sien desiccats."

**What the tokens say:** The longest paragraph (62 tokens, 6 lines). po header (new mode). ch dominant (14 tokens) — maximum monitoring. cth observation MIDDLE (L44a: chcthy, adjust+transfer+watch — monitoring what's being transformed). chekar x1. dar x1 (daldy L45: careful material placement). Mean e-depth **0.42** — still very low, confirming continued gentle dry fire. Multiple am tokens throughout (phase closures). Final tokens: olkaiin (vessel sustained heating), oty (transfer done), ary (complete — respond and end).

**Match assessment:** COHERENT. The largest paragraph on the folio encodes the long final phase: sustained gentle fire monitoring ("a poch a poch" = gradually). The cth observation MIDDLE monitors the transformation endpoint. The ary line-final token (respond and complete) at L47 encodes true procedural termination. Low e-depth maintained throughout confirms dry-fire (not balneum) operation to the end.

## Cross-Paragraph Patterns

### e-depth Thermal Arc (Complete)

```
P1  ████████░░░░░░  0.81  Opening separation (balneum)
P2  ██████░░░░░░░░  0.64  Phlegmatic water
P3  ███████░░░░░░░  0.74  Quality gate
P4  █████████░░░░░  0.91  Animated water distillation
P5  █████████░░░░░  0.93  Water on dregs
P6  ██████████████  1.41  *** PEAK: "en bany marie" ***
P7  ███████████░░░  1.14  Continue balneum / transition
P8  █████████░░░░░  0.90  Ash fire switch
P9  ██████░░░░░░░░  0.60  *** COOLING: "lexa refradar" ***
P10 ███████████░░░  1.11  Return liquor (heat resumed)
P11 ██████░░░░░░░░  0.67  Begin iteration
P12 █████████░░░░░  0.90  Continue iteration
P13 ███░░░░░░░░░░░  0.30  *** LOWEST: gentle dry fire ***
P14 █████░░░░░░░░░  0.58  Continue gentle fire
P15 ████░░░░░░░░░░  0.42  Termination: desiccation
```

The two-hump-then-decline shape is the central structural finding: balneum operations peak at P6-P7, cooling creates a clear valley at P9, the return/iteration phase partially recovers, then the final gentle-fire phase shows a sustained decline to the folio's lowest values. This arc maps directly onto the recipe's three thermal regimes.

### dar Distribution Pattern

| Region | Paragraphs | dar count | Recipe phase |
|--------|-----------|-----------|-------------|
| Opening | P1-P4 | 5 | Taking lunaria, separating elements, dividing fractions |
| Peak balneum | P5-P7 | 0 | Sustained distillation (no new material) |
| Mode switch | P8-P9 | 1 | Material handling at ash fire transition |
| Iteration | P10-P12 | 0 | Repeated distillation (cycling existing material) |
| Final phase | P13-P15 | 4 | Material handling during binding/desiccation |

dar concentrates in the material-handling phases (opening separation and final combination/binding), with depletion during sustained distillation phases where no new material is introduced. This matches the recipe's structure: material addition at the start, pure distillation in the middle, and material manipulation during the final binding phase.

## Verdict: COHERENT

### Strength of Evidence

The f112v ↔ III.1.0 match shows strong structural coherence across multiple independent dimensions:

1. **e-depth thermal arc** — The folio's highest e-depth (1.41) occurs at the explicit "en bany marie" paragraph. The lowest values (0.30-0.42) occur at the gentle dry-fire desiccation phase. The cooling paragraph (P9) has zero qo tokens. These three features independently encode the recipe's three thermal regimes.

2. **dar distribution** — 10 dar tokens distributed across 8 paragraphs match a material-intensive recipe with separation, division, return, and recombination operations.

3. **Observation MIDDLEs** — cfh at the animated-water quality gate (P3), ckh at the fire-level monitoring during gentle-fire binding (P14), cth at the final transformation monitoring (P15). All three occur at recipe-predicted monitoring points.

4. **fch mercury marker** — Present in P1 where the recipe introduces lunaria/mercury material.

5. **Paragraph count and size** — 15 paragraphs for a 13-step recipe, with paragraph sizes roughly proportional to operational complexity (P6/P9 short for simple operations, P4/P5/P15 long for complex ones).

6. **Zero-heat cooling** — P9's 5-token zero-qo paragraph directly encodes "let it cool."

### Weaknesses

- The apparatus switch prediction (balneum → ash fire) is visible as an e-depth shift but not as a clean prefix-profile discontinuity.
- P5 (water on dregs) lacks dar despite being a material-combination step — the argument that this is material return rather than new introduction is plausible but ad hoc.
- Some paragraphs (P11, P12) are very short and could map to multiple recipe phases; the one-to-one paragraph-to-step mapping is approximate, not exact.

### Overall Assessment

f112v shows structural coherence with III.1.0 across thermal arc shape, material distribution, observation MIDDLE placement, mercury marking, and cooling encoding. The evidence is not merely "consistent" — the e-depth peak at the explicit balneum marie paragraph and the zero-heat cooling paragraph at the explicit cooling step are specific structural predictions that would NOT hold for an arbitrary recipe assignment.

## Discrimination Summary

**To be completed when negative control (III.19.3) finishes.**

The key discrimination question: does the thermal arc shape, dar distribution, and observation MIDDLE placement distinguish III.1.0 from the negative control recipe? The predictions that should fail for III.19.3:
- III.19.3 is a short maceration (3 days), NOT a multi-regime distillation → e-depth should not show the two-hump pattern
- III.19.3 has minimal material handling → 10 dar should be excessive
- III.19.3 has no explicit "let it cool" step → P9's zero-qo should be unexplained
- III.19.3 has no balneum → P6's peak e-depth should be unmotivated
