# Phase 525: The e->y Safe Pathway and Recovery Architecture

**Date:** 2026-03-05
**Status:** COMPLETE
**New Constraints:** C1457-C1462

---

## Research Question

Phase 523 (C1448) identified e->y as the largest single safe frame in the grammar: 3,475 tokens at near-zero hazard. C105 established that 54.7% of recovery paths converge on the `e` operator. Is e->y the backbone of recovery architecture? How does this massive safe frame connect to escape routes, hazard avoidance, and the grammar's stability design?

---

## Key Findings

### T1: e->y Token Inventory (C1457)

e->y comprises **3,475 tokens (15.0% of the corpus)** -- one in every 6.7 tokens. Despite this enormous population, the vocabulary is remarkably narrow: only **7 unique MIDDLEs**, dominated by three forms:

| MIDDLE | Count | Fraction | Category |
|--------|-------|----------|----------|
| edy | 1,938 | 55.8% | OPERATION |
| ey | 889 | 25.6% | TRANSITION |
| eey | 644 | 18.5% | THERMAL |
| eody/echy/ecty | 4 | 0.1% | various |

e-depth distribution: single-e = 2,831 tokens (81.5%), double-e = 644 tokens (18.5%). The modifier `d` dominates (edy = 55.8%), with `d` functioning as the containment/seal modifier (C1195). The modified form `edy` is OPERATION-classified; the bare form `ey` is TRANSITION; the extended `eey` is THERMAL.

e->y accounts for **49.6% of all e-HEAD tokens** -- half of all cooling-initiated operations terminate with the y (end) terminal.

### T2: e->y Category Profile (C1458)

e->y tokens are categorically specialized in OPERATION (3.94x enrichment) and TRANSITION (1.73x), with near-total exclusion from hazardous categories:

| Category | e->y rate | Corpus rate | Enrichment |
|----------|-----------|-------------|------------|
| OPERATION | 55.8% | 14.2% | 3.94x |
| TRANSITION | 25.6% | 14.8% | 1.73x |
| THERMAL | 18.6% | 23.4% | 0.79x |
| FLOW | 0.06% | 19.2% | 0.003x |
| CONTAINMENT | 0.0% | 4.8% | 0.00x |
| MARKING | 0.03% | 7.7% | 0.004x |

**e->y hazard rate: 0.06% (2/3,475)** vs corpus 23.9% -- a **400x hazard reduction**. The 2 FLOW-classified tokens are edge cases at the category classifier boundary. Functionally, e->y is categorically safe.

Comparison with other e-HEAD frames reveals the y-terminal's unique safety: e->d has 64.7% hazard, e->k has 35.6%, e->t has 16.4%, e->h has 14.3%. Only e->l (0%), e->bare (0%), and e->y (0.06%) are safe among high-frequency e-HEAD frames.

### T3: e->y is NOT Recovery-Specific (C1459)

The most surprising finding: **e->y is NOT preferentially deployed after hazard events.**

| Context | e->y rate | Enrichment | p-value |
|---------|-----------|------------|---------|
| Overall | 15.05% | 1.00x | -- |
| Post-hazard token | 14.75% | 0.98x | -- |
| Post-safe token | 15.35% | 1.02x | -- |
| Post-forbidden-source | 16.45% | 1.09x | -- |
| Mann-Whitney | -- | -- | p=0.310 (NS) |

e->y appears at the same rate regardless of whether the preceding token is hazardous or safe. Furthermore:
- Pre-e->y hazard rate: 23.0% (matches corpus baseline)
- Post-e->y hazard rate: 22.9% (matches corpus baseline)

**Interpretation:** e->y is not a reactive recovery mechanism -- it is a **structural constant**. It pervades the grammar as an ambient safety substrate rather than being deployed in response to danger. The recovery convergence on e (C105) operates through e->y as omnipresent infrastructure, not targeted intervention.

### T4: e->y Positional Profile (C1460)

e->y tokens show mild early-line bias with strong line-final avoidance:

| Metric | e->y | Corpus | Enrichment |
|--------|------|--------|------------|
| Mean position | 0.463 | 0.500 | -- |
| Line-initial rate | 9.5% | 10.5% | 0.91x |
| Line-final rate | 5.7% | 10.5% | 0.55x |
| Q0 (0-20%) | 23.6% | 21.7% | 1.09x |
| Q1 (20-40%) | 20.5% | 18.1% | 1.13x |
| Q4 (80-100%) | 18.4% | 24.1% | 0.76x |

e->y is depleted at line-final positions (0.55x) -- it does not close lines. Instead, it concentrates in the early-to-middle work zone (Q0-Q1 enriched), consistent with the THERMAL peak-then-decline gradient (C1428). e->y does the thermal work; other mechanisms (m-terminal, -am suffix) handle line/paragraph closure.

### T5: e->y PREFIX Channels (C1461)

e->y is a **CHSH-channel token with dramatic sh enrichment**:

| PREFIX | e->y count | Enrichment | Interpretation |
|--------|-----------|------------|----------------|
| sh | 859 | **2.45x** | Monitor-verify (passive) |
| ch | 915 | 1.74x | Test-check (active) |
| lch | 177 | 3.74x | Hold-test |
| lsh | 70 | 4.01x | Hold-monitor |
| ok | 329 | 1.48x | Vessel thermal check |
| ot | 353 | 1.62x | Vessel transfer check |
| qo | 23 | **0.04x** | Heat source (almost excluded) |
| BARE | 1 | **0.002x** | Categorically excluded |
| da | 0 | 0.00x | Categorically excluded |

The ch/sh ratio for e->y is 1.07:1, dramatically lower than the corpus ratio of 1.50:1. e->y tokens are **sh-enriched** -- passive monitoring rather than active testing. This is consistent with e->y as steady-state process verification rather than diagnostic intervention.

The near-total exclusion from qo (0.04x) and BARE (0.002x) channels is striking. e->y is almost never a bare operation and almost never fires on the heat source channel. It operates on the monitoring/verification channel (ch/sh) and the vessel/transfer channels (ok/ot).

### T6: e->y Suffix Behavior

e->y tokens are **categorically unsuffixed** -- suffix rate 0.46% vs corpus 48.3% (0.01x ratio). This is expected: y is an opaque terminal (C1440, 4.2% suffix rate overall for y-terminal MIDDLEs). The y-terminal categorically suppresses suffix attachment. e->y tokens are Mode B by default (bare = Mode B per C1229), making them continuation/equilibration tokens rather than specification tokens.

Only 16 of 3,475 e->y tokens have any suffix at all. e->y operates as an atomic, unsuffixed instruction -- no parametric modification needed.

### T7: e->y Stability Anchor (C1462)

e->y tokens are **AXM-enriched (1.16x)** and completely excluded from FL_HAZ, FL_SAFE, and CC macro-states:

| Macro-state | e->y rate | Corpus rate | Enrichment |
|-------------|-----------|-------------|------------|
| AXM | 78.1% | 67.7% | 1.16x |
| FQ | 17.4% | 18.0% | 0.97x |
| AXm | 4.5% | 3.0% | 1.47x |
| CC | 0.0% | 4.6% | 0.00x |
| FL_HAZ | 0.0% | 6.0% | 0.00x |
| FL_SAFE | 0.0% | 0.8% | 0.00x |

**Transition asymmetry:** After e->y, the system moves to AXM at 77.0% (vs 67.6% before e->y). The post-e->y AXM rate (77%) is significantly higher than the pre-e->y rate (67.6%), a +9.4pp increase in AXM targeting. e->y acts as a **one-way ratchet toward AXM**.

Post-e->y, the dominant next HEAD is k (817 tokens, 34.3%) -- the system transitions from cooling/stabilization (e->y) directly to energy operations (k). The e->y->k transition is the dominant recovery pathway: cool -> end -> heat again.

Self-chaining rate: 18.7% -- e->y tokens chain with themselves at substantial rates, creating extended safe runs of cooling/stabilization within the AXM attractor.

### T8: e->y Among Safe Frames

21 HEAD x TERM frames have exactly 0% hazard with N >= 100. The largest are:

| Frame | N tokens | Note |
|-------|----------|------|
| k->bare | 2,083 | Energy operations (always safe) |
| e->bare | 867 | Cooling operations (always safe) |
| l->bare | 855 | State marking (always safe) |
| o->l | 777 | Arrangement + state (always safe) |
| ee->y | 644 | Deep cooling + end |
| ii->n | 560 | Double iteration + bind |
| y->bare | 513 | End operations |
| k->e | 428 | Energy + cooling |

Note: The atomization splits e->y into "e->y" (single-e, ~2,831 tokens, 0.07% hazard from 2 edge cases) and "ee->y" (644 tokens, 0% hazard). Combined, the e*->y family at 3,475 tokens is the largest safe pathway in the grammar.

### T9: e->y and Paragraph Structure

e->y shows a paragraph-depth gradient:

| Position | e->y rate | Interpretation |
|----------|-----------|----------------|
| Header lines | 12.0% | Lower at specification |
| Early body | 14.8% | Rising in work phase |
| Late body | 17.5% | Peak at sustained operation |

e->y is depleted in paragraph headers (0.80x vs late body) and enriched in late body lines (1.19x vs header). This is consistent with e->y as an operational steady-state token: specification phase uses other vocabulary, but once operations are running, e->y dominates the sustained work phase.

Paragraph-level e->y rate correlates positively with AXM fraction (rho=+0.274, p<0.000001, N=573 paragraphs).

### T10: e->y Predicts Program Forgiveness (C1462 extension)

The strongest finding: **folio-level e->y rate is a powerful predictor of program forgiveness.**

| Correlation | rho | p-value | Interpretation |
|-------------|-----|---------|----------------|
| e->y vs AXM fraction | +0.471 | 8e-6 | More e->y = more AXM |
| e->y vs AXM self-transition | **+0.569** | **<1e-7** | More e->y = stronger AXM attractor |
| e->y vs FQ rate | -0.369 | 6e-4 | More e->y = fewer escape events |
| e->y vs hazard rate | **-0.473** | **7e-6** | More e->y = less hazard |

Quartile analysis (82 folios):

| Quartile | Mean e->y | AXM rate | AXM self | FQ rate | Hazard rate |
|----------|-----------|----------|----------|---------|-------------|
| Q1 (low e->y) | 6.6% | 58.3% | 40.6% | 24.8% | 28.4% |
| Q2 | 11.0% | 63.0% | 45.5% | 21.0% | 25.6% |
| Q3 | 15.6% | 67.1% | 49.8% | 16.9% | 22.9% |
| Q4 (high e->y) | 21.1% | 70.6% | 55.0% | 16.5% | 22.1% |

Programs with high e->y are:
- **More forgiving** (stronger AXM attractor, self-transition from 40.6% to 55.0%)
- **Less hazardous** (28.4% to 22.1%)
- **Less escape-dependent** (FQ from 24.8% to 16.5%)

The e->y rate is the **mechanical basis of the forgiveness gradient** (C458, C980). Programs with more cooling/stabilization/ending operations spend more time in the AXM attractor and less time in hazardous transitions.

---

## Synthesis

### The e->y Design Principle

e->y is not a recovery mechanism. It is a **stability substrate** -- an ambient, omnipresent safe operation that the grammar deploys at a constant ~15% rate regardless of local context. Its properties are:

1. **Structurally safe:** 0.06% hazard rate (400x below corpus baseline)
2. **Positionally neutral:** Appears everywhere except line-final (closure is handled separately)
3. **Context-independent:** Same rate after hazard and safe tokens alike
4. **AXM-enriching:** Acts as one-way ratchet toward AXM attractor (+9.4pp post-e->y)
5. **Unsuffixed:** Atomic operations requiring no parametric modification
6. **CHSH-channel:** Operates on monitoring/verification channels, not heat source
7. **Forgiveness predictor:** Folio-level e->y rate is the strongest single predictor of program forgiveness (rho=+0.569 with AXM self-transition)

### Connection to Existing Architecture

- **C105 (e = STABILITY_ANCHOR):** e->y is the primary vehicle through which e achieves stability anchoring. Half of all e-HEAD tokens terminate in y.
- **C1446 (k-HEAD hazard immunity):** k-HEAD provides safe energy input; e->y provides safe energy output/stabilization. Together they form the grammar's thermal safety envelope.
- **C458 (design asymmetry):** e->y rate is the parameter that determines where each program sits on the forgiveness gradient. Hazard is clamped; e->y rate is free to vary, and this variation IS the recovery freedom.
- **C1448 (frame hazard map):** e->y is confirmed as the largest safe frame, but its role is substrate not recovery.
- **C1229 (suffix modes):** e->y tokens are categorically Mode B (unsuffixed), forming the continuation/equilibration backbone.
- **C929 (ch/sh discrimination):** e->y is sh-enriched (2.45x), confirming its role as passive monitoring rather than active testing.

### The Thermal Safety Envelope

The grammar's safety architecture rests on two pillars:
- **k-HEAD (energy input):** Unconditionally safe regardless of terminal (C1446). 2,083+ tokens at 0% hazard.
- **e->y (energy output):** Near-unconditionally safe cooling-then-end operations. 3,475 tokens at 0.06% hazard.

Between them, k-HEAD and e->y account for ~5,558 tokens (24% of corpus) at effectively zero hazard. This is the **thermal safety envelope** -- the grammar guarantees that heating and cooling operations are categorically safe, concentrating all hazard in the transitions between them (FLOW, CONTAINMENT, and certain TRANSITION tokens).

---

## New Constraints

### C1457: e->y Narrow Vocabulary Dominance
3,475 tokens (15.0% of corpus) from only 7 unique MIDDLEs. edy (55.8%), ey (25.6%), eey (18.5%) account for 99.9%. e->y is 49.6% of all e-HEAD tokens. Modified (d-modifier) forms dominate over bare.

### C1458: e->y Categorical Safety with OPERATION Enrichment
e->y hazard rate 0.06% (2/3,475) vs corpus 23.9% -- 400x hazard reduction. OPERATION 3.94x enriched, TRANSITION 1.73x enriched. FLOW/CONTAINMENT/MARKING categorically excluded. Among e-HEAD frames, only e->l, e->bare, and e->y are safe; e->d (64.7%), e->k (35.6%) are hazardous.

### C1459: e->y Context-Independent Deployment (Not Recovery-Specific)
e->y rate is 15.0% regardless of preceding context: post-hazard 14.75%, post-safe 15.35% (Mann-Whitney p=0.310 NS). Pre-e->y and post-e->y hazard rates both match corpus baseline (23%). e->y is ambient safety substrate, not reactive recovery mechanism.

### C1460: e->y Early-Line Concentration with Final Avoidance
Mean line position 0.463 (vs corpus 0.500). Line-final depleted 0.55x. Q0-Q1 enriched 1.09-1.13x. Paragraph late-body enriched (17.5%) vs header (12.0%). e->y does thermal work; does not close lines or paragraphs.

### C1461: e->y CHSH-Channel with sh Enrichment and qo/BARE Exclusion
sh 2.45x enriched, ch 1.74x; ch/sh ratio 1.07 vs corpus 1.50 (sh-biased). qo 0.04x, BARE 0.002x, da 0.00x -- categorically excluded from energy source and infrastructure channels. Operates on monitoring/verification channels.

### C1462: e->y Rate Predicts Folio Forgiveness via AXM Attractor
e->y vs AXM self-transition: rho=+0.569, p<1e-7 (82 folios). e->y vs hazard rate: rho=-0.473, p=7e-6. Quartile analysis: Q1 (6.6% e->y) = 40.6% AXM self, Q4 (21.1% e->y) = 55.0% AXM self. e->y fraction is the mechanical basis of program forgiveness. Post-e->y AXM rate 77% vs pre-e->y 67.6% (+9.4pp one-way ratchet).

---

## Script

`phases/EY_SAFE_PATHWAY/scripts/ey_safe_pathway.py`

## Results

`phases/EY_SAFE_PATHWAY/results/ey_safe_pathway.json`
