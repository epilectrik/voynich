# Process Class Exclusion Analysis

## Question
Which known process classes are structurally incompatible with Voynich control-signatures?

## Aggregate Signature Metrics

- **reset_ratio:** 0.036
- **mean_hazard_density:** 0.582
- **mean_cycle_count:** 106.73
- **cycle_variance:** 71.25
- **recovery_present:** True
- **terminal_statec_ratio:** 0.578

---

## Exclusion Analysis

### [~] Mechanical timing systems
**Status:** SOFT_EXCLUDED
**Triggers:** insufficient reset pattern
**Justification:** Some timing characteristics but not conclusive

### [~] Astronomical/calendrical
**Status:** SOFT_EXCLUDED
**Triggers:** missing symbolic encoding patterns
**Justification:** No clear astronomical number patterns

### [~] Biological cultivation
**Status:** SOFT_EXCLUDED
**Triggers:** high variance in cycle structure
**Justification:** Cultivation requires growth/decay asymmetry

### [~] Open-loop control
**Status:** SOFT_EXCLUDED
**Triggers:** some recovery ops present
**Justification:** System shows closed-loop characteristics

### [?] Discrete batch processing
**Status:** PLAUSIBLE
**Supporting Features:** some terminal variation
**Justification:** Cannot rule out batch-like segments

### [?] Continuous closed-loop control
**Status:** PLAUSIBLE
**Supporting Features:** cyclic structure (mean 106.7 cycles), hazard density 0.58, kernel-centric operation
**Justification:** Signature compatible with closed-loop thermal/chemical control

---

## Legend

- **HARD_EXCLUDED**: Structurally impossible given signature
- **SOFT_EXCLUDED**: Incompatible with most known instances of this class
- **PLAUSIBLE**: Signature is compatible; note supporting features
