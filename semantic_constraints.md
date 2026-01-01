# Semantic Constraints (Phase 18)

**Date:** 2025-12-30
**Status:** Established from validated structural findings

This document defines what semantic claims can and cannot be made based on the rigorous structural analysis conducted in Phases 15-18. These constraints must guide any future interpretation attempts.

---

## 1. Entity-Level Constraints

### What We Know

| Constraint | Evidence | Confidence |
|------------|----------|------------|
| Currier A defines ~114 distinct entities | 114 entries identified by folio | HIGH |
| Each entity has three-part description | Statistical validation of Part 1/2/3 structure | HIGH |
| 78.3% of entity identifiers (headings) are unique to single entry | Heading uniqueness analysis | HIGH |
| Headings are proper names, not common nouns | Uniqueness + positional specificity | HIGH |
| Headings follow word grammar at higher rate than body | 86.8% vs 75.6% grammar compliance | HIGH |
| Headings are longer than body words | Mean 6.43 vs 5.1 characters | HIGH |

### Constraint Implications

- Each Currier A entry is DEFINITIONAL (defines something)
- The "something" being defined is specific enough to warrant a unique identifier
- Entity identifiers are constructed, not random strings

---

## 2. Relational Constraints

### What We Know

| Constraint | Evidence | Confidence |
|------------|----------|------------|
| B entries reference A entities | INFINITE asymmetry (809 vs 0 cross-references) | VERY HIGH |
| Not all A entities are equally referenced | In-degree variance: 0-26 references per entry | HIGH |
| Some A entities are never referenced by B | 34 isolated A nodes (30% of A entries) | HIGH |
| B entries can reference multiple A entities | Mean B out-degree: 1.82 | HIGH |
| Most referenced A entry: f58v (heading 'tol') | 26 B entries reference it | HIGH |
| Reference pattern is DISTRIBUTED, not sequential | Spearman r = -0.17 between folio position and reference count | HIGH |

### Constraint Implications

- B is EXPOSITORY, not definitional (discusses A entities, doesn't define new ones)
- A entities have varying "importance" in B discussion
- The A→B relationship is author-intentional, not accidental
- B entries synthesize information about A entities

---

## 3. Structural Constraints

### Three-Part Entry Structure

| Part | Function | Evidence |
|------|----------|----------|
| Part 1 | Entity identification | Contains heading word, unique vocabulary |
| Part 2 | Entity properties/attributes | Different prefix distribution than Parts 1 and 3 |
| Part 3 | Entity applications/relations | Most variation in vocabulary |

### Grammar Constraints

| Constraint | Evidence |
|------------|----------|
| Words have PREFIX + MIDDLE + SUFFIX structure | Position constraints validated |
| 41% of words end in 'y' | Consistent across manuscript |
| Character position rules are strict | q=first only, y/n/m=final, i/h/e=middle |
| Section-specific prefix enrichment | 2-6x enrichment vs scrambled control |

---

## 4. Vocabulary Constraints

### Population Separation

| Constraint | Evidence |
|------------|----------|
| Currier A and B are distinct text populations | Only 14.1% vocabulary overlap |
| 69.9% of A vocabulary is A-exclusive | 3,473 words only in A |
| 79.1% of B vocabulary is B-exclusive | 5,668 words only in B |
| Shared vocabulary is asymmetric | Shared words appear more in B than A |

### Heading-Specific Vocabulary

| Constraint | Evidence |
|------------|----------|
| Heading prefixes differ from body prefixes | Top: po (17), pc (16), ko (11) in headings |
| 33 part-specific words identified | Appear only in Part 1, 2, or 3 |
| Heading vocabulary is distinct | 95.6% of headings are unique |

---

## 5. What We Can Now Say

Based on validated findings, the following statement is scientifically defensible:

> **"The Voynich Manuscript (Currier A section) is a reference work where approximately 114 entries each define a distinct entity using three-part descriptions. Entity identifiers (headings) are unique proper names, not common vocabulary. Currier B provides extended discussion that references these defined entities, with some entities receiving substantially more discussion than others. The relationship is definitional-to-expository, analogous to a dictionary or encyclopedia being referenced by a treatise."**

### Specific Defensible Claims

1. **The manuscript has organizational structure** - not random text
2. **Entries define entities** - three-part structure with unique headings
3. **Cross-referencing exists** - B references A entities systematically
4. **Author intentionality** - structural patterns are not accidental
5. **Genre is reference-like** - definitional entries with expository discussion

---

## 6. What We Cannot Yet Say

### Blocked Without Visual Correlation

| Claim | Why Blocked |
|-------|-------------|
| What any entity IS | No external anchor to content |
| Whether entities are real-world objects | Illustrations not yet correlated |
| What visual features mean | Visual coding not yet complete |
| Anything about plant identities | Visual-text correlation required first |

### Blocked Without Translation

| Claim | Why Blocked |
|-------|-------------|
| What any word MEANS | No validated translation |
| What language underlies the text | Encoding/language undetermined |
| Semantic content of Parts 1, 2, 3 | Labels are structural, not semantic |
| Whether text is meaningful or hoax | Content meaning unknown |

### Blocked by Failed Tests

| Claim | Why Blocked |
|-------|-------------|
| PLANT-PROCESS-BODY procedures | Pattern failed randomization tests |
| Zodiac phonetic labels | Control scored equal/higher |
| Medical recipe structure | Poor fit (37-50%) |
| Specific Latin morpheme mappings | Based on invalidated patterns |

---

## 7. Gating Conditions for Semantic Claims

### To Claim "This Entry Describes Plant X"

**REQUIRED (in order):**
1. Visual features coded for the folio (Task 1 protocol)
2. Text features extracted (Task 2 complete)
3. Visual-text correlation statistically significant (Task 3)
4. Correlation survives null model comparison
5. Visual features match known plant X
6. Then and only then: compare heading phonetics to plant X name

### To Claim "This Word Means Y"

**REQUIRED:**
1. Multiple independent confirmations
2. Consistent usage across all occurrences
3. No contradicting evidence
4. Statistical significance above chance

---

## 8. Pre-Registered Success/Failure Criteria

### Visual Correlation Pilot Study

**Success Defined As:**
- ≥3 visual features correlating with text features at p < 0.01 (Bonferroni-corrected)
- ≥1 correlation surviving null model comparison (>99th percentile)
- Correlations must be interpretable (not arbitrary)

**Failure Defined As:**
- <3 significant correlations
- All correlations explained by null model
- No interpretable patterns

### Reference Graph Analysis

**Success Criteria Met:**
- Graph successfully constructed: 151 edges
- Reference pattern characterized: DISTRIBUTED
- Most-referenced entries identified: f58v (26 refs)

---

## 9. Constraint Summary Table

| ID | Constraint | Evidence Level |
|----|------------|----------------|
| C1 | ~114 entries define distinct entities | HIGH |
| C2 | Three-part entry structure | HIGH |
| C3 | 78.3% heading uniqueness | HIGH |
| C4 | B→A asymmetry is INFINITE | VERY HIGH |
| C5 | 14.1% vocabulary overlap A/B | HIGH |
| C6 | Section-conditioned vocabulary (2-6x enrichment) | HIGH |
| C7 | Words have PREFIX + MIDDLE + SUFFIX | HIGH |
| C8 | 41% final-y rate | HIGH |
| C9 | Extremely low repetition (0.1-0.3%) | HIGH |
| C10 | High position entropy (9.4 bits) | HIGH |
| C11 | PLANT-PROCESS-BODY patterns are artifacts | HIGH |
| C12 | Currier A = DESCRIPTIVE_HERBAL genre | MEDIUM |
| C13 | Currier B = ENCYCLOPEDIA genre | MEDIUM |
| C14 | Headings are proper names | HIGH |
| C15 | 33 part-specific words exist | HIGH |
| C16 | Reference pattern is DISTRIBUTED | HIGH |
| C17 | Headings longer than body words | HIGH |
| C18 | Headings have higher grammar compliance | HIGH |

---

## 10. How to Use These Constraints

### For Decipherment Attempts

1. Check your hypothesis against ALL 18 constraints
2. Hypothesis must not violate any HIGH confidence constraint
3. Document which constraints your hypothesis explains
4. Pre-register tests before looking at results

### For Semantic Claims

1. Follow the gating conditions (Section 7)
2. Use visual correlation as first external anchor
3. Do not skip ahead to plant identification
4. Report negative results with same rigor

### For Publication

1. Cite constraint table with evidence levels
2. Distinguish structural findings from semantic hypotheses
3. Acknowledge limitations explicitly
4. Include falsification test results

---

## Conclusion

We have established a rigorous foundation of structural constraints that bound future semantic interpretation. The key breakthrough is the B→A asymmetry proving intentional cross-referencing. However, semantic meaning remains inaccessible without external anchoring through visual correlation.

**Next Step:** Complete visual coding for 30 pilot folios, then run correlation framework.
