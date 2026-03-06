# C1476: k-HEAD Immunity Is Intrinsic Not Compositional

**Tier:** 2
**Scope:** B, MIDDLE, atom, HEAD, k, hazard, immunity, intrinsic, modifier
**Phase:** HEAD_DOMAIN_DIFFERENTIATION (Phase 533)
**Date:** 2026-03-05

## Statement

k-HEAD hazard immunity (C1446, 0.0% across 3,100 tokens) is INTRINSIC to the k atom itself, not a consequence of modifier quenching (C1450) or terminal selection. Evidence: (1) k without any modifier = 0.0% forbidden rate (N=2,682), (2) k with modifiers = 0.0% (N=418), (3) 0/6 k frames have any forbidden participation, (4) k never appears as source or target in any of 2,897 forbidden adjacency pairs. In contrast, modifiers quench e/o/t to 0% but FAIL to quench a (with_modifier rate = 52.8% vs without = 79.9%). k is the ONLY HEAD with immunity independent of all compositional context.

## Evidence

- **k bare (no modifier):** 0/2,682 forbidden = 0.000%
- **k with modifier:** 0/418 forbidden = 0.000%
- **k per-frame:** k->bare 0/2,868; k->h 0/202; k->l 0/15; k->y 0/7; k->r 0/7; k->m 0/1 — ALL zero
- **k in forbidden pairs:** 0 as source, 0 as target, across 2,897 tested pairs
- **Modifier quench comparison:**
  - e: with_mod=0.000% (N=3,123), without_mod=3.89% (N=3,879) — modifier quenches to zero
  - o: with_mod=0.000% (N=851), without_mod=44.7% (N=1,866) — modifier quenches to zero
  - t: with_mod=0.000% (N=189), without_mod=78.7% (N=732) — modifier quenches to zero
  - a: with_mod=52.8% (N=1,580), without_mod=79.9% (N=1,499) — modifier REDUCES but does NOT quench
  - k: with_mod=0.000% (N=418), without_mod=0.000% (N=2,682) — intrinsically zero

## Relationship to Prior Constraints

- Deepens C1446 (k-HEAD complete hazard immunity) with mechanism: intrinsic, not compositional
- Refines C1450 (modifier quenching) — quenching works for e/o/t but fails for a
- Connects to C103 (k = ENERGY_MODULATOR) — the energy channel is inherently safe
- Extends C1448 (frame hazard map) — k frames are categorically immune regardless of terminal
- Resolves Phase 533 research question: "Is k-immunity intrinsic or compositional?" — INTRINSIC

## Falsifiable Prediction

If k-immunity were compositional (e.g., from k's typical modifier profile or terminal selection), then artificially pairing k-HEAD with a-HEAD's modifier+terminal distributions should introduce nonzero hazard. The immunity being intrinsic predicts it cannot be disrupted by any compositional manipulation.
