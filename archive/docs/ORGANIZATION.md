# Project Organization Guide

This document describes the directory structure and file organization for the Voynich Manuscript analysis project.

## Root Directory

The root contains only core documentation and directory structures:

| File/Dir | Purpose |
|----------|---------|
| `CLAUDE.md` | Complete project documentation (model locked) |
| `README.md` | Public-facing project summary |
| `ORGANIZATION.md` | This file |
| `limits_statement.md` | Epistemological boundaries |
| `assumption_boundary.md` | What physics audit does NOT prove |
| `overall_verdict.md` | Final judgment summary |
| `validated_structural_findings.md` | 165 constraints list |

## Directory Structure

### `phases/` - Analysis Phases

Each phase contains all related scripts, outputs, and reports in a flat structure.

**Core Sequential Phases:**
- `01-09_early_hypothesis/` - Initial analysis and model building
- `10-14_domain_characterization/` - Domain discrimination tests
- `15-20_kernel_grammar/` - Kernel structure and grammar discovery
- `21-23_enumeration/` - Full enumeration and regime boundaries
- `X_adversarial_audit/` - Falsification and adversarial testing

**Specialized Analysis Phases:**
- `CCF_circular_folios/` - Circular folio analysis
- `ILL_illustration_independence/` - Illustration coupling tests
- `FSS_family_syntax/` - Family syntax significance
- `CSM_control_signature/` - Control signature matching
- `HCG_historical_comparison/` - Historical grammar comparison
- `PMS_prefix_material/` - Prefix material selection tests
- `PCS_coordinate_system/` - Prefix/suffix coordinate geometry
- `ARE_apparatus_engineering/` - Apparatus reverse engineering
- `HFM_human_factors/` - Human factors and manual design
- `PPA_physics_plausibility/` - Physics plausibility audit
- `L1L2_forward_inference/` - Lane 1 and 2 experiments
- `L3_material_class/` - Material class compatibility
- `L4_geometry/` - Geometry compatibility
- `EPM_exploratory_process/` - Exploratory process mapping
- `APF_adversarial_process/` - Adversarial process comparison
- `HTO_human_track_ordering/` - Human-track ordering analysis
- `CDCE_cross_domain/` - Cross-domain engineering comparison
- `SRP_speculative_reconstruction/` - Speculative reconstruction
- `PIA_product_isolation/` - Product isolation analysis
- `PIAA_plant_illustration/` - Plant illustration alignment
- `PPC_program_plant_correlation/` - Program-plant correlation
- `FMR_failure_mode_reconstruction/` - Failure mode reconstruction

**Auxiliary Phases:**
- `VIS_visual_analysis/` - Visual and AI analysis
- `CUR_currier_analysis/` - Currier A/B analysis
- `ANN_annotation_analysis/` - Annotation and coding
- `COR_correlation_analysis/` - Correlation testing
- `ZOD_zodiac_analysis/` - Zodiac page analysis
- `NAI_naibbe_investigation/` - NAIBBE token investigation
- `DAI_daiin_analysis/` - DAIIN token analysis
- `ENT_entry_structure/` - Entry structure analysis

### `legacy/` - Preserved Falsified Hypotheses

Scientific record of rejected approaches:

- `translation_attempts/` - Semantic decoding attempts (rejected Phase X.5)
- `dictionary_building/` - Lexicon construction (superseded)
- `semantic_analysis/` - Meaning-layer analysis (falsified)

### `lib/` - Reusable Code

- `analysis/` - Analysis modules (crypto, linguistic, ml, statistical)
- `tools/` - Helper tools (parser, search, visualizer)
- `utilities/` - Standalone utility scripts

### `data/` - Input Data

- `transcriptions/` - EVA transcriptions of manuscript text
- `scans/` - Folio images (if present)

### `results/` - Frozen Canonical Outputs

- `canonical_grammar.json` - The 49-class instruction grammar
- `full_recipe_atlas.txt` - Complete 83-folio recipe enumeration
- `control_signatures.json` - Kernel operator definitions
- `summary_reports/` - High-level summary documents

### `folio_analysis/` - Per-Folio Deep Dives

- `hazard_maps/` - Hazard analysis for 15 special folios
- `kernel_trajectories/` - State trajectory analysis
- `outlier_traces/` - Outlier detection traces

### Other Directories

- `annotation_data/` - Manual annotation data
- `research/` - External reference materials
- `temp_images/` - Temporary image files

## File Naming Conventions

| Pattern | Meaning |
|---------|---------|
| `phase{N}_*.py` | Phase N script |
| `phase{N}_*.json` | Phase N output data |
| `*_report.md` | Primary report document |
| `*_analysis.md` | Detailed analysis |
| `*_results.json` | Test/analysis results |
| `*_synthesis.json` | Phase summary |

## Adding New Analysis

To add a new phase:

1. Create directory: `phases/{ABBR}_{descriptive_name}/`
2. Add scripts, outputs, and reports to that directory
3. Update CLAUDE.md with findings
4. Update this file if adding a new category

## Cross-References

CLAUDE.md references files throughout the project. When moving files, update the Project Structure and Key Outputs sections in CLAUDE.md.
