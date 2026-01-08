# Organizational Constraints (C153-C165, C323-C340, C353-C403)

**Scope:** Organizational structure, quire-level, line-level, program structure
**Status:** CLOSED

---

## Organizational Structure (C153-C165)

### C153 - Prefix/Suffix Axes Independent
**Tier:** 2 | **Status:** CLOSED
MI=0.075. Partial independence of morphological axes.
**Source:** Phase 20

### C154 - Extreme Local Continuity
**Tier:** 2 | **Status:** CLOSED
d=17.5 local continuity (vs random).
**Source:** Phase 20

### C155 - Piecewise-Sequential Geometry
**Tier:** 2 | **Status:** CLOSED
PC1 rho=-0.624. Manuscript follows piecewise order.
**Source:** Phase 20

### C156 - Sections Match Codicology
**Tier:** 2 | **Status:** CLOSED
Detected sections match physical quires (4.3x alignment).
**Source:** QLA

### C157 - Circulatory Reflux Compatible
**Tier:** 2 | **Status:** CLOSED
100% compatibility with circulatory reflux systems.
**Source:** Phase 16

### C161 - Folio Ordering = Risk Gradient
**Tier:** 2 | **Status:** CLOSED
rho=0.39 correlation between folio order and risk.
**Source:** OPS-6

### C164 - 86.7% Perfumery-Aligned Plants
**Tier:** 2 | **Status:** CLOSED
p<0.001 significance.
**Source:** PIAA

### C165 - No Program-Morphology Correlation
**Tier:** 2 | **Status:** CLOSED
Plant illustrations don't predict program type.
**Source:** PPC

---

## Terminal State Distribution (C323-C327)

### C323 - Terminal Distribution
**Tier:** 2 | **Status:** CLOSED
57.8% STATE-C, 38.6% transitional, 3.6% initial/reset.
**Source:** SEL-F

### C324 - Section-Dependent Terminals
**Tier:** 2 | **Status:** CLOSED
H/S ~50% STATE-C; B/C 70-100% STATE-C.
**Source:** SEL-F

### C325 - Completion Gradient
**Tier:** 2 | **Status:** CLOSED
STATE-C increases with position (rho=+0.24). Later folios = higher completion.
**Source:** SEL-F

---

## Grammar Robustness (C328-C331)

### C328 - Noise Robustness
**Tier:** 2 | **Status:** CLOSED
10% token corruption = only 3.3% entropy increase. Graceful degradation.
**Source:** ROBUST

### C329 - Ablation Robustness
**Tier:** 2 | **Status:** CLOSED
Top 10 tokens (15% corpus) removal = 0.8% entropy change.
**Source:** ROBUST

### C330 - Cross-Validation Stable
**Tier:** 2 | **Status:** CLOSED
Leave-one-folio-out: max 0.25% entropy change.
**Source:** ROBUST

### C331 - 49-Class Minimality
**Tier:** 2 | **Status:** CLOSED
Functional classification confirmed. Silhouette near zero for all k.
**Source:** ROBUST

---

## Kernel and LINK (C332-C334)

### C332 - Kernel Bigram Ordering
**Tier:** 2 | **Status:** CLOSED
h→k suppressed (0 observed). k→k, h→h enriched.
**Source:** KERNEL

### C333 - Kernel Trigram Dominance
**Tier:** 2 | **Status:** CLOSED
e→e→e = 97.2% of kernel trigrams. System dominated by 'e' state.
**Source:** KERNEL

### C334 - LINK Section Conditioning
**Tier:** 2 | **Status:** CLOSED
LINK varies by section (B=19.6%). NOT kernel-conditioned (z=0.05).
**Source:** LINK

---

## Cross-System Integration (C335-C340)

### C335 - 69.8% Vocabulary Integration
**Tier:** 2 | **Status:** CLOSED
69.8% of B tokens appear in A vocabulary.
**Source:** AB_INTEGRATION

### C336 - Hybrid A-Access Pattern
**Tier:** 2 | **Status:** CLOSED
Adjacent B folios share more A-vocab (0.548 vs 0.404). Sequential + semantic.
**Source:** AB_INTEGRATION

### C337 - Mixed-Marker Dominance
**Tier:** 2 | **Status:** CLOSED
89.2% of A lines contain 2+ marker classes.
**Source:** MIXED

### C338 - Marker Independence
**Tier:** 2 | **Status:** CLOSED
All marker pair ratios 0.9-1.0. Markers mix freely.
**Source:** MIXED

### C339 - E-Class Dominance
**Tier:** 2 | **Status:** CLOSED
36% of B tokens are e-class. Stability-dominated grammar.
**Source:** PHYS

### C340 - LINK-Escalation Complementarity
**Tier:** 2 | **Status:** CLOSED
LINK density 0.605x near escalation. Waiting and intervention segregated.
**Source:** PHYS

---

## Folio Gap Analysis (C353-C356)

### C353 - State Continuity Better Than Random
**Tier:** 2 | **Status:** CLOSED
d=-0.20 between adjacent folios. No extreme discontinuities.
**Source:** FG

### C354 - HT Orientation Intact
**Tier:** 2 | **Status:** CLOSED
EARLY-phase HT prefixes 2.69x enriched at folio starts.
**Source:** FG

### C355 - 75.9% Known Prefixes at Folio Start
**Tier:** 2 | **Status:** CLOSED
No structurally anomalous folio starts.
**Source:** FG

### C356 - Section Symmetry Preserved
**Tier:** 2 | **Status:** CLOSED
Max variance asymmetry 0.0027. No truncation signal.
**Source:** FG

---

## Line-Level Architecture (C357-C360)

### C357 - Lines Deliberately Chunked
→ See [C357_lines_chunked.md](C357_lines_chunked.md)

### C358 - Boundary Tokens Identified
**Tier:** 2 | **Status:** CLOSED
daiin, saiin, sain line-initial (3-11x). am, oly, dy line-final (4-31x).
**Source:** LINE

### C359 - LINK Suppressed at Boundaries
**Tier:** 2 | **Status:** CLOSED
0.60x vs mid-line. Lines ≠ pause points.
**Source:** LINE

### C360 - Grammar Line-Invariant
**Tier:** 2 | **Status:** CLOSED
0 forbidden violations in 2,338 cross-line bigrams.
**Source:** LINE

---

## Quire-Level Organization (C367-C370)

### C367 - Section-Quire Alignment
**Tier:** 2 | **Status:** CLOSED
12/18 quires single-section. Mean homogeneity 0.923 (4.3x random).
**Source:** QLA

### C368 - Regime Clustering in Quires
**Tier:** 2 | **Status:** CLOSED
Within-quire same-regime 2.20x between-quire rate.
**Source:** QLA

### C369 - Quire Vocabulary Continuity
**Tier:** 2 | **Status:** CLOSED
Within-quire Jaccard 1.69x between-quire.
**Source:** QLA

### C370 - Quire Boundaries = Discontinuities
**Tier:** 2 | **Status:** CLOSED
1.67x vocabulary drop at boundaries. 41% section changes.
**Source:** QLA

---

## Program Archetypes (C403)

### C403 - Program Continuum
**Tier:** 2 | **Status:** CLOSED
83 programs form continuum (silhouette 0.14-0.19) with 5 archetypes: Conservative Waiting, Aggressive Intervention, Balanced Standard, FREQUENT_OPERATOR-Dominated, Energy-Intensive.
**Source:** PAS

---

## Navigation

← [INDEX.md](INDEX.md) | ↑ [../CLAUDE_INDEX.md](../CLAUDE_INDEX.md)
