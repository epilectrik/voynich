# C1168: Dual Boundary Architecture

**Tier:** 2
**Scope:** B, folio, AXM residual, boundary
**Phase:** EXIT_DIVERGENCE_SYMMETRY (Phase 416)
**Depends on:** C1035, C1158, C1163, C1165, C1166, C1167

## Statement

Entry and exit boundary features constitute independent predictive channels for AXM self-transition rate. The dual model (C1035 baseline + entry features + exit features) achieves R²=0.852, LOO=0.732, with exit adding dR²=0.039 and LOO gain of +0.036 beyond the entry-only model. All three testable sections benefit: B (dR²=0.189), H (dR²=0.107), S (dR²=0.100). Entry and exit retain partial correlation (rho=0.259, p=0.025) after controlling for baseline predictors. C1035 irreducible residual reduced from ~57% (original) to ~27% (dual boundary model).

## Evidence

| Model | R² | LOO |
|-------|-----|-----|
| Entry only (baseline + entry_div + AXM_return) | 0.814 | 0.696 |
| Exit only (baseline + exit features) | 0.690 | 0.545 |
| Dual (baseline + entry + exit) | 0.852 | 0.732 |
| Exit increment in dual: dR² | 0.039 | — |
| Exit increment in dual: LOO gain | — | +0.036 |

| Section | n | Entry-only R² | Dual R² | Exit dR² |
|---------|---|---------------|---------|----------|
| B | 20 | 0.723 | 0.912 | 0.189 |
| H | 17 | 0.540 | 0.647 | 0.107 |
| S | 23 | 0.796 | 0.897 | 0.100 |

| Metric | Value |
|--------|-------|
| Partial rho(entry, exit \| baseline) | 0.259 (p=0.025) |
| Sections where exit helps | 3/3 |
| Gatekeeper exit mechanism R² | 0.108 (partial, not dominant) |
| Overall verdict | DUAL_CHANNEL |

## Interpretation

Lines in Currier B have two independently informative boundaries: entry (how the program begins each control block) and exit (how it closes). Entry dominates (C1158: 3.5× stronger) but exit carries non-redundant signal through AXM departure rate rather than aggregate divergence. The dual boundary model explains ~73% of AXM self-transition variance, leaving ~27% irreducible. The gatekeeper mechanism (C1007-C1009) contributes partially to exit structure (R²=0.108) but is not the dominant exit channel — AXM departure routing is.

## C1035 Residual Trajectory

| Phase | Model | R² | LOO | Irreducible |
|-------|-------|----|-----|-------------|
| 412 (C1035) | Baseline | 0.636 | 0.511 | ~57% |
| 413 | + boundary_div | 0.734 | 0.601 | ~49% |
| 415 | + entry_div + AXM_return | 0.814 | 0.696 | ~32% |
| **416** | **+ exit features (dual)** | **0.852** | **0.732** | **~27%** |

## Provenance

- Phase 416 Test 5: DUAL_BOUNDARY_ARCHITECTURE
- Script: `phases/EXIT_DIVERGENCE_SYMMETRY/scripts/exit_divergence_symmetry.py`
- Results: `phases/EXIT_DIVERGENCE_SYMMETRY/results/exit_divergence_symmetry.json` → test5_dual_boundary_architecture, synthesis
