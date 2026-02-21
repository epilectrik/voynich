# C1183: Sister Choice Is Independent of Bridge/Dark Pipeline Balance

**Tier:** 2
**Scope:** B, sister pairs, vocabulary architecture
**Phase:** SISTER_PAIR_MECHANISM (Phase 420)
**Depends on:** C639, C1146

## Statement

Sister preference (ch/(ch+sh)) does not correlate with bridge or dark-pipeline density after controlling for section. Partial Spearman correlations: bridge density rho=-0.082, dark density rho=0.159, bridge/(bridge+dark) ratio rho=-0.147 — all below the 0.25 threshold. Raw correlations are larger (bridge rho=-0.277, dark rho=0.319) but collapse under section control, confirming a section confound. Sister choice operates on a different axis from the vocabulary composition pipeline.

## Evidence

| Metric | Raw rho | Partial rho (ctrl section) |
|--------|---------|---------------------------|
| Bridge density | -0.277 | -0.082 |
| Dark density | +0.319 | +0.159 |
| Bridge/(bridge+dark) | -0.309 | -0.147 |

n=82 folios.

## Interpretation

This is consistent with C1149-C1151 (vocabulary balance orthogonal to dynamical archetypes). Sister choice modulates dynamics (C1181) but not through vocabulary composition. The raw correlations are section-driven: sections with more ch also tend to have different bridge/dark balances, but within any section, sister preference is independent of pipeline architecture.

## Provenance

- Phase 420 Test 4: BRIDGE_DARK_COUPLING
- Script: `phases/SISTER_PAIR_MECHANISM/scripts/sister_pair_mechanism.py`
- Results: `phases/SISTER_PAIR_MECHANISM/results/sister_pair_mechanism.json` -> test4_bridge_dark_coupling
