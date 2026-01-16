# A/C INTERNAL CHARACTERIZATION Phase

**Status:** COMPLETE | **Result:** PARTIAL SIGNAL | **Date:** 2026-01-15

---

## Purpose

Characterize A/C AZC folios via internal structural metrics, NOT product correlation. Following expert guidance that A/C encodes "fine-discrimination legality checkpoints" rather than product semantics.

**Key Insight:**
> Zodiac = sustained legality flow under coarse discrimination
> A/C = punctuated legality checkpoints under fine discrimination

---

## Background

The stratification tests (F-AZC-017, F-AZC-018) showed:
- Zodiac: p=0.85 (NO product correlation)
- A/C: p=0.29 (NO product correlation)

This is a **positive finding** - it confirms AZC is orthogonal to product identity by design.

But A/C still has unexplained structural features:
- Low cross-folio consistency (0.340 vs Zodiac 0.945)
- Varied scaffolds per folio
- Higher HT oscillation (C457)

**The question shifts from:** "What products does A/C encode?"
**To:** "What discrimination burden does A/C manage?"

---

## Three Probes

All probes are internal and operator-centric:

| # | Probe | Question |
|---|-------|----------|
| 1 | HT Phase-Reset Frequency | Do A/C folios force more attention resets? |
| 2 | MIDDLE Incompatibility Density | Are A/C folios activating denser constraint bundles? |
| 3 | Zone-Transition Entropy | Do A/C contexts require more frequent zone switching? |

---

## Results

| Probe | Prediction | Result | P-value | Effect |
|-------|------------|--------|---------|--------|
| **1. HT Phase-Reset** | A/C > Zodiac | NO SIGNAL | 1.00 | n/a |
| **2. MIDDLE Incompatibility** | A/C > Zodiac | **STRONG SIGNAL** | **0.0006** | r=-0.70 |
| **3. Zone-Transition** | A/C > Zodiac | NO SIGNAL | 0.9999 | opposite |

### Key Findings

**Probe 2 confirms the expert's hypothesis:**
- A/C mean incompatibility density: **0.55**
- Zodiac mean incompatibility density: **0.38**
- A/C activates significantly more densely incompatible MIDDLE subsets

**Unexpected finding from Probe 3:**
- Zodiac switch rate: 0.0176 (higher)
- A/C switch rate: 0.0039 (lower)
- A/C manages higher constraint density while staying WITHIN zones, not through zone switching

**Probe 1 is uninformative:**
- HT phase-class (EARLY/LATE) doesn't apply well to AZC data
- Zero transitions in both families

### Interpretation

> **A/C folios manage fine-discrimination through higher MIDDLE incompatibility density, not through zone switching. They hold more mutually exclusive constraints simultaneously while maintaining positional stability.**

This supports the expert's framing:
- Zodiac = sustained legality flow (more zone movement, lower incompatibility)
- A/C = punctuated checkpoints (less zone movement, higher incompatibility)

---

## Scripts

| File | Purpose |
|------|---------|
| `ac_ht_phase_reset.py` | Probe 1: HT transition frequency |
| `ac_incompatibility_density.py` | Probe 2: Local MIDDLE incompatibility |
| `ac_zone_transition.py` | Probe 3: Zone-transition entropy |

---

## Output Files

- `results/ac_ht_phase_reset.json`
- `results/ac_incompatibility_density.json`
- `results/ac_zone_transition.json`

---

## Expected Outcomes

| Probe | If A/C > Zodiac | If A/C ≈ Zodiac |
|-------|-----------------|-----------------|
| HT Phase-Reset | A/C manages attention burden | HT is system-agnostic |
| Incompatibility Density | A/C manages exclusion burden | Incompatibility is uniform |
| Zone-Transition | A/C manages context-switching | Zones are uniformly distributed |

**Any positive signal** confirms: A/C's scaffold diversity serves fine-discrimination, not product semantics.

**All null results** would suggest: A/C diversity is purely historical/scribal, not functional.

---

## Documentation Plan

Results go to FITs (F-AZC-019 through F-AZC-021), NOT constraints:

| Probe | FIT ID | Tier |
|-------|--------|------|
| HT Phase-Reset | F-AZC-019 | F2-F3 |
| Incompatibility Density | F-AZC-020 | F2-F3 |
| Zone-Transition Entropy | F-AZC-021 | F2-F3 |

---

## Semantic Guardrails

**DO:**
- Measure internal structural metrics
- Compare A/C vs Zodiac within AZC
- Interpret as "discrimination burden" or "attention load"
- Stay operator-centric

**DO NOT:**
- Correlate with products, materials, or Brunschwig
- Assert "A/C = complex products"
- Add structural constraints based on these probes
- Claim semantic content

---

*Phase created 2026-01-15*
