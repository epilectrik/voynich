# Phase LRM: Local Role Motifs

## Core Question

> **Are there recurring role-level patterns that reveal the "grammar skeleton"?**

We know from TRANS phase that 99.6% of trigrams are hapax at TOKEN level. But role-level (6 classes) might show recurring structural patterns.

## Results

### Token vs Role Compression

| N-gram | Token Level | Role Level | Compression |
|--------|-------------|------------|-------------|
| 2-gram | 19,660 unique (91.6% hapax) | 48 unique (4.2% hapax) | **409.6x** |
| 3-gram | 22,913 unique (99.6% hapax) | 185 unique (27.6% hapax) | **123.9x** |
| 4-gram | 22,947 unique (100% hapax) | 454 unique (38.5% hapax) | **50.5x** |
| 5-gram | 22,867 unique (100% hapax) | 888 unique (48.2% hapax) | **25.8x** |

**Key insight**: Role-level shows massive compression (400x for bigrams), but patterns still don't repeat universally — even role-level sequences are generative, not templatic.

### Categorized-Only Analysis (excluding UNCATEGORIZED 85% residue)

Role distribution in categorized tokens:
| Role | % |
|------|---|
| ENERGY_OPERATOR | 40.2% |
| CORE_CONTROL | 21.6% |
| FREQUENT_OPERATOR | 11.0% |
| HIGH_IMPACT | 10.3% |
| AUXILIARY | 8.5% |
| FLOW_OPERATOR | 8.4% |

### Self-Transition Rates

| Role | Self-Transition Rate |
|------|---------------------|
| ENERGY_OPERATOR | **45.6%** |
| CORE_CONTROL | **25.0%** |
| HIGH_IMPACT | 17.8% |
| FREQUENT_OPERATOR | 14.8% |
| FLOW_OPERATOR | 11.7% |
| AUXILIARY | 9.6% |

**Key finding**: ENERGY_OPERATOR has 45.6% self-transition — nearly half the time it repeats. This is the primary structural pattern.

### Enriched Bigrams

Only one bigram significantly enriched (≥1.5x expected):
- **HIGH_IMPACT → HIGH_IMPACT**: 1.73x enriched

No bigrams significantly depleted (≤0.67x expected).

### Top Categorized Trigrams

| Pattern | Count | % |
|---------|-------|---|
| ENERGY → ENERGY → ENERGY | 311 | 9.6% |
| CORE → ENERGY → ENERGY | 110 | 3.4% |
| ENERGY → CORE → ENERGY | 101 | 3.1% |
| ENERGY → ENERGY → CORE | 95 | 2.9% |

The dominant pattern is ENERGY_OPERATOR runs with occasional CORE_CONTROL interruptions.

## Interpretation

The grammar skeleton is:

1. **Self-repetition dominant**: ENERGY_OPERATOR stays in same state 45.6% of time
2. **Only one enriched transition**: HIGH_IMPACT → HIGH_IMPACT (big moves cluster)
3. **No depleted transitions**: Role-level topology is flat (confirms CAP phase)
4. **Pattern**: ENERGY runs interrupted by occasional CORE_CONTROL

This is consistent with a control system that:
- Maintains stability through repeated small adjustments (ENERGY runs)
- Occasionally coordinates between energy and phase control (ENERGY ↔ CORE)
- Executes big interventions in bursts (HIGH_IMPACT clustering)

## Constraints Added

**Constraint 401**: SELF-TRANSITION DOMINANCE: ENERGY_OPERATOR has 45.6% self-transition rate (nearly half stay in same role); CORE_CONTROL has 25.0%; grammar skeleton is dominated by role persistence rather than role switching; consistent with stability-maintaining control where small adjustments cluster (LRM, Tier 2)

**Constraint 402**: HIGH_IMPACT CLUSTERING: HIGH_IMPACT → HIGH_IMPACT is the only enriched role bigram (1.73x expected); big interventions cluster together rather than being evenly distributed; no depleted role bigrams exist (role topology is flat with selective clustering) (LRM, Tier 2)

## Files

- `archive/scripts/local_role_motifs.py` - Main analysis

## Status

**CLOSED** - 2 constraints established (401-402)

Role-level patterns show massive compression from token level (400x) but remain generative rather than templatic. The grammar skeleton is dominated by self-transitions and occasional HIGH_IMPACT bursts.
