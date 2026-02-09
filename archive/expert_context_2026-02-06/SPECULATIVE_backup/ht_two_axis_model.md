# HT Two-Axis Model: Vigilance vs Spare Capacity

**Tier:** 2-3 | **Status:** VALIDATED | **Date:** 2026-01-12

---

## Discovery

An attempt to test whether HT PREFIX encodes "perceptual load" (sensory multiplexing) yielded an **unexpected inverse correlation**:

| Metric | Expected | Observed |
|--------|----------|----------|
| LATE in high-complexity folios | HIGH | **LOW** (0.180) |
| LATE in low-complexity folios | LOW | **HIGH** (0.281) |
| Correlation | Positive | **Negative (r=-0.301, p=0.007)** |

This apparent contradiction **refined rather than weakened** the HT model.

---

## The Key Insight: Two Orthogonal Dimensions

HT is not a single signal. It has **two independent axes**:

### Axis 1: HT DENSITY (Vigilance Demand)

| Property | Evidence |
|----------|----------|
| Tracks upcoming discrimination complexity | C477 (r=0.504 with tail MIDDLEs) |
| Rises before difficult sections | C459 (anticipatory) |
| Correlates with rare MIDDLE pressure | HT variance decomposition |

**This axis is UNCHANGED by the new finding.**

### Axis 2: HT MORPHOLOGICAL COMPLEXITY (Spare Capacity)

| Property | Evidence |
|----------|----------|
| Complex forms (LATE) appear in LOW-load contexts | r=-0.301, p=0.007 |
| Simple forms (EARLY) appear in HIGH-load contexts | Section ranking inverted |
| Reflects available cognitive bandwidth | C344 (inverse A-coupling) |

**This axis is the NEW finding.**

---

## The Reconciled Model

```
DIMENSION 1: HT DENSITY
  - Tracks UPCOMING discrimination complexity
  - Grammar-generated vigilance signal
  - "How much attention is NEEDED"

DIMENSION 2: HT MORPHOLOGICAL COMPLEXITY
  - Tracks CURRENT spare cognitive capacity
  - Human-generated practice signal
  - "How much attention is AVAILABLE"
```

### Why This Makes Sense

> **When the task is hard, HT is frequent but morphologically simple.**
> **When the task is easy, HT is less frequent but morphologically richer.**

This is a classic human-factors pattern:
- Under high load: frequent simple responses
- Under low load: less frequent but more elaborate engagement

---

## Constraint Alignment

| Constraint | How This Fits |
|------------|---------------|
| **C344** - HT-A Inverse Coupling | Direct instantiation: high A-complexity suppresses complex HT forms |
| **C417** - HT Modular Additive | HT is composite: density = vigilance, form = engagement |
| **C221** - Deliberate Skill Practice | Complex HT shapes occur during low-load intervals |
| **C404/C405** - Non-operational | HT form reflects behavior, doesn't instruct it |
| **C477** - Tail correlation | UNCHANGED - applies to density, not morphology |

---

## What HT Does NOT Encode

The original hypothesis was:
> "LATE means harder sensing / more senses needed"

This is **NOT SUPPORTED**. HT form does not encode sensory requirements.

### Correct Division of Labor

| Component | Encodes |
|-----------|---------|
| Currier A vocabulary | Discrimination problems (with implied sensory affordances) |
| AZC phase | Process position |
| HT DENSITY | Upcoming vigilance demand |
| HT MORPHOLOGY | Current spare capacity for practice |

**Sensory multiplexing requirements are implicit in the discrimination problem itself, not encoded in HT form.**

---

## The Final Integrated Statement

> **HT has two orthogonal properties:**
>
> 1. **HT density tracks upcoming discrimination complexity** (tail MIDDLE pressure, AZC commitment).
>
> 2. **HT morphological complexity tracks operator spare cognitive capacity**, increasing during low-load phases and decreasing during high-load phases.
>
> **HT does not encode what sensory modalities are needed. Sensory demands are implicit in the discrimination problem itself. HT reflects how the human allocates attention when grammar permits engagement, including deliberate written skill practice during idle or low-stress intervals.**

---

## Why This Is a Win

The "failed" hypothesis revealed a subtler mechanism:
- The contradiction was productive
- The new model fits MORE constraints, not fewer
- The division of labor is cleaner
- Human-factors interpretation is stronger

---

## Testable Predictions

| Prediction | Test |
|------------|------|
| Density and morphology are statistically independent | Correlation between density and LATE ratio should be weak |
| LATE clusters in LINK-heavy (waiting) contexts | Compare LATE ratio by LINK proximity |
| High-stress sections show simple HT but HIGH density | Check hazard-adjacent HT profiles |

---

## Files

- `phases/SENSORY_MAPPING/ht_perceptual_load_test.py` - Original test
- `phases/SENSORY_MAPPING/ht_perceptual_load_test_v2.py` - Folio-level refinement
- `results/ht_perceptual_load_test_v2.json` - Results showing inverse correlation

---

## Navigation

- [human_track.md](../CLAIMS/human_track.md) - HT constraint registry
- [SENSORY_VALIDATION_2026-01-12.md](SENSORY_VALIDATION_2026-01-12.md) - Sensory affordance validation

---

*Discovered 2026-01-12 through hypothesis testing. Inverse correlation refined rather than falsified the HT model.*
