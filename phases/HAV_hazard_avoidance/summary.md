# Phase HAV: Hazard Avoidance Microstructure

## Status: CLOSED (REVISED 2026-01-31)

> **REVISION NOTE:** Original interpretation of "escape routes" was incorrect.
> Later constraints (C601, C645) established that QO is DEPLETED near hazards
> and CHSH handles hazard recovery. The measurements below are valid, but the
> "escape" interpretation has been corrected to "lane transition pattern."

## Core Question

> **What tokens follow hazard source positions? What tokens precede hazard target positions?**

## Motivation

We knew:
- 17 forbidden transitions (hard hazards)
- 8 suppressed transitions (soft hazards)
- Recovery via `e` (stability anchor, C105)

What was missing:
- The *local neighborhoods* around hazards
- What follows hazard source tokens
- What precedes hazard target tokens

## Key Insight

**Forbidden transitions by definition don't occur in the corpus.** We analyze:

1. What FOLLOWS hazard source tokens (tokens that are the first element of a forbidden pair)
2. What PRECEDES hazard target tokens (tokens that are the second element)

## Results

### 1. QO-PREFIX Follows Hazard Source Tokens

After hazard source tokens, qo-prefixed tokens appear at elevated rates:

| Hazard Source | qo- Tokens After | Examples |
|---------------|------------------|----------|
| chedy | 47.5% | qokeey, qokain, qokedy, qol, qokaiin |
| chey | 37% | qokeedy, qol, qokeey, qokain, qokaiin |
| shey | 25% | qokain, qokaiin, qokey, qokeedy |
| dy | 9.2% | qokal, qokedy, qokeedy |

**Observation:** The hazard sources (chedy, chey, shey) are CHSH-lane tokens. QO following them reflects the normal CHSH→QO lane transition pattern (C643), not hazard avoidance.

### 2. Role Distribution After Hazard Sources

After hazard source tokens, ENERGY_OPERATOR and CORE_CONTROL appear:

| After Source | ENERGY_OP | CORE_CONTROL | Notes |
|--------------|-----------|--------------|-------|
| chedy | 52.5% | 22.0% | |
| chey | 25.0% | 27.8% | |
| chol | 52.9% | 29.4% | |
| dy | 40.9% | 31.8% | |
| or | 25.0% | 7.4% | HIGH_IMPACT dominant (61.8%) |
| shey | 50.0% | 26.9% | |

**Observation:** These rates reflect baseline role frequencies after CHSH tokens, not special "escape" behavior.

### 3. Tokens Preceding Hazard Targets

Hazard targets are preceded by:

| Before Target | ENERGY_OP | CORE_CONTROL |
|---------------|-----------|--------------|
| chol | 66.7% | 6.7% |
| aiin | 8.7% | 52.2% |
| chedy | 33.0% | 32.0% |
| chey | 23.6% | 29.1% |
| dal | 48.3% | 24.1% |
| r | 50.0% | 30.0% |

### 4. Near-Miss Buffers

When hazard sources and targets appear close but not adjacent, intervening tokens act as buffers:

**chey → ... → chedy (18 near-misses):**
- Gap=2: qol (4), dain, okal, lkaiin, qokeey

**shey → ... → aiin (7 near-misses):**
- Gap=2: dain, keedal
- Gap=3: pchor, lol, yches

## Corrected Interpretation

~~The grammar has **positive avoidance guidance**, not just prohibitions.~~

**REVISED (2026-01-31):** The pattern observed is the **CHSH→QO lane transition**, not hazard escape:

1. **Hazard sources are CHSH tokens:** chedy, chey, shey are ch/sh-prefixed (CHSH lane)
2. **QO follows CHSH naturally:** C643 documents rapid QO-CHSH alternation
3. **When hazards are NEARBY, QO is depleted:** C645 shows post-hazard is 75% CHSH, QO at 0.55x
4. **CHSH handles hazard recovery:** CHSH MIDDLEs are 68.7% e-content (stability anchor)

The correct model:
- CHSH (e-rich) operates in hazard-adjacent contexts and handles recovery
- QO (k-rich) operates in hazard-distant contexts
- QO following hazard sources reflects lane transition, not escape

## Constraints (REVISED)

**Constraint 397**: ~~QO-PREFIX ESCAPE ROUTE~~ **QO-PREFIX POST-SOURCE FREQUENCY**: After hazard source tokens (which are CHSH-lane tokens), qo-prefixed tokens appear 25-47% of the time. This reflects the normal CHSH→QO lane transition pattern (C643), not hazard escape. When hazards are actually nearby, QO is depleted (C645). (HAV, Tier 2, REVISED 2026-01-31)

**Constraint 398**: ~~ESCAPE ROLE STRATIFICATION~~ **POST-SOURCE ROLE DISTRIBUTION**: After hazard source tokens, ENERGY_OPERATOR appears 40-67%, CORE_CONTROL 22-32%. This reflects baseline role frequencies after CHSH tokens. Actual hazard recovery is handled by CHSH (75.2% post-hazard per C645). (HAV, Tier 2, REVISED 2026-01-31)

**Constraint 399**: SAFE PRECEDENCE PATTERN: ENERGY_OPERATOR and CORE_CONTROL precede hazard targets (33-67%). Hazard targets are approached from common operational contexts. (HAV, Tier 2)

## Files

- `archive/scripts/hazard_avoidance_analysis.py` - Main analysis
- `archive/scripts/hazard_neighborhood_analysis.py` - Initial exploration

## Cross-References (Added 2026-01-31)

| Constraint | Relationship |
|------------|--------------|
| C601 | QO never participates in hazards (0/19) |
| C643 | QO-CHSH rapid alternation pattern |
| C645 | CHSH 75.2% post-hazard, QO depleted 0.55x |
| C105 | e = STABILITY_ANCHOR, dominates recovery |

## Revision History

- **Original:** Interpreted as "escape routes" to QO
- **2026-01-31:** Corrected to "lane transition pattern" per C601, C643, C645
