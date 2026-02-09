# C899 - A-B Within-Line Positional Correspondence

**Tier:** 2 (Structural) | **Scope:** A↔B | **Phase:** A_PP_INTERNAL_STRUCTURE

## Statement

PP MIDDLEs have consistent within-line positional roles across Currier A and Currier B. MIDDLEs that appear late within A lines also appear late within B lines, and vice versa. This is a property of the shared vocabulary grammar, not a record-to-program mapping.

| Metric | Value | Significance |
|--------|-------|--------------|
| Pearson r | 0.654 | p < 0.0001 |
| Spearman rho | 0.576 | p = 0.0001 |
| Zone preservation | 92.5% | vs 33% by chance |
| Sample | 40 MIDDLEs | n ≥ 20 in each system |

---

## What Was Measured

- **A position:** Normalized position within A LINES (0 = first token, 1 = last token)
- **B position:** Normalized position within B LINES (0 = first token, 1 = last token)
- **Correlation:** Mean A position vs mean B position for each shared MIDDLE

This measures **within-line positional tendencies**, not relationships between A records and B programs.

---

## C899.a: Aggregation Level

The correspondence is a **corpus-level grammar property**, not a folio-level operational rule:

| Level | Correlation | Interpretation |
|-------|-------------|----------------|
| Corpus | r = 0.654 | Strong - vocabulary items have consistent roles |
| Folio (mean) | r = 0.149 | Weak - individual folios don't predict each other |

Only 7.3% of individual A folios show significant positive correlation with B positions. The pattern emerges from averaging across the corpus, not from folio-to-folio correspondence.

This differs from C885 (vocabulary correspondence), which operates at folio level.

---

## C899.b: Positional Role Examples

| MIDDLE | A within-line | B within-line | Role |
|--------|---------------|---------------|------|
| or | 0.354 | 0.485 | EARLY-MID in both |
| ol | 0.470 | 0.490 | MIDDLE in both |
| m | 0.848 | 0.851 | LATE in both |
| am | 0.787 | 0.923 | LATE in both |

These MIDDLEs maintain their positional role (early, middle, late) regardless of which system they appear in.

---

## C899.c: Hub Positional Stability

All 5 network hubs from C898.b maintain MIDDLE-zone position in both systems:

| Hub | A position | B position | Zone |
|-----|------------|------------|------|
| iin | 0.577 | 0.393 | MIDDLE |
| ol | 0.470 | 0.490 | MIDDLE |
| s | 0.616 | 0.577 | MIDDLE |
| or | 0.354 | 0.485 | MIDDLE |
| y | 0.543 | 0.642 | MIDDLE |

Hubs are grammatically MIDDLE-position elements in both systems.

---

## C899.d: Cross-Folio Variance

MIDDLEs show moderate variance in position across A folios (mean std = 0.153), indicating positions are tendencies rather than fixed rules:

| Stability | MIDDLEs | Cross-folio std |
|-----------|---------|-----------------|
| Most stable | m, y, e, ey | 0.095 - 0.128 |
| Most variable | in, ar, aiin, or | 0.185 - 0.215 |

---

## Interpretation

Position within a line carries **consistent semantic meaning** across A and B:

- LATE-position MIDDLEs (m, am) → closure/completion function
- EARLY-position MIDDLEs (or) → opening/initiation function
- MIDDLE-position MIDDLEs (hubs) → central processing/connection function

This is a **shared grammar property**: vocabulary items have positional roles baked into them, maintained across both systems. It is NOT a mapping where specific A records predict specific B program execution order.

---

## What This Is NOT

- NOT: "A folio structure predicts B program structure"
- NOT: "Reading an A line left-to-right predicts B execution order"
- NOT: A folio-level operational correspondence (that's C885 for vocabulary)

The correspondence is about vocabulary items carrying consistent within-line positional semantics across systems.

---

## Relationship to Other Constraints

| Constraint | Relationship |
|------------|--------------|
| C234 | **COMPATIBLE** - Position-freedom applies to token CLASS; C899 describes MIDDLE-level tendencies |
| C885 | **DISTINCT** - C885 is folio-level vocabulary correspondence; C899 is corpus-level positional correspondence |
| C898 | **EXTENDS** - A's PP positional structure uses same vocabulary roles as B |
| C816 | **CONSISTENT** - B's canonical phase ordering reflects same positional semantics |

---

## Methodological Notes

- Sample: 40 MIDDLEs with n ≥ 20 occurrences in both Currier A (PP only) and Currier B
- Positions normalized within lines (0 = first token, 1 = last token)
- Lines with < 2 tokens excluded
- A positions restricted to PP tokens (RI prefixes excluded)
- Folio-level analysis: 55 A folios tested, mean r = 0.149

---

## Provenance

- `phases/A_PP_INTERNAL_STRUCTURE/results/a_b_positional_mapping.json`
- `phases/A_PP_INTERNAL_STRUCTURE/results/positional_correspondence_level.json`

## Status

CONFIRMED - Strong corpus-level correlation with clear aggregation-level characterization.
