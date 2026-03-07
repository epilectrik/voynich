# C1557: o-HEAD y-Terminal Near-Complete Depletion

**Tier:** 2
**Scope:** B, MIDDLE, atom, HEAD, o-HEAD, y-terminal, depletion, safety, PHASE_ORDERING, hazard, C1388, C1475, C1546, C1551, C1557
**Phase:** O_DOMAIN_DEEP_DIVE (Phase 548)
**Date:** 2026-03-06

## Claim

o-HEAD depletes y-terminal to 0.007x enrichment (approximately 19 tokens out of 2,717 o-HEAD tokens). This is the strongest single-terminal depletion for any HEAD atom: k-HEAD y-terminal = 0.082x, e-HEAD y-terminal = 1.792x (strongly enriched), a-HEAD y-terminal = 0.804x (mildly depleted). Since y-terminal is the exclusive PHASE_ORDERING hazard vector (C1551: dy = 100% of PHASE_ORDERING violations), o-HEAD's categorical y-avoidance is a structural safety mechanism. o-HEAD cannot produce PHASE_ORDERING failures because it categorically lacks the terminal atom that causes them. Combined with C1546 (universal HEAD hazard source immunity), this creates double protection: o-HEAD tokens are immune as sources (via HEAD presence) AND avoid the y-terminal hazard vector.

## Evidence

### y-Terminal enrichment by HEAD

| HEAD | y-terminal enrichment | Note |
|---|---|---|
| e | 1.792x | Strongly enriched |
| a | 0.804x | Mildly depleted |
| k | 0.082x | Low but present |
| **o** | **0.007x** | **Near-complete depletion** |
| t | (insufficient data) | - |

### Connection to hazard topology

- C1551: PHASE_ORDERING = exclusively headless y-terminal dy (100% of violations)
- C1546: All HEADs have 0% hazard source rate
- C1557: o-HEAD additionally avoids the y-terminal that carries PHASE_ORDERING risk
- Result: Double structural safety -- HEAD immunity + terminal avoidance

### Inner atom confirmation

The y-atom depletion is even more extreme when measured across all atom positions within o-HEAD compounds: y appears at 0.4% of inner atom slots vs 15.8% corpus baseline = 0.023x enrichment. This is the most extreme single-atom divergence in the entire atom system.

## Interpretation

The y-terminal produces OPERATION/closure semantics (y = "end", C1195). o-HEAD's avoidance of y-terminal means the arrangement domain does not produce closure/ending operations. Arrangement specifications describe configurations, not endings. The safety consequence (PHASE_ORDERING immunity) may be a structural byproduct of this functional incompatibility rather than a designed safety feature, but the effect is the same.

## Falsification Criteria

1. If a significant population of o-HEAD y-terminal MIDDLEs is discovered
2. If y-terminal depletion in o-HEAD is shown to be a sampling artifact
3. If PHASE_ORDERING violations are found involving non-y-terminal MIDDLEs

## Source

`phases/O_DOMAIN_DEEP_DIVE/results/o_domain_deep_dive.json`
