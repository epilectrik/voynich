# C1556: o-HEAD Terminal-to-Category Deterministic Mapping

**Tier:** 2
**Scope:** B, MIDDLE, atom, HEAD, o-HEAD, terminal, category, deterministic, STAGING, FLOW, OPERATION, C1388, C1475, C1483, C1485, C1487, C1556
**Phase:** O_DOMAIN_DEEP_DIVE (Phase 548)
**Date:** 2026-03-06

## Claim

Within o-HEAD MIDDLEs (2,717 tokens, 11.8% of Currier B), the terminal atom deterministically selects the operational category. The three largest o-HEAD MIDDLEs achieve 100% category purity: ol (762 tokens) = 100% STAGING, or (446 tokens) = 100% FLOW, bare o (388 tokens) = 100% OPERATION. Aggregated by terminal: l-terminal = 92.9% STAGING (N=820), r-terminal = 88.6% FLOW (N=508), bare = 76.7% OPERATION (N=647). This is the sharpest terminal-category coupling for any HEAD atom -- C1483 found overall terminal category specificity V=0.463 across all HEADs, but within o-HEAD the l-terminal and r-terminal achieve near-100% categorical purity. This resolves the vague "arrangement" label (C1388): o-HEAD is an arrangement domain BECAUSE it uses different terminals to specify different arrangement ASPECTS -- staging arrangements (l), flow arrangements (r), and operational arrangements (bare).

## Evidence

### Terminal-to-category mapping (o-HEAD MIDDLEs, Currier B)

| Terminal | Dominant Category | Rate | N |
|---|---|---|---|
| l | STAGING | 92.9% | 820 |
| r | FLOW | 88.6% | 508 |
| bare | OPERATION | 76.7% | 647 |
| h | MARKING/MONITORING | 33.8%/25.4% | 287/63 |
| bare (subset) | CONTAINMENT | 100% | 102 |
| bare (subset) | THERMAL | 100% | 63 |
| bare (subset) | TRANSITION | 100% | 39 |

### Top three o-HEAD MIDDLEs

| MIDDLE | Tokens | Category | Suffix Rate | Mode A Rate |
|---|---|---|---|---|
| ol | 762 | 100% STAGING | 3% | 2% |
| or | 446 | 100% FLOW | 3% | 0% |
| bare o | 388 | 100% OPERATION | 77% | 54% |

### Contrast with other HEADs

No other HEAD atom achieves this degree of terminal-category determinism. k-HEAD and t-HEAD are single-category domains (C1475), so terminal variation exists within one category. e-HEAD is multi-category but terminal-category coupling is weaker. o-HEAD uniquely uses terminal atoms as categorical switches.

## Interpretation

The o-HEAD domain is an ARRANGEMENT SPECIFICATION SYSTEM. Different terminal atoms produce different arrangement types: l-terminal = how things are arranged/positioned (STAGING), r-terminal = how things flow through the system (FLOW), bare = what operational configuration is active (OPERATION). The terminal atom IS the arrangement type.

## Falsification Criteria

1. If a significant population of ol tokens is found outside STAGING category
2. If or tokens are found outside FLOW category
3. If terminal-category determinism is shown to be a frequency artifact of a few dominant MIDDLEs

## Source

`phases/O_DOMAIN_DEEP_DIVE/results/o_domain_deep_dive.json`
