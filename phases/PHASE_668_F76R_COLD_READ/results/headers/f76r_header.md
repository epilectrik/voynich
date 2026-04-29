# Validated Reading: f76r ↔ II.16.0 Element Separation (Sevenfold Distillation)

**Match tier:** CONFIRMED
**Expert verdict:** Coherent (5/8 structural predictions confirmed, 2 mismatches explained)
**Full token listing:** `data/f76r_cold_read.txt` (546 tokens, 47 lines)

---

## How to Read This Document

This recipe is 515 words. This folio is 546 tokens. That ratio — nearly 1:1 — makes this our most proportionate match. II.16.0 is the longest procedural chapter in the Practica, describing a multi-phase element separation with seven distillation passes and a silver-plate quality test. The folio dedicates 65% of its tokens (P1, 357 tokens) to a single massive paragraph encoding the seven-pass distillation cycle.

The tokens give you the **verb** (test, watch, heat, load, transfer). The recipe gives you the **noun** (dregs, silver plate, water of life). Together they read as complete instructions; apart, the tokens are operational rhythm. This document shows every token on every line with its workshop reading and source. Where a reading is confident (B Dictionary), it is cited. Where it is composed from atoms (Comp-v2), it is labeled. Where a token is truly unparseable, it says *unrecognized*.

**What makes this match credible:**

- **Two thermal regimes**: e-depth 0.599 (P1, distillation) vs 0.462 (P3, calcination) — matching the recipe's "foch calcinant" vs "septena distillació"
- **dar distribution tracks dregs handling**: 19 dar in P1 (70% of total) = ~1 material event per 1.5 lines during 7-pass distillation with feces removal at each pass
- **P3 prefix shift**: ok-prefix jumps from 6% (P1) to 17% (P3) — calcination is vessel-focused, distillation is fire-focused
- **Observation MIDDLEs**: ckh×16 across the folio = continuous temperature monitoring during extended distillation

**Honest gaps:** No ×7 counting anchor (C1965 counting shorthand doesn't generalize to all recipes). Only 4 paragraphs for a 7-step recipe (the scribe encoded the entire distillation cycle as one paragraph).

The negative control (f82r ↔ II.16.0, wrong folio) scored 0/6 INCOHERENT. This reading scores 5/8.

---

## The Recipe

### Catalan (II.16.0, SISMEL — Part II cipher, no letter codes in this sub-recipe)

> Fill, quant hauràs divisida la pedra per les .iiii. elements, és-te mester que les purgues per aquest regiment. La terra e lo foch són resemblats en la substancia pedrenca, e per ço han mester preparació del foch calcinant. L'ayre e l'aygua són de natura aquaticha; per ço t'és ops preparació que's fa ab septena distillació en tro són buyts de tota adustió qui vinga del part del menstruall. L'aygua e l'ayre distillaràs a·ppart en lur rectificació cascú per si; e les feces de l'aygua posaràs ab la terra. E aprés la .vi. distillació, posa'n un gota o dues sobre una lamina de pur argent: e si lo negrifica, no és buyda de tota adustió. D'on met-lo a la setena distillació, en tro lex l'argent sens nulla corrupció. Adonchs hauràs aygua de vida.

### English

Son, when you have divided the stone into 4 elements, you must purge them. Earth and fire are stone-like — they need calcining fire. Water and air are aquatic — they need sevenfold distillation until free of all burning from the menstrual. Distill water and air separately, each on its own; put the water's dregs with the earth after each distillation. After the 6th distillation, put a drop or two on a plate of pure silver: if it blackens, it is not free of burning. Put it through the 7th distillation until it leaves the silver without corruption. Then you have water of life.

### Recipe Structure

| Step | Operation | Materials | Heat | Count |
|------|-----------|-----------|------|-------|
| 1 | Divide stone into 4 elements | stone | — | — |
| 2 | Calcine earth + fire | earth, fire | calcining fire (hot, dry) | — |
| 3 | Distill water (rectification) | water | aquatic (balneum) | ×7 |
| 4 | Distill air (rectification) | air | aquatic (balneum) | ×7 |
| 5 | At each distillation: put dregs with earth | feces/dregs | — | per pass |
| 6 | After 6th: silver-plate test | 1-2 drops on silver | — | — |
| 7 | If blackens: 7th distillation | — | aquatic | — |
| 8 | Result: water of life | — | — | — |

---

## Structural Predictions (derived from recipe before reading folio)

| # | Prediction | Rationale | Result |
|---|-----------|-----------|--------|
| 1 | Two thermal regimes (low e-depth calcination + high e-depth distillation) | "foch calcinant" + "septena distillació" | **MATCH** — P1=0.599, P3=0.462 |
| 2 | ×7 counting anchor | "septena distillació" | **MISMATCH** — no counting run found (C1965: doesn't generalize) |
| 3 | Silver-plate test signature (chekar cluster) | quality gate after 6th distillation | **PARTIAL** — 3 chekar in P1, positioned early not late |
| 4 | 12 paragraphs for multi-phase recipe | 4 elements + 7 passes + test + result | **MISMATCH** — only 4 paragraphs (P1=357 tokens encodes all 7 passes) |
| 5 | dar at each distillation (feces handling) | "les feces posaràs ab la terra" | **MATCH** — 19 dar in P1, ~1 per 1.5 lines |
| 6 | qo-prefix dominant (sustained fire management) | continuous heat across 7+ passes | **MATCH** — qo=104 (19%) |
| 7 | Transfer tokens for distillation outputs | material transferred at each pass | **MATCH** — ~25 ot/qot-family tokens |
| 8 | Observation MIDDLEs at quality test | watching silver plate | **MATCH** — ckh×16 distributed across folio |

**Score: 5/8 confirmed, 1 partial, 2 mismatches (both explained)**

---

## Folio Overview

| Metric | Value |
|--------|-------|
| Total tokens | 546 |
| Lines | 47 |
| Paragraphs | 4 |
| dar (material-add) | 27 |
| Quality checks (chek/shek class) | 3 |
| Observation MIDDLEs | ckh×16, ecth×3, ecthe×1, cth×4, cfh×1 |
| hh (extended observation) | 0 |
