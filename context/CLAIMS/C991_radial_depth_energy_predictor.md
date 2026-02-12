# C991: Radial Depth Dominates Line-Level Energy

**Tier:** 2 | **Scope:** A↔B | **Phase:** CONSTRAINT_ENERGY_FUNCTIONAL

## Statement

Radial depth in the residual embedding (norm of residual vector) is the dominant predictor of line-level energy: ρ = -0.517 (p = 10⁻¹⁶⁴). Lines composed of shallow-manifold MIDDLEs are compatible (E = +0.001); deep-manifold MIDDLEs create tension (E = -0.027). AZC zone restrictiveness maps to radial depth (R3 deepest at 1.74, C shallowest at 1.45), and escape potential correlates weakly with energy (ρ = +0.100). This establishes geometric closure: escape rate is a projection of position in the constraint manifold.

## Evidence

### Depth-Energy Correlation (T3)

| Depth Bin | E | Interpretation |
|-----------|---|----------------|
| Shallow (Q1) | +0.001 | Compatible |
| Mid-shallow (Q2) | -0.006 | Mildly tense |
| Mid-deep (Q3) | -0.013 | Tense |
| Deep (Q4) | -0.027 | High tension |

Spearman ρ(depth, E) = -0.517 (p = 10⁻¹⁶⁴) — strongest single predictor found in this phase.

### Zone-Depth Mapping (T3)

| AZC Zone | Mean Radial Depth | Escape Rate |
|----------|-------------------|-------------|
| C | 1.449 | 1.4% |
| R1 | 1.417 | 2.0% |
| R2 | 1.532 | 1.2% |
| R3 | 1.740 | 0.0% |
| S1 | 1.470 | 0.0% |
| S2 | 1.619 | 0.0% |

R3 (most restricted, zero escape) is the deepest. This mechanizes C443: restrictiveness = depth in the constraint manifold.

### Geometric Closure Triangle (T3)

| Link | ρ | p |
|------|---|---|
| Depth → Energy | -0.517 | 10⁻¹⁶⁴ |
| Escape → Energy | +0.100 | 8×10⁻⁷ |
| Escape → Depth | -0.102 | 5×10⁻⁷ |

All three links significant. Escape rate, radial depth, and energy form a coherent geometric triangle.

### Interpretation

1. **Radial depth is the geometric mechanism** behind constraint tension — deeper MIDDLEs have more unique constraint neighborhoods, less mutual overlap
2. AZC zone restrictiveness is not arbitrary — it reflects actual depth in the constraint manifold
3. Escape potential correlates with shallowness — MIDDLEs from shallow regions have more compatible neighbors and thus more "escape routes"
4. This is the expert's "geometric closure": escape rate becomes a projection of position in the constraint manifold

## Provenance

- T3 (escape and zone association)
- Mechanizes C443 (positional escape gradient) geometrically
- Extends C987 (continuous manifold) — the manifold has a radial structure from compatible core to tense periphery
- Explains C990 (elevated tension) — B uses deep-manifold MIDDLEs that create tension by construction
