# C763 - f57v R2 Single-Character Ring Anomaly

**Tier:** 2 | **Status:** CLOSED | **Scope:** AZC

## Statement

Folio f57v (cosmological diagram) ring R2 is 100% single characters with no morphological structure, unlike all other AZC text. The sequence shows a repeating ~27-character pattern with systematic single-letter variations (p/f substitution).

## Data

### Ring Comparison

| Ring | Tokens | Single-char % | Has Morphology |
|------|--------|---------------|----------------|
| R1 | 50 | 26% | Yes (ok-, da-, so-) |
| **R2** | **50** | **100%** | **No** |
| R3 | 29 | 28% | Yes (da-, ot-, ok-) |
| R4 | 29 | 72% | Partial |

### R2 Sequence (asterisks removed)

```
o d r x k k p t r y c o l c y r t l k k x r d p r o c l d r x k k f t r y c o y r t f k x r d l m n
```

**50 single characters. Zero multi-character Voynichese words.**

### Repeating Structure

- `d r x k k` at positions 1, 28 (distance 27)
- `t r y c o` at positions 7, 34 (distance 27)
- Two variants: `x k k p t r y c o` vs `x k k f t r y c o` (p→f substitution)
- Unique ending: `m n` (only occurrence of these chars)

### Character Frequency

| Char | Count | Char | Count |
|------|-------|------|-------|
| r | 9 | l | 4 |
| k | 7 | p | 2 |
| o | 4 | f | 2 |
| d | 4 | m | 1 |
| x | 4 | n | 1 |
| t | 4 | | |
| y | 4 | | |
| c | 4 | | |

## Structural Interpretation

1. **R2 is non-Voynichese.** No PREFIX/MIDDLE/SUFFIX structure. No gallows. No standard word forms.

2. **Boundary rings vs content rings.** R1 and R3 (26-28% single chars) contain normal Voynichese with standard morphology. R2 and R4 (72-100% single chars) are structurally distinct.

3. **Repeating pattern suggests encoding.** The ~27-char period with p/f variation is not random. Could be:
   - Position markers around the ring (like clock positions)
   - Cipher key or alphabet reference
   - Index to other content

4. **Unique terminators.** Characters `m` and `n` appear only at the sequence end, potentially marking ring completion.

## Contrast with Other Single-Char Sequences

| Folio | System | Location | Function |
|-------|--------|----------|----------|
| f49v | Currier A | L (margin) | Instructional (C497) |
| f76r | Currier B | L (margin) | Control sentinels (C497) |
| **f57v** | **AZC** | **R2 (ring)** | **Unknown - diagram integrated** |

Unlike f49v/f76r margin labels, f57v R2 is **part of the diagram structure itself**.

## Cross-References

- C430 (AZC Bifurcation - f57v in Zodiac family)
- C762 (Cross-System Single-Char Primitives)
- C497 (f49v/f76r single-char functions)

## Source

AZC_FOLIO_DIFFERENTIATION phase, f57v_ring_analysis
