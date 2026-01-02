# Exploratory Program Roles
## Program Role Taxonomy
Classification based on control signature metrics. Each program assigned roles across 6 dimensions.
### Role Dimensions
| Dimension | Description | Metric Basis |
|-----------|-------------|---------------|
| Stability | How conservative vs aggressive | link_density, hazard_density, near_miss_count |
| Waiting | LINK operator usage pattern | link_density, max_consecutive_link |
| Convergence | Cycle behavior and terminal state | cycle_regularity, terminal_state |
| Recovery | Error recovery posture | recovery_ops_count |
| Scale | Program length/complexity | total_length |
| Special | Unique markers | reset_present, intervention_frequency |

### Role Distribution

**STABILITY**
| Role | Count | Percentage |
|------|-------|------------|
| MODERATE | 46 | 55.4% |
| CONSERVATIVE | 18 | 21.7% |
| AGGRESSIVE | 15 | 18.1% |
| ULTRA_CONSERVATIVE | 4 | 4.8% |

**WAITING**
| Role | Count | Percentage |
|------|-------|------------|
| LINK_MODERATE | 39 | 47.0% |
| LINK_HEAVY | 24 | 28.9% |
| LINK_SPARSE | 14 | 16.9% |
| LINK_HEAVY_EXTENDED | 6 | 7.2% |

**CONVERGENCE**
| Role | Count | Percentage |
|------|-------|------------|
| REGULAR_STABLE | 39 | 47.0% |
| REGULAR_OPEN | 33 | 39.8% |
| IRREGULAR | 8 | 9.6% |
| FAST_STABLE | 3 | 3.6% |

**RECOVERY**
| Role | Count | Percentage |
|------|-------|------------|
| HIGHLY_RECOVERABLE | 35 | 42.2% |
| RECOVERABLE | 28 | 33.7% |
| LOW_RECOVERY | 20 | 24.1% |

**SCALE**
| Role | Count | Percentage |
|------|-------|------------|
| EXTENDED | 43 | 51.8% |
| STANDARD | 29 | 34.9% |
| COMPACT | 11 | 13.3% |

**SPECIAL**
| Role | Count | Percentage |
|------|-------|------------|
| NONE | 70 | 84.3% |
| HIGH_INTERVENTION | 10 | 12.0% |
| RESTART_CAPABLE | 3 | 3.6% |

## Representative Programs by Role

### Stability Dimension
- **ULTRA_CONSERVATIVE**: f26v, f41v, f48v
  - Sample (f26v): link_density=0.504, hazard_density=0.496, near_miss=9
- **CONSERVATIVE**: f31v, f40v, f48r
  - Sample (f31v): link_density=0.469, hazard_density=0.515, near_miss=11
- **MODERATE**: f26r, f31r, f33r
  - Sample (f26r): link_density=0.396, hazard_density=0.554, near_miss=9
- **AGGRESSIVE**: f75r, f76r, f76v
  - Sample (f75r): link_density=0.303, hazard_density=0.668, near_miss=34

### Waiting Dimension
- **LINK_HEAVY_EXTENDED**: f26v, f48r, f48v
  - Sample (f26v): link_density=0.504, max_consecutive_link=7
- **LINK_HEAVY**: f31v, f34v, f40v
  - Sample (f31v): link_density=0.469, max_consecutive_link=6
- **LINK_MODERATE**: f26r, f33v, f34r
  - Sample (f26r): link_density=0.396, max_consecutive_link=5
- **LINK_SPARSE**: f31r, f33r, f46r
  - Sample (f31r): link_density=0.295, max_consecutive_link=7

## Quantitative Metric Summary
| Metric | Min | Max | Mean | Stdev |
|--------|-----|-----|------|-------|
| link_density | 0.204 | 0.576 | 0.383 | 0.070 |
| hazard_density | 0.406 | 0.771 | 0.582 | 0.067 |
| kernel_contact_ratio | 0.424 | 0.796 | 0.617 | 0.070 |
| cycle_regularity | 0.687 | 4.412 | 3.448 | 0.633 |
| intervention_frequency | 2.140 | 14.620 | 5.943 | 2.077 |
| near_miss_count | 2.000 | 79.000 | 23.699 | 17.216 |
| recovery_ops_count | 0.000 | 67.000 | 16.072 | 13.240 |
| total_length | 163.000 | 2222.000 | 906.602 | 555.507 |

## Cluster-Role Correlation
How do Lane 1 template clusters map to program roles?

| Cluster | Template | ULTRA_CONS | CONSERVATIVE | MODERATE | AGGRESSIVE |
|---------|----------|------------|--------------|----------|------------|
| 1 | TEMPLATE_C | 0 | 4 | 23 | 15 |
| 2 | TEMPLATE_A | 3 | 8 | 1 | 0 |
| 3 | TEMPLATE_A | 1 | 2 | 0 | 0 |
| 4 | TEMPLATE_A | 0 | 4 | 5 | 0 |
| 5 | TEMPLATE_B | 0 | 0 | 17 | 0 |

## Special Program Markers

**RESTART_CAPABLE** (3): f50v, f57r, f82v
- These programs can return to initial state
- **SPECULATIVE**: May represent full reset protocols or error recovery starting points

**HIGH_INTERVENTION** (10): f33r, f33v, f39r, f55r, f66v, f86v4, f94v, f95r2, f95v2, f116r
- Intervention frequency > 8 operations per cycle
- **SPECULATIVE**: May handle rapidly-changing conditions or sensitive substrates

**EXTENDED** (43): f66r, f75r, f75v, f76r, f76v, f77r, f77v, f78r, f78v, f79r, f79v, f80r, f80v, f81r, f81v, f82r, f82v, f83r, f83v, f84r, f84v, f86v6, f103r, f103v, f104r, f104v, f105v, f106r, f106v, f107r, f107v, f108r, f108v, f111r, f111v, f112r, f112v, f113r, f113v, f114r, f115r, f115v, f116r
- Program length > 800 instructions
- **STRUCTURALLY SUPPORTED**: Required for complete operational envelope (12.6% gap without)
