# C614: AX MIDDLE-Level Routing

**Tier:** 2 | **Status:** CLOSED | **Scope:** CURRIER_B | **Source:** AX_BEHAVIORAL_UNPACKING

## Statement

AX MIDDLE predicts successor role within INIT and MED subgroups (V=0.147-0.167, p<0.001) but NOT FINAL (p=0.645). However, AX MIDDLE does NOT predict the successor's MIDDLE (no priming). AX MIDDLE diversity strongly couples with operational diversity at folio level (EN rho=+0.796***, FQ rho=+0.660***). Class 22 is a positional outlier: 62.2% line-final vs 32.4% for other AX_FINAL classes.

## Evidence

### MIDDLE-Level Routing (Section 1)

| Subgroup | Chi-squared | p-value | Cramer's V | MIDDLEs tested |
|----------|-------------|---------|-------------|----------------|
| AX_INIT | 136.69 | 0.000003 | 0.167 | 6 |
| AX_MED | 190.49 | <0.000001 | 0.147 | 13 |
| AX_FINAL | 4.15 | 0.645 | 0.061 | 4 |

Within INIT and MED, the specific MIDDLE carried by an AX token adds routing information beyond what subgroup position alone provides. FINAL subgroup shows no MIDDLE-level differentiation.

### Priming Test (Section 2)

No priming effect detected. AX MIDDLE does not predict the MIDDLE of the next operational token:

| Subgroup | Observed match | Null mean | Permutation p |
|----------|---------------|-----------|---------------|
| AX_INIT | ~3.5% | ~3.5% | >0.05 |
| AX_MED | ~3.5% | ~3.5% | >0.05 |
| AX_FINAL | ~3.5% | ~3.5% | >0.05 |

Partial match rate (shared substring >= 2 chars): 7.1% (not significantly above null).

AX MIDDLEs select WHICH ROLE follows, not which specific material that role carries.

### Diversity Coupling (Section 3)

| Correlation | Spearman rho | p-value |
|-------------|-------------|---------|
| AX vs EN MIDDLE diversity | +0.796 | <0.001 *** |
| AX vs FQ MIDDLE diversity | +0.660 | <0.001 *** |

Folios with richer AX vocabulary use richer operational vocabulary. This coupling is structural, not causal (shared complexity driver).

### Class 22 (Section 4)

| Metric | Class 22 | Other AX_FINAL |
|--------|----------|----------------|
| Mean position | 0.799 | ~0.65 |
| Line-final rate | 62.2% | 32.4% |
| Members | 7 tokens (ly, ry, lr, tey, m, g, empty) |
| Occurrences | 45 |

Class 22's 60% context detectability (C572) is explained by extreme line-final positioning, not behavioral distinctiveness.

## Refines

- **C572**: Class-level collapse is confirmed, but MIDDLE-level routing exists within INIT and MED subgroups
- **C571**: Confirms PREFIX selects role, MIDDLE carries material. Extends: MIDDLE also influences routing target selection

## Related

C563, C571, C572, C599

## Method

Chi-squared contingency tables (MIDDLE x successor role), permutation test for priming (1000 shuffles), Spearman correlation for diversity coupling. Bonferroni-corrected within script.
