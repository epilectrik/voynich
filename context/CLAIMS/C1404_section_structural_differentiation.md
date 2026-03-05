# C1404: Section Structural Differentiation is REGIME-Dominated

**Tier:** 2 (ESTABLISHED)
**Scope:** B, section, REGIME, macro-state, kernel, hazard, morphology
**Phase:** SECTION_PARAGRAPH_AXM_DRIVERS (Phase 514)
**Extends:** C1403 (MONOSTATE thematic dominance), C1029 (section-parameterized grammar weights)
**Relates to:** C179 (4 stable REGIMEs), C1084 (section-specific AXM ordering), C551 (grammar universality/REGIME specialization)

---

## Statement

Currier B sections are structurally differentiated across 6 dimensions, but the dominant differentiator is **REGIME composition** (V=0.573), which is 7.4x stronger than the next-largest effect (macro-state profile V=0.077). Section B is pure REGIME_1; sections T and C have no REGIME_1 folios. Transition entropy ranges from 3.09 bits (T, tightest grammar) to 4.47 bits (S, loosest). The 5 sections are primarily REGIME mixtures with modest independent effects on kernel balance and morphological profiles.

### REGIME Distribution by Section (V=0.573)

| Section | R1 | R2 | R3 | R4 |
|---------|-----|-----|-----|-----|
| B | 100% | 0% | 0% | 0% |
| S | 43% | 0% | 52% | 4% |
| H | 6% | 41% | 16% | 38% |
| C | 0% | 40% | 40% | 20% |
| T | 0% | 0% | 50% | 50% |

### Macro-State Profiles (chi2=384.8, V=0.077)

| Section | AXM | FQ | CC | FL_HAZ | AXm | FL_SAFE |
|---------|-----|-----|-----|--------|-----|---------|
| B | 0.744 | 0.131 | 0.059 | 0.044 | 0.016 | 0.005 |
| S | 0.670 | 0.193 | 0.033 | 0.063 | 0.035 | 0.007 |
| C | 0.604 | 0.213 | 0.048 | 0.082 | 0.043 | 0.009 |
| H | 0.589 | 0.240 | 0.049 | 0.072 | 0.039 | 0.011 |
| T | 0.582 | 0.183 | 0.064 | 0.082 | 0.067 | 0.022 |

### Kernel Profiles (chi2=142.8, V=0.071)

| Section | k-frac | h-frac | e-frac |
|---------|--------|--------|--------|
| B | 0.242 | 0.062 | 0.364 |
| S | 0.177 | 0.073 | 0.390 |
| H | 0.170 | 0.074 | 0.290 |
| C | 0.132 | 0.071 | 0.246 |
| T | 0.148 | 0.097 | 0.334 |

### Hazard Profiles

Section B has the lowest FL_HAZ rate (4.4%) and zero forbidden violations. Sections C and T have the highest FL_HAZ rates (8.2%).

### Transition Entropy

| Section | H(class_t \| class_{t-1}) |
|---------|---------------------------|
| T | 3.094 bits |
| C | 3.813 bits |
| B | 4.221 bits |
| H | 4.252 bits |
| S | 4.470 bits |

### Morphological Signatures

- **B**: qo-dominated (23.7%), depleted in ok/ot
- **H**: ch-dominant (17.0%), balanced ok (8.4%)
- **S**: Balanced ch/qo/BARE (each ~17%), highest lk (3.4%)
- **C**: BARE-dominant (22.3%), high ot (8.6%)
- **T**: sh-dominant (14.2%), unusual sh>ch inversion

---

## Falsification Criteria

1. If REGIME composition is shown to be a consequence of section membership (rather than its primary discriminant), the causal ordering reverses
2. If a non-REGIME dimension achieves V > 0.30 between sections, REGIME dominance is weakened
3. If within-REGIME section differences are as large as between-REGIME differences, sections carry independent structural signal beyond REGIME

---

## Method

- 82 B folios classified into 5 sections (B=12, C=5, H=27, S=36, T=2) via `scripts/voynich.py` Transcript
- 16,054 classified tokens (49-class grammar) mapped to 6 macro-states via C976 partition
- REGIME assignments from `data/regime_folio_mapping.json`
- Chi-squared tests with Cramer's V for categorical comparisons
- Conditional entropy for transition grammar comparison
- PREFIX fractions, kernel fractions, suffix rates, token lengths for morphological profiling

**Script:** `phases/SECTION_PARAGRAPH_AXM_DRIVERS/scripts/section_paragraph_drivers.py`
**Results:** `phases/SECTION_PARAGRAPH_AXM_DRIVERS/results/section_paragraph_drivers.json` (tests A1-A6)
