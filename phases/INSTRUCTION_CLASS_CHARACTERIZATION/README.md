# INSTRUCTION_CLASS_CHARACTERIZATION Phase

**Status:** ACTIVE
**Started:** 2026-01-25
**Goal:** Deep characterization of the 49 instruction classes

---

## Background

We have established:
- 49 instruction classes (C121)
- 7 role categories (CORE_CONTROL, ENERGY_OPERATOR, AUXILIARY, FREQUENT_OPERATOR, HIGH_IMPACT, FLOW_OPERATOR, LINK)
- 479 tokens mapping to these classes (9.8x compression)
- 17 forbidden transitions in 5 hazard classes

**What we DON'T know:**
- What distinguishes Class 1 from Class 2 within AUXILIARY?
- Do certain classes appear in control-intensive vs output-intensive folios?
- What are individual class behavior profiles?
- How do classes co-occur and interact?

---

## Research Questions

### Q1: Class Distribution Patterns
- Which classes are folio-specific vs universal?
- Which classes cluster by section (B, H, S, C)?
- Which classes are REGIME-correlated?

### Q2: Class Positional Behavior
- Do classes have line-position preferences?
- Are certain classes line-initial or line-final specialists?
- Do classes show position shifts across sections?

### Q3: Class Co-occurrence
- Which classes co-occur within lines?
- Are there class "sequences" that repeat?
- Which class pairs are enriched/depleted?

### Q4: Class Morphological Structure
- What PREFIX/SUFFIX patterns distinguish classes within a role?
- Do classes differ by morphological complexity?
- Are there class-specific MIDDLE patterns?

### Q5: Class Hazard Proximity
- Which classes appear adjacent to forbidden transitions?
- Do classes differ in hazard exposure?
- Are certain classes "gateway" vs "terminal"?

### Q6: Class REGIME Correlation
- Do control-intensive REGIMEs favor certain classes?
- Are there REGIME-exclusive classes?
- How does class distribution differ by REGIME?

---

## Role Breakdown (from class_token_map.json)

| Role | Classes | Count |
|------|---------|-------|
| AUXILIARY | 1-6, 15-29 | 20 |
| ENERGY_OPERATOR | 8, 31-49 | 19 |
| FREQUENT_OPERATOR | 9, 13, 14, 23 | 4 |
| FLOW_OPERATOR | 7, 30, 38, 40 | 4 |
| CORE_CONTROL | 10, 11, 12 | 3 |

### CORE_CONTROL Classes (3)
- Class 10: daiin
- Class 11: ol
- Class 12: k

### FLOW_OPERATOR Classes (4)
- Class 7: ar, al
- Class 30: dar, dal, dain, dair, dam
- Class 38: aral, aldy, arody, aram, arol, daim
- Class 40: daly, aly, ary, dary, daiir, dan

### ENERGY_OPERATOR Classes (19)
- Class 8: chedy, shedy, chol (basic energy)
- Class 31: chey, shey, chor, shol, chy, chdy, sho, shy, shor, char, cho, cheo
- Class 32-49: qo-family and complex ch/sh compounds

### AUXILIARY Classes (20)
- Classes 1-6: Complex ok/ot/ol/y-prefixed tokens
- Classes 15-29: Varied auxiliary operations

### FREQUENT_OPERATOR Classes (4)
- Class 9: aiin, or, o
- Class 13: ok/ot-aiin family
- Class 14: ok/ot-al/ar/y family
- Class 23: dy, s, y, r, am, l, d (simple terminals)

---

## Planned Scripts

1. `class_distribution_analysis.py` - Basic frequency by folio, section, REGIME
2. `class_position_analysis.py` - Line position preferences per class
3. `class_cooccurrence_analysis.py` - Class pair statistics
4. `class_morphology_analysis.py` - PREFIX/SUFFIX patterns per class
5. `class_hazard_proximity.py` - Distance to forbidden transitions
6. `class_regime_correlation.py` - REGIME-specific patterns
7. `class_differentiation_test.py` - What distinguishes classes within roles

---

## Expected Outcomes

1. **Class behavior profiles** - Individual characterization of each class
2. **Class taxonomy refinement** - Are the 49 classes the right granularity?
3. **Class-based folio signatures** - Can we characterize folios by class distribution?
4. **Operational interpretation hints** - Do class patterns suggest procedural stages?

---

## Dependencies

- `phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json` - Class-token mapping
- `phases/REGIME_SEMANTIC_INTERPRETATION/results/regime_folio_mapping.json` - REGIME classification

---

## Success Criteria

Phase is complete when:
1. All 49 classes have documented behavior profiles
2. Class distribution patterns across section/REGIME are characterized
3. Within-role differentiation is explained
4. At least one new structural insight emerges

---

## Navigation

<- [../REGIME_SEMANTIC_INTERPRETATION/RESULTS.md](../REGIME_SEMANTIC_INTERPRETATION/RESULTS.md)
