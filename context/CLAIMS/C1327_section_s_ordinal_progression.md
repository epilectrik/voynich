# C1327: Section S Block Ordinal Progression

**Tier:** 2
**Scope:** B, section-S
**Phase:** SECTION_S_BLOCK_ARCHITECTURE (465)
**Date:** 2026-02-26

## Finding

Section S blocks show significant ordinal progression within folios. Later blocks on a folio shift from OPERATION-focused to THERMAL/TRANSITION-focused.

**Significant ordinal correlations (3/12 metrics, 286 blocks from 23 folios):**
- OPERATION: rho=-0.169, perm p<0.001 (decreases with block position)
- TRANSITION: rho=+0.160, perm p=0.002 (increases with block position)
- THERMAL: rho=+0.123, perm p=0.003 (increases with block position)

**Marginal trends:**
- kernel_h: rho=-0.082, p=0.049 (monitoring kernel decreases)
- lk_rate: rho=+0.130, p=0.014 (fire-method monitoring increases)
- MARKING: rho=-0.099, p=0.035 (specification decreases)

**Non-significant (flat):** kernel_k (p=0.086), kernel_e (p=0.359), FLOW (p=0.053), CONTAINMENT (p=0.371), STAGING (p=0.263), MONITORING (p=0.189).

Permutation test: 1000 shuffles of block order within each folio, seed 42.

## Interpretation

Section S blocks are NOT exchangeable parallel stations — they are ordered monitoring checkpoints that progress from active manipulation (OPERATION) to thermal/transition monitoring. This is consistent with a process maturation sequence: early blocks describe active setup/intervention, later blocks describe thermal monitoring and state changes as the process matures.

The kernel fractions remain flat (REGIME-stable per C1325), while the category composition shifts. This means the same thermal mode persists throughout, but the operational FOCUS shifts within that mode.

## Falsifies

- **Parallel stations hypothesis** (proposed Phase 465): Block exchangeability requires no ordinal signal. 3/12 significant correlations demonstrate ordered progression.
- Partially extends C1120 (lifecycle progression falsified at folio level) — the progression exists at BLOCK level within S folios, not at folio level across the manuscript.

## Extends

- C1317 (block census) — S blocks have section-specific structure
- C1106 (Stars e-stability enrichment) — kernel flatness with ordinal confirms stable thermal mode

## Evidence Files

- `phases/SECTION_S_BLOCK_ARCHITECTURE/results/section_s_block_architecture.json` (S2)
