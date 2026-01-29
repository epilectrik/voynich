# C604: C412 REGIME Decomposition

**Tier:** 2 | **Status:** CLOSED | **Scope:** B

---

## Statement

> The C412 anticorrelation (ch-preference ~ escape-density, rho=-0.304) is partially a REGIME artifact. Controlling for REGIME reduces the effect by 27.6% (partial rho=-0.220). Within-REGIME stratification shows C412 vanishes in REGIME_1 (rho=-0.075, p=0.73, n=23) and REGIME_2 (rho=-0.051, p=0.81, n=24), persists strongly only in REGIME_3 (rho=-0.690, p=0.058, n=8), and weakly in REGIME_4 (rho=-0.231, p=0.25, n=27). EN subfamily balance and CC composition do NOT mediate C412 (8.2% and 11.7% reduction respectively).

---

## Evidence

**Test:** `phases/SISTER_PAIR_DECOMPOSITION/scripts/sister_pair_decomposition.py`

### C412 Replication

Spearman rho=-0.304, p=0.0055, n=82 folios. Expected: rho~-0.326. Replication successful.

### Mediation Analysis

| Mediator | Direct rho | Partial rho | Reduction |
|----------|-----------|-------------|-----------|
| EN subfamily (en_chsh_proportion) | -0.304 | -0.279 | 8.2% |
| CC composition (cc_old_fraction) | -0.301 | -0.266 | 11.7% |
| **REGIME** | **-0.304** | **-0.220** | **27.6%** |

Only REGIME exceeds the 20% mediation threshold. EN subfamily does not mediate despite escape_density correlating very strongly with en_qo_proportion (rho=0.726). The weak link is ch_preference -> en_chsh_proportion (rho=0.189, p=0.09) — ch PREFIX usage does not predict EN subfamily balance.

### Within-REGIME Stratification

| REGIME | rho | p | n | C412 Present? |
|--------|-----|---|---|---------------|
| REGIME_1 | -0.075 | 0.733 | 23 | NO |
| REGIME_2 | -0.051 | 0.812 | 24 | NO |
| REGIME_3 | -0.690 | 0.058 | 8 | YES (marginal) |
| REGIME_4 | -0.231 | 0.246 | 27 | Weak |

C412 disappears in the two largest REGIMEs (47 of 82 folios). The pooled correlation is driven by between-REGIME variation: REGIME_1 has lower ch_preference (mean=0.534) and higher escape density, while REGIME_2/3/4 have higher ch_preference (0.635-0.655).

### REGIME -> ch_preference

Kruskal-Wallis H=9.882, p=0.020. REGIME_1 mean ch_preference=0.534 vs REGIME_2=0.635, REGIME_4=0.655.

---

## Interpretation

C412 is not a universal within-folio property. It arises because different REGIMEs have different baseline ch-preference and escape-density profiles. Within a single REGIME, folios do not show the anticorrelation. This does NOT invalidate C412 — the pooled anticorrelation is real — but it relocates the mechanism from the folio level to the REGIME level.

The sister-pair choice (ch vs sh prefix) is not directly coupled to escape density within a processing context. Instead, REGIMEs that happen to favor different ch/sh ratios also happen to have different escape profiles.

---

## C412 Annotation

C412 remains valid as a folio-level statistical observation but should be interpreted as REGIME-mediated rather than intrinsic. The mechanism operates at the REGIME level, not the folio level.

---

## Cross-References

| Constraint | Relationship |
|------------|--------------|
| C412 | Refined — decomposed through REGIME; 27.6% mediation |
| C408 | Context — sister pair equivalence classes still valid |
| C602 | Connected — REGIME modulates sub-role routing, including ch/sh balance |
| C603 | Independent — CC composition drives EN subfamily but does not mediate C412 |
| C605 | Complementary — two-lane model captures folio-level escape variation independently |

---

## Provenance

- **Phase:** SISTER_PAIR_DECOMPOSITION
- **Date:** 2026-01-26
- **Script:** sister_pair_decomposition.py

---

## Navigation

<- [C603_cc_folio_level_subfamily_prediction.md](C603_cc_folio_level_subfamily_prediction.md) | [INDEX.md](INDEX.md) ->
