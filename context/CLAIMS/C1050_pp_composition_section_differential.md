# C1050: PP Composition Predicts Section-Differential Coverage

**Tier:** 2 (STRUCTURAL INFERENCE)
**Scope:** A<>B
**Phase:** A_B_SECTION_CORRESPONDENCE (Phase 367)
**Extends:** C506 (PP composition uniform, cosine=0.995), C751 (pool-size confound)
**Relates to:** C1049 (shared vocabulary universal substrate), C708 (funnel topology)

---

## Statement

After controlling for PP pool size (r=0.84-0.90), PP MIDDLE composition features predict section-specific B coverage. Two features tested:

| Feature | → B-BIO | → B-HERBAL | → B-RECIPE |
|---------|---------|-----------|-----------|
| core_fraction (PP MIDDLEs in ≥3 sections) | **r=0.457** | **r=0.452** | **r=0.332** |
| section_bias (mean Herfindahl of PP MIDDLEs) | **r=-0.351** | **r=-0.322** | r=-0.164 |

A folios with more section-universal PP MIDDLEs (higher core_fraction, lower section_bias) achieve higher coverage at every B section, even after pool size is controlled. The effect is strongest for BIO and HERBAL (r=0.45) and weaker for RECIPE (r=0.33).

Additionally, A folio rankings across sections are only moderately stable after pool-size control:

| Section pair | Raw rho | Residualized rho |
|-------------|---------|-----------------|
| B vs H | 0.952 | **0.849** |
| B vs S | 0.953 | **0.857** |
| H vs S | 0.937 | **0.811** |

Rankings shift substantially when pool-size is removed. The best A folio for BIO is not necessarily the best for RECIPE (rho=0.857, not 1.0).

---

## Evidence

- 111 A folios (95 Herbal + 16 Pharmaceutical)
- Pool-size controlled via linear regression residualization
- core_fraction: fraction of A folio's PP MIDDLEs appearing in ≥3 B sections (mean=0.811)
- section_bias: mean Herfindahl of A folio's PP MIDDLEs in B (mean=0.508)
- All partial correlations use Spearman rho after pool-size residualization

---

## Interpretation

C506 showed PP MIDDLE composition is nearly uniform across A folios (cosine=0.995). This constraint does NOT contradict C506 — it extends it by showing that even small compositional differences have functional consequences. The 0.5% compositional variation creates 15-46% partial correlation with section-specific coverage.

The QUALITY of the PP pool (how section-universal its MIDDLEs are) matters beyond mere pool SIZE. This deepens the C753 reframe: A→B is a constraint propagation pipeline, and the pipeline's section throughput depends on whether PP MIDDLEs belong to the universal substrate (C1049) or to section-concentrated vocabulary.

---

## Method

- PP MIDDLE features computed per A folio: core_fraction, section_bias, pp_pool_size
- Per-section coverage = mean fraction of section's B folio vocabulary that is legal under C502.a
- Partial correlations computed by residualizing both predictor and outcome on pool_size
- Ranking stability = Spearman rho of residualized per-section coverage rankings

**Script:** `phases/A_B_SECTION_CORRESPONDENCE/scripts/ab_section_correspondence.py`
**Results:** `phases/A_B_SECTION_CORRESPONDENCE/results/ab_section_correspondence.json`
