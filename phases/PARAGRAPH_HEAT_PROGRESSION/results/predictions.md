# Heat-Degree Predictions (LOCKED 2026-04-25)

**Methodology:** For each of 7 confirmed-match folios, predict per-paragraph fire-degree based on the matched recipe's operational content at that phase. Predictions LOCKED before computing any heat metrics.

**Scale:**
- `1` = low / no heat (setup, mixing, observation, closure, no thermal operation)
- `2` = moderate gentle heat (balneum, slow decoction, gentle fermentation, sustained low)
- `3` = vigorous heat (open fire, calcination, foch de sots, vigorous distillation pivot)

---

## f75r ↔ III.19.0 (aqua vitae × 4-9 reflux)

**Paragraphs:** 3
**Recipe heat profile:** Most operations after initial separation are balneum (gentle). Bresca addition is no-heat. Iteration is sustained balneum.

| Para | Phase | Predicted heat | Rationale |
|------|-------|:---:|-----------|
| P1 | primary distillation procedure with × 4 anchor | **2** | Fermentation in "laugera calor" + balneum distillation cycles |
| P2 | bresca-addition middle paragraph | **1** | Mixing/setup operation, no heat |
| P3 | × 9 expanded iteration | **2** | Sustained balneum reflux |

**Predicted:** `[2, 1, 2]`

---

## f84r ↔ II.12.0 (gold dissolution / putrefaction)

**Paragraphs:** 18
**Recipe heat profile:** 12 specification headers (no heat) → 5 body operations (balneum + putrefaction = sustained low) → 1 closure.

| Para | Phase | Predicted heat | Rationale |
|------|-------|:---:|-----------|
| P1-P12 | 12-parties specification (micro-headers) | **1** each | Specification block, no thermal operations yet |
| P13 | body operational onset | **2** | Initial balneum (.ii. dies) |
| P14-P17 | body operational continuation | **2** each | Putrefaction 1.5 months (sustained gentle) |
| P18 | closure | **1** | Single-token closure |

**Predicted:** `[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 1]`

---

## f78r ↔ III.36.0 (mercury congelation)

**Paragraphs:** 8
**Recipe heat profile:** "Foch de sots" (fire underneath) = vigorous heat in primary procedure. Reiteration cycles also vigorous.

| Para | Phase | Predicted heat | Rationale |
|------|-------|:---:|-----------|
| P1 | primary procedure (4-elements + 6-stage) | **3** | "Foch de sots" — vigorous heat directly applied |
| P2-P7 | reiteration sub-procedure cycles | **2** each | Repeated vigorous heat application (slightly less intense than initial) |
| P8 | final reiteration close | **2** | Same as iteration cycles |

**Predicted:** `[3, 2, 2, 2, 2, 2, 2, 2]`

---

## f86v3 ↔ II.10.0 (3-day coniuncció)

**Paragraphs:** 7
**Recipe heat profile:** Initial vigorous heating (11 hours, sawdust fire) → menstruum addition → 3-day balneum (gentle sustained) → reiterate → 1.5 month putrefaction (sustained low).

| Para | Phase | Predicted heat | Rationale |
|------|-------|:---:|-----------|
| P1 | primary heating + 11-hour distillation | **3** | Vigorous fire over fine ashes for 11 hours |
| P2 | menstruum addition setup | **2** | Transfer + sealing |
| P3 | 3-day balneum onset | **2** | Hot bath sustained |
| P4-P5 | bath continues + reiterate | **2** each | Continued balneum + distillation cycles |
| P6 | putrefaction wind-down | **2** | 1.5 months at temperate heat (sustained low gentle) |
| P7 | closure | **1** | Final state |

**Predicted:** `[3, 2, 2, 2, 2, 2, 1]`

---

## f82r ↔ III.19.3 (lunaria 3-day sealed maceration)

**Paragraphs:** 4
**Recipe heat profile:** Setup + sealing (low) → cendres × 3 days with sawdust fire (vigorous) → bath distillation (gentle) → set aside.

| Para | Phase | Predicted heat | Rationale |
|------|-------|:---:|-----------|
| P1 | 3-parts lunaria addition + setup | **1** | Material addition, no heat yet |
| P2 | sealing operation | **1** | "Tapa la carabasa ab cera" — sealing, no heat |
| P3 | 3-day cendres heating | **3** | "Sobre cendres per .iii. dies ab foch de serradura" — vigorous |
| P4 | bath distillation + set aside | **2** | "Distilla per lo bany" — gentle balneum |

**Predicted:** `[1, 1, 3, 2]`

---

## f108v ↔ III.29.0 (mercury sublimation)

**Paragraphs:** 10
**Recipe heat profile:** "Longues e lentes decoccions" (long slow decoctions) — sustained moderate gentle heat throughout. Sublimation is gentle by nature.

| Para | Phase | Predicted heat | Rationale |
|------|-------|:---:|-----------|
| P1-P3 | setup / specification opening | **1** each | Theoretical/specification content, no operations yet |
| P4-P8 | sustained sublimation body | **2** each | Long slow decoctions = gentle sustained |
| P9 | long iteration body (L33-L51) | **2** | Same gentle sustained over extended time |
| P10 | closure | **1** | Final state |

**Predicted:** `[1, 1, 1, 2, 2, 2, 2, 2, 2, 1]`

---

## f79v ↔ II.8.0 (first liquefaction)

**Paragraphs:** 7
**Recipe heat profile:** Setup + cutting (low) → material addition (low) → 3-day balneum (gentle sustained) → wind-down → closure.

| Para | Phase | Predicted heat | Rationale |
|------|-------|:---:|-----------|
| P1 | cutting/dividing F (long opening) | **1** | Mechanical setup, no heat |
| P2 | material addition setup | **1** | Adding E + menstruum, no heat |
| P3 | sealing + 3-day balneum onset | **2** | "In balneo calido per tres dies" |
| P4-P5 | bath continues | **2** each | Balneum sustained |
| P6 | wind-down | **1** | Bath ending |
| P7 | closure | **1** | "Ut Deus det tibi bonam diem" — final |

**Predicted:** `[1, 1, 2, 2, 2, 1, 1]`

---

## Summary

| Folio | Paragraphs | Predicted profile | Pattern |
|-------|:---:|---|---------|
| f75r | 3 | [2, 1, 2] | mid-low-mid (V-shape) |
| f84r | 18 | [1×12, 2×5, 1] | spec-low → body-mid → closure-low |
| f78r | 8 | [3, 2, 2, 2, 2, 2, 2, 2] | high → sustained mid |
| f86v3 | 7 | [3, 2, 2, 2, 2, 2, 1] | high → sustained mid → low |
| f82r | 4 | [1, 1, 3, 2] | low-low-HIGH-mid |
| f108v | 10 | [1, 1, 1, 2×6, 1] | low-spec → mid-body → low-closure |
| f79v | 7 | [1, 1, 2, 2, 2, 1, 1] | low → mid-body → low |

**Predictions LOCKED.** Proceed to metric computation.
