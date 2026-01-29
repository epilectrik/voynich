# C813: Canonical Phase Ordering

## Constraint

Within lines, phases have a canonical positional ordering:

**LINK (0.476) → KERNEL (0.482) → FL (0.576)**

- LINK is earliest (monitoring setup)
- KERNEL is middle (processing)
- FL is latest (escape if needed)

Statistical significance:
- KERNEL vs FL: p < 0.0001 (KERNEL earlier)
- LINK vs FL: p < 0.0001 (LINK earlier)
- KERNEL vs LINK: p = 0.19 (not significantly different)

## Evidence

Mean positions (0 = line start, 1 = line end):
| Phase | Mean Position | N |
|-------|---------------|---|
| LINK | 0.476 | 3,034 |
| KERNEL | 0.482 | 14,160 |
| FL | 0.576 | 1,078 |
| OTHER | 0.552 | 4,802 |

FL quintile distribution shows strong late-line bias:
| Quintile | FL% |
|----------|-----|
| 0.0-0.2 | 18.0% |
| 0.2-0.4 | 13.4% |
| 0.4-0.6 | 15.7% |
| 0.6-0.8 | 17.9% |
| 0.8-1.0 | **35.1%** |

Most common line-level orderings:
1. LINK → KERNEL: 30.5%
2. KERNEL → LINK: 27.1%
3. LINK → KERNEL → FL: 9.2%
4. KERNEL → FL: 8.2%
5. KERNEL → LINK → FL: 5.9%

## Interpretation

The control loop has spatial structure: monitoring (LINK) tends to occur early, processing (KERNEL) throughout, and escape (FL) late. This supports the model:

```
[LINK monitoring early] → [KERNEL processing] → [FL escape late if needed]
```

However, LINK and KERNEL are interleaved (p=0.19 difference), suggesting monitoring and processing overlap rather than strict sequencing.

## Provenance

- Phase: CONTROL_LOOP_SYNTHESIS
- Script: t4_line_phase_sequence.py
- Related: C360, C807, C809

## Tier

2 (Validated Finding)
