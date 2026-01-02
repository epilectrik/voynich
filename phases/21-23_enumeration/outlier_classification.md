# Outlier Classification Report

*Generated: 2025-12-31T21:22:16.788270*

---

## Summary

| Folio | Classification | Confidence |
|-------|----------------|------------|
| f57r | BOUNDARY_CONDITION | HIGH |
| f76r | EXTENDED_RUN | MEDIUM |
| f85v2 | UNKNOWN | LOW |
| f48r | UNKNOWN | LOW |
| f83v | EXTENDED_RUN | MEDIUM |
| f86v4 | UNKNOWN | LOW |
| f33r | UNKNOWN | LOW |
| f94v | UNKNOWN | LOW |
| f95r2 | UNKNOWN | LOW |
| f95v2 | UNKNOWN | LOW |
| f105r | UNKNOWN | LOW |
| f105v | EXTENDED_RUN | MEDIUM |
| f111r | EXTENDED_RUN | MEDIUM |
| f111v | EXTENDED_RUN | MEDIUM |
| f115v | EXTENDED_RUN | MEDIUM |

## Classification Legend

| Classification | Definition |
|----------------|------------|
| BOUNDARY_CONDITION | Represents startup, shutdown, or regime edge |
| RECOVERY_OPERATION | Contains repair/reset sequences for deviation correction |
| STRESSED_REGIME | Normal operation under extreme parameters |
| EXTENDED_RUN | Same control logic, just longer duration |
| SCRIBAL_ANOMALY | Structural irregularities suggesting copying error |
| UNKNOWN | Cannot classify with available evidence |

## Detailed Classifications

### f57r
**Classification:** BOUNDARY_CONDITION
**Confidence:** HIGH

**Supporting Evidence:**
- Only folio with reset_present=true
- Contains restart/regime change point

---

### f76r
**Classification:** EXTENDED_RUN
**Confidence:** MEDIUM

**Supporting Evidence:**
- Length 2222 exceeds baseline by >50%

**Alternative Interpretations:**
- Could be STRESSED_REGIME if hazard density high

---

### f85v2
**Classification:** UNKNOWN
**Confidence:** LOW

---

### f48r
**Classification:** UNKNOWN
**Confidence:** LOW

**Alternative Interpretations:**
- Possibly normal with measurement noise

---

### f83v
**Classification:** EXTENDED_RUN
**Confidence:** MEDIUM

**Supporting Evidence:**
- Length 1021 exceeds baseline by >50%
- Hazard density 0.771 exceeds baseline

**Alternative Interpretations:**
- Could be STRESSED_REGIME if hazard density high

---

### f86v4
**Classification:** UNKNOWN
**Confidence:** LOW

**Alternative Interpretations:**
- Possibly normal with measurement noise

---

### f33r
**Classification:** UNKNOWN
**Confidence:** LOW

**Alternative Interpretations:**
- Possibly normal with measurement noise

---

### f94v
**Classification:** UNKNOWN
**Confidence:** LOW

**Alternative Interpretations:**
- Possibly normal with measurement noise

---

### f95r2
**Classification:** UNKNOWN
**Confidence:** LOW

**Alternative Interpretations:**
- Possibly normal with measurement noise

---

### f95v2
**Classification:** UNKNOWN
**Confidence:** LOW

**Alternative Interpretations:**
- Possibly normal with measurement noise

---

### f105r
**Classification:** UNKNOWN
**Confidence:** LOW

**Alternative Interpretations:**
- Possibly normal with measurement noise

---

### f105v
**Classification:** EXTENDED_RUN
**Confidence:** MEDIUM

**Supporting Evidence:**
- Length 1169 exceeds baseline by >50%

**Alternative Interpretations:**
- Could be STRESSED_REGIME if hazard density high

---

### f111r
**Classification:** EXTENDED_RUN
**Confidence:** MEDIUM

**Supporting Evidence:**
- Length 1800 exceeds baseline by >50%

**Alternative Interpretations:**
- Could be STRESSED_REGIME if hazard density high

---

### f111v
**Classification:** EXTENDED_RUN
**Confidence:** MEDIUM

**Supporting Evidence:**
- Length 2199 exceeds baseline by >50%

**Alternative Interpretations:**
- Could be STRESSED_REGIME if hazard density high

---

### f115v
**Classification:** EXTENDED_RUN
**Confidence:** MEDIUM

**Supporting Evidence:**
- Length 817 exceeds baseline by >50%

**Alternative Interpretations:**
- Could be STRESSED_REGIME if hazard density high

---
