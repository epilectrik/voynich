# AZC: Astronomical/Zodiac/Cosmological Section Analysis

## Phase Code
`AZC` (Astronomical/Zodiac/Cosmological)

## Discovery Context

During routine audit of Currier A/B coverage, we discovered:

| Classification | Tokens | Percentage |
|----------------|--------|------------|
| Currier B | 23,243 | 61.3% |
| Currier A | 11,415 | 30.1% |
| **NA (unclassified)** | **3,299** | **8.7%** |

**Note (2026-01-16):** Counts corrected after fixing transcriber filtering bug. Values above use PRIMARY (H) transcriber only.

The 8.7% unclassified tokens are concentrated in:
- Section C (Cosmological): 3,298 tokens
- Section Z (Zodiac): 3,184 tokens
- Section A (Astronomical): 2,785 tokens
- Section H (Herbal): 132 tokens (spillover)

These sections were never cleanly classified by Currier's original A/B schema.

---

## Research Question

**What is the grammatical/structural nature of the AZC text?**

Possibilities:
1. **A-LIKE**: Registry/catalog structure (marker prefixes, LINE_ATOMIC, non-sequential)
2. **B-LIKE**: Procedural grammar (49-class coverage, hazard topology, LINK density)
3. **HYBRID**: Mixed characteristics from both A and B
4. **UNIQUE**: Third distinct system with its own structure
5. **TRANSITIONAL**: Intermediate between A and B (evolution or bridging text)

---

## Hypotheses

### H1: AZC Follows B Grammar
AZC text is procedural, following the 49-class grammar.

**Tests:**
- Grammar coverage >= 70% (B threshold)
- Transition validity >= 50%
- Zero hazard violations
- LINK density comparable to B (~6.6%)

### H2: AZC Follows A Patterns
AZC text is registry-like, following Currier A patterns.

**Tests:**
- Marker prefix presence (ch, qo, sh, da, ok, ot, ct, ol)
- LINE_ATOMIC structure (low tokens/line, low inter-line MI)
- POSITION_FREE distribution
- High bigram reuse (>50%)

### H3: AZC is Hybrid
AZC shows measurable characteristics of BOTH A and B.

**Tests:**
- Partial grammar coverage (30-70%)
- Mixed vocabulary (significant overlap with both A and B)
- Intermediate LINK density

### H4: AZC is Unique
AZC has its own distinct structure not explained by A or B.

**Tests:**
- Low grammar coverage (<30%)
- Low marker prefix presence
- High proportion of unique vocabulary
- Distinct morphological patterns

---

## Analysis Plan

### Step 1: Token Inventory
- Extract all 3,299 AZC tokens (H-only)
- Count unique types
- Map to folios
- Calculate basic statistics (TTR, tokens/line)

### Step 2: B-Grammar Test
- Apply 49-class grammar classification
- Calculate coverage percentage
- Test transition validity
- Check hazard violations
- Measure LINK density

### Step 3: A-Pattern Test
- Check marker prefix distribution (ch, qo, sh, da, ok, ot, ct, ol)
- Test LINE_ATOMIC property (tokens/line, inter-line MI)
- Test POSITION_FREE property (JS divergence)
- Calculate bigram reuse rate

### Step 4: Vocabulary Analysis
- Calculate overlap with Currier A vocabulary
- Calculate overlap with Currier B vocabulary
- Identify AZC-exclusive vocabulary
- Compare enrichment ratios

### Step 5: Morphological Analysis
- Apply PREFIX/MIDDLE/SUFFIX decomposition
- Compare component distributions to A and B
- Check for unique components

### Step 6: Structural Analysis
- Analyze line structure
- Check for repetition patterns (like A's multiplicity encoding)
- Look for procedural sequences (like B's transition structure)

### Step 7: Cross-System Relationships
- Do AZC tokens appear in A or B folios?
- Do A/B tokens appear in AZC folios?
- Is there vocabulary bridging between systems?

---

## Success Criteria

| Outcome | Classification | Implication |
|---------|---------------|-------------|
| B-grammar coverage >= 70% | **B-LIKE** | AZC is procedural text |
| A-pattern match >= 5/7 tests | **A-LIKE** | AZC is registry text |
| Both partial (30-70%) | **HYBRID** | AZC bridges A and B |
| Neither matches (<30% each) | **UNIQUE** | Third distinct system |

---

## Output Files

- `AZC_PLAN.md` - This document
- `azc_token_inventory.json` - Complete token inventory
- `azc_grammar_test.json` - B-grammar test results
- `azc_pattern_test.json` - A-pattern test results
- `azc_vocabulary_analysis.json` - Vocabulary overlap analysis
- `azc_morphology_analysis.json` - Morphological decomposition
- `AZC_REPORT.md` - Final analysis report

---

## Scripts

- `archive/scripts/azc_analysis.py` - Main analysis script

---

*Phase AZC initiated.*
