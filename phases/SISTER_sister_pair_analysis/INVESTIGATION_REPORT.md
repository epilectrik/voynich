# Investigation Report: Restart Folios & HT Rotation Trigger

**Date:** 2026-01-08
**Status:** CLOSED

---

## Investigation 1: Restart Folios (f50v, f57r, f82v)

### Question
What structurally distinguishes restart-capable programs?

### Findings

**The 3 restart folios are HIGHLY HETEROGENEOUS:**

| Folio | Forgiveness | Escape Density | Hazard Density | Quartile |
|-------|-------------|----------------|----------------|----------|
| f50v | 1.576 | 0.112 | 0.031 (LOWEST) | Q3 |
| f57r | 0.405 | 0.069 | 0.080 | Q1 (BRITTLE) |
| f82v | 2.553 | 0.310 (HIGHEST) | 0.109 | Q4 (FORGIVING) |

**Only shared property:** Below-average LINK density (-28.8% vs population)

### f57r Uniqueness (only reset-present folio)

f57r is the most brittle of the three:
- Forgiveness: -1.659 below average of f50v/f82v
- Escape density: -0.142 below average

Post-reset shows re-initialization pattern:
- ch-: 43.6% → 25.0% (-18.6%)
- da-: 7.7% → 25.0% (+17.3%)

### Interpretation

No generalizable structural signature for restart capability. Reset appears to be a **design response to specific program needs** rather than a program-type property.

### Tier Assessment

**CLOSURE** — No constraint warranted. The heterogeneity is the finding.

---

## Investigation 2: HT Prefix Rotation Trigger

### Question
What triggers HT prefix rotation (EARLY: op, pc, do vs LATE: ta)?

### Findings

**Preceding grammar prefix predicts HT prefix choice:**

| Test | Value | Significance |
|------|-------|--------------|
| Chi-square | 214.70 | p < 0.000001 |
| Cramer's V (full table) | 0.143 | Weak |
| Permutation test | p = 0.001 | PASS |
| **EARLY vs LATE V** | **0.319** | **MODERATE** |

**Key discriminators:**

| Grammar Prefix | EARLY % | LATE % | Difference |
|----------------|---------|--------|------------|
| ch- | 17.1% | 46.6% | **+29.5% (LATE)** |
| qo- | 27.7% | 11.4% | **-16.4% (EARLY)** |
| sh- | 15.3% | 8.0% | -7.4% (EARLY) |

**ta-after-ch enrichment:**
- Observed: 46.6%
- Baseline: 24.0%
- Enrichment: **1.94x**
- z-score: 4.96
- p < 0.000001

### What Does NOT Trigger Rotation

| Factor | EARLY | LATE | Verdict |
|--------|-------|------|---------|
| Line position | 26.3% init | 27.0% init | NO SIGNAL |
| Kernel contact | 95.2% | 97.1% | UNIVERSAL |

### Interpretation

HT prefix choice is predicted by the preceding grammar token:
- **ta (LATE)** strongly follows **ch-** tokens (1.94x enrichment)
- **EARLY prefixes** follow **qo-** and **ot-** tokens more often

This suggests HT "watches" the grammar stream and responds to phase-indicating events.

### Tier Assessment

**TIER 2** — Significant correlation with moderate effect size (V = 0.319 for EARLY/LATE).

---

## New Constraint

### C413 (Tier 2, STRUCTURAL) - CANDIDATE

**HT prefix phase-class (EARLY vs LATE) is predicted by preceding grammar prefix. LATE (ta) follows ch- at 1.94x enrichment; EARLY (op, pc, do) follows qo- preferentially. Cramer's V = 0.319.**

---

## Scripts

- `restart_folio_analysis.py` — Restart folio structural analysis
- `ht_rotation_trigger.py` — Initial HT trigger exploration
- `ht_grammar_correlation_test.py` — Rigorous statistical validation

---

## Summary

| Investigation | Finding | Tier |
|---------------|---------|------|
| Restart folios | No structural signature (heterogeneous) | Closure |
| HT rotation trigger | Preceding grammar prefix predicts HT prefix | **Tier 2** |

---

*Investigation complete.*
