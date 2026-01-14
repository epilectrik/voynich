# C477 - HT TAIL CORRELATION

**Tier:** 2 | **Status:** CLOSED | **Source:** HT_VARIANCE_DECOMPOSITION probe (2026-01-12)

---

## Statement

HT density correlates with tail MIDDLE pressure (r = 0.504, p = 0.0045). When folios have more rare MIDDLEs, HT density is higher.

---

## Evidence

### Regression Analysis (N = 30 AZC folios)

| Predictor | Correlation (r) | p-value | Ablation Importance |
|-----------|-----------------|---------|---------------------|
| **tail_pressure** | **0.504** | **0.0045*** | **68.2%** |
| incompatibility_density | 0.174 | 0.36 | 1.8% |
| novelty | 0.153 | 0.42 | 6.3% |
| hub_suppression | 0.026 | 0.89 | 0.1% |

**Overall R² = 0.2793** (28% of HT variance explained)

### Interpretation

| R² Range | Interpretation | This Result |
|----------|----------------|-------------|
| 0.50+ | Strongly tied to discrimination | - |
| **0.25-0.40** | **Coarse vigilance signal** | **R² = 0.28** |
| 0.10-0.25 | Weak connection | - |
| <0.10 | HT signals something else | - |

---

## Mechanism

- **Common MIDDLEs (hubs)** are easy to recognize → LOW cognitive load → LOW HT
- **Rare MIDDLEs (tail)** require more attention to discriminate → HIGH cognitive load → HIGH HT
- **HT rises when rare variants are in play** → anticipatory vigilance

| MIDDLE Type | Cognitive Load | HT Response |
|-------------|---------------|-------------|
| Hubs ('a','o','e') | LOW | Lower HT |
| Common MIDDLEs | LOW | Lower HT |
| **Rare MIDDLEs (tail)** | **HIGH** | **Higher HT** |

---

## Integration

This grounds HT as a **cognitive load balancer** specifically tied to **tail discrimination complexity**:

| Layer | Role | Grounding |
|-------|------|-----------|
| Currier B | Execution safety | Frozen Tier 0 |
| Currier A | Coverage control | C476 (hub rationing) |
| AZC | Decision gating | C437-C444 |
| **HT** | **Vigilance signal** | **C477 (this constraint)** |

---

## Related Constraints

- C461 - HT density correlates with MIDDLE rarity (earlier Tier 3 finding, now elevated)
- C476 - Coverage Optimality (what A optimizes)
- C478 - Temporal Scheduling (how A achieves coverage)

---

## Files

- `phases/HT_VARIANCE_DECOMPOSITION/ht_variance_decomposition.py`
- `results/ht_variance_decomposition.json`

---

← [INDEX.md](INDEX.md)
