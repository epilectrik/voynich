# C1426: Line-Initial Specification Profile

**Tier:** 2 (ESTABLISHED)
**Scope:** B, line, position, initial, specification
**Phase:** LINE_LEVEL_ARCHITECTURE (Phase 519)
**Extends:** C1417 (ARTICULATOR line-initial concentration), C557 (daiin line-initial trigger), C931 (PREFIX positional phase mapping)
**Relates to:** C556 (SETUP->WORK->CHECK->CLOSE), C1218 (PREFIX base-modifier grammar), C1287 (paragraph headers MARKING-enriched)

---

## Statement

Line-initial tokens (position 1) show a distinct specification profile: ARTICULATOR 3.93x enriched (17.4% vs 4.4% baseline), STAGING category 1.57x, MARKING 1.42x. PREFIXes with modifier characters are strongly initial-biased: po 7.93x, dch 6.42x, so 6.11x, to 5.15x. Head atom distribution is e-dominant (53.7% vs 40.1% overall). Lines open with cooling/stability specification vocabulary, not thermal execution.

### Line-Initial Enrichment

| Feature | Initial Rate | Baseline | Enrichment |
|---------|-------------|----------|------------|
| ARTICULATOR | 17.36% | 4.41% | 3.93x |
| STAGING | 20.46% | 13.00% | 1.57x |
| MARKING | 11.05% | 7.78% | 1.42x |
| THERMAL | 22.02% | 23.87% | 0.92x |
| CONTAINMENT | 2.27% | 4.82% | 0.47x |

### Top Initial PREFIXes (enrichment vs overall)

| PREFIX | Initial % | Overall % | Enrichment |
|--------|----------|-----------|------------|
| po | 5.22% | 0.66% | 7.93x |
| dch | 3.24% | 0.50% | 6.42x |
| so | 5.59% | 0.91% | 6.11x |
| to | 2.87% | 0.56% | 5.15x |
| tch | 3.84% | 0.83% | 4.61x |
| pch | 5.27% | 1.19% | 4.44x |
| sa | 6.56% | 1.59% | 4.12x |

### Implication

The SPECIFICATION zone (line positions 0-0.2) is distinct from the THERMAL WORK zone. Modifier-initial PREFIXes (p-, d-, s-, t-) concentrate here, validating C1218's dedicated modifiers at POS-0. The opener specifies the operational context for the rest of the line.

---

## Falsification Criteria

1. If THERMAL enrichment at line-initial exceeds 1.2x (would indicate lines begin with execution, not specification)
2. If modifier PREFIXes show uniform distribution across line positions (no initial concentration)

---

## Method

- 2,420 line-initial tokens from Currier B (H-track, labels excluded)
- Enrichment = initial rate / overall rate for each feature
- Morphological decomposition via `scripts/voynich.py` Morphology class
- Category assignment via CategoryClassifier atom plurality vote

**Script:** `phases/LINE_LEVEL_ARCHITECTURE/scripts/line_architecture.py` (T2)
**Results:** `phases/LINE_LEVEL_ARCHITECTURE/results/line_architecture.json`
