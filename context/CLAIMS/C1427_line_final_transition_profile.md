# C1427: Line-Final Transition Profile

**Tier:** 2 (ESTABLISHED)
**Scope:** B, line, position, final, transition, closure
**Phase:** LINE_LEVEL_ARCHITECTURE (Phase 519)
**Extends:** C539 (LATE prefix morphological class), C1237 (paragraph termination by -am), C1235 (line-final routing architecture)
**Relates to:** C556 (SETUP->WORK->CHECK->CLOSE), C562 (FLOW role structure), C1302 (BARE anti-thermal)

---

## Statement

Line-final tokens show a distinct transition/closure profile: TRANSITION category 1.63x enriched (24.5% vs 15.0%), THERMAL 0.56x depleted (13.4% vs 23.9%). Terminal atom m jumps to 11.8% from 0.06% at position 1 (196x increase). Suffix -m 9.54x enriched at line-final, -am 7.83x. PREFIXes ar/al/or are 3.4-4.6x enriched. Lines close with state-change/closure vocabulary, not thermal operations.

### Line-Final Enrichment

| Feature | Final Rate | Baseline | Enrichment |
|---------|-----------|----------|------------|
| TRANSITION | 24.51% | 15.02% | 1.63x |
| CONTAINMENT | 6.08% | 4.82% | 1.26x |
| MARKING | 9.57% | 7.78% | 1.23x |
| THERMAL | 13.39% | 23.87% | 0.56x |

### Top Final PREFIXes (enrichment vs overall)

| PREFIX | Final % | Overall % | Enrichment |
|--------|--------|-----------|------------|
| ar | 3.59% | 0.79% | 4.56x |
| al | 3.59% | 1.00% | 3.59x |
| or | 3.37% | 1.00% | 3.37x |
| ko | 0.83% | 0.42% | 1.99x |
| ol | 9.77% | 5.06% | 1.93x |

### Terminal Atom m Concentration

| Position | m-terminal % |
|----------|-------------|
| Pos 1 | 0.06% |
| Q0 | 0.17% |
| Q1 | 0.23% |
| Q2 | 0.48% |
| Q3 | 0.71% |
| Q4 | 5.67% |
| Final token | 11.82% |

### Implication

The CLOSURE zone (line positions 0.7-1.0) is TRANSITION/FLOW-dominant with THERMAL depleted. The m-terminal gradient is the most extreme positional effect in the entire line. The pattern: specification opens -> thermal work -> state-change closure.

---

## Falsification Criteria

1. If THERMAL enrichment at line-final exceeds 1.0x (would indicate thermal work extends to line end)
2. If m-terminal concentration at line-final drops below 5x enrichment

---

## Method

- 2,420 line-final tokens from Currier B (H-track, labels excluded)
- Enrichment = final rate / overall rate
- Terminal atom extraction from MIDDLE morphology

**Script:** `phases/LINE_LEVEL_ARCHITECTURE/scripts/line_architecture.py` (T3)
**Results:** `phases/LINE_LEVEL_ARCHITECTURE/results/line_architecture.json`
