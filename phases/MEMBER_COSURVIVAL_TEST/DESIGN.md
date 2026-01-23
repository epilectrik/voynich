# MEMBER_COSURVIVAL_TEST

## Objective

Test which B tokens survive under A record legality constraints using the **strict interpretation**: only MIDDLEs present in the A record itself are legal for B execution.

**Critical Discovery**: The union-based model (AZC expands vocabulary) was WRONG. The strict model (A-record MIDDLEs define legality directly) is correct, validated against C481 (~128-dimensional space) and expert review.

## What This Test Measured

| Question | Answer |
|----------|--------|
| How many B tokens survive per A context? | ~95.9 (20% of 480) |
| How many are filtered out? | ~384 (80%) |
| Does this match C481? | **Yes** (~128-dimensional space) |
| What is the legality model? | Strict: A-record MIDDLEs only |

## Research Questions

1. **Availability breadth**: How many MIDDLEs are legal per context?
2. **Intra-class availability**: How many members are available per class?
3. **Hazard atomicity**: Which hazard classes have atomic (MIDDLE=None) tokens?
4. **PP as activator**: Do PP MIDDLEs activate broader legality fields?

## Key Findings

1. **Strict interpretation correct**: Only A-record MIDDLEs are legal (expert validated)
2. **80% filtering**: ~384 of 480 B tokens become illegal per A context
3. **~96-dimensional space**: Matches C481's ~128-dimensional prediction
4. Class 11 (`ol`) is **ATOMIC** (MIDDLE=None)
5. Specification incompatibility: 98.67% of MIDDLE pairs never co-occur in same A record

## What This Test Does NOT Measure

- Grammar constraints or forbidden transitions
- Semantic interpretation of instructions
- Why specific MIDDLEs are specified together

## Scripts

| Script | Purpose | Tests |
|--------|---------|-------|
| `compute_member_survivors.py` | Token-level availability per A record | Availability |
| `intraclass_pruning.py` | Per-class availability profiles | Availability |
| `middle_cosurvival_matrix.py` | MIDDLE availability co-occurrence | Availability (negative control) |
| `hazard_suppression.py` | Hazard class atomicity verification | Token structure |
| `pp_role_analysis.py` | PP legality activation analysis | Availability |
| **`specification_compatibility.py`** | **MIDDLE co-occurrence within A records** | **Specification (C475)** |

## Epistemic Status

- **Tier 3 characterization** (not extending Tier 0-2)
- **Expert validated**: Strict interpretation consistent with frozen architecture
- Validates: C481 (~128-dim space), C475 (98.67% incompatibility), C469 (categorical resolution)
- Corrects: Union-based model was WRONG (contradicted multiple Tier 2 constraints)

## Results

See [results/FINDINGS.md](results/FINDINGS.md) for detailed analysis with methodological corrections.
