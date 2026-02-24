# C1237 - Paragraph Termination by -am

**Tier:** 2 | **Scope:** B | **Phase:** CONTROL_LOOP_ARCHITECTURE (Phase 441)

## Statement

-am is the paragraph termination signal, enriched 5.19x at the paragraph-final token and 29.25x at line-final positions generally. Terminal suffixes (-edy, -am) at line-final are batch-close signals within the paragraph, NOT paragraph termination — they are actually depleted on last body lines (-am 0.53x, -edy 0.58x). Last body lines are shortened (7.3 vs 10.0 tokens), cooling-enriched (e-kernel 60.8% vs 57.0%), with -aiin enriched 2.22x. The paragraph runs at steady state (STOP rate flat, slope -0.82) until -am terminates.

## Evidence

### Dataset

367 last body lines, 1632 non-last body lines from paragraphs with 3+ body lines.

### -am enrichment by position

| Position | Enrichment | Rate |
|----------|------------|------|
| Paragraph-final TOKEN | 5.19x | 9.8% vs 1.9% |
| Line-final (general) | 29.25x | Confirms C1002 |

### Suffix enrichment on last body lines

| Suffix | Enrichment on last line | Interpretation |
|--------|------------------------|----------------|
| -am | 0.53x (depleted) | Within-paragraph batch-close, not termination |
| -edy | 0.58x (depleted) | Mid-paragraph batch-close |
| -aiin | 2.22x (enriched) | Loop return signal |

### STOP enrichment on last body line

| Metric | Value |
|--------|-------|
| STOP enrichment on last line | 0.78x (DEPLETED) |

STOP tokens are depleted, not enriched, on the last body line — the paragraph does not "wind down."

### Last line properties

| Property | Last line | Non-last lines |
|----------|-----------|----------------|
| Length (tokens) | 7.3 | 10.0 |
| e-kernel rate | 60.8% | 57.0% |

### STOP rate by paragraph quintile

| Q1 | Q2 | Q3 | Q4 | Q5 |
|----|----|----|----|----|
| 38.7% | 28.2% | 35.5% | 40.4% | 28.5% |

Slope: -0.82 (flat). The paragraph runs at steady state, not declining toward termination.

### Key observations

1. **-am terminates the paragraph**: 5.19x enrichment at paragraph-final token
2. **Within-paragraph batch-close is distinct from termination**: -am and -edy are depleted on last body lines
3. **Last lines are shortened and cooling-enriched**: Consistent with a final extraction pass
4. **Steady state until termination**: STOP rate flat across paragraph quintiles, slope -0.82
5. **-aiin enriched on last lines**: Loop return is the dominant last-line signal, not closure

## Related constraints

- C1002: am 88% line-final
- C932: Body vocabulary gradient
- C1232: Paragraph tail product signatures
- C1235: Line-final routing architecture (batch-close within paragraph)

## Provenance

- `phases/CONTROL_LOOP_ARCHITECTURE/scripts/stop_vs_ending_test.py`
- `phases/CONTROL_LOOP_ARCHITECTURE/scripts/loop_deep_analysis.py` (Test 2)
- `phases/CONTROL_LOOP_ARCHITECTURE/results/stop_vs_ending.json`
- `phases/CONTROL_LOOP_ARCHITECTURE/results/loop_deep_analysis.json`
