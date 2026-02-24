# C1240 - Paragraph-Final -am Trigger Context

**Tier:** 2 | **Scope:** B | **Phase:** PARAGRAPH_TERMINATION_MECHANICS (Phase 442)

## Statement

Paragraph-final -am has distinctive trigger context: qo prefix absent (0% vs 19.7% non-final), ch enriched 2.81x, al enriched 3.80x, e-MIDDLE enriched 2.53x, preceded by loop-check tokens (aiin/aiiin). Termination is a cooling-verified shutdown, not a processing operation. n=31, small sample.

## Evidence

### Sample sizes

| Context | Count |
|---------|-------|
| Paragraph-final -am | 31 |
| Non-paragraph-final -am | 157 |

### PREFIX differences at -am

| Property | Para-final | Non-final | Ratio |
|----------|-----------|-----------|-------|
| qo prefix | 0% | 19.7% | 0x (absent) |
| ch prefix | enriched | baseline | 2.81x |
| al prefix | enriched | baseline | 3.80x |
| e-MIDDLE | enriched | baseline | 2.53x |

### Top paragraph-final -am words

alkam (3), olkam (3), chctham (2), cheokam (1), charam (1), opalkam (1), lcheam (1), okalam (1), cheam (1), chedam (1)

### Top non-paragraph-final -am words

qokam (19), ram (12), qotam (6), chdam (5), lam (4), olkam (3), daram (3), chedam (3), opam (3), otaram (3)

### Positional and structural differences

| Property | Para-final | Non-final |
|----------|-----------|-----------|
| Mean body position | 0.677 | 0.313 |
| Mean line length | 8.6 tokens | 10.6 tokens |
| Preceded by aiin/aiiin | yes | less frequent |

### Key finding

qo (the processing prefix) is completely absent from paragraph-final -am tokens, while ch (monitoring) and al (monitoring) are strongly enriched. The system switches from active processing to monitoring/cooling before firing the termination signal. The preceding token context includes loop-check tokens (aiin/aiiin), suggesting a check-then-terminate sequence.

## Interpretation

Paragraph-final -am represents a cooling-verified shutdown sequence: the system stops processing (qo disappears), switches to monitoring (ch/al enriched), verifies thermal state (e-MIDDLE enriched), performs a loop check (aiin/aiiin), then fires -am to terminate. This is structurally distinct from mid-paragraph batch-close -am (where qo appears 19.7% of the time), confirming that termination is a deliberate shutdown, not an incidental processing step.

## Caveats

- Small sample (n=31 paragraph-final -am tokens)
- Enrichment ratios should be treated as approximate given sample size
- The specific trigger sequence (monitor -> cool -> loop-check -> am) is inferred from compositional analysis, not from sequential observation within single tokens

## Related constraints

- C1237: -am 5.19x at paragraph-final (established the termination signal)
- C1002: am 88% line-final
- C1234: Iteration two-track system (aiin at penultimate for loop control)
- C1235: Line-final routing architecture

## Provenance

- `phases/PARAGRAPH_TERMINATION_MECHANICS/scripts/termination_analysis.py`
- `phases/PARAGRAPH_TERMINATION_MECHANICS/results/termination_analysis.json`
