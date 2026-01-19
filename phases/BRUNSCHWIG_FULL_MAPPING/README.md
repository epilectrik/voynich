# BRUNSCHWIG_FULL_MAPPING Phase

## Goal

Extract ALL recipes from Brunschwig's *Liber de arte distillandi* (1500), convert to Voynich-compatible procedural structures, and search for semantic anchors through exhaustive reverse mapping.

## Why This Matters

Previous investigation tested only 3 recipes. With ~200 materials in Brunschwig, comprehensive coverage may reveal patterns that only emerge at scale.

## Source Data

| File | Content |
|------|---------|
| `sources/brunschwig_1500_text.txt` | 47,736 lines OCR'd early modern German |
| `sources/BRUNSCHWIG_1500_REFERENCE.md` | ~200 materials catalogued by category |

## Entry Structure (from OCR)

Each water entry follows this pattern:

```
[German Name] waſſer. Das krut von den kriechiſchen [Greek] genant /
und in arabiſchen [Arabic] / und in latiniſcher zungen [Latin] /
von den tütſchen [common German].

[Physical description - height, leaves, flowers, habitat]

Das beſte teyl und zyt ſyner diſtillierung iſt [best part and time]

A [First use - dosage and indication]
B [Second use]
...
[Up to Z uses per material]
```

## Phase Structure

| Phase | Script | Output |
|-------|--------|--------|
| 1 | `phase1_material_extraction.py` | `data/brunschwig_materials_master.json` |
| 2 | `phase2_procedure_extraction.py` | Procedural skeletons per recipe |
| 3 | `phase3_instruction_mapping.py` | Voynich 49-class mappings |
| 4 | `phase4_grammar_compliance.py` | Compliance validation |
| 5 | `phase5_regime_assignment.py` | REGIME/product type assignments |
| 6 | `phase6_reverse_mapping.py` | Semantic anchor search |

## JSON Schema

See plan file for complete schema. Key fields:
- `recipe_id`, `name_german`, `name_latin`, `name_english`
- `material_source`, `fire_degree`, `predicted_regime`, `predicted_product_type`
- `procedural_steps[]` with `brunschwig_text`, `step_type`, `instruction_class`
- `grammar_compliance` with violation count and status

## Constraints

| Constraint | Requirement |
|------------|-------------|
| **C171** | Zero material encoding - map operations only |
| **C384** | No entry-level A-B coupling |
| **C493** | Grammar embedding - zero violations required |
| **C494** | REGIME_4 = precision, not intensity |

## Success Criteria

- >95% grammar compliance
- REGIME assignment predicts PREFIX profile (p < 0.01)
- Material categories cluster with MIDDLE hierarchy
