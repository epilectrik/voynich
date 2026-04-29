# Phase 640: B Operational Dictionary

**Phase:** 640
**Status:** IN PROGRESS (Sub-Phase 1: Foundation)
**Type:** Compilation + Validation
**Started:** 2026-04-14

## Purpose

Build a complete operational dictionary for the 479 Currier B token types. Each token gets an operational definition — what it instructs a workshop operator to DO in a closed-loop thermal control system.

This is NOT translation. It is assigning operational function (C171 semantic ceiling preserved).

## Key Insight

The vocabulary is a CLOSED 479-word dictionary (C1028: 0.9% of 48,640 possible atom combinations exist). The scribe selected from a fixed vocabulary, not generated tokens from atom rules. Decoding = defining 479 specific words.

## Methodology

### Evidence Sources
1. Atom glosses (C1195, C1394) — compositional readings for all 479
2. 49 instruction classes (C121) — behavioral groupings
3. 8 operational categories (C1250)
4. 41 matched folios with known recipes
5. 3 confirmed folios with line-level decode (f75r, f76r, f84r)
6. Modern chemistry SOPs (validated on f84r)
7. Brunschwig parallel procedures
8. Dark pipeline identifiers (C1939-C1941)
9. Distributional data (position, section, REGIME, co-occurrence)

### Confidence Tiers
| Tier | Label | Criteria |
|------|-------|----------|
| D0 | LOCKED | Atom + recipe + distribution + cross-folio all converge |
| D1 | STRONG | Atom + at least one independent confirmation |
| D2 | COMPOSITIONAL | Atom gloss consistent with category/position, no recipe confirmation |
| D3 | CONTEXTUAL | Distributional context only, atoms ambiguous |
| D4 | SKELETAL | Structural role known, operational meaning underdetermined |
| U | UNRESOLVED | Insufficient evidence |

### Sub-Phases
1. **Foundation** — Schema, baseline data, seed definitions
2. **Compositional expansion** — Atom-driven definitions for all 479
3. **Recipe calibration** — Cross-check against matched folios + Brunschwig + modern SOPs
4. **Distributional validation** — Internal consistency checks
5. **Special populations** — Hapax, folio-unique, dark pipeline
6. **Assembly** — Final compilation, indices, cheat sheet

## Scripts
| Script | Purpose |
|--------|---------|
| `populate_baseline.py` | Structural data for all 479 tokens |
| `seed_definitions.py` | D0/D1 seed entries |

## Results
| File | Purpose |
|------|---------|
| `b_dictionary_v1.json` | Primary dictionary (machine-readable) |
| `b_dictionary_v1.tsv` | Flat table (human-reviewable) |
| `b_dictionary_cheatsheet.md` | Top 100 quick reference |

## Constraints
- Pending: will register after Sub-Phase 4 validation
