# C1085: Bio Section Kernel-Balance Distinctiveness

**Tier:** 2 (STRUCTURAL INFERENCE)
**Scope:** B
**Phase:** BIO_DOMAIN_DISTINCTIVENESS (Phase 385)
**Extends:** C553 (BIO-REGIME energy independence), C547 (qo-chain REGIME_1 enrichment), C545 (REGIME instruction class profiles)
**Strengthens:** C1048 (Bio LOO R2=0.754), C1084 (section-AXM ordering)
**Relates to:** C600 (CC trigger sub-group selectivity), C601 (hazard sub-group concentration), C574 (EN distributional convergence), C911 (PREFIX-MIDDLE compatibility)

---

## Statement

Bio section folios (f74-f84, 20 folios, 6850 tokens) show k-enriched kernel balance: k=34.1% vs non-Bio k=24.9% (chi2=146.9, p=1.24e-32, Cramer's V=0.096). This enrichment survives REGIME control: within REGIME_1 only, Bio k=34.1% vs non-Bio k=27.1% (chi2=86.6, p=1.57e-19). Bio is not simply "more REGIME_1" — it has a distinct kernel profile within REGIME_1. The k-enrichment is compensated by e-depletion (Bio 57.0% vs non-Bio 64.2%), while h is slightly depleted (Bio 8.9% vs non-Bio 10.9%).

---

## Evidence

### Kernel Balance (Full Population)

| Kernel | Bio | Bio% | Non-Bio | Non-Bio% | Ratio |
|--------|-----|------|---------|----------|-------|
| k | 1659 | 34.1% | 2779 | 24.9% | 1.37x |
| h | 431 | 8.9% | 1221 | 10.9% | 0.81x |
| e | 2774 | 57.0% | 7178 | 64.2% | 0.89x |

Chi-square: 146.9, dof=2, p=1.24e-32, Cramer's V=0.096.

### REGIME-Controlled (REGIME_1 Only)

| Kernel | Bio-R1 | Non-Bio-R1 |
|--------|--------|------------|
| k | 34.1% | 27.1% |
| h | 8.9% | 6.4% |
| e | 57.0% | 66.5% |

Chi-square: 86.6, p=1.57e-19. Effect is not an artifact of REGIME composition.

### CC Trigger Causal Chain

Bio CC triggers are QO-dominant (44.8% QO_ENERGY vs 13.0% non-Bio, chi2=272.4, Cramer's V=0.373). This connects to kernel balance through the QO→k selection pathway: C911 shows qo prefix selects k-family MIDDLEs at 4.6-5.5x. C600 shows ol-derived triggers route to QO lane at 1.39x. The chain is: Bio → more ol-derived CC triggers → QO lane → k-family MIDDLEs → k-enriched kernel balance.

---

## Interpretation

The k-enrichment profile is consistent with a sustained-heating operational mode: more energy modulation (k), less endpoint processing (e), less hazard handling (h). At Tier 3, this aligns with balneum mariae (water bath distillation) — a gentle, continuously-engaged heating process that requires sustained kernel operations rather than endpoint transitions.

---

## Method

- 20 Bio folios (section=B), 62 non-Bio folios (sections S, H, C, T)
- Kernel assignment via BFolioDecoder._get_middle_kernel()
- Chi-square test for distributional equality
- REGIME-controlled replication with REGIME_1 folios only (20 Bio, 12 non-Bio)
- Pre-registered test with falsification criteria

**Script:** `phases/BIO_DOMAIN_DISTINCTIVENESS/scripts/bio_domain_tests.py`
**Results:** `phases/BIO_DOMAIN_DISTINCTIVENESS/results/bio_domain_results.json`

---

## Verdict

**BIO_K_ENRICHED**: Bio section has a distinct k-enriched kernel balance that survives REGIME control, driven by QO-dominant CC trigger routing through the QO→k PREFIX-MIDDLE compatibility pathway.
