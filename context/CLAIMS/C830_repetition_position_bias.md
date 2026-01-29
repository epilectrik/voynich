# C830: Repetition Position Bias

**Status:** VALIDATED | **Tier:** 2 | **Phase:** A_RECORD_B_ROUTING_TOPOLOGY | **Scope:** A

## Finding

Repeated tokens in Currier A are **LATE-biased**, with mean relative position 0.675 (where 0=start, 1=end). FINAL position shows 12x higher repeat rate than INITIAL (4.9% vs 0.4%).

## Key Numbers

| Metric | Value |
|--------|-------|
| Mean position (repeats) | 0.675 |
| Mean position (non-repeats) | 0.494 |
| Position shift | +0.181 toward end |

### Position Distribution

| Position | Repeats | Non-repeats | Repeat Rate |
|----------|---------|-------------|-------------|
| INITIAL (0-0.2) | 11 | 2,526 | 0.4% |
| MEDIAL (0.2-0.8) | 221 | 5,879 | 3.6% |
| FINAL (0.8-1.0) | 125 | 2,412 | 4.9% |

## Interpretation

The late-biased position pattern suggests a **sequential structure** within A records:

```
A Record Flow:
[IDENTITY] → [OPERATIONS] → [PARAMETERS]
  (RI)         (PP once)      (PP repeat)
  early        medial         late
```

This aligns with:

**C422 (DA Articulation):** Line-final position shows special properties - parameters/confirmation follow identity specification.

**C530 (Line-Final Closure):** A records show line-final preference for certain closure functions.

**Functional interpretation:**
1. INITIAL: Establish identity (RI tokens, no repetition)
2. MEDIAL: Specify operations (PP tokens, single occurrence)
3. FINAL: Set parameters (PP tokens, repetition for intensity/count)

## Relationship to Gallows Reset (T8)

Gallows-initial lines show **vocabulary reset** (3.7% vs 5.9% repeat rate from previous line, p=0.047). Combined with late-biased repetition, this suggests:

- Gallows marks START of new operational unit
- Repetition clusters at END of operational unit
- The structure is: [gallows-initial → build vocabulary → repeat for parameters → end]

## Provenance

- Script: `phases/A_RECORD_B_ROUTING_TOPOLOGY/scripts/t9_repeat_function.py`
- Related: C422 (DA articulation), C530 (line-final closure), C827 (paragraph operational unit)
