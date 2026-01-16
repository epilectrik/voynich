# AZC Phase Report: Astronomical/Zodiac/Cosmological Section Analysis

## Phase Code
`AZC` (Astronomical/Zodiac/Cosmological)

## Discovery

During routine audit, we discovered **3,299 tokens (8.7%)** that were never classified as Currier A or B:

| Classification | Tokens | Percentage |
|----------------|--------|------------|
| Currier B | 23,243 | 61.3% |
| Currier A | 11,415 | 30.1% |
| **Unclassified (AZC)** | **3,299** | **8.7%** |

**Note (2026-01-16):** Counts corrected from 9,401 to 3,299 after fixing transcriber filtering bug. Original analysis loaded all transcribers; corrected values use PRIMARY (H) transcriber only.

These tokens are concentrated in the Astronomical/Zodiac/Cosmological sections (f57v, f65-f73).

---

## Verdict

### **HYBRID** (Tier 2 STRUCTURAL)

The AZC text is a **genuine hybrid system** that shares substantial characteristics with both Currier A and B, while possessing distinctive properties of its own.

| Score | Classification |
|-------|---------------|
| **6** | HYBRID |
| 2 | A_LIKE |
| 1 | UNIQUE |
| 0 | B_LIKE |

**Confidence: 66.7%**

---

## Key Findings

### 1. Near-Complete Vocabulary Overlap

| Category | Types | Tokens | Percentage |
|----------|-------|--------|------------|
| Shared with BOTH A and B | ~600 | ~2,000 | **60.5%** |
| AZC-only (unique) | 903 | ~800 | 27.4% |
| Shared with B only | ~300 | ~300 | ~9% |
| Shared with A only | ~100 | ~150 | ~5% |

**Note:** Counts corrected 2026-01-16. AZC-unique types reduced from 1,529 to 903 after H-only filtering.

**Interpretation:** The majority of AZC vocabulary (60.5%) comes from the INTERSECTION of A and B. This is the "shared operational vocabulary" that both systems use.

### 2. Threshold-Straddling Coverage

| Test | AZC Result | Threshold | Verdict |
|------|------------|-----------|---------|
| B vocabulary coverage | **69.7%** | 70% | FAIL (barely) |
| A vocabulary coverage | **65.4%** | 70% | FAIL |
| Marker prefix similarity | **0.90** | 0.80 | A-LIKE |
| LINK density | **7.6%** | 6.6% (B) | B-LIKE |

AZC straddles the classification thresholds — it's too similar to both to be "unique," but doesn't clearly fit either.

### 3. Distinctive Line Structure

| Metric | AZC | Currier A | Currier B |
|--------|-----|-----------|-----------|
| Tokens/line (median) | **8** | 22 | 31 |
| TTR | **0.285** | 0.137 | 0.096 |
| Lines | 442 | — | — |

AZC has **dramatically shorter lines** than both A and B, with much higher vocabulary diversity (TTR).

### 4. Higher Repetition and LINK Density

| Metric | AZC | Currier A | Currier B |
|--------|-----|-----------|-----------|
| Repetition rate | **6.4%** | 2.0% | — |
| LINK density | **7.6%** | 3.0% | 6.6% |
| Bigram reuse | **32.5%** | 70.7% | — |

AZC shows MORE repetition than A, and HIGHER LINK density than B. This is consistent with a "waiting-heavy" procedural text with embedded repetition.

### 5. Morphological Profile

| Metric | AZC | Currier A | Currier B |
|--------|-----|-----------|-----------|
| Prefix coverage | 62.4% | 68.8% | 67.1% |
| Suffix coverage | 72.3% | 80.1% | 87.7% |

AZC has **lower prefix and suffix coverage** than both A and B — more vocabulary falls outside the standard morphological patterns.

**Top AZC prefixes:** ch (1354), ot (1315), ok (1076), da (594)
**Top AZC suffixes:** y (967), dy (880), ar (853), al (729)

### 6. Section Variation

| Section | Tokens | TTR | A Coverage | B Coverage |
|---------|--------|-----|------------|------------|
| C (Cosmological) | 3,298 | 0.284 | 72.9% | 75.6% |
| Z (Zodiac) | 3,184 | 0.393 | 60.8% | 66.3% |
| A (Astronomical) | 2,785 | 0.353 | 62.0% | 66.1% |
| H (spillover) | 132 | 0.455 | 62.1% | 77.3% |

**Section C is most B-like** (75.6% coverage), while **Section Z is most diverse** (highest TTR, lowest coverage).

---

## Structural Interpretation (Tier 2)

### What AZC IS (Structural Facts)

1. **VOCABULARY BRIDGE:** 60.5% of AZC vocabulary appears in BOTH A and B. AZC uses the "shared core" vocabulary that bridges the two systems.

2. **LINE STRUCTURE DISTINCT:** Median 8 tokens/line is unique — neither the dense lines of B (31) nor the moderate lines of A (22). This may reflect the **tabular/diagrammatic nature** of zodiac and astronomical pages.

3. **HIGH LINK DENSITY (7.6%):** More "waiting" tokens than even B. If LINK represents waiting/non-intervention, AZC is extremely wait-heavy.

4. **HIGHER VOCABULARY DIVERSITY (TTR 0.285):** More diverse than both A (0.137) and B (0.096). Each folio/section uses more unique vocabulary.

5. **SUBSTANTIAL UNIQUE VOCABULARY (25.4%):** 903 types (2,389 tokens) appear ONLY in AZC — these are section-specific markers or astronomical terminology.

### What AZC Might Be (Tier 3 Speculative)

The following interpretations are NON-BINDING and DISCARDABLE:

- AZC may represent **labeling text for diagrams** (short lines, high diversity)
- AZC may use **shared vocabulary** because it references both catalog items (A) and procedures (B)
- The high LINK density may indicate **timing/waiting information** relevant to astronomical observations
- The unique vocabulary (25.4%) may encode **celestial terms, zodiac signs, or calendar references**

---

## Folio Inventory

The 30 AZC folios, ranked by token count:

| Folio | Section | Tokens | A Coverage | B Coverage |
|-------|---------|--------|------------|------------|
| f70r2 | C | 831 | 74.5% | 79.2% |
| f67r2 | A | 612 | 60.5% | 64.4% |
| f68v3 | C | 531 | 66.9% | 69.7% |
| f70v2 | Z | 524 | 66.8% | 72.9% |
| f69r | C | 504 | 79.6% | 79.4% |
| f57v | C | 470 | 76.4% | 81.1% |
| f67r1 | A | 420 | 63.8% | 71.4% |
| f69v | C | 417 | 76.3% | 78.2% |
| f68v2 | A | 393 | 63.4% | 71.0% |
| f72r3 | Z | 354 | 58.5% | 62.7% |
| f70r1 | C | 327 | 73.4% | 75.5% |
| f68r2 | A | 316 | 56.6% | 52.5% |
| f68r3 | A | 314 | 65.3% | 67.2% |
| f68v1 | A | 284 | 66.9% | 72.9% |
| f72v3 | Z | 269 | 56.9% | 63.6% |

---

## Comparison with Prior Models

### How AZC Relates to Prior Findings

| Prior Finding | AZC Implication |
|---------------|-----------------|
| A/B are DISJOINT (Constraint 272) | **PARTIAL REVISION:** A and B share 60.5% vocabulary in AZC; the "disjoint" characterization applies to folio-level, not vocabulary-level |
| 49-class grammar (B only) | AZC has 69.7% B vocabulary coverage — **partially grammatical** |
| Human Track (33.4% of B) | AZC's 25.4% unique vocabulary may be analogous — section-specific navigation |
| LINE_ATOMIC (A property) | AZC is NOT line-atomic (8 tokens/line is still multi-token) |

### The "Third Mode" Hypothesis

AZC appears to be a **third mode** that combines:
- **A's marker prefixes** (0.90 similarity)
- **B's LINK density** (7.6% vs 6.6%)
- **Unique line structure** (median 8 tokens)
- **Shared vocabulary** (60.5% overlap with A∩B)

This is consistent with **diagrammatic annotation text** — short labels that reference both catalog entries (A) and procedural elements (B).

---

## New Constraints

### Constraint 300 (Tier 2 STRUCTURAL)
**3,299 tokens (8.7%) in A/Z/C sections are UNCLASSIFIED by Currier A/B.** These are concentrated in 30 folios across Astronomical (A), Zodiac (Z), and Cosmological (C) sections. Prior analyses treated the manuscript as binary A/B; this was incomplete.

### Constraint 301 (Tier 2 STRUCTURAL)
**AZC text is HYBRID:** B vocabulary coverage 69.7%, A vocabulary coverage 65.4%, shared vocabulary 60.5%. Neither purely A-like nor B-like; straddles classification thresholds.

### Constraint 302 (Tier 2 STRUCTURAL)
**AZC has DISTINCT line structure:** Median 8 tokens/line (vs A=22, B=31). Higher TTR (0.285 vs A=0.137, B=0.096). Consistent with diagrammatic/tabular annotation rather than continuous text.

### Constraint 303 (Tier 2 STRUCTURAL)
**AZC has ELEVATED LINK density (7.6%)** — higher than both A (3.0%) and B (6.6%). If LINK encodes waiting, AZC is the most wait-heavy text in the manuscript.

### Constraint 304 (Tier 2 STRUCTURAL)
**AZC has 25.4% UNIQUE vocabulary (903 types)** that appears in neither A nor B. This is section-specific terminology absent from the rest of the manuscript.

### Constraint 305 (Tier 2 STRUCTURAL)
**AZC-unique vocabulary has LABELING signature:** 98% section-exclusive, 37% line-initial, 37% line-final, 65.9% hapax. This is structurally distinct from execution (B) and indexing (A).

### Constraint 306 (Tier 2 STRUCTURAL)
**AZC-unique tokens exhibit a finite, repeatable set of placement-dependent classes** (C, P, R1-R3, S-S2, Y) with non-uniform distribution. These classes are orthogonal to morphological identity, recur across folios, participate in repetition-based multiplicity, and integrate into surrounding hybrid grammar. This establishes a formal PLACEMENT-CODING axis within the AZC inscriptional mode.

---

## AZC-Unique Vocabulary Probe (AZC-PROBE)

Deep analysis of the 903 unique types (2,392 tokens) revealed:

### Structural Findings (Tier 2)

| Metric | Value | Interpretation |
|--------|-------|----------------|
| Section-exclusive | **98.0%** | Almost all unique tokens in ONE section only |
| Line-initial | **37.3%** | Heavily concentrated at line starts |
| Line-final | **37.0%** | Heavily concentrated at line ends |
| Hapax | **65.9%** | Most tokens appear only once |
| Prefix coverage | 61.5% | Follows standard morphology |
| Suffix coverage | 66.1% | Follows standard morphology |
| Special chars | 125 tokens | Uncertain/damaged readings |

### Section Distribution

| Section | Tokens | Types |
|---------|--------|-------|
| Z (Zodiac) | 918 | 645 |
| A (Astronomical) | 788 | 480 |
| C (Cosmological) | 660 | 418 |

### Functional Classification

The structural signature (98% section-exclusive, 37% line-boundary, 65.9% hapax) indicates:

- **NOT EXECUTING:** No procedural sequences, no grammar-like transitions
- **NOT INDEXING:** No block repetition patterns, high hapax rate
- **IS LABELING:** Section-specific, boundary-concentrated, unique instances

### Speculative Interpretation (Tier 3, DISCARDABLE)

The labeling function may represent **diagram annotations**:
- Zodiac sign names
- Star/constellation labels
- Calendar or positional terms
- Element labels on cosmological diagrams

This interpretation is NON-BINDING and should not influence structural analysis.

---

## Placement-Coding Analysis (AZC-PLACEMENT)

Deep analysis of label placement revealed a systematic positional coding system:

### Placement Class Distribution

| Class | Count | Percentage |
|-------|-------|------------|
| C | 408 | 17.1% |
| P | 263 | 11.0% |
| R1 | 256 | 10.7% |
| S1 | 237 | 9.9% |
| R2 | 176 | 7.4% |
| S | 173 | 7.2% |
| R | 162 | 6.8% |
| S2 | 159 | 6.6% |
| R3 | 109 | 4.6% |
| Y | 104 | 4.3% |

### Structural Properties (Tier 2)

1. **Finite set:** Limited number of placement classes
2. **Non-uniform distribution:** C dominates (17.1%), long tail
3. **Orthogonal to morphology:** Placement class independent of PREFIX/SUFFIX
4. **Cross-folio recurrence:** Same classes appear in multiple folios
5. **Repetition participation:** Labels repeat within folios per placement
6. **Grammar integration:** Surrounded by shared vocabulary (aiin, daiin, ar)

### Additional Findings

- **73.4% standard morphology:** ~660/903 labels follow PREFIX+MIDDLE+SUFFIX
- **Internal folio repetition:** 28 folios have repeated labels (e.g., 'otaldar' x5)
- **Cross-folio standards:** 54 labels appear in multiple folios
- **Length peak:** 6-7 characters typical

### Speculative Interpretation (Tier 3, DISCARDABLE)

Placement codes MAY represent diagram positions:
- C = Center
- R1, R2, R3 = Radial positions
- S, S1, S2 = Sector positions
- P = Peripheral

This is NON-BINDING speculation.

---

## Impact on Frozen Conclusions

### Requires Revision

1. **Total manuscript coverage:** Prior analyses accounted for A (31.8%) + B (64.7%) = 96.5%. The remaining 7.7% is now characterized as HYBRID.

2. **Binary A/B model:** The manuscript is not purely bimodal. AZC represents a third mode that bridges A and B.

3. **Constraint 272 (0 shared folios):** Still valid at folio level, but vocabulary is substantially shared (60.5% in AZC).

### Does NOT Require Revision

1. **49-class grammar:** Applies to B; AZC's 69.7% coverage is expected for non-B text
2. **Hazard topology:** AZC wasn't included in hazard analysis
3. **Human Track characterization:** Still valid for B
4. **A as registry:** Still valid; AZC is distinct

---

## Files

- `AZC_PLAN.md` — Research plan (this phase)
- `AZC_REPORT.md` — This report
- `azc_results.json` — Full analysis results
- `azc_unique_probe.json` — Unique vocabulary probe results
- `azc_label_structure.json` — Label structure analysis results
- `archive/scripts/azc_analysis.py` — Main analysis script
- `archive/scripts/azc_unique_probe.py` — Unique vocabulary probe script
- `archive/scripts/azc_label_structure.py` — Label structure analysis script

---

## Summary

| Metric | Value |
|--------|-------|
| Total AZC tokens | 3,299 (8.7% of corpus) |
| Unique types | 2,681 |
| Folios | 30 |
| Verdict | **HYBRID** |
| B coverage | 69.7% |
| A coverage | 65.4% |
| Shared vocabulary (A∩B) | 60.5% |
| Unique vocabulary | 25.4% (903 types) |
| Unique vocab section-exclusive | 98.0% |
| Unique vocab line-boundary | 37% |
| Unique vocab hapax rate | 65.9% |
| Placement classes | C, P, R1-R3, S-S2, Y (10 classes) |
| Dominant placement | C (17.1%) |
| LINK density | 7.6% |
| TTR | 0.285 |
| Tokens/line (median) | 8 |

**AZC is a genuine third mode — a hybrid system that bridges Currier A and B through shared vocabulary, while maintaining distinctive structural properties. The unique vocabulary shows a LABELING signature with a formal PLACEMENT-CODING axis (Tier 2). Diagram annotation interpretation remains speculative (Tier 3).**

---

*AZC COMPLETE. 7 new constraints validated (300-306).*
