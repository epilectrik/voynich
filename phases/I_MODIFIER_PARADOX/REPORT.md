# Phase 534: i-Modifier Paradox Resolution

**Date:** 2026-03-05
**Status:** COMPLETE
**Constraints:** C1480-C1482

---

## Research Question

The i-modifier exhibits a Simpson's paradox (C1452-C1456): marginally it appears to boost hazard (1.69x crude ratio), but conditionally within each HEAD x TERMINAL frame it protects (weighted delta -0.407, 12/19 frames protective). Phase 533 discovered that i demands a-HEAD at 88.6% of headed tokens (C1479), and a-HEAD is the primary hazard carrier at 66.0% forbidden rate (C1477). This phase closes the loop by providing the complete mechanistic explanation.

## Key Findings

### T1: Causal Chain Verification

i selects a-HEAD at 53.15% of ALL i-tokens (88.6% of headed i-tokens, consistent with C1479). Non-i modifiers distribute across HEADs: d favors e-HEAD (60.4%), c favors headless (46.4%), p favors o-HEAD (41.2%). i's concentration in a-HEAD is uniquely extreme.

HEAD hazard rates (category-based: FLOW + CONTAINMENT):
- k: 3.3% (near-immune, consistent with C1476)
- e: 8.7%
- o: 22.5%
- a: **54.2%** (highest headed, consistent with C1477)
- t: 86.9% (highest overall)
- headless: 27.6%

### T2: Counterfactual Analysis

| Scenario | Hazard Rate | Interpretation |
|----------|-------------|----------------|
| i actual | 17.88% | What we observe |
| Non-i modified | 24.77% | i is SAFER than other modifiers |
| i with avg HEAD dist | 10.12% | What i would be without a-HEAD bias |
| i with non-i HEAD dist | 17.56% | What i would be with other modifiers' HEAD dist |

HEAD selection inflates i's hazard by 7.8 percentage points (from 10.1% to 17.9%). But i is still NET SAFER than non-i modified tokens (17.9% vs 24.8%), because the conditional protection within each HEAD more than compensates for the selection effect.

### T3: Within a-HEAD Frame Protection

All 5 testable a-HEAD frames show i as protective:

| Frame (a→X) | i hazard | non-i hazard | delta | N(i) | p-value |
|-------------|----------|-------------|-------|------|---------|
| a→n | 33.5% | 100.0% | -0.665 | 1,254 | <0.001 |
| a→r | 75.0% | 99.7% | -0.247 | 8 | <0.001 |
| a→l | 0.0% | 99.8% | -0.998 | 5 | <0.001 |
| a→bare | 5.5% | 8.3% | -0.028 | 253 | 0.278 |
| a→h | 0.0% | 15.4% | -0.154 | 8 | 0.243 |

Weighted delta within a-HEAD = **-0.536** (stronger than C1452's -0.407 across all HEADs).

The a→n frame dominates: 1,254 of 1,528 i-modified a-HEAD tokens (82.1%) are n-terminal.

### T4: Double-ii Gradient

Within a-HEAD, hazard follows a monotonic i-count gradient:

| i-count | N | Hazard | n-terminal% | Category |
|---------|---|--------|-------------|----------|
| 0 (no-i) | 1,551 | 79.3% | 1.2% | FLOW 78.1% |
| 1 (single-i) | 641 | 68.6% | 65.5% | FLOW 68.6% |
| 2 (double-ii) | 887 | **0.0%** | **94.0%** | TRANSITION 94.0% |

Double-ii is 0.0% hazardous across ALL terminals tested (n=834, bare=48, r=2, h=2, l=1 — all zero). The mechanism is progressive n-terminal lock-in: each i-count pushes more tokens toward n-terminal TRANSITION, away from r/l-terminal FLOW.

### T5: Modifier Comparison within a-HEAD

Bare a-HEAD hazard = 83.6%. All modifiers are protective:

| Modifier | N | Hazard | Delta from bare | Quench to 0? |
|----------|---|--------|-----------------|-------------|
| f | 6 | 0.0% | -0.836 | YES |
| s | 16 | 6.3% | -0.774 | No |
| d | 27 | 11.1% | -0.725 | No |
| p | 9 | 11.1% | -0.725 | No |
| c | 28 | 17.9% | -0.658 | No |
| **i** | **1,528** | **28.8%** | **-0.548** | No |

i is NOT the strongest quencher — but it is by far the MOST COMMON modifier within a-HEAD (1,528 vs 86 total for c+d+f+p+s). This explains C1477's finding that "modifier quenching fails for a-HEAD" in aggregate: the aggregate is dominated by i, which reduces but doesn't eliminate hazard. The rare quench modifiers DO work in a-HEAD, they're just extremely uncommon there.

### T6: Full Effect Decomposition

Oaxaca-Blinder decomposition:
- Total effect (i vs non-i): **-0.069** (i is net safer)
- Selection effect: **+0.319** (a-HEAD concentration inflates)
- Conditional effect: **-0.388** (within-HEAD protection)

The selection effect inflates hazard, but the conditional protection MORE than compensates. The "1.69x marginal inflation" from C1452 compared i to ALL non-i tokens; comparing to other MODIFIED tokens shows i is 28% safer (17.9% vs 24.8%).

### T7: Operational Profile Transformation

i within a-HEAD produces a complete operational transformation:

| Metric | a-HEAD with i | a-HEAD without i |
|--------|---------------|------------------|
| Dominant terminal | n (82.1%) | r (43.8%) |
| Dominant category | TRANSITION (66.2%) | FLOW (78.1%) |
| Mean line position | 0.536 (medial) | 0.627 (late) |
| Line-final rate | 8.6% | 21.8% |
| Suffix rate | 17.7% | 14.7% |
| Top MIDDLEs | aiin, ain, ai | ar, al, am |

i converts a-HEAD from line-final FLOW operations (ar, al — routing/closure) to medial TRANSITION operations (aiin, ain — iteration/cycling).

### T8: Protection Mechanism

- Terminal redirection: **FALSE** — i does NOT avoid high-hazard terminals (82.9% in high-hazard terms)
- Category redirection: **TRUE** — i changes the CATEGORY of a→n from CONTAINMENT to TRANSITION
- Double-ii exclusive safe frame: **TRUE** — ii creates a terminal-locked TRANSITION pathway

The mechanism is CATEGORICAL, not positional. i doesn't move tokens to safe terminals — it changes what happens AT the same terminal.

## Constraints Produced

| ID | Statement | Tier |
|----|-----------|------|
| C1480 | i-modifier Simpson's paradox full resolution via HEAD domain selection | 2 |
| C1481 | i-modifier terminal transformation within a-HEAD (n-terminal 82% with i) | 2 |
| C1482 | Double-ii safety via TRANSITION-locked n-terminal (monotonic i-count gradient) | 2 |

## Relationship to Prior Work

| Constraint | Status | Note |
|------------|--------|------|
| C1452 | **CLOSED** | Non-monotonic gradient explained by HEAD selection |
| C1453 | **CONFIRMED** | Within-frame protection confirmed at a-HEAD level |
| C1454 | **CLOSED** | Frame selection mechanism identified as a-HEAD affinity |
| C1455 | **CONFIRMED + EXPLAINED** | Double-ii safety = terminal-locked TRANSITION via n |
| C1456 | **CONFIRMED** | i-count determines frame (a→n TRANSITION) not hazard directly |
| C1473 | **USED** | Modifier avoidance is frame incompatibility — i's a-HEAD selectivity |
| C1475 | **USED** | HEAD domain taxonomy — a-HEAD as FLOW+TRANSITION domain |
| C1477 | **REFINED** | a-HEAD quench resistance is aggregate effect of i dominance; rare modifiers DO quench |
| C1479 | **USED** | HEAD-modifier selectivity partition — i monopolizes a-HEAD |

## Verdict

The i-modifier Simpson's paradox is **FULLY RESOLVED**. The complete causal chain:

1. i demands a-HEAD at 88.6% of headed tokens (C1479)
2. a-HEAD is the primary hazard carrier (C1477)
3. This inflates i's marginal hazard via selection effect (+0.319)
4. But within a-HEAD, i protects via terminal transformation (-0.388 conditional)
5. Net result: i is 28% SAFER than other modifiers (17.9% vs 24.8%)
6. Double-ii achieves categorical safety (0.0%) via complete n-terminal lock-in
7. The monotonic gradient (79.3% → 68.6% → 0.0%) reflects progressive terminal capture

The paradox was an artifact of comparing i-tokens to ALL non-i tokens (which includes unmodified tokens in safe HEADs like k and e). When compared to appropriately matched tokens (other modifiers, or same-HEAD), i is consistently protective.
