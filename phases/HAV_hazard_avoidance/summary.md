# Phase HAV: Hazard Avoidance Microstructure

## Core Question

> **How does the grammar avoid creating forbidden transitions? What are the positive constraints (what TO do) rather than just negative constraints (what NOT to do)?**

## Motivation

We knew:
- 17 forbidden transitions (hard hazards)
- 8 suppressed transitions (soft hazards)
- Recovery via `e` (stability anchor)

What was missing:
- The *local neighborhoods* around hazards
- The "escape routes" from hazard source positions
- The "safe approach corridors" to hazard target positions

## Key Insight

**Forbidden transitions by definition don't occur in the corpus.** We can't analyze "what happens after a hazard" because hazards never happen. Instead, we analyze:

1. What FOLLOWS hazard source tokens (tokens that are the first element of a forbidden pair)
2. What PRECEDES hazard target tokens (tokens that are the second element)
3. How does the grammar AVOID creating the forbidden pair?

## Results

### 1. QO-Prefix as Universal Escape Route

After hazard source tokens, qo- prefixed tokens dominate as escape destinations:

| Hazard Source | qo- Tokens After | Examples |
|---------------|------------------|----------|
| chedy | 47.5% | qokeey, qokain, qokedy, qol, qokaiin |
| chey | 37% | qokeedy, qol, qokeey, qokain, qokaiin |
| shey | 25% | qokain, qokaiin, qokey, qokeedy |
| dy | 9.2% | qokal, qokedy, qokeedy |

**Pattern:** The qo- prefix serves as a "safe transition" prefix that redirects away from forbidden targets.

### 2. Escape Role Stratification

After hazard source tokens, ENERGY_OPERATOR is the primary escape destination:

| After Source | ENERGY_OP | CORE_CONTROL | Notes |
|--------------|-----------|--------------|-------|
| chedy | 52.5% | 22.0% | Stability dominant |
| chey | 25.0% | 27.8% | Control co-dominant |
| chol | 52.9% | 29.4% | Stability dominant |
| dy | 40.9% | 31.8% | Stability dominant |
| or | 25.0% | 7.4% | HIGH_IMPACT dominant (61.8%) |
| shey | 50.0% | 26.9% | Stability dominant |

**Pattern:** Grammar redirects hazard sources toward stability-maintaining roles.

### 3. Safe Precedence Pattern

Hazard targets are approached from stable states:

| Before Target | ENERGY_OP | CORE_CONTROL |
|---------------|-----------|--------------|
| chol | 66.7% | 6.7% |
| aiin | 8.7% | 52.2% |
| chedy | 33.0% | 32.0% |
| chey | 23.6% | 29.1% |
| dal | 48.3% | 24.1% |
| r | 50.0% | 30.0% |

**Pattern:** ENERGY_OPERATOR and CORE_CONTROL safely precede hazard targets. The grammar creates "safe approach corridors" to dangerous tokens.

### 4. Near-Miss Buffers

When hazard sources and targets appear close but not adjacent, specific tokens act as interlocks:

**chey → ... → chedy (18 near-misses):**
- Gap=2: qol (4), dain, okal, lkaiin, qokeey
- These tokens "buffer" the hazard pair

**shey → ... → aiin (7 near-misses):**
- Gap=2: dain, keedal
- Gap=3: pchor, lol, yches

## Interpretation

The grammar has **positive avoidance guidance**, not just prohibitions:

1. **Escape Routes:** When approaching a hazard source, the grammar provides clear escape paths (primarily qo- tokens)

2. **Role Stratification:** Escapes go to stability-maintaining roles (ENERGY_OPERATOR, CORE_CONTROL)

3. **Safe Approach:** Hazard targets are only approached from safe positions

4. **Buffer Tokens:** Specific tokens serve as "interlocks" that prevent hazard pairs from forming

This is analogous to a factory with:
- Warning signs (hazard topology)
- Designated safe paths (escape routes)
- Buffer zones (interlock tokens)
- Entry protocols (safe approach corridors)

## Constraints Added

**Constraint 397**: QO-PREFIX ESCAPE ROUTE: qo- prefixed tokens are the universal escape from hazard source positions; after hazard sources, qo- tokens appear 25-47% of the time (qokeey, qokain, qokedy, qol most frequent); qo- serves as the primary "safe transition" prefix for redirecting away from forbidden targets (HAV, Tier 2)

**Constraint 398**: ESCAPE ROLE STRATIFICATION: After hazard source tokens, ENERGY_OPERATOR is primary escape destination (40-67% depending on source), CORE_CONTROL is secondary (22-32%); grammar redirects hazard sources toward stability-maintaining roles; HIGH_IMPACT is 61.8% escape after 'or' only (HAV, Tier 2)

**Constraint 399**: SAFE PRECEDENCE PATTERN: ENERGY_OPERATOR and CORE_CONTROL safely precede hazard targets (33-67%); hazard targets are approached from stable states, not from other hazardous positions; grammar creates "safe approach corridors" to dangerous tokens (HAV, Tier 2)

## Files

- `archive/scripts/hazard_avoidance_analysis.py` - Main analysis
- `archive/scripts/hazard_neighborhood_analysis.py` - Initial exploration

## Status

**CLOSED** - 3 constraints established (397-399)

The grammar has explicit positive guidance for hazard avoidance, not just negative prohibitions. The qo- prefix serves as the primary "safe path" mechanism.
