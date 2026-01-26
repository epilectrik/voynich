# PP CLASSIFICATION SYSTEM

**Date:** 2026-01-25
**Status:** COMPLETE

---

## Overview

This phase establishes Tier 4 semantic properties for PP MIDDLEs and projects them onto RI through compositional analysis.

---

## PP Classification Results

### Material-Class Distribution

| Class | Count | % | Description |
|-------|-------|---|-------------|
| ANIMAL | 63 | 15.6% | >2x enriched in animal-suffix records |
| HERB | 113 | 28.0% | >2x enriched in herb-suffix records |
| MIXED | 67 | 16.6% | Present in both, no strong preference |
| NEUTRAL | 161 | 39.9% | Not enriched in either |

### Top Animal-Associated PPs

| PP | Evidence |
|----|----------|
| pch | 43x animal-enriched |
| opch | 18x animal-enriched |
| octh | 9x animal-enriched |
| cph | 3.7x animal-enriched |
| kch | 3.7x animal-enriched |
| ch | 2.9x animal-enriched |
| h | 2.5x animal-enriched |

### Top Herb-Associated PPs

| PP | Evidence |
|----|----------|
| keo | 66x herb-enriched |
| eok | 52x herb-enriched |
| ko | 33x herb-enriched |
| cho | 33x herb-enriched |
| to | 33x herb-enriched |
| eo | 3.3x herb-enriched |

---

## RI Projection Results

### Methodology

1. Find PP substrings (atoms) within each RI
2. Look up material class for each PP atom
3. Project class based on atom composition

### Statistics

- RI with PP atoms: 584/609 (95.9%)
- Mean PP atoms per RI: 4.36
- Max PP atoms per RI: 16

### Projected RI Distribution

| Class | Count | % |
|-------|-------|---|
| MIXED | 271 | 44.5% |
| HERB | 169 | 27.8% |
| ANIMAL | 107 | 17.6% |
| UNKNOWN | 25 | 4.1% |
| HERB_MIXED | 23 | 3.8% |
| ANIMAL_MIXED | 8 | 1.3% |
| NEUTRAL | 6 | 1.0% |

### High-Confidence RI (>70% confidence)

- **Animal RI:** 16 (e.g., `cphodaiil`, `hodaii`, `odaiii`)
- **Herb RI:** 57 (e.g., `octo`, `yto`, `koi`, `lot`)

---

## Tier 4 Semantic Framework

### PP Role

```
PP MIDDLE = Material-class signal + Token variant selector

Material classes:
- ANIMAL: Heat-sensitive operations (precision required)
- HERB: Standard plant processing
- MIXED: Multi-material applicability
- NEUTRAL: Infrastructure/universal operations
```

### RI Role

```
RI MIDDLE = PP1 ^ PP2 ^ ... (compatibility intersection)

Material projection:
- RI inherits material-class from constituent PP atoms
- Multi-atom RI = more specific material reference
- High-confidence RI = substance-specific identifiers
```

### Combined Model

```
A Record:
+-- RI (WHAT: specific substance)
|   +-- PP atoms define material-class inheritance
|   +-- Folio-localized (87% to 1-2 folios)
|
+-- PP (HOW: execution tuning)
    +-- Material-class determines token variants
    +-- Same grammar, different behavioral parameters
```

---

## Constraint Implications

### New Findings (Tier 4)

| Finding | Status |
|---------|--------|
| PP material-class distribution (15.6% animal, 28% herb) | Documented |
| RI projection through PP composition | Documented |
| 95.9% of RI contain classifiable PP atoms | Confirmed |
| High-confidence material-specific RI identifiable | 73 RI classified |

### Relationship to Existing Constraints

| Constraint | Relationship |
|------------|--------------|
| C498 | PP/RI split confirmed (404/609) |
| C505 | PP material signatures extended to full classification |
| C516 | 85% multi-atom RI confirmed (mean 4.36 atoms) |
| C526 | RI as lexical layer - now with material-class projection |

---

## Files

| File | Purpose |
|------|---------|
| `scripts/pp_classification.py` | PP classification engine |
| `scripts/ri_projection.py` | RI projection through PP atoms |
| `results/pp_classification.json` | Full PP classification data |
| `results/ri_projection.json` | Full RI projection data |

---

## Usage

### Lookup PP Material Class

```python
import json
with open('phases/PP_CLASSIFICATION/results/pp_classification.json') as f:
    data = json.load(f)

pp = 'ch'
cls = data['pp_classification'][pp]['material_class']
print(f"{pp} -> {cls}")  # ch -> ANIMAL
```

### Lookup RI Projected Class

```python
with open('phases/PP_CLASSIFICATION/results/ri_projection.json') as f:
    data = json.load(f)

ri = 'cphodaiil'
cls = data['ri_classification'][ri]['projected_class']
conf = data['ri_classification'][ri]['confidence']
print(f"{ri} -> {cls} ({conf:.0%})")  # cphodaiil -> ANIMAL (80%)
```

---

## Next Steps

1. **Validate projection** against independent Brunschwig material categories
2. **Test token variant differentiation** using projected RI classes
3. **Build material-class inference** for full A records
