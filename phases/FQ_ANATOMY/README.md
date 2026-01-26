# FQ_ANATOMY Phase

**Date:** 2026-01-26
**Goal:** Characterize the internal structure of the FREQUENT_OPERATOR (FQ) role — 4 classes {9, 13, 14, 23}, 2890 tokens (12.5% of Currier B).
**Status:** COMPLETE

## Key Findings

### Organizing Principle: 3-Group Structure (C593)

FQ splits into three behaviorally distinct sub-groups:

| Sub-Group | Classes | Tokens | Character |
|-----------|---------|--------|-----------|
| CONNECTOR | {9} | 630 | Bare, medial, hazardous, or→aiin bigram |
| PREFIXED_PAIR | {13, 14} | 1898 | ok/ot-prefixed, medial-to-final, non-hazardous |
| CLOSER | {23} | 362 | Bare, final-biased, hazardous, minimal tokens |

- k=3 clustering recovers this exactly (silhouette 0.68)
- PC1 (64.2%) separates by position, PC2 (28.2%) by morphology
- Morphology × hazard: **perfect overlap** — BARE={9,23}=HAZARDOUS, PREFIXED={13,14}=SAFE

### 13-14 Complete Vocabulary Bifurcation (C594)

Classes 13 and 14 share **zero MIDDLEs** (Jaccard = 0.000):
- Class 13: aiin, ain, e, edy, eey, eol (6 MIDDLEs, 18.2% suffixed)
- Class 14: al, am, ar, ey, ol, or, y (7 MIDDLEs, 0% suffixed)

Both use ok/ot prefixes (13 is 55% ok, 14 is 57% ot). Positionally separated (0.530 vs 0.615, p=1.6e-10). Regime/section near-identical (JS=0.0018/0.0051). This parallels EN's QO/CHSH bifurcation (C576) but is even more extreme — complete non-overlap vs 87% non-overlap.

### Internal Transitions Are Structured (C595)

470 FQ-FQ adjacent pairs, chi2=111, p<0.0001:
- Class 23→9: **2.85x enriched** (closer feeds back to connector)
- Class 9→13: **4.6:1 directional** (connector feeds workhorse)
- All classes self-chain above random (9: 1.60x, 13: 1.39x, 14: 1.45x)
- 2×2 BARE/PREFIXED aggregate: chi2=69.7, p<0.0001

### FQ-FL Symbiosis Is Position-Driven (C596)

310 FQ-FL adjacent pairs. Hazard alignment NOT significant (p=0.33):
- FL Class 7 connects preferentially to FQ Class 9
- FL Class 30 connects to FQ Classes 13/14
- The symbiosis is positional, not hazard-mediated

### Boundary Behavior (C597)

Class 23 dominates FQ final position:
- 29.8% final rate (vs 3.7% for Class 9)
- Provides 39% of all FQ final-position tokens
- Mean FQ run length: 1.19 (mostly singletons)

### Context Classifier

Accuracy 44.6% vs majority baseline 41.2% (+3.4pp). Context provides minimal signal for FQ class prediction — consistent with distributional convergence within sub-groups.

## Upstream Re-Verification

C592 flagged C550, C551, C552, C556 for re-verification with corrected FQ={9,13,14,23} (was {9,20,21,23}).

| Constraint | Verdict | Key Change |
|-----------|---------|------------|
| C550 | MAGNITUDES_SHIFTED | FQ self 2.38x→1.44x, FL→FQ 1.73x→1.34x (directions preserved) |
| C551 | UNCHANGED | Mean evenness 0.911→0.916 |
| C552 | MAGNITUDES_SHIFTED | FQ baseline 5.6%→12.5%, PHARMA enrichment 1.31x→0.79x |
| C556 | DIRECTION_SHIFTED | FQ final 1.67x→0.91x (no longer final-biased) |

The old FQ included AX_FINAL Classes 20,21, inflating self-transition and final-position metrics. C550 directional patterns are preserved but magnitudes are weaker. C556's FQ annotation changes direction — FQ is position-neutral, not final-biased.

## Scripts

| Script | Purpose | Output |
|--------|---------|--------|
| fq_structural_anatomy.py | Organizing principle, partitions, PCA, clustering, 13-14 deep dive | fq_structural_anatomy.json |
| fq_transition_context.py | Internal transitions, context classifier, FQ-FL symbiosis, boundary | fq_transition_context.json |
| fq_upstream_reverify.py | C550, C551, C552, C556 re-verification | fq_upstream_reverify.json |

## New Constraints

| # | Name | Key Finding |
|---|------|-------------|
| C593 | FQ 3-Group Structure | {9} connector, {13,14} prefixed-pair, {23} closer; silhouette 0.68 |
| C594 | FQ 13-14 Vocabulary Bifurcation | Jaccard=0.000, complete MIDDLE non-overlap, suffix complement |
| C595 | FQ Internal Transition Grammar | chi2=111, p<0.0001; 23→9 enriched 2.85x, directional flow |
| C596 | FQ-FL Position-Driven Symbiosis | Hazard alignment p=0.33; positional, not hazard-mediated |
| C597 | FQ Class 23 Boundary Dominance | 29.8% final rate, 39% of FQ finals |
