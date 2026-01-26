# C547: qo-Chain REGIME_1 Enrichment

**Tier:** 3 | **Status:** OPEN | **Scope:** B

---

## Statement

> qo-family chains (2+ consecutive Class 32/33/36 tokens) show 1.53x enrichment in REGIME_1, with 51.4% of all chains occurring in REGIME_1 despite only ~34% of tokens. REGIME_2 and REGIME_3 are depleted (0.42x and 0.55x respectively).

---

## Evidence

**Test:** `phases/CLASS_SEMANTIC_VALIDATION/scripts/qo_chain_thermal_test.py`

| REGIME | qo-Chains | Expected | Enrichment |
|--------|-----------|----------|------------|
| REGIME_1 | 161 (51.4%) | 105.2 | **1.53x** |
| REGIME_2 | 36 (11.5%) | 84.7 | 0.42x |
| REGIME_3 | 13 (4.2%) | 23.5 | 0.55x |
| REGIME_4 | 103 (32.9%) | 99.6 | 1.03x |

**Total chains:** 313 (mean length 2.21, max 6)

**Chain length distribution:**
- Length 2: 259 chains (82.7%)
- Length 3: 47 chains (15.0%)
- Length 4+: 7 chains (2.2%)

---

## Longest Chains

| Folio | Line | REGIME | Chain |
|-------|------|--------|-------|
| f108v | 39 | REGIME_4 | qokeedy qokeedy qokeedy qotey qokeey qokeey |
| f75r | 13 | REGIME_1 | qokedy qokedy qokedy qokedy qokain |
| f75r | 38 | REGIME_1 | qokeedy qokeedy qokedy qokedy qokeedy |
| f77r | 34 | REGIME_1 | qokeedy qotedy qokeedy qokeedy qokeey |

9 of top 10 longest chains are in REGIME_1 Section B folios (f75-f84).

---

## Interpretation (Tier 3)

The REGIME_1 enrichment suggests qo-family tokens represent sustained operations that cluster in thermal processing contexts (Section B = balneological section). This is consistent with:

- C397: qo-prefix as "escape route" (25-47%)
- C545: REGIME_1 = ENERGY-heavy, qo-concentrated

The depletion in REGIME_2/3 suggests qo-chains are incompatible with output-intensive (REGIME_2) or intervention-heavy (REGIME_3) modes.

**Speculative:** qo-chains may represent continuous venting/release operations that require sustained thermal processing contexts rather than punctuated interventions.

---

## Why Tier 3

This finding is **distributional** (observed pattern) rather than **architectural** (structural necessity):

1. The enrichment could vary in another manuscript using the same grammar
2. "Sustained escape/venting" is interpretation, not mechanism
3. No invariant claim (qo-chains don't REQUIRE REGIME_1)

---

## Cross-References

| Constraint | Relationship |
|------------|--------------|
| C397 | Extended - chain-level evidence for qo escape route |
| C545 | Extended - qo-chain enrichment in REGIME_1 profiles |
| C544 | Consistent - qo/ch-sh interleaving pattern |
| C458 | Consistent - recovery freedom allows REGIME variation |

---

## Provenance

- **Phase:** CLASS_SEMANTIC_VALIDATION
- **Date:** 2026-01-25
- **Script:** qo_chain_thermal_test.py

---

## Navigation

<- [C546_class40_safe_flow.md](C546_class40_safe_flow.md) | [INDEX.md](INDEX.md) ->
