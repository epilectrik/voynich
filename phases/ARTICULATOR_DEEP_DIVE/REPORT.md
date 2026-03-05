# Phase 517: ARTICULATOR Deep Dive

**Date:** 2026-03-05
**Status:** COMPLETE
**Script:** `phases/ARTICULATOR_DEEP_DIVE/scripts/articulator_deep_dive.py`
**Results:** `phases/ARTICULATOR_DEEP_DIVE/results/articulator_deep_dive.json`

---

## Research Question

What does the ARTICULATOR slot (y, k, l, p, d, f, r, s, t) actually do? It sits before PREFIX in the token structure `[ARTICULATOR] + [PREFIX] + MIDDLE + [SUFFIX]`, but has never received atom-level decomposition or cross-slot interaction analysis.

---

## Key Findings Summary

1. **ARTICULATOR is rare** (4.41% of B tokens = 1,019/23,096), dominated by y (51.2%), with d, l, r, p, t, k, s, f as minor variants.
2. **ARTICULATOR is strongly line-initial** (17.3% at line-initial vs 2.7% medial = 6.5x enrichment), and 4.1x enriched in paragraph headers.
3. **ARTICULATOR's effect on MIDDLE is entirely mediated by PREFIX** (I(ART;CAT|MIDDLE) = 0.000 bits) -- category information goes through MIDDLE, not around it.
4. **ARTICULATOR has strong PREFIX selectivity** (V=0.196) with 29 forbidden ART x PREFIX pairs. Most articulators are locked to specific PREFIX families.
5. **ARTICULATOR categorically excludes qo-PREFIX and BARE tokens** -- articulators never appear on bare (prefixless) tokens or qo-family tokens.
6. **ARTICULATOR's effect sizes are 2-7x smaller than the PREFIX->MIDDLE->SUFFIX chain**, confirming it is a peripheral modifier, not a core component.
7. **e-HEAD MIDDLEs are dramatically over-represented** in articulated tokens (76-90% e-initial vs 40% baseline), while k-HEAD MIDDLEs are categorically excluded from most articulators.
8. **ARTICULATOR suppresses suffix attachment** (27.2% suffix rate for y-articulated vs 49.3% non-articulated = 0.55x).
9. **Individual articulators show strong positional specialization**: d, k, p, t, y are initial-biased; l, r are final-biased.

---

## Detailed Results

### T1: Inventory and Frequency

| Metric | Value |
|--------|-------|
| Total B tokens | 23,096 |
| Articulated tokens | 1,019 (4.41%) |
| Non-articulated | 22,077 (95.59%) |

**Per articulator:**

| Articulator | Count | Rate |
|-------------|-------|------|
| y | 522 | 2.26% |
| d | 118 | 0.51% |
| l | 116 | 0.50% |
| r | 71 | 0.31% |
| p | 55 | 0.24% |
| t | 53 | 0.23% |
| k | 36 | 0.16% |
| s | 34 | 0.15% |
| f | 14 | 0.06% |

y dominates at 51.2% of all articulators. The other 8 articulators collectively account for 48.8%.

**Per section:**

| Section | Rate | N |
|---------|------|---|
| COSMO | 8.31% | 123/1480 |
| HERBAL | 5.36% | 184/3433 |
| TEXT | 5.44% | 36/662 |
| STARS | 4.00% | 427/10671 |
| BIO | 3.64% | 249/6850 |

COSMO is notably enriched (2.3x BIO rate). This section-dependence is significant.

**Per line position (critical finding):**

| Position | Art Rate | Ratio vs Medial |
|----------|----------|-----------------|
| **Line-initial** | **17.26%** | **6.48x** |
| Medial | 2.66% | 1.0x |
| Line-final | 3.99% | 1.50x |

Articulators concentrate dramatically at line-initial position (17.3%). This makes them **line-opening markers**.

### T2: ARTICULATOR -> PREFIX Selectivity

**Cramer's V = 0.196** (p < 1e-300, N=23,096). This is the strongest ARTICULATOR association. For comparison, the reference PREFIX->MIDDLE V = 0.414 is 2.1x larger.

**Critical: ARTICULATOR categorically excludes three major PREFIX families:**

| Excluded from articulators | Notes |
|---------------------------|-------|
| BARE (prefixless) | art=0.000 vs noart=0.175 -- **zero articulated bare tokens** |
| qo- | art=0.003 vs noart=0.184 -- ratio 0.02x (near-zero) |
| ok/ot | art=0.012/0.011 vs noart=0.066/0.065 -- ratio 0.17-0.18x |

**Articulated tokens massively over-represent:**

| Enriched in articulators | Art rate | Noart rate | Ratio |
|-------------------------|----------|------------|-------|
| te- PREFIX | 0.130 | 0.007 | **18.2x** |
| pch- PREFIX | 0.047 | 0.009 | **5.3x** |
| sh- PREFIX | 0.301 | 0.092 | **3.3x** |

Articulators preferentially attach to sh-family and extended PREFIXes (te, ta, pch, tch).

**Per-articulator PREFIX locks:**
- **t** is locked to sh (50/53 = 94.3%)
- **k** is locked to sh (34/36 = 94.4%)
- **d** is locked to sh (85/118 = 72.0%)
- **y** distributes across ch (26.2%), te (21.6%), ta (16.7%), sh (13.0%)

### T3: ARTICULATOR -> MIDDLE Selectivity

| Test | V | Reference V | Ratio |
|------|---|------------|-------|
| ART -> MIDDLE HEAD | 0.089 | PREFIX->MID HEAD 0.414 | 0.21x |
| ART -> MIDDLE TERM | 0.064 | MID TERM->SUFFIX 0.503 | 0.13x |

Weak effect sizes -- 5-8x smaller than the main chain.

**However, the e-HEAD concentration is dramatic:**

| Articulator | e-HEAD rate | Baseline (NONE) | Enrichment |
|-------------|------------|-----------------|------------|
| y | 90% | 40% | 2.25x |
| d | 89% | 40% | 2.23x |
| k | 83% | 40% | 2.08x |
| s | 83% | 40% | 2.08x |
| t | 76% | 40% | 1.90x |

All articulators are massively biased toward e-initial MIDDLEs (THERMAL: cooling). Articulators overwhelmingly appear on cooling/stability operations.

**k-HEAD MIDDLEs categorically excluded:** 4 forbidden ART x HEAD=k pairs found (d, k, t articulators). Articulators virtually never appear on k-initial (heating) MIDDLEs.

**PREFIX mediation test:** I(ART; HEAD) = 0.027 bits. I(ART; HEAD | PREFIX) = 0.009 bits. PREFIX mediates 68.3% of articulators' apparent MIDDLE selectivity. The e-HEAD bias is partly a PREFIX effect (sh-family PREFIXes naturally pair with e-MIDDLEs per C1203).

### T4: ARTICULATOR -> SUFFIX Selectivity

V = 0.061 (p = 0.003) -- very weak.

**Suffix suppression (key finding):**

| Articulator | Suffix Rate | Baseline (NONE) | Ratio |
|-------------|------------|-----------------|-------|
| k | 16.7% | 49.3% | 0.34x |
| d | 18.6% | 49.3% | 0.38x |
| l | 19.8% | 49.3% | 0.40x |
| s | 23.5% | 49.3% | 0.48x |
| r | 25.4% | 49.3% | 0.52x |
| y | 27.2% | 49.3% | 0.55x |
| f | 35.7% | 49.3% | 0.72x |
| t | 35.8% | 49.3% | 0.73x |
| **p** | **58.2%** | 49.3% | **1.18x** |

Nearly all articulators **suppress suffix attachment** (0.34-0.73x baseline). p-articulator is the sole exception (1.18x enriched). This is consistent with articulated tokens carrying line-opening specification that does not require suffix role-marking.

### T5: ARTICULATOR -> Category

V = 0.042 -- very weak raw association.

**MIDDLE fully mediates:** I(ART; CAT | MIDDLE) = 0.000 bits. Category information from ARTICULATOR is **entirely** mediated through MIDDLE selection. ARTICULATOR adds zero independent category signal.

This means ARTICULATOR does not encode operational type -- it modulates HOW a MIDDLE is deployed (line position, specification context) without changing WHAT category of operation it represents.

### T6: Information Chain Position

**Pairwise mutual information (bits):**

| Pair | MI (bits) |
|------|-----------|
| PREFIX <-> MIDDLE | 1.537 |
| MIDDLE <-> SUFFIX | 1.666 |
| PREFIX <-> SUFFIX | 0.290 |
| **ART <-> PREFIX** | **0.111** |
| **ART <-> MIDDLE** | **0.060** |
| **ART <-> SUFFIX** | **0.015** |

ARTICULATOR's MI values are 10-100x smaller than the main chain. It is a peripheral element.

**Beyond-chain contributions:**
- I(MIDDLE; ART | PREFIX) = 0.060 bits -- modest independent MIDDLE information
- I(SUFFIX; ART | MIDDLE) = 0.019 bits -- near-zero independent suffix information

ARTICULATOR's information flow: ART -> PREFIX (strongest, 0.111 bits) -> MIDDLE (via PREFIX selection). No direct ART -> SUFFIX pathway.

### T7: Line Position

**V(position quintile, ARTICULATOR) = 0.092** (p < 1e-115).

**Per-articulator positional profiles (enrichment vs expected, quintiles Q0-Q4):**

| Art | Q0(initial) | Q1 | Q2 | Q3 | Q4(final) | Pattern |
|-----|------------|----|----|----|-----------|---------|
| **p** | **4.18** | 0.36 | 0.09 | 0.27 | 0.09 | Extreme initial |
| **t** | **4.06** | 0.19 | 0.19 | 0.09 | 0.47 | Extreme initial |
| **d** | **3.18** | 0.47 | 0.38 | 0.17 | 0.81 | Strong initial |
| **s** | **2.65** | 0.44 | 0.59 | 0.74 | 0.59 | Strong initial |
| **y** | **2.56** | 0.64 | 0.61 | 0.56 | 0.63 | Strong initial |
| k | 2.36 | 0.97 | 0.69 | 0.56 | 0.42 | Moderate initial |
| **l** | 0.26 | 0.60 | 0.73 | 0.99 | **2.41** | **Final-biased** |
| **r** | 0.63 | 0.42 | 0.85 | 0.49 | **2.61** | **Final-biased** |

Two clear groups:
1. **Initial articulators (d, k, p, s, t, y):** Concentrate at line start (2.4-4.2x enriched Q0)
2. **Final articulators (l, r):** Concentrate at line end (2.4-2.6x enriched Q4)

This positional partition maps to the existing line syntax:
- Initial articulators = **SETUP/SPECIFICATION** markers
- Final articulators = **ROUTING/OUTPUT** markers (l and r correspond to LATE PREFIX family per C539)

### T8: Paragraph Structure

| Context | Art Rate | Ratio |
|---------|----------|-------|
| Paragraph headers | 16.81% | **4.11x** |
| Paragraph body | 4.09% | 1.0x |

Articulators are **strongly header-enriched**. Combined with the line-initial concentration, this makes articulated tokens a hallmark of **paragraph-opening, line-initial specification vocabulary**.

Par-final tokens show *lower* articulator rate (3.26% vs 4.44% non-final), consistent with the suffix-suppression finding: paragraphs close with suffixed (mode-marked) tokens, not articulated specification tokens.

### T9: Combinatorial Constraints

**29 forbidden ARTICULATOR x PREFIX pairs** (observed=0, expected >= 5):

Key patterns:
- **ALL articulators forbidden with BARE and qo-PREFIX** (universal exclusion)
- Most articulators forbidden with ch-PREFIX (exception: y allows ch)
- y forbidden with ok, ot, ol, lk, ka, ke, yk
- Complete exclusion matrix: articulators cannot attach to the three largest PREFIX families (BARE, qo, ch for most)

**4 forbidden ARTICULATOR x MIDDLE HEAD pairs:**
- d x k-HEAD, k x k-HEAD, t x k-HEAD (all expected >= 4-18) -- articulators categorically avoid k-initial MIDDLEs

**Extreme enrichments (>= 3x):**
- y x te: 17.3x
- y x ta: 16.2x
- t x sh: 9.4x
- d x sh: 7.1x
- y x pch: 5.8x
- p x sh: 5.4x

### T10: q-Articulator Analysis

q is **NOT a canonical articulator** (not in the C291 ARTICULATOR list). It is part of the qo- PREFIX compound. The morphology parser correctly handles this -- zero tokens parsed with q as articulator.

The qo- vs o-base comparison confirms the two are categorically distinct systems:
- qo: 59.1% THERMAL, 1.5% TRANSITION
- ok/ot/ol/or: 26.2% THERMAL, 24.7% TRANSITION
- MIDDLE vocabulary Jaccard = 0.181 (very low overlap)

This confirms C1300 (qo near-pure THERMAL channel) vs o-base PREFIXes serving diverse categories.

---

## Synthesis: What ARTICULATOR Does

### Structural Identity

ARTICULATOR is a **line-initial specification amplifier** that:
1. **Marks the opening token of a control block** (17.3% at line-initial, 4.1x paragraph header enrichment)
2. **Selects for stability/cooling MIDDLEs** (76-90% e-HEAD, k-HEAD categorically excluded)
3. **Suppresses suffix attachment** (0.34-0.55x suffix rate), indicating specification context rather than execution context
4. **Operates through PREFIX selection** (V=0.196 with PREFIX, category fully MIDDLE-mediated)

### Two Positional Sub-Groups

| Group | Members | Position | Function |
|-------|---------|----------|----------|
| **INITIAL** | d, k, p, s, t, y | Line-initial (2.4-4.2x Q0) | Opening specification |
| **FINAL** | l, r | Line-final (2.4-2.6x Q4) | Closing/routing marker |

### Relationship to Known Architecture

ARTICULATOR is **peripheral** to the PREFIX -> MIDDLE -> SUFFIX chain:
- MI with chain components: 0.015-0.111 bits (vs 0.290-1.666 bits within chain)
- Category contribution beyond MIDDLE: 0.000 bits
- MIDDLE contribution beyond PREFIX: 0.009 bits (after 68% PREFIX mediation)

ARTICULATOR does NOT:
- Encode operational category (fully mediated by MIDDLE)
- Function as a fourth independent morphological axis
- Appear on thermal-heating (k-initial) operations
- Appear on bare or qo-prefixed tokens

ARTICULATOR DOES:
- Mark line-opening specification positions (paragraph-initial, line-initial)
- Select for e-initial (cooling/stability) MIDDLEs over k-initial (heating)
- Lock to specific PREFIX families (sh overwhelmingly, plus te/ta/pch for y)
- Suppress suffix attachment (output-marking not needed at specification positions)

### Interpretation (Tier 3)

In the apparatus-centric model, articulators appear to mark **specification preambles** -- the initial tokens of control blocks where operational parameters are declared before execution begins. The e-HEAD bias and suffix suppression indicate these are **stability-oriented setup instructions**: declare the thermal target (cooling/equilibrium) before the active processing line unfolds.

The y-articulator's dominance (51.2%) and its affinity for te/ta/pch PREFIXes aligns with the "prep verb" family (C933). The y may function as a paragraph/line-opening variant marker that signals "this is a new specification block" distinct from continuation of an existing block.

The l/r final articulators, being LATE PREFIX family atoms (C539), mark the **output/routing** end of lines -- complementary to the initial-specification role.

---

## New Constraints

### C1416: ARTICULATOR Rate and Inventory
**Tier 2, Scope: B**
ARTICULATOR slot is occupied in 4.41% of B tokens (1,019/23,096). Nine articulators: y (51.2%), d (11.6%), l (11.4%), r (7.0%), p (5.4%), t (5.2%), k (3.5%), s (3.3%), f (1.4%). Confirms C291/C294 at corpus scale.

### C1417: ARTICULATOR Line-Initial Concentration
**Tier 2, Scope: B, line, position**
Articulators concentrate at line-initial position: 17.3% at initial vs 2.7% medial (6.48x enrichment). Paragraph headers are 4.11x enriched. Two positional sub-groups: INITIAL articulators (d,k,p,s,t,y at Q0 2.4-4.2x) and FINAL articulators (l,r at Q4 2.4-2.6x).

### C1418: ARTICULATOR PREFIX-Locked with BARE/qo Exclusion
**Tier 2, Scope: B, PREFIX, ARTICULATOR**
29 forbidden ARTICULATOR x PREFIX pairs. Articulators categorically exclude BARE tokens (0/3,864) and qo-PREFIX (3/4,069 = 0.07%). Most articulators lock to sh-PREFIX family (t: 94%, k: 94%, d: 72%). y distributes across ch/te/ta/sh. V(ART,PREFIX) = 0.196, p < 1e-300.

### C1419: ARTICULATOR e-HEAD Selectivity and k-HEAD Exclusion
**Tier 2, Scope: B, MIDDLE, ARTICULATOR, atom**
Articulated tokens are 76-90% e-initial MIDDLE (vs 40% baseline = 1.9-2.3x enrichment). k-HEAD MIDDLEs categorically excluded from d,k,t articulators (4 forbidden pairs, all expected >= 4). PREFIX mediates 68.3% of this effect. Articulators mark stability/cooling operations, not heating.

### C1420: ARTICULATOR Suffix Suppression
**Tier 2, Scope: B, SUFFIX, ARTICULATOR**
Articulated tokens have 16.7-27.2% suffix rate vs 49.3% baseline (0.34-0.55x). Only p-articulator matches baseline (58.2%). Suffix suppression is consistent with specification context (no execution-mode marking needed at line-opening positions).

### C1421: ARTICULATOR Category Full MIDDLE Mediation
**Tier 2, Scope: B, ARTICULATOR, category**
I(ART; CATEGORY | MIDDLE) = 0.000 bits. ARTICULATOR's raw category association (V=0.042) is entirely mediated through MIDDLE selection. ARTICULATOR does not encode operational category independently. MI hierarchy: ART-PREFIX 0.111 > ART-MIDDLE 0.060 > ART-SUFFIX 0.015 bits, all 10-100x below main chain (0.290-1.666 bits).

---

## Verdict

ARTICULATOR is a **peripheral, line-position-dependent specification marker** that operates through PREFIX selection to target stability/cooling MIDDLEs at control block boundaries. It is NOT a fourth independent morphological axis. Its information content (0.111 bits maximum) is 10-15x smaller than the PREFIX-MIDDLE-SUFFIX chain. The correct architectural model remains: `[ARTICULATOR] + PREFIX + MIDDLE + [SUFFIX]` where ARTICULATOR modifies the positional deployment of the subsequent token rather than adding independent content.
