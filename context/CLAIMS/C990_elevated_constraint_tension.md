# C990: B Operates at Elevated Constraint Tension

**Tier:** 2 | **Scope:** A↔B | **Phase:** CONSTRAINT_ENERGY_FUNCTIONAL

## Statement

The line-level energy functional E(line) = mean pairwise residual cosine similarity is well-defined (std=0.022, 99.7% coverage) and reveals that Currier B lines operate at ELEVATED constraint tension: mean E = -0.011, significantly below random (shift -0.016, KS p = 10⁻¹⁰¹). B does not minimize compatibility energy — it operates at a specific tension level modulated by EN density (ρ=+0.216), lane identity (QO > CHSH), and REGIME (R4 lowest). Currier A lines are the opposite: E = +0.073, well above random.

## Evidence

### Energy Distribution (T1)

| System | Mean E | vs Random | KS p |
|--------|--------|-----------|------|
| Currier B | -0.011 | -0.016 below | 10⁻¹⁰¹ |
| Currier A | +0.073 | +0.067 above | 10⁻⁸⁴ |
| Random null | +0.004 | — | — |

B-A shift = -0.084 (massive, p = 10⁻¹⁷⁵). No line-size correlation (ρ=-0.029).

### Hazard Modulation (T2)

| Modulator | Effect | p-value |
|-----------|--------|---------|
| EN density | ρ=+0.216 (more EN → higher E) | 6×10⁻²⁷ |
| QO vs CHSH lane | QO +0.002 higher | 0.001 |
| REGIME | R4 lowest (-0.014), R1 highest (-0.010) | 0.002 |
| Folio position | Flat (ρ=0.003) | 0.90 |

### Interpretation

1. B execution DOES NOT minimize compatibility energy — it actively maintains elevated tension
2. The 80.2% token-level concordance (C989) coexists with net negative cosine — B respects boundaries while operating near them
3. EN tokens (energy operators) carry more compatible MIDDLEs — the operational core runs at lower tension than scaffold
4. REGIME_4 (precision) runs at highest tension — precision requires operating closer to constraint boundaries
5. This reversal (elevated tension, not minimized) suggests B's grammar uses constraint tension functionally — as an operating parameter, not a penalty to avoid

## Provenance

- T1 (energy definition), T2 (hazard association)
- Extends C989 (B inhabits A's geometry) with the qualifier: inhabits at elevated tension
- Consistent with C669 (hazard proximity tightening) — tighter proximity = operation near constraints
- REGIME modulation consistent with C979 (topology invariant, weights shift)
