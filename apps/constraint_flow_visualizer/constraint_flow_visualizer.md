# Constraint Flow Visualizer

A PyQt5 desktop application that visualizes the A→AZC→B constraint pipeline from the Voynich manuscript research.

---

## Overview

### What This Is

This is a **reachable-state explorer**, not a decoder. It visualizes how Currier A constraint bundles propagate through AZC legality fields to restrict Currier B execution space.

### What This Is NOT

- Not a decoder or translator
- Not a search tool for "matching" records
- Not a prediction engine

### Core Conceptual Model

```
Currier A specifies constraint bundles (what must not be confused).
AZC projects those bundles into position-indexed legality fields (when things are allowed).
Currier B executes blind grammar within the shrinking reachable space.

Grammar unchanged. Option space contracts.
```

---

## Quick Start

### Dependencies

```
PyQt5>=5.15.0
```

Install:
```bash
pip install PyQt5
```

### Running

```bash
cd apps/constraint_flow_visualizer
python main.py
```

### Required Data Files

The app loads these files from the repository root:

| File | Purpose |
|------|---------|
| `data/transcriptions/interlinear_full_words.txt` | A + B records corpus |
| `phases/01-09_early_hypothesis/phase20a_operator_equivalence.json` | 49 instruction classes |
| `phases/AZC_REACHABILITY_SUPPRESSION/middle_class_index.json` | MIDDLE → class mapping |
| `phases/AZC_REACHABILITY_SUPPRESSION/phase1_results.json` | Forbidden transitions |
| `results/azc_folio_features.json` | AZC folio metadata |
| `results/middle_zone_legality.json` | Zone legality per MIDDLE |
| `results/b_folio_class_footprints.json` | B folio class usage |
| `results/regime_folio_mapping.json` | REGIME assignments |
| `results/unified_folio_profiles.json` | Folio metrics |

---

## Architecture

### Directory Layout

```
apps/constraint_flow_visualizer/
├── main.py                    # Entry point
├── requirements.txt           # Dependencies
├── README.md                  # Design principles
├── constraint_flow_visualizer.md  # This file
├── fonts/
│   └── VoynichEVA.ttf         # EVA font for rendering
├── core/                      # Computation layer
│   ├── __init__.py
│   ├── data_loader.py
│   ├── constraint_bundle.py
│   ├── azc_projection.py
│   ├── reachability_engine.py
│   ├── morphology.py
│   ├── a_record_loader.py
│   ├── control_graph.py
│   ├── reachability_computer.py
│   ├── role_classifier.py
│   └── sufficiency_engine.py
├── ui/                        # PyQt5 widgets
│   ├── __init__.py
│   ├── main_window.py
│   ├── a_entry_panel.py
│   ├── azc_field_panel.py
│   ├── b_reachability_panel.py
│   ├── baseline_grammar_panel.py
│   ├── legality_dashboard.py      # PRIMARY: Legality envelope visualization
│   ├── control_loop_panel.py      # (Legacy)
│   ├── hazard_summary_panel.py
│   ├── legality_metrics_panel.py
│   ├── reachability_view.py
│   ├── role_node_item.py
│   └── connectivity_edge_item.py
├── scripts/                   # Utility scripts
│   └── [analysis and diagnostic tools]
└── parsing/
    └── __init__.py
```

### Technology Stack

| Component | Technology |
|-----------|------------|
| Framework | PyQt5 |
| Language | Python 3.8+ |
| Graphics | PyQt5 QGraphicsView (no external plotting) |
| Data Format | JSON files |
| Database | None (file-based) |

### Bootstrap Flow

1. Add app directory to Python path
2. Import core infrastructure modules
3. Load all data via `get_data_store()` (singleton)
4. Create `QApplication`
5. Create and show `MainWindow`
6. Run event loop

---

## Core Layer (`core/`)

### Module Responsibilities

| Module | Responsibility |
|--------|----------------|
| `data_loader.py` | Load and index all data; provide singleton DataStore |
| `constraint_bundle.py` | Extract AZC-active MIDDLEs; compute compatible folios |
| `azc_projection.py` | Project bundle through AZC legality fields |
| `reachability_engine.py` | Compute B folio reachability under legality |
| `morphology.py` | Decompose tokens into PREFIX/MIDDLE/SUFFIX (per C267) |
| `a_record_loader.py` | Load Currier A records from corpus |
| `control_graph.py` | Represent 49-class grammar as directed graph |
| `reachability_computer.py` | Aggregate to 6-role connectivity level |
| `role_classifier.py` | Map 49 classes → 6 roles |
| `sufficiency_engine.py` | Check REGIME completeness (Tier 3) |

### Key Data Structures

#### ConstraintBundle
The A record's constraint signature.
```python
ConstraintBundle
├── token: str
├── middles: Set[str]           # All MIDDLEs in record
├── azc_active: Set[str]        # AZC-discriminating MIDDLEs only
└── bundle_type: BundleType     # NEUTRAL / ACTIVATING / BLOCKED
```

#### AZCConstraintBundle
Canonical bundle unit (immutable, hashable).
```python
AZCConstraintBundle (frozen)
├── azc_active_middles: FrozenSet[str]
├── compatible_folios: FrozenSet[str]
└── bundle_type: BundleType
```

#### LegalityProfile
Zone-indexed legality for a bundle.
```python
LegalityProfile
├── folio_signature: FrozenSet[str]
├── survives_C: bool
├── survives_P: bool
├── survives_R: bool
├── survives_S: bool
└── commitment_zone: Optional[str]
```

#### AZCProjectionResult
Per-folio projection output.
```python
AZCProjectionResult
├── folio: str
└── reachability_by_zone: Dict[str, ZoneReachability]
```

#### ReachabilityResult
Complete reachability computation output.
```python
ReachabilityResult
├── grammar_state: GrammarState
├── grammar_by_zone: Dict[str, GrammarState]
└── folio_results: Dict[str, FolioReachability]
```

#### FolioReachability
B folio status classification.
```python
FolioReachability
├── folio: str
├── status: ReachabilityStatus  # REACHABLE / CONDITIONAL / UNREACHABLE
├── required_classes: Set[int]
├── available_classes: Set[int]
└── sufficiency: Optional[FolioSufficiency]
```

---

## UI Layer (`ui/`)

### Panel Responsibilities

| Panel | Purpose |
|-------|---------|
| `main_window.py` | Top-level window, layout, dark theme, signal routing |
| `a_entry_panel.py` | Folio→Line→Record selector; emits bundle selection |
| `azc_field_panel.py` | AZC legality visualization; compatible folios + zone legality |
| `b_reachability_panel.py` | Table: folio status (REACHABLE/CONDITIONAL/UNREACHABLE) |
| `baseline_grammar_panel.py` | Side-by-side baseline vs conditioned grammar |
| `legality_dashboard.py` | **PRIMARY**: Shows what CHANGES between A records |
| `control_loop_panel.py` | (Legacy) Workflow diagram: A→AZC→B pipeline |
| `hazard_summary_panel.py` | Atomic vs decomposable hazard breakdown |
| `legality_metrics_panel.py` | KPIs: reachable classes, pruned, zones |
| `reachability_view.py` | QGraphicsView-based graph visualization |
| `role_node_item.py` | QGraphicsItem for graph nodes |
| `connectivity_edge_item.py` | QGraphicsItem for graph edges |

### A Record Color Coding

The A entry panel uses color to indicate bundle type:

| Color | Bundle Type | Meaning |
|-------|-------------|---------|
| **Orange** | ACTIVATING | Has restricted MIDDLEs that constrain AZC compatibility |
| **Red** | BLOCKED | Incompatible with all AZC folios |
| **Grey/Blue** | NEUTRAL | No AZC-active MIDDLEs (doesn't constrain anything) |

**Orange entries are the interesting ones** - they have unique constraint fingerprints (C481: 0 collisions across 1,575 records tested) and show dramatic variation in the Legality Dashboard.

### Legality Dashboard

The Legality Dashboard (`legality_dashboard.py`) is the primary visualization for understanding A record variation. It shows what CHANGES when you select different A records, not the fixed grammar structure.

**Key insight:** The grammar is universal (same 49 classes, same topology). What varies dramatically is the **legality envelope** - which AZC folios are activated, which MIDDLEs are compatible, and how this affects B folio execution.

**Dashboard Panels:**

1. **AZC Folio Activation** - Shows which of 29 AZC folios are activated by this A record's MIDDLEs
2. **Recovery Budget** - Escape rate meter (1.0% to 28.6% range per C468)
3. **MIDDLE Compatibility** - Compatible vs blocked MIDDLEs (95.7% incompatible per C475)
4. **B Folio Compilation** - Select a B folio to see impact: available vs blocked classes

### Signal Flow

```
AEntryPanel
    │
    │ token_selected(ConstraintBundle)
    v
MainWindow
    │
    ├──> AZCFieldPanel.update(bundle)
    ├──> BReachabilityPanel.update(result)
    ├──> BaselineGrammarPanel.update(grammar_state)
    ├──> LegalityDashboard.update_from_bundle(bundle)  ← PRIMARY
    └──> [other panels receive updates]
```

---

## Data Flow

### Pipeline Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    CURRIER A RECORD INPUT                    │
│  (Selected via AEntryPanel: folio → line → record)           │
└────────────────────────┬────────────────────────────────────┘
                         │
                         v
        ┌────────────────────────────────────┐
        │  CONSTRAINT BUNDLE COMPUTATION      │
        │  (constraint_bundle.py)             │
        │                                     │
        │  1. Extract tokens from record      │
        │  2. Decompose: PREFIX/MIDDLE/SUFFIX │
        │  3. Filter to AZC-active MIDDLEs    │
        │  4. Create ConstraintBundle         │
        │  5. Compute compatible AZC folios   │
        └────────────────┬────────────────────┘
                         │
                         v
        ┌────────────────────────────────────┐
        │   AZC PROJECTION ENGINE             │
        │   (azc_projection.py)               │
        │                                     │
        │  For each compatible AZC folio:     │
        │  - For each zone (C, P, R, S):      │
        │    * Apply zone legality            │
        │    * Compute zone-legal MIDDLEs     │
        │    * Map to reachable classes       │
        │  Output: AZCProjectionResult        │
        └────────────────┬────────────────────┘
                         │
                         v
        ┌────────────────────────────────────┐
        │  REACHABILITY ENGINE                │
        │  (reachability_engine.py)           │
        │                                     │
        │  1. Aggregate vocabularies (UNION)  │
        │  2. Compute grammar state per zone  │
        │  3. For each B folio:               │
        │     - Get required classes          │
        │     - Check zone survival           │
        │     - Classify status               │
        │     - Compute sufficiency           │
        │  Output: ReachabilityResult         │
        └────────────────┬────────────────────┘
                         │
                         v
        ┌────────────────────────────────────┐
        │         UI UPDATE (all panels)      │
        └────────────────────────────────────┘
```

### Zone Legality Semantics

Per constraint C313:
- Missing zone data = unrestricted carrier (legal everywhere)
- Zone restrictions are EXCEPTIONAL, not default
- MIDDLE absence in a zone = illegal in that zone
- Lookup via `middle_zone_legality.json`

### Folio Compatibility (Asymmetric Filter)

Per constraints C442, C470, C472:
- **Restricted MIDDLEs** (1-3 folios spread): CAN forbid compatibility
- **Universal MIDDLEs** (4+ folios): CANNOT forbid compatibility
- Both still participate in grammar computation

---

## Integration with Constraint System

### Implemented Constraints

The app implements behavior defined in these structural contracts:

| Contract | Purpose |
|----------|---------|
| `currierA.casc.yaml` | A record structure, morphology, participation rules |
| `azc_activation.act.yaml` | A→AZC transformation, zone legality |
| `azc_b_activation.act.yaml` | AZC→B propagation, legality inheritance |
| `currierB.bcsc.yaml` | B internal grammar, 49 classes, hazards |

### Key Constraint References

| Constraint | Implementation |
|------------|----------------|
| C267 | Morphology decomposition (PREFIX/MIDDLE/SUFFIX) |
| C313 | Zone legality defaults (missing = unrestricted) |
| C442, C470, C472 | Folio compatibility asymmetric filter |
| C085, C089, C107, C171, C485 | Kernel class protection |
| C396.a | Infrastructure AUXILIARY role protection |

### Tier 3 Interpretation (Sufficiency)

REGIME completeness thresholds (observational, not enforced):
- REGIME_4: `link_density >= 0.25`
- REGIME_3: `recovery_ops >= 2`
- REGIME_2/1: No thresholds

---

## Design Principles

### 1. Always Show Baseline + Conditioned

Grammar never changes. The app always displays:
- **Baseline**: Full 49-class grammar
- **Conditioned**: Grammar with unreachable classes grayed

### 2. Zone-Indexed Reachability

Not just "allowed/not allowed" but WHERE in the AZC position space:
- **C zone**: Center position
- **P zone**: Peripheral position
- **R zones**: R1, R2, R3 radial positions
- **S zones**: S1, S2 peripheral positions

### 3. Binary Classification First

Primary classification is discrete:
- **REACHABLE**: All required classes available
- **CONDITIONAL**: Some required classes available
- **UNREACHABLE**: Missing critical classes

Percentage coverage is secondary metric only.

### 4. Language Discipline

**Allowed terms:**
- "reachable under"
- "legality field"
- "grammar unchanged"
- "option space contracts"

**Forbidden terms:**
- "selects" (AZC never selects)
- "triggers" (B never triggers)
- "matches" (no matching semantics)
- "predicts" (no prediction)

---

## Scripts (`scripts/`)

Utility scripts for data generation and diagnostics:

| Script | Purpose |
|--------|---------|
| `compute_b_folio_footprints.py` | Generate B folio class usage |
| `compute_middle_zone_legality.py` | Generate zone legality mapping |
| `create_regime_mapping.py` | Generate REGIME assignments |

Additional scripts handle various analysis and debugging tasks for the constraint pipeline.

---

## State Management

### Singleton Pattern

`data_loader.py` provides `get_data_store()` which returns a single `DataStore` instance, cached at module level. Data is loaded once at startup.

### Immutable Data Structures

Key classes use `@dataclass(frozen=True)`:
- `AZCConstraintBundle`
- `MorphologyResult`
- Various value types in `reachability_engine.py`

This enables safe caching and hashing.

### Signal-Based UI

PyQt5 signals connect components:
- `AEntryPanel` emits `token_selected(ConstraintBundle)`
- `MainWindow` receives signal, triggers pipeline
- Results propagate to panels via direct calls

---

## Fonts

The `fonts/VoynichEVA.ttf` font renders tokens in EVA transcription format for authentic display of Voynich text.
