# C1314: Overshoot-Correct Bigram Enrichment

**Tier:** 2
**Scope:** B
**Phase:** DISTILLATION_TERMINOLOGY_MAPPING (461)
**Date:** 2026-02-25

## Finding

Within lines, qo-k tokens followed by ok-e tokens occur significantly above chance:

- Forward (qo-k -> ok-e): 103 observed vs 72.0 null mean (43% above chance, p = 0.0)
- Reverse (ok-e -> qo-k): 112 observed vs 72.1 null mean (55% above chance, p = 0.0)
- Total within-line bigrams: 20,676

The qo-k to ok-e transition and its reverse are both strongly enriched, indicating a systematic cycling pattern between k-enriched and e-enriched tokens within the same line.

## Negative Control

da->sa bigram: 6 observed vs null expectation, permutation p = 0.996. Random infrastructure prefix pairs show no elevated transition rate, confirming the effect is specific to the qo/ok thermal pair.

## Interpretation (Tier 2 only)

The structural fact is that k-bearing tokens under qo systematically transition to e-bearing tokens under ok within lines, and back. This is a measurable within-line sequencing pattern independent of any physical interpretation.

## Extends

- C1313 (two-channel thermal atom separation) — the separated channels show systematic within-line cycling
- C360 (line-invariant grammar) — cycling is line-internal

## Falsifiability

Would be falsified if permutation p exceeds 0.01 for either direction, or if the negative control pair shows comparable enrichment.

## Evidence Files

- `phases/DISTILLATION_TERMINOLOGY_MAPPING/results/distillation_terminology_mapping.json` (T2)
