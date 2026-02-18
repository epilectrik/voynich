# C1107: Stars Section LINK Monitoring Concentration

**Tier:** 2 (STRUCTURAL INFERENCE)
**Scope:** B
**Phase:** STARS_RECIPE_CHARACTERIZATION (Phase 392)
**Contrasts:** C1085 (Bio reduced LINK — 0.6% vs 2.8%)

---

## Statement

The Stars/Recipe section has 7.4x higher LINK operator density than non-Stars sections (0.032 vs 0.004, Mann-Whitney p<0.0001, rank-biserial r=-0.913). This survives REGIME_1 control (Stars_R1=0.034 vs non-Stars_R1=0.006, p<0.0001).

This is the OPPOSITE of Bio, which has 4.7x FEWER LINK operators than non-Bio (Phase 385). The two sections occupy opposite extremes of the LINK spectrum.

---

## Evidence

### S5: LINK Density
- Stars: mean 0.0324, n=23
- Non-Stars (B+H): mean 0.0044, n=52
- Mann-Whitney U=1144, p<0.0001
- Rank-biserial r=-0.913 (very large effect)
- REGIME_1 controlled: Stars_R1=0.0337, non-Stars_R1=0.0058, p<0.0001

### Contrast with Bio (Phase 385 T3)
- Bio LINK: 0.006 (4.7x LOWER than non-Bio 0.028)
- Stars LINK: 0.032 (7.4x HIGHER than non-Stars 0.004)

### S4: CC Trigger Profile
Stars also shows a radically different control entry pattern:
| Trigger | Stars | Non-Stars |
|---------|-------|-----------|
| CLOSE_FLOW | 39.5% | 28.6% |
| FQ_FREQUENT | 27.7% | 15.3% |
| QO_ENERGY | 12.7% | 31.0% |
| CHSH_PRECISION | 20.1% | 25.1% |

Chi2=117.3, p=3.0e-25, Cramer's V=0.260.

Stars is CLOSE_FLOW and FQ_FREQUENT dominant while non-Stars is QO_ENERGY dominant. Stars avoids the energy lane.

---

## Interpretation

Stars programs require intensive monitoring (high LINK density) with frequent status checks (FQ_FREQUENT elevated) and flow closure operations (CLOSE_FLOW elevated), while avoiding direct energy manipulation (QO_ENERGY depleted). Combined with the e-stability kernel enrichment (C1106), this paints a consistent picture: Stars encodes a process requiring careful observation and stability management rather than direct thermal manipulation.

The Bio-Stars LINK contrast is striking: Bio needs almost no external monitoring (self-contained sustained heating), while Stars needs maximum monitoring (fire-method observation per C930). This is consistent with the Brunschwig framework: balneum mariae (Bio) maintains gentle, uniform heat that needs no adjustment, while direct fire (Stars) requires constant vigilance to prevent overheating.

---

## Provenance

- Phase: 392 (STARS_RECIPE_CHARACTERIZATION), Tests S4, S5
- Script: `phases/STARS_RECIPE_CHARACTERIZATION/scripts/stars_recipe_characterization.py`
- Results: `phases/STARS_RECIPE_CHARACTERIZATION/results/stars_recipe_characterization.json`
- Related: C930, C1085, C1106
