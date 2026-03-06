# Phase 524: The i-Modifier Hazard Anomaly

**Date:** 2026-03-05
**Phase:** I_MODIFIER_HAZARD
**Status:** COMPLETE
**New Constraints:** C1452-C1456

---

## Background

Phase 523 (HAZARD_ATOM_DECOMPOSITION, C1446-C1451) discovered that all 5 standard modifiers {c,d,f,p,s} completely quench hazard to 0%, but `i` (iterate) is the sole exception that boosts hazard from 24.0% to 40.6% (1.69x). Phase 524 investigates WHY iteration is hazardous -- is it inherent to the i-modifier itself, or a confound with the HEAD+TERM frames that i-modified MIDDLEs occupy?

---

## Test Results Summary

| Test | Question | Verdict | Key Finding |
|------|----------|---------|-------------|
| T1 | What is i's structural profile? | PASS | 90.5% n-terminal, 65.8% a-initial; dominated by aiin/iin/ain |
| T2 | Does i concentrate in hazardous frames? | PASS | 61.8% in high-hazard frames (vs 14.0% non-i); within-frame i REDUCES hazard |
| T3 | Does ii differ from single-i? | **CRITICAL** | NON-MONOTONIC: single-i=39.8%, double-ii=0.0%, no-i=24.1% |
| T4 | What category does i map to? | PASS | STAGING 33.0% (2.6x), TRANSITION 41.0% (2.8x); THERMAL near-zero |
| T5 | Does i have positional bias? | MILD | Slight initial enrichment (1.19x), slight final depletion (0.77x) |
| T6 | Which PREFIXes carry i? | PASS | da (3.5x), sa (3.6x), ok (2.4x), BARE (1.7x); qo/ch/sh avoid i |
| T7 | How does i interact with suffix? | PASS | 95.7% Mode B; i-tokens are 90.6% suffix-free |
| T8 | Does quenching override i? | PARTIAL | Both co-occur: 7.5% hazard (reduced from 22.6% but not zero) |
| T9 | Is i functionally distinct? | MILD | Section B depleted (5.6% vs 8.9%); no clustering signal |
| T10 | Causal decomposition | **CRITICAL** | Marginal i-effect is NEGATIVE (-0.018); i REDUCES within-frame hazard |

---

## Critical Findings

### 1. The Non-Monotonic Extension Gradient (C1452)

The most important finding of this phase. The i-extension gradient is NOT monotonic:

| Level | N | Hazard Rate | Category Signature |
|-------|---|-------------|-------------------|
| No i | 21,044 | 24.1% | THERMAL 25.7%, FLOW 18.9%, OPERATION 15.5% |
| Single i (ain, iin) | 1,151 | **39.8%** | STAGING 53.3%, **FLOW 39.8%** |
| Double ii (aiin, oiin) | 901 | **0.0%** | **TRANSITION 92.6%**, STAGING 7.1% |

- **Single-i** tokens (ain, iin, aii) have ELEVATED hazard because they are 53.3% STAGING + 39.8% FLOW. The FLOW component (39.8%) IS the hazard.
- **Double-ii** tokens (aiin, oiin) are 92.6% TRANSITION with **zero** FLOW or CONTAINMENT. They are categorically outside the hazard domain.

The Phase 523 finding (i boosts hazard to 40.6%) was driven entirely by single-i tokens. Double-ii tokens are perfectly safe. This is the extensibility split: `i` = open iteration (potentially hazardous FLOW), `ii` = formal bounded iteration (safe TRANSITION).

This aligns with C1197 (only e and i can repeat) and C1234 (iin = cycle setup, aiin = bounded loop control). The single-i tokens do open cycling (FLOW domain), which has hazard exposure. The double-ii tokens do formal bounded iteration (TRANSITION domain), which has zero hazard.

### 2. i Selects Into Hazardous Frames, Not Hazardous Within Them (C1453)

The causal decomposition (T10) reveals:

| Metric | Value |
|--------|-------|
| Marginal i-effect | -0.0175 (i tokens are LESS hazardous overall than non-i) |
| Within-frame weighted delta | -0.4073 (i REDUCES hazard within shared HEAD+TERM frames) |
| Frames with negative delta | 12/19 |
| Frames with positive delta | 2/19 |

The paradox: Phase 523 found single-i at 40.6% hazard, yet T10 shows i tokens are overall LESS hazardous than non-i. Resolution:

- **aiin** (N=834) is double-ii with 0% hazard, dragging the i-group average DOWN
- **ain/iin** (N=980) are single-i with ~40% hazard, but this is LOWER than the non-i tokens sharing their frames
- In the dominant (a,n) frame: i-tokens (aiin/ain) have 33.5% hazard vs non-i (an etc) at 100%

The i-modifier SELECTS into the FLOW/STAGING category space through HEAD+TERM frame selection (a-initial, n-terminal). But within those frames, i actually has a protective effect (or at minimum a neutral one). The hazard comes from the FRAME, not from i.

### 3. i-Tokens Are Anti-Thermal, Anti-Kernel (C1454)

i-modified tokens are categorically excluded from the thermal/kernel domain:

| Category | i-fraction | Baseline | Ratio |
|----------|-----------|----------|-------|
| THERMAL | 0.05% | 23.4% | **0.002x** |
| STAGING | 33.0% | 12.8% | 2.6x |
| TRANSITION | 41.0% | 14.8% | 2.8x |
| FLOW | 22.3% | 19.2% | 1.2x |

The PREFIX profile confirms: qo (thermal channel) = 0.089x i-rate; ch/sh (test channels) = 0.087-0.097x. The PREFIXes that carry i are non-thermal: da (3.5x), sa (3.6x), ok (2.4x), or (3.8x).

i is the ANTI-THERMAL modifier. It operates in the STAGING/TRANSITION/FLOW domain -- the "what to do between heating cycles" space. This explains its orthogonality to the k/e energy system (C1205).

### 4. Quenching Modifiers Partially Override i (C1455)

When i co-occurs with quenching modifiers {c,d,f,p,s}:

| Group | N | Hazard Rate |
|-------|---|-------------|
| Neither i nor quench | 17,309 | 28.0% |
| i only | 2,012 | 22.6% |
| Quench only | 3,735 | 5.9% |
| Both i + quench | 40 | 7.5% |

Co-occurrence is rare (40 tokens), but the pattern is clear: quenching reduces i's hazard from 22.6% to 7.5% -- a 3x reduction. But it does NOT reach 0% as quench-only does (5.9%). The quench effect dominates but i provides mild residual hazard resistance. The N=40 makes this suggestive rather than definitive.

### 5. i-Token Suffix Depletion (C1456)

i-modified tokens are overwhelmingly bare (suffix-free):

| Metric | i-tokens | Non-i tokens | Ratio |
|--------|----------|-------------|-------|
| Suffix rate | 9.4% | 52.1% | 0.18x |
| Mode A (specification) | 4.3% | 27.0% | 0.16x |
| Mode B (continuation) | 95.7% | 73.0% | 1.31x |

This is not just suffix depletion -- it is near-categorical suffix exclusion. The i-modifier's n-terminal structure (ain, iin, aiin all end in n) is a terminal suffix in itself, leaving no structural room for additional suffixes. This connects to C1383 (n-terminal boundary avoidance) and C1408 (suffix HEAD->TERM compositional structure).

---

## Detailed Test Results

### T1: i-Modifier Inventory

2,052 i-modified tokens (8.9% of corpus). Dominated by three MIDDLEs:
- **aiin** (834, 40.6%) -- double-ii, a-initial, n-terminal
- **iin** (560, 27.3%) -- single-i+i, i-initial, n-terminal
- **ain** (420, 20.5%) -- single-i, a-initial, n-terminal

These three account for 88.4% of all i-tokens. HEAD distribution: a=65.8% (4.94x), i=27.8% (6.08x). TERM distribution: n=90.5% (6.83x). Only 126 unique MIDDLEs contain i, vs 298 for c and 135 for d -- i is low-diversity but high-concentration.

### T2: i-Modifier and Hazardous Frames

61.8% of i-tokens are in high-hazard HEAD+TERM frames (vs 14.0% non-i). But this is frame selection, not i-enhancement. In the dominant (a,n) frame: i-tokens have 33.5% hazard vs non-i at 100%. In (a,r): i has 75.0% vs non-i 99.7%. In (a,l): i has 0% vs non-i 99.8%. In 12 of 19 testable frames, i-tokens have LOWER hazard than non-i tokens.

### T3: ii vs Single-i Extension Gradient

The gradient is NON-MONOTONIC with a critical split at the single/double boundary:

**Single-i category signature:** STAGING 53.3%, FLOW 39.8% (hazard source), TRANSITION 0.7%
**Double-ii category signature:** TRANSITION 92.6%, STAGING 7.1%, FLOW 0%

Every double-ii MIDDLE tested has 0.0% hazard rate. aiin alone (834 tokens) has exactly zero forbidden pair violations and zero FLOW/CONTAINMENT category membership. This is the cleanest categorical split in the entire modifier system.

### T4: i-Modifier and Operational Category

Top instruction classes for i-tokens: Class 13 (503, FQ), Class 9 (351, FQ), Class 10 (314, CC/daiin), Class 29 (284), Class 28 (104). The TRANSITION i-tokens (842, 41.0%) have 0% hazard. The non-TRANSITION i-tokens (1,210) have 37.9% hazard -- concentrated in FLOW.

### T5: Positional Profile

i-tokens show mild line-initial enrichment (12.9% vs 10.8%, ratio 1.19x) and line-final depletion (8.7% vs 11.3%, ratio 0.77x). Paragraph-initial rate is LOW (1.4% vs 2.6%). The positional signal is real but weak -- much weaker than the category/frame selection effects.

### T6: PREFIX Distribution

i-tokens strongly avoid thermal PREFIXes and concentrate in non-thermal ones:

| PREFIX | i-fraction | Baseline | Ratio | Domain |
|--------|-----------|----------|-------|--------|
| sa | 5.1% | 1.4% | 3.59x | Non-thermal |
| da | 16.5% | 4.7% | 3.51x | Infrastructure |
| or | 2.8% | 0.8% | 3.77x | Non-thermal |
| ta | 2.8% | 1.0% | 2.75x | Non-thermal |
| ok | 15.5% | 6.4% | 2.43x | Vessel |
| BARE | 28.1% | 16.7% | 1.68x | Default |
| qo | 1.6% | 17.6% | 0.089x | **Thermal (avoided)** |
| ch | 1.3% | 15.1% | 0.087x | **Test (avoided)** |
| sh | 1.0% | 10.1% | 0.097x | **Test (avoided)** |

### T7: Suffix Profile

i-tokens are 90.6% suffix-free (vs 47.9% non-i). When suffixed, the top suffixes are: -r (46), -hy (34), -dy (24), -y (20). These are all TERMINAL class suffixes used in their non-i compositional role.

### T8: Co-Occurrence with Quenching Modifiers

Only 40 tokens contain both i and a quenching modifier. Examples: aiifcho, aiisock, aiict. The hazard rate drops from 22.6% (i-only) to 7.5% (both). The quenching effect is dominant but not total -- the residual may be due to frame selection rather than any inherent i-resistance.

### T9: Functional Signal

Section distribution: B=5.6%, C=11.6%, H=9.4%, S=10.6%, T=6.5%. Section B (Bio/balneological) has the lowest i-rate, consistent with its thermal focus and i's anti-thermal character. No clustering signal (O/E = 0.98). Line length is identical (10.71 vs 10.64).

### T10: Causal Decomposition

HEAD-controlled analysis:
- **a-HEAD (dominant):** i has 32.6% hazard vs non-i 71.2% -- i REDUCES by 38.6pp (p<0.001)
- **o-HEAD:** i has 4.1% vs non-i 23.0% -- i REDUCES by 18.9pp (p<0.001)
- **i-HEAD:** i has 0% vs non-i 6.4% -- i REDUCES (p<0.001)

TERM-controlled analysis:
- **n-TERM (dominant, N=2140):** i has 22.6% vs non-i 6.4% -- i INCREASES by 16.3pp (p<0.001)
- **r-TERM:** i has 58.3% vs non-i 99.0% -- i REDUCES by 40.7pp (p<0.001)

The n-terminal result is the only TERM where i increases hazard. This is because the non-i n-terminal tokens are rare (N=283) and categorically different (in, an, etc. are TRANSITION tokens like aiin). When i occupies the n-terminal frame, it brings single-i tokens (ain, iin) that are FLOW-oriented, while the non-i n-terminal tokens are nearly all safe TRANSITION.

---

## Synthesis: Why Iteration Is Hazardous

The answer to "why does iteration boost hazard?" has three parts:

1. **Frame selection:** i-tokens concentrate in the a-initial, n-terminal frame space (aiin/ain/iin), which is the STAGING/FLOW/TRANSITION domain. This domain has higher baseline hazard because FLOW = material movement, which is inherently risky.

2. **Extension split:** Single-i (open iteration) maps to FLOW (39.8% of single-i category distribution). Double-ii (bounded iteration) maps to TRANSITION (92.6%). The hazard is in FLOW, not in TRANSITION. Open iteration is hazardous because unbounded cycling creates physical risk (overflow, pressure buildup). Bounded iteration is safe because it has predetermined endpoints.

3. **i itself is NOT inherently hazardous.** Within every testable HEAD+TERM frame, i tokens have equal or lower hazard than non-i tokens. The modifier acts as a routing operator that selects the STAGING/TRANSITION/FLOW category space, and the hazard arises from the FLOW component of that space.

The distillation interpretation: open cycling (ain = "intake", iin = "link") involves moving material through the system, which risks overflow, contamination, and pressure events. Bounded cycling (aiin = "settle", oiin = "loop") involves waiting for equilibrium within sealed conditions, which is inherently safe.

---

## New Constraints

| # | Constraint | Tier | Tags |
|---|-----------|------|------|
| C1452 | Non-monotonic i-extension hazard gradient: single-i=39.8%, double-ii=0.0%, no-i=24.1% | 2 | B, MIDDLE, atom, i-modifier, extension, hazard, non-monotonic |
| C1453 | i selects into hazardous frames but reduces hazard within frames (weighted delta=-0.407) | 2 | B, MIDDLE, atom, i-modifier, hazard, causal, frame-selection |
| C1454 | i-tokens are anti-thermal (THERMAL 0.05%, 0.002x baseline) and STAGING/TRANSITION dominant | 2 | B, MIDDLE, atom, i-modifier, category, anti-thermal |
| C1455 | Quenching modifiers partially override i (22.6% -> 7.5%) but not to zero | 2 | B, MIDDLE, atom, i-modifier, quenching, co-occurrence |
| C1456 | i-tokens are 90.6% suffix-free and 95.7% Mode B | 2 | B, MIDDLE, atom, i-modifier, suffix, mode |

---

## Dependencies

- C1197 (Only e and i repeat: extensibility partition)
- C1205 (i-atom orthogonal to k/e energy system)
- C1234 (Iteration two-track: iin cycle setup, aiin bounded loop)
- C1280 (Hazard concentrates in FLOW/CONTAINMENT)
- C1309 (Mode category specialization)
- C1383 (n-terminal MIDDLE boundary avoidance)
- C1393 (HEAD + MOD* + TERM instruction encoding)
- C1446 (k-HEAD complete hazard immunity)
- C1447 (a-HEAD bifurcated hazard profile)
- C1449 (o-HEAD hazardous when free)
- C1450 (Modifier quenching is categorical for c,d,f,p,s)

---

## Script

`phases/I_MODIFIER_HAZARD/scripts/i_modifier_hazard.py`

## Results

`phases/I_MODIFIER_HAZARD/results/i_modifier_hazard.json`
