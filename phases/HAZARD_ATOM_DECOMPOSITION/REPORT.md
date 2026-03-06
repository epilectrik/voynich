# Phase 523: Hazard Topology Atom-Level Decomposition

**Date:** 2026-03-05
**Status:** COMPLETE
**Constraints produced:** C1446-C1451

## Objective

Decompose the 17 forbidden transitions (C109, Tier 0) and hazard topology at atom-level resolution using the HEAD+MOD*+TERM instruction encoding framework (C1393-C1394). This connects the execution-layer hazard architecture to the construction-layer atom grammar.

## Method

10 pre-registered tests (T1-T10) examining how compound MIDDLE decomposition, terminal atoms, HEAD atoms, modifier stacks, PREFIX channels, line position, suffix mode, and the closure system interact with hazard exposure.

**Script:** `phases/HAZARD_ATOM_DECOMPOSITION/scripts/hazard_atom_decomposition.py`
**Results:** `phases/HAZARD_ATOM_DECOMPOSITION/results/hazard_atom_decomposition.json`

**Corpus:** 23,096 clean Currier B tokens, 20,676 adjacency pairs, 11 actual forbidden pair violations.

---

## Results

### T1: Hub MIDDLE Atom Decomposition

23 hub MIDDLEs (C1000) decomposed into HEAD/MOD/TERM slots:

| Sub-Role | Hub MIDDLEs | HEAD atoms | TERM atoms |
|----------|-------------|------------|------------|
| HAZARD_SOURCE (6) | ar, dy, ey, l, ol, or | a(2), d(1), e(1), l(1), o(2) | r(2), y(2), l(1) |
| HAZARD_TARGET (6) | aiin, al, ee, o, r, t | a(2), e(1), o(1), r(1), t(1) | n(1), l(1), e(1) |
| SAFETY_BUFFER (3) | eol, k, od | e(1), k(1), o(1) | l(1), d(1) |
| PURE_CONNECTOR (8) | d, e, eey, ek, eo, iin, s, y | d(1), e(4), i(1), s(1), y(1) | y(1), k(1), o(1), n(1) |

**Key pattern:** HAZARD_SOURCE concentrates r-terminal (FLOW) and y-terminal (OPERATION/CONTAINMENT). HAZARD_TARGET concentrates a-HEAD (yield domain). SAFETY_BUFFER favors k (THERMAL) and o-HEAD. PURE_CONNECTOR is dominated by e-HEAD (4/8).

### T2: Hazard Class Atom Signatures

| Failure Class | N pairs | Source signature | Target signature | Category focus |
|---------------|---------|-----------------|-----------------|----------------|
| PHASE_ORDERING (41%) | 7 | y-terminal (4/4 sources), ch/sh-prefix | a-HEAD (2/6), e-enriched | TRANSITION 44%, FLOW 28% |
| COMPOSITION_JUMP (24%) | 4 | r-terminal (2/3 sources) | a-HEAD, mixed terminals | FLOW 43%, TRANSITION 32% |
| CONTAINMENT_TIMING (24%) | 4 | h/e sources (he 2x) | o-enriched targets, c-HEAD | FLOW 54%, STAGING 45% |
| RATE_MISMATCH (6%) | 1 | c (adjust) | ee (deep thermal) | THERMAL 97% |
| ENERGY_OVERSHOOT (6%) | 1 | chol (monitoring+staging) | r (pure FLOW) | FLOW 100% |

**Key finding:** The dominant PHASE_ORDERING class is characterized by y-terminal sources -- operations that have "ended" (y="end") being improperly followed. COMPOSITION_JUMP involves r-terminal FLOW sources followed by yield/transition targets.

### T3: HEAD Atom Hazard Exposure (C1446)

| HEAD atom | N tokens | Source rate | Target rate | Any hazard | Category |
|-----------|----------|------------|------------|------------|----------|
| **k** | **3,100** | **0.0%** | **0.0%** | **0.0%** | **THERMAL 90.4%** |
| **e** | 7,002 | 0.0% | 2.2% | 2.2% | THERMAL 34.7%, OPERATION 32.2% |
| h | 64 | 3.1% | 0.0% | 3.1% | MONITORING 92.2% |
| i | 1,055 | 0.0% | 0.0% | 0.0% | STAGING 71.2% |
| o | 2,717 | 16.4% | 30.7% | 30.7% | STAGING 30.2%, OPERATION 23.8% |
| a | 3,079 | 22.0% | 44.0% | 66.0% | FLOW 53.7%, TRANSITION 41.0% |
| d | 1,142 | 59.1% | 0.7% | 59.8% | CONTAINMENT 59.1%, MARKING 37.3% |
| t | 416 | 0.0% | 62.5% | 62.5% | FLOW 40.1% |
| l | 1,283 | 66.6% | 0.0% | 66.6% | STAGING 75.9% |
| r | 1,309 | 0.0% | 86.0% | 86.0% | FLOW 76.2% |

**Key findings:**
- **k is completely hazard-immune** (0.0% across 3,100 tokens). The ENERGY_MODULATOR atom never participates in any hazard -- neither as source nor target. This is the most striking result.
- **e is nearly hazard-free** (2.2%, only as target via ee frame). The STABILITY_ANCHOR is almost completely safe.
- **Kernel atoms collectively are the safest domain:** k=0%, e=2.2%, h=3.1% -- all kernel primitives are hazard-depleted.
- **r is the most hazard-exposed** (86.0%, almost entirely as target).
- **a is the most bidirectional hazard atom** (22% source + 44% target = 66% total).

### T4: TERMINAL Atom Hazard Exposure (C1447)

| Terminal | N tokens | Hazard rate | Role |
|----------|----------|------------|------|
| r | 1,962 | **92.58%** | Pure hazard concentrator |
| n | 2,147 | 38.97% | Transition endpoint |
| l | 2,568 | 30.88% | State marker |
| e | 540 | 16.49% | Thermal target (ee only) |
| y | 4,780 | 15.82% | Operation closer |
| k | 909 | 0.0% | Safe thermal |
| m | 289 | 0.0% | Safe batch-close (confirms C1437) |
| h | 1,284 | 0.0% | Transparent monitor |

**TERMINAL hazard partition:**
- **HIGH (>30%):** r, n, l -- these terminals carry the hazard burden
- **LOW (1-20%):** e, y -- moderate risk from specific frames
- **ZERO:** k, m, h -- never in hazard context

### T5: HEAD x TERM Frame Hazard Map (C1448)

High-hazard frames (>50%):

| Frame | N tokens | Hazard rate | Category |
|-------|----------|------------|----------|
| o→bare | 388 | 100.0% | OPERATION |
| d→y | 675 | 99.7% | CONTAINMENT |
| a→l | 527 | 98.86% | FLOW |
| a→r | 687 | 98.54% | FLOW |
| o→r | 455 | 98.02% | FLOW |
| e→e | 151 | 75.5% | THERMAL |
| a→n | 1,272 | 65.57% | TRANSITION |

**k-HEAD complete immunity:** k as HEAD produces 0% hazard across ALL terminal frames:

| k-Frame | N tokens | Hazard rate | Category |
|---------|----------|------------|----------|
| k→bare | 2,083 | 0.0% | THERMAL |
| k→e | 464 | 0.0% | THERMAL |
| k→h | 202 | 0.0% | THERMAL |
| k→d | 93 | 0.0% | FLOW/MARKING |
| k→c | 56 | 0.0% | CONTAINMENT |
| k→o | 92 | 0.0% | STAGING/TRANSITION |

**Even when k combines with normally hazardous terminals (r, n, l), hazard drops to 0%.** k as HEAD has 15 tokens with r-terminal, 0 hazardous. k has 1 token with n-terminal, 0 hazardous. k completely neutralizes hazard in all combinations.

**The massive safe pathway:** e→y has 3,475 tokens at 0% hazard despite both e-HEAD and y-terminal having nonzero hazard rates individually. The cooling-then-end combination is categorically safe.

### T6: PREFIX Channel Hazard Exposure (C1449)

Top 5 highest and lowest hazard PREFIXes:

| PREFIX | N tokens | Hazard rate | Notes |
|--------|----------|------------|-------|
| do | 337 | 73.02% | Highest |
| so | 63 | 52.38% | |
| ko | 48 | 52.08% | |
| to | 316 | 49.57% | |
| BARE | 2,680 | 43.97% | |
| ... | | | |
| sh | 3,150 | 9.88% | Sister LOW |
| lsh | 58 | 6.90% | |
| ct | 60 | 3.33% | Lowest |

**Sister pair analysis:**

| Pair | Rates | Ratio | Gap |
|------|-------|-------|-----|
| ch vs sh | 12.77% vs 9.88% | 1.29x | 2.89pp |
| ok vs ot | 32.11% vs 30.73% | 1.04x | 1.38pp |

Sister pairs show remarkably similar hazard rates, especially ok/ot (ratio 1.04x). The ch/sh difference (1.29x) is modest and consistent with ch's active-test role (C929) carrying slightly more risk than sh's passive-monitor role.

**Actual forbidden violations by PREFIX:** ch=5, sh=2, kch=1, lch=1, ol=1, te=1. Only 6 PREFIXes out of 35+ carry any forbidden violations, with ch accounting for 45% (5/11).

**qo safe channel confirmed:** qo at 17.77% hazard is well below the 25.5% corpus average, consistent with C601 (QO lane zero hazard participation).

### T7: Hazard and Line Position

| Quintile | N tokens | Hazard rate | FLOW+CONTAINMENT |
|----------|----------|------------|------------------|
| Q0 (initial) | 5,022 | 22.2% | 20.8% |
| Q1 | 4,186 | 22.5% | 20.8% |
| Q2 (medial) | 4,141 | 26.6% | 25.0% |
| Q3 | 4,186 | 25.9% | 24.8% |
| Q4 (final) | 5,561 | 29.6% | 27.6% |

Hazard rises from line-initial to line-final (+7.4pp). This is consistent with C1427 (line-final transition/closure profile) and C1428 (THERMAL peaks early then declines).

| Position | N | Hazard rate |
|----------|---|------------|
| Initial | 2,420 | 21.3% |
| Body | 18,262 | 25.9% |
| Final | 2,420 | 26.7% |

Forbidden violations by quintile: Q0=2, Q1=1, Q2=2, Q3=2, Q4=4. Line-final position concentrates forbidden violations (4/11 = 36%).

### T8: Hazard and Two-Level Closure System (C1450)

| Opacity Tier | Terminals | N tokens | Hazard rate | Suffix rate |
|-------------|-----------|----------|------------|-------------|
| OPAQUE | n, y, m | 6,620 | 22.8% | 1.2% |
| SEMI_TRANSPARENT | l, r | 2,926 | **56.5%** | 10.3% |
| TRANSPARENT | h | 1,236 | **0.0%** | 98.6% |

**SEMI_TRANSPARENT terminals concentrate hazard at 2.5x the OPAQUE rate.** These are the l and r terminals that allow partial suffix attachment -- they sit at the hazard/safe boundary. TRANSPARENT terminals (h) are completely hazard-free.

**Suffix status and hazard:**

| Suffix status | N tokens | Hazard rate |
|--------------|----------|------------|
| Suffixed | 11,151 | 14.6% |
| Unsuffixed | 11,945 | 35.6% |

Suffixed tokens have 2.44x lower hazard rate than unsuffixed tokens. The suffix layer provides a hazard-reduction mechanism -- suffix attachment signals safe specification rather than raw hazardous content.

### T9: Hazard and Suffix Mode (C1451)

| Mode | N tokens | Hazard rate | Forbidden violations |
|------|----------|------------|---------------------|
| **Mode A** (specification) | 5,773 | **9.5%** | **0** |
| **Mode B** (continuation) | 17,323 | **30.8%** | **11 (ALL)** |

**Mode B concentrates 100% of forbidden violations.** All 11 actual forbidden pair violations occur in Mode B (bare/continuation) tokens. Mode A (terminal/specification suffixes) has zero violations.

Mode A HEAD distribution: k=28.7%, e=26.9% (kernel-dominant).
Mode B HEAD distribution: e=31.5%, a=16.9%, o=11.7% (yield/arrange-dominant).

**Interpretation:** Mode A lines are specification/parametric -- they describe WHAT to do using kernel-centric vocabulary. Mode B lines are execution/continuation -- they carry out the work using yield/flow/transition vocabulary. Hazard occurs during execution, not specification.

### T10: Modifier Stack and Hazard Modulation

| Modifier | N with | N without | Hazard with | Hazard without | Ratio | Effect |
|----------|--------|-----------|-------------|----------------|-------|--------|
| c (adjust) | 1,277 | 21,819 | 0.0% | 27.0% | 0.0x | **QUENCH** |
| d (mark) | 2,136 | 20,960 | 0.0% | 28.1% | 0.0x | **QUENCH** |
| f (flag) | 91 | 23,005 | 0.0% | 25.6% | 0.0x | **QUENCH** |
| p (pause) | 331 | 22,765 | 0.0% | 25.9% | 0.0x | **QUENCH** |
| s (sequence) | 245 | 22,851 | 0.0% | 25.8% | 0.0x | **QUENCH** |
| **i (iterate)** | **2,052** | **21,044** | **40.6%** | **24.0%** | **1.69x** | **BOOST** |

**All 5 standard modifiers (c, d, f, p, s) completely quench hazard to 0%.** Any compound MIDDLE containing these modifiers has zero hazard exposure. The i-modifier is the sole exception, BOOSTING hazard 1.69x above baseline.

This creates a binary partition:
- **SAFE modifiers** {c, d, f, p, s}: Infrastructure/parametric operators that eliminate hazard
- **HAZARDOUS modifier** {i}: Iteration/cycling operator that amplifies hazard

**MIDDLE length and hazard:**

| Length | N tokens | Hazard rate |
|--------|----------|------------|
| 1 atom | 6,943 | 37.1% |
| 2 atoms | 7,687 | 32.2% |
| 3 atoms | 6,058 | 0.1% |
| 4 atoms | 1,870 | 44.6% |
| 5+ atoms | 472 | 0.0% |

Length 3 and 5+ MIDDLEs have near-zero hazard. Length 4 has elevated hazard (44.6%) driven by iteration compounds (a+ii+n = aiin at 100% hazard). The non-monotonic pattern reflects the modifier quenching effect: 3-atom compounds typically have one modifier which quenches hazard, while 4-atom compounds with ii (iteration) amplify it.

---

## Constraint Summary

| # | Constraint | Tier |
|---|-----------|------|
| C1446 | k-HEAD complete hazard immunity | 2 |
| C1447 | Terminal atom hazard partition (HIGH/LOW/ZERO) | 2 |
| C1448 | HEAD x TERM frame hazard map with k-neutralization | 2 |
| C1449 | PREFIX channel hazard with sister parity | 2 |
| C1450 | Opacity tier hazard gradient (SEMI_TRANSPARENT concentrates) | 2 |
| C1451 | Mode B exclusive forbidden violation concentration | 2 |

---

## Synthesis

### The Hazard Architecture at Atom Resolution

The hazard topology (C109, 17 forbidden transitions) is not a uniform property of the grammar. It has extremely specific atom-level structure:

1. **k-HEAD complete immunity (C1446):** The ENERGY_MODULATOR atom never participates in hazard at any level -- not as HEAD, not in any frame combination, not even when combined with normally-hazardous terminals like r. This is the system's fundamental safety guarantee: energy operations are always safe by construction.

2. **Modifier quenching (T10):** All 5 standard modifiers {c, d, f, p, s} reduce hazard to exactly 0%. Adding parametric specification to any instruction makes it safe. The sole exception is i (iterate), which amplifies hazard 1.69x. **Iteration is the hazardous operation; specification is the safe operation.**

3. **Mode B execution concentrates all violations (C1451):** 100% of forbidden pair violations occur in Mode B (bare/continuation) tokens. Mode A (specification) has zero violations. This extends the Mode A/B distinction from suffix typing to hazard: specification lines are safe, execution lines carry risk.

4. **The r-terminal concentrates hazard (C1447):** r-terminal is 92.58% hazardous, acting as the primary hazard concentrator. Combined with HEAD analysis, the hazard frames are almost entirely:
   - a→r (98.5%, FLOW)
   - o→r (98.0%, FLOW)
   - a→l (98.9%, FLOW)
   - d→y (99.7%, CONTAINMENT)

5. **SEMI_TRANSPARENT terminals at the hazard boundary (C1450):** The l and r terminals (C1440 semi-transparent tier) concentrate hazard at 56.5% -- 2.5x the opaque tier rate. These terminals allow partial suffix attachment, sitting exactly at the hazard/safe boundary. Fully transparent terminals (h) are 0% hazard.

6. **Sister pairs show hazard parity (C1449):** ch/sh (ratio 1.29x) and ok/ot (ratio 1.04x) differ minimally in hazard exposure. Sister choice is NOT a hazard-modulation mechanism -- it modulates precision/tolerance (C929) orthogonally to hazard.

### Connecting to the Interpretive Framework

This analysis reveals why the system is safe by construction:
- **Energy operations (k) are inherently safe** -- you cannot create a hazardous instruction by heating
- **Specification (modifiers, Mode A) is inherently safe** -- describing what to do is never dangerous
- **Execution (Mode B, bare MIDDLEs) carries the risk** -- actually doing the work is where hazard concentrates
- **The r-terminal (FLOW/respond) and iteration (i-modifier) are the two hazard amplifiers** -- flow responses and cycling are where things go wrong

This matches the distillation interpretation perfectly: the most dangerous moments in distillation are when material is flowing (r-terminal) and when cycles are repeating (i-modifier), not when you are adjusting the fire (k-HEAD) or specifying parameters (c/d/f/p/s modifiers).

---

## Dependencies

- C109 (5 failure classes, 17 forbidden transitions) - Tier 0
- C541 (hazard class enumeration)
- C1000 (hub MIDDLE sub-roles)
- C1280 (hazard concentrates in FLOW/CONTAINMENT)
- C1393-C1394 (instruction encoding architecture)
- C1437 (m-terminal hazard exclusion)
- C1440 (three-tier terminal opacity gradient)

## Files

- `phases/HAZARD_ATOM_DECOMPOSITION/scripts/hazard_atom_decomposition.py`
- `phases/HAZARD_ATOM_DECOMPOSITION/results/hazard_atom_decomposition.json`
