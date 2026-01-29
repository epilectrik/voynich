# C659: PP Axis Independence

**Tier:** 2 | **Status:** CLOSED | **Scope:** A, B

## Finding

PP classification axes — co-occurrence, B-side behavior, material class, pathway, lane character, and section — are mutually independent. Cross-validation ARI between co-occurrence clusters and behavioral clusters: 0.052 (independent). No axis pair exceeds NMI=0.13. Co-occurrence tells you nothing about behavioral profile, and vice versa. Role variance explained by co-occurrence pools averages 14.6% (eta-squared range: 0.08-0.25). PP occupies a high-dimensional space where independent weak gradients along each axis produce unique per-MIDDLE positions.

## Evidence

- Co-occurrence vs behavioral: ARI=0.052, chi2 p=0.109 (84 PP overlap)
- NMI (pool, material) = 0.129
- NMI (pool, pathway) = 0.032
- NMI (pool, lane) = 0.062
- NMI (pool, section) = 0.087
- All cross-axis NMI < 0.15 — no axis captures another
- Role eta-squared by pool:
  - AUXILIARY: 0.247, ENERGY_OPERATOR: 0.174, FREQUENT_OPERATOR: 0.144
  - CORE_CONTROL: 0.087, FLOW_OPERATOR: 0.080
  - Mean: 0.146
- ARI(co-occurrence, existing material clusters) = 0.057

## Interpretation

PP structure is genuinely multi-dimensional. Knowing which PP co-occur in A records tells you almost nothing about how they behave in B execution. Knowing their material class tells you almost nothing about which other PP they co-occur with. Each classification axis captures a different, nearly orthogonal slice of PP identity. This explains why no single-axis classification compresses the PP vocabulary well: the space requires multiple independent coordinates to describe each MIDDLE's identity.

## Cross-References

- C509: PP and RI dimensions are orthogonal — extends here to WITHIN-PP orthogonality
- C506: PP composition doesn't propagate to B class structure — consistent with axis independence
- C656: Co-occurrence is continuous
- C657: Behavioral profiles are continuous
- C658: Material gradient is weak (36.2% entropy reduction)

## Provenance

PP_POOL_CLASSIFICATION, Script 2 (pp_pool_validation.py), Tests 6-7
