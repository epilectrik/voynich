# C1549: q-Modifier Hazard Protection on o-Base (qo 4.15% vs Other o-Modifiers 27-52%)

**Tier:** 2
**Scope:** B, PREFIX, modifier, q, o-base, hazard, protection, qo, C1538, C1546, C1548, C1452, C1480
**Phase:** HAZARD_PREFIX_INTEGRATION (Phase 546)
**Date:** 2026-03-06

## Claim

Within o-base PREFIXes, the q-modifier produces a 4.15% hazard source rate (0.52x vs base mean), while ALL other o-base modifiers produce 27-52% source rates (3.4-6.5x vs base mean). The q-modifier provides ~7x hazard protection compared to the average non-q o-modifier. This is mechanistically explained by C1538: q uniquely activates k-HEAD at 64% on o-base, and k-HEAD is categorically hazard-immune (C1546). The other o-modifiers produce 65-87% headless tokens, which are hazard-vulnerable. q-modifier on o-base is the STRONGEST single-PREFIX hazard protection mechanism in the system.

## Evidence

### Modifier effects within o-base (B corpus, Phase 546)

| Modifier + o | Source rate | Enrichment vs base | k-HEAD % (C1538) | Headless % |
|---|---|---|---|---|
| **q**o | **4.15%** | **0.52x** | 64.0% | 11.1% |
| po | 27.21% | 3.41x | 8.1% | 65.4% |
| so | 28.04% | 3.51x | 18.5% | 73.0% |
| to | 30.43% | 3.81x | 15.7% | 67.0% |
| ko | 31.25% | 3.91x | 6.2% | 79.2% |
| do | 51.59% | 6.46x | 4.8% | 86.5% |

q-modifier protection ratio vs next-safest (po): 4.15% / 27.21% = 0.153 (6.6x safer).

### Mechanism: HEAD-mediated protection

qo produces 64% k-HEAD tokens (C1538). k-HEAD has 0% hazard source rate (C1546). The remaining 11.1% headless qo tokens account for essentially all of qo's 4.15% source rate. Other o-modifiers produce 65-87% headless, and headless o-base tokens have ~8% hazard source rate (C1548), resulting in their elevated rates.

### Comparison with h-base modifiers

| Modifier + h | Source rate | Enrichment vs base |
|---|---|---|
| ch | 4.73% | 1.00x (reference) |
| sh | 2.76% | 0.58x |
| kch | 21.65% | 4.56x |
| tch | 15.12% | 3.18x |

On h-base, the k-modifier (kch) INCREASES hazard — opposite of its effect as a HEAD atom. This confirms C1542 (c-atom slot-switching): atoms function differently depending on their slot position. On o-base, q provides protection by activating k-HEAD. On h-base, k as a modifier does not provide HEAD immunity because k occupies the modifier slot, not the HEAD slot.

## Interpretation

The q-modifier's protective effect parallels the i-modifier Simpson's paradox (C1452, C1480) but in the OPPOSITE direction. The i-modifier routes into hazardous a-HEAD frames but protects within them. The q-modifier routes into safe k-HEAD frames and thus achieves protection at the aggregate level. Both demonstrate that PREFIX modifiers achieve their safety effects through HEAD domain selection, not through direct hazard avoidance. qo's status as the primary THERMAL channel (C1300, C1313) is MECHANISTICALLY EXPLAINED: thermal work requires k-HEAD MIDDLEs, k-HEAD is hazard-immune, therefore thermal work is inherently safe.

## Falsification Criteria

1. If another o-base modifier achieves <10% source rate
2. If qo's protection disappears after controlling for section/REGIME
3. If the k-HEAD mediation pathway is insufficient (qo headless tokens have higher-than-expected hazard rate)

## Source

`phases/HAZARD_PREFIX_INTEGRATION/results/hazard_prefix_integration.json`
