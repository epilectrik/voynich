# C905: FL_TERMINAL Early-Line Concentration

**Status:** VALIDATED
**Tier:** 2 (Structural Inference)
**Scope:** B-internal
**Phase:** B_PARAGRAPH_POSITION_STRUCTURE

## Claim

TERMINAL FL vocabulary (suffixes: y, aly, am, dy) concentrates in **early folio lines** rather than late lines, serving as **input-state declaration** rather than output-completion marking. When B folios are divided into thirds by line position, early lines show significantly higher TERMINAL FL rates than late lines.

Same-section folios share TERMINAL FL vocabulary (1.30x Jaccard, p<0.0001), reflecting **domain coherence** rather than procedural chaining.

## Evidence

**Test 1: Folio-level gradient** (Script 07)

| Metric | Value |
|--------|-------|
| Folios analyzed | 82 |
| Mean TERMINAL FL gradient (late - early) | **-3.7%** |
| Folios with decrease (early > late) | 55 (67%) |
| Folios with increase (late > early) | 27 (33%) |
| One-sample t-test | t = -3.62, **p = 0.0005** |

**Test 2: Cross-folio vocabulary echo** (Script 08)

| Metric | Value |
|--------|-------|
| Late→Early echo vs null model | z = -0.61 (NOT significant) |
| Same-section folio pairs Jaccard | 0.0308 |
| Different-section folio pairs Jaccard | 0.0237 |
| Section effect | t = 5.84, **p < 0.0001** |

The cross-folio echo test ruled out procedural chaining (folio X output → folio Y input). Instead, section-level vocabulary sharing reflects domain coherence.

## Interpretation

**Key insight:** TERMINAL FL is **stable-state vocabulary**, not completion marking.

| Old interpretation | Refined interpretation |
|---|---|
| TERMINAL = completion marking | TERMINAL = **stable-state descriptor** |
| Appears at procedure end | Describes stable material states |
| Output-focused | **State-descriptor** (inputs OR outputs) |

A material in a "terminal" state (-y, -am, -aly suffixes per C777) could be:
- The **output** of a previous procedure
- The **input** to the current procedure
- Same physical state, different procedural role

Early folio lines **declare what state the input material is in** using vocabulary that describes stable/completed states. This aligns with the header function established in C840.

## Non-Conflict with C777

C777 (FL STATE INDEX) and C905 operate at **orthogonal levels**:

| Constraint | Level | Finding |
|------------|-------|---------|
| C777 | Within-line position | TERMINAL FL at line-final positions |
| C905 | Folio-level position | TERMINAL FL in early folio lines |

Both are true: TERMINAL FL marks line-final positions (C777), and lines containing TERMINAL FL cluster in early folio regions (C905).

## Related Constraints

- **C777:** FL STATE INDEX - within-line positioning (orthogonal, non-conflicting)
- **C840:** Line 1 = HEADER (44.9% HT) - early lines serve header/declaration function
- **C897:** FL MIDDLEs mark states, not necessarily endpoints
- **C671:** Vocabulary introduced early, reused late (TERMINAL FL fits this pattern)
- **C870:** Line-1 has folio-specific vocabulary for identification
- **C878, C860:** Section specialization explains domain coherence

## Contrast

- **AX prefix:** No significant gradient (p = 0.52)
- **CHSH prefix:** No significant gradient (p = 0.93)
- **Vocabulary overlap (early vs late):** Jaccard = 0.305 (moderate)
- **Cross-folio chaining:** NOT supported (z = -0.61)

## Provenance

- **Phase:** B_PARAGRAPH_POSITION_STRUCTURE
- **Scripts:**
  - `phases/B_PARAGRAPH_POSITION_STRUCTURE/scripts/07_folio_level_analysis.py`
  - `phases/B_PARAGRAPH_POSITION_STRUCTURE/scripts/08_cross_folio_terminal_echo.py`
- **Results:**
  - `phases/B_PARAGRAPH_POSITION_STRUCTURE/results/07_folio_level_analysis.json`
  - `phases/B_PARAGRAPH_POSITION_STRUCTURE/results/08_cross_folio_terminal_echo.json`
- **Date:** 2026-02-03
- **Expert validation:** Confirmed non-conflict with C777, interpretation as input-state declaration
