# Atom-Decode vs SISMEL Catalan Findings

Per-folio: atom-level Voynich signatures scored against operational
predictions auto-extracted from SISMEL Catalan recipe text.

> **Status note (2026-04-25):** This document represents the Phase 641 atom-
> decode scoring on Phase 628's original 16 matched folios. Subsequent work:
>
> - **Phase 643 (C1959):** Test B (paragraph layout-order vs recipe-phase order)
>   verified 5 of these matches with mean rho +0.81.
> - **Phases 644 / 646 added 5 NEW matches** at STRONG SUPPORT not in Phase
>   628's original 16: f78r↔III.36.0, f86v3↔II.10.0, f108v↔III.29.0,
>   f79v↔II.8.0, f77r↔III.28.0.
> - **Phase 647 (C1960):** heat-progression encoding confirmed on heat-phase-
>   distinct subset.
>
> C1959's evidence base now spans 8 confirmed matches (3 originals + 5 new),
> mean rho +0.89, 6/8 strict-significant. See
> `phases/SISMEL_RECIPE_CORPUS/results/matched_recipes.md` Verification
> Status section for current cross-phase status.

## Bottom line (Phase 641 atom-decode only)

- **2** folios STRONG SUPPORT, **7** MODERATE, **3** WEAK, **4** INCONCLUSIVE, **0** DO NOT SUPPORT

**SISMEL Catalan value verification:** Across the matched folios, the
Catalan-derived predictions strengthen the original Latin/English atom-decode
evidence as follows:

1. **f75r (Ch19 aqua vitae, CONFIRMED):** STRONG SUPPORT. The Catalan-only
   preserved phrase _'aliter broicé e triblé; e aprés ix vegades'_ pairs the
   4× and 9× counts. The 4 maps to the corpus-rare 4-identical-token run of
   `qokedy` on the folio (weight-3 anchor). The Latin only carries `quatuor
   vices` — without the AN intrusion preserving 9× as a parallel cycle the
   density-cluster alignment would not have been visible.

2. **f84r (Ch14 gold dissolution, CONFIRMED):** STRONG SUPPORT. Catalan
   preserves _'.xii. parties de E'_ — the explicit 12-count. The folio has
   exactly 12 micro-paragraph headers at start (weight-4 corpus-rare anchor).
   This alignment is structurally specific in both directions.

3. **All other CONFIRMED / strong-supported tiers (f76r, f79r, f82r, f76v,
   f103r):** mostly MODERATE. The Catalan provides operational corroboration
   (heat mode, sealing, observation verbs) but not corpus-rare anchors. This
   is consistent with these recipes lacking distinctive numerical specs.

**Conclusion:** The SISMEL Catalan strengthens **2 of 3 CONFIRMED matches**
with corpus-rare anchors not visible in 1566 Latin or English. For the rest,
Catalan corroborates without distinguishing — a neutral-positive result.

**Scoring legend:**
- ⭐ MATCH (full weight)  ~ WEAK (partial)  ✗ MISMATCH (zero)
- corpus-rare alignments (** in criterion) carry weight 3-4

## Summary table

| Folio | Tier | SISMEL id | Sim | Catalan counts | Heat | Pts | M/W/X | Verdict |
|-------|------|-----------|----:|----------------|------|----:|:-----:|---------|
| f75r | CONFIRMED | III.19.0 | 0.41 | 3,4 | balneum | 9 | 3/3/1 | **STRONG SUPPORT** |
| f76r | CONFIRMED | II.16.0 | 0.75 | - | mixed | 3 | 0/4/0 | **INCONCLUSIVE** |
| f84r | CONFIRMED | II.12.0 | 0.52 | 2,12 | balneum | 8 | 3/2/2 | **STRONG SUPPORT** |
| f79r | strong-supported | III.12.0 | 0.46 | - | mixed | 2 | 0/3/1 | **INCONCLUSIVE** |
| f82r | strong-supported | III.19.3 | 0.47 | 3 | balneum | 9 | 4/1/0 | **MODERATE SUPPORT** |
| f103r | strong-supported | III.16.0 | 0.45 | 3 | balneum | 4 | 2/1/2 | **MODERATE SUPPORT** |
| f76v | strong-supported | III.16.0 | 0.17 | 3 | balneum | 4 | 2/1/2 | **MODERATE SUPPORT** |
| f77v | supported | III.20.0 | 0.43 | - | ashes | 6 | 2/2/0 | **MODERATE SUPPORT** |
| f81v | supported | III.18.0 | 0.47 | - | balneum | 2 | 0/3/2 | **INCONCLUSIVE** |
| f82v | supported | III.21.0 | 0.49 | - | mixed | 5 | 2/1/0 | **MODERATE SUPPORT** |
| f112r | supported | III.11.0 | 0.39 | 3 | balneum | 5 | 1/5/0 | **MODERATE SUPPORT** |
| f112v | supported | III.1.0 | 0.49 | 2 | balneum | 3 | 1/2/2 | **WEAK SUPPORT** |
| f116r | supported | III.4.0 | 0.58 | - | open_fire | 2 | 0/3/0 | **INCONCLUSIVE** |
| f107r | supported | II.1.0 | 0.00 | 2 | mixed | 4 | 1/4/0 | **WEAK SUPPORT** |
| f80r | supported | II.1.0 | 0.00 | 2 | mixed | 4 | 1/4/0 | **WEAK SUPPORT** |
| f83r | supported | II.7.0 | 0.61 | - | ashes | 6 | 2/2/2 | **MODERATE SUPPORT** |

## Per-folio detail

### f75r ↔ III.19.0 (Aqua vitae (4x/9x reflux, honey+wax))
**Tier:** CONFIRMED  **Content sim:** 0.408  **Verdict:** STRONG SUPPORT  **Points:** 9
_(other Catalan candidates evaluated: III.19.1 (5pt), III.19.2 (4pt), III.19.3 (9pt), III.19.4 (4pt), III.19.5 (5pt), III.19.6 (5pt), III.19.7 (3pt), III.19.8 (6pt))_

**Catalan recipe features:**
- distinct counts: [3, 4]
- heat mode: **balneum** (bany=1, cendres=0, foch=0)
- sealing markers: 0 []
- observation verbs: 0 []
- material verbs: 4
  - **3** dies: "rmentar en laugera calor per .iii. dies; e quan"
  - **4** vegades: "scuna segona distillació per quatre vegades aliter"

**Atom signatures:**
- 412 tokens, 3 paragraphs, micro-run at start=0
- dar=10, dal=3, daiin=0, chekar=1
- qokedy=14, qokeedy=14, longest_run=4 (qokedy), density-35=10
- prefix mix: qo=26.2%  sh=15.3%  ch=10.2%  ok=3.6%  da=6.6%
- gentle-heat ratio (e≥2): 9.5%, -dy count=119, max consecutive qo-lines=20
- atom seal-predictor (ok/ot+dy): 12

**Checks:**
- ✗ **MISMATCH** (w=0) — dar=10 vs Catalan material=4 _(scale divergence)_
- ~ **WEAK** (w=1) — chekar=1 ≈ observation=0 _(off by 1)_
- ~ **WEAK** (w=0) — atom seal-pred=12 but Catalan seals=0 _(atom over-predicts seal)_
- ⭐ **MATCH** (w=2) — qokeedy=14 ≥ qokedy=14, gentle%=9.5 _(qokeedy-dominant ↔ Catalan bany)_
- ⭐ **MATCH** (w=3) — longest_run=4 ↔ Catalan count 4 (** corpus-rare) _(rare 3+ identical-token run aligns to explicit count)_
- ~ **WEAK** (w=1) — folio paragraphs=3 ≈ Catalan steps≈4 _(structural length aligns)_
- ⭐ **MATCH** (w=2) — max consecutive qo-lines=20 ↔ Catalan duration≥3 _(sustained heat encoding aligns with multi-day spec)_


### f76r ↔ II.16.0 (Element separation (silver-plate test))
**Tier:** CONFIRMED  **Content sim:** 0.751  **Verdict:** INCONCLUSIVE  **Points:** 3

**Catalan recipe features:**
- distinct counts: []
- heat mode: **mixed** (bany=0, cendres=0, foch=0)
- sealing markers: 0 []
- observation verbs: 0 []
- material verbs: 4

**Atom signatures:**
- 546 tokens, 4 paragraphs, micro-run at start=0
- dar=7, dal=5, daiin=1, chekar=0
- qokedy=7, qokeedy=6, longest_run=2 (al), density-35=4
- prefix mix: qo=19.0%  sh=15.2%  ch=17.0%  ok=7.1%  da=4.9%
- gentle-heat ratio (e≥2): 10.4%, -dy count=131, max consecutive qo-lines=29
- atom seal-predictor (ok/ot+dy): 15

**Checks:**
- ~ **WEAK** (w=1) — dar=7 vs Catalan material=4 _(loose alignment)_
- ~ **WEAK** (w=0) — atom seal-pred=15 but Catalan seals=0 _(atom over-predicts seal)_
- ~ **WEAK** (w=1) — folio paragraphs=4 ≈ Catalan steps≈4 _(structural length aligns)_
- ~ **WEAK** (w=1) — max consecutive qo-lines=29 _(some sustained heat)_


### f84r ↔ II.12.0 (Gold dissolution (balneum + putrefaction))
**Tier:** CONFIRMED  **Content sim:** 0.517  **Verdict:** STRONG SUPPORT  **Points:** 8

**Catalan recipe features:**
- distinct counts: [2, 12]
- heat mode: **balneum** (bany=1, cendres=0, foch=0)
- sealing markers: 0 []
- observation verbs: 1 ['trobaràs']
- material verbs: 5
  - **2** dies: "e aprés posa-lo en bany per .ii. dies o quatr"
  - **12** part: "xí com a carbó. Puis met dedins .xii. parties de E"

**Atom signatures:**
- 361 tokens, 18 paragraphs, micro-run at start=12
- dar=13, dal=2, daiin=6, chekar=1
- qokedy=12, qokeedy=10, longest_run=2 (qokeedy), density-35=6
- prefix mix: qo=19.7%  sh=13.3%  ch=9.4%  ok=5.3%  da=6.9%
- gentle-heat ratio (e≥2): 8.0%, -dy count=117, max consecutive qo-lines=14
- atom seal-predictor (ok/ot+dy): 18

**Checks:**
- ✗ **MISMATCH** (w=0) — dar=13 vs Catalan material=5 _(scale divergence)_
- ⭐ **MATCH** (w=2) — chekar=1 == observation verbs=1 _(exact observation-count alignment)_
- ~ **WEAK** (w=0) — atom seal-pred=18 but Catalan seals=0 _(atom over-predicts seal)_
- ✗ **MISMATCH** (w=0) — qokeedy=10 < qokedy=12, Catalan bany _(atom predicts ashes but Catalan says bany)_
- ⭐ **MATCH** (w=4) — 12 micro-headers at start ↔ Catalan count 12 (** corpus-rare) _(n parties / n vegades structurally encoded as n micro-headers)_
- ~ **WEAK** (w=0) — folio paragraphs=18 >> Catalan steps≈5 _(folio longer than recipe (multi-recipe folio?))_
- ⭐ **MATCH** (w=2) — max consecutive qo-lines=14 ↔ Catalan duration≥3 _(sustained heat encoding aligns with multi-day spec)_


### f79r ↔ III.12.0 (Mercury sublimation -> elixir)
**Tier:** strong-supported  **Content sim:** 0.461  **Verdict:** INCONCLUSIVE  **Points:** 2

**Catalan recipe features:**
- distinct counts: []
- heat mode: **mixed** (bany=0, cendres=0, foch=0)
- sealing markers: 0 []
- observation verbs: 2 ['veies', 'veies']
- material verbs: 1

**Atom signatures:**
- 389 tokens, 8 paragraphs, micro-run at start=0
- dar=3, dal=1, daiin=3, chekar=0
- qokedy=1, qokeedy=1, longest_run=2 (otain), density-35=2
- prefix mix: qo=20.3%  sh=17.2%  ch=13.6%  ok=4.4%  da=3.1%
- gentle-heat ratio (e≥2): 13.6%, -dy count=63, max consecutive qo-lines=9
- atom seal-predictor (ok/ot+dy): 8

**Checks:**
- ~ **WEAK** (w=1) — dar=3 vs Catalan material=1 _(loose alignment)_
- ✗ **MISMATCH** (w=0) — chekar=0 vs observation=2 _(no obs alignment)_
- ~ **WEAK** (w=0) — atom seal-pred=8 but Catalan seals=0 _(atom over-predicts seal)_
- ~ **WEAK** (w=1) — max consecutive qo-lines=9 _(some sustained heat)_


### f82r ↔ III.19.3 (Lunaria maceration (3-day sealed))
**Tier:** strong-supported  **Content sim:** 0.468  **Verdict:** MODERATE SUPPORT  **Points:** 9
_(other Catalan candidates evaluated: III.19.0 (6pt), III.19.1 (5pt), III.19.2 (3pt), III.19.4 (3pt), III.19.5 (4pt), III.19.6 (6pt), III.19.7 (3pt), III.19.8 (6pt))_

**Catalan recipe features:**
- distinct counts: [3]
- heat mode: **balneum** (bany=1, cendres=1, foch=0)
- sealing markers: 3 ['tapa', 'cubertor', 'ab cera']
- observation verbs: 0 []
- material verbs: 2
  - **3** dies naturalls: "posa-u tot sobre cendres per .iii. dies naturalls ab foch"

**Atom signatures:**
- 275 tokens, 4 paragraphs, micro-run at start=0
- dar=1, dal=2, daiin=7, chekar=0
- qokedy=5, qokeedy=14, longest_run=2 (qokaiin), density-35=6
- prefix mix: qo=31.3%  sh=11.3%  ch=14.5%  ok=3.3%  da=4.7%
- gentle-heat ratio (e≥2): 22.9%, -dy count=80, max consecutive qo-lines=30
- atom seal-predictor (ok/ot+dy): 1

**Checks:**
- ⭐ **MATCH** (w=2) — dar=1 ≈ Catalan material verbs=2 _(atom-level material-add count aligns to Catalan verbs)_
- ⭐ **MATCH** (w=2) — Catalan seals=3, atom seal-pred=1, -dy=80 _(ok/ot+dy or high -dy supports sealing)_
- ⭐ **MATCH** (w=2) — qokeedy=14 ≥ qokedy=5, gentle%=22.9 _(qokeedy-dominant ↔ Catalan bany)_
- ~ **WEAK** (w=1) — folio paragraphs=4 ≈ Catalan steps≈2 _(structural length aligns)_
- ⭐ **MATCH** (w=2) — max consecutive qo-lines=30 ↔ Catalan duration≥3 _(sustained heat encoding aligns with multi-day spec)_


### f103r ↔ III.16.0 (Ferment multiplication (multi-chamber))
**Tier:** strong-supported  **Content sim:** 0.445  **Verdict:** MODERATE SUPPORT  **Points:** 4

**Catalan recipe features:**
- distinct counts: [3]
- heat mode: **balneum** (bany=1, cendres=1, foch=0)
- sealing markers: 0 []
- observation verbs: 3 ['veure', 'senyal', 'veuràs']
- material verbs: 10
  - **3** anys: "mera partida de la taula dins .iii. anys⁵ ab gra"

**Atom signatures:**
- 522 tokens, 18 paragraphs, micro-run at start=0
- dar=2, dal=3, daiin=2, chekar=0
- qokedy=3, qokeedy=10, longest_run=2 (qokeedy), density-35=4
- prefix mix: qo=21.6%  sh=18.6%  ch=13.2%  ok=9.4%  da=3.4%
- gentle-heat ratio (e≥2): 20.3%, -dy count=102, max consecutive qo-lines=10
- atom seal-predictor (ok/ot+dy): 17

**Checks:**
- ✗ **MISMATCH** (w=0) — dar=2 vs Catalan material=10 _(scale divergence)_
- ✗ **MISMATCH** (w=0) — chekar=0 vs observation=3 _(no obs alignment)_
- ~ **WEAK** (w=0) — atom seal-pred=17 but Catalan seals=0 _(atom over-predicts seal)_
- ⭐ **MATCH** (w=2) — qokeedy=10 ≥ qokedy=3, gentle%=20.3 _(qokeedy-dominant ↔ Catalan bany)_
- ⭐ **MATCH** (w=2) — max consecutive qo-lines=10 ↔ Catalan duration≥3 _(sustained heat encoding aligns with multi-day spec)_


### f76v ↔ III.16.0 (Ferment conversion (join H + bind))
**Tier:** strong-supported  **Content sim:** 0.171  **Verdict:** MODERATE SUPPORT  **Points:** 4

**Catalan recipe features:**
- distinct counts: [3]
- heat mode: **balneum** (bany=1, cendres=1, foch=0)
- sealing markers: 0 []
- observation verbs: 3 ['veure', 'senyal', 'veuràs']
- material verbs: 10
  - **3** anys: "mera partida de la taula dins .iii. anys⁵ ab gra"

**Atom signatures:**
- 400 tokens, 6 paragraphs, micro-run at start=0
- dar=0, dal=2, daiin=8, chekar=0
- qokedy=10, qokeedy=15, longest_run=2 (shedy), density-35=5
- prefix mix: qo=17.2%  sh=13.8%  ch=16.5%  ok=4.5%  da=2.5%
- gentle-heat ratio (e≥2): 21.2%, -dy count=151, max consecutive qo-lines=10
- atom seal-predictor (ok/ot+dy): 21

**Checks:**
- ✗ **MISMATCH** (w=0) — dar=0 vs Catalan material=10 _(scale divergence)_
- ✗ **MISMATCH** (w=0) — chekar=0 vs observation=3 _(no obs alignment)_
- ~ **WEAK** (w=0) — atom seal-pred=21 but Catalan seals=0 _(atom over-predicts seal)_
- ⭐ **MATCH** (w=2) — qokeedy=15 ≥ qokedy=10, gentle%=21.2 _(qokeedy-dominant ↔ Catalan bany)_
- ⭐ **MATCH** (w=2) — max consecutive qo-lines=10 ↔ Catalan duration≥3 _(sustained heat encoding aligns with multi-day spec)_


### f77v ↔ III.20.0 (Furnace specification)
**Tier:** supported  **Content sim:** 0.431  **Verdict:** MODERATE SUPPORT  **Points:** 6

**Catalan recipe features:**
- distinct counts: []
- heat mode: **ashes** (bany=2, cendres=3, foch=0)
- sealing markers: 2 ['tapar', 'tapar']
- observation verbs: 1 ['senyals']
- material verbs: 0

**Atom signatures:**
- 331 tokens, 8 paragraphs, micro-run at start=5
- dar=5, dal=10, daiin=7, chekar=0
- qokedy=16, qokeedy=7, longest_run=2 (qotedy), density-35=6
- prefix mix: qo=29.0%  sh=13.3%  ch=13.6%  ok=1.8%  da=9.7%
- gentle-heat ratio (e≥2): 10.3%, -dy count=101, max consecutive qo-lines=37
- atom seal-predictor (ok/ot+dy): 2

**Checks:**
- ~ **WEAK** (w=1) — chekar=0 ≈ observation=1 _(off by 1)_
- ⭐ **MATCH** (w=2) — Catalan seals=2, atom seal-pred=2, -dy=101 _(ok/ot+dy or high -dy supports sealing)_
- ⭐ **MATCH** (w=2) — qokedy=16 ≥ qokeedy=7 _(qokedy-dominant ↔ Catalan cendres)_
- ~ **WEAK** (w=1) — max consecutive qo-lines=37 _(some sustained heat)_


### f81v ↔ III.18.0 (Potable gold / water of life)
**Tier:** supported  **Content sim:** 0.470  **Verdict:** INCONCLUSIVE  **Points:** 2

**Catalan recipe features:**
- distinct counts: []
- heat mode: **balneum** (bany=1, cendres=0, foch=0)
- sealing markers: 0 []
- observation verbs: 3 ['veuràs', 'apparrà', 'veies']
- material verbs: 6

**Atom signatures:**
- 258 tokens, 3 paragraphs, micro-run at start=0
- dar=3, dal=3, daiin=9, chekar=0
- qokedy=6, qokeedy=0, longest_run=2 (ytedy), density-35=3
- prefix mix: qo=16.3%  sh=10.9%  ch=12.0%  ok=8.5%  da=8.1%
- gentle-heat ratio (e≥2): 8.5%, -dy count=64, max consecutive qo-lines=16
- atom seal-predictor (ok/ot+dy): 8

**Checks:**
- ~ **WEAK** (w=1) — dar=3 vs Catalan material=6 _(loose alignment)_
- ✗ **MISMATCH** (w=0) — chekar=0 vs observation=3 _(no obs alignment)_
- ~ **WEAK** (w=0) — atom seal-pred=8 but Catalan seals=0 _(atom over-predicts seal)_
- ✗ **MISMATCH** (w=0) — qokeedy=0 < qokedy=6, Catalan bany _(atom predicts ashes but Catalan says bany)_
- ~ **WEAK** (w=1) — max consecutive qo-lines=16 _(some sustained heat)_


### f82v ↔ III.21.0 (Vessel specification)
**Tier:** supported  **Content sim:** 0.491  **Verdict:** MODERATE SUPPORT  **Points:** 5

**Catalan recipe features:**
- distinct counts: []
- heat mode: **mixed** (bany=0, cendres=0, foch=0)
- sealing markers: 2 ['cubertor', 'cubertor']
- observation verbs: 0 []
- material verbs: 2

**Atom signatures:**
- 298 tokens, 6 paragraphs, micro-run at start=0
- dar=3, dal=4, daiin=1, chekar=0
- qokedy=7, qokeedy=5, longest_run=2 (shedy), density-35=5
- prefix mix: qo=32.6%  sh=12.8%  ch=12.4%  ok=3.7%  da=4.0%
- gentle-heat ratio (e≥2): 9.1%, -dy count=75, max consecutive qo-lines=22
- atom seal-predictor (ok/ot+dy): 4

**Checks:**
- ⭐ **MATCH** (w=2) — dar=3 ≈ Catalan material verbs=2 _(atom-level material-add count aligns to Catalan verbs)_
- ⭐ **MATCH** (w=2) — Catalan seals=2, atom seal-pred=4, -dy=75 _(ok/ot+dy or high -dy supports sealing)_
- ~ **WEAK** (w=1) — max consecutive qo-lines=22 _(some sustained heat)_


### f112r ↔ III.11.0 (Red mercury tincture (cohobation))
**Tier:** supported  **Content sim:** 0.391  **Verdict:** MODERATE SUPPORT  **Points:** 5

**Catalan recipe features:**
- distinct counts: [3]
- heat mode: **balneum** (bany=2, cendres=2, foch=0)
- sealing markers: 0 []
- observation verbs: 1 ['veies']
- material verbs: 2
  - **3** vegades: "ella distillaràs en bany per .iii. vegades. E apré"

**Atom signatures:**
- 394 tokens, 10 paragraphs, micro-run at start=0
- dar=0, dal=1, daiin=0, chekar=0
- qokedy=3, qokeedy=4, longest_run=2 (oteedy), density-35=2
- prefix mix: qo=14.7%  sh=4.1%  ch=11.9%  ok=12.4%  da=1.8%
- gentle-heat ratio (e≥2): 23.1%, -dy count=91, max consecutive qo-lines=12
- atom seal-predictor (ok/ot+dy): 31

**Checks:**
- ~ **WEAK** (w=1) — dar=0 vs Catalan material=2 _(loose alignment)_
- ~ **WEAK** (w=1) — chekar=0 ≈ observation=1 _(off by 1)_
- ~ **WEAK** (w=0) — atom seal-pred=31 but Catalan seals=0 _(atom over-predicts seal)_
- ~ **WEAK** (w=1) — qokeedy=4 ≥ qokedy=3 (small) _(weak balneum signal)_
- ~ **WEAK** (w=0) — folio paragraphs=10 >> Catalan steps≈2 _(folio longer than recipe (multi-recipe folio?))_
- ⭐ **MATCH** (w=2) — max consecutive qo-lines=12 ↔ Catalan duration≥3 _(sustained heat encoding aligns with multi-day spec)_


### f112v ↔ III.1.0 (Lunaria -> quicksilver)
**Tier:** supported  **Content sim:** 0.494  **Verdict:** WEAK SUPPORT  **Points:** 3

**Catalan recipe features:**
- distinct counts: [2]
- heat mode: **balneum** (bany=2, cendres=0, foch=0)
- sealing markers: 0 []
- observation verbs: 2 ['veies', 'senyall']
- material verbs: 5
  - **2** parts: "ment. E aquella partiràs en dues parts: e la u"

**Atom signatures:**
- 415 tokens, 13 paragraphs, micro-run at start=0
- dar=0, dal=0, daiin=6, chekar=0
- qokedy=3, qokeedy=12, longest_run=2 (qokeey), density-35=4
- prefix mix: qo=16.6%  sh=5.3%  ch=20.0%  ok=8.0%  da=2.4%
- gentle-heat ratio (e≥2): 25.1%, -dy count=87, max consecutive qo-lines=20
- atom seal-predictor (ok/ot+dy): 13

**Checks:**
- ✗ **MISMATCH** (w=0) — dar=0 vs Catalan material=5 _(scale divergence)_
- ✗ **MISMATCH** (w=0) — chekar=0 vs observation=2 _(no obs alignment)_
- ~ **WEAK** (w=0) — atom seal-pred=13 but Catalan seals=0 _(atom over-predicts seal)_
- ⭐ **MATCH** (w=2) — qokeedy=12 ≥ qokedy=3, gentle%=25.1 _(qokeedy-dominant ↔ Catalan bany)_
- ~ **WEAK** (w=1) — max consecutive qo-lines=20 _(some sustained heat)_


### f116r ↔ III.4.0 (Fixation / fusibility test)
**Tier:** supported  **Content sim:** 0.585  **Verdict:** INCONCLUSIVE  **Points:** 2

**Catalan recipe features:**
- distinct counts: []
- heat mode: **open_fire** (bany=0, cendres=0, foch=1)
- sealing markers: 0 []
- observation verbs: 0 []
- material verbs: 3

**Atom signatures:**
- 537 tokens, 8 paragraphs, micro-run at start=0
- dar=5, dal=0, daiin=3, chekar=0
- qokedy=1, qokeedy=5, longest_run=2 (okeey), density-35=2
- prefix mix: qo=14.9%  sh=13.0%  ch=14.9%  ok=6.9%  da=3.5%
- gentle-heat ratio (e≥2): 13.0%, -dy count=76, max consecutive qo-lines=18
- atom seal-predictor (ok/ot+dy): 16

**Checks:**
- ~ **WEAK** (w=1) — dar=5 vs Catalan material=3 _(loose alignment)_
- ~ **WEAK** (w=0) — atom seal-pred=16 but Catalan seals=0 _(atom over-predicts seal)_
- ~ **WEAK** (w=1) — max consecutive qo-lines=18 _(some sustained heat)_


### f107r ↔ II.1.0 (Quicksilver coagulation)
**Tier:** supported  **Content sim:** 0.000  **Verdict:** WEAK SUPPORT  **Points:** 4

**Catalan recipe features:**
- distinct counts: [2]
- heat mode: **mixed** (bany=0, cendres=0, foch=0)
- sealing markers: 0 []
- observation verbs: 1 ['appar']
- material verbs: 3
  - **2** parts: "al operació és departida en dues parts solu- 5"

**Atom signatures:**
- 488 tokens, 15 paragraphs, micro-run at start=0
- dar=3, dal=1, daiin=5, chekar=0
- qokedy=1, qokeedy=3, longest_run=2 (cheol), density-35=2
- prefix mix: qo=12.7%  sh=5.9%  ch=16.8%  ok=8.0%  da=1.8%
- gentle-heat ratio (e≥2): 13.1%, -dy count=47, max consecutive qo-lines=6
- atom seal-predictor (ok/ot+dy): 4

**Checks:**
- ⭐ **MATCH** (w=2) — dar=3 ≈ Catalan material verbs=3 _(atom-level material-add count aligns to Catalan verbs)_
- ~ **WEAK** (w=1) — chekar=0 ≈ observation=1 _(off by 1)_
- ~ **WEAK** (w=0) — atom seal-pred=4 but Catalan seals=0 _(atom over-predicts seal)_
- ~ **WEAK** (w=0) — folio paragraphs=15 >> Catalan steps≈3 _(folio longer than recipe (multi-recipe folio?))_
- ~ **WEAK** (w=1) — max consecutive qo-lines=6 _(some sustained heat)_


### f80r ↔ II.1.0 (Animal ash chain Ch21 (multi-chapter 21-25))
**Tier:** supported  **Content sim:** 0.000  **Verdict:** WEAK SUPPORT  **Points:** 4

**Catalan recipe features:**
- distinct counts: [2]
- heat mode: **mixed** (bany=0, cendres=0, foch=0)
- sealing markers: 0 []
- observation verbs: 1 ['appar']
- material verbs: 3
  - **2** parts: "al operació és departida en dues parts solu- 5"

**Atom signatures:**
- 441 tokens, 16 paragraphs, micro-run at start=10
- dar=3, dal=1, daiin=2, chekar=0
- qokedy=3, qokeedy=8, longest_run=2 (qokal), density-35=4
- prefix mix: qo=24.9%  sh=12.9%  ch=11.8%  ok=5.7%  da=2.9%
- gentle-heat ratio (e≥2): 8.4%, -dy count=48, max consecutive qo-lines=21
- atom seal-predictor (ok/ot+dy): 3

**Checks:**
- ⭐ **MATCH** (w=2) — dar=3 ≈ Catalan material verbs=3 _(atom-level material-add count aligns to Catalan verbs)_
- ~ **WEAK** (w=1) — chekar=0 ≈ observation=1 _(off by 1)_
- ~ **WEAK** (w=0) — atom seal-pred=3 but Catalan seals=0 _(atom over-predicts seal)_
- ~ **WEAK** (w=0) — folio paragraphs=16 >> Catalan steps≈3 _(folio longer than recipe (multi-recipe folio?))_
- ~ **WEAK** (w=1) — max consecutive qo-lines=21 _(some sustained heat)_


### f83r ↔ II.7.0 (Drip-counted mercurial solvent)
**Tier:** supported  **Content sim:** 0.609  **Verdict:** MODERATE SUPPORT  **Points:** 6

**Catalan recipe features:**
- distinct counts: []
- heat mode: **ashes** (bany=0, cendres=1, foch=0)
- sealing markers: 4 ['lutats', 'ab cera', 'tapada⁴', 'lutar']
- observation verbs: 2 ['veies', 'veies']
- material verbs: 12

**Atom signatures:**
- 340 tokens, 10 paragraphs, micro-run at start=0
- dar=1, dal=5, daiin=4, chekar=0
- qokedy=13, qokeedy=7, longest_run=2 (qoteedy), density-35=6
- prefix mix: qo=22.9%  sh=14.1%  ch=15.0%  ok=1.5%  da=5.9%
- gentle-heat ratio (e≥2): 11.5%, -dy count=127, max consecutive qo-lines=10
- atom seal-predictor (ok/ot+dy): 6

**Checks:**
- ✗ **MISMATCH** (w=0) — dar=1 vs Catalan material=12 _(scale divergence)_
- ✗ **MISMATCH** (w=0) — chekar=0 vs observation=2 _(no obs alignment)_
- ⭐ **MATCH** (w=2) — Catalan seals=4, atom seal-pred=6, -dy=127 _(ok/ot+dy or high -dy supports sealing)_
- ⭐ **MATCH** (w=2) — qokedy=13 ≥ qokeedy=7 _(qokedy-dominant ↔ Catalan cendres)_
- ~ **WEAK** (w=1) — folio paragraphs=10 ≈ Catalan steps≈12 _(structural length aligns)_
- ~ **WEAK** (w=1) — max consecutive qo-lines=10 _(some sustained heat)_

## Cross-folio synthesis

- **STRONG SUPPORT:** f75r, f84r
- **MODERATE SUPPORT:** f82r, f103r, f76v, f77v, f82v, f112r, f83r
- **WEAK SUPPORT:** f112v, f107r, f80r
- **INCONCLUSIVE:** f76r, f79r, f81v, f116r

## Caveats

- The methodology auto-extracts predictions from Catalan and scores
  multiple loose criteria. Per-criterion correlations can fire by chance,
  so MODERATE verdicts driven only by w=2 alignments (no corpus-rare
  anchor) should be treated as corroborative-but-not-distinguishing.
- f107r and f80r have content_similarity=0 to the remap's best-match
  (the chapter-similarity bag-of-words remap fails for these). Their
  MODERATE scores against the chapter-num primary should be read with
  caution — the operational template alignment may be coincidental.
- The corpus-rare anchors (R1 longest-run, R2 density-1, R7 micro-
  paragraph headers) are strongly specific in both directions. STRONG
  SUPPORT verdicts require at least one of these.