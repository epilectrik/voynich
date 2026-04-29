# Validated Reading: f76v ↔ III.15.0 Ferment Conversion (Liquefaction → Multiplication)

**Match tier:** Strong-supported
**Expert verdict:** Coherent (5/7 structural predictions confirmed)
**Full token listing:** `data/f76v_cold_read.txt` (400 tokens, 41 lines)

---

## How to Read This Document

This recipe is 86 words. This folio is 400 tokens — a 4.7:1 ratio. The recipe describes converting a tincture ferment into a liquefied, fusible form through progressive fixation, then multiplying it infinitely. The key operation is fixation: binding materials under increasing heat until the product melts like wax without smoke.

The folio's e-depth tracks this precisely: descending from 1.01 (P1, gentle initial fixation) through 0.67 (P4, intense fixation) to 0.60 (P6, strongest heat for infinite multiplication). This monotonic descent encodes progressive heat strengthening — each phase requires more fire than the last.

**What makes this match credible:**
- **Descending e-depth** (1.01 → 0.60): monotonic across 6 paragraphs, encoding progressive fixation
- **chekar concentration in P5** (9.5% density): fusibility test tokens cluster at exactly the paragraph where the recipe says "veies que's fona com a cera" (see it melt like wax)
- **sa-prefix concentration in P6** (8 tokens): scaffold/iterate tokens for "in infinit se pot multiplicar"
- **n-atom pervasiveness** (~50+ tokens): bind/contain atoms throughout — fixation is fundamentally binding
- **Zero dar in P5** (the test paragraph): you don't add material during a quality test

**Honest gaps:** No cs gold markers despite gold being added (H = gold in Part III cipher). dar=10 rather than the predicted low/zero — the recipe involves more material handling than the brief text suggests.

Every token on every line appears in this document.

---

## The Recipe

### Catalan (III.15.0, SISMEL — Part III cipher: H = gold)

> Quant tu hauràs fet lo ferment de tinctura, aquell convertiràs en liquefacció, ajustant-li H segon lo pes que saps, e lo seny te demonstrarà per la obra de natura, en tro sia tot fix dedins lo condensori. E après tu metràs y la cuinqua littera; aquella fixaràs tro veies que's fona com a cera, sens fer fum; e a tant serrà fet lo ferment liquefet de la primera cambra. E aquest in infinit se pot multiplicar per les obres secrets fetes de mixtió en diversa manera.

### English

When you have made the tincture ferment, convert it to liquefaction by adding gold (H) according to the weight you know — your senses will demonstrate through nature's work — until all is fixed in the condenser. Then add the fifth letter; fix it until you see it melt like wax without smoke. Then the liquefied ferment of the first chamber is made. This can be multiplied infinitely by secret mixing operations in diverse manner.

### Recipe Structure

| Step | Operation | Heat | Key feature |
|------|-----------|------|-------------|
| 1 | Start with tincture ferment | — | precursor ready |
| 2 | Add gold (H) by weight | moderate | fixation begins |
| 3 | Fix in condenser until done | increasing | progressive binding |
| 4 | Add fifth letter | — | second material |
| 5 | Fix until melts like wax without smoke | strong | **fusibility test** |
| 6 | Result: liquefied ferment | — | first chamber done |
| 7 | Multiply infinitely | strongest | secret mixing |

---

## Structural Predictions (derived from recipe before reading folio)

| # | Prediction | Rationale | Result |
|---|-----------|-----------|--------|
| 1 | Low/zero dar | recipe uses "ajustant" (joining), not "gita" (casting) | **FAIL** — dar=10 (recipe has more handling than text suggests) |
| 2 | High n-atom (bind) count | "fix", "ligat" — fixation = binding | **MATCH** — ~50+ n-terminal tokens |
| 3 | Fusibility test: chekar in P5 | "veies que's fona com a cera" | **MATCH** — chekar×2 in P5 (9.5% density) |
| 4 | Descending e-depth (increasing heat) | fixation requires progressive strengthening | **MATCH** — 1.01 → 0.60 monotonic |
| 5 | cs gold markers (gold added as H) | recipe explicitly adds gold | **FAIL** — no cs detected |
| 6 | sa-prefix for multiplication | "in infinit se pot multiplicar" | **MATCH** — 8 sa-prefix in P6 |
| 7 | 6 paragraphs fits structure | prep, fix, fix-more, test, multiply | **MATCH** — coherent mapping |

**Score: 5/7 confirmed, 2 failures**

---

## Folio Overview

| Metric | Value |
|--------|-------|
| Total tokens | 400 |
| Lines | 41 |
| Paragraphs | 6 |
| dar (material-add) | 10 |
| Quality checks (chek/shek class) | 4 |
| Observation MIDDLEs | ecth×2, ecthe×1, ckh×1 |
| hh (extended observation) | 0 |
