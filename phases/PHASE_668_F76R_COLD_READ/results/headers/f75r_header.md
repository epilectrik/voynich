# Cold Read: f75r ↔ III.19.0 Aqua Vitae (Reflux Distillation)

**Match tier:** CONFIRMED
**Expert verdict:** Coherent (8/8 structural predictions confirmed)
**Full token listing:** `data/f75r_cold_read.txt` (412 tokens, 46 lines)

---

## How to Read This Document

This recipe is 100 words. This folio is 412 tokens. That ratio — roughly 4:1 — is not a mismatch. It is the expected behavior of a notation system encoding operational control programs.

The recipe is a **specification**: it tells you what materials to combine, in what order, at what temperature, for how many cycles. "Reiterate, renewing the honeycomb at each second distillation, four times; and after, nine times" is one sentence. But executing a 4-then-9-cycle reflux distillation requires the operator to manage the fire across 13 passes, monitor the distillate, renew the honeycomb at intervals, transfer between vessels, and verify quality at each stage. The folio encodes all of that.

**What makes this match credible is not narrative plausibility** — generic agents produced COHERENT readings for wrong recipes in negative controls. What makes it credible is **specific structural features that discriminate**:

- **Counting anchors**: 4 consecutive identical `qokedy` tokens on L13 (corpus-singular in Currier B per C1889), directly encoding "per quatre vegades." 9 qok-class tokens spanning L37-38, encoding "ix vegades."
- **e-depth thermal arc**: V-shaped profile crashing to 0.18 at P7 (physical vessel transfer — no heat), consistent with reflux distillation's mid-process apparatus change
- **dar distribution**: Back-loaded (46% in P9), matching the recipe's "renew honeycomb at each second distillation" during the x9 cycle
- **Zero-dar fermentation phase**: P3-P4 have zero material additions, matching "put to ferment" (sealed, no additions)
- **Observation MIDDLE fade-out**: P5 has zero observation MIDDLEs during autonomous cycling

The negative control for this folio (f75r ↔ III.21.0, wrong recipe) scored 0/7 on structural predictions. The correct recipe scores 8/8. That gap is the evidence.

Every token on every line appears in this document. Where a token has a confident workshop reading, it is cited with source. Where a token is truly unparseable (5 of 412, 1.2%), it says *unrecognized*.

---

## The Recipe

### Catalan (III.19.0, SISMEL — Part III cipher, no letter codes in this sub-recipe)

> Tu pendràs l'aygua de vida e separa'n sa humiditat tota per distillació; e la substancia de l'aygua, qui és pur or, tu metràs a part; e dedins la humiditat vejetal metràs la terça part de **bresca** ab tota sa substancia, ço és assaber ab la mel e ab la cera. E aquella metràs a fermentar en laugera calor per .iii. dies; e quant més hi està, més val. Puys mit-ho a distillar en bany; e aquesta distillació e fermentació reitera en renovellant la bresca a cascuna segona distillació per quatre vegades; e aprés ix vegades.

*Cipher note: "bresca" (honeycomb) appears in mirror-script cipher at first occurrence (Tavola 2, entry 24). No Part III letter codes in this sub-recipe.*

### English

Take the water of life and separate all its moisture by distillation. The substance of the water, which is pure gold, set aside. In the vegetal moisture put a third part of **honeycomb** with all its substance (honey and wax). Put to ferment in gentle heat for 3 days — the longer the better. Then distill in balneum. Reiterate this distillation and fermentation, renewing the honeycomb at each second distillation, **four times**; and after, **nine times**.

### Recipe Structure

| Step | Operation | Materials | Heat | Count |
|------|-----------|-----------|------|-------|
| 1 | Separate water of life | water of life | distillation | — |
| 2 | Set aside gold substance | pure gold | — | — |
| 3 | Add honeycomb to vegetal moisture | 1/3 part honeycomb (honey + wax) | — | — |
| 4 | Ferment | — | gentle heat | 3 days |
| 5 | Distill in balneum | — | water bath | — |
| 6 | Reiterate (renew honeycomb every 2nd distillation) | fresh honeycomb | balneum | **x4** |
| 7 | Continue reiterating | fresh honeycomb | balneum | **x9** |

---

## Structural Predictions (derived from recipe before reading folio)

| # | Prediction | Rationale | Result |
|---|-----------|-----------|--------|
| 1 | High e-depth (balneum throughout) | "distillar en bany" | **MATCH** — 0.42-0.63, balneum range |
| 2 | dar tokens for honeycomb renewal | "renovellant la bresca" | **MATCH** — 27 dar total, back-loaded |
| 3 | qo-prefix dominant (fire management) | reflux = continuous heat | **MATCH** — qo=108 (26%) |
| 4 | x4 counting anchor | "per quatre vegades" | **MATCH** — 4x qokedy on L13 (C1889, corpus-singular) |
| 5 | x9 counting anchor | "ix vegades" | **MATCH** — 9 qok-class on L37-38 (C1969) |
| 6 | Multi-paragraph procedural folio | complex multi-phase recipe | **MATCH** — 9 paragraphs |
| 7 | Observation MIDDLEs present | monitoring distillation quality | **MATCH** — ckh x6, ecth x2, cth x2 |
| 8 | Thermal arc with transfer interruption | mid-process vessel change | **MATCH** — e-depth crashes to 0.18 at P7 |

**Score: 8/8 confirmed**

---

## Folio Overview

| Metric | Value |
|--------|-------|
| Total tokens | 412 |
| Lines | 46 |
| Paragraphs | 9 |
| Workshop-readable tokens | 407/412 (99%) |
| Truly unrecognized | 5 (1.2%) |
| dar (material-add) | 27 |
| Quality checks (chek/shek class) | 4 |
| Observation MIDDLEs | ckh x6, ecth x2, cth x2 |
| hh (extended observation) | 0 |
