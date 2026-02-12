# PP_CONSTRAINT_AFFORDANCE_MAP

**Tier:** 4 (SPECULATIVE)
**Status:** OPEN
**Purpose:** Map geometric regions of the 972-MIDDLE discrimination space to physical constraint families, anchored to distillation.

## Motivation

The ~101D discrimination manifold (C981-C989) encodes compatibility constraints between MIDDLEs. If anchored to distillation, these constraints should decompose into recognizable physical parameter families (volatility, phase stability, thermal response, recovery topology, solvent interaction). This phase tests whether the geometry is interpretable as a physical constraint polytope.

## Tests

| # | Name | Purpose |
|---|------|---------|
| T1 | Eigenvector Property Atlas | What do the top ~30 residual eigenvectors encode? |
| T2 | Geometric Region Profiling | Extract and profile natural clusters |
| T3 | Kernel-Lane-Role Overlay | Do known categories partition the manifold? |
| T4 | Incompatibility Topology | Build the exclusion graph between regions |
| T5 | Physical Affordance Mapping | Label regions with distillation constraint families |

## Scope

No new Tier 2 constraints. Findings go to `context/SPECULATIVE/` if warranted. Deliverable: a physical affordance map for eventual Tier 4 decoder mode.
