# C888 - Section-Specific Registry Architecture

**Tier:** 2 (structure) / 3 (interpretation) | **Scope:** A | **Phase:** CURRIER_A_STRUCTURE_V2

## Statement

Currier A sections (H, P, T) have distinct registry architectures, not just different content:

1. **WITH-RI/WITHOUT-RI ratio** differs significantly between sections
2. **WITHOUT-RI function** varies by section (cross-referencing vs safety protocols)
3. **MIDDLE vocabulary** is largely section-exclusive (Jaccard ~0.2)

---

## C888.a: WITH-RI Ratio Differentiation (2026-01-30)

P section uses significantly more WITH-RI paragraphs than H section:

| Section | WITH-RI | WITHOUT-RI | % WITH-RI |
|---------|---------|------------|-----------|
| H | 114 | 118 | 49.1% |
| P | 40 | 22 | **64.5%** |
| T | 11 | 12 | 47.8% |

**Chi-square (H vs P):** chi2=4.04, p=0.044

**Interpretation:**
- P = Material specification focus (high WITH-RI for identification)
- H = Cross-reference balance (even WITH/WITHOUT ratio)
- T = Underpowered (n=23 paragraphs)

**Provenance:** `scripts/section_architecture_comparison.py`

---

## C888.b: WITHOUT-RI Function by Section

WITHOUT-RI paragraphs serve different functions in different sections, evidenced by distinct PP PREFIX profiles:

| Section | % WITHOUT-RI | Distinctive PREFIX | Enrichment |
|---------|--------------|-------------------|------------|
| H (Herbal) | 48.7% | ct (LINKER) | 3.87x |
| P (Pharmaceutical) | 20.8% | qo, ok, ol | 0.35-0.63x (depleted ct) |

## Evidence

From CURRIER_A_STRUCTURE_V2 tests 20, 23:

**Section Distribution:**

| Section | Folios | WITH-RI | WITHOUT-RI | % WITHOUT |
|---------|--------|---------|------------|-----------|
| H | 95 | 101 | 96 | **48.7%** |
| P | 16 | 103 | 27 | 20.8% |
| T | 3 | 11 | 4 | 26.7% |

**PP PREFIX Profile Comparison (WITHOUT-RI only):**

| Prefix | Section H | Section P | H/P Ratio | Function |
|--------|-----------|-----------|-----------|----------|
| ct | 6.6% | 1.7% | **3.87x** | LINKER |
| qo | 13.2% | 21.1% | 0.63x | ESCAPE |
| ok | 5.4% | 15.5% | 0.35x | AUXILIARY |
| ol | 1.7% | 5.5% | 0.31x | LINK/MONITOR |

## Structural Interpretation (Tier 2)

The PREFIX enrichment patterns are measurable facts:
- Section H WITHOUT-RI: ct-enriched (3.87x)
- Section P WITHOUT-RI: qo/ok/ol-enriched, ct-depleted

## Functional Interpretation (Tier 3)

The enrichment patterns suggest different purposes:
- **Section H:** Cross-referencing/indexing between plant materials (ct-LINKER vocabulary)
- **Section P:** Safety and recovery protocols (ESCAPE + AUXILIARY + MONITOR vocabulary)

This aligns with section names:
- Herbal section needs material cross-referencing
- Pharmaceutical section needs hazard management

---

## C888.c: Section Vocabulary Distinctiveness

MIDDLE vocabulary overlap between sections is low:

| Comparison | Jaccard | Shared MIDDLEs |
|------------|---------|----------------|
| H-P | 0.209 | 192 |
| H-T | 0.151 | 127 |
| P-T | 0.198 | 99 |

**Section-exclusive MIDDLEs:**
- H: 513 (69% of H vocabulary)
- P: 171 (46% of P vocabulary)
- T: 93 (41% of T vocabulary)

This supports C260 (section vocabulary isolation) with paragraph-level quantification.

---

## C888.d: Section-Distinctive PREFIXes

Beyond WITHOUT-RI function, each section has enriched PREFIXes (>2x vs other sections):

| Section | Enriched PREFIXes | Pattern |
|---------|-------------------|---------|
| H | kch (7.4x), sch (5.4x), dch (4.4x), tch (4.1x), ct (2.6x) | Gallows-ch compounds, cross-ref |
| P | or (4.2x), lch (2.7x), ol (2.2x) | LINK prefixes |
| T | al (17.9x), ar (6.9x), ta (6.5x), ka (3.9x) | Highly distinctive |

**Provenance:** `scripts/section_architecture_comparison.py`

---

## Provenance

- `phases/CURRIER_A_STRUCTURE_V2/results/section_distribution.json`
- `phases/CURRIER_A_STRUCTURE_V2/results/section_subtype_interaction.json`
- `results/section_architecture_comparison.json`
- Related: C849 (A paragraph section profile), C260 (section vocabulary isolation)

## Status

CONFIRMED (structure) - WITH-RI ratio, PREFIX enrichment, vocabulary overlap measured.
SPECULATIVE (interpretation) - Functional labels (cross-ref vs safety) require validation.
