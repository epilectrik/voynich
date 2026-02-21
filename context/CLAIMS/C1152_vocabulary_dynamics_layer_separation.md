# C1152: Section-M2 Captures Vocabulary Composition but Not Sequential Dynamics

**Tier:** 2
**Scope:** B, section differentiation, generative model
**Phase:** SECTION_CONDITIONED_GENERATIVE_FIDELITY (Phase 411)
**Depends on:** C1016, C1025, C1029, C1035, C1055

## Statement

Section-conditioned M2 reproduces inter-folio class distribution variance (mean ratio 1.48x, near-captured) but NOT AXM self-transition spread (1.76x) or kernel profile variance (1.79x). Vocabulary composition is section-determined; sequential dynamics and kernel engagement are program-specific. This establishes a clean two-layer architecture: sections define the operational palette, individual programs define the execution strategy.

## Evidence

**Test 1 (class distribution):** Mean pairwise JSD across real folios within-section is only 1.48x larger than synthetic section-M2 folios. Per-section: BIO 1.69x, COSMO 1.35x, HERBAL_B 1.20x, STARS_RECIPE 1.69x. Section-M2 accounts for most class distribution heterogeneity.

**Test 2 (AXM spread):** Per-folio AXM self-transition SD is 1.76x larger in real data than section-M2 synthetic. BIO 2.56x, STARS_RECIPE 2.24x, HERBAL 1.54x. Section-M2 cannot reproduce the program-level AXM variation documented in C1035.

**Test 3 (kernel profile):** Per-folio k/h/e fraction SD is 1.79x larger in real than synthetic (mean across all sections and kernels). k-kernel ratio 1.82-2.32x and e-kernel 1.76-2.21x uniformly uncaptured. h-kernel variable: captured in BIO (1.29x), HERBAL (1.04x) but not STARS_RECIPE (2.18x).

**Test 4 (fidelity):** Section-conditioning improves KL divergence for 87% of folios (71/82). Universal across sections (81-100% per section). Mean KL improvement 0.085 bits.

## Layer Separation

| Layer | What it determines | Section-captured? | Evidence |
|-------|-------------------|-------------------|----------|
| Vocabulary composition | Which classes appear, at what rates | YES (ratio 1.48x) | T1 |
| Sequential dynamics | AXM stability, transition patterns | NO (ratio 1.76x) | T2 |
| Kernel engagement | k/h/e operational profile | NO (ratio 1.79x) | T3 |

## Structural Implications

- C1029 showed section modulates transition weights, not topology. C1152 extends this: the weight modulation is sufficient for vocabulary composition but NOT for sequential dynamics.
- C1016's 66.3% residual operates at the transition level (Layer 2), which this confirms is program-specific.
- C1055's "near-decomposability" was measured on aggregate section tests. At folio resolution, decomposability holds for vocabulary but breaks for dynamics.
