# Validated Reading: f79r ↔ III.12.0 Mercury Sublimation → Red Elixir

**Match tier:** Strong-supported
**Expert verdict:** Coherent (5/7 structural predictions confirmed, 1 ambiguous, 1 explained mismatch)
**Full token listing:** `data/f79r_cold_read.txt` (389 tokens, 44 lines)

---

## How to Read This Document

This recipe is 209 words. This folio is 389 tokens — a 1.9:1 ratio. The recipe describes a mercury sublimation procedure with a distinctive thermal arc: gentle dissolution → three distillation-return cycles → gradually strengthen fire → rubification (material turns red) → separation (sublimate rises white, fixed turns red) → fix elements on the residue.

The folio's e-depth tracks this arc precisely: 0.76 (gentle dissolution) → 0.34 (fire strengthening — lowest on folio) → 0.91 (congelation/cooling) → 1.50 (maximum cooling at a 4-token micro-paragraph) → 0.45 (final fixation). The non-monotonic V-shape with the 0.34 minimum at P4 is the recipe's thermal fingerprint — "paulatinament fortifica ton foch" (gradually strengthen your fire) produces the lowest e-depth at exactly the right position.

**What makes this match credible:**
- **e-depth minimum at fire-strengthening**: P4 = 0.34 (lowest on folio) exactly where the recipe says to strengthen the fire
- **fch mercury markers** (C1939): exclusively in P5 (sublimation paragraph) where mercury volatility is operationally critical
- **cth transfer-watches** concentrate in P2-P3-P5 (distillation and sublimation phases involving material movement)
- **Zero dar in P6** (autonomous fire continuation) matching "continua donchs ton foch"
- **P9 e-depth 1.50** (maximum cooling) at a 4-token micro-paragraph between quality check and final fixation

Every token on every line appears in this document. 

---

## The Recipe

### Catalan (III.12.0, SISMEL — Part III cipher: B=simple water, D=simple dissolved gold)

> Pren mercuri sublimat e blanch axí com te havem dit, e dissol-lo en aygua del mercuri, de la qual és tret lo foch de la pedra mercuriosa, en la qual sia dissolt lo foch de la pedra axí substancialment com essencialment. Aprés separes l'aygua per distillació en tro sia tot congelat. E altra vegada retorna l'aygua sobre lo mercuri; e terça vegada distilla. E aprés paulatinament fortifica ton foch, en trou veies molt fort rubificar. E si res hi ha que no sia ligat ab lo foch de la pedra, allò se'n muntarà e sublimarà per la virtut del foch tot blanch. Continua donchs ton foch en tro veies que'l sublimatiu se sia sublimat, e el fix que és baix se sia rubificat. E sobre aquest fixe sos elements; hauràs del mercuri elixir complit.

### English

Take white sublimated mercury and dissolve it in mercury water (from which the fire of the mercurial stone was drawn). Separate the water by distillation until all is congealed. Return the water to the mercury again; and a third time distill. Then gradually strengthen your fire until you see strong rubification. If anything is not bound with the stone's fire, it will rise and sublimate by the fire's virtue, all white. Continue your fire until the sublimate has sublimated and the fixed part at the bottom has turned red. Fix the elements on this fixed part — you will have complete mercury elixir.

### Recipe Structure

| Step | Operation | Heat | Key feature |
|------|-----------|------|-------------|
| 1 | Dissolve white mercury in mercury water | gentle | passive dissolution |
| 2 | Distill water until congealed | moderate | distillation |
| 3 | Return water to mercury, distill 3rd time | moderate | iterative cycling (×3) |
| 4 | Gradually strengthen fire | increasing → strong | "paulatinament fortifica" |
| 5 | Rubification — watch for red | strong | visual quality gate |
| 6 | Continue fire — sublimate rises white, fixed turns red | sustained strong | separation phase |
| 7 | Fix elements on the fixed residue | — | final operation → complete elixir |

---

## Structural Predictions (derived from recipe before reading folio)

| # | Prediction | Rationale | Result |
|---|-----------|-----------|--------|
| 1 | e-depth DECREASES across folio (fire strengthening) | "paulatinament fortifica ton foch" | **MATCH** — 0.76 → 0.34, then V-shape |
| 2 | ×3 counting anchor | "terça vegada distilla" | **AMBIGUOUS** — distributed iteration markers, not clean counting run |
| 3 | fch mercury markers (mercury is central subject) | mercury sublimation recipe | **MATCH** — fch exclusively in P5 (sublimation) |
| 4 | Sublimation signature: transfer tokens going up | material rises, separates | **MATCH** — ot-dominant P5 |
| 5 | Two-phase structure: dissolution/cycling then fire strengthening | clear phase break at "aprés paulatinament" | **MATCH** — P1-P3 gentle → P4 minimum e-depth |
| 6 | Quality gate at rubification | "en tro veies molt fort rubificar" | **MATCH** — chekar + observation tokens in P8 |
| 7 | dar concentrated early (dissolution, not sublimation) | sublimation is autonomous | **MISMATCH (explained)** — dar in P5 reflects operator managing physical separation products |

**Score: 5/7 confirmed, 1 ambiguous, 1 explained mismatch**

---

## Folio Overview

| Metric | Value |
|--------|-------|
| Total tokens | 389 |
| Lines | 44 |
| Paragraphs | 10 |
| dar (material-add) | 12 |
| Quality checks (chek/shek class) | 4 |
| Observation MIDDLEs | cth×4, ckh×3 |
| hh (extended observation) | 0 |
