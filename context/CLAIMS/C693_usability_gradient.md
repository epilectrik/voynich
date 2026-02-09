# C693: Usability Gradient

**Status:** VALIDATED | **Tier:** 2 | **Phase:** A_RECORD_B_FILTERING | **Scope:** A-B

## Finding

The usability of filtered B folios spans a **266x dynamic range**. The composite usability metric (legality x role_coverage x (1 - empty_rate)) ranges from 0.000 (total elimination) to 0.107 (marginally functional). **25 of 32 pairings (78%) render the folio unusable** (>50% empty lines). Only the most permissive A records (~14 PP MIDDLEs) produce non-trivial residual programs.

> **Aggregation Note (2026-01-30):** This constraint tests single A records against B folios.
> The finding that single records are insufficient is consistent with C885, which establishes
> A FOLIO (not single paragraph/record) as the operational unit for A-B correspondence (81%
> coverage at folio level vs 58% at paragraph level).

## Usability Matrix

| Record | Largest | REGIME_1 | REGIME_2 | REGIME_4 |
|--------|---------|----------|----------|----------|
| Max-classes | **0.106** | 0.088 | 0.062 | 0.058 |
| High-PP | 0.015 | 0.007 | 0.018 | 0.013 |
| Low-PP | 0.001 | 0.001 | 0.002 | 0.001 |
| PURE_PP | 0.000 | 0.001 | 0.001 | 0.001 |
| Median-PP | 0.001 | 0.001 | 0.000 | 0.000 |
| Min-classes | 0.000 | 0.000 | 0.000 | 0.000 |
| PURE_RI | 0.000 | 0.000 | 0.000 | 0.000 |
| Minimal-PP | 0.000 | 0.000 | 0.000 | 0.000 |

## Key Numbers

| Metric | Value |
|--------|-------|
| Best pairing | Max-classes + Largest (0.107) |
| Worst pairing | Minimal-PP + any (0.000) |
| Dynamic range (nonzero) | 266x |
| Unusable pairings (>50% empty) | 25 / 32 (78.1%) |
| Records with >0 usability on all folios | 1 (Max-classes only) |

## Interpretation

A single A record does NOT produce a usable B program. The filtering is too severe: the median A record creates 74-100% empty lines, with <1% composite usability. This is structurally expected — A records are **individual configuration tokens** that each specify a narrow morphological slice. The manuscript's design implies that B programs operate under the **aggregate constraint** of multiple A records (a full A folio, perhaps), not single-record filtering. The question "what does a filtered folio look like?" has its answer: **mostly empty, with scattered legal tokens that lack operational coherence.**

## Provenance

- Script: `phases/A_RECORD_B_FILTERING/scripts/instance_trace_analysis.py` (Test 12)
- Extends: C690 (legality), C691 (coherence), C682-C689 (population context)
