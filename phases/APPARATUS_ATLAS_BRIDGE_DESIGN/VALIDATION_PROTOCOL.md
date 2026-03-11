# Validation Protocol

**Phase 582: APPARATUS_ATLAS_BRIDGE_DESIGN**

## Experiment Order

Order matters -- each experiment builds on the previous.

0. E0_rig_characterization (PREREQUISITE)
1. E1_family_analog_calibration
2. E2_closure_threshold_mapping
3. E3_counterfeit_closure_probe
4. E4_productive_disruption_assay
5. E5_sister_mode_observation
6. E6_subroutine_independence

## Overview

| Experiment | Level | Min Runs | Priority | Constraints Tested |
|------------|-------|----------|----------|--------------------|
| Rig Characterization | 1 | 3 | PREREQUISITE -- before anything else | N/A |
| Family Analog Calibration | 2 | 9 | First hypothesis test | C1668 (family gradient), C1640 (family partition) |
| Closure Threshold Mapping | 1 | 15 | Core validation experiment | C1642 (strength-dependent), C1644 |
| Counterfeit Closure Probe | 2 | 12 | Key differentiator between families | C1645 (morphology-selective counterfeiting), C1639 (close-recovery dominance) |
| Productive Disruption Assay | 1 | 10 | Core DYE validation | C1632 (YGA validated), C1633 (DYE validated), C1634 (DVA validated) |
| Sister-Mode Observation Assay | 1 | 6 | Lower priority | C929, C1298, C1299 |
| Subroutine Independence Analog | 1 | 6 | Lowest priority | C845, C1399, C1400 |

## Rig Characterization

**Priority:** PREREQUISITE -- before anything else

**Purpose:** Establish baseline behavior of the apparatus before any hypothesis testing.

**Equipment level:** 1

**Minimum runs:** 3

### Measurements

- Thermal lag: time from heater change to body temperature response
- Steady-state reproducibility: T_body variance over 30 min at constant setting
- Sensor noise floor: temperature reading variance at thermal equilibrium
- Condensation onset: time and temperature at first condensate appearance
- Cooling curve: body temperature decay after heater cutoff

### Procedure

1. Bring apparatus to thermal equilibrium at operating temperature
2. Record all channels for 30 minutes (baseline)
3. Step-change heater setting (3 levels: low, medium, high)
4. Record thermal response curves for each step
5. Perform 3 closure maneuvers (seal and unseal) to measure repeatability
6. Record cooling curve after full heater cutoff

### Pass/Fail Criteria

- Temperature sensors respond to heater changes within 60s (thermal lag < 60s)
- Steady-state T_body variance < 2 degrees C over 30 min
- Closure maneuver timing repeatable within 5s
- Sensor noise < 0.5 degrees C at equilibrium

## Family Analog Calibration

**Priority:** First hypothesis test

**Purpose:** Tune three operating modes on the rig to approximate A1/A2/A3 families.

**Equipment level:** 2

**Minimum runs:** 9

### Measurements

- DVA_phys for each family configuration
- YGA_phys for each family configuration
- DYE_phys for each family configuration
- CCS1_phys (forgivingness): null vs grammar closure comparison
- Thermal gradient profiles (body-head) per family

### Procedure

1. Configure A1-like mode: water bath, loose head, no recirculation
2. Run 3 identical batches with lavender, measuring all channels
3. Configure A2-like mode: sealed joints, recirculation loop active
4. Run 3 identical batches with same material
5. Configure A3-like mode: partial seal, collection without full recirculation
6. Run 3 identical batches with same material
7. Compare DVA_phys/YGA_phys/DYE_phys across configurations

### Pass/Fail Criteria

- A2-like configuration shows higher forgivingness (CCS1_phys) than A1-like
- Thermal gradient profiles differ measurably between configurations
- At least 2/3 family analogs are distinguishable by DVA_phys or YGA_phys

**Hardware nulls:** N5_sham_intervention

**Constraints tested:** C1668 (family gradient), C1640 (family partition)

## Closure Threshold Mapping

**Priority:** Core validation experiment

**Purpose:** Vary closure strength systematically. Estimate CTS_phys threshold per family.

**Equipment level:** 1

**Minimum runs:** 15

### Measurements

- DVA_phys at each closure strength level
- YGA_phys at each closure strength level
- DYE_phys at each closure strength level
- CTS_phys composite score at each level

### Procedure

1. Define 5 closure strength levels: 20%, 40%, 60%, 80%, 100% of full closure
2. 20% = slight heat reduction only, no seal change
3. 40% = moderate heat reduction, partial seal (loose gasket)
4. 60% = significant heat reduction, seal tightened but not luted
5. 80% = major heat reduction, seal complete, flow partially diverted
6. 100% = full closure: heat off, seal complete, flow fully diverted
7. Run each level 3 times, randomized order within family configuration
8. Compute CTS_phys for each closure and plot DYE_phys vs CTS_phys
9. Identify threshold where DYE_phys turns positive

### Pass/Fail Criteria

- DYE_phys increases monotonically with CTS_phys (Spearman rho > 0.5)
- Identifiable threshold where DYE_phys transitions from negative to positive
- Threshold differs between A1-like and A2-like configurations (if Level 2)

**Hardware nulls:** N1_matched_time_no_seal, N5_sham_intervention

**Constraints tested:** C1642 (strength-dependent), C1644

## Counterfeit Closure Probe

**Priority:** Key differentiator between families

**Purpose:** Inject weak/morphologically fake closures to test which configurations accept them productively.

**Equipment level:** 2

**Minimum runs:** 12

### Measurements

- DVA_phys for counterfeit vs real closures
- YGA_phys for counterfeit vs real closures
- DYE_phys comparison (counterfeit vs real vs null)
- CTS_phys of counterfeit closures (should be sub-threshold)

### Procedure

1. Define 3 counterfeit closure types:
   a. Matched-time without seal (N1): same timing, seal omitted
   b. Matched-heat without routing (N2): temperature drops, flow unchanged
   c. Partial seal without heat change: seal tightened, heat maintained
2. Run each counterfeit type on A1-like and A2-like configurations
3. Compare DYE_phys to: (a) real closure, (b) sham intervention (N5)
4. Record which counterfeits A2-like accepts productively (DYE_phys > 0)

### Pass/Fail Criteria

- A2-like configuration accepts more counterfeit closures productively than A1-like
- At least one counterfeit type produces DYE_phys > 0 in A2-like but not A1-like
- Sham intervention (N5) produces DYE_phys near zero in both configurations

**Hardware nulls:** N1_matched_time_no_seal, N2_matched_heat_no_routing, N5_sham_intervention

**Constraints tested:** C1645 (morphology-selective counterfeiting), C1639 (close-recovery dominance)

## Productive Disruption Assay

**Priority:** Core DYE validation

**Purpose:** Matched disturbance: real packet vs null packet analogs. Tests whether grammar-specified packets produce positive DYE_phys.

**Equipment level:** 1

**Minimum runs:** 10

### Measurements

- DVA_phys for grammar-derived vs null packets
- YGA_phys for grammar-derived vs null packets
- DYE_phys comparison
- Process quality before and after intervention (sensory assessment)

### Procedure

1. Define grammar-derived closure packet: full sequence per packet library
2. Define matched null packet: same energy budget, random timing (N4)
3. Run alternating grammar/null packets within same session
4. Measure DVA_phys and YGA_phys for each packet
5. Compute DYE_phys = YGA_phys / DVA_phys for each
6. Compare grammar DYE_phys to null DYE_phys

### Pass/Fail Criteria

- Grammar-specified packets produce mean DYE_phys > 0 (useful gain per disturbance)
- Grammar DYE_phys > null DYE_phys (p < 0.1, paired comparison)
- DVA_phys > 0 for both grammar and null packets (confirming actual disturbance)

**Hardware nulls:** N4_random_timing_matched_energy, N5_sham_intervention, N6_delayed_intervention

**Constraints tested:** C1632 (YGA validated), C1633 (DYE validated), C1634 (DVA validated), C1635, C1636

## Sister-Mode Observation Assay

**Priority:** Lower priority

**Purpose:** Test ch-style discrete verification vs sh-style continuous monitoring.

**Equipment level:** 1

**Minimum runs:** 6

### Measurements

- Product quality under discrete-check protocol
- Product quality under continuous-monitor protocol
- Number of interventions under each protocol
- Failure rate under each protocol

### Procedure

1. ch-style (discrete): check product at defined intervals only (every 5 min)
2. sh-style (continuous): monitor process continuously, intervene when needed
3. Run same distillation batch under each protocol, 3x each
4. Compare product quality and failure rates

### Pass/Fail Criteria

- ch-style produces more precise outcomes (lower quality variance)
- sh-style produces fewer failures (lower failure count)
- Protocols are distinguishable by at least one metric

**Constraints tested:** C929, C1298, C1299

## Subroutine Independence Analog

**Priority:** Lowest priority

**Purpose:** Test whether operational subroutine order matters.

**Equipment level:** 1

**Minimum runs:** 6

### Measurements

- Product quality under order A-then-B
- Product quality under order B-then-A
- Process metrics (DVA_phys, YGA_phys) for each order

### Procedure

1. Define two operational subroutines (e.g., two distillation passes)
2. Execute in order A->B for 3 runs
3. Execute in order B->A for 3 runs
4. Compare final product quality

### Pass/Fail Criteria

- No significant difference in product quality between orders (p > 0.1)
- Process metrics comparable within measurement uncertainty

**Constraints tested:** C845, C1399, C1400

## Statistical Notes

- **minimum_effect_size:** Medium (Cohen d > 0.5) for primary experiments (E2, E4)
- **alpha_level:** 0.1
- **power_target:** 0.8
- **primary_tests:** Paired comparisons within session (reduces between-run variance)
- **randomization:** Randomize intervention order within sessions where possible
- **blinding:** Not feasible for operator; use sham intervention (N5) as attention control
- **multiple_comparisons:** Pre-specify primary comparison per experiment; secondary comparisons are exploratory

## Safety Precautions

- All experiments conducted with fume hood or adequate ventilation
- Class B fire extinguisher within arm reach
- Heat-resistant gloves worn when handling hot apparatus
- Safety glasses worn during all operations
- Never leave apparatus unattended while heat source is active
- Keep water source nearby for cooling emergencies
- Lavender is GRAS (generally recognized as safe); no toxic material in primary validation
- If using ethanol: eliminate ignition sources, ensure ventilation
- E0 MUST complete before any hypothesis-testing experiments

---

*All experiments are Tier 3-4. Pass/fail criteria are interpretive predictions, not structural guarantees.*
