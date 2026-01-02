# Candidate Elimination Stress Test Report

*Generated: 2026-01-01*
*Status: Adversarial Comparison (Interpretive Firewall Active)*

---

## Executive Summary

| Candidate | Domain | Initial Similarity | Overall Score | Verdict |
|-----------|--------|-------------------|---------------|---------|
| Reflux Distillation | Chemical Process | 0.952 | 1.000 | **SURVIVES** |
| Blood Glucose Regulation | Biological Systems | 0.886 | 0.750 | **WEAKENED** |
| Distillation Column (Industrial) | Chemical Process | 0.885 | 0.875 | **SURVIVES** |
| Temperature Regulation (Mammalian) | Biological Systems | 0.878 | 0.750 | **WEAKENED** |
| Biological Homeostasis | Biological Systems | 0.871 | 0.750 | **WEAKENED** |
| Steam Boiler Pressure Control | Industrial Systems | 0.858 | 0.833 | **SURVIVES** |

---

## Test Results by Candidate

### Reflux Distillation (Chemical Process)
- Initial similarity: 0.952
- Overall score: 1.000
- Verdict: **SURVIVES**

| Test | Score | Verdict | Key Issues |
|------|-------|---------|------------|
| TEST_1 | 1.00 | PASS | None |
| TEST_2 | 1.00 | PASS | None |
| TEST_3 | 1.00 | PASS | None |
| TEST_4 | 1.00 | PASS | None |
| TEST_5 | 1.00 | PASS | None |
| TEST_6 | 1.00 | PASS | None |

### Blood Glucose Regulation (Biological Systems)
- Initial similarity: 0.886
- Overall score: 0.750
- Verdict: **WEAKENED**

| Test | Score | Verdict | Key Issues |
|------|-------|---------|------------|
| TEST_1 | 1.00 | PASS | None |
| TEST_2 | 0.75 | PASS | hazard_nature |
| TEST_3 | 0.00 | FAIL | external_termination, operator_presence, deliberate_non_intervention, teaching_intent |
| TEST_4 | 1.00 | PASS | None |
| TEST_5 | 0.75 | PASS | external_operator_exists |
| TEST_6 | 1.00 | PASS | None |

### Distillation Column (Industrial) (Chemical Process)
- Initial similarity: 0.885
- Overall score: 0.875
- Verdict: **SURVIVES**

| Test | Score | Verdict | Key Issues |
|------|-------|---------|------------|
| TEST_1 | 1.00 | PASS | None |
| TEST_2 | 1.00 | PASS | None |
| TEST_3 | 0.75 | PASS | teaching_intent |
| TEST_4 | 1.00 | PASS | None |
| TEST_5 | 0.75 | PASS | no_parameters |
| TEST_6 | 0.75 | PASS | combined_robustness |

### Temperature Regulation (Mammalian) (Biological Systems)
- Initial similarity: 0.878
- Overall score: 0.750
- Verdict: **WEAKENED**

| Test | Score | Verdict | Key Issues |
|------|-------|---------|------------|
| TEST_1 | 1.00 | PASS | None |
| TEST_2 | 0.75 | PASS | hazard_nature |
| TEST_3 | 0.00 | FAIL | external_termination, operator_presence, deliberate_non_intervention, teaching_intent |
| TEST_4 | 1.00 | PASS | None |
| TEST_5 | 0.75 | PASS | external_operator_exists |
| TEST_6 | 1.00 | PASS | None |

### Biological Homeostasis (Biological Systems)
- Initial similarity: 0.871
- Overall score: 0.750
- Verdict: **WEAKENED**

| Test | Score | Verdict | Key Issues |
|------|-------|---------|------------|
| TEST_1 | 1.00 | PASS | None |
| TEST_2 | 0.75 | PASS | hazard_nature |
| TEST_3 | 0.00 | FAIL | external_termination, operator_presence, deliberate_non_intervention, teaching_intent |
| TEST_4 | 1.00 | PASS | None |
| TEST_5 | 0.75 | PASS | external_operator_exists |
| TEST_6 | 1.00 | PASS | None |

### Steam Boiler Pressure Control (Industrial Systems)
- Initial similarity: 0.858
- Overall score: 0.833
- Verdict: **SURVIVES**

| Test | Score | Verdict | Key Issues |
|------|-------|---------|------------|
| TEST_1 | 1.00 | PASS | None |
| TEST_2 | 1.00 | PASS | None |
| TEST_3 | 0.50 | MARGINAL | external_termination, teaching_intent |
| TEST_4 | 1.00 | PASS | None |
| TEST_5 | 0.75 | PASS | no_parameters |
| TEST_6 | 0.75 | PASS | combined_robustness |

---

## Detailed Failure Analysis

### TEST_1: Perturbation Response Shape

*No candidates failed this test.*

### TEST_2: Hard Hazard Topology

*No candidates failed this test.*

### TEST_3: Non-Intervention Role (LINK Analog)

**3 candidate(s) failed:**
- **Biological Homeostasis** (Biological Systems)
  - external_termination: Candidate has CONTINUOUS termination (Voynich requires EXTERNAL - operator decides completion)
  - operator_presence: System is autonomous (no external operator)
  - deliberate_non_intervention: Non-intervention is not a deliberate operator choice
  - teaching_intent: Intent is OPERATIONAL (Voynich is a TEACHING document recording operator decisions)
- **Blood Glucose Regulation** (Biological Systems)
  - external_termination: Candidate has CONTINUOUS termination (Voynich requires EXTERNAL - operator decides completion)
  - operator_presence: System is autonomous (no external operator)
  - deliberate_non_intervention: Non-intervention is not a deliberate operator choice
  - teaching_intent: Intent is OPERATIONAL (Voynich is a TEACHING document recording operator decisions)
- **Temperature Regulation (Mammalian)** (Biological Systems)
  - external_termination: Candidate has CONTINUOUS termination (Voynich requires EXTERNAL - operator decides completion)
  - operator_presence: System is autonomous (no external operator)
  - deliberate_non_intervention: Non-intervention is not a deliberate operator choice
  - teaching_intent: Intent is OPERATIONAL (Voynich is a TEACHING document recording operator decisions)

### TEST_4: Mode/Regime Multiplicity

*No candidates failed this test.*

### TEST_5: Operator Granularity & Expertise

*No candidates failed this test.*

### TEST_6: Representation Invariance

*No candidates failed this test.*

---

## Survivors Analysis

**Survivors:** 3
- Reflux Distillation (1.000)
- Steam Boiler Pressure Control (0.833)
- Distillation Column (Industrial) (0.875)

**Weakened (1 test failed):** 3
- Biological Homeostasis (0.750)
- Blood Glucose Regulation (0.750)
- Temperature Regulation (Mammalian) (0.750)

**Marginal:** 0

**Eliminated (≥2 tests failed):** 0

---

## Interpretive Firewall Statement

### What These Results Say

1. **Elimination is structural**: Candidates fail because they diverge from the Voynich control profile on specific, measurable dimensions.
2. **Survival is not identification**: Surviving candidates share operational homology with the Voynich signature. This does NOT mean the manuscript "is" or "represents" any specific process.
3. **Biological systems face structural barriers**: The lack of an external human operator making deliberate control decisions is a fundamental architectural difference.

### Permitted Interpretations

- "Candidate X fails to reproduce Voynich control behavior on [dimension]"
- "Candidate X shares operational homology with the Voynich signature on [dimension]"
- "The Voynich control profile is structurally compatible with process class [Y]"

### Forbidden Interpretations

- ~~"This proves the Voynich Manuscript is about [X]"~~
- ~~"The author was working with [X]"~~
- ~~"[X] is eliminated as a possibility"~~ (Only high-similarity candidates were tested)

---

*Document closes the adversarial stress test phase.*