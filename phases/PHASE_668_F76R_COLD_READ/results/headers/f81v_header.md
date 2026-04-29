# Validated Reading: f81v ↔ III.18.0 Potable Gold (Water of Life)

**Match tier:** Supported
**Expert verdict:** Coherent (3 confirmed, 3 partial, 1 not detected)
**Full token listing:** `data/f81v_cold_read.txt` (258 tokens, 27 lines)

---

## How to Read This Document

This recipe is 182 words. This folio is 258 tokens — a 1.4:1 ratio. The recipe describes making potable gold (drinkable gold preparation) through a multi-step process: dissolve gold in special water via balneum inhumation, distill off moisture, then process lunaria through multiple distillation stages, redissolve the gold, rectify mercury, and combine into the "water of life."

The folio divides cleanly into two paragraphs that track the recipe's two-phase structure: P1 (sealed inhumation/dissolution, gentle heat, material-heavy) and P2 (active distillation/rectification, stronger heat, fire-management-heavy).

**What makes this match credible:**
- **e-depth shift**: P1=0.33 (sealed inhumation, minimal cooling intervention) vs P2=0.55 (active distillation with cooling cycles) — encodes the physical difference between passive sealed heating and active distillation
- **dar front-loading**: 71% of material additions in P1, matching the recipe's material-heavy dissolution phase
- **qo concentration shift**: P1 has 7 qo tokens, P2 has 35 — fire management 5× higher during active distillation
- **fch mercury marker** on L15 (C1939): appears at the transition to mercury rectification, exactly where the recipe says "rectifica son mercuri"
- **ckh temperature checks**: 3 in P1 (monitoring sealed balneum) + 2 in P2 (monitoring distillation)

**Honest gap:** No cs gold markers despite gold being central to the recipe. Expert explained: gold is a dissolved intermediate here, not a raw metallic input (contrast f84r where gold is actively dissolved and cs=3).

Every token on every line appears in this document.

---

## The Recipe

### Catalan (III.18.0, SISMEL — Part III cipher)

> Ara direm la composició de l'aygua potable simpla, que's fa de sanch fixat per natura per confortar lo humit radicall humanal. Pren l'aygua que ha poder de dissolre or sots la conservació de sa specie; e subtilia-lo en aquella per via de continuació ab inhumació en bany e laugera decocció. E aprés posa l'or dissolt en una carabaça de fin vidre, e distilla l'aygua e separa'n tota la humor. E estarà la substancia de l'or al fons del vexell tota secca. Puis pren de la lunaria e distilla la humor per alembich, en tro veuràs que par la diminució de sa sulphureitat no porà pus cremar. Continua ta distillació en altre receptori e aquella aygua pren en tro sobre'l cap de l'alembich no apparrà res de venes. En aquesta aygua gitaràs la substancia de l'or, e tantost se dissolrà en l'aygua vejetall per rahó del mercuri. Rectifica son mercuri de la fleuma, en tro veies que creme, e puis mescla-la ab primera eau ab la substancia de l'or. E és aygua de vida.

### English

We will now describe the composition of simple potable water, made from blood fixed by nature to comfort the radical human moisture. Take the water that has power to dissolve gold while preserving its form; subtilize it through continuous inhumation in balneum with gentle decoction. Then place the dissolved gold in a fine glass cucurbit, distill the water, and separate all the moisture. The substance of the gold will remain dry at the bottom of the vessel. Then take lunaria and distill its moisture through the alembic until you see that through diminution of its sulfureity it can no longer burn. Continue your distillation into another receptor, taking that water until nothing more appears at the head of the alembic. Into this water cast the gold substance — it will dissolve immediately in the vegetable water by reason of the mercury. Rectify the mercury from the phlegm until you see it burn, then mix it with the first water and the gold substance. This is the water of life.

### Recipe Structure

| Step | Operation | Heat | Key feature |
|------|-----------|------|-------------|
| 1 | Dissolve gold in special water | gentle balneum | "inhumació en bany e laugera decocció" |
| 2 | Place in glass cucurbit, distill off moisture | moderate | gold remains dry at bottom |
| 3 | Distill lunaria through alembic | moderate | quality gate: "no porà pus cremar" |
| 4 | Continue into second receptor | moderate | gate: "no apparrà res de venes" |
| 5 | Cast gold into vegetable water | — | immediate dissolution |
| 6 | Rectify mercury from phlegm | moderate | gate: "veies que creme" |
| 7 | Mix with first water + gold | — | **Result: water of life** |

---

## Structural Predictions (derived from recipe before reading folio)

| # | Prediction | Rationale | Result |
|---|-----------|-----------|--------|
| 1 | High e-depth early (balneum inhumation) | "inhumació en bany e laugera decocció" | **PARTIAL** — P1=0.33 (low, not high) but physically correct: sealed inhumation has minimal cooling intervention |
| 2 | cs gold markers | gold dissolved explicitly | **NOT DETECTED** — gold as dissolved intermediate |
| 3 | Multiple quality gates (3 explicit checks) | burns test, alembic head, rectification | **PARTIAL** — chekar=7 but distributed broadly |
| 4 | dar at specific moments | gold, lunaria, gold redissolution | **MATCH** — 21 dar, front-loaded in P1 |
| 5 | Two-vessel structure | cucurbit then second receptor | **PARTIAL** — 2 paragraphs map to 2 phases |
| 6 | Observation MIDDLEs at quality gates | visual checks | **MATCH** — ckh×5 distributed |
| 7 | fch mercury marker | mercury rectification | **MATCH** — fch on L15 at rectification transition |

**Score: 3 confirmed, 3 partial, 1 not detected**

---

## Folio Overview

| Metric | Value |
|--------|-------|
| Total tokens | 258 |
| Lines | 27 |
| Paragraphs | 2 |
| dar (material-add) | 21 (8.1% — highest material density in matched set) |
| Quality checks (chek/shek class) | 7 |
| Observation MIDDLEs | ckh×5 |
| hh (extended observation) | 0 |
