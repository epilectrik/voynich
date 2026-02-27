# C1325: Folio REGIME Homogeneity

**Tier:** 2
**Scope:** B
**Phase:** BLOCK_EXECUTION_CYCLE (464)
**Date:** 2026-02-26

## Finding

Blocks within the same folio are REGIME-homogeneous: within-folio between-block kernel distances are significantly smaller than between-folio distances.

- Within-folio between-block kernel distance: 0.056 (n=2098 pairs)
- Between-folio kernel distance: 0.065 (n=111905 pairs)
- Mann-Whitney z=-8.62, p<0.001
- Permutation p<0.001 (1000 shuffles, seed 42)

478 blocks from 75 folios tested. The folio sets the thermal REGIME; blocks operate within that REGIME but specialize operationally (C1318, C1320).

## Interpretation

The folio is the REGIME container. All blocks on a folio share a common thermal character (kernel k/h/e balance), while differing in PREFIX specialization and operational category. This connects the block architecture to the folio-level REGIME model: the folio defines "what fire we're running" and blocks define "what stages happen within that fire."

Combined with C1320 (blocks maximize internal diversity) and C1318 (PREFIX complementarity), the picture is: folio = REGIME, block = processing stage, paragraph = specialized operator. The REGIME is inherited downward, while operational specialization increases at each level.

## Extends

- C979 (REGIME modulation of transition weights) — REGIME operates at folio level, blocks inherit it
- C1320 (block internal diversity) — blocks diversify operationally WITHIN a shared REGIME
- C1318 (PREFIX complementarity) — PREFIX specialization occurs within REGIME-homogeneous blocks

## Falsifiability

Would be falsified if within-folio between-block kernel distance exceeds between-folio distance (p<0.01), showing blocks on the same folio are REGIME-diverse.

## Evidence Files

- `phases/BLOCK_EXECUTION_CYCLE/results/block_execution_cycle.json` (C1)
