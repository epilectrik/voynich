# C878 - Section Program Variation

**Tier:** 2 | **Scope:** B | **Phase:** B_CONTROL_FLOW_SEMANTICS

## Statement

Sections show distinct program profiles: BIO has highest EN rate (40.1%, intensive processing), HERBAL_B has highest FL (6.1%) and FQ (16.3%, state-heavy). FL/FQ ratio is similar across sections (~0.37).

## Evidence

| Section | EN | FL | FQ | FL/FQ |
|---------|-----|-----|-----|-------|
| HERBAL_B | 22.8% | 6.1% | 16.3% | 0.37 |
| BIO | 40.1% | 3.9% | 10.2% | 0.38 |
| RECIPE_B | 29.6% | 4.6% | 12.7% | 0.36 |

Kernel rates similar across sections (k: 32-33%, h: 38-41%, e: 37-48%).

## Interpretation

- BIO = intensive processing programs
- HERBAL_B = state-heavy, more escape needed
- Similar stability (FL/FQ ratio) across sections
- Sections encode different process complexities, not different processes

## Provenance

- `phases/B_CONTROL_FLOW_SEMANTICS/scripts/06_section_program_profiles.py`
- `phases/B_CONTROL_FLOW_SEMANTICS/results/section_program_profiles.json`
- Related: C552, C860 (section organization)
