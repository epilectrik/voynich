# Validated Reading: f112r ↔ III.11.0 Red Mercury Tincture (Cohobation)

**Match tier:** Supported
**Expert verdict:** Partially Coherent (P14 e-depth contradicts calcination endpoint; no ×3 counting anchor)
**Full token listing:** `data/f112r_cold_read.txt` (394 tokens, 49 lines)

---

## How to Read This Document

This recipe is 213 words. This folio is 394 tokens — a 1.8:1 ratio. The recipe describes creating red mercury tincture through cohobation: alternating balneum and ash distillation, returning water to viscous earth each time, extracting the fire/soul from the earth, and finally washing the fire by distillation and calcination until "red as burning fire."

The folio has 14 paragraphs — a high fragmentation count that encodes the recipe's multi-phase iterative structure with micro-gates at transition points.

**What works:**
- **e-depth oscillation** encodes alternating balneum/ash distillation
- **dar distribution** concentrates in P2-P5 (extraction phases), zero in P6-P14 (process management)
- **Observation MIDDLEs** at the 4 highest-risk moments
- **ok-prefix shift** from transfer monitoring (first half) to vessel management (second half)

**What doesn't work (expert-identified):**
- **P14 e-depth = 0.923** directly contradicts the recipe's calcination endpoint — "lavalo ab distillació et calcinació en tro que sia bé roig" (wash by calcination until red as fire). Per C1225/C1970, calcination should produce near-zero e-depth. This is the strongest negative signal.
- **No ×3 counting anchor** for ".iii. vegades" (three times balneum). Per C1965 standard, the counting shorthand is absent.

Every token on every line appears in this document.

---

## The Recipe

### Catalan (III.11.0, SISMEL — Part III cipher)

> Fill, tu prendràs la liquor derrera que pus greu és separada per distillació sobre cendres; e aquella distillaràs en bany per .iii. vegades. E aprés cascuna distillació, metràs l'aygua sobre la terra viscosa. Separa altra vegada aquella aygua per cendres; açò's fa per entenció que l'aygua traga lo foch qui és en la terra e sia guardat per tinctura. Distilla aquella liquor altra vegada per bany, a fi que's dissoulle del foch, e mit lo foch tot temps a part. Distillada que sia, tira més de la ànima de la terra ab foch sech. E guarda emperò que la terra no's rubifich, car tantost cremaria la tinctura del sofre blanch. E açò reitera en tro que veies la terra comminuida, defallent de tota humiditat. Puis pren lo foch e lavalo ab la distillació et calcinació en tro que sia bé roig así com a foch ardent.

### English

Son, take the last liquor (hardest to separate) by distillation on ashes; distill it in balneum 3 times. After each distillation, put the water on the viscous earth (it dissolves quickly). Separate that water again by ashes — this is to extract the fire from the earth for tincture. Distill the liquor again by balneum to strip the fire; set fire aside. After distillation, extract more soul from the earth with dry fire. But BEWARE: don't let the earth turn red — it would burn the white sulfur tincture. Repeat until the earth is depleted of all moisture. Then take the fire and wash it by distillation and calcination until red as burning fire.

### Recipe Structure

| Step | Operation | Heat | Key feature |
|------|-----------|------|-------------|
| 1 | Distill last liquor on ashes | ashes | initial separation |
| 2 | ×3 balneum distillation + earth return | balneum | cohobation cycle |
| 3 | Ash distillation to extract fire from earth | ashes | alternating regime |
| 4 | Balneum to strip fire from water | balneum | alternating regime |
| 5 | Dry fire extraction of earth's soul | dry fire | strongest heat |
| 6 | BEWARE: don't let earth redden | — | **critical quality gate** |
| 7 | Repeat until earth depleted | gentle | iterative |
| 8 | Wash fire to red via distillation + calcination | calcination | **endpoint: "red as fire"** |

---

## Structural Predictions (derived from recipe before reading folio)

| # | Prediction | Rationale | Result |
|---|-----------|-----------|--------|
| 1 | Alternating e-depth (balneum/ashes cycling) | cohobation = repeated regime switches | **MATCH** — oscillating profile |
| 2 | ×3 counting anchor | ".iii. vegades" | **NOT DETECTED** — no 3-token counting run |
| 3 | dar at earth-return positions | "metràs l'aygua sobre la terra" | **MATCH** — dar in P2-P5 |
| 4 | Quality gate observation MIDDLE | "guarda que la terra no's rubifich" | **MATCH** — observation tokens in P6 area |
| 5 | Final paragraphs = calcination (low e-depth) | "lavalo ab calcinació" | **FAIL** — P14 e-depth 0.923, should be near-zero |
| 6 | Iterative structure | "açò reitera" | **MATCH** — 14 paragraphs with micro-gates |
| 7 | fch mercury markers | creating mercury tincture | **PARTIAL** — low fch presence |

**Score: 4/7 confirmed, 1 partial, 1 not detected, 1 fail**

---

## Folio Overview

| Metric | Value |
|--------|-------|
| Total tokens | 394 |
| Lines | 49 |
| Paragraphs | 14 |
| dar (material-add) | 7 |
| Quality checks (chek/shek class) | 1 |
| Observation MIDDLEs | ckh×1, cth×2, ckhh×1 |
| hh (extended observation) | 0 |
