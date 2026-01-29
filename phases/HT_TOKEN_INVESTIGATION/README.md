# HT_TOKEN_INVESTIGATION Phase

**Question:** What are HT (Human Track / Unclassified) tokens? Why is Line 1 enriched for HT?

**Answer:** HT tokens are MATERIAL IDENTIFICATION vocabulary that concentrates in paragraph Line 1 (the "header"). They are highly folio-specific, representing names and identifiers unique to each material/procedure.

---

## Key Statistics

| Metric | Value |
|--------|-------|
| Total HT tokens | 7,042 (30.5% of B) |
| Unique HT vocabulary | 4,421 types |
| Line-1 HT rate | ~47% |
| Later-line HT rate | ~27% |
| Line-1 enrichment | 1.74x |
| Folio-singleton rate | 85.9% |
| Mixed lines (HT + PP) | 89.4% |

---

## Key Discoveries

### 1. HT is Line-Positional (C740)

Line 1 of each paragraph has 47% HT vs 27% elsewhere. This 1.74x enrichment is universal across all gallows types:

| Gallows | Line-1 HT | Later HT | Ratio |
|---------|-----------|----------|-------|
| p | 46.7% | 25.7% | 1.82x |
| t | 43.7% | 27.1% | 1.62x |
| k | 47.8% | 23.3% | 2.05x |
| f | 51.9% | 34.4% | 1.51x |

### 2. HT is Folio-Specific (C741)

86% of Line-1 HT tokens appear in only ONE folio. 1,229 tokens are both folio-unique AND Line-1 exclusive. This is identification vocabulary unique to each material.

### 3. HT Cooccurs with Grammar (C742)

89% of lines mix HT with classified (PP) tokens. Only 2.6% of lines are HT-only. HT is integrated with the instruction grammar, not isolated.

### 4. HT Avoids Control Zones (C743)

- HT ENRICHED on lines with FL (flow control)
- HT DEPLETED on lines with CC (core control) and FQ (frequent operators)
- HT appears in "setup/identification" zones, not "execution" zones

### 5. Line-1 HT is NOT the Gallows (C744)

- Only 19.5% of Line-1 HT IS the paragraph opener
- Only 25.5% of Line-1 HT is gallows-initial
- The HT enrichment is positions 2, 3, 4... not just position 1

### 6. F-Initial Paragraphs are HT-Rich (C745)

f-initial paragraphs have 38.6% HT (vs 30% for p). f = folio opener, front-biased. F-paragraphs mark folio-level identification/setup.

---

## Model

```
Line 1 = HEADER
  [Gallows] [HT: Material ID] [HT: Variant] [AX_INIT]
     |            |                |            |
  Procedure    "What?"         "Which one?"   Scaffold
    type       Material          State        Initialize

Later Lines = BODY
  [EN: Energy] [CC: Control] [FQ: Ops] [FL: Flow]
       |            |            |          |
    Modulate     Bound        Execute    Direct
      energy     blocks        work       flow
```

**HT is the "human" layer:**
- Names, identifiers, material-specific markers
- Varies between folios (different materials)
- Concentrates in headers (identification)
- Mixes with grammar (integrated system)

**PP is the "program" layer:**
- Shared instruction vocabulary
- Same across folios (common grammar)
- Concentrates in body (execution)
- Encodes control logic

---

## Scripts

| Script | Purpose | Key Finding |
|--------|---------|-------------|
| 00 | HT Census | 30.5% HT, 4421 unique, 74% singletons |
| 01 | Gallows Connection | f-initial 38.6% HT, Line-1 universal enrichment |
| 02 | Line-1 Identity | 86% folio-singletons, 1229 Line-1-only |
| 03 | C475 Compliance | 89% mixed lines, avoids CC/FQ |
| 04 | Synthesis | Material identification vocabulary |

---

## Section Variation

| Section | HT Rate | Interpretation |
|---------|---------|----------------|
| PHARMA | 40.1% | Most HT - complex material identification |
| RECIPE_B | 34.1% | High HT |
| HERBAL_B | 32.3% | Moderate HT |
| OTHER | 30.1% | Average |
| BIO | 22.3% | Lowest HT - simpler identification? |

---

## Constraints

### Pre-existing (validated)

| # | Name | Tier | Finding |
|---|------|------|---------|
| C740 | HT-UN Population Identity | 2 | HT = UN, same population (4,421 types, 7,042 occ) |
| C747 | Line-1 HT Enrichment | 0 | 50.2% vs 29.8%, +20.3pp, d=0.99 |
| C748 | Line-1 Step Function | 0 | Enrichment confined to single opening line |
| C851 | B Paragraph HT Variance | 2 | Paragraph Line-1 46.5% vs body 23.7% |

### New (this phase)

| # | Name | Tier | Finding |
|---|------|------|---------|
| C870 | Line-1 HT Folio Specificity | 2 | 86% folio-singletons, 1,229 Line-1-only |
| C871 | HT Role Cooccurrence Pattern | 2 | Enriched FL, depleted CC/FQ |
| C872 | HT Discrimination Vocabulary | 3 | Folio-specific discrimination vocabulary |

---

## Data Dependencies

- `phases/PARAGRAPH_INTERNAL_PROFILING/results/b_paragraph_inventory.json`
- `phases/PARAGRAPH_INTERNAL_PROFILING/results/b_paragraph_tokens.json`
- `phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json`
- `phases/FOLIO_PARAGRAPH_ARCHITECTURE/results/folio_paragraph_census.json`

---

## Expert Validation

**Status:** VALIDATED

Quantitative findings confirmed against:
- C740 (HT = UN identity) - exact match
- C747 (Line-1 HT enrichment) - ~47% vs frozen 50.2%, within expected variance
- C748 (Line-1 step function) - consistent
- C766 (UN derived identification vocabulary) - supports interpretation
- C792 (B-exclusive = HT identity) - aligned
- C794-C795 (A-context prediction) - supports discrimination function

**Key refinement:** "Material identification" interpretation refined to "folio-specific discrimination vocabulary" to respect semantic ceiling (C120). HT discriminates procedures without encoding what materials ARE.
