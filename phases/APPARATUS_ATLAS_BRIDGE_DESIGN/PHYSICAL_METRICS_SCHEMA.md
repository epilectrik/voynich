# Physical Metrics Schema

**Phase 582: APPARATUS_ATLAS_BRIDGE_DESIGN**

## Metric Definitions

5 virtual process metrics mapped to physical analogs.

### DVA_phys: Disruption Value Analog (physical)

**Virtual source:** DVA: magnitude of grammar-induced process disturbance

**Definition:** Magnitude of induced process disturbance during intervention window

**Formula:** `DVA_phys = sqrt(delta_T_body^2 + delta_T_head^2 + delta_flow_rate^2 + delta_gradient^2) over intervention window`

**Interpretation:** How much did the intervention actually disturb the process?

**Required sensors:** temp_body, temp_head

**Optional sensors:** flow_meter, FLIR

**Components:**

- delta_T_body: K-type thermocouple at body (degrees C, weight=1.0)
- delta_T_head: K-type thermocouple at head (degrees C, weight=1.0)
- delta_flow_rate: Condensate mass/time (manual or drip counter) (ml/min, weight=0.5)
- delta_gradient: FLIR body-head gradient (degrees C, weight=0.5)

**Constraint basis:** C1634 (DVA validated)

### YGA_phys: Y-Gain Analog (physical)

**Virtual source:** YGA: useful product/quality gain during/after intervention

**Definition:** Useful product or quality gain during or immediately after intervention window

**Formula:** `YGA_phys = delta_condensate_rate * quality_score over observation window`

**Interpretation:** Did the intervention produce useful product improvement?

**Required sensors:** condensate_mass, quality_assessment

**Optional sensors:** refractometer

**Components:**

- delta_condensate_rate: Condensate collection mass/time (ml/min, weight=1.0)
- quality_score: Sensory assessment (clarity, scent intensity) (ordinal 0-5, weight=1.0)
- fraction_purity: Visual clarity check or refractometer (binary or index, weight=0.5)

**Constraint basis:** C1632 (YGA validated)

### DYE_phys: Disruption-to-Y Efficiency (physical)

**Virtual source:** DYE: useful gain per unit disturbance

**Definition:** Ratio of YGA_phys to DVA_phys

**Formula:** `DYE_phys = YGA_phys / DVA_phys (undefined if DVA_phys = 0)`

**Interpretation:** How efficiently does disturbance convert to useful output? DYE_phys > 0 means the intervention was productive.

**Required sensors:** (all DVA_phys sensors), (all YGA_phys sensors)

**Constraint basis:** C1633 (DYE validated), C1637 (WCP demoted, DYE primary)

### CTS_phys: Closure Threshold Strength (physical)

**Virtual source:** CTS: continuous closure strength index

**Definition:** Composite closure strength from observable closure state variables

**Formula:** `CTS_phys = w1*seal_completion + w2*heat_reduction_slope + w3*gradient_collapse_rate + w4*flow_change_magnitude`

**Interpretation:** How strong is this closure? Above threshold -> productive in A2. Below threshold -> loses to null in A2 (C1642).

**Required sensors:** temp_body, temp_head, event_annotation

**Optional sensors:** FLIR, flow_meter

**Components:**

- seal_completion: Manual event annotation (binary or timed) (fraction 0-1, weight=0.35)
- heat_reduction_slope: Temperature probe derivative (degrees C/s, weight=0.25)
- gradient_collapse_rate: FLIR body-head delta derivative (degrees C/s, weight=0.25)
- flow_change_magnitude: Condensate rate change (ml/min, weight=0.15)

**Constraint basis:** C1642 (strength-dependent), C1644, C1639 (close-recovery 159.5%)

### forgivingness_phys: Forgivingness Index (physical)

**Virtual source:** CCS1: null vs grammar closure performance retention

**Definition:** Ratio of process quality under null (random) closure to process quality under grammar-specified closure

**Formula:** `Forgivingness_phys = mean(YGA_phys under null_closures) / mean(YGA_phys under grammar_closures)`

**Interpretation:** How much does the apparatus compensate for random (non-optimal) closures? Values near 1.0 = highly forgiving (A2-like). Values near 0 = unforgiving (A1-like).

**Required sensors:** (all YGA_phys sensors), controlled null conditions

**Constraint basis:** C1639 (A2 CCS1=0.114), C1642 (STRONG vs WEAK)

## Data Model

**Synchronization:** All sensors on common clock (NTP or manual sync)

### Raw Channels

| Channel | Sensor | Rate | Unit | Required |
|---------|--------|------|------|----------|
| temp_body | K-type thermocouple | 1.0 Hz | degrees C | Yes |
| temp_head | K-type thermocouple | 1.0 Hz | degrees C | Yes |
| temp_bath | K-type thermocouple | 1.0 Hz | degrees C | No |
| temp_collection | K-type thermocouple | 1.0 Hz | degrees C | No |
| flir_frame | FLIR thermal camera | 0.5 Hz | thermal image | No |
| condensate_mass | Scale under receiving flask | 0.1 Hz | grams | Yes |
| heater_state | Relay state log | 1.0 Hz | binary on/off | No |

### Derived Channels

| Channel | Formula | Unit |
|---------|---------|------|
| thermal_gradient | temp_body - temp_head | degrees C |
| gradient_slope | d(thermal_gradient)/dt | degrees C/s |
| condensate_rate | d(condensate_mass)/dt | g/min |
| CTS_phys_running | weighted composite (see CTS_phys definition) | composite index |
| DVA_phys_running | euclidean disturbance magnitude | composite index |

### Trigger Annotations

- `packet_start`
- `packet_end`
- `seal_start`
- `seal_complete`
- `heat_change_start`
- `heat_change_complete`
- `collection_divert_start`
- `collection_divert_complete`
- `sensory_check`
- `quality_assessment`

### Event Windows

- **intervention_window:** From packet_start to process stabilization (thermal gradient < threshold)
- **observation_window:** From stabilization to next packet_start (or end of run)
- **stabilization_criterion:** abs(gradient_slope) < 0.1 C/s for 30 consecutive seconds

## Hardware Null Conditions

7 null conditions for controlled experimentation.

| Null | Controls For | Expected Result |
|------|-------------|-----------------|
| N1_matched_time_no_seal | Separates seal effect from timing effect | Lower CTS_phys; lower YGA_phys than real closure in A2... |
| N2_matched_heat_no_routing | Separates thermal from routing effects | Partial DVA_phys (thermal only); attenuated YGA_phys... |
| N3_matched_routing_no_seal | Separates routing from containment effects | Flow disruption without pressure change; tests routing contr... |
| N4_random_timing_matched_energy | Total energy vs timing precision | Tests whether WHEN matters or only HOW MUCH... |
| N5_sham_intervention | Operator attention bias | No DVA_phys, no YGA_phys (if the process is physics-driven)... |
| N6_delayed_intervention | Timing sensitivity | Tests how rapidly DYE_phys degrades with timing error... |
| N7_phase_misaligned | Phase-ordering hazard (41% of hazard topology) | Tests C109 PHASE_ORDERING: should produce the most dangerous... |

### N1_matched_time_no_seal

**Description:** Same timing as closure, but sealing step omitted/incomplete

**Controls for:** Separates seal effect from timing effect

**Procedure:** At the closure trigger point, reduce heat on the same schedule but do not seal the vessel. Leave joints open.

**Expected result:** Lower CTS_phys; lower YGA_phys than real closure in A2

### N2_matched_heat_no_routing

**Description:** Temperature drops on same schedule but flow path unchanged

**Controls for:** Separates thermal from routing effects

**Procedure:** Reduce heat to target, but do not divert collection or change condensate routing. Material continues same path.

**Expected result:** Partial DVA_phys (thermal only); attenuated YGA_phys

### N3_matched_routing_no_seal

**Description:** Divert flow but do not seal body

**Controls for:** Separates routing from containment effects

**Procedure:** Switch collection flask or divert condensate, but leave the body/head junction open.

**Expected result:** Flow disruption without pressure change; tests routing contribution

### N4_random_timing_matched_energy

**Description:** Same total energy budget but random intervention timing

**Controls for:** Total energy vs timing precision

**Procedure:** Same heat reduction magnitude, applied at random point in the operation cycle rather than at grammar-specified position.

**Expected result:** Tests whether WHEN matters or only HOW MUCH

### N5_sham_intervention

**Description:** Go through motions without physical effect

**Controls for:** Operator attention bias

**Procedure:** Touch the apparatus, log an event, but do not actually change any setting. Controls for Hawthorne-type effects.

**Expected result:** No DVA_phys, no YGA_phys (if the process is physics-driven)

### N6_delayed_intervention

**Description:** Same closure, delayed by T seconds

**Controls for:** Timing sensitivity

**Procedure:** Execute the full closure procedure, but start T seconds after the grammar-specified trigger point.

**Expected result:** Tests how rapidly DYE_phys degrades with timing error

### N7_phase_misaligned

**Description:** Closure at wrong phase state

**Controls for:** Phase-ordering hazard (41% of hazard topology)

**Procedure:** Execute closure when material is in wrong phase (e.g., still actively boiling, or already cooled).

**Expected result:** Tests C109 PHASE_ORDERING: should produce the most dangerous failure mode

---

*All metric definitions are Tier 3. Formula details are interpretive. Sensor specifications are practical recommendations.*
