# C1563: Terminal-to-Next-HEAD Cross-Token Routing Grammar

**Tier:** 2
**Scope:** B, MIDDLE, atom, terminal, HEAD, routing, cross-token, sequential, instruction-phrases, C1212, C1440, C1475, C1483, C1484, C1487
**Phase:** ATOM_ARCHITECTURE_CLEANUP (Phase 549)
**Date:** 2026-03-06

## Claim

Terminal atoms route to specific next-token HEAD domains with strong enrichment asymmetries, creating atom-level instruction phrases. r->a 2.231x, n->a 1.424x (FLOW/CONTAINMENT terminals feed iteration domain); y->k 1.597x, y->t 1.455x, h->t 1.892x, h->k 1.321x (OPERATION/MONITORING terminals feed thermal/flow domains); l->e 1.246x (STAGING terminal feeds stability domain); m->o 1.554x (TRANSITION closure feeds arrangement domain); bare terminals are neutral routers (all near 1.0x). Extends C1212 (TERMINAL->INITIAL is strongest sequential signal, z=20.3) from atom-pair level to HEAD-domain level. TERM is revealed as a dual-function atom: it simultaneously closes the current instruction (suffix gating, C1440) and opens the next (HEAD routing).

## Evidence

### Terminal-to-next-HEAD enrichment matrix

| Terminal | Strongest Next HEAD | Enrichment | Depleted Next HEAD | Enrichment |
|---|---|---|---|---|
| r | a | 2.231x | HEADLESS 0.691x, k 0.397x, t 0.296x |
| y | k | 1.597x | a 0.539x, o 0.678x |
| y | t | 1.455x | -- |
| h | t | 1.892x | a 0.496x, e 0.736x |
| h | k | 1.321x | -- |
| h | HEADLESS | 1.225x | -- |
| n | a | 1.424x | HEADLESS 0.790x, k 0.525x, t 0.320x |
| n | e | 1.214x | -- |
| l | e | 1.246x | k 0.541x, t 0.490x |
| m | o | 1.554x | k 0.095x |
| bare | (all near 1.0) | -- | (neutral) |

### Routing patterns

1. **FLOW/CONTAINMENT -> iteration**: r->a (2.231x), n->a (1.424x) -- after flow or containment state, iterate
2. **OPERATION/MONITORING -> thermal/flow**: y->k (1.597x), h->t (1.892x) -- after operation or monitoring, apply heat or flow
3. **STAGING -> stability**: l->e (1.246x) -- after staging, stabilize
4. **TRANSITION -> arrangement**: m->o (1.554x) -- after closure/transition, rearrange
5. **Bare -> neutral**: No routing preference -- bare terminals carry no forward routing signal

### Functional interpretation

The terminal atom of instruction N determines the operational domain of instruction N+1. This creates atom-level "instruction phrases" where successive instructions are semantically linked: finish monitoring (h), then apply flow (t); finish iterating (n/r), then iterate again (a); finish staging (l), then cool/stabilize (e).

## Interpretation

C1563 completes the cross-token routing chain at atom resolution:

```
TOKEN N:  PREFIX -> MIDDLE [HEAD + MOD* + TERM] -> SUFFIX
                                    |
                                    | TERM routes to next HEAD
                                    v
TOKEN N+1: PREFIX -> MIDDLE [HEAD + MOD* + TERM] -> SUFFIX
```

1. PREFIX selects MIDDLE HEAD domain (C1411, C1536)
2. HEAD selects operational category (C1475)
3. MOD parameterizes the instruction (C1472, C1479)
4. TERM gates suffix attachment (C1440) AND routes next-token HEAD domain (C1563)
5. SUFFIX carries intra-token outcome info (C1510) with ZERO forward propagation (C1564)

TERM is the dual-function linchpin: simultaneously closing and opening.

## Falsification Criteria

1. If terminal-to-HEAD enrichments shown to be entirely PREFIX-confounded
2. If the routing patterns reverse under section or REGIME control
3. If bare terminals show significant routing when analyzed at higher resolution

## Source

`phases/ATOM_ARCHITECTURE_CLEANUP/results/atom_cleanup.json`
