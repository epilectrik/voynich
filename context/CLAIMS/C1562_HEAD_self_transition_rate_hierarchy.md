# C1562: HEAD Self-Transition Rate Hierarchy

**Tier:** 2
**Scope:** B, MIDDLE, atom, HEAD, self-transition, sequential, hierarchy, persistence, switching, C1212, C1384, C1475, C1478, C1521
**Phase:** ATOM_ARCHITECTURE_CLEANUP (Phase 549)
**Date:** 2026-03-06

## Claim

HEAD atoms form a three-tier self-transition hierarchy: PERSISTENT (e 28.5%, headless 28.4%, a 25.2%), SWITCHING (k 16.7%, o 13.6%), RARE (t 9.1%). Stability/identification/iteration domains maintain longer runs; active thermal/arrangement/flow domains transition to other domains after shorter runs. Asymmetric cross-HEAD transitions: e->k enriched 1.493x, e->t 1.355x (stability feeds thermal/flow); a->k depleted 0.528x, a->t 0.483x (iteration avoids thermal/flow). t->t has the strongest self-enrichment (2.138x) despite the lowest absolute rate, indicating t-HEAD tokens cluster into short intense bursts. Extends C1212 (TERMINAL->INITIAL chaining) to HEAD-domain resolution; consistent with C521 (kernel directional asymmetry) and C1384 (k-initial predicts AXM dwell).

## Evidence

### Self-transition rates by HEAD

| HEAD | Self-Rate | Self-Count | Total From | Enrichment |
|---|---|---|---|---|
| e | 28.5% | 1,875 | 6,588 | baseline |
| HEADLESS | 28.4% | 1,503 | 5,299 | ~1.0x vs e |
| a | 25.2% | 662 | 2,631 | ~0.89x vs e |
| k | 16.7% | 485 | 2,897 | ~0.59x vs e |
| o | 13.6% | 327 | 2,413 | ~0.48x vs e |
| t | 9.1% | 77 | 848 | ~0.32x vs e |

### Key asymmetric transitions

| Transition | Enrichment | Pattern |
|---|---|---|
| e->k | 1.493x | Stability feeds thermal |
| e->t | 1.355x | Stability feeds flow |
| a->a | 1.753x | Strong iteration self-continuation |
| t->t | 2.138x | Strongest self-enrichment (burst mode) |
| a->k | 0.528x | Iteration avoids thermal |
| a->t | 0.483x | Iteration avoids flow |
| HEADLESS->k | 0.672x | Headless avoids thermal |
| HEADLESS->t | 0.702x | Headless avoids flow |

### Operational interpretation

- e-HEAD is the universal DONOR to k and t domains (enrichment 1.49x, 1.36x)
- a-HEAD and headless AVOID k and t domains (0.48-0.70x)
- This extends C521's one-way valve pattern from kernel atoms to full HEAD-level sequential routing

## Interpretation

The self-transition hierarchy reflects operational dynamics: stability (e) and iteration (a) are sustained activities that maintain state, while thermal (k) and arrangement (o) are punctuated interventions that quickly hand off. Flow (t) is the rarest and most burst-like. This is consistent with C1384's finding that k-initial fraction predicts AXM dwell: thermal work bursts keep the system in its attractor (high AXM), and k's low self-transition (16.7%) means thermal runs are brief but frequent.

## Falsification Criteria

1. If a different corpus subset shows a different HEAD self-transition ordering
2. If the e->k/t enrichment pattern reverses under section control
3. If the a->k/t avoidance is shown to be a PREFIX confound

## Source

`phases/ATOM_ARCHITECTURE_CLEANUP/results/atom_cleanup.json`
