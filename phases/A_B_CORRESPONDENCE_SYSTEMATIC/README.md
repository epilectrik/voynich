# A_B_CORRESPONDENCE_SYSTEMATIC

**Date:** 2026-01-29
**Status:** PLANNED
**Objective:** Systematically test all plausible A-B correspondence mechanisms

---

## Background

Previous investigation established:
- A paragraphs cover only ~5% of total B vocabulary (folio level)
- A paragraphs cover ~84% of B paragraphs (but inflated by tiny B paragraphs)
- A and B share 100% of classified/PP vocabulary
- "A constrains B" doesn't work operationally as a filtering mechanism
- They appear to be parallel systems with shared vocabulary

**Key constraint to respect (C384.a):** Record-level correspondence via multi-axis constraint composition IS permitted, even though token-level lookup is not.

---

## Investigation Approaches

### Unit Size Matrix

Test all combinations:

| A Unit | B Unit | Script |
|--------|--------|--------|
| A paragraph | B paragraph | 01 |
| A paragraph | B paragraph (≥15 PP) | 02 |
| A folio | B folio | 03 |
| A paragraph | B folio | 04 |
| A folio | B paragraph | 05 |

### Profile-Based Matching (Expert Recommendations)

| Approach | Rationale | Script |
|----------|-----------|--------|
| Instruction class profile | C503.a: ~7 classes survive per A record | 06 |
| Kernel character accessibility | C503.c: h=95.6%, k=81.1%, e=60.8% varies by A | 07 |
| REGIME prediction | C536: Material type → REGIME mapping | 08 |
| Lane balance prediction | C646-647: 20/99 PP predict QO vs CHSH | 09 |
| Hazard exposure | C684: 83.9% of A records eliminate all hazards | 10 |
| Role composition | C683: Asymmetric role depletion by A | 11 |
| AZC-mediated only | C498.a: 214 AZC-mediated vs 198 B-native | 12 |

### Structural Matching

| Approach | Rationale | Script |
|----------|-----------|--------|
| Linker network position | C835: 4 linkers create 12 directed links | 13 |
| Header-header matching | C848, C840: Both have header-body structure | 14 |
| Section-constrained | C299: Section H → 91.6% of B | 15 |

### Vocabulary Level Variations

| Level | Description | Script |
|-------|-------------|--------|
| Full tokens | Exact word match | 16 |
| MIDDLEs only | Standard approach | 17 |
| PREFIX+MIDDLE | Role-carrying morphology | 18 |
| PREFIX profile | Distribution matching | 19 |

---

## Script Specifications

### 01_unit_para_para.py
- A paragraph → B paragraph matching
- Filter B paragraphs to ≥5 PP MIDDLEs
- Compute coverage, find best matches
- Report coverage distribution

### 02_unit_para_para_large.py
- Same as 01, but B paragraphs ≥15 PP MIDDLEs
- Tests if coverage holds for substantial B programs

### 03_unit_folio_folio.py
- A folio → B folio matching
- Aggregate all PP from A folio, test B folio coverage

### 04_unit_para_folio.py
- A paragraph → B folio matching (baseline comparison)

### 05_unit_folio_para.py
- A folio → B paragraph matching
- Tests if whole A folio covers B mini-programs

### 06_class_profile_matching.py
- Compute B instruction class survival per A paragraph
- Cluster A paragraphs by class fingerprint
- Match to B execution contexts with similar profiles

### 07_kernel_accessibility.py
- Compute k/h/e accessibility per A paragraph
- Match to B paragraphs with similar kernel profiles
- Test if e-depleted A → FL-heavy B

### 08_regime_prediction.py
- Extract PREFIX distribution from A paragraphs
- Predict B REGIME from A morphology
- Validate against C494 REGIME definitions

### 09_lane_balance.py
- Compute PP lane character (k-rich = QO, e-rich = CHSH)
- Predict B lane balance from A PP
- Test QO fraction prediction

### 10_hazard_exposure.py
- Compute active hazard subset per A paragraph
- Match A to B by hazard exposure profile
- Binary signal - should be cleanest test

### 11_role_composition.py
- Compute expected role distribution per A
- Match to B paragraph role profiles
- Test by role (FL weakest, FQ strongest)

### 12_azc_mediated.py
- Restrict to AZC-mediated vocabulary only
- Filter out B-native overlap
- Test if correspondence improves

### 13_linker_network.py
- Map RI linker topology to B execution
- Test if hub folios (f93v: 5 inputs) differ in B

### 14_header_matching.py
- Match A paragraph line-1 to B paragraph line-1
- Compare header-header vs body-body strength

### 15_section_constrained.py
- Restrict matching within section constraints
- Section T should show zero B correspondence (control)

### 16-19_vocabulary_levels.py
- Repeat best approach at different vocabulary levels
- Full tokens, MIDDLEs, PREFIX+MIDDLE, PREFIX profile

### 20_synthesis.py
- Meta-analysis across all approaches
- Identify which approaches produce signal
- Rank by effect size and statistical significance

---

## Success Criteria

| Level | Criteria |
|-------|----------|
| STRONG | ≥3 approaches show significant A-B correspondence (p<0.05, lift >2x) |
| MODERATE | 1-2 approaches show significant correspondence |
| WEAK | Some signal but not statistically robust |
| NULL | No approach produces meaningful correspondence |

**NULL result is informative** - confirms A and B are parallel systems without operational coupling.

---

## Priority Order

Based on expert assessment:

1. **10_hazard_exposure.py** - Binary signal, cleanest prediction
2. **12_azc_mediated.py** - Removes known noise source
3. **09_lane_balance.py** - Demonstrated cross-system signal
4. **06_class_profile_matching.py** - C503.a establishes mechanism
5. **07_kernel_accessibility.py** - Core control architecture
6. **02_unit_para_para_large.py** - Direct test with substantial B programs

Lower priority: 01, 03-05, 08, 11, 13-19

---

## Expected Output

```
phases/A_B_CORRESPONDENCE_SYSTEMATIC/
├── README.md (this file)
├── FINDINGS.md (final results)
├── scripts/
│   ├── 01_unit_para_para.py
│   ├── 02_unit_para_para_large.py
│   ├── ...
│   └── 20_synthesis.py
└── results/
    ├── unit_tests.json
    ├── profile_matching.json
    ├── synthesis.json
    └── ...
```
