# C1309: Mode Category Specialization

**Tier:** 2
**Scope:** B
**Phase:** CROSS_MODE_CATEGORY_COUPLING (460)
**Date:** 2026-02-25

## Finding

Mode A and Mode B lines have distinct category specializations. Mode A concentrates THERMAL (32.5% vs 20.7%, 1.57x) and MONITORING (2.6% vs 1.0%, 2.57x). Mode B concentrates STAGING (15.0% vs 10.9%, 0.73x ratio), TRANSITION (18.0% vs 11.0%, 0.61x), and FLOW (20.2% vs 16.5%, 0.82x). Together they cover 6.1 of 8 categories vs 4.8 alone, but this complementarity is mode-level (not pair-specific: coverage permutation p=1.0).

## Category Profiles

| Category | Mode A | Mode B | A/B Ratio | Dominant |
|----------|--------|--------|-----------|----------|
| THERMAL | 0.325 | 0.207 | 1.57 | A |
| MONITORING | 0.026 | 0.010 | 2.57 | A |
| MARKING | 0.061 | 0.055 | 1.11 | SHARED |
| OPERATION | 0.157 | 0.145 | 1.09 | SHARED |
| CONTAINMENT | 0.046 | 0.051 | 0.90 | SHARED |
| FLOW | 0.165 | 0.202 | 0.82 | B |
| STAGING | 0.109 | 0.150 | 0.73 | B |
| TRANSITION | 0.110 | 0.180 | 0.61 | B |

## Interpretation

Mode A is the specification/parameter voice — it carries thermal parameters and monitoring checks. Mode B is the execution/process voice — it carries flow routing, staging preparation, and state transitions. This maps directly onto the suffix mode characterization: Mode A (terminal-heavy = endpoint specification) encodes WHAT to achieve thermally, Mode B (bare-heavy = continuation) encodes HOW to execute flow and transitions.

## Extends

- C1229 (alternating suffix modes) — adds category dimension to mode distinction
- C1258 (parallel mode tracks) — characterizes what each track carries
- C1279 (mode-category differentiation) — provides full profile

## Falsifiability

Would be falsified if Mode A and Mode B have identical category distributions (chi-squared p > 0.05).

## Evidence Files

- `phases/CROSS_MODE_CATEGORY_COUPLING/results/cross_mode_category_coupling.json` (T8 profiles)
- `phases/CROSS_MODE_CATEGORY_COUPLING/results/parallel_track_probe.json` (P5 specialization)
