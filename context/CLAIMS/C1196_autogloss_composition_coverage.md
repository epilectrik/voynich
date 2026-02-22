# C1196: Autogloss Composition Coverage

**Tier:** 2
**Scope:** B
**Phase:** ATOM_GLOSS_AUDIT (Phase 424)
**Depends on:** C1190 (MIDDLE additive composition), C1195 (atom gloss confidence tiers)

## Constraint

1144 of 1273 compound MIDDLEs (89.9%) can be auto-glossed by composing validated atom glosses. The remaining 58 (4.6%) contain q (no atom gloss; qo-form prefix variant). 71 compounds already had manual glosses.

Autogloss confidence distribution (inherits weakest atom tier):

| Confidence | Count | Fraction | Meaning |
|------------|-------|----------|---------|
| LOCKED | 72 | 6.3% | All atoms LOCKED (e.g., ke → heat-cool = "sustained heat") |
| SOLID | 86 | 7.5% | Weakest atom is SOLID |
| PLAUSIBLE | 289 | 25.3% | Weakest atom is PLAUSIBLE |
| WEAK | 768 | 67.1% | Contains o, l, or r (generic atoms) |

## Evidence

The autogloss system decomposes each compound MIDDLE into its constituent atoms, joins atom glosses with "-", and assigns confidence equal to the weakest atom in the compound.

Cross-check against 71 existing manual glosses shows additive composition explains most compound glosses:
- ke(heat-cool) = "sustained heat" — composition captures the semantic
- ed(cool-mark) = "discharge" — plausible as cool+product
- ol(work-frame) = "continue" — generic but directionally correct
- ain(yield-iterate-halt) = "intake" — yield+iterate+halt maps to intake process

The high WEAK count (67.1%) is driven by three generic atoms (o, l, r) appearing in many compounds. Refining these three glosses would upgrade ~768 compounds.

## Falsification

Would be falsified if spot-checking reveals systematic failures where autogloss contradicts the operational meaning of compounds (not just label refinement, but wrong direction).

## Provenance

- `phases/ATOM_GLOSS_AUDIT/scripts/generate_autogloss.py` — autogloss generator
- `phases/ATOM_GLOSS_AUDIT/results/autogloss_review.txt` — full review file for spot-checking
- `phases/ATOM_GLOSS_AUDIT/results/autogloss_summary.json` — summary statistics
- `data/middle_dictionary.json` v3.0 — updated dictionary with autogloss fields
