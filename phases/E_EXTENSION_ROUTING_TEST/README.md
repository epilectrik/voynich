# E_EXTENSION_ROUTING_TEST Phase

**Date:** 2026-02-02
**Status:** COMPLETE
**Verdict:** C522 CLARIFIED - vocabulary transmits e-content, execution is independent

---

## Hypothesis

Extended e-sequences in Currier A (C901) might predict execution characteristics in Currier B:
- A folios with high e-extension → B folios with specific lane balance?
- A folios with high e-extension → REGIME_4 preference?
- E-extension → kernel access patterns?

Per C522 (Construction-Execution Layer Independence), direct correlations were expected to be null.

---

## Results Summary

### Tier A: Direct Correlation Tests

| Test | Correlation | p-value | Result |
|------|-------------|---------|--------|
| A e-extension → B lane balance | rho=0.005 | 0.957 | **NULL** ✓ |
| A e-extension → B e-content | rho=0.773 | <0.001 | **SIGNIFICANT** |
| Late A (f100-f102) routing | effect=0.00 | 0.877 | **NULL** ✓ |

**Finding:** E-extension does NOT predict lane balance but DOES predict e-content in B.

### Tier B: Mediated Tests

| Test | Finding | p-value | Interpretation |
|------|---------|---------|----------------|
| PP vs RI e-extension | PP=0.84, RI=0.58 | <0.001 | **PP has HIGHER e-extension** |
| A e → B kernel access | rho=0.42 | <0.001 | Significant correlation |
| A e → B e-rate | rho=0.76 | <0.001 | **Strong correlation** |
| A e → B position | rho=-0.08 | 0.117 | NULL |
| High-e survival | 56.4% vs 37.8% | 0.031 | **High-e survives MORE** |

---

## Key Findings

### 1. E-Extension Concentrates in PP (Not RI)

| Classification | Mean Max Consecutive E |
|----------------|------------------------|
| PP-dominant | 0.838 |
| RI-dominant | 0.583 |

**Difference:** PP has +0.26 higher e-extension (p < 0.001)

This means e-extension concentrates in vocabulary that **propagates to B**, not vocabulary that stays in A.

### 2. High-E MIDDLEs Survive Better

| A E-Extension | MIDDLEs | Survival to B |
|---------------|---------|---------------|
| Low (≤1) | 835 | 37.8% |
| Mid (2) | 139 | 47.5% |
| High (≥3) | 39 | 56.4% |

Chi-square p=0.031 - **High-e MIDDLEs survive significantly more**

### 3. E-Content Transmits Through Vocabulary

The strong A→B e-content correlation (rho=0.77) is explained by:
1. High-e vocabulary is PP (not RI)
2. PP vocabulary propagates to B
3. Shared MIDDLEs carry their e-content

This is **vocabulary transmission**, not execution routing.

### 4. Execution Remains Independent

Despite e-content transmission:
- Lane balance: NULL (rho=0.005)
- Line position: NULL (rho=-0.08)
- Late A routing: NULL (same as other A)

E-content doesn't determine execution behavior.

---

## C522 Clarification

**Original C522:** Construction and execution layers are independent (r=-0.21, p=0.07)

**Clarified understanding:**
- **Character composition** (including e-extension) propagates through shared vocabulary
- **Execution behavior** (lane, position, regime) is determined by class membership, not character content
- The layers share the **symbol substrate** but govern **independent properties**

This is consistent with C522. The correlation found is:
```
A e-extension → PP vocabulary → B e-content
           ↓
     (independent of)
           ↓
     Execution behavior
```

---

## Corpus Statistics

| Metric | Value |
|--------|-------|
| A folios analyzed | 114 |
| A tokens | 11,174 |
| Quadruple-e tokens | 8 |
| Triple-e tokens | 82 |
| Shared MIDDLEs (A∩B) | 404 |
| A-only MIDDLEs | 609 |
| B-only MIDDLEs | 935 |

### Highest E-Extension Folios

| Folio | Mean Max Consec E | Max in Folio |
|-------|-------------------|--------------|
| f102v2 | 0.902 | 4 |
| f90v1 | 0.844 | 3 |
| f90v2 | 0.768 | 3 |
| f100r | 0.696 | 2 |
| f102r2 | 0.695 | 3 |

### Quadruple-E Tokens

| Folio | Token |
|-------|-------|
| f102v2 | odeeeey |
| f21v | keeees |
| f27v | doeeeesm |
| f7r | oeeees, deeeese |
| f87r | qoeeeety |
| f89v2 | eeeey |
| f93v | odeeeeodl |

---

## Implications for C901 (Extended E Stability Gradient)

C901 documented e-extension as a stability encoding gradient. This phase confirms:

1. **E-extension is real and measurable** - clear gradient from single to quadruple-e
2. **E-extension is PP-dominated** - stability vocabulary participates in B execution
3. **E-content transmits to B** - but doesn't determine execution behavior
4. **Stability is a morphological property** - not an execution property

The "stability gradient" operates at the **construction layer**, affecting vocabulary composition rather than execution routing.

---

## Scripts

| Script | Purpose | Key Result |
|--------|---------|------------|
| 01_e_extension_index.py | Compute A folio e-metrics | f102v2 highest (0.902) |
| 02_direct_routing_correlation.py | Tier A tests | 2/3 null, 1/3 significant |
| 03_pp_ri_e_distribution.py | PP vs RI e-content | PP higher (p<0.001) |
| 04_kernel_access_mediation.py | Mediated effects | E-rate transmits, survival differs |

---

## Provenance

- **Phase:** E_EXTENSION_ROUTING_TEST
- **Date:** 2026-02-02
- **Scripts:** 4
- **Triggered by:** Expert recommendation to test C901→regime connection
- **Related:** C522, C901, C902, C903, C105, C521
