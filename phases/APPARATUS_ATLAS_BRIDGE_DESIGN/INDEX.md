# Phase 582: Apparatus Atlas Bridge Design

**Status:** COMPLETE
**Phase type:** Synthesis/documentation (no new corpus analysis, no simulation)
**Simulation budget:** 0 traces

## Goal

Bridge the abstract apparatus response manifold (5.88-dimensional, 76 folios, 1,674 constraints) to physical apparatus specifications. The bridge centers on manifold-to-knob mapping (not instruction-to-action translation), with intervention packet library, physical metrics schema, counterfeit closure atlas, and staged experiments as primary deliverables.

## Target Constraints

| ID | Track | Verdict | Runtime |
|----|-------|---------|---------|
| C1675 | Component atlas coverage | ATLAS_COMPLETE | <1s |
| C1676 | Instruction translation coverage | TRANSLATION_COMPLETE | <1s |
| C1677 | Safety protocol derivability | SAFETY_DERIVABLE | <1s |
| C1678 | Validation experiment feasibility | EXPERIMENTS_FEASIBLE | <1s |
| C1679 | Metric bridge adequacy | METRIC_BRIDGE_COMPLETE | <1s |
| C1680 | Manifold knob identifiability | KNOB_MAPPING_IDENTIFIABLE | <1s |

## Scripts

| Script | Purpose | Status |
|--------|---------|--------|
| t0_data_assembly.py | Gather all apparatus data from 8 prior phases | PASS |
| t1_manifold_knob_mapping.py | F1-F5 -> physical control surfaces (CORE) | PASS |
| t2_intervention_packet_library.py | 11 physical packet types, counterfeit closure atlas | PASS |
| t3_physical_metrics_schema.py | DVA/YGA/DYE/CTS/forgivingness physical analogs, 7 hardware nulls | PASS |
| t4_operator_bridge.py | Heuristic layer: safety, judgment boundaries, softened labels | PASS |
| t5_equipment_specification.py | 3-level rig: MVP ($560) -> recirculatory ($735) -> pelican ($1235) | PASS |
| t6_validation_protocol.py | Staged experiments E0-E6, 61 minimum runs | PASS |
| t7_synthesis.py | 5 output documents, C1675-C1680 verdicts | PASS |

## Output Documents

| Document | Purpose |
|----------|---------|
| APPARATUS_ATLAS.md | Manifold atlas with family analogs, knob maps, equipment |
| INTERVENTION_PACKET_LIBRARY.md | Physical packet definitions and counterfeit closure atlas |
| PHYSICAL_METRICS_SCHEMA.md | Sensor mappings, formulas, event windows, hardware nulls |
| OPERATOR_BRIDGE_MANUAL.md | Heuristic interpretations, safety, operator judgment |
| VALIDATION_PROTOCOL.md | Staged experiments E0-E6 |

## Data Sources

| File | Fields |
|------|--------|
| APPARATUS_RESPONSE_MANIFOLD_SYNTHESIS (Phase 580) | F1-F5, PCA, family geometry, landscape alignment |
| PRODUCTIVE_DISRUPTION_EXPANSION (Phase 572) | DYE, DVA, YGA per folio |
| A2_FORGIVINGNESS_MECHANISM (Phase 573) | CCS1, recovery channels, excess forgivingness |
| COUNTERFEIT_CLOSURE_THRESHOLD (Phase 574) | CTS, strength-dependent behavior, landscape model |
| VIRTUAL_APPARATUS_COUPLING (Phase 563) | A1/A2/A3 family profiles |
| LINE_INTERNAL_ATOM_GRADIENT_DECOMPOSITION (Phase 581) | HEAD/TERM quintile profiles, hazard coupling |
| FOLIO_ACCENT_VECTOR (Phase 480) | Folio accent scores |
| data/decoder_maps.json | Frame hazard map |

## Key Results

- 5/5 F-axes mapped to physical knob candidates with directional predictions
- 11 physical packet types defined with grammar provenance
- 5/5 virtual metrics have operational physical definitions with sensors and formulas
- 7 hardware null conditions predesigned for controlled experimentation
- 7/7 staged experiments feasible (61 minimum runs total)
- 3-level rig specification: MVP -> recirculatory -> pelican
- All 5 hazard classes mapped with physical failure modes and prevention protocols
- 13 non-encodable operator judgment types identified
- Operator bridge explicitly framed as secondary heuristic layer

## Key Design Decisions

- Manifold-to-knob mapping is the core, not class-to-action translation (expert revision)
- CTS_phys must be defined before hardware -- without it closure threshold experiments become subjective
- Hardware nulls predesigned -- the simulator taught that success depends on comparison design
- Paragraph = self-contained operational subroutine, not "complete run" (expert correction)
- a-HEAD = active transformation / primary hazard-bearing domain, not "yield" (expert correction)
- MVP rig first, pelican-faithful later -- optimize for observability, not iconographic romance
