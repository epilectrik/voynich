# C1477: a-HEAD Is the Primary Hazard Carrier

**Tier:** 2
**Scope:** B, MIDDLE, atom, HEAD, a, hazard, forbidden, modifier, quench-resistant
**Phase:** HEAD_DOMAIN_DIFFERENTIATION (Phase 533)
**Date:** 2026-03-05

## Statement

a-HEAD carries 66.0% overall forbidden rate (2,032/3,079 tokens), the highest of any HEAD atom, and is the ONLY HEAD where modifier quenching fails — modifiers reduce a-HEAD hazard from 79.9% to 52.8% but do not eliminate it. a-HEAD hazard concentrates in three terminal frames: a->l (98.9%, N=527), a->r (98.5%, N=687), and a->n (65.6%, N=1,272). The a->bare frame (N=397) is safe at 0.0%. a-HEAD exclusively attracts modifier i (4.08x enrichment, 78.5% of a-HEAD tokens have i), creating the a+i frame family (aiin, ain, ai, aii) that dominates the FLOW+TRANSITION dual category. The combination of highest hazard rate, quench resistance, and i-modifier monopoly makes a-HEAD the system's primary hazard carrier.

## Evidence

- **a-HEAD forbidden rate:** 2,032/3,079 = 66.0% (vs e=2.2%, k=0.0%, o=30.7%, t=62.5%, headless=36.6%)
- **a-HEAD modifier quench:** with_modifier=52.8% (834/1,580), without_modifier=79.9% (1,198/1,499)
  - a is the ONLY HEAD where quenching fails (e/o/t all reach 0.0% with modifiers)
- **a-HEAD terminal hazard frames:**
  - a->l: 521/527 = 98.9% forbidden
  - a->r: 677/687 = 98.5% forbidden
  - a->n: 834/1,272 = 65.6% forbidden
  - a->bare: 0/397 = 0.0% safe
  - a->m: 0/174 = 0.0% safe
  - a->h: 0/21 = 0.0% safe
- **a-HEAD modifier profile:** i=78.5% (4.08x enrichment); all other modifiers <1% each
- **a-HEAD category:** FLOW 54.2% + TRANSITION 41.4% = 95.6% dual-category
- **a-HEAD position:** mean=0.582 (most line-final of all HEADs), final_rate=14.6% (highest)

## Relationship to Prior Constraints

- Extends C1447 (terminal atom hazard partition) — a-HEAD is where hazard originates
- Deepens C1448 (frame hazard map) — a-HEAD frames account for majority of HIGH-hazard entries
- Connects to C1452-C1456 (i-modifier Simpson's paradox) — a+i is the frame where i appears
- Refines C1382 (a-initial Mode B polarization) — a-HEAD's suffix-bare profile drives Mode B
- Validates C1384 (k-initial predicts AXM dwell, a/o/d anticorrelate) — a-HEAD's hazard drives anti-AXM

## Falsifiable Prediction

If a-HEAD hazard were terminal-determined rather than HEAD-determined, then swapping a-HEAD terminals with k-HEAD terminals should transfer the hazard to k. C1476 predicts this transfer will NOT occur (k is intrinsically immune).
