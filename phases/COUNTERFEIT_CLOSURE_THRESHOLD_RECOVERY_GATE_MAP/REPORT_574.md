# Phase 574: Counterfeit Closure Threshold + Recovery Gate Map

**Recovery gate verdict: RECOVERY_GATE_R1_C_DOMINANT**
**Threshold verdict: THRESHOLD_A2_SHIFTED_GRADUAL**
**Morphology verdict: MORPHOLOGY_SELECTIVE_COUNTERFEITING**
**Landscape verdict: LANDSCAPE_THREE_POLE**
**New constraints:** 4 (C1643-C1646)

---

## 1. Summary

Phase 574 follows Phase 573's identification of NO_CLOSE_RECOVERY as the dominant mechanism behind A2's excess forgivingness (C1639). It decomposes the recovery gate into R1-R5 sub-channels, models the counterfeit closure threshold curve, identifies which closure packet morphologies are counterfeitable, and maps the continuous apparatus response landscape.

## 2. Recovery Gate Decomposition (T1)

**Verdict: RECOVERY_GATE_R1_C_DOMINANT**

A2 recovery gate diagnosis: RECOVERY_GATE_R1_C_DOMINANT. R1_C share=117.3%, R4_C share=118.8%, R1_C+R4_C joint=236.2%. Sub-channel additivity: STRONGLY_INTERACTIVE (interaction fraction=-1.0590)

### Sub-Channel Shares (A2)

| Profile | R1_C Share | R4_C Share | Joint R1_C+R4_C | Interpretation | Additivity |
|---------|-----------|-----------|-----------------|----------------|------------|
| A1_BATH_REFLUX | 0.3383 | 0.3346 | 0.6729 | R1_R4_COUPLED | STRONGLY_INTERACTIVE |
| A2_SEALED_RECIRCULATION | 1.1731 | 1.1884 | 2.3615 | R1_C_DOMINANT | STRONGLY_INTERACTIVE |
| A3_DISTILL_COLLECT | 0.3383 | 0.3346 | 0.6729 | R1_R4_COUPLED | WEAKLY_INTERACTIVE |

### Parameter Sensitivity (A2 only)

Parameters tested at +/-10%: R1_C_MULT, R4_C_TO_Y

## 3. Counterfeit Threshold Curves (T2)

**Verdict: THRESHOLD_A2_SHIFTED_GRADUAL**

Threshold verdict: THRESHOLD_A2_SHIFTED_GRADUAL. A2 vs A1 magnitude shift=0.1380 (MODERATELY_SHIFTED). A1_BATH_REFLUX: binary=0.042, magnitude=0.042. A2_SEALED_RECIRCULATION: binary=0.0737, magnitude=0.18. A3_DISTILL_COLLECT: binary=0.0297, magnitude=0.0297. 

### Per-Profile Thresholds

| Profile | Binary Threshold | Magnitude Threshold | Transition Width | Steepness | R-squared |
|---------|-----------------|--------------------|--------------------|-----------|-----------|
| A1_BATH_REFLUX | 0.042 | 0.042 | None | 5.0087 | -763.0651 |
| A2_SEALED_RECIRCULATION | 0.0737 | 0.18 | 0.327 | 5.0029 | 0.902 |
| A3_DISTILL_COLLECT | 0.0297 | 0.0297 | None | 5.0005 | -1.9055 |

### Profile Shifts

- A2 vs A1 magnitude shift: 0.1380 (MODERATELY_SHIFTED)

## 4. Closure Packet Morphology (T3)

**Verdict: MORPHOLOGY_SELECTIVE_COUNTERFEITING**

Morphology verdict: MORPHOLOGY_SELECTIVE_COUNTERFEITING. Signature classes: A2_COUNTERFEITABLE=5, RESISTANT=5, UNIVERSALLY_WEAK=0, total signatures=11. Top A2 protective features: [('headless_involved', 0.125922), ('high_cts', 0.107451), ('armed', 0.09203)].

### Packet Signature Classification

| Signature | Classification | N_events | A2 DYE_adv |
|-----------|---------------|----------|------------|
| armed+has_e_head_support+headless_involved | RESISTANT | 21 | 0.111748 |
| armed+has_e_head_support+headless_involved+high_cts | INSUFFICIENT_DATA | 21 | None |
| armed+has_e_head_support+headless_involved+high_cts+high_opaque+m_terminal_present | RESISTANT | 9 | 0.042375 |
| armed+has_e_head_support+headless_involved+high_cts+m_terminal_present | RESISTANT | 22 | 0.121726 |
| armed+has_e_head_support+headless_involved+high_opaque | A2_COUNTERFEITABLE | 29 | -0.051073 |
| has_e_head_support | A2_COUNTERFEITABLE | 31 | -0.115861 |
| has_e_head_support+headless_involved | RESISTANT | 226 | 0.007499 |
| has_e_head_support+headless_involved+high_cts+m_terminal_present | RESISTANT | 10 | 0.073147 |
| has_e_head_support+headless_involved+high_opaque | A2_COUNTERFEITABLE | 25 | -0.133845 |
| has_e_head_support+headless_involved+m_terminal_present | A2_COUNTERFEITABLE | 8 | -0.043085 |
| headless_involved | A2_COUNTERFEITABLE | 20 | -0.03554 |

## 5. Continuous Landscape (T4)

**Verdict: LANDSCAPE_THREE_POLE**

Landscape verdict: LANDSCAPE_THREE_POLE. STABLE_AMPLIFIER=25.0% (n=19), THRESHOLD_DEPENDENT=63.2% (n=48), FORGIVING_RECIRCULATOR=11.8% (n=9). Cross-cut fraction=0.2500.

NOTE: Three-way classification is a **descriptive convenience overlay** on a continuous surface, NOT ontological folio species.

### Classification Summary

| Class | N_folios | Fraction | Profile Distribution | Mean Margin |
|-------|----------|----------|---------------------|-------------|
| STABLE_AMPLIFIER | 19 | 25.0% | {'A3_DISTILL_COLLECT': 12, 'A1_BATH_REFLUX': 6, 'A2_SEALED_RECIRCULATION': 1} | 0.1749 |
| THRESHOLD_DEPENDENT | 48 | 63.2% | {'A3_DISTILL_COLLECT': 24, 'A2_SEALED_RECIRCULATION': 9, 'A1_BATH_REFLUX': 15} | 0.0976 |
| FORGIVING_RECIRCULATOR | 9 | 11.8% | {'A2_SEALED_RECIRCULATION': 8, 'A3_DISTILL_COLLECT': 1} | -0.0608 |

## 6. New Constraints

**C1643** (Tier 2, scope B)
  A2 recovery gate sub-channel decomposition: RECOVERY_GATE_R1_C_DOMINANT. A2 recovery gate diagnosis: RECOVERY_GATE_R1_C_DOMINANT. R1_C share=117.3%, R4_C share=118.8%, R1_C+R4_C joint=236.2%. Sub-channel additivity: STRONGLY_INTERACTIVE (interaction fraction=-1.0590)

**C1644** (Tier 2, scope B)
  Counterfeit closure threshold: THRESHOLD_A2_SHIFTED_GRADUAL. Threshold verdict: THRESHOLD_A2_SHIFTED_GRADUAL. A2 vs A1 magnitude shift=0.1380 (MODERATELY_SHIFTED). A1_BATH_REFLUX: binary=0.042, magnitude=0.042. A2_SEALED_RECIRCULATION: binary=0.0737, magnitude=0.18. A3_DISTILL_COLLECT: binary=0.0297, magnitude=0.0297. 

**C1645** (Tier 2, scope B)
  Closure packet morphology selectivity: MORPHOLOGY_SELECTIVE_COUNTERFEITING. Morphology verdict: MORPHOLOGY_SELECTIVE_COUNTERFEITING. Signature classes: A2_COUNTERFEITABLE=5, RESISTANT=5, UNIVERSALLY_WEAK=0, total signatures=11. Top A2 protective features: [('headless_involved', 0.125922), ('high_cts', 0.107451), ('armed', 0.09203)].

**C1646** (Tier 2, scope B)
  Apparatus response landscape: LANDSCAPE_THREE_POLE. Landscape verdict: LANDSCAPE_THREE_POLE. STABLE_AMPLIFIER=25.0% (n=19), THRESHOLD_DEPENDENT=63.2% (n=48), FORGIVING_RECIRCULATOR=11.8% (n=9). Cross-cut fraction=0.2500.

## 7. Interpretive Synthesis

### Post-573 Interpretation (Tier 3, frozen)

> "Currier B's closure grammar advantage is not uniformly visible across apparatus conditions because apparatus families differ in counterfeit-closure susceptibility. A2_SEALED_RECIRCULATION is a forgiving closure-response regime in which close-recovery dynamics redeem generic disturbance too readily, especially when closure packets are weakly specified. Strong closure packets still outperform nulls there, showing that the grammar remains active, but the apparatus imposes a higher specificity threshold before productive disruption becomes discriminative. Across Currier B, folio accent and residual variance are better modeled as position on a continuous response landscape -- anchored by a distinct forgiving A2 pole and a broad productive field -- than as crisp discrete families."

### Post-574 Interpretation (Tier 3, contingent)

> "The main observable apparatus-side difference among Currier B folios is not endpoint recovery capacity but counterfeit-closure susceptibility: how much closure specificity must be present before the plant stops redeeming generic disturbance and starts rewarding grammar-aligned disturbance preferentially."

This interpretation is frozen only if T1-T4 results support it (A2 threshold shifted right, selective morphology counterfeiting, landscape showing forgiving pole).

---

*Generated: 2026-03-11T00:48:53.480207+00:00*
