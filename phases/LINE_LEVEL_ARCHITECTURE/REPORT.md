# Phase 519: Line-Level Architecture

**Date:** 2026-03-05
**Status:** COMPLETE
**Constraints produced:** C1425-C1430 (6 new)
**Phase type:** Systematic profiling

---

## Objective

Characterize the Currier B line as a structural unit: its length distribution, boundary profiles, internal gradients, transition grammar, independence from adjacent lines, information content, typology, and boundary marking hierarchy.

## Method

10 systematic tests (T1-T10) applied to 23,096 tokens across 2,420 lines in 83 B folios. Morphological decomposition via `scripts/voynich.py` (Morphology + CategoryClassifier). Line position normalized 0-1 within each line. Quintile binning for gradient analysis.

## Results

### T1: Line Length Distribution

| Metric | Value |
|--------|-------|
| Mean | 9.54 tokens |
| Median | 10 |
| CV | 0.340 |
| Mode | 10 (19.9% of lines) |
| Range | 1-54 |
| IQR | 7-12 |

The distribution is strongly unimodal with a sharp peak at 10 tokens. 94.7% of lines fall in the 3-13 range. Outliers above 16 are exclusively COSMO section (std=9.14, max=54) which contains atypical long-line folios. Excluding COSMO, max=16 and CV drops to ~0.27.

**Header vs body:** Header lines (paragraph-initial) average 10.25 tokens vs body 9.34 (ratio 1.097). The ~10% header excess is modest but consistent -- headers carry slightly more specification vocabulary (C932, C1287).

**Section variation:** BIO shortest (8.97), COSMO longest (11.65), others cluster at 9.1-9.9. Section explains some variance but the modal line of 10 tokens is universal.

**Verdict:** Line length is moderately constrained (CV=0.34), consistent with C958 (opener determines length, R^2=0.937 with folio+opener) and C677 (late lines slightly shorter). Not discrete -- continuous distribution.

### T2: Line-Initial Token Profile

| Feature | Initial Rate | Baseline | Enrichment |
|---------|-------------|----------|------------|
| ARTICULATOR | 17.36% | 4.41% | 3.93x |
| po- PREFIX | 5.22% | 0.66% | 7.93x |
| dch- PREFIX | 3.24% | 0.50% | 6.42x |
| so- PREFIX | 5.59% | 0.91% | 6.11x |
| to- PREFIX | 2.87% | 0.56% | 5.15x |
| STAGING cat. | 20.46% | 13.00% | 1.57x |
| MARKING cat. | 11.05% | 7.78% | 1.42x |

Top initial words: daiin (3.5%), saiin (2.0%), dain/sain (1.4% each). These are CC trigger tokens (C557) and prep markers (C933).

**Head atom shift:** Position 1 is e-dominant (53.7%) compared to overall (40.1%). k-atoms are present but not enriched. The line opens with cooling/stability specification, not heating.

**ARTICULATOR concentration:** 3.93x validates C1417 direction (that constraint found 6.48x using a different position calculation). Articulators are strongly line-initial markers, functioning as specification modifiers at line entry.

### T3: Line-Final Token Profile

| Feature | Final Rate | Baseline | Enrichment |
|---------|-----------|----------|------------|
| ar- PREFIX | 3.59% | 0.79% | 4.56x |
| al- PREFIX | 3.59% | 1.00% | 3.59x |
| or- PREFIX | 3.37% | 1.00% | 3.37x |
| -m suffix | 1.57% | 0.16% | 9.54x |
| -am suffix | 3.59% | 0.46% | 7.83x |
| TRANSITION cat. | 24.51% | 15.02% | 1.63x |
| THERMAL cat. | 13.39% | 23.87% | 0.56x |

Top final words: am (1.8%), ol (1.7%), dy (1.6%), chedy (1.5%).

**Terminal atom shift:** m-terminal jumps from 0.06% at position 1 to 11.82% at line-final (196x). n-terminal drops from 19.5% to 8.9%. This is the -am suffix final enrichment (C1237) and the TRANSITION category rise at line end.

**THERMAL depletion:** Line-final positions show 0.56x THERMAL enrichment -- the thermal work is done, the line closes with state transition/flow markers. Strongly validates C556 (SETUP->WORK->CHECK->CLOSE).

### T4: Positional Category Gradient (Quintile Analysis)

| Category | Q0 | Q1 | Q2 | Q3 | Q4 | Gradient |
|----------|-----|-----|-----|-----|-----|----------|
| THERMAL | 24.3% | **29.4%** | 24.8% | 24.6% | 17.6% | peaks Q1, falls late |
| FLOW | 17.6% | 16.5% | 19.6% | 20.2% | **22.6%** | rises steadily |
| TRANSITION | 14.1% | 14.0% | 12.5% | 14.2% | **19.1%** | flat then jumps Q4 |
| STAGING | **15.6%** | 12.1% | 12.4% | 10.9% | 13.5% | peaks Q0 |
| MARKING | 8.4% | 6.5% | 7.7% | 8.3% | 7.9% | flat (weak Q0 peak) |
| ARTICULATOR | 9.7% | 2.8% | 2.8% | 2.5% | 3.5% | drops sharply after Q0 |

**Key gradient:** THERMAL peaks at Q1 (29.4%) not Q0, because Q0 includes prep/staging vocabulary (articulators, specification PREFIXes). The "work zone" begins at position 2 and peaks around position 3. FLOW and TRANSITION rise toward line-end, consistent with the CHECK->CLOSE pattern.

**BARE PREFIX gradient:** Rises monotonically Q0-Q4 (14.3% to 21.9%), confirming C1302 (BARE is THERMAL-depleted, associated with boundary/closing operations).

### T5: PREFIX Positional Grammar Validation

33 PREFIXes with N>=25 tested:

| Class | Count | Examples (mean position) |
|-------|-------|--------------------------|
| INITIAL_BIASED | 12 | po (0.107), dch (0.168), so (0.189), to (0.267), tch (0.283), pch (0.299), sa (0.362), sh (0.396) |
| CENTRAL | 13 | kch (0.436), qo (0.485), ch (0.515), ok (0.538), ot (0.588) |
| FINAL_BIASED | 8 | da (0.521), ol (0.560), ka (0.570), or (0.664), al (0.692), ar (0.744) |

**Key findings:**
- **Modifier-initial PREFIXes cluster early:** p-, d-, s-, t- modifiers all create INITIAL_BIASED PREFIXes (mean 0.362 for modifier chars). This validates C1218 (dedicated modifiers at POS-0).
- **sh before ch:** sh mean=0.396 vs ch mean=0.515 (delta=+0.120). Validates C929 (sh=passive monitor earlier, ch=active test later).
- **ok vs ot:** ok mean=0.538 vs ot mean=0.588. ok slightly earlier, consistent with C1316 (ok=coarse verification, ot=fine adjustment).
- **LATE PREFIXes confirmed:** ar (0.744), al (0.692), or (0.664) are line-final. Validates C539.

### T6: Internal Category Transitions

Category self-transition rate: 0.185 (vs 0.125 expected if uniform across 8 categories). Categories mildly self-chain.

| Transition | Rate | Note |
|-----------|------|------|
| THERMAL->THERMAL | 0.277 | Strongest self-chaining |
| FLOW->FLOW | 0.228 | Second strongest |
| OPERATION->THERMAL | 0.295 | Strongest cross-category |
| THERMAL->FLOW | 0.192 | Second cross-category |

PREFIX self-transitions: BARE highest (0.283), then qo (0.210), ch (0.152). BARE tokens chain because they occur in line-final sequences. qo chains because thermal operations are sequential.

Mean transition entropy: 2.806 bits (max possible ~3.0 for 8 categories). High entropy indicates category transitions are only weakly constrained within lines -- consistent with C964 (free interior).

### T7: Cross-Line Independence

| Metric | Value | Interpretation |
|--------|-------|----------------|
| Suffix mode MI | 0.003 bits | Negligible |
| Dominant category MI | 0.032 bits | Very weak |
| Boundary category MI | 0.025 bits | Very weak |
| Line length correlation | 0.406 | Moderate (folio-mediated) |
| Vocabulary Jaccard | 0.153 | Low overlap |

**Verdict: INDEPENDENT.** Adjacent lines share almost no mutual information about category composition, suffix mode, or vocabulary. The line length correlation (0.406) is folio-mediated -- folios with long lines tend to have consistently long lines (C958, C680). Validates C670 (no vocabulary coupling), C673 (no CC trigger memory), C674 (no lane balance memory), and C1233 (cross-line independence).

### T8: Information Content Profile

| Quintile | Mean info (bits) | N tokens |
|----------|-----------------|----------|
| Q0 | 10.29 | 5,014 |
| Q1 | 9.61 | 4,186 |
| Q2 | 9.58 | 4,135 |
| Q3 | 9.62 | 4,186 |
| Q4 | 10.11 | 5,553 |

**U-shaped information gradient:** Boundaries carry more information than interior. Initial tokens are most informative (opener = specification, folio-specific vocabulary). Final tokens are second-most informative (routing/termination markers). Interior tokens are lower-information (routine thermal operations, common MIDDLEs).

Global word entropy: 9.875 bits. Mean line entropy: 3.117 bits. Position-1 PREFIX predicts rest-of-line category with MI=0.084 bits (weak but non-zero -- confirms C1219 base determines MIDDLE content, and C958 opener determines length).

### T9: Line Type Characterization

**Dominant category distribution (body lines):**
- THERMAL-dominant: 52.2% (most common)
- FLOW-dominant: 21.1%
- TRANSITION-dominant: 16.7%
- STAGING-dominant: 8.6%
- MARKING-dominant: 1.4%

**Header vs body:** Headers have elevated MARKING (15.4% vs 1.4% body dominant). THERMAL drops from 52.2% body to 40.3% header. Headers are specification lines; body lines are execution lines.

**Section profiles:** BIO most THERMAL-dominant (58.5%), COSMO most FLOW-dominant (32.5%). Herbal and COSMO show more TRANSITION-dominant lines (25.8% and 24.6% respectively). Section modulates the distribution of line types but THERMAL dominance is universal.

### T10: Boundary Marker Hierarchy

| Boundary Type | Mean Entropy | Ratio to Within-Line |
|---------------|-------------|---------------------|
| Within-line | 2.806 | 1.000 |
| Cross-line (same paragraph) | 2.760 | 0.984 |
| Cross-paragraph | 2.669 | 0.951 |
| Cross-line (non-paragraph) | 2.674 | 0.953 |

**Verdict: LINE = PARAGRAPH boundary strength.** The cross-line entropy drop is only 1.6% below within-line, meaning line boundaries are nearly as porous as within-line transitions. Paragraph boundaries show an additional modest drop (3.3% below cross-line). The boundary hierarchy is very flat -- the grammar does not dramatically shift at boundaries, confirming C964 (boundary-constrained free-interior) and C672 (line boundaries grammar-transparent).

**Suffix final markers:** -m is 9.54x enriched at line-final (including -am at 7.83x). -ry at 5.59x. These are the primary line-end markers. Bare (no suffix) rate at line-final: 50.5% (vs 51.7% baseline) -- essentially the same.

---

## New Constraints

### C1425: Line Length Unimodal Distribution (Tier 2)
Mean=9.54, median=10, CV=0.340. Mode at 10 tokens (19.9%). 94.7% within 3-13 range. Header lines 1.097x longer than body. BIO shortest (8.97), COSMO longest (11.65, inflated by outliers). Line length is continuous and unimodal, not discrete.

### C1426: Line-Initial Specification Profile (Tier 2)
Line-initial tokens: ARTICULATOR 3.93x enriched, STAGING 1.57x, MARKING 1.42x. PREFIXes po/dch/so/to 5-8x enriched. Head atom e-dominant (53.7% vs 40.1% baseline). Lines open with specification/staging vocabulary, not thermal execution. Top words: daiin (3.5%), saiin (2.0%).

### C1427: Line-Final Transition Profile (Tier 2)
Line-final tokens: TRANSITION 1.63x enriched, THERMAL 0.56x depleted. Terminal atom m jumps to 11.8% from 0.06% at pos-1 (196x). Suffix -m 9.54x enriched, -am 7.83x. PREFIXes ar/al/or 3.4-4.6x enriched. Lines close with state-change/closure vocabulary.

### C1428: THERMAL-Peak-Then-Decline Positional Gradient (Tier 2)
THERMAL category peaks at Q1 (29.4%), not Q0 (24.3%), because Q0 contains specification/prep vocabulary. Declines to 17.6% at Q4. FLOW rises monotonically Q0->Q4 (17.6%->22.6%). TRANSITION jumps at Q4 (14.1%->19.1%). BARE PREFIX rises Q0->Q4 (14.3%->21.9%). Category gradient is SPECIFICATION->THERMAL_WORK->FLOW/TRANSITION.

### C1429: Cross-Line Category Independence (Tier 2)
Adjacent lines: suffix mode MI=0.003 bits, dominant category MI=0.032 bits, vocabulary Jaccard=0.153. Line length correlation=0.406 (folio-mediated, not sequential). Lines are categorically independent units. Validates C670, C673, C674, C1233.

### C1430: Information U-Shape at Line Boundaries (Tier 2)
Token information content forms U-shape: Q0=10.29, Q1-Q3=9.58-9.62, Q4=10.11 bits. Boundaries carry more information than interior. Initial tokens specify (folio-specific vocabulary), final tokens route (closure markers). Interior tokens are routine thermal operations.

---

## Relationship to Existing Constraints

| Existing | Relationship | This Phase |
|----------|-------------|------------|
| C556 | SETUP->WORK->CHECK->CLOSE | T4 gradient validates with category-level resolution |
| C929 | sh earlier, ch later | T5: sh mean=0.396, ch=0.515, delta=+0.120 |
| C931 | PREFIX temporal ordering | T5: full 33-PREFIX positional map confirms |
| C932 | Body vocabulary gradient | T4: THERMAL peak at Q1, rarity gradient confirmed |
| C957 | Token-level bigram constraints | T6: category transitions weakly structured |
| C958 | Opener determines line length | T1: header/body length difference 1.097x |
| C964 | Boundary-constrained free-interior | T10: entropy ratio 0.984, flat hierarchy |
| C1001 | PREFIX dual encoding | T5: 33 PREFIXes with positional profiles |
| C1218-C1219 | PREFIX base-modifier grammar | T5: modifier chars mean 0.362, base chars central/late |
| C1237 | Paragraph termination by -am | T3: -am 7.83x final-enriched |
| C1302 | BARE anti-thermal | T4: BARE rises Q0->Q4, anti-correlates with THERMAL |
| C1358 | Class positional specialization | T4-T5: category and PREFIX gradients confirm |
| C1417 | ARTICULATOR line-initial | T2: 3.93x enrichment validates |

---

## Integration with Frozen Model

The line is a **self-contained execution unit** with three zones:

1. **SPECIFICATION zone** (positions 0-0.2): Articulated, staged, marked. PREFIXes with modifier characters (p,d,s,t). Specifies what this control cycle will do.

2. **THERMAL WORK zone** (positions 0.2-0.7): THERMAL-dominant. qo/ch/sh PREFIXes. The actual heating/cooling/monitoring operations.

3. **CLOSURE zone** (positions 0.7-1.0): TRANSITION/FLOW-dominant. BARE and LATE PREFIXes (ar,al,or). Terminal suffixes (-am,-m). State change and routing to next cycle.

Lines are **independent** of each other (MI < 0.035 bits on all category metrics) but **coherent within** (category transitions mildly structured, entropy 2.806/3.0 bits). The grammar produces each line as a fresh sample from the folio's operational profile, with no sequential memory.

This validates and extends the C556 execution cycle model with quantitative category-level resolution across all 23,096 tokens.

---

## Files

| File | Purpose |
|------|---------|
| `phases/LINE_LEVEL_ARCHITECTURE/scripts/line_architecture.py` | Analysis script |
| `phases/LINE_LEVEL_ARCHITECTURE/results/line_architecture.json` | Full results |
| `phases/LINE_LEVEL_ARCHITECTURE/REPORT.md` | This report |
