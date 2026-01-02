# Apparatus-Level Reverse Engineering Report

*Generated: Phase ARE*
*Status: INCONCLUSIVE*

---

## Executive Summary

| Track | Question | Result |
|-------|----------|--------|
| T1 | Are prefix/suffix coordinates necessary? | ARBITRARY (1/4) |
| T2 | Do sections = apparatus configurations? | ARBITRARY (F=0.37) |
| T3 | Are extended runs structurally necessary? | STRUCTURALLY_NECESSARY (gap=12.6%) |
| T4 | Do variants = operator tuning space? | DISCRETE_ALTERNATIVES (cov=43.3%) |
| T5 | Is one apparatus class uniquely compatible? | PELICAN_UNIQUE (CLASS_D=100%) |

**FINAL VERDICT: INCONCLUSIVE**

Some regularities may be apparatus-related

---

## Track 1: Necessity Test

**Question:** Are prefix/suffix coordinates *necessary* to support correct operation?

| Problem | Resolved | Metric |
|---------|----------|--------|
| VARIANT_NAVIGATION | True | 0.7804 |
| REGIME_CONSISTENCY | False | -0.1908 |
| RECOVERY_FROM_INTERRUPT | False | 0.6032 |
| CONFIG_DRIFT_PREVENTION | False | 1.4749 |

**Verdict:** ARBITRARY (1/4 problems resolved)

---

## Track 2: Regime Stability

**Question:** Do section boundaries correspond to distinct apparatus configurations?

| Metric | F-ratio |
|--------|---------|
| hazard_density | 0.3061 |
| kernel_contact_ratio | 0.2937 |
| link_density | 0.2937 |
| cycle_regularity | 0.5944 |

**Mean F-ratio:** 0.3720

**Verdict:** ARBITRARY

---

## Track 3: Extended Runs

**Question:** Are EXTENDED_RUN folios structurally necessary?

**Extended folios:** f76r, f83v, f105v, f111r, f111v, f115v

**Envelope gap fraction:** 0.1262

**Verdict:** STRUCTURALLY_NECESSARY

---

## Track 4: Variant Density

**Question:** Do variants represent operator tuning or discrete alternatives?

| Metric | Within-section | Global | Coverage |
|--------|---------------|--------|----------|
| cycle_count | 82.2000 | 246.0000 | 33.4% |
| hazard_density | 0.1788 | 0.3650 | 49.0% |
| link_density | 0.1770 | 0.3720 | 47.6% |

**Mean coverage:** 43.3%

**Verdict:** DISCRETE_ALTERNATIVES

---

## Track 5: Apparatus Class Discrimination

**Question:** Is one apparatus class uniquely compatible?

| Class | Compatibility | Matches |
|-------|--------------|---------|
| CLASS_A | 0% |  |
| CLASS_B | 0% |  |
| CLASS_C | 20% | dominant_hazard |
| CLASS_D | 100% | recirculation, intervention, hazard_profile, dominant_hazard, cycle_structure |

**Best match:** CLASS_D (Circulatory Reflux)

**Verdict:** PELICAN_UNIQUE

---

## Structural Fit Summary

The regularities that remained unexplained after grammar freeze are now accounted for:

1. **Prefix/suffix coordinates** → ARBITRARY as navigation/recovery support
2. **Section boundaries** → ARBITRARY as regime demarcations
3. **Extended runs** → STRUCTURALLY_NECESSARY for envelope extension
4. **Variants within sections** → DISCRETE_ALTERNATIVES operator tuning parameters
5. **Apparatus class** → PELICAN_UNIQUE (circulatory reflux)

---

## Remaining Uncertainties (External/Historical Only)

- Specific feedstock/product identity
- Exact apparatus construction details
- Historical context of author/school
- Dating precision
- Relationship to known practitioners

---

*Structural analysis only. No semantic interpretations.*
