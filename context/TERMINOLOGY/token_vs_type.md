# Token vs Type

**Status:** CLOSED | Fundamental distinction

---

## Definitions

| Term | Definition | Example |
|------|------------|---------|
| **Token** | Single occurrence of a word | "daiin" appearing on f1r line 3 |
| **Type** | Unique word form | "daiin" as a vocabulary entry |

---

## Counts in This Project

| Metric | Value |
|--------|-------|
| Tokens (Currier B) | 75,248 |
| Types (Currier B vocabulary) | 479 |
| Instruction classes | 49 |

---

## Token-Type Ratio (TTR)

TTR = Unique Types / Total Tokens

| System | TTR | Interpretation |
|--------|-----|----------------|
| Currier A | 0.137 | Low = high repetition (registry) |
| Currier B | 0.096 | Lowest = most repetitive (grammar) |
| AZC | 0.285 | Highest = most diverse (labeling) |
| Human Track | ~0.275 | High = compositional variety |

---

## Why This Matters

### Grammar Analysis
- **49 classes** compress **479 types** (9.8x)
- Compression proves formal structure

### Frequency Analysis
- High-frequency types dominate
- 28 prefix+suffix combinations cover 50% of tokens

### Error Analysis
- Damaged tokens are counted once per occurrence
- Recovery patches affect token counts, not type inventory

---

## Hapax Legomena

**Definition:** Types appearing exactly once.

| System | Hapax Rate |
|--------|------------|
| Human Track | 67.5% |
| AZC-unique | 65.9% |
| Currier B | ~15% |

High hapax rate suggests compositional generation, not memorized vocabulary.

---

## Navigation

← [currier_vs_section.md](currier_vs_section.md) | [folio_line_position.md](folio_line_position.md) →
