# C1448: HEAD x TERM Frame Hazard Map with k-Neutralization

**Tier:** 2
**Scope:** B, MIDDLE, atom, HEAD, TERM, frame, hazard, k-neutralization, C109, C1393, C1446, C1447
**Phase:** 523 (HAZARD_ATOM_DECOMPOSITION)
**Date:** 2026-03-05

## Claim

HEAD x TERMINAL frame combinations produce a sparse hazard map where 7 frames account for >95% of all hazard tokens. High-hazard frames (>50%): o→bare (100%, N=388), d→y (99.7%, N=675), a→l (98.86%, N=527), a→r (98.54%, N=687), o→r (98.02%, N=455), e→e (75.5%, N=151), a→n (65.57%, N=1272). k as HEAD completely neutralizes hazard to 0% across ALL terminal combinations, including normally hazardous terminals r and n. The massive safe pathway e→y (3,475 tokens, 0%) demonstrates that cooling-then-end is categorically safe.

## Evidence

### High-hazard frames (>50%)

| Frame | N tokens | Hazard rate | Category |
|-------|----------|------------|----------|
| o→bare | 388 | 100.0% | OPERATION |
| d→y | 675 | 99.7% | CONTAINMENT |
| a→l | 527 | 98.86% | FLOW |
| a→r | 687 | 98.54% | FLOW |
| o→r | 455 | 98.02% | FLOW |
| e→e | 151 | 75.5% | THERMAL |
| a→n | 1,272 | 65.57% | TRANSITION |

### k-neutralization across all terminals

| k-Frame | N tokens | Hazard rate |
|---------|----------|------------|
| k→bare | 2,083 | 0.0% |
| k→e | 464 | 0.0% |
| k→h | 202 | 0.0% |
| k→d | 93 | 0.0% |
| k→c | 56 | 0.0% |
| k→o | 92 | 0.0% |
| k→r | 15 | 0.0% |
| k→n | 1 | 0.0% |

### Major safe frames (>500 tokens, 0% hazard)

| Frame | N tokens | Hazard rate |
|-------|----------|------------|
| e→y | 3,475 | 0.0% |
| k→bare | 2,083 | 0.0% |
| i→n | 991 | 0.0% |
| k→e | 464 | 0.0% |

### Hazard concentration

The 7 high-hazard frames contain 4,155 tokens accounting for the vast majority of hazard exposure. The frame space is NOT uniformly hazardous -- hazard is concentrated in specific HEAD x TERMINAL combinations involving a, o, d, and e as HEAD with r, l, y, n, e, and bare as TERMINAL.

## Interpretation

The frame hazard map reveals the instruction-level safety architecture. Energy operations (k-HEAD) are unconditionally safe regardless of what terminal they combine with. Yield operations (a-HEAD) with flow/state terminals (r, l, n) are almost universally hazardous. The e→y frame (cooling+end = 3,475 tokens at 0%) represents the system's primary safe exit pathway from thermal processing. Hazard is not a property of individual atoms but of specific HEAD x TERMINAL frames.

## Falsification Criteria

1. If any k-HEAD frame reaches >2% hazard
2. If e→y moves above 2% hazard
3. If any frame listed at >95% hazard drops below 80%

## Method

- 23,096 clean Currier B tokens decomposed into HEAD x TERMINAL frames
- Hazard = FLOW + CONTAINMENT categories (C1280)
- All HEAD x TERMINAL combinations with N >= 10 analyzed
- Frame hazard rate = fraction of tokens in hazard categories

**Script:** `phases/HAZARD_ATOM_DECOMPOSITION/scripts/hazard_atom_decomposition.py`
**Results:** `phases/HAZARD_ATOM_DECOMPOSITION/results/hazard_atom_decomposition.json`

## Dependencies

- C109 (5 failure classes, 17 forbidden transitions)
- C1280 (hazard concentrates in FLOW/CONTAINMENT)
- C1393-C1394 (instruction encoding architecture)
- C1446 (k-HEAD complete hazard immunity)
- C1447 (terminal atom hazard partition)
