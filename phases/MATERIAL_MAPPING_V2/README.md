# MATERIAL_MAPPING_V2 Phase

## Objective

Systematically map Brunschwig materials to Voynich RI tokens using multi-dimensional signature matching based on BRSC/BCSC predictions.

## Background

### Previous Work

| Phase | Finding | Limitation |
|-------|---------|------------|
| ANIMAL_PRECISION_CORRELATION | **eoschso = ennen (chicken)** via ESCAPE+AUX pattern | Only 1 high-confidence mapping |
| MATERIAL_REGIME_MAPPING | Materials don't differentiate at REGIME level | Both animal/herb → REGIME_4 |
| BRUNSCHWIG_FULL_MAPPING | 86.8% grammar compliance, category→product works | No entry-level token mapping |

### Why V2 Can Do Better

New tools available:
1. **BRSC** - Formalizes 9 Brunschwig protocols with Voynich mappings
2. **BCSC** - 49 instruction classes with role taxonomy (EN/FL/FQ/CC/AX)
3. **Multi-dimensional signatures** - Fire degree + instruction pattern + kernel profile + suffix morphology

### Key Insight

Materials encode through **AFFORDANCE OCCUPATION**, not direct mapping:
- Same grammar, different token variants (Jaccard=0.38)
- Material type → instruction pattern → PREFIX profile → token selection

## Methodology

### Fire Degree → REGIME Mapping (from BRSC)

| Degree | REGIME | Description |
|--------|--------|-------------|
| 1 | REGIME_2 | Gentle (balneum marie) |
| 2 | REGIME_1 | Standard |
| 3 | REGIME_3 | Intense |
| 4 | REGIME_4 | Precision |

### Instruction Pattern → PREFIX Profile (from BCSC)

| Role | PREFIX Association | Kernel Content |
|------|-------------------|----------------|
| e_ESCAPE | qo (escape route) | k+e, 0% h |
| AUX | ok/ot (auxiliary) | balanced |
| FLOW | da (flow redirect) | 0% kernel |
| LINK | ol/or/al/ar | monitoring |
| h_HAZARD | ch/sh (phase) | h dominant |
| k_ENERGY | qo (energy) | k dominant |

## Scripts

| Script | Purpose | Status |
|--------|---------|--------|
| 00_compute_brunschwig_signatures.py | GATE: Compute signatures for 245 recipes | DONE |
| 01_extract_a_record_profiles.py | Profile A records with animal/material RI | DONE |
| 02_multidim_matching.py | Score all (material, record) pairs | DONE |
| 03_validate_mappings.py | Statistical validation | DONE |
| 04_kernel_pattern_test.py | Test kernel predictions | DONE |
| 05_suffix_correlation_test.py | Test suffix predictions | DONE |
| 06_synthesis.py | Final mapping table | DONE |

## Results

**Verdict: MODERATE**

- 20 validated mappings covering 2 unique materials
- Ox blood water: 15 mappings (HIGH confidence)
- Hen (chicken): 5 mappings (MEDIUM confidence)
- eoschso=chicken not reproduced (different methodology)

See [FINDINGS.md](FINDINGS.md) for detailed analysis.

## Success Criteria

| Level | Criteria |
|-------|----------|
| STRONG | 5+ validated mappings with p < 0.05 |
| MODERATE | 2-4 validated mappings |
| WEAK | Only confirms existing eoschso=chicken |
| FAILURE | No validated mappings |

## Data Dependencies

- `data/brunschwig_curated_v3.json` - 245 recipes with fire_degree, procedural_steps
- `phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json` - Token→class mapping
- `context/STRUCTURAL_CONTRACTS/brunschwig.brsc.yaml` - Protocol specifications
- `context/STRUCTURAL_CONTRACTS/currierB.bcsc.yaml` - Role taxonomy
