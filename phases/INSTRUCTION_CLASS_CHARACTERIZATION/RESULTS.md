# INSTRUCTION_CLASS_CHARACTERIZATION Results

**Phase:** INSTRUCTION_CLASS_CHARACTERIZATION
**Date:** 2026-01-25
**Status:** IN PROGRESS

---

## Goal

Deep characterization of the 49 instruction classes beyond role taxonomy.

---

## Key Finding: Class 12 (k) Never Appears Standalone

**Finding:** The kernel operator `k` (Class 12, CORE_CONTROL) never appears as a standalone token in the entire Voynich manuscript.

| Metric | Value |
|--------|-------|
| Standalone `k` tokens in Currier B | 0 |
| Standalone `k` tokens in Currier A | 0 |
| Words containing `k` in Currier B | 1,557 |

**Interpretation:** The kernel always operates in **bound form** - never in isolation. This suggests the kernel is a modifier/operator that must attach to other morphological components, not an independent instruction.

**Constraint Implication:** This supports the view that `k` is an intervention marker (per existing constraints) rather than a standalone operation.

---

## Class Distribution Analysis

### Universality Tiers

| Tier | Criterion | Classes |
|------|-----------|---------|
| Universal | 80%+ folio coverage | 21 classes (43%) |
| Common | 50-79% coverage | 16 classes (33%) |
| Rare | <50% coverage | 12 classes (24%) |

### Top Universal Classes

| Class | Role | Coverage | Tokens |
|-------|------|----------|--------|
| 8 | ENERGY_OPERATOR | 82/82 (100%) | chedy, shedy, chol |
| 13 | FREQUENT_OPERATOR | 81/82 (99%) | okaiin, okeey, otedy |
| 23 | FREQUENT_OPERATOR | 81/82 (99%) | dy, s, y, r, am, l, d |
| 33 | ENERGY_OPERATOR | 80/82 (98%) | qokeey, qokeedy, qokain |

### Rare Classes (<50% coverage)

| Class | Role | Coverage | Tokens |
|-------|------|----------|--------|
| 12 | CORE_CONTROL | 0% | k (standalone - never appears) |
| 45 | ENERGY_OPERATOR | 25/82 (30%) | qoteol, qoar, qotam |
| 42 | ENERGY_OPERATOR | 26/82 (32%) | chckhdy, shckhey, chotchy |
| 44 | ENERGY_OPERATOR | 29/82 (35%) | qopchdy, qotchor, qotchol |

---

## Class Position Analysis

### Line Position Specialists

**LINE-INITIAL Specialists (mean < 0.35):**

| Class | Role | Mean Position | Initial Rate | Tokens |
|-------|------|---------------|--------------|--------|
| 4 | AUXILIARY | 0.32 | 42.8% | ykeody, lkchedy, yteody |
| 26 | AUXILIARY | 0.34 | 40.9% | ykeedy, opchey, yteedy |

**LINE-FINAL Specialists (mean > 0.65):**

| Class | Role | Mean Position | Final Rate | Tokens |
|-------|------|---------------|------------|--------|
| 40 | FLOW_OPERATOR | 0.85 | 69.0% | daly, aly, ary |
| 22 | AUXILIARY | 0.80 | 62.2% | ly, ry |
| 38 | FLOW_OPERATOR | 0.78 | 58.0% | aral, aldy, arody |
| 15 | AUXILIARY | 0.75 | 55.9% | cthy, cthol, oly |

### Role Position Profiles

| Role | Mean Position | Tendency |
|------|---------------|----------|
| CORE_CONTROL | 0.45 | Initial-biased |
| ENERGY_OPERATOR | 0.48 | Neutral |
| AUXILIARY | 0.53 | Neutral (high variance) |
| FREQUENT_OPERATOR | 0.57 | Slightly final |
| FLOW_OPERATOR | 0.68 | **Final-biased** |

**Key Insight:** FLOW_OPERATOR classes cluster toward line-final positions (0.68 average), consistent with their role as flow terminators/redirectors.

### Section-Specific Position Shift

**Class 11 (ol)** shows significant position shift by section:

| Section | Mean Position |
|---------|---------------|
| B | 0.51 (neutral) |
| H | 0.46 (neutral) |
| S | 0.47 (neutral) |
| C | **0.71 (final)** |

**Interpretation:** In cosmological section (C), `ol` shifts toward final position, suggesting different procedural role.

---

## Class Co-occurrence Analysis

### Enriched Adjacent Pairs

| Pattern | Enrichment | Occurrences | Interpretation |
|---------|------------|-------------|----------------|
| 7 → 7 (ar/al → ar/al) | 3.91x | 39 | FLOW self-chaining |
| 9 → 9 (aiin/or → aiin/or) | 3.12x | 64 | FREQ self-chaining |
| 32 → 8 (qo → ch/sh) | 2.56x | 104 | qo-family triggers ch/sh |
| 8 → 33 (ch/sh → qo) | 2.24x | 210 | ch/sh followed by qokeey |
| 10 → 34 (daiin → cheey) | 2.31x | 42 | CORE triggers ENERGY |

### Energy Operator Chain Pattern

The most common trigram patterns reveal an **ENERGY_OPERATOR chain**:

```
(33, 33, 33) - 45 occurrences: qokeey → qokeey → qokeey
(32, 8, 33) - 33 occurrences: qokal → chedy → qokeey
(33, 34, 33) - 30 occurrences: qokeey → cheey → qokeey
```

**Pattern:** qo-family and ch/sh-family interleave, creating sustained energy operator sequences.

### Self-Repetition Leaders

| Class | Role | Self-Repeat Rate | Tokens |
|-------|------|------------------|--------|
| 33 | ENERGY_OPERATOR | 14.6% | qokeey, qokeedy |
| 13 | FREQUENT_OPERATOR | 11.2% | okaiin, okeey |
| 9 | FREQUENT_OPERATOR | 10.3% | aiin, or |
| 7 | FLOW_OPERATOR | 9.0% | ar, al |

---

## Class Behavior Profiles (Preliminary)

### CORE_CONTROL Classes (10, 11, 12)

| Class | Token | Position | Behavior |
|-------|-------|----------|----------|
| 10 | daiin | 0.40 (initial-biased) | High initial rate (35%), triggers ENERGY chains |
| 11 | ol | 0.51 (neutral) | Section-dependent; final in Section C |
| 12 | k | N/A | **Never standalone** - always bound to other morphemes |

### FLOW_OPERATOR Classes (7, 30, 38, 40)

| Class | Tokens | Position | Behavior |
|-------|--------|----------|----------|
| 7 | ar, al | 0.57 | Self-chains (3.91x), high FREQ co-occurrence |
| 30 | dar, dal, dain | 0.53 | Flexible positioning |
| 38 | aral, aldy | 0.78 | Final specialist (58%) |
| 40 | daly, aly, ary | 0.85 | **Strongest final specialist** (69%) |

### ENERGY_OPERATOR Pattern

qo-family (32, 33, 36, 44-46, 49) and ch/sh-family (8, 31, 34, 35) form an interleaving pattern, creating sustained energy sequences.

---

## Class Morphology Analysis

### PREFIX-Based Class Families

Within each role, classes are **primarily differentiated by PREFIX**:

**ENERGY_OPERATOR** splits into two major families:
| Family | Classes | Prefix | Tokens |
|--------|---------|--------|--------|
| ch/sh-family | 8, 31, 34, 35, 37, 39, 41, 42, 43, 47, 48 | ch, sh | chedy, cheey, chol... |
| qo-family | 32, 33, 36, 44, 45, 46, 49 | qo | qokeey, qokal, qotar... |

**AUXILIARY** splits by prefix:
| Family | Classes | Prefix | Tokens |
|--------|---------|--------|--------|
| ok-family | 1, 2, 16, 19 | ok/ot | okeeody, okody... |
| ol-family | 3, 15, 17, 25 | ol | olain, olaiin... |
| Articulated | 4, 5, 6, 26 | y + various | ykeody, ykeedy... |

**FLOW_OPERATOR** splits by prefix:
| Family | Classes | Prefix | Tokens |
|--------|---------|--------|--------|
| Atomic | 7 | none | ar, al |
| da-family | 30, 40 | da | dar, daly |
| ar-family | 38 | ar | aral, arody |

### Complexity Spectrum

| Complexity | Classes | Pattern |
|------------|---------|---------|
| 3.0 (max) | 1, 18, 33, 36, 42, 44, 46, 48 | ART + PRE + MID + SUF |
| 1.0 (min) | 7, 9, 11, 23 | Atomic tokens only |

**Atomic classes** (complexity=1.0) have no PREFIX or SUFFIX:
- Class 7: ar, al
- Class 9: aiin, or, o
- Class 11: ol
- Class 23: dy, s, y, r, am, l, d

### Articulator Usage

Only 3 classes show >30% articulator usage, all AUXILIARY:
- Class 4, 5: y-articulator + pch prefix
- Class 26: y-articulator + yk prefix

**Pattern:** Articulators are AUXILIARY-specific and always co-occur with certain prefixes.

---

## Class Hazard Proximity Analysis

### Only 6 Classes Are Hazard-Involved

Of 49 instruction classes, **only 6 (12%)** are directly involved in the 17 forbidden transitions:

| Class | Role | Tokens | Hazard Types |
|-------|------|--------|--------------|
| 7 | FLOW_OPERATOR | ar, al | PHASE_ORDERING, RATE_MISMATCH |
| 8 | ENERGY_OPERATOR | chedy, shedy, chol | COMPOSITION_JUMP, PHASE_ORDERING, CONTAINMENT |
| 9 | FREQUENT_OPERATOR | aiin, or, o | PHASE_ORDERING, COMPOSITION_JUMP, CONTAINMENT |
| 23 | FREQUENT_OPERATOR | dy, s, y | PHASE_ORDERING, CONTAINMENT |
| 30 | FLOW_OPERATOR | dar, dal, dain | CONTAINMENT, RATE_MISMATCH |
| 31 | ENERGY_OPERATOR | chey, shey, chor | PHASE_ORDERING (6 instances!) |

**43 classes (88%) have ZERO direct hazard involvement.**

### Role-Level Hazard Exposure

| Role | Hazard Exposure | Interpretation |
|------|-----------------|----------------|
| FLOW_OPERATOR | 1.23% | Highest - flow redirects are hazard zones |
| FREQUENT_OPERATOR | 0.42% | Moderate |
| ENERGY_OPERATOR | 0.23% | Low |
| CORE_CONTROL | **0%** | Safe - kernel intervention never hazardous |
| AUXILIARY | **0%** | Safe - support operations never hazardous |

### Gateway vs Terminal Classes

Classes show asymmetric hazard behavior:

| Class | Role | Gateway | Terminal | Balance | Interpretation |
|-------|------|---------|----------|---------|----------------|
| 30 | FLOW | 7 | 0 | +1.00 | **Pure gateway** - leads INTO hazards |
| 8 | ENERGY | 5 | 3 | +0.25 | Slight gateway bias |
| 31 | ENERGY | 0 | 8 | -1.00 | **Pure terminal** - follows hazards |

**Insight:** Class 30 (dar/dal) is the "on-ramp" to hazards, while Class 31 (chey/shey) is the "off-ramp" after hazard recovery.

### Distance from Hazards

| Position | Classes | Avg Distance |
|----------|---------|--------------|
| AT hazard | 7, 8, 9 | 0.00 |
| Near hazard | 31, 23, 30 | 1.2-2.0 |
| **Maximally distant** | 40, 21, 4 | 3.7-4.2 |

**Class 40 (daly/aly)** is maximally distant from hazards (4.22) despite being FLOW_OPERATOR - it appears to be a "safe flow" class, used for non-hazardous redirection.

### Structural Safety Pattern

The hazard architecture shows deliberate design:
1. **CORE_CONTROL (daiin, ol)** = intervention never triggers hazards
2. **AUXILIARY classes** = support operations are structurally safe
3. **FLOW_OPERATOR split**:
   - Class 30 (dar/dal) = hazardous gateway
   - Class 40 (daly/aly) = safe alternative
4. **Only basic ENERGY tokens** (ch/sh simple forms) participate in hazards - complex forms (qo-family, ch-extended) do not

---

## Class REGIME Correlation Analysis

### Role-Level REGIME Patterns

Each REGIME has a distinctive role distribution:

| REGIME | Enriched Role | Enrichment | Depleted Role | Depletion |
|--------|---------------|------------|---------------|-----------|
| REGIME_1 | ENERGY_OPERATOR | 1.19x | FREQUENT_OPERATOR | 0.68x |
| REGIME_2 | FREQUENT_OPERATOR | 1.21x | ENERGY_OPERATOR | 0.86x |
| REGIME_3 | **CORE_CONTROL** | **1.83x** | ENERGY_OPERATOR | 0.89x |
| REGIME_4 | FREQUENT_OPERATOR | 1.17x | (balanced) | - |

**Key insight:** REGIME_3 shows 1.83x CORE_CONTROL enrichment - both `daiin` (Class 10) and `ol` (Class 11) are signature classes. This is the "control without output" regime.

### REGIME Signature Classes

Each REGIME has distinctive class signatures:

**REGIME_1 (Control-infrastructure-heavy, 70% Section B):**
| Class | Distinctiveness | Tokens |
|-------|-----------------|--------|
| 32 | 2.01x vs others | qokal, qokar, qol |
| 25 | 1.82x vs others | olor, oldy, olky |
| 43 | 1.66x vs others | chodar, sheeol |
| 8 | 1.53x vs others | chedy, shedy, chol |

**REGIME_2 (Output-intensive):**
| Class | Distinctiveness | Tokens |
|-------|-----------------|--------|
| 45 | 2.34x vs others | qoteol, qoar, qotam |
| 38 | 2.21x vs others | aral, aldy, arody |
| 4 | 2.11x vs others | ykeody, lkchedy |
| 9 | 1.78x vs others | aiin, or, o |

**REGIME_3 (Control without output):**
| Class | Distinctiveness | Tokens |
|-------|-----------------|--------|
| 11 | 2.06x vs others | ol |
| 17 | 1.98x vs others | olaiin, olkeedy |
| 16 | 1.89x vs others | okaly, okchdy |
| 10 | 1.84x vs others | daiin |

**REGIME_4 (Precision mode):**
| Class | Distinctiveness | Tokens |
|-------|-----------------|--------|
| 19 | 1.89x vs others | otchy, oteol |
| 26 | 1.54x vs others | ykeedy, opchey |
| 13 | 1.40x vs others | okaiin, okeey |

### Best REGIME Discriminators

Classes with highest variance across REGIMEs (best discriminators):

| Class | Role | Variance | Pattern |
|-------|------|----------|---------|
| 33 | ENERGY | 0.00067 | High in REGIME_1 (13.8%), low in REGIME_2 (7.4%) |
| 32 | ENERGY | 0.00031 | High in REGIME_1 (7.0%), low in REGIME_2 (2.8%) |
| 13 | FREQUENT | 0.00022 | Low in REGIME_1 (5.2%), high in REGIME_4 (9.2%) |
| 9 | FREQUENT | 0.00021 | Low in REGIME_1 (2.0%), high in REGIME_2 (5.8%) |

**Pattern:** The qo-family (Classes 32, 33) concentrates in REGIME_1, while FREQUENT operators (Classes 9, 13) concentrate in REGIME_2/4.

### REGIME-Independent Classes

Classes with near-flat distribution (appear regardless of REGIME):

| Class | Role | Max Variance | Tokens |
|-------|------|--------------|--------|
| 37 | ENERGY | ~0% | chty, choy, shes |
| 41 | ENERGY | ~0% | qo, chl, she |
| 22 | AUXILIARY | ~0% | ly, ry |
| 40 | FLOW | ~0% | daly, aly, ary |

These classes represent "universal" operations needed in all procedural contexts.

### Structural Interpretation

The REGIME-class correlation reveals procedural differentiation:

1. **REGIME_1 = Energy-dominated** - qo/ch families for thermal processing (Section B)
2. **REGIME_2 = Output-dominated** - FLOW (Class 38) and articulated forms for product collection
3. **REGIME_3 = Intervention-dominated** - CORE_CONTROL (daiin, ol) for heavy monitoring
4. **REGIME_4 = Balanced/Precision** - FREQUENT operators for measured, controlled execution

---

## Phase Summary

The INSTRUCTION_CLASS_CHARACTERIZATION phase has completed all 6 research questions:

| Question | Finding |
|----------|---------|
| Q1: Distribution | 21 universal, 16 common, 12 rare classes |
| Q2: Position | FLOW final-biased (0.68), CORE initial-biased (0.45) |
| Q3: Co-occurrence | qo/ch-sh interleave; Class 33 highest self-repeat (14.6%) |
| Q4: Morphology | PREFIX differentiates within-role; 4 atomic classes |
| Q5: Hazard | Only 6 classes hazard-involved; CORE/AUX are safe |
| Q6: REGIME | REGIME_3 = 1.83x CORE_CONTROL; qo-family concentrates in REGIME_1 |

### Major Structural Insights

1. **Class 12 (k) never standalone** - kernel is always bound
2. **Only 6 classes participate in hazards** - 88% are structurally safe
3. **Gateway/Terminal asymmetry** - Class 30 leads IN, Class 31 leads OUT of hazards
4. **REGIME_3 is intervention-heavy** - CORE_CONTROL 1.83x enriched
5. **qo-family is thermal** - concentrates in REGIME_1 (Section B)

---

## Scripts

| Script | Purpose | Status |
|--------|---------|--------|
| class_distribution_analysis.py | Class universality and REGIME patterns | Complete |
| class_position_analysis.py | Line position preferences | Complete |
| class_cooccurrence_analysis.py | Co-occurrence and motif patterns | Complete |
| class_morphology_analysis.py | PREFIX/SUFFIX/complexity patterns | Complete |
| class_hazard_proximity.py | Hazard involvement and gateway/terminal | Complete |
| class_regime_correlation.py | REGIME signatures and class discrimination | Complete |

---

## Structural Insights

1. **Bound kernel:** k never standalone → intervention marker, not instruction
2. **FLOW termination:** FLOW_OPERATOR classes cluster at line-final → flow redirection/termination role confirmed
3. **Energy chains:** qo and ch/sh families interleave → sustained energy operation sequences
4. **Section sensitivity:** ol shifts final in Section C → context-dependent behavior

---

## Navigation

<- [../REGIME_SEMANTIC_INTERPRETATION/RESULTS.md](../REGIME_SEMANTIC_INTERPRETATION/RESULTS.md)
