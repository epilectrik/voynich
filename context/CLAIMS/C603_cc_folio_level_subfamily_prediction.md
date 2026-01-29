# C603: CC Folio-Level Subfamily Prediction

**Tier:** 2 | **Status:** CLOSED | **Scope:** B

---

## Statement

> CC trigger composition predicts EN subfamily balance at the folio level. Folios with higher CC_OL_D fraction have higher QO proportion (Spearman rho=0.355, p=0.0012, n=81). Folios with higher CC_DAIIN fraction have higher CHSH proportion (rho=0.345, p=0.0016, n=81). CC composition is the strongest predictor of EN subfamily balance, exceeding section (V=0.092), REGIME (V=0.047), and line position (V=0.045).

---

## Evidence

**Test:** `phases/SISTER_PAIR_DECOMPOSITION/scripts/en_subfamily_selection.py`

### CC Composition vs EN Subfamily (Folio Level)

| Test | rho | p | n | Direction |
|------|-----|---|---|-----------|
| CC_OL_D fraction -> QO proportion | **0.355** | 0.0012 | 81 | OL_D predicts QO |
| CC_DAIIN fraction -> CHSH proportion | **0.345** | 0.0016 | 81 | DAIIN predicts CHSH |
| FL_HAZ fraction -> CHSH proportion | -0.048 | 0.671 | 82 | Not significant |

### Predictor Ranking (Effect Size)

| Rank | Predictor | Effect | p |
|------|-----------|--------|---|
| 1 | CC_OL_D -> QO | rho=0.355 | 0.0012 |
| 2 | CC_DAIIN -> CHSH | rho=0.345 | 0.0016 |
| 3 | Section | V=0.092 | 9.6e-23 |
| 4 | REGIME | V=0.047 | 1.3e-05 |
| 5 | Line position | V=0.045 | 2.6e-04 |

### REGIME x EN Subfamily

Chi-squared=32.48, df=6, p=0.000013. Cramer's V=0.047. Statistically significant but very small effect. REGIME_2 is CHSH-enriched (61.0%) vs REGIME_1 QO-enriched (46.2%).

### Section x EN Subfamily

Chi-squared=122.61, df=8, p<1e-22. Cramer's V=0.092. Section B (Biopharmaceutical) is QO-enriched (50.3%), Section H (Herbal_B) is strongly CHSH-enriched (69.4%).

### Folio-Level QO Proportion Distribution

Mean=0.401, Std=0.135, Range=[0.050, 0.664]. Substantial variation across folios — not a constant ratio.

---

## Interpretation

C600 showed that CC sub-groups have differentiated trigger profiles at the token level (daiin->CHSH, ol-derived->QO). C603 confirms this relationship scales up to the folio level: the fraction of CC triggers that are OL_D vs DAIIN predicts the folio's EN subfamily balance. Folios are not randomly mixed — their CC composition determines which processing lane dominates.

This is the strongest single predictor of EN subfamily selection, stronger than REGIME or section membership.

---

## Cross-References

| Constraint | Relationship |
|------------|--------------|
| C600 | Extended — token-level trigger selectivity scales to folio level |
| C576 | Connected — EN QO/CHSH bifurcation is CC-driven at folio scale |
| C602 | Complementary — REGIME modulates magnitude, CC composition drives selection |
| C412 | Foundation — ch-preference anticorrelation decomposition uses this |

---

## Provenance

- **Phase:** SISTER_PAIR_DECOMPOSITION
- **Date:** 2026-01-26
- **Script:** en_subfamily_selection.py

---

## Navigation

<- [C602_regime_conditioned_subrole_grammar.md](C602_regime_conditioned_subrole_grammar.md) | [INDEX.md](INDEX.md) ->
