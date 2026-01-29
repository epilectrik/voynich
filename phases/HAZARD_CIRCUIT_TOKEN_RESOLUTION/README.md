# HAZARD_CIRCUIT_TOKEN_RESOLUTION

**Phase status:** COMPLETE | **Constraints:** C625-C627 | **Date:** 2026-01-26

## Objective

Determine whether the hazard circuit's directionality (C601) explains which specific token pairs are forbidden, and whether the two-lane architecture (C600, C606-C608) predicts hazard participation at the token or MIDDLE level.

## Key Findings

1. **Circuit direction explains 75% of classifiable forbidden pairs** (C625). Six of 12 classifiable pairs are reverse-circuit flows (EN->FQ, EN->FL, FQ->FL); 3 are within-subgroup restrictions. Fisher's p=0.193 (trending, not significant at n=12).

2. **Two-lane architecture does NOT predict hazard** (C626, null finding). Forbidden-exclusive MIDDLEs are in neither lane vocabulary (4/5 = NEITHER). CC trigger shows no forbidden/non-forbidden difference (Fisher p=0.866). QO contexts contain 55% more hazard bigrams than CHSH contexts.

3. **Forbidden pairs are directionally asymmetric, not frequency-biased** (C627). Zero reciprocal forbidden pairs (0/17 both-direction). Mean frequency rank 0.562 vs 0.500 expected. FQ_CLOSER boundary tokens account for all 3 unexplained classifiable pairs.

4. **Five forbidden pairs involve 4 tokens outside the 49-class system** (c, ee, he, t). Two (ee, he) have zero Currier B occurrences -- structurally trivial.

## Scripts

| Script | Sections | Output |
|--------|----------|--------|
| `hazard_circuit_token_mapping.py` | Sub-group classification, direction analysis, traffic volume, unclassified tokens | `results/hazard_circuit_token_mapping.json` |
| `lane_middle_discrimination.py` | MIDDLE vocabulary, CC trigger, lane activation, lane x direction | `results/lane_middle_discrimination.json` |
| `forbidden_pair_selectivity.py` | Within-pair discrimination, frequency, reciprocal pairs, predictive summary | `results/forbidden_pair_selectivity.json` |

## Verdict

The hazard system is a **directional, token-specific lookup table** partially structured by circuit topology (75%) with a secondary FQ_CLOSER boundary component (25%). It is not frequency-driven, not morphologically predictable, and not lane-dependent. The two-lane model operates at the routing level, not the hazard level.

## Data Dependencies

- `phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json`
- `phases/15-20_kernel_grammar/phase18a_forbidden_inventory.json`
- `scripts/voynich.py`
