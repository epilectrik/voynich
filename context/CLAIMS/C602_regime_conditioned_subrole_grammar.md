# C602: REGIME-Conditioned Sub-Role Grammar

**Tier:** 2 | **Status:** CLOSED | **Scope:** B

---

## Statement

> Sub-group routing is REGIME-dependent for 4/5 tested pairs: EN->FQ (chi2=50.7, p=9.2e-6), FQ->EN (chi2=31.4, p=7.8e-3), AX->EN (chi2=30.0, p=1.2e-2), CC->EN (chi2=26.5, p=3.3e-2). The exception is AX->FQ (chi2=16.7, p=0.86) which is REGIME-independent. Core routing patterns (FQ_CONN->EN_CHSH, CC_OL_D->EN_QO) persist across all REGIMEs, but magnitudes shift.

---

## Evidence

**Test:** `phases/SUB_ROLE_INTERACTION/scripts/sub_role_conditioning.py`

### Homogeneity Tests

| Pair | chi2 | p | Verdict |
|------|------|---|---------|
| EN->FQ | 50.73 | 9.2e-6 | **REGIME-DEPENDENT** |
| FQ->EN | 31.37 | 7.8e-3 | **REGIME-DEPENDENT** |
| AX->EN | 29.99 | 1.2e-2 | **REGIME-DEPENDENT** |
| CC->EN | 26.54 | 3.3e-2 | **REGIME-DEPENDENT** |
| AX->FQ | 16.69 | 8.6e-1 | REGIME-INDEPENDENT |

### FQ_CONN->EN_QO Avoidance by REGIME

The core asymmetry (FQ_CONN avoids EN_QO) holds in every REGIME:

| REGIME | FQ_CONN->EN_QO | FQ_CONN->EN_CHSH |
|--------|---------------|-----------------|
| REGIME_1 | 0.31x | 1.28x |
| REGIME_2 | 0.16x | 1.32x |
| REGIME_3 | 0.00x | 1.53x |
| REGIME_4 | 0.12x | 1.63x |

The **direction** is invariant. The **magnitude** shifts — REGIME_3/4 show stronger CHSH preference than REGIME_1/2.

### EN->FQ REGIME Variation (Strongest Effect)

| REGIME | EN_CHSH->FQ_CONN | EN_QO->FQ_CONN |
|--------|-----------------|----------------|
| REGIME_1 | 1.08x | 0.93x |
| REGIME_2 | 1.19x | 0.68x |
| REGIME_3 | 0.95x | 1.03x |
| REGIME_4 | 1.54x | 0.54x |

REGIME_4 shows the strongest CHSH->FQ_CONN preference (1.54x). REGIME_3 is the most balanced.

### AX->FQ REGIME Independence

AX->FQ routing (AX_INIT->FQ_CONN preference) is stable regardless of REGIME:

| REGIME | AX_INIT->FQ_CONN |
|--------|-----------------|
| REGIME_1 | 1.71x |
| REGIME_2 | 1.29x |
| REGIME_3 | 1.44x |
| REGIME_4 | 1.81x |

Homogeneity p=0.86 — no significant REGIME effect. This is structural routing, not contextual.

---

## Interpretation

The sub-role grammar has two layers:
1. **Invariant routing** (structural): FQ_CONN->EN_CHSH, CC_OL_D->EN_QO, AX->FQ patterns hold across all REGIMEs. These are hardwired into the grammar.
2. **REGIME-modulated magnitudes**: The strength of preferences shifts with REGIME. REGIME_4 amplifies the CHSH preference; REGIME_3 partially relaxes it.

AX->FQ routing is purely structural (REGIME-independent), consistent with AX being a positional scaffold (C565) rather than a content-sensitive operator.

---

## Cross-References

| Constraint | Relationship |
|------------|--------------|
| C551 | Extended - REGIME specialization now visible at sub-group routing level |
| C545 | Extended - REGIME class profiles modulate cross-role sub-group routing |
| C598 | Refined - cross-boundary structure is partially REGIME-dependent |
| C599 | Connected - AX->FQ routing is the REGIME-independent exception |

---

## Provenance

- **Phase:** SUB_ROLE_INTERACTION
- **Date:** 2026-01-26
- **Script:** sub_role_conditioning.py

---

## Navigation

<- [C601_hazard_subgroup_concentration.md](C601_hazard_subgroup_concentration.md) | [INDEX.md](INDEX.md) ->
