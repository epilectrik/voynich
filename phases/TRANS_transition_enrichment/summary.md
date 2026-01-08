# Phase TRANS: Transition Enrichment and Higher-Order Sequence Analysis

## Core Question

Beyond the 17 forbidden transitions, what transitions are PREFERRED? Does higher-order (trigram/4-gram) structure exist?

## Key Findings

### Transition Enrichment

| Finding | Value | Significance |
|---------|-------|--------------|
| Suppressed transitions | Only 8 | Far fewer than forbidden (17) |
| All suppressed involve | `chedy`, `shedy`, `aiin`, `ar` | KERNEL-HEAVY cluster |
| Self-transitions | 3.76x mean enrichment | Repetition preferred |

**Prefix-level patterns:**

| Transition | Enrichment | Interpretation |
|------------|------------|----------------|
| sh -> qo | 2.04x | INTERVENTION feeds qo |
| ot -> ot | 1.98x | Self-repeat (stabilization?) |
| ok -> ok | 1.43x | Self-repeat |
| da -> qo | 0.43x | MONITORING avoids qo |
| al -> qo | 0.36x | LINK-attracted avoids qo |
| sh -> al | 0.30x | INTERVENTION avoids LINK-attracted |
| sa -> qo | 0.23x | MONITORING avoids qo |

The pattern is clear: **MONITORING prefixes (da, sa, al) avoid qo-transitions; INTERVENTION (sh) prefers qo-transitions**.

### Higher-Order Sequence Analysis

| Metric | 1-gram | 2-gram | 3-gram | 4-gram |
|--------|--------|--------|--------|--------|
| Unique | 4,917 | 19,660 | 22,913 | 22,947 |
| Hapax % | 67.3% | 91.6% | 99.6% | 100% |
| Entropy | 9.88 | 14.08 | 14.48 | 14.49 |
| Efficiency | 0.806 | 0.987 | 1.000 | 1.000 |

**Conditional entropy (predictability of next token):**

| Context | H(X|context) | Reduction |
|---------|--------------|-----------|
| None | 9.88 bits | — |
| 1 token | 4.19 bits | 57.6% |
| 2 tokens | 0.41 bits | 95.9% cumulative |
| 3 tokens | 0.006 bits | 99.9% cumulative |

**Critical finding:** Once you know the previous 2 tokens, the next token is almost fully determined (H = 0.41 bits ≈ 1.3 outcomes). This is **extreme local determinism** — far tighter than natural language.

**No recurring phrases:** 99.6% of trigrams are hapax. No universal trigrams appear across >=30% of folios. The grammar has no "formulas" or "stock phrases" beyond bigram-level constraints.

## Interpretation

1. **BIGRAM-DOMINANT with EXTREME LOCAL DETERMINISM**: The grammar is almost fully characterized by adjacent pair constraints. Once context is established, the next token is nearly predetermined.

2. **QO is a TRANSITION HUB**: The qo- prefix is strongly preferred as a target from INTERVENTION prefixes (sh) but avoided by MONITORING prefixes (da, sa, al). This suggests qo marks a phase transition point.

3. **Self-repetition as STABILIZATION**: The 3.76x enrichment of self-transitions (especially qo-prefixed tokens) suggests repetition is a control strategy — "keep doing what you're doing."

4. **No memorized sequences**: The absence of repeated n-grams (n>=3) means there are no "stock phrases" or "formulas." Each instruction sequence is locally generated, not recalled from templates.

## Why This Matters

- The 17 forbidden transitions capture what's WRONG
- The 8 suppressed transitions capture what's DISCOURAGED (less catastrophic)
- Self-transition enrichment captures what's STABLE
- Prefix avoidance patterns capture PHASE-SEPARATION rules

Together with the bigram-dominant structure, this confirms the grammar is:
- Locally determined (not random)
- Phase-separated (MONITORING vs INTERVENTION don't mix)
- Stabilization-seeking (self-transitions preferred)
- Not template-based (no recurring formulas)

### Structural Synthesis (Tier 2)

The grammar encodes **both negative and positive guidance**:

| Constraint Type | What It Encodes | Structural Evidence |
|-----------------|-----------------|---------------------|
| Forbidden (17) | Catastrophic failure | 0 occurrences in corpus |
| Suppressed (8) | Risky pathways | 0.19-0.48x expected |
| Enriched (self) | Stabilization | 3.76x expected |
| Enriched (sh→qo) | Preferred flow | 2.04x expected |

This is a **complete control doctrine** — the grammar tells operators what to avoid AND what to pursue. The hazard topology (17 forbidden) and preferred pathways (enriched transitions) are complementary structural features.

**Tier boundary:** We can observe that certain transitions are structurally preferred. We CANNOT claim these preferences correlate with external "success" metrics (yield, quality, efficiency). The enrichment is internal to the grammar; its operational meaning is not recoverable.

## Constraints Added

**Constraint 386**: TRANSITION SUPPRESSION: Beyond the 17 forbidden transitions, 8 transitions are significantly suppressed (<0.5x expected); all 8 involve KERNEL-HEAVY tokens (chedy, shedy, aiin, ar); suppression is within INTERVENTION cluster, not cross-phase; supports phase-internal hazard avoidance (TRANS, Tier 2)

**Constraint 387**: PREFIX TRANSITION ASYMMETRY: Prefix transitions show strong asymmetry: sh->qo enriched (2.04x), da/sa/al->qo suppressed (0.23-0.43x); INTERVENTION prefixes feed into qo; MONITORING prefixes avoid qo; establishes qo as phase-transition hub (TRANS, Tier 2)

**Constraint 388**: SELF-TRANSITION ENRICHMENT: Self-transitions are 3.76x enriched on average; qokeedy->qokeedy (4.7x), qokedy->qokedy (4.4x); self-repetition is a preferred control strategy indicating stabilization or continuation phases (TRANS, Tier 2)

**Constraint 389**: BIGRAM-DOMINANT LOCAL DETERMINISM: Grammar is almost fully determined by 2-token context; H(X|prev 2)=0.41 bits (95.9% reduction from unconditioned); once 2 prior tokens known, next token nearly predetermined; this is EXTREME for any known notation system (HOS, Tier 2)

**Constraint 390**: NO RECURRING N-GRAMS: 99.6% of trigrams are hapax; 100% of 5-grams and beyond are unique; zero "universal trigrams" appear across >=30% of folios; grammar generates sequences locally, not from memorized templates or stock phrases (HOS, Tier 2)

## Files

- `archive/scripts/transition_enrichment_probe.py` - Enrichment analysis
- `archive/scripts/higher_order_sequence_analysis.py` - N-gram analysis

## Status

**CLOSED** - Five constraints established (386-390)
