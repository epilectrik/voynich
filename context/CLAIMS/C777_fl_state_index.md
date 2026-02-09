# C777: FL State Index

**Tier:** 2
**Scope:** B
**Phase:** FL_PRIMITIVE_ARCHITECTURE

> **Terminology Note:** "FL" here refers to the MIDDLE-based material state taxonomy
> (~25% of tokens), NOT the FLOW_OPERATOR 49-class role (classes 7/30/38/40, 4.7% of tokens).
> See [TERMINOLOGY/fl_disambiguation.md](../TERMINOLOGY/fl_disambiguation.md).

## Constraint

FL MIDDLEs function as state indices marking material progression through a process. The 17 FL MIDDLEs show strong positional differentiation (range 0.64) with 'i'-forms at process start and 'y'-forms at process end.

## Evidence

From t5_fl_index_test.py:

**FL MIDDLE Positional Gradient:**

| MIDDLE | Mean Position | Stage |
|--------|---------------|-------|
| 'ii'   | 0.299         | INITIAL |
| 'i'    | 0.345         | INITIAL |
| 'in'   | 0.421         | EARLY |
| 'r'    | 0.507         | MEDIAL |
| 'ar'   | 0.545         | MEDIAL |
| 'al'   | 0.606         | LATE |
| 'l'    | 0.618         | LATE |
| 'ol'   | 0.643         | LATE |
| 'o'    | 0.751         | FINAL |
| 'ly'   | 0.785         | FINAL |
| 'am'   | 0.802         | FINAL |
| 'm'    | 0.861         | TERMINAL |
| 'dy'   | 0.908         | TERMINAL |
| 'ry'   | 0.913         | TERMINAL |
| 'y'    | 0.942         | TERMINAL |

**Position Statistics:**
- Range across FL MIDDLEs: 0.643 (64% of line span)
- Std across FL MIDDLEs: 0.203

**Character Split:**
- Early FL (pos < 0.4): 'ii', 'i' - uses only character 'i'
- Late FL (pos > 0.6): 'al', 'l', 'ol', 'o', 'ly', 'am', 'm', 'dy', 'ry', 'y' - uses a, d, l, m, o, r, y

**State Transitions:**
- Self-transition rate: 23% (same MIDDLE follows same MIDDLE)
- State change rate: 77% (MIDDLE changes when FL follows FL)
- Most common transition: 'ar' -> 'al' (29 occurrences)

## Interpretation

FL MIDDLEs are state labels, not operators:

```
PROCESS START                              PROCESS END
    |                                           |
    v                                           v
  [i/ii/in] --> [r/ar] --> [al/l/ol] --> [o/ly/m] --> [y/ry/dy]
    0.30         0.51        0.61          0.78         0.92
```

The character composition encodes process stage:
- 'i' = initial marker
- Consonants (r, l, n, m) = intermediate markers
- 'y' = terminal marker

FL doesn't transform material - it **indexes where material is** in the transformation process. The kernel-modulated roles (EN, CC) do the actual transformations between FL state markers.

## Provenance

- t5_fl_index_test.json: position_range = 0.643, fl_middle_stats
- Relates to: C770-C776 (FL primitive architecture), C772 (FL as substrate)

## Status

CONFIRMED - FL MIDDLEs show strong positional differentiation consistent with state indexing.
